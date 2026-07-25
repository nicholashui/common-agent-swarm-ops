"""Trusted request context, client-authority guards, and API authorization dependencies."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol, runtime_checkable

from fastapi import Request, status

from app.api.v1.errors import PublicApiException
from app.api.v1.schemas import PublicError
from app.models.contracts import ErrorCode
from app.models.identifiers import ActorId, CorrelationId, OrganizationId, new_correlation_id

AUTHENTICATED_CONTEXT_STATE_KEY = "authenticated_context"
REQUEST_CORRELATION_ID_STATE_KEY = "request_correlation_id"
_AUTHORITY_FIELD_NAMES = frozenset(
    {
        "actor",
        "actor_id",
        "organization",
        "organization_id",
        "permission",
        "permissions",
        "tenant",
        "tenant_id",
    }
)


class AuthorizationAction(StrEnum):
    """The protected operation categories exposed by the public API."""

    READ = "read"
    MUTATION = "mutation"
    AGGREGATE = "aggregate"
    TOPIC = "topic"
    REPLAY = "replay"
    ARTIFACT_REFERENCE = "artifact_reference"
    TOOL_OPERATION = "tool_operation"


@dataclass(frozen=True, slots=True)
class ProtectedOperation:
    """An opaque, route-derived protected operation submitted for authorization."""

    action: AuthorizationAction
    subject: str

    @classmethod
    def from_request(cls, request: Request) -> ProtectedOperation:
        """Classify the route without accepting a client-selected authority subject."""
        path = request.url.path
        if "/replay" in path:
            action = AuthorizationAction.REPLAY
        elif path.endswith("/events") or "/topics/" in path:
            action = AuthorizationAction.TOPIC
        elif "/artifacts" in path:
            action = AuthorizationAction.ARTIFACT_REFERENCE
        elif "/dispatch" in path or "/operations/" in path:
            action = AuthorizationAction.TOOL_OPERATION
        elif path.endswith("/memory/retrieve"):
            action = AuthorizationAction.AGGREGATE
        elif request.method in {"POST", "PUT", "PATCH", "DELETE"}:
            action = AuthorizationAction.MUTATION
        else:
            action = AuthorizationAction.READ
        route = request.scope.get("route")
        subject = getattr(route, "path", path)
        return cls(action=action, subject=f"route:{subject}")


@dataclass(frozen=True, slots=True)
class AuthenticatedRequestContext:
    """Immutable identity and permissions established only by server-side authentication."""

    tenant_id: OrganizationId
    actor_id: ActorId
    correlation_id: CorrelationId
    permissions: frozenset[str] = frozenset()

    def __post_init__(self) -> None:
        """Reject incomplete identities and freeze normalized server-derived permissions."""
        values = (self.tenant_id, self.actor_id, self.correlation_id)
        if any(not str(value).strip() for value in values):
            raise ValueError("Authenticated request context fields must be non-empty.")
        permissions = frozenset(str(permission).strip() for permission in self.permissions)
        if any(not permission for permission in permissions):
            raise ValueError("Authenticated request context permissions must be non-empty strings.")
        object.__setattr__(self, "permissions", permissions)

    @property
    def organization_id(self) -> OrganizationId:
        """Return the tenant identifier using durable-record terminology."""
        return self.tenant_id


@runtime_checkable
class AuthorizationService(Protocol):
    """Authorize every protected API operation before a protected lookup or effect."""

    def authorize(
        self, context: AuthenticatedRequestContext, operation: ProtectedOperation
    ) -> None:
        """Allow the operation or raise the single enumeration-safe authorization error."""


class PermissionAuthorizationService:
    """Fail-closed permission authorization for route-derived protected operations."""

    def authorize(
        self, context: AuthenticatedRequestContext, operation: ProtectedOperation
    ) -> None:
        """Require the action permission, a control-plane wildcard, or the global wildcard."""
        required_permission = f"control_plane:{operation.action.value}"
        permitted = {"*", "control_plane:*", required_permission, operation.action.value}
        if context.permissions.isdisjoint(permitted):
            _raise_enumeration_safe_authorization_error(context.correlation_id)


class ContextConflictGuard:
    """Reject browser-supplied authority values before a handler can access protected state."""

    async def ensure_no_conflict(
        self, request: Request, context: AuthenticatedRequestContext
    ) -> None:
        """Deny all client authority fields, including matching values, without revealing state."""
        await reject_client_authority_fields(request, context.correlation_id)

    async def has_client_authority_field(self, request: Request) -> bool:
        """Return whether the request contains authority that only the server may derive."""
        return (
            self._has_authority_field(request.path_params)
            or self._has_authority_field(dict(request.query_params.multi_items()))
            or self._has_authority_field(dict(request.headers.items()))
            or self._has_authority_field(await self._json_body(request))
        )

    def _has_authority_field(self, value: object) -> bool:
        if isinstance(value, Mapping):
            for key, item in value.items():
                if self._normalized_field_name(str(key)) in _AUTHORITY_FIELD_NAMES:
                    return True
                if self._has_authority_field(item):
                    return True
        if isinstance(value, list | tuple):
            return any(self._has_authority_field(item) for item in value)
        return False

    @staticmethod
    async def _json_body(request: Request) -> object:
        try:
            body = await request.body()
        except RuntimeError:
            # Unit-level request objects without an ASGI receive channel have no body to inspect.
            return None
        if not body:
            return None
        try:
            return json.loads(body)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _normalized_field_name(value: str) -> str:
        normalized = value.strip().lower().replace("-", "_")
        return normalized.removeprefix("x_")


async def reject_client_authority_fields(request: Request, correlation_id: CorrelationId) -> None:
    """Reject client authority before FastAPI validates or invokes a protected route."""
    if await ContextConflictGuard().has_client_authority_field(request):
        _raise_enumeration_safe_authorization_error(correlation_id)


def set_authenticated_request_context(
    request: Request, context: AuthenticatedRequestContext
) -> None:
    """Store the immutable context produced by trusted server-side identity processing only."""
    setattr(request.state, AUTHENTICATED_CONTEXT_STATE_KEY, context)
    setattr(request.state, REQUEST_CORRELATION_ID_STATE_KEY, context.correlation_id)


def get_authorization_service(request: Request) -> AuthorizationService:
    """Return the deployment-provided authorizer or the secure in-process default."""
    try:
        configured = request.app.state.authorization_service
    except (AttributeError, KeyError, RuntimeError):
        return _DEFAULT_AUTHORIZATION_SERVICE
    if isinstance(configured, AuthorizationService):
        return configured
    return _DEFAULT_AUTHORIZATION_SERVICE


def get_request_correlation_id(request: Request) -> CorrelationId:
    """Return the correlation identifier shared by response, error, and durable request work."""
    context = getattr(request.state, AUTHENTICATED_CONTEXT_STATE_KEY, None)
    if isinstance(context, AuthenticatedRequestContext):
        return context.correlation_id

    correlation_id = getattr(request.state, REQUEST_CORRELATION_ID_STATE_KEY, None)
    if isinstance(correlation_id, str) and correlation_id.strip():
        return CorrelationId(correlation_id)

    correlation_id = new_correlation_id()
    setattr(request.state, REQUEST_CORRELATION_ID_STATE_KEY, correlation_id)
    return correlation_id


async def get_authenticated_request_context(request: Request) -> AuthenticatedRequestContext:
    """Derive the trusted context, reject conflicts, and authorize before every route handler."""
    context = getattr(request.state, AUTHENTICATED_CONTEXT_STATE_KEY, None)
    if not isinstance(context, AuthenticatedRequestContext):
        correlation_id = get_request_correlation_id(request)
        raise PublicApiException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error=PublicError(
                code=ErrorCode.AUTHENTICATION_REQUIRED.value,
                message="Authentication is required for control-plane access.",
                correlation_id=str(correlation_id),
            ),
        )

    await ContextConflictGuard().ensure_no_conflict(request, context)
    get_authorization_service(request).authorize(context, ProtectedOperation.from_request(request))
    return context


def _raise_enumeration_safe_authorization_error(correlation_id: CorrelationId) -> None:
    """Emit the only externally observable result for hidden, foreign, absent, or denied state."""
    raise PublicApiException(
        status_code=status.HTTP_403_FORBIDDEN,
        error=PublicError(
            code=ErrorCode.AUTHORIZATION_DENIED.value,
            message="You are not authorized to perform this action.",
            correlation_id=str(correlation_id),
        ),
    )


_DEFAULT_AUTHORIZATION_SERVICE = PermissionAuthorizationService()
