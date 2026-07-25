"""Complete, stateless authorization-intersection checks for Host effects."""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from math import isfinite
from types import MappingProxyType
from urllib.parse import urlsplit

from app.models.common import CompatibilityRange


class ApprovalState(StrEnum):
    """The Host-derived approval state for one requested effect."""

    NOT_REQUIRED = "not_required"
    APPROVED = "approved"
    PENDING = "pending"
    DENIED = "denied"


class AuthorizationConstraint(StrEnum):
    """Every independent constraint in a tool authorization intersection."""

    AGENT_ALLOWED_TOOLS = "agent_allowed_tools"
    STEP_DECLARED_TOOLS = "step_declared_tools"
    ROLE_PERMISSIONS = "role_permissions"
    ORGANIZATION_SCOPE = "organization_scope"
    RISK_POLICY = "risk_policy"
    APPROVAL_STATE = "approval_state"


class ScopeConstraint(StrEnum):
    """Independent tenant, pack, identity, memory, and outbound constraints."""

    ORGANIZATION_SCOPE = "organization_scope"
    DOMAIN_SCOPE = "domain_scope"
    PACK_VERSION_RANGE = "pack_version_range"
    AGENT_IDENTITY = "agent_identity"
    MEMORY_SCOPE = "memory_scope"
    OUTBOUND_DESTINATION = "outbound_destination"


@dataclass(frozen=True, slots=True)
class AuthorizationContext:
    """Host-derived authority for a single agent step; never workflow payload authority."""

    agent_id: str
    step_id: str
    organization_id: str
    actor_id: str
    correlation_id: str
    agent_allowed_tools: frozenset[str]
    step_declared_tools: frozenset[str]
    role_allowed_tools: frozenset[str]
    organization_allowed_tools: frozenset[str]
    risk_allowed_tools: frozenset[str]
    approval_state: ApprovalState
    # Adoption authorization scope. These defaults preserve the legacy local-tool API;
    # an explicit data-access or outbound request is still fail-closed when scope is absent.
    domain_id: str | None = None
    pack_version: str | None = None
    supported_pack_range: CompatibilityRange | None = None
    declared_memory_scopes: frozenset[str] = frozenset()
    declared_outbound_destinations: frozenset[str] = frozenset()
    declared_tool_ids: frozenset[str] | None = None


@dataclass(frozen=True, slots=True)
class DataAccessRequest:
    """Untrusted data-access target that must match Host-derived authorization."""

    organization_id: str
    domain_id: str
    pack_version: str
    agent_id: str
    memory_scope: str


@dataclass(frozen=True, slots=True)
class OutboundRequest:
    """An outbound destination request checked before any adapter dispatch."""

    destination: str


@dataclass(frozen=True, slots=True)
class AuthorizationDecision:
    """The complete result of evaluating one requested effect without caching it."""

    adapter_id: str
    denied_constraints: tuple[StrEnum, ...]

    @property
    def permitted(self) -> bool:
        """Return whether all intersection constraints passed."""
        return not self.denied_constraints


class ToolInputValidationError(ValueError):
    """Raised when untrusted adapter input is not safe, local, data-only input."""


type ToolInputValue = (
    str | int | float | bool | None | tuple["ToolInputValue", ...] | Mapping[str, "ToolInputValue"]
)

_SAFE_TOOL_IDENTIFIER = re.compile(r"[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*\Z")
_SAFE_OUTBOUND_HOST = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?(?::[0-9]{1,5})?\Z")
_PROHIBITED_INPUT_KEY_PARTS = frozenset(
    {
        "api_key",
        "apikey",
        "authorization",
        "command",
        "credential",
        "cookie",
        "endpoint",
        "executable",
        "header",
        "host",
        "password",
        "script",
        "secret",
        "shell",
        "token",
        "uri",
        "url",
    }
)


def is_safe_tool_identifier(value: str) -> bool:
    """Return whether an adapter identifier is a local registry identifier."""
    return isinstance(value, str) and _SAFE_TOOL_IDENTIFIER.fullmatch(value) is not None


def is_safe_outbound_destination(value: str) -> bool:
    """Return whether a destination has a safe, comparable host/URI shape."""
    if not isinstance(value, str) or not value or any(character.isspace() for character in value):
        return False
    try:
        parsed = urlsplit(value)
        if parsed.username is not None or parsed.password is not None or parsed.fragment:
            return False
        if parsed.scheme:
            return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
        return _SAFE_OUTBOUND_HOST.fullmatch(value) is not None
    except ValueError:
        return False


