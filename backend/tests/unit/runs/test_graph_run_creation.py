"""Focused checks for graph-backed run creation and provenance snapshots."""

from __future__ import annotations

from datetime import UTC, datetime

from app.models.common import RecordMetadata
from app.models.contracts import ErrorCode
from app.models.control_plane import (
    AgentVersionId,
    CommonAgentVersion,
    CommonPatternVersion,
    CommonPatternVersionId,
    ContractStatus,
    GraphRevision,
    GraphRevisionId,
    SwarmInstance,
    SwarmInstanceId,
)
from app.models.identifiers import CorrelationId, OrganizationId, RecordId
from app.models.runs import RunRecord
from app.repositories.control_plane import InMemoryControlPlaneDatabase
from app.repositories.graph_repository import InMemoryGraphRepository
from app.repositories.run_repository import InMemoryRunRepository
from app.runs import GraphRunCreationService, RunService
from app.workflows import GraphService, RegisteredReferences

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_ORGANIZATION = OrganizationId("graph-run-organization")
_CORRELATION = CorrelationId("graph-run-correlation")


def _metadata(record_id: str) -> RecordMetadata:
    return RecordMetadata(
        record_id=RecordId(record_id),
        organization_id=_ORGANIZATION,
        correlation_id=_CORRELATION,
        schema_version=1,
        version=1,
        created_at=_NOW,
        updated_at=_NOW,
    )


def _references() -> RegisteredReferences:
    return RegisteredReferences(
        agent_ids=frozenset(),
        tool_ids=frozenset(),
        memory_scope_ids=frozenset({"organization"}),
        risk_gate_ids=frozenset({"low-risk"}),
        rollback_plan_ids=frozenset({"compensate.crm"}),
        authorization_ids=frozenset({"approval-1"}),
    )


def _agent() -> CommonAgentVersion:
    return CommonAgentVersion(
        metadata=_metadata("agent-record"),
        agent_version_id=AgentVersionId("agent-v1"),
        status=ContractStatus.PUBLISHED,
        canonical_identity="ops.planner",
        category="planning",
        responsibilities=("plan",),
        boundaries=("no-production",),
        escalation_targets=("operator",),
        approval_authority=("approval-1",),
        runtime_policy={},
        tool_policy={"allow": ("crm.lookup",)},
        quality_rubric={},
        critique_relationships=(),
        knowledge_bindings=(),
        input_schema={"type": "object"},
        output_schema={"type": "object"},
        provenance_policy={},
        content_digest="sha256:agent-v1",
    )


def _pattern() -> CommonPatternVersion:
    return CommonPatternVersion(
        metadata=_metadata("pattern-record"),
        pattern_version_id=CommonPatternVersionId("pattern-v1"),
        status=ContractStatus.PUBLISHED,
        graph_template={},
        slot_constraints={},
        compatibility_rules={},
        risk_requirements={},
        verification_requirements={"verification_level": "strict"},
        provenance={},
        content_digest="sha256:pattern-v1",
    )


def _revision(tool_id: str = "crm.lookup", revision_number: int = 1) -> GraphRevision:
    return GraphRevision(
        metadata=_metadata(f"graph-record-{revision_number}"),
        graph_revision_id=GraphRevisionId(f"graph-v{revision_number}"),
        swarm_instance_id=SwarmInstanceId("swarm-v1"),
        revision=revision_number,
        nodes=(
            {
                "id": "plan",
                "agent_version_id": "agent-v1",
                "tool_ids": [tool_id],
                "memory_reads": ["organization"],
                "memory_writes": ["organization"],
            },
        ),
        edges=(),
        layout={"plan": {"x": 0, "y": 0}},
        version_pins={
            "agent_version_ids": ["agent-v1"],
            "pattern_version_ids": ["pattern-v1"],
        },
        policies={
            "workflow_definition": {
                "id": "ops.graph-run",
                "version": "1.0.0",
                "owner_id": "ops.owner",
                "authorization_id": "approval-1",
                "engine": "graph",
                "execution_budget": {
                    "max_node_visits": 1,
                    "max_handoffs": 0,
                    "max_wall_clock_seconds": 30,
                    "max_tool_requests": 1,
                },
                "memory": {"reads": ["organization"], "writes": ["organization"]},
                "risk_gate_ids": ["low-risk"],
                "rollback": {
                    "plan_id": "compensate.crm",
                    "compensation_step_ids": ["plan"],
                },
                "pattern": "pipeline",
                "entry_node": "plan",
                "terminal_node_ids": ["plan"],
            },
            "verification": {"verification_level": "strict"},
        },
    )


