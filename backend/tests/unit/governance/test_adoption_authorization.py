"""Focused adoption authorization and broker boundary tests."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

import pytest

from app.audit import AuditWriter
from app.governance.authorization import (
    ApprovalState,
    AuthorizationContext,
    DataAccessRequest,
    OutboundRequest,
    ScopeConstraint,
)
from app.governance.tool_broker import (
    BrokerDenialReason,
    HostToolBroker,
    LocalAdapterResult,
    ToolRequest,
)
from app.models.audit import AuditEvent
from app.models.common import CompatibilityRange
from app.models.contracts import ErrorCode, ErrorDetail, Result


@dataclass
class _AuditRepository:
    available: bool = True
    events: list[AuditEvent] = field(default_factory=list)

    def append(self, event: AuditEvent) -> Result[AuditEvent, ErrorDetail]:
        if not self.available:
            return Result.failure(
                ErrorDetail(
                    code=ErrorCode.AUDIT_UNAVAILABLE,
                    message="audit unavailable",
                    correlation_id=event.metadata.correlation_id,
                )
            )
        self.events.append(event)
        return Result.success(event)


@dataclass
class _Adapter:
    adapter_id: str = "crm.lookup"
    version: str = "1.0.0"
    local_only: bool = True
    invocations: list[Mapping[str, object]] = field(default_factory=list)

    def execute(self, arguments: Mapping[str, object]) -> LocalAdapterResult:
        self.invocations.append(arguments)
        return LocalAdapterResult("completed", "effect-digest", reversible=True)


def _context() -> AuthorizationContext:
    allowed_tools = frozenset({"crm.lookup"})
    return AuthorizationContext(
        agent_id="agent-1",
        step_id="step-1",
        organization_id="org-1",
        actor_id="actor-1",
        correlation_id="correlation-1",
        agent_allowed_tools=allowed_tools,
        step_declared_tools=allowed_tools,
        role_allowed_tools=allowed_tools,
        organization_allowed_tools=allowed_tools,
        risk_allowed_tools=allowed_tools,
        approval_state=ApprovalState.NOT_REQUIRED,
        domain_id="domain-1",
        pack_version="1.2.0",
        supported_pack_range=CompatibilityRange("1.0.0", "2.0.0"),
        declared_memory_scopes=frozenset({"memory-1"}),
        declared_outbound_destinations=frozenset({"https://api.example.test"}),
        declared_tool_ids=allowed_tools,
    )


def _data_access(**changes: str) -> DataAccessRequest:
    values = {
        "organization_id": "org-1",
        "domain_id": "domain-1",
        "pack_version": "1.2.0",
        "agent_id": "agent-1",
        "memory_scope": "memory-1",
    }
    values.update(changes)
    return DataAccessRequest(**values)


@pytest.mark.parametrize(
    ("field", "value", "constraint"),
    [
        ("organization_id", "org-foreign", ScopeConstraint.ORGANIZATION_SCOPE),
        ("domain_id", "domain-foreign", ScopeConstraint.DOMAIN_SCOPE),
        ("pack_version", "3.0.0", ScopeConstraint.PACK_VERSION_RANGE),
        ("agent_id", "agent-foreign", ScopeConstraint.AGENT_IDENTITY),
        ("memory_scope", "memory-undeclared", ScopeConstraint.MEMORY_SCOPE),
    ],
)
def test_data_access_requires_every_adoption_scope(
    field: str, value: str, constraint: ScopeConstraint
) -> None:
    """Every organization, domain, pack, agent, and memory boundary is independent."""
    from app.governance.authorization import AuthorizationService

    decision = AuthorizationService().authorize_data_access(
        _context(), _data_access(**{field: value})
    )

    assert not decision.permitted
    assert constraint in decision.denied_constraints


def test_broker_denies_scoped_tool_before_adapter_dispatch_and_audits() -> None:
    """A denied access target cannot reach an otherwise authorized local adapter."""
    adapter = _Adapter()
    audit_repository = _AuditRepository()
    broker = HostToolBroker((adapter,), AuditWriter(audit_repository))

    result = broker.request_tool(
        ToolRequest(
            "crm.lookup",
            {"account_id": "acct-1"},
            data_access=_data_access(memory_scope="memory-undeclared"),
        ),
        _context(),
    )

    assert not result.allowed
    assert ScopeConstraint.MEMORY_SCOPE in result.authorization.denied_constraints
    assert not adapter.invocations
    assert result.denial_audit_recorded is True
    assert len(audit_repository.events) == 1


def test_outbound_destination_must_be_declared_before_tool_dispatch() -> None:
    """Only an exact Host-declared outbound destination may accompany a tool call."""
    adapter = _Adapter()
    audit_repository = _AuditRepository()
    broker = HostToolBroker((adapter,), AuditWriter(audit_repository))

    allowed = broker.request_tool(
        ToolRequest(
            "crm.lookup",
            {"account_id": "acct-1"},
            outbound_destination="https://api.example.test",
        ),
        _context(),
    )
    denied = broker.request_tool(
        ToolRequest(
            "crm.lookup",
            {"account_id": "acct-2"},
            outbound_destination="https://evil.example.test",
        ),
        _context(),
    )

    assert allowed.allowed
    assert not denied.allowed
    assert ScopeConstraint.OUTBOUND_DESTINATION in denied.authorization.denied_constraints
    assert BrokerDenialReason.UNDECLARED_OUTBOUND_DESTINATION in denied.denial_reasons
    assert len(adapter.invocations) == 1
    assert len(audit_repository.events) == 1


def test_explicit_outbound_authorization_is_audited_without_dispatch() -> None:
    """The standalone outbound gate returns a decision and never performs I/O itself."""
    audit_repository = _AuditRepository()
    broker = HostToolBroker((), AuditWriter(audit_repository))

    decision = broker.request_outbound(
        OutboundRequest("https://evil.example.test"),
        _context(),
    )

    assert not decision.permitted
    assert decision.denied_constraints == (ScopeConstraint.OUTBOUND_DESTINATION,)
    assert len(audit_repository.events) == 1


def test_denial_remains_effective_when_audit_writer_fails() -> None:
    """An audit outage cannot convert a denied scope request into an adapter effect."""
    adapter = _Adapter()
    broker = HostToolBroker((adapter,), AuditWriter(_AuditRepository(available=False)))

    result = broker.request_tool(
        ToolRequest(
            "crm.lookup",
            {"account_id": "acct-1"},
            data_access=_data_access(organization_id="org-foreign"),
        ),
        _context(),
    )

    assert not result.allowed
    assert result.denial_audit_recorded is False
    assert not adapter.invocations


def test_partial_flattened_scope_is_not_treated_as_a_legacy_request() -> None:
    """Transport scope fields must be complete before a tool can be dispatched."""
    adapter = _Adapter()
    broker = HostToolBroker((adapter,), AuditWriter(_AuditRepository()))

    result = broker.request_tool(
        ToolRequest("crm.lookup", {}, organization_id="org-1"),
        _context(),
    )

    assert not result.allowed
    assert BrokerDenialReason.INVALID_TOOL_INPUT in result.denial_reasons
    assert not adapter.invocations
