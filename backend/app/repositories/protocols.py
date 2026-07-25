"""Repository protocols with explicit optimistic-concurrency seams."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Protocol, TypeVar, runtime_checkable

from app.models.audit import AuditEvent
from app.models.common import OptimisticTransition, VersionedRecord
from app.models.contracts import RepositoryError, Result
from app.models.evidence import EvidenceItem
from app.models.identifiers import (
    ApprovalId,
    CorrelationId,
    OrganizationId,
    RecordId,
    RunId,
)
from app.models.runs import RunRecord

if TYPE_CHECKING:
    from app.evaluation.product_bar import ProductBarEvidenceRecord
    from app.governance.approvals import ApprovalDecision, ApprovalGate
    from app.memory.models import AuditUnavailableLatch, MemoryScope, ScopedMemory
    from app.models.control_plane import (
        AgentLifecycle,
        AgentNodeAttemptId,
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
    from app.models.identifiers import AgentId, DomainPackId
    from app.models.runs import AgentNodeAttempt
    from app.runs.checkpoints import CheckpointRecord

# Records used in protocol base classes must be available at runtime: Python evaluates
# generic protocol bases while importing this module, even with postponed annotations.
from app.models.control_plane import (
    AgentLifecycle,
    AgentNodeAttemptId,
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
from app.models.identifiers import AgentId, DomainPackId
from app.models.runs import AgentNodeAttempt

T = TypeVar("T", bound=VersionedRecord)
A = TypeVar("A", bound=VersionedRecord)


@runtime_checkable
class VersionedRepository(Protocol[T]):
    """Persistence contract for immutable records transitioned by version."""

    def create(self, record: T) -> Result[T, RepositoryError]:
        """Persist an initial immutable record."""

    def get(
        self, organization_id: OrganizationId, record_id: RecordId
    ) -> Result[T, RepositoryError]:
        """Return one organization-scoped record."""

    def transition(
        self, record: T, transition: OptimisticTransition
    ) -> Result[T, RepositoryError]:
        """Persist only when the expected version still matches."""


@runtime_checkable
class RunRepository(VersionedRepository[RunRecord], Protocol):
    """Durable run storage; queue persistence precedes dispatch."""

    def create_queued(self, record: RunRecord) -> Result[RunRecord, RepositoryError]:
        """Persist a newly created run only in its pre-dispatch queued state."""

    def get_by_run_id(
        self, organization_id: OrganizationId, run_id: RunId
    ) -> Result[RunRecord, RepositoryError]:
        """Return a run scoped to its owning organization."""


@runtime_checkable
class AuditRepository(Protocol):
    """Append-only audit storage; audit events are never transitioned."""

    def append(self, event: AuditEvent) -> Result[AuditEvent, RepositoryError]:
        """Durably append one immutable audit event."""


@runtime_checkable
class EvidenceRepository(Protocol):
    """Append-only evidence storage used by operational gates."""

    def append(self, item: EvidenceItem) -> Result[EvidenceItem, RepositoryError]:
        """Durably append one immutable evidence item."""


@runtime_checkable
class ProductBarEvidenceRepository(Protocol):
    """Append-only local Product-Bar evidence storage seam."""

    def append(
        self, record: ProductBarEvidenceRecord
    ) -> Result[ProductBarEvidenceRecord, RepositoryError]:
        """Persist one immutable criterion-specific evidence record."""

    def list_for_organization(
        self, organization_id: OrganizationId
    ) -> Result[tuple[ProductBarEvidenceRecord, ...], RepositoryError]:
        """Return Product-Bar evidence only for the owning organization."""


@runtime_checkable
class ApprovalRepository(Protocol):
    """Organization-scoped approval gates with append-only decision submissions."""

    def create(self, record: ApprovalGate) -> Result[ApprovalGate, RepositoryError]:
        """Persist an initial paused approval gate."""

    def get(
        self, organization_id: OrganizationId, record_id: RecordId
    ) -> Result[ApprovalGate, RepositoryError]:
        """Return one approval gate by durable record ID within its organization."""

    def get_by_approval_id(
        self, organization_id: OrganizationId, approval_id: ApprovalId
    ) -> Result[ApprovalGate, RepositoryError]:
        """Return one approval gate by public ID within its organization."""

    def transition(
        self, record: ApprovalGate, transition: OptimisticTransition
    ) -> Result[ApprovalGate, RepositoryError]:
        """Persist an optimistic-concurrency-guarded approval gate transition."""

    def append_decision(
        self, decision: ApprovalDecision
    ) -> Result[ApprovalDecision, RepositoryError]:
        """Append an immutable decision, including invalid and denied submissions."""

    def decisions(
        self, organization_id: OrganizationId, approval_id: ApprovalId
    ) -> Result[tuple[ApprovalDecision, ...], RepositoryError]:
        """Return every submitted decision for one organization-scoped gate."""


@runtime_checkable
class CheckpointRepository(Protocol):
    """Organization-scoped durable graph checkpoint persistence seam."""

    def save(
        self, checkpoint: CheckpointRecord
    ) -> Result[CheckpointRecord, RepositoryError]:
        """Append one organization-scoped checkpoint without a local fallback."""

    def get_for_resume(
        self, organization_id: OrganizationId, run_id: RunId
    ) -> Result[CheckpointRecord, RepositoryError]:
        """Return only the latest checkpoint eligible for same-organization resume."""


@runtime_checkable
class PackRepository(VersionedRepository[VersionedRecord], Protocol):
    """Version-guarded domain-pack and agent registration persistence seam."""


@runtime_checkable
class MemoryRepository(Protocol):
    """Scoped-memory storage and its durable high-impact audit safety latch."""

    def create(self, record: ScopedMemory) -> Result[ScopedMemory, RepositoryError]:
        """Persist one immutable memory record."""

    def get(
        self, organization_id: OrganizationId, record_id: RecordId
    ) -> Result[ScopedMemory, RepositoryError]:
        """Return one record only from its owning organization."""

    def records_for_scope(
        self, organization_id: OrganizationId, scope: MemoryScope
    ) -> Result[tuple[ScopedMemory, ...], RepositoryError]:
        """Return only records that match the exact organization and scope."""

    def get_audit_unavailable_latch(
        self,
    ) -> Result[AuditUnavailableLatch, RepositoryError]:
        """Return the durable high-impact write block state."""

    def trip_audit_unavailable_latch(
        self, tripped_at: datetime
    ) -> Result[AuditUnavailableLatch, RepositoryError]:
        """Persist the audit-outage block state."""

    def clear_audit_unavailable_latch(
        self,
    ) -> Result[AuditUnavailableLatch, RepositoryError]:
        """Clear the block only after an audit health check succeeds."""


@runtime_checkable
class EvaluationRepository(VersionedRepository[VersionedRecord], Protocol):
    """Version-guarded evaluation result persistence seam."""


@runtime_checkable
class ArtifactRepository(VersionedRepository[VersionedRecord], Protocol):
    """Version-guarded immutable artifact-version persistence seam."""


@runtime_checkable
class AdoptionRecordRepository(Protocol[A]):
    """Append-only, organization-scoped persistence for adoption evidence."""

    def append(self, record: A) -> Result[A, RepositoryError]:
        """Persist one immutable adoption record."""

    def get(
        self, organization_id: OrganizationId, record_id: RecordId
    ) -> Result[A, RepositoryError]:
        """Return one record only inside its owning organization."""

    def list_for_organization(
        self, organization_id: OrganizationId
    ) -> Result[tuple[A, ...], RepositoryError]:
        """Return immutable records in deterministic insertion order."""


@runtime_checkable
class RegistrationRepository(AdoptionRecordRepository[Registration], Protocol):
    """Enforce one immutable registration per pack and version."""

    def get_by_pack_version(
        self,
        organization_id: OrganizationId,
        pack_id: DomainPackId,
        immutable_version: str,
    ) -> Result[Registration, RepositoryError]:
        """Return the registration for one immutable pack identity."""


@runtime_checkable
class InvocationAssociationRepository(
    AdoptionRecordRepository[InvocationAssociation], Protocol
):
    """Persist the complete invocation association before execution starts."""

    def get_by_invocation_id(
        self, organization_id: OrganizationId, invocation_id: str
    ) -> Result[InvocationAssociation, RepositoryError]:
        """Return one organization-scoped invocation association."""


@runtime_checkable
class AuthorizationDecisionRepository(
    AdoptionRecordRepository[AuthorizationDecision], Protocol
):
    """Retain immutable authorization outcomes independently of audit writes."""


@runtime_checkable
class ArtifactHandoffRepository(AdoptionRecordRepository[ArtifactHandoff], Protocol):
    """Persist opaque handoff metadata without accepting protected content."""

    def available_for_downstream(
        self, organization_id: OrganizationId
    ) -> Result[tuple[ArtifactHandoff, ...], RepositoryError]:
        """Return only metadata-confirmed handoffs available to downstream nodes."""


@runtime_checkable
class AgentLifecycleRepository(AdoptionRecordRepository[AgentLifecycle], Protocol):
    """Retain immutable lifecycle evidence for learning-required agents."""


@runtime_checkable
class AgentNodeAttemptRepository(AdoptionRecordRepository[AgentNodeAttempt], Protocol):
    """Retain attempt identities used by retrieval and terminal-episode barriers."""

    def get_by_attempt_id(
        self, organization_id: OrganizationId, attempt_id: AgentNodeAttemptId
    ) -> Result[AgentNodeAttempt, RepositoryError]:
        """Return one organization-scoped node attempt."""

    def mark_blocked_for_recovery(
        self,
        organization_id: OrganizationId,
        attempt_id: AgentNodeAttemptId,
        correlation_id: CorrelationId,
    ) -> Result[AgentNodeAttempt, RepositoryError]:
        """Durably block an attempt when terminal learning evidence needs recovery."""


@runtime_checkable
class RetrievalRecordRepository(AdoptionRecordRepository[RetrievalRecord], Protocol):
    """Enforce exactly one pre-action retrieval record for each attempt."""

    def get_by_attempt_id(
        self, organization_id: OrganizationId, attempt_id: AgentNodeAttemptId
    ) -> Result[RetrievalRecord, RepositoryError]:
        """Return the retrieval evidence for one node attempt."""


@runtime_checkable
class LearningEpisodeRepository(AdoptionRecordRepository[LearningEpisode], Protocol):
    """Enforce one immutable terminal learning episode per attempt."""

    def get_by_attempt_id(
        self, organization_id: OrganizationId, attempt_id: AgentNodeAttemptId
    ) -> Result[LearningEpisode, RepositoryError]:
        """Return the terminal episode for one node attempt."""


@runtime_checkable
class LessonRepository(AdoptionRecordRepository[Lesson], Protocol):
    """Retain scoped, assessed lessons as references to trusted content."""

    def retrievable_for(
        self,
        organization_id: OrganizationId,
        domain_id: str,
        pack_version: str,
        agent_id: AgentId,
        memory_scope: str,
    ) -> Result[tuple[Lesson, ...], RepositoryError]:
        """Return only current passed lessons matching every approved scope."""

    def revoke(
        self, organization_id: OrganizationId, lesson_id: str
    ) -> Result[Lesson, RepositoryError]:
        """Persist the post-audit revoked version of one Lesson."""


@runtime_checkable
class VerificationRunRepository(AdoptionRecordRepository[VerificationRun], Protocol):
    """Retain layered verification evidence without replacing prior runs."""


@runtime_checkable
class ReleaseReadinessDecisionRepository(
    AdoptionRecordRepository[ReleaseReadinessDecision], Protocol
):
    """Enforce one terminal release decision for an evaluated workflow version."""

    def get_terminal(
        self,
        organization_id: OrganizationId,
        pack_id: DomainPackId,
        immutable_version: str,
        workflow_id: str,
    ) -> Result[ReleaseReadinessDecision, RepositoryError]:
        """Return the terminal decision for one release evaluation identity."""


@runtime_checkable
class RecoveryActionRepository(AdoptionRecordRepository[RecoveryAction], Protocol):
    """Retain recovery evidence before any version restoration occurs."""

    def replace(
        self, record: RecoveryAction
    ) -> Result[RecoveryAction, RepositoryError]:
        """Retain the completed immutable snapshot for an approved recovery action."""


@runtime_checkable
class MaturityStateRepository(AdoptionRecordRepository[MaturityState], Protocol):
    """Retain independent maturity state for each pack-version agent."""


@runtime_checkable
class AuditRecordRepository(Protocol):
    """Append-only audit storage whose failure cannot turn a denial into an allow."""

    def append(self, record: AuditRecord) -> Result[AuditRecord, RepositoryError]:
        """Attempt to persist one immutable adoption audit record."""

    def list_for_organization(
        self, organization_id: OrganizationId
    ) -> Result[tuple[AuditRecord, ...], RepositoryError]:
        """Return audit records only within the owning organization."""
