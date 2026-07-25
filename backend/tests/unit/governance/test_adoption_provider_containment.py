"""Focused provider authorization and fail-closed execution tests."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import cast

import pytest

from app.audit import AuditWriter
from app.governance.adapter_execution import (
    AuthorizedMockProviderRegistry,
    ProviderAdapterDeclaration,
    ProviderDenialReason,
)
from app.governance.operation_guard import OperationGuard
from app.governance.operational_containment import (
    CapacityAction,
    MandatoryVideoGate,
    OperationalContainmentService,
    PackOperationalStatus,
    VideoReleaseGates,
)
from app.models.audit import AuditEvent
from app.models.common import RecordMetadata
from app.models.contracts import ErrorCode, ErrorDetail, Result
from app.models.control_plane import ArtifactHandoff, ArtifactHandoffId, MaturityLevel, TaskId
from app.models.identifiers import (
    AgentId,
    CorrelationId,
    DomainPackId,
    OrganizationId,
    RecordId,
    RunId,
)
from tests.fakes.adoption import DeterministicAdoptionRepositories, FakeFailurePlan
from tests.fakes.broker import InMemoryAuditRepository
from tests.fakes.provider import MockProviderAdapter, ProviderFailureMode

_CORRELATION = CorrelationId("provider-test-correlation")
_ORGANIZATION = OrganizationId("organization-provider-containment")
_PACK = DomainPackId("pack-video")
_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_DECLARATION = ProviderAdapterDeclaration(
    provider_id="provider-adoption",
    capability="text.generate",
    cost_limit=2,
    retention_policy="reference_only",
    residency="test-local",
    safety_policy="deny-on-unsafe",
)


@dataclass
class UnavailableAuditRepository:
    """Audit storage fake that deterministically rejects every write."""

    events: list[AuditEvent] = field(default_factory=list)

    def append(self, event: AuditEvent) -> Result[AuditEvent, ErrorDetail]:
        """Return an unavailable result without retaining the event."""
        return Result.failure(
            ErrorDetail(
                ErrorCode.AUDIT_UNAVAILABLE,
                "audit unavailable",
                _CORRELATION,
            )
        )


@dataclass
class UnmarkedProvider:
    """A provider-shaped object that is not permitted in verification workflows."""

    provider_id: str = "unmarked-provider"
    capability: str = "text.generate"
    authorized: bool = True

    def invoke(
        self,
        capability: str,
        arguments: dict[str, object],
        *,
        correlation_id: object | None = None,
    ) -> object:
        """This method must never be reachable through the mock registry."""
        raise AssertionError("unmarked provider was exposed")


def _provider() -> MockProviderAdapter:
    return MockProviderAdapter("provider-adoption", "text.generate")


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


def _handoff(handoff_id: str) -> ArtifactHandoff:
    return ArtifactHandoff(
        metadata=_metadata(f"record-{handoff_id}"),
        handoff_id=ArtifactHandoffId(handoff_id),
        artifact_identity="video-artifact",
        artifact_version="1.0.0",
        parent_lineage=(),
        source_task_id=TaskId("source-task"),
        source_run_reference=str(RunId("source-run")),
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
        approval_reference="approval-1",
    )


def _containment_service(
    failure_plan: FakeFailurePlan | None = None,
) -> tuple[OperationalContainmentService, DeterministicAdoptionRepositories]:
    repositories = DeterministicAdoptionRepositories(failure_plan)
    return (
        OperationalContainmentService(
            repositories.release_decisions,
            repositories.maturity,
            repositories.audit,
            clock=lambda: _NOW,
        ),
        repositories,
    )


def test_complete_declaration_authorizes_and_executes_one_provider_action() -> None:
    """A complete pack declaration is required before the mock can run."""
    provider = _provider()
    audit_repository = InMemoryAuditRepository()
    result = OperationGuard(audit_writer=AuditWriter(audit_repository)).execute_provider(
        provider,
        _DECLARATION,
        {"input_reference": "reference:request"},
        correlation_id=_CORRELATION,
    )

    assert result.allowed
    assert result.invoked
    assert result.denial_reasons == ()
    assert provider.calls
    assert audit_repository.events == []


@pytest.mark.parametrize(
    ("field", "value", "reason"),
    [
        ("capability", None, ProviderDenialReason.MISSING_CAPABILITY_DECLARATION),
        ("cost_limit", None, ProviderDenialReason.MISSING_COST_DECLARATION),
        ("retention_policy", None, ProviderDenialReason.MISSING_RETENTION_DECLARATION),
        ("residency", None, ProviderDenialReason.MISSING_RESIDENCY_DECLARATION),
        ("safety_policy", None, ProviderDenialReason.MISSING_SAFETY_DECLARATION),
    ],
)
def test_missing_provider_declaration_field_denies_and_audits(
    field: str,
    value: object,
    reason: ProviderDenialReason,
) -> None:
    """Every required provider declaration category is independently mandatory."""
    declaration_values: dict[str, object] = {
        "provider_id": _DECLARATION.provider_id,
        "capability": _DECLARATION.capability,
        "cost_limit": _DECLARATION.cost_limit,
        "retention_policy": _DECLARATION.retention_policy,
        "residency": _DECLARATION.residency,
        "safety_policy": _DECLARATION.safety_policy,
    }
    declaration_values[field] = value
    declaration = ProviderAdapterDeclaration(
        provider_id=cast(str, declaration_values["provider_id"]),
        capability=cast(str | None, declaration_values["capability"]),
        cost_limit=cast(float | int | None, declaration_values["cost_limit"]),
        retention_policy=cast(str | None, declaration_values["retention_policy"]),
        residency=cast(str | None, declaration_values["residency"]),
        safety_policy=cast(str | None, declaration_values["safety_policy"]),
    )
    provider = _provider()
    audit_repository = InMemoryAuditRepository()

    result = OperationGuard(audit_writer=AuditWriter(audit_repository)).execute_provider(
        provider,
        declaration,
        {},
        correlation_id=_CORRELATION,
    )

    assert not result.allowed
    assert not result.invoked
    assert reason in result.denial_reasons
    assert not provider.calls
    assert len(audit_repository.events) == 1
    event = audit_repository.events[0]
    assert event.operation == "provider.authorize"
    assert event.decision.value == "denied"
    assert event.metadata.correlation_id == _CORRELATION
    assert reason.value in event.reason


def test_provider_denial_audit_contains_no_provider_request_content() -> None:
    """Provider denial audits retain decision references rather than request payloads."""
    provider = _provider()
    provider.set_failure_mode(ProviderFailureMode.UNSAFE_RESULT)
    audit_repository = InMemoryAuditRepository()
    secret_reference = "reference:request-only"

    result = OperationGuard(audit_writer=AuditWriter(audit_repository)).execute_provider(
        provider,
        _DECLARATION,
        {"secret": secret_reference},
        correlation_id=_CORRELATION,
    )

    assert not result.allowed
    assert result.audit_recorded is True
    assert len(audit_repository.events) == 1
    event = audit_repository.events[0]
    assert event.operation == "provider.execute"
    assert event.decision.value == "denied"
    assert event.metadata.correlation_id == _CORRELATION
    assert event.reason == "provider-adoption:text.generate:unsafe_provider_result"
    assert secret_reference not in event.reason


def test_provider_faults_deny_before_or_after_adapter_execution() -> None:
    """Timeout, unsafe, budget, and unavailable modes never become allowed results."""
    for failure_mode, reason in (
        (ProviderFailureMode.TIMEOUT, ProviderDenialReason.PROVIDER_TIMEOUT),
        (ProviderFailureMode.UNSAFE_RESULT, ProviderDenialReason.UNSAFE_PROVIDER_RESULT),
        (ProviderFailureMode.BUDGET_EXCEEDED, ProviderDenialReason.PROVIDER_BUDGET_EXCEEDED),
        (ProviderFailureMode.UNAVAILABLE, ProviderDenialReason.PROVIDER_UNAVAILABLE),
    ):
        provider = _provider()
        provider.set_failure_mode(failure_mode)
        result = OperationGuard().execute_provider(provider, _DECLARATION, {})

        assert not result.allowed
        assert not result.invoked
        assert result.denial_reasons == (reason,)
        assert not provider.calls

    provider = _provider()
    over_budget = OperationGuard().execute_provider(
        provider,
        _DECLARATION,
        {},
        requested_cost=3,
    )
    assert not over_budget.allowed
    assert over_budget.denial_reasons == (ProviderDenialReason.PROVIDER_BUDGET_EXCEEDED,)
    assert not provider.calls


def test_provider_denial_survives_audit_persistence_failure() -> None:
    """An unavailable audit sink cannot turn a provider denial into execution."""
    provider = _provider()
    provider.set_failure_mode(ProviderFailureMode.UNSAFE_RESULT)
    result = OperationGuard(
        audit_writer=AuditWriter(UnavailableAuditRepository())
    ).execute_provider(
        provider,
        _DECLARATION,
        {},
        correlation_id=_CORRELATION,
    )

    assert not result.allowed
    assert result.audit_recorded is False
    assert result.denial_reasons == (ProviderDenialReason.UNSAFE_PROVIDER_RESULT,)
    assert not provider.calls


def test_verification_registry_exposes_only_authorized_marked_mocks() -> None:
    """Verification workflows cannot resolve real-shaped or unauthorized adapters."""
    authorized = _provider()
    unauthorized = MockProviderAdapter("provider-denied", "text.generate", authorized=False)
    unmarked = UnmarkedProvider()
    registry = AuthorizedMockProviderRegistry(
        (authorized, unauthorized, unmarked),
        {
            "provider-adoption": _DECLARATION,
            "provider-denied": _DECLARATION,
            "unmarked-provider": _DECLARATION,
        },
    )

    assert registry.provider_ids == ("provider-adoption",)
    assert registry.get("provider-adoption") is authorized
    assert registry.get("provider-denied") is None
    assert registry.get("unmarked-provider") is None


def test_maturity_reporting_keeps_all_four_operational_values_distinct() -> None:
    """Cataloged, registered, active, and production-proven are separate values."""
    service, repositories = _containment_service()

    for index, level in enumerate(service.maturity_levels()):
        result = service.report_maturity(
            _ORGANIZATION,
            _PACK,
            "1.0.0",
            AgentId(f"agent-{index}"),
            level,
            (f"evidence:{level.value}",),
            correlation_id=_CORRELATION,
        )
        assert result.is_success and result.value is not None

    records = repositories.maturity.records()
    assert tuple(record.level for record in records) == service.maturity_levels()
    assert {record.level.value for record in records} == {
        "cataloged",
        "registered",
        "active",
        "production_proven",
    }


def test_capacity_throttle_and_disable_actions_are_audited() -> None:
    """Over-limit throttle and disable actions contain the pack and emit audits."""
    service, repositories = _containment_service()
    states = tuple(
        service.report_maturity(
            _ORGANIZATION,
            _PACK,
            "1.0.0",
            AgentId(f"agent-{index}"),
            level,
            (f"evidence:{index}",),
            correlation_id=_CORRELATION,
        ).value
        for index, level in enumerate((MaturityLevel.ACTIVE, MaturityLevel.PRODUCTION_PROVEN))
    )
    retained = tuple(state for state in states if state is not None)

    throttled = service.apply_capacity_action(
        _ORGANIZATION,
        _PACK,
        observed_load=11,
        approved_load_limit=10,
        action=CapacityAction.THROTTLE,
        immutable_version="1.0.0",
        maturity_states=retained,
        correlation_id=_CORRELATION,
    )
    assert throttled.is_success and throttled.value is not None
    assert throttled.value.operational_status is PackOperationalStatus.THROTTLED
    assert throttled.value.audit_recorded is True
    assert tuple(state.level for state in throttled.value.maturity_states) == tuple(
        state.level for state in retained
    )

    disabled = service.apply_capacity_action(
        _ORGANIZATION,
        _PACK,
        observed_load=11,
        approved_load_limit=10,
        action=CapacityAction.DISABLE,
        immutable_version="1.0.0",
        maturity_states=retained,
        correlation_id=_CORRELATION,
    )
    assert disabled.is_success and disabled.value is not None
    assert disabled.value.operational_status is PackOperationalStatus.DISABLED
    assert disabled.value.audit_recorded is True
    assert tuple(state.level for state in disabled.value.maturity_states) == tuple(
        state.level for state in retained
    )
    assert tuple(audit.action for audit in repositories.audit.records) == (
        "domain_pack.capacity_action",
        "domain_pack.capacity_action",
    )
    assert all(
        audit.metadata.correlation_id == _CORRELATION for audit in repositories.audit.records
    )


@pytest.mark.parametrize("missing_gate", tuple(MandatoryVideoGate))
def test_video_release_blocks_and_audits_each_missing_mandatory_gate(
    missing_gate: MandatoryVideoGate,
) -> None:
    """Rights, consent, continuity, media quality, channel, and approval each fail closed."""
    service, repositories = _containment_service()
    values: dict[str, object] = {
        "rights": True,
        "consent": True,
        "continuity": "continuous",
        "media_quality": "passed",
        "channel": ("internal",),
        "approval": "approval-1",
    }
    values[missing_gate.value] = None

    result = service.evaluate_video_release(
        _handoff(f"handoff-missing-{missing_gate.value}"),
        pack_id=_PACK,
        immutable_version="1.0.0",
        workflow_id="video.release",
        gates=VideoReleaseGates.from_mapping(values),
        correlation_id=_CORRELATION,
    )

    assert result.is_success and result.value is not None
    assert result.value.status.value == "blocked"
    assert result.value.unmet_gate_references == (missing_gate.value,)
    assert len(repositories.audit.records) == 1
    audit = repositories.audit.records[0]
    assert audit.action == "video.release.blocked"
    assert audit.outcome == "blocked"
    assert audit.reason is not None
    assert missing_gate.value in audit.reason
    assert audit.metadata.correlation_id == _CORRELATION


def test_capacity_containment_remains_applied_when_audit_write_fails() -> None:
    """Audit persistence failure cannot undo an already selected containment action."""
    failure_plan = FakeFailurePlan()
    service, _ = _containment_service(failure_plan)
    failure_plan.fail_next_audit()

    result = service.apply_capacity_action(
        _ORGANIZATION,
        _PACK,
        observed_load=12,
        approved_load_limit=10,
        action=CapacityAction.DISABLE,
        correlation_id=_CORRELATION,
    )

    assert result.is_success and result.value is not None
    assert result.value.applied
    assert result.value.operational_status is PackOperationalStatus.DISABLED
    assert result.value.audit_recorded is False
