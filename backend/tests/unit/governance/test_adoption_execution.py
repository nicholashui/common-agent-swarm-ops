"""Deterministic governance and Artifact_Handoff resilience tests."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime

from app.artifacts.handoff_service import ArtifactHandoffService
from app.audit import AuditWriter
from app.governance.authorization import (
    ApprovalState,
    AuthorizationContext,
    DataAccessRequest,
    OutboundRequest,
    ScopeConstraint,
    ToolInputValue,
)
from app.governance.tool_broker import (
    BrokerDenialReason,
    HostToolBroker,
    LocalAdapterResult,
    ToolRequest,
)
from app.models.audit import AuditDecision, AuditEvent
from app.models.common import CompatibilityRange, RecordMetadata
from app.models.contracts import ErrorCode, ErrorDetail, Result
from app.models.control_plane import (
    ArtifactAvailabilityStatus,
    ArtifactHandoff,
    ArtifactHandoffId,
    InvocationAssociation,
    TaskId,
)
from app.models.identifiers import (
    AgentId,
    CorrelationId,
    DomainId,
    InvocationId,
    OrganizationId,
    RecordId,
    RunId,
)
from app.repositories.artifact_repository import InMemoryArtifactRepository
from app.repositories.run_repository import InMemoryRunRepository
from app.runs.service import RunService
from app.workflows.validator import RegisteredReferences
from tests.fakes.adoption import (
    DeterministicAuditRepository,
    DeterministicInvocationAssociationRepository,
    FakeFailurePlan,
)

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_ORGANIZATION = OrganizationId("execution-organization")
_CORRELATION = CorrelationId("execution-correlation")


@dataclass
class _AuditEventRepository:
    """Deterministic AuditEvent sink for HostToolBroker governance assertions."""

    available: bool = True
    events: list[AuditEvent] = field(default_factory=list)

    def append(self, event: AuditEvent) -> Result[AuditEvent, ErrorDetail]:
        if not self.available:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.AUDIT_UNAVAILABLE,
                    "Audit event persistence is unavailable.",
                    event.metadata.correlation_id,
                )
            )
        self.events.append(event)
        return Result.success(event)


@dataclass
class _LocalAdapter:
    """A deterministic local adapter that records whether dispatch was attempted."""

    adapter_id: str = "crm.lookup"
    version: str = "1.0.0"
    local_only: bool = True
    invocations: list[Mapping[str, ToolInputValue]] = field(default_factory=list)

    def execute(self, arguments: Mapping[str, ToolInputValue]) -> LocalAdapterResult:
        self.invocations.append(arguments)
        return LocalAdapterResult("completed", "effect-digest", reversible=True)


def _metadata(record_id: str) -> RecordMetadata:
    return RecordMetadata(
        record_id=RecordId(record_id),
        organization_id=_ORGANIZATION,
        correlation_id=_CORRELATION,
        schema_version=1,
        version=1,
        created_at=_NOW,
        updated_at=_NOW,
    )


def _context(*, declared_tool_ids: frozenset[str] | None = None) -> AuthorizationContext:
    tools = frozenset({"crm.lookup"})
    return AuthorizationContext(
        agent_id="agent-execution",
        step_id="step-execution",
        organization_id=str(_ORGANIZATION),
        actor_id="actor-execution",
        correlation_id=str(_CORRELATION),
        agent_allowed_tools=tools,
        step_declared_tools=tools,
        role_allowed_tools=tools,
        organization_allowed_tools=tools,
        risk_allowed_tools=tools,
        approval_state=ApprovalState.NOT_REQUIRED,
        domain_id="domain-execution",
        pack_version="1.0.0",
        supported_pack_range=CompatibilityRange.exact("1.0.0"),
        declared_memory_scopes=frozenset({"memory:agent-execution"}),
        declared_outbound_destinations=frozenset({"https://api.example.test"}),
        declared_tool_ids=declared_tool_ids if declared_tool_ids is not None else tools,
    )


def _data_access(*, memory_scope: str = "memory:agent-execution") -> DataAccessRequest:
    return DataAccessRequest(
        organization_id=str(_ORGANIZATION),
        domain_id="domain-execution",
        pack_version="1.0.0",
        agent_id="agent-execution",
        memory_scope=memory_scope,
    )


def _handoff(handoff_id: str, parents: tuple[str, ...] = ()) -> ArtifactHandoff:
    return ArtifactHandoff(
        metadata=_metadata(f"record-{handoff_id}"),
        handoff_id=ArtifactHandoffId(handoff_id),
        artifact_identity="artifact-execution",
        artifact_version="1.0.0",
        parent_lineage=parents,
        source_task_id=TaskId("source-task"),
        source_run_reference="source-run",
        brief_scope="brief-reference",
        technical_specification={"schema_version": "1"},
        rights_and_consent_state="approved",
        continuity_state="continuous",
        quality_control_state="passed",
        target_channels=("internal",),
        provenance_reference="provenance-reference",
        owner_reference="owner-reference",
        classification="internal",
        integrity_reference="sha256:artifact",
        approval_reference="approval-reference",
    )


def _association() -> InvocationAssociation:
    return InvocationAssociation(
        metadata=_metadata("invocation-record"),
        invocation_id=InvocationId("invocation-execution"),
        organization_id=_ORGANIZATION,
        domain_id=DomainId("domain-execution"),
        pack_version="1.0.0",
        agent_id=AgentId("agent-execution"),
        workflow_id="workflow-execution",
        run_id=RunId("run-execution"),
        correlation_id=_CORRELATION,
    )


def test_association_denial_audit_record_retains_complete_shape() -> None:
    """Association persistence failure denies before start and records its correlation."""
    failure_plan = FakeFailurePlan()
    failure_plan.fail_next_persistence("invocation.append")
    association_repository = DeterministicInvocationAssociationRepository(failure_plan)
    audit_repository = DeterministicAuditRepository(failure_plan)
    service = RunService(
        InMemoryRunRepository(),
        RegisteredReferences(
            agent_ids=frozenset(),
            tool_ids=frozenset(),
            memory_scope_ids=frozenset(),
            risk_gate_ids=frozenset(),
            rollback_plan_ids=frozenset(),
            authorization_ids=frozenset(),
        ),
        clock=lambda: _NOW,
        invocation_association_repository=association_repository,
        audit_repository=audit_repository,
    )
    starts: list[InvocationAssociation] = []

    result = service.begin_invocation(_association(), starts.append)

    assert not result.is_success
    assert result.error is not None
    assert result.error.code is ErrorCode.AUTHORIZATION_DENIED
    assert starts == []
    assert association_repository.records() == ()
    assert len(audit_repository.records) == 1
    audit = audit_repository.records[0]
    assert audit.action == "invocation.association.denied"
    assert audit.subject_reference == "invocation-execution"
    assert audit.outcome == "denied:association_persistence_failed"
    assert audit.metadata.organization_id == _ORGANIZATION
    assert audit.metadata.correlation_id == _CORRELATION


def test_data_denial_audit_event_has_scope_reason_and_correlation() -> None:
    """A cross-memory request is denied and its AuditEvent identifies the failed scope."""
    adapter = _LocalAdapter()
    audit_repository = _AuditEventRepository()
    broker = HostToolBroker((adapter,), AuditWriter(audit_repository))

    result = broker.request_tool(
        ToolRequest(
            "crm.lookup",
            {"account_id": "account-1"},
            data_access=_data_access(memory_scope="memory:other"),
        ),
        _context(),
    )

    assert not result.allowed
    assert result.denial_audit_recorded is True
    assert ScopeConstraint.MEMORY_SCOPE in result.authorization.denied_constraints
    assert not adapter.invocations
    assert len(audit_repository.events) == 1
    event = audit_repository.events[0]
    assert event.operation == "tool.request"
    assert event.decision is AuditDecision.DENIED
    assert "memory_scope" in event.reason
    assert event.metadata.organization_id == _ORGANIZATION
    assert event.metadata.correlation_id == _CORRELATION


def test_denial_remains_effective_when_allowed_data_audit_write_fails() -> None:
    """The explicitly tolerated data-denial audit outage cannot permit adapter dispatch."""
    adapter = _LocalAdapter()
    audit_repository = _AuditEventRepository(available=False)
    broker = HostToolBroker((adapter,), AuditWriter(audit_repository))

    result = broker.request_tool(
        ToolRequest(
            "crm.lookup",
            {"account_id": "account-1"},
            data_access=_data_access(memory_scope="memory:other"),
        ),
        _context(),
    )

    assert not result.allowed
    assert result.denial_audit_recorded is False
    assert not adapter.invocations
    assert audit_repository.events == []


def test_undeclared_tool_denial_is_audited_without_dispatch() -> None:
    """A tool absent from the declared step allow-list cannot reach a registered adapter."""
    adapter = _LocalAdapter()
    audit_repository = _AuditEventRepository()
    broker = HostToolBroker((adapter,), AuditWriter(audit_repository))

    result = broker.request_tool(
        ToolRequest("crm.lookup", {"account_id": "account-1"}),
        _context(declared_tool_ids=frozenset()),
    )

    assert not result.allowed
    assert not result.invoked
    assert BrokerDenialReason.LOCAL_ADAPTER_NOT_ALLOWLISTED not in result.denial_reasons
    assert not adapter.invocations
    assert len(audit_repository.events) == 1
    event = audit_repository.events[0]
    assert event.operation == "tool.request"
    assert event.decision is AuditDecision.DENIED
    assert "step_declared_tools" in event.reason


def test_undeclared_outbound_denial_is_audited_before_dispatch() -> None:
    """An undeclared outbound destination is denied with a stable audited operation."""
    audit_repository = _AuditEventRepository()
    broker = HostToolBroker((), AuditWriter(audit_repository))

    result = broker.request_outbound(
        OutboundRequest("https://unapproved.example.test"),
        _context(),
    )

    assert not result.permitted
    assert result.denied_constraints == (ScopeConstraint.OUTBOUND_DESTINATION,)
    assert len(audit_repository.events) == 1
    event = audit_repository.events[0]
    assert event.operation == "outbound.request"
    assert event.decision is AuditDecision.DENIED
    assert event.reason == "outbound_destination,undeclared_outbound_destination"
    assert event.metadata.correlation_id == _CORRELATION


def test_invalid_va_extension_is_blocked_and_audited_before_handoff_persistence() -> None:
    """A VA metadata extension must pass its registered schema before acceptance."""
    repository = InMemoryArtifactRepository()
    audit_repository = DeterministicAuditRepository()
    service = ArtifactHandoffService(
        repository,
        audit_repository,
        va_extension_schema={"schema_version": str},
        clock=lambda: _NOW,
    )

    result = service.create_internal(
        _ORGANIZATION,
        replace(_handoff("va-invalid"), technical_specification={"schema_version": 1}),
    )

    assert not result.is_success
    assert result.error is not None
    assert result.error.code is ErrorCode.VALIDATION_FAILED
    assert tuple(field.name for field in result.error.fields) == ("schema_version",)
    assert repository.handoffs_for_organization(_ORGANIZATION) == ()
    assert len(audit_repository.records) == 1
    audit = audit_repository.records[0]
    assert audit.action == "artifact_handoff.va_extension.blocked"
    assert audit.subject_reference == "artifact_handoff:va-invalid"
    assert audit.outcome == "blocked"
    assert audit.metadata.correlation_id == _CORRELATION


def test_external_handoff_premature_availability_is_revoked_and_audited() -> None:
    """Prematurely exposed external metadata is revoked and excluded downstream."""
    repository = InMemoryArtifactRepository()
    audit_repository = DeterministicAuditRepository()
    service = ArtifactHandoffService(repository, audit_repository, clock=lambda: _NOW)
    pending = replace(_handoff("premature"), external=True)
    assert repository.append(pending).is_success

    result = service.revoke_premature_availability(_ORGANIZATION, pending.handoff_id, _CORRELATION)

    assert result.is_success and result.value is not None
    assert result.value.availability is ArtifactAvailabilityStatus.REVOKED
    available = repository.available_for_downstream(_ORGANIZATION)
    assert available.is_success and available.value == ()
    assert len(audit_repository.records) == 1
    audit = audit_repository.records[0]
    assert audit.action == "artifact_handoff.availability.revoked"
    assert audit.subject_reference == "artifact_handoff:premature"
    assert audit.outcome == "revoked"
    assert audit.metadata.correlation_id == _CORRELATION


def test_cyclic_handoff_lineage_is_rejected_without_persisting_candidate() -> None:
    """A candidate that closes a retained lineage cycle cannot be stored or exposed."""
    repository = InMemoryArtifactRepository()
    service = ArtifactHandoffService(repository, clock=lambda: _NOW)
    parent = _handoff("parent", ("child",))
    child = _handoff("child", ("parent",))

    assert service.create_internal(_ORGANIZATION, parent).is_success
    result = service.create_internal(_ORGANIZATION, child)

    assert not result.is_success
    assert result.error is not None
    assert result.error.code is ErrorCode.CONFLICT
    retained = repository.handoffs_for_organization(_ORGANIZATION)
    assert tuple(str(record.handoff_id) for record in retained) == ("parent",)
    available = repository.available_for_downstream(_ORGANIZATION)
    assert available.is_success
    assert available.value is not None
    assert tuple(str(record.handoff_id) for record in available.value) == ("parent",)
