"""Lock-protected local retention for sandbox-only evolution records."""

from __future__ import annotations

from threading import RLock
from typing import TypeVar

from app.evolution.models import (
    CanaryId,
    CanaryRecord,
    CanaryState,
    PromotionApprovalId,
    PromotionApprovalRecord,
    PromotionAssessment,
    PromotionAssessmentId,
    RollbackRecord,
    RollbackRecordId,
    SandboxVariant,
    SandboxVariantId,
)
from app.models.common import VersionedRecord
from app.models.contracts import ErrorCode, ErrorDetail, Result
from app.models.control_plane import AuditRecord, ImprovementProposal, ProposalId
from app.models.identifiers import CorrelationId, OrganizationId, RecordId

T = TypeVar("T", bound=VersionedRecord)


class InMemoryEvolutionRepository:
    """Append-only assessments plus versioned sandbox and canary lifecycle records."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._variants: dict[SandboxVariantId, SandboxVariant] = {}
        self._rollbacks: dict[RollbackRecordId, RollbackRecord] = {}
        self._canaries: dict[CanaryId, CanaryRecord] = {}
        self._assessments: dict[PromotionAssessmentId, PromotionAssessment] = {}
        self._approvals: dict[PromotionApprovalId, PromotionApprovalRecord] = {}
        self._improvement_proposals: dict[ProposalId, ImprovementProposal] = {}
        self._improvement_proposal_history: dict[
            ProposalId, tuple[ImprovementProposal, ...]
        ] = {}
        self._promotion_audits: dict[str, AuditRecord] = {}
        self._record_ids: set[RecordId] = set()
        self._promotion_blocked = True

    def create_variant(
        self, record: SandboxVariant
    ) -> Result[SandboxVariant, ErrorDetail]:
        """Persist a sandbox variant without touching its production baseline."""
        with self._lock:
            if record.variant_id in self._variants or not self._claim(
                record.metadata.record_id
            ):
                return Result.failure(
                    self._error(ErrorCode.CONFLICT, "Sandbox variant already exists.")
                )
            self._variants[record.variant_id] = record
            self._promotion_blocked = True
            return Result.success(record)

    def create_improvement_proposal(
        self, record: ImprovementProposal
    ) -> Result[ImprovementProposal, ErrorDetail]:
        """Append the first proposal snapshot before sandbox work is attempted."""
        with self._lock:
            if record.proposal_id in self._improvement_proposals or not self._claim(
                record.metadata.record_id
            ):
                return Result.failure(
                    self._error(
                        ErrorCode.CONFLICT, "Improvement proposal already exists."
                    )
                )
            self._improvement_proposals[record.proposal_id] = record
            self._improvement_proposal_history[record.proposal_id] = (record,)
            self._promotion_blocked = True
            return Result.success(record)

    def get_improvement_proposal(
        self, organization_id: OrganizationId, proposal_id: ProposalId
    ) -> Result[ImprovementProposal, ErrorDetail]:
        """Return the current proposal snapshot only within its owning organization."""
        with self._lock:
            return self._scoped(
                self._improvement_proposals.get(proposal_id),
                organization_id,
                "Improvement proposal",
            )

    def transition_improvement_proposal(
        self, record: ImprovementProposal
    ) -> Result[ImprovementProposal, ErrorDetail]:
        """Append a versioned proposal transition while retaining every prior snapshot."""
        with self._lock:
            current = self._improvement_proposals.get(record.proposal_id)
            if not self._matches(current, record):
                return Result.failure(
                    self._error(
                        ErrorCode.CONFLICT, "Improvement proposal transition conflicts."
                    )
                )
            self._improvement_proposals[record.proposal_id] = record
            history = self._improvement_proposal_history[record.proposal_id]
            self._improvement_proposal_history[record.proposal_id] = (*history, record)
            self._promotion_blocked = record.promotion_state.value != "promoted"
            return Result.success(record)

    def improvement_proposal_history(
        self, organization_id: OrganizationId, proposal_id: ProposalId
    ) -> tuple[ImprovementProposal, ...]:
        """Return immutable proposal snapshots for an organization-scoped proposal."""
        with self._lock:
            current = self._improvement_proposals.get(proposal_id)
            if current is None or current.metadata.organization_id != organization_id:
                return ()
            return self._improvement_proposal_history.get(proposal_id, ())

    def promote_improvement_proposal(
        self, record: ImprovementProposal, audit: AuditRecord
    ) -> Result[ImprovementProposal, ErrorDetail]:
        """Commit a promoted snapshot and its audit as one local repository operation."""
        with self._lock:
            current = self._improvement_proposals.get(record.proposal_id)
            if not self._matches(current, record):
                return Result.failure(
                    self._error(
                        ErrorCode.CONFLICT, "Improvement proposal promotion conflicts."
                    )
                )
            if audit.metadata.organization_id != record.metadata.organization_id:
                return Result.failure(
                    self._error(
                        ErrorCode.AUTHORIZATION_DENIED,
                        "Promotion audit scope conflicts.",
                    )
                )
            if audit.audit_id in self._promotion_audits:
                return Result.failure(
                    self._error(ErrorCode.CONFLICT, "Promotion audit already exists.")
                )
            if audit.subject_reference != str(record.proposal_id):
                return Result.failure(
                    self._error(
                        ErrorCode.VALIDATION_FAILED,
                        "Promotion audit subject is invalid.",
                    )
                )
            self._improvement_proposals[record.proposal_id] = record
            history = self._improvement_proposal_history[record.proposal_id]
            self._improvement_proposal_history[record.proposal_id] = (*history, record)
            self._promotion_audits[audit.audit_id] = audit
            self._promotion_blocked = False
            return Result.success(record)

    def promotion_audits(
        self, organization_id: OrganizationId
    ) -> tuple[AuditRecord, ...]:
        """Return promotion audits without exposing another organization's records."""
        with self._lock:
            return tuple(
                audit
                for audit in self._promotion_audits.values()
                if audit.metadata.organization_id == organization_id
            )

    def get_variant(
        self, organization_id: OrganizationId, variant_id: SandboxVariantId
    ) -> Result[SandboxVariant, ErrorDetail]:
        """Return one organization-scoped sandbox variant."""
        with self._lock:
            return self._scoped(
                self._variants.get(variant_id), organization_id, "Sandbox variant"
            )

    def variants_for_organization(
        self, organization_id: OrganizationId
    ) -> tuple[SandboxVariant, ...]:
        with self._lock:
            return tuple(
                record
                for record in self._variants.values()
                if record.metadata.organization_id == organization_id
            )

    def transition_variant(
        self, record: SandboxVariant
    ) -> Result[SandboxVariant, ErrorDetail]:
        """Compare-and-swap a lifecycle-only variant transition."""
        with self._lock:
            current = self._variants.get(record.variant_id)
            if not self._matches(current, record):
                return Result.failure(
                    self._error(
                        ErrorCode.CONFLICT, "Sandbox variant transition conflicts."
                    )
                )
            self._variants[record.variant_id] = record
            self._promotion_blocked = True
            return Result.success(record)

    def create_rollback(
        self, record: RollbackRecord
    ) -> Result[RollbackRecord, ErrorDetail]:
        """Persist a unique predeclared rollback plan."""
        with self._lock:
            if (
                record.rollback_record_id in self._rollbacks
                or record.variant_id not in self._variants
                or not self._claim(record.metadata.record_id)
            ):
                return Result.failure(
                    self._error(
                        ErrorCode.CONFLICT,
                        "Rollback record already exists or is invalid.",
                    )
                )
            self._rollbacks[record.rollback_record_id] = record
            return Result.success(record)

    def get_rollback(
        self, organization_id: OrganizationId, rollback_id: RollbackRecordId
    ) -> Result[RollbackRecord, ErrorDetail]:
        with self._lock:
            return self._scoped(
                self._rollbacks.get(rollback_id), organization_id, "Rollback record"
            )

    def transition_rollback(
        self, record: RollbackRecord
    ) -> Result[RollbackRecord, ErrorDetail]:
        """Compare-and-swap a rollback lifecycle transition."""
        with self._lock:
            current = self._rollbacks.get(record.rollback_record_id)
            if not self._matches(current, record):
                return Result.failure(
                    self._error(ErrorCode.CONFLICT, "Rollback transition conflicts.")
                )
            self._rollbacks[record.rollback_record_id] = record
            return Result.success(record)

    def create_canary(self, record: CanaryRecord) -> Result[CanaryRecord, ErrorDetail]:
        """Persist approved-but-inactive canary state."""
        with self._lock:
            if (
                record.canary_id in self._canaries
                or record.variant_id not in self._variants
                or record.rollback_record_id not in self._rollbacks
                or not self._claim(record.metadata.record_id)
            ):
                return Result.failure(
                    self._error(
                        ErrorCode.CONFLICT,
                        "Canary record already exists or is invalid.",
                    )
                )
            self._canaries[record.canary_id] = record
            self._promotion_blocked = True
            return Result.success(record)

    def get_canary(
        self, organization_id: OrganizationId, canary_id: CanaryId
    ) -> Result[CanaryRecord, ErrorDetail]:
        with self._lock:
            return self._scoped(
                self._canaries.get(canary_id), organization_id, "Canary"
            )

    def active_canary_for_variant(
        self, organization_id: OrganizationId, variant_id: SandboxVariantId
    ) -> CanaryRecord | None:
        with self._lock:
            return next(
                (
                    record
                    for record in self._canaries.values()
                    if record.metadata.organization_id == organization_id
                    and record.variant_id == variant_id
                    and record.state is CanaryState.ACTIVE
                ),
                None,
            )

    def transition_canary(
        self, record: CanaryRecord
    ) -> Result[CanaryRecord, ErrorDetail]:
        """Compare-and-swap a canary transition and preserve a production block."""
        with self._lock:
            current = self._canaries.get(record.canary_id)
            if not self._matches(current, record):
                return Result.failure(
                    self._error(ErrorCode.CONFLICT, "Canary transition conflicts.")
                )
            self._canaries[record.canary_id] = record
            self._promotion_blocked = True
            return Result.success(record)

    def stop_canary_and_perform_rollback(
        self,
        canary: CanaryRecord,
        rollback: RollbackRecord,
    ) -> Result[tuple[CanaryRecord, RollbackRecord], ErrorDetail]:
        """Atomically stop a failed canary and retain rollback completion evidence."""
        with self._lock:
            current_canary = self._canaries.get(canary.canary_id)
            current_rollback = self._rollbacks.get(rollback.rollback_record_id)
            if not self._matches(current_canary, canary) or not self._matches(
                current_rollback, rollback
            ):
                return Result.failure(
                    self._error(
                        ErrorCode.CONFLICT, "Canary rollback transition conflicts."
                    )
                )
            self._canaries[canary.canary_id] = canary
            self._rollbacks[rollback.rollback_record_id] = rollback
            self._promotion_blocked = True
            return Result.success((canary, rollback))

    def create_approval(
        self, record: PromotionApprovalRecord
    ) -> Result[PromotionApprovalRecord, ErrorDetail]:
        """Retain human promotion approval independently from every assessment."""
        with self._lock:
            if (
                record.approval_id in self._approvals
                or record.variant_id not in self._variants
                or not self._claim(record.metadata.record_id)
            ):
                return Result.failure(
                    self._error(
                        ErrorCode.CONFLICT,
                        "Promotion approval already exists or is invalid.",
                    )
                )
            self._approvals[record.approval_id] = record
            self._promotion_blocked = True
            return Result.success(record)

    def get_approval(
        self, organization_id: OrganizationId, approval_id: PromotionApprovalId
    ) -> Result[PromotionApprovalRecord, ErrorDetail]:
        with self._lock:
            return self._scoped(
                self._approvals.get(approval_id), organization_id, "Promotion approval"
            )

    def append_assessment(
        self, record: PromotionAssessment
    ) -> Result[PromotionAssessment, ErrorDetail]:
        """Append an immutable promotion decision and atomically update its guard latch."""
        with self._lock:
            if record.assessment_id in self._assessments or not self._claim(
                record.metadata.record_id
            ):
                return Result.failure(
                    self._error(
                        ErrorCode.CONFLICT, "Promotion assessment already exists."
                    )
                )
            self._assessments[record.assessment_id] = record
            self._promotion_blocked = record.decision.value != "permitted"
            return Result.success(record)

    def promotion_permitted(
        self, organization_id: OrganizationId, assessment_id: PromotionAssessmentId
    ) -> bool:
        """Return a permission only for a retained local assessment in this organization."""
        with self._lock:
            assessment = self._assessments.get(assessment_id)
            return bool(
                assessment is not None
                and assessment.metadata.organization_id == organization_id
                and not self._promotion_blocked
                and assessment.decision.value == "permitted"
            )

    def _claim(self, record_id: RecordId) -> bool:
        if record_id in self._record_ids:
            return False
        self._record_ids.add(record_id)
        return True

    @staticmethod
    def _matches(current: T | None, next_record: T) -> bool:
        if current is None:
            return False
        current_metadata = current.metadata
        next_metadata = next_record.metadata
        return (
            current_metadata.record_id == next_metadata.record_id
            and current_metadata.organization_id == next_metadata.organization_id
            and next_metadata.version == current_metadata.version + 1
        )

    @staticmethod
    def _scoped(
        record: T | None, organization_id: OrganizationId, name: str
    ) -> Result[T, ErrorDetail]:
        if record is None or record.metadata.organization_id != organization_id:
            return Result.failure(
                InMemoryEvolutionRepository._error(
                    ErrorCode.NOT_FOUND, f"{name} was not found."
                )
            )
        return Result.success(record)

    @staticmethod
    def _error(code: ErrorCode, message: str) -> ErrorDetail:
        return ErrorDetail(code, message, CorrelationId("evolution-repository"))
