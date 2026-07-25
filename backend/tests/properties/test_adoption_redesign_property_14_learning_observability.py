"""Property checks for redacted per-agent learning observability."""

from __future__ import annotations

# The required property label is intentionally kept in its exact documented form below.
# ruff: noqa: E501
from dataclasses import dataclass, fields
from datetime import UTC, datetime

from hypothesis import given, settings, strategies as st

from app.memory.lesson_service import LessonService
from app.models.common import SCHEMA_VERSION, CompatibilityRange, RecordMetadata
from app.models.control_plane import (
    AgentNodeAttemptId,
    LearningEpisodeId,
    LessonId,
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
    AgentId,
    CorrelationId,
    DomainId,
    OrganizationId,
    RecordId,
)
from tests.fakes.adoption import DeterministicAdoptionRepositories

_NOW = datetime(2025, 1, 1, tzinfo=UTC)


@dataclass(frozen=True, slots=True)
class _LessonEvidence:
    """Generated Lesson state retained in the source evidence set."""

    assessment: LessonAssessmentOutcome
    stale: bool
    revoked: bool


@dataclass(frozen=True, slots=True)
class _ObservabilityCase:
    """Mixed target- and non-target-agent evidence for one projection."""

    case_id: int
    target_episode_outcomes: tuple[LearningTerminalOutcome, ...]
    other_episode_outcomes: tuple[LearningTerminalOutcome, ...]
    target_lessons: tuple[_LessonEvidence, ...]
    other_lessons: tuple[_LessonEvidence, ...]
    target_retrieval_sizes: tuple[int, ...]
    other_retrieval_sizes: tuple[int, ...]


@st.composite
def _observability_cases(draw: st.DrawFn) -> _ObservabilityCase:
    """Generate bounded mixed evidence for two agents in one organization."""
    case_id = draw(st.integers(min_value=0, max_value=10_000))
    episode_strategy = st.lists(
        st.sampled_from(tuple(LearningTerminalOutcome)), min_size=0, max_size=4
    )
    target_episode_outcomes = tuple(draw(episode_strategy))
    other_episode_outcomes = tuple(draw(episode_strategy))

    lesson_strategy = st.lists(
        st.tuples(
            st.sampled_from(tuple(LessonAssessmentOutcome)),
            st.booleans(),
            st.booleans(),
        ),
        min_size=0,
        max_size=4,
    )
    target_lessons = tuple(
        _LessonEvidence(assessment, stale, revoked)
        for assessment, stale, revoked in draw(lesson_strategy)
    )
    other_lessons = tuple(
        _LessonEvidence(assessment, stale, revoked)
        for assessment, stale, revoked in draw(lesson_strategy)
    )

    def retrieval_sizes(lesson_count: int) -> tuple[int, ...]:
        size_strategy = st.integers(min_value=0, max_value=min(3, lesson_count))
        return tuple(draw(st.lists(size_strategy, min_size=0, max_size=4)))

    return _ObservabilityCase(
        case_id=case_id,
        target_episode_outcomes=target_episode_outcomes,
        other_episode_outcomes=other_episode_outcomes,
        target_lessons=target_lessons,
        other_lessons=other_lessons,
        target_retrieval_sizes=retrieval_sizes(len(target_lessons)),
        other_retrieval_sizes=retrieval_sizes(len(other_lessons)),
    )


def _organization(case: _ObservabilityCase) -> OrganizationId:
    """Return the organization shared by the mixed target and other-agent records."""
    return OrganizationId(f"organization-property-14-{case.case_id}")


def _target_agent(case: _ObservabilityCase) -> AgentId:
    """Return the agent whose projection is being checked."""
    return AgentId(f"agent-target-property-14-{case.case_id}")


def _other_agent(case: _ObservabilityCase) -> AgentId:
    """Return an agent whose records must not affect the target projection."""
    return AgentId(f"agent-other-property-14-{case.case_id}")


def _metadata(
    case: _ObservabilityCase,
    record_kind: str,
    owner: str,
    index: int,
) -> RecordMetadata:
    """Build deterministic metadata for one generated evidence record."""
    organization_id = _organization(case)
    return RecordMetadata(
        record_id=RecordId(f"{record_kind}-record-property-14-{case.case_id}-{owner}-{index}"),
        organization_id=organization_id,
        correlation_id=CorrelationId(f"correlation-property-14-{case.case_id}"),
        schema_version=SCHEMA_VERSION,
        version=1,
        created_at=_NOW,
        updated_at=_NOW,
    )


def _episode(
    case: _ObservabilityCase,
    owner: str,
    agent_id: AgentId,
    index: int,
    outcome: LearningTerminalOutcome,
) -> LearningEpisode:
    """Build one terminal Learning_Episode for the selected agent."""
    return LearningEpisode(
        metadata=_metadata(case, "episode", owner, index),
        episode_id=LearningEpisodeId(f"episode-property-14-{case.case_id}-{owner}-{index}"),
        attempt_id=AgentNodeAttemptId(f"attempt-property-14-{case.case_id}-{owner}-{index}"),
        organization_id=_organization(case),
        domain_id=DomainId(f"domain-property-14-{case.case_id}"),
        pack_version="1.0.0",
        agent_id=agent_id,
        terminal_outcome=outcome,
        outcome_reference=f"outcome-property-14-{case.case_id}-{owner}-{index}",
        recorded_at=_NOW,
    )


