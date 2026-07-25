"""Canonical, deterministic serialization helpers for migration records."""

from __future__ import annotations

import hashlib
import json
import math
import re
import unicodedata
from collections.abc import Mapping, Sequence
from dataclasses import fields, is_dataclass
from datetime import UTC, date, datetime
from enum import Enum
from pathlib import Path

_MAX_DIAGNOSTIC_LENGTH = 256
_SENSITIVE_ASSIGNMENT = re.compile(
    r"(?i)(api[_-]?key|secret|token|password|credential|authorization)\s*[:=]\s*[^\s,;]+"
)
_LONG_SECRET_LIKE_VALUE = re.compile(r"(?i)\b(?:bearer\s+)?[a-z0-9_\-]{32,}\b")


def canonicalize_json(value: object) -> str:
    """Serialize JSON-compatible data with stable keys and UTF-8 semantics.

    Object keys are ordered, while array order is retained because arrays in the
    migration contract are ordered records (for example, approved file lists).
    """
    return json.dumps(
        to_canonical_data(value),
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def canonical_json_bytes(value: object) -> bytes:
    """Return the canonical JSON representation as UTF-8 bytes."""
    return canonicalize_json(value).encode("utf-8")


def canonical_json(value: object) -> str:
    """Compatibility alias for :func:`canonicalize_json`."""
    return canonicalize_json(value)


def to_canonical_data(value: object) -> object:
    """Convert typed records and JSON values into deterministic JSON data."""
    if is_dataclass(value) and not isinstance(value, type):
        return {
            field.name: to_canonical_data(getattr(value, field.name))
            for field in sorted(fields(value), key=lambda item: item.name)
        }
    if isinstance(value, Enum):
        return to_canonical_data(value.value)
    if isinstance(value, datetime):
        if value.tzinfo is None:
            raise ValueError("Canonical timestamps must be timezone-aware.")
        return value.astimezone(UTC).isoformat().replace("+00:00", "Z")
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, Mapping):
        normalized: dict[str, object] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError("Canonical JSON object keys must be strings.")
            normalized[key] = to_canonical_data(item)
        return normalized
    if isinstance(value, (tuple, list)):
        return [to_canonical_data(item) for item in value]
    if isinstance(value, (set, frozenset)):
        items = [to_canonical_data(item) for item in value]
        return sorted(items, key=canonicalize_json)
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("Canonical JSON cannot contain non-finite numbers.")
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise TypeError(f"Unsupported canonical JSON value: {type(value).__name__}.")


def digest_json(value: object) -> str:
    """Return the lowercase SHA-256 digest of canonical JSON data."""
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def sha256_digest(value: bytes | bytearray | memoryview | str | object) -> str:
    """Digest raw bytes or canonicalize structured input before hashing it."""
    if isinstance(value, (bytes, bytearray, memoryview)):
        payload = bytes(value)
    elif isinstance(value, str):
        payload = value.encode("utf-8")
    else:
        payload = canonical_json_bytes(value)
    return hashlib.sha256(payload).hexdigest()


def canonical_digest(value: bytes | bytearray | memoryview | str | object) -> str:
    """Compatibility alias for :func:`sha256_digest`."""
    return sha256_digest(value)


def redact_diagnostic(value: object) -> str:
    """Keep diagnostics bounded and prevent common secret forms from being copied."""
    text = unicodedata.normalize("NFKC", str(value)).replace("\x00", " ")
    text = text.splitlines()[0] if text.splitlines() else ""
    text = _SENSITIVE_ASSIGNMENT.sub(lambda match: f"{match.group(1)}=<redacted>", text)
    text = _LONG_SECRET_LIKE_VALUE.sub("<redacted>", text)
    if len(text) > _MAX_DIAGNOSTIC_LENGTH:
        text = f"{text[: _MAX_DIAGNOSTIC_LENGTH - 3]}..."
    return text.strip()


def finding_sort_key(finding: object) -> tuple[str, str, str, str]:
    """Return a stable, redaction-safe ordering key for diagnostic findings."""
    return (
        redact_diagnostic(getattr(finding, "code", "")),
        redact_diagnostic(getattr(finding, "path", "")),
        redact_diagnostic(getattr(finding, "field", "")),
        redact_diagnostic(getattr(finding, "message", "")),
    )


def sort_findings[T](findings: Sequence[T]) -> tuple[T, ...]:
    """Sort findings by stable code, path, field, and safe message fields."""
    return tuple(sorted(findings, key=finding_sort_key))


def record_digest(record: object) -> str:
    """Return a reproducible digest for a typed migration record."""
    return digest_json(record)
