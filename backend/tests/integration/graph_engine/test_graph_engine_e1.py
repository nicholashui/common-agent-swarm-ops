"""Deterministic GraphEngine integration and target-local E1 evidence coverage."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime

from fastapi.testclient import TestClient

from app.api.v1.dependencies import AuthenticatedRequestContext, get_authenticated_request_context
from app.api.v1.services import ControlPlaneServices, get_control_plane_services
from app.audit import AuditWriter
from app.engines.compiler import CompiledGraphNode, GraphCompiler
from app.engines.graph import (
    GraphEngine,
    GraphExecutionOutcome,
    GraphNodeResult,
    GraphNodeServices,
)
from app.engines.migration import LegacyEngineRetirement
from app.evaluation.migration_evidence import (
    InMemoryMigrationEvidenceRepository,
    MigrationEvidenceService,
    MigrationGate,
    MigrationGateEvidence,
)
from app.evaluation.product_bar import (
    ProductBarCommandResult,
    ProductBarCriterion,
    ProductBarEvidenceOutcome,
    ProductBarEvidenceService,
    ProductBarStatus,
)
from app.governance.approvals import ActionPreview, ApprovalDecisionValue, GovernanceService
from app.governance.authorization import ApprovalState, AuthorizationContext, ToolInputValue
from app.governance.tool_broker import HostToolBroker, LocalAdapterResult, ToolRequest
from app.main import create_app
from app.models.common import RecordMetadata
from app.models.contracts import ErrorCode, ErrorDetail, RepositoryError, Result
from app.models.evidence import EvidenceReference
from app.models.identifiers import (
    ActorId,
    CorrelationId,
    EvidenceId,
    OrganizationId,
    RecordId,
    RunId,
    WorkflowDefinitionId,
)
from app.models.runs import RunRecord, RunStatus, WorkflowEngineKind
from app.repositories.approval_repository import InMemoryApprovalRepository
from app.repositories.product_bar_repository import InMemoryProductBarEvidenceRepository
from app.repositories.run_repository import InMemoryRunRepository
from app.runs.checkpoints import CheckpointRecord, CheckpointResumeService, checkpoint_thread_id
from tests.fakes.broker import InMemoryAuditRepository

NOW = datetime(2025, 1, 1, tzinfo=UTC)
ORGANIZATION_ID = OrganizationId("org-graph-integration")
FOREIGN_ORGANIZATION_ID = OrganizationId("org-graph-foreign")
CORRELATION_ID = CorrelationId("corr-graph-integration")
ADAPTER_ID = "crm.lookup"
EVIDENCE_HASH = "a" * 64
DEFAULT_RUN_ID = RunId("run-graph-integration")


@dataclass
class _RecordingLocalAdapter:
    """A registered deterministic local adapter used through the real Host broker."""

    adapter_id: str = ADAPTER_ID
    version: str = "graph-integration-v1"
    local_only: bool = True
    invocations: list[Mapping[str, ToolInputValue]] = field(default_factory=list)

    def execute(self, arguments: Mapping[str, ToolInputValue]) -> LocalAdapterResult:
        self.invocations.append(arguments)
        return LocalAdapterResult("completed", "graph-effect", reversible=True)


@dataclass
class _InterruptToken:
    """Host-owned local cancellation state set by a deterministic graph node fake."""

    reason: str | None = None

    def cancellation_reason(self) -> str | None:
        return self.reason


@dataclass
class _NodeExecutor:
    """Host-owned graph node fake that can request one declared local adapter."""

    visited_node_ids: list[str] = field(default_factory=list)
    adapter_requested: bool = False
    interrupt_token: _InterruptToken | None = None

    def execute(
        self,
        _run: RunRecord,
        node: CompiledGraphNode,
        services: GraphNodeServices,
    ) -> GraphNodeResult:
        self.visited_node_ids.append(node.node_id)
        if self.adapter_requested and node.node_id == "plan":
            services.request_tool(ADAPTER_ID, {"account_id": "local-account"})
        if self.interrupt_token is not None and node.node_id == "plan":
            self.interrupt_token.reason = "operator-interrupt"
        return GraphNodeResult()


@dataclass
class _CountingCheckpointRepository:
    """Host-owned checkpoint fake that proves denial happens before durable lookup."""

    lookup_calls: int = 0

    def save(self, checkpoint: CheckpointRecord) -> Result[CheckpointRecord, RepositoryError]:
        return Result.success(checkpoint)

    def get_for_resume(
        self, organization_id: OrganizationId, run_id: RunId
    ) -> Result[CheckpointRecord, RepositoryError]:
        self.lookup_calls += 1
        return Result.failure(
            ErrorDetail(ErrorCode.NOT_FOUND, "No local checkpoint exists.", CORRELATION_ID)
        )


def _graph_definition() -> dict[str, object]:
    return {
        "definition_type": "pack_graph",
        "id": "ops.graph-integration",
        "version": "1.0.0",
        "owner_id": "ops.owner",
        "authorization_id": "approval-1",
        "engine": "graph",
        "execution_budget": {
            "max_node_visits": 3,
            "max_handoffs": 2,
            "max_wall_clock_seconds": 30,
            "max_tool_requests": 1,
        },
        "memory": {"reads": ["organization"], "writes": ["workflow"]},
        "risk_gate_ids": ["low-risk"],
        "rollback": {"plan_id": "compensate.crm", "compensation_step_ids": ["plan"]},
        "pattern": "pipeline",
        "nodes": [
            {
                "id": "plan",
                "agent_id": "ops.planner",
                "tool_ids": [ADAPTER_ID],
                "memory_reads": ["organization"],
                "memory_writes": ["workflow"],
            },
            {
                "id": "review",
                "agent_id": "ops.reviewer",
                "tool_ids": [],
                "memory_reads": ["organization"],
                "memory_writes": ["workflow"],
            },
            {
                "id": "deliver",
                "agent_id": "ops.delivery",
                "tool_ids": [],
                "memory_reads": ["organization"],
                "memory_writes": ["workflow"],
            },
        ],
        "edges": [
            {"from": "plan", "to": "review", "max_traversals": 1},
            {"from": "review", "to": "deliver", "max_traversals": 1},
        ],
        "entry_node": "plan",
        "terminal_node_ids": ["deliver"],
    }


def _manifest() -> dict[str, object]:
    return {
        "pack_id": "graph-operations",
        "agents": [
            {"agent_id": "ops.planner", "status": "registered", "allowed_tools": [ADAPTER_ID]},
            {"agent_id": "ops.reviewer", "status": "registered", "allowed_tools": []},
            {"agent_id": "ops.delivery", "status": "registered", "allowed_tools": []},
        ],
    }


def _run(
    definition: Mapping[str, object],
    *,
    organization_id: OrganizationId = ORGANIZATION_ID,
    run_id: RunId = DEFAULT_RUN_ID,
    status: RunStatus = RunStatus.DISPATCHING,
    graph_initialized: bool = False,
) -> RunRecord:
    return RunRecord(
        metadata=RecordMetadata(
            record_id=RecordId(f"record-{run_id}"),
            organization_id=organization_id,
            correlation_id=CORRELATION_ID,
            schema_version=1,
            version=1,
            created_at=NOW,
            updated_at=NOW,
        ),
        run_id=run_id,
        workflow_definition_id=WorkflowDefinitionId("ops.graph-integration"),
        workflow_definition_version="1.0.0",
        workflow_definition_digest=GraphCompiler.definition_digest(definition),
        engine=WorkflowEngineKind.GRAPH,
        status=status,
        created_for_dispatch_at=NOW,
        graph_id="graph-checkpoint" if graph_initialized else None,
        graph_thread_id=(
            checkpoint_thread_id(organization_id, run_id) if graph_initialized else None
        ),
    )


def _context(run: RunRecord, node: CompiledGraphNode) -> AuthorizationContext:
    allowed_tools = frozenset(node.declared_tool_ids)
    return AuthorizationContext(
        agent_id=node.agent_id,
        step_id=node.node_id,
        organization_id=str(run.metadata.organization_id),
        actor_id="host-graph-engine",
        correlation_id=str(CORRELATION_ID),
        agent_allowed_tools=allowed_tools,
        step_declared_tools=allowed_tools,
        role_allowed_tools=allowed_tools,
        organization_allowed_tools=allowed_tools,
        risk_allowed_tools=allowed_tools,
        approval_state=ApprovalState.NOT_REQUIRED,
    )


def _broker(adapter: _RecordingLocalAdapter | None = None) -> HostToolBroker:
    adapters: tuple[object, ...] = (adapter,) if adapter is not None else ()
    return HostToolBroker(adapters, AuditWriter(InMemoryAuditRepository()))


def _completed_graph_outcome() -> tuple[GraphExecutionOutcome, _RecordingLocalAdapter]:
    definition = _graph_definition()
    repository = InMemoryRunRepository()
    record = _run(definition)
    assert repository.create(record).is_success
    adapter = _RecordingLocalAdapter()
    outcome = GraphEngine(
        repository,
        _NodeExecutor(adapter_requested=True),
        _broker(adapter),
        _context,
    ).execute(ORGANIZATION_ID, record.run_id, definition, CORRELATION_ID)
    assert outcome.is_success and outcome.value is not None
    return outcome.value, adapter


def test_graph_engine_completes_bounded_multi_specialist_handoffs_through_host_broker() -> None:
    """Three graph nodes may use exactly two bounded handoffs and retain the local effect."""
    outcome, adapter = _completed_graph_outcome()

    assert outcome.completed
    assert outcome.record.status is RunStatus.COMPLETED
    assert outcome.metrics.node_visits == 3
    assert outcome.metrics.handoffs == 2
    assert outcome.metrics.tool_requests == 1
    assert [dict(arguments) for arguments in adapter.invocations] == [
        {"account_id": "local-account"}
    ]
    assert outcome.record.tool_effects[0].adapter_id == ADAPTER_ID
    assert outcome.record.output == {
        "graph_metrics": {"node_visits": 3, "handoffs": 2, "tool_requests": 1}
    }


def test_versioned_host_exposes_graph_topology_and_interrupted_graph_state() -> None:
    """Topology is safe to inspect and interruption preserves visible graph state locally."""
    application = create_app()
    services = ControlPlaneServices()
    context = AuthenticatedRequestContext(
        tenant_id=ORGANIZATION_ID,
        actor_id=ActorId("graph-operator"),
        correlation_id=CORRELATION_ID,
    )
    application.dependency_overrides[get_authenticated_request_context] = lambda: context
    application.dependency_overrides[get_control_plane_services] = lambda: services
    definition = _graph_definition()

    try:
        with TestClient(application) as client:
            registration = client.post(
                "/api/v1/domains/register", json={"manifest": _manifest()}
            )
            assert registration.status_code == 200
            assert client.post(
                "/api/v1/workflows/definitions", json={"definition": definition}
            ).status_code == 201
            created = client.post(
                "/api/v1/workflows/ops.graph-integration/run", json={"version": "1.0.0"}
            )
            assert created.status_code == 201
            run_id = RunId(str(created.json()["run_id"]))
            dispatched = client.post(
                "/api/v1/workflow-runs/dispatch",
                json={"run_id": run_id, "idempotency_key": "graph-interrupt", "confirm": True},
            )
            assert dispatched.status_code == 200

            token = _InterruptToken()
            interrupted = GraphEngine(
                services.run_repository,
                _NodeExecutor(interrupt_token=token),
                _broker(),
                _context,
                cancellation_token=token,
            ).execute(ORGANIZATION_ID, run_id, definition, CORRELATION_ID)
            assert interrupted.is_success and interrupted.value is not None
            assert not interrupted.value.completed

            topology = client.get(
                "/api/v1/workflows/ops.graph-integration/topology?version=1.0.0"
            )
            graph_state = client.get(f"/api/v1/workflow-runs/{run_id}/graph-state")

        assert topology.status_code == 200
        assert topology.json()["pattern"] == "pipeline"
        assert [node["node_id"] for node in topology.json()["nodes"]] == [
            "plan",
            "review",
            "deliver",
        ]
        assert topology.json()["edges"] == [
            {"source": "plan", "target": "review", "max_traversals": 1},
            {"source": "review", "target": "deliver", "max_traversals": 1},
        ]
        assert graph_state.status_code == 200
        assert graph_state.json()["status"] == "failed"
        assert graph_state.json()["failure_code"] == "operator-interrupt"
        assert graph_state.json()["graph_thread_id"] == f"{ORGANIZATION_ID}:{run_id}"

        stored = services.get_run(ORGANIZATION_ID, run_id, CORRELATION_ID)
        assert stored.is_success and stored.value is not None and stored.value.output is not None
        state = stored.value.output["graph_state"]
        assert isinstance(state, Mapping)
        assert state == {
            "graph_id": stored.value.graph_id,
            "current_node_id": "plan",
            "visited_node_ids": ["plan"],
            "unstarted_node_ids": ("review", "deliver"),
            "interruption": "operator-interrupt",
        }
    finally:
        application.dependency_overrides.clear()


def test_graph_run_approval_resumes_only_after_valid_fresh_host_authorization() -> None:
    """A valid approval resumes a paused graph run and invokes only the local broker adapter."""
    definition = _graph_definition()
    repository = InMemoryRunRepository()
    record = _run(definition, run_id=RunId("run-graph-approval"))
    assert repository.create(record).is_success
    approvals = InMemoryApprovalRepository()
    adapter = _RecordingLocalAdapter()
    governance = GovernanceService(
        repository,
        approvals,
        _broker(adapter),
        clock=lambda: NOW,
    )
    gate = governance.pause_before_effect(
        ORGANIZATION_ID,
        record.run_id,
        CORRELATION_ID,
        "critical",
        ActionPreview(
            action_id="graph-critical-effect",
            summary="Apply the reviewed local graph effect.",
            intended_effect="One deterministic local CRM effect is recorded.",
            supporting_evidence=("graph-review",),
            correction_control="Deny to retain the graph pause.",
        ),
    )
    assert gate.is_success and gate.value is not None

    resumed = governance.submit_decision(
        ORGANIZATION_ID,
        gate.value.approval_id,
        ActorId("graph-approver"),
        ApprovalDecisionValue.APPROVED,
        "The local graph evidence supports this action.",
        AuthorizationContext(
            agent_id="ops.planner",
            step_id="plan",
            organization_id=str(ORGANIZATION_ID),
            actor_id="graph-approver",
            correlation_id=str(CORRELATION_ID),
            agent_allowed_tools=frozenset({ADAPTER_ID}),
            step_declared_tools=frozenset({ADAPTER_ID}),
            role_allowed_tools=frozenset({ADAPTER_ID}),
            organization_allowed_tools=frozenset({ADAPTER_ID}),
            risk_allowed_tools=frozenset({ADAPTER_ID}),
            approval_state=ApprovalState.PENDING,
        ),
        ToolRequest(ADAPTER_ID, {"account_id": "approved-local-account"}),
        CORRELATION_ID,
    )

    assert resumed.is_success and resumed.value is not None
    assert resumed.value.resumed
    assert resumed.value.decision.is_valid_approval
    assert resumed.value.invocation is not None and resumed.value.invocation.allowed
    assert [dict(arguments) for arguments in adapter.invocations] == [
        {"account_id": "approved-local-account"}
    ]
    stored = repository.get_by_run_id(ORGANIZATION_ID, record.run_id)
    decisions = approvals.decisions(ORGANIZATION_ID, gate.value.approval_id)
    assert stored.is_success and stored.value is not None
    assert stored.value.status is RunStatus.DISPATCHING
    assert decisions.is_success and decisions.value == (resumed.value.decision,)


def test_cross_organization_graph_checkpoint_resume_is_denied_before_fake_lookup() -> None:
    """A foreign requester cannot cause even a local durable checkpoint lookup for a graph run."""
    repository = _CountingCheckpointRepository()
    service = CheckpointResumeService(repository, clock=lambda: NOW)
    record = _run(
        _graph_definition(),
        run_id=RunId("run-graph-checkpoint"),
        status=RunStatus.WAITING_FOR_APPROVAL,
        graph_initialized=True,
    )

    denied = service.resume(FOREIGN_ORGANIZATION_ID, record, CORRELATION_ID)

    assert not denied.is_success and denied.error is not None
    assert denied.error.code is ErrorCode.AUTHORIZATION_DENIED
    assert repository.lookup_calls == 0


def test_full_migration_evidence_retires_legacy_execution_and_cancels_active_lease() -> None:
    """All six local graph migration proofs retire LegacyEngine immediately and durably."""
    evidence = MigrationEvidenceService(
        InMemoryMigrationEvidenceRepository(), clock=lambda: NOW
    )
    retirement = LegacyEngineRetirement(evidence)
    active = retirement.begin_legacy_execution(
        ORGANIZATION_ID, RunId("run-active-legacy"), CORRELATION_ID
    )
    assert active.is_success and active.value is not None
    gates = tuple(
        MigrationGateEvidence(gate, True, (EVIDENCE_HASH,)) for gate in MigrationGate
    )

    result = retirement.assess_and_retire(CORRELATION_ID, EVIDENCE_HASH, gates)
    new_legacy_execution = retirement.begin_legacy_execution(
        ORGANIZATION_ID, RunId("run-retired-legacy"), CORRELATION_ID
    )

    assert result.is_success and result.value is not None
    assert result.value.assessment.is_satisfied
    assert result.value.retired_now
    assert result.value.retirement_evidence is not None
    assert active.value.retirement_evidence == result.value.retirement_evidence
    assert not retirement.is_available()
    assert not new_legacy_execution.is_success


def test_graph_e1_evidence_is_target_local_and_independently_retained() -> None:
    """A completed bounded graph run records an independent local E1 pass without overclaiming."""
    outcome, adapter = _completed_graph_outcome()
    service = ProductBarEvidenceService(
        InMemoryProductBarEvidenceRepository(), clock=lambda: NOW
    )
    recorded = service.record_evidence(
        ORGANIZATION_ID,
        CORRELATION_ID,
        ProductBarCriterion.E1,
        ProductBarEvidenceOutcome.PASS,
        run_ids=(outcome.record.run_id,),
        evidence_hashes=(GraphCompiler.definition_digest(_graph_definition()),),
        command_results=(
            ProductBarCommandResult(
                command="python -m pytest --tb=short -q tests/integration/graph_engine",
                exit_code=0,
                output_digest=EVIDENCE_HASH,
                completed_at=NOW,
            ),
        ),
        supporting_references=(
            EvidenceReference(
                evidence_id=EvidenceId("graph-e1-run"),
                digest=outcome.record.workflow_definition_digest,
                kind="target-local-graph-run",
            ),
        ),
    )
    assessment = service.assess(ORGANIZATION_ID, CORRELATION_ID)

    assert recorded.is_success and recorded.value is not None
    assert recorded.value.run_ids == (outcome.record.run_id,)
    assert recorded.value.command_results[0].exit_code == 0
    assert recorded.value.supporting_references[0].kind == "target-local-graph-run"
    assert [dict(arguments) for arguments in adapter.invocations] == [
        {"account_id": "local-account"}
    ]
    assert assessment.is_success and assessment.value is not None
    e1_entry = assessment.value.entries[0]
    assert e1_entry.criterion is ProductBarCriterion.E1
    assert e1_entry.outcome is ProductBarEvidenceOutcome.PASS
    assert assessment.value.status is ProductBarStatus.INCOMPLETE
