"""Redaction helpers for control-plane projections."""

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType
from typing import Final

REDACTED: Final[str] = "[REDACTED]"
SENSITIVE_FIELD_PARTS: Final[frozenset[str]] = frozenset(
    {"api_key", "authorization", "credential", "password", "secret", "token"}
)


def redact_mapping(values: Mapping[str, object]) -> Mapping[str, object]:
    """Return an immutable, recursively redacted projection of untrusted values."""
    return MappingProxyType({key: _redact_value(key, value) for key, value in values.items()})


def _redact_value(key: str, value: object) -> object:
    if _is_sensitive(key):
        return REDACTED
    if isinstance(value, Mapping):
        return redact_mapping({str(child_key): child for child_key, child in value.items()})
    if isinstance(value, list | tuple | set | frozenset):
        return tuple(_redact_value(key, item) for item in value)
    return value


def _is_sensitive(key: str) -> bool:
    normalized = key.casefold().replace("-", "_")
    return any(part in normalized for part in SENSITIVE_FIELD_PARTS)
