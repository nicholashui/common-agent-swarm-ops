"""Focused examples for Host-only, fail-closed tool brokerage."""

from __future__ import annotations

from dataclasses import dataclass, field, replace

import pytest

from app.audit import AuditWriter
from app.governance.authorization import (
    ApprovalState,
    AuthorizationConstraint,
    AuthorizationContext,
)
from app.governance.operation_guard import OperationGuard
from app.governance.tool_broker import (
    BrokerDenialReason,
    HostToolBroker,
    LocalAdapterResult,
    ToolRequest,
)
from app.models.audit import AuditEvent
from app.models.contracts import ErrorCode, ErrorDetail, Result
from app.models.identifiers import CorrelationId
from app.models.operations import OperationDecisionStatus, OperationKind, RequestedOperation


@dataclass
class RecordingAuditRepository:
    """In-memory audit storage that can deterministically simulate an outage."""

    available: bool = True
    events: list[AuditEvent] = field(default_factory=list)

    def append(self, event: AuditEvent) -> Result[AuditEvent, ErrorDetail]:
        if not self.available:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.REPOSITORY_UNAVAILABLE,
                    "audit unavailable",
                    CorrelationId("corr"),
                )
            )
        self.events.append(event)
        return Result.success(event)


@dataclass
class RecordingLocalAdapter:
    """A deterministic local adapter fixture with no external resource access."""

    adapter_id: str
    version: str = "1.0.0"
    local_only: bool = True
    invocations: list[object] = field(default_factory=list)

    def execute(self, arguments: object) -> LocalAdapterResult:
        self.invocations.append(arguments)
        return LocalAdapterResult("completed", "effect-digest", reversible=True)


@pytest.fixture
def context() -> AuthorizationContext:
    """Return a Host-derived context allowing the two registered fixture tools."""
    tools = frozenset({"crm.lookup", "audit.log"})
    return AuthorizationContext(
        agent_id="ops.planner",
        step_id="lookup",
        organization_id="org-1",
        actor_id="actor-1",
        correlation_id="correlation-1",
        agent_allowed_tools=tools,
        step_declared_tools=tools,
        role_allowed_tools=tools,
        organization_allowed_tools=tools,
        risk_allowed_tools=tools,
        approval_state=ApprovalState.NOT_REQUIRED,
    )


def test_broker_invokes_only_an_allowlisted_local_adapter_when_all_constraints_pass(
    context: AuthorizationContext,
) -> None:
    """A complete intersection produces one deterministic local effect."""
    adapter = RecordingLocalAdapter("crm.lookup")
    broker = HostToolBroker((adapter,), AuditWriter(RecordingAuditRepository()))

    result = broker.request_tool(ToolRequest("crm.lookup", {"account_id": "acct-1"}), context)

    assert result.allowed
    assert result.invoked
    assert result.effect is not None
    assert result.effect.adapter_id == "crm.lookup"
    assert len(adapter.invocations) == 1


@pytest.mark.parametrize("constraint", list(AuthorizationConstraint))
def test_each_failed_intersection_constraint_denies_without_an_adapter_effect(
    context: AuthorizationContext, constraint: AuthorizationConstraint
) -> None:
    """Each factor is independently required and every denial is audited."""
    adapter = RecordingLocalAdapter("crm.lookup")
    audit_repository = RecordingAuditRepository()
    denied_context = _context_denied_by(context, constraint)
    broker = HostToolBroker((adapter,), AuditWriter(audit_repository))

    result = broker.request_tool(
        ToolRequest("crm.lookup", {"account_id": "acct-1"}),
        denied_context,
    )

    assert not result.allowed
    assert not result.invoked
    assert result.effect is None
    assert constraint in result.authorization.denied_constraints
    assert result.denial_audit_recorded
    assert not adapter.invocations
    assert len(audit_repository.events) == 1


def test_denied_call_stays_denied_when_audit_recording_fails(
    context: AuthorizationContext,
) -> None:
    """Audit unavailability cannot turn a denied request into an adapter call."""
    adapter = RecordingLocalAdapter("crm.lookup")
    unavailable_audit = RecordingAuditRepository(available=False)
    denied_context = replace(context, agent_allowed_tools=frozenset())

    result = HostToolBroker((adapter,), AuditWriter(unavailable_audit)).request_tool(
        ToolRequest("crm.lookup", {"account_id": "acct-1"}), denied_context
    )

    assert not result.allowed
    assert not result.invoked
    assert result.denial_audit_recorded is False
    assert not adapter.invocations


