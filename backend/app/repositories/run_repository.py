"""Run persistence with version checks and an explicitly seed-only JSON loader."""

from __future__ import annotations

import json
from collections.abc import Mapping
from datetime import datetime
from pathlib import Path
from threading import RLock

from app.models.common import OptimisticTransition, RecordMetadata
from app.models.contracts import ErrorCode, ErrorDetail, RepositoryError, Result
from app.models.identifiers import (
    CorrelationId,
    OrganizationId,
    RecordId,
    RunId,
    WorkflowDefinitionId,
)
from app.models.runs import (
    DispatchAttempt,
    DispatchAttemptStatus,
    RunRecord,
    RunStatus,
    WorkflowEngineKind,
)

DEFAULT_RUN_SEED_PATH = (
    Path(__file__).resolve().parents[3] / "business" / "seeds" / "runs.json"
)


class InMemoryRunRepository:
    """Lock-protected local run store with compare-and-swap transitions."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._runs: dict[RunId, RunRecord] = {}
        self._record_ids: dict[RecordId, RunId] = {}

    def create(self, record: RunRecord) -> Result[RunRecord, RepositoryError]:
        """Persist a new queued run exactly once."""
        with self._lock:
            if record.run_id in self._runs or record.metadata.record_id in self._record_ids:
                return Result.failure(self._error(ErrorCode.CONFLICT, "Run record already exists."))
            self._runs[record.run_id] = record
            self._record_ids[record.metadata.record_id] = record.run_id
            return Result.success(record)

    def create_queued(self, record: RunRecord) -> Result[RunRecord, RepositoryError]:
        """Persist only a pristine queued run before a service may dispatch it."""
        if record.status is not RunStatus.QUEUED or record.dispatch_attempts:
            return Result.failure(
                self._error(
                    ErrorCode.INVALID_TRANSITION,
                    "New runs must be persisted as queued without dispatch attempts.",
                )
            )
        return self.create(record)

    def get(
        self, organization_id: OrganizationId, record_id: RecordId
    ) -> Result[RunRecord, RepositoryError]:
        """Return one run only when it belongs to the requesting organization."""
        with self._lock:
            run_id = self._record_ids.get(record_id)
            record = self._runs.get(run_id) if run_id is not None else None
            return self._scoped_record(organization_id, record)

    def get_by_run_id(
        self, organization_id: OrganizationId, run_id: RunId
    ) -> Result[RunRecord, RepositoryError]:
        """Return a run by its public run identifier within its organization."""
        with self._lock:
            return self._scoped_record(organization_id, self._runs.get(run_id))

    def transition(
        self, record: RunRecord, transition: OptimisticTransition
    ) -> Result[RunRecord, RepositoryError]:
        """Atomically replace one immutable run only when all version guards match."""
        with self._lock:
            current = self._runs.get(record.run_id)
            if (
                current is None
                or current.metadata.record_id != transition.record_id
                or current.metadata.organization_id != transition.organization_id
                or current.metadata.version != transition.expected_version
                or record.metadata.record_id != transition.record_id
                or record.metadata.organization_id != transition.organization_id
                or record.metadata.version != transition.expected_version + 1
                or record.run_id != current.run_id
            ):
                return Result.failure(
                    self._error(
                        ErrorCode.CONFLICT,
                        "Run record transition conflicts with current state.",
                    )
                )
            self._runs[record.run_id] = record
            return Result.success(record)

    def records(self) -> tuple[RunRecord, ...]:
        """Return immutable local snapshots for deterministic inspection."""
        with self._lock:
            return tuple(self._runs.values())

    def _scoped_record(
        self, organization_id: OrganizationId, record: RunRecord | None
    ) -> Result[RunRecord, RepositoryError]:
        if record is None or record.metadata.organization_id != organization_id:
            return Result.failure(self._error(ErrorCode.NOT_FOUND, "Run record was not found."))
        return Result.success(record)

    @staticmethod
    def _error(code: ErrorCode, message: str) -> ErrorDetail:
        return ErrorDetail(code, message, CorrelationId("run-repository"))


class SeedOnlyJsonRunRepository(InMemoryRunRepository):
    """Load target-local JSON fixtures once; subsequent state is never written to JSON."""

    def __init__(self, seed_path: Path = DEFAULT_RUN_SEED_PATH) -> None:
        super().__init__()
        self.seed_path = seed_path.resolve()
        for record in self._load_seed_records(self.seed_path):
            persisted = self.create(record)
            if not persisted.is_success:
                raise ValueError("Run seed contains duplicate record identities.")

    @classmethod
    def _load_seed_records(cls, seed_path: Path) -> tuple[RunRecord, ...]:
        try:
            loaded: object = json.loads(seed_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise ValueError("Run seed data could not be read.") from error
        root = cls._mapping(loaded, "seed root")
        if root.get("schema_version") != 1:
            raise ValueError("Run seed schema version is unsupported.")
        raw_runs = root.get("runs")
        if not isinstance(raw_runs, list):
            raise ValueError("Run seed must contain a runs array.")
        return tuple(cls._record_from_json(cls._mapping(item, "run")) for item in raw_runs)

    @classmethod
    def _record_from_json(cls, raw: Mapping[str, object]) -> RunRecord:
        metadata = RecordMetadata(
            record_id=RecordId(cls._string(raw, "record_id")),
            organization_id=OrganizationId(cls._string(raw, "organization_id")),
            correlation_id=CorrelationId(cls._string(raw, "correlation_id")),
            schema_version=cls._integer(raw, "schema_version"),
            version=cls._integer(raw, "version"),
            created_at=cls._timestamp(raw, "created_at"),
            updated_at=cls._timestamp(raw, "updated_at"),
        )
        attempts = cls._dispatch_attempts(raw.get("dispatch_attempts", []))
        output_value = raw.get("output")
        output = cls._mapping(output_value, "output") if output_value is not None else None
        return RunRecord(
            metadata=metadata,
            run_id=RunId(cls._string(raw, "run_id")),
            workflow_definition_id=WorkflowDefinitionId(cls._string(raw, "workflow_definition_id")),
            workflow_definition_version=cls._string(raw, "workflow_definition_version"),
            workflow_definition_digest=cls._string(raw, "workflow_definition_digest"),
            engine=WorkflowEngineKind(cls._string(raw, "engine")),
            status=RunStatus(cls._string(raw, "status")),
            created_for_dispatch_at=cls._timestamp(raw, "created_for_dispatch_at"),
            dispatch_attempts=attempts,
            output=output,
            graph_id=cls._optional_string(raw, "graph_id"),
            graph_thread_id=cls._optional_string(raw, "graph_thread_id"),
        )

    @classmethod
    def _dispatch_attempts(cls, value: object) -> tuple[DispatchAttempt, ...]:
        if not isinstance(value, list):
            raise ValueError("Run seed dispatch attempts must be an array.")
        attempts: list[DispatchAttempt] = []
        for item in value:
            raw = cls._mapping(item, "dispatch attempt")
            attempts.append(
                DispatchAttempt(
                    idempotency_key=cls._string(raw, "idempotency_key"),
                    requested_at=cls._timestamp(raw, "requested_at"),
                    status=DispatchAttemptStatus(cls._string(raw, "status")),
                    failure_code=cls._optional_string(raw, "failure_code"),
                )
            )
        if len({attempt.idempotency_key for attempt in attempts}) != len(attempts):
            raise ValueError("Run seed dispatch attempt keys must be unique.")
        return tuple(attempts)

    @staticmethod
    def _mapping(value: object, label: str) -> Mapping[str, object]:
        if not isinstance(value, Mapping) or not all(isinstance(key, str) for key in value):
            raise ValueError(f"Run seed {label} must be an object.")
        return {key: item for key, item in value.items() if isinstance(key, str)}

    @staticmethod
    def _string(raw: Mapping[str, object], field: str) -> str:
        value = raw.get(field)
        if not isinstance(value, str) or not value:
            raise ValueError(f"Run seed {field} must be a non-empty string.")
        return value

    @classmethod
    def _optional_string(cls, raw: Mapping[str, object], field: str) -> str | None:
        value = raw.get(field)
        if value is None:
            return None
        if not isinstance(value, str) or not value:
            raise ValueError(f"Run seed {field} must be a non-empty string or null.")
        return value

    @staticmethod
    def _integer(raw: Mapping[str, object], field: str) -> int:
        value = raw.get(field)
        if not isinstance(value, int) or isinstance(value, bool) or value < 1:
            raise ValueError(f"Run seed {field} must be a positive integer.")
        return value

    @classmethod
    def _timestamp(cls, raw: Mapping[str, object], field: str) -> datetime:
        value = cls._string(raw, field)
        try:
            timestamp = datetime.fromisoformat(value)
        except ValueError as error:
            raise ValueError(f"Run seed {field} must be an ISO timestamp.") from error
        if timestamp.tzinfo is None:
            raise ValueError(f"Run seed {field} must include a timezone.")
        return timestamp
