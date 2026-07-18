"""Fail-closed scoped-memory writes guarded by provenance and audit health."""

from __future__ import annotations

from collections.abc import Callable, Collection
from dataclasses import dataclass
from datetime import datetime
from threading import RLock
from uuid import uuid4

from app.audit import AuditWriter
from app.memory.models import (
    MemoryImpact,
    MemoryScope,
    MemoryWrite,
    MemoryWritePath,
    ScopedMemory,
)
from app.models.audit import AuditDecision, AuditEvent
from app.models.common import SCHEMA_VERSION, RecordMetadata, utc_now
from app.models.contracts import ErrorCode, ErrorDetail, ErrorField, Result
from app.models.identifiers import (
    ActorId,
    AuditEventId,
    CorrelationId,
    OrganizationId,
    new_record_id,
)
from app.repositories.protocols import MemoryRepository


@dataclass(frozen=True, slots=True)
class MemoryWriteRequest:
    """The Host-derived context needed to persist one scoped-memory write."""

    write: MemoryWrite
    organization_id: OrganizationId
    correlation_id: CorrelationId
    approved_scopes: Collection[MemoryScope]
    path: MemoryWritePath = MemoryWritePath.NORMAL


class MemoryService:
    """Persist scoped memory only after high-impact provenance and audit checks pass."""

    def __init__(
        self,
        repository: MemoryRepository,
        audit_writer: AuditWriter,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._repository = repository
        self._audit_writer = audit_writer
        self._clock = clock
        self._lock = RLock()
        self._transient_latch_active = False

    def store(self, request: MemoryWriteRequest) -> Result[ScopedMemory, ErrorDetail]:
        """Store a write while enforcing its scope and high-impact audit obligations."""
        with self._lock:
            if request.write.impact is MemoryImpact.HIGH:
                latch = self._repository.get_audit_unavailable_latch()
                if not latch.is_success:
                    return self._repository_failure(request.correlation_id)
                latch_active = self._transient_latch_active or _required_value(latch).active
                if latch_active and not self._restore_audit_health(request):
                    return self._audit_unavailable(request.correlation_id)

            validation = self._validate(request)
            if validation is not None:
                self._audit_denial(request, validation.message)
                return Result.failure(validation)

            if request.write.impact is MemoryImpact.HIGH:
                audited = self._audit_writer.append(
                    self._audit_event(request, "memory.write", AuditDecision.RECORDED)
                )
                if not audited.recorded:
                    self._trip_audit_latch()
                    return self._audit_unavailable(request.correlation_id)

            timestamp = self._clock()
            record = ScopedMemory(
                metadata=RecordMetadata(
                    record_id=new_record_id(),
                    organization_id=request.organization_id,
                    correlation_id=request.correlation_id,
                    schema_version=SCHEMA_VERSION,
                    version=1,
                    created_at=timestamp,
                    updated_at=timestamp,
                ),
                scope=request.write.scope,
                impact=request.write.impact,
                writer=request.write.writer,
                content_reference=request.write.content_reference,
                provenance=request.write.provenance,
                source_log_set_id=request.write.source_log_set_id,
            )
            return self._repository.create(record)


    def _restore_audit_health(self, request: MemoryWriteRequest) -> bool:
        probe = self._audit_event(
            request,
            "memory.audit_health_check",
            AuditDecision.RECORDED,
        )
        if not self._audit_writer.check_health(probe).recorded:
            return False
        cleared = self._repository.clear_audit_unavailable_latch()
        if not cleared.is_success:
            return False
        self._transient_latch_active = False
        return True

    def _trip_audit_latch(self) -> None:
        self._transient_latch_active = True
        self._repository.trip_audit_unavailable_latch(self._clock())

    def _audit_denial(self, request: MemoryWriteRequest, reason: str) -> None:
        if request.write.impact is not MemoryImpact.HIGH:
            return
        recorded = self._audit_writer.append(
            self._audit_event(request, "memory.write.denied", AuditDecision.DENIED, reason)
        )
        if not recorded.recorded:
            self._trip_audit_latch()

    @staticmethod
    def _validate(request: MemoryWriteRequest) -> ErrorDetail | None:
        write = request.write
        if not write.writer.strip():
            return _validation_error(request.correlation_id, "writer", "Writer is required.")
        if not write.content_reference.strip():
            return _validation_error(
                request.correlation_id,
                "content_reference",
                "Content reference is required.",
            )
        if write.scope not in request.approved_scopes:
            return ErrorDetail(
                ErrorCode.AUTHORIZATION_DENIED,
                "Memory scope is not approved for this write.",
                request.correlation_id,
                fields=(ErrorField("scope", "not approved"),),
            )
        if write.impact is MemoryImpact.HIGH and not write.provenance:
            return _validation_error(
                request.correlation_id,
                "provenance",
                "High-impact memory requires provenance.",
            )
        return None

    def _audit_event(
        self,
        request: MemoryWriteRequest,
        operation: str,
        decision: AuditDecision,
        reason: str = "high-impact scoped-memory write",
    ) -> AuditEvent:
        timestamp = self._clock()
        writer = request.write.writer.strip()
        return AuditEvent(
            metadata=RecordMetadata(
                record_id=new_record_id(),
                organization_id=request.organization_id,
                correlation_id=request.correlation_id,
                schema_version=SCHEMA_VERSION,
                version=1,
                created_at=timestamp,
                updated_at=timestamp,
            ),
            audit_event_id=AuditEventId(str(uuid4())),
            actor_id=ActorId(writer or "unknown-writer"),
            operation=operation,
            decision=decision,
            reason=f"{reason}; path={request.path}",
            recorded_at=timestamp,
            evidence_references=request.write.provenance,
        )

    @staticmethod
    def _audit_unavailable(correlation_id: CorrelationId) -> Result[ScopedMemory, ErrorDetail]:
        return Result.failure(
            ErrorDetail(
                ErrorCode.AUDIT_UNAVAILABLE,
                "High-impact memory writes are blocked until audit health is restored.",
                correlation_id,
            )
        )

    @staticmethod
    def _repository_failure(correlation_id: CorrelationId) -> Result[ScopedMemory, ErrorDetail]:
        return Result.failure(
            ErrorDetail(
                ErrorCode.REPOSITORY_UNAVAILABLE,
                "Scoped-memory safety state is unavailable.",
                correlation_id,
            )
        )


def _validation_error(correlation_id: CorrelationId, name: str, message: str) -> ErrorDetail:
    """Build a redaction-safe validation denial for a memory write."""
    return ErrorDetail(
        ErrorCode.VALIDATION_FAILED,
        message,
        correlation_id,
        fields=(ErrorField(name, "required"),),
    )


def _required_value[T](result: Result[T, ErrorDetail]) -> T:
    """Extract a successful result while preserving strict optional typing."""
    if result.value is None:
        raise RuntimeError("Successful repository results must include a value.")
    return result.value