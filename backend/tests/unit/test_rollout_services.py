"""Focused deterministic ProposalService and RolloutService tests for task 10.1."""

# ruff: noqa: E501 - descriptive test names and assertions remain directly readable.
from __future__ import annotations

from collections.abc import Mapping
from datetime import UTC, datetime

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
    WorkState,
)
from app.models.identifiers import CorrelationId, OrganizationId, RecordId
from app.repositories.control_plane import InMemoryControlPlaneDatabase

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_ORGANIZATION = OrganizationId("rollout-organization")
_CORRELATION = CorrelationId("rollout-correlation")


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


def _published_agent() -> CommonAgentVersion:
    return CommonAgentVersion(
        metadata=_metadata("agent-record"),
        agent_version_id=AgentVersionId("agent-published"),
        status=ContractStatus.PUBLISHED,
        canonical_identity="operations.planner",
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
        content_digest="sha256:agent-published",
    )


def _proposal(*, complete: bool = True) -> ImprovementProposal:
    return ImprovementProposal(
        metadata=_metadata("proposal-record"),
        proposal_id=ProposalId("proposal-1"),
        source_version_reference="agent-published",
        immutable_difference={"runtime": {"max_retries": 3}},
        source_evidence=("source-evidence",),
        validation_evidence=("validation-evidence",) if complete else (),
        evaluation_evidence=("evaluation-evidence",) if complete else (),
        reviewer_decisions=("reviewed",),
        approval_evidence=("approval-evidence",) if complete else (),
        rollback_evidence=("rollback-evidence",) if complete else (),
        impact_summary="Controlled retry improvement.",
    )


def _campaign(campaign_id: str = "campaign-1") -> RolloutCampaign:
    return RolloutCampaign(
        metadata=_metadata(f"{campaign_id}-record"),
        campaign_id=RolloutCampaignId(campaign_id),
        proposal_id=ProposalId("proposal-1"),
        selected_version_reference="agent-published-v2",
        target_scope=("tenant-a",),
        evaluation_evidence_references=("evaluation-1",),
        required_approval_references=(f"approval-{campaign_id.rsplit('-', maxsplit=1)[-1]}",),
        success_criteria={"error_rate": "below-baseline"},
        rollback_reference="rollback-plan-1",
        status=RolloutCampaignStatus.PENDING,
        measured_outcomes={},
    )


def _services(database: InMemoryControlPlaneDatabase) -> tuple[ProposalService, RolloutService]:
    command_service = CommandService(
        database.unit_of_work, clock=lambda: _NOW, next_event_sequence=iter(range(1, 20)).__next__
    )
    return ProposalService(database.unit_of_work), RolloutService(
        database.unit_of_work, command_service, clock=lambda: _NOW
    )


def _seed_published_source(database: InMemoryControlPlaneDatabase) -> CommonAgentVersion:
    agent = _published_agent()
    with database.unit_of_work() as unit_of_work:
        assert unit_of_work.common_contracts.append_agent_version(agent).is_success
    return agent


def _seed_start_evidence(database: InMemoryControlPlaneDatabase) -> None:
    evidence = QualityEvidence(
        metadata=_metadata("evaluation-record"),
        evidence_id="evaluation-1",
        kind=QualityEvidenceKind.GATE,
        subject_reference="proposal:proposal-1",
        passed=True,
        evidence_reference="evaluation-artifact-1",
        recorded_at=_NOW,
    )
    approval = ApprovalGate(
        metadata=_metadata("approval-record"),
        approval_gate_id=ApprovalGateId("approval-1"),
        pending_operation_reference="rollout:campaign-1",
        status=ApprovalGateStatus.APPROVED,
        decision="approve",
        decision_reason="all evidence reviewed",
        reviewer_reference="release-owner",
    )
    with database.unit_of_work() as unit_of_work:
        assert unit_of_work.evidence.append_quality(evidence).is_success
        assert unit_of_work.evidence.append_approval(approval).is_success


