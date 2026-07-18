"""Property tests for provenance-safe, auditable scoped-memory writes."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from hypothesis import example, given, settings, strategies as st

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

# Feature: generic-swarm-business-os, Property 6: High-impact memory is provenance-, scope-,
# and audit-safe.
# **Validates: Requirements 3.2, 3.3, 3.5**

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_ORGANIZATION_ID = OrganizationId("org-property-6")
_FOREIGN_ORGANIZATION_ID = OrganizationId("org-property-6-foreign")
_CORRELATION_ID = CorrelationId("corr-property-6")
_SCOPE = MemoryScope(MemoryScopeType.WORKFLOW, "workflow-property-6")
_FOREIGN_SCOPE = MemoryScope(MemoryScopeType.AGENT, "agent-property-6")
_PROVENANCE = EvidenceReference(
    evidence_id=EvidenceId("evidence-property-6"),
    digest="digest-property-6",
    kind="permitted-event-log",
)


@dataclass(frozen=True, slots=True)
class HighImpactWriteCase:
    """A bounded input matrix for provenance, scope, audit, and execution path controls."""

    writer_present: bool
    provenance_present: bool
    scope_approved: bool
    primary_available: bool
    alternate_available: bool
    path: MemoryWritePath


@dataclass
class RecordingAuditSink:
    """Deterministic append-only audit fake that may be locally unavailable."""

    available: bool
    events: list[AuditEvent] = field(default_factory=list)

    def append(self, event: AuditEvent) -> Result[AuditEvent, ErrorDetail]:
        """Retain events only while this deterministic local sink is available."""
        if not self.available:
            return Result.failure(
                ErrorDetail(ErrorCode.REPOSITORY_UNAVAILABLE, "audit unavailable", _CORRELATION_ID)
            )
        self.events.append(event)
        return Result.success(event)


@st.composite
def _high_impact_write_cases(draw: st.DrawFn) -> HighImpactWriteCase:
    """Generate all bounded input dimensions relevant to Property 6."""
    return HighImpactWriteCase(
        writer_present=draw(st.booleans()),
        provenance_present=draw(st.booleans()),
        scope_approved=draw(st.booleans()),
        primary_available=draw(st.booleans()),
        alternate_available=draw(st.booleans()),
        path=draw(st.sampled_from(tuple(MemoryWritePath))),
    )


def _request(
    case: HighImpactWriteCase,
    *,
    force_valid: bool = False,
    path: MemoryWritePath | None = None,
) -> MemoryWriteRequest:
    """Build one high-impact write request without external services or mutable data."""
    writer = "ops.writer" if force_valid or case.writer_present else ""
    provenance = (_PROVENANCE,) if force_valid or case.provenance_present else ()
    approved_scopes = (_SCOPE,) if force_valid or case.scope_approved else ()
    return MemoryWriteRequest(
        write=MemoryWrite(
            scope=_SCOPE,
            impact=MemoryImpact.HIGH,
            writer=ActorId(writer),
            content_reference="content-digest-property-6",
            provenance=provenance,
            source_log_set_id="permitted-log-set-property-6",
        ),
        organization_id=_ORGANIZATION_ID,
        correlation_id=_CORRELATION_ID,
        approved_scopes=approved_scopes,
        path=path or case.path,
    )


def _assert_recovery_latch(
    service: MemoryService,
    repository: InMemoryMemoryRepository,
    primary: RecordingAuditSink,
    case: HighImpactWriteCase,
) -> None:
    """Assert the durable latch blocks all paths until a successful audit health probe."""
    latched = repository.get_audit_unavailable_latch()
    assert latched.is_success and latched.value is not None and latched.value.active

    for path in MemoryWritePath:
        blocked = service.store(_request(case, force_valid=True, path=path))
        assert not blocked.is_success
        assert blocked.error is not None
        assert blocked.error.code is ErrorCode.AUDIT_UNAVAILABLE

    primary.available = True
    recovered = service.store(_request(case, force_valid=True, path=MemoryWritePath.RECOVERY))
    restored_latch = repository.get_audit_unavailable_latch()

    assert recovered.is_success
    assert restored_latch.is_success
    assert restored_latch.value is not None
    assert not restored_latch.value.active


@settings(max_examples=100, deadline=None, derandomize=True)
@example(
    case=HighImpactWriteCase(True, True, True, True, False, MemoryWritePath.NORMAL)
)
@example(
    case=HighImpactWriteCase(True, True, True, False, True, MemoryWritePath.CRITICAL)
)
@example(
    case=HighImpactWriteCase(True, False, True, True, True, MemoryWritePath.RECOVERY)
)
@example(
    case=HighImpactWriteCase(True, True, True, False, False, MemoryWritePath.NORMAL)
)
@given(case=_high_impact_write_cases())
def test_high_impact_memory_writes_are_provenance_scope_and_audit_safe(
    case: HighImpactWriteCase,
) -> None:
    """High-impact storage succeeds exactly when all safety controls permit it."""
    repository = InMemoryMemoryRepository()
    primary = RecordingAuditSink(case.primary_available)
    alternate = RecordingAuditSink(case.alternate_available)
    service = MemoryService(repository, AuditWriter(primary, alternate), clock=lambda: _NOW)

    result = service.store(_request(case))
    auditable = case.primary_available or case.alternate_available
    valid = case.writer_present and case.provenance_present and case.scope_approved

    assert result.is_success is (valid and auditable)
    if result.is_success:
        assert result.value is not None
        stored = result.value
        exact_scope = repository.records_for_scope(_ORGANIZATION_ID, _SCOPE)
        foreign_scope = repository.records_for_scope(_ORGANIZATION_ID, _FOREIGN_SCOPE)
        foreign_organization = repository.records_for_scope(_FOREIGN_ORGANIZATION_ID, _SCOPE)

        assert stored.writer == ActorId("ops.writer")
        assert stored.provenance == (_PROVENANCE,)
        assert exact_scope.value == (stored,)
        assert foreign_scope.value == ()
        assert foreign_organization.value == ()
        recorded_events = primary.events if case.primary_available else alternate.events
        assert len(recorded_events) == 1
        assert recorded_events[0].operation == "memory.write"
        assert recorded_events[0].alternate_sink_used is (not case.primary_available)
    else:
        assert not repository.records()

    if not case.provenance_present and auditable:
        denial_events = primary.events if case.primary_available else alternate.events
        assert len(denial_events) == 1
        assert denial_events[0].operation == "memory.write.denied"
        assert denial_events[0].decision is AuditDecision.DENIED

    if not auditable:
        _assert_recovery_latch(service, repository, primary, case)
