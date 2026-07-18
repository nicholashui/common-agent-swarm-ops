"""Deterministic integration coverage for the stub-only Video_Pack controls.

The test uses only Host-owned in-memory services and the registered ``media.stub``
adapter. It never contacts a media provider or releases an artifact.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from fastapi.testclient import TestClient

from app.adapters import StubMediaAdapter, default_local_adapters
from app.api.v1.dependencies import AuthenticatedRequestContext, get_authenticated_request_context
from app.api.v1.services import ControlPlaneServices, get_control_plane_services
from app.audit import AuditWriter
from app.engines.compiler import CompiledGraphNode, GraphCompiler
from app.engines.graph import GraphEngine
from app.governance.authorization import ApprovalState, AuthorizationContext
from app.governance.tool_broker import HostToolBroker
from app.main import create_app
from app.models.common import RecordMetadata
from app.models.identifiers import (
    ActorId,
    CorrelationId,
    OrganizationId,
    RecordId,
    RunId,
    WorkflowDefinitionId,
)
from app.models.runs import RunRecord, RunStatus, WorkflowEngineKind
from app.repositories.run_repository import InMemoryRunRepository
from app.video.blockers import (
    COMPLIANCE_AGENT_ID,
    LocalMonotonicBlockerScheduler,
    VideoBlockerCancellationToken,
    VideoBlockerDraft,
    VideoSpineNodeExecutor,
)
from tests.fakes.broker import InMemoryAuditRepository

# **Validates: Requirements 9.2-9.5, 6.5-6.6, 10.1-10.2**

NOW = datetime(2025, 1, 1, tzinfo=UTC)
ORGANIZATION_ID = OrganizationId("org-video-integration")
CORRELATION_ID = CorrelationId("video-integration")


class _DetectedComplianceBlocker:
    """Deterministically detect one local ComplianceAgent blocker."""

    def detect(self, _run: RunRecord, _node: CompiledGraphNode) -> VideoBlockerDraft:
        return VideoBlockerDraft(
            blocker_id="blocker-compliance-integration",
            source_agent_id=COMPLIANCE_AGENT_ID,
            category="rights-consent",
            evidence_reference="evidence-video-compliance-integration",
        )


def _definition() -> dict[str, object]:
    path = (
        Path(__file__).resolve().parents[4]
        / "business"
        / "video"
        / "workflows"
        / "pack_spine.json"
    )
    parsed: object = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(parsed, dict)
    return parsed


def _run(definition: dict[str, object]) -> RunRecord:
    return RunRecord(
        metadata=RecordMetadata(
            RecordId("record-video-integration"),
            ORGANIZATION_ID,
            CORRELATION_ID,
            1,
            1,
            NOW,
            NOW,
        ),
        run_id=RunId("run-video-integration"),
        workflow_definition_id=WorkflowDefinitionId("video.pack-spine"),
        workflow_definition_version="1.0.0",
        workflow_definition_digest=GraphCompiler.definition_digest(definition),
        engine=WorkflowEngineKind.GRAPH,
        status=RunStatus.DISPATCHING,
        created_for_dispatch_at=NOW,
    )


def _authorization_context(run: RunRecord, node: CompiledGraphNode) -> AuthorizationContext:
    declared_tools = frozenset(node.declared_tool_ids)
    return AuthorizationContext(
        agent_id=node.agent_id,
        step_id=node.node_id,
        organization_id=str(run.metadata.organization_id),
        actor_id="video-integration-actor",
        correlation_id=str(run.metadata.correlation_id),
        agent_allowed_tools=declared_tools,
        step_declared_tools=declared_tools,
        role_allowed_tools=declared_tools,
        organization_allowed_tools=declared_tools,
        risk_allowed_tools=declared_tools,
        approval_state=ApprovalState.NOT_REQUIRED,
    )


def _artifact_payload(*, quality_passed: bool) -> dict[str, object]:
    return {
        "artifact_id": "integration-video",
        "parent_version_ids": [],
        "rights_and_consent_passed": True,
        "provenance_and_signoff_passed": True,
        "quality_checks": [
            {
                "name": "sharpness",
                "passed": quality_passed,
                "evidence_reference": "quality-integration",
            }
        ],
        "release_checks": [
            {
                "name": "brand-review",
                "passed": True,
                "evidence_reference": "release-integration",
            }
        ],
    }


def test_stub_spine_blocker_gates_tenant_scoped_release_readiness() -> None:
    """A blocker stops local scheduling, preserves state, and gates safe readiness decisions."""
    definition = _definition()
    run_repository = InMemoryRunRepository()
    run = _run(definition)
    assert run_repository.create(run).is_success
    scheduler = LocalMonotonicBlockerScheduler(clock=iter((10.0, 14.99)).__next__)
    cancellation = VideoBlockerCancellationToken(
        run_repository,
        ORGANIZATION_ID,
        run.run_id,
        CORRELATION_ID,
        scheduler=scheduler,
        timestamp_clock=lambda: NOW,
    )
    adapters = default_local_adapters()
    broker = HostToolBroker(adapters, AuditWriter(InMemoryAuditRepository()))
    outcome = GraphEngine(
        run_repository,
        VideoSpineNodeExecutor(cancellation, _DetectedComplianceBlocker()),
        broker,
        _authorization_context,
        cancellation_token=cancellation,
    ).execute(ORGANIZATION_ID, run.run_id, definition, CORRELATION_ID)

    assert outcome.is_success and outcome.value is not None
    blocked_run = outcome.value.record
    assert not outcome.value.completed
    assert blocked_run.status is RunStatus.FAILED
    assert blocked_run.failure is not None
    assert blocked_run.failure.code == "video_compliance_blocker_detected"
    assert blocked_run.failure.stopped_step_ids == ("complete",)
    assert cancellation.last_stop_elapsed_seconds is not None
    assert cancellation.last_stop_elapsed_seconds < 5
    assert {effect.adapter_id for effect in blocked_run.tool_effects} == {"media.stub"}
    graph_state = blocked_run.output["graph_state"] if blocked_run.output is not None else None
    assert graph_state == {
        "graph_id": blocked_run.graph_id,
        "current_node_id": "compliance-review",
        "visited_node_ids": ["compliance-review", "media-stub", "supervise"],
        "unstarted_node_ids": ("complete",),
        "interruption": "video_compliance_blocker_detected",
    }
    stub_adapter = next(adapter for adapter in adapters if isinstance(adapter, StubMediaAdapter))
    assert len(stub_adapter.retained_effects) == 1
    assert all(not adapter.retained_effects for adapter in adapters if adapter is not stub_adapter)

    application = create_app()
    services = ControlPlaneServices(run_repository=run_repository)
    context: dict[str, AuthenticatedRequestContext] = {
        "current": AuthenticatedRequestContext(
            ORGANIZATION_ID,
            ActorId("video-owner"),
            CORRELATION_ID,
        )
    }
    application.dependency_overrides[get_authenticated_request_context] = lambda: context["current"]
    application.dependency_overrides[get_control_plane_services] = lambda: services
    try:
        with TestClient(application) as client:
            denied_artifact = client.post(
                "/api/v1/video/artifacts",
                json=_artifact_payload(quality_passed=False),
            )
            assert denied_artifact.status_code == 201
            denied = client.post(
                f"/api/v1/video/artifacts/{denied_artifact.json()['artifact_version_id']}"
                "/release-requests"
            )
            assert denied.status_code == 201
            denied_body = denied.json()
            assert denied_body["decision"] == "denied"
            assert denied_body["artifact_released"] is False
            unmet_conditions = set(denied_body["unmet_conditions"])
            assert {"quality:sharpness", "no_unresolved_blockers"} <= unmet_conditions
            action_preview = denied_body["action_preview"]
            assert action_preview["confidence"] == 1.0
            assert "no video artifact is released" in action_preview["intended_effect"]

            assert cancellation.resolve("blocker-compliance-integration", "local human correction")
            permitted_artifact = client.post(
                "/api/v1/video/artifacts",
                json=_artifact_payload(quality_passed=True),
            )
            assert permitted_artifact.status_code == 201
            permitted = client.post(
                f"/api/v1/video/artifacts/{permitted_artifact.json()['artifact_version_id']}"
                "/release-requests"
            )
            assert permitted.status_code == 201
            permitted_body = permitted.json()
            assert permitted_body["decision"] == "permitted"
            assert permitted_body["unmet_conditions"] == []
            assert permitted_body["artifact_released"] is False
            release_requests = services.artifact_repository.release_requests_for_organization(
                ORGANIZATION_ID
            )
            assert len(release_requests) == 2

            context["current"] = AuthenticatedRequestContext(
                OrganizationId("foreign-video-tenant"),
                ActorId("foreign-actor"),
                CorrelationId("foreign-video"),
            )
            foreign_read = client.get(
                f"/api/v1/video/release-requests/{denied_body['release_request_id']}"
            )
            assert foreign_read.status_code == 404
            assert foreign_read.json()["detail"]["code"] == "not_found"
    finally:
        application.dependency_overrides.clear()
