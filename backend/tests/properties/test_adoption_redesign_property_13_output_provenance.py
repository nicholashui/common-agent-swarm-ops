"""Property checks for complete output provenance with optional retrieval evidence."""

from __future__ import annotations

from dataclasses import dataclass
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
class _OutputProvenanceCase:
    """Bounded source-episode and optional retrieval lineage inputs."""

    case_id: int
    retrieval_present: bool
    lesson_source_indices: tuple[tuple[int, ...], ...]
    direct_source_indices: tuple[int, ...]


@st.composite
def _output_provenance_cases(draw: st.DrawFn) -> _OutputProvenanceCase:
    """Generate valid source episodes with or without retrieval evidence."""
    case_id = draw(st.integers(min_value=0, max_value=10_000))
    retrieval_present = draw(st.booleans())
    lesson_source_indices = (
        tuple(
            tuple(indices)
            for indices in draw(
                st.lists(
                    st.lists(
                        st.integers(min_value=0, max_value=2),
                        min_size=1,
                        max_size=3,
                        unique=True,
                    ),
                    min_size=1,
                    max_size=3,
                )
            )
        )
        if retrieval_present
        else ()
    )
    direct_source_indices = tuple(
        draw(
            st.lists(
                st.integers(min_value=0, max_value=2),
                min_size=0 if retrieval_present else 1,
                max_size=3,
                unique=True,
            )
        )
    )
    return _OutputProvenanceCase(
        case_id=case_id,
        retrieval_present=retrieval_present,
        lesson_source_indices=lesson_source_indices,
        direct_source_indices=direct_source_indices,
    )


def _metadata(case: _OutputProvenanceCase, record_kind: str, suffix: str) -> RecordMetadata:
    """Build deterministic metadata for one generated evidence record."""
    organization_id = OrganizationId(f"organization-property-13-{case.case_id}")
    return RecordMetadata(
        record_id=RecordId(f"{record_kind}-record-property-13-{case.case_id}-{suffix}"),
        organization_id=organization_id,
        correlation_id=CorrelationId(f"correlation-property-13-{case.case_id}"),
        schema_version=SCHEMA_VERSION,
        version=1,
        created_at=_NOW,
        updated_at=_NOW,
    )


def _episode(case: _OutputProvenanceCase, index: int) -> LearningEpisode:
    """Build one source Learning_Episode referenced by generated provenance."""
    organization_id = OrganizationId(f"organization-property-13-{case.case_id}")
    return LearningEpisode(
        metadata=_metadata(case, "episode", str(index)),
        episode_id=LearningEpisodeId(f"episode-property-13-{case.case_id}-{index}"),
        attempt_id=AgentNodeAttemptId(f"attempt-property-13-{case.case_id}-{index}"),
        organization_id=organization_id,
        domain_id=DomainId(f"domain-property-13-{case.case_id}"),
        pack_version="1.0.0",
        agent_id=AgentId(f"agent-property-13-{case.case_id}"),
        terminal_outcome=LearningTerminalOutcome.COMPLETED,
        outcome_reference=f"outcome-property-13-{case.case_id}-{index}",
        recorded_at=_NOW,
    )


def _lesson(
    case: _OutputProvenanceCase,
    index: int,
    source_references: tuple[str, ...],
) -> Lesson:
    """Build a retrieved Lesson whose source episodes must reach the output."""
    organization_id = OrganizationId(f"organization-property-13-{case.case_id}")
    return Lesson(
        metadata=_metadata(case, "lesson", str(index)),
        lesson_id=LessonId(f"lesson-property-13-{case.case_id}-{index}"),
        organization_id=organization_id,
        domain_id=DomainId(f"domain-property-13-{case.case_id}"),
        pack_version_range=CompatibilityRange.exact("1.0.0"),
        agent_id=AgentId(f"agent-property-13-{case.case_id}"),
        memory_scope=f"agent:agent-property-13-{case.case_id}:memory",
        assessment=LessonAssessmentOutcome.PASSED,
        source_episode_references=source_references,
        content_reference=f"content-reference-property-13-{case.case_id}-{index}",
        assessed_at=_NOW,
        retrievable=True,
    )


def _retrieval(
    case: _OutputProvenanceCase,
    lesson_references: tuple[str, ...],
) -> RetrievalRecord:
    """Build the Retrieval_Record selecting the generated Lessons."""
    organization_id = OrganizationId(f"organization-property-13-{case.case_id}")
    return RetrievalRecord(
        metadata=_metadata(case, "retrieval", "0"),
        retrieval_record_id=RetrievalRecordId(f"retrieval-property-13-{case.case_id}"),
        attempt_id=AgentNodeAttemptId(f"attempt-property-13-{case.case_id}-retrieval"),
        organization_id=organization_id,
        domain_id=DomainId(f"domain-property-13-{case.case_id}"),
        pack_version="1.0.0",
        agent_id=AgentId(f"agent-property-13-{case.case_id}"),
        memory_scope=f"agent:agent-property-13-{case.case_id}:memory",
        retrieved_at=_NOW,
        lesson_references=lesson_references,
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


# Feature: adoption-redesign, Property 13: Output provenance is complete without inventing retrieval
# **Validates: Requirements 5.7, 5.8**
@settings(max_examples=100, deadline=None)
@given(case=_output_provenance_cases())
def test_property_13_output_provenance_is_complete_without_inventing_retrieval(
    case: _OutputProvenanceCase,
) -> None:
    """Output links include every retrieved Lesson source and never fabricate retrieval."""
    repositories = DeterministicAdoptionRepositories()
    episodes = tuple(_episode(case, index) for index in range(3))
    for episode in episodes:
        assert repositories.episodes.append(episode).is_success

    lesson_references: list[str] = []
    expected_source_references = [
        str(episodes[index].episode_id) for index in case.direct_source_indices
    ]
    for lesson_index, source_indices in enumerate(case.lesson_source_indices):
        lesson = _lesson(
            case,
            lesson_index,
            tuple(str(episodes[index].episode_id) for index in source_indices),
        )
        assert repositories.lessons.append(lesson).is_success
        lesson_references.append(str(lesson.lesson_id))
        expected_source_references.extend(lesson.source_episode_references)

    retrieval = _retrieval(case, tuple(lesson_references)) if case.retrieval_present else None
    if retrieval is not None:
        assert repositories.retrievals.append(retrieval).is_success

    service = _service(repositories)
    direct_sources = tuple(str(episodes[index].episode_id) for index in case.direct_source_indices)
    result = service.link_output(
        output_reference=f"output-property-13-{case.case_id}",
        retrieval=retrieval,
        source_episode_references=direct_sources,
        organization_id=OrganizationId(f"organization-property-13-{case.case_id}"),
    )

    assert result.is_success and result.value is not None
    provenance = result.value
    assert provenance.source_episode_references == tuple(dict.fromkeys(expected_source_references))
    if retrieval is None:
        assert provenance.retrieval_record_id is None
        assert repositories.retrievals.records() == ()
    else:
        assert provenance.retrieval_record_id == retrieval.retrieval_record_id
        assert repositories.retrievals.records() == (retrieval,)
