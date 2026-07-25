"""Authorized, deterministic Provider_Adapter fakes for adoption verification."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from hashlib import sha256
from threading import RLock

from app.models.contracts import ErrorCode, ErrorDetail, RepositoryError, Result
from app.models.identifiers import CorrelationId


class ProviderFailureMode(StrEnum):
    """External conditions that must deny a provider action."""

    TIMEOUT = "timeout"
    UNSAFE_RESULT = "unsafe_result"
    BUDGET_EXCEEDED = "budget_exceeded"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True, slots=True)
class MockProviderCall:
    """Redacted deterministic evidence of one provider invocation."""

    provider_id: str
    capability: str
    request_digest: str


@dataclass(frozen=True, slots=True)
class MockProviderResult:
    """Reference-only provider result returned by the fake adapter."""

    provider_id: str
    capability: str
    response_reference: str
    response_digest: str


@dataclass
class MockProviderAdapter:
    """A local-only Provider_Adapter with explicit declarations and fail-closed modes.

    The adapter never contacts a network or stores raw request payloads. It accepts a
    request only when it is authorized, declared for the requested capability, and not
    configured to simulate a provider safety or availability failure.
    """

    provider_id: str
    capability: str
    version: str = "1.0.0"
    authorized: bool = True
    verification_mock: bool = field(default=True, init=False)
    cost_limit: int = 1
    retention_policy: str = "reference_only"
    residency: str = "test-local"
    safety_policy: str = "deny-on-unsafe"
    failure_mode: ProviderFailureMode | None = None
    _calls: list[MockProviderCall] = field(default_factory=list, init=False, repr=False)
    _lock: RLock = field(default_factory=RLock, init=False, repr=False)

    def __post_init__(self) -> None:
        if not self.provider_id.strip() or not self.capability.strip():
            raise ValueError("Mock providers require a provider identifier and capability.")
        if not self.version.strip():
            raise ValueError("Mock providers require a version.")
        if self.cost_limit < 0:
            raise ValueError("Mock provider cost limits must not be negative.")
        self.failure_mode = (
            ProviderFailureMode(self.failure_mode) if self.failure_mode is not None else None
        )

    @property
    def declared_capabilities(self) -> frozenset[str]:
        """Return the explicit capability declaration consumed by governance tests."""
        return frozenset((self.capability,))

    @property
    def calls(self) -> tuple[MockProviderCall, ...]:
        """Return redacted calls in deterministic invocation order."""
        with self._lock:
            return tuple(self._calls)

    def execute(
        self, arguments: Mapping[str, object], *, correlation_id: CorrelationId | None = None
    ) -> Result[MockProviderResult, RepositoryError]:
        """Execute a deterministic reference-only provider operation."""
        digest = _digest(arguments)
        with self._lock:
            if not self.authorized:
                return Result.failure(self._denial(ErrorCode.AUTHORIZATION_DENIED, correlation_id))
            if self.failure_mode is not None:
                return Result.failure(self._failure(self.failure_mode, correlation_id))
            self._calls.append(MockProviderCall(self.provider_id, self.capability, digest))
        response_digest = sha256(
            f"{self.provider_id}|{self.version}|{self.capability}|{digest}".encode()
        ).hexdigest()
        result = MockProviderResult(
            provider_id=self.provider_id,
            capability=self.capability,
            response_reference=f"provider:{self.provider_id}:{response_digest[:16]}",
            response_digest=response_digest,
        )
        return Result.success(result)

    def invoke(
        self,
        capability: str,
        arguments: Mapping[str, object],
        *,
        correlation_id: CorrelationId | None = None,
    ) -> Result[MockProviderResult, RepositoryError]:
        """Invoke only the capability declared by this adapter."""
        if capability != self.capability:
            return Result.failure(self._denial(ErrorCode.AUTHORIZATION_DENIED, correlation_id))
        return self.execute(arguments, correlation_id=correlation_id)

    def set_failure_mode(self, failure_mode: ProviderFailureMode | None) -> None:
        """Change the deterministic failure mode for the next calls."""
        self.failure_mode = ProviderFailureMode(failure_mode) if failure_mode is not None else None

    def _denial(self, code: ErrorCode, correlation_id: CorrelationId | None) -> ErrorDetail:
        return ErrorDetail(
            code,
            "Provider action denied.",
            correlation_id or CorrelationId("fake-provider"),
        )

    def _failure(
        self, failure_mode: ProviderFailureMode, correlation_id: CorrelationId | None
    ) -> ErrorDetail:
        code = {
            ProviderFailureMode.TIMEOUT: ErrorCode.HEALTH_UNAVAILABLE,
            ProviderFailureMode.UNSAFE_RESULT: ErrorCode.AUTHORIZATION_DENIED,
            ProviderFailureMode.BUDGET_EXCEEDED: ErrorCode.RATE_LIMITED,
            ProviderFailureMode.UNAVAILABLE: ErrorCode.HEALTH_UNAVAILABLE,
        }[failure_mode]
        return ErrorDetail(
            code,
            f"Provider action denied: {failure_mode.value}.",
            correlation_id or CorrelationId("fake-provider"),
            retryable=failure_mode
            in {
                ProviderFailureMode.TIMEOUT,
                ProviderFailureMode.UNAVAILABLE,
            },
        )


def _digest(arguments: Mapping[str, object]) -> str:
    """Hash canonical JSON rather than retaining provider request content."""
    canonical = json.dumps(arguments, sort_keys=True, separators=(",", ":"), default=str)
    return sha256(canonical.encode("utf-8")).hexdigest()


# The explicit alias makes the test fixture read like the specification terminology.
ProviderAdapter = MockProviderAdapter
