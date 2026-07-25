"""Public_API coverage for the VA translation-only routes."""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi.testclient import TestClient

from app.api.v1.dependencies import AuthenticatedRequestContext, get_authenticated_request_context
from app.api.v1.services import ControlPlaneServices, get_control_plane_services
from app.main import create_app
from app.models.common import RecordMetadata
from app.models.control_plane import (
    CommonPatternVersion,
    CommonPatternVersionId,
    ContractStatus,
)
from app.models.identifiers import (
    ActorId,
    CorrelationId,
    OrganizationId,
    RecordId,
)

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_ORG = OrganizationId("va-api-org")
_CORRELATION = CorrelationId("va-api-correlation")


def _services() -> ControlPlaneServices:
    services = ControlPlaneServices()
    pattern = CommonPatternVersion(
        metadata=RecordMetadata(
            record_id=RecordId("va-api-pattern-record"),
            organization_id=_ORG,
            correlation_id=_CORRELATION,
            schema_version=1,
            version=1,
            created_at=_NOW,
            updated_at=_NOW,
        ),
        pattern_version_id=CommonPatternVersionId("va-api-pattern-v1"),
        status=ContractStatus.PUBLISHED,
        graph_template={"va_templates": ("campaign",)},
        slot_constraints={"required": ("producer",)},
        compatibility_rules={"va_production_phases": ("production",)},
        risk_requirements={"approval": "required"},
        verification_requirements={"quality": True},
        provenance={"source": "registry"},
        content_digest="sha256:va-api-pattern-v1",
    )
    with services.control_plane_database.unit_of_work() as unit_of_work:
        assert unit_of_work.common_contracts.append_pattern_version(pattern).is_success
    return services


def test_va_metadata_and_actions_exist_only_under_public_api() -> None:
    application = create_app()
    services = _services()
    context = AuthenticatedRequestContext(
        tenant_id=_ORG,
        actor_id=ActorId("va-api-actor"),
        correlation_id=_CORRELATION,
    )
    application.dependency_overrides[get_authenticated_request_context] = lambda: context
    application.dependency_overrides[get_control_plane_services] = lambda: services

    with TestClient(application) as client:
        unversioned = client.get(
            "/va/patterns/va-api-pattern-v1/metadata",
            params={"template": "campaign", "production_phase": "production"},
        )
        metadata = client.get(
            "/api/v1/va/patterns/va-api-pattern-v1/metadata",
            params={"template": "campaign", "production_phase": "production"},
        )
        invalid_action = client.post(
            "/api/v1/va/actions",
            json={
                "pattern_version_id": "va-api-pattern-v1",
                "template": "unknown",
                "production_phase": "production",
                "action": "dispatch_run",
                "run_reference": "run-1",
                "idempotency_key": "va-invalid-key",
            },
        )
        valid_action = client.post(
            "/api/v1/va/actions",
            json={
                "pattern_version_id": "va-api-pattern-v1",
                "template": "campaign",
                "production_phase": "production",
                "action": "dispatch_run",
                "run_reference": "run-1",
                "idempotency_key": "va-valid-key",
            },
        )

    assert unversioned.status_code == 404
    assert metadata.status_code == 200
    assert metadata.json()["data"]["valid"] is True
    assert invalid_action.status_code == 422
    assert invalid_action.json()["error"]["fields"] == [
        {"field": "template", "reason": "must be allowed by the published common pattern"}
    ]
    assert valid_action.status_code == 200
    assert valid_action.json()["data"]["canonical_command"] == "run.dispatch"
    assert valid_action.json()["data"]["canonical_subject_reference"] == "run:run-1"


def test_va_metadata_route_returns_safe_invalid_pattern_result() -> None:
    """Missing pattern metadata remains a field-safe public validation projection."""
    application = create_app()
    services = _services()
    context = AuthenticatedRequestContext(
        tenant_id=_ORG,
        actor_id=ActorId("va-api-actor"),
        correlation_id=_CORRELATION,
    )
    application.dependency_overrides[get_authenticated_request_context] = lambda: context
    application.dependency_overrides[get_control_plane_services] = lambda: services

    with TestClient(application) as client:
        response = client.get(
            "/api/v1/va/patterns/missing-pattern/metadata",
            params={"template": "campaign", "production_phase": "production"},
        )

    assert response.status_code == 200
    metadata = response.json()["data"]
    assert metadata["pattern_version_id"] == "missing-pattern"
    assert metadata["valid"] is False
    assert metadata["pattern_content_digest"] is None
    assert metadata["validation_issues"] == [
        {
            "field": "pattern_version_id",
            "reason": "must reference an available published common pattern version",
        }
    ]
