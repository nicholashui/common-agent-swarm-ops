"""Focused v1 resource-route examples for the deterministic Host control plane."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from datetime import UTC, datetime

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.dependencies import AuthenticatedRequestContext, get_authenticated_request_context
from app.api.v1.services import ControlPlaneServices, get_control_plane_services
from app.governance.approvals import ActionPreview
from app.governance.authorization import ApprovalState, AuthorizationContext
from app.governance.tool_broker import ToolRequest
from app.main import create_app
from app.memory import MemoryImpact, MemoryScope, MemoryScopeType, ScopedMemory
from app.models.common import RecordMetadata
from app.models.evidence import EvidenceReference
from app.models.identifiers import (
    ActorId,
    CorrelationId,
    EvidenceId,
    OrganizationId,
    RecordId,
    RunId,
)

ORG_ID = OrganizationId("org-api")
CORRELATION_ID = CorrelationId("corr-api")


@dataclass
class ApiFixture:
    """One isolated app, Host composition, and trusted authenticated context."""

    application: FastAPI
    client: TestClient
    services: ControlPlaneServices
    context: AuthenticatedRequestContext


@pytest.fixture
def api_fixture() -> Iterator[ApiFixture]:
    """Override only trusted dependency seams; payload headers cannot authenticate requests."""
    application = create_app()
    services = ControlPlaneServices()
    context = AuthenticatedRequestContext(
        tenant_id=ORG_ID,
        actor_id=ActorId("trusted-actor"),
        correlation_id=CORRELATION_ID,
    )
    application.dependency_overrides[get_authenticated_request_context] = lambda: context
    application.dependency_overrides[get_control_plane_services] = lambda: services
    with TestClient(application) as client:
        yield ApiFixture(application, client, services, context)
    application.dependency_overrides.clear()


def _manifest() -> dict[str, object]:
    return {
        "pack_id": "operations",
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


def _register_and_create_run(fixture: ApiFixture) -> str:
    registration = fixture.client.post(
        "/api/v1/domains/register",
        json={"manifest": _manifest()},
    )
    assert registration.status_code == 200
    definition = fixture.client.post(
        "/api/v1/workflows/definitions", json={"definition": _definition()}
    )
    assert definition.status_code == 201
    run = fixture.client.post("/api/v1/workflows/ops.onboarding/run", json={"version": "1.0.0"})
    assert run.status_code == 201
    return str(run.json()["run_id"])


def test_resources_register_definitions_queue_runs_and_emit_preview_before_dispatch(
    api_fixture: ApiFixture,
) -> None:
    """Definitions are tenant-scoped and a confirmed dispatch follows a persisted preview event."""
    run_id = _register_and_create_run(api_fixture)

    topology = api_fixture.client.get("/api/v1/workflows/ops.onboarding/topology?version=1.0.0")
    assert topology.status_code == 200
    assert topology.json()["nodes"] == [
        {"node_id": "step-1", "agent_id": "ops.planner", "tool_ids": ["crm.lookup"]}
    ]

    preview = api_fixture.client.post(
        "/api/v1/workflow-runs/dispatch",
        json={"run_id": run_id, "idempotency_key": "dispatch-1", "confirm": False},
    )
    assert preview.status_code == 200
    assert preview.json()["executed"] is False
    assert preview.json()["status"] == "queued"

    dispatched = api_fixture.client.post(
        "/api/v1/workflow-runs/dispatch",
        json={"run_id": run_id, "idempotency_key": "dispatch-1", "confirm": True},
    )
    assert dispatched.status_code == 200
    assert dispatched.json()["executed"] is True
    assert dispatched.json()["status"] == "dispatching"

    events = api_fixture.client.get(f"/api/v1/workflow-runs/{run_id}/events")
    assert events.status_code == 200
    assert [event["kind"] for event in events.json()] == [
        "action_preview",
        "action_preview",
        "dispatch",
    ]
    assert events.json()[1]["action_preview"]["action_id"] == f"dispatch:{run_id}"

    graph_state = api_fixture.client.get(f"/api/v1/workflow-runs/{run_id}/graph-state")
    assert graph_state.status_code == 200
    assert graph_state.json()["status"] == "dispatching"
    assert len(graph_state.json()["action_previews"]) == 2


def test_routes_scope_runs_to_trusted_context_and_reject_identity_overrides(
    api_fixture: ApiFixture,
) -> None:
    """Payload tenant or actor fields cannot select another organization or impersonate an actor."""
    run_id = _register_and_create_run(api_fixture)

    override_attempt = api_fixture.client.post(
        "/api/v1/workflow-runs/dispatch",
        json={
            "run_id": run_id,
            "idempotency_key": "dispatch-identity",
            "confirm": False,
            "actor_id": "attacker",
        },
    )
    assert override_attempt.status_code == 422

    foreign_context = AuthenticatedRequestContext(
        tenant_id=OrganizationId("other-org"),
        actor_id=ActorId("other-actor"),
        correlation_id=CorrelationId("corr-other"),
    )
    api_fixture.application.dependency_overrides[get_authenticated_request_context] = (
        lambda: foreign_context
    )
    foreign_read = api_fixture.client.get(f"/api/v1/workflow-runs/{run_id}")
    assert foreign_read.status_code == 404
    assert foreign_read.json()["detail"]["code"] == "not_found"


def test_approval_decision_uses_trusted_actor_and_redacts_raw_reason(
    api_fixture: ApiFixture,
) -> None:
    """Approval decisions retain only server-derived actor identity in the public projection."""
    run_id = _register_and_create_run(api_fixture)
    dispatched = api_fixture.client.post(
        "/api/v1/workflow-runs/dispatch",
        json={"run_id": run_id, "idempotency_key": "dispatch-approval", "confirm": True},
    )
    assert dispatched.status_code == 200

    gate = api_fixture.services.governance.pause_before_effect(
        ORG_ID,
        RunId(run_id),
        CORRELATION_ID,
        "critical",
        ActionPreview(
            action_id="crm-update",
            summary="Update the approved local CRM account.",
            intended_effect="A deterministic local CRM effect will be recorded.",
            supporting_evidence=("case-123",),
            confidence=0.9,
            correction_control="Deny the change to keep the run paused.",
        ),
    )
    assert gate.is_success and gate.value is not None
    api_fixture.services.register_pending_approval(
        gate.value,
        AuthorizationContext(
            agent_id="ops.planner",
            step_id="step-1",
            organization_id=ORG_ID,
            actor_id="engine-actor",
            correlation_id=CORRELATION_ID,
            agent_allowed_tools=frozenset({"crm.lookup"}),
            step_declared_tools=frozenset({"crm.lookup"}),
            role_allowed_tools=frozenset({"crm.lookup"}),
            organization_allowed_tools=frozenset({"crm.lookup"}),
            risk_allowed_tools=frozenset({"crm.lookup"}),
            approval_state=ApprovalState.PENDING,
        ),
        ToolRequest("crm.lookup", {"account_id": "acct-1"}),
    )

    response = api_fixture.client.post(
        f"/api/v1/approvals/{gate.value.approval_id}/decision",
        json={"selected_value": "approved", "reason": "contains a secret but is not returned"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["actor_id"] == "trusted-actor"
    assert body["resumed"] is True
    assert "reason" not in body
    assert body["action_preview"]["action_id"] == "crm-update"


def test_approval_gate_preview_is_tenant_scoped_and_available_before_decision(
    api_fixture: ApiFixture,
) -> None:
    """The operator can inspect redacted evidence before submitting an executable approval."""
    run_id = _register_and_create_run(api_fixture)
    dispatched = api_fixture.client.post(
        "/api/v1/workflow-runs/dispatch",
        json={"run_id": run_id, "idempotency_key": "dispatch-preview", "confirm": True},
    )
    assert dispatched.status_code == 200

    gate = api_fixture.services.governance.pause_before_effect(
        ORG_ID,
        RunId(run_id),
        CORRELATION_ID,
        "critical",
        ActionPreview(
            action_id="crm-update",
            summary="Update the approved local CRM account.",
            intended_effect="A deterministic local CRM effect will be recorded.",
            supporting_evidence=("case-123",),
            confidence=0.9,
            correction_control="Deny the change to keep the run paused.",
        ),
    )
    assert gate.is_success and gate.value is not None

    preview = api_fixture.client.get(f"/api/v1/approvals/{gate.value.approval_id}")

    assert preview.status_code == 200
    body = preview.json()
    assert body["run_id"] == run_id
    assert body["gate_status"] == "paused"
    assert body["action_preview"]["supporting_evidence"] == ["case-123"]

    foreign_context = AuthenticatedRequestContext(
        tenant_id=OrganizationId("other-org"),
        actor_id=ActorId("other-actor"),
        correlation_id=CorrelationId("corr-other"),
    )
    api_fixture.application.dependency_overrides[get_authenticated_request_context] = (
        lambda: foreign_context
    )
    foreign_preview = api_fixture.client.get(f"/api/v1/approvals/{gate.value.approval_id}")

    assert foreign_preview.status_code == 404
    assert foreign_preview.json()["detail"]["code"] == "not_found"


def test_video_artifact_handoff_and_release_readiness_are_versioned_and_non_releasing(
    api_fixture: ApiFixture,
) -> None:
    """Video controls retain local immutable evidence and never invoke a release effect."""
    artifact = api_fixture.client.post(
        "/api/v1/video/artifacts",
        json={
            "artifact_id": "campaign-video",
            "parent_version_ids": [],
            "rights_and_consent_passed": False,
            "provenance_and_signoff_passed": True,
            "quality_checks": [
                {"name": "sharpness", "passed": False, "evidence_reference": "quality-1"}
            ],
            "release_checks": [
                {"name": "brand-review", "passed": True, "evidence_reference": "gate-1"}
            ],
        },
    )
    assert artifact.status_code == 201
    artifact_version_id = artifact.json()["artifact_version_id"]

    decision = api_fixture.client.post(
        f"/api/v1/video/artifacts/{artifact_version_id}/release-requests"
    )
    assert decision.status_code == 201
    body = decision.json()
    assert body["decision"] == "denied"
    assert body["artifact_released"] is False
    assert {"rights_and_consent", "quality:sharpness"} <= set(body["unmet_conditions"])
    assert body["action_preview"]["intended_effect"].endswith("no video artifact is released.")

    retained = api_fixture.client.get(
        f"/api/v1/video/release-requests/{body['release_request_id']}"
    )
    assert retained.status_code == 200
    assert retained.json()["artifact_released"] is False


def _seed_memory(
    fixture: ApiFixture,
    *,
    record_id: str,
    organization_id: OrganizationId,
    scope: MemoryScope,
    content_reference: str,
) -> None:
    """Seed one provenance-bearing record in the target-local in-memory repository."""
    timestamp = datetime(2025, 1, 1, tzinfo=UTC)
    stored = fixture.services.memory_repository.create(
        ScopedMemory(
            metadata=RecordMetadata(
                record_id=RecordId(record_id),
                organization_id=organization_id,
                correlation_id=CORRELATION_ID,
                schema_version=1,
                version=1,
                created_at=timestamp,
                updated_at=timestamp,
            ),
            scope=scope,
            impact=MemoryImpact.LOW,
            writer=ActorId("internal-memory-writer"),
            content_reference=content_reference,
            provenance=(
                EvidenceReference(
                    evidence_id=EvidenceId(f"evidence-{record_id}"),
                    digest=f"digest-{record_id}",
                    kind="target-local-record",
                ),
            ),
            source_log_set_id="internal-log-set-should-be-redacted",
        )
    )
    assert stored.is_success


def test_memory_retrieval_uses_authenticated_scopes_and_redacts_internal_metadata(
    api_fixture: ApiFixture,
) -> None:
    """Only Host-derived organization and actor scopes reach the redacted public projection."""
    trusted_actor_scope = MemoryScope(MemoryScopeType.AGENT, "trusted-actor")
    seeded_records = (
        (
            "approved-organization",
            ORG_ID,
            MemoryScope(MemoryScopeType.ORGANIZATION, str(ORG_ID)),
            "recovery guidance for organization",
        ),
        ("approved-agent", ORG_ID, trusted_actor_scope, "recovery guidance for actor"),
        (
            "foreign-workflow",
            ORG_ID,
            MemoryScope(MemoryScopeType.WORKFLOW, "workflow-1"),
            "recovery guidance for workflow",
        ),
        (
            "foreign-agent",
            ORG_ID,
            MemoryScope(MemoryScopeType.AGENT, "other-actor"),
            "recovery guidance for another actor",
        ),
        (
            "foreign-organization",
            OrganizationId("other-org"),
            MemoryScope(MemoryScopeType.ORGANIZATION, "other-org"),
            "recovery guidance for another organization",
        ),
    )
    for record_id, organization_id, scope, content_reference in seeded_records:
        _seed_memory(
            api_fixture,
            record_id=record_id,
            organization_id=organization_id,
            scope=scope,
            content_reference=content_reference,
        )

    response = api_fixture.client.post(
        "/api/v1/memory/retrieve",
        json={"query": "recovery guidance", "requires_relationships": True},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["no_knowledge"] is False
    assert body["searched_tiers"] == ["tier-0-semantic"]
    assert {result["source_record_ids"][0] for result in body["results"]} == {
        "approved-organization",
        "approved-agent",
    }
    expected_result_keys = {
        "tier",
        "content_reference",
        "source_record_ids",
        "provenance",
        "confidence",
    }
    assert all(set(result) == expected_result_keys for result in body["results"])
    public_payload = response.text
    assert "internal-memory-writer" not in public_payload
    assert "internal-log-set-should-be-redacted" not in public_payload
    assert "foreign-workflow" not in public_payload
    assert "foreign-agent" not in public_payload
    assert "foreign-organization" not in public_payload


def test_memory_retrieval_is_confined_to_the_versioned_target_control_plane(
    api_fixture: ApiFixture,
) -> None:
    """The local memory endpoint cannot be reached through an unversioned public path."""
    unversioned = api_fixture.client.post("/memory/retrieve", json={"query": "anything"})
    versioned = api_fixture.client.post("/api/v1/memory/retrieve", json={"query": "anything"})

    assert unversioned.status_code == 404
    assert unversioned.json()["detail"]["code"] == "public_route_not_found"
    assert versioned.status_code == 200
    assert versioned.json()["no_knowledge"] is True
