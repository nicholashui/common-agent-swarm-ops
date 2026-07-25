"""Services that retain immutable proposals and fail-closed promotion assessments."""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Callable, Mapping, Sequence
from dataclasses import replace
from datetime import datetime

from app.evaluation.models import EvaluationCheckKind, EvaluationOutcome, EvaluationRun
from app.evolution.models import (
    CanaryCriterionResult,
    CanaryId,
    CanaryRecord,
    CanaryScope,
    CanaryState,
    ImprovementDirection,
    MetricComparison,
    PromotionApprovalId,
    PromotionApprovalRecord,
    PromotionAssessment,
    PromotionAssessmentId,
    PromotionCondition,
    PromotionDecision,
    RollbackRecord,
    RollbackRecordId,
    RollbackStatus,
    SandboxVariant,
    SandboxVariantId,
    SandboxVariantState,
)
from app.models.common import SCHEMA_VERSION, RecordMetadata, utc_now
from app.models.contracts import ErrorCode, ErrorDetail, ErrorField, Result
from app.models.control_plane import (
    AuditRecord,
    ImprovementProposal,
    ProposalId,
    ProposalPromotionState,
    ProposalSandboxState,
)
from app.models.identifiers import (
    ActorId,
    CorrelationId,
    EvaluationRunId,
    OrganizationId,
    new_record_id,
)
from app.repositories.evaluation_repository import InMemoryEvaluationRepository
from app.repositories.evolution_repository import InMemoryEvolutionRepository


