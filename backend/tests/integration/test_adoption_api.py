"""FastAPI integration coverage for fail-closed adoption API behavior."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import cast

import pytest
from fastapi.testclient import TestClient
from httpx import Response

from app.api.v1.adoption_services import (
    AdoptionRepositories,
    AdoptionServices,
    get_adoption_services,
)
from app.api.v1.dependencies import AuthenticatedRequestContext, get_authenticated_request_context
from app.artifacts.handoff_service import ArtifactHandoffService
from app.main import create_app
from app.models.contracts import ErrorCode, ErrorDetail, Result
from app.models.control_plane import ArtifactHandoff, ArtifactHandoffId
from app.models.identifiers import ActorId, CorrelationId, OrganizationId
from tests.fakes.adoption import (
    DeterministicAdoptionRepositories,
    DeterministicArtifactHandoffRepository,
    FakeFailurePlan,
)

_ORGANIZATION = OrganizationId("adoption-api-org")
_ACTOR = ActorId("adoption-api-actor")
_CORRELATION = CorrelationId("adoption-api-correlation")
_DOMAIN = "adoption-api-domain"
_PACK_ID = "adoption-api-pack"
_AGENT_ID = "adoption-api-agent"
_PACK_VERSION = "1.0.0"
_MEMORY_SCOPE = "agent:adoption-api-agent:memory"


@dataclass
class ApiFixture:
    """One isolated public API composition backed entirely by deterministic fakes."""

    client: TestClient
    services: AdoptionServices
    repositories: DeterministicAdoptionRepositories


class _UnconfirmedExternalHandoffRepository(DeterministicArtifactHandoffRepository):
    """Fake an incomplete external metadata confirmation barrier."""

    def confirm_metadata_persistence(
        self,
        organization_id: OrganizationId,
        handoff_id: ArtifactHandoffId,
    ) -> Result[ArtifactHandoff, ErrorDetail]:
        del organization_id, handoff_id
        return Result.failure(
            ErrorDetail(
                ErrorCode.REPOSITORY_UNAVAILABLE,
                "External handoff metadata confirmation is unavailable.",
                CorrelationId("fake-handoff-confirmation"),
                retryable=True,
            )
        )


@pytest.fixture
def api_fixture() -> Iterator[ApiFixture]:
    """Provide a versioned app with trusted identity and no production dependencies."""
    failure_plan = FakeFailurePlan()
    repositories = DeterministicAdoptionRepositories(failure_plan)
    adoption_repositories = AdoptionRepositories(
        registrations=repositories.registrations,
        invocations=repositories.invocations,
        authorizations=repositories.authorizations,
        handoffs=repositories.handoffs,
        lifecycles=repositories.lifecycle,
        attempts=repositories.attempts,
        retrievals=repositories.retrievals,
        episodes=repositories.episodes,
        lessons=repositories.lessons,
        verifications=repositories.verifications,
        releases=repositories.release_decisions,
        recoveries=repositories.recoveries,
        maturity=repositories.maturity,
        audits=repositories.audit,
    )
    services = AdoptionServices(adoption_repositories)
    application = create_app()
    context = AuthenticatedRequestContext(
        tenant_id=_ORGANIZATION,
        actor_id=_ACTOR,
        correlation_id=_CORRELATION,
    )
    application.dependency_overrides[get_authenticated_request_context] = lambda: context
    application.dependency_overrides[get_adoption_services] = lambda: services
    with TestClient(application) as client:
        yield ApiFixture(client, services, repositories)
    application.dependency_overrides.clear()


def _payload(response: Response) -> object:
    """Return the data member from a successful public response envelope."""
    body = cast(dict[str, object], response.json())
    return body.get("data", body)


def _data(response: Response) -> dict[str, object]:
    """Return a typed object payload for route assertions."""
    return cast(dict[str, object], _payload(response))


def _error(response: Response) -> dict[str, object]:
    """Return the redaction-safe public error object."""
    body = cast(dict[str, object], response.json())
    return cast(dict[str, object], body["error"])


def _manifest(
    pack_id: str = _PACK_ID,
    *,
    immutable_version: str = _PACK_VERSION,
    agent_id: str = _AGENT_ID,
) -> dict[str, object]:
    """Build a complete declarative manifest accepted by Pack_Contract admission."""
    return {
        "pack_id": pack_id,
        "immutable_version": immutable_version,
        "pack_contract_version": "1.0.0",
        "host_compatibility_range": {
            "minimum": "1.0.0",
            "maximum": "1.0.0",
            "include_minimum": True,
            "include_maximum": True,
        },
        "alc_compatibility_range": {
            "minimum": "1.0.0",
            "maximum": "1.0.0",
            "include_minimum": True,
            "include_maximum": True,
        },
        "content_digest": f"sha256:{pack_id}-{immutable_version}",
        "agents": [
            {
                "agent_id": agent_id,
                "status": "registered",
                "allowed_tools": ["declared.tool"],
                "memory_scopes": [_MEMORY_SCOPE],
                "allowed_outbound_destinations": ["https://approved.example"],
            }
        ],
        "workflows": ["adoption-api.workflow"],
        "capabilities": ["memory.read", "text.generate"],
        "data_classifications": ["internal"],
        "evaluation_references": ["evaluation:adoption-api"],
        "required_alc_version": "1.0.0",
        "asset_references": [
            f"asset:{pack_id}:workflow@{immutable_version}#sha256:{pack_id}-workflow"
        ],
        "domain_id": _DOMAIN,
    }


def _register(client: TestClient, pack_id: str = _PACK_ID) -> dict[str, object]:
    """Register one valid pack through the public route."""
    response = client.post("/api/v1/adoption/packs", json={"manifest": _manifest(pack_id)})
    assert response.status_code == 201
    result = _data(response)
    assert result["decision"] == "approved"
    return result


def _handoff_payload(handoff_id: str = "handoff-api-1") -> dict[str, object]:
    """Build complete reference-only handoff metadata without artifact content."""
    return {
        "handoff_id": handoff_id,
        "artifact_identity": "artifact:adoption-api",
        "artifact_version": "1.0.0",
        "parent_lineage": [],
        "source_task_id": "task:adoption-api",
        "source_run_reference": "run:adoption-api",
        "brief_scope": "integration-test",
        "technical_specification": {"schema_reference": "schema:adoption-api"},
        "rights_and_consent_state": "passed",
        "continuity_state": "passed",
        "quality_control_state": "passed",
        "target_channels": ["review"],
        "provenance_reference": "provenance:adoption-api",
        "owner_reference": "owner:adoption-api",
        "classification": "internal",
        "integrity_reference": "sha256:adoption-api-artifact",
        "approval_reference": "approval:adoption-api",
    }


def _activation_payload(
    *, evidence: dict[str, object], candidates: list[dict[str, object]]
) -> dict[str, object]:
    """Build one learning activation request with explicit host-owned evidence."""
    return {
        "lifecycle_id": "lifecycle:adoption-api",
        "pack_id": _PACK_ID,
        "immutable_version": _PACK_VERSION,
        "agent_id": _AGENT_ID,
        "learning_required": True,
        "effective_alc_version": "1.0.0",
        "alc_candidates": candidates,
        "evidence": evidence,
    }


def _alc_candidate() -> dict[str, object]:
    """Build the sole effective agent-scoped ALC candidate."""
    return {
        "agent_id": _AGENT_ID,
        "version": "1.0.0",
        "memory_scopes": [_MEMORY_SCOPE],
        "retrieval_policy": "enabled",
        "reflection_policy": "enabled",
        "evaluation_references": ["evaluation:adoption-api-alc"],
        "retention_policy": "retain-assessed",
        "human_promotion_policy": "required",
    }


def _activation_evidence() -> dict[str, object]:
    """Build complete activation evidence for the learning lifecycle."""
    return {
        "approved_agent_scoped_memory": True,
        "pre_action_retrieval_enabled": True,
        "learning_episode_capture_enabled": True,
        "reflection_evaluator_enabled": True,
        "retention_policy": "retain-assessed",
        "required_evaluations_passed": True,
        "evidence_references": ["evidence:adoption-api-activation"],
    }


def _retrieval_payload(attempt_id: str) -> dict[str, object]:
    """Build a learning-required retrieval request with an intentionally empty result."""
    return {
        "attempt_id": attempt_id,
        "run_id": f"run:{attempt_id}",
        "node_id": "planner",
        "domain_id": _DOMAIN,
        "pack_id": _PACK_ID,
        "pack_version": _PACK_VERSION,
        "agent_id": _AGENT_ID,
        "workflow_id": "adoption-api.workflow",
        "status": "queued",
        "memory_scope": _MEMORY_SCOPE,
        "lesson_references": [],
    }


def _episode_payload(
    attempt_id: str,
    retrieval_record_id: str,
    outcome_reference: str,
    evidence_references: list[str] | None = None,
) -> dict[str, object]:
    """Build a strict terminal Learning_Episode request without retrieval-only fields."""
    return {
        "attempt_id": attempt_id,
        "run_id": f"run:{attempt_id}",
        "node_id": "planner",
        "domain_id": _DOMAIN,
        "pack_id": _PACK_ID,
        "pack_version": _PACK_VERSION,
        "agent_id": _AGENT_ID,
        "workflow_id": "adoption-api.workflow",
        "status": "completed",
        "terminal_outcome": "completed",
        "outcome_reference": outcome_reference,
        "retrieval_record_id": retrieval_record_id,
        "evidence_references": evidence_references or [],
    }


def test_rejected_registration_returns_safe_error_and_audits_the_pack() -> None:
    """Executable declarations are rejected before registration and retained as audit evidence."""
    failure_plan = FakeFailurePlan()
    repositories = DeterministicAdoptionRepositories(failure_plan)
    adoption_repositories = AdoptionRepositories(
        registrations=repositories.registrations,
        invocations=repositories.invocations,
        authorizations=repositories.authorizations,
        handoffs=repositories.handoffs,
        lifecycles=repositories.lifecycle,
        attempts=repositories.attempts,
        retrievals=repositories.retrievals,
        episodes=repositories.episodes,
        lessons=repositories.lessons,
        verifications=repositories.verifications,
        releases=repositories.release_decisions,
        recoveries=repositories.recoveries,
        maturity=repositories.maturity,
        audits=repositories.audit,
    )
    services = AdoptionServices(adoption_repositories)
    application = create_app()
    context = AuthenticatedRequestContext(_ORGANIZATION, _ACTOR, _CORRELATION)
    application.dependency_overrides[get_authenticated_request_context] = lambda: context
    application.dependency_overrides[get_adoption_services] = lambda: services

    manifest = _manifest("rejected-adoption-pack")
    manifest["runtime"] = "python"
    with TestClient(application) as client:
        response = client.post("/api/v1/adoption/packs", json={"manifest": manifest})

    assert response.status_code == 422
    assert _error(response)["code"] == ErrorCode.VALIDATION_FAILED.value
    fields = cast(list[dict[str, object]], _error(response)["fields"])
    assert {str(field["field"]) for field in fields} == {"executable_code"}
    assert repositories.registrations.records() == ()
    assert len(repositories.audit.records) == 1
    assert repositories.audit.records[0].action == "pack.registration.rejected.executable_code"
    assert "code_locations" in repositories.audit.records[0].outcome
    application.dependency_overrides.clear()


def test_incompatible_pack_status_blocks_invocation_and_keeps_activation_non_active(
    api_fixture: ApiFixture,
) -> None:
    """Incompatible compatibility evidence is visible and cannot become an active invocation."""
    client = api_fixture.client
    compatibility = client.post(
        "/api/v1/adoption/compatibility",
        json={
            "pack_id": "incompatible-adoption-pack",
            "immutable_version": "1.0.0",
            "pack_contract_version": "1.0.0",
            "declared_host_range": {"minimum": "9.0.0", "maximum": "9.0.0"},
            "declared_alc_range": {"minimum": "9.0.0", "maximum": "9.0.0"},
            "supported_host_version": "1.0.0",
            "supported_alc_version": "1.0.0",
        },
    )
    assert compatibility.status_code == 200
    assert _data(compatibility)["status"] == "incompatible"

    activation = client.post(
        "/api/v1/adoption/lifecycle/activate",
        json=_activation_payload(evidence={}, candidates=[]),
    )
    assert activation.status_code == 200
    assert _data(activation)["status"] == "blocked"

    invocation = client.post(
        "/api/v1/adoption/invocations",
        json={
            "invocation_id": "invocation:incompatible",
            "domain_id": _DOMAIN,
            "pack_id": "incompatible-adoption-pack",
            "pack_version": "1.0.0",
            "agent_id": _AGENT_ID,
            "workflow_id": "adoption-api.workflow",
            "run_id": "run:incompatible",
        },
    )
    assert invocation.status_code == 403
    assert _error(invocation)["code"] == ErrorCode.AUTHORIZATION_DENIED.value
    assert api_fixture.repositories.invocations.records() == ()


def test_undeclared_data_tool_and_outbound_requests_are_denied_and_audited(
    api_fixture: ApiFixture,
) -> None:
    """Each declared-capability boundary returns an explicit denial without dispatch."""
    _register(api_fixture.client)
    base = {"domain_id": _DOMAIN, "pack_version": _PACK_VERSION, "agent_id": _AGENT_ID}

    data = api_fixture.client.post(
        "/api/v1/adoption/governance/data",
        json={**base, "memory_scope": "agent:adoption-api:undeclared"},
    )
    tool = api_fixture.client.post(
        "/api/v1/adoption/governance/tools",
        json={**base, "capability": "undeclared.tool"},
    )
    outbound = api_fixture.client.post(
        "/api/v1/adoption/governance/outbound",
        json={**base, "destination": "https://unapproved.example"},
    )

    for response in (data, tool, outbound):
        assert response.status_code == 200
        result = _data(response)
        assert result["outcome"] == "denied"
        assert result["allowed"] is False
        assert result["reason_code"]
    assert len(api_fixture.repositories.authorizations.records()) == 3
    assert [record.action for record in api_fixture.repositories.audit.records] == [
        "governance.denied",
        "governance.denied",
        "governance.denied",
    ]


def test_external_handoff_is_not_available_when_metadata_confirmation_fails(
    api_fixture: ApiFixture,
) -> None:
    """A failed external confirmation leaves the handoff pending and unavailable downstream."""
    pending_repository = _UnconfirmedExternalHandoffRepository(
        api_fixture.repositories.failure_plan
    )
    api_fixture.services.artifact_handoffs = ArtifactHandoffService(
        pending_repository,
        api_fixture.repositories.audit,
    )

    external = api_fixture.client.post(
        "/api/v1/adoption/handoffs/external",
        json=_handoff_payload("handoff:pending-external"),
    )
    assert external.status_code == 503
    assert _error(external)["code"] == ErrorCode.REPOSITORY_UNAVAILABLE.value

    available = api_fixture.client.get("/api/v1/adoption/handoffs/available")
    assert available.status_code == 200
    assert _payload(available) == []
    assert len(pending_repository.records()) == 1
    assert pending_repository.records()[0].metadata_persisted is False


def test_incomplete_internal_handoff_metadata_is_rejected_before_availability(
    api_fixture: ApiFixture,
) -> None:
    """Required lineage metadata cannot be omitted to cross the internal handoff barrier."""
    request = _handoff_payload("handoff:incomplete-internal")
    request.pop("approval_reference")
    response = api_fixture.client.post("/api/v1/adoption/handoffs/internal", json=request)

    assert response.status_code == 422
    assert _error(response)["code"] == ErrorCode.VALIDATION_FAILED.value
    fields = cast(list[dict[str, object]], _error(response)["fields"])
    assert {str(field["field"]) for field in fields} == {"approval_reference"}
    available = api_fixture.client.get("/api/v1/adoption/handoffs/available")
    assert available.status_code == 200
    assert _payload(available) == []


def test_learning_activation_and_retrieval_fail_closed_before_episode_capture(
    api_fixture: ApiFixture,
) -> None:
    """Activation, retrieval, and terminal evidence routes preserve their ordering barriers."""
    client = api_fixture.client
    blocked = client.post(
        "/api/v1/adoption/lifecycle/activate",
        json=_activation_payload(evidence={}, candidates=[]),
    )
    assert blocked.status_code == 200
    assert _data(blocked)["status"] == "blocked"

    active = client.post(
        "/api/v1/adoption/lifecycle/activate",
        json=_activation_payload(evidence=_activation_evidence(), candidates=[_alc_candidate()]),
    )
    assert active.status_code == 200
    assert _data(active)["status"] == "active"

    retrieval = client.post(
        "/api/v1/adoption/retrievals",
        json=_retrieval_payload("attempt:learning-success"),
    )
    assert retrieval.status_code == 200
    retrieval_data = _data(retrieval)
    assert retrieval_data["lesson_references"] == []

    api_fixture.repositories.failure_plan.fail_next_persistence("retrieval.append")
    failed_retrieval = client.post(
        "/api/v1/adoption/retrievals",
        json=_retrieval_payload("attempt:learning-retrieval-failure"),
    )
    assert failed_retrieval.status_code == 503
    assert _error(failed_retrieval)["code"] == ErrorCode.REPOSITORY_UNAVAILABLE.value
    assert any(
        record.action == "learning.retrieval.blocked"
        for record in api_fixture.repositories.audit.records
    )

    episode = client.post(
        "/api/v1/adoption/episodes",
        json=_episode_payload(
            "attempt:learning-success",
            cast(str, retrieval_data["retrieval_record_id"]),
            "output:learning-success",
            ["evidence:learning-episode"],
        ),
    )
    assert episode.status_code == 200
    assert _data(episode)["terminal_outcome"] == "completed"


def test_provider_failure_is_denied_and_release_projections_are_redacted_and_blocked(
    api_fixture: ApiFixture,
) -> None:
    """Provider authorization, learning projections, and release gates fail closed at the API."""
    _register(api_fixture.client)
    provider = api_fixture.client.post(
        "/api/v1/adoption/governance/providers",
        json={
            "domain_id": _DOMAIN,
            "pack_version": _PACK_VERSION,
            "agent_id": _AGENT_ID,
            "provider_id": "missing-provider-declaration",
            "capability": "text.generate",
        },
    )
    assert provider.status_code == 200
    provider_data = _data(provider)
    assert provider_data["outcome"] == "denied"
    assert provider_data["allowed"] is False
    assert "missing_domain_pack_declaration" in str(provider_data["reason_code"])

    retrieval = api_fixture.client.post(
        "/api/v1/adoption/retrievals",
        json=_retrieval_payload("attempt:observability"),
    )
    assert retrieval.status_code == 200
    retrieval_data = _data(retrieval)
    episode = api_fixture.client.post(
        "/api/v1/adoption/episodes",
        json=_episode_payload(
            "attempt:observability",
            cast(str, retrieval_data["retrieval_record_id"]),
            "output:observability",
        ),
    )
    assert episode.status_code == 200

    observability = api_fixture.client.get(f"/api/v1/adoption/observability/{_AGENT_ID}")
    assert observability.status_code == 200
    projection = _data(observability)
    assert projection["learning_episode_count"] == 1
    assert projection["assessed_lesson_count"] == 0
    assert projection["retrieved_lesson_reuse_count"] == 0
    assert "sensitive lesson content" not in repr(projection)
    assert "output:observability" not in repr(projection)

    verification = api_fixture.client.post(
        "/api/v1/adoption/release/verify",
        json={
            "pack_id": _PACK_ID,
            "immutable_version": _PACK_VERSION,
            "pack_contract_version": "1.0.0",
            "host_contract_version": "1.0.0",
            "alc_version": "1.0.0",
            "workflow_id": "adoption-api.workflow",
            "fixed_seed": "adoption-api-seed",
            "fixture_digest": "sha256:adoption-api-fixtures",
            "checks": [
                {
                    "name": "schema.contract",
                    "layer": "schema",
                    "passed": True,
                    "evidence_reference": "evidence:schema",
                },
                {
                    "name": "integration.coverage",
                    "layer": "integration",
                    "passed": True,
                    "evidence_reference": "evidence:integration",
                },
            ],
            "integration_coverage_complete": True,
        },
    )
    assert verification.status_code == 200
    verification_data = _data(verification)
    assert verification_data["release_decision_status"] == "eligible"
    assert verification_data["check_count"] == 2
    assert verification_data["passed_check_count"] == 2
    assert verification_data["failure_count"] == 0

    blocked_video = api_fixture.client.post(
        "/api/v1/adoption/release/video",
        json={
            "handoff": _handoff_payload("handoff:video-release"),
            "pack_id": _PACK_ID,
            "immutable_version": _PACK_VERSION,
            "workflow_id": "adoption-api.video-workflow",
            "gates": {},
            "evidence_references": ["evidence:video-release"],
        },
    )
    assert blocked_video.status_code == 200
    video_data = _data(blocked_video)
    assert video_data["status"] == "blocked"
    assert video_data["artifact_released"] is False
    assert video_data["unmet_gate_references"] == [
        "rights",
        "consent",
        "continuity",
        "media_quality",
        "channel",
        "approval",
    ]
    assert any(
        record.action == "video.release.blocked"
        for record in api_fixture.repositories.audit.records
    )
