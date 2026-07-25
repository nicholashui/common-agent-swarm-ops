"""Property checks for safe deployment configuration and browser transport."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Literal

from fastapi import status
from fastapi.testclient import TestClient
from httpx import Response
from hypothesis import given, settings, strategies as st

from app.core.configuration import ConfigurationService, StartupComponent
from app.core.ingress import IngressPolicy
from app.main import create_app
from app.models.common import RecordMetadata
from app.models.contracts import ErrorCode
from app.models.control_plane import DeploymentConfiguration, SessionModel
from app.models.identifiers import CorrelationId, OrganizationId, RecordId

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_SECRET_REFERENCE = "DEPLOYMENT_SECRET"
_SAFE_VALUES = st.text(alphabet="abcdefghijklmnopqrstuvwxyz0123456789", min_size=1, max_size=8)
_RESOURCE_PATHS = ("/api/v1/context", "/api/v1/resources/possibly-protected")
_SECURITY_HEADERS = (
    "Strict-Transport-Security",
    "Content-Security-Policy",
    "Permissions-Policy",
    "Referrer-Policy",
    "X-Content-Type-Options",
    "X-Frame-Options",
    "Cache-Control",
)


@dataclass
class _SecretManagerFake:
    """Deterministically resolves configured values without a deployment secret manager."""

    values: dict[str, str]
    calls: list[str] = field(default_factory=list)

    def get_secret(self, reference: str) -> str | None:
        self.calls.append(reference)
        return self.values.get(reference)


def _configuration(
    value: str,
    *,
    trusted_origin: str,
    production_transport_enabled: bool,
    session_model: SessionModel,
    rate_limit: int = 20,
    invalid_component: StartupComponent | None = None,
) -> DeploymentConfiguration:
    """Build a valid deployment configuration or a configuration with one invalid domain."""
    identity_integration = "oidc"
    persistence_adapter = "postgres"
    dispatch_adapter = "local_queue"
    retention_policies: dict[str, object] = {
        "audit_records": {
            "max_age_days": 30,
            "action": "archive",
            "preserve_authorization_evidence": True,
            "preserve_provenance_evidence": True,
        }
    }
    rate_limits: dict[str, object] = {"/api/v1": rate_limit}
    feature_flags: dict[str, object] = {"events": True}
    origins = (trusted_origin,)
    if invalid_component is StartupComponent.ORIGINS:
        origins = (f"{trusted_origin}/path",)
    elif invalid_component is StartupComponent.IDENTITY:
        identity_integration = "invalid.identity"
    elif invalid_component is StartupComponent.PERSISTENCE:
        persistence_adapter = "invalid.adapter"
    elif invalid_component is StartupComponent.DISPATCH:
        dispatch_adapter = "invalid.adapter"
    elif invalid_component is StartupComponent.RETENTION:
        retention_policies = {"audit_records": {"max_age_days": 0}}
    elif invalid_component is StartupComponent.RATE_LIMITS:
        rate_limits = {"/api/v1": 0}
    elif invalid_component is StartupComponent.FEATURE_FLAGS:
        feature_flags = {"invalid.flag": True}

    return DeploymentConfiguration(
        metadata=RecordMetadata(
            record_id=RecordId(f"configuration-{value}"),
            organization_id=OrganizationId("deployment"),
            correlation_id=CorrelationId("property-18"),
            schema_version=1,
            version=1,
            created_at=_NOW,
            updated_at=_NOW,
        ),
        configuration_id=f"deployment-{value}",
        trusted_origins=origins,
        identity_integration=identity_integration,
        persistence_adapter=persistence_adapter,
        dispatch_adapter=dispatch_adapter,
        retention_policies=retention_policies,
        rate_limits=rate_limits,
        feature_flags=feature_flags,
        secret_references=(_SECRET_REFERENCE,),
        production_transport_enabled=production_transport_enabled,
        session_model=session_model,
    )


def _rate_limit_response(
    configuration: DeploymentConfiguration, path: str, trusted_origin: str
) -> Response:
    """Consume one deterministic slot and return the next public response."""
    application = create_app(
        deployment_configuration=configuration,
        ingress_policy=IngressPolicy(rate_window_seconds=30),
    )
    with TestClient(application, base_url="https://testserver") as client:
        client.get(path, headers={"Origin": trusted_origin})
        return client.get(path, headers={"Origin": trusted_origin})


def _public_error_shape(response: Response) -> tuple[object, object, object, object]:
    """Compare public errors without their request-specific correlation identifier."""
    payload = response.json()["error"]
    return payload["code"], payload["message"], payload["retryable"], payload["fields"]


# Feature: backend-redesign, Property 18
# **Validates: Requirements 13.1, 13.2, 13.6, 13.7, 13.8**
@settings(max_examples=100, deadline=None)
@given(
    value=_SAFE_VALUES,
    invalid_component=st.one_of(st.none(), st.sampled_from(tuple(StartupComponent))),
    production_transport_enabled=st.booleans(),
    session_model=st.sampled_from(tuple(SessionModel)),
    request_uses_https=st.booleans(),
    origin_kind=st.sampled_from(("none", "trusted", "untrusted")),
    rate_limit_reached=st.booleans(),
)
def test_property_18_deployment_configuration_and_transport_fail_safely(
    value: str,
    invalid_component: StartupComponent | None,
    production_transport_enabled: bool,
    session_model: SessionModel,
    request_uses_https: bool,
    origin_kind: Literal["none", "trusted", "untrusted"],
    rate_limit_reached: bool,
) -> None:
    """Startup failures isolate components and public transport failures disclose no resources."""
    trusted_origin = f"https://console-{value}.example"
    secret_value = f"secret-value-{value}"
    secret_manager = _SecretManagerFake({_SECRET_REFERENCE: secret_value})
    startup_configuration = _configuration(
        value,
        trusted_origin=trusted_origin,
        production_transport_enabled=production_transport_enabled,
        session_model=session_model,
        invalid_component=invalid_component,
    )
    startup_status = ConfigurationService(environment={}, secret_manager=secret_manager).initialize(
        startup_configuration
    )

    assert secret_manager.calls == [_SECRET_REFERENCE]
    for component in StartupComponent:
        is_affected = component is invalid_component
        assert startup_status.is_enabled(component) is not is_affected
        failure = startup_status.failure_for(component)
        if is_affected:
            assert failure is not None and failure.code is ErrorCode.CONFIGURATION_INVALID
            assert secret_value not in repr(failure)
            assert _SECRET_REFERENCE not in repr(failure)
        else:
            assert failure is None

    transport_configuration = _configuration(
        value,
        trusted_origin=trusted_origin,
        production_transport_enabled=production_transport_enabled,
        session_model=session_model,
    )
    origin = {
        "none": None,
        "trusted": trusted_origin,
        "untrusted": f"https://attacker-{value}.example",
    }[origin_kind]
    headers = {} if origin is None else {"Origin": origin}
    base_url = "https://testserver" if request_uses_https else "http://testserver"
    application = create_app(deployment_configuration=transport_configuration)
    with TestClient(application, base_url=base_url) as client:
        transport_response = client.get("/api/v1/context", headers=headers)

    if production_transport_enabled:
        for header in _SECURITY_HEADERS:
            assert header in transport_response.headers
        if not request_uses_https:
            assert transport_response.status_code == status.HTTP_400_BAD_REQUEST
            assert _public_error_shape(transport_response)[0] == "validation_failed"
        elif origin_kind == "untrusted":
            assert transport_response.status_code == status.HTTP_403_FORBIDDEN
            assert _public_error_shape(transport_response)[0] == "authorization_denied"
            assert "Access-Control-Allow-Origin" not in transport_response.headers
        else:
            assert transport_response.status_code == status.HTTP_401_UNAUTHORIZED
            if origin_kind == "trusted":
                assert transport_response.headers["Access-Control-Allow-Origin"] == trusted_origin
                assert transport_response.headers["Vary"] == "Origin"
                assert (
                    transport_response.headers.get("Access-Control-Allow-Credentials") == "true"
                ) is (session_model is SessionModel.COOKIE)
            else:
                assert "Access-Control-Allow-Origin" not in transport_response.headers
    else:
        assert transport_response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Strict-Transport-Security" not in transport_response.headers

    rate_limit = 1 if rate_limit_reached else 2
    rate_configuration = _configuration(
        value,
        trusted_origin=trusted_origin,
        production_transport_enabled=True,
        session_model=session_model,
        rate_limit=rate_limit,
    )
    rate_responses = tuple(
        _rate_limit_response(rate_configuration, path, trusted_origin) for path in _RESOURCE_PATHS
    )
    if rate_limit_reached:
        for rate_response in rate_responses:
            assert rate_response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
            assert int(rate_response.headers["Retry-After"]) > 0
            assert _public_error_shape(rate_response) == (
                "rate_limited",
                "Too many requests were received. Try again later.",
                True,
                [],
            )
            assert secret_value not in repr(rate_response.json())
            assert _SECRET_REFERENCE not in repr(rate_response.json())
        assert _public_error_shape(rate_responses[0]) == _public_error_shape(rate_responses[1])
    else:
        assert all(
            response.status_code != status.HTTP_429_TOO_MANY_REQUESTS for response in rate_responses
        )
