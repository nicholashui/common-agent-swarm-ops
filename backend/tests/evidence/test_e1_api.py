"""Target-local API evidence for the versioned LegacyEngine control-plane path."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, replace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.dependencies import AuthenticatedRequestContext, get_authenticated_request_context
from app.api.v1.services import ControlPlaneServices, get_control_plane_services
from app.governance.approvals import ActionPreview
from app.governance.authorization import ApprovalState, AuthorizationContext
from app.governance.tool_broker import ToolRequest
from app.main import API_V1_PREFIX, create_app
from app.models.common import OptimisticTransition
from app.models.identifiers import ActorId, ApprovalId, CorrelationId, OrganizationId, RunId
from app.models.redaction import REDACTED

ORGANIZATION_ID = OrganizationId("org-e1-api")
CORRELATION_ID = CorrelationId("corr-e1-api")


@dataclass
class ApiFixture:
    """One deterministic API app with only server-derived authenticated context."""

    application: FastAPI
    client: TestClient
    services: ControlPlaneServices
    context: AuthenticatedRequestContext


@pytest.fixture
def api_fixture() -> Iterator[ApiFixture]:
    application = create_app()
    services = ControlPlaneServices()
    context = AuthenticatedRequestContext(
        tenant_id=ORGANIZATION_ID,
        actor_id=ActorId("e1-operator"),
        correlation_id=CORRELATION_ID,
    )
    application.dependency_overrides[get_authenticated_request_context] = lambda: context
    application.dependency_overrides[get_control_plane_services] = lambda: services
    with TestClient(application) as client:
        yield ApiFixture(application, client, services, context)
    application.dependency_overrides.clear()


def _manifest() -> dict[str, object]:
    return {
        "pack_id": "e1-operations",
        "agents": [
            {
                "agent_id": "ops.planner",
                "status": "registered",
                "allowed_tools": ["crm.lookup"],
            }
        ],
    }


def _definition() -> dict[str, object]:
    return {
        "definition_type": "workflow_dna",
        "id": "ops.e1-api",
        "version": "1.0.0",
        "owner_id": "ops.owner",
        "authorization_id": "approval-1",
        "engine": "legacy",
        "execution_budget": {
            "max_node_visits": 1,
            "max_handoffs": 1,
            "max_wall_clock_seconds": 30,
            "max_tool_requests": 1,
        },
        "memory": {"reads": ["organization"], "writes": ["workflow"]},
        "risk_gate_ids": ["low-risk"],
        "rollback": {"plan_id": "compensate.crm", "compensation_step_ids": ["step-1"]},
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


def _register_and_queue_run(fixture: ApiFixture) -> str:
    registered = fixture.client.post("/api/v1/domains/register", json={"manifest": _manifest()})
    assert registered.status_code == 200
    definition = fixture.client.post(
        "/api/v1/workflows/definitions", json={"definition": _definition()}
    )
    assert definition.status_code == 201
    created = fixture.client.post("/api/v1/workflows/ops.e1-api/run", json={"version": "1.0.0"})
    assert created.status_code == 201
    assert created.json()["status"] == "queued"
    assert created.json()["engine"] == "legacy"
    return str(created.json()["run_id"])


def _set_sensitive_output(fixture: ApiFixture, run_id: str) -> None:
    current = fixture.services.run_repository.get_by_run_id(ORGANIZATION_ID, RunId(run_id))
    assert current.is_success and current.value is not None
    record = current.value
    updated = replace(
        record,
        metadata=replace(record.metadata, version=record.metadata.version + 1),
        output={"api_token": "e1-secret", "summary": "operator-safe summary"},
    )
    persisted = fixture.services.run_repository.transition(
        updated,
        OptimisticTransition(
            record_id=record.metadata.record_id,
            organization_id=ORGANIZATION_ID,
            expected_version=record.metadata.version,
            correlation_id=CORRELATION_ID,
        ),
    )
    assert persisted.is_success


def test_e1_api_exposes_only_versioned_routes_and_observes_queue_dispatch(
    api_fixture: ApiFixture,
) -> None:
    """The versioned API retains queued-before-dispatch state and preview-first observations."""
    assert all(
        getattr(route, "path", "").startswith(f"{API_V1_PREFIX}/")
        for route in api_fixture.application.routes
    )
    assert api_fixture.client.get("/docs").status_code == 404
    assert api_fixture.client.post("/workflow-runs/dispatch", json={}).status_code == 404

    run_id = _register_and_queue_run(api_fixture)
    stored = api_fixture.services.run_repository.get_by_run_id(ORGANIZATION_ID, RunId(run_id))
    assert stored.is_success and stored.value is not None
    assert stored.value.workflow_definition_digest

    preview = api_fixture.client.post(
        "/api/v1/workflow-runs/dispatch",
        json={"run_id": run_id, "idempotency_key": "e1-dispatch", "confirm": False},
    )
    assert preview.status_code == 200
    assert preview.json()["status"] == "queued"
    assert preview.json()["executed"] is False

    dispatched = api_fixture.client.post(
        "/api/v1/workflow-runs/dispatch",
        json={"run_id": run_id, "idempotency_key": "e1-dispatch", "confirm": True},
    )
    assert dispatched.status_code == 200
    assert dispatched.json()["status"] == "dispatching"
    assert dispatched.json()["executed"] is True

    events = api_fixture.client.get(f"/api/v1/workflow-runs/{run_id}/events")
    assert events.status_code == 200
    assert [event["kind"] for event in events.json()] == [
        "action_preview",
        "action_preview",
        "dispatch",
    ]
    assert events.json()[1]["action_preview"]["supporting_evidence"] == [
        stored.value.workflow_definition_digest
    ]
    graph_state = api_fixture.client.get(f"/api/v1/workflow-runs/{run_id}/graph-state")
    assert graph_state.status_code == 200
    assert graph_state.json()["status"] == "dispatching"
    assert len(graph_state.json()["action_previews"]) == 2


def test_e1_api_scopes_tenants_redacts_output_and_retains_paused_approval(
    api_fixture: ApiFixture,
) -> None:
    """Foreign tenants cannot observe a redacted run or its approval gate before effect."""
    run_id = _register_and_queue_run(api_fixture)
    _set_sensitive_output(api_fixture, run_id)
    dispatched = api_fixture.client.post(
        "/api/v1/workflow-runs/dispatch",
        json={"run_id": run_id, "idempotency_key": "e1-approval", "confirm": True},
    )
    assert dispatched.status_code == 200

    read_run = api_fixture.client.get(f"/api/v1/workflow-runs/{run_id}")
    assert read_run.status_code == 200
    assert read_run.json()["output"] == {
        "api_token": REDACTED,
        "summary": "operator-safe summary",
    }
    assert "e1-secret" not in read_run.text

    gate_result = api_fixture.services.governance.pause_before_effect(
        ORGANIZATION_ID,
        RunId(run_id),
        CORRELATION_ID,
        "critical",
        ActionPreview(
            action_id="e1-crm-update",
            summary="Update a local CRM record.",
            intended_effect="A local CRM effect would be recorded after authorization.",
            supporting_evidence=("case-e1",),
            confidence=0.9,
            correction_control="Deny to retain the paused run.",
        ),
    )
    assert gate_result.is_success and gate_result.value is not None
    gate = gate_result.value
    api_fixture.services.register_pending_approval(
        gate,
        AuthorizationContext(
            agent_id="ops.planner",
            step_id="step-1",
            organization_id=ORGANIZATION_ID,
            actor_id="engine-actor",
            correlation_id=CORRELATION_ID,
            agent_allowed_tools=frozenset({"crm.lookup"}),
            step_declared_tools=frozenset({"crm.lookup"}),
            role_allowed_tools=frozenset({"crm.lookup"}),
            organization_allowed_tools=frozenset({"crm.lookup"}),
            risk_allowed_tools=frozenset({"crm.lookup"}),
            approval_state=ApprovalState.PENDING,
        ),
        ToolRequest("crm.lookup", {"account_id": "local-e1-account"}),
    )

    approval_preview = api_fixture.client.get(f"/api/v1/approvals/{gate.approval_id}")
    assert approval_preview.status_code == 200
    assert approval_preview.json()["gate_status"] == "paused"
    assert approval_preview.json()["action_preview"]["action_id"] == "e1-crm-update"
    decision = api_fixture.client.post(
        f"/api/v1/approvals/{gate.approval_id}/decision",
        json={"selected_value": "denied", "reason": "Needs human review."},
    )
    assert decision.status_code == 200
    assert decision.json()["actor_id"] == "e1-operator"
    assert decision.json()["resumed"] is False
    assert decision.json()["gate_status"] == "paused"
    assert "reason" not in decision.json()

    foreign_context = AuthenticatedRequestContext(
        tenant_id=OrganizationId("org-e1-foreign"),
        actor_id=ActorId("foreign-operator"),
        correlation_id=CorrelationId("corr-e1-foreign"),
    )
    api_fixture.application.dependency_overrides[get_authenticated_request_context] = (
        lambda: foreign_context
    )
    foreign_run = api_fixture.client.get(f"/api/v1/workflow-runs/{run_id}")
    foreign_approval = api_fixture.client.get(f"/api/v1/approvals/{ApprovalId(gate.approval_id)}")

    assert foreign_run.status_code == 404
    assert foreign_approval.status_code == 404
    assert foreign_run.json()["detail"]["code"] == "not_found"
    assert foreign_approval.json()["detail"]["code"] == "not_found"
    assert "e1-secret" not in foreign_run.text
