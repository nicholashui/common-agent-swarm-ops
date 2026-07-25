"""Focused governance, provenance, and observability tests for Lessons."""

from __future__ import annotations

from datetime import UTC, datetime

from app.memory.lesson_service import LessonAssessment, LessonRetrievalRequest, LessonService
from app.models.common import CompatibilityRange, RecordMetadata
from app.models.control_plane import (
    AgentNodeAttemptId,
    LearningEpisodeId,
    RetrievalRecordId,
)
from app.models.evidence import (
    LearningEpisode,
    LearningTerminalOutcome,
    Lesson,
    LessonAssessmentOutcome,
    RetrievalRecord,
)
from app.models.identifiers import (
    ActorId,
    AgentId,
    CorrelationId,
    DomainId,
    OrganizationId,
    RecordId,
)
from tests.fakes.adoption import DeterministicAdoptionRepositories, FakeFailurePlan

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_ORGANIZATION = OrganizationId("organization-lessons")
_DOMAIN = DomainId("domain-lessons")
_AGENT = AgentId("agent-lessons")
_CORRELATION = CorrelationId("correlation-lessons")


def _metadata(record_id: str) -> RecordMetadata:
    return RecordMetadata(
        record_id=RecordId(record_id),
        organization_id=_ORGANIZATION,
        correlation_id=_CORRELATION,
        schema_version=1,
        version=1,
        created_at=_NOW,
        updated_at=_NOW,
    )


def _episode(
    record_id: str = "episode-record-1",
    episode_id: str = "episode-1",
    *,
    outcome: LearningTerminalOutcome = LearningTerminalOutcome.COMPLETED,
    attempt_id: str = "attempt-1",
) -> LearningEpisode:
    return LearningEpisode(
        metadata=_metadata(record_id),
        episode_id=LearningEpisodeId(episode_id),
        attempt_id=AgentNodeAttemptId(attempt_id),
        organization_id=_ORGANIZATION,
        domain_id=_DOMAIN,
        pack_version="1.0.0",
        agent_id=_AGENT,
        terminal_outcome=outcome,
        outcome_reference=f"outcome:{episode_id}",
        recorded_at=_NOW,
    )


def _lesson(
    record_id: str = "lesson-record-1",
    lesson_id: str = "lesson-1",
    *,
    episode_reference: str = "episode-1",
    stale: bool = False,
) -> Lesson:
    return Lesson(
        metadata=_metadata(record_id),
        lesson_id=lesson_id,  # type: ignore[arg-type]
        organization_id=_ORGANIZATION,
        domain_id=_DOMAIN,
        pack_version_range=CompatibilityRange.exact("1.0.0"),
        agent_id=_AGENT,
        memory_scope="agent:agent-lessons",
        assessment=LessonAssessmentOutcome.FAILED,
        source_episode_references=(episode_reference,),
        content_reference=f"content:{lesson_id}",
        assessed_at=_NOW,
        stale=stale,
    )


def _service(
    repositories: DeterministicAdoptionRepositories,
) -> LessonService:
    return LessonService(
        repositories.lessons,
        repositories.retrievals,
        repositories.episodes,
        repositories.audit,
        clock=lambda: _NOW,
    )


def _passed_assessment() -> LessonAssessment:
    return LessonAssessment(
        format_valid=True,
        source_episode_references_valid=True,
        safety_policy_passed=True,
        domain_policy_passed=True,
        evaluation_score=0.95,
        evaluation_threshold=0.8,
        evidence_references=("assessment:lesson",),
    )


def _retrieval() -> RetrievalRecord:
    return RetrievalRecord(
        metadata=_metadata("retrieval-record-1"),
        retrieval_record_id=RetrievalRecordId("retrieval-1"),
        attempt_id=AgentNodeAttemptId("attempt-1"),
        organization_id=_ORGANIZATION,
        domain_id=_DOMAIN,
        pack_version="1.0.0",
        agent_id=_AGENT,
        memory_scope="agent:agent-lessons",
        retrieved_at=_NOW,
        lesson_references=("lesson-1",),
    )


