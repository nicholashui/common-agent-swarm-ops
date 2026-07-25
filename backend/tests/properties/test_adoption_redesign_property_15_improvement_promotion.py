"""Property checks for sandboxed Improvement_Proposal promotion governance."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from hypothesis import example, given, settings, strategies as st

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
_LIVE_CHANGE_TARGETS = (
    "prompt",
    "rubric",
    "tool_policy",
    "workflow",
    "risk_tier",
    "tool_authorization",
)


@dataclass(frozen=True, slots=True)
class ImprovementPromotionCase:
    """Bounded evidence, sandbox transition, and reviewer decision inputs."""

    case_id: int
    source_evidence: tuple[str, ...]
    validation_evidence: tuple[str, ...]
    assessment_evidence: tuple[str, ...]
    failure_evidence: tuple[str, ...]
    transition_fails: bool
    reviewer_approved: bool
    designated_reviewer: bool
    reviewer_evidence: tuple[str, ...]
    rollback_reference_present: bool
    promotion_evidence: tuple[str, ...]

    @property
    def rollback_reference(self) -> str | None:
        """Return the generated rollback provenance when it is present."""
        return (
            f"rollback-property-15-{self.case_id}"
            if self.rollback_reference_present
            else None
        )


_REFERENCE_TEXT = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyz0123456789-_",
    min_size=1,
    max_size=12,
)


@st.composite
def _improvement_promotion_cases(draw: st.DrawFn) -> ImprovementPromotionCase:
    """Generate repeated-failure evidence and every governed transition branch."""
    return ImprovementPromotionCase(
        case_id=draw(st.integers(min_value=0, max_value=10_000)),
        source_evidence=tuple(
            draw(st.lists(_REFERENCE_TEXT, min_size=2, max_size=4, unique=True))
        ),
        validation_evidence=tuple(
            draw(st.lists(_REFERENCE_TEXT, min_size=1, max_size=3, unique=True))
        ),
        assessment_evidence=tuple(
            draw(st.lists(_REFERENCE_TEXT, min_size=1, max_size=3, unique=True))
        ),
        failure_evidence=tuple(
            draw(st.lists(_REFERENCE_TEXT, min_size=1, max_size=3, unique=True))
        ),
        transition_fails=draw(st.booleans()),
        reviewer_approved=draw(st.booleans()),
        designated_reviewer=draw(st.booleans()),
        reviewer_evidence=tuple(
            draw(st.lists(_REFERENCE_TEXT, max_size=3, unique=True))
        ),
        rollback_reference_present=draw(st.booleans()),
        promotion_evidence=tuple(
            draw(st.lists(_REFERENCE_TEXT, min_size=1, max_size=3, unique=True))
        ),
    )


def _fakes() -> tuple[EvolutionService, InMemoryEvolutionRepository]:
    """Return isolated evolution repositories with a deterministic clock."""
    repository = InMemoryEvolutionRepository()
    return (
        EvolutionService(
            repository,
            InMemoryEvaluationRepository(),
            clock=lambda: _NOW,
        ),
        repository,
    )


def _proposal_id(case: ImprovementPromotionCase) -> ProposalId:
    """Return the stable proposal identity for one generated case."""
    return ProposalId(f"proposal-property-15-{case.case_id}")


def _create_proposal(
    case: ImprovementPromotionCase,
    service: EvolutionService,
    repository: InMemoryEvolutionRepository,
    organization_id: OrganizationId,
    correlation_id: CorrelationId,
) -> Result[ImprovementProposal, ErrorDetail]:
    """Create a proposal while checking that evidence is retained first."""
    proposal_id = _proposal_id(case)
    callback_observations: list[tuple[int, ProposalSandboxState, tuple[str, ...]]] = []

    def transition_callback(proposal: ImprovementProposal) -> bool:
        """Observe the retained proposal before the sandbox transition runs."""
        history = repository.improvement_proposal_history(organization_id, proposal_id)
        current = repository.get_improvement_proposal(organization_id, proposal_id)
        assert current.is_success and current.value is proposal
        assert len(history) == 1
        assert history[0].source_evidence == case.source_evidence
        assert history[0].evaluation_evidence == case.assessment_evidence
        callback_observations.append(
            (len(history), history[0].sandbox_state, history[0].source_evidence)
        )
        return not case.transition_fails

    result = service.create_improvement_proposal(
        organization_id,
        correlation_id,
        source_version_reference="agent-v1",
        immutable_difference={"prompt": {"change": f"sandbox-{case.case_id}"}},
        source_learning_episode_references=case.source_evidence,
        validation_evidence_references=case.validation_evidence,
        assessment_evidence_references=case.assessment_evidence,
        impact_summary="Improve repeated failure handling in a governed sandbox.",
        proposal_id=proposal_id,
        sandbox_transition=transition_callback,
        transition_failure_evidence=case.failure_evidence,
    )
    assert callback_observations == [
        (1, ProposalSandboxState.SANDBOX, case.source_evidence)
    ]
    return result


# Feature: adoption-redesign, Property 15: Improvement remains sandboxed until governed promotion
# **Validates: Requirements 5.10, 5.11, 5.12, 5.14, 7.3**
@settings(max_examples=100, deadline=None)
@example(
    case=ImprovementPromotionCase(
        case_id=0,
        source_evidence=("episode-failure-1", "episode-failure-2"),
        validation_evidence=("validation-1",),
        assessment_evidence=("assessment-1",),
        failure_evidence=("sandbox-timeout",),
        transition_fails=True,
        reviewer_approved=True,
        designated_reviewer=True,
        reviewer_evidence=("review-1",),
        rollback_reference_present=True,
        promotion_evidence=("promotion-1",),
    )
)
@example(
    case=ImprovementPromotionCase(
        case_id=1,
        source_evidence=("episode-failure-1", "episode-failure-2"),
        validation_evidence=("validation-1",),
        assessment_evidence=("assessment-1",),
        failure_evidence=("sandbox-failure",),
        transition_fails=False,
        reviewer_approved=True,
        designated_reviewer=True,
        reviewer_evidence=("review-1",),
        rollback_reference_present=True,
        promotion_evidence=("promotion-1",),
    )
)
@given(case=_improvement_promotion_cases())
def test_property_15_improvement_remains_sandboxed_until_governed_promotion(
    case: ImprovementPromotionCase,
) -> None:
    """Live behavior changes require retained evidence and designated approval."""
    service, repository = _fakes()
    organization_id = OrganizationId(f"organization-property-15-{case.case_id}")
    correlation_id = CorrelationId(f"correlation-property-15-{case.case_id}")
    proposal_id = _proposal_id(case)

    created = _create_proposal(
        case, service, repository, organization_id, correlation_id
    )
    current = repository.get_improvement_proposal(organization_id, proposal_id)
    assert current.is_success and current.value is not None
    proposal = current.value
    assert proposal.source_evidence == case.source_evidence
    assert proposal.validation_evidence == case.validation_evidence
    assert proposal.evaluation_evidence == case.assessment_evidence
    assert proposal.promotion_state is ProposalPromotionState.NOT_APPROVED

    for target in _LIVE_CHANGE_TARGETS:
        denied = service.authorize_live_change(
            organization_id, correlation_id, proposal_id, target
        )
        assert not denied.is_success
        assert denied.error is not None
        assert denied.error.code is ErrorCode.AUTHORIZATION_DENIED

    if case.transition_fails:
        assert not created.is_success
        assert proposal.sandbox_state is ProposalSandboxState.TRANSITION_FAILED
        assert proposal.state_transition_failure_evidence == case.failure_evidence
        history = repository.improvement_proposal_history(organization_id, proposal_id)
        assert tuple(record.sandbox_state for record in history) == (
            ProposalSandboxState.SANDBOX,
            ProposalSandboxState.TRANSITION_FAILED,
        )
        assert repository.promotion_audits(organization_id) == ()
        return

    assert created.is_success
    assert proposal.sandbox_state is ProposalSandboxState.SANDBOX
    assert proposal.state_transition_failure_evidence == ()
    assert repository.improvement_proposal_history(organization_id, proposal_id) == (
        proposal,
    )

    rollback_reference = case.rollback_reference
    decision = service.record_reviewer_decision(
        organization_id,
        ActorId(f"reviewer-property-15-{case.case_id}"),
        correlation_id,
        proposal_id,
        approved=case.reviewer_approved,
        evidence_references=case.reviewer_evidence,
        rollback_reference=rollback_reference,
        designated_reviewer=case.designated_reviewer,
    )
    approval_succeeds = (
        case.designated_reviewer
        and bool(case.reviewer_evidence)
        and (not case.reviewer_approved or rollback_reference is not None)
    )

    if not approval_succeeds:
        assert not decision.is_success
        promoted = service.promote_improvement_proposal(
            organization_id,
            correlation_id,
            proposal_id,
            replaced_version_reference="agent-v1",
            promoted_version_reference="agent-v2",
            rollback_reference=rollback_reference or "rollback-property-15-missing",
            evidence_references=case.promotion_evidence,
            live_change_target="prompt",
        )
        assert not promoted.is_success
        assert repository.promotion_audits(organization_id) == ()
        return

    assert decision.is_success and decision.value is not None
    decided = decision.value
    assert decided.reviewer_id == f"reviewer-property-15-{case.case_id}"
    assert decided.decision_timestamp == _NOW
    assert decided.decision_evidence_references == case.reviewer_evidence

    if not case.reviewer_approved:
        assert decided.promotion_state is ProposalPromotionState.NOT_APPROVED
        promoted = service.promote_improvement_proposal(
            organization_id,
            correlation_id,
            proposal_id,
            replaced_version_reference="agent-v1",
            promoted_version_reference="agent-v2",
            rollback_reference=rollback_reference or "rollback-property-15-missing",
            evidence_references=case.promotion_evidence,
        )
        assert not promoted.is_success
        assert repository.promotion_audits(organization_id) == ()
        return

    assert decided.promotion_state is ProposalPromotionState.APPROVED
    assert decided.rollback_reference == rollback_reference
    for target in _LIVE_CHANGE_TARGETS:
        authorized = service.authorize_live_change(
            organization_id, correlation_id, proposal_id, target
        )
        assert authorized.is_success and authorized.value is True

    promoted = service.promote_improvement_proposal(
        organization_id,
        correlation_id,
        proposal_id,
        replaced_version_reference="agent-v1",
        promoted_version_reference="agent-v2",
        rollback_reference=rollback_reference or "rollback-property-15-missing",
        evidence_references=case.promotion_evidence,
        live_change_target="prompt",
    )
    assert promoted.is_success and promoted.value is not None
    promoted_proposal = promoted.value
    assert promoted_proposal.promotion_state is ProposalPromotionState.PROMOTED
    assert promoted_proposal.replaced_version_reference == "agent-v1"
    assert promoted_proposal.promoted_version_reference == "agent-v2"
    assert promoted_proposal.rollback_reference == rollback_reference

    history = repository.improvement_proposal_history(organization_id, proposal_id)
    assert tuple(record.sandbox_state for record in history) == (
        ProposalSandboxState.SANDBOX,
        ProposalSandboxState.SANDBOX,
        ProposalSandboxState.SANDBOX,
    )
    audits = repository.promotion_audits(organization_id)
    assert len(audits) == 1
    audit = audits[0]
    assert audit.action == "improvement.promotion"
    assert audit.outcome == "promoted"
    assert audit.actor_id == ActorId(f"reviewer-property-15-{case.case_id}")
    assert {
        str(proposal_id),
        "agent-v1",
        "agent-v2",
        rollback_reference,
        *case.source_evidence,
        *case.validation_evidence,
        *case.assessment_evidence,
        *case.reviewer_evidence,
        *case.promotion_evidence,
    }.issubset(audit.source_references)
