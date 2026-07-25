"""Evidence-gated migration rollback and immutable-version recovery services."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from threading import RLock
from typing import Protocol

from app.models.common import (
    SCHEMA_VERSION,
    RecordMetadata,
    utc_now,
    validate_semantic_version,
)
from app.models.contracts import (
    ErrorCode,
    ErrorDetail,
    ErrorField,
    RepositoryError,
    Result,
)
from app.models.control_plane import (
    RecoveryAction,
    RecoveryActionId,
    RecoveryActionStatus,
)
from app.models.evidence import Lesson
from app.models.identifiers import (
    CorrelationId,
    DomainPackId,
    OrganizationId,
    new_record_id,
)
from app.repositories.protocols import RecoveryActionRepository


class ImmutableVersionRestorer(Protocol):
    """Restore one already-approved immutable Domain_Pack version."""

    def restore(
        self,
        organization_id: OrganizationId,
        pack_id: DomainPackId,
        immutable_version: str,
        correlation_id: CorrelationId,
    ) -> Result[str, ErrorDetail]:
        """Restore exactly the requested version or return a fail-closed error."""


@dataclass(frozen=True, slots=True)
class ContractChangeEvidence:
    """The complete evidence vector required for a contract-breaking change."""

    architecture_decision_record: str = ""
    migration_plan: str = ""
    consumer_compatibility_evidence: str = ""
    deprecation_window: str = ""
    rollback_plan: str = ""

    def __post_init__(self) -> None:
        for name, value in self._field_values():
            if not isinstance(value, str):
                raise ValueError(f"{name} must be a string reference.")
            object.__setattr__(self, name, value.strip())

    @property
    def missing_artifacts(self) -> tuple[str, ...]:
        """Return every required artifact that is absent from this evidence record."""
        return tuple(name for name, value in self._field_values() if not value)

    @property
    def is_complete(self) -> bool:
        """Return whether all five contract-change artifacts are present."""
        return not self.missing_artifacts

    @property
    def references(self) -> tuple[str, ...]:
        """Return retained evidence references in the required decision order."""
        return tuple(value for _, value in self._field_values() if value)

    @classmethod
    def from_mapping(cls, values: Mapping[str, object]) -> ContractChangeEvidence:
        """Normalize boundary mappings while retaining references only."""
        aliases = {
            "architecture_decision_record": (
                "architecture_decision_record",
                "architecture_decision",
                "adr",
            ),
            "migration_plan": ("migration_plan",),
            "consumer_compatibility_evidence": (
                "consumer_compatibility_evidence",
                "consumer_compatibility",
            ),
            "deprecation_window": ("deprecation_window",),
            "rollback_plan": ("rollback_plan",),
        }
        normalized: dict[str, str] = {}
        for field_name, names in aliases.items():
            value = next((values.get(name) for name in names if values.get(name) is not None), "")
            normalized[field_name] = str(value) if value is not None else ""
        return cls(**normalized)

    def _field_values(self) -> tuple[tuple[str, str], ...]:
        return (
            ("architecture_decision_record", self.architecture_decision_record),
            ("migration_plan", self.migration_plan),
            ("consumer_compatibility_evidence", self.consumer_compatibility_evidence),
            ("deprecation_window", self.deprecation_window),
            ("rollback_plan", self.rollback_plan),
        )


@dataclass(frozen=True, slots=True)
class ContractChangeApproval:
    """The immutable approval decision for one contract-breaking change."""

    change_id: str
    approved: bool
    evidence: ContractChangeEvidence
    correlation_id: CorrelationId

    def __post_init__(self) -> None:
        if not self.change_id.strip():
            raise ValueError("change_id must be non-empty.")


class LessonRetentionOutcome(StrEnum):
    """Reference-only outcome of applying one ALC Lesson retention policy."""

    RETAINED = "retained"
    STALE = "stale"
    REVOKED = "revoked"
    DELETED = "deleted"
    APPLIED = "applied"


@dataclass(frozen=True, slots=True)
class LessonRetentionRecord:
    """Retention evidence that never copies Lesson content."""

    lesson_reference: str
    policy_reference: str
    outcome: LessonRetentionOutcome

    def __post_init__(self) -> None:
        if not self.lesson_reference.strip():
            raise ValueError("lesson_reference must be non-empty.")
        if not self.policy_reference.strip():
            raise ValueError("policy_reference must be non-empty.")
        object.__setattr__(self, "outcome", LessonRetentionOutcome(self.outcome))


class LessonRetentionService(Protocol):
    """Apply an ALC-selected retention policy without exposing Lesson bodies."""

    def apply(
        self,
        organization_id: OrganizationId,
        pack_id: DomainPackId,
        restored_version: str,
        lessons: tuple[Lesson, ...],
        policy_reference: str,
        correlation_id: CorrelationId,
    ) -> Result[tuple[LessonRetentionRecord, ...], ErrorDetail]:
        """Persist or retain policy outcomes before restoration proceeds."""


class ReferenceLessonRetentionService:
    """Deterministic default that records policy application by Lesson reference."""

    def apply(
        self,
        organization_id: OrganizationId,
        pack_id: DomainPackId,
        restored_version: str,
        lessons: tuple[Lesson, ...],
        policy_reference: str,
        correlation_id: CorrelationId,
    ) -> Result[tuple[LessonRetentionRecord, ...], ErrorDetail]:
        if not policy_reference.strip():
            return Result.failure(
                ErrorDetail(
                    ErrorCode.VALIDATION_FAILED,
                    "ALC Lesson retention requires a policy reference.",
                    correlation_id,
                )
            )
        outcome = _retention_outcome(policy_reference)
        return Result.success(
            tuple(
                LessonRetentionRecord(str(lesson.lesson_id), policy_reference, outcome)
                for lesson in lessons
            )
        )


class InMemoryLessonRetentionService(ReferenceLessonRetentionService):
    """Deterministic retention fake with an explicit pre-restoration failure seam."""

    def __init__(self, *, fail_writes: bool = False) -> None:
        self.fail_writes = fail_writes
        self.calls: list[tuple[DomainPackId, str, tuple[str, ...], str]] = []

    def apply(
        self,
        organization_id: OrganizationId,
        pack_id: DomainPackId,
        restored_version: str,
        lessons: tuple[Lesson, ...],
        policy_reference: str,
        correlation_id: CorrelationId,
    ) -> Result[tuple[LessonRetentionRecord, ...], ErrorDetail]:
        self.calls.append(
            (
                pack_id,
                restored_version,
                tuple(str(lesson.lesson_id) for lesson in lessons),
                policy_reference,
            )
        )
        if self.fail_writes:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.REPOSITORY_UNAVAILABLE,
                    "ALC Lesson retention persistence is unavailable.",
                    correlation_id,
                    retryable=True,
                )
            )
        return super().apply(
            organization_id,
            pack_id,
            restored_version,
            lessons,
            policy_reference,
            correlation_id,
        )


class InMemoryImmutableVersionStore:
    """Approved-version registry and target-exact restorer for deterministic tests."""

    def __init__(self) -> None:
        self._approved: set[tuple[OrganizationId, DomainPackId, str]] = set()
        self.current_versions: dict[tuple[OrganizationId, DomainPackId], str] = {}
        self.restore_calls: list[tuple[OrganizationId, DomainPackId, str]] = []

    def approve_version(
        self,
        organization_id: OrganizationId,
        pack_id: DomainPackId,
        immutable_version: str,
    ) -> None:
        validate_semantic_version(immutable_version, "immutable_version")
        self._approved.add((organization_id, pack_id, immutable_version))

    def restore(
        self,
        organization_id: OrganizationId,
        pack_id: DomainPackId,
        immutable_version: str,
        correlation_id: CorrelationId,
    ) -> Result[str, ErrorDetail]:
        key = (organization_id, pack_id, immutable_version)
        if key not in self._approved:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.AUTHORIZATION_DENIED,
                    "Only an approved immutable Domain_Pack version can be restored.",
                    correlation_id,
                )
            )
        self.restore_calls.append(key)
        self.current_versions[(organization_id, pack_id)] = immutable_version
        return Result.success(immutable_version)


class MigrationRollbackStatus(StrEnum):
    """Append-only migration rollback evidence state."""

    APPROVED = "approved"
    RESTORED = "restored"


@dataclass(frozen=True, slots=True)
class MigrationRollbackEvidence:
    """Durable migration rollback evidence retained before and after restoration."""

    metadata: RecordMetadata
    rollback_id: str
    pack_id: DomainPackId
    designated_immutable_version: str
    status: MigrationRollbackStatus
    approval_reference: str
    affected_lesson_references: tuple[str, ...]
    alc_retention_policy: str
    evidence_references: tuple[str, ...]
    retention_records: tuple[LessonRetentionRecord, ...] = ()
    restored_immutable_version: str | None = None
    recorded_at: datetime | None = None

    def __post_init__(self) -> None:
        if not self.rollback_id.strip():
            raise ValueError("rollback_id must be non-empty.")
        validate_semantic_version(self.designated_immutable_version, "designated_immutable_version")
        if not self.approval_reference.strip():
            raise ValueError("approval_reference must be non-empty.")
        if not self.alc_retention_policy.strip():
            raise ValueError("alc_retention_policy must be non-empty.")
        _required_references(self.affected_lesson_references, "affected_lesson_references")
        _required_references(self.evidence_references, "evidence_references")
        object.__setattr__(self, "status", MigrationRollbackStatus(self.status))
        if self.restored_immutable_version is not None:
            validate_semantic_version(self.restored_immutable_version, "restored_immutable_version")
        if self.status is MigrationRollbackStatus.RESTORED:
            if self.restored_immutable_version != self.designated_immutable_version:
                raise ValueError("Completed rollback evidence must retain the designated version.")
            if not self.retention_records and self.affected_lesson_references:
                raise ValueError("Completed rollback evidence requires Lesson retention outcomes.")
        if self.recorded_at is not None and self.recorded_at.tzinfo is None:
            raise ValueError("recorded_at must be timezone-aware.")
        object.__setattr__(self, "retention_records", tuple(self.retention_records))


class RollbackEvidenceRepository(Protocol):
    """Append/replace seam for immutable migration rollback evidence snapshots."""

    def append(
        self, record: MigrationRollbackEvidence
    ) -> Result[MigrationRollbackEvidence, RepositoryError]:
        """Retain the approved rollback evidence before restoration."""

    def replace(
        self, record: MigrationRollbackEvidence
    ) -> Result[MigrationRollbackEvidence, RepositoryError]:
        """Retain the completed immutable evidence snapshot."""

    def list_for_organization(
        self, organization_id: OrganizationId
    ) -> Result[tuple[MigrationRollbackEvidence, ...], RepositoryError]:
        """List rollback evidence for one organization."""


class InMemoryRollbackEvidenceRepository:
    """Lock-protected rollback evidence fake with configurable write failure."""

    def __init__(self, *, fail_writes: bool = False) -> None:
        self.fail_writes = fail_writes
        self._lock = RLock()
        self._records: dict[str, MigrationRollbackEvidence] = {}

    def append(
        self, record: MigrationRollbackEvidence
    ) -> Result[MigrationRollbackEvidence, RepositoryError]:
        with self._lock:
            if self.fail_writes:
                return Result.failure(self._unavailable(record.metadata.correlation_id))
            if record.rollback_id in self._records:
                return Result.failure(
                    ErrorDetail(
                        ErrorCode.CONFLICT,
                        "Migration rollback evidence already exists.",
                        record.metadata.correlation_id,
                    )
                )
            self._records[record.rollback_id] = record
            return Result.success(record)

    def replace(
        self, record: MigrationRollbackEvidence
    ) -> Result[MigrationRollbackEvidence, RepositoryError]:
        with self._lock:
            if self.fail_writes:
                return Result.failure(self._unavailable(record.metadata.correlation_id))
            if record.rollback_id not in self._records:
                return Result.failure(
                    ErrorDetail(
                        ErrorCode.NOT_FOUND,
                        "Migration rollback evidence was not found.",
                        record.metadata.correlation_id,
                    )
                )
            self._records[record.rollback_id] = record
            return Result.success(record)

    def list_for_organization(
        self, organization_id: OrganizationId
    ) -> Result[tuple[MigrationRollbackEvidence, ...], RepositoryError]:
        with self._lock:
            return Result.success(
                tuple(
                    record
                    for record in self._records.values()
                    if record.metadata.organization_id == organization_id
                )
            )

    @property
    def records(self) -> tuple[MigrationRollbackEvidence, ...]:
        """Return immutable snapshots for focused deterministic assertions."""
        with self._lock:
            return tuple(self._records.values())

    @staticmethod
    def _unavailable(correlation_id: CorrelationId) -> ErrorDetail:
        return ErrorDetail(
            ErrorCode.REPOSITORY_UNAVAILABLE,
            "Migration rollback evidence persistence is unavailable.",
            correlation_id,
            retryable=True,
        )


class RecoveryService:
    """Coordinate target-exact recovery and evidence-first migration rollback."""

    def __init__(
        self,
        recovery_repository: RecoveryActionRepository,
        version_restorer: ImmutableVersionRestorer,
        lesson_retention: LessonRetentionService | None = None,
        rollback_evidence_repository: RollbackEvidenceRepository | None = None,
        *,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._recovery_repository = recovery_repository
        self._version_restorer = version_restorer
        self._lesson_retention = lesson_retention or ReferenceLessonRetentionService()
        self._rollback_evidence = (
            rollback_evidence_repository or InMemoryRollbackEvidenceRepository()
        )
        self._clock = clock
        self._contract_decisions: list[ContractChangeApproval] = []

    @property
    def rollback_evidence_repository(self) -> RollbackEvidenceRepository:
        """Expose the evidence seam for composition and deterministic inspection."""
        return self._rollback_evidence

    @property
    def contract_decisions(self) -> tuple[ContractChangeApproval, ...]:
        """Return retained contract-change decisions without raw change content."""
        return tuple(self._contract_decisions)

    def approve_contract_change(
        self,
        correlation_id: CorrelationId,
        evidence: ContractChangeEvidence | Mapping[str, object],
        *,
        change_id: str = "contract-breaking-change",
    ) -> Result[ContractChangeApproval, ErrorDetail]:
        """Approve a contract-breaking change only when every required artifact exists."""
        try:
            normalized = self._coerce_contract_evidence(evidence)
            decision = ContractChangeApproval(
                change_id, normalized.is_complete, normalized, correlation_id
            )
        except (TypeError, ValueError) as error:
            return Result.failure(
                ErrorDetail(ErrorCode.VALIDATION_FAILED, str(error), correlation_id)
            )
        self._contract_decisions.append(decision)
        if not decision.approved:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.VALIDATION_FAILED,
                    "Contract-breaking change evidence is incomplete.",
                    correlation_id,
                    fields=tuple(
                        ErrorField(name, "required") for name in normalized.missing_artifacts
                    ),
                )
            )
        return Result.success(decision)

    def evaluate_contract_change(
        self,
        correlation_id: CorrelationId,
        evidence: ContractChangeEvidence | Mapping[str, object],
        *,
        change_id: str = "contract-breaking-change",
    ) -> Result[ContractChangeApproval, ErrorDetail]:
        """Return an explicit approved or blocked decision for every evidence vector."""
        try:
            normalized = self._coerce_contract_evidence(evidence)
            decision = ContractChangeApproval(
                change_id, normalized.is_complete, normalized, correlation_id
            )
        except (TypeError, ValueError) as error:
            return Result.failure(
                ErrorDetail(ErrorCode.VALIDATION_FAILED, str(error), correlation_id)
            )
        self._contract_decisions.append(decision)
        return Result.success(decision)

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
        """Persist rollback evidence, apply retention, and then restore the exact target."""
        try:
            if request is None:
                if (
                    organization_id is None
                    or pack_id is None
                    or designated_immutable_version is None
                    or approval_reference is None
                    or alc_retention_policy is None
                ):
                    raise ValueError(
                        "Migration rollback requires organization, pack, target, "
                        "approval, and retention policy."
                    )
                resolved = MigrationRollbackRequest(
                    organization_id=organization_id,
                    pack_id=pack_id,
                    designated_immutable_version=designated_immutable_version,
                    approval_reference=approval_reference,
                    affected_lessons=tuple(affected_lessons),
                    alc_retention_policy=alc_retention_policy,
                    evidence_references=tuple(evidence_references),
                    rollback_id=rollback_id,
                    approved=approved,
                )
            else:
                resolved = request
        except (TypeError, ValueError) as error:
            return Result.failure(
                ErrorDetail(ErrorCode.VALIDATION_FAILED, str(error), correlation_id)
            )
        if not resolved.approved:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.AUTHORIZATION_DENIED,
                    "Migration rollback requires explicit approval.",
                    correlation_id,
                )
            )
        if resolved.organization_id is None or resolved.pack_id is None:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.VALIDATION_FAILED,
                    "Migration rollback requires organization and pack identity.",
                    correlation_id,
                )
            )
        rollback_organization = resolved.organization_id
        rollback_pack = resolved.pack_id
        if resolved.evidence_references == ():
            resolved = resolved.with_evidence((resolved.approval_reference,))
        existing = self._find_rollback(rollback_organization, resolved.rollback_id, correlation_id)
        if not existing.is_success or existing.value is None:
            return Result.failure(existing.error or self._repository_error(correlation_id))
        existing_record = existing.value[1]
        if existing.value[0] and existing_record is not None:
            if existing_record.status is MigrationRollbackStatus.RESTORED:
                return Result.success(existing_record)
            retained = existing_record
        else:
            retained = self._new_rollback_evidence(resolved, correlation_id)
            persisted = self._rollback_evidence.append(retained)
            if not persisted.is_success or persisted.value is None:
                return Result.failure(
                    self._repository_failure(
                        persisted.error,
                        correlation_id,
                        "Rollback evidence persistence failed.",
                    )
                )
            retained = persisted.value

        retention = self._lesson_retention.apply(
            rollback_organization,
            rollback_pack,
            resolved.designated_immutable_version,
            resolved.affected_lessons,
            resolved.alc_retention_policy,
            correlation_id,
        )
        if not retention.is_success or retention.value is None:
            return Result.failure(retention.error or self._repository_error(correlation_id))
        restored = self._restore(resolved, correlation_id)
        if not restored.is_success or restored.value is None:
            return Result.failure(restored.error or self._repository_error(correlation_id))
        if restored.value != resolved.designated_immutable_version:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.INVALID_TRANSITION,
                    "Version restorer returned a non-designated immutable version.",
                    correlation_id,
                )
            )
        completed = MigrationRollbackEvidence(
            metadata=self._next_metadata(retained.metadata, correlation_id),
            rollback_id=retained.rollback_id,
            pack_id=retained.pack_id,
            designated_immutable_version=retained.designated_immutable_version,
            status=MigrationRollbackStatus.RESTORED,
            approval_reference=retained.approval_reference,
            affected_lesson_references=retained.affected_lesson_references,
            alc_retention_policy=retained.alc_retention_policy,
            evidence_references=retained.evidence_references,
            retention_records=retention.value,
            restored_immutable_version=restored.value,
            recorded_at=self._clock(),
        )
        finalized = self._rollback_evidence.replace(completed)
        if not finalized.is_success or finalized.value is None:
            return Result.failure(
                self._repository_failure(
                    finalized.error,
                    correlation_id,
                    "Completed rollback evidence persistence failed.",
                )
            )
        return Result.success(finalized.value)

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
        """Retain prior-version investigation evidence before target-exact restoration."""
        try:
            resolved = action or self._new_recovery_action(
                organization_id=organization_id,
                recovery_action_id=recovery_action_id,
                pack_id=pack_id,
                designated_immutable_version=designated_immutable_version,
                approval_reference=approval_reference,
                investigation_evidence_references=investigation_evidence_references,
                approved=approved,
                correlation_id=correlation_id,
            )
        except (TypeError, ValueError) as error:
            return Result.failure(
                ErrorDetail(ErrorCode.VALIDATION_FAILED, str(error), correlation_id)
            )
        if resolved.metadata.organization_id != organization_id and organization_id is not None:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.AUTHORIZATION_DENIED,
                    "Recovery action is outside the requested organization.",
                    correlation_id,
                )
            )
        if resolved.status is RecoveryActionStatus.RESTORED:
            if resolved.restored_immutable_version != resolved.designated_immutable_version:
                return Result.failure(
                    ErrorDetail(
                        ErrorCode.INVALID_TRANSITION,
                        "Recovery action target is not exact.",
                        correlation_id,
                    )
                )
            return Result.success(resolved)
        if resolved.status is not RecoveryActionStatus.APPROVED:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.AUTHORIZATION_DENIED,
                    "Recovery_Action requires explicit approval.",
                    correlation_id,
                )
            )
        existing = self._find_recovery(
            resolved.metadata.organization_id,
            resolved.recovery_action_id,
            correlation_id,
        )
        if not existing.is_success or existing.value is None:
            return Result.failure(existing.error or self._repository_error(correlation_id))
        existing_record = existing.value[1]
        if existing.value[0] and existing_record is not None:
            if existing_record.status is RecoveryActionStatus.RESTORED:
                return Result.success(existing_record)
            retained = existing_record
        else:
            persisted = self._recovery_repository.append(resolved)
            if not persisted.is_success or persisted.value is None:
                return Result.failure(
                    self._repository_failure(
                        persisted.error,
                        correlation_id,
                        "Recovery_Action evidence persistence failed.",
                    )
                )
            retained = persisted.value
        restored = self._version_restorer.restore(
            retained.metadata.organization_id,
            retained.pack_id,
            retained.designated_immutable_version,
            correlation_id,
        )
        if not restored.is_success or restored.value is None:
            return Result.failure(restored.error or self._repository_error(correlation_id))
        if restored.value != retained.designated_immutable_version:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.INVALID_TRANSITION,
                    "Recovery restored a non-designated immutable version.",
                    correlation_id,
                )
            )
        completed = RecoveryAction(
            metadata=self._next_metadata(retained.metadata, correlation_id),
            recovery_action_id=retained.recovery_action_id,
            pack_id=retained.pack_id,
            designated_immutable_version=retained.designated_immutable_version,
            status=RecoveryActionStatus.RESTORED,
            approval_reference=retained.approval_reference,
            investigation_evidence_references=retained.investigation_evidence_references,
            restored_immutable_version=restored.value,
        )
        finalized = self._replace_recovery(completed, correlation_id)
        if not finalized.is_success or finalized.value is None:
            return Result.failure(finalized.error or self._repository_error(correlation_id))
        return Result.success(finalized.value)

    # Design terminology aliases retain the integration surface used by the spec.
    approveContractChange = approve_contract_change  # noqa: N815
    evaluateContractChange = evaluate_contract_change  # noqa: N815
    recoverAction = recover  # noqa: N815
    restore = recover

    def _restore(
        self, request: MigrationRollbackRequest, correlation_id: CorrelationId
    ) -> Result[str, ErrorDetail]:
        if request.organization_id is None or request.pack_id is None:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.VALIDATION_FAILED,
                    "Migration rollback requires organization and pack identity.",
                    correlation_id,
                )
            )
        return self._version_restorer.restore(
            request.organization_id,
            request.pack_id,
            request.designated_immutable_version,
            correlation_id,
        )

    def _replace_recovery(
        self, record: RecoveryAction, correlation_id: CorrelationId
    ) -> Result[RecoveryAction, ErrorDetail]:
        replacer = getattr(self._recovery_repository, "replace", None)
        if not callable(replacer):
            return Result.failure(
                ErrorDetail(
                    ErrorCode.REPOSITORY_UNAVAILABLE,
                    "Recovery_Action completion persistence is unavailable.",
                    correlation_id,
                    retryable=True,
                )
            )
        try:
            result = replacer(record)
        except Exception:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.REPOSITORY_UNAVAILABLE,
                    "Recovery_Action completion persistence is unavailable.",
                    correlation_id,
                    retryable=True,
                )
            )
        if not result.is_success or result.value is None:
            return Result.failure(
                self._repository_failure(
                    result.error,
                    correlation_id,
                    "Recovery_Action completion persistence failed.",
                )
            )
        return Result.success(result.value)

    def _find_recovery(
        self,
        organization_id: OrganizationId,
        action_id: RecoveryActionId,
        correlation_id: CorrelationId,
    ) -> Result[tuple[bool, RecoveryAction | None], ErrorDetail]:
        records = self._recovery_repository.list_for_organization(organization_id)
        if not records.is_success or records.value is None:
            return Result.failure(
                self._repository_failure(
                    records.error, correlation_id, "Recovery_Action lookup failed."
                )
            )
        found = next(
            (record for record in records.value if record.recovery_action_id == action_id),
            None,
        )
        return Result.success((found is not None, found))

    def _find_rollback(
        self,
        organization_id: OrganizationId,
        rollback_id: str | None,
        correlation_id: CorrelationId,
    ) -> Result[tuple[bool, MigrationRollbackEvidence | None], ErrorDetail]:
        if rollback_id is None:
            return Result.success((False, None))
        records = self._rollback_evidence.list_for_organization(organization_id)
        if not records.is_success or records.value is None:
            return Result.failure(
                self._repository_failure(
                    records.error, correlation_id, "Rollback evidence lookup failed."
                )
            )
        found = next(
            (record for record in records.value if record.rollback_id == rollback_id),
            None,
        )
        return Result.success((found is not None, found))

    def _new_rollback_evidence(
        self, request: MigrationRollbackRequest, correlation_id: CorrelationId
    ) -> MigrationRollbackEvidence:
        if request.organization_id is None or request.pack_id is None:
            raise ValueError("Migration rollback requires organization and pack identity.")
        return MigrationRollbackEvidence(
            metadata=self._metadata(request.organization_id, correlation_id),
            rollback_id=request.rollback_id or str(new_record_id()),
            pack_id=request.pack_id,
            designated_immutable_version=request.designated_immutable_version,
            status=MigrationRollbackStatus.APPROVED,
            approval_reference=request.approval_reference,
            affected_lesson_references=tuple(
                str(lesson.lesson_id) for lesson in request.affected_lessons
            ),
            alc_retention_policy=request.alc_retention_policy,
            evidence_references=request.evidence_references,
            recorded_at=self._clock(),
        )

    def _new_recovery_action(
        self,
        *,
        organization_id: OrganizationId | None,
        recovery_action_id: RecoveryActionId | None,
        pack_id: DomainPackId | None,
        designated_immutable_version: str | None,
        approval_reference: str | None,
        investigation_evidence_references: Sequence[str],
        approved: bool,
        correlation_id: CorrelationId,
    ) -> RecoveryAction:
        if organization_id is None or pack_id is None or designated_immutable_version is None:
            raise ValueError("Recovery_Action requires organization, pack, and designated version.")
        if approval_reference is None:
            raise ValueError("Recovery_Action requires an approval reference.")
        references = tuple(investigation_evidence_references)
        if not references:
            raise ValueError("Recovery_Action requires prior-version investigation evidence.")
        return RecoveryAction(
            metadata=self._metadata(organization_id, correlation_id),
            recovery_action_id=recovery_action_id or RecoveryActionId(str(new_record_id())),
            pack_id=pack_id,
            designated_immutable_version=designated_immutable_version,
            status=(RecoveryActionStatus.APPROVED if approved else RecoveryActionStatus.HALTED),
            approval_reference=approval_reference,
            investigation_evidence_references=references,
        )

    @staticmethod
    def _coerce_contract_evidence(
        evidence: ContractChangeEvidence | Mapping[str, object],
    ) -> ContractChangeEvidence:
        return (
            evidence
            if isinstance(evidence, ContractChangeEvidence)
            else ContractChangeEvidence.from_mapping(evidence)
        )

    def _metadata(
        self, organization_id: OrganizationId, correlation_id: CorrelationId
    ) -> RecordMetadata:
        timestamp = self._clock()
        return RecordMetadata(
            record_id=new_record_id(),
            organization_id=organization_id,
            correlation_id=correlation_id,
            schema_version=SCHEMA_VERSION,
            version=1,
            created_at=timestamp,
            updated_at=timestamp,
        )

    def _next_metadata(
        self, metadata: RecordMetadata, correlation_id: CorrelationId
    ) -> RecordMetadata:
        timestamp = self._clock()
        return RecordMetadata(
            record_id=new_record_id(),
            organization_id=metadata.organization_id,
            correlation_id=correlation_id,
            schema_version=metadata.schema_version,
            version=metadata.version + 1,
            created_at=metadata.created_at,
            updated_at=timestamp,
        )

    @staticmethod
    def _repository_failure(
        error: RepositoryError | None,
        correlation_id: CorrelationId,
        fallback: str,
    ) -> ErrorDetail:
        if error is None:
            return ErrorDetail(
                ErrorCode.REPOSITORY_UNAVAILABLE,
                fallback,
                correlation_id,
                retryable=True,
            )
        return ErrorDetail(
            error.code,
            error.message,
            correlation_id,
            retryable=error.retryable,
            fields=error.fields,
        )

    @staticmethod
    def _repository_error(correlation_id: CorrelationId) -> ErrorDetail:
        return ErrorDetail(
            ErrorCode.REPOSITORY_UNAVAILABLE,
            "Recovery persistence is unavailable.",
            correlation_id,
            retryable=True,
        )


@dataclass(frozen=True, slots=True)
class MigrationRollbackRequest:
    """Validated command input for one approved migration rollback."""

    organization_id: OrganizationId | None
    pack_id: DomainPackId | None
    designated_immutable_version: str
    approval_reference: str
    affected_lessons: tuple[Lesson, ...] = ()
    alc_retention_policy: str = "retain"
    evidence_references: tuple[str, ...] = ()
    rollback_id: str | None = None
    approved: bool = True

    def __post_init__(self) -> None:
        if self.organization_id is None or self.pack_id is None:
            raise ValueError("Migration rollback requires organization and pack identity.")
        validate_semantic_version(self.designated_immutable_version, "designated_immutable_version")
        if not self.approval_reference.strip():
            raise ValueError("approval_reference must be non-empty.")
        if not self.alc_retention_policy.strip():
            raise ValueError("alc_retention_policy must be non-empty.")
        if self.rollback_id is not None and not self.rollback_id.strip():
            raise ValueError("rollback_id must be non-empty when provided.")
        object.__setattr__(self, "affected_lessons", tuple(self.affected_lessons))
        object.__setattr__(
            self, "evidence_references", _unique_references(self.evidence_references)
        )

    def with_evidence(self, references: Sequence[str]) -> MigrationRollbackRequest:
        return MigrationRollbackRequest(
            organization_id=self.organization_id,
            pack_id=self.pack_id,
            designated_immutable_version=self.designated_immutable_version,
            approval_reference=self.approval_reference,
            affected_lessons=self.affected_lessons,
            alc_retention_policy=self.alc_retention_policy,
            evidence_references=tuple(references),
            rollback_id=self.rollback_id,
            approved=self.approved,
        )


def _unique_references(values: Sequence[str]) -> tuple[str, ...]:
    references = tuple(str(value).strip() for value in values)
    if any(not value for value in references):
        raise ValueError("Evidence references must be non-empty.")
    return tuple(dict.fromkeys(references))


def _required_references(values: Sequence[str], name: str) -> None:
    references = tuple(str(value) for value in values)
    if any(not value.strip() for value in references):
        raise ValueError(f"{name} references must be non-empty.")


def _retention_outcome(policy_reference: str) -> LessonRetentionOutcome:
    normalized = policy_reference.strip().casefold()
    if normalized in {"retain", "keep"}:
        return LessonRetentionOutcome.RETAINED
    if normalized in {"stale", "archive", "archived"}:
        return LessonRetentionOutcome.STALE
    if normalized in {"revoke", "revoked"}:
        return LessonRetentionOutcome.REVOKED
    if normalized in {"delete", "deleted"}:
        return LessonRetentionOutcome.DELETED
    return LessonRetentionOutcome.APPLIED


# Design terminology aliases.
Recovery_Action = RecoveryAction
Migration_Rollback_Evidence = MigrationRollbackEvidence
Contract_Change_Evidence = ContractChangeEvidence