def test_distinct_later_call_is_rechecked_and_unknown_tools_never_run(
    context: AuthorizationContext,
) -> None:
    """No earlier allowance authorizes a later distinct or unregistered request."""
    crm = RecordingLocalAdapter("crm.lookup")
    audit = RecordingLocalAdapter("audit.log")
    broker = HostToolBroker((crm, audit), AuditWriter(RecordingAuditRepository()))
    first = broker.request_tool(ToolRequest("crm.lookup", {"account_id": "acct-1"}), context)
    second = broker.request_tool(
        ToolRequest("audit.log", {"message": "review"}),
        replace(context, step_declared_tools=frozenset({"crm.lookup"})),
    )
    unknown = broker.request_tool(ToolRequest("billing.charge", {"amount": 1}), context)

    assert first.allowed and first.invoked
    assert not second.allowed and not second.invoked
    assert AuthorizationConstraint.STEP_DECLARED_TOOLS in second.authorization.denied_constraints
    assert not unknown.allowed and not unknown.invoked
    assert BrokerDenialReason.LOCAL_ADAPTER_NOT_ALLOWLISTED in unknown.denial_reasons
    assert len(crm.invocations) == 1
    assert not audit.invocations


@pytest.mark.parametrize(
    "arguments",
    [
        {"value": lambda: None},
        {"command": "echo unsafe"},
        {"credential": "not-accepted"},
        {"target": "https://example.test/action"},
    ],
)
def test_callables_shell_commands_credentials_and_urls_are_never_invoked(
    context: AuthorizationContext, arguments: dict[str, object]
) -> None:
    """Agent request input is constrained to safe data, never executable or credentialed data."""
    adapter = RecordingLocalAdapter("crm.lookup")
    result = HostToolBroker((adapter,), AuditWriter(RecordingAuditRepository())).request_tool(
        ToolRequest("crm.lookup", arguments), context
    )

    assert not result.allowed
    assert not result.invoked
    assert result.effect is None
    assert BrokerDenialReason.INVALID_TOOL_INPUT in result.denial_reasons
    assert not adapter.invocations


def _context_denied_by(
    context: AuthorizationContext,
    constraint: AuthorizationConstraint,
) -> AuthorizationContext:
    """Return an otherwise-valid context missing exactly one authorization factor."""
    if constraint is AuthorizationConstraint.AGENT_ALLOWED_TOOLS:
        return replace(context, agent_allowed_tools=frozenset())
    if constraint is AuthorizationConstraint.STEP_DECLARED_TOOLS:
        return replace(context, step_declared_tools=frozenset())
    if constraint is AuthorizationConstraint.ROLE_PERMISSIONS:
        return replace(context, role_allowed_tools=frozenset())
    if constraint is AuthorizationConstraint.ORGANIZATION_SCOPE:
        return replace(context, organization_allowed_tools=frozenset())
    if constraint is AuthorizationConstraint.RISK_POLICY:
        return replace(context, risk_allowed_tools=frozenset())
    return replace(context, approval_state=ApprovalState.PENDING)


def test_undeliverable_prohibited_error_blocks_a_later_production_adapter_effect() -> None:
    """A failed prohibited-error response trips the latch before a later production change."""
    adapter = RecordingLocalAdapter("crm.lookup")
    guard = OperationGuard()

    delivery = guard.assess_and_deliver_prohibited_error(
        (RequestedOperation("automatic", OperationKind.PRODUCTION_PROMOTION, True, True),),
        lambda _: False,
    )
    later = guard.assess(
        (RequestedOperation("production-change", OperationKind.OTHER, targets_production=True),)
    )
    if later.decisions[0].status is OperationDecisionStatus.PERMITTED:
        adapter.execute({"change_id": "production-change"})

    assert delivery.error_delivered is False
    assert delivery.assessment.production_changes_blocked
    assert later.decisions[0].status is OperationDecisionStatus.BLOCKED_BY_PRODUCTION_LATCH
    assert not adapter.invocations
