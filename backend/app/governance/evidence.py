"""Directed critique, independent quality evidence, and fail-closed approval gates."""

# ruff: noqa: E501

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import datetime
from enum import StrEnum

from app.models.common import utc_now
from app.models.contracts import ErrorCode, ErrorDetail, Result
from app.models.control_plane import (
    ApprovalGate,
    ApprovalGateId,
    ApprovalGateStatus,
    CritiqueRecord,
    QualityEvidence,
    QualityEvidenceKind,
)
from app.models.identifiers import CorrelationId, OrganizationId
from app.repositories.control_plane import ControlPlaneUnitOfWork


@dataclass(frozen=True, slots=True)
class CritiqueDirection:
    """One permitted published source-to-target critique relationship."""

    source_reference: str
    target_task_reference: str
    relationship_reference: str

    @classmethod
    def from_record(cls, record: CritiqueRecord) -> CritiqueDirection:
        """Represent a critique record's directed relationship for policy comparison."""
        return cls(
            source_reference=record.source_reference,
            target_task_reference=str(record.target_task_id),
            relationship_reference=record.relationship_reference,
        )


class GateProgress(StrEnum):
    """The only outcomes of a gate evaluation before an effect can resume."""

    READY = "ready"
    PENDING = "pending"
    BLOCKED = "blocked"


@dataclass(frozen=True, slots=True)
class GateEvaluation:
    """A fail-closed gate result that callers use to retain or block a subject."""

    gate_id: ApprovalGateId
    subject_reference: str
    progress: GateProgress
    blocking_checks: tuple[str, ...]

    @property
    def may_resume(self) -> bool:
        """Return whether every required independently retained check passed."""
        return self.progress is GateProgress.READY

    @property
    def subject_blocked(self) -> bool:
        """Return whether evidence failure requires a task or rollout transition block."""
        return self.progress is GateProgress.BLOCKED


HumanReviewAuthorizer = Callable[[OrganizationId, CritiqueRecord], bool]
ResumeCheck = Callable[[OrganizationId, str, str], bool]


