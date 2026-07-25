"""Immutable evidence records used by the adoption Verification_Suite.

The release evidence layer deliberately stores references and digests rather than
verification output.  This keeps release decisions reviewable without allowing a
fixture, command output, or Lesson body to become an authority-bearing record.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from threading import RLock
from typing import Protocol

from app.models.common import RecordMetadata, validate_semantic_version
from app.models.contracts import ErrorCode, ErrorDetail, RepositoryError, Result
from app.models.control_plane import (
    AuditRecord,
    CompatibilityStatus,
    ReleaseReadinessDecision,
    VerificationCoverageStatus,
    VerificationRun,
)
from app.models.identifiers import (
    CorrelationId,
    DomainPackId,
    EvidenceId,
    OrganizationId,
    new_record_id,
)


class VerificationLayer(StrEnum):
    """The four independently retained verification layers."""

    SCHEMA = "schema"
    UNIT = "unit"
    PROPERTY = "property"
    INTEGRATION = "integration"


class VerificationOutcome(StrEnum):
    """The result of one deterministic verification check."""

    PASS = "pass"
    FAIL = "fail"


@dataclass(frozen=True, slots=True)
class VerificationCheckResult:
    """Digest-only outcome for one schema, unit, property, or integration check."""

    metadata: RecordMetadata
    evidence_id: EvidenceId
    layer: VerificationLayer
    check_name: str
    outcome: VerificationOutcome
    evidence_digest: str
    fixed_seed: str
    fixture_digest: str
    recorded_at: datetime
    supporting_references: tuple[str, ...] = ()
    failure_reference: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "layer", VerificationLayer(self.layer))
        object.__setattr__(self, "outcome", VerificationOutcome(self.outcome))
        for value, name in (
            (str(self.evidence_id), "evidence_id"),
            (self.check_name, "check_name"),
            (self.evidence_digest, "evidence_digest"),
            (self.fixed_seed, "fixed_seed"),
            (self.fixture_digest, "fixture_digest"),
        ):
            _required(value, name)
        _timestamp(self.recorded_at, "recorded_at")
        references = _references(self.supporting_references, "supporting_references")
        object.__setattr__(self, "supporting_references", references)
        if self.outcome is VerificationOutcome.PASS and self.failure_reference is not None:
            raise ValueError("Passing checks cannot retain failure evidence.")
        if self.failure_reference is not None:
            _required(self.failure_reference, "failure_reference")

    @property
    def passed(self) -> bool:
        """Return whether this check passed."""
        return self.outcome is VerificationOutcome.PASS

    @property
    def failed(self) -> bool:
        """Return whether this check failed."""
        return not self.passed

    @property
    def category(self) -> VerificationLayer:
        """Compatibility alias for callers using category terminology."""
        return self.layer

    @property
    def check_id(self) -> EvidenceId:
        """Return the stable evidence identity of this check."""
        return self.evidence_id


@dataclass(frozen=True, slots=True)
class VerificationFailureRecord:
    """Immutable, redaction-safe evidence for a failed verification check."""

    metadata: RecordMetadata
    failure_id: EvidenceId
    verification_evidence_id: EvidenceId
    layer: VerificationLayer
    check_name: str
    failure_reference: str
    failure_digest: str
    recorded_at: datetime
    after_integration_coverage: bool

    def __post_init__(self) -> None:
        object.__setattr__(self, "layer", VerificationLayer(self.layer))
        for value, name in (
            (str(self.failure_id), "failure_id"),
            (str(self.verification_evidence_id), "verification_evidence_id"),
            (self.check_name, "check_name"),
            (self.failure_reference, "failure_reference"),
            (self.failure_digest, "failure_digest"),
        ):
            _required(value, name)
        _timestamp(self.recorded_at, "recorded_at")

    @property
    def evidence_id(self) -> EvidenceId:
        """Return the failure evidence identity."""
        return self.failure_id

    @property
    def coverage_complete(self) -> bool:
        """Expose the post-coverage classification in requirement vocabulary."""
        return self.after_integration_coverage


@dataclass(frozen=True, slots=True)
class CompatibilityEvidenceRecord:
    """Immutable compatibility result retained alongside a release evaluation."""

    metadata: RecordMetadata
    evidence_id: EvidenceId
    pack_contract_version: str
    host_contract_version: str
    alc_version: str
    status: CompatibilityStatus
    designated: bool
    evidence_reference: str
    recorded_at: datetime
    pack_id: DomainPackId | None = None
    immutable_version: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "status", CompatibilityStatus(self.status))
        for value, name in (
            (str(self.evidence_id), "evidence_id"),
            (self.pack_contract_version, "pack_contract_version"),
            (self.host_contract_version, "host_contract_version"),
            (self.alc_version, "alc_version"),
            (self.evidence_reference, "evidence_reference"),
        ):
            _required(value, name)
        for value, name in (
            (self.pack_contract_version, "pack_contract_version"),
            (self.host_contract_version, "host_contract_version"),
            (self.alc_version, "alc_version"),
        ):
            validate_semantic_version(value, name)
        if self.immutable_version is not None:
            validate_semantic_version(self.immutable_version, "immutable_version")
        _timestamp(self.recorded_at, "recorded_at")
        if not self.designated:
            raise ValueError("Compatibility evidence must be for a designated combination.")

    @property
    def result(self) -> CompatibilityStatus:
        """Return the recorded compatibility status."""
        return self.status


@dataclass(frozen=True, slots=True)
class UIProjectionEvidence:
    """Reference-only UI evidence; projection content is never retained here."""

    metadata: RecordMetadata
    projection_id: EvidenceId
    projection_type: str
    projection_digest: str
    recorded_at: datetime
    supporting_references: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for value, name in (
            (str(self.projection_id), "projection_id"),
            (self.projection_type, "projection_type"),
            (self.projection_digest, "projection_digest"),
        ):
            _required(value, name)
        _timestamp(self.recorded_at, "recorded_at")
        object.__setattr__(
            self,
            "supporting_references",
            _references(self.supporting_references, "supporting_references"),
        )

    @property
    def ui_projection_id(self) -> EvidenceId:
        """Descriptive alias used by release projections."""
        return self.projection_id


@dataclass(frozen=True, slots=True)
class ReleasePolicy:
    """Explicit policy controlling exceptional administrative release decisions."""

    allow_administrative_failure: bool = False
    administrative_failure_reference: str | None = None
    allow_incomplete_coverage: bool = False

    def __post_init__(self) -> None:
        if self.allow_administrative_failure and not self.administrative_failure_reference:
            raise ValueError(
                "Administrative failure permission requires a policy evidence reference."
            )
        if self.administrative_failure_reference is not None:
            _required(self.administrative_failure_reference, "administrative_failure_reference")

    @property
    def administrative_failure_allowed(self) -> bool:
        """Compatibility alias for policy evaluators."""
        return self.allow_administrative_failure


@dataclass(frozen=True, slots=True)
class ReleaseEvidenceBundle:
    """Complete immutable projection returned by one Verification_Suite execution."""

    verification_run: VerificationRun
    check_results: tuple[VerificationCheckResult, ...]
    failure_records: tuple[VerificationFailureRecord, ...]
    compatibility_results: tuple[CompatibilityEvidenceRecord, ...]
    audit_records: tuple[AuditRecord, ...]
    ui_projections: tuple[UIProjectionEvidence, ...]
    release_decision: ReleaseReadinessDecision | None
    failure_persistence_errors: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "check_results", tuple(self.check_results))
        object.__setattr__(self, "failure_records", tuple(self.failure_records))
        object.__setattr__(self, "compatibility_results", tuple(self.compatibility_results))
        object.__setattr__(self, "audit_records", tuple(self.audit_records))
        object.__setattr__(self, "ui_projections", tuple(self.ui_projections))
        object.__setattr__(
            self,
            "failure_persistence_errors",
            _references(self.failure_persistence_errors, "failure_persistence_errors"),
        )

    @property
    def verification_results(self) -> tuple[VerificationCheckResult, ...]:
        """Alias for callers that use the requirement's result terminology."""
        return self.check_results

    @property
    def coverage_status(self) -> VerificationCoverageStatus:
        """Return the immutable coverage state retained on the verification run."""
        return self.verification_run.coverage_status


