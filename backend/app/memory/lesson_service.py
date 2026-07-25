"""Governed Lesson assessment, retrieval provenance, revocation, and observability."""

from __future__ import annotations

import math
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, replace
from datetime import datetime
from typing import cast

from app.models.common import (
    SCHEMA_VERSION,
    RecordMetadata,
    utc_now,
    validate_semantic_version,
)
from app.models.contracts import ErrorCode, ErrorDetail, RepositoryError, Result
from app.models.control_plane import (
    AuditRecord,
    LessonId,
    RetrievalRecordId,
)
from app.models.evidence import (
    LearningEpisode,
    LearningObservability,
    LearningTerminalOutcome,
    Lesson,
    LessonAssessmentOutcome,
    OutputProvenance,
    RetrievalRecord,
)
from app.models.identifiers import (
    ActorId,
    AgentId,
    CorrelationId,
    DomainId,
    OrganizationId,
    RecordId,
    new_record_id,
)
from app.repositories.protocols import (
    AuditRecordRepository,
    LearningEpisodeRepository,
    LessonRepository,
    RetrievalRecordRepository,
)


@dataclass(frozen=True, slots=True)
class LessonAssessment:
    """The complete, reference-only assessment vector for a candidate Lesson."""

    format_valid: bool = False
    source_episode_references_valid: bool = False
    safety_policy_passed: bool = False
    domain_policy_passed: bool = False
    evaluation_score: float | None = None
    evaluation_threshold: float | None = None
    evidence_references: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.evaluation_score is not None and not _score_is_valid(self.evaluation_score):
            raise ValueError("evaluation_score must be a finite value between zero and one.")
        if self.evaluation_threshold is not None and not _score_is_valid(self.evaluation_threshold):
            raise ValueError("evaluation_threshold must be a finite value between zero and one.")
        references = tuple(str(reference) for reference in self.evidence_references)
        if any(not reference.strip() for reference in references):
            raise ValueError("Assessment evidence references must be non-empty.")
        if len(references) != len(set(references)):
            raise ValueError("Assessment evidence references must be unique.")
        object.__setattr__(self, "evidence_references", references)

    @property
    def threshold_passed(self) -> bool:
        """Return whether a configured score meets its configured threshold."""
        return (
            self.evaluation_score is not None
            and self.evaluation_threshold is not None
            and self.evaluation_score >= self.evaluation_threshold
        )

    @property
    def passed(self) -> bool:
        """Return whether every required Lesson assessment criterion passed."""
        return (
            self.format_valid
            and self.source_episode_references_valid
            and self.safety_policy_passed
            and self.domain_policy_passed
            and self.threshold_passed
        )

    @classmethod
    def from_mapping(cls, values: Mapping[str, object]) -> LessonAssessment:
        """Normalize integration-boundary assessment data without retaining raw content."""
        return cls(
            format_valid=_mapping_bool(values, "format_valid", "format_passed", "format"),
            source_episode_references_valid=_mapping_bool(
                values,
                "source_episode_references_valid",
                "source_references_valid",
                "source_episodes_valid",
            ),
            safety_policy_passed=_mapping_bool(
                values, "safety_policy_passed", "safety_policy", "safety"
            ),
            domain_policy_passed=_mapping_bool(
                values, "domain_policy_passed", "domain_policy", "domain"
            ),
            evaluation_score=_mapping_float(values, "evaluation_score", "score"),
            evaluation_threshold=_mapping_float(values, "evaluation_threshold", "threshold"),
            evidence_references=_mapping_references(values.get("evidence_references", ())),
        )


LessonAssessmentCriteria = LessonAssessment


@dataclass(frozen=True, slots=True)
class LessonRetrievalRequest:
    """The exact approved scope used for one Lesson retrieval request."""

    organization_id: OrganizationId
    domain_id: DomainId
    pack_version: str
    agent_id: AgentId
    memory_scope: str

    def __post_init__(self) -> None:
        for value, name in (
            (str(self.organization_id), "organization_id"),
            (str(self.domain_id), "domain_id"),
            (str(self.agent_id), "agent_id"),
            (self.memory_scope, "memory_scope"),
        ):
            if not value.strip():
                raise ValueError(f"{name} must be non-empty.")
        validate_semantic_version(self.pack_version, "pack_version")


@dataclass(frozen=True, slots=True)
class _ResolvedRetrieval:
    """Non-null Result wrapper for an optional Retrieval_Record."""

    record: RetrievalRecord | None


