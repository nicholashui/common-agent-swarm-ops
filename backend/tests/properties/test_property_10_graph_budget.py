"""Property tests for GraphEngine's first-breach budget enforcement."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Final, Literal

from hypothesis import example, given, settings, strategies as st

from app.engines.compiler import CompiledGraphNode, GraphCompiler
from app.engines.graph import GraphEngine, GraphNodeResult, GraphNodeServices
from app.governance.authorization import ApprovalState, AuthorizationContext, AuthorizationDecision
from app.governance.tool_broker import ToolInvocationResult, ToolRequest
from app.models.common import RecordMetadata
from app.models.identifiers import (
    CorrelationId,
    OrganizationId,
    RecordId,
    RunId,
    WorkflowDefinitionId,
)
from app.models.runs import RunRecord, RunStatus, ToolEffect, WorkflowEngineKind
from app.repositories.run_repository import InMemoryRunRepository
from app.workflows.validator import RegisteredReferences, WorkflowDefinitionValidator

# Feature: generic-swarm-business-os, Property 10: Graph budget enforcement stops at the first
# breached limit.
# **Validates: Requirements 4.5**

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_ORGANIZATION_ID = OrganizationId("org-property-10")
_CORRELATION_ID = CorrelationId("corr-property-10")
type BudgetKind = Literal["node", "handoff", "tool", "wall"]
type GraphDefinition = Mapping[str, object]
type GraphNodeDefinition = Mapping[str, object]
type GraphEdgeDefinition = Mapping[str, object]
type ExpectedFailure = tuple[str, int, int, int, int]
_BUDGET_KINDS: Final[tuple[BudgetKind, ...]] = ("node", "handoff", "tool", "wall")
_FIRST_BREACH_EVENT_COUNTS: Final[Mapping[BudgetKind, int]] = {
    "node": 101,
    "handoff": 13,
    "tool": 51,
    "wall": 2,
}
_EXPECTED_FAILURES: Final[Mapping[BudgetKind, ExpectedFailure]] = {
    "node": ("graph_node_budget_exceeded", 100, 0, 0, 0),
    "handoff": ("graph_handoff_budget_exceeded", 13, 12, 0, 0),
    "tool": ("graph_tool_budget_exceeded", 1, 0, 50, 50),
    "wall": ("graph_wall_clock_budget_exceeded", 0, 0, 0, 0),
}
_DEFINITION_VALIDATOR = WorkflowDefinitionValidator(
    RegisteredReferences(
        agent_ids=frozenset({"agent-0", "agent-alpha", "agent-beta", "agent-worker"}),
        tool_ids=frozenset({"local.tool"}),
        memory_scope_ids=frozenset(),
        risk_gate_ids=frozenset({"low-risk"}),
        rollback_plan_ids=frozenset({"compensate"}),
        authorization_ids=frozenset({"authorization-1"}),
    )
)


@dataclass(frozen=True, slots=True)
class BudgetBreachSequence:
    """A bounded counter sequence with exactly one first budget breach."""

    kind: BudgetKind
    event_ids: tuple[int, ...]
    suffix: int


@dataclass(slots=True)
class _RecordingBroker:
    """A deterministic broker fake that records only permitted local requests."""

    calls: list[ToolRequest] = field(default_factory=list)

    def request_tool(
        self, request: ToolRequest, _context: AuthorizationContext
    ) -> ToolInvocationResult:
        """Record a deterministic successful local tool invocation."""
        self.calls.append(request)
        return ToolInvocationResult(
            authorization=AuthorizationDecision(request.adapter_id, ()),
            invoked=True,
            effect=ToolEffect(
                adapter_id=request.adapter_id,
                request_digest=f"request-{len(self.calls)}",
                outcome="completed",
                effect_digest=f"effect-{len(self.calls)}",
                completed_at=_NOW,
                reversible=True,
            ),
        )


@dataclass(slots=True)
class _RecordingExecutor:
    """A graph-node executor that emits only the generated local tool event sequence."""

    tool_event_ids: tuple[int, ...]
    visited_node_ids: list[str] = field(default_factory=list)

    def execute(
        self,
        _run: RunRecord,
        node: CompiledGraphNode,
        services: GraphNodeServices,
    ) -> GraphNodeResult:
        """Record a node visit and request each generated local tool event when configured."""
        self.visited_node_ids.append(node.node_id)
        for event_id in self.tool_event_ids:
            services.request_tool("local.tool", {"event_id": event_id})
        return GraphNodeResult()


@dataclass(slots=True)
class _BreachClock:
    """Return zero at graph start and a configured elapsed value on every later read."""

    elapsed_seconds: float
    reads: int = 0

    def __call__(self) -> float:
        """Supply a deterministic monotonic timestamp without sleeping."""
        value = 0.0 if self.reads == 0 else self.elapsed_seconds
        self.reads += 1
        return value


@st.composite
def _budget_breach_sequences(draw: st.DrawFn) -> BudgetBreachSequence:
    """Generate bounded event lists that exceed one fixed GraphEngine limit by one."""
    kind: BudgetKind = draw(st.sampled_from(_BUDGET_KINDS))
    event_count = _FIRST_BREACH_EVENT_COUNTS[kind]
    return BudgetBreachSequence(
        kind=kind,
        event_ids=tuple(
            draw(
                st.lists(
                    st.integers(min_value=0, max_value=9_999),
                    min_size=event_count,
                    max_size=event_count,
                )
            )
        ),
        suffix=draw(st.integers(min_value=0, max_value=9_999)),
    )


def _node(
    node_id: str, agent_id: str, tool_ids: tuple[str, ...] = ()
) -> GraphNodeDefinition:
    """Return a graph node valid for both Host definition validation and compilation."""
    return {
        "id": node_id,
        "agent_id": agent_id,
        "tool_ids": list(tool_ids),
        "memory_reads": [],
        "memory_writes": [],
    }


def _base_definition(
    suffix: int,
    nodes: Sequence[GraphNodeDefinition],
    edges: Sequence[GraphEdgeDefinition],
    entry_node: str,
    terminal_node_ids: Sequence[str],
) -> GraphDefinition:
    """Build the smallest valid graph definition around a generated event sequence."""
    return {
        "definition_type": "pack_graph",
        "id": f"ops.graph-budget-{suffix}",
        "version": "1.0.0",
        "owner_id": "ops.owner",
        "authorization_id": "authorization-1",
        "engine": "graph",
        "execution_budget": {
            "max_node_visits": 100,
            "max_handoffs": 12,
            "max_wall_clock_seconds": 900,
            "max_tool_requests": 50,
        },
        "memory": {"reads": [], "writes": []},
        "risk_gate_ids": ["low-risk"],
        "rollback": {"plan_id": "compensate", "compensation_step_ids": [entry_node]},
        "pattern": "pipeline",
        "nodes": list(nodes),
        "edges": list(edges),
        "entry_node": entry_node,
        "terminal_node_ids": list(terminal_node_ids),
    }


def _definition(sequence: BudgetBreachSequence) -> GraphDefinition:
    """Compile a valid graph that can breach only the selected limit first."""
    if sequence.kind == "node":
        node_ids = [f"node-{sequence.suffix}-{index}" for index in range(100)]
        nodes: list[GraphNodeDefinition] = [_node(node_id, "agent-0") for node_id in node_ids]
        edges: list[GraphEdgeDefinition] = [
            {"from": node_ids[0], "to": node_ids[0], "max_traversals": 10}
        ]
        edges.extend(
            {"from": node_ids[index], "to": node_ids[index + 1], "max_traversals": 1}
            for index in range(99)
        )
        return _base_definition(sequence.suffix, nodes, edges, node_ids[0], [node_ids[-1]])

    if sequence.kind == "handoff":
        alpha = f"alpha-{sequence.suffix}"
        beta = f"beta-{sequence.suffix}"
        terminal = f"terminal-{sequence.suffix}"
        handoff_nodes: list[GraphNodeDefinition] = [
            _node(alpha, "agent-alpha"),
            _node(beta, "agent-beta"),
            _node(terminal, "agent-beta"),
        ]
        handoff_edges: list[GraphEdgeDefinition] = [
            {"from": alpha, "to": beta, "max_traversals": 10},
            {"from": beta, "to": alpha, "max_traversals": 10},
            {"from": beta, "to": terminal, "max_traversals": 1},
        ]
        return _base_definition(sequence.suffix, handoff_nodes, handoff_edges, alpha, [terminal])

    worker = f"worker-{sequence.suffix}"
    tool_ids = ("local.tool",) if sequence.kind == "tool" else ()
    return _base_definition(
        sequence.suffix,
        [_node(worker, "agent-worker", tool_ids)],
        [],
        worker,
        [worker],
    )


def _run(definition: GraphDefinition, suffix: int) -> RunRecord:
    """Build one persisted dispatched graph run bound to the generated definition."""
    return RunRecord(
        metadata=RecordMetadata(
            record_id=RecordId(f"record-property-10-{suffix}"),
            organization_id=_ORGANIZATION_ID,
            correlation_id=_CORRELATION_ID,
            schema_version=1,
            version=1,
            created_at=_NOW,
            updated_at=_NOW,
        ),
        run_id=RunId(f"run-property-10-{suffix}"),
        workflow_definition_id=WorkflowDefinitionId(str(definition["id"])),
        workflow_definition_version="1.0.0",
        workflow_definition_digest=GraphCompiler.definition_digest(definition),
        engine=WorkflowEngineKind.GRAPH,
        status=RunStatus.DISPATCHING,
        created_for_dispatch_at=_NOW,
    )


def _authorization_context(
    _run_record: RunRecord, node: CompiledGraphNode
) -> AuthorizationContext:
    """Authorize only the declared deterministic local tool for the executing node."""
    declared_tools = frozenset(node.declared_tool_ids)
    return AuthorizationContext(
        agent_id=node.agent_id,
        step_id=node.node_id,
        organization_id=str(_ORGANIZATION_ID),
        actor_id="actor-property-10",
        correlation_id=str(_CORRELATION_ID),
        agent_allowed_tools=declared_tools,
        step_declared_tools=declared_tools,
        role_allowed_tools=declared_tools,
        organization_allowed_tools=declared_tools,
        risk_allowed_tools=declared_tools,
        approval_state=ApprovalState.NOT_REQUIRED,
    )


def _expected_failure(sequence: BudgetBreachSequence) -> ExpectedFailure:
    """Return the durable code and accepted-work counts immediately before each breach."""
    return _EXPECTED_FAILURES[sequence.kind]


def _expected_visited_nodes(sequence: BudgetBreachSequence) -> tuple[str, ...]:
    """Return the exact scheduled prefix, excluding the rejected breaching event."""
    if sequence.kind == "node":
        initial = f"node-{sequence.suffix}-0"
        return (initial,) * 11 + tuple(
            f"node-{sequence.suffix}-{index}" for index in range(1, 90)
        )
    if sequence.kind == "handoff":
        alpha = f"alpha-{sequence.suffix}"
        beta = f"beta-{sequence.suffix}"
        return (alpha, beta) * 6 + (alpha,)
    if sequence.kind == "tool":
        return (f"worker-{sequence.suffix}",)
    return ()


def _expected_unstarted_nodes(sequence: BudgetBreachSequence) -> tuple[str, ...]:
    """Return every node that must remain unscheduled when the first breach occurs."""
    if sequence.kind == "node":
        return tuple(f"node-{sequence.suffix}-{index}" for index in range(90, 100))
    if sequence.kind == "handoff":
        return (f"terminal-{sequence.suffix}",)
    if sequence.kind == "wall":
        return (f"worker-{sequence.suffix}",)
    return ()


@settings(max_examples=100, deadline=None, derandomize=True)
@example(BudgetBreachSequence("node", tuple(range(101)), 1))
@example(BudgetBreachSequence("handoff", tuple(range(13)), 2))
@example(BudgetBreachSequence("tool", tuple(range(51)), 3))
@example(BudgetBreachSequence("wall", (0, 1), 4))
@given(sequence=_budget_breach_sequences())
def test_graph_engine_stops_at_the_first_budget_breach(
    sequence: BudgetBreachSequence,
) -> None:
    """Every over-limit event fails before it schedules work beyond the accepted prefix."""
    definition = _definition(sequence)
    assert _DEFINITION_VALIDATOR.validate(definition).is_valid
    GraphCompiler().compile(definition)

    run = _run(definition, sequence.suffix)
    repository = InMemoryRunRepository()
    assert repository.create(run).is_success
    executor = _RecordingExecutor(sequence.event_ids if sequence.kind == "tool" else ())
    broker = _RecordingBroker()
    clock = _BreachClock(901.0 if sequence.kind == "wall" else 0.0)

    outcome = GraphEngine(
        repository,
        executor,
        broker,
        _authorization_context,
        monotonic_clock=clock,
    ).execute(_ORGANIZATION_ID, run.run_id, definition, _CORRELATION_ID)

    expected_code, node_visits, handoffs, tool_requests, broker_calls = _expected_failure(sequence)
    assert len(sequence.event_ids) == _FIRST_BREACH_EVENT_COUNTS[sequence.kind]
    assert outcome.is_success and outcome.value is not None
    assert not outcome.value.completed
    assert outcome.value.metrics.node_visits == node_visits
    assert outcome.value.metrics.handoffs == handoffs
    assert outcome.value.metrics.tool_requests == tool_requests
    assert tuple(executor.visited_node_ids) == _expected_visited_nodes(sequence)
    assert len(broker.calls) == broker_calls
    assert [call.arguments["event_id"] for call in broker.calls] == list(
        sequence.event_ids[:broker_calls]
    )

    stored = repository.get_by_run_id(_ORGANIZATION_ID, run.run_id)
    assert stored.is_success and stored.value is not None
    assert stored.value == outcome.value.record
    assert stored.value.status is RunStatus.FAILED
    assert stored.value.failure is not None
    assert stored.value.failure.code == expected_code
    assert stored.value.failure.failure_processing_complete
    assert stored.value.failure.stopped_step_ids == _expected_unstarted_nodes(sequence)
    assert stored.value.output == {
        "graph_metrics": {
            "node_visits": node_visits,
            "handoffs": handoffs,
            "tool_requests": tool_requests,
        }
    }
    assert tuple(effect.effect_digest for effect in stored.value.tool_effects) == tuple(
        f"effect-{index}" for index in range(1, broker_calls + 1)
    )
