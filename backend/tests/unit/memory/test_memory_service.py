"""Focused examples for provenance-safe scoped-memory writes and audit recovery."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

import pytest

from app.audit import AuditWriter
from app.memory import (
    InMemoryMemoryRepository,
    MemoryImpact,
    MemoryScope,
    MemoryScopeType,
    MemoryService,
    MemoryWrite,
    MemoryWritePath,
    MemoryWriteRequest,
)
from app.models.audit import AuditDecision, AuditEvent
from app.models.contracts import ErrorCode, ErrorDetail, Result
from app.models.evidence import EvidenceReference
from app.models.identifiers import ActorId, CorrelationId, EvidenceId, OrganizationId

NOW = datetime(2025, 1, 1, tzinfo=UTC)
ORG_ID = OrganizationId("org-1")
CORRELATION_ID = CorrelationId("corr-memory")
SCOPE = MemoryScope(MemoryScopeType.WORKFLOW, "workflow-1")
PROVENANCE = EvidenceReference(EvidenceId("evidence-1"), "digest-1", "event-log")


@dataclass
class RecordingAuditRepository:
    """An append-only local audit sink that can deterministically be unavailable."""

    available: bool = True
    events: list[AuditEvent] = field(default_factory=list)

    def append(self, event: AuditEvent) -> Result[AuditEvent, ErrorDetail]:
        if not self.available:
            return Result.failure(
                ErrorDetail(ErrorCode.REPOSITORY_UNAVAILABLE, "audit unavailable", CORRELATION_ID)
            )
        self.events.append(event)
        return Result.success(event)


def _request(
    *,
    provenance: tuple[EvidenceReference, ...] = (PROVENANCE,),
    path: MemoryWritePath = MemoryWritePath.NORMAL,
    scope: MemoryScope = SCOPE,
) -> MemoryWriteRequest:
    """Build a high-impact write request with target-local evidence references."""
    return MemoryWriteRequest(
        write=MemoryWrite(
            scope=scope,
            impact=MemoryImpact.HIGH,
            writer=ActorId("ops.writer"),
            content_reference="memory-content-digest",
            provenance=provenance,
            source_log_set_id="log-set-1",
        ),
        organization_id=ORG_ID,
        correlation_id=CORRELATION_ID,
        approved_scopes=(SCOPE,),
        path=path,
    )


def _service(
    repository: InMemoryMemoryRepository,
    primary: RecordingAuditRepository,
    alternate: RecordingAuditRepository | None = None,
) -> MemoryService:
    return MemoryService(repository, AuditWriter(primary, alternate), clock=lambda: NOW)


def test_high_impact_write_retains_writer_provenance_and_exact_scope() -> None:
    """A permitted write is auditable and can only be inspected in its exact tenant scope."""
    repository = InMemoryMemoryRepository()
    primary = RecordingAuditRepository()

    stored = _service(repository, primary).store(_request())
    scoped = repository.records_for_scope(ORG_ID, SCOPE)
    foreign = repository.records_for_scope(OrganizationId("org-2"), SCOPE)

    assert stored.is_success
    assert stored.value is not None
    assert stored.value.writer == ActorId("ops.writer")
    assert stored.value.provenance == (PROVENANCE,)
    assert stored.value.source_log_set_id == "log-set-1"
    assert scoped.value == (stored.value,)
    assert foreign.value == ()
    assert [event.operation for event in primary.events] == ["memory.write"]


def test_high_impact_write_without_provenance_is_denied_and_audited() -> None:
    """Missing provenance never persists memory and produces a safe denial audit record."""
    repository = InMemoryMemoryRepository()
    primary = RecordingAuditRepository()

    result = _service(repository, primary).store(_request(provenance=()))

    assert not result.is_success
    assert result.error is not None
    assert result.error.code is ErrorCode.VALIDATION_FAILED
    assert [event.decision for event in primary.events] == [AuditDecision.DENIED]
    assert primary.events[0].operation == "memory.write.denied"
    assert not repository.records()


def test_alternate_audit_sink_permits_a_high_impact_write() -> None:
    """A primary outage uses the configured alternate sink and marks the audit record."""
    repository = InMemoryMemoryRepository()
    primary = RecordingAuditRepository(available=False)
    alternate = RecordingAuditRepository()

    result = _service(repository, primary, alternate).store(_request())

    latch = repository.get_audit_unavailable_latch()

    assert result.is_success
    assert not primary.events
    assert len(alternate.events) == 1
    assert alternate.events[0].alternate_sink_used
    assert latch.is_success
    assert latch.value is not None
    assert not latch.value.active


@pytest.mark.parametrize(
    "path",
    [MemoryWritePath.NORMAL, MemoryWritePath.CRITICAL, MemoryWritePath.RECOVERY],
)
def test_total_audit_outage_blocks_every_high_impact_write_path(path: MemoryWritePath) -> None:
    """Normal, critical, and recovery flows all remain blocked after the durable latch trips."""
    repository = InMemoryMemoryRepository()
    primary = RecordingAuditRepository(available=False)
    service = _service(repository, primary)

    result = service.store(_request(path=path))

    latch = repository.get_audit_unavailable_latch()

    assert not result.is_success
    assert result.error is not None
    assert result.error.code is ErrorCode.AUDIT_UNAVAILABLE
    assert latch.is_success
    assert latch.value is not None
    assert latch.value.active
    assert not repository.records()


def test_durable_latch_requires_a_successful_health_probe_before_recovery_write() -> None:
    """A new service remains blocked until primary or alternate audit health is confirmed."""
    repository = InMemoryMemoryRepository()
    primary = RecordingAuditRepository(available=False)
    first_service = _service(repository, primary)
    first = first_service.store(_request())

    recovered_service = _service(repository, primary)
    still_blocked = recovered_service.store(_request(path=MemoryWritePath.RECOVERY))
    primary.available = True
    recovered = recovered_service.store(_request(path=MemoryWritePath.RECOVERY))

    latch = repository.get_audit_unavailable_latch()

    assert not first.is_success
    assert not still_blocked.is_success
    assert still_blocked.error is not None
    assert still_blocked.error.code is ErrorCode.AUDIT_UNAVAILABLE
    assert recovered.is_success
    assert latch.is_success
    assert latch.value is not None
    assert not latch.value.active
    assert [event.operation for event in primary.events] == [
        "memory.audit_health_check",
        "memory.write",
    ]


def test_recovery_write_uses_an_alternate_audit_sink_after_a_total_outage() -> None:
    """A healthy alternate sink clears the durable latch and records recovery safely."""
    repository = InMemoryMemoryRepository()
    primary = RecordingAuditRepository(available=False)
    alternate = RecordingAuditRepository(available=False)
    service = _service(repository, primary, alternate)

    outage = service.store(_request())
    alternate.available = True
    recovered = service.store(_request(path=MemoryWritePath.RECOVERY))
    latch = repository.get_audit_unavailable_latch()

    assert not outage.is_success
    assert recovered.is_success
    assert latch.is_success and latch.value is not None
    assert not latch.value.active
    assert [event.operation for event in alternate.events] == [
        "memory.audit_health_check",
        "memory.write",
    ]
    assert all(event.alternate_sink_used for event in alternate.events)