class EvolutionService:
    """Implements sandbox-only proposal, canary, rollback, and assessment lifecycles."""

    def __init__(
        self,
        repository: InMemoryEvolutionRepository,
        evaluation_repository: InMemoryEvaluationRepository,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._repository = repository
        self._evaluation_repository = evaluation_repository
        self._clock = clock

    def create_improvement_proposal(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        proposal: ImprovementProposal | None = None,
        *,
        source_version_reference: str | None = None,
        immutable_difference: Mapping[str, object] | None = None,
        source_learning_episode_references: Sequence[str] = (),
        assessment_evidence_references: Sequence[str] = (),
        validation_evidence_references: Sequence[str] = (),
        impact_summary: str | None = None,
        proposal_id: ProposalId | None = None,
        sandbox_transition: (
            Callable[[ImprovementProposal], bool | Result[object, ErrorDetail]] | None
        ) = None,
        transition_failure_evidence: Sequence[str] = (),
    ) -> Result[ImprovementProposal, ErrorDetail]:
        """Persist evidence before attempting a sandbox transition.

        The initial proposal is always retained first.  A transition callback may then
        fail; in that case a second immutable proposal snapshot retains the failure
        evidence and the operation returns a recoverable failure.
        """
        if proposal is None:
            if (
                source_version_reference is None
                or immutable_difference is None
                or impact_summary is None
            ):
                return Result.failure(
                    self._validation(
                        (
                            "Improvement proposals require a source version, difference, "
                            "and impact summary."
                        ),
                        correlation_id,
                    )
                )
            try:
                proposal = ImprovementProposal(
                    metadata=self._metadata(organization_id, correlation_id),
                    proposal_id=proposal_id or ProposalId(str(new_record_id())),
                    source_version_reference=source_version_reference,
                    immutable_difference=immutable_difference,
                    source_evidence=self._references(
                        source_learning_episode_references,
                        "source_learning_episode_references",
                    ),
                    validation_evidence=self._references(
                        validation_evidence_references, "validation_evidence_references"
                    ),
                    evaluation_evidence=self._references(
                        assessment_evidence_references, "assessment_evidence_references"
                    ),
                    reviewer_decisions=(),
                    approval_evidence=(),
                    rollback_evidence=(),
                    impact_summary=impact_summary,
                )
            except ValueError as error:
                return Result.failure(self._validation(str(error), correlation_id))
        elif proposal.metadata.organization_id != organization_id:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.AUTHORIZATION_DENIED,
                    "Improvement proposal is outside the requested organization.",
                    correlation_id,
                )
            )

        if proposal.sandbox_state is not ProposalSandboxState.SANDBOX:
            return Result.failure(
                self._validation(
                    "Only a new sandbox proposal can begin a sandbox transition.",
                    correlation_id,
                )
            )
        if not proposal.source_evidence or not proposal.evaluation_evidence:
            return Result.failure(
                self._validation(
                    "Improvement proposals require Learning_Episode and assessment evidence.",
                    correlation_id,
                )
            )
        created = self._repository.create_improvement_proposal(proposal)
        if not created.is_success or created.value is None:
            return self._repository_failure(created.error, correlation_id)
        retained = created.value
        if sandbox_transition is None:
            return Result.success(retained)

        transition_error: ErrorDetail | None = None
        try:
            transition_result = sandbox_transition(retained)
            if isinstance(transition_result, Result):
                if not transition_result.is_success:
                    transition_error = transition_result.error or ErrorDetail(
                        ErrorCode.REPOSITORY_UNAVAILABLE,
                        "Sandbox transition failed.",
                        correlation_id,
                        retryable=True,
                    )
            elif not transition_result:
                transition_error = ErrorDetail(
                    ErrorCode.INVALID_TRANSITION,
                    "Sandbox transition was rejected.",
                    correlation_id,
                )
        except Exception:
            transition_error = ErrorDetail(
                ErrorCode.REPOSITORY_UNAVAILABLE,
                "Sandbox transition failed and requires recovery.",
                correlation_id,
                retryable=True,
            )
        if transition_error is None:
            return Result.success(retained)

        try:
            evidence = self._references(
                transition_failure_evidence or ("sandbox-transition-failed",),
                "transition_failure_evidence",
            )
        except ValueError as error:
            return Result.failure(self._validation(str(error), correlation_id))
        failed = replace(
            retained,
            metadata=self._next_metadata(retained.metadata, correlation_id),
            sandbox_state=ProposalSandboxState.TRANSITION_FAILED,
            sandbox_transition_failure_evidence=evidence,
        )
        persisted_failure = self._repository.transition_improvement_proposal(failed)
        if not persisted_failure.is_success:
            return self._repository_failure(persisted_failure.error, correlation_id)
        return Result.failure(transition_error)

    def record_sandbox_transition_failure(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        proposal_id: ProposalId,
        failure_evidence: Sequence[str],
    ) -> Result[ImprovementProposal, ErrorDetail]:
        """Retain a failed sandbox transition as a versioned proposal snapshot."""
        current = self._repository.get_improvement_proposal(
            organization_id, proposal_id
        )
        if not current.is_success or current.value is None:
            return self._repository_failure(current.error, correlation_id)
        try:
            evidence = self._references(failure_evidence, "failure_evidence")
        except ValueError as error:
            return Result.failure(self._validation(str(error), correlation_id))
        updated = replace(
            current.value,
            metadata=self._next_metadata(current.value.metadata, correlation_id),
            sandbox_state=ProposalSandboxState.TRANSITION_FAILED,
            sandbox_transition_failure_evidence=evidence,
        )
        persisted = self._repository.transition_improvement_proposal(updated)
        if not persisted.is_success:
            return self._repository_failure(persisted.error, correlation_id)
        return persisted

    def record_reviewer_decision(
        self,
        organization_id: OrganizationId,
        reviewer_id: ActorId,
        correlation_id: CorrelationId,
        proposal_id: ProposalId,
        *,
        approved: bool,
        evidence_references: Sequence[str],
        rollback_reference: str | None = None,
        designated_reviewer: bool = True,
    ) -> Result[ImprovementProposal, ErrorDetail]:
        """Retain a designated reviewer decision without changing live behavior."""
        current = self._repository.get_improvement_proposal(
            organization_id, proposal_id
        )
        if not current.is_success or current.value is None:
            return self._repository_failure(current.error, correlation_id)
        proposal = current.value
        if not designated_reviewer:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.AUTHORIZATION_DENIED,
                    "Only the designated reviewer may decide an improvement proposal.",
                    correlation_id,
                )
            )
        if proposal.sandbox_state is not ProposalSandboxState.SANDBOX:
            return Result.failure(
                self._validation(
                    "A proposal with a failed sandbox transition cannot be approved.",
                    correlation_id,
                )
            )
        try:
            evidence = self._references(evidence_references, "evidence_references")
        except ValueError as error:
            return Result.failure(self._validation(str(error), correlation_id))
        if not evidence:
            return Result.failure(
                self._validation(
                    "Reviewer decisions require evidence references.", correlation_id
                )
            )
        if approved:
            missing = self._missing_proposal_evidence(
                proposal, include_promotion_evidence=False
            )
            if missing:
                return Result.failure(
                    ErrorDetail(
                        ErrorCode.VALIDATION_FAILED,
                        "Required proposal assessment evidence is incomplete.",
                        correlation_id,
                        fields=tuple(
                            ErrorField(name, "required before reviewer approval")
                            for name in missing
                        ),
                    )
                )
            if rollback_reference is None or not rollback_reference.strip():
                return Result.failure(
                    self._validation(
                        "Reviewer approval requires a rollback reference.",
                        correlation_id,
                    )
                )
        timestamp = self._clock()
        decision_reference = (
            f"reviewer:{reviewer_id}:{timestamp.isoformat()}:"
            f"{'approved' if approved else 'rejected'}"
        )
        approval_evidence = (
            tuple(dict.fromkeys((*proposal.approval_evidence, *evidence)))
            if approved
            else proposal.approval_evidence
        )
        rollback_evidence = proposal.rollback_evidence
        if approved and rollback_reference is not None:
            rollback_evidence = tuple(
                dict.fromkeys((*rollback_evidence, rollback_reference))
            )
        updated = replace(
            proposal,
            metadata=self._next_metadata(proposal.metadata, correlation_id, timestamp),
            reviewer_decisions=(*proposal.reviewer_decisions, decision_reference),
            approval_evidence=approval_evidence,
            rollback_evidence=rollback_evidence,
            promotion_state=(
                ProposalPromotionState.APPROVED
                if approved
                else ProposalPromotionState.NOT_APPROVED
            ),
            reviewer_identity=str(reviewer_id),
            reviewer_decision_timestamp=timestamp,
            reviewer_evidence_references=evidence,
            rollback_reference=(
                rollback_reference if approved else proposal.rollback_reference
            ),
        )
        persisted = self._repository.transition_improvement_proposal(updated)
        if not persisted.is_success:
            return self._repository_failure(persisted.error, correlation_id)
        return persisted

    def authorize_live_change(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        proposal_id: ProposalId,
        target: str,
    ) -> Result[bool, ErrorDetail]:
        """Authorize only a proposal that has passed reviewer approval.

        The method never applies a live change; callers must use the governed promotion
        command, so direct unapproved writes cannot mutate prompts, policies, or risk.
        """
        if target not in {
            "prompt",
            "rubric",
            "tool_policy",
            "workflow",
            "risk_tier",
            "tool_authorization",
        }:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.AUTHORIZATION_DENIED,
                    "Live-change target is not governed.",
                    correlation_id,
                )
            )
        current = self._repository.get_improvement_proposal(
            organization_id, proposal_id
        )
        if not current.is_success or current.value is None:
            return self._repository_failure(current.error, correlation_id)
        if current.value.promotion_state is ProposalPromotionState.NOT_APPROVED:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.AUTHORIZATION_DENIED,
                    "Unapproved Improvement_Proposal live changes are denied.",
                    correlation_id,
                )
            )
        return Result.success(True)

    def promote_improvement_proposal(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        proposal_id: ProposalId,
        *,
        replaced_version_reference: str,
        promoted_version_reference: str,
        rollback_reference: str,
        evidence_references: Sequence[str] = (),
        live_change_target: str | None = None,
    ) -> Result[ImprovementProposal, ErrorDetail]:
        """Promote only an approved proposal into a new immutable version and audit it."""
        if live_change_target is not None and live_change_target not in {
            "prompt",
            "rubric",
            "tool_policy",
            "workflow",
            "risk_tier",
            "tool_authorization",
        }:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.AUTHORIZATION_DENIED,
                    "Live-change target is not governed.",
                    correlation_id,
                )
            )
        try:
            references = self._references(evidence_references, "evidence_references")
        except ValueError as error:
            return Result.failure(self._validation(str(error), correlation_id))
        if (
            not replaced_version_reference.strip()
            or not promoted_version_reference.strip()
        ):
            return Result.failure(
                self._validation(
                    "Immutable replacement and promoted versions are required.",
                    correlation_id,
                )
            )
        if replaced_version_reference == promoted_version_reference:
            return Result.failure(
                self._validation(
                    "Promoted version must replace a distinct immutable version.",
                    correlation_id,
                )
            )
        if not rollback_reference.strip():
            return Result.failure(
                self._validation("Rollback reference is required.", correlation_id)
            )
        current = self._repository.get_improvement_proposal(
            organization_id, proposal_id
        )
        if not current.is_success or current.value is None:
            return self._repository_failure(current.error, correlation_id)
        proposal = current.value
        if proposal.promotion_state is not ProposalPromotionState.APPROVED:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.AUTHORIZATION_DENIED,
                    "Improvement_Proposal lacks designated reviewer promotion approval.",
                    correlation_id,
                )
            )
        if proposal.source_version_reference != replaced_version_reference:
            return Result.failure(
                self._validation(
                    "Promotion must replace the proposal source immutable version.",
                    correlation_id,
                )
            )
        missing = self._missing_proposal_evidence(proposal)
        if missing or not proposal.reviewer_evidence_references:
            missing = (
                (*missing, "reviewer_evidence")
                if not proposal.reviewer_evidence_references
                else missing
            )
            return Result.failure(
                ErrorDetail(
                    ErrorCode.VALIDATION_FAILED,
                    "Promotion requires complete retained assessment and reviewer evidence.",
                    correlation_id,
                    fields=tuple(
                        ErrorField(name, "required before promotion")
                        for name in missing
                    ),
                )
            )
        if proposal.reviewer_identity is None:
            return Result.failure(
                self._validation(
                    "Promotion requires a designated reviewer identity.", correlation_id
                )
            )
        promoted = replace(
            proposal,
            metadata=self._next_metadata(proposal.metadata, correlation_id),
            promotion_state=ProposalPromotionState.PROMOTED,
            replaced_version_reference=replaced_version_reference,
            promoted_version_reference=promoted_version_reference,
            rollback_reference=rollback_reference,
            approval_evidence=tuple(
                dict.fromkeys((*proposal.approval_evidence, *references))
            ),
            rollback_evidence=tuple(
                dict.fromkeys((*proposal.rollback_evidence, rollback_reference))
            ),
        )
        audit_references = tuple(
            dict.fromkeys(
                (
                    str(proposal.proposal_id),
                    replaced_version_reference,
                    promoted_version_reference,
                    rollback_reference,
                    *proposal.source_evidence,
                    *proposal.validation_evidence,
                    *proposal.evaluation_evidence,
                    *proposal.reviewer_evidence_references,
                    *references,
                )
            )
        )
        audit = AuditRecord(
            metadata=self._metadata(organization_id, correlation_id),
            audit_id=str(new_record_id()),
            action="improvement.promotion",
            subject_reference=str(proposal.proposal_id),
            outcome="promoted",
            recorded_at=self._clock(),
            actor_id=ActorId(proposal.reviewer_identity),
            reason="Approved Improvement_Proposal promoted as an immutable replacement.",
            source_references=audit_references,
        )
        persisted = self._repository.promote_improvement_proposal(promoted, audit)
        if not persisted.is_success:
            return self._repository_failure(persisted.error, correlation_id)
        return persisted

    # Design terminology aliases retain a stable camelCase integration surface.
    createImprovementProposal = create_improvement_proposal  # noqa: N815
    createProposal = create_improvement_proposal  # noqa: N815
    create_proposal = create_improvement_proposal
    recordSandboxTransitionFailure = record_sandbox_transition_failure  # noqa: N815
    record_sandbox_failure = record_sandbox_transition_failure
    recordReviewerDecision = record_reviewer_decision  # noqa: N815
    authorizeLiveChange = authorize_live_change  # noqa: N815
    promoteImprovementProposal = promote_improvement_proposal  # noqa: N815
    promote_proposal = promote_improvement_proposal

    def propose(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        production_configuration: Mapping[str, object],
        sandbox_configuration: Mapping[str, object],
        target_metric: str,
        improvement_direction: ImprovementDirection,
    ) -> Result[SandboxVariant, ErrorDetail]:
        """Capture a detached sandbox proposal without mutating production inputs."""
        if not target_metric.strip() or self._contains_host_code(sandbox_configuration):
            return Result.failure(
                self._validation(
                    "Sandbox proposals require a metric and cannot modify Host code.",
                    correlation_id,
                )
            )
        try:
            production_json = self._canonical_json(production_configuration)
            sandbox_json = self._canonical_json(sandbox_configuration)
        except ValueError as error:
            return Result.failure(self._validation(str(error), correlation_id))
        record = SandboxVariant(
            self._metadata(organization_id, correlation_id),
            SandboxVariantId(str(new_record_id())),
            self._digest(production_json),
            self._digest(sandbox_json),
            sandbox_json,
            target_metric,
            improvement_direction,
            SandboxVariantState.DRAFT,
        )
        return self._repository.create_variant(record)

    def consider(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        variant_id: SandboxVariantId,
    ) -> Result[SandboxVariant, ErrorDetail]:
        """Mark one existing sandbox proposal as a promotion candidate."""
        current = self._repository.get_variant(organization_id, variant_id)
        if not current.is_success:
            return self._repository_failure(current.error, correlation_id)
        variant = self._value(current)
        if variant.state is SandboxVariantState.WITHDRAWN:
            return Result.failure(
                self._validation(
                    "Withdrawn variants cannot be considered.", correlation_id
                )
            )
        if variant.state is SandboxVariantState.UNDER_CONSIDERATION:
            return Result.success(variant)
        updated = replace(
            variant,
            metadata=self._next_metadata(variant.metadata, correlation_id),
            state=SandboxVariantState.UNDER_CONSIDERATION,
        )
        return self._repository.transition_variant(updated)

    def create_rollback_plan(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        variant_id: SandboxVariantId,
        rollback_plan: Mapping[str, object],
    ) -> Result[RollbackRecord, ErrorDetail]:
        """Retain a declarative rollback plan before canary activity is possible."""
        variant = self._repository.get_variant(organization_id, variant_id)
        if not variant.is_success:
            return self._repository_failure(variant.error, correlation_id)
        try:
            plan_json = self._canonical_json(rollback_plan)
        except ValueError as error:
            return Result.failure(self._validation(str(error), correlation_id))
        if plan_json == "{}":
            return Result.failure(
                self._validation("Rollback plans must not be empty.", correlation_id)
            )
        record = RollbackRecord(
            self._metadata(organization_id, correlation_id),
            RollbackRecordId(str(new_record_id())),
            variant_id,
            self._digest(plan_json),
            RollbackStatus.PLANNED,
        )
        return self._repository.create_rollback(record)

    def record_human_approval(
        self,
        organization_id: OrganizationId,
        actor_id: ActorId,
        correlation_id: CorrelationId,
        variant_id: SandboxVariantId,
        reason: str,
    ) -> Result[PromotionApprovalRecord, ErrorDetail]:
        """Append a trusted-actor approval for a specific sandbox candidate."""
        if not 1 <= len(reason) <= 1_000:
            return Result.failure(
                self._validation(
                    "Approval reason must contain 1 through 1,000 characters.",
                    correlation_id,
                )
            )
        variant = self._repository.get_variant(organization_id, variant_id)
        if not variant.is_success:
            return self._repository_failure(variant.error, correlation_id)
        timestamp = self._clock()
        record = PromotionApprovalRecord(
            self._metadata(organization_id, correlation_id, timestamp),
            PromotionApprovalId(str(new_record_id())),
            variant_id,
            actor_id,
            reason,
            timestamp,
        )
        return self._repository.create_approval(record)

    def approve_canary(
        self,
        organization_id: OrganizationId,
        actor_id: ActorId,
        correlation_id: CorrelationId,
        variant_id: SandboxVariantId,
        scope: CanaryScope,
        criteria: Sequence[str],
        rollback_record_id: RollbackRecordId,
    ) -> Result[CanaryRecord, ErrorDetail]:
        """Retain canary approval in an inactive state until explicit activation."""
        if scope.organization_id != organization_id or not (
            scope.workflow_id or scope.case_id
        ):
            return Result.failure(
                self._validation(
                    "Canary scope must be tenant-owned and narrow.", correlation_id
                )
            )
        normalized_criteria = tuple(item.strip() for item in criteria if item.strip())
        if not normalized_criteria or len(set(normalized_criteria)) != len(
            normalized_criteria
        ):
            return Result.failure(
                self._validation(
                    "Canary criteria must be unique and non-empty.", correlation_id
                )
            )
        variant = self._repository.get_variant(organization_id, variant_id)
        rollback = self._repository.get_rollback(organization_id, rollback_record_id)
        if not variant.is_success:
            return self._repository_failure(variant.error, correlation_id)
        if not rollback.is_success or self._value(rollback).variant_id != variant_id:
            return Result.failure(
                self._validation(
                    "Canary requires its variant rollback plan.", correlation_id
                )
            )
        timestamp = self._clock()
        record = CanaryRecord(
            self._metadata(organization_id, correlation_id, timestamp),
            CanaryId(str(new_record_id())),
            variant_id,
            scope,
            normalized_criteria,
            (),
            rollback_record_id,
            CanaryState.APPROVED,
            actor_id,
            timestamp,
        )
        return self._repository.create_canary(record)

    def activate_canary(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        canary_id: CanaryId,
    ) -> Result[CanaryRecord, ErrorDetail]:
        """Activate only an approved canary; approval alone remains inert."""
        current = self._repository.get_canary(organization_id, canary_id)
        if not current.is_success:
            return self._repository_failure(current.error, correlation_id)
        canary = self._value(current)
        if canary.state is not CanaryState.APPROVED:
            return Result.failure(
                self._validation(
                    "Only an approved inactive canary can activate.", correlation_id
                )
            )
        if (
            self._repository.active_canary_for_variant(
                organization_id, canary.variant_id
            )
            is not None
        ):
            return Result.failure(
                self._validation(
                    "A canary is already active for this variant.", correlation_id
                )
            )
        updated = replace(
            canary,
            metadata=self._next_metadata(canary.metadata, correlation_id),
            state=CanaryState.ACTIVE,
        )
        return self._repository.transition_canary(updated)

    def authorize_canary_operation(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        canary_id: CanaryId,
        requested_scope: CanaryScope,
    ) -> Result[bool, ErrorDetail]:
        """Authorize only a no-effect operation that is contained in active canary scope."""
        canary = self._repository.get_canary(organization_id, canary_id)
        if not canary.is_success:
            return self._repository_failure(canary.error, correlation_id)
        record = self._value(canary)
        allowed = record.state is CanaryState.ACTIVE and record.scope.contains(
            requested_scope
        )
        if not allowed:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.AUTHORIZATION_DENIED,
                    "Canary operation is outside its approved active scope.",
                    correlation_id,
                )
            )
        return Result.success(True)

    def record_canary_criterion(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        canary_id: CanaryId,
        criterion: str,
        passed: bool,
        evidence_reference: str,
    ) -> Result[CanaryRecord, ErrorDetail]:
        """Record criterion evidence; failure atomically stops the canary and rolls back."""
        current = self._repository.get_canary(organization_id, canary_id)
        if not current.is_success:
            return self._repository_failure(current.error, correlation_id)
        canary = self._value(current)
        if canary.state is not CanaryState.ACTIVE or criterion not in canary.criteria:
            return Result.failure(
                self._validation(
                    "Canary criterion is not active or not configured.", correlation_id
                )
            )
        if not evidence_reference.strip():
            return Result.failure(
                self._validation(
                    "Canary evidence reference is required.", correlation_id
                )
            )
        result = CanaryCriterionResult(
            criterion, passed, evidence_reference, self._clock()
        )
        updated = replace(
            canary,
            metadata=self._next_metadata(
                canary.metadata, correlation_id, result.recorded_at
            ),
            criterion_results=(*canary.criterion_results, result),
            state=CanaryState.ACTIVE if passed else CanaryState.STOPPED,
        )
        if passed:
            return self._repository.transition_canary(updated)
        rollback_result = self._repository.get_rollback(
            organization_id, canary.rollback_record_id
        )
        if not rollback_result.is_success:
            return self._repository_failure(rollback_result.error, correlation_id)
        rollback = self._value(rollback_result)
        performed = replace(
            rollback,
            metadata=self._next_metadata(
                rollback.metadata, correlation_id, result.recorded_at
            ),
            status=RollbackStatus.PERFORMED,
            performed_at=result.recorded_at,
            failure_evidence=evidence_reference,
        )
        stopped = self._repository.stop_canary_and_perform_rollback(updated, performed)
        if not stopped.is_success:
            return self._repository_failure(stopped.error, correlation_id)
        return Result.success(self._value(stopped)[0])

    def assess_promotion(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        requested_variant_id: SandboxVariantId | None,
        evaluation_run_id: EvaluationRunId,
        target_metric: MetricComparison,
        safety: MetricComparison,
        compliance: MetricComparison,
        rollback_record_id: RollbackRecordId,
        canary_id: CanaryId,
        audit_record_ids: Sequence[str],
        evidence_references: Sequence[str],
        approval_id: PromotionApprovalId,
    ) -> Result[PromotionAssessment, ErrorDetail]:
        """Assess exactly one candidate; a permitted result still leaves production untouched."""
        candidates = tuple(
            variant
            for variant in self._repository.variants_for_organization(organization_id)
            if variant.state is SandboxVariantState.UNDER_CONSIDERATION
        )
        candidate = candidates[0] if len(candidates) == 1 else None
        conditions = self._promotion_conditions(
            organization_id,
            candidate,
            requested_variant_id,
            evaluation_run_id,
            target_metric,
            safety,
            compliance,
            rollback_record_id,
            canary_id,
            audit_record_ids,
            evidence_references,
            approval_id,
            len(candidates),
        )
        missing = tuple(
            condition.name for condition in conditions if not condition.passed
        )
        record = PromotionAssessment(
            self._metadata(organization_id, correlation_id),
            PromotionAssessmentId(str(new_record_id())),
            candidate.variant_id if candidate is not None else None,
            len(candidates),
            str(evaluation_run_id),
            target_metric,
            safety,
            compliance,
            conditions,
            missing,
            PromotionDecision.PERMITTED if not missing else PromotionDecision.BLOCKED,
        )
        persisted = self._repository.append_assessment(record)
        if not persisted.is_success:
            return self._repository_failure(persisted.error, correlation_id)
        return persisted

    @staticmethod
    def _references(values: Sequence[str], name: str) -> tuple[str, ...]:
        references = tuple(str(value) for value in values)
        if any(not reference.strip() for reference in references):
            raise ValueError(f"{name} references must be non-empty.")
        if len(references) != len(set(references)):
            raise ValueError(f"{name} references must be unique.")
        return references

    @staticmethod
    def _missing_proposal_evidence(
        proposal: ImprovementProposal, *, include_promotion_evidence: bool = True
    ) -> tuple[str, ...]:
        required = {
            "source_evidence": proposal.source_evidence,
            "validation_evidence": proposal.validation_evidence,
            "evaluation_evidence": proposal.evaluation_evidence,
        }
        if include_promotion_evidence:
            required.update(
                {
                    "approval_evidence": proposal.approval_evidence,
                    "rollback_evidence": proposal.rollback_evidence,
                }
            )
        return tuple(name for name, references in required.items() if not references)

    def _promotion_conditions(
        self,
        organization_id: OrganizationId,
        candidate: SandboxVariant | None,
        requested_variant_id: SandboxVariantId | None,
        evaluation_run_id: EvaluationRunId,
        target_metric: MetricComparison,
        safety: MetricComparison,
        compliance: MetricComparison,
        rollback_record_id: RollbackRecordId,
        canary_id: CanaryId,
        audit_record_ids: Sequence[str],
        evidence_references: Sequence[str],
        approval_id: PromotionApprovalId,
        candidate_count: int,
    ) -> tuple[PromotionCondition, ...]:
        """Evaluate every required promotion condition independently and fail closed."""
        one_candidate = candidate is not None and candidate_count == 1
        selected = (
            candidate is not None
            and one_candidate
            and requested_variant_id == candidate.variant_id
        )
        evaluation = self._evaluation_for(organization_id, evaluation_run_id)
        target_improved = selected and self._strictly_improved(candidate, target_metric)
        if evaluation is None:
            evaluation_permitted = False
            regression_passed = False
            adversarial_passed = False
        else:
            evaluation_permitted = (
                evaluation.completed and evaluation.transition_permitted
            )
            regression_passed = evaluation_permitted and self._checks_pass(
                evaluation, EvaluationCheckKind.REGRESSION
            )
            adversarial_passed = evaluation_permitted and self._checks_pass(
                evaluation, EvaluationCheckKind.ADVERSARIAL
            )
        safety_no_worse = self._no_worse(safety)
        compliance_no_worse = self._no_worse(compliance)
        rollback_passed = self._valid_rollback(
            organization_id, candidate, rollback_record_id
        )
        canary_passed = self._valid_canary(
            organization_id, candidate, canary_id, rollback_record_id
        )
        approval_passed = self._valid_approval(organization_id, candidate, approval_id)
        audit_complete = bool(audit_record_ids) and all(
            value.strip() for value in audit_record_ids
        )
        evidence_retained = bool(evidence_references) and all(
            value.strip() for value in evidence_references
        )
        return (
            PromotionCondition("exactly_one_candidate", one_candidate and selected, ()),
            PromotionCondition("target_metric_strictly_improved", target_improved, ()),
            PromotionCondition("safety_no_worse", safety_no_worse, ()),
            PromotionCondition("compliance_no_worse", compliance_no_worse, ()),
            PromotionCondition(
                "named_regression_checks_pass",
                regression_passed,
                (str(evaluation_run_id),),
            ),
            PromotionCondition(
                "named_adversarial_checks_pass",
                adversarial_passed,
                (str(evaluation_run_id),),
            ),
            PromotionCondition(
                "rollback_plan_recorded", rollback_passed, (str(rollback_record_id),)
            ),
            PromotionCondition(
                "approved_scoped_canary", canary_passed, (str(canary_id),)
            ),
            PromotionCondition(
                "complete_audit_records", audit_complete, tuple(audit_record_ids)
            ),
            PromotionCondition(
                "evidence_retained", evidence_retained, tuple(evidence_references)
            ),
            PromotionCondition(
                "recorded_human_approval", approval_passed, (str(approval_id),)
            ),
        )

    def _evaluation_for(
        self, organization_id: OrganizationId, evaluation_run_id: EvaluationRunId
    ) -> EvaluationRun | None:
        return next(
            (
                record
                for record in self._evaluation_repository.records()
                if record.metadata.organization_id == organization_id
                and record.evaluation_run_id == evaluation_run_id
            ),
            None,
        )

    @staticmethod
    def _checks_pass(evaluation: EvaluationRun, kind: EvaluationCheckKind) -> bool:
        expected = tuple(check for check in evaluation.checks if check.kind is kind)
        matching = tuple(
            result for result in evaluation.results if result.check_kind is kind
        )
        return (
            bool(expected)
            and bool(matching)
            and all(result.outcome is EvaluationOutcome.PASS for result in matching)
        )

    def _valid_rollback(
        self,
        organization_id: OrganizationId,
        candidate: SandboxVariant | None,
        rollback_record_id: RollbackRecordId,
    ) -> bool:
        if candidate is None:
            return False
        rollback = self._repository.get_rollback(organization_id, rollback_record_id)
        return bool(
            rollback.is_success
            and rollback.value is not None
            and rollback.value.variant_id == candidate.variant_id
            and rollback.value.status
            in {RollbackStatus.PLANNED, RollbackStatus.PERFORMED}
        )

    def _valid_canary(
        self,
        organization_id: OrganizationId,
        candidate: SandboxVariant | None,
        canary_id: CanaryId,
        rollback_record_id: RollbackRecordId,
    ) -> bool:
        if candidate is None:
            return False
        canary = self._repository.get_canary(organization_id, canary_id)
        return bool(
            canary.is_success
            and canary.value is not None
            and canary.value.variant_id == candidate.variant_id
            and canary.value.rollback_record_id == rollback_record_id
            and canary.value.state in {CanaryState.APPROVED, CanaryState.ACTIVE}
        )

    def _valid_approval(
        self,
        organization_id: OrganizationId,
        candidate: SandboxVariant | None,
        approval_id: PromotionApprovalId,
    ) -> bool:
        if candidate is None:
            return False
        approval = self._repository.get_approval(organization_id, approval_id)
        return bool(
            approval.is_success
            and approval.value is not None
            and approval.value.variant_id == candidate.variant_id
        )

    @staticmethod
    def _strictly_improved(
        candidate: SandboxVariant | None, comparison: MetricComparison
    ) -> bool:
        if candidate is None or not EvolutionService._finite(comparison):
            return False
        if candidate.improvement_direction is ImprovementDirection.INCREASE:
            return comparison.candidate > comparison.baseline
        return comparison.candidate < comparison.baseline

    @staticmethod
    def _no_worse(comparison: MetricComparison) -> bool:
        return (
            EvolutionService._finite(comparison)
            and comparison.candidate >= comparison.baseline
        )

    @staticmethod
    def _finite(comparison: MetricComparison) -> bool:
        return math.isfinite(comparison.baseline) and math.isfinite(
            comparison.candidate
        )

    def _metadata(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        timestamp: datetime | None = None,
    ) -> RecordMetadata:
        recorded_at = timestamp or self._clock()
        return RecordMetadata(
            new_record_id(),
            organization_id,
            correlation_id,
            SCHEMA_VERSION,
            1,
            recorded_at,
            recorded_at,
        )

    def _next_metadata(
        self,
        metadata: RecordMetadata,
        correlation_id: CorrelationId,
        timestamp: datetime | None = None,
    ) -> RecordMetadata:
        return replace(
            metadata,
            correlation_id=correlation_id,
            version=metadata.version + 1,
            updated_at=timestamp or self._clock(),
        )

    @staticmethod
    def _canonical_json(value: Mapping[str, object]) -> str:
        try:
            return json.dumps(
                value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
            )
        except (TypeError, ValueError) as error:
            raise ValueError(
                "Evolution configuration must be JSON serializable."
            ) from error

    @staticmethod
    def _contains_host_code(value: object) -> bool:
        if isinstance(value, Mapping):
            return any(
                str(key).lower().replace("-", "_") in {"host_code", "host_source"}
                or EvolutionService._contains_host_code(item)
                for key, item in value.items()
            )
        if isinstance(value, list):
            return any(EvolutionService._contains_host_code(item) for item in value)
        return False

    @staticmethod
    def _digest(value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    @staticmethod
    def _validation(message: str, correlation_id: CorrelationId) -> ErrorDetail:
        return ErrorDetail(ErrorCode.VALIDATION_FAILED, message, correlation_id)

    @staticmethod
    def _value[T](result: Result[T, ErrorDetail]) -> T:
        if result.value is None:
            raise RuntimeError("Successful evolution operation had no value.")
        return result.value

    @staticmethod
    def _repository_failure[T](
        error: ErrorDetail | None, correlation_id: CorrelationId
    ) -> Result[T, ErrorDetail]:
        if error is None:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.REPOSITORY_UNAVAILABLE,
                    "Evolution storage failed.",
                    correlation_id,
                )
            )
        return Result.failure(
            ErrorDetail(
                error.code, error.message, correlation_id, error.retryable, error.fields
            )
        )
