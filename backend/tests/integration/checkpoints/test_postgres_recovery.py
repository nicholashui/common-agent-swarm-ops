"""Isolated local integration checks for configured Postgres checkpoint recovery."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from app.models.common import RecordMetadata
from app.models.contracts import ErrorCode
from app.models.identifiers import (
    CorrelationId,
    OrganizationId,
    RecordId,
    RunId,
    WorkflowDefinitionId,
)
from app.models.runs import RunRecord, RunStatus, WorkflowEngineKind
from app.repositories.postgres_checkpoint import PostgresCheckpointRepository
from app.runs.checkpoints import CheckpointResumeService, checkpoint_thread_id
from tests.integration.checkpoints.local_postgres import IsolatedLocalPostgres

NOW = datetime(2025, 1, 1, tzinfo=UTC)
PRIMARY_ORGANIZATION_ID = OrganizationId("org-checkpoint-primary")
FOREIGN_ORGANIZATION_ID = OrganizationId("org-checkpoint-foreign")
RUN_ID = RunId("run-checkpoint-recovery")
CORRELATION_ID = CorrelationId("corr-checkpoint-recovery")


@pytest.fixture
def local_postgres() -> IsolatedLocalPostgres:
    """Provide a new pinned, in-process fixture with no database endpoint."""
    return IsolatedLocalPostgres()


def _run(organization_id: OrganizationId = PRIMARY_ORGANIZATION_ID) -> RunRecord:
    """Build a waiting graph run with a tenant-scoped durable thread identity."""
    return RunRecord(
        metadata=RecordMetadata(
            record_id=RecordId(f"record-{organization_id}"),
            organization_id=organization_id,
            correlation_id=CORRELATION_ID,
            schema_version=1,
            version=2,
            created_at=NOW,
            updated_at=NOW,
        ),
        run_id=RUN_ID,
        workflow_definition_id=WorkflowDefinitionId("ops.checkpoint-recovery"),
        workflow_definition_version="1.0.0",
        workflow_definition_digest="a" * 64,
        engine=WorkflowEngineKind.GRAPH,
        status=RunStatus.WAITING_FOR_APPROVAL,
        created_for_dispatch_at=NOW,
        graph_id="ops-checkpoint-recovery",
        graph_thread_id=checkpoint_thread_id(organization_id, RUN_ID),
    )


def _service(
    local_postgres: IsolatedLocalPostgres, record_id: str
) -> CheckpointResumeService:
    """Create one process-local service around a fresh configured repository instance."""
    repository = PostgresCheckpointRepository(local_postgres.connection_factory)

    def record_id_factory() -> RecordId:
        """Return the fixed record identity allocated to this test service."""
        return RecordId(record_id)

    return CheckpointResumeService(
        repository,
        clock=lambda: NOW,
        record_id_factory=record_id_factory,
    )


def test_restart_recovers_the_latest_durable_checkpoint(
    local_postgres: IsolatedLocalPostgres,
) -> None:
    """A new repository/service process resumes the newest committed checkpoint."""
    initial_process = _service(local_postgres, "checkpoint-initial")
    persisted = initial_process.persist(
        _run(),
        "production",
        1,
        {"route": "review", "tool_effects": ["effect-one"]},
        "snapshot-one",
        CORRELATION_ID,
    )
    assert persisted.is_success

    restarting_process = _service(local_postgres, "checkpoint-restarted")
    latest = restarting_process.persist(
        _run(),
        "production",
        2,
        {"route": "approve", "tool_effects": ["effect-one", "effect-two"]},
        "snapshot-two",
        CORRELATION_ID,
    )
    assert latest.is_success

    recovered = _service(local_postgres, "checkpoint-after-restart").resume(
        PRIMARY_ORGANIZATION_ID,
        _run(),
        CORRELATION_ID,
    )

    assert recovered.is_success and recovered.value is not None
    assert recovered.value.checkpoint.sequence == 2
    assert dict(recovered.value.checkpoint.checkpoint) == {
        "route": "approve",
        "tool_effects": ["effect-one", "effect-two"],
    }
    assert local_postgres.connections_opened == 3
    assert local_postgres.lookup_calls == 1


def test_same_organization_resume_uses_only_its_own_checkpoint(
    local_postgres: IsolatedLocalPostgres,
) -> None:
    """Same-named runs in different organizations cannot supply each other's state."""
    primary_checkpoint = _service(local_postgres, "checkpoint-primary").persist(
        _run(PRIMARY_ORGANIZATION_ID),
        "production",
        1,
        {"route": "primary"},
        "snapshot-primary",
        CORRELATION_ID,
    )
    foreign_checkpoint = _service(local_postgres, "checkpoint-foreign").persist(
        _run(FOREIGN_ORGANIZATION_ID),
        "production",
        7,
        {"route": "foreign"},
        "snapshot-foreign",
        CORRELATION_ID,
    )
    assert primary_checkpoint.is_success and foreign_checkpoint.is_success

    resumed = _service(local_postgres, "checkpoint-resume").resume(
        PRIMARY_ORGANIZATION_ID,
        _run(PRIMARY_ORGANIZATION_ID),
        CORRELATION_ID,
    )

    assert resumed.is_success and resumed.value is not None
    assert resumed.value.checkpoint.thread_id == "org-checkpoint-primary:run-checkpoint-recovery"
    assert dict(resumed.value.checkpoint.checkpoint) == {"route": "primary"}
    assert local_postgres.lookup_calls == 1


def test_cross_organization_resume_is_denied_before_local_postgres_lookup(
    local_postgres: IsolatedLocalPostgres,
) -> None:
    """A foreign requester is denied without opening a Postgres connection or lookup."""
    denied = _service(local_postgres, "checkpoint-denied").resume(
        FOREIGN_ORGANIZATION_ID,
        _run(PRIMARY_ORGANIZATION_ID),
        CORRELATION_ID,
    )

    assert not denied.is_success and denied.error is not None
    assert denied.error.code is ErrorCode.AUTHORIZATION_DENIED
    assert local_postgres.connections_opened == 0
    assert local_postgres.lookup_calls == 0


def test_postgres_outage_blocks_persistence_and_resume_without_a_fallback(
    local_postgres: IsolatedLocalPostgres,
) -> None:
    """Configured durable-store outages fail closed for writes and post-restart reads."""
    durable_service = _service(local_postgres, "checkpoint-before-outage")
    persisted = durable_service.persist(
        _run(),
        "production",
        1,
        {"route": "durable"},
        "snapshot-durable",
        CORRELATION_ID,
    )
    assert persisted.is_success
    assert len(local_postgres.rows) == 1

    local_postgres.available = False
    unavailable_write = _service(local_postgres, "checkpoint-during-outage").persist(
        _run(),
        "production",
        2,
        {"route": "must-not-fallback"},
        "snapshot-unavailable",
        CORRELATION_ID,
    )
    unavailable_resume = _service(local_postgres, "checkpoint-resume-outage").resume(
        PRIMARY_ORGANIZATION_ID,
        _run(),
        CORRELATION_ID,
    )

    assert not unavailable_write.is_success and unavailable_write.error is not None
    assert unavailable_write.error.code is ErrorCode.REPOSITORY_UNAVAILABLE
    assert not unavailable_resume.is_success and unavailable_resume.error is not None
    assert unavailable_resume.error.code is ErrorCode.REPOSITORY_UNAVAILABLE
    assert len(local_postgres.rows) == 1
    assert local_postgres.lookup_calls == 0