def _lesson(
    case: _ObservabilityCase,
    owner: str,
    agent_id: AgentId,
    index: int,
    evidence: _LessonEvidence,
) -> Lesson:
    """Build one Lesson with unique sensitive content that must not reach projections."""
    return Lesson(
        metadata=_metadata(case, "lesson", owner, index),
        lesson_id=LessonId(f"lesson-property-14-{case.case_id}-{owner}-{index}"),
        organization_id=_organization(case),
        domain_id=DomainId(f"domain-property-14-{case.case_id}"),
        pack_version_range=CompatibilityRange.exact("1.0.0"),
        agent_id=agent_id,
        memory_scope=f"agent:{agent_id}:memory",
        assessment=evidence.assessment,
        source_episode_references=(f"episode-source-property-14-{case.case_id}-{owner}-{index}",),
        content_reference=f"SENSITIVE-LESSON-CONTENT-property-14-{case.case_id}-{owner}-{index}",
        assessed_at=_NOW,
        retrievable=(
            evidence.assessment is LessonAssessmentOutcome.PASSED
            and not evidence.stale
            and not evidence.revoked
        ),
        revoked=evidence.revoked,
        stale=evidence.stale,
    )


def _retrieval(
    case: _ObservabilityCase,
    owner: str,
    agent_id: AgentId,
    index: int,
    lesson_ids: tuple[LessonId, ...],
    reference_count: int,
) -> RetrievalRecord:
    """Build a Retrieval_Record referencing existing Lessons for the selected agent."""
    return RetrievalRecord(
        metadata=_metadata(case, "retrieval", owner, index),
        retrieval_record_id=RetrievalRecordId(
            f"retrieval-property-14-{case.case_id}-{owner}-{index}"
        ),
        attempt_id=AgentNodeAttemptId(
            f"retrieval-attempt-property-14-{case.case_id}-{owner}-{index}"
        ),
        organization_id=_organization(case),
        domain_id=DomainId(f"domain-property-14-{case.case_id}"),
        pack_version="1.0.0",
        agent_id=agent_id,
        memory_scope=f"agent:{agent_id}:memory",
        retrieved_at=_NOW,
        lesson_references=tuple(str(lesson_id) for lesson_id in lesson_ids[:reference_count]),
    )


def _service(repositories: DeterministicAdoptionRepositories) -> LessonService:
    """Compose the Lesson service from deterministic repositories only."""
    return LessonService(
        repositories.lessons,
        repositories.retrievals,
        repositories.episodes,
        repositories.audit,
        clock=lambda: _NOW,
    )


def _append_case_evidence(
    case: _ObservabilityCase,
    repositories: DeterministicAdoptionRepositories,
) -> tuple[str, ...]:
    """Persist all generated evidence and return every sensitive Lesson reference."""
    sensitive_content: list[str] = []
    for owner, agent_id, outcomes in (
        ("target", _target_agent(case), case.target_episode_outcomes),
        ("other", _other_agent(case), case.other_episode_outcomes),
    ):
        for index, outcome in enumerate(outcomes):
            assert repositories.episodes.append(
                _episode(case, owner, agent_id, index, outcome)
            ).is_success

    lesson_ids_by_owner: dict[str, tuple[LessonId, ...]] = {}
    for owner, agent_id, lesson_evidence in (
        ("target", _target_agent(case), case.target_lessons),
        ("other", _other_agent(case), case.other_lessons),
    ):
        lessons = tuple(
            _lesson(case, owner, agent_id, index, evidence)
            for index, evidence in enumerate(lesson_evidence)
        )
        for lesson in lessons:
            assert repositories.lessons.append(lesson).is_success
            sensitive_content.append(lesson.content_reference)
        lesson_ids_by_owner[owner] = tuple(lesson.lesson_id for lesson in lessons)

    for owner, agent_id, sizes in (
        ("target", _target_agent(case), case.target_retrieval_sizes),
        ("other", _other_agent(case), case.other_retrieval_sizes),
    ):
        for index, reference_count in enumerate(sizes):
            retrieval = _retrieval(
                case,
                owner,
                agent_id,
                index,
                lesson_ids_by_owner[owner],
                reference_count,
            )
            assert repositories.retrievals.append(retrieval).is_success

    return tuple(sensitive_content)


# Feature: adoption-redesign, Property 14: Learning observability preserves counts while redacting content
# **Validates: Requirements 5.9**
@settings(max_examples=100, deadline=None)
@given(case=_observability_cases())
def test_property_14_learning_observability_preserves_counts_while_redacting_content(
    case: _ObservabilityCase,
) -> None:
    """The target projection counts only its agent's evidence and contains no Lesson body."""
    repositories = DeterministicAdoptionRepositories()
    sensitive_content = _append_case_evidence(case, repositories)

    result = _service(repositories).observability(_organization(case), _target_agent(case))

    assert result.is_success and result.value is not None
    projection = result.value
    expected_assessment_outcomes: dict[str, int] = {}
    for lesson in case.target_lessons:
        outcome = str(lesson.assessment)
        expected_assessment_outcomes[outcome] = expected_assessment_outcomes.get(outcome, 0) + 1

    assert projection.learning_episode_count == len(case.target_episode_outcomes)
    assert projection.assessed_lesson_count == len(case.target_lessons)
    assert projection.retrieved_lesson_reuse_count == sum(case.target_retrieval_sizes)
    assert projection.stale_lesson_count == sum(lesson.stale for lesson in case.target_lessons)
    assert projection.revoked_lesson_count == sum(lesson.revoked for lesson in case.target_lessons)
    assert projection.escalation_count == sum(
        outcome is LearningTerminalOutcome.ESCALATED for outcome in case.target_episode_outcomes
    )
    assert dict(projection.assessment_outcomes) == expected_assessment_outcomes

    projection_fields = fields(projection)
    assert all(field.name != "content_reference" for field in projection_fields)
    projection_text = repr(projection)
    assert all(content_reference not in projection_text for content_reference in sensitive_content)
