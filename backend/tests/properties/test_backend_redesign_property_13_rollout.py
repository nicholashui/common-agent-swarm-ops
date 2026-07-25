"""Property checks for evidence-bound proposal and rollout progression."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import UTC, datetime
from typing import cast

from hypothesis import given, settings, strategies as st

from app.core.command_service import CommandService
from app.evolution.rollout_service import ProposalService, RolloutService
from app.models.common import RecordMetadata
from app.models.contracts import ErrorCode
from app.models.control_plane import (
    AgentVersionId,
    ApprovalGate,
    ApprovalGateId,
    ApprovalGateStatus,
    CommonAgentVersion,
    ContractStatus,
    ImprovementProposal,
    ProposalId,
    QualityEvidence,
    QualityEvidenceKind,
    RolloutCampaign,
    RolloutCampaignId,
    RolloutCampaignStatus,
)
from app.models.identifiers import CorrelationId, OrganizationId, RecordId
from app.repositories.control_plane import ControlPlaneUnitOfWork, InMemoryControlPlaneDatabase

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_ORGANIZATION = OrganizationId("property-13-organization")
_CORRELATION = CorrelationId("property-13-correlation")
_SAFE_VALUES = st.text(alphabet="abcdefghijklmnopqrstuvwxyz0123456789", min_size=1, max_size=12)
_PROPOSAL_EVIDENCE_SETS = st.fixed_dictionaries(
    {
        "validation_evidence": st.booleans(),
        "evaluation_evidence": st.booleans(),
        "approval_evidence": st.booleans(),
        "rollback_evidence": st.booleans(),
    }
)
_START_EVIDENCE_STATES = st.tuples(st.booleans(), st.booleans())
_CRITERION_OUTCOMES = st.lists(st.booleans(), min_size=1, max_size=3)


def _metadata(record_id: str, *, version: int = 1) -> RecordMetadata:
    return RecordMetadata(
        record_id=RecordId(record_id),
        organization_id=_ORGANIZATION,
        correlation_id=_CORRELATION,
        schema_version=1,
        version=version,
        created_at=_NOW,
        updated_at=_NOW,
    )


def _unit_of_work_factory(
    database: InMemoryControlPlaneDatabase,
) -> Callable[[], ControlPlaneUnitOfWork]:
    def factory() -> ControlPlaneUnitOfWork:
        return cast(ControlPlaneUnitOfWork, database.unit_of_work())

    return factory


def _services(database: InMemoryControlPlaneDatabase) -> tuple[ProposalService, RolloutService]:
    command_service = CommandService(
        _unit_of_work_factory(database),
        clock=lambda: _NOW,
        next_event_sequence=iter(range(1, 100)).__next__,
    )
    return ProposalService(_unit_of_work_factory(database)), RolloutService(
        _unit_of_work_factory(database), command_service, clock=lambda: _NOW
    )


def _published_agent(value: str) -> CommonAgentVersion:
    return CommonAgentVersion(
        metadata=_metadata(f"agent-record-{value}"),
        agent_version_id=AgentVersionId(f"agent-published-{value}"),
        status=ContractStatus.PUBLISHED,
        canonical_identity=f"operations.planner.{value}",
        category="planning",
        responsibilities=("plan",),
        boundaries=("no-production",),
        escalation_targets=("operator",),
        approval_authority=("release-approval",),
        runtime_policy={"max_retries": 2},
        tool_policy={"allow": ("knowledge.lookup",)},
        quality_rubric={"minimum": 0.8},
        critique_relationships=("reviewer",),
        knowledge_bindings=("operations-knowledge",),
        input_schema={"type": "object"},
        output_schema={"type": "object"},
        provenance_policy={"retain": True},
        content_digest=f"sha256:agent-published-{value}",
    )


def _proposal(value: str, evidence_set: Mapping[str, bool]) -> ImprovementProposal:
    return ImprovementProposal(
        metadata=_metadata(f"proposal-record-{value}"),
        proposal_id=ProposalId(f"proposal-{value}"),
        source_version_reference=f"agent-published-{value}",
        immutable_difference={"runtime": {"candidate": value, "max_retries": 3}},
        source_evidence=(f"source-evidence-{value}",),
        validation_evidence=(f"validation-evidence-{value}",)
        if evidence_set["validation_evidence"]
        else (),
        evaluation_evidence=(f"evaluation-evidence-{value}",)
        if evidence_set["evaluation_evidence"]
        else (),
        reviewer_decisions=(f"reviewer-decision-{value}",),
        approval_evidence=(f"approval-evidence-{value}",)
        if evidence_set["approval_evidence"]
        else (),
        rollback_evidence=(f"rollback-evidence-{value}",)
        if evidence_set["rollback_evidence"]
        else (),
        impact_summary=f"Controlled rollout change {value}.",
    )


def _campaign(value: str, suffix: str, criteria: tuple[str, ...]) -> RolloutCampaign:
    campaign_id = f"campaign-{suffix}-{value}"
    return RolloutCampaign(
        metadata=_metadata(f"{campaign_id}-record"),
        campaign_id=RolloutCampaignId(campaign_id),
        proposal_id=ProposalId(f"proposal-{value}"),
        selected_version_reference=f"agent-selected-{value}",
        target_scope=(f"tenant-{value}",),
        evaluation_evidence_references=(f"evaluation-{campaign_id}",),
        required_approval_references=(f"approval-{campaign_id}",),
        success_criteria={criterion: "must-pass" for criterion in criteria},
        rollback_reference=f"rollback-plan-{campaign_id}",
        status=RolloutCampaignStatus.PENDING,
        measured_outcomes={},
    )


def _seed_start_evidence(
    database: InMemoryControlPlaneDatabase,
    campaign: RolloutCampaign,
    *,
    evaluation_passed: bool,
    approval_approved: bool,
) -> None:
    evaluation_id = campaign.evaluation_evidence_references[0]
    approval_id = campaign.required_approval_references[0]
    with database.unit_of_work() as unit_of_work:
        assert unit_of_work.evidence.append_quality(
            QualityEvidence(
                metadata=_metadata(f"evaluation-record-{campaign.campaign_id}"),
                evidence_id=evaluation_id,
                kind=QualityEvidenceKind.GATE,
                subject_reference=f"proposal:{campaign.proposal_id}",
                passed=evaluation_passed,
                evidence_reference=f"evaluation-artifact-{campaign.campaign_id}",
                recorded_at=_NOW,
            )
        ).is_success
        assert unit_of_work.evidence.append_approval(
            ApprovalGate(
                metadata=_metadata(f"approval-record-{campaign.campaign_id}"),
                approval_gate_id=ApprovalGateId(approval_id),
                pending_operation_reference=f"rollout:{campaign.campaign_id}",
                status=(
                    ApprovalGateStatus.APPROVED if approval_approved else ApprovalGateStatus.PENDING
                ),
                decision="approve" if approval_approved else None,
                decision_reason="evidence reviewed" if approval_approved else None,
                reviewer_reference="release-owner" if approval_approved else None,
            )
        ).is_success


def _missing_start_conditions(
    campaign: RolloutCampaign, start_evidence: tuple[bool, bool]
) -> set[str]:
    evaluation_passed, approval_approved = start_evidence
    missing: set[str] = set()
    if not evaluation_passed:
        missing.add(f"evaluation_evidence:{campaign.evaluation_evidence_references[0]}")
    if not approval_approved:
        missing.add(f"approval_evidence:{campaign.required_approval_references[0]}")
    return missing


# Feature: backend-redesign, Property 13
# **Validates: Requirements 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7**
@settings(max_examples=100)
@given(
    value=_SAFE_VALUES,
    proposal_evidence=_PROPOSAL_EVIDENCE_SETS,
    primary_start_evidence=_START_EVIDENCE_STATES,
    criterion_outcomes=_CRITERION_OUTCOMES,
    peer_start_evidence=_START_EVIDENCE_STATES,
)
def test_property_13_proposal_and_rollout_progression_is_evidence_bound(
    value: str,
    proposal_evidence: dict[str, bool],
    primary_start_evidence: tuple[bool, bool],
    criterion_outcomes: list[bool],
    peer_start_evidence: tuple[bool, bool],
) -> None:
    """Only retained complete evidence permits rollout; failure is terminal pending rollback."""
    database = InMemoryControlPlaneDatabase()
    proposal_service, rollout_service = _services(database)
    source = _published_agent(value)
    proposal = _proposal(value, proposal_evidence)
    with database.unit_of_work() as unit_of_work:
        assert unit_of_work.common_contracts.append_agent_version(source).is_success

    proposal_result = proposal_service.create_proposal(_ORGANIZATION, proposal)
    assert proposal_result.is_success and proposal_result.value == proposal
    assert database._state.proposals[proposal.proposal_id] == proposal
    assert database._state.agent_versions[source.agent_version_id] == source
    assert proposal.immutable_difference == {"runtime": {"candidate": value, "max_retries": 3}}
    assert proposal.source_evidence and proposal.reviewer_decisions

    expected_missing_evidence = tuple(
        name for name, present in proposal_evidence.items() if not present
    )
    readiness = ProposalService.readiness(proposal)
    assert readiness.missing_evidence == expected_missing_evidence
    assert readiness.production_eligible is (not expected_missing_evidence)

    first_failure_index = next(
        (index for index, passed in enumerate(criterion_outcomes) if not passed), None
    )
    criteria = tuple(f"criterion-{index}" for index in range(len(criterion_outcomes)))
    if first_failure_index is not None:
        criteria += ("criterion-after-failure",)
    primary_campaign = _campaign(value, "primary", criteria)
    created_campaign = rollout_service.create_campaign(_ORGANIZATION, primary_campaign)

    if expected_missing_evidence:
        assert not created_campaign.is_success and created_campaign.error is not None
        assert created_campaign.error.code is ErrorCode.VALIDATION_FAILED
        assert {field.name for field in created_campaign.error.fields} == set(
            expected_missing_evidence
        )
        assert database._state.rollouts == {}
        return

    assert created_campaign.is_success and created_campaign.value is not None
    stored_campaign = database._state.rollouts[primary_campaign.campaign_id]
    assert stored_campaign.selected_version_reference == primary_campaign.selected_version_reference
    assert stored_campaign.target_scope == primary_campaign.target_scope
    assert (
        stored_campaign.required_approval_references
        == primary_campaign.required_approval_references
    )
    assert stored_campaign.success_criteria == primary_campaign.success_criteria
    assert stored_campaign.rollback_reference == primary_campaign.rollback_reference
    assert stored_campaign.status is RolloutCampaignStatus.PENDING
    assert stored_campaign.measured_outcomes == {
        criterion: {"status": "pending"} for criterion in criteria
    }

    _seed_start_evidence(
        database,
        primary_campaign,
        evaluation_passed=primary_start_evidence[0],
        approval_approved=primary_start_evidence[1],
    )
    started = rollout_service.start_campaign(
        _ORGANIZATION,
        _CORRELATION,
        primary_campaign.campaign_id,
        idempotency_key=f"start-{primary_campaign.campaign_id}",
    )
    primary_missing_start_conditions = _missing_start_conditions(
        primary_campaign, primary_start_evidence
    )
    if primary_missing_start_conditions:
        assert not started.is_success and started.error is not None
        assert started.error.code is ErrorCode.VALIDATION_FAILED
        assert {field.name for field in started.error.fields} == primary_missing_start_conditions
        assert (
            database._state.rollouts[primary_campaign.campaign_id].status
            is RolloutCampaignStatus.PENDING
        )
        assert database._state.work_items == {}
        return

    assert started.is_success and started.value is not None
    assert started.value.campaign.status is RolloutCampaignStatus.RUNNING
    assert [work.subject_reference for work in database._state.work_items.values()] == [
        f"rollout:{primary_campaign.campaign_id}"
    ]

    for index, passed in enumerate(criterion_outcomes):
        criterion = f"criterion-{index}"
        outcome = rollout_service.record_criterion_outcome(
            _ORGANIZATION,
            _CORRELATION,
            primary_campaign.campaign_id,
            criterion,
            passed=passed,
            evidence_reference=f"criterion-evidence-{value}-{index}",
        )
        assert outcome.is_success and outcome.value is not None
        if not passed:
            assert first_failure_index == index
            assert outcome.value.campaign.status is RolloutCampaignStatus.ROLLING_BACK
            assert outcome.value.rollback_submission is not None
            assert outcome.value.campaign.measured_outcomes[criterion] == {
                "status": "failed",
                "evidence_reference": f"criterion-evidence-{value}-{index}",
            }
            break
        expected_status = (
            RolloutCampaignStatus.COMPLETE
            if index == len(criterion_outcomes) - 1
            else RolloutCampaignStatus.RUNNING
        )
        assert outcome.value.campaign.status is expected_status
        assert outcome.value.rollback_submission is None

    if first_failure_index is None:
        assert (
            database._state.rollouts[primary_campaign.campaign_id].status
            is RolloutCampaignStatus.COMPLETE
        )
        assert len(database._state.work_items) == 1
        return

    assert [work.subject_reference for work in database._state.work_items.values()] == [
        f"rollout:{primary_campaign.campaign_id}",
        f"rollout:{primary_campaign.campaign_id}:rollback",
    ]
    override = RolloutService.manual_override(_CORRELATION)
    assert not override.is_success and override.error is not None
    assert override.error.code is ErrorCode.INVALID_TRANSITION
    stopped = rollout_service.record_criterion_outcome(
        _ORGANIZATION,
        _CORRELATION,
        primary_campaign.campaign_id,
        "criterion-after-failure",
        passed=True,
        evidence_reference=f"criterion-evidence-after-failure-{value}",
    )
    assert not stopped.is_success and stopped.error is not None
    assert stopped.error.code is ErrorCode.INVALID_TRANSITION
    assert (
        database._state.rollouts[primary_campaign.campaign_id].status
        is RolloutCampaignStatus.ROLLING_BACK
    )

    peer_campaign = _campaign(value, "peer", ("peer-criterion",))
    peer_created = rollout_service.create_campaign(_ORGANIZATION, peer_campaign)
    assert peer_created.is_success and peer_created.value is not None
    _seed_start_evidence(
        database,
        peer_campaign,
        evaluation_passed=peer_start_evidence[0],
        approval_approved=peer_start_evidence[1],
    )
    peer_started = rollout_service.start_campaign(
        _ORGANIZATION,
        _CORRELATION,
        peer_campaign.campaign_id,
        idempotency_key=f"start-{peer_campaign.campaign_id}",
    )
    peer_missing_start_conditions = _missing_start_conditions(peer_campaign, peer_start_evidence)
    if peer_missing_start_conditions:
        assert not peer_started.is_success and peer_started.error is not None
        assert peer_started.error.code is ErrorCode.VALIDATION_FAILED
        assert {field.name for field in peer_started.error.fields} == peer_missing_start_conditions
        assert (
            database._state.rollouts[peer_campaign.campaign_id].status
            is RolloutCampaignStatus.PENDING
        )
        assert len(database._state.work_items) == 2
    else:
        assert peer_started.is_success and peer_started.value is not None
        assert peer_started.value.campaign.status is RolloutCampaignStatus.RUNNING
        assert [work.subject_reference for work in database._state.work_items.values()] == [
            f"rollout:{primary_campaign.campaign_id}",
            f"rollout:{primary_campaign.campaign_id}:rollback",
            f"rollout:{peer_campaign.campaign_id}",
        ]
