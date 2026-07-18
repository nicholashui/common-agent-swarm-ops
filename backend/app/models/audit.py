"""Immutable audit records and their safe operator projections."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from app.models.common import RecordMetadata
from app.models.evidence import EvidenceReference
from app.models.identifiers import ActorId, AuditEventId


class AuditDecision(StrEnum):
    """The durable decision associated with a governed event."""

    ALLOWED = "allowed"
    DENIED = "denied"
    RECORDED = "recorded"


@dataclass(frozen=True, slots=True)
class AuditEvent:
    """An append-only audit record; mutations require a new event."""

    metadata: RecordMetadata
    audit_event_id: AuditEventId
    actor_id: ActorId
    operation: str
    decision: AuditDecision
    reason: str
    recorded_at: datetime
    evidence_references: tuple[EvidenceReference, ...] = ()
    alternate_sink_used: bool = False

    def to_projection(self) -> AuditEventProjection:
        """Return the reason-free representation safe for operators."""
        return AuditEventProjection(
            audit_event_id=self.audit_event_id,
            correlation_id=self.metadata.correlation_id,
            operation=self.operation,
            decision=self.decision,
            recorded_at=self.recorded_at,
            evidence_references=self.evidence_references,
        )


@dataclass(frozen=True, slots=True)
class AuditEventProjection:
    """A reason-free audit representation for external responses."""

    audit_event_id: AuditEventId
    correlation_id: str
    operation: str
    decision: AuditDecision
    recorded_at: datetime
    evidence_references: tuple[EvidenceReference, ...]
