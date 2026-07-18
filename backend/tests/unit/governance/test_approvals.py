"""Focused examples for approval gates, immutable submissions, and resume authorization."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime

import pytest

from app.audit import AuditWriter
from app.governance.approvals import (
    ActionPreview,
    ApprovalDecisionValue,
    ApprovalGate,
    ApprovalGateStatus,
    ApprovalResumeEngine,
    GovernanceService,
)
from app.governance.authorization import ApprovalState, AuthorizationContext, ToolInputValue
from app.governance.tool_broker import (
    HostToolBroker,
    LocalAdapterResult,
    ToolInvocationResult,
    ToolRequest,
)
from app.models.audit import AuditEvent
from app.models.common import RecordMetadata
from app.models.contracts import ErrorDetail, Result
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

NOW = datetime(2025, 1, 1, tzinfo=UTC)
ORG_ID = OrganizationId("org-1")
CORRELATION_ID = CorrelationId("correlation-1")
RUN_ID = RunId("run-1")


@dataclass
class RecordingAuditRepository:
    """Append-only local audit fixture."""

    events: list[AuditEvent] = field(default_factory=list)

    def append(self, event: AuditEvent) -> Result[AuditEvent, ErrorDetail]:
        self.events.append(event)
        return Result.success(event)


@dataclass
class RecordingAdapter:
    """Deterministic local adapter that records only invocation count."""
    adapter_id: str = "crm.lookup"
    version: str = "1.0.0"
    local_only: bool = True
    invocations: list[Mapping[str, ToolInputValue]] = field(default_factory=list)

    def execute(self, arguments: Mapping[str, ToolInputValue]) -> LocalAdapterResult:
        self.invocations.append(arguments)
        return LocalAdapterResult("completed", "effect-digest", reversible=True)


@dataclass
class ApprovalFixture:
    """The repositories and host services used by one deterministic gate scenario."""

    service: GovernanceService
    approvals: InMemoryApprovalRepository
    runs: InMemoryRunRepository
    adapter: RecordingAdapter


@dataclass
class RecordingApprovalResumeEngine:
    """A local engine seam that records the state it receives before using the broker."""

    broker: HostToolBroker
    observations: list[tuple[RunStatus, ApprovalGateStatus, ApprovalState]] = field(
        default_factory=list
    )

    def resume_from_approval(
        self,
        run: RunRecord,
        gate: ApprovalGate,
        authorization_context: AuthorizationContext,
        tool_request: ToolRequest,
    ) -> ToolInvocationResult:
        self.observations.append(
            (run.status, gate.status, authorization_context.approval_state)
        )
        return self.broker.request_tool(tool_request, authorization_context)


def _fixture(
    resume_engine_factory: Callable[[HostToolBroker], ApprovalResumeEngine] | None = None,
) -> ApprovalFixture:
    runs = InMemoryRunRepository()
    record = RunRecord(
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
        workflow_definition_id=WorkflowDefinitionId("ops.onboarding"),
        workflow_definition_version="1.0.0",
        workflow_definition_digest="definition-digest",
        engine=WorkflowEngineKind.LEGACY,
        status=RunStatus.DISPATCHING,
        created_for_dispatch_at=NOW,
    )
    assert runs.create(record).is_success
    approvals = InMemoryApprovalRepository()
    adapter = RecordingAdapter()
    broker = HostToolBroker((adapter,), AuditWriter(RecordingAuditRepository()))
    resume_engine = (
        resume_engine_factory(broker) if resume_engine_factory is not None else None
    )
    return ApprovalFixture(
        service=GovernanceService(
            runs,
            approvals,
            broker,
            clock=lambda: NOW,
            resume_engine=resume_engine,
        ),
        approvals=approvals,
        runs=runs,
        adapter=adapter,
    )


def _preview() -> ActionPreview:
    return ActionPreview(
        action_id="crm-update",
        summary="Update the approved customer account.",
        intended_effect="A local CRM record will be updated.",
        rollback_preview="Restore the previous local CRM value.",
        supporting_evidence=("case-123",),
        confidence=0.9,
        uncertainty="The local CRM effect may require later correction.",
        correction_control="Cancel this approval and edit the case.",
    )


def _pause(fixture: ApprovalFixture) -> ApprovalGate:
    paused = fixture.service.pause_before_effect(
        ORG_ID,
        RUN_ID,
        CORRELATION_ID,
        "critical",
        _preview(),
    )
    assert paused.is_success
    assert paused.value is not None
    return paused.value


def _context(allowed: bool = True) -> AuthorizationContext:
    tools = frozenset({"crm.lookup"}) if allowed else frozenset()
    return AuthorizationContext(
        agent_id="ops.planner",
        step_id="update",
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
    assert result.is_success
    assert result.value is not None
    return result.value.status


def test_pause_before_effect_persists_the_human_centered_preview_and_pauses_the_run() -> None:
    """A critical effect receives a visible preview before execution can be requested."""
    fixture = _fixture()

    gate = _pause(fixture)

    assert gate.status is ApprovalGateStatus.PAUSED
    assert gate.action_preview == _preview()
    assert _run_status(fixture) is RunStatus.WAITING_FOR_APPROVAL
    assert not fixture.adapter.invocations


@pytest.mark.parametrize(
    ("selected_value", "reason", "reason_is_valid", "value_is_valid"),
    [
        (ApprovalDecisionValue.APPROVED, "", False, True),
        (ApprovalDecisionValue.APPROVED, "x" * 1001, False, True),
        ("defer", "Need a human review.", True, False),
    ],
)
def test_invalid_submissions_are_immutable_and_leave_the_run_paused(
    selected_value: str,
    reason: str,
    reason_is_valid: bool,
    value_is_valid: bool,
) -> None:
    """Invalid reason bounds and values are retained without invoking the pending effect."""
    fixture = _fixture()
    gate = _pause(fixture)

    result = fixture.service.submit_decision(
        ORG_ID,
        gate.approval_id,
        ActorId("actor-1"),
        selected_value,
        reason,
        _context(),
        ToolRequest("crm.lookup", {"account_id": "acct-1"}),
        CORRELATION_ID,
    )

    assert result.is_success
    assert result.value is not None
    assert not result.value.resumed
    assert result.value.decision.reason_is_valid is reason_is_valid
    assert result.value.decision.value_is_valid is value_is_valid
    decisions = fixture.approvals.decisions(ORG_ID, gate.approval_id)
    assert decisions.is_success and decisions.value == (result.value.decision,)
    assert _run_status(fixture) is RunStatus.WAITING_FOR_APPROVAL
    assert not fixture.adapter.invocations


def test_valid_denial_is_retained_and_keeps_the_run_paused() -> None:
    """A valid human denial never resumes the previously paused critical effect."""
    fixture = _fixture()
    gate = _pause(fixture)

    result = fixture.service.submit_decision(
        ORG_ID,
        gate.approval_id,
        ActorId("actor-1"),
        ApprovalDecisionValue.DENIED,
        "The customer requested no change.",
        _context(),
        ToolRequest("crm.lookup", {"account_id": "acct-1"}),
        CORRELATION_ID,
    )

    assert result.is_success
    assert result.value is not None
    assert result.value.decision.is_valid_denial
    assert not result.value.resumed
    assert result.value.gate.status is ApprovalGateStatus.PAUSED
    assert _run_status(fixture) is RunStatus.WAITING_FOR_APPROVAL
    assert not fixture.adapter.invocations


def test_valid_approval_reauthorizes_and_invokes_only_after_the_run_resumes() -> None:
    """A valid approval activates a fresh broker check rather than caching pending authority."""
    fixture = _fixture()
    gate = _pause(fixture)

    result = fixture.service.submit_decision(
        ORG_ID,
        gate.approval_id,
        ActorId("actor-1"),
        ApprovalDecisionValue.APPROVED,
        "The documented customer request is verified.",
        _context(),
        ToolRequest("crm.lookup", {"account_id": "acct-1"}),
        CORRELATION_ID,
    )

    assert result.is_success
    assert result.value is not None
    assert result.value.resumed
    assert result.value.invocation is not None and result.value.invocation.allowed
    assert result.value.gate.status is ApprovalGateStatus.RESUMED
    assert _run_status(fixture) is RunStatus.DISPATCHING
    assert len(fixture.adapter.invocations) == 1


def test_approval_does_not_bypass_a_changed_authorization_intersection() -> None:
    """A valid approval returns to paused when fresh resume-time authorization denies the tool."""
    fixture = _fixture()
    gate = _pause(fixture)

    result = fixture.service.submit_decision(
        ORG_ID,
        gate.approval_id,
        ActorId("actor-1"),
        ApprovalDecisionValue.APPROVED,
        "The documented customer request is verified.",
        _context(allowed=False),
        ToolRequest("crm.lookup", {"account_id": "acct-1"}),
        CORRELATION_ID,
    )

    assert result.is_success
    assert result.value is not None
    assert not result.value.resumed
    assert result.value.invocation is not None and not result.value.invocation.allowed
    assert result.value.gate.status is ApprovalGateStatus.PAUSED
    assert _run_status(fixture) is RunStatus.WAITING_FOR_APPROVAL
    assert not fixture.adapter.invocations


def test_every_invalid_or_denied_submission_is_retained_while_the_gate_remains_paused() -> None:
    """Sequential invalid and denied submissions remain an immutable gate-local history."""
    fixture = _fixture()
    gate = _pause(fixture)

    invalid = fixture.service.submit_decision(
        ORG_ID,
        gate.approval_id,
        ActorId("actor-1"),
        "defer",
        "Need a human review.",
        _context(),
        ToolRequest("crm.lookup", {"account_id": "acct-1"}),
        CORRELATION_ID,
    )
    denied = fixture.service.submit_decision(
        ORG_ID,
        gate.approval_id,
        ActorId("actor-1"),
        ApprovalDecisionValue.DENIED,
        "The customer requested no change.",
        _context(),
        ToolRequest("crm.lookup", {"account_id": "acct-1"}),
        CORRELATION_ID,
    )

    assert invalid.is_success and denied.is_success
    decisions = fixture.approvals.decisions(ORG_ID, gate.approval_id)
    assert decisions.is_success
    assert decisions.value is not None
    assert tuple(decision.selected_value for decision in decisions.value) == ("defer", "denied")
    assert _run_status(fixture) is RunStatus.WAITING_FOR_APPROVAL
    assert not fixture.adapter.invocations


def test_valid_approval_reaches_the_broker_through_the_claimed_run_engine_seam() -> None:
    """The resume seam sees a claimed gate and dispatching run before broker invocation."""
    engines: list[RecordingApprovalResumeEngine] = []

    def make_resume_engine(broker: HostToolBroker) -> ApprovalResumeEngine:
        engine = RecordingApprovalResumeEngine(broker)
        engines.append(engine)
        return engine

    fixture = _fixture(make_resume_engine)
    gate = _pause(fixture)

    result = fixture.service.submit_decision(
        ORG_ID,
        gate.approval_id,
        ActorId("actor-1"),
        ApprovalDecisionValue.APPROVED,
        "The documented customer request is verified.",
        _context(),
        ToolRequest("crm.lookup", {"account_id": "acct-1"}),
        CORRELATION_ID,
    )

    assert result.is_success and result.value is not None and result.value.resumed
    assert engines[0].observations == [
        (
            RunStatus.DISPATCHING,
            ApprovalGateStatus.REAUTHORIZING,
            ApprovalState.APPROVED,
        )
    ]
    assert len(fixture.adapter.invocations) == 1


def test_approval_repository_rejects_conflicts_and_hides_foreign_gate_data() -> None:
    """Duplicate submissions conflict, while another organization cannot inspect or append."""
    fixture = _fixture()
    gate = _pause(fixture)
    other_organization = OrganizationId("org-2")

    duplicate_gate = fixture.approvals.create(gate)
    assert not duplicate_gate.is_success
    assert duplicate_gate.error is not None
    assert duplicate_gate.error.code.value == "conflict"
    assert not fixture.approvals.get_by_approval_id(other_organization, gate.approval_id).is_success

    submission = fixture.service.submit_decision(
        ORG_ID,
        gate.approval_id,
        ActorId("actor-1"),
        ApprovalDecisionValue.APPROVED,
        "",
        _context(),
        ToolRequest("crm.lookup", {"account_id": "acct-1"}),
        CORRELATION_ID,
    )

    assert submission.is_success and submission.value is not None
    decision = submission.value.decision
    assert not decision.reason_is_valid
    foreign_decision = replace(
        decision,
        metadata=replace(
            decision.metadata,
            record_id=RecordId("foreign-decision"),
            organization_id=other_organization,
        ),
        decision_id=RecordId("foreign-decision"),
    )
    foreign_append = fixture.approvals.append_decision(foreign_decision)
    duplicate_append = fixture.approvals.append_decision(decision)

    assert not foreign_append.is_success
    assert foreign_append.error is not None
    assert foreign_append.error.code.value == "not_found"
    assert not duplicate_append.is_success
    assert duplicate_append.error is not None
    assert duplicate_append.error.code.value == "conflict"
    assert not fixture.approvals.decisions(other_organization, gate.approval_id).is_success
    decisions = fixture.approvals.decisions(ORG_ID, gate.approval_id)
    assert decisions.is_success and decisions.value == (decision,)
    assert not fixture.adapter.invocations
