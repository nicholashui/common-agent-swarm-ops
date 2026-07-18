"""Immutable, provenance-bearing records for approved scoped memory."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from app.models.common import RecordMetadata
from app.models.evidence import EvidenceReference
from app.models.identifiers import ActorId


class MemoryImpact(StrEnum):
    """The safety tier that determines scoped-memory write controls."""

    LOW = "low"
    HIGH = "high"


class MemoryScopeType(StrEnum):
    """The allowed ownership boundary for a scoped-memory record."""

    WORKFLOW = "workflow"
    ORGANIZATION = "organization"
    AGENT = "agent"


class MemoryWritePath(StrEnum):
    """Execution paths that must all honor the high-impact audit latch."""

    NORMAL = "normal"
    CRITICAL = "critical"
    RECOVERY = "recovery"


@dataclass(frozen=True, slots=True)
class MemoryScope:
    """An approved workflow, organization, or agent scope."""

    scope_type: MemoryScopeType
    scope_id: str

    def __post_init__(self) -> None:
        if not self.scope_id.strip():
            raise ValueError("Memory scopes require a non-empty scope identifier.")


@dataclass(frozen=True, slots=True)
class MemoryWrite:
    """A caller-provided memory write; content remains outside the durable record."""

    scope: MemoryScope
    impact: MemoryImpact
    writer: ActorId
    content_reference: str
    provenance: tuple[EvidenceReference, ...] = ()
    source_log_set_id: str | None = None


@dataclass(frozen=True, slots=True)
class ScopedMemory:
    """A durable record whose content reference is bound to one memory scope."""

    metadata: RecordMetadata
    scope: MemoryScope
    impact: MemoryImpact
    writer: ActorId
    content_reference: str
    provenance: tuple[EvidenceReference, ...]
    source_log_set_id: str | None


@dataclass(frozen=True, slots=True)
class AuditUnavailableLatch:
    """The persistent high-impact write block state for an audit outage."""

    active: bool
    tripped_at: datetime | None
