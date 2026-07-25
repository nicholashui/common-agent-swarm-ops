"""Focused tests for the versioned public control-plane boundary."""

from __future__ import annotations

import asyncio
from dataclasses import FrozenInstanceError, dataclass, field

import pytest
from fastapi import FastAPI
from starlette.requests import Request

from app.api.v1.dependencies import (
    AuthenticatedRequestContext,
    AuthorizationAction,
    ProtectedOperation,
    get_authenticated_request_context,
    set_authenticated_request_context,
)
from app.api.v1.errors import PublicApiException
from app.main import API_V1_PREFIX, app, is_public_api_path
from app.models.identifiers import ActorId, CorrelationId, OrganizationId


@dataclass
class RecordingAuthorizationService:
    """Record only route-derived operations; it never receives resource lookup results."""

    operations: list[ProtectedOperation] = field(default_factory=list)

    def authorize(
        self, _context: AuthenticatedRequestContext, operation: ProtectedOperation
    ) -> None:
        self.operations.append(operation)


def _request(
    headers: list[tuple[bytes, bytes]] | None = None,
    *,
    path: str = "/api/v1/context",
    query_string: bytes = b"",
    body: bytes = b"",
    application: FastAPI | None = None,
) -> Request:
    scope: dict[str, object] = {
        "type": "http",
        "method": "GET",
        "path": path,
        "query_string": query_string,
        "headers": headers or [],
        "state": {},
    }
    if application is not None:
        scope["app"] = application
    request = Request(scope)
    request._body = body
    return request


def _context(
    *, permissions: frozenset[str] = frozenset({"control_plane:*"})
) -> AuthenticatedRequestContext:
    return AuthenticatedRequestContext(
        tenant_id=OrganizationId("tenant-1"),
        actor_id=ActorId("actor-1"),
        correlation_id=CorrelationId("correlation-1"),
        permissions=permissions,
    )


def test_public_routes_are_versioned_and_undocumented() -> None:
    """The app mounts only versioned public routes and disables framework docs."""
    assert all(
        getattr(route, "path", "").startswith(f"{API_V1_PREFIX}/") for route in app.routes
    )
    assert app.docs_url is None
    assert app.redoc_url is None
    assert app.openapi_url is None
    assert is_public_api_path("/api/v1/context")
    assert not is_public_api_path("/api/v1")
    assert not is_public_api_path("/docs")


def test_authenticated_context_comes_only_from_trusted_request_state() -> None:
    """Client-supplied headers cannot substitute for a server-authenticated context."""
    request = _request([(b"x-tenant-id", b"client-tenant")])
    with pytest.raises(PublicApiException) as error:
        asyncio.run(get_authenticated_request_context(request))
    assert error.value.status_code == 401

    trusted_request = _request()
    context = _context()
    set_authenticated_request_context(trusted_request, context)

    assert asyncio.run(get_authenticated_request_context(trusted_request)) == context
    assert context.organization_id == OrganizationId("tenant-1")


def test_authenticated_context_is_immutable_and_rejects_blank_identity_fields() -> None:
    """Trusted server identity cannot be altered after construction or contain blank values."""
    context = _context()
    with pytest.raises(FrozenInstanceError):
        context.actor_id = ActorId("attacker")  # type: ignore[misc]
    with pytest.raises(ValueError, match="must be non-empty"):
        AuthenticatedRequestContext(
            tenant_id=OrganizationId("tenant-1"),
            actor_id=ActorId(" "),
            correlation_id=CorrelationId("correlation-1"),
        )


@pytest.mark.parametrize(
    ("query_string", "body"),
    [
        (b"actor_id=attacker", b""),
        (b"", b'{"organization_id":"foreign-tenant"}'),
    ],
)
def test_context_conflicts_fail_before_authorization_or_resource_access(
    query_string: bytes, body: bytes
) -> None:
    """Browser authority values always receive the one safe error before downstream access."""
    application = FastAPI()
    authorizer = RecordingAuthorizationService()
    application.state.authorization_service = authorizer
    request = _request(
        path="/api/v1/workflow-runs/run-1",
        query_string=query_string,
        body=body,
        application=application,
    )
    set_authenticated_request_context(request, _context())

    with pytest.raises(PublicApiException) as error:
        asyncio.run(get_authenticated_request_context(request))

    assert error.value.status_code == 403
    assert error.value.error.code == "authorization_denied"
    assert authorizer.operations == []


def test_authorization_service_receives_route_derived_operation_before_handler() -> None:
    """Protected aggregate access is authorized from the route, not from client authority data."""
    application = FastAPI()
    authorizer = RecordingAuthorizationService()
    application.state.authorization_service = authorizer
    request = _request(path="/api/v1/memory/retrieve", application=application)
    context = _context()
    set_authenticated_request_context(request, context)

    assert asyncio.run(get_authenticated_request_context(request)) == context
    assert authorizer.operations == [
        ProtectedOperation(AuthorizationAction.AGGREGATE, "route:/api/v1/memory/retrieve")
    ]


def test_missing_permission_uses_the_enumeration_safe_authorization_error() -> None:
    """A denied protected route does not reveal a distinguishable authorization reason."""
    request = _request(path="/api/v1/workflow-runs/run-1")
    set_authenticated_request_context(request, _context(permissions=frozenset()))

    with pytest.raises(PublicApiException) as error:
        asyncio.run(get_authenticated_request_context(request))

    assert error.value.status_code == 403
    assert error.value.error.code == "authorization_denied"
