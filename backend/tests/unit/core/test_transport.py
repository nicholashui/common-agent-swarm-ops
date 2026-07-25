"""Focused tests for production transport and public rate-limit middleware."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.core.ingress import IngressPolicy
from app.core.transport import TransportSecurityPolicy
from app.main import create_app
from app.models.common import RecordMetadata
from app.models.control_plane import DeploymentConfiguration, SessionModel
from app.models.identifiers import CorrelationId, OrganizationId, RecordId

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_TRUSTED_ORIGIN = "https://console.example"


def _configuration(
    *,
    session_model: SessionModel = SessionModel.BEARER_TOKEN,
    rate_limit: int = 20,
) -> DeploymentConfiguration:
    return DeploymentConfiguration(
        metadata=RecordMetadata(
            record_id=RecordId("transport-configuration"),
            organization_id=OrganizationId("deployment"),
            correlation_id=CorrelationId("transport-test"),
            schema_version=1,
            version=1,
            created_at=_NOW,
            updated_at=_NOW,
        ),
        configuration_id="transport-v1",
        trusted_origins=(_TRUSTED_ORIGIN,),
        identity_integration="oidc",
        persistence_adapter="postgres",
        dispatch_adapter="queue",
        retention_policies={
            "audit_records": {
                "max_age_days": 30,
                "action": "delete",
                "preserve_authorization_evidence": False,
                "preserve_provenance_evidence": False,
            }
        },

        rate_limits={"/api/v1": rate_limit},
        feature_flags={},
        secret_references=(),
        production_transport_enabled=True,
        session_model=session_model,
    )


def test_production_transport_rejects_plain_http_with_safe_envelope() -> None:
    """Production requests cannot reach routing unless the ASGI transport is HTTPS."""
    application = create_app(deployment_configuration=_configuration())

    with TestClient(application, base_url="http://testserver") as client:
        response = client.get("/api/v1/context")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "error": {
            "code": "validation_failed",
            "message": "The request could not be validated.",
            "correlation_id": response.headers["X-Correlation-ID"],
            "retryable": False,
            "fields": [],
        }
    }
    assert response.headers["Strict-Transport-Security"].startswith("max-age=")


@pytest.mark.parametrize(
    ("session_model", "allows_credentials"),
    (
        (SessionModel.BEARER_TOKEN, False),
        (SessionModel.COOKIE, True),
    ),
)
def test_production_transport_applies_exact_origin_and_session_headers(
    session_model: SessionModel, allows_credentials: bool
) -> None:
    """Only the configured origin is reflected and cookie sessions enable credentials."""
    application = create_app(
        deployment_configuration=_configuration(session_model=session_model)
    )

    with TestClient(application, base_url="https://testserver") as client:
        response = client.get("/api/v1/context", headers={"Origin": _TRUSTED_ORIGIN})

    assert response.headers["Access-Control-Allow-Origin"] == _TRUSTED_ORIGIN
    assert (response.headers.get("Access-Control-Allow-Credentials") == "true") is (
        allows_credentials
    )
    assert response.headers["Vary"] == "Origin"
    assert response.headers["Content-Security-Policy"].startswith("default-src 'none'")
    assert response.headers["Permissions-Policy"] == "camera=(), geolocation=(), microphone=()"
    assert response.headers["Referrer-Policy"] == "no-referrer"
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Cache-Control"] == "no-store"



def test_production_transport_rejects_untrusted_origin_before_routing() -> None:
    """An untrusted browser origin receives one safe denial without CORS authorization."""
    application = create_app(deployment_configuration=_configuration())

    with TestClient(application, base_url="https://testserver") as client:
        response = client.get(
            "/api/v1/resources/possibly-protected",
            headers={"Origin": "https://attacker.example"},
        )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["error"] == {
        "code": "authorization_denied",
        "message": "You are not authorized to perform this action.",
        "correlation_id": response.headers["X-Correlation-ID"],
        "retryable": False,
        "fields": [],
    }
    assert "Access-Control-Allow-Origin" not in response.headers


def test_trusted_preflight_is_bounded_and_does_not_reach_a_route() -> None:
    """Configured preflight methods and headers receive an empty restrictive response."""
    application = create_app(
        deployment_configuration=_configuration(session_model=SessionModel.COOKIE)
    )

    with TestClient(application, base_url="https://testserver") as client:
        response = client.options(
            "/api/v1/context",
            headers={
                "Origin": _TRUSTED_ORIGIN,
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Authorization, Content-Type",
            },
        )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.content == b""
    assert response.headers["Access-Control-Allow-Origin"] == _TRUSTED_ORIGIN
    assert response.headers["Access-Control-Allow-Credentials"] == "true"
    assert response.headers["Access-Control-Allow-Headers"] == "authorization, content-type"
    assert "GET" in response.headers["Access-Control-Allow-Methods"]


def test_production_transport_rejects_disallowed_preflight_headers() -> None:
    """A trusted origin cannot broaden the configured browser request header allowlist."""
    application = create_app(deployment_configuration=_configuration())

    with TestClient(application, base_url="https://testserver") as client:
        response = client.options(
            "/api/v1/context",
            headers={
                "Origin": _TRUSTED_ORIGIN,
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "X-Untrusted-Header",
            },
        )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["error"] == {
        "code": "validation_failed",
        "message": "The request could not be validated.",
        "correlation_id": response.headers["X-Correlation-ID"],
        "retryable": False,
        "fields": [],
    }
    assert response.headers["Access-Control-Allow-Origin"] == _TRUSTED_ORIGIN
    assert response.headers["X-Content-Type-Options"] == "nosniff"


@pytest.mark.parametrize("path", ("/api/v1/context", "/api/v1/resources/hidden"))
def test_rate_limit_is_resource_independent_and_returns_retry_after(path: str) -> None:
    """A peer and endpoint limit never depends on protected resource existence."""
    application = create_app(
        deployment_configuration=_configuration(rate_limit=1),
        ingress_policy=IngressPolicy(rate_window_seconds=30),
    )

    with TestClient(application, base_url="https://testserver") as client:
        client.get(path)
        response = client.get(path)

    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    assert 1 <= int(response.headers["Retry-After"]) <= 30
    assert response.json()["error"] == {
        "code": "rate_limited",
        "message": "Too many requests were received. Try again later.",
        "correlation_id": response.headers["X-Correlation-ID"],
        "retryable": True,
        "fields": [],
    }


def test_transport_policy_rejects_wildcard_or_non_https_production_origins() -> None:
    """Production origin policy cannot be weakened to a wildcard or cleartext origin."""
    for origin in (
        "*",
        "http://console.example",
        "https://console.example/",
        "https://console.example/path",
        "https://user:password@console.example",
        "https://console.example:not-a-port",
    ):
        with pytest.raises(ValueError, match="exact HTTPS origins"):
            TransportSecurityPolicy(
                production_transport_enabled=True,
                trusted_origins=(origin,),
            )