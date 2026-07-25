"""Deterministic tests for sandboxed Improvement_Proposal governance."""

from __future__ import annotations

from datetime import UTC, datetime

from app.evolution.service import EvolutionService
from app.models.contracts import ErrorCode, ErrorDetail, Result
from app.models.control_plane import (
    ImprovementProposal,
    ProposalId,
    ProposalPromotionState,
    ProposalSandboxState,
)
from app.models.identifiers import ActorId, CorrelationId, OrganizationId
from app.repositories.evaluation_repository import InMemoryEvaluationRepository
from app.repositories.evolution_repository import InMemoryEvolutionRepository

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_ORGANIZATION = OrganizationId("improvement-organization")
_CORRELATION = CorrelationId("improvement-correlation")


def _service() -> tuple[EvolutionService, InMemoryEvolutionRepository]:
    repository = InMemoryEvolutionRepository()
    return (
        EvolutionService(
            repository,
            InMemoryEvaluationRepository(),
            clock=lambda: _NOW,
        ),
        repository,
    )


def _create(
    service: EvolutionService, proposal_id: str = "proposal-1"
) -> Result[ImprovementProposal, ErrorDetail]:
    return service.create_improvement_proposal(
        _ORGANIZATION,
        _CORRELATION,
        source_version_reference="agent-v1",
        immutable_difference={"rubric": {"minimum": 0.9}},
        source_learning_episode_references=("episode-1",),
        validation_evidence_references=("validation-1",),
        assessment_evidence_references=("evaluation-1",),
        impact_summary="Improve repeated failure handling.",
        proposal_id=ProposalId(proposal_id),
    )


def test_proposal_evidence_is_retained_before_failed_sandbox_transition() -> None:
    service, repository = _service()

    result = service.create_improvement_proposal(
        _ORGANIZATION,
        _CORRELATION,
        source_version_reference="agent-v1",
        immutable_difference={"prompt": {"change": "sandbox-only"}},
        source_learning_episode_references=("episode-1",),
        validation_evidence_references=("validation-1",),
        assessment_evidence_references=("evaluation-1",),
        impact_summary="Retain failed transition evidence.",
        proposal_id=ProposalId("failed-proposal"),
        sandbox_transition=lambda _proposal: False,
        transition_failure_evidence=("sandbox-error-1",),
    )

    assert not result.is_success
    current = repository.get_improvement_proposal(_ORGANIZATION, ProposalId("failed-proposal"))
    assert current.is_success and current.value is not None
    assert current.value.sandbox_state is ProposalSandboxState.TRANSITION_FAILED
    assert current.value.source_evidence == ("episode-1",)
    assert current.value.state_transition_failure_evidence == ("sandbox-error-1",)
    history = repository.improvement_proposal_history(_ORGANIZATION, ProposalId("failed-proposal"))
    assert [record.sandbox_state for record in history] == [
        ProposalSandboxState.SANDBOX,
        ProposalSandboxState.TRANSITION_FAILED,
    ]


def test_live_targets_require_designated_approval_and_promotion_is_audited() -> None:
    service, repository = _service()
    created = _create(service)
    assert created.is_success and created.value is not None

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

    unauthorized = service.record_reviewer_decision(
        _ORGANIZATION,
        ActorId("not-designated"),
        _CORRELATION,
        ProposalId("proposal-1"),
        approved=True,
        evidence_references=("review-1",),
        rollback_reference="rollback-v1",
        designated_reviewer=False,
    )
    assert not unauthorized.is_success

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
    assert approved.value.promotion_state is ProposalPromotionState.APPROVED
    assert approved.value.reviewer_id == "designated-reviewer"
    assert approved.value.decision_timestamp == _NOW
    assert approved.value.decision_evidence_references == ("review-1",)

    promoted = service.promote_improvement_proposal(
        _ORGANIZATION,
        _CORRELATION,
        ProposalId("proposal-1"),
        replaced_version_reference="agent-v1",
        promoted_version_reference="agent-v2",
        rollback_reference="rollback-v1",
        evidence_references=("promotion-evaluation-1",),
        live_change_target="rubric",
    )

    assert promoted.is_success and promoted.value is not None
    assert promoted.value.promotion_state is ProposalPromotionState.PROMOTED
    assert promoted.value.replaced_version_reference == "agent-v1"
    assert promoted.value.promoted_version_reference == "agent-v2"
    assert promoted.value.rollback_reference == "rollback-v1"
    audits = repository.promotion_audits(_ORGANIZATION)
    assert len(audits) == 1
    assert audits[0].action == "improvement.promotion"
    assert audits[0].outcome == "promoted"
    assert audits[0].actor_id == ActorId("designated-reviewer")
    assert {
        "agent-v1",
        "agent-v2",
        "rollback-v1",
        "review-1",
        "promotion-evaluation-1",
    }.issubset(audits[0].source_references)
