"""Isolated FastAPI integration coverage for backend-redesign access boundaries."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import cast

import pytest
from fastapi.testclient import TestClient
from httpx import Response

from app.api.v1.dependencies import AuthenticatedRequestContext, get_authenticated_request_context
from app.api.v1.services import ControlPlaneServices, get_control_plane_services
from app.main import create_app
from app.models.identifiers import ActorId, CorrelationId, OrganizationId

# **Validates: Requirements 2.1, 2.2, 2.4, 2.5, 2.7**

ORGANIZATION_ID = OrganizationId("org-access-integration")
CORRELATION_ID = CorrelationId("corr-access-integration")


@dataclass
class ApiFixture:
    """One in-memory public API composition with a server-derived context."""

    client: TestClient
    contexts: dict[str, AuthenticatedRequestContext]


@pytest.fixture
def api_fixture() -> Iterator[ApiFixture]:
    """Provide deterministic API dependencies without an external identity provider."""
    application = create_app()
    contexts = {
        "current": AuthenticatedRequestContext(
            ORGANIZATION_ID, ActorId("trusted-actor"), CORRELATION_ID
        )
    }
    services = ControlPlaneServices()
    application.dependency_overrides[get_authenticated_request_context] = lambda: contexts[
        "current"
    ]
    application.dependency_overrides[get_control_plane_services] = lambda: services
    with TestClient(application) as client:
        yield ApiFixture(client, contexts)
    application.dependency_overrides.clear()


def _body(response: Response) -> object:
    """Return either an already-public response payload or its stable data envelope."""
    payload = cast(dict[str, object], response.json())
    return payload.get("data", payload)


def _safe_error(response: Response) -> tuple[int, str, str, bool]:
    """Compare only the externally observable authorization outcome."""
    payload = cast(dict[str, object], response.json())
    error = cast(dict[str, object], payload["error"])
    return (
        response.status_code,
        str(error["code"]),
        str(error["message"]),
        bool(error["retryable"]),
    )


def _create_run(client: TestClient) -> str:
    """Create one valid workflow run entirely through the versioned public API."""
    manifest = {
        "pack_id": "operations",
        "agents": [
            {
                "agent_id": "ops.planner",
                "status": "registered",
                "allowed_tools": ["crm.lookup"],
            }
        ],
    }
    assert client.post("/api/v1/domains/register", json={"manifest": manifest}).status_code == 200
    definition = {
        "definition_type": "workflow_dna",
        "id": "ops.onboarding",
        "version": "1.0.0",
        "owner_id": "ops.owner",
        "authorization_id": "approval-1",
        "engine": "legacy",
        "execution_budget": {
            "max_node_visits": 2,
            "max_handoffs": 1,
            "max_wall_clock_seconds": 30,
            "max_tool_requests": 2,
        },
        "memory": {"reads": ["organization"], "writes": ["workflow"]},
        "risk_gate_ids": ["low-risk"],
        "rollback": {
            "plan_id": "compensate.crm",
            "compensation_step_ids": ["step-1"],
        },
        "steps": [
            {
                "id": "step-1",
                "agent_id": "ops.planner",
                "tool_ids": ["crm.lookup"],
                "memory_reads": ["organization"],
                "memory_writes": ["workflow"],
            }
        ],
    }
    definition_response = client.post(
        "/api/v1/workflows/definitions", json={"definition": definition}
    )
    assert definition_response.status_code == 201
    run = client.post("/api/v1/workflows/ops.onboarding/run", json={"version": "1.0.0"})
    assert run.status_code == 201
    return str(cast(dict[str, object], _body(run))["run_id"])


def test_server_identity_is_derived_and_client_authority_is_rejected(
    api_fixture: ApiFixture,
) -> None:
    """Server state supplies identity; a body authority value yields the safe denial first."""
    with TestClient(create_app()) as anonymous_client:
        anonymous = anonymous_client.get("/api/v1/context")
    assert anonymous.status_code == 401
    assert _safe_error(anonymous)[1] == "authentication_required"

    identity = api_fixture.client.get("/api/v1/context")
    assert identity.status_code == 200
    assert _body(identity) == {
        "organization_id": str(ORGANIZATION_ID),
        "actor_id": "trusted-actor",
        "correlation_id": str(CORRELATION_ID),
    }
    conflict = api_fixture.client.post(
        "/api/v1/workflow-runs/dispatch",
        json={
            "run_id": "unavailable",
            "idempotency_key": "conflict-key",
            "confirm": True,
            "actor_id": "attacker",
        },
    )
    assert _safe_error(conflict) == (
        403,
        "authorization_denied",
        "You are not authorized to perform this action.",
        False,
    )


def test_absent_and_foreign_runs_have_the_same_enumeration_safe_failure(
    api_fixture: ApiFixture,
) -> None:
    """A foreign run and an absent run have no externally distinguishable outcome."""
    run_id = _create_run(api_fixture.client)
    api_fixture.contexts["current"] = AuthenticatedRequestContext(
        OrganizationId("foreign-org"),
        ActorId("foreign-actor"),
        CorrelationId("foreign-correlation"),
    )
    foreign = api_fixture.client.get(f"/api/v1/workflow-runs/{run_id}")
    api_fixture.contexts["current"] = AuthenticatedRequestContext(
        ORGANIZATION_ID, ActorId("trusted-actor"), CORRELATION_ID
    )
    absent = api_fixture.client.get("/api/v1/workflow-runs/not-present")
    assert _safe_error(foreign) == _safe_error(absent)


def test_dispatch_requires_an_idempotency_key_and_replays_its_stored_response(
    api_fixture: ApiFixture,
) -> None:
    """Missing keys have no effect, while same actor/key requests replay without redispatch."""
    run_id = _create_run(api_fixture.client)
    event_url = f"/api/v1/workflow-runs/{run_id}/events"
    before = cast(list[object], _body(api_fixture.client.get(event_url)))
    missing_key = api_fixture.client.post(
        "/api/v1/workflow-runs/dispatch", json={"run_id": run_id, "confirm": True}
    )
    assert missing_key.status_code == 422
    assert _safe_error(missing_key)[1] == "validation_failed"
    assert len(cast(list[object], _body(api_fixture.client.get(event_url)))) == len(before)

    request = {"run_id": run_id, "idempotency_key": "replay-key", "confirm": True}
    first = api_fixture.client.post("/api/v1/workflow-runs/dispatch", json=request)
    replay = api_fixture.client.post("/api/v1/workflow-runs/dispatch", json=request)
    assert first.status_code == replay.status_code == 200
    assert _body(replay) == _body(first)
    assert len(cast(list[object], _body(api_fixture.client.get(event_url)))) == len(before) + 2


def test_default_composition_mounts_only_versioned_authorized_routes() -> None:
    """The app factory wires trusted context and public services through one versioned surface."""
    context = AuthenticatedRequestContext(
        ORGANIZATION_ID,
        ActorId("composed-actor"),
        CorrelationId("composed-correlation"),
        permissions=frozenset({"control_plane:*"}),
    )
    application = create_app(trusted_context_resolver=lambda _request: context)

    with TestClient(application) as client:
        identity = client.get("/api/v1/context")
        stream = client.get("/api/v1/events/work/stream")

    assert identity.status_code == 200
    assert _body(identity) == {
        "organization_id": str(ORGANIZATION_ID),
        "actor_id": "composed-actor",
        "correlation_id": "composed-correlation",
    }
    assert stream.status_code == 200
    assert stream.headers["content-type"].startswith("text/event-stream")
    assert all(getattr(route, "path", "").startswith("/api/v1/") for route in application.routes)
    composition = application.state.control_plane
    assert composition.services.command_service is application.state.command_service
    assert composition.services.idempotency_service is application.state.idempotency_service
