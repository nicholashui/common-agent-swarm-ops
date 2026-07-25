"""Immutable proposals and evidence-bound bounded rollout campaigns."""

# ruff: noqa: E501 - policy and evidence messages deliberately remain whole stable strings.
from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, replace
from datetime import datetime

from app.core.command_service import (
    CommandService,
    CommandSubmission,
    DispatchCallback,
    PublicationCallback,
    WorkCommand,
    WorkKind,
)
from app.models.common import utc_now
from app.models.contracts import ErrorCode, ErrorDetail, ErrorField, Result
from app.models.control_plane import (
    AgentVersionId,
    ApprovalGateId,
    ApprovalGateStatus,
    CommonPatternVersionId,
    ContractStatus,
    ImprovementProposal,
    RolloutCampaign,
    RolloutCampaignId,
    RolloutCampaignStatus,
)
from app.models.identifiers import CorrelationId, OrganizationId
from app.repositories.control_plane import ControlPlaneUnitOfWork


@dataclass(frozen=True, slots=True)
class ProposalReadiness:
    """The production-eligibility result retained independently of proposal submission."""

    proposal: ImprovementProposal
    missing_evidence: tuple[str, ...]

    @property
    def production_eligible(self) -> bool:
        """Return whether this retained proposal may enter a production campaign."""
        return not self.missing_evidence


@dataclass(frozen=True, slots=True)
class RolloutStart:
    """Committed campaign start and its shared durable-work submission."""

    campaign: RolloutCampaign
    submission: CommandSubmission


@dataclass(frozen=True, slots=True)
class CriterionOutcome:
    """One immutable per-criterion outcome and any atomically initiated rollback work."""

    campaign: RolloutCampaign
    criterion: str
    passed: bool
    rollback_submission: CommandSubmission | None


UnitOfWorkFactory = Callable[[], ControlPlaneUnitOfWork]


class ProposalService:
    """Retain proposal snapshots without modifying their published contract source."""

    def __init__(self, unit_of_work_factory: UnitOfWorkFactory) -> None:
        self._unit_of_work_factory = unit_of_work_factory

    def create_proposal(
        self, organization_id: OrganizationId, proposal: ImprovementProposal
    ) -> Result[ImprovementProposal, ErrorDetail]:
        """Append an immutable proposal only against an existing published source version."""
        if proposal.metadata.organization_id != organization_id:
            return Result.failure(self._unavailable(proposal.metadata.correlation_id, "Proposal"))
        with self._unit_of_work_factory() as unit_of_work:
            if not self._published_source_exists(unit_of_work, organization_id, proposal):
                return Result.failure(
                    ErrorDetail(
                        ErrorCode.VALIDATION_FAILED,
                        "Proposal source must reference a published common contract version.",
                        proposal.metadata.correlation_id,
                    )
                )
            created = unit_of_work.evidence.append_proposal(proposal)
            return self._repository_result(created, proposal.metadata.correlation_id)

    @staticmethod
    def readiness(proposal: ImprovementProposal) -> ProposalReadiness:
        """Identify evidence missing from production eligibility without discarding the proposal."""
        evidence = {
            "validation_evidence": proposal.validation_evidence,
            "evaluation_evidence": proposal.evaluation_evidence,
            "approval_evidence": proposal.approval_evidence,
            "rollback_evidence": proposal.rollback_evidence,
        }
        return ProposalReadiness(
            proposal=proposal,
            missing_evidence=tuple(name for name, values in evidence.items() if not values),
        )

    @staticmethod
    def _published_source_exists(
        unit_of_work: ControlPlaneUnitOfWork,
        organization_id: OrganizationId,
        proposal: ImprovementProposal,
    ) -> bool:
        agent = unit_of_work.common_contracts.get_agent_version(
            organization_id, AgentVersionId(proposal.source_version_reference)
        )
        if agent.is_success and agent.value is not None:
            return agent.value.status is ContractStatus.PUBLISHED
        pattern = unit_of_work.common_contracts.get_pattern_version(
            organization_id, CommonPatternVersionId(proposal.source_version_reference)
        )
        return bool(
            pattern.is_success
            and pattern.value is not None
            and pattern.value.status is ContractStatus.PUBLISHED
        )

    @staticmethod
    def _unavailable(correlation_id: CorrelationId, subject: str) -> ErrorDetail:
        return ErrorDetail(
            ErrorCode.AUTHORIZATION_DENIED, f"{subject} is unavailable.", correlation_id
        )

    @staticmethod
    def _repository_result[T](
        result: Result[T, ErrorDetail], correlation_id: CorrelationId
    ) -> Result[T, ErrorDetail]:
        if result.is_success:
            return result
        error = result.error
        return Result.failure(
            replace(error, correlation_id=correlation_id)
            if error is not None
            else ErrorDetail(
                ErrorCode.REPOSITORY_UNAVAILABLE, "Proposal storage is unavailable.", correlation_id
            )
        )


