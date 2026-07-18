"""Shared immutable metadata and optimistic-transition contracts."""

from __future__ import annotations

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
