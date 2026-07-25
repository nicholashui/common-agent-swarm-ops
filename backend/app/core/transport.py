"""Production HTTPS, restrictive origin, security-header, and rate-limit middleware."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from urllib.parse import urlparse

from fastapi import Request, status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from starlette.types import ASGIApp

from app.api.v1.dependencies import get_request_correlation_id
from app.api.v1.errors import public_error_from_detail, public_error_response
from app.core.ingress import EndpointRateLimiter
from app.models.contracts import ErrorCode, ErrorDetail
from app.models.control_plane import DeploymentConfiguration, SessionModel
from app.models.identifiers import CorrelationId

_API_PREFIX = "/api/v1/"
_ALLOWED_METHODS = frozenset({"DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"})
_ALLOWED_HEADERS = frozenset(
    {"accept", "authorization", "content-type", "idempotency-key", "last-event-id"}
)


@dataclass(frozen=True, slots=True)
class TransportSecurityPolicy:
    """Validated browser transport policy derived only from deployment configuration."""

    production_transport_enabled: bool = False
    trusted_origins: tuple[str, ...] = ()
    session_model: SessionModel = SessionModel.BEARER_TOKEN

    def __post_init__(self) -> None:
        if not isinstance(self.session_model, SessionModel):
            raise ValueError("A supported session model is required.")
        if self.production_transport_enabled and not self.trusted_origins:
            raise ValueError("Production transport requires a trusted origin.")
        if len(set(self.trusted_origins)) != len(self.trusted_origins):
            raise ValueError("Trusted origins must be unique.")
        if any(not _is_restrictive_origin(origin) for origin in self.trusted_origins):
            raise ValueError("Trusted origins must be exact HTTPS origins.")

    @classmethod
    def from_deployment(cls, configuration: DeploymentConfiguration) -> TransportSecurityPolicy:
        """Create transport policy without accepting browser-provided settings."""
        return cls(
            production_transport_enabled=configuration.production_transport_enabled,
            trusted_origins=configuration.trusted_origins,
            session_model=configuration.session_model,
        )


class PublicApiRateLimitMiddleware(BaseHTTPMiddleware):
    """Limit requests before routing using endpoint and remote-peer identity only."""

    def __init__(
        self,
        app: ASGIApp,
        *,
        endpoint_rate_limits: Mapping[str, int],
        window_seconds: int,
        rate_limiter: EndpointRateLimiter | None = None,
    ) -> None:
        super().__init__(app)
        if window_seconds <= 0 or any(limit <= 0 for limit in endpoint_rate_limits.values()):
            raise ValueError("Rate limits and their window must be positive.")
        self._endpoint_rate_limits = dict(endpoint_rate_limits)
        self._window_seconds = window_seconds
        self._rate_limiter = rate_limiter or EndpointRateLimiter()

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        endpoint = _matching_endpoint(request.url.path, self._endpoint_rate_limits)
        if endpoint is None:
            return await call_next(request)
        subject = request.client.host if request.client is not None else "unknown-client"
        retry_after = self._rate_limiter.check(
            endpoint=endpoint,
            subject=subject,
            limit=self._endpoint_rate_limits[endpoint],
            window_seconds=self._window_seconds,
        )
        if retry_after is None:
            return await call_next(request)
        correlation_id = get_request_correlation_id(request)
        response = _safe_error_response(
            ErrorCode.RATE_LIMITED,
            status.HTTP_429_TOO_MANY_REQUESTS,
            correlation_id,
            retryable=True,
            headers={"Retry-After": str(retry_after)},
        )
        response.headers["X-Correlation-ID"] = str(correlation_id)
        return response


class ProductionTransportMiddleware(BaseHTTPMiddleware):
    """Enforce production HTTPS and an exact configured browser-origin allowlist."""

    def __init__(self, app: ASGIApp, *, policy: TransportSecurityPolicy) -> None:
        super().__init__(app)
        self._policy = policy
        self._trusted_origins = frozenset(policy.trusted_origins)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if not self._policy.production_transport_enabled:
            return await call_next(request)
        correlation_id = get_request_correlation_id(request)
        if request.url.scheme != "https":
            response = _safe_error_response(
                ErrorCode.VALIDATION_FAILED,
                status.HTTP_400_BAD_REQUEST,
                correlation_id,
            )
            return self._secure(response, origin=None, correlation_id=correlation_id)

        origin = request.headers.get("origin")
        if origin is not None and origin not in self._trusted_origins:
            response = _safe_error_response(
                ErrorCode.AUTHORIZATION_DENIED,
                status.HTTP_403_FORBIDDEN,
                correlation_id,
            )
            return self._secure(response, origin=None, correlation_id=correlation_id)

        if origin is not None and _is_preflight(request):
            response = self._preflight_response(request, correlation_id)
        else:
            response = await call_next(request)
        return self._secure(response, origin=origin, correlation_id=correlation_id)

    def _preflight_response(self, request: Request, correlation_id: CorrelationId) -> Response:
        requested_method = request.headers.get("access-control-request-method", "").upper()
        requested_headers = {
            value.strip().casefold()
            for value in request.headers.get("access-control-request-headers", "").split(",")
            if value.strip()
        }
        if requested_method not in _ALLOWED_METHODS or not requested_headers <= _ALLOWED_HEADERS:
            return _safe_error_response(
                ErrorCode.VALIDATION_FAILED,
                status.HTTP_400_BAD_REQUEST,
                correlation_id,
            )
        response = Response(status_code=status.HTTP_204_NO_CONTENT)
        response.headers["Access-Control-Allow-Methods"] = ", ".join(sorted(_ALLOWED_METHODS))
        if requested_headers:
            response.headers["Access-Control-Allow-Headers"] = ", ".join(sorted(requested_headers))
        response.headers["Access-Control-Max-Age"] = "600"
        return response

    def _secure(
        self,
        response: Response,
        *,
        origin: str | None,
        correlation_id: CorrelationId,
    ) -> Response:
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
        response.headers["Content-Security-Policy"] = (
            "default-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'"
        )
        response.headers["Permissions-Policy"] = "camera=(), geolocation=(), microphone=()"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Correlation-ID"] = str(correlation_id)
        if origin is not None:
            response.headers["Access-Control-Allow-Origin"] = origin
            _append_vary(response, "Origin")
            if self._policy.session_model is SessionModel.COOKIE:
                response.headers["Access-Control-Allow-Credentials"] = "true"
        return response


def _safe_error_response(
    code: ErrorCode,
    status_code: int,
    correlation_id: CorrelationId,
    *,
    retryable: bool = False,
    headers: Mapping[str, str] | None = None,
) -> Response:
    error = public_error_from_detail(
        ErrorDetail(code, "Transport request rejected.", correlation_id, retryable=retryable)
    )
    return public_error_response(error, status_code=status_code, headers=headers)


def _matching_endpoint(path: str, limits: Mapping[str, int]) -> str | None:
    matches = [prefix for prefix in limits if path.startswith(prefix)]
    return max(matches, key=len) if matches else None


def _is_preflight(request: Request) -> bool:
    return request.method == "OPTIONS" and "access-control-request-method" in request.headers


def _is_restrictive_origin(origin: str) -> bool:
    """Accept only a canonical HTTPS browser origin without credentials or path data."""
    if not isinstance(origin, str) or origin != origin.strip():
        return False
    parsed = urlparse(origin)
    try:
        port = parsed.port
    except ValueError:
        return False
    if port == 0:
        return False
    return (
        parsed.scheme == "https"
        and parsed.hostname is not None
        and parsed.username is None
        and parsed.password is None
        and parsed.path == ""
        and not parsed.params
        and not parsed.query
        and not parsed.fragment
        and "*" not in origin
    )


def _append_vary(response: Response, value: str) -> None:
    existing = {item.strip() for item in response.headers.get("Vary", "").split(",") if item}
    response.headers["Vary"] = ", ".join(sorted(existing | {value}))
