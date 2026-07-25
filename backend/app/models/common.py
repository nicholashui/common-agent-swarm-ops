"""Shared immutable metadata and optimistic-transition contracts."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol, runtime_checkable

from app.models.identifiers import CorrelationId, OrganizationId, RecordId

SCHEMA_VERSION = 1


def utc_now() -> datetime:
    """Return a timezone-aware timestamp for durable Host records."""
    return datetime.now(UTC)


@dataclass(frozen=True, slots=True)
class RecordMetadata:
    """Version and trace metadata carried by every durable record."""

    record_id: RecordId
    organization_id: OrganizationId
    correlation_id: CorrelationId
    schema_version: int
    version: int
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class OptimisticTransition:
    """A compare-and-swap precondition for an immutable record transition."""

    record_id: RecordId
    organization_id: OrganizationId
    expected_version: int
    correlation_id: CorrelationId


@runtime_checkable
class VersionedRecord(Protocol):
    """Structural protocol implemented by records guarded by a version check."""

    @property
    def metadata(self) -> RecordMetadata:
        """Return immutable version and trace metadata."""


_SEMANTIC_VERSION = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")


def validate_semantic_version(value: str, name: str = "version") -> str:
    """Validate and return a strict ``major.minor.patch`` version string."""
    if not isinstance(value, str) or _SEMANTIC_VERSION.fullmatch(value) is None:
        raise ValueError(f"{name} must use semantic version format major.minor.patch.")
    return value


def semantic_version_key(value: str) -> tuple[int, int, int]:
    """Return the comparable tuple for a validated semantic version."""
    validated = validate_semantic_version(value)
    match = _SEMANTIC_VERSION.fullmatch(validated)
    assert match is not None  # The validator above guarantees a match.
    return tuple(int(part) for part in match.groups())  # type: ignore[return-value]


@dataclass(frozen=True, slots=True)
class CompatibilityRange:
    """An inclusive or exclusive range of independently versioned contracts."""

    minimum: str | None = None
    maximum: str | None = None
    include_minimum: bool = True
    include_maximum: bool = True

    def __post_init__(self) -> None:
        if self.minimum is None and self.maximum is None:
            raise ValueError("A compatibility range must have at least one bound.")
        if self.minimum is not None:
            validate_semantic_version(self.minimum, "minimum")
        if self.maximum is not None:
            validate_semantic_version(self.maximum, "maximum")
        if self.minimum is not None and self.maximum is not None:
            lower = semantic_version_key(self.minimum)
            upper = semantic_version_key(self.maximum)
            if lower > upper or (
                lower == upper and not (self.include_minimum and self.include_maximum)
            ):
                raise ValueError("Compatibility range bounds are not ordered.")

    @classmethod
    def exact(cls, version: str) -> CompatibilityRange:
        """Build a range containing exactly one semantic version."""
        validated = validate_semantic_version(version)
        return cls(validated, validated)

    def contains(self, version: str) -> bool:
        """Return whether ``version`` is covered by this range."""
        candidate = semantic_version_key(version)
        if self.minimum is not None:
            lower = semantic_version_key(self.minimum)
            if candidate < lower or (candidate == lower and not self.include_minimum):
                return False
        if self.maximum is not None:
            upper = semantic_version_key(self.maximum)
            if candidate > upper or (candidate == upper and not self.include_maximum):
                return False
        return True

    def intersects(self, other: CompatibilityRange) -> bool:
        """Return whether two ranges share at least one semantic version."""
        lower_value: tuple[int, int, int] | None = None
        lower_inclusive = True
        if self.minimum is not None:
            lower_value = semantic_version_key(self.minimum)
            lower_inclusive = self.include_minimum
        if other.minimum is not None:
            candidate = semantic_version_key(other.minimum)
            if lower_value is None or candidate > lower_value:
                lower_value = candidate
                lower_inclusive = other.include_minimum
            elif candidate == lower_value:
                lower_inclusive = lower_inclusive and other.include_minimum

        upper_value: tuple[int, int, int] | None = None
        upper_inclusive = True
        if self.maximum is not None:
            upper_value = semantic_version_key(self.maximum)
            upper_inclusive = self.include_maximum
        if other.maximum is not None:
            candidate = semantic_version_key(other.maximum)
            if upper_value is None or candidate < upper_value:
                upper_value = candidate
                upper_inclusive = other.include_maximum
            elif candidate == upper_value:
                upper_inclusive = upper_inclusive and other.include_maximum

        if lower_value is None:
            if upper_value is None:
                return True
            return upper_inclusive or upper_value > (0, 0, 0)

        candidate = (
            lower_value
            if lower_inclusive
            else (
                lower_value[0],
                lower_value[1],
                lower_value[2] + 1,
            )
        )
        if upper_value is None:
            return True
        return candidate < upper_value or (candidate == upper_value and upper_inclusive)

    @property
    def min_version(self) -> str | None:
        """Compatibility alias for callers using ``min_version`` terminology."""
        return self.minimum

    @property
    def max_version(self) -> str | None:
        """Compatibility alias for callers using ``max_version`` terminology."""
        return self.maximum


VersionRange = CompatibilityRange
