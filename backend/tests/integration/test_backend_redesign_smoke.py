"""Final isolated FastAPI smoke coverage for the composed backend redesign host."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import cast

from fastapi.testclient import TestClient

from app.api.v1.dependencies import AuthenticatedRequestContext
from app.contracts.release import (
    ContractReleaseService,
    InMemoryContractLifecycleRepository,
    InMemoryManualRetentionHandoff,
    ReleaseStatus,
)
from app.core.configuration import StartupComponent
from app.main import API_V1_PREFIX, create_app, is_public_api_path
from app.models.common import RecordMetadata
from app.models.control_plane import (
    CommonPatternVersion,
    CommonPatternVersionId,
    ContractStatus,
    DeploymentConfiguration,
)
from app.models.identifiers import ActorId, CorrelationId, OrganizationId, RecordId

# **Validates: Requirements 1.1, 1.4, 2.1, 5.1, 10.2, 13.1, 14.1, 15.1, 16.1**

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_ORGANIZATION = OrganizationId("smoke-org")
_CORRELATION = CorrelationId("smoke-correlation")


def _configuration() -> DeploymentConfiguration:
    """Return a complete deployment-selected configuration with no external adapters."""
    return DeploymentConfiguration(
        metadata=RecordMetadata(
            record_id=RecordId("smoke-deployment"),
            organization_id=OrganizationId("deployment"),
            correlation_id=_CORRELATION,
            schema_version=1,
            version=1,
            created_at=_NOW,
            updated_at=_NOW,
        ),
        configuration_id="smoke-v1",
        trusted_origins=("https://console.example",),
        identity_integration="isolated_identity",
        persistence_adapter="in_memory",
        dispatch_adapter="local_inline",
        retention_policies={
            "audit_records": {
                "max_age_days": 30,
                "action": "archive",
                "preserve_authorization_evidence": True,
                "preserve_provenance_evidence": True,
            }
        },
        rate_limits={"/api/v1": 100},
        feature_flags={"events": True},
        secret_references=(),
        production_transport_enabled=True,
        work_recovery_policy={
            "claim_expiry_decision": "reclaim",
            "worker_stop_decision": "manual_recovery",
            "max_attempts": 3,
            "retry_delay_seconds": 1,
        },
    )


def _published_pattern() -> CommonPatternVersion:
    """Create the published common-pattern prerequisite for the VA command."""
    return CommonPatternVersion(
        metadata=RecordMetadata(
            record_id=RecordId("smoke-pattern-record"),
            organization_id=_ORGANIZATION,
            correlation_id=_CORRELATION,
            schema_version=1,
            version=1,
            created_at=_NOW,
            updated_at=_NOW,
        ),
        pattern_version_id=CommonPatternVersionId("smoke-pattern-v1"),
        status=ContractStatus.PUBLISHED,
        graph_template={"va_templates": ("campaign",)},
        slot_constraints={"required": ("producer",)},
        compatibility_rules={"va_production_phases": ("production",)},
        risk_requirements={"approval": "required"},
        verification_requirements={"quality": True},
        provenance={"source": "isolated-smoke"},
        content_digest="sha256:smoke-pattern-v1",
    )


def test_validated_configuration_activates_public_composition_and_artifacts() -> None:
    """One isolated host composes public query/command, SSE, and release paths end to end."""
    context = AuthenticatedRequestContext(
        _ORGANIZATION,
        ActorId("smoke-actor"),
        _CORRELATION,
        permissions=frozenset({"control_plane:*"}),
    )
    application = create_app(
        deployment_configuration=_configuration(),
        trusted_context_resolver=lambda _request: context,
    )
    configuration_status = application.state.configuration_service.status
    assert configuration_status is not None
    assert all(configuration_status.is_enabled(component) for component in StartupComponent)
    composition = application.state.control_plane
    assert composition.services.command_service is application.state.command_service
    assert composition.governed_local_adapter is application.state.governed_local_adapter

    with application.state.control_plane_database.unit_of_work() as unit_of_work:
        assert unit_of_work.common_contracts.append_pattern_version(_published_pattern()).is_success

    with TestClient(application, base_url="https://testserver") as client:
        context_response = client.get(f"{API_V1_PREFIX}/context")
        metadata_response = client.get(
            f"{API_V1_PREFIX}/va/patterns/smoke-pattern-v1/metadata",
            params={"template": "campaign", "production_phase": "production"},
        )
        action_response = client.post(
            f"{API_V1_PREFIX}/va/actions",
            json={
                "pattern_version_id": "smoke-pattern-v1",
                "template": "campaign",
                "production_phase": "production",
                "action": "dispatch_run",
                "run_reference": "smoke-run",
                "idempotency_key": "smoke-command-key",
            },
        )
        stream_response = client.get(f"{API_V1_PREFIX}/events/work/stream")

    assert context_response.status_code == 200
    assert context_response.json()["data"]["organization_id"] == str(_ORGANIZATION)
    assert metadata_response.status_code == 200
    assert metadata_response.json()["data"]["valid"] is True
    assert action_response.status_code == 200
    action_data = cast(dict[str, object], action_response.json()["data"])
    assert action_data["canonical_command"] == "run.dispatch"
    assert action_data["canonical_subject_reference"] == "run:smoke-run"
    assert stream_response.status_code == 200
    assert stream_response.headers["content-type"].startswith("text/event-stream")
    assert stream_response.headers["cache-control"] == "no-store"
    assert stream_response.headers["x-correlation-id"] == str(_CORRELATION)

    database_state = application.state.control_plane_database._state
    assert len(database_state.work_items) == len(database_state.audits) == 1
    assert len(database_state.events) == len(database_state.outbox) == 1

    release = ContractReleaseService(
        application,
        InMemoryContractLifecycleRepository(),
        InMemoryManualRetentionHandoff(),
        clock=lambda: _NOW,
    ).publish("1.0.0")

    assert release.status is ReleaseStatus.PUBLISHED
    assert release.openapi_document is not None
    paths = cast(dict[str, object], release.openapi_document["paths"])
    assert paths and all(is_public_api_path(path) for path in paths)
    assert f"{API_V1_PREFIX}/va/actions" in paths
    assert f"{API_V1_PREFIX}/events/{{topic}}/stream" in paths
    assert release.typed_artifact is not None
    assert release.typed_artifact.strip()
