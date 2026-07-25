"""Property checks for audit-gated Lesson revocation."""

from __future__ import annotations

# The required property label is intentionally kept in its exact documented form below.
# ruff: noqa: E501
from dataclasses import dataclass
from datetime import UTC, datetime

from hypothesis import given, settings, strategies as st

from app.memory.lesson_service import LessonAssessment, LessonRetrievalRequest, LessonService
from app.models.common import SCHEMA_VERSION, CompatibilityRange, RecordMetadata
from app.models.control_plane import LessonId
from app.models.evidence import Lesson, LessonAssessmentOutcome
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


@dataclass(frozen=True, slots=True)
class _RevocationCase:
    """Bounded revocation audit persistence outcome."""

    case_id: int
    audit_commits: bool


@st.composite
def _revocation_cases(draw: st.DrawFn) -> _RevocationCase:
    """Generate deterministic Lesson identities and audit persistence outcomes."""
    return _RevocationCase(
        case_id=draw(st.integers(min_value=0, max_value=10_000)),
        audit_commits=draw(st.booleans()),
    )


def _metadata(case: _RevocationCase, organization_id: OrganizationId) -> RecordMetadata:
    """Build deterministic trace metadata for the generated Lesson."""
    return RecordMetadata(
        record_id=RecordId(f"lesson-record-property-12-{case.case_id}"),
        organization_id=organization_id,
        correlation_id=CorrelationId(f"correlation-property-12-{case.case_id}"),
        schema_version=SCHEMA_VERSION,
        version=1,
        created_at=_NOW,
        updated_at=_NOW,
    )


def _lesson(case: _RevocationCase) -> Lesson:
    """Build an assessed candidate with the scope used by its retrieval request."""
    organization_id = OrganizationId(f"organization-property-12-{case.case_id}")
    return Lesson(
        metadata=_metadata(case, organization_id),
        lesson_id=LessonId(f"lesson-property-12-{case.case_id}"),
        organization_id=organization_id,
        domain_id=DomainId(f"domain-property-12-{case.case_id}"),
        pack_version_range=CompatibilityRange.exact("1.0.0"),
        agent_id=AgentId(f"agent-property-12-{case.case_id}"),
        memory_scope=f"agent:{case.case_id}:memory",
        assessment=LessonAssessmentOutcome.FAILED,
        source_episode_references=(f"source-property-12-{case.case_id}",),
        content_reference=f"content-reference-property-12-{case.case_id}",
        assessed_at=_NOW,
    )


def _service(
    repositories: DeterministicAdoptionRepositories,
) -> LessonService:
    """Compose the Lesson service from deterministic repositories only."""
    return LessonService(
        repositories.lessons,
        repositories.retrievals,
        episode_repository=None,
        audit_repository=repositories.audit,
        clock=lambda: _NOW,
    )


def _request(lesson: Lesson) -> LessonRetrievalRequest:
    """Build the exact approved retrieval scope for the generated Lesson."""
    return LessonRetrievalRequest(
        lesson.organization_id,
        lesson.domain_id,
        "1.0.0",
        lesson.agent_id,
        lesson.memory_scope,
    )


# Feature: adoption-redesign, Property 12: Revocation changes retrieval only after auditable commitment
# **Validates: Requirements 5.5, 5.6**
@settings(max_examples=100, deadline=None)
@given(case=_revocation_cases())
def test_property_12_lesson_revocation_changes_retrieval_only_after_auditable_commitment(
    case: _RevocationCase,
) -> None:
    """A Lesson leaves retrieval unchanged on audit failure and is excluded after commit."""
    failure_plan = FakeFailurePlan(fail_audit=not case.audit_commits)
    repositories = DeterministicAdoptionRepositories(failure_plan)
    service = _service(repositories)
    candidate = _lesson(case)
    assessment = LessonAssessment(
        format_valid=True,
        source_episode_references_valid=True,
        safety_policy_passed=True,
        domain_policy_passed=True,
        evaluation_score=1.0,
        evaluation_threshold=1.0,
        evidence_references=(f"assessment-property-12-{case.case_id}",),
    )

    assessed = service.assess_lesson(candidate, assessment)
    assert assessed.is_success and assessed.value is not None
    retrievable_lesson = assessed.value
    request = _request(retrievable_lesson)
    before_revocation = service.retrieve_lessons(request)
    assert before_revocation.is_success and before_revocation.value == (retrievable_lesson,)

    revocation = service.revoke_lesson(
        retrievable_lesson,
        reason=f"revocation-reason-property-12-{case.case_id}",
        actor_id=ActorId(f"actor-property-12-{case.case_id}"),
        source_references=(f"revocation-source-property-12-{case.case_id}",),
    )
    after_revocation = service.retrieve_lessons(request)
    assert after_revocation.is_success and after_revocation.value is not None

    if case.audit_commits:
        assert revocation.is_success and revocation.value is not None
        assert len(repositories.audit.records) == 1
        assert repositories.audit.records[0].action == "lesson.revocation"
        assert repositories.audit.records[0].subject_reference == str(retrievable_lesson.lesson_id)
        assert after_revocation.value == ()
        revoked_lesson = repositories.lessons.records()[0]
        assert revoked_lesson.revoked
        assert not revoked_lesson.retrievable
        return

    assert not revocation.is_success
    assert repositories.audit.records == ()
    assert after_revocation.value == (retrievable_lesson,)
    persisted_lesson = repositories.lessons.records()[0]
    assert not persisted_lesson.revoked
    assert persisted_lesson.retrievable
