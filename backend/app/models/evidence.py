"""Immutable evidence records retained for operational decisions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.models.common import RecordMetadata
from app.models.identifiers import EvidenceId


@dataclass(frozen=True, slots=True)
class EvidenceReference:
    """A stable reference to evidence held by a trusted repository."""

    evidence_id: EvidenceId
    digest: str
    kind: str


@dataclass(frozen=True, slots=True)
class EvidenceItem:
    """Append-only test, evaluation, or operational evidence."""

    metadata: RecordMetadata
    evidence_id: EvidenceId
    category: str
    outcome: str
    content_digest: str
    recorded_at: datetime
    supporting_references: tuple[EvidenceReference, ...] = ()
    command: str | None = None


@dataclass(frozen=True, slots=True)
class EvidenceProjection:
    """Safe evidence fields suitable for an operator response."""

    evidence_id: EvidenceId
    category: str
    outcome: str
    recorded_at: datetime
    supporting_references: tuple[EvidenceReference, ...]
