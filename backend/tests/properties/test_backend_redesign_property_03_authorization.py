"""Property checks for non-disclosing trusted-context authorization."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field

from fastapi import FastAPI
from hypothesis import given, settings, strategies as st
from starlette.requests import Request

from app.api.v1.dependencies import (
    AuthenticatedRequestContext,
    AuthorizationAction,
    PermissionAuthorizationService,
    ProtectedOperation,
    get_authenticated_request_context,
    set_authenticated_request_context,
)
from app.api.v1.errors import PublicApiException
from app.models.identifiers import ActorId, CorrelationId, OrganizationId

AuthorizationOutcome = tuple[int, str, str, str, bool, int]

_SAFE_SUFFIXES = st.text(alphabet="abcdefghijklmnopqrstuvwxyz0123456789", min_size=1, max_size=12)
_TENANT_RELATIONS = st.sampled_from(("owned", "foreign"))
_VISIBILITY_STATES = st.sampled_from(("visible", "hidden", "absent"))
_EXPECTED_DENIAL: AuthorizationOutcome = (
    403,
    "authorization_denied",
    "You are not authorized to perform this action.",
    "property-3-correlation",
    False,
    0,
)


@dataclass
class _LookupDeliverySpy:
    """Expose lookups and deliveries that handlers may perform only after authorization."""

    lookup_calls: int = 0
    delivery_calls: int = 0

    def lookup(self, _organization_id: OrganizationId, _subject: str) -> object:
        self.lookup_calls += 1
        return {"authorized": "projection"}

    def deliver(self, _projection: object) -> None:
        self.delivery_calls += 1


@dataclass
class _RecordingPermissionAuthorizer:
    """Delegate safe denials to production authorization while recording its pre-handler call."""

    operations: list[ProtectedOperation] = field(default_factory=list)

    def authorize(
        self, context: AuthenticatedRequestContext, operation: ProtectedOperation
    ) -> None:
        self.operations.append(operation)
        PermissionAuthorizationService().authorize(context, operation)


def _request(application: FastAPI, path: str, has_authority_conflict: bool) -> Request:
    query_string = b"tenant_id=client-selected-tenant" if has_authority_conflict else b""
    scope: dict[str, object] = {
        "type": "http",
        "method": "GET",
        "path": path,
        "query_string": query_string,
        "headers": [],
        "state": {},
        "app": application,
    }
    return Request(scope)


def _outcome(error: PublicApiException) -> AuthorizationOutcome:
    return (
        error.status_code,
        error.error.code,
        error.error.message,
        error.error.correlation_id,
        error.error.retryable,
        len(error.error.fields),
    )


def _read_after_authorization(
    request: Request, spy: _LookupDeliverySpy
) -> AuthorizationOutcome | None:
    try:
        context = asyncio.run(get_authenticated_request_context(request))
    except PublicApiException as error:
        return _outcome(error)
    spy.deliver(spy.lookup(context.organization_id, request.url.path))
    return None


# **Validates: Requirements 2.2, 2.3, 2.4, 10.2, 10.6**
# Feature: backend-redesign, Property 3
@settings(max_examples=100)
@given(
    subject_suffix=_SAFE_SUFFIXES,
    tenant_relation=_TENANT_RELATIONS,
    visibility=_VISIBILITY_STATES,
    has_read_permission=st.booleans(),
    has_authority_conflict=st.booleans(),
)
def test_property_3_trusted_context_authorization_is_non_disclosing(
    subject_suffix: str,
    tenant_relation: str,
    visibility: str,
    has_read_permission: bool,
    has_authority_conflict: bool,
) -> None:
    """Conflict, absent, hidden, foreign, and denied paths share one result before lookup."""
    access_is_allowed = (
        tenant_relation == "owned" and visibility == "visible" and has_read_permission
    )
    permissions = frozenset({"control_plane:read"}) if access_is_allowed else frozenset()
    context = AuthenticatedRequestContext(
        tenant_id=OrganizationId("trusted-tenant"),
        actor_id=ActorId("trusted-actor"),
        correlation_id=CorrelationId("property-3-correlation"),
        permissions=permissions,
    )
    application = FastAPI()
    authorizer = _RecordingPermissionAuthorizer()
    application.state.authorization_service = authorizer
    path = f"/api/v1/workflow-runs/subject-{subject_suffix}"
    request = _request(application, path, has_authority_conflict)
    set_authenticated_request_context(request, context)
    spy = _LookupDeliverySpy()

    outcome = _read_after_authorization(request, spy)
    expected_operation = ProtectedOperation(AuthorizationAction.READ, f"route:{path}")

    if has_authority_conflict or not access_is_allowed:
        assert outcome == _EXPECTED_DENIAL
        assert spy.lookup_calls == 0
        assert spy.delivery_calls == 0
        assert authorizer.operations == ([] if has_authority_conflict else [expected_operation])
    else:
        assert outcome is None
        assert spy.lookup_calls == 1
        assert spy.delivery_calls == 1
        assert authorizer.operations == [expected_operation]
