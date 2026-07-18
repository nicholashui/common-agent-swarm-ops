"""Repository protocols with explicit optimistic-concurrency seams."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Protocol, TypeVar, runtime_checkable

from app.models.audit import AuditEvent
from app.models.common import OptimisticTransition, VersionedRecord
from app.models.contracts import RepositoryError, Result
from app.models.evidence import EvidenceItem
from app.models.identifiers import ApprovalId, OrganizationId, RecordId, RunId
from app.models.runs import RunRecord

if TYPE_CHECKING:
    from app.evaluation.product_bar import ProductBarEvidenceRecord
    from app.governance.approvals import ApprovalDecision, ApprovalGate
    from app.memory.models import AuditUnavailableLatch, MemoryScope, ScopedMemory
    from app.runs.checkpoints import CheckpointRecord

T = TypeVar("T", bound=VersionedRecord)


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

    def get_audit_unavailable_latch(self) -> Result[AuditUnavailableLatch, RepositoryError]:
        """Return the durable high-impact write block state."""

    def trip_audit_unavailable_latch(
        self, tripped_at: datetime
    ) -> Result[AuditUnavailableLatch, RepositoryError]:
        """Persist the audit-outage block state."""

    def clear_audit_unavailable_latch(self) -> Result[AuditUnavailableLatch, RepositoryError]:
        """Clear the block only after an audit health check succeeds."""


@runtime_checkable
class EvaluationRepository(VersionedRepository[VersionedRecord], Protocol):
    """Version-guarded evaluation result persistence seam."""


@runtime_checkable
class ArtifactRepository(VersionedRepository[VersionedRecord], Protocol):
    """Version-guarded immutable artifact-version persistence seam."""
