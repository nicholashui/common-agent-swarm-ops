"""Property checks for public contract envelopes and safe output."""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass

from fastapi import FastAPI, Request, status
from hypothesis import given, settings, strategies as st
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import Response
from starlette.types import Scope

from app.api.v1.errors import (
    PUBLIC_ENVELOPE_HEADER,
    public_error_from_detail,
    public_error_response,
    public_success_response,
)
from app.core.ingress import EndpointRateLimiter
from app.core.transport import PublicApiRateLimitMiddleware
from app.models.contracts import ErrorCode, ErrorDetail, ErrorField
from app.models.identifiers import CorrelationId
from app.models.redaction import REDACTED, configure_deployment_secrets

_SAFE_VALUES = st.text(alphabet="abcdefghijklmnopqrstuvwxyz0123456789", min_size=1, max_size=8)
_SAFE_DOMAIN_CODES = (
    ErrorCode.CONFLICT,
    ErrorCode.REPOSITORY_UNAVAILABLE,
    ErrorCode.VALIDATION_FAILED,
)
_SAFE_MESSAGES = {
    ErrorCode.CONFLICT: "The requested change conflicts with the current resource state.",
    ErrorCode.REPOSITORY_UNAVAILABLE: "The service is temporarily unavailable.",
    ErrorCode.VALIDATION_FAILED: "The request could not be validated.",
}


@dataclass
class _DeterministicClock:
    """Mutable monotonic clock used by the actual rate limiter."""

    now: float

    def __call__(self) -> float:
        return self.now


def _request(path: str, correlation_id: CorrelationId) -> Request:
    """Build a request with server-held correlation state and no external transport."""
    scope: Scope = {
        "type": "http",
        "asgi": {"version": "3.0", "spec_version": "2.3"},
        "http_version": "1.1",
        "method": "GET",
        "scheme": "https",
        "path": path,
        "raw_path": path.encode(),
        "query_string": b"",
        "root_path": "",
        "headers": [],
        "client": ("property-test", 50000),
        "server": ("testserver", 443),
        "state": {},
    }
    request = Request(scope)
    request.state.request_correlation_id = correlation_id
    return request


def _dispatch(
    middleware: PublicApiRateLimitMiddleware,
    request: Request,
    call_next: RequestResponseEndpoint,
) -> Response:
    """Run one middleware call synchronously without a nondeterministic HTTP client."""
    return asyncio.run(middleware.dispatch(request, call_next))


# Feature: backend-redesign, Property 1
# **Validates: Requirements 1.2, 1.3, 12.6, 13.5, 13.8**
@settings(max_examples=100, deadline=None)
@given(
    value=_SAFE_VALUES,
    error_code=st.sampled_from(_SAFE_DOMAIN_CODES),
    retryable=st.booleans(),
)
def test_property_1_contract_envelope_and_safe_output_invariants(
    value: str, error_code: ErrorCode, retryable: bool
) -> None:
    """Every generated public outcome has a safe exact envelope and propagated correlation."""
    correlation_id = CorrelationId(f"correlation-{value}")
    secret = f"deployment-value-{value}"
    configure_deployment_secrets((secret,))
    try:
        success_response = public_success_response(
            {
                "resource_id": f"resource-{value}",
                "summary": f"healthy: {secret}",
                "deployment_secret": secret,
                "nested": {"access_token": secret},
            },
            correlation_id,
            status_code=status.HTTP_201_CREATED,
        )
        success_envelope = json.loads(bytes(success_response.body))
        assert success_response.status_code == status.HTTP_201_CREATED
        assert success_response.headers[PUBLIC_ENVELOPE_HEADER] == "1"
        assert success_envelope == {
            "data": {
                "resource_id": f"resource-{value}",
                "summary": f"healthy: {REDACTED}",
                "deployment_secret": REDACTED,
                "nested": {"access_token": REDACTED},
            },
            "meta": {"correlation_id": str(correlation_id)},
        }
        assert secret not in json.dumps(success_envelope)

        public_error = public_error_from_detail(
            ErrorDetail(
                code=error_code,
                message=f"internal diagnostic: {secret}",
                correlation_id=correlation_id,
                retryable=retryable,
                fields=(ErrorField("request", "Invalid value."),),
            )
        )
        error_response = public_error_response(
            public_error,
            status_code=status.HTTP_409_CONFLICT,
        )
        error_envelope = json.loads(bytes(error_response.body))
        assert error_response.headers[PUBLIC_ENVELOPE_HEADER] == "1"
        assert error_envelope == {
            "error": {
                "code": error_code.value,
                "message": _SAFE_MESSAGES[error_code],
                "correlation_id": str(correlation_id),
                "retryable": retryable,
                "fields": [{"field": "request", "reason": "Invalid value."}],
            }
        }
        assert secret not in json.dumps(error_envelope)

        clock = _DeterministicClock(now=100.0)
        middleware = PublicApiRateLimitMiddleware(
            FastAPI(),
            endpoint_rate_limits={"/api/v1/": 1},
            window_seconds=30,
            rate_limiter=EndpointRateLimiter(clock=clock),
        )
        delivered_paths: list[str] = []

        async def call_next(request: Request) -> Response:
            delivered_paths.append(request.url.path)
            return public_success_response({"accepted": True}, correlation_id)

        first_response = _dispatch(
            middleware,
            _request(f"/api/v1/resources/visible-{value}", correlation_id),
            call_next,
        )
        clock.now = 105.0
        rate_limited_response = _dispatch(
            middleware,
            _request(f"/api/v1/resources/hidden-{value}", correlation_id),
            call_next,
        )
        rate_envelope = json.loads(bytes(rate_limited_response.body))

        assert delivered_paths == [f"/api/v1/resources/visible-{value}"]
        assert json.loads(bytes(first_response.body)) == {
            "data": {"accepted": True},
            "meta": {"correlation_id": str(correlation_id)},
        }
        assert rate_limited_response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert rate_limited_response.headers[PUBLIC_ENVELOPE_HEADER] == "1"
        assert rate_limited_response.headers["Retry-After"] == "25"
        assert rate_limited_response.headers["X-Correlation-ID"] == str(correlation_id)
        assert rate_envelope == {
            "error": {
                "code": ErrorCode.RATE_LIMITED.value,
                "message": "Too many requests were received. Try again later.",
                "correlation_id": str(correlation_id),
                "retryable": True,
                "fields": [],
            }
        }
        assert secret not in json.dumps(rate_envelope)
    finally:
        configure_deployment_secrets(())
