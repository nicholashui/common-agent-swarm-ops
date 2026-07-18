"""Configured-Postgres persistence for organization-scoped graph checkpoints."""

from __future__ import annotations

import json
from collections.abc import Callable, Sequence
from datetime import datetime
from typing import Protocol

from app.models.common import RecordMetadata
from app.models.contracts import ErrorCode, ErrorDetail, RepositoryError, Result
from app.models.identifiers import CorrelationId, OrganizationId, RecordId, RunId
from app.runs.checkpoints import CheckpointRecord, checkpoint_thread_id


class PostgresCursor(Protocol):
    """Subset of a configured Postgres DB-API cursor used by this repository."""

    def execute(self, operation: str, parameters: Sequence[object] = ()) -> object:
        """Execute one parameterized statement."""

    def fetchone(self) -> Sequence[object] | None:
        """Return one selected row when available."""

    def close(self) -> object:
        """Release cursor resources."""


class PostgresConnection(Protocol):
    """Subset of a configured Postgres DB-API connection used by this repository."""

    def cursor(self) -> PostgresCursor:
        """Open a cursor for a single checkpoint transaction."""

    def commit(self) -> object:
        """Commit a checkpoint write transaction."""

    def rollback(self) -> object:
        """Roll back a failed checkpoint write transaction."""

    def close(self) -> object:
        """Release connection resources."""


PostgresConnectionFactory = Callable[[], PostgresConnection]


