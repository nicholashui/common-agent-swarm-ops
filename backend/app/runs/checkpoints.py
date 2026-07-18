"""Organization-scoped durable checkpoint creation and resume controls."""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime
from types import MappingProxyType

from app.models.common import SCHEMA_VERSION, RecordMetadata, utc_now
from app.models.contracts import ErrorCode, ErrorDetail, Result
from app.models.identifiers import (
    CorrelationId,
    OrganizationId,
    RecordId,
    RunId,
    new_record_id,
)
from app.models.runs import RunRecord, WorkflowEngineKind
from app.repositories.protocols import CheckpointRepository


def checkpoint_thread_id(organization_id: OrganizationId, run_id: RunId) -> str:
    """Build the unambiguous graph checkpoint thread identity for one tenant run."""
    organization = str(organization_id)
    run = str(run_id)
    if not organization or not run or ":" in organization or ":" in run:
        message = "Checkpoint organization and run identifiers must be non-empty and colon-free."
        raise ValueError(message)
    return f"{organization}:{run}"


@dataclass(frozen=True, slots=True)
class CheckpointRecord:
    """One immutable, JSON-serializable graph checkpoint persisted in Postgres."""

    metadata: RecordMetadata
    run_id: RunId
    thread_id: str
    namespace: str
    sequence: int
    checkpoint: Mapping[str, object]
    snapshot_reference: str

    def __post_init__(self) -> None:
        """Reject malformed checkpoints before a persistence adapter can receive them."""
        expected_thread_id = checkpoint_thread_id(self.metadata.organization_id, self.run_id)
        if self.thread_id != expected_thread_id:
            raise ValueError("Checkpoint thread ID must exactly match its organization and run.")
        if not self.namespace.strip() or self.sequence < 1 or not self.snapshot_reference.strip():
            raise ValueError("Checkpoint namespace, sequence, and snapshot reference are required.")
        try:
            normalized = json.loads(
                json.dumps(dict(self.checkpoint), allow_nan=False, sort_keys=True)
            )
        except (TypeError, ValueError) as error:
            raise ValueError("Checkpoint payload must be JSON-serializable.") from error
        if not isinstance(normalized, dict) or not all(
            isinstance(key, str) for key in normalized
        ):
            raise ValueError("Checkpoint payload must be a JSON object with string keys.")
        object.__setattr__(self, "checkpoint", MappingProxyType(normalized))


@dataclass(frozen=True, slots=True)
class CheckpointResume:
    """A validated checkpoint that a GraphEngine may resume in-process."""

    run: RunRecord
    checkpoint: CheckpointRecord


class CheckpointResumeService:
    """Create checkpoints and authorize resume without any non-durable fallback."""

    def __init__(
        self,
        repository: CheckpointRepository,
        *,
        clock: Callable[[], datetime] = utc_now,
        record_id_factory: Callable[[], RecordId] = new_record_id,
    ) -> None:
        self._repository = repository
        self._clock = clock
        self._record_id_factory = record_id_factory

    def persist(
        self,
        run: RunRecord,
        namespace: str,
        sequence: int,
        checkpoint: Mapping[str, object],
        snapshot_reference: str,
        correlation_id: CorrelationId,
    ) -> Result[CheckpointRecord, ErrorDetail]:
        """Persist a graph checkpoint or fail without silently using local memory."""
        expected_thread_id = self._expected_graph_thread(run, correlation_id)
        if isinstance(expected_thread_id, ErrorDetail):
            return Result.failure(expected_thread_id)
        now = self._clock()
        try:
            record = CheckpointRecord(
                metadata=RecordMetadata(
                    record_id=self._record_id_factory(),
                    organization_id=run.metadata.organization_id,
                    correlation_id=correlation_id,
                    schema_version=SCHEMA_VERSION,
                    version=1,
                    created_at=now,
                    updated_at=now,
                ),
                run_id=run.run_id,
                thread_id=expected_thread_id,
                namespace=namespace,
                sequence=sequence,
                checkpoint=checkpoint,
                snapshot_reference=snapshot_reference,
            )
        except ValueError:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.VALIDATION_FAILED,
                    "Graph checkpoint data is invalid.",
                    correlation_id,
                )
            )
        persisted = self._repository.save(record)
        if not persisted.is_success:
            return Result.failure(self._with_correlation(persisted.error, correlation_id))
        return persisted

    def resume(
        self,
        request_organization_id: OrganizationId,
        run: RunRecord,
        correlation_id: CorrelationId,
    ) -> Result[CheckpointResume, ErrorDetail]:
        """Authorize tenant scope before any durable checkpoint lookup occurs."""
        if run.metadata.organization_id != request_organization_id:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.AUTHORIZATION_DENIED,
                    "Cross-organization checkpoint resume is denied.",
                    correlation_id,
                )
            )
        expected_thread_id = self._expected_graph_thread(run, correlation_id)
        if isinstance(expected_thread_id, ErrorDetail):
            return Result.failure(expected_thread_id)
        fetched = self._repository.get_for_resume(request_organization_id, run.run_id)
        if not fetched.is_success:
            return Result.failure(self._with_correlation(fetched.error, correlation_id))
        checkpoint = self._required_value(fetched)
        if (
            checkpoint.metadata.organization_id != request_organization_id
            or checkpoint.run_id != run.run_id
            or checkpoint.thread_id != expected_thread_id
        ):
            return Result.failure(
                ErrorDetail(
                    ErrorCode.AUTHORIZATION_DENIED,
                    "Checkpoint scope does not authorize this resume.",
                    correlation_id,
                )
            )
        return Result.success(CheckpointResume(run=run, checkpoint=checkpoint))

    @staticmethod
    def _expected_graph_thread(run: RunRecord, correlation_id: CorrelationId) -> str | ErrorDetail:
        if run.engine is not WorkflowEngineKind.GRAPH:
            return ErrorDetail(
                ErrorCode.INVALID_TRANSITION,
                "Only GraphEngine runs may persist or resume graph checkpoints.",
                correlation_id,
            )
        try:
            expected_thread_id = checkpoint_thread_id(run.metadata.organization_id, run.run_id)
        except ValueError:
            return ErrorDetail(
                ErrorCode.VALIDATION_FAILED,
                "Graph run identifiers cannot form a checkpoint thread ID.",
                correlation_id,
            )
        if run.graph_thread_id != expected_thread_id:
            return ErrorDetail(
                ErrorCode.INVALID_TRANSITION,
                "Graph run checkpoint identity has not been durably initialized.",
                correlation_id,
            )
        return expected_thread_id

    @staticmethod
    def _with_correlation(
        error: ErrorDetail | None, correlation_id: CorrelationId
    ) -> ErrorDetail:
        if error is None:
            return ErrorDetail(
                ErrorCode.REPOSITORY_UNAVAILABLE,
                "Durable checkpoint persistence is unavailable.",
                correlation_id,
            )
        return ErrorDetail(
            error.code,
            error.message,
            correlation_id,
            retryable=error.retryable,
            fields=error.fields,
        )

    @staticmethod
    def _required_value(result: Result[CheckpointRecord, ErrorDetail]) -> CheckpointRecord:
        if result.value is None:
            raise RuntimeError("A successful checkpoint result did not contain a checkpoint.")
        return result.value