def test_proposal_retains_immutable_difference_and_preserves_published_source() -> None:
    """Proposal submission snapshots mutable input without modifying its published source."""
    database = InMemoryControlPlaneDatabase()
    proposal_service, _ = _services(database)
    source = _seed_published_source(database)
    difference = {"runtime": {"max_retries": 3}}
    proposal = _proposal()
    proposal = ImprovementProposal(
        metadata=proposal.metadata,
        proposal_id=proposal.proposal_id,
        source_version_reference=proposal.source_version_reference,
        immutable_difference=difference,
        source_evidence=proposal.source_evidence,
        validation_evidence=proposal.validation_evidence,
        evaluation_evidence=proposal.evaluation_evidence,
        reviewer_decisions=proposal.reviewer_decisions,
        approval_evidence=proposal.approval_evidence,
        rollback_evidence=proposal.rollback_evidence,
        impact_summary=proposal.impact_summary,
    )

    created = proposal_service.create_proposal(_ORGANIZATION, proposal)
    difference["runtime"]["max_retries"] = 99

    assert created.is_success and created.value is not None
    runtime_difference = created.value.immutable_difference["runtime"]
    assert isinstance(runtime_difference, Mapping)
    assert runtime_difference["max_retries"] == 3
    assert database._state.agent_versions[source.agent_version_id] == source
    assert database._state.agent_versions[source.agent_version_id].metadata.version == 1


def test_incomplete_proposal_is_retained_but_cannot_create_production_campaign() -> None:
    """Missing validation, evaluation, approval, or rollback evidence keeps a proposal out of production."""
    database = InMemoryControlPlaneDatabase()
    proposal_service, rollout_service = _services(database)
    _seed_published_source(database)

    assert proposal_service.create_proposal(_ORGANIZATION, _proposal(complete=False)).is_success
    campaign = rollout_service.create_campaign(_ORGANIZATION, _campaign())

    assert not campaign.is_success
    assert campaign.error is not None
    assert campaign.error.code is ErrorCode.VALIDATION_FAILED
    assert {field.name for field in campaign.error.fields} == {
        "validation_evidence",
        "evaluation_evidence",
        "approval_evidence",
        "rollback_evidence",
    }
    assert ProposalId("proposal-1") in database._state.proposals
    assert database._state.rollouts == {}


def test_start_requires_retained_evaluation_and_approved_evidence() -> None:
    """A campaign stays pending when configured start evidence is absent."""
    database = InMemoryControlPlaneDatabase()
    proposal_service, rollout_service = _services(database)
    _seed_published_source(database)
    assert proposal_service.create_proposal(_ORGANIZATION, _proposal()).is_success
    assert rollout_service.create_campaign(_ORGANIZATION, _campaign()).is_success

    started = rollout_service.start_campaign(
        _ORGANIZATION,
        _CORRELATION,
        RolloutCampaignId("campaign-1"),
        idempotency_key="start-campaign-1",
    )

    assert not started.is_success
    assert started.error is not None
    assert started.error.code is ErrorCode.VALIDATION_FAILED
    assert {field.name for field in started.error.fields} == {
        "evaluation_evidence:evaluation-1",
        "approval_evidence:approval-1",
    }
    assert (
        database._state.rollouts[RolloutCampaignId("campaign-1")].status
        is RolloutCampaignStatus.PENDING
    )
    assert database._state.work_items == {}