def test_assessment_requires_every_criterion_and_retrieval_enforces_all_scope() -> None:
    repositories = DeterministicAdoptionRepositories()
    assert repositories.episodes.append(_episode()).is_success
    service = _service(repositories)

    assessed = service.assess_lesson(_lesson(), _passed_assessment())
    assert assessed.is_success and assessed.value is not None
    assert assessed.value.retrievable

    in_scope = service.retrieve_lessons(
        LessonRetrievalRequest(_ORGANIZATION, _DOMAIN, "1.0.0", _AGENT, "agent:agent-lessons")
    )
    assert in_scope.is_success and in_scope.value == (assessed.value,)

    cross_domain = service.retrieve_lessons(
        _ORGANIZATION, DomainId("foreign-domain"), "1.0.0", _AGENT, "agent:agent-lessons"
    )
    assert cross_domain.is_success and cross_domain.value == ()

    failed = service.assess_lesson(
        _lesson("lesson-record-2", "lesson-2"),
        LessonAssessment(
            format_valid=True,
            source_episode_references_valid=True,
            safety_policy_passed=True,
            domain_policy_passed=False,
            evaluation_score=0.95,
            evaluation_threshold=0.8,
        ),
    )
    assert failed.is_success and failed.value is not None
    assert failed.value.assessment is LessonAssessmentOutcome.FAILED
    assert not failed.value.retrievable


def test_revocation_is_audit_gated_and_records_reason_actor_and_sources() -> None:
    plan = FakeFailurePlan()
    repositories = DeterministicAdoptionRepositories(plan)
    assert repositories.episodes.append(_episode()).is_success
    service = _service(repositories)
    assessed = service.assess_lesson(_lesson(), _passed_assessment())
    assert assessed.is_success and assessed.value is not None

    plan.fail_next_audit()
    pending = service.revoke_lesson(
        assessed.value,
        "source evidence was superseded",
        ActorId("reviewer-lessons"),
        ("episode-1",),
    )
    assert not pending.is_success
    retained = service.retrieve_lessons(
        _ORGANIZATION, _DOMAIN, "1.0.0", _AGENT, "agent:agent-lessons"
    )
    assert retained.is_success and retained.value == (assessed.value,)

    revoked = service.revoke_lesson(
        assessed.value,
        "source evidence was superseded",
        ActorId("reviewer-lessons"),
        ("episode-1",),
    )
    assert revoked.is_success and revoked.value is not None and revoked.value.revoked
    assert (
        service.retrieve_lessons(
            _ORGANIZATION, _DOMAIN, "1.0.0", _AGENT, "agent:agent-lessons"
        ).value
        == ()
    )
    audit = repositories.audit.records[-1]
    assert audit.action == "lesson.revocation"
    assert audit.actor_id == ActorId("reviewer-lessons")
    assert audit.reason == "source evidence was superseded"
    assert audit.source_references == ("episode-1",)


def test_output_provenance_never_invents_retrieval_and_observability_is_redacted() -> None:
    repositories = DeterministicAdoptionRepositories()
    assert repositories.episodes.append(_episode()).is_success
    assert repositories.episodes.append(
        _episode(
            "episode-record-2",
            "episode-2",
            outcome=LearningTerminalOutcome.ESCALATED,
            attempt_id="attempt-2",
        )
    ).is_success
    service = _service(repositories)
    assessed = service.assess_lesson(_lesson(), _passed_assessment())
    assert assessed.is_success
    assert repositories.retrievals.append(_retrieval()).is_success

    with_retrieval = service.link_output("output-1", _retrieval())
    assert with_retrieval.is_success and with_retrieval.value is not None
    assert with_retrieval.value.retrieval_record_id == RetrievalRecordId("retrieval-1")
    assert with_retrieval.value.source_episode_references == ("episode-1",)

    without_retrieval = service.link_output(
        "output-2",
        source_episode_references=("episode-1",),
        organization_id=_ORGANIZATION,
    )
    assert without_retrieval.is_success and without_retrieval.value is not None
    assert without_retrieval.value.retrieval_record_id is None
    assert without_retrieval.value.source_episode_references == ("episode-1",)

    projection = service.observability(_ORGANIZATION, _AGENT)
    assert projection.is_success and projection.value is not None
    assert projection.value.learning_episode_count == 2
    assert projection.value.assessed_lesson_count == 1
    assert projection.value.retrieved_lesson_reuse_count == 1
    assert projection.value.escalation_count == 1
    assert projection.value.assessment_outcomes == {"passed": 1}
    assert not hasattr(projection.value, "content_reference")
