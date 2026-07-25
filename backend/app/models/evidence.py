"""Immutable evidence records retained for operational decisions."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from types import MappingProxyType

from app.models.common import CompatibilityRange, RecordMetadata, validate_semantic_version
from app.models.control_plane import (
    AgentNodeAttemptId,
    LearningEpisodeId,
    LessonId,
    RetrievalRecordId,
    _adoption_references,
    _validate_adoption_metadata,
)
from app.models.identifiers import (
    AgentId,
    DomainId,
    EvidenceId,
    OrganizationId,
)


@dataclass(frozen=True, slots=True)
class EvidenceReference:
    """A stable reference to evidence held by a trusted repository."""

    evidence_id: EvidenceId
    digest: str
    kind: str

    def __post_init__(self) -> None:
        _evidence_required(str(self.evidence_id), "evidence_id")
        _evidence_required(self.digest, "digest")
        _evidence_required(self.kind, "kind")


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

    def __post_init__(self) -> None:
        _validate_adoption_metadata(self.metadata)
        for value, name in (
            (str(self.evidence_id), "evidence_id"),
            (self.category, "category"),
            (self.outcome, "outcome"),
            (self.content_digest, "content_digest"),
        ):
            _evidence_required(value, name)
        if self.recorded_at.tzinfo is None:
            raise ValueError("recorded_at must be timezone-aware.")
        references = tuple(self.supporting_references)
        if len({str(reference.evidence_id) for reference in references}) != len(references):
            raise ValueError("Supporting evidence references must be unique.")
        object.__setattr__(self, "supporting_references", references)
        if self.command is not None:
            _evidence_required(self.command, "command")


@dataclass(frozen=True, slots=True)
class EvidenceProjection:
    """Safe evidence fields suitable for an operator response."""

    evidence_id: EvidenceId
    category: str
    outcome: str
    recorded_at: datetime
    supporting_references: tuple[EvidenceReference, ...]


class LearningTerminalOutcome(StrEnum):
    """The only terminal outcomes permitted for one Agent_Node_Attempt."""

    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    RETRIED = "retried"
    ESCALATED = "escalated"


class LessonAssessmentOutcome(StrEnum):
    """Assessment result controlling whether a Lesson can be retrieved."""

    PASSED = "passed"
    FAILED = "failed"


def _freeze_evidence_value(value: object) -> object:
    if isinstance(value, Mapping):
        return MappingProxyType(
            {str(key): _freeze_evidence_value(item) for key, item in value.items()}
        )
    if isinstance(value, (list, tuple)):
        return tuple(_freeze_evidence_value(item) for item in value)
    if isinstance(value, (set, frozenset)):
        return frozenset(_freeze_evidence_value(item) for item in value)
    return value


def _freeze_evidence_mapping(value: Mapping[str, object]) -> Mapping[str, object]:
    """Store filters and aggregate projections without retaining mutable containers."""
    return MappingProxyType({str(key): _freeze_evidence_value(item) for key, item in value.items()})


def _evidence_required(value: str, name: str) -> None:
    if not value.strip():
        raise ValueError(f"{name} must be non-empty.")


@dataclass(frozen=True, slots=True)
class RetrievalRecord:
    """Immutable pre-action retrieval evidence, including an empty result."""

    metadata: RecordMetadata
    retrieval_record_id: RetrievalRecordId
    attempt_id: AgentNodeAttemptId
    organization_id: OrganizationId
    domain_id: DomainId
    pack_version: str
    agent_id: AgentId
    memory_scope: str
    retrieved_at: datetime
    lesson_references: tuple[str, ...] = ()
    approved_filters: Mapping[str, object] | None = None

    def __post_init__(self) -> None:
        _validate_adoption_metadata(self.metadata)
        for value, name in (
            (str(self.retrieval_record_id), "retrieval_record_id"),
            (str(self.attempt_id), "attempt_id"),
            (str(self.organization_id), "organization_id"),
            (str(self.domain_id), "domain_id"),
            (self.pack_version, "pack_version"),
            (str(self.agent_id), "agent_id"),
            (self.memory_scope, "memory_scope"),
        ):
            _evidence_required(value, name)
        validate_semantic_version(self.pack_version, "pack_version")
        if self.organization_id != self.metadata.organization_id:
            raise ValueError("Retrieval organization must match record metadata.")
        object.__setattr__(
            self,
            "lesson_references",
            _adoption_references(self.lesson_references, "lesson_references"),
        )
        filters = self.approved_filters or {
            "organization_id": str(self.organization_id),
            "domain_id": str(self.domain_id),
            "pack_version": self.pack_version,
            "agent_id": str(self.agent_id),
            "memory_scope": self.memory_scope,
        }
        confirmed_filters = _freeze_evidence_mapping(filters)
        object.__setattr__(self, "approved_filters", confirmed_filters)
        if confirmed_filters.get("organization_id") != str(self.organization_id):
            raise ValueError("Retrieval filters must retain the approved organization.")
        if confirmed_filters.get("domain_id") != str(self.domain_id):
            raise ValueError("Retrieval filters must retain the approved domain.")
        if confirmed_filters.get("pack_version") != self.pack_version:
            raise ValueError("Retrieval filters must retain the approved pack version.")
        if confirmed_filters.get("agent_id") != str(self.agent_id):
            raise ValueError("Retrieval filters must retain the approved agent.")
        if confirmed_filters.get("memory_scope") != self.memory_scope:
            raise ValueError("Retrieval filters must retain the approved memory scope.")
        if self.retrieved_at.tzinfo is None:
            raise ValueError("retrieved_at must be timezone-aware.")


@dataclass(frozen=True, slots=True)
class LearningEpisode:
    """Immutable terminal outcome for exactly one node attempt."""

    metadata: RecordMetadata
    episode_id: LearningEpisodeId
    attempt_id: AgentNodeAttemptId
    organization_id: OrganizationId
    domain_id: DomainId
    pack_version: str
    agent_id: AgentId
    terminal_outcome: LearningTerminalOutcome
    outcome_reference: str
    recorded_at: datetime
    retrieval_record_id: RetrievalRecordId | None = None
    evidence_references: tuple[str, ...] = ()
    blocked_for_recovery: bool = False

    def __post_init__(self) -> None:
        _validate_adoption_metadata(self.metadata)
        for value, name in (
            (str(self.episode_id), "episode_id"),
            (str(self.attempt_id), "attempt_id"),
            (str(self.organization_id), "organization_id"),
            (str(self.domain_id), "domain_id"),
            (self.pack_version, "pack_version"),
            (str(self.agent_id), "agent_id"),
            (self.outcome_reference, "outcome_reference"),
        ):
            _evidence_required(value, name)
        validate_semantic_version(self.pack_version, "pack_version")
        if self.organization_id != self.metadata.organization_id:
            raise ValueError("Learning episode organization must match record metadata.")
        object.__setattr__(self, "terminal_outcome", LearningTerminalOutcome(self.terminal_outcome))
        object.__setattr__(
            self,
            "evidence_references",
            _adoption_references(self.evidence_references, "evidence_references"),
        )
        if self.recorded_at.tzinfo is None:
            raise ValueError("recorded_at must be timezone-aware.")

    @property
    def terminal_identity(self) -> tuple[OrganizationId, AgentNodeAttemptId]:
        """Return the uniqueness key enforced for one terminal attempt outcome."""
        return self.organization_id, self.attempt_id


@dataclass(frozen=True, slots=True)
class Lesson:
    """Versioned, assessed, scoped Lesson containing only a trusted content reference."""

    metadata: RecordMetadata
    lesson_id: LessonId
    organization_id: OrganizationId
    domain_id: DomainId
    pack_version_range: CompatibilityRange
    agent_id: AgentId
    memory_scope: str
    assessment: LessonAssessmentOutcome
    source_episode_references: tuple[str, ...]
    content_reference: str
    assessed_at: datetime
    retrievable: bool = False
    revoked: bool = False
    stale: bool = False

    def __post_init__(self) -> None:
        _validate_adoption_metadata(self.metadata)
        for value, name in (
            (str(self.lesson_id), "lesson_id"),
            (str(self.organization_id), "organization_id"),
            (str(self.domain_id), "domain_id"),
            (str(self.agent_id), "agent_id"),
            (self.memory_scope, "memory_scope"),
            (self.content_reference, "content_reference"),
        ):
            _evidence_required(value, name)
        if self.organization_id != self.metadata.organization_id:
            raise ValueError("Lesson organization must match record metadata.")
        object.__setattr__(self, "assessment", LessonAssessmentOutcome(self.assessment))
        object.__setattr__(
            self,
            "source_episode_references",
            _adoption_references(
                self.source_episode_references, "source_episode_references", required=True
            ),
        )
        if self.retrievable and (
            self.assessment is not LessonAssessmentOutcome.PASSED or self.revoked or self.stale
        ):
            raise ValueError("Only current passed Lessons can be retrievable.")
        if self.assessed_at.tzinfo is None:
            raise ValueError("assessed_at must be timezone-aware.")


@dataclass(frozen=True, slots=True)
class LearningObservability:
    """Redacted per-agent learning counts; no Lesson body is retained."""

    metadata: RecordMetadata
    agent_id: AgentId
    learning_episode_count: int
    assessed_lesson_count: int
    retrieved_lesson_reuse_count: int
    stale_lesson_count: int
    revoked_lesson_count: int
    escalation_count: int
    assessment_outcomes: Mapping[str, int]

    def __post_init__(self) -> None:
        _validate_adoption_metadata(self.metadata)
        _evidence_required(str(self.agent_id), "agent_id")
        counts = (
            self.learning_episode_count,
            self.assessed_lesson_count,
            self.retrieved_lesson_reuse_count,
            self.stale_lesson_count,
            self.revoked_lesson_count,
            self.escalation_count,
        )
        if any(count < 0 for count in counts):
            raise ValueError("Learning observability counts must not be negative.")
        if any(value < 0 for value in self.assessment_outcomes.values()):
            raise ValueError("Assessment outcome counts must not be negative.")
        object.__setattr__(
            self, "assessment_outcomes", _freeze_evidence_mapping(self.assessment_outcomes)
        )


@dataclass(frozen=True, slots=True)
class OutputProvenance:
    """Output lineage links source episodes without fabricating a retrieval record."""

    metadata: RecordMetadata
    output_reference: str
    retrieval_record_id: RetrievalRecordId | None
    source_episode_references: tuple[str, ...]

    def __post_init__(self) -> None:
        _validate_adoption_metadata(self.metadata)
        _evidence_required(self.output_reference, "output_reference")
        object.__setattr__(
            self,
            "source_episode_references",
            _adoption_references(self.source_episode_references, "source_episode_references"),
        )


Retrieval_Record = RetrievalRecord
Learning_Episode = LearningEpisode
Lesson_Assessment_Outcome = LessonAssessmentOutcome
Learning_Observability = LearningObservability
Output_Provenance = OutputProvenance
