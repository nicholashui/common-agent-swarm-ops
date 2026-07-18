"""Deterministic local storage for scoped memory and its audit safety latch."""

from __future__ import annotations

from datetime import datetime
from threading import RLock

from app.memory.models import AuditUnavailableLatch, MemoryScope, ScopedMemory
from app.models.contracts import ErrorCode, ErrorDetail, RepositoryError, Result
from app.models.identifiers import CorrelationId, OrganizationId, RecordId


class InMemoryMemoryRepository:
    """Lock-protected scoped-memory store with a shared durable latch state."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._records: dict[RecordId, ScopedMemory] = {}
        self._audit_latch = AuditUnavailableLatch(active=False, tripped_at=None)

    def create(self, record: ScopedMemory) -> Result[ScopedMemory, RepositoryError]:
        """Store an immutable scoped-memory record exactly once."""
        with self._lock:
            if record.metadata.record_id in self._records:
                return Result.failure(
                    self._error(ErrorCode.CONFLICT, "Memory record already exists.")
                )
            self._records[record.metadata.record_id] = record
            return Result.success(record)

    def get(
        self, organization_id: OrganizationId, record_id: RecordId
    ) -> Result[ScopedMemory, RepositoryError]:
        """Return a memory record only within its owning organization."""
        with self._lock:
            record = self._records.get(record_id)
            if record is None or record.metadata.organization_id != organization_id:
                return Result.failure(
                    self._error(ErrorCode.NOT_FOUND, "Memory record was not found.")
                )
            return Result.success(record)

    def records_for_scope(
        self, organization_id: OrganizationId, scope: MemoryScope
    ) -> Result[tuple[ScopedMemory, ...], RepositoryError]:
        """Return records only for the exact tenant and approved scope boundary."""
        with self._lock:
            records = tuple(
                record
                for record in self._records.values()
                if record.metadata.organization_id == organization_id and record.scope == scope
            )
            return Result.success(records)


    def get_audit_unavailable_latch(
        self,
    ) -> Result[AuditUnavailableLatch, RepositoryError]:
        """Return the durable high-impact write safety state."""
        with self._lock:
            return Result.success(self._audit_latch)

    def trip_audit_unavailable_latch(
        self, tripped_at: datetime
    ) -> Result[AuditUnavailableLatch, RepositoryError]:
        """Persist the first audit failure and block later high-impact writes."""
        with self._lock:
            if not self._audit_latch.active:
                self._audit_latch = AuditUnavailableLatch(active=True, tripped_at=tripped_at)
            return Result.success(self._audit_latch)

    def clear_audit_unavailable_latch(
        self,
    ) -> Result[AuditUnavailableLatch, RepositoryError]:
        """Clear the durable block only after the service records a health probe."""
        with self._lock:
            self._audit_latch = AuditUnavailableLatch(active=False, tripped_at=None)
            return Result.success(self._audit_latch)

    def records(self) -> tuple[ScopedMemory, ...]:
        """Return immutable snapshots for deterministic local inspection."""
        with self._lock:
            return tuple(self._records.values())

    @staticmethod
    def _error(code: ErrorCode, message: str) -> ErrorDetail:
        return ErrorDetail(code, message, CorrelationId("memory-repository"))