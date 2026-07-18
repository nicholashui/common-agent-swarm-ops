"""Deterministic local fakes shared by broker and adapter tests."""

from __future__ import annotations

from dataclasses import dataclass, field

from app.governance.authorization import ApprovalState, AuthorizationContext
from app.models.audit import AuditEvent
from app.models.contracts import ErrorDetail, Result


@dataclass
class InMemoryAuditRepository:
    """Append-only local audit storage with no I/O outside the test process."""

    events: list[AuditEvent] = field(default_factory=list)

    def append(self, event: AuditEvent) -> Result[AuditEvent, ErrorDetail]:
        """Retain one audit event for assertions."""
        self.events.append(event)
        return Result.success(event)


def authorized_context(adapter_ids: tuple[str, ...]) -> AuthorizationContext:
    """Return Host-derived authority permitting exactly the supplied adapters."""
    allowed = frozenset(adapter_ids)
    return AuthorizationContext(
        agent_id="ops.planner",
        step_id="local-adapter-step",
        organization_id="org-1",
        actor_id="actor-1",
        correlation_id="correlation-1",
        agent_allowed_tools=allowed,
        step_declared_tools=allowed,
        role_allowed_tools=allowed,
        organization_allowed_tools=allowed,
        risk_allowed_tools=allowed,
        approval_state=ApprovalState.NOT_REQUIRED,
    )
