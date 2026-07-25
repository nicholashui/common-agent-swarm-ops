"""Immutable local evidence for the dual-engine migration gate."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from string import hexdigits
from threading import RLock
from typing import Protocol

from app.models.common import SCHEMA_VERSION, RecordMetadata, utc_now
from app.models.contracts import ErrorCode, ErrorDetail, RepositoryError, Result
from app.models.evidence import EvidenceReference
from app.models.identifiers import (
    CorrelationId,
    EvidenceId,
    OrganizationId,
    RunId,
    new_record_id,
)

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

    def __post_init__(self) -> None:
        """Freeze collection inputs so retained evidence cannot be mutated in place."""
        object.__setattr__(self, "evidence_hashes", tuple(self.evidence_hashes))
        object.__setattr__(self, "supporting_references", tuple(self.supporting_references))


@dataclass(frozen=True, slots=True)
class MigrationAssessmentEvidence:
    """An append-only assessment of the migration gates at one configuration."""

    metadata: RecordMetadata
    evidence_id: EvidenceId
    configuration_digest: str
    gates: tuple[MigrationGateEvidence, ...]
    recorded_at: datetime

    def __post_init__(self) -> None:
        """Freeze the retained gate snapshot as immutable tuples."""
        object.__setattr__(self, "gates", tuple(self.gates))

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

    def __post_init__(self) -> None:
        """Freeze the active-run evidence captured at retirement time."""
        object.__setattr__(self, "active_run_ids", tuple(self.active_run_ids))


@dataclass(frozen=True, slots=True)
class MigrationGateAssessment:
    """The current assessment result, retained even when retirement remains blocked."""

    record: MigrationAssessmentEvidence

    @property
    def is_satisfied(self) -> bool:
        """Expose the all-evidence conjunction without weakening it."""
        return self.record.is_satisfied

    @property
    def missing_gates(self) -> tuple[MigrationGate, ...]:
        """Expose mandatory gates that were not present in this assessment."""
        return self.record.missing_gates

    @property
    def failed_gates(self) -> tuple[MigrationGate, ...]:
        """Expose mandatory gates whose retained proof did not pass."""
        return self.record.failed_gates


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


class _LegacyInMemoryMigrationEvidenceRepository:
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


class _LegacyMigrationEvidenceService:
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
        normalized_gates, validation_error = self._normalize_assessment(configuration_digest, gates)
        if validation_error is not None or normalized_gates is None:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.VALIDATION_FAILED,
                    validation_error or "Migration assessment evidence is invalid.",
                    correlation_id,
                )
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
            gates=normalized_gates,
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
    def _normalize_assessment(
        cls,
        configuration_digest: str,
        gates: Sequence[object],
    ) -> tuple[tuple[MigrationGateEvidence, ...] | None, str | None]:
        """Validate and canonicalize a gate snapshot before it is retained."""
        if not cls._is_sha256(configuration_digest):
            return None, "Migration assessments require a SHA-256 configuration digest."

        normalized: list[MigrationGateEvidence] = []
        for evidence in gates:
            if not isinstance(evidence, MigrationGateEvidence):
                return (
                    None,
                    "Migration assessments require typed gate evidence records.",
                )
            try:
                gate = MigrationGate(evidence.gate)
            except (TypeError, ValueError):
                return None, "Migration assessments cannot contain an unknown gate."
            passed: object = evidence.passed
            if not isinstance(passed, bool):
                return None, "Migration gate outcomes must be boolean values."
            if not evidence.evidence_hashes or not all(
                cls._is_sha256(digest) for digest in evidence.evidence_hashes
            ):
                return (
                    None,
                    "Each migration gate requires one or more SHA-256 evidence hashes.",
                )
            normalized.append(
                MigrationGateEvidence(
                    gate=gate,
                    passed=passed,
                    evidence_hashes=evidence.evidence_hashes,
                    supporting_references=evidence.supporting_references,
                )
            )

        gate_ids = tuple(evidence.gate for evidence in normalized)
        if len(gate_ids) != len(set(gate_ids)):
            return None, "Migration assessments cannot contain duplicate gate results."
        if any(gate not in REQUIRED_MIGRATION_GATES for gate in gate_ids):
            return None, "Migration assessments cannot contain an unknown gate."
        return tuple(normalized), None

    @staticmethod
    def _is_sha256(value: object) -> bool:
        return (
            isinstance(value, str)
            and len(value) == 64
            and all(character in hexdigits for character in value)
        )

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


# Controlled migration evidence introduced for the VA migration workflow.
class SourceDisposition(StrEnum):
    """Allowed dispositions for a frozen source-baseline asset."""

    RETAIN = "retain"
    MIGRATE = "migrate"
    DEPRECATE = "deprecate"
    EXCLUDE = "exclude"
    QUARANTINE = "quarantine"


@dataclass(frozen=True, slots=True)
class MigrationPhaseRecord:
    """Immutable scope and review evidence for one migration phase."""

    metadata: RecordMetadata
    phase_id: str
    phase_scope: tuple[str, ...]
    required_evidence: tuple[str, ...]
    exit_criteria: tuple[str, ...]
    rollback_procedure: str
    host_owner_review: str
    va_owner_review: str
    status: str = "open"

    def __post_init__(self) -> None:
        for value, name in (
            (self.phase_id, "phase_id"),
            (self.rollback_procedure, "rollback_procedure"),
            (self.host_owner_review, "host_owner_review"),
            (self.va_owner_review, "va_owner_review"),
        ):
            if not value.strip():
                raise ValueError(f"{name} must be non-empty.")
        for values, name in (
            (self.phase_scope, "phase_scope"),
            (self.required_evidence, "required_evidence"),
            (self.exit_criteria, "exit_criteria"),
        ):
            if not values or any(not value.strip() for value in values):
                raise ValueError(f"{name} must contain non-empty values.")
        if len(self.phase_scope) != len(set(self.phase_scope)):
            raise ValueError("phase_scope must not contain duplicates.")

    @property
    def scope(self) -> tuple[str, ...]:
        """Return the phase scope using the concise design vocabulary."""
        return self.phase_scope

    @property
    def evidence(self) -> tuple[str, ...]:
        """Return the required evidence references for phase exit."""
        return self.required_evidence

    @property
    def exit(self) -> tuple[str, ...]:
        """Return the declared phase exit criteria."""
        return self.exit_criteria

    @property
    def rollback(self) -> str:
        """Return the retained rollback procedure."""
        return self.rollback_procedure

    @property
    def host_review(self) -> str:
        """Return the host-owner review evidence."""
        return self.host_owner_review

    @property
    def va_review(self) -> str:
        """Return the VA-owner review evidence."""
        return self.va_owner_review


@dataclass(frozen=True, slots=True)
class SourceIndexEntry:
    """One frozen source asset with a complete disposition decision."""

    metadata: RecordMetadata
    asset_id: str
    asset_hash: str
    owner: str
    license_or_consent_classification: str
    disposition: SourceDisposition

    def __post_init__(self) -> None:
        for value, name in (
            (self.asset_id, "asset_id"),
            (self.asset_hash, "asset_hash"),
            (self.owner, "owner"),
            (
                self.license_or_consent_classification,
                "license_or_consent_classification",
            ),
        ):
            if not value.strip():
                raise ValueError(f"{name} must be non-empty.")
        object.__setattr__(self, "disposition", SourceDisposition(self.disposition))

    @property
    def license_or_consent(self) -> str:
        """Compatibility alias for the concise Source_Index field name."""
        return self.license_or_consent_classification


@dataclass(frozen=True, slots=True)
class WorkflowActivationEvidence:
    """The independently evaluated evidence vector for one VA workflow."""

    workflow_id: str
    domain_evaluations: tuple[bool, ...]
    reproducible_trace: bool
    human_approvals: tuple[bool, ...]
    maturity_level: str
    designated_approval_evaluation: bool
    evidence_references: tuple[EvidenceReference, ...] = ()

    def __post_init__(self) -> None:
        if not self.workflow_id.strip():
            raise ValueError("workflow_id must be non-empty.")
        if not self.maturity_level.strip():
            raise ValueError("maturity_level must be documented.")
        object.__setattr__(self, "domain_evaluations", tuple(self.domain_evaluations))
        object.__setattr__(self, "human_approvals", tuple(self.human_approvals))
        object.__setattr__(self, "evidence_references", tuple(self.evidence_references))

    @property
    def is_complete(self) -> bool:
        """Return true only when every required activation gate passes."""
        return (
            bool(self.domain_evaluations)
            and all(self.domain_evaluations)
            and self.reproducible_trace
            and bool(self.human_approvals)
            and all(self.human_approvals)
            and bool(self.maturity_level.strip())
            and self.designated_approval_evaluation
        )

    @property
    def declared_domain_evaluations(self) -> tuple[bool, ...]:
        """Descriptive alias matching the requirement vocabulary."""
        return self.domain_evaluations

    @property
    def applicable_human_approvals(self) -> tuple[bool, ...]:
        """Descriptive alias matching the requirement vocabulary."""
        return self.human_approvals


class WorkflowActivationStatus(StrEnum):
    """Fail-closed workflow activation lifecycle."""

    INELIGIBLE = "ineligible"
    ACTIVATION_ELIGIBLE = "activation_eligible"
    ACTIVE = "active"


@dataclass(frozen=True, slots=True)
class WorkflowActivationRecord:
    """Durable eligibility or active-status decision for a workflow."""

    metadata: RecordMetadata
    workflow_id: str
    status: WorkflowActivationStatus
    evidence: WorkflowActivationEvidence
    activation_approval_id: str | None = None

    def __post_init__(self) -> None:
        if not self.workflow_id.strip():
            raise ValueError("workflow_id must be non-empty.")
        if self.workflow_id != self.evidence.workflow_id:
            raise ValueError("Workflow activation evidence must identify the same workflow.")
        object.__setattr__(self, "status", WorkflowActivationStatus(self.status))
        if self.status is WorkflowActivationStatus.ACTIVE and not self.activation_approval_id:
            raise ValueError("Active workflows require an explicit activation approval.")

    @property
    def activation_eligible(self) -> bool:
        """Return whether this record has passed the eligibility gate."""
        return self.status in (
            WorkflowActivationStatus.ACTIVATION_ELIGIBLE,
            WorkflowActivationStatus.ACTIVE,
        )


@dataclass(frozen=True, slots=True)
class ActivationApproval:
    """Explicit, durable human approval required for an eligible workflow to activate."""

    metadata: RecordMetadata
    approval_id: str
    workflow_id: str
    approved: bool
    reviewer_identity: str
    decision_reason: str
    evidence_references: tuple[EvidenceReference, ...] = ()

    def __post_init__(self) -> None:
        for value, name in (
            (self.approval_id, "approval_id"),
            (self.workflow_id, "workflow_id"),
            (self.reviewer_identity, "reviewer_identity"),
            (self.decision_reason, "decision_reason"),
        ):
            if not value.strip():
                raise ValueError(f"{name} must be non-empty.")
        object.__setattr__(self, "evidence_references", tuple(self.evidence_references))


# Names used by the design's data-model summary.
MigrationPhase = MigrationPhaseRecord
WorkflowActivation = WorkflowActivationRecord


class MigrationControlEvidenceRepository(MigrationEvidenceRepository, Protocol):
    """Persistence seam for migration phases, source baselines, and activation gates."""

    def append_phase(
        self, record: MigrationPhaseRecord
    ) -> Result[MigrationPhaseRecord, RepositoryError]:
        """Persist an immutable migration phase."""

    def phases(self) -> tuple[MigrationPhaseRecord, ...]:
        """Return all retained phase records."""

    def append_source_index(
        self, records: tuple[SourceIndexEntry, ...]
    ) -> Result[tuple[SourceIndexEntry, ...], RepositoryError]:
        """Persist a complete frozen source index atomically."""

    def source_index(self) -> tuple[SourceIndexEntry, ...]:
        """Return all retained source-index entries."""

    def append_activation(
        self, record: WorkflowActivationRecord
    ) -> Result[WorkflowActivationRecord, RepositoryError]:
        """Persist an immutable workflow activation decision."""

    def activation_records(self, workflow_id: str) -> tuple[WorkflowActivationRecord, ...]:
        """Return activation decisions for one workflow."""

    def append_activation_approval(
        self, record: ActivationApproval
    ) -> Result[ActivationApproval, RepositoryError]:
        """Persist an explicit activation approval or denial."""

    def activation_approvals(self, workflow_id: str) -> tuple[ActivationApproval, ...]:
        """Return approval history for one workflow."""


_BaseInMemoryMigrationEvidenceRepository = _LegacyInMemoryMigrationEvidenceRepository


class InMemoryMigrationEvidenceRepository(_BaseInMemoryMigrationEvidenceRepository):
    """In-memory retention for the complete controlled migration evidence set."""

    def __init__(self) -> None:
        super().__init__()
        self._control_lock = RLock()
        self._phases: list[MigrationPhaseRecord] = []
        self._source_entries: dict[str, SourceIndexEntry] = {}
        self._activations: dict[str, list[WorkflowActivationRecord]] = {}
        self._activation_approvals: dict[str, list[ActivationApproval]] = {}
        self._control_record_ids: set[str] = set()

    def append_phase(
        self, record: MigrationPhaseRecord
    ) -> Result[MigrationPhaseRecord, RepositoryError]:
        with self._control_lock:
            if str(record.metadata.record_id) in self._control_record_ids:
                return Result.failure(self._control_error("Migration phase record already exists."))
            self._control_record_ids.add(str(record.metadata.record_id))
            self._phases.append(record)
            return Result.success(record)

    def phases(self) -> tuple[MigrationPhaseRecord, ...]:
        with self._control_lock:
            return tuple(self._phases)

    def append_source_index(
        self, records: tuple[SourceIndexEntry, ...]
    ) -> Result[tuple[SourceIndexEntry, ...], RepositoryError]:
        with self._control_lock:
            asset_ids = tuple(record.asset_id for record in records)
            if len(asset_ids) != len(set(asset_ids)) or any(
                asset_id in self._source_entries for asset_id in asset_ids
            ):
                return Result.failure(
                    self._control_error("Source_Index asset identifiers must be unique.")
                )
            if any(
                str(record.metadata.record_id) in self._control_record_ids for record in records
            ):
                return Result.failure(self._control_error("Source_Index record already exists."))
            for record in records:
                self._source_entries[record.asset_id] = record
                self._control_record_ids.add(str(record.metadata.record_id))
            return Result.success(records)

    def source_index(self) -> tuple[SourceIndexEntry, ...]:
        with self._control_lock:
            return tuple(self._source_entries.values())

    def append_activation(
        self, record: WorkflowActivationRecord
    ) -> Result[WorkflowActivationRecord, RepositoryError]:
        with self._control_lock:
            if str(record.metadata.record_id) in self._control_record_ids:
                return Result.failure(
                    self._control_error("Workflow activation record already exists.")
                )
            self._control_record_ids.add(str(record.metadata.record_id))
            self._activations.setdefault(record.workflow_id, []).append(record)
            return Result.success(record)

    def activation_records(self, workflow_id: str) -> tuple[WorkflowActivationRecord, ...]:
        with self._control_lock:
            return tuple(self._activations.get(workflow_id, ()))

    def append_activation_approval(
        self, record: ActivationApproval
    ) -> Result[ActivationApproval, RepositoryError]:
        with self._control_lock:
            if str(record.metadata.record_id) in self._control_record_ids:
                return Result.failure(self._control_error("Activation approval already exists."))
            self._control_record_ids.add(str(record.metadata.record_id))
            self._activation_approvals.setdefault(record.workflow_id, []).append(record)
            return Result.success(record)

    def activation_approvals(self, workflow_id: str) -> tuple[ActivationApproval, ...]:
        with self._control_lock:
            return tuple(self._activation_approvals.get(workflow_id, ()))

    @staticmethod
    def _control_error(message: str) -> ErrorDetail:
        return ErrorDetail(ErrorCode.CONFLICT, message, CorrelationId("migration-control"))


_BaseMigrationEvidenceService = _LegacyMigrationEvidenceService


class MigrationEvidenceService(_BaseMigrationEvidenceService):
    """Migration evidence service including phase, roster, and activation gates."""

    def __init__(
        self,
        repository: MigrationControlEvidenceRepository,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        super().__init__(repository, clock)
        self._control_repository = repository

    def record_phase(
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
        """Persist the complete phase gate before migration work begins."""
        try:
            record = MigrationPhaseRecord(
                metadata=self._metadata(correlation_id),
                phase_id=phase_id,
                phase_scope=tuple(phase_scope),
                required_evidence=tuple(required_evidence),
                exit_criteria=tuple(exit_criteria),
                rollback_procedure=rollback_procedure,
                host_owner_review=host_owner_review,
                va_owner_review=va_owner_review,
            )
        except (TypeError, ValueError) as error:
            return Result.failure(
                ErrorDetail(ErrorCode.VALIDATION_FAILED, str(error), correlation_id)
            )
        persisted = self._control_repository.append_phase(record)
        if not persisted.is_success or persisted.value is None:
            return Result.failure(self._control_error(persisted.error, correlation_id))
        return Result.success(persisted.value)

    def record_source_index(
        self,
        correlation_id: CorrelationId,
        entries: Sequence[SourceIndexEntry | Mapping[str, object]],
    ) -> Result[tuple[SourceIndexEntry, ...], ErrorDetail]:
        """Validate every frozen source disposition and persist the index atomically."""
        if not entries:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.VALIDATION_FAILED,
                    "Source_Index must contain assets.",
                    correlation_id,
                )
            )
        timestamp = self._clock()
        normalized: list[SourceIndexEntry] = []
        try:
            for index, entry in enumerate(entries):
                if isinstance(entry, SourceIndexEntry):
                    normalized.append(entry)
                    continue
                if not isinstance(entry, Mapping):
                    raise ValueError(f"Source_Index entry {index} must be an object.")
                asset_id = self._source_value(entry, "asset_id", "source_id", "id")
                asset_hash = self._source_value(entry, "asset_hash", "hash", "digest")
                owner = self._source_value(entry, "owner", "owner_id")
                license_classification = self._source_value(
                    entry,
                    "license_or_consent_classification",
                    "license_or_consent",
                    "classification",
                )
                disposition = entry.get("disposition")
                if not isinstance(disposition, str):
                    raise ValueError(f"Source_Index entry {index} requires a disposition.")
                normalized.append(
                    SourceIndexEntry(
                        metadata=self._metadata(correlation_id, timestamp),
                        asset_id=asset_id,
                        asset_hash=asset_hash,
                        owner=owner,
                        license_or_consent_classification=license_classification,
                        disposition=SourceDisposition(disposition),
                    )
                )
        except (TypeError, ValueError) as error:
            return Result.failure(
                ErrorDetail(ErrorCode.VALIDATION_FAILED, str(error), correlation_id)
            )
        asset_ids = tuple(entry.asset_id for entry in normalized)
        if len(asset_ids) != len(set(asset_ids)):
            return Result.failure(
                ErrorDetail(
                    ErrorCode.VALIDATION_FAILED,
                    "Source_Index asset identifiers must be unique.",
                    correlation_id,
                )
            )
        persisted = self._control_repository.append_source_index(tuple(normalized))
        if not persisted.is_success or persisted.value is None:
            return Result.failure(self._control_error(persisted.error, correlation_id))
        return Result.success(persisted.value)

    def evaluate_activation_eligibility(
        self,
        correlation_id: CorrelationId,
        evidence: WorkflowActivationEvidence,
    ) -> Result[WorkflowActivationRecord, ErrorDetail]:
        """Persist eligibility only after every declared activation evidence gate passes."""
        status = (
            WorkflowActivationStatus.ACTIVATION_ELIGIBLE
            if evidence.is_complete
            else WorkflowActivationStatus.INELIGIBLE
        )
        record = WorkflowActivationRecord(
            metadata=self._metadata(correlation_id),
            workflow_id=evidence.workflow_id,
            status=status,
            evidence=evidence,
        )
        persisted = self._control_repository.append_activation(record)
        if not persisted.is_success or persisted.value is None:
            return Result.failure(self._control_error(persisted.error, correlation_id))
        return Result.success(persisted.value)

    def record_activation_approval(
        self,
        correlation_id: CorrelationId,
        approval_id: str,
        workflow_id: str,
        reviewer_identity: str,
        decision_reason: str,
        approved: bool = True,
        evidence_references: Sequence[EvidenceReference] = (),
    ) -> Result[ActivationApproval, ErrorDetail]:
        """Persist explicit activation approval independently from eligibility."""
        try:
            record = ActivationApproval(
                metadata=self._metadata(correlation_id),
                approval_id=approval_id,
                workflow_id=workflow_id,
                approved=approved,
                reviewer_identity=reviewer_identity,
                decision_reason=decision_reason,
                evidence_references=tuple(evidence_references),
            )
        except (TypeError, ValueError) as error:
            return Result.failure(
                ErrorDetail(ErrorCode.VALIDATION_FAILED, str(error), correlation_id)
            )
        persisted = self._control_repository.append_activation_approval(record)
        if not persisted.is_success or persisted.value is None:
            return Result.failure(self._control_error(persisted.error, correlation_id))
        return Result.success(persisted.value)

    def activate_workflow(
        self, correlation_id: CorrelationId, workflow_id: str
    ) -> Result[WorkflowActivationRecord, ErrorDetail]:
        """Allow active status only for eligible workflows with approved activation evidence."""
        records = self._control_repository.activation_records(workflow_id)
        latest = records[-1] if records else None
        if latest is None or latest.status is not WorkflowActivationStatus.ACTIVATION_ELIGIBLE:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.INVALID_TRANSITION,
                    "Workflow activation requires Activation_Eligible evidence.",
                    correlation_id,
                )
            )
        approvals = self._control_repository.activation_approvals(workflow_id)
        approval = approvals[-1] if approvals else None
        if approval is None or not approval.approved:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.AUTHORIZATION_DENIED,
                    "Workflow activation requires explicit approved activation evidence.",
                    correlation_id,
                )
            )
        active = WorkflowActivationRecord(
            metadata=self._metadata(correlation_id),
            workflow_id=workflow_id,
            status=WorkflowActivationStatus.ACTIVE,
            evidence=latest.evidence,
            activation_approval_id=approval.approval_id,
        )
        persisted = self._control_repository.append_activation(active)
        if not persisted.is_success or persisted.value is None:
            return Result.failure(self._control_error(persisted.error, correlation_id))
        return Result.success(persisted.value)

    def latest_activation(self, workflow_id: str) -> WorkflowActivationRecord | None:
        """Return the last retained activation decision for a workflow."""
        records = self._control_repository.activation_records(workflow_id)
        return records[-1] if records else None

    def _metadata(
        self, correlation_id: CorrelationId, timestamp: datetime | None = None
    ) -> RecordMetadata:
        recorded_at = self._clock() if timestamp is None else timestamp
        return RecordMetadata(
            record_id=new_record_id(),
            organization_id=MIGRATION_CONTROL_ORGANIZATION_ID,
            correlation_id=correlation_id,
            schema_version=SCHEMA_VERSION,
            version=1,
            created_at=recorded_at,
            updated_at=recorded_at,
        )

    @staticmethod
    def _source_value(entry: Mapping[str, object], *names: str) -> str:
        for name in names:
            value = entry.get(name)
            if isinstance(value, str) and value.strip():
                return value
        raise ValueError(f"Source_Index requires {names[0]}.")

    @staticmethod
    def _control_error(error: RepositoryError | None, correlation_id: CorrelationId) -> ErrorDetail:
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