class ReleaseEvidenceRepository(Protocol):
    """Append-only storage for the evidence that is not in core adoption repositories."""

    def append_check_result(
        self, record: VerificationCheckResult
    ) -> Result[VerificationCheckResult, RepositoryError]: ...

    def append_failure(
        self, record: VerificationFailureRecord
    ) -> Result[VerificationFailureRecord, RepositoryError]: ...

    def append_compatibility(
        self, record: CompatibilityEvidenceRecord
    ) -> Result[CompatibilityEvidenceRecord, RepositoryError]: ...

    def append_ui_projection(
        self, record: UIProjectionEvidence
    ) -> Result[UIProjectionEvidence, RepositoryError]: ...

    def append_audit(self, record: AuditRecord) -> Result[AuditRecord, RepositoryError]: ...

    def check_results(self) -> tuple[VerificationCheckResult, ...]: ...

    def failures(self) -> tuple[VerificationFailureRecord, ...]: ...

    def compatibilities(self) -> tuple[CompatibilityEvidenceRecord, ...]: ...

    def ui_projections(self) -> tuple[UIProjectionEvidence, ...]: ...

    def audits(self) -> tuple[AuditRecord, ...]: ...


class InMemoryReleaseEvidenceRepository:
    """Thread-safe append-only local repository used by verification and tests."""

    def __init__(self, *, fail_failure_persistence: bool = False) -> None:
        self.fail_failure_persistence = fail_failure_persistence
        self._lock = RLock()
        self._check_results: dict[EvidenceId, VerificationCheckResult] = {}
        self._failures: dict[EvidenceId, VerificationFailureRecord] = {}
        self._compatibilities: dict[EvidenceId, CompatibilityEvidenceRecord] = {}
        self._ui_projections: dict[EvidenceId, UIProjectionEvidence] = {}
        self._audits: dict[str, AuditRecord] = {}

    def append_check_result(
        self, record: VerificationCheckResult
    ) -> Result[VerificationCheckResult, RepositoryError]:
        with self._lock:
            if record.evidence_id in self._check_results:
                return Result.failure(_conflict("Verification check result already exists."))
            self._check_results[record.evidence_id] = record
            return Result.success(record)

    def append_failure(
        self, record: VerificationFailureRecord
    ) -> Result[VerificationFailureRecord, RepositoryError]:
        with self._lock:
            if self.fail_failure_persistence:
                return Result.failure(
                    ErrorDetail(
                        ErrorCode.REPOSITORY_UNAVAILABLE,
                        "Verification failure persistence is unavailable.",
                        record.metadata.correlation_id,
                        retryable=True,
                    )
                )
            if record.failure_id in self._failures:
                return Result.failure(_conflict("Verification failure already exists."))
            self._failures[record.failure_id] = record
            return Result.success(record)

    def append_compatibility(
        self, record: CompatibilityEvidenceRecord
    ) -> Result[CompatibilityEvidenceRecord, RepositoryError]:
        with self._lock:
            if record.evidence_id in self._compatibilities:
                return Result.failure(_conflict("Compatibility evidence already exists."))
            self._compatibilities[record.evidence_id] = record
            return Result.success(record)

    def append_ui_projection(
        self, record: UIProjectionEvidence
    ) -> Result[UIProjectionEvidence, RepositoryError]:
        with self._lock:
            if record.projection_id in self._ui_projections:
                return Result.failure(_conflict("UI projection evidence already exists."))
            self._ui_projections[record.projection_id] = record
            return Result.success(record)

    def append_audit(self, record: AuditRecord) -> Result[AuditRecord, RepositoryError]:
        with self._lock:
            if record.audit_id in self._audits:
                return Result.failure(_conflict("Audit record already exists."))
            self._audits[record.audit_id] = record
            return Result.success(record)

    def check_results(self) -> tuple[VerificationCheckResult, ...]:
        with self._lock:
            return tuple(self._check_results.values())

    def failures(self) -> tuple[VerificationFailureRecord, ...]:
        with self._lock:
            return tuple(self._failures.values())

    def compatibilities(self) -> tuple[CompatibilityEvidenceRecord, ...]:
        with self._lock:
            return tuple(self._compatibilities.values())

    def ui_projections(self) -> tuple[UIProjectionEvidence, ...]:
        with self._lock:
            return tuple(self._ui_projections.values())

    def audits(self) -> tuple[AuditRecord, ...]:
        with self._lock:
            return tuple(self._audits.values())

    @property
    def records(self) -> tuple[VerificationCheckResult, ...]:
        """Convenient alias used by focused tests."""
        return self.check_results()

    @property
    def failure_records(self) -> tuple[VerificationFailureRecord, ...]:
        """Convenient alias used by focused tests."""
        return self.failures()

    @property
    def compatibility_records(self) -> tuple[CompatibilityEvidenceRecord, ...]:
        """Convenient alias used by focused tests."""
        return self.compatibilities()