def test_failed_criterion_starts_rollback_atomically_and_allows_independent_campaign() -> None:
    """Failure stops one campaign, retains evidence, denies override, and never blocks a valid peer campaign."""
    database = InMemoryControlPlaneDatabase()
    proposal_service, rollout_service = _services(database)
    _seed_published_source(database)
    _seed_start_evidence(database)
    assert proposal_service.create_proposal(_ORGANIZATION, _proposal()).is_success
    assert rollout_service.create_campaign(_ORGANIZATION, _campaign()).is_success
    observed_subjects: list[str] = []

    started = rollout_service.start_campaign(
        _ORGANIZATION,
        _CORRELATION,
        RolloutCampaignId("campaign-1"),
        idempotency_key="start-campaign-1",
        dispatch=lambda work: observed_subjects.append(work.subject_reference),
    )
    failed = rollout_service.record_criterion_outcome(
        _ORGANIZATION,
        _CORRELATION,
        RolloutCampaignId("campaign-1"),
        "error_rate",
        passed=False,
        evidence_reference="criterion-evidence-1",
        dispatch=lambda work: observed_subjects.append(work.subject_reference),
    )

    assert started.is_success and started.value is not None
    assert failed.is_success and failed.value is not None
    assert failed.value.rollback_submission is not None
    assert failed.value.campaign.status is RolloutCampaignStatus.ROLLING_BACK
    assert failed.value.campaign.measured_outcomes["error_rate"] == {
        "status": "failed",
        "evidence_reference": "criterion-evidence-1",
    }
    assert [item.subject_reference for item in database._state.work_items.values()] == [
        "rollout:campaign-1",
        "rollout:campaign-1:rollback",
    ]
    assert all(item.state is WorkState.PENDING for item in database._state.work_items.values())
    assert observed_subjects == ["rollout:campaign-1", "rollout:campaign-1:rollback"]
    override = RolloutService.manual_override(_CORRELATION)
    assert not override.is_success and override.error is not None
    assert override.error.code is ErrorCode.INVALID_TRANSITION


def test_campaign_during_rollback_validates_its_own_start_evidence() -> None:
    """A peer campaign stays pending until its own approval passes during another rollback."""
    database = InMemoryControlPlaneDatabase()
    proposal_service, rollout_service = _services(database)
    _seed_published_source(database)
    _seed_start_evidence(database)
    assert proposal_service.create_proposal(_ORGANIZATION, _proposal()).is_success
    assert rollout_service.create_campaign(_ORGANIZATION, _campaign()).is_success
    assert rollout_service.start_campaign(
        _ORGANIZATION,
        _CORRELATION,
        RolloutCampaignId("campaign-1"),
        idempotency_key="start-campaign-1",
    ).is_success
    rollback = rollout_service.record_criterion_outcome(
        _ORGANIZATION,
        _CORRELATION,
        RolloutCampaignId("campaign-1"),
        "error_rate",
        passed=False,
        evidence_reference="criterion-evidence-1",
    )
    assert rollback.is_success and rollback.value is not None
    assert rollback.value.campaign.status is RolloutCampaignStatus.ROLLING_BACK

    assert rollout_service.create_campaign(_ORGANIZATION, _campaign("campaign-2")).is_success
    pending = rollout_service.start_campaign(
        _ORGANIZATION,
        _CORRELATION,
        RolloutCampaignId("campaign-2"),
        idempotency_key="start-campaign-2",
    )
    assert not pending.is_success and pending.error is not None
    assert {field.name for field in pending.error.fields} == {"approval_evidence:approval-2"}
    assert (
        database._state.rollouts[RolloutCampaignId("campaign-2")].status
        is RolloutCampaignStatus.PENDING
    )

    with database.unit_of_work() as unit_of_work:
        assert unit_of_work.evidence.append_approval(
            ApprovalGate(
                metadata=_metadata("approval-record-2"),
                approval_gate_id=ApprovalGateId("approval-2"),
                pending_operation_reference="rollout:campaign-2",
                status=ApprovalGateStatus.APPROVED,
                decision="approve",
                decision_reason="peer campaign independently reviewed",
                reviewer_reference="release-owner",
            )
        ).is_success
    started = rollout_service.start_campaign(
        _ORGANIZATION,
        _CORRELATION,
        RolloutCampaignId("campaign-2"),
        idempotency_key="start-campaign-2",
    )

    assert started.is_success and started.value is not None
    assert started.value.campaign.status is RolloutCampaignStatus.RUNNING
    assert len(database._state.work_items) == 3
