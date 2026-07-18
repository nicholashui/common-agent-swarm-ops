"""Dependencies that expose server-authenticated request identity to API handlers."""

from __future__ import annotations

from dataclasses import dataclass

from fastapi import HTTPException, Request, status

from app.models.identifiers import ActorId, CorrelationId, OrganizationId

AUTHENTICATED_CONTEXT_STATE_KEY = "authenticated_context"


@dataclass(frozen=True, slots=True)
class AuthenticatedRequestContext:
    """Identity established by trusted server-side authentication middleware."""

    tenant_id: OrganizationId
    actor_id: ActorId
    correlation_id: CorrelationId

    def __post_init__(self) -> None:
        """Reject incomplete identities before they can enter request state."""
        values = (self.tenant_id, self.actor_id, self.correlation_id)
        if any(not str(value).strip() for value in values):
            raise ValueError("Authenticated request context fields must be non-empty.")

    @property
    def organization_id(self) -> OrganizationId:
        """Return the tenant identifier using durable-record terminology."""
        return self.tenant_id


def set_authenticated_request_context(
    request: Request, context: AuthenticatedRequestContext
) -> None:
    """Store a context after trusted authentication; never derive it from client input."""
    setattr(request.state, AUTHENTICATED_CONTEXT_STATE_KEY, context)


async def get_authenticated_request_context(request: Request) -> AuthenticatedRequestContext:
    """Return the trusted context or fail closed before a control-plane operation."""
    context = getattr(request.state, AUTHENTICATED_CONTEXT_STATE_KEY, None)
    if isinstance(context, AuthenticatedRequestContext):
        return context

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={
            "code": "authenticated_request_context_required",
            "message": "Authentication is required for control-plane access.",
        },
    )