class PostgresCheckpointRepository:
    """Persist checkpoints only through an explicitly configured Postgres connection."""

    _INSERT = """
        INSERT INTO graph_checkpoints (
            record_id, organization_id, run_id, thread_id, checkpoint_namespace,
            sequence, checkpoint, snapshot_reference, correlation_id, schema_version,
            version, created_at, updated_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb, %s, %s, %s, %s, %s, %s)
    """

    _SELECT_LATEST = """
        SELECT record_id, organization_id, run_id, thread_id, checkpoint_namespace,
               sequence, checkpoint, snapshot_reference, correlation_id, schema_version,
               version, created_at, updated_at
        FROM graph_checkpoints
        WHERE organization_id = %s AND run_id = %s AND thread_id = %s
        ORDER BY sequence DESC
        LIMIT 1
    """

    def __init__(self, connection_factory: PostgresConnectionFactory) -> None:
        self._connection_factory = connection_factory

    def save(self, checkpoint: CheckpointRecord) -> Result[CheckpointRecord, RepositoryError]:
        """Append one checkpoint through Postgres, returning no in-memory substitute on error."""
        connection: PostgresConnection | None = None
        cursor: PostgresCursor | None = None
        try:
            connection = self._connection_factory()
            cursor = connection.cursor()
            cursor.execute(self._INSERT, self._insert_parameters(checkpoint))
            connection.commit()
            return Result.success(checkpoint)
        except Exception as error:
            self._rollback(connection)
            return Result.failure(self._database_error(error))
        finally:
            self._close(cursor)
            self._close(connection)

    def get_for_resume(
        self, organization_id: OrganizationId, run_id: RunId
    ) -> Result[CheckpointRecord, RepositoryError]:
        """Return the latest checkpoint within the requested organization and run only."""
        connection: PostgresConnection | None = None
        cursor: PostgresCursor | None = None
        try:
            expected_thread_id = checkpoint_thread_id(organization_id, run_id)
        except ValueError:
            return Result.failure(
                self._error(
                    ErrorCode.VALIDATION_FAILED,
                    "Checkpoint organization and run identifiers are invalid.",
                )
            )
        try:
            connection = self._connection_factory()
            cursor = connection.cursor()
            cursor.execute(
                self._SELECT_LATEST,
                (str(organization_id), str(run_id), expected_thread_id),
            )
            row = cursor.fetchone()
            if row is None:
                return Result.failure(self._error(ErrorCode.NOT_FOUND, "Checkpoint was not found."))
            return Result.success(self._record_from_row(row))
        except Exception as error:
            return Result.failure(self._database_error(error))
        finally:
            self._close(cursor)
            self._close(connection)

    @staticmethod
    def _insert_parameters(checkpoint: CheckpointRecord) -> tuple[object, ...]:
        metadata = checkpoint.metadata
        return (
            str(metadata.record_id),
            str(metadata.organization_id),
            str(checkpoint.run_id),
            checkpoint.thread_id,
            checkpoint.namespace,
            checkpoint.sequence,
            json.dumps(dict(checkpoint.checkpoint), allow_nan=False, sort_keys=True),
            checkpoint.snapshot_reference,
            str(metadata.correlation_id),
            metadata.schema_version,
            metadata.version,
            metadata.created_at,
            metadata.updated_at,
        )

    @classmethod
    def _record_from_row(cls, row: Sequence[object]) -> CheckpointRecord:
        if len(row) != 13:
            raise ValueError("Checkpoint query returned an unexpected row shape.")
        (
            raw_record_id,
            raw_organization_id,
            raw_run_id,
            raw_thread_id,
            raw_namespace,
            raw_sequence,
            raw_checkpoint,
            raw_snapshot_reference,
            raw_correlation_id,
            raw_schema_version,
            raw_version,
            raw_created_at,
            raw_updated_at,
        ) = row
        if (
            not isinstance(raw_record_id, str)
            or not isinstance(raw_organization_id, str)
            or not isinstance(raw_run_id, str)
            or not isinstance(raw_thread_id, str)
            or not isinstance(raw_namespace, str)
            or not isinstance(raw_snapshot_reference, str)
            or not isinstance(raw_correlation_id, str)
        ):
            raise ValueError("Checkpoint query returned invalid identifier fields.")
        if (
            not isinstance(raw_sequence, int)
            or isinstance(raw_sequence, bool)
            or not isinstance(raw_schema_version, int)
            or isinstance(raw_schema_version, bool)
            or not isinstance(raw_version, int)
            or isinstance(raw_version, bool)
            or not isinstance(raw_created_at, datetime)
            or not isinstance(raw_updated_at, datetime)
            or raw_created_at.tzinfo is None
            or raw_updated_at.tzinfo is None
        ):
            raise ValueError("Checkpoint query returned invalid record metadata.")
        return CheckpointRecord(
            metadata=RecordMetadata(
                record_id=RecordId(raw_record_id),
                organization_id=OrganizationId(raw_organization_id),
                correlation_id=CorrelationId(raw_correlation_id),
                schema_version=raw_schema_version,
                version=raw_version,
                created_at=raw_created_at,
                updated_at=raw_updated_at,
            ),
            run_id=RunId(raw_run_id),
            thread_id=raw_thread_id,
            namespace=raw_namespace,
            sequence=raw_sequence,
            checkpoint=cls._checkpoint_mapping(raw_checkpoint),
            snapshot_reference=raw_snapshot_reference,
        )

    @staticmethod
    def _checkpoint_mapping(raw_checkpoint: object) -> dict[str, object]:
        decoded = json.loads(raw_checkpoint) if isinstance(raw_checkpoint, str) else raw_checkpoint
        if not isinstance(decoded, dict) or not all(isinstance(key, str) for key in decoded):
            raise ValueError("Checkpoint query returned invalid checkpoint JSON.")
        return {key: value for key, value in decoded.items()}

    @staticmethod
    def _rollback(connection: PostgresConnection | None) -> None:
        if connection is None:
            return
        try:
            connection.rollback()
        except Exception:
            return

    @staticmethod
    def _close(resource: PostgresCursor | PostgresConnection | None) -> None:
        if resource is None:
            return
        try:
            resource.close()
        except Exception:
            return

    @classmethod
    def _database_error(cls, error: Exception) -> RepositoryError:
        if getattr(error, "sqlstate", None) == "23505":
            return cls._error(ErrorCode.CONFLICT, "Checkpoint sequence already exists.")
        return cls._error(
            ErrorCode.REPOSITORY_UNAVAILABLE,
            "Configured durable checkpoint persistence is unavailable.",
        )

    @staticmethod
    def _error(code: ErrorCode, message: str) -> RepositoryError:
        return ErrorDetail(code, message, CorrelationId("postgres-checkpoint-repository"))
