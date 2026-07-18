"""Focused local checks for durable checkpoint scoping and fail-closed recovery."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime

from app.models.common import RecordMetadata
from app.models.contracts import ErrorCode, ErrorDetail, Result
from app.models.identifiers import (
    CorrelationId,
    OrganizationId,
    RecordId,
    RunId,
    WorkflowDefinitionId,
)
from app.models.runs import RunRecord, RunStatus, WorkflowEngineKind
from app.repositories.postgres_checkpoint import PostgresCheckpointRepository
from app.runs.checkpoints import CheckpointRecord, CheckpointResumeService, checkpoint_thread_id

NOW = datetime(2025, 1, 1, tzinfo=UTC)
ORG_ID = OrganizationId("org-checkpoints")
FOREIGN_ORG_ID = OrganizationId("org-checkpoints-foreign")
CORRELATION_ID = CorrelationId("corr-checkpoints")
RUN_ID = RunId("run-checkpoints")


def _run(organization_id: OrganizationId = ORG_ID) -> RunRecord:
    """Create one already initialized graph run for checkpoint service examples."""
    return RunRecord(
        metadata=RecordMetadata(
            record_id=RecordId("record-checkpoints"),
            organization_id=organization_id,
            correlation_id=CORRELATION_ID,
            schema_version=1,
            version=2,
            created_at=NOW,
            updated_at=NOW,
        ),
        run_id=RUN_ID,
        workflow_definition_id=WorkflowDefinitionId("ops.checkpoints"),
        workflow_definition_version="1.0.0",
        workflow_definition_digest="a" * 64,
        engine=WorkflowEngineKind.GRAPH,
        status=RunStatus.WAITING_FOR_APPROVAL,
        created_for_dispatch_at=NOW,
        graph_id="ops-checkpoints",
        graph_thread_id=checkpoint_thread_id(organization_id, RUN_ID),
    )


@dataclass
class _RecordingCheckpointRepository:
    """Deterministic repository fake exposing save and lookup decisions."""

    saved: list[CheckpointRecord] = field(default_factory=list)
    resume_result: Result[CheckpointRecord, ErrorDetail] | None = None
    lookup_calls: int = 0

    def save(self, checkpoint: CheckpointRecord) -> Result[CheckpointRecord, ErrorDetail]:
        """Retain the supplied checkpoint locally."""
        self.saved.append(checkpoint)
        return Result.success(checkpoint)

    def get_for_resume(
        self, _organization_id: OrganizationId, _run_id: RunId
    ) -> Result[CheckpointRecord, ErrorDetail]:
        """Return the configured local result while exposing lookup count."""
        self.lookup_calls += 1
        if self.resume_result is not None:
            return self.resume_result
        return Result.failure(ErrorDetail(ErrorCode.NOT_FOUND, "missing", CORRELATION_ID))


@dataclass
class _UnavailableCheckpointRepository(_RecordingCheckpointRepository):
    """Repository fake that represents an unavailable configured durable store."""

    def save(self, _checkpoint: CheckpointRecord) -> Result[CheckpointRecord, ErrorDetail]:
        """Fail as an unavailable durable repository without storing a fallback."""
        return Result.failure(
            ErrorDetail(ErrorCode.REPOSITORY_UNAVAILABLE, "unavailable", CORRELATION_ID)
        )


def _checkpoint(organization_id: OrganizationId = ORG_ID) -> CheckpointRecord:
    """Create a valid checkpoint representative of an initialized graph run."""
    return CheckpointRecord(
        metadata=RecordMetadata(
            record_id=RecordId("checkpoint-record"),
            organization_id=organization_id,
            correlation_id=CORRELATION_ID,
            schema_version=1,
            version=1,
            created_at=NOW,
            updated_at=NOW,
        ),
        run_id=RUN_ID,
        thread_id=checkpoint_thread_id(organization_id, RUN_ID),
        namespace="production",
        sequence=1,
        checkpoint={"route": "review", "tool_effects": []},
        snapshot_reference="snapshot-checkpoints",
    )


def test_checkpoint_service_persists_the_exact_organization_run_thread_id() -> None:
    """A graph checkpoint uses the required tenant-scoped thread ID before persistence."""
    repository = _RecordingCheckpointRepository()

    result = CheckpointResumeService(repository, clock=lambda: NOW).persist(
        _run(),
        "production",
        1,
        {"route": "review"},
        "snapshot-checkpoints",
        CORRELATION_ID,
    )

    assert result.is_success and result.value is not None
    assert result.value.thread_id == "org-checkpoints:run-checkpoints"
    assert repository.saved == [result.value]


def test_same_organization_resume_returns_the_durable_checkpoint() -> None:
    """A matching organization resumes only from its own validated checkpoint."""
    checkpoint = _checkpoint()
    repository = _RecordingCheckpointRepository(resume_result=Result.success(checkpoint))

    result = CheckpointResumeService(repository).resume(ORG_ID, _run(), CORRELATION_ID)

    assert result.is_success and result.value is not None
    assert result.value.run == _run()
    assert result.value.checkpoint == checkpoint
    assert repository.lookup_calls == 1


def test_cross_organization_resume_is_denied_before_checkpoint_lookup() -> None:
    """A foreign requester cannot use lookup timing or existence to probe checkpoints."""
    repository = _RecordingCheckpointRepository()

    result = CheckpointResumeService(repository).resume(FOREIGN_ORG_ID, _run(), CORRELATION_ID)

    assert not result.is_success and result.error is not None
    assert result.error.code is ErrorCode.AUTHORIZATION_DENIED
    assert repository.lookup_calls == 0


def test_unavailable_durable_persistence_has_no_local_checkpoint_fallback() -> None:
    """A configured durable-store outage fails closed before checkpoint state can proceed."""
    repository = _UnavailableCheckpointRepository()

    result = CheckpointResumeService(repository, clock=lambda: NOW).persist(
        _run(),
        "production",
        1,
        {"route": "review"},
        "snapshot-checkpoints",
        CORRELATION_ID,
    )

    assert not result.is_success and result.error is not None
    assert result.error.code is ErrorCode.REPOSITORY_UNAVAILABLE
    assert repository.saved == []


def test_unavailable_durable_resume_has_no_local_checkpoint_fallback() -> None:
    """A configured durable-store read outage denies resume without a fallback checkpoint."""
    repository = _RecordingCheckpointRepository(
        resume_result=Result.failure(
            ErrorDetail(ErrorCode.REPOSITORY_UNAVAILABLE, "unavailable", CORRELATION_ID)
        )
    )

    result = CheckpointResumeService(repository).resume(ORG_ID, _run(), CORRELATION_ID)

    assert not result.is_success and result.error is not None
    assert result.error.code is ErrorCode.REPOSITORY_UNAVAILABLE
    assert repository.lookup_calls == 1


@dataclass
class _Cursor:
    """Minimal parameter-recording cursor for repository unit checks."""

    row: tuple[object, ...] | None = None
    statements: list[tuple[str, tuple[object, ...]]] = field(default_factory=list)
    closed: bool = False

    def execute(self, operation: str, parameters: Sequence[object] = ()) -> None:
        """Record one parameterized database operation."""
        self.statements.append((operation, tuple(parameters)))

    def fetchone(self) -> tuple[object, ...] | None:
        """Return the configured local row."""
        return self.row

    def close(self) -> None:
        """Record release of the fake cursor."""
        self.closed = True


@dataclass
class _Connection:
    """Minimal connection fake that never reaches a database server."""

    cursor_instance: _Cursor
    committed: bool = False
    closed: bool = False

    def cursor(self) -> _Cursor:
        """Return the fixed local cursor."""
        return self.cursor_instance

    def commit(self) -> None:
        """Record successful transaction completion."""
        self.committed = True

    def rollback(self) -> None:
        """Provide the rollback seam required by the repository."""

    def close(self) -> None:
        """Record release of the fake connection."""
        self.closed = True


def test_postgres_repository_scopes_resume_lookup_to_the_exact_thread_identity() -> None:
    """The configured repository asks Postgres for exactly one tenant-run thread."""
    checkpoint = _checkpoint()
    metadata = checkpoint.metadata
    cursor = _Cursor(
        row=(
            str(metadata.record_id),
            str(metadata.organization_id),
            str(checkpoint.run_id),
            checkpoint.thread_id,
            checkpoint.namespace,
            checkpoint.sequence,
            dict(checkpoint.checkpoint),
            checkpoint.snapshot_reference,
            str(metadata.correlation_id),
            metadata.schema_version,
            metadata.version,
            metadata.created_at,
            metadata.updated_at,
        )
    )
    connection = _Connection(cursor)

    result = PostgresCheckpointRepository(lambda: connection).get_for_resume(ORG_ID, RUN_ID)

    assert result.is_success and result.value is not None
    assert result.value.thread_id == checkpoint.thread_id
    statement, parameters = cursor.statements[0]
    assert "thread_id = %s" in statement
    assert parameters == ("org-checkpoints", "run-checkpoints", "org-checkpoints:run-checkpoints")
    assert cursor.closed and connection.closed


def test_postgres_repository_rejects_ambiguous_thread_identifiers_before_connecting() -> None:
    """Malformed identifiers cannot cause a durable checkpoint lookup."""
    connection_calls = 0

    def connection_factory() -> _Connection:
        nonlocal connection_calls
        connection_calls += 1
        return _Connection(_Cursor())

    result = PostgresCheckpointRepository(connection_factory).get_for_resume(
        OrganizationId("org:invalid"), RUN_ID
    )

    assert not result.is_success and result.error is not None
    assert result.error.code is ErrorCode.VALIDATION_FAILED
    assert connection_calls == 0


def test_postgres_repository_uses_parameterized_insert_without_a_database_connection() -> None:
    """The repository binds checkpoint data rather than interpolating it into Postgres SQL."""
    connection = _Connection(_Cursor())
    repository = PostgresCheckpointRepository(lambda: connection)

    result = repository.save(_checkpoint())

    assert result.is_success
    statement, parameters = connection.cursor_instance.statements[0]
    assert "VALUES (%s, %s, %s" in statement
    assert "org-checkpoints" not in statement
    expected_scope = (
        "org-checkpoints",
        "run-checkpoints",
        "org-checkpoints:run-checkpoints",
    )
    assert parameters[1:4] == expected_scope
    assert connection.committed and connection.cursor_instance.closed and connection.closed
