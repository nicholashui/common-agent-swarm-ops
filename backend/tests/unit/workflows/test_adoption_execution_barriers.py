"""Deterministic invocation and declared workflow-policy barriers."""

from __future__ import annotations

from datetime import UTC, datetime

from app.models.common import RecordMetadata
from app.models.contracts import ErrorCode
from app.models.control_plane import InvocationAssociation
from app.models.identifiers import (
    AgentId,
    CorrelationId,
    DomainId,
    InvocationId,
    OrganizationId,
    RecordId,
    RunId,
)
from app.models.runs import RunRecord
from app.repositories.run_repository import InMemoryRunRepository
from app.runs.service import RunService
from app.workflows.policy import (
    ApprovalStatus,
    WorkflowAction,
    WorkflowActionKind,
    WorkflowPolicyBarrier,
)
from app.workflows.validator import RegisteredReferences
from tests.fakes.adoption import DeterministicAdoptionRepositories, FakeFailurePlan

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_ORGANIZATION = OrganizationId("org-adoption")
_CORRELATION = CorrelationId("corr-adoption")


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


def _association(run_id: RunId) -> InvocationAssociation:
    return InvocationAssociation(
        metadata=_metadata("invocation-record"),
        invocation_id=InvocationId("invocation-1"),
        organization_id=_ORGANIZATION,
        domain_id=DomainId("domain-1"),
        pack_version="1.0.0",
        agent_id=AgentId("ops.planner"),
        workflow_id="ops.workflow",
        run_id=run_id,
        correlation_id=_CORRELATION,
    )


def _references() -> RegisteredReferences:
    return RegisteredReferences(
        agent_ids=frozenset({"ops.planner"}),
        tool_ids=frozenset({"crm.lookup"}),
        memory_scope_ids=frozenset({"read.scope", "write.scope"}),
        risk_gate_ids=frozenset({"risk.low"}),
        rollback_plan_ids=frozenset({"rollback.crm"}),
        authorization_ids=frozenset({"approval-1"}),
    )


def _definition() -> dict[str, object]:
    return {
        "definition_type": "workflow_dna",
        "id": "ops.workflow",
        "version": "1.0.0",
        "owner_id": "ops.owner",
        "authorization_id": "approval-1",
        "engine": "legacy",
        "execution_budget": {
            "max_node_visits": 1,
            "max_handoffs": 1,
            "max_wall_clock_seconds": 30,
            "max_tool_requests": 1,
        },
        "memory": {"reads": ["read.scope"], "writes": ["write.scope"]},
        "risk_gate_ids": ["risk.low"],
        "rollback": {"plan_id": "rollback.crm", "compensation_step_ids": ["step-1"]},
        "steps": [
            {
                "id": "step-1",
                "agent_id": "ops.planner",
                "tool_ids": ["crm.lookup"],
                "memory_reads": ["read.scope"],
                "memory_writes": ["write.scope"],
            }
        ],
    }


def _run_service(
    run_repository: InMemoryRunRepository,
    adoption: DeterministicAdoptionRepositories,
) -> RunService:
    return RunService(
        run_repository,
        _references(),
        clock=lambda: _NOW,
        invocation_association_repository=adoption.invocations,
        audit_repository=adoption.audit,
    )


def _create_run(service: RunService) -> RunRecord:
    result = service.create_queued_run(_ORGANIZATION, _CORRELATION, _definition())
    assert result.is_success and result.value is not None
    return result.value


def test_association_persists_before_dispatch_starts_node() -> None:
    adoption = DeterministicAdoptionRepositories()
    service = _run_service(InMemoryRunRepository(), adoption)
    run = _create_run(service)
    started: list[str] = []

    result = service.dispatch(
        _ORGANIZATION,
        run.run_id,
        "dispatch-1",
        lambda claimed: started.append(str(claimed.invocation_association_id)),
        _CORRELATION,
        association=_association(run.run_id),
    )

    assert result.is_success
    assert started == ["invocation-1"]
    assert adoption.invocations.records()[0].run_id == run.run_id


def test_association_persistence_failure_denies_and_audits_without_starting() -> None:
    plan = FakeFailurePlan(persistence_operations={"invocation.append"})
    adoption = DeterministicAdoptionRepositories(plan)
    service = _run_service(InMemoryRunRepository(), adoption)
    run = _create_run(service)
    started: list[str] = []

    result = service.dispatch(
        _ORGANIZATION,
        run.run_id,
        "dispatch-1",
        lambda _claimed: started.append("started"),
        _CORRELATION,
        association=_association(run.run_id),
    )

    assert not result.is_success
    assert result.error is not None and result.error.code is ErrorCode.AUTHORIZATION_DENIED
    assert started == []
    assert len(adoption.audit.records) == 1
    assert adoption.audit.records[0].action == "invocation.association.denied"


def test_policy_barrier_denies_budget_and_memory_escapes() -> None:
    barrier = WorkflowPolicyBarrier(_definition())

    first_node = barrier.authorize_action({"id": "node-1", "kind": "node"})
    second_node = barrier.authorize_action({"id": "node-2", "kind": "node"})
    denied_read = barrier.authorize_action(
        {"id": "read-1", "kind": "memory_read", "memory_scope": "foreign.scope"}
    )
    denied_write = barrier.authorize_action(
        {"id": "write-1", "kind": "memory_write", "memory_scope": "read.scope"}
    )

    assert first_node.is_allowed
    assert not second_node.is_allowed
    assert not denied_read.is_allowed
    assert not denied_write.is_allowed


def test_policy_barrier_blocks_pending_approval_and_runs_declared_rollback() -> None:
    rollback_actions: list[str] = []

    def rollback(action: WorkflowAction) -> bool:
        rollback_actions.append(action.action_id)
        return True

    barrier = WorkflowPolicyBarrier(
        {
            **_definition(),
            "approval": {"required": True},
        },
        rollback=rollback,
    )

    pending = barrier.authorize_action(
        {
            "id": "tool-1",
            "kind": WorkflowActionKind.TOOL,
            "requires_approval": True,
            "approval_id": "approval-1",
        },
        approval_status=ApprovalStatus.PENDING,
    )
    failed = barrier.execute_action(
        {"id": "tool-2", "kind": "tool"},
        lambda: (_ for _ in ()).throw(RuntimeError("adapter failed")),
        approval_status=ApprovalStatus.APPROVED,
    )

    assert not pending.is_allowed
    assert failed.kind.value == "failed_recoverable"
    assert rollback_actions == ["tool-2"]
