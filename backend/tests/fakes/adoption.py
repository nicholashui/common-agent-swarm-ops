"""Deterministic adoption repositories with isolated, configurable failure seams."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field, replace
from threading import RLock
from typing import Protocol

from app.models.common import RecordMetadata
from app.models.contracts import ErrorCode, ErrorDetail, RepositoryError, Result
from app.models.control_plane import (
    AgentLifecycle,
    AgentNodeAttemptId,
    ArtifactAvailabilityStatus,
    ArtifactHandoff,
    AuditRecord,
    AuthorizationDecision,
    InvocationAssociation,
    MaturityState,
    RecoveryAction,
    Registration,
    ReleaseReadinessDecision,
    VerificationRun,
)
from app.models.evidence import LearningEpisode, Lesson, RetrievalRecord
from app.models.identifiers import (
    AgentId,
    CorrelationId,
    DomainPackId,
    OrganizationId,
    RecordId,
)
from app.models.runs import AgentNodeAttempt, AgentNodeAttemptStatus


@dataclass
class FakeFailurePlan:
    """Mutable test-only controls for persistence and audit outages."""

    fail_persistence: bool = False
    fail_audit: bool = False
    persistence_operations: set[str] = field(default_factory=set)
    audit_operations: set[str] = field(default_factory=set)

    def persistence_is_unavailable(self, operation: str) -> bool:
        """Return whether this operation should fail before mutating fake state."""
        return self.fail_persistence or operation in self.persistence_operations

    def audit_is_unavailable(self, operation: str = "audit.append") -> bool:
        """Return whether the independent audit sink should fail."""
        return self.fail_audit or operation in self.audit_operations

    def fail_next_persistence(self, operation: str) -> None:
        """Schedule one named operation to fail on its next attempted write."""
        self.persistence_operations.add(operation)

    def fail_next_audit(self, operation: str = "audit.append") -> None:
        """Schedule one named audit operation to fail on its next attempted write."""
        self.audit_operations.add(operation)

    def consume_persistence_failure(self, operation: str) -> bool:
        """Consume a one-shot operation failure while preserving global failure mode."""
        if self.fail_persistence:
            return True
        if operation not in self.persistence_operations:
            return False
        self.persistence_operations.remove(operation)
        return True

    def consume_audit_failure(self, operation: str = "audit.append") -> bool:
        """Consume a one-shot audit failure while preserving global failure mode."""
        if self.fail_audit:
            return True
        if operation not in self.audit_operations:
            return False
        self.audit_operations.remove(operation)
        return True


class _RecordWithMetadata(Protocol):
    @property
    def metadata(self) -> RecordMetadata: ...


class _AppendOnlyStore[RecordT: _RecordWithMetadata, KeyT]:
    """Thread-safe append-only store shared by deterministic adoption fakes."""

    def __init__(
        self,
        failure_plan: FakeFailurePlan,
        operation: str,
        label: str,
        key_for: Callable[[RecordT], KeyT],
    ) -> None:
        self.failure_plan = failure_plan
        self._operation = operation
        self._label = label
        self._key_for = key_for
        self._lock = RLock()
        self._records: dict[KeyT, RecordT] = {}
        self._record_ids: set[RecordId] = set()

    def append(self, record: RecordT) -> Result[RecordT, RepositoryError]:
        """Append one immutable record, failing before state changes when configured."""
        with self._lock:
            if self.failure_plan.consume_persistence_failure(self._operation):
                return Result.failure(self._unavailable())
            key = self._key_for(record)
            if key in self._records or record.metadata.record_id in self._record_ids:
                return Result.failure(self._conflict(f"{self._label} already exists."))
            self._records[key] = record
            self._record_ids.add(record.metadata.record_id)
            return Result.success(record)

    def replace(self, record: RecordT) -> Result[RecordT, RepositoryError]:
        """Replace one append-only current snapshot while preserving its logical key."""
        with self._lock:
            if self.failure_plan.consume_persistence_failure(self._operation):
                return Result.failure(self._unavailable())
            key = self._key_for(record)
            existing = self._records.get(key)
            if existing is None:
                return Result.failure(self._missing())
            if existing.metadata.organization_id != record.metadata.organization_id:
                return Result.failure(
                    self._conflict(f"{self._label} organization conflicts.")
                )
            self._records[key] = record
            self._record_ids.add(record.metadata.record_id)
            return Result.success(record)

    def get(
        self, organization_id: OrganizationId, record_id: RecordId
    ) -> Result[RecordT, RepositoryError]:
        """Return one immutable record only within its organization."""
        with self._lock:
            record = next(
                (
                    candidate
                    for candidate in self._records.values()
                    if candidate.metadata.record_id == record_id
                ),
                None,
            )
            return self._scoped(record, organization_id)

    def list_for_organization(
        self, organization_id: OrganizationId
    ) -> Result[tuple[RecordT, ...], RepositoryError]:
        """Return records in deterministic insertion order."""
        with self._lock:
            return Result.success(
                tuple(
                    record
                    for record in self._records.values()
                    if record.metadata.organization_id == organization_id
                )
            )

    def records(self) -> tuple[RecordT, ...]:
        """Return local immutable snapshots for focused assertions."""
        with self._lock:
            return tuple(self._records.values())

    def _record_for_key(self, key: KeyT) -> RecordT | None:
        return self._records.get(key)

    def _scoped(
        self, record: RecordT | None, organization_id: OrganizationId
    ) -> Result[RecordT, RepositoryError]:
        if record is None or record.metadata.organization_id != organization_id:
            return Result.failure(self._missing())
        return Result.success(record)

    def _missing(self) -> ErrorDetail:
        return ErrorDetail(
            ErrorCode.NOT_FOUND,
            f"{self._label} was not found.",
            self._correlation_id(),
        )

    def _conflict(self, message: str) -> ErrorDetail:
        return ErrorDetail(ErrorCode.CONFLICT, message, self._correlation_id())

    def _unavailable(self) -> ErrorDetail:
        return ErrorDetail(
            ErrorCode.REPOSITORY_UNAVAILABLE,
            f"{self._label} persistence is unavailable.",
            self._correlation_id(),
            retryable=True,
        )

    def _correlation_id(self) -> CorrelationId:
        return CorrelationId(f"fake-{self._operation}")


class DeterministicRegistrationRepository(
    _AppendOnlyStore[Registration, tuple[DomainPackId, str]]
):
    """Registration fake enforcing immutable ``(pack_id, immutable_version)`` identity."""

    def __init__(self, failure_plan: FakeFailurePlan | None = None) -> None:
        super().__init__(
            failure_plan or FakeFailurePlan(),
            "registration.append",
            "Registration",
            lambda record: record.identity_key,
        )

    def get_by_pack_version(
        self,
        organization_id: OrganizationId,
        pack_id: DomainPackId,
        immutable_version: str,
    ) -> Result[Registration, RepositoryError]:
        with self._lock:
            return self._scoped(
                self._record_for_key((pack_id, immutable_version)), organization_id
            )


class DeterministicInvocationAssociationRepository(
    _AppendOnlyStore[InvocationAssociation, str]
):
    """Invocation fake whose record is complete before a caller may start a node."""

    def __init__(self, failure_plan: FakeFailurePlan | None = None) -> None:
        super().__init__(
            failure_plan or FakeFailurePlan(),
            "invocation.append",
            "Invocation association",
            lambda record: str(record.invocation_id),
        )

    def get_by_invocation_id(
        self, organization_id: OrganizationId, invocation_id: str
    ) -> Result[InvocationAssociation, RepositoryError]:
        with self._lock:
            return self._scoped(self._record_for_key(invocation_id), organization_id)


class DeterministicAuthorizationDecisionRepository(
    _AppendOnlyStore[AuthorizationDecision, object]
):
    """Append-only authorization evidence fake."""

    def __init__(self, failure_plan: FakeFailurePlan | None = None) -> None:
        super().__init__(
            failure_plan or FakeFailurePlan(),
            "authorization.append",
            "Authorization decision",
            lambda record: record.decision_id,
        )


class DeterministicArtifactHandoffRepository(_AppendOnlyStore[ArtifactHandoff, object]):
    """Opaque handoff fake with availability and simple lineage cycle barriers."""

    def __init__(self, failure_plan: FakeFailurePlan | None = None) -> None:
        super().__init__(
            failure_plan or FakeFailurePlan(),
            "handoff.append",
            "Artifact handoff",
            lambda record: record.handoff_id,
        )

    def append(
        self, record: ArtifactHandoff
    ) -> Result[ArtifactHandoff, RepositoryError]:
        with self._lock:
            if str(record.handoff_id) in record.parent_lineage:
                return Result.failure(
                    self._conflict("Artifact handoff lineage contains a cycle.")
                )
            for parent_reference in record.parent_lineage:
                parent = self._record_for_key(parent_reference)
                if (
                    parent is not None
                    and str(record.handoff_id) in parent.parent_lineage
                ):
                    return Result.failure(
                        self._conflict("Artifact handoff lineage contains a cycle.")
                    )
            return super().append(record)

    def available_for_downstream(
        self, organization_id: OrganizationId
    ) -> Result[tuple[ArtifactHandoff, ...], RepositoryError]:
        with self._lock:
            return Result.success(
                tuple(
                    record
                    for record in self._records.values()
                    if record.metadata.organization_id == organization_id
                    and record.availability is ArtifactAvailabilityStatus.AVAILABLE
                    and record.metadata_persisted
                )
            )


class DeterministicAgentLifecycleRepository(_AppendOnlyStore[AgentLifecycle, object]):
    """Append-only lifecycle evidence fake."""

    def __init__(self, failure_plan: FakeFailurePlan | None = None) -> None:
        super().__init__(
            failure_plan or FakeFailurePlan(),
            "lifecycle.append",
            "Agent lifecycle",
            lambda record: record.lifecycle_id,
        )


class DeterministicAgentNodeAttemptRepository(
    _AppendOnlyStore[AgentNodeAttempt, object]
):
    """Attempt fake keyed by the immutable attempt identifier."""

    def __init__(self, failure_plan: FakeFailurePlan | None = None) -> None:
        super().__init__(
            failure_plan or FakeFailurePlan(),
            "attempt.append",
            "Agent node attempt",
            lambda record: record.attempt_id,
        )

    def get_by_attempt_id(
        self, organization_id: OrganizationId, attempt_id: AgentNodeAttemptId
    ) -> Result[AgentNodeAttempt, RepositoryError]:
        with self._lock:
            return self._scoped(self._record_for_key(attempt_id), organization_id)

    def mark_blocked_for_recovery(
        self,
        organization_id: OrganizationId,
        attempt_id: AgentNodeAttemptId,
        correlation_id: CorrelationId,
    ) -> Result[AgentNodeAttempt, RepositoryError]:
        """Retain a blocked attempt state after terminal evidence cannot be written."""
        with self._lock:
            if self.failure_plan.consume_persistence_failure("attempt.block"):
                return Result.failure(self._unavailable())
            current = self._record_for_key(attempt_id)
            scoped = self._scoped(current, organization_id)
            if not scoped.is_success or scoped.value is None:
                return scoped
            blocked = replace(
                scoped.value,
                metadata=replace(
                    scoped.value.metadata,
                    correlation_id=correlation_id,
                    version=scoped.value.metadata.version + 1,
                ),
                status=AgentNodeAttemptStatus.BLOCKED,
                terminal_outcome_reference=(
                    scoped.value.terminal_outcome_reference or f"recovery:{attempt_id}"
                ),
            )
            self._records[attempt_id] = blocked
            return Result.success(blocked)


class DeterministicRetrievalRecordRepository(_AppendOnlyStore[RetrievalRecord, object]):
    """Retrieval fake enforcing exactly one record for each node attempt."""

    def __init__(self, failure_plan: FakeFailurePlan | None = None) -> None:
        super().__init__(
            failure_plan or FakeFailurePlan(),
            "retrieval.append",
            "Retrieval record",
            lambda record: record.retrieval_record_id,
        )
        self._attempt_ids: set[AgentNodeAttemptId] = set()

    def append(
        self, record: RetrievalRecord
    ) -> Result[RetrievalRecord, RepositoryError]:
        with self._lock:
            if record.attempt_id in self._attempt_ids:
                return Result.failure(
                    self._conflict("A retrieval record already exists for attempt.")
                )
            result = super().append(record)
            if result.is_success:
                self._attempt_ids.add(record.attempt_id)
            return result

    def get_by_attempt_id(
        self, organization_id: OrganizationId, attempt_id: AgentNodeAttemptId
    ) -> Result[RetrievalRecord, RepositoryError]:
        with self._lock:
            record = next(
                (
                    item
                    for item in self._records.values()
                    if item.attempt_id == attempt_id
                ),
                None,
            )
            return self._scoped(record, organization_id)


class DeterministicLearningEpisodeRepository(_AppendOnlyStore[LearningEpisode, object]):
    """Learning fake enforcing one immutable terminal episode per attempt."""

    def __init__(self, failure_plan: FakeFailurePlan | None = None) -> None:
        super().__init__(
            failure_plan or FakeFailurePlan(),
            "episode.append",
            "Learning episode",
            lambda record: record.episode_id,
        )
        self._attempt_ids: set[AgentNodeAttemptId] = set()

    def append(
        self, record: LearningEpisode
    ) -> Result[LearningEpisode, RepositoryError]:
        with self._lock:
            if record.attempt_id in self._attempt_ids:
                return Result.failure(
                    self._conflict("A terminal episode already exists for attempt.")
                )
            result = super().append(record)
            if result.is_success:
                self._attempt_ids.add(record.attempt_id)
            return result

    def get_by_attempt_id(
        self, organization_id: OrganizationId, attempt_id: AgentNodeAttemptId
    ) -> Result[LearningEpisode, RepositoryError]:
        with self._lock:
            record = next(
                (
                    item
                    for item in self._records.values()
                    if item.attempt_id == attempt_id
                ),
                None,
            )
            return self._scoped(record, organization_id)


class DeterministicLessonRepository(_AppendOnlyStore[Lesson, object]):
    """Reference-only lesson fake with complete scope matching on retrieval."""

    def __init__(self, failure_plan: FakeFailurePlan | None = None) -> None:
        super().__init__(
            failure_plan or FakeFailurePlan(),
            "lesson.append",
            "Lesson",
            lambda record: record.lesson_id,
        )

    def retrievable_for(
        self,
        organization_id: OrganizationId,
        domain_id: str,
        pack_version: str,
        agent_id: AgentId,
        memory_scope: str,
    ) -> Result[tuple[Lesson, ...], RepositoryError]:
        with self._lock:
            return Result.success(
                tuple(
                    lesson
                    for lesson in self._records.values()
                    if lesson.metadata.organization_id == organization_id
                    and lesson.domain_id == domain_id
                    and lesson.pack_version_range.contains(pack_version)
                    and lesson.agent_id == agent_id
                    and lesson.memory_scope == memory_scope
                    and lesson.retrievable
                    and not lesson.revoked
                    and not lesson.stale
                )
            )

    def revoke(
        self, organization_id: OrganizationId, lesson_id: str
    ) -> Result[Lesson, RepositoryError]:
        """Persist the revoked Lesson version only after the audit barrier."""
        with self._lock:
            if self.failure_plan.consume_persistence_failure("lesson.revoke"):
                return Result.failure(self._unavailable())
            current = next(
                (
                    lesson
                    for lesson in self._records.values()
                    if str(lesson.lesson_id) == lesson_id
                ),
                None,
            )
            scoped = self._scoped(current, organization_id)
            if not scoped.is_success or scoped.value is None:
                return scoped
            if scoped.value.revoked and not scoped.value.retrievable:
                return Result.success(scoped.value)
            revoked = replace(
                scoped.value,
                metadata=replace(
                    scoped.value.metadata,
                    version=scoped.value.metadata.version + 1,
                    updated_at=scoped.value.metadata.updated_at,
                ),
                retrievable=False,
                revoked=True,
            )
            self._records[scoped.value.lesson_id] = revoked
            return Result.success(revoked)


class DeterministicVerificationRunRepository(_AppendOnlyStore[VerificationRun, object]):
    """Append-only verification run fake."""

    def __init__(self, failure_plan: FakeFailurePlan | None = None) -> None:
        super().__init__(
            failure_plan or FakeFailurePlan(),
            "verification.append",
            "Verification run",
            lambda record: record.verification_run_id,
        )


class DeterministicReleaseReadinessDecisionRepository(
    _AppendOnlyStore[ReleaseReadinessDecision, object]
):
    """Release fake enforcing one terminal decision per evaluated workflow version."""

    def __init__(self, failure_plan: FakeFailurePlan | None = None) -> None:
        super().__init__(
            failure_plan or FakeFailurePlan(),
            "release.append",
            "Release readiness decision",
            lambda record: (
                record.pack_id,
                record.immutable_version,
                record.workflow_id,
            ),
        )

    def get_terminal(
        self,
        organization_id: OrganizationId,
        pack_id: DomainPackId,
        immutable_version: str,
        workflow_id: str,
    ) -> Result[ReleaseReadinessDecision, RepositoryError]:
        with self._lock:
            return self._scoped(
                self._record_for_key((pack_id, immutable_version, workflow_id)),
                organization_id,
            )


class DeterministicRecoveryActionRepository(_AppendOnlyStore[RecoveryAction, object]):
    """Append-only recovery evidence fake."""

    def __init__(self, failure_plan: FakeFailurePlan | None = None) -> None:
        super().__init__(
            failure_plan or FakeFailurePlan(),
            "recovery.append",
            "Recovery action",
            lambda record: record.recovery_action_id,
        )


class DeterministicMaturityStateRepository(_AppendOnlyStore[MaturityState, object]):
    """Maturity fake enforcing independent pack-version-agent identity."""

    def __init__(self, failure_plan: FakeFailurePlan | None = None) -> None:
        super().__init__(
            failure_plan or FakeFailurePlan(),
            "maturity.append",
            "Maturity state",
            lambda record: record.identity_key,
        )


class DeterministicAuditRepository:
    """Independent append-only adoption audit fake with configurable outage behavior."""

    def __init__(self, failure_plan: FakeFailurePlan | None = None) -> None:
        self.failure_plan = failure_plan or FakeFailurePlan()
        self._lock = RLock()
        self._records: dict[str, AuditRecord] = {}

    def append(self, record: AuditRecord) -> Result[AuditRecord, RepositoryError]:
        with self._lock:
            if self.failure_plan.consume_audit_failure():
                return Result.failure(
                    ErrorDetail(
                        ErrorCode.AUDIT_UNAVAILABLE,
                        "Audit persistence is unavailable.",
                        record.metadata.correlation_id,
                        retryable=True,
                    )
                )
            if record.audit_id in self._records:
                return Result.failure(
                    ErrorDetail(
                        ErrorCode.CONFLICT,
                        "Audit record already exists.",
                        record.metadata.correlation_id,
                    )
                )
            self._records[record.audit_id] = record
            return Result.success(record)

    def list_for_organization(
        self, organization_id: OrganizationId
    ) -> Result[tuple[AuditRecord, ...], RepositoryError]:
        with self._lock:
            return Result.success(
                tuple(
                    record
                    for record in self._records.values()
                    if record.metadata.organization_id == organization_id
                )
            )

    @property
    def records(self) -> tuple[AuditRecord, ...]:
        """Return immutable audit snapshots for assertions."""
        with self._lock:
            return tuple(self._records.values())


class DeterministicAdoptionRepositories:
    """Isolated repository bundle for tests; it never reads or writes production storage."""

    def __init__(self, failure_plan: FakeFailurePlan | None = None) -> None:
        self.failure_plan = failure_plan or FakeFailurePlan()
        self.registrations = DeterministicRegistrationRepository(self.failure_plan)
        self.invocations = DeterministicInvocationAssociationRepository(
            self.failure_plan
        )
        self.authorizations = DeterministicAuthorizationDecisionRepository(
            self.failure_plan
        )
        self.handoffs = DeterministicArtifactHandoffRepository(self.failure_plan)
        self.lifecycle = DeterministicAgentLifecycleRepository(self.failure_plan)
        self.attempts = DeterministicAgentNodeAttemptRepository(self.failure_plan)
        self.retrievals = DeterministicRetrievalRecordRepository(self.failure_plan)
        self.episodes = DeterministicLearningEpisodeRepository(self.failure_plan)
        self.lessons = DeterministicLessonRepository(self.failure_plan)
        self.verifications = DeterministicVerificationRunRepository(self.failure_plan)
        self.release_decisions = DeterministicReleaseReadinessDecisionRepository(
            self.failure_plan
        )
        self.recoveries = DeterministicRecoveryActionRepository(self.failure_plan)
        self.maturity = DeterministicMaturityStateRepository(self.failure_plan)
        self.audit = DeterministicAuditRepository(self.failure_plan)

    @property
    def registration(self) -> DeterministicRegistrationRepository:
        """Singular compatibility alias for focused tests."""
        return self.registrations

    @property
    def invocation_associations(self) -> DeterministicInvocationAssociationRepository:
        """Descriptive alias for the invocation association store."""
        return self.invocations

    @property
    def learning_episodes(self) -> DeterministicLearningEpisodeRepository:
        """Descriptive alias for the terminal episode store."""
        return self.episodes

    @property
    def retrieval_records(self) -> DeterministicRetrievalRecordRepository:
        """Descriptive alias for the pre-action retrieval store."""
        return self.retrievals


# Short names make the test seam convenient without exposing a production persistence class.
FakeAdoptionRepositories = DeterministicAdoptionRepositories
FakeAuditRepository = DeterministicAuditRepository
InMemoryAdoptionRepositories = DeterministicAdoptionRepositories
