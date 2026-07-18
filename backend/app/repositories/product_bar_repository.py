"""Append-only, organization-scoped Product-Bar evidence retention."""

from __future__ import annotations

from threading import RLock

from app.evaluation.product_bar import ProductBarEvidenceRecord
from app.models.contracts import ErrorCode, ErrorDetail, RepositoryError, Result
from app.models.identifiers import CorrelationId, EvidenceId, OrganizationId, RecordId


class InMemoryProductBarEvidenceRepository:
    """Lock-protected local retention for immutable Product-Bar evidence records."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._records: dict[EvidenceId, ProductBarEvidenceRecord] = {}
        self._record_ids: dict[RecordId, EvidenceId] = {}

    def append(
        self, record: ProductBarEvidenceRecord
    ) -> Result[ProductBarEvidenceRecord, RepositoryError]:
        """Persist a unique evidence record without replacing earlier observations."""
        with self._lock:
            if record.evidence_id in self._records or record.metadata.record_id in self._record_ids:
                return Result.failure(
                    self._error(ErrorCode.CONFLICT, "Product-Bar evidence already exists.")
                )
            self._records[record.evidence_id] = record
            self._record_ids[record.metadata.record_id] = record.evidence_id
            return Result.success(record)

    def list_for_organization(
        self, organization_id: OrganizationId
    ) -> Result[tuple[ProductBarEvidenceRecord, ...], RepositoryError]:
        """Return immutable records visible to one organization only."""
        with self._lock:
            return Result.success(
                tuple(
                    record
                    for record in self._records.values()
                    if record.metadata.organization_id == organization_id
                )
            )

    def records(self) -> tuple[ProductBarEvidenceRecord, ...]:
        """Return all local snapshots for deterministic internal inspection."""
        with self._lock:
            return tuple(self._records.values())

    @staticmethod
    def _error(code: ErrorCode, message: str) -> ErrorDetail:
        return ErrorDetail(code, message, CorrelationId("product-bar-repository"))