class InMemoryReleaseReadinessRepository:
    """Append-only local repository for terminal release decisions."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._records: dict[tuple[DomainPackId, str, str], ReleaseReadinessDecision] = {}

    def append(
        self, record: ReleaseReadinessDecision
    ) -> Result[ReleaseReadinessDecision, RepositoryError]:
        key = (record.pack_id, record.immutable_version, record.workflow_id)
        with self._lock:
            if key in self._records:
                return Result.failure(_conflict("Release readiness decision already exists."))
            self._records[key] = record
            return Result.success(record)

    def get_terminal(
        self,
        organization_id: OrganizationId,
        pack_id: DomainPackId,
        immutable_version: str,
        workflow_id: str,
    ) -> Result[ReleaseReadinessDecision, RepositoryError]:
        with self._lock:
            record = self._records.get((pack_id, immutable_version, workflow_id))
            if record is None or record.metadata.organization_id != organization_id:
                return Result.failure(
                    ErrorDetail(
                        ErrorCode.NOT_FOUND,
                        "Release readiness decision was not found.",
                        CorrelationId("release-evidence"),
                    )
                )
            return Result.success(record)

    def records(self) -> tuple[ReleaseReadinessDecision, ...]:
        """Return terminal decisions in insertion order."""
        with self._lock:
            return tuple(self._records.values())


def build_metadata(
    organization_id: OrganizationId,
    correlation_id: CorrelationId,
    timestamp: datetime,
) -> RecordMetadata:
    """Build standard metadata for a new release evidence record."""
    return RecordMetadata(
        record_id=new_record_id(),
        organization_id=organization_id,
        correlation_id=correlation_id,
        schema_version=1,
        version=1,
        created_at=timestamp,
        updated_at=timestamp,
    )


def _required(value: str, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be non-empty.")


def _timestamp(value: datetime, name: str) -> None:
    if value.tzinfo is None:
        raise ValueError(f"{name} must be timezone-aware.")


def _references(values: Iterable[str], name: str) -> tuple[str, ...]:
    references = tuple(str(value) for value in values)
    if any(not value.strip() for value in references):
        raise ValueError(f"{name} references must be non-empty.")
    if len(references) != len(set(references)):
        raise ValueError(f"{name} references must be unique.")
    return references


def _conflict(message: str) -> ErrorDetail:
    return ErrorDetail(ErrorCode.CONFLICT, message, CorrelationId("release-evidence"))


# Specification spelling aliases are intentionally exported for callers that use
# the domain vocabulary rather than the Python class naming convention.
Verification_Result = VerificationCheckResult
Verification_Failure_Record = VerificationFailureRecord
Compatibility_Result = CompatibilityEvidenceRecord
UI_Projection = UIProjectionEvidence
Release_Policy = ReleasePolicy
Release_Evidence = ReleaseEvidenceBundle
InMemoryReleaseEvidenceStore = InMemoryReleaseEvidenceRepository
InMemoryReleaseDecisionRepository = InMemoryReleaseReadinessRepository
