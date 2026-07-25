"""Directed critique retention and evidence-bound approval gate evaluation."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass, replace
from datetime import datetime

from app.models.common import RecordMetadata, utc_now
from app.models.contracts import ErrorCode, ErrorDetail, Result
from app.models.control_plane import (
    AgentTask,
    ApprovalGate,
    ApprovalGateId,
    ApprovalGateStatus,
    CritiqueRecord,
    QualityEvidence,
    QualityEvidenceKind,
    TaskId,
    TaskLifecycle,
)
from app.models.identifiers import CorrelationId, OrganizationId
from app.repositories.control_plane import ControlPlaneUnitOfWork


@dataclass(frozen=True, slots=True)
class ApprovalSubmissionOutcome:
    """The retained gate and whether a human decision was valid and authorized."""

    gate: ApprovalGate
    accepted: bool


@dataclass(frozen=True, slots=True)
class GateRequirements:
    """Server-selected category and non-score checks required for one pending operation."""

    required_evidence_kinds: tuple[QualityEvidenceKind, ...] = tuple(QualityEvidenceKind)
    requires_rights_and_consent: bool = True
    requires_provenance: bool = True

    def __post_init__(self) -> None:
        if not self.required_evidence_kinds:
            raise ValueError("A gate must require at least one independently retained category.")
        if len(self.required_evidence_kinds) != len(set(self.required_evidence_kinds)):
            raise ValueError("A gate cannot require an evidence category more than once.")


@dataclass(frozen=True, slots=True)
class GateEvaluation:
    """A category-specific decision explaining whether an effect may progress."""

    gate: ApprovalGate
    subject_reference: str
    progression_permitted: bool
    missing_evidence_kinds: tuple[QualityEvidenceKind, ...]
    failed_evidence_kinds: tuple[QualityEvidenceKind, ...]
    rights_and_consent_passed: bool
    provenance_passed: bool
    authorization_rechecked: bool
    policy_rechecked: bool
    affected_task_id: TaskId | None


UnitOfWorkFactory = Callable[[], ControlPlaneUnitOfWork]
GateRecheck = Callable[[ApprovalGate], bool]


class EvidenceService:
    """Persist authorized directed critiques and independent evidence without aggregation."""

    def __init__(
        self,
        unit_of_work_factory: UnitOfWorkFactory,
        *,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._clock = clock

    def submit_critique(
        self,
        organization_id: OrganizationId,
        critique: CritiqueRecord,
        *,
        published_relationships: Iterable[str],
        human_review_authorized: bool,
    ) -> Result[CritiqueRecord, ErrorDetail]:
        """Retain a critique only along an authoritative published or human-review direction."""
        if critique.metadata.organization_id != organization_id:
            return Result.failure(self._unavailable(critique.metadata.correlation_id, "Critique"))
        permitted_relationships = frozenset(published_relationships)
        if (
            critique.relationship_reference not in permitted_relationships
            and not human_review_authorized
        ):
            return Result.failure(self._unavailable(critique.metadata.correlation_id, "Critique"))
        with self._unit_of_work_factory() as unit_of_work:
            appended = unit_of_work.evidence.append_critique(critique)
            return self._repository_result(appended, critique.metadata.correlation_id)

    def retain_quality_evidence(
        self,
        organization_id: OrganizationId,
        evidence: QualityEvidence,
    ) -> Result[QualityEvidence, ErrorDetail]:
        """Append one category result; categories are never combined into an aggregate score."""
        if evidence.metadata.organization_id != organization_id:
            return Result.failure(
                self._unavailable(evidence.metadata.correlation_id, "Quality evidence")
            )
        with self._unit_of_work_factory() as unit_of_work:
            appended = unit_of_work.evidence.append_quality(evidence)
            return self._repository_result(appended, evidence.metadata.correlation_id)

    def create_pending_gate(
        self,
        organization_id: OrganizationId,
        metadata: RecordMetadata,
        approval_gate_id: ApprovalGateId,
        pending_operation_reference: str,
    ) -> Result[ApprovalGate, ErrorDetail]:
        """Create the server-owned pending operation before any human decision is accepted."""
        if metadata.organization_id != organization_id:
            return Result.failure(self._unavailable(metadata.correlation_id, "Approval gate"))
        gate = ApprovalGate(
            metadata=metadata,
            approval_gate_id=approval_gate_id,
            pending_operation_reference=pending_operation_reference,
            status=ApprovalGateStatus.PENDING,
        )
        with self._unit_of_work_factory() as unit_of_work:
            appended = unit_of_work.evidence.append_approval(gate)
            return self._repository_result(appended, metadata.correlation_id)

    def submit_human_decision(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        approval_gate_id: ApprovalGateId,
        *,
        decision: str,
        decision_reason: str,
        reviewer_reference: str,
        reviewer_authorized: bool,
    ) -> Result[ApprovalSubmissionOutcome, ErrorDetail]:
        """Bind a valid human decision to its server-created pending operation only."""
        with self._unit_of_work_factory() as unit_of_work:
            stored = unit_of_work.evidence.get_approval(organization_id, approval_gate_id)
            gate = stored.value
            if not stored.is_success or gate is None:
                return Result.failure(self._repository_error(stored.error, correlation_id))
            if gate.status is not ApprovalGateStatus.PENDING:
                return Result.failure(
                    ErrorDetail(
                        ErrorCode.INVALID_TRANSITION,
                        "Approval gate no longer accepts a decision.",
                        correlation_id,
                    )
                )
            if not (
                reviewer_authorized
                and decision.strip()
                and decision_reason.strip()
                and reviewer_reference.strip()
            ):
                return Result.success(ApprovalSubmissionOutcome(gate=gate, accepted=False))
            approved = replace(
                gate,
                metadata=self._next_metadata(gate.metadata, correlation_id),
                status=ApprovalGateStatus.APPROVED,
                decision=decision,
                decision_reason=decision_reason,
                reviewer_reference=reviewer_reference,
            )
            persisted = unit_of_work.evidence.replace_approval(approved)
            if not persisted.is_success or persisted.value is None:
                return Result.failure(self._repository_error(persisted.error, correlation_id))
            return Result.success(ApprovalSubmissionOutcome(gate=approved, accepted=True))

    def _next_metadata(
        self, metadata: RecordMetadata, correlation_id: CorrelationId
    ) -> RecordMetadata:
        return replace(
            metadata,
            correlation_id=correlation_id,
            version=metadata.version + 1,
            updated_at=self._clock(),
        )

    @staticmethod
    def _unavailable(correlation_id: CorrelationId, subject: str) -> ErrorDetail:
        return ErrorDetail(
            ErrorCode.AUTHORIZATION_DENIED,
            f"{subject} is unavailable.",
            correlation_id,
        )

    @staticmethod
    def _repository_error(error: ErrorDetail | None, correlation_id: CorrelationId) -> ErrorDetail:
        if error is None:
            return ErrorDetail(
                ErrorCode.REPOSITORY_UNAVAILABLE,
                "Evidence storage is unavailable.",
                correlation_id,
            )
        return replace(error, correlation_id=correlation_id)

    @classmethod
    def _repository_result[T](
        cls, result: Result[T, ErrorDetail], correlation_id: CorrelationId
    ) -> Result[T, ErrorDetail]:
        if result.is_success:
            return result
        return Result.failure(cls._repository_error(result.error, correlation_id))


class GateEvaluator:
    """Evaluate only retained category evidence and rechecked server-owned approvals."""

    def __init__(
        self,
        unit_of_work_factory: UnitOfWorkFactory,
        *,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._clock = clock

    def evaluate(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        subject_reference: str,
        approval_gate_id: ApprovalGateId,
        requirements: GateRequirements,
        *,
        rights_and_consent_passed: bool,
        provenance_passed: bool,
        authorization_recheck: GateRecheck,
        policy_recheck: GateRecheck,
        affected_task_id: TaskId | None = None,
    ) -> Result[GateEvaluation, ErrorDetail]:
        """Permit progression only after retained evidence and current checks all succeed."""
        with self._unit_of_work_factory() as unit_of_work:
            gate_result = unit_of_work.evidence.get_approval(organization_id, approval_gate_id)
            gate = gate_result.value
            if not gate_result.is_success or gate is None:
                return Result.failure(self._repository_error(gate_result.error, correlation_id))
            evidence_result = unit_of_work.evidence.quality_for_subject(
                organization_id, subject_reference
            )
            records = evidence_result.value
            if not evidence_result.is_success or records is None:
                return Result.failure(self._repository_error(evidence_result.error, correlation_id))

            latest_by_kind = self._latest_by_kind(records)
            missing = tuple(
                kind for kind in requirements.required_evidence_kinds if kind not in latest_by_kind
            )
            failed = tuple(
                kind
                for kind in requirements.required_evidence_kinds
                if kind in latest_by_kind and not latest_by_kind[kind].passed
            )
            decision_valid = self._decision_is_valid(gate)
            can_recheck = (
                not missing
                and not failed
                and (rights_and_consent_passed or not requirements.requires_rights_and_consent)
                and (provenance_passed or not requirements.requires_provenance)
                and decision_valid
            )
            authorization_passed = authorization_recheck(gate) if can_recheck else False
            policy_passed = policy_recheck(gate) if can_recheck else False
            permitted = can_recheck and authorization_passed and policy_passed

            current_gate = gate
            if not permitted and gate.status is ApprovalGateStatus.APPROVED:
                pending = replace(
                    gate,
                    metadata=self._next_metadata(gate.metadata, correlation_id),
                    status=ApprovalGateStatus.PENDING,
                )
                persisted_gate = unit_of_work.evidence.replace_approval(pending)
                if not persisted_gate.is_success or persisted_gate.value is None:
                    unit_of_work.rollback()
                    return Result.failure(
                        self._repository_error(persisted_gate.error, correlation_id)
                    )
                current_gate = pending

            changed_task = self._update_affected_task(
                unit_of_work,
                organization_id,
                correlation_id,
                affected_task_id,
                permitted,
                missing,
                failed,
                rights_and_consent_passed,
                provenance_passed,
                can_recheck and not authorization_passed,
                can_recheck and not policy_passed,
            )
            if not changed_task.is_success:
                unit_of_work.rollback()
                return Result.failure(
                    changed_task.error or self._repository_error(None, correlation_id)
                )
            return Result.success(
                GateEvaluation(
                    gate=current_gate,
                    subject_reference=subject_reference,
                    progression_permitted=permitted,
                    missing_evidence_kinds=missing,
                    failed_evidence_kinds=failed,
                    rights_and_consent_passed=rights_and_consent_passed,
                    provenance_passed=provenance_passed,
                    authorization_rechecked=can_recheck and authorization_passed,
                    policy_rechecked=can_recheck and policy_passed,
                    affected_task_id=affected_task_id if changed_task.value else None,
                )
            )

    @staticmethod
    def _latest_by_kind(
        records: tuple[QualityEvidence, ...],
    ) -> dict[QualityEvidenceKind, QualityEvidence]:
        latest: dict[QualityEvidenceKind, QualityEvidence] = {}
        for record in records:
            current = latest.get(record.kind)
            if current is None or (
                record.recorded_at,
                record.metadata.version,
                record.evidence_id,
            ) > (
                current.recorded_at,
                current.metadata.version,
                current.evidence_id,
            ):
                latest[record.kind] = record
        return latest

    def _update_affected_task(
        self,
        unit_of_work: ControlPlaneUnitOfWork,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        affected_task_id: TaskId | None,
        permitted: bool,
        missing: tuple[QualityEvidenceKind, ...],
        failed: tuple[QualityEvidenceKind, ...],
        rights_and_consent_passed: bool,
        provenance_passed: bool,
        authorization_recheck_failed: bool,
        policy_recheck_failed: bool,
    ) -> Result[bool, ErrorDetail]:
        if affected_task_id is None:
            return Result.success(False)
        task_result = unit_of_work.tasks.get(organization_id, affected_task_id)
        task = task_result.value
        if not task_result.is_success or task is None:
            return Result.failure(self._repository_error(task_result.error, correlation_id))
        replacement = self._task_replacement(
            task,
            correlation_id,
            permitted,
            missing,
            failed,
            rights_and_consent_passed,
            provenance_passed,
            authorization_recheck_failed,
            policy_recheck_failed,
        )
        if replacement is None:
            return Result.success(False)
        persisted = unit_of_work.tasks.replace(replacement, task.metadata.version)
        if not persisted.is_success:
            return Result.failure(self._repository_error(persisted.error, correlation_id))
        return Result.success(True)

    def _task_replacement(
        self,
        task: AgentTask,
        correlation_id: CorrelationId,
        permitted: bool,
        missing: tuple[QualityEvidenceKind, ...],
        failed: tuple[QualityEvidenceKind, ...],
        rights_and_consent_passed: bool,
        provenance_passed: bool,
        authorization_recheck_failed: bool,
        policy_recheck_failed: bool,
    ) -> AgentTask | None:
        if task.state in {TaskLifecycle.COMPLETE, TaskLifecycle.FAILED}:
            return None
        if permitted:
            if task.state is TaskLifecycle.BLOCKED and all(
                field.startswith("gate:") for field in task.blocked_fields
            ):
                return replace(
                    task,
                    metadata=self._next_metadata(task.metadata, correlation_id),
                    state=TaskLifecycle.IDLE,
                    blocked_fields=(),
                )
            return None
        reasons = [
            *(f"gate:missing:{kind.value}" for kind in missing),
            *(f"gate:failed:{kind.value}" for kind in failed),
        ]
        if not rights_and_consent_passed:
            reasons.append("gate:rights_and_consent")
        if not provenance_passed:
            reasons.append("gate:provenance")
        if authorization_recheck_failed:
            reasons.append("gate:authorization")
        if policy_recheck_failed:
            reasons.append("gate:policy")
        blocked_fields = tuple(dict.fromkeys((*task.blocked_fields, *reasons)))
        if task.state is TaskLifecycle.BLOCKED and task.blocked_fields == blocked_fields:
            return None
        return replace(
            task,
            metadata=self._next_metadata(task.metadata, correlation_id),
            state=TaskLifecycle.BLOCKED,
            blocked_fields=blocked_fields,
        )

    def _next_metadata(
        self, metadata: RecordMetadata, correlation_id: CorrelationId
    ) -> RecordMetadata:
        return replace(
            metadata,
            correlation_id=correlation_id,
            version=metadata.version + 1,
            updated_at=self._clock(),
        )

    @staticmethod
    def _decision_is_valid(gate: ApprovalGate) -> bool:
        return (
            gate.status is ApprovalGateStatus.APPROVED
            and bool(gate.decision and gate.decision.strip())
            and bool(gate.decision_reason and gate.decision_reason.strip())
            and bool(gate.reviewer_reference and gate.reviewer_reference.strip())
        )

    @staticmethod
    def _repository_error(error: ErrorDetail | None, correlation_id: CorrelationId) -> ErrorDetail:
        if error is None:
            return ErrorDetail(
                ErrorCode.REPOSITORY_UNAVAILABLE,
                "Evidence storage is unavailable.",
                correlation_id,
            )
        return replace(error, correlation_id=correlation_id)
