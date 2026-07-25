"""Central redaction for every public and observability surface."""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from enum import StrEnum
from types import MappingProxyType
from typing import Final

REDACTED: Final[str] = "[REDACTED]"


class RedactionSurface(StrEnum):
    """Explicit destinations that may receive only sanitized values."""

    LOG = "log"
    TRACE = "trace"
    METRIC = "metric"
    AUDIT = "audit"
    OPERATIONAL_EVENT = "operational_event"
    ERROR_RESPONSE = "error_response"
    PUBLIC_RESPONSE = "public_response"
    BROWSER_CONFIGURATION = "browser_configuration"
    DIAGNOSTIC = "diagnostic"


_SENSITIVE_FIELD_PARTS: Final[frozenset[str]] = frozenset(
    {
        "api_key",
        "authorization",
        "credential",
        "deployment_secret",
        "password",
        "private_key",
        "protected_artifact",
        "raw_prompt",
        "secret",
        "session_cookie",
        "token",
        "prohibited_tool",
    }
)
_CREDENTIAL_TEXT = re.compile(
    r"(?i)(?:bearer\s+\S+|(?:api[_-]?key|password|secret|token)\s*[:=]\s*\S+)"
)

_configured_deployment_secrets: tuple[str, ...] = ()


def configure_deployment_secrets(secrets: Iterable[str]) -> None:
    """Update the centrally applied deployment-secret literals for all output surfaces."""
    global _configured_deployment_secrets
    _configured_deployment_secrets = tuple(
        dict.fromkeys(secret for secret in secrets if isinstance(secret, str) and secret)
    )


class RedactionService:
    """Recursively remove sensitive values before they cross a named surface."""

    def __init__(self, deployment_secrets: Iterable[str] | None = None) -> None:
        self._deployment_secrets = (
            None
            if deployment_secrets is None
            else tuple(
                secret for secret in deployment_secrets if isinstance(secret, str) and secret
            )
        )

    def redact(self, value: object, *, surface: RedactionSurface) -> object:
        """Return an immutable safe projection for the requested output surface."""
        if not isinstance(surface, RedactionSurface):
            raise ValueError("A recognized redaction surface is required.")
        return self._redact_value(None, value, surface)

    def redact_mapping(
        self, values: Mapping[str, object], *, surface: RedactionSurface
    ) -> Mapping[str, object]:
        """Return an immutable recursively redacted mapping."""
        redacted = {
            str(key): self._redact_value(str(key), value, surface) for key, value in values.items()
        }
        return MappingProxyType(redacted)

    def _redact_value(self, key: str | None, value: object, surface: RedactionSurface) -> object:
        if key is not None and _is_sensitive_field(key):
            return REDACTED
        if isinstance(value, Mapping):
            return self.redact_mapping(value, surface=surface)
        if isinstance(value, list | tuple | set | frozenset):
            return tuple(self._redact_value(key, item, surface) for item in value)
        if isinstance(value, str):
            return self.redact_text(value, surface=surface)
        return value

    def redact_text(self, value: str, *, surface: RedactionSurface) -> str:
        """Remove configured secret literals and recognizable credential text."""
        if not isinstance(surface, RedactionSurface):
            raise ValueError("A recognized redaction surface is required.")
        safe_value = value
        for secret in self._secret_values():
            safe_value = safe_value.replace(secret, REDACTED)
        return _CREDENTIAL_TEXT.sub(REDACTED, safe_value)

    def _secret_values(self) -> tuple[str, ...]:
        """Combine dynamic deployment secrets with explicitly injected test/service secrets."""
        explicit_secrets = self._deployment_secrets or ()
        return tuple(dict.fromkeys((*_configured_deployment_secrets, *explicit_secrets)))


_DEFAULT_REDACTOR = RedactionService()


def redact_mapping(
    values: Mapping[str, object],
    *,
    surface: RedactionSurface = RedactionSurface.PUBLIC_RESPONSE,
) -> Mapping[str, object]:
    """Compatibility entry point backed by the centralized redaction service."""
    return _DEFAULT_REDACTOR.redact_mapping(values, surface=surface)


def redact_value(
    value: object,
    *,
    surface: RedactionSurface = RedactionSurface.PUBLIC_RESPONSE,
) -> object:
    """Redact any JSON-like value through the centralized service."""
    return _DEFAULT_REDACTOR.redact(value, surface=surface)


def _is_sensitive_field(key: str) -> bool:
    normalized = re.sub(r"[^a-z0-9]+", "_", key.casefold()).strip("_")
    return any(part in normalized for part in _SENSITIVE_FIELD_PARTS)
