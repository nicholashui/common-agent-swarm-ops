"""Focused unit tests for organization-owned graph revision validation."""

from __future__ import annotations

from datetime import UTC, datetime

from app.models.common import RecordMetadata
from app.models.control_plane import (
    AgentVersionId,
    CommonAgentVersion,
    CommonPatternVersion,
    CommonPatternVersionId,
    ContractStatus,
    GraphRevision,
    GraphRevisionId,
    GraphValidationCategory,
    SwarmInstance,
    SwarmInstanceId,
)
from app.models.identifiers import CorrelationId, OrganizationId, RecordId
from app.repositories.control_plane import ControlPlaneUnitOfWork, InMemoryControlPlaneDatabase
from app.repositories.graph_repository import InMemoryGraphRepository
from app.workflows import GraphService, RegisteredReferences

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_ORGANIZATION = OrganizationId("organization-a")


def _metadata(record_id: str) -> RecordMetadata:
    return RecordMetadata(
        record_id=RecordId(record_id),
        organization_id=_ORGANIZATION,
        correlation_id=CorrelationId("correlation-1"),
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
        authorization_ids=frozenset({"approval-123"}),
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
        approval_authority=("approval-123",),
        runtime_policy={},
        tool_policy={"allow": ["crm.lookup"]},
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


def _revision(revision: int = 1, tool_id: str = "crm.lookup") -> GraphRevision:
    return GraphRevision(
        metadata=_metadata(f"revision-record-{revision}"),
        graph_revision_id=GraphRevisionId(f"graph-revision-{revision}"),
        swarm_instance_id=SwarmInstanceId("swarm-1"),
        revision=revision,
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
        version_pins={"agent_version_ids": ["agent-v1"], "pattern_version_ids": ["pattern-v1"]},
        policies={
            "workflow_definition": {
                "id": "ops.compose",
                "version": "1.0.0",
                "owner_id": "ops.owner",
                "authorization_id": "approval-123",
                "engine": "graph",
                "execution_budget": {
                    "max_node_visits": 1,
                    "max_handoffs": 0,
                    "max_wall_clock_seconds": 30,
                    "max_tool_requests": 1,
                },
                "memory": {"reads": ["organization"], "writes": ["organization"]},
                "risk_gate_ids": ["low-risk"],
                "rollback": {"plan_id": "compensate.crm", "compensation_step_ids": ["plan"]},
                "pattern": "pipeline",
                "entry_node": "plan",
                "terminal_node_ids": ["plan"],
            },
            "verification": {"verification_level": "strict"},
        },
    )


def _service() -> tuple[GraphService, InMemoryGraphRepository]:
    database = InMemoryControlPlaneDatabase()
    with database.unit_of_work() as unit_of_work:
        assert unit_of_work.common_contracts.append_agent_version(_agent()).is_success
        assert unit_of_work.common_contracts.append_pattern_version(_pattern()).is_success
    repository = InMemoryGraphRepository()

    def unit_of_work_factory() -> ControlPlaneUnitOfWork:
        return database.unit_of_work()

    return GraphService(
        unit_of_work_factory, repository, _references(), clock=lambda: _NOW
    ), repository


def test_fully_validated_revision_persists_library_workflow_and_is_eligible() -> None:
    """Only complete category success retains a versioned runnable library definition."""
    service, _ = _service()
    instance = SwarmInstance(
        metadata=_metadata("instance-record"), swarm_instance_id=SwarmInstanceId("swarm-1")
    )
    created = service.create_revision(_ORGANIZATION, instance, _revision(), expected_revision=0)

    assert created.is_success
    validated = service.validate_revision(_ORGANIZATION, GraphRevisionId("graph-revision-1"))

    assert validated.is_success and validated.value is not None
    report = validated.value
    assert report.eligible_for_run
    assert all(result.passed for result in report.categories)
    assert report.workflow_definition is not None
    workflow_nodes = report.workflow_definition["nodes"]
    assert isinstance(workflow_nodes, tuple)
    assert workflow_nodes[0] == {
        "id": "plan",
        "tool_ids": ("crm.lookup",),
        "memory_reads": ("organization",),
        "memory_writes": ("organization",),
        "agent_id": "ops.planner",
    }
    assert report.workflow_definition_version == "1.0.0"


def test_validation_persists_field_safe_failure_and_leaves_revision_ineligible() -> None:
    """Rejected values produce complete, retained reports without echoing the submitted value."""
    service, repository = _service()
    instance = SwarmInstance(
        metadata=_metadata("instance-record"), swarm_instance_id=SwarmInstanceId("swarm-1")
    )
    secret_tool_id = "crm.write?token=secret-tool-token"
    assert service.create_revision(
        _ORGANIZATION, instance, _revision(tool_id=secret_tool_id), 0
    ).is_success

    result = service.validate_revision(_ORGANIZATION, GraphRevisionId("graph-revision-1"))

    assert result.is_success and result.value is not None
    assert tuple(item.category for item in result.value.categories) == tuple(
        GraphValidationCategory
    )
    assert not result.value.eligible_for_run
    assert result.value.workflow_definition is None
    assert result.value.workflow_definition_version is None
    tool_result = next(
        item
        for item in result.value.categories
        if item.category is GraphValidationCategory.TOOL_POLICY
    )
    assert not tool_result.passed
    assert any(field.name == "nodes[0].tool_ids" for field in tool_result.fields)
    assert all(
        secret_tool_id not in field.name and secret_tool_id not in field.reason
        for category in result.value.categories
        for field in category.fields
    )
    latest = repository.latest_validation(_ORGANIZATION, GraphRevisionId("graph-revision-1"))
    assert latest.is_success and latest.value == result.value


def test_custom_agent_node_accepts_either_fork_origin_or_custom_reason() -> None:
    """A custom node is accepted when either required provenance justification is supplied."""
    for field, value in (
        ("fork_origin", "published-agent-origin"),
        ("custom_reason", "specialized organization workflow"),
    ):
        service, repository = _service()
        instance = SwarmInstance(
            metadata=_metadata(f"instance-record-{field}"),
            swarm_instance_id=SwarmInstanceId("swarm-1"),
        )
        revision = _revision()
        node = {**revision.nodes[0], "node_type": "custom_agent", field: value}
        custom_revision = GraphRevision(
            metadata=revision.metadata,
            graph_revision_id=revision.graph_revision_id,
            swarm_instance_id=revision.swarm_instance_id,
            revision=revision.revision,
            nodes=(node,),
            edges=revision.edges,
            layout=revision.layout,
            version_pins=revision.version_pins,
            policies=revision.policies,
        )

        created = service.create_revision(_ORGANIZATION, instance, custom_revision, 0)

        assert created.is_success and created.value == custom_revision
        retained = repository.get_revision(_ORGANIZATION, custom_revision.graph_revision_id)
        assert retained.is_success and retained.value == custom_revision


def test_custom_agent_node_without_nonblank_origin_or_reason_is_rejected() -> None:
    """Missing or blank custom-node justifications fail safely before a revision is appended."""
    for justification in ({}, {"fork_origin": "   "}, {"custom_reason": "\t"}):
        service, repository = _service()
        instance = SwarmInstance(
            metadata=_metadata("instance-record"), swarm_instance_id=SwarmInstanceId("swarm-1")
        )
        revision = _revision()
        node = {**revision.nodes[0], "node_type": "custom_agent", **justification}
        custom_revision = GraphRevision(
            metadata=revision.metadata,
            graph_revision_id=revision.graph_revision_id,
            swarm_instance_id=revision.swarm_instance_id,
            revision=revision.revision,
            nodes=(node,),
            edges=revision.edges,
            layout=revision.layout,
            version_pins=revision.version_pins,
            policies=revision.policies,
        )

        rejected = service.create_revision(_ORGANIZATION, instance, custom_revision, 0)

        assert not rejected.is_success and rejected.error is not None
        assert rejected.error.code.value == "validation_failed"
        assert rejected.error.fields[0].name == "nodes[0]"
        assert "fork origin or custom reason" in rejected.error.fields[0].reason
        assert not repository.get_revision(
            _ORGANIZATION, custom_revision.graph_revision_id
        ).is_success


def test_stale_expected_revision_returns_conflict_and_preserves_current_revision() -> None:
    """A stale update retains the previous revision and does not append the candidate."""
    service, repository = _service()
    instance = SwarmInstance(
        metadata=_metadata("instance-record"), swarm_instance_id=SwarmInstanceId("swarm-1")
    )
    initial_revision = _revision()
    assert service.create_revision(_ORGANIZATION, instance, initial_revision, 0).is_success
    candidate = _revision(revision=2)

    stale = service.create_revision(_ORGANIZATION, instance, candidate, expected_revision=0)

    assert not stale.is_success and stale.error is not None
    assert stale.error.code.value == "conflict"
    assert stale.error.message == "Swarm revision conflict."
    assert stale.error.correlation_id == candidate.metadata.correlation_id
    assert stale.error.fields == ()
    stored = repository.get_instance(_ORGANIZATION, SwarmInstanceId("swarm-1"))
    assert stored.is_success and stored.value is not None
    assert stored.value.current_revision == initial_revision.revision
    assert stored.value.current_graph_revision_id == initial_revision.graph_revision_id
    assert repository.get_revision(_ORGANIZATION, initial_revision.graph_revision_id).is_success
    assert not repository.get_revision(_ORGANIZATION, candidate.graph_revision_id).is_success
