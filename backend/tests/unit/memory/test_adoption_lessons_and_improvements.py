"""Deterministic tests for Lesson revocation and Improvement_Proposal governance."""

from __future__ import annotations

from datetime import UTC, datetime

from app.evolution.service import EvolutionService
from app.memory.lesson_service import LessonAssessment, LessonService
from app.models.common import CompatibilityRange, RecordMetadata
from app.models.contracts import ErrorCode
from app.models.control_plane import (
    AgentNodeAttemptId,
    AuditRecord,
    LearningEpisodeId,
    ProposalId,
    ProposalPromotionState,
)
from app.models.evidence import (
    LearningEpisode,
    LearningTerminalOutcome,
    Lesson,
    LessonAssessmentOutcome,
)
from app.models.identifiers import (
    ActorId,
    AgentId,
    CorrelationId,
    DomainId,
    OrganizationId,
    RecordId,
)
from app.repositories.evaluation_repository import InMemoryEvaluationRepository
from app.repositories.evolution_repository import InMemoryEvolutionRepository
from tests.fakes.adoption import DeterministicAdoptionRepositories, FakeFailurePlan

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_ORGANIZATION = OrganizationId("organization-lessons-improvements")
_DOMAIN = DomainId("domain-lessons-improvements")
_AGENT = AgentId("agent-lessons-improvements")
_CORRELATION = CorrelationId("correlation-lessons-improvements")


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


def _episode() -> LearningEpisode:
    return LearningEpisode(
        metadata=_metadata("episode-record-1"),
        episode_id=LearningEpisodeId("episode-1"),
        attempt_id=AgentNodeAttemptId("attempt-1"),
        organization_id=_ORGANIZATION,
        domain_id=_DOMAIN,
        pack_version="1.0.0",
        agent_id=_AGENT,
        terminal_outcome=LearningTerminalOutcome.COMPLETED,
        outcome_reference="outcome:episode-1",
        recorded_at=_NOW,
    )


def _lesson() -> Lesson:
    return Lesson(
        metadata=_metadata("lesson-record-1"),
        lesson_id="lesson-1",  # type: ignore[arg-type]
        organization_id=_ORGANIZATION,
        domain_id=_DOMAIN,
        pack_version_range=CompatibilityRange.exact("1.0.0"),
        agent_id=_AGENT,
        memory_scope="agent:agent-lessons-improvements",
        assessment=LessonAssessmentOutcome.FAILED,
        source_episode_references=("episode-1",),
        content_reference="content:lesson-1",
        assessed_at=_NOW,
    )


def _lesson_service(repositories: DeterministicAdoptionRepositories) -> LessonService:
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
        evidence_references=("assessment:lesson-1",),
    )


def _evolution_service() -> tuple[EvolutionService, InMemoryEvolutionRepository]:
    repository = InMemoryEvolutionRepository()
    return (
        EvolutionService(
            repository,
            InMemoryEvaluationRepository(),
            clock=lambda: _NOW,
        ),
        repository,
    )


def _create_proposal(service: EvolutionService) -> None:
    created = service.create_improvement_proposal(
        _ORGANIZATION,
        _CORRELATION,
        source_version_reference="agent-v1",
        immutable_difference={"rubric": {"minimum": 0.9}},
        source_learning_episode_references=("episode-1",),
        validation_evidence_references=("validation-1",),
        assessment_evidence_references=("assessment-1",),
        impact_summary="Improve repeated failure handling.",
        proposal_id=ProposalId("proposal-1"),
    )
    assert created.is_success and created.value is not None


def test_revocation_audit_contains_required_payload_and_gates_retrieval() -> None:
    failure_plan = FakeFailurePlan()
    repositories = DeterministicAdoptionRepositories(failure_plan)
    assert repositories.episodes.append(_episode()).is_success
    service = _lesson_service(repositories)
    assessed = service.assess_lesson(_lesson(), _passed_assessment())
    assert assessed.is_success and assessed.value is not None

    failure_plan.fail_next_audit()
    audit_pending = service.revoke_lesson(
        assessed.value,
        "source evidence was superseded",
        ActorId("reviewer-lessons"),
        ("episode-1", "source:lesson-1"),
    )
    assert not audit_pending.is_success
    retained = service.retrieve_lessons(
        _ORGANIZATION,
        _DOMAIN,
        "1.0.0",
        _AGENT,
        "agent:agent-lessons-improvements",
    )
    assert retained.is_success and retained.value == (assessed.value,)
    assert repositories.audit.records == ()

    revoked = service.revoke_lesson(
        assessed.value,
        "source evidence was superseded",
        ActorId("reviewer-lessons"),
        ("episode-1", "source:lesson-1"),
    )
    assert revoked.is_success and revoked.value is not None and revoked.value.revoked
    assert not revoked.value.retrievable

    audit = repositories.audit.records[-1]
    assert isinstance(audit, AuditRecord)
    assert audit.action == "lesson.revocation"
    assert audit.subject_reference == "lesson-1"
    assert audit.outcome == "revocation_committed"
    assert audit.actor_id == ActorId("reviewer-lessons")
    assert audit.actor == ActorId("reviewer-lessons")
    assert audit.reason == "source evidence was superseded"
    assert audit.revocation_reason == "source evidence was superseded"
    assert audit.recorded_at == _NOW
    assert audit.timestamp == _NOW
    assert audit.source_references == ("episode-1", "source:lesson-1")
    assert audit.source_episode_references == ("episode-1", "source:lesson-1")

    excluded = service.retrieve_lessons(
        _ORGANIZATION,
        _DOMAIN,
        "1.0.0",
        _AGENT,
        "agent:agent-lessons-improvements",
    )
    assert excluded.is_success and excluded.value == ()


