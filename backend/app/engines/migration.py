"""All-evidence migration assessment and one-way LegacyEngine retirement."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from threading import RLock
from typing import Protocol
from weakref import WeakValueDictionary

from app.engines.recovery import (
    ContractChangeApproval,
    ContractChangeEvidence,
    MigrationRollbackEvidence,
    MigrationRollbackRequest,
    RecoveryService,
)
from app.evaluation.migration_evidence import (
    ActivationApproval,
    LegacyRetirementEvidence,
    MigrationEvidenceService,
    MigrationGateAssessment,
    MigrationGateEvidence,
    MigrationPhaseRecord,
    WorkflowActivationEvidence,
    WorkflowActivationRecord,
)
from app.models.contracts import ErrorCode, ErrorDetail, Result
from app.models.control_plane import RecoveryAction, RecoveryActionId
from app.models.evidence import EvidenceReference, Lesson
from app.models.identifiers import CorrelationId, DomainPackId, OrganizationId, RunId


class LegacyExecutionAvailability(Protocol):
    """Shared guard required by queueing, dispatch, and LegacyEngine execution."""

    def is_available(self) -> bool:
        """Return whether a new LegacyEngine execution may start."""

    def begin_legacy_execution(
        self,
        organization_id: OrganizationId,
        run_id: RunId,
        correlation_id: CorrelationId,
    ) -> Result[LegacyExecutionLease, ErrorDetail]:
        """Atomically admit an active legacy execution or reject retirement."""


class LegacyExecutionLease:
    """A live legacy execution observed and cancelled by the retirement registry."""

    def __init__(self, organization_id: OrganizationId, run_id: RunId) -> None:
        self.organization_id = organization_id
        self.run_id = run_id
        self._retirement: LegacyRetirementEvidence | None = None

    @property
    def retirement_evidence(self) -> LegacyRetirementEvidence | None:
        """Return retained retirement evidence when this active execution was disabled."""
        return self._retirement

    def retire(self, evidence: LegacyRetirementEvidence) -> None:
        """Cancel this execution without permitting a further legacy step."""
        self._retirement = evidence


@dataclass(frozen=True, slots=True)
class LegacyRetirementOutcome:
    """Result of assessing the gate and, only when satisfied, retiring LegacyEngine."""

    assessment: MigrationGateAssessment
    retirement_evidence: LegacyRetirementEvidence | None
    retired_now: bool


class LegacyEngineRetirement:
    """Atomically retires LegacyEngine after all current evidence gates pass.

    The registry does not deploy, roll back, or re-enable an engine. A retained retirement
    decision is intentionally one-way; restoration requires a separately reviewed release.
    """

    def __init__(self, evidence_service: MigrationEvidenceService) -> None:
        self._evidence_service = evidence_service
        self._lock = RLock()
        try:
            self._retirement = evidence_service.latest_retirement()
            self._evidence_state_unavailable = False
        except Exception:
            # A missing durable state cannot prove that retirement happened. Keep the
            # guard fail-closed until a later assessment can re-read the repository.
            self._retirement = None
            self._evidence_state_unavailable = True
        self._retired = self._retirement is not None
        self._active: WeakValueDictionary[tuple[OrganizationId, RunId], LegacyExecutionLease] = (
            WeakValueDictionary()
        )

    @property
    def retirement_evidence(self) -> LegacyRetirementEvidence | None:
        """Return the durable one-way retirement decision, when present."""
        with self._lock:
            return self._retirement

    def is_available(self) -> bool:
        """Return whether durable state permits a new LegacyEngine execution."""
        with self._lock:
            return not self._retired and not self._evidence_state_unavailable

    def begin_legacy_execution(
        self,
        organization_id: OrganizationId,
        run_id: RunId,
        correlation_id: CorrelationId,
    ) -> Result[LegacyExecutionLease, ErrorDetail]:
        """Register an active execution under the same lock used by retirement."""
        with self._lock:
            if self._evidence_state_unavailable:
                return Result.failure(self._unavailable_error(correlation_id))
            if self._retired:
                return Result.failure(self._retired_error(correlation_id))
            if not str(organization_id).strip() or not str(run_id).strip():
                return Result.failure(
                    ErrorDetail(
                        ErrorCode.VALIDATION_FAILED,
                        "Legacy execution admission requires organization and run identifiers.",
                        correlation_id,
                    )
                )
            lease = LegacyExecutionLease(organization_id, run_id)
            self._active[(organization_id, run_id)] = lease
            return Result.success(lease)

    def assess_and_retire(
        self,
        correlation_id: CorrelationId,
        configuration_digest: str,
        gates: Sequence[MigrationGateEvidence],
    ) -> Result[LegacyRetirementOutcome, ErrorDetail]:
        """Retain assessment evidence and retire immediately only on full conjunction."""
        try:
            assessment_result = self._evidence_service.assess(
                correlation_id, configuration_digest, gates
            )
        except Exception:
            return Result.failure(self._unavailable_error(correlation_id))
        if not assessment_result.is_success:
            return Result.failure(self._error(assessment_result.error, correlation_id))
        if assessment_result.value is None:
            raise RuntimeError("Successful migration assessment had no result.")
        assessment = assessment_result.value
        with self._lock:
            if self._evidence_state_unavailable:
                try:
                    self._retirement = self._evidence_service.latest_retirement()
                except Exception:
                    return Result.failure(self._unavailable_error(correlation_id))
                self._evidence_state_unavailable = False
                self._retired = self._retirement is not None
            if self._retirement is not None:
                return Result.success(LegacyRetirementOutcome(assessment, self._retirement, False))
            if not assessment.is_satisfied:
                return Result.success(LegacyRetirementOutcome(assessment, None, False))
            active_run_ids = tuple(lease.run_id for lease in self._active.values())
            try:
                retained = self._evidence_service.record_retirement(
                    correlation_id, assessment, active_run_ids
                )
            except Exception:
                return Result.failure(self._unavailable_error(correlation_id))
            if not retained.is_success:
                return Result.failure(self._error(retained.error, correlation_id))
            if retained.value is None:
                raise RuntimeError("Successful LegacyEngine retirement had no evidence.")
            self._retirement = retained.value
            self._retired = True
            for lease in tuple(self._active.values()):
                lease.retire(retained.value)
            return Result.success(LegacyRetirementOutcome(assessment, retained.value, True))

    @staticmethod
    def retirement_reference(evidence: LegacyRetirementEvidence) -> EvidenceReference:
        """Create failure-safe evidence linked to the durable retirement decision."""
        return EvidenceReference(
            evidence_id=evidence.evidence_id,
            digest=evidence.configuration_digest,
            kind="legacy-engine-retirement",
        )

    @staticmethod
    def _retired_error(correlation_id: CorrelationId) -> ErrorDetail:
        return ErrorDetail(
            ErrorCode.INVALID_TRANSITION,
            "LegacyEngine is unavailable because migration retirement evidence is retained.",
            correlation_id,
        )

    @staticmethod
    def _unavailable_error(correlation_id: CorrelationId) -> ErrorDetail:
        return ErrorDetail(
            ErrorCode.REPOSITORY_UNAVAILABLE,
            "Migration evidence storage is unavailable; LegacyEngine remains blocked.",
            correlation_id,
            retryable=True,
        )

    @staticmethod
    def _error(error: ErrorDetail | None, correlation_id: CorrelationId) -> ErrorDetail:
        if error is None:
            return ErrorDetail(
                ErrorCode.REPOSITORY_UNAVAILABLE,
                "Migration evidence storage is unavailable.",
                correlation_id,
            )
        return ErrorDetail(
            error.code,
            error.message,
            correlation_id,
            retryable=error.retryable,
            fields=error.fields,
        )


class MigrationController:
    """Coordinate durable migration phases and fail-closed VA activation gates."""

    def __init__(
        self,
        evidence_service: MigrationEvidenceService,
        recovery_service: RecoveryService | None = None,
    ) -> None:
        self._evidence_service = evidence_service
        self._recovery_service = recovery_service

    def start_phase(
        self,
        correlation_id: CorrelationId,
        phase_id: str,
        phase_scope: Sequence[str],
        required_evidence: Sequence[str],
        exit_criteria: Sequence[str],
        rollback_procedure: str,
        host_owner_review: str,
        va_owner_review: str,
    ) -> Result[MigrationPhaseRecord, ErrorDetail]:
        """Create and retain all required phase scope, exit, rollback, and review fields."""
        return self._evidence_service.record_phase(
            correlation_id,
            phase_id,
            phase_scope,
            required_evidence,
            exit_criteria,
            rollback_procedure,
            host_owner_review,
            va_owner_review,
        )

    def evaluate_activation_eligibility(
        self,
        correlation_id: CorrelationId,
        evidence: WorkflowActivationEvidence,
    ) -> Result[WorkflowActivationRecord, ErrorDetail]:
        """Record Activation_Eligible only when every declared evidence gate passes."""
        return self._evidence_service.evaluate_activation_eligibility(correlation_id, evidence)

    def approve_activation(
        self,
        correlation_id: CorrelationId,
        approval_id: str,
        workflow_id: str,
        reviewer_identity: str,
        decision_reason: str,
        approved: bool = True,
    ) -> Result[ActivationApproval, ErrorDetail]:
        """Retain explicit activation approval separately from eligibility evidence."""
        return self._evidence_service.record_activation_approval(
            correlation_id,
            approval_id,
            workflow_id,
            reviewer_identity,
            decision_reason,
            approved,
        )

    def rollback(
        self,
        correlation_id: CorrelationId,
        request: MigrationRollbackRequest | None = None,
        *,
        organization_id: OrganizationId | None = None,
        pack_id: DomainPackId | None = None,
        designated_immutable_version: str | None = None,
        approval_reference: str | None = None,
        affected_lessons: Sequence[Lesson] = (),
        alc_retention_policy: str | None = None,
        evidence_references: Sequence[str] = (),
        rollback_id: str | None = None,
        approved: bool = False,
    ) -> Result[MigrationRollbackEvidence, ErrorDetail]:
        """Delegate an evidence-first migration rollback to the recovery service."""
        if self._recovery_service is None:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.REPOSITORY_UNAVAILABLE,
                    "Migration recovery service is not configured.",
                    correlation_id,
                )
            )
        return self._recovery_service.rollback(
            correlation_id,
            request,
            organization_id=organization_id,
            pack_id=pack_id,
            designated_immutable_version=designated_immutable_version,
            approval_reference=approval_reference,
            affected_lessons=affected_lessons,
            alc_retention_policy=alc_retention_policy,
            evidence_references=evidence_references,
            rollback_id=rollback_id,
            approved=approved,
        )

    def approve_contract_change(
        self,
        correlation_id: CorrelationId,
        evidence: ContractChangeEvidence | Mapping[str, object],
        *,
        change_id: str = "contract-breaking-change",
    ) -> Result[ContractChangeApproval, ErrorDetail]:
        """Approve contract-breaking changes only with the complete evidence vector."""
        if self._recovery_service is None:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.REPOSITORY_UNAVAILABLE,
                    "Migration recovery service is not configured.",
                    correlation_id,
                )
            )
        return self._recovery_service.approve_contract_change(
            correlation_id, evidence, change_id=change_id
        )

    def recover(
        self,
        correlation_id: CorrelationId,
        action: RecoveryAction | None = None,
        *,
        organization_id: OrganizationId | None = None,
        recovery_action_id: RecoveryActionId | None = None,
        pack_id: DomainPackId | None = None,
        designated_immutable_version: str | None = None,
        approval_reference: str | None = None,
        investigation_evidence_references: Sequence[str] = (),
        approved: bool = False,
    ) -> Result[RecoveryAction, ErrorDetail]:
        """Delegate evidence-gated Recovery_Action restoration."""
        if self._recovery_service is None:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.REPOSITORY_UNAVAILABLE,
                    "Migration recovery service is not configured.",
                    correlation_id,
                )
            )
        return self._recovery_service.recover(
            correlation_id,
            action,
            organization_id=organization_id,
            recovery_action_id=recovery_action_id,
            pack_id=pack_id,
            designated_immutable_version=designated_immutable_version,
            approval_reference=approval_reference,
            investigation_evidence_references=investigation_evidence_references,
            approved=approved,
        )

    # Design-level command aliases retain the integration vocabulary.
    approveContractChange = approve_contract_change  # noqa: N815
    evaluateContractChange = approve_contract_change  # noqa: N815
    recoverAction = recover  # noqa: N815


# Design-level aliases retained for callers that use the data-model names directly.
MigrationPhase = MigrationPhaseRecord
WorkflowActivation = WorkflowActivationRecord
ActivationEligibilityEvidence = WorkflowActivationEvidence
