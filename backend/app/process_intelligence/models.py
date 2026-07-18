"""Immutable process-intelligence event-log and artifact records."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from app.models.common import RecordMetadata


class ProcessArtifactKind(StrEnum):
    """The permitted process-intelligence artifact categories."""

    DISCOVERED_PROCESS = "discovered_process"
    CONFORMANCE = "conformance"
    BOTTLENECK = "bottleneck"
    CAUSAL_HYPOTHESIS = "causal_hypothesis"


@dataclass(frozen=True, slots=True)
class EventLogRecord:
    """One validated event record eligible to support a derived artifact."""

    record_id: str
    case_id: str
    activity: str
    occurred_at: datetime


@dataclass(frozen=True, slots=True)
class EventLogSet:
    """A permitted log set with uniquely identifiable supporting records."""

    log_set_id: str
    records: tuple[EventLogRecord, ...]


@dataclass(frozen=True, slots=True)
class ProcessArtifactDraft:
    """A requested artifact derivation before durable traceability metadata is added."""

    kind: ProcessArtifactKind
    supporting_record_refs: tuple[str, ...]
    output: Mapping[str, object]


@dataclass(frozen=True, slots=True)
class ProcessArtifact:
    """A durable, source-traceable process-intelligence result."""

    metadata: RecordMetadata
    kind: ProcessArtifactKind
    source_log_set_id: str
    supporting_record_refs: tuple[str, ...]
    output: Mapping[str, object]
