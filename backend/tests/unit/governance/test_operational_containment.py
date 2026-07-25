"""Deterministic video release, maturity, and capacity containment tests."""

from __future__ import annotations

from datetime import UTC, datetime

from app.governance.operational_containment import (
    CapacityAction,
    MandatoryVideoGate,
    OperationalContainmentService,
    PackOperationalStatus,
    VideoReleaseGates,
)
from app.models.common import RecordMetadata
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

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_ORGANIZATION = OrganizationId("organization-containment")
_PACK = DomainPackId("pack-video")
_CORRELATION = CorrelationId("correlation-containment")


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


def _handoff(
    handoff_id: str,
    *,
    rights_and_consent: str | None = "approved",
    continuity: str | None = "continuous",
    quality: str | None = "passed",
    channels: tuple[str, ...] = ("internal",),
    approval: str | None = "approval-1",
) -> ArtifactHandoff:
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
        rights_and_consent_state=rights_and_consent,
        continuity_state=continuity,
        quality_control_state=quality,
        target_channels=channels,
        provenance_reference="provenance-reference",
        owner_reference="owner-reference",
        classification="internal",
        integrity_reference="sha256:artifact",
        approval_reference=approval,
    )


def _service(
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


def test_video_release_blocks_each_missing_mandatory_handoff_gate_and_audits() -> None:
    """A missing gate produces one blocked terminal decision and an audit record."""
    service, repositories = _service()
    result = service.evaluate_video_release(
        _handoff(
            "handoff-blocked",
            rights_and_consent=None,
            continuity=None,
            quality=None,
            channels=(),
            approval=None,
        ),
        pack_id=_PACK,
        immutable_version="1.0.0",
        workflow_id="video.release",
    )

    assert result.is_success and result.value is not None
    assert result.value.status.value == "blocked"
    assert result.value.unmet_gate_references == (
        MandatoryVideoGate.RIGHTS.value,
        MandatoryVideoGate.CONSENT.value,
        MandatoryVideoGate.CONTINUITY.value,
        MandatoryVideoGate.MEDIA_QUALITY.value,
        MandatoryVideoGate.CHANNEL.value,
        MandatoryVideoGate.APPROVAL.value,
    )
    assert repositories.release_decisions.records() == (result.value,)
    assert len(repositories.audit.records) == 1
    assert repositories.audit.records[0].action == "video.release.blocked"
    assert repositories.audit.records[0].metadata.correlation_id == _CORRELATION


def test_video_release_is_eligible_only_when_all_six_gates_pass() -> None:
    """Complete rights, consent, continuity, quality, channel, and approval evidence passes."""
    service, repositories = _service()
    result = service.evaluate_video_release(
        _handoff("handoff-ready"),
        pack_id=_PACK,
        immutable_version="1.0.0",
        workflow_id="video.release",
        gates=VideoReleaseGates(
            rights=True,
            consent=True,
            continuity="continuous",
            media_quality="passed",
            channel=("internal",),
            approval="approval-1",
        ),
    )

    assert result.is_success and result.value is not None
    assert result.value.status.value == "eligible"
    assert result.value.unmet_gate_references == ()
    assert repositories.audit.records == ()


def test_maturity_reporting_exposes_four_distinct_states() -> None:
    """Cataloged, registered, active, and production-proven remain distinct values."""
    service, repositories = _service()

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
    assert len({record.level.value for record in records}) == 4


def test_capacity_action_applies_declared_action_and_preserves_maturity_on_disable() -> None:
    """Throttle and disable are explicit, audited actions independent of agent maturity."""
    service, repositories = _service()
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
    assert all(state is not None for state in states)
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

    disabled = service.disable_pack_for_provider_failure(
        _ORGANIZATION,
        _PACK,
        immutable_version="1.0.0",
        correlation_id=_CORRELATION,
    )
    assert disabled.is_success and disabled.value is not None
    assert disabled.value.operational_status is PackOperationalStatus.DISABLED
    assert disabled.value.audit_recorded is True
    assert tuple(state.level for state in disabled.value.maturity_states) == tuple(
        state.level for state in retained
    )
    assert all(not state.pack_operational for state in disabled.value.maturity_states)
    persisted = repositories.maturity.records()
    assert tuple(state.level for state in persisted) == tuple(state.level for state in retained)
    assert all(not state.pack_operational for state in persisted)
    assert tuple(audit.action for audit in repositories.audit.records) == (
        "domain_pack.capacity_action",
        "domain_pack.capacity_action",
    )


def test_capacity_action_remains_applied_when_audit_persistence_fails() -> None:
    """An audit outage cannot undo fail-closed containment."""
    failure_plan = FakeFailurePlan()
    service, _ = _service(failure_plan)
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
