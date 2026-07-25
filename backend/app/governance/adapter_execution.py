"""Execution scopes and declarations for governed provider adapters."""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Mapping
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from enum import StrEnum
from math import isfinite
from types import MappingProxyType
from typing import Protocol, cast


class BrokerOnlyAdapterError(PermissionError):
    """Raised when a local adapter is called outside HostToolBroker."""


class ProviderDenialReason(StrEnum):
    """Stable, redaction-safe reasons for refusing a provider action."""

    MISSING_DOMAIN_PACK_DECLARATION = "missing_domain_pack_declaration"
    MISSING_CAPABILITY_DECLARATION = "missing_capability_declaration"
    CAPABILITY_NOT_DECLARED = "capability_not_declared"
    MISSING_COST_DECLARATION = "missing_cost_declaration"
    MISSING_RETENTION_DECLARATION = "missing_retention_declaration"
    MISSING_RESIDENCY_DECLARATION = "missing_residency_declaration"
    MISSING_SAFETY_DECLARATION = "missing_safety_declaration"
    PROVIDER_NOT_AUTHORIZED = "provider_not_authorized"
    PROVIDER_NOT_VERIFICATION_MOCK = "provider_not_verification_mock"
    PROVIDER_ID_MISMATCH = "provider_id_mismatch"
    PROVIDER_TIMEOUT = "provider_timeout"
    UNSAFE_PROVIDER_RESULT = "unsafe_provider_result"
    PROVIDER_BUDGET_EXCEEDED = "provider_budget_exceeded"
    PROVIDER_UNAVAILABLE = "provider_unavailable"


@dataclass(frozen=True, slots=True)
class ProviderAdapterDeclaration:
    """The complete provider declaration required by a Domain_Pack.

    Missing values are represented as ``None`` or an empty collection instead of
    raising during construction.  That is intentional: an incomplete declaration
    must produce an auditable denial, not bypass governance through a validation
    exception.
    """

    provider_id: str = ""
    capabilities: frozenset[str] | tuple[str, ...] = frozenset()
    capability: str | None = None
    cost_limit: float | int | None = None
    retention_policy: str | None = None
    residency: str | None = None
    safety_policy: str | None = None

    def __post_init__(self) -> None:
        """Normalize declaration collections while retaining incomplete fields."""
        raw_capabilities: Iterable[object]
        raw_value = cast(object, self.capabilities)
        if isinstance(raw_value, str):
            raw_capabilities = (raw_value,)
        elif raw_value is None:
            raw_capabilities = ()
        else:
            raw_capabilities = cast(Iterable[object], raw_value)
        normalized = frozenset(
            value.strip() for value in raw_capabilities if isinstance(value, str) and value.strip()
        )
        if isinstance(self.capability, str) and self.capability.strip():
            normalized = normalized | frozenset((self.capability.strip(),))
        object.__setattr__(self, "capabilities", normalized)
        if isinstance(self.provider_id, str):
            object.__setattr__(self, "provider_id", self.provider_id.strip())
        for name in ("retention_policy", "residency", "safety_policy"):
            value = getattr(self, name)
            if isinstance(value, str):
                object.__setattr__(self, name, value.strip())

    @property
    def is_complete(self) -> bool:
        """Return whether every required declaration is explicitly present and valid."""
        return not provider_declaration_failures(self)


@dataclass(frozen=True, slots=True)
class ProviderAuthorizationDecision:
    """A provider authorization decision that cannot be truthy when denied."""

    provider_id: str
    capability: str
    allowed: bool
    denied_reasons: tuple[ProviderDenialReason, ...] = ()
    audit_recorded: bool | None = None

    @property
    def permitted(self) -> bool:
        """Return whether all provider declaration checks passed."""
        return self.allowed and not self.denied_reasons

    @property
    def is_allowed(self) -> bool:
        """Return the typed authorization outcome using the common vocabulary."""
        return self.permitted

    def __bool__(self) -> bool:
        """Prevent callers from treating a partial decision as authorization."""
        return self.permitted


