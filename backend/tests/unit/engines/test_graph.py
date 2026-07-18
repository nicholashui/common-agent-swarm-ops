"""Focused deterministic checks for the bounded in-process GraphEngine."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

import pytest

from app.engines.compiler import CompiledGraphNode, GraphCompilationError, GraphCompiler
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

NOW = datetime(2025, 1, 1, tzinfo=UTC)
ORG_ID = OrganizationId("org-graph")
CORRELATION_ID = CorrelationId("corr-graph")


def _definition() -> dict[str, object]:
    return {
        "definition_type": "pack_graph",
        "id": "ops.graph",
        "version": "1.0.0",
        "owner_id": "ops.owner",
        "authorization_id": "authorization-1",
        "engine": "graph",
        "execution_budget": {
            "max_node_visits": 2,
            "max_handoffs": 1,
            "max_wall_clock_seconds": 30,
            "max_tool_requests": 1,
        },
        "memory": {"reads": [], "writes": []},
        "risk_gate_ids": ["low-risk"],
        "rollback": {"plan_id": "compensate", "compensation_step_ids": ["start"]},
        "pattern": "pipeline",
        "nodes": [
            {
                "id": "start",
                "agent_id": "ops.planner",
                "tool_ids": ["crm.lookup"],
                "memory_reads": [],
                "memory_writes": [],
            },
            {
                "id": "review",
                "agent_id": "ops.reviewer",
                "tool_ids": [],
                "memory_reads": [],
                "memory_writes": [],
            },
        ],
        "edges": [{"from": "start", "to": "review", "max_traversals": 1}],
        "entry_node": "start",
        "terminal_node_ids": ["review"],
    }


@dataclass
class _RecordingBroker:
    """Host-owned broker fake that records only broker-mediated requests."""

    calls: list[ToolRequest] = field(default_factory=list)

    def request_tool(
        self, request: ToolRequest, _context: AuthorizationContext
    ) -> ToolInvocationResult:
        self.calls.append(request)
        return ToolInvocationResult(
            authorization=AuthorizationDecision(request.adapter_id, ()),
            invoked=True,
            effect=ToolEffect(
                adapter_id=request.adapter_id,
                request_digest="request-digest",
                outcome="completed",
                effect_digest="effect-digest",
                completed_at=NOW,
                reversible=True,
            ),
        )


class _Executor:
    """Request the declared tool only from the first deterministic graph node."""

    def __init__(self) -> None:
        self.nodes: list[str] = []

    def execute(
        self,
        _run: RunRecord,
        node: CompiledGraphNode,
        services: GraphNodeServices,
    ) -> GraphNodeResult:
        self.nodes.append(node.node_id)
        if node.node_id == "start":
            services.request_tool("crm.lookup", {"account": "account-1"})
        return GraphNodeResult()


def _run(definition: dict[str, object]) -> RunRecord:
    return RunRecord(
        metadata=RecordMetadata(
            record_id=RecordId("record-graph"),
            organization_id=ORG_ID,
            correlation_id=CORRELATION_ID,
            schema_version=1,
            version=1,
            created_at=NOW,
            updated_at=NOW,
        ),
        run_id=RunId("run-graph"),
        workflow_definition_id=WorkflowDefinitionId("ops.graph"),
        workflow_definition_version="1.0.0",
        workflow_definition_digest=GraphCompiler.definition_digest(definition),
        engine=WorkflowEngineKind.GRAPH,
        status=RunStatus.DISPATCHING,
        created_for_dispatch_at=NOW,
    )


def _context(_run: RunRecord, _node: CompiledGraphNode) -> AuthorizationContext:
    return AuthorizationContext(
        agent_id="ops.planner",
        step_id="start",
        organization_id="org-graph",
        actor_id="actor-graph",
        correlation_id="corr-graph",
        agent_allowed_tools=frozenset({"crm.lookup"}),
        step_declared_tools=frozenset({"crm.lookup"}),
        role_allowed_tools=frozenset({"crm.lookup"}),
        organization_allowed_tools=frozenset({"crm.lookup"}),
        risk_allowed_tools=frozenset({"crm.lookup"}),
        approval_state=ApprovalState.NOT_REQUIRED,
    )


def test_graph_engine_compiles_and_executes_only_through_the_broker() -> None:
    definition = _definition()
    repository = InMemoryRunRepository()
    run = _run(definition)
    assert repository.create(run).is_success
    executor = _Executor()
    broker = _RecordingBroker()

    outcome = GraphEngine(repository, executor, broker, _context).execute(
        ORG_ID, run.run_id, definition, CORRELATION_ID
    )

    assert outcome.is_success and outcome.value is not None
    assert outcome.value.completed
    assert outcome.value.metrics.node_visits == 2
    assert outcome.value.metrics.handoffs == 1
    assert outcome.value.metrics.tool_requests == 1
    assert executor.nodes == ["start", "review"]
    assert [request.adapter_id for request in broker.calls] == ["crm.lookup"]
    record = outcome.value.record
    assert record.status is RunStatus.COMPLETED
    assert record.graph_id is not None
    assert record.graph_thread_id == "org-graph:run-graph"
    assert record.tool_effects[0].adapter_id == "crm.lookup"


def test_compiler_rejects_unapproved_patterns_before_execution() -> None:
    definition = _definition()
    definition["pattern"] = "unbounded"

    with pytest.raises(GraphCompilationError, match="not approved"):
        GraphCompiler().compile(definition)