class EvidenceService:
    """Persist only permitted critiques, independent evidence, and server-owned gates."""

    def __init__(
        self,
        unit_of_work_factory: Callable[[], ControlPlaneUnitOfWork],
        published_directions: frozenset[CritiqueDirection] = frozenset(),
        human_review_authorizer: HumanReviewAuthorizer | None = None,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._published_directions = published_directions
        self._human_review_authorizer = human_review_authorizer or (lambda _org, _record: False)
        self._clock = clock

    def submit_critique(
        self, organization_id: OrganizationId, record: CritiqueRecord
    ) -> Result[CritiqueRecord, ErrorDetail]:
        """Retain a critique only after its published or human direction is authorized."""
        mismatch = self._organization_mismatch(organization_id, record.metadata.organization_id, record.metadata.correlation_id)
        if mismatch is not None:
            return Result.failure(mismatch)
        direction = CritiqueDirection.from_record(record)
        if direction not in self._published_directions and not self._human_authorized(organization_id, record):
            return Result.failure(
                ErrorDetail(
                    ErrorCode.AUTHORIZATION_DENIED,
                    "The critique direction is not permitted.",
                    record.metadata.correlation_id,
                )
            )
        with self._unit_of_work_factory() as unit_of_work:
            return unit_of_work.evidence.append_critique(record)

    def record_quality_evidence(
        self, organization_id: OrganizationId, record: QualityEvidence
    ) -> Result[QualityEvidence, ErrorDetail]:
        """Append one category-specific quality result without synthesizing an aggregate."""
        mismatch = self._organization_mismatch(organization_id, record.metadata.organization_id, record.metadata.correlation_id)
        if mismatch is not None:
            return Result.failure(mismatch)
        with self._unit_of_work_factory() as unit_of_work:
            return unit_of_work.evidence.append_quality(record)

    def create_pending_gate(
        self, organization_id: OrganizationId, gate: ApprovalGate
    ) -> Result[ApprovalGate, ErrorDetail]:
        """Create a server-owned pending operation before any human decision is accepted."""
        mismatch = self._organization_mismatch(organization_id, gate.metadata.organization_id, gate.metadata.correlation_id)
        if mismatch is not None:
            return Result.failure(mismatch)
        if gate.status is not ApprovalGateStatus.PENDING or any(
            value is not None
            for value in (gate.decision, gate.decision_reason, gate.reviewer_reference)
        ):
            return Result.failure(
                ErrorDetail(
                    ErrorCode.INVALID_TRANSITION,
                    "New approval gates must be server-owned pending operations.",
                    gate.metadata.correlation_id,
                )
            )
        with self._unit_of_work_factory() as unit_of_work:
            return unit_of_work.evidence.append_approval(gate)

    def submit_approval_decision(
        self,
        organization_id: OrganizationId,
        approval_gate_id: ApprovalGateId,
        decision: str | None,
        decision_reason: str | None,
        reviewer_reference: str | None,
        authorization_recheck: ResumeCheck,
        policy_recheck: ResumeCheck,
    ) -> Result[ApprovalGate, ErrorDetail]:
        """Retain every decision and approve a gate only after fresh server checks pass."""
        with self._unit_of_work_factory() as unit_of_work:
            fetched = unit_of_work.evidence.get_approval(organization_id, approval_gate_id)
            if not fetched.is_success:
                return Result.failure(self._repository_error(fetched))
            gate = self._value(fetched)
            if gate.status is not ApprovalGateStatus.PENDING:
                return Result.failure(
                    ErrorDetail(
                        ErrorCode.CONFLICT,
                        "The approval gate is no longer pending.",
                        gate.metadata.correlation_id,
                    )
                )

            normalized_decision = self._normalized_value(decision)
            normalized_reason = self._normalized_value(decision_reason)
            normalized_reviewer = self._normalized_value(reviewer_reference)
            has_required_decision = all(
                (normalized_decision, normalized_reason, normalized_reviewer)
            )
            allowed_to_resume = (
                has_required_decision
                and normalized_decision == "approved"
                and self._check(
                    authorization_recheck,
                    organization_id,
                    gate.pending_operation_reference,
                    normalized_reviewer,
                )
                and self._check(
                    policy_recheck,
                    organization_id,
                    gate.pending_operation_reference,
                    normalized_reviewer,
                )
            )
            updated = replace(
                gate,
                metadata=replace(
                    gate.metadata,
                    version=gate.metadata.version + 1,
                    updated_at=self._clock(),
                ),
                status=(ApprovalGateStatus.APPROVED if allowed_to_resume else ApprovalGateStatus.PENDING),
                decision=normalized_decision,
                decision_reason=normalized_reason,
                reviewer_reference=normalized_reviewer,
            )
            return unit_of_work.evidence.replace_approval(updated)

    def _human_authorized(
        self, organization_id: OrganizationId, record: CritiqueRecord
    ) -> bool:
        """Treat an unavailable human-policy decision as denial rather than bypassing direction policy."""
        try:
            return self._human_review_authorizer(organization_id, record)
        except Exception:
            return False

    @staticmethod
    def _normalized_value(value: str | None) -> str:
        return value.strip() if isinstance(value, str) else ""

    @staticmethod
    def _check(
        check: ResumeCheck,
        organization_id: OrganizationId,
        pending_operation_reference: str,
        reviewer_reference: str,
    ) -> bool:
        try:
            return check(organization_id, pending_operation_reference, reviewer_reference)
        except Exception:
            return False

    @staticmethod
    def _organization_mismatch(
        organization_id: OrganizationId,
        record_organization_id: OrganizationId,
        correlation_id: CorrelationId,
    ) -> ErrorDetail | None:
        if organization_id == record_organization_id:
            return None
        return ErrorDetail(
            ErrorCode.AUTHORIZATION_DENIED,
            "The evidence record is unavailable.",
            correlation_id,
        )

    @staticmethod
    def _repository_error(result: Result[object, ErrorDetail]) -> ErrorDetail:
        error = result.error
        if error is None:
            raise RuntimeError("A failed evidence repository result did not contain an error.")
        return error

    @staticmethod
    def _value(result: Result[ApprovalGate, ErrorDetail]) -> ApprovalGate:
        if result.value is None:
            raise RuntimeError("A successful evidence repository result did not contain a gate.")
        return result.value


class GateEvaluator:
    """Evaluate only independently retained evidence and a server-owned approved decision."""

    def __init__(self, unit_of_work_factory: Callable[[], ControlPlaneUnitOfWork]) -> None:
        self._unit_of_work_factory = unit_of_work_factory

    def evaluate(
        self,
        organization_id: OrganizationId,
        approval_gate_id: ApprovalGateId,
        subject_reference: str,
        applicable_evidence_kinds: frozenset[QualityEvidenceKind],
        *,
        rights_and_consent_passed: bool,
        provenance_passed: bool,
    ) -> Result[GateEvaluation, ErrorDetail]:
        """Permit progression exactly when all applicable category, rights, provenance, and gate checks pass."""
        with self._unit_of_work_factory() as unit_of_work:
            gate_result = unit_of_work.evidence.get_approval(organization_id, approval_gate_id)
            if not gate_result.is_success:
                return Result.failure(EvidenceService._repository_error(gate_result))
            evidence_result = unit_of_work.evidence.quality_for_subject(
                organization_id, subject_reference
            )
            if not evidence_result.is_success:
                return Result.failure(EvidenceService._repository_error(evidence_result))
            gate = EvidenceService._value(gate_result)
            evidence = evidence_result.value
            if evidence is None:
                raise RuntimeError("A successful evidence lookup did not contain records.")

        blocking_checks = self._blocking_checks(
            evidence,
            applicable_evidence_kinds | frozenset({QualityEvidenceKind.GATE}),
            rights_and_consent_passed,
            provenance_passed,
        )
        if (
            gate.status is not ApprovalGateStatus.APPROVED
            or gate.decision != "approved"
            or not gate.decision_reason
            or not gate.reviewer_reference
        ):
            return Result.success(
                GateEvaluation(
                    approval_gate_id,
                    subject_reference,
                    GateProgress.PENDING,
                    (*blocking_checks, "approval"),
                )
            )
        if blocking_checks:
            return Result.success(
                GateEvaluation(
                    approval_gate_id,
                    subject_reference,
                    GateProgress.BLOCKED,
                    blocking_checks,
                )
            )
        return Result.success(
            GateEvaluation(approval_gate_id, subject_reference, GateProgress.READY, ())
        )

    @staticmethod
    def _blocking_checks(
        evidence: tuple[QualityEvidence, ...],
        applicable_evidence_kinds: frozenset[QualityEvidenceKind],
        rights_and_consent_passed: bool,
        provenance_passed: bool,
    ) -> tuple[str, ...]:
        blocking: list[str] = []
        for kind in sorted(applicable_evidence_kinds, key=str):
            category_records = tuple(record for record in evidence if record.kind is kind)
            if not category_records or any(not record.passed for record in category_records):
                blocking.append(kind.value)
        if not rights_and_consent_passed:
            blocking.append("rights_and_consent")
        if not provenance_passed:
            blocking.append("provenance")
        return tuple(blocking)