class LessonService:
    """Enforce evidence-complete Lesson governance at every memory boundary."""

    def __init__(
        self,
        lesson_repository: LessonRepository,
        retrieval_repository: RetrievalRecordRepository,
        episode_repository: LearningEpisodeRepository | None,
        audit_repository: AuditRecordRepository,
        *,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._lesson_repository = lesson_repository
        self._retrieval_repository = retrieval_repository
        self._episode_repository = episode_repository
        self._audit_repository = audit_repository
        self._clock = clock

    def assess_lesson(
        self,
        candidate: Lesson,
        assessment: LessonAssessment | Mapping[str, object] | None = None,
        *,
        format_valid: bool | None = None,
        source_episode_references_valid: bool | None = None,
        safety_policy_passed: bool | None = None,
        domain_policy_passed: bool | None = None,
        evaluation_score: float | None = None,
        evaluation_threshold: float | None = None,
        correlation_id: CorrelationId | None = None,
    ) -> Result[Lesson, ErrorDetail]:
        """Assess and append a candidate, making failed candidates non-retrievable."""
        effective_correlation = correlation_id or candidate.metadata.correlation_id
        try:
            criteria = _coerce_assessment(
                assessment,
                format_valid=format_valid,
                source_episode_references_valid=source_episode_references_valid,
                safety_policy_passed=safety_policy_passed,
                domain_policy_passed=domain_policy_passed,
                evaluation_score=evaluation_score,
                evaluation_threshold=evaluation_threshold,
            )
        except ValueError as error:
            return Result.failure(
                _validation_error(effective_correlation, "assessment", str(error))
            )

        source_check = self._source_references_are_available(candidate, effective_correlation)
        if not source_check.is_success:
            return Result.failure(source_check.error or _repository_error(effective_correlation))
        source_references_available = source_check.value is True
        passed = criteria.passed and source_references_available
        failures = _assessment_failures(criteria, source_references_available)
        assessed = replace(
            candidate,
            assessment=LessonAssessmentOutcome.PASSED if passed else LessonAssessmentOutcome.FAILED,
            assessed_at=self._clock(),
            retrievable=passed and not candidate.revoked and not candidate.stale,
        )

        persisted = self._append_lesson(assessed, effective_correlation)
        if not persisted.is_success or persisted.value is None:
            return persisted
        # ``failures`` is deliberately computed even though Lesson stores only the
        # aggregate outcome; the categories remain available to diagnostics without
        # retaining candidate Lesson content.
        _ = failures
        return Result.success(persisted.value)

    def retrieve_lessons(
        self,
        request: LessonRetrievalRequest | OrganizationId,
        domain_id: DomainId | str | None = None,
        pack_version: str | None = None,
        agent_id: AgentId | str | None = None,
        memory_scope: str | None = None,
        *,
        correlation_id: CorrelationId | None = None,
    ) -> Result[tuple[Lesson, ...], ErrorDetail]:
        """Return only passed Lessons inside every requested and approved scope."""
        try:
            resolved = _coerce_retrieval_request(
                request, domain_id, pack_version, agent_id, memory_scope
            )
        except ValueError as error:
            return Result.failure(
                _validation_error(
                    correlation_id or CorrelationId("lesson-retrieval"), "scope", str(error)
                )
            )
        effective_correlation = correlation_id or CorrelationId(
            f"lesson-retrieval:{resolved.organization_id}"
        )
        available = self._lesson_repository.retrievable_for(
            resolved.organization_id,
            str(resolved.domain_id),
            resolved.pack_version,
            resolved.agent_id,
            resolved.memory_scope,
        )
        if not available.is_success or available.value is None:
            return Result.failure(
                _repository_error(
                    effective_correlation, available.error, "Lesson retrieval is unavailable."
                )
            )
        revoked = self._revoked_lesson_ids(resolved.organization_id, effective_correlation)
        if not revoked.is_success or revoked.value is None:
            return Result.failure(revoked.error or _repository_error(effective_correlation))
        return Result.success(
            tuple(
                lesson
                for lesson in available.value
                if _lesson_matches_request(lesson, resolved)
                and str(lesson.lesson_id) not in revoked.value
            )
        )

    def revoke_lesson(
        self,
        lesson: Lesson | LessonId | str,
        reason: str,
        actor_id: ActorId,
        source_references: Iterable[str] = (),
        *,
        organization_id: OrganizationId | None = None,
        correlation_id: CorrelationId | None = None,
    ) -> Result[Lesson, ErrorDetail]:
        """Commit a revocation audit before changing Lesson retrieval eligibility."""
        resolved_organization = (
            lesson.organization_id if isinstance(lesson, Lesson) else organization_id
        )
        effective_correlation = correlation_id or (
            lesson.metadata.correlation_id
            if isinstance(lesson, Lesson)
            else CorrelationId("lesson-revocation")
        )
        if resolved_organization is None:
            return Result.failure(
                _validation_error(
                    effective_correlation,
                    "organization_id",
                    "Lesson revocation requires an organization scope.",
                )
            )
        if not reason.strip() or not str(actor_id).strip():
            return Result.failure(
                _validation_error(
                    effective_correlation,
                    "revocation",
                    "Lesson revocation requires a reason and actor.",
                )
            )
        resolved_lesson = self._resolve_lesson(lesson, resolved_organization, effective_correlation)
        if not resolved_lesson.is_success or resolved_lesson.value is None:
            return Result.failure(resolved_lesson.error or _repository_error(effective_correlation))
        source_refs = _references(source_references, "source_references")
        timestamp = self._clock()
        audit = AuditRecord(
            metadata=self._metadata(resolved_organization, effective_correlation, timestamp),
            audit_id=str(new_record_id()),
            action="lesson.revocation",
            subject_reference=str(resolved_lesson.value.lesson_id),
            outcome="revocation_committed",
            recorded_at=timestamp,
            actor_id=actor_id,
            reason=reason,
            source_references=source_refs,
        )
        try:
            audited = self._audit_repository.append(audit)
        except Exception:
            audited = Result.failure(
                RepositoryError(
                    ErrorCode.AUDIT_UNAVAILABLE,
                    "Lesson revocation audit persistence is unavailable.",
                    effective_correlation,
                    retryable=True,
                )
            )
        if not audited.is_success:
            return Result.failure(
                _repository_error(
                    effective_correlation,
                    audited.error,
                    "Lesson revocation remains retrievable until its audit commits.",
                )
            )

        try:
            revoked = self._lesson_repository.revoke(
                resolved_organization, str(resolved_lesson.value.lesson_id)
            )
        except Exception:
            revoked = Result.failure(
                RepositoryError(
                    ErrorCode.REPOSITORY_UNAVAILABLE,
                    "Lesson revocation persistence is unavailable after audit commitment.",
                    effective_correlation,
                    retryable=True,
                )
            )
        if revoked.is_success and revoked.value is not None:
            return Result.success(revoked.value)
        # The committed audit is itself the durable retrieval barrier.  Returning
        # the original immutable Lesson keeps callers from treating a failed update
        # as a new retrievable version; retrieval also checks the audit stream.
        return Result.failure(
            _repository_error(
                effective_correlation,
                revoked.error,
                "Lesson revocation was audited but requires repository recovery.",
            )
        )

    def link_output(
        self,
        output_reference: str,
        retrieval: RetrievalRecord | RetrievalRecordId | str | None = None,
        source_episode_references: Iterable[str | LearningEpisode] = (),
        *,
        organization_id: OrganizationId | None = None,
        correlation_id: CorrelationId | None = None,
    ) -> Result[OutputProvenance, ErrorDetail]:
        """Build output lineage without creating a Retrieval_Record that did not exist."""
        if not output_reference.strip():
            return Result.failure(
                _validation_error(
                    correlation_id or CorrelationId("lesson-output"),
                    "output_reference",
                    "Output references must be non-empty.",
                )
            )
        output_correlation = correlation_id or CorrelationId("lesson-output")
        resolved_retrieval = self._resolve_retrieval(retrieval, organization_id, output_correlation)
        if not resolved_retrieval.is_success or resolved_retrieval.value is None:
            return Result.failure(resolved_retrieval.error or _repository_error(output_correlation))
        retrieval_record = resolved_retrieval.value.record
        resolved_organization = (
            retrieval_record.organization_id if retrieval_record is not None else organization_id
        )
        if resolved_organization is None:
            return Result.failure(
                _validation_error(
                    correlation_id or CorrelationId("lesson-output"),
                    "organization_id",
                    "Output provenance requires an organization scope.",
                )
            )
        effective_correlation = correlation_id or CorrelationId(
            f"lesson-output:{resolved_organization}"
        )
        source_refs = list(_episode_reference(value) for value in source_episode_references)
        if retrieval_record is not None:
            lessons = self._lessons_for_organization(resolved_organization, effective_correlation)
            if not lessons.is_success or lessons.value is None:
                return Result.failure(lessons.error or _repository_error(effective_correlation))
            by_id = {str(lesson.lesson_id): lesson for lesson in lessons.value}
            missing = [
                reference
                for reference in retrieval_record.lesson_references
                if reference not in by_id
            ]
            if missing:
                return Result.failure(
                    _validation_error(
                        effective_correlation,
                        "lesson_references",
                        "Output provenance cannot resolve every retrieved Lesson reference.",
                    )
                )
            for lesson in lessons.value:
                if str(lesson.lesson_id) in retrieval_record.lesson_references:
                    source_refs.extend(lesson.source_episode_references)
        normalized_sources = _unique_references(source_refs)
        if not normalized_sources:
            return Result.failure(
                _validation_error(
                    effective_correlation,
                    "source_episode_references",
                    "Output provenance requires at least one source Learning_Episode.",
                )
            )
        episode_check = self._validate_episode_references(
            resolved_organization, normalized_sources, effective_correlation
        )
        if not episode_check.is_success:
            return Result.failure(episode_check.error or _repository_error(effective_correlation))
        timestamp = self._clock()
        provenance = OutputProvenance(
            metadata=self._metadata(resolved_organization, effective_correlation, timestamp),
            output_reference=output_reference,
            retrieval_record_id=(
                retrieval_record.retrieval_record_id if retrieval_record is not None else None
            ),
            source_episode_references=normalized_sources,
        )
        return Result.success(provenance)

    def observability(
        self,
        organization_id: OrganizationId,
        agent_id: AgentId,
        *,
        correlation_id: CorrelationId | None = None,
    ) -> Result[LearningObservability, ErrorDetail]:
        """Expose exact per-agent counts while returning no Lesson content."""
        effective_correlation = correlation_id or CorrelationId(
            f"lesson-observability:{organization_id}:{agent_id}"
        )
        episodes = self._episodes_for_organization(organization_id, effective_correlation)
        lessons = self._lessons_for_organization(organization_id, effective_correlation)
        retrievals = self._retrievals_for_organization(organization_id, effective_correlation)
        if (
            not episodes.is_success
            or episodes.value is None
            or not lessons.is_success
            or lessons.value is None
            or not retrievals.is_success
            or retrievals.value is None
        ):
            response_error = episodes.error or lessons.error or retrievals.error
            return Result.failure(response_error or _repository_error(effective_correlation))
        episode_records = episodes.value
        lesson_records = lessons.value
        retrieval_records = retrievals.value
        agent_episodes = tuple(
            episode for episode in episode_records if episode.agent_id == agent_id
        )
        agent_lessons = tuple(lesson for lesson in lesson_records if lesson.agent_id == agent_id)
        agent_retrievals = tuple(
            retrieval for retrieval in retrieval_records if retrieval.agent_id == agent_id
        )
        outcomes: dict[str, int] = {}
        for lesson in agent_lessons:
            key = str(lesson.assessment)
            outcomes[key] = outcomes.get(key, 0) + 1
        timestamp = self._clock()
        projection = LearningObservability(
            metadata=self._metadata(organization_id, effective_correlation, timestamp),
            agent_id=agent_id,
            learning_episode_count=len(agent_episodes),
            assessed_lesson_count=len(agent_lessons),
            retrieved_lesson_reuse_count=sum(
                len(retrieval.lesson_references) for retrieval in agent_retrievals
            ),
            stale_lesson_count=sum(lesson.stale for lesson in agent_lessons),
            revoked_lesson_count=sum(lesson.revoked for lesson in agent_lessons),
            escalation_count=sum(
                episode.terminal_outcome is LearningTerminalOutcome.ESCALATED
                for episode in agent_episodes
            ),
            assessment_outcomes=outcomes,
        )
        return Result.success(projection)

    def learning_observability(
        self,
        organization_id: OrganizationId,
        agent_id: AgentId,
        *,
        correlation_id: CorrelationId | None = None,
    ) -> Result[LearningObservability, ErrorDetail]:
        """Descriptive alias for the per-agent observability projection."""
        return self.observability(organization_id, agent_id, correlation_id=correlation_id)

    # Keep the design document's camelCase command names available to integrations.
    assessLesson = assess_lesson  # noqa: N815
    assess = assess_lesson
    retrieveLessons = retrieve_lessons  # noqa: N815
    retrieve = retrieve_lessons
    revokeLesson = revoke_lesson  # noqa: N815
    linkOutput = link_output  # noqa: N815
    getObservability = observability  # noqa: N815

    def _source_references_are_available(
        self, candidate: Lesson, correlation_id: CorrelationId
    ) -> Result[bool, ErrorDetail]:
        if self._episode_repository is None:
            return Result.success(True)
        episodes = self._episode_repository.list_for_organization(candidate.organization_id)
        if not episodes.is_success or episodes.value is None:
            return Result.failure(
                _repository_error(
                    correlation_id, episodes.error, "Source Learning_Episode lookup is unavailable."
                )
            )
        available = {
            reference
            for episode in episodes.value
            for reference in (str(episode.episode_id), str(episode.metadata.record_id))
        }
        return Result.success(
            all(reference in available for reference in candidate.source_episode_references)
        )

    def _append_lesson(
        self, lesson: Lesson, correlation_id: CorrelationId
    ) -> Result[Lesson, ErrorDetail]:
        try:
            persisted = self._lesson_repository.append(lesson)
        except Exception:
            return Result.failure(
                _repository_error(correlation_id, fallback="Lesson persistence is unavailable.")
            )
        if persisted.is_success and persisted.value is not None:
            return Result.success(persisted.value)
        return Result.failure(_repository_error(correlation_id, persisted.error))

    def _resolve_lesson(
        self,
        lesson: Lesson | LessonId | str,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
    ) -> Result[Lesson, ErrorDetail]:
        if isinstance(lesson, Lesson):
            if lesson.organization_id != organization_id:
                return Result.failure(
                    ErrorDetail(
                        ErrorCode.AUTHORIZATION_DENIED,
                        "Lesson organization is outside the requested scope.",
                        correlation_id,
                    )
                )
            return Result.success(lesson)
        lessons = self._lessons_for_organization(organization_id, correlation_id)
        if not lessons.is_success or lessons.value is None:
            return Result.failure(lessons.error or _repository_error(correlation_id))
        for candidate in lessons.value:
            if str(candidate.lesson_id) == str(lesson):
                return Result.success(candidate)
        return Result.failure(
            ErrorDetail(ErrorCode.NOT_FOUND, "Lesson was not found.", correlation_id)
        )

    def _resolve_retrieval(
        self,
        retrieval: RetrievalRecord | RetrievalRecordId | str | None,
        organization_id: OrganizationId | None,
        correlation_id: CorrelationId,
    ) -> Result[_ResolvedRetrieval, ErrorDetail]:
        if retrieval is None:
            return Result.success(_ResolvedRetrieval(None))
        if isinstance(retrieval, RetrievalRecord):
            if organization_id is not None and retrieval.organization_id != organization_id:
                return Result.failure(
                    ErrorDetail(
                        ErrorCode.AUTHORIZATION_DENIED,
                        "Retrieval_Record organization is outside the requested scope.",
                        correlation_id,
                    )
                )
            return Result.success(_ResolvedRetrieval(retrieval))
        if organization_id is None:
            return Result.failure(
                _validation_error(
                    correlation_id,
                    "organization_id",
                    "Resolving a Retrieval_Record identifier requires organization scope.",
                )
            )
        try:
            found = self._retrieval_repository.get(organization_id, RecordId(str(retrieval)))
        except Exception:
            return Result.failure(
                _repository_error(
                    correlation_id, fallback="Retrieval_Record lookup is unavailable."
                )
            )
        if not found.is_success or found.value is None:
            return Result.failure(
                _repository_error(correlation_id, found.error, "Retrieval_Record was not found.")
            )
        return Result.success(_ResolvedRetrieval(found.value))

    def _revoked_lesson_ids(
        self, organization_id: OrganizationId, correlation_id: CorrelationId
    ) -> Result[frozenset[str], ErrorDetail]:
        try:
            audits = self._audit_repository.list_for_organization(organization_id)
        except Exception:
            return Result.failure(
                _repository_error(
                    correlation_id, fallback="Lesson revocation audit lookup is unavailable."
                )
            )
        if not audits.is_success or audits.value is None:
            return Result.failure(
                _repository_error(
                    correlation_id, audits.error, "Lesson revocation audit lookup failed."
                )
            )
        return Result.success(
            frozenset(
                audit.subject_reference
                for audit in audits.value
                if audit.action == "lesson.revocation"
            )
        )

    def _lessons_for_organization(
        self, organization_id: OrganizationId, correlation_id: CorrelationId
    ) -> Result[tuple[Lesson, ...], ErrorDetail]:
        try:
            records = self._lesson_repository.list_for_organization(organization_id)
        except Exception:
            return Result.failure(
                _repository_error(correlation_id, fallback="Lesson lookup is unavailable.")
            )
        if not records.is_success or records.value is None:
            return Result.failure(_repository_error(correlation_id, records.error))
        return Result.success(records.value)

    def _episodes_for_organization(
        self, organization_id: OrganizationId, correlation_id: CorrelationId
    ) -> Result[tuple[LearningEpisode, ...], ErrorDetail]:
        if self._episode_repository is None:
            return Result.success(())
        try:
            records = self._episode_repository.list_for_organization(organization_id)
        except Exception:
            return Result.failure(
                _repository_error(
                    correlation_id, fallback="Learning_Episode lookup is unavailable."
                )
            )
        if not records.is_success or records.value is None:
            return Result.failure(_repository_error(correlation_id, records.error))
        return Result.success(records.value)

    def _retrievals_for_organization(
        self, organization_id: OrganizationId, correlation_id: CorrelationId
    ) -> Result[tuple[RetrievalRecord, ...], ErrorDetail]:
        try:
            records = self._retrieval_repository.list_for_organization(organization_id)
        except Exception:
            return Result.failure(
                _repository_error(
                    correlation_id, fallback="Retrieval_Record lookup is unavailable."
                )
            )
        if not records.is_success or records.value is None:
            return Result.failure(_repository_error(correlation_id, records.error))
        return Result.success(records.value)

    def _validate_episode_references(
        self,
        organization_id: OrganizationId,
        references: tuple[str, ...],
        correlation_id: CorrelationId,
    ) -> Result[bool, ErrorDetail]:
        if self._episode_repository is None:
            return Result.success(True)
        episodes = self._episodes_for_organization(organization_id, correlation_id)
        if not episodes.is_success or episodes.value is None:
            return Result.failure(episodes.error or _repository_error(correlation_id))
        available = {
            reference
            for episode in episodes.value
            for reference in (str(episode.episode_id), str(episode.metadata.record_id))
        }
        if any(reference not in available for reference in references):
            return Result.failure(
                _validation_error(
                    correlation_id,
                    "source_episode_references",
                    "Output provenance references an unavailable Learning_Episode.",
                )
            )
        return Result.success(True)

    @staticmethod
    def _metadata(
        organization_id: OrganizationId, correlation_id: CorrelationId, timestamp: datetime
    ) -> RecordMetadata:
        return RecordMetadata(
            record_id=new_record_id(),
            organization_id=organization_id,
            correlation_id=correlation_id,
            schema_version=SCHEMA_VERSION,
            version=1,
            created_at=timestamp,
            updated_at=timestamp,
        )


def _coerce_assessment(
    assessment: LessonAssessment | Mapping[str, object] | None,
    *,
    format_valid: bool | None,
    source_episode_references_valid: bool | None,
    safety_policy_passed: bool | None,
    domain_policy_passed: bool | None,
    evaluation_score: float | None,
    evaluation_threshold: float | None,
) -> LessonAssessment:
    if assessment is None:
        return LessonAssessment(
            format_valid=format_valid or False,
            source_episode_references_valid=source_episode_references_valid or False,
            safety_policy_passed=safety_policy_passed or False,
            domain_policy_passed=domain_policy_passed or False,
            evaluation_score=evaluation_score,
            evaluation_threshold=evaluation_threshold,
        )
    if isinstance(assessment, Mapping):
        base = LessonAssessment.from_mapping(assessment)
    else:
        base = assessment
    return LessonAssessment(
        format_valid=base.format_valid if format_valid is None else format_valid,
        source_episode_references_valid=(
            base.source_episode_references_valid
            if source_episode_references_valid is None
            else source_episode_references_valid
        ),
        safety_policy_passed=(
            base.safety_policy_passed if safety_policy_passed is None else safety_policy_passed
        ),
        domain_policy_passed=(
            base.domain_policy_passed if domain_policy_passed is None else domain_policy_passed
        ),
        evaluation_score=base.evaluation_score if evaluation_score is None else evaluation_score,
        evaluation_threshold=(
            base.evaluation_threshold if evaluation_threshold is None else evaluation_threshold
        ),
        evidence_references=base.evidence_references,
    )


def _coerce_retrieval_request(
    request: LessonRetrievalRequest | OrganizationId,
    domain_id: DomainId | str | None,
    pack_version: str | None,
    agent_id: AgentId | str | None,
    memory_scope: str | None,
) -> LessonRetrievalRequest:
    if isinstance(request, LessonRetrievalRequest):
        if any(value is not None for value in (domain_id, pack_version, agent_id, memory_scope)):
            raise ValueError(
                "A LessonRetrievalRequest cannot be combined with positional scope fields."
            )
        return request
    if None in (domain_id, pack_version, agent_id, memory_scope):
        raise ValueError(
            "organization, domain, pack version, agent, and memory scope are required."
        )
    return LessonRetrievalRequest(
        organization_id=request,
        domain_id=DomainId(cast(str, domain_id)),
        pack_version=cast(str, pack_version),
        agent_id=AgentId(cast(str, agent_id)),
        memory_scope=cast(str, memory_scope),
    )


def _lesson_matches_request(lesson: Lesson, request: LessonRetrievalRequest) -> bool:
    try:
        return (
            lesson.metadata.organization_id == request.organization_id
            and lesson.domain_id == request.domain_id
            and lesson.pack_version_range.contains(request.pack_version)
            and lesson.agent_id == request.agent_id
            and lesson.memory_scope == request.memory_scope
            and lesson.assessment is LessonAssessmentOutcome.PASSED
            and lesson.retrievable
            and not lesson.revoked
            and not lesson.stale
        )
    except ValueError:
        return False


def _assessment_failures(
    assessment: LessonAssessment, source_references_available: bool
) -> tuple[str, ...]:
    failures: list[str] = []
    if not assessment.format_valid:
        failures.append("format")
    if not assessment.source_episode_references_valid or not source_references_available:
        failures.append("source_learning_episodes")
    if not assessment.safety_policy_passed:
        failures.append("safety_policy")
    if not assessment.domain_policy_passed:
        failures.append("domain_policy")
    if not assessment.threshold_passed:
        failures.append("evaluation_threshold")
    return tuple(failures)


def _score_is_valid(value: float) -> bool:
    return math.isfinite(value) and 0 <= value <= 1


def _mapping_bool(values: Mapping[str, object], *names: str) -> bool:
    for name in names:
        value = values.get(name)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.strip().casefold() in {"true", "yes", "on", "enabled", "passed"}
    return False


def _mapping_float(values: Mapping[str, object], *names: str) -> float | None:
    for name in names:
        value = values.get(name)
        if isinstance(value, bool):
            return float(value)
        if isinstance(value, int | float):
            return float(value)
    return None


def _mapping_references(value: object) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple, set, frozenset)):
        return ()
    return _references(value, "evidence_references")


