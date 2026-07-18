"""Property tests for approval-gate submission retention and resume authorization."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime

from hypothesis import given, settings, strategies as st

from app.audit import AuditWriter
from app.governance.approvals import (
    ActionPreview,
    ApprovalDecisionValue,
    ApprovalGate,
    ApprovalGateStatus,
    GovernanceService,
)
from app.governance.authorization import ApprovalState, AuthorizationContext, ToolInputValue
from app.governance.tool_broker import HostToolBroker, LocalAdapterResult, ToolRequest
from app.models.common import RecordMetadata
from app.models.identifiers import (
    ActorId,
    CorrelationId,
    OrganizationId,
    RecordId,
    RunId,
    WorkflowDefinitionId,
)
from app.models.runs import RunRecord, RunStatus, WorkflowEngineKind
from app.repositories.approval_repository import InMemoryApprovalRepository
from app.repositories.run_repository import InMemoryRunRepository
from tests.fakes.broker import InMemoryAuditRepository

# Feature: generic-swarm-business-os, Property 14: Approval gates retain submissions and
# reauthorize effects.
# **Validates: Requirements 5.6, 5.7, 5.9, 5.10, 5.11**

NOW = datetime(2025, 1, 1, tzinfo=UTC)
ORG_ID = OrganizationId("org-1")
CORRELATION_ID = CorrelationId("correlation-1")
RUN_ID = RunId("run-1")
TOOL_ID = "crm.lookup"


@dataclass
class RecordingAdapter:
    """Deterministic local adapter that records only authorized invocations."""

    adapter_id: str = TOOL_ID
    version: str = "test-v1"
    local_only: bool = True
    invocations: list[Mapping[str, ToolInputValue]] = field(default_factory=list)

    def execute(self, arguments: Mapping[str, ToolInputValue]) -> LocalAdapterResult:
        self.invocations.append(arguments)
        return LocalAdapterResult("completed", "effect-digest", reversible=True)


@dataclass
class ApprovalFixture:
    """One isolated approval-gate lifecycle with deterministic local dependencies."""

    service: GovernanceService
    approvals: InMemoryApprovalRepository
    runs: InMemoryRunRepository
    adapter: RecordingAdapter


def _fixture() -> ApprovalFixture:
    runs = InMemoryRunRepository()
    run = RunRecord(
        metadata=RecordMetadata(
            record_id=RecordId("run-record-1"),
            organization_id=ORG_ID,
            correlation_id=CORRELATION_ID,
            schema_version=1,
            version=1,
            created_at=NOW,
            updated_at=NOW,
        ),
        run_id=RUN_ID,
        workflow_definition_id=WorkflowDefinitionId("ops.approval-workflow"),
        workflow_definition_version="1.0.0",
        workflow_definition_digest="definition-digest",
        engine=WorkflowEngineKind.LEGACY,
        status=RunStatus.DISPATCHING,
        created_for_dispatch_at=NOW,
    )
    assert runs.create(run).is_success
    approvals = InMemoryApprovalRepository()
    adapter = RecordingAdapter()
    service = GovernanceService(
        runs,
        approvals,
        HostToolBroker((adapter,), AuditWriter(InMemoryAuditRepository())),
        clock=lambda: NOW,
    )
    return ApprovalFixture(service, approvals, runs, adapter)


def _preview() -> ActionPreview:
    return ActionPreview(
        action_id="crm-update",
        summary="Update the approved local customer record.",
        intended_effect="A local CRM record will be updated.",
        supporting_evidence=("case-123",),
    )


def _pause(fixture: ApprovalFixture) -> ApprovalGate:
    result = fixture.service.pause_before_effect(
        ORG_ID,
        RUN_ID,
        CORRELATION_ID,
        "critical",
        _preview(),
    )
    assert result.is_success and result.value is not None
    return result.value


def _resume_context(allows_tool: bool) -> AuthorizationContext:
    tools = frozenset({TOOL_ID}) if allows_tool else frozenset()
    return AuthorizationContext(
        agent_id="ops.planner",
        step_id="crm-update",
        organization_id=ORG_ID,
        actor_id="actor-1",
        correlation_id=CORRELATION_ID,
        agent_allowed_tools=tools,
        step_declared_tools=tools,
        role_allowed_tools=tools,
        organization_allowed_tools=tools,
        risk_allowed_tools=tools,
        approval_state=ApprovalState.PENDING,
    )


def _run_status(fixture: ApprovalFixture) -> RunStatus:
    result = fixture.runs.get_by_run_id(ORG_ID, RUN_ID)
    assert result.is_success and result.value is not None
    return result.value.status


@settings(max_examples=100, deadline=None)
@given(
    reason_length=st.sampled_from((0, 1, 1_000, 1_001)),
    selected_value=st.sampled_from(
        (
            ApprovalDecisionValue.APPROVED,
            ApprovalDecisionValue.DENIED,
            "",
            "defer",
            "pending",
        )
    ),
    authorization_changed_at_resume=st.booleans(),
)
def test_approval_gates_retain_every_submission_and_reauthorize_before_effect(
    reason_length: int,
    selected_value: str,
    authorization_changed_at_resume: bool,
) -> None:
    """All boundary submissions remain durable, and only freshly authorized approvals resume."""
    fixture = _fixture()
    gate = _pause(fixture)
    reason = "r" * reason_length

    assert gate.status is ApprovalGateStatus.PAUSED
    assert _run_status(fixture) is RunStatus.WAITING_FOR_APPROVAL
    assert fixture.adapter.invocations == []

    result = fixture.service.submit_decision(
        ORG_ID,
        gate.approval_id,
        ActorId("actor-1"),
        selected_value,
        reason,
        _resume_context(allows_tool=not authorization_changed_at_resume),
        ToolRequest(TOOL_ID, {"account_id": "acct-1"}),
        CORRELATION_ID,
    )

    assert result.is_success and result.value is not None
    outcome = result.value
    assert outcome.decision.selected_value == selected_value
    assert outcome.decision.reason == reason
    assert outcome.decision.reason_is_valid == (1 <= reason_length <= 1_000)
    assert outcome.decision.value_is_valid == (
        selected_value in {ApprovalDecisionValue.APPROVED, ApprovalDecisionValue.DENIED}
    )
    decisions = fixture.approvals.decisions(ORG_ID, gate.approval_id)
    assert decisions.is_success and decisions.value == (outcome.decision,)

    approval_can_resume = outcome.decision.is_valid_approval and not authorization_changed_at_resume
    if approval_can_resume:
        assert outcome.resumed
        assert outcome.invocation is not None and outcome.invocation.allowed
        assert outcome.gate.status is ApprovalGateStatus.RESUMED
        assert _run_status(fixture) is RunStatus.DISPATCHING
        assert len(fixture.adapter.invocations) == 1
    else:
        assert not outcome.resumed
        assert outcome.gate.status is ApprovalGateStatus.PAUSED
        assert _run_status(fixture) is RunStatus.WAITING_FOR_APPROVAL
        assert fixture.adapter.invocations == []
        if outcome.decision.is_valid_approval:
            assert outcome.invocation is not None and not outcome.invocation.allowed
        else:
            assert outcome.invocation is None
