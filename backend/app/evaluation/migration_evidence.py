"""Immutable local evidence for the dual-engine migration gate."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from string import hexdigits
from threading import RLock
from typing import Protocol

from app.models.common import SCHEMA_VERSION, RecordMetadata, utc_now
from app.models.contracts import ErrorCode, ErrorDetail, RepositoryError, Result
from app.models.evidence import EvidenceReference
from app.models.identifiers import CorrelationId, EvidenceId, OrganizationId, RunId, new_record_id

MIGRATION_CONTROL_ORGANIZATION_ID = OrganizationId("host-migration")


class MigrationGate(StrEnum):
    """Every independently retained proof required before LegacyEngine retirement."""

    DUAL_ENGINE = "dual-engine"
    MULTI_SPECIALIST_HANDOFFS = "multi-specialist-handoffs"
    VISIBLE_GRAPH_AND_INTERRUPT = "visible-graph-and-interrupt"
    STUBBED_VIDEO_SPINE_RELEASE_GATE = "stubbed-video-spine-release-gate"
    CROSS_ORGANIZATION_RESUME_DENIAL = "cross-organization-resume-denial"
    FAIL_CLOSED_TOOL_ALLOWLIST = "fail-closed-tool-allowlist"


REQUIRED_MIGRATION_GATES = tuple(MigrationGate)


@dataclass(frozen=True, slots=True)
class MigrationGateEvidence:
    """One independently verifiable migration-gate result."""

    gate: MigrationGate
    passed: bool
    evidence_hashes: tuple[str, ...]
    supporting_references: tuple[EvidenceReference, ...] = ()


@dataclass(frozen=True, slots=True)
class MigrationAssessmentEvidence:
    """An append-only assessment of the migration gates at one configuration."""
    metadata: RecordMetadata
    evidence_id: EvidenceId
    configuration_digest: str
    gates: tuple[MigrationGateEvidence, ...]
    recorded_at: datetime

    @property
    def missing_gates(self) -> tuple[MigrationGate, ...]:
        """Return mandatory gates that have no current retained result."""
        recorded = {evidence.gate for evidence in self.gates}
        return tuple(gate for gate in REQUIRED_MIGRATION_GATES if gate not in recorded)

    @property
    def failed_gates(self) -> tuple[MigrationGate, ...]:
        """Return mandatory gates whose current retained result is not passing."""
        return tuple(evidence.gate for evidence in self.gates if not evidence.passed)

    @property
    def is_satisfied(self) -> bool:
        """Require exactly every current migration gate to pass."""
        return not self.missing_gates and not self.failed_gates


@dataclass(frozen=True, slots=True)
class LegacyRetirementEvidence:
    """Durable evidence that a satisfied assessment disabled LegacyEngine execution."""

    metadata: RecordMetadata
    evidence_id: EvidenceId
    assessment_evidence_id: EvidenceId
    configuration_digest: str
    active_run_ids: tuple[RunId, ...]
    recorded_at: datetime


@dataclass(frozen=True, slots=True)
class MigrationGateAssessment:
    """The current assessment result, retained even when retirement remains blocked."""

    record: MigrationAssessmentEvidence

    @property
    def is_satisfied(self) -> bool:
        """Expose the all-evidence conjunction without weakening it."""
        return self.record.is_satisfied


class MigrationEvidenceRepository(Protocol):
    """Append-only persistence seam for assessment and retirement evidence."""

    def append_assessment(
        self, record: MigrationAssessmentEvidence
    ) -> Result[MigrationAssessmentEvidence, RepositoryError]:
        """Persist an immutable migration assessment."""

    def append_retirement(
        self, record: LegacyRetirementEvidence
    ) -> Result[LegacyRetirementEvidence, RepositoryError]:
        """Persist immutable evidence before LegacyEngine is disabled."""

    def latest_retirement(self) -> LegacyRetirementEvidence | None:
        """Return the one-way retirement decision, when one has been retained."""

    def assessments(self) -> tuple[MigrationAssessmentEvidence, ...]:
        """Return retained assessment snapshots for deterministic inspection."""


class InMemoryMigrationEvidenceRepository:
    """Lock-protected local retention used by deterministic Host composition and tests."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._assessments: list[MigrationAssessmentEvidence] = []
        self._retirements: list[LegacyRetirementEvidence] = []
        self._evidence_ids: set[EvidenceId] = set()

    def append_assessment(
        self, record: MigrationAssessmentEvidence
    ) -> Result[MigrationAssessmentEvidence, RepositoryError]:
        """Append a distinct assessment without replacing older gate evidence."""
        with self._lock:
            if record.evidence_id in self._evidence_ids:
                return Result.failure(
                    self._conflict("Migration assessment evidence already exists.")
                )
            self._evidence_ids.add(record.evidence_id)
            self._assessments.append(record)
            return Result.success(record)

    def append_retirement(
        self, record: LegacyRetirementEvidence
    ) -> Result[LegacyRetirementEvidence, RepositoryError]:
        """Persist a single irreversible retirement decision."""
        with self._lock:
            if self._retirements:
                return Result.failure(
                    self._conflict("LegacyEngine retirement is already retained.")
                )
            if record.evidence_id in self._evidence_ids:
                return Result.failure(self._conflict("Legacy retirement evidence already exists."))
            self._evidence_ids.add(record.evidence_id)
            self._retirements.append(record)
            return Result.success(record)

    def latest_retirement(self) -> LegacyRetirementEvidence | None:
        """Expose the persisted retirement state without an automatic rollback path."""
        with self._lock:
            return self._retirements[-1] if self._retirements else None

    def assessments(self) -> tuple[MigrationAssessmentEvidence, ...]:
        """Return append-only local assessment evidence."""
        with self._lock:
            return tuple(self._assessments)

    @staticmethod
    def _conflict(message: str) -> ErrorDetail:
        return ErrorDetail(ErrorCode.CONFLICT, message, CorrelationId("migration-evidence"))