class ProviderAdapter(Protocol):
    """The narrow interface required by the provider governance boundary."""

    provider_id: str
    capability: str
    authorized: bool

    def invoke(
        self,
        capability: str,
        arguments: Mapping[str, object],
        *,
        correlation_id: object | None = None,
    ) -> object:
        """Invoke one capability without exposing a raw external client."""


def provider_declaration_failures(
    declaration: ProviderAdapterDeclaration | Mapping[str, object] | None,
) -> tuple[ProviderDenialReason, ...]:
    """Return every missing provider declaration category in stable order."""
    normalized = _coerce_declaration(declaration)
    if normalized is None:
        return (ProviderDenialReason.MISSING_DOMAIN_PACK_DECLARATION,)
    failures: list[ProviderDenialReason] = []
    if not normalized.capabilities:
        failures.append(ProviderDenialReason.MISSING_CAPABILITY_DECLARATION)
    if normalized.cost_limit is None or not _valid_cost_limit(normalized.cost_limit):
        failures.append(ProviderDenialReason.MISSING_COST_DECLARATION)
    if not normalized.retention_policy:
        failures.append(ProviderDenialReason.MISSING_RETENTION_DECLARATION)
    if not normalized.residency:
        failures.append(ProviderDenialReason.MISSING_RESIDENCY_DECLARATION)
    if not normalized.safety_policy:
        failures.append(ProviderDenialReason.MISSING_SAFETY_DECLARATION)
    return tuple(failures)


def authorize_provider_adapter(
    adapter: object,
    declaration: ProviderAdapterDeclaration | Mapping[str, object] | None,
    *,
    capability: str | None = None,
) -> ProviderAuthorizationDecision:
    """Authorize an adapter only against a complete, explicit pack declaration."""
    provider_id = _provider_id(adapter)
    requested_capability = capability or _adapter_capability(adapter)
    reasons = list(provider_declaration_failures(declaration))
    normalized = _coerce_declaration(declaration)
    if normalized is not None:
        if requested_capability not in normalized.capabilities:
            reasons.append(
                ProviderDenialReason.CAPABILITY_NOT_DECLARED
                if normalized.capabilities
                else ProviderDenialReason.MISSING_CAPABILITY_DECLARATION
            )
        if normalized.provider_id and normalized.provider_id != provider_id:
            reasons.append(ProviderDenialReason.PROVIDER_ID_MISMATCH)
    if getattr(adapter, "authorized", True) is not True:
        reasons.append(ProviderDenialReason.PROVIDER_NOT_AUTHORIZED)
    adapter_capabilities = _adapter_capabilities(adapter)
    if adapter_capabilities and requested_capability not in adapter_capabilities:
        reasons.append(ProviderDenialReason.CAPABILITY_NOT_DECLARED)
    return ProviderAuthorizationDecision(
        provider_id=provider_id,
        capability=requested_capability,
        allowed=not reasons,
        denied_reasons=tuple(dict.fromkeys(reasons)),
    )


_broker_invocation_depth: ContextVar[int] = ContextVar("broker_invocation_depth", default=0)
_provider_invocation_depth: ContextVar[int] = ContextVar("provider_invocation_depth", default=0)


@contextmanager
def broker_invocation() -> Iterator[None]:
    """Mark the current call stack as an authorized local-broker invocation."""
    token = _broker_invocation_depth.set(_broker_invocation_depth.get() + 1)
    try:
        yield
    finally:
        _broker_invocation_depth.reset(token)


def require_broker_invocation() -> None:
    """Reject direct local execution outside HostToolBroker."""
    if _broker_invocation_depth.get() < 1:
        raise BrokerOnlyAdapterError("Local adapters may only execute through HostToolBroker")


@contextmanager
def authorized_provider_invocation() -> Iterator[None]:
    """Mark the current call stack as a governed provider invocation."""
    token = _provider_invocation_depth.set(_provider_invocation_depth.get() + 1)
    try:
        yield
    finally:
        _provider_invocation_depth.reset(token)