def _services(
    tool_id: str = "crm.lookup",
) -> tuple[
    InMemoryControlPlaneDatabase,
    GraphService,
    GraphRunCreationService,
    RunService,
    InMemoryRunRepository,
    GraphRevision,
]:
    database = InMemoryControlPlaneDatabase()
    with database.unit_of_work() as unit_of_work:
        assert unit_of_work.common_contracts.append_agent_version(_agent()).is_success
        assert unit_of_work.common_contracts.append_pattern_version(_pattern()).is_success
    graph_service = GraphService(
        database.unit_of_work,
        InMemoryGraphRepository(),
        _references(),
        clock=lambda: _NOW,
    )
    run_repository = InMemoryRunRepository()
    run_service = RunService(run_repository, _references(), clock=lambda: _NOW)
    creation = GraphRunCreationService(
        graph_service,
        run_service,
        database.unit_of_work,
        clock=lambda: _NOW,
    )
    revision = _revision(tool_id)
    instance = SwarmInstance(
        metadata=_metadata("swarm-record"),
        swarm_instance_id=revision.swarm_instance_id,
    )
    assert graph_service.create_revision(_ORGANIZATION, instance, revision, 0).is_success
    return database, graph_service, creation, run_service, run_repository, revision


def test_graph_run_persists_immutable_snapshot_before_dispatch() -> None:
    """A dispatch starter observes the complete retained graph provenance snapshot."""
    database, graph_service, creation, run_service, run_repository, revision = _services()
    validated = graph_service.validate_revision(_ORGANIZATION, revision.graph_revision_id)
    report = validated.value
    assert validated.is_success and report is not None

    created = creation.create_queued_run(_ORGANIZATION, _CORRELATION, revision.graph_revision_id)

    assert created.is_success and created.value is not None
    run = created.value
    provenance_id = run.provenance_id
    assert provenance_id is not None
    with database.unit_of_work() as unit_of_work:
        stored_snapshot = unit_of_work.provenance.get(_ORGANIZATION, provenance_id)
    snapshot = stored_snapshot.value
    assert stored_snapshot.is_success and snapshot is not None
    assert snapshot.graph_revision_id == revision.graph_revision_id
    assert snapshot.workflow_definition == report.workflow_definition
    assert snapshot.workflow_definition_version == "1.0.0"
    assert snapshot.agent_version_ids == (AgentVersionId("agent-v1"),)
    assert snapshot.pattern_version_ids == (CommonPatternVersionId("pattern-v1"),)

    observed_provenance_ids: list[object] = []

    def starter(record: RunRecord) -> None:
        assert record.run_id == run.run_id
        assert record.provenance_id == provenance_id
        with database.unit_of_work() as unit_of_work:
            retained = unit_of_work.provenance.get(_ORGANIZATION, provenance_id)
        assert retained.is_success and retained.value == snapshot
        observed_provenance_ids.append(provenance_id)

    dispatched = run_service.dispatch(
        _ORGANIZATION, run.run_id, "dispatch-key", starter, _CORRELATION
    )

    assert dispatched.is_success
    assert observed_provenance_ids == [provenance_id]
    assert run_repository.records()[0].provenance_id == provenance_id


def test_unvalidated_or_failed_graph_creates_no_run_or_provenance() -> None:
    """Both absent and failed validation outcomes fail before any partial run is created."""
    _, _, creation, _, run_repository, revision = _services()

    unvalidated = creation.create_queued_run(
        _ORGANIZATION, _CORRELATION, revision.graph_revision_id
    )

    assert not unvalidated.is_success and unvalidated.error is not None
    assert unvalidated.error.code is ErrorCode.VALIDATION_FAILED
    assert run_repository.records() == ()

    _, failed_graph_service, failed_creation, _, failed_run_repository, failed_revision = _services(
        "crm.write"
    )
    failed = failed_graph_service.validate_revision(
        _ORGANIZATION, failed_revision.graph_revision_id
    )

    assert failed.is_success and failed.value is not None
    assert not failed.value.eligible_for_run
    rejected = failed_creation.create_queued_run(
        _ORGANIZATION, _CORRELATION, failed_revision.graph_revision_id
    )
    assert not rejected.is_success and rejected.error is not None
    assert rejected.error.code is ErrorCode.VALIDATION_FAILED
    assert failed_run_repository.records() == ()
