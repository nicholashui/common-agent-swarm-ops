"""All-evidence migration assessment and one-way LegacyEngine retirement."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from threading import RLock
from typing import Protocol
from weakref import WeakValueDictionary

from app.evaluation.migration_evidence import (
    LegacyRetirementEvidence,
    MigrationEvidenceService,
    MigrationGateAssessment,
    MigrationGateEvidence,
)
from app.models.contracts import ErrorCode, ErrorDetail, Result
from app.models.evidence import EvidenceReference
from app.models.identifiers import CorrelationId, OrganizationId, RunId


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
        self._retirement = evidence_service.latest_retirement()
        self._retired = self._retirement is not None
        self._active: WeakValueDictionary[
            tuple[OrganizationId, RunId], LegacyExecutionLease
        ] = WeakValueDictionary()

    def is_available(self) -> bool:
        """Return false once retirement evidence exists or evidence storage is unavailable."""
        with self._lock:
            return not self._retired

    def begin_legacy_execution(
        self,
        organization_id: OrganizationId,
        run_id: RunId,
        correlation_id: CorrelationId,
    ) -> Result[LegacyExecutionLease, ErrorDetail]:
        """Register an active execution under the same lock used by retirement."""
        with self._lock:
            if self._retired:
                return Result.failure(self._retired_error(correlation_id))
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
        assessment_result = self._evidence_service.assess(
            correlation_id, configuration_digest, gates
        )
        if not assessment_result.is_success:
            return Result.failure(self._error(assessment_result.error, correlation_id))
        if assessment_result.value is None:
            raise RuntimeError("Successful migration assessment had no result.")
        assessment = assessment_result.value
        with self._lock:
            if self._retirement is not None:
                return Result.success(LegacyRetirementOutcome(assessment, self._retirement, False))
            if not assessment.is_satisfied:
                return Result.success(LegacyRetirementOutcome(assessment, None, False))
            active_run_ids = tuple(lease.run_id for lease in self._active.values())
            retained = self._evidence_service.record_retirement(
                correlation_id, assessment, active_run_ids
            )
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
