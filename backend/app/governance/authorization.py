"""Complete, stateless authorization-intersection checks for Host tool calls."""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from math import isfinite
from types import MappingProxyType
from urllib.parse import urlsplit


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


@dataclass(frozen=True, slots=True)
class AuthorizationDecision:
    """The complete result of evaluating one tool request without caching it."""

    adapter_id: str
    denied_constraints: tuple[AuthorizationConstraint, ...]

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
    return _SAFE_TOOL_IDENTIFIER.fullmatch(value) is not None


class AuthorizationService:
    """Evaluate every authorization factor for every distinct request."""

    def evaluate(self, context: AuthorizationContext, adapter_id: str) -> AuthorizationDecision:
        """Compute the authorization intersection without retaining prior decisions."""
        checks = (
            (AuthorizationConstraint.AGENT_ALLOWED_TOOLS, context.agent_allowed_tools),
            (AuthorizationConstraint.STEP_DECLARED_TOOLS, context.step_declared_tools),
            (AuthorizationConstraint.ROLE_PERMISSIONS, context.role_allowed_tools),
            (AuthorizationConstraint.ORGANIZATION_SCOPE, context.organization_allowed_tools),
            (AuthorizationConstraint.RISK_POLICY, context.risk_allowed_tools),
        )
        denied = [
            constraint for constraint, allowed_tools in checks if adapter_id not in allowed_tools
        ]
        if context.approval_state not in {ApprovalState.NOT_REQUIRED, ApprovalState.APPROVED}:
            denied.append(AuthorizationConstraint.APPROVAL_STATE)
        return AuthorizationDecision(adapter_id, tuple(denied))


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