def require_authorized_provider_invocation() -> None:
    """Reject provider execution that did not pass the governance execution boundary."""
    if _provider_invocation_depth.get() < 1:
        raise BrokerOnlyAdapterError(
            "Provider adapters may only execute through the governed operation guard"
        )


class AuthorizedMockProviderRegistry:
    """Expose only complete, authorized verification mocks to verification workflows."""

    def __init__(
        self,
        adapters: Iterable[object],
        declarations: Mapping[str, ProviderAdapterDeclaration | Mapping[str, object]],
    ) -> None:
        registered: dict[str, object] = {}
        for adapter in adapters:
            provider_id = _provider_id(adapter)
            if not _is_verification_mock(adapter):
                continue
            declaration = declarations.get(provider_id)
            decision = authorize_provider_adapter(adapter, declaration)
            if decision.permitted:
                if provider_id in registered:
                    raise ValueError("Provider identifiers must be unique")
                registered[provider_id] = adapter
        self._adapters = MappingProxyType(registered)

    def get(self, provider_id: str) -> object | None:
        """Resolve only a mock that passed declaration authorization at registration."""
        return self._adapters.get(provider_id)

    @property
    def provider_ids(self) -> tuple[str, ...]:
        """Return deterministic identifiers exposed to the verification workflow."""
        return tuple(self._adapters)

    def __iter__(self) -> Iterator[object]:
        """Iterate over the immutable authorized mock set."""
        return iter(self._adapters.values())


# Descriptive aliases keep the API discoverable for verification callers.
VerificationProviderRegistry = AuthorizedMockProviderRegistry
AuthorizedProviderAdapterRegistry = AuthorizedMockProviderRegistry
ProviderDeclaration = ProviderAdapterDeclaration
ProviderAuthorization = ProviderAuthorizationDecision


def _coerce_declaration(
    declaration: ProviderAdapterDeclaration | Mapping[str, object] | None,
) -> ProviderAdapterDeclaration | None:
    if declaration is None or isinstance(declaration, ProviderAdapterDeclaration):
        return declaration
    return ProviderAdapterDeclaration(
        provider_id=_text_value(declaration.get("provider_id")) or "",
        capabilities=_capabilities_value(declaration.get("capabilities", ())),
        capability=_text_value(declaration.get("capability")),
        cost_limit=_number_value(declaration.get("cost_limit", declaration.get("cost"))),
        retention_policy=_text_value(declaration.get("retention_policy")),
        residency=_text_value(declaration.get("residency")),
        safety_policy=_text_value(declaration.get("safety_policy")),
    )


def _capabilities_value(value: object) -> frozenset[str] | tuple[str, ...]:
    if isinstance(value, str):
        return (value,)
    if isinstance(value, Iterable):
        return tuple(item for item in value if isinstance(item, str))
    return ()


def _text_value(value: object) -> str | None:
    return value.strip() if isinstance(value, str) and value.strip() else None


def _number_value(value: object) -> float | int | None:
    return value if isinstance(value, (int, float)) and not isinstance(value, bool) else None


def _valid_cost_limit(value: object) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and isfinite(value)
        and value >= 0
    )


def _provider_id(adapter: object) -> str:
    value = getattr(adapter, "provider_id", "")
    return value.strip() if isinstance(value, str) else ""


def _adapter_capability(adapter: object) -> str:
    value = getattr(adapter, "capability", "")
    return value.strip() if isinstance(value, str) else ""


def _adapter_capabilities(adapter: object) -> frozenset[str]:
    declared = getattr(adapter, "declared_capabilities", ())
    if isinstance(declared, str):
        declared = (declared,)
    values = {value.strip() for value in declared if isinstance(value, str) and value.strip()}
    capability = _adapter_capability(adapter)
    if capability:
        values.add(capability)
    return frozenset(values)


def _is_verification_mock(adapter: object) -> bool:
    """Require an explicit mock marker; production adapters are never inferred safe."""
    return getattr(adapter, "verification_mock", False) is True
