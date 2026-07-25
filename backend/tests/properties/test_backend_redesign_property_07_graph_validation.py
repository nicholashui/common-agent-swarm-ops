"""Property checks for graph revision validation and run eligibility."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import cast

from hypothesis import given, settings, strategies as st

from app.models.common import RecordMetadata
from app.models.contracts import ErrorCode, ErrorDetail, Result
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
from app.models.runs import RunRecord
from app.repositories.control_plane import ControlPlaneUnitOfWork, InMemoryControlPlaneDatabase
from app.repositories.graph_repository import InMemoryGraphRepository
from app.repositories.run_repository import InMemoryRunRepository
from app.runs.service import RunService
from app.workflows import GraphService, RegisteredReferences

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_ORGANIZATION = OrganizationId("property-7-organization")
_CORRELATION = CorrelationId("property-7-correlation")
_SAFE_VALUES = st.text(alphabet="abcdefghijklmnopqrstuvwxyz0123456789", min_size=1, max_size=12)
_CUSTOM_JUSTIFICATIONS = st.sampled_from(("none", "fork_origin", "custom_reason"))
_VALIDATION_OUTCOMES = st.one_of(st.none(), st.sampled_from(tuple(GraphValidationCategory)))


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


def _agent(value: str) -> CommonAgentVersion:
    return CommonAgentVersion(
        metadata=_metadata(f"agent-record-{value}"),
        agent_version_id=AgentVersionId(f"agent-{value}"),
        status=ContractStatus.PUBLISHED,
        canonical_identity=f"planner-{value}",
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
        content_digest=f"sha256:agent-{value}",
    )


def _pattern(value: str) -> CommonPatternVersion:
    return CommonPatternVersion(
        metadata=_metadata(f"pattern-record-{value}"),
        pattern_version_id=CommonPatternVersionId(f"pattern-{value}"),
        status=ContractStatus.PUBLISHED,
        graph_template={},
        slot_constraints={},
        compatibility_rules={},
        risk_requirements={},
        verification_requirements={"verification_level": "strict"},
        provenance={},
        content_digest=f"sha256:pattern-{value}",
    )


def _references(agent: CommonAgentVersion) -> RegisteredReferences:
    return RegisteredReferences(
        agent_ids=frozenset({agent.canonical_identity}),
        tool_ids=frozenset({"crm.lookup"}),
        memory_scope_ids=frozenset({"organization"}),
        risk_gate_ids=frozenset({"low-risk"}),
        rollback_plan_ids=frozenset({"compensate.crm"}),
        authorization_ids=frozenset({"approval-1"}),
    )


def _revision(
    value: str,
    revision_number: int,
    agent: CommonAgentVersion,
    pattern: CommonPatternVersion,
    *,
    custom_node: bool = False,
    custom_justification: str = "none",
    failed_category: GraphValidationCategory | None = None,
) -> GraphRevision:
    node: dict[str, object] = {
        "id": "plan",
        "agent_version_id": str(agent.agent_version_id),
        "tool_ids": ["crm.lookup"],
        "memory_reads": ["organization"],
        "memory_writes": ["organization"],
    }
    budget: dict[str, object] = {
        "max_node_visits": 1,
        "max_handoffs": 0,
        "max_wall_clock_seconds": 30,
        "max_tool_requests": 1,
    }
    rollback: dict[str, object] = {
        "plan_id": "compensate.crm",
        "compensation_step_ids": ["plan"],
    }
    workflow_definition: dict[str, object] = {
        "id": f"ops.compose.{value}",
        "version": "1.0.0",
        "owner_id": "ops.owner",
        "authorization_id": "approval-1",
        "engine": "graph",
        "execution_budget": budget,
        "memory": {"reads": ["organization"], "writes": ["organization"]},
        "risk_gate_ids": ["low-risk"],
        "rollback": rollback,
        "pattern": "pipeline",
        "entry_node": "plan",
        "terminal_node_ids": ["plan"],
    }
    version_pins: dict[str, object] = {
        "agent_version_ids": [str(agent.agent_version_id)],
        "pattern_version_ids": [str(pattern.pattern_version_id)],
    }
    policies: dict[str, object] = {
        "workflow_definition": workflow_definition,
        "verification": {"verification_level": "strict"},
    }

    if custom_node:
        node["node_type"] = "custom_agent"
        if custom_justification == "fork_origin":
            node["fork_origin"] = "published-agent-origin"
        elif custom_justification == "custom_reason":
            node["custom_reason"] = "specialized organization workflow"

    if failed_category is GraphValidationCategory.VERSION_RESOLUTION:
        version_pins["pattern_version_ids"] = ["unknown-pattern"]
    elif failed_category is GraphValidationCategory.SCHEMA_COMPATIBILITY:
        del workflow_definition["owner_id"]
    elif failed_category is GraphValidationCategory.TOOL_POLICY:
        node["tool_ids"] = ["crm.write"]
    elif failed_category is GraphValidationCategory.BUDGET_POLICY:
        budget["max_node_visits"] = 0
    elif failed_category is GraphValidationCategory.VERIFICATION_POLICY:
        policies["verification"] = {"verification_level": "relaxed"}
    elif failed_category is GraphValidationCategory.ROLLBACK_POLICY:
        rollback["plan_id"] = "unknown-rollback"
    elif failed_category is GraphValidationCategory.APPROVAL_POLICY:
        workflow_definition["authorization_id"] = "unknown-approval"

    return GraphRevision(
        metadata=_metadata(f"graph-record-{value}-{revision_number}"),
        graph_revision_id=GraphRevisionId(f"graph-{value}-{revision_number}"),
        swarm_instance_id=SwarmInstanceId("property-7-swarm"),
        revision=revision_number,
        nodes=(node,),
        edges=(),
        layout={"plan": {"x": revision_number, "y": 0}},
        version_pins=version_pins,
        policies=policies,
    )


def _unit_of_work_factory(database: InMemoryControlPlaneDatabase) -> ControlPlaneUnitOfWork:
    return cast(ControlPlaneUnitOfWork, database.unit_of_work())


@dataclass(frozen=True, slots=True)
class _GraphValidatedRunGate:
    """Deterministic command-boundary fake that creates a run only from retained eligibility."""

    graph_service: GraphService
    run_service: RunService

    def create(self, graph_revision_id: GraphRevisionId) -> Result[RunRecord, ErrorDetail]:
        validation = self.graph_service.latest_validation(_ORGANIZATION, graph_revision_id)
        if not validation.is_success or validation.value is None:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.VALIDATION_FAILED,
                    "A successful graph validation is required before a run is created.",
                    _CORRELATION,
                )
            )
        report = validation.value
        if not report.eligible_for_run or report.workflow_definition is None:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.VALIDATION_FAILED,
                    "The graph revision is not eligible for run creation.",
                    _CORRELATION,
                )
            )
        return self.run_service.create_queued_run(
            _ORGANIZATION,
            _CORRELATION,
            report.workflow_definition,
        )


# Feature: backend-redesign, Property 7: Graph revision validation gates runs and
# preserves concurrency.
# **Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8**
@settings(max_examples=100, deadline=None)
@given(
    value=_SAFE_VALUES,
    custom_node=st.booleans(),
    custom_justification=_CUSTOM_JUSTIFICATIONS,
    stale_expected_revision=st.booleans(),
    failed_category=_VALIDATION_OUTCOMES,
)
def test_property_7_graph_revision_validation_gates_runs_and_preserves_concurrency(
    value: str,
    custom_node: bool,
    custom_justification: str,
    stale_expected_revision: bool,
    failed_category: GraphValidationCategory | None,
) -> None:
    """Only an exact revision with every successful category can create one queued run."""
    database = InMemoryControlPlaneDatabase()
    graph_repository = InMemoryGraphRepository()
    agent = _agent(value)
    pattern = _pattern(value)
    with database.unit_of_work() as unit_of_work:
        assert unit_of_work.common_contracts.append_agent_version(agent).is_success
        assert unit_of_work.common_contracts.append_pattern_version(pattern).is_success

    graph_service = GraphService(
        lambda: _unit_of_work_factory(database),
        graph_repository,
        _references(agent),
        clock=lambda: _NOW,
    )
    run_repository = InMemoryRunRepository()
    run_gate = _GraphValidatedRunGate(
        graph_service,
        RunService(run_repository, _references(agent), clock=lambda: _NOW),
    )
    instance = SwarmInstance(
        metadata=_metadata("property-7-swarm-record"),
        swarm_instance_id=SwarmInstanceId("property-7-swarm"),
    )
    initial_revision = _revision("initial", 1, agent, pattern)
    created_initial = graph_service.create_revision(
        _ORGANIZATION,
        instance,
        initial_revision,
        expected_revision=0,
    )
    assert created_initial.is_success and created_initial.value == initial_revision

    candidate = _revision(
        value,
        2,
        agent,
        pattern,
        custom_node=custom_node,
        custom_justification=custom_justification,
        failed_category=failed_category,
    )
    expected_revision = 0 if stale_expected_revision else 1
    created_candidate = graph_service.create_revision(
        _ORGANIZATION,
        instance,
        candidate,
        expected_revision=expected_revision,
    )
    custom_node_is_unjustified = custom_node and custom_justification == "none"

    if stale_expected_revision or custom_node_is_unjustified:
        assert not created_candidate.is_success
        blocked_run = run_gate.create(candidate.graph_revision_id)
        assert not blocked_run.is_success
        assert blocked_run.error is not None
        assert blocked_run.error.code is ErrorCode.VALIDATION_FAILED
        assert run_repository.records() == ()
        current = graph_repository.get_instance(_ORGANIZATION, instance.swarm_instance_id)
        assert current.is_success and current.value is not None
        assert current.value.current_revision == 1
        assert current.value.current_graph_revision_id == initial_revision.graph_revision_id
        return

    assert created_candidate.is_success and created_candidate.value == candidate
    retained_candidate = graph_repository.get_revision(_ORGANIZATION, candidate.graph_revision_id)
    assert retained_candidate.is_success and retained_candidate.value == candidate

    unvalidated_run = run_gate.create(candidate.graph_revision_id)
    assert not unvalidated_run.is_success
    assert unvalidated_run.error is not None
    assert unvalidated_run.error.code is ErrorCode.VALIDATION_FAILED
    assert run_repository.records() == ()

    validation = graph_service.validate_revision(_ORGANIZATION, candidate.graph_revision_id)
    assert validation.is_success and validation.value is not None
    report = validation.value
    assert tuple(result.category for result in report.categories) == tuple(GraphValidationCategory)
    expected_failed_categories: set[GraphValidationCategory] = set()
    if failed_category is not None:
        expected_failed_categories.add(failed_category)
    assert {
        result.category for result in report.categories if not result.passed
    } == expected_failed_categories
    assert report.eligible_for_run is (failed_category is None)

    created_run = run_gate.create(candidate.graph_revision_id)
    if failed_category is not None:
        assert not created_run.is_success
        assert created_run.error is not None
        assert created_run.error.code is ErrorCode.VALIDATION_FAILED
        assert report.workflow_definition is None
        assert report.workflow_definition_version is None
        assert run_repository.records() == ()
        return

    assert report.workflow_definition is not None
    assert report.workflow_definition_version == "1.0.0"
    assert created_run.is_success and created_run.value is not None
    assert len(run_repository.records()) == 1
    assert run_repository.records()[0] == created_run.value
    assert created_run.value.workflow_definition_id == report.workflow_definition["id"]
    assert created_run.value.workflow_definition_version == report.workflow_definition_version