class AuthorizationService:
    """Evaluate every authorization factor for every distinct request."""

    def evaluate(
        self,
        context: AuthorizationContext,
        adapter_id: str,
        *,
        data_access: DataAccessRequest | None = None,
        outbound_destination: str | None = None,
    ) -> AuthorizationDecision:
        """Compute the authorization intersection without retaining prior decisions."""
        declared_tools = (
            context.step_declared_tools
            if context.declared_tool_ids is None
            else context.declared_tool_ids
        )
        checks = (
            (AuthorizationConstraint.AGENT_ALLOWED_TOOLS, context.agent_allowed_tools),
            (AuthorizationConstraint.STEP_DECLARED_TOOLS, declared_tools),
            (AuthorizationConstraint.ROLE_PERMISSIONS, context.role_allowed_tools),
            (AuthorizationConstraint.ORGANIZATION_SCOPE, context.organization_allowed_tools),
            (AuthorizationConstraint.RISK_POLICY, context.risk_allowed_tools),
        )
        denied: list[StrEnum] = [
            constraint for constraint, allowed_tools in checks if adapter_id not in allowed_tools
        ]
        if context.approval_state not in {ApprovalState.NOT_REQUIRED, ApprovalState.APPROVED}:
            denied.append(AuthorizationConstraint.APPROVAL_STATE)
        if data_access is not None:
            denied.extend(self.authorize_data_access(context, data_access).denied_constraints)
        if outbound_destination is not None:
            denied.extend(self.authorize_outbound(context, outbound_destination).denied_constraints)
        return AuthorizationDecision(adapter_id, tuple(dict.fromkeys(denied)))

    def authorize_data_access(
        self, context: AuthorizationContext, request: DataAccessRequest
    ) -> AuthorizationDecision:
        """Authorize every organization, domain, pack, agent, and memory boundary."""
        denied: list[StrEnum] = []
        if not request.organization_id or request.organization_id != context.organization_id:
            denied.append(ScopeConstraint.ORGANIZATION_SCOPE)
        if (
            not request.domain_id
            or context.domain_id is None
            or request.domain_id != context.domain_id
        ):
            denied.append(ScopeConstraint.DOMAIN_SCOPE)
        if not self._pack_version_allowed(context, request.pack_version):
            denied.append(ScopeConstraint.PACK_VERSION_RANGE)
        if not request.agent_id or request.agent_id != context.agent_id:
            denied.append(ScopeConstraint.AGENT_IDENTITY)
        if (
            not request.memory_scope
            or not context.declared_memory_scopes
            or request.memory_scope not in context.declared_memory_scopes
        ):
            denied.append(ScopeConstraint.MEMORY_SCOPE)
        return AuthorizationDecision(request.memory_scope, tuple(denied))

    def authorize_outbound(
        self, context: AuthorizationContext, destination: str
    ) -> AuthorizationDecision:
        """Authorize an exact declared outbound destination before dispatch."""
        denied: list[StrEnum] = []
        if (
            not is_safe_outbound_destination(destination)
            or destination not in context.declared_outbound_destinations
        ):
            denied.append(ScopeConstraint.OUTBOUND_DESTINATION)
        return AuthorizationDecision(destination, tuple(denied))

    # Explicit aliases make the scope-specific API easy to discover for callers.
    authorize_data = authorize_data_access
    authorize_outbound_destination = authorize_outbound

    @staticmethod
    def _pack_version_allowed(context: AuthorizationContext, requested: str) -> bool:
        if not requested:
            return False
        if context.pack_version is not None and requested != context.pack_version:
            return False
        if context.supported_pack_range is not None:
            try:
                return context.supported_pack_range.contains(requested)
            except ValueError:
                return False
        # A pinned pack version is itself an approved singleton range. Without either
        # declaration there is no supported pack evidence, so the request is denied.
        return context.pack_version is not None


def normalize_tool_input(arguments: Mapping[str, object]) -> Mapping[str, ToolInputValue]:
    """Validate and freeze a JSON-like local-adapter payload.

    Inputs cannot carry executable objects, shell directives, credential-bearing fields,
    or URLs. Registered adapters receive only this normalized, data-only structure.
    """
    return MappingProxyType(
        {key: _normalize_value(value, key) for key, value in _validated_items(arguments, "input")}
    )


def _validated_items(
    values: Mapping[str, object],
    location: str,
) -> tuple[tuple[str, object], ...]:
    items: list[tuple[str, object]] = []
    for key, value in values.items():
        if not isinstance(key, str) or not key:
            raise ToolInputValidationError(f"{location} contains an invalid key")
        normalized_key = key.casefold().replace("-", "_")
        if any(part in normalized_key for part in _PROHIBITED_INPUT_KEY_PARTS):
            raise ToolInputValidationError(f"{location}.{key} is not allowed")
        items.append((key, value))
    return tuple(items)


def _normalize_value(value: object, location: str) -> ToolInputValue:
    if value is None or isinstance(value, bool | int):
        return value
    if isinstance(value, float):
        if not isfinite(value):
            raise ToolInputValidationError(f"{location} must be finite")
        return value
    if isinstance(value, str):
        parsed = urlsplit(value)
        if parsed.scheme or value.startswith("//"):
            raise ToolInputValidationError(f"{location} must not contain a URL")
        return value
    if isinstance(value, Mapping):
        return MappingProxyType(
            {
                key: _normalize_value(child, f"{location}.{key}")
                for key, child in _validated_items(value, location)
            }
        )
    if isinstance(value, list | tuple):
        return tuple(
            _normalize_value(child, f"{location}[{index}]") for index, child in enumerate(value)
        )
    raise ToolInputValidationError(f"{location} must contain only data values")


def canonical_tool_input(arguments: Mapping[str, ToolInputValue]) -> str:
    """Return a deterministic digest input without retaining a raw payload."""
    return _canonical_value(arguments)


def _canonical_value(value: ToolInputValue) -> str:
    if isinstance(value, Mapping):
        parts = [f"{key}:{_canonical_value(child)}" for key, child in sorted(value.items())]
        return "{" + ",".join(parts) + "}"
    if isinstance(value, tuple):
        return "[" + ",".join(_canonical_value(child) for child in value) + "]"
    return repr(value)