def _references(values: Iterable[object], name: str) -> tuple[str, ...]:
    references = tuple(str(value) for value in values)
    if any(not reference.strip() for reference in references):
        raise ValueError(f"{name} references must be non-empty.")
    if len(references) != len(set(references)):
        raise ValueError(f"{name} references must be unique.")
    return references


def _unique_references(values: Iterable[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(reference for reference in values if reference.strip()))


def _episode_reference(value: str | LearningEpisode) -> str:
    return str(value.episode_id) if isinstance(value, LearningEpisode) else str(value)


def _validation_error(correlation_id: CorrelationId, field_name: str, message: str) -> ErrorDetail:
    from app.models.contracts import ErrorField

    return ErrorDetail(
        ErrorCode.VALIDATION_FAILED,
        message,
        correlation_id,
        fields=(ErrorField(field_name, "invalid"),),
    )


def _repository_error(
    correlation_id: CorrelationId,
    error: RepositoryError | None = None,
    fallback: str = "Lesson repository is unavailable.",
) -> ErrorDetail:
    if error is None:
        return ErrorDetail(
            ErrorCode.REPOSITORY_UNAVAILABLE,
            fallback,
            correlation_id,
            retryable=True,
        )
    return ErrorDetail(
        error.code,
        error.message,
        correlation_id,
        retryable=error.retryable,
        fields=error.fields,
    )
