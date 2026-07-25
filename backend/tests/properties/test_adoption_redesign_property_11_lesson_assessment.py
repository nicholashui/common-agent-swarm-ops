"""Property checks for evidence-complete Lesson assessment and scoped retrieval."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from hypothesis import given, settings, strategies as st

from app.memory.lesson_service import LessonAssessment, LessonRetrievalRequest, LessonService
from app.models.common import SCHEMA_VERSION, CompatibilityRange, RecordMetadata
from app.models.control_plane import AgentNodeAttemptId, LearningEpisodeId, LessonId
from app.models.evidence import (
    LearningEpisode,
    LearningTerminalOutcome,
    Lesson,
    LessonAssessmentOutcome,
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
class _ScopeVector:
    """Generated request scope, including independent match outcomes."""

    organization_id: OrganizationId
    domain_id: DomainId
    pack_version: str
    agent_id: AgentId
    memory_scope: str
    requested_organization_id: OrganizationId
    requested_domain_id: DomainId
    requested_pack_version: str
    requested_agent_id: AgentId
    requested_memory_scope: str

    @property
    def matches_every_dimension(self) -> bool:
        """Return whether the request exactly matches the approved Lesson scope."""
        return (
            self.requested_organization_id == self.organization_id
            and self.requested_domain_id == self.domain_id
            and self.requested_pack_version == self.pack_version
            and self.requested_agent_id == self.agent_id
            and self.requested_memory_scope == self.memory_scope
        )


@dataclass(frozen=True, slots=True)
class _LessonCase:
    """Bounded assessment criteria and a complete retrieval scope vector."""

    case_id: int
    assessment: LessonAssessment
    scope: _ScopeVector


def _metadata(case_id: int, record_kind: str, organization_id: OrganizationId) -> RecordMetadata:
    """Build deterministic trace metadata for one generated record."""
    return RecordMetadata(
        record_id=RecordId(f"{record_kind}-record-property-11-{case_id}"),
        organization_id=organization_id,
        correlation_id=CorrelationId(f"correlation-property-11-{case_id}"),
        schema_version=SCHEMA_VERSION,
        version=1,
        created_at=_NOW,
        updated_at=_NOW,
    )


def _episode(case: _LessonCase) -> LearningEpisode:
    """Build the source episode that makes the generated reference resolvable."""
    return LearningEpisode(
        metadata=_metadata(case.case_id, "episode", case.scope.organization_id),
        episode_id=LearningEpisodeId(f"episode-property-11-{case.case_id}"),
        attempt_id=AgentNodeAttemptId(f"attempt-property-11-{case.case_id}"),
        organization_id=case.scope.organization_id,
        domain_id=case.scope.domain_id,
        pack_version=case.scope.pack_version,
        agent_id=case.scope.agent_id,
        terminal_outcome=LearningTerminalOutcome.COMPLETED,
        outcome_reference=f"outcome-property-11-{case.case_id}",
        recorded_at=_NOW,
    )


def _lesson(case: _LessonCase) -> Lesson:
    """Build a candidate Lesson with a single available source episode reference."""
    return Lesson(
        metadata=_metadata(case.case_id, "lesson", case.scope.organization_id),
        lesson_id=LessonId(f"lesson-property-11-{case.case_id}"),
        organization_id=case.scope.organization_id,
        domain_id=case.scope.domain_id,
        pack_version_range=CompatibilityRange.exact(case.scope.pack_version),
        agent_id=case.scope.agent_id,
        memory_scope=case.scope.memory_scope,
        assessment=LessonAssessmentOutcome.FAILED,
        source_episode_references=(str(_episode(case).episode_id),),
        content_reference=f"content-reference-property-11-{case.case_id}",
        assessed_at=_NOW,
    )


def _scope_vector(case_id: int, draw: st.DrawFn) -> _ScopeVector:
    """Generate independent exact/mismatched values for every approved scope field."""
    organization_id = OrganizationId(f"organization-property-11-{case_id}")
    domain_id = DomainId(f"domain-property-11-{case_id}")
    pack_version = "1.0.0"
    agent_id = AgentId(f"agent-property-11-{case_id}")
    memory_scope = f"agent:{agent_id}:memory"

    organization_matches = draw(st.booleans())
    domain_matches = draw(st.booleans())
    pack_version_matches = draw(st.booleans())
    agent_matches = draw(st.booleans())
    memory_scope_matches = draw(st.booleans())
    return _ScopeVector(
        organization_id=organization_id,
        domain_id=domain_id,
        pack_version=pack_version,
        agent_id=agent_id,
        memory_scope=memory_scope,
        requested_organization_id=(
            organization_id
            if organization_matches
            else OrganizationId(f"foreign-organization-property-11-{case_id}")
        ),
        requested_domain_id=(
            domain_id if domain_matches else DomainId(f"foreign-domain-property-11-{case_id}")
        ),
        requested_pack_version=(pack_version if pack_version_matches else "2.0.0"),
        requested_agent_id=(
            agent_id if agent_matches else AgentId(f"foreign-agent-property-11-{case_id}")
        ),
        requested_memory_scope=(
            memory_scope if memory_scope_matches else f"foreign:{case_id}:memory"
        ),
    )


@st.composite
def _lesson_cases(draw: st.DrawFn) -> _LessonCase:
    """Generate every assessment criterion and every approved scope dimension."""
    case_id = draw(st.integers(min_value=0, max_value=10_000))
    score = draw(st.sampled_from((0.0, 0.25, 0.5, 0.75, 1.0)))
    threshold = draw(st.sampled_from((0.0, 0.25, 0.5, 0.75, 1.0)))
    assessment = LessonAssessment(
        format_valid=draw(st.booleans()),
        source_episode_references_valid=draw(st.booleans()),
        safety_policy_passed=draw(st.booleans()),
        domain_policy_passed=draw(st.booleans()),
        evaluation_score=score,
        evaluation_threshold=threshold,
        evidence_references=(f"assessment-evidence-property-11-{case_id}",),
    )
    return _LessonCase(case_id, assessment, _scope_vector(case_id, draw))


def _service(repositories: DeterministicAdoptionRepositories) -> LessonService:
    """Compose the Lesson service entirely from deterministic repository fakes."""
    return LessonService(
        repositories.lessons,
        repositories.retrievals,
        repositories.episodes,
        repositories.audit,
        clock=lambda: _NOW,
    )


# Feature: adoption-redesign, Property 11: Lesson assessment and retrieval enforce complete scope
# **Validates: Requirements 5.1, 5.2, 5.3**
@settings(max_examples=100, deadline=None)
@given(case=_lesson_cases())
def test_property_11_lesson_assessment_and_retrieval_enforce_complete_scope(
    case: _LessonCase,
) -> None:
    """Only fully assessed Lessons with an exact five-dimensional scope are retrievable."""
    repositories = DeterministicAdoptionRepositories()
    source_episode = _episode(case)
    assert repositories.episodes.append(source_episode).is_success
    service = _service(repositories)

    assessed = service.assess_lesson(_lesson(case), case.assessment)

    assert assessed.is_success and assessed.value is not None
    candidate = assessed.value
    assert (candidate.assessment is LessonAssessmentOutcome.PASSED) is case.assessment.passed
    assert candidate.retrievable is case.assessment.passed
    assert len(repositories.lessons.records()) == 1

    request = LessonRetrievalRequest(
        case.scope.requested_organization_id,
        case.scope.requested_domain_id,
        case.scope.requested_pack_version,
        case.scope.requested_agent_id,
        case.scope.requested_memory_scope,
    )
    retrieved = service.retrieve_lessons(request)

    assert retrieved.is_success and retrieved.value is not None
    expected_retrieval = case.assessment.passed and case.scope.matches_every_dimension
    assert retrieved.value == ((candidate,) if expected_retrieval else ())