def test_unapproved_improvement_proposal_denies_every_live_change_target() -> None:
    service, _repository = _evolution_service()
    _create_proposal(service)
    targets = (
        "prompt",
        "rubric",
        "tool_policy",
        "workflow",
        "risk_tier",
        "tool_authorization",
    )

    for target in targets:
        denied = service.authorize_live_change(
            _ORGANIZATION,
            _CORRELATION,
            ProposalId("proposal-1"),
            target,
        )
        assert not denied.is_success
        assert denied.error is not None
        assert denied.error.code is ErrorCode.AUTHORIZATION_DENIED


def test_designated_reviewer_decision_retains_identity_timestamp_evidence_and_rollback() -> None:
    service, repository = _evolution_service()
    _create_proposal(service)

    not_designated = service.record_reviewer_decision(
        _ORGANIZATION,
        ActorId("not-designated"),
        _CORRELATION,
        ProposalId("proposal-1"),
        approved=True,
        evidence_references=("review-1",),
        rollback_reference="rollback-v1",
        designated_reviewer=False,
    )
    assert not not_designated.is_success
    assert not_designated.error is not None
    assert not_designated.error.code is ErrorCode.AUTHORIZATION_DENIED

    approved = service.record_reviewer_decision(
        _ORGANIZATION,
        ActorId("designated-reviewer"),
        _CORRELATION,
        ProposalId("proposal-1"),
        approved=True,
        evidence_references=("review-1",),
        rollback_reference="rollback-v1",
    )
    assert approved.is_success and approved.value is not None
    proposal = approved.value
    assert proposal.promotion_state is ProposalPromotionState.APPROVED
    assert proposal.reviewer_identity == "designated-reviewer"
    assert proposal.reviewer_id == "designated-reviewer"
    assert proposal.reviewer_decision_timestamp == _NOW
    assert proposal.decision_timestamp == _NOW
    assert proposal.reviewer_evidence_references == ("review-1",)
    assert proposal.decision_evidence_references == ("review-1",)
    assert proposal.rollback_reference == "rollback-v1"
    assert proposal.rollback_evidence == ("rollback-v1",)
    assert (
        repository.improvement_proposal_history(_ORGANIZATION, ProposalId("proposal-1"))[-1]
        == proposal
    )


def test_approved_promotion_records_immutable_versions_and_rollback_audit() -> None:
    service, repository = _evolution_service()
    _create_proposal(service)
    approved = service.record_reviewer_decision(
        _ORGANIZATION,
        ActorId("designated-reviewer"),
        _CORRELATION,
        ProposalId("proposal-1"),
        approved=True,
        evidence_references=("review-1",),
        rollback_reference="rollback-v1",
    )
    assert approved.is_success

    promoted = service.promote_improvement_proposal(
        _ORGANIZATION,
        _CORRELATION,
        ProposalId("proposal-1"),
        replaced_version_reference="agent-v1",
        promoted_version_reference="agent-v2",
        rollback_reference="rollback-v1",
        evidence_references=("promotion-assessment-1",),
        live_change_target="rubric",
    )
    assert promoted.is_success and promoted.value is not None
    assert promoted.value.promotion_state is ProposalPromotionState.PROMOTED
    assert promoted.value.replaced_version_reference == "agent-v1"
    assert promoted.value.promoted_version_reference == "agent-v2"
    assert promoted.value.rollback_reference == "rollback-v1"

    audits = repository.promotion_audits(_ORGANIZATION)
    assert len(audits) == 1
    audit = audits[0]
    assert audit.action == "improvement.promotion"
    assert audit.subject_reference == "proposal-1"
    assert audit.outcome == "promoted"
    assert audit.actor_id == ActorId("designated-reviewer")
    assert {
        "agent-v1",
        "agent-v2",
        "rollback-v1",
    }.issubset(audit.source_references)
