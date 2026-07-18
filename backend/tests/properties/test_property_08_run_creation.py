"""Property tests for workflow-definition validation and durable run creation."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime

from hypothesis import example, given, settings, strategies as st

from app.models.contracts import RepositoryError, Result
from app.models.identifiers import CorrelationId, OrganizationId
from app.models.runs import RunRecord, RunStatus, WorkflowEngineKind
from app.repositories.run_repository import InMemoryRunRepository
from app.runs.service import RunService
from app.workflows.validator import RegisteredReferences

# Feature: generic-swarm-business-os, Property 8: Definition validation controls run creation
# and dispatch ordering.
# **Validates: Requirements 4.1, 4.2, 6.1**

_ORGANIZATION_ID = OrganizationId("org-property-8")
_CORRELATION_ID = CorrelationId("corr-property-8")
_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_REFERENCES = RegisteredReferences(
    agent_ids=frozenset({"ops.planner"}),
    tool_ids=frozenset({"crm.lookup"}),
    memory_scope_ids=frozenset({"organization", "workflow"}),
    risk_gate_ids=frozenset({"low-risk"}),
    rollback_plan_ids=frozenset({"compensate.crm"}),
    authorization_ids=frozenset({"approval-1"}),
)


@dataclass(frozen=True, slots=True)
class DefinitionCase:
    """One bounded workflow-definition input and its expected validity."""

    kind: str
    definition: Mapping[str, object]
    is_valid: bool


class RecordingRunRepository(InMemoryRunRepository):
    """Deterministic repository fake that records pre-dispatch queued writes."""

    def __init__(self) -> None:
        super().__init__()
        self.queued_records: list[RunRecord] = []
        self.events: list[str] = []

    def create_queued(self, record: RunRecord) -> Result[RunRecord, RepositoryError]:
        result = super().create_queued(record)
        if result.is_success and result.value is not None:
            self.queued_records.append(result.value)
            self.events.append("queued-persisted")
        return result


@dataclass(slots=True)
class RecordingStarter:
    """Deterministic dispatch fake that observes durable state before execution begins."""

    repository: RecordingRunRepository
    calls: list[RunRecord] = field(default_factory=list)

    def __call__(self, record: RunRecord) -> None:
        stored = self.repository.get_by_run_id(_ORGANIZATION_ID, record.run_id)
        assert stored.is_success and stored.value is not None
        assert stored.value.status is RunStatus.DISPATCHING
        assert stored.value.engine is record.engine
        self.calls.append(record)
        self.repository.events.append("starter-invoked")


def _budget(
    max_node_visits: int,
    max_handoffs: int,
    max_wall_clock_seconds: int,
    max_tool_requests: int,
) -> dict[str, int]:
    """Build a validator-bounded execution budget."""
    return {
        "max_node_visits": max_node_visits,
        "max_handoffs": max_handoffs,
        "max_wall_clock_seconds": max_wall_clock_seconds,
        "max_tool_requests": max_tool_requests,
    }


def _valid_dna_definition(
    suffix: int,
    step_count: int,
    engine: str,
    budget: dict[str, int],
) -> dict[str, object]:
    """Build a bounded valid WorkflowDNA fixture."""
    step_ids = [f"step-{index}" for index in range(step_count)]
    return {
        "definition_type": "workflow_dna",
        "id": f"ops.workflow-{suffix}",
        "version": "1.0.0",
        "owner_id": "ops.owner",
        "authorization_id": "approval-1",
        "engine": engine,
        "execution_budget": budget,
        "memory": {"reads": ["organization"], "writes": ["workflow"]},
        "risk_gate_ids": ["low-risk"],
        "rollback": {"plan_id": "compensate.crm", "compensation_step_ids": step_ids},
        "steps": [
            {
                "id": step_id,
                "agent_id": "ops.planner",
                "tool_ids": ["crm.lookup"],
                "memory_reads": ["organization"],
                "memory_writes": ["workflow"],
            }
            for step_id in step_ids
        ],
    }


def _valid_graph_definition(
    suffix: int,
    node_count: int,
    pattern: str,
    budget: dict[str, int],
) -> dict[str, object]:
    """Build a reachable bounded permitted pack graph fixture."""
    node_ids = [f"node-{index}" for index in range(node_count)]
    return {
        "definition_type": "pack_graph",
        "id": f"ops.graph-{suffix}",
        "version": "1.0.0",
        "owner_id": "ops.owner",
        "authorization_id": "approval-1",
        "engine": "graph",
        "execution_budget": budget,
        "memory": {"reads": ["organization"], "writes": ["workflow"]},
        "risk_gate_ids": ["low-risk"],
        "rollback": {"plan_id": "compensate.crm", "compensation_step_ids": node_ids},
        "pattern": pattern,
        "nodes": [
            {
                "id": node_id,
                "agent_id": "ops.planner",
                "tool_ids": ["crm.lookup"],
                "memory_reads": ["organization"],
                "memory_writes": ["workflow"],
            }
            for node_id in node_ids
        ],
        "edges": [
            {"from": node_ids[index], "to": node_ids[index + 1], "max_traversals": 1}
            for index in range(node_count - 1)
        ],
        "entry_node": node_ids[0],
        "terminal_node_ids": [node_ids[-1]],
    }


@st.composite
def _valid_dna_case(draw: st.DrawFn) -> DefinitionCase:
    """Generate a valid DNA with only bounded definition dimensions."""
    budget = _budget(
        draw(st.integers(min_value=1, max_value=100)),
        draw(st.integers(min_value=0, max_value=12)),
        draw(st.integers(min_value=1, max_value=900)),
        draw(st.integers(min_value=0, max_value=50)),
    )
    return DefinitionCase(
        "valid-dna",
        _valid_dna_definition(
            draw(st.integers(min_value=0, max_value=9_999)),
            draw(st.integers(min_value=1, max_value=5)),
            draw(st.sampled_from(("legacy", "graph"))),
            budget,
        ),
        True,
    )


@st.composite
def _valid_graph_case(draw: st.DrawFn) -> DefinitionCase:
    """Generate a valid graph whose chain topology is reachable and terminally complete."""
    budget = _budget(
        draw(st.integers(min_value=1, max_value=100)),
        draw(st.integers(min_value=0, max_value=12)),
        draw(st.integers(min_value=1, max_value=900)),
        draw(st.integers(min_value=0, max_value=50)),
    )
    return DefinitionCase(
        "valid-graph",
        _valid_graph_definition(
            draw(st.integers(min_value=0, max_value=9_999)),
            draw(st.integers(min_value=1, max_value=5)),
            draw(st.sampled_from(("pipeline", "supervisor", "router", "critique", "map_reduce"))),
            budget,
        ),
        True,
    )


@st.composite
def _invalid_dna_case(draw: st.DrawFn) -> DefinitionCase:
    """Generate DNA inputs that each violate one mandatory validator constraint."""
    valid = draw(_valid_dna_case())
    definition = dict(valid.definition)
    failure = draw(st.sampled_from(("engine", "budget", "steps", "risk_gate")))
    if failure == "engine":
        definition["engine"] = "unsupported"
    elif failure == "budget":
        definition["execution_budget"] = _budget(101, 0, 1, 0)
    elif failure == "steps":
        definition["steps"] = []
    else:
        definition["risk_gate_ids"] = ["unregistered-gate"]
    return DefinitionCase("invalid-dna", definition, False)


@st.composite
def _invalid_graph_case(draw: st.DrawFn) -> DefinitionCase:
    """Generate graph inputs that each violate engine, pattern, topology, or node bounds."""
    valid = draw(_valid_graph_case())
    definition = dict(valid.definition)
    failure = draw(st.sampled_from(("engine", "pattern", "terminal", "nodes")))
    if failure == "engine":
        definition["engine"] = "legacy"
    elif failure == "pattern":
        definition["pattern"] = "unbounded"
    elif failure == "terminal":
        definition["terminal_node_ids"] = ["missing-node"]
    else:
        definition["nodes"] = []
    return DefinitionCase("invalid-graph", definition, False)


@st.composite
def _definition_cases(draw: st.DrawFn) -> DefinitionCase:
    """Cover valid and invalid DNA and graph definitions without unbounded payloads."""
    case_strategy = draw(
        st.sampled_from(
            (
                _valid_dna_case(),
                _valid_graph_case(),
                _invalid_dna_case(),
                _invalid_graph_case(),
            )
        )
    )
    return draw(case_strategy)


@settings(max_examples=100, deadline=None)
@example(
    case=DefinitionCase(
        "valid-dna", _valid_dna_definition(1, 1, "legacy", _budget(1, 0, 1, 0)), True
    )
)
@example(
    case=DefinitionCase(
        "valid-graph", _valid_graph_definition(2, 1, "pipeline", _budget(1, 0, 1, 0)), True
    )
)
@example(
    case=DefinitionCase(
        "invalid-dna",
        {
            **_valid_dna_definition(3, 1, "legacy", _budget(1, 0, 1, 0)),
            "steps": [],
        },
        False,
    )
)
@example(
    case=DefinitionCase(
        "invalid-graph",
        {**_valid_graph_definition(4, 1, "pipeline", _budget(1, 0, 1, 0)), "pattern": "unbounded"},
        False,
    )
)
@given(case=_definition_cases())
def test_definition_validation_controls_run_creation_and_dispatch_ordering(
    case: DefinitionCase,
) -> None:
    """Only valid definitions persist unique queued records before deterministic dispatch."""
    repository = RecordingRunRepository()
    service = RunService(repository, _REFERENCES, clock=lambda: _NOW)
    starter = RecordingStarter(repository)

    first_creation = service.create_queued_run(_ORGANIZATION_ID, _CORRELATION_ID, case.definition)

    if not case.is_valid:
        assert not first_creation.is_success
        assert repository.records() == ()
        assert repository.queued_records == []
        assert starter.calls == []
        assert repository.events == []
        return

    assert first_creation.is_success and first_creation.value is not None
    first_run = first_creation.value
    second_creation = service.create_queued_run(_ORGANIZATION_ID, _CORRELATION_ID, case.definition)
    assert second_creation.is_success and second_creation.value is not None
    second_run = second_creation.value
    expected_engine = WorkflowEngineKind(str(case.definition["engine"]))

    assert first_run.run_id != second_run.run_id
    assert first_run.metadata.record_id != second_run.metadata.record_id
    assert tuple(record.status for record in repository.queued_records) == (
        RunStatus.QUEUED,
        RunStatus.QUEUED,
    )
    assert tuple(record.engine for record in repository.queued_records) == (
        expected_engine,
        expected_engine,
    )

    dispatched = service.dispatch(
        _ORGANIZATION_ID,
        first_run.run_id,
        "dispatch-property-8",
        starter,
        _CORRELATION_ID,
    )

    assert dispatched.is_success and dispatched.value is not None
    assert not dispatched.value.is_idempotent
    assert starter.calls == [dispatched.value.record]
    assert repository.events == ["queued-persisted", "queued-persisted", "starter-invoked"]
    assert tuple(record.tool_effects for record in repository.records()) == ((), ())
    stored_second = repository.get_by_run_id(_ORGANIZATION_ID, second_run.run_id)
    assert stored_second.is_success and stored_second.value is not None
    assert stored_second.value.status is RunStatus.QUEUED