class RolloutService:
    """Start, measure, and roll back campaigns through the shared durable-work boundary."""

    def __init__(
        self,
        unit_of_work_factory: UnitOfWorkFactory,
        command_service: CommandService,
        *,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._command_service = command_service
        self._clock = clock

    def create_campaign(
        self, organization_id: OrganizationId, campaign: RolloutCampaign
    ) -> Result[RolloutCampaign, ErrorDetail]:
        """Retain a pending campaign only for a production-eligible retained proposal."""
        if campaign.metadata.organization_id != organization_id:
            return Result.failure(self._unavailable(campaign.metadata.correlation_id))
        if campaign.status is not RolloutCampaignStatus.PENDING:
            return Result.failure(
                self._validation(
                    campaign.metadata.correlation_id, "New rollout campaigns must be pending."
                )
            )
        invalid = self._campaign_shape_error(campaign)
        if invalid is not None:
            return Result.failure(invalid)
        with self._unit_of_work_factory() as unit_of_work:
            proposal_result = unit_of_work.evidence.get_proposal(
                organization_id, campaign.proposal_id
            )
            proposal = proposal_result.value
            if not proposal_result.is_success or proposal is None:
                return Result.failure(self._unavailable(campaign.metadata.correlation_id))
            readiness = ProposalService.readiness(proposal)
            if not readiness.production_eligible:
                return Result.failure(
                    ErrorDetail(
                        ErrorCode.VALIDATION_FAILED,
                        "Proposal is retained outside production rollout until required evidence is present.",
                        campaign.metadata.correlation_id,
                        fields=tuple(
                            ErrorField(name, "required before production rollout")
                            for name in readiness.missing_evidence
                        ),
                    )
                )
            normalized = replace(
                campaign,
                measured_outcomes={
                    criterion: campaign.measured_outcomes.get(criterion, {"status": "pending"})
                    for criterion in campaign.success_criteria
                },
            )
            persisted = unit_of_work.evidence.append_rollout(normalized)
            return self._repository_result(persisted, campaign.metadata.correlation_id)

    def start_campaign(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        campaign_id: RolloutCampaignId,
        *,
        idempotency_key: str,
        dispatch: DispatchCallback | None = None,
        publish: PublicationCallback | None = None,
    ) -> Result[RolloutStart, ErrorDetail]:
        """Commit start state and rollout work together, then dispatch only after the commit."""
        with self._unit_of_work_factory() as unit_of_work:
            current_result = unit_of_work.evidence.get_rollout(organization_id, campaign_id)
            current = current_result.value
            if not current_result.is_success or current is None:
                return Result.failure(self._unavailable(correlation_id))
            if current.status is not RolloutCampaignStatus.PENDING:
                return Result.failure(
                    self._invalid_transition(correlation_id, "Campaign cannot be started.")
                )
            missing = self._missing_start_conditions(unit_of_work, organization_id, current)
            if missing:
                return Result.failure(self._missing_conditions_error(correlation_id, missing))
            started = self._next_campaign(current, correlation_id, RolloutCampaignStatus.RUNNING)
            replaced = unit_of_work.evidence.replace_rollout(started, current.metadata.version)
            if not replaced.is_success:
                unit_of_work.rollback()
                return Result.failure(self._repository_error(replaced.error, correlation_id))
            submission = self._command_service.submit_in_transaction(
                unit_of_work,
                organization_id,
                correlation_id,
                WorkCommand(
                    kind=WorkKind.ROLLOUT,
                    subject_reference=f"rollout:{current.campaign_id}",
                    idempotency_key=idempotency_key,
                    scheduled_at=self._clock(),
                ),
            )
            if not submission.is_success or submission.value is None:
                unit_of_work.rollback()
                return Result.failure(self._repository_error(submission.error, correlation_id))
        delivered = self._command_service.deliver(
            submission.value, dispatch=dispatch, publish=publish
        )
        return Result.success(RolloutStart(campaign=started, submission=delivered))

    def record_criterion_outcome(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        campaign_id: RolloutCampaignId,
        criterion: str,
        *,
        passed: bool,
        evidence_reference: str,
        dispatch: DispatchCallback | None = None,
        publish: PublicationCallback | None = None,
    ) -> Result[CriterionOutcome, ErrorDetail]:
        """Retain an outcome; failed criteria atomically create retained rollback work."""
        if not criterion.strip() or not evidence_reference.strip():
            return Result.failure(
                self._validation(correlation_id, "Criterion and criterion evidence are required.")
            )
        with self._unit_of_work_factory() as unit_of_work:
            current_result = unit_of_work.evidence.get_rollout(organization_id, campaign_id)
            current = current_result.value
            if not current_result.is_success or current is None:
                return Result.failure(self._unavailable(correlation_id))
            if current.status is not RolloutCampaignStatus.RUNNING:
                return Result.failure(
                    self._invalid_transition(
                        correlation_id,
                        "Campaign progression is stopped and cannot accept this outcome.",
                    )
                )
            if criterion not in current.success_criteria:
                return Result.failure(
                    self._validation(correlation_id, "Unknown rollout success criterion.")
                )
            outcomes = dict(current.measured_outcomes)
            outcomes[criterion] = {
                "status": "passed" if passed else "failed",
                "evidence_reference": evidence_reference,
            }
            status = (
                RolloutCampaignStatus.COMPLETE
                if passed and self._all_criteria_passed(current.success_criteria, outcomes)
                else RolloutCampaignStatus.RUNNING
                if passed
                else RolloutCampaignStatus.ROLLING_BACK
            )
            updated = self._next_campaign(current, correlation_id, status, outcomes)
            replaced = unit_of_work.evidence.replace_rollout(updated, current.metadata.version)
            if not replaced.is_success:
                unit_of_work.rollback()
                return Result.failure(self._repository_error(replaced.error, correlation_id))
            rollback_submission: CommandSubmission | None = None
            if not passed:
                rollback = self._command_service.submit_in_transaction(
                    unit_of_work,
                    organization_id,
                    correlation_id,
                    WorkCommand(
                        kind=WorkKind.ROLLOUT,
                        subject_reference=f"rollout:{current.campaign_id}:rollback",
                        idempotency_key=f"rollback:{current.campaign_id}:{criterion}",
                        scheduled_at=self._clock(),
                    ),
                )
                if not rollback.is_success or rollback.value is None:
                    unit_of_work.rollback()
                    return Result.failure(self._repository_error(rollback.error, correlation_id))
                rollback_submission = rollback.value
        if rollback_submission is not None:
            rollback_submission = self._command_service.deliver(
                rollback_submission, dispatch=dispatch, publish=publish
            )
        return Result.success(
            CriterionOutcome(
                campaign=updated,
                criterion=criterion,
                passed=passed,
                rollback_submission=rollback_submission,
            )
        )

    @staticmethod
    def manual_override(
        correlation_id: CorrelationId,
    ) -> Result[None, ErrorDetail]:
        """Reject every manual campaign override; no caller may bypass a failed criterion."""
        return Result.failure(
            ErrorDetail(
                ErrorCode.INVALID_TRANSITION,
                "Manual rollout overrides are prohibited.",
                correlation_id,
            )
        )

    def _missing_start_conditions(
        self,
        unit_of_work: ControlPlaneUnitOfWork,
        organization_id: OrganizationId,
        campaign: RolloutCampaign,
    ) -> tuple[str, ...]:
        missing: list[str] = []
        if not campaign.target_scope or not self._is_bounded_scope(campaign.target_scope):
            missing.append("target_scope")
        if not campaign.success_criteria:
            missing.append("success_criteria")
        if not campaign.rollback_reference.strip():
            missing.append("rollback_reference")
        for evidence_id in campaign.evaluation_evidence_references:
            evidence = unit_of_work.evidence.get_quality(organization_id, evidence_id)
            if not evidence.is_success or evidence.value is None or not evidence.value.passed:
                missing.append(f"evaluation_evidence:{evidence_id}")
        if not campaign.evaluation_evidence_references:
            missing.append("evaluation_evidence")
        for approval_id in campaign.required_approval_references:
            approval = unit_of_work.evidence.get_approval(
                organization_id, ApprovalGateId(approval_id)
            )
            if (
                not approval.is_success
                or approval.value is None
                or approval.value.status is not ApprovalGateStatus.APPROVED
                or approval.value.pending_operation_reference != f"rollout:{campaign.campaign_id}"
            ):
                missing.append(f"approval_evidence:{approval_id}")
        if not campaign.required_approval_references:
            missing.append("approval_evidence")
        return tuple(missing)

    def _campaign_shape_error(self, campaign: RolloutCampaign) -> ErrorDetail | None:
        if not self._is_bounded_scope(campaign.target_scope):
            return self._validation(
                campaign.metadata.correlation_id,
                "Rollout target scope must be finite and explicit.",
            )
        if any(not criterion.strip() for criterion in campaign.success_criteria):
            return self._validation(
                campaign.metadata.correlation_id, "Rollout success criteria must be named."
            )
        return None

    @staticmethod
    def _is_bounded_scope(target_scope: tuple[str, ...]) -> bool:
        return bool(target_scope) and all(
            target.strip() and target.strip().lower() not in {"*", "all"} for target in target_scope
        )

    def _next_campaign(
        self,
        campaign: RolloutCampaign,
        correlation_id: CorrelationId,
        status: RolloutCampaignStatus,
        measured_outcomes: Mapping[str, object] | None = None,
    ) -> RolloutCampaign:
        return replace(
            campaign,
            metadata=replace(
                campaign.metadata,
                correlation_id=correlation_id,
                version=campaign.metadata.version + 1,
                updated_at=self._clock(),
            ),
            status=status,
            measured_outcomes=(
                campaign.measured_outcomes if measured_outcomes is None else measured_outcomes
            ),
        )

    @staticmethod
    def _all_criteria_passed(
        success_criteria: Mapping[str, object], outcomes: Mapping[str, object]
    ) -> bool:
        def criterion_passed(criterion: str) -> bool:
            outcome = outcomes.get(criterion)
            return isinstance(outcome, Mapping) and outcome.get("status") == "passed"

        return all(criterion_passed(criterion) for criterion in success_criteria)

    @staticmethod
    def _missing_conditions_error(
        correlation_id: CorrelationId, missing: tuple[str, ...]
    ) -> ErrorDetail:
        return ErrorDetail(
            ErrorCode.VALIDATION_FAILED,
            "Rollout campaign lacks required start conditions.",
            correlation_id,
            fields=tuple(ErrorField(name, "required before campaign start") for name in missing),
        )

    @staticmethod
    def _validation(correlation_id: CorrelationId, message: str) -> ErrorDetail:
        return ErrorDetail(ErrorCode.VALIDATION_FAILED, message, correlation_id)

    @staticmethod
    def _invalid_transition(correlation_id: CorrelationId, message: str) -> ErrorDetail:
        return ErrorDetail(ErrorCode.INVALID_TRANSITION, message, correlation_id)

    @staticmethod
    def _unavailable(correlation_id: CorrelationId) -> ErrorDetail:
        return ErrorDetail(
            ErrorCode.AUTHORIZATION_DENIED, "Rollout campaign is unavailable.", correlation_id
        )

    @staticmethod
    def _repository_error(error: ErrorDetail | None, correlation_id: CorrelationId) -> ErrorDetail:
        if error is None:
            return ErrorDetail(
                ErrorCode.REPOSITORY_UNAVAILABLE, "Rollout storage is unavailable.", correlation_id
            )
        return replace(error, correlation_id=correlation_id)

    @classmethod
    def _repository_result[T](
        cls, result: Result[T, ErrorDetail], correlation_id: CorrelationId
    ) -> Result[T, ErrorDetail]:
        if result.is_success:
            return result
        return Result.failure(cls._repository_error(result.error, correlation_id))