class MigrationEvidenceService:
    """Retain current migration evidence and prove the gate only by conjunction."""

    def __init__(
        self,
        repository: MigrationEvidenceRepository,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._repository = repository
        self._clock = clock

    def assess(
        self,
        correlation_id: CorrelationId,
        configuration_digest: str,
        gates: Sequence[MigrationGateEvidence],
    ) -> Result[MigrationGateAssessment, ErrorDetail]:
        """Append a current assessment; any missing or failed gate remains blocked."""
        validation_error = self._validate_assessment(configuration_digest, gates)
        if validation_error is not None:
            return Result.failure(
                ErrorDetail(ErrorCode.VALIDATION_FAILED, validation_error, correlation_id)
            )
        timestamp = self._clock()
        record = MigrationAssessmentEvidence(
            metadata=RecordMetadata(
                record_id=new_record_id(),
                organization_id=MIGRATION_CONTROL_ORGANIZATION_ID,
                correlation_id=correlation_id,
                schema_version=SCHEMA_VERSION,
                version=1,
                created_at=timestamp,
                updated_at=timestamp,
            ),
            evidence_id=EvidenceId(str(new_record_id())),
            configuration_digest=configuration_digest,
            gates=tuple(gates),
            recorded_at=timestamp,
        )
        persisted = self._repository.append_assessment(record)
        if not persisted.is_success:
            return Result.failure(self._repository_error(persisted.error, correlation_id))
        if persisted.value is None:
            raise RuntimeError("Successful migration assessment persistence had no record.")
        return Result.success(MigrationGateAssessment(persisted.value))

    def record_retirement(
        self,
        correlation_id: CorrelationId,
        assessment: MigrationGateAssessment,
        active_run_ids: tuple[RunId, ...],
    ) -> Result[LegacyRetirementEvidence, ErrorDetail]:
        """Persist retirement evidence only from a fully passing retained assessment."""
        if not assessment.is_satisfied:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.INVALID_TRANSITION,
                    "LegacyEngine retirement requires every current migration gate to pass.",
                    correlation_id,
                )
            )
        timestamp = self._clock()
        record = LegacyRetirementEvidence(
            metadata=RecordMetadata(
                record_id=new_record_id(),
                organization_id=MIGRATION_CONTROL_ORGANIZATION_ID,
                correlation_id=correlation_id,
                schema_version=SCHEMA_VERSION,
                version=1,
                created_at=timestamp,
                updated_at=timestamp,
            ),
            evidence_id=EvidenceId(str(new_record_id())),
            assessment_evidence_id=assessment.record.evidence_id,
            configuration_digest=assessment.record.configuration_digest,
            active_run_ids=tuple(dict.fromkeys(active_run_ids)),
            recorded_at=timestamp,
        )
        persisted = self._repository.append_retirement(record)
        if not persisted.is_success:
            return Result.failure(self._repository_error(persisted.error, correlation_id))
        if persisted.value is None:
            raise RuntimeError("Successful retirement evidence persistence had no record.")
        return Result.success(persisted.value)

    def latest_retirement(self) -> LegacyRetirementEvidence | None:
        """Return the durable one-way retirement decision for process recovery."""
        return self._repository.latest_retirement()

    @classmethod
    def _validate_assessment(
        cls, configuration_digest: str, gates: Sequence[MigrationGateEvidence]
    ) -> str | None:
        if not cls._is_sha256(configuration_digest):
            return "Migration assessments require a SHA-256 configuration digest."
        gate_ids = tuple(evidence.gate for evidence in gates)
        if len(gate_ids) != len(set(gate_ids)):
            return "Migration assessments cannot contain duplicate gate results."
        for evidence in gates:
            if not evidence.evidence_hashes or not all(
                cls._is_sha256(digest) for digest in evidence.evidence_hashes
            ):
                return "Each migration gate requires one or more SHA-256 evidence hashes."
        return None

    @staticmethod
    def _is_sha256(value: str) -> bool:
        return len(value) == 64 and all(character in hexdigits for character in value)

    @staticmethod
    def _repository_error(
        error: RepositoryError | None, correlation_id: CorrelationId
    ) -> ErrorDetail:
        if error is None:
            return ErrorDetail(
                ErrorCode.REPOSITORY_UNAVAILABLE,
                "Migration evidence storage failed.",
                correlation_id,
            )
        return ErrorDetail(
            error.code,
            error.message,
            correlation_id,
            retryable=error.retryable,
            fields=error.fields,
        )
