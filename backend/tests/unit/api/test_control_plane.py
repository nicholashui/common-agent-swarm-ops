"""Focused tests for the versioned public control-plane boundary."""

from __future__ import annotations

import asyncio

import pytest
from fastapi import HTTPException
from starlette.requests import Request

from app.api.v1.dependencies import (
    AuthenticatedRequestContext,
    get_authenticated_request_context,
    set_authenticated_request_context,
)
from app.main import API_V1_PREFIX, app, is_public_api_path
from app.models.identifiers import ActorId, CorrelationId, OrganizationId


def _request(headers: list[tuple[bytes, bytes]] | None = None) -> Request:
    return Request({"type": "http", "headers": headers or [], "state": {}})


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
    with pytest.raises(HTTPException) as error:
        asyncio.run(get_authenticated_request_context(request))
    assert error.value.status_code == 401

    context = AuthenticatedRequestContext(
        tenant_id=OrganizationId("tenant-1"),
        actor_id=ActorId("actor-1"),
        correlation_id=CorrelationId("correlation-1"),
    )
    set_authenticated_request_context(request, context)

    assert asyncio.run(get_authenticated_request_context(request)) == context
    assert context.organization_id == OrganizationId("tenant-1")


def test_authenticated_context_rejects_blank_identity_fields() -> None:
    """Incomplete trusted identities cannot be stored for an API request."""
    with pytest.raises(ValueError, match="must be non-empty"):
        AuthenticatedRequestContext(
            tenant_id=OrganizationId("tenant-1"),
            actor_id=ActorId(" "),
            correlation_id=CorrelationId("correlation-1"),
        )
