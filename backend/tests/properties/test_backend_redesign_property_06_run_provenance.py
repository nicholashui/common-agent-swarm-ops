"""Property checks for immutable pre-dispatch run provenance."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime
from typing import cast

from hypothesis import given, settings, strategies as st

from app.models.common import RecordMetadata
from app.models.control_plane import (
    AgentVersionId,
    CommonAgentVersion,
    CommonPatternVersion,
    CommonPatternVersionId,
    ContractStatus,
    GraphRevision,
    GraphRevisionId,
    RunProvenance,
    RunProvenanceId,
    SwarmInstance,
    SwarmInstanceId,
)
from app.models.identifiers import CorrelationId, OrganizationId, RecordId
from app.registry.service import RegistryService
from app.repositories.control_plane import ControlPlaneUnitOfWork, InMemoryControlPlaneDatabase
from app.repositories.graph_repository import InMemoryGraphRepository
from app.workflows import GraphService, RegisteredReferences

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_ORGANIZATION = OrganizationId("property-6-organization")
_CORRELATION = CorrelationId("property-6-correlation")
_SAFE_VALUES = st.text(alphabet="abcdefghijklmnopqrstuvwxyz0123456789", min_size=1, max_size=12)


def _metadata(record_id: str, version: int = 1) -> RecordMetadata:
    return RecordMetadata(
        record_id=RecordId(record_id),
        organization_id=_ORGANIZATION,
        correlation_id=_CORRELATION,
        schema_version=1,
        version=version,
        created_at=_NOW,
        updated_at=_NOW,
    )


def _agent(value: str) -> CommonAgentVersion:
    return CommonAgentVersion(
        metadata=_metadata(f"agent-record-{value}"),
        agent_version_id=AgentVersionId(f"agent-{value}"),
        status=ContractStatus.PUBLISHED,
        canonical_identity=f"planner-{value}",
        category="planning",
        responsibilities=(f"plan-{value}",),
        boundaries=("no-production",),
        escalation_targets=("operator",),
        approval_authority=("approval-1",),
        runtime_policy={"profile": value},
        tool_policy={"allow": ("crm.lookup",)},
        quality_rubric={"minimum": 0.8},
        critique_relationships=(),
        knowledge_bindings=(),
        input_schema={"type": "object"},
        output_schema={"type": "object"},
        provenance_policy={"source": value},
        content_digest=f"sha256:agent-{value}",
    )


def _pattern(value: str) -> CommonPatternVersion:
    return CommonPatternVersion(
        metadata=_metadata(f"pattern-record-{value}"),
        pattern_version_id=CommonPatternVersionId(f"pattern-{value}"),
        status=ContractStatus.PUBLISHED,
        graph_template={"nodes": ("plan",), "edges": ()},
        slot_constraints={"required": ("plan",)},
        compatibility_rules={"schema": value},
        risk_requirements={"level": "low"},
        verification_requirements={"verification_level": "strict"},
        provenance={"source": value},
        content_digest=f"sha256:pattern-{value}",
    )


def _revision(
    value: str,
    revision_number: int,
    agent: CommonAgentVersion,
    pattern: CommonPatternVersion,
    workflow_version: str,
) -> GraphRevision:
    return GraphRevision(
        metadata=_metadata(f"graph-record-{value}-{revision_number}"),
        graph_revision_id=GraphRevisionId(f"graph-{value}-{revision_number}"),
        swarm_instance_id=SwarmInstanceId("property-6-swarm"),
        revision=revision_number,
        nodes=(
            {
                "id": "plan",
                "agent_version_id": str(agent.agent_version_id),
                "tool_ids": ["crm.lookup"],
                "memory_reads": ["organization"],
                "memory_writes": ["organization"],
            },
        ),
        edges=(),
        layout={"plan": {"x": revision_number, "y": 0}},
        version_pins={
            "agent_version_ids": [str(agent.agent_version_id)],
            "pattern_version_ids": [str(pattern.pattern_version_id)],
        },
        policies={
            "workflow_definition": {
                "id": f"ops.compose.{value}",
                "version": workflow_version,
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
                "rollback": {"plan_id": "compensate.crm", "compensation_step_ids": ["plan"]},
                "pattern": "pipeline",
                "entry_node": "plan",
                "terminal_node_ids": ["plan"],
            },
            "verification": {"verification_level": "strict"},
        },
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


def _unit_of_work_factory(database: InMemoryControlPlaneDatabase) -> ControlPlaneUnitOfWork:
    return cast(ControlPlaneUnitOfWork, database.unit_of_work())


# Feature: backend-redesign, Property 6: Run provenance is a pre-dispatch immutable snapshot.
# **Validates: Requirements 3.7, 3.8**
@settings(max_examples=100)
@given(
    initial_value=_SAFE_VALUES,
    later_value=_SAFE_VALUES,
    retained_run_count=st.integers(min_value=1, max_value=3),
)
def test_property_6_run_provenance_is_a_pre_dispatch_immutable_snapshot(
    initial_value: str, later_value: str, retained_run_count: int
) -> None:
    """Later graph and common-contract edits cannot rewrite any retained run snapshot."""
    database = InMemoryControlPlaneDatabase()
    registry = RegistryService(lambda: _unit_of_work_factory(database))
    graph_service = GraphService(
        lambda: _unit_of_work_factory(database),
        InMemoryGraphRepository(),
        _references(),
        clock=lambda: _NOW,
    )
    published_agent = _agent(initial_value)
    published_pattern = _pattern(initial_value)
    assert registry.publish_agent(_ORGANIZATION, published_agent).is_success
    assert registry.publish_pattern(_ORGANIZATION, published_pattern).is_success

    instance = SwarmInstance(
        metadata=_metadata("swarm-record"),
        swarm_instance_id=SwarmInstanceId("property-6-swarm"),
    )
    initial_revision = _revision(initial_value, 1, published_agent, published_pattern, "1.0.0")
    assert graph_service.create_revision(_ORGANIZATION, instance, initial_revision, 0).is_success
    validated = graph_service.validate_revision(_ORGANIZATION, initial_revision.graph_revision_id)
    assert validated.is_success and validated.value is not None
    initial_report = validated.value
    assert initial_report.eligible_for_run
    assert initial_report.workflow_definition is not None
    assert initial_report.workflow_definition_version is not None

    snapshots: list[RunProvenance] = []
    dispatched_provenance_ids: list[RunProvenanceId] = []
    for run_number in range(retained_run_count):
        snapshot = RunProvenance(
            metadata=_metadata(f"run-record-{initial_value}-{run_number}"),
            run_provenance_id=RunProvenanceId(f"run-{initial_value}-{run_number}"),
            graph_revision_id=initial_report.graph_revision_id,
            workflow_definition=initial_report.workflow_definition,
            workflow_definition_version=initial_report.workflow_definition_version,
            agent_version_ids=initial_report.agent_version_ids,
            pattern_version_ids=initial_report.pattern_version_ids,
        )
        with database.unit_of_work() as unit_of_work:
            stored_before_dispatch = unit_of_work.provenance.append(snapshot)
            assert stored_before_dispatch.is_success
            retained = unit_of_work.provenance.get(_ORGANIZATION, snapshot.run_provenance_id)
            assert retained.is_success and retained.value == snapshot
        snapshots.append(snapshot)
        dispatched_provenance_ids.append(snapshot.run_provenance_id)

    agent_draft = replace(
        published_agent,
        metadata=_metadata(f"agent-draft-{later_value}"),
        agent_version_id=AgentVersionId(f"agent-draft-{later_value}"),
        status=ContractStatus.DRAFT,
        content_digest=f"sha256:agent-draft-{later_value}",
    )
    edited_agent_draft = replace(
        agent_draft,
        metadata=replace(agent_draft.metadata, version=2),
        responsibilities=(f"edited-plan-{later_value}",),
        runtime_policy={"profile": later_value},
    )
    pattern_draft = replace(
        published_pattern,
        metadata=_metadata(f"pattern-draft-{later_value}"),
        pattern_version_id=CommonPatternVersionId(f"pattern-draft-{later_value}"),
        status=ContractStatus.DRAFT,
        content_digest=f"sha256:pattern-draft-{later_value}",
    )
    edited_pattern_draft = replace(
        pattern_draft,
        metadata=replace(pattern_draft.metadata, version=2),
        compatibility_rules={"schema": later_value},
    )
    assert registry.create_agent_draft(
        _ORGANIZATION, published_agent.agent_version_id, agent_draft
    ).is_success
    assert registry.update_agent_draft(_ORGANIZATION, edited_agent_draft).is_success
    assert registry.create_pattern_draft(
        _ORGANIZATION, published_pattern.pattern_version_id, pattern_draft
    ).is_success
    assert registry.update_pattern_draft(_ORGANIZATION, edited_pattern_draft).is_success

    later_revision = _revision(later_value, 2, published_agent, published_pattern, "2.0.0")
    assert graph_service.create_revision(_ORGANIZATION, instance, later_revision, 1).is_success
    later_validation = graph_service.validate_revision(
        _ORGANIZATION, later_revision.graph_revision_id
    )
    assert later_validation.is_success and later_validation.value is not None
    assert later_validation.value.eligible_for_run

    with database.unit_of_work() as unit_of_work:
        retained_snapshots = [
            unit_of_work.provenance.get(_ORGANIZATION, snapshot.run_provenance_id)
            for snapshot in snapshots
        ]
    assert all(
        result.is_success and result.value == snapshot
        for result, snapshot in zip(retained_snapshots, snapshots, strict=True)
    )
    assert all(
        snapshot.graph_revision_id == initial_report.graph_revision_id
        and snapshot.workflow_definition == initial_report.workflow_definition
        and snapshot.workflow_definition_version == initial_report.workflow_definition_version
        and snapshot.agent_version_ids == initial_report.agent_version_ids
        and snapshot.pattern_version_ids == initial_report.pattern_version_ids
        for snapshot in snapshots
    )
    assert dispatched_provenance_ids == [snapshot.run_provenance_id for snapshot in snapshots]
