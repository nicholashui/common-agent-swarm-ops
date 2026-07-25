"""Property checks for fail-closed mandatory video release gates."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from hypothesis import example, given, settings, strategies as st

from app.governance.operational_containment import (
    MandatoryVideoGate,
    OperationalContainmentService,
    VideoReleaseGates,
)
from app.models.common import SCHEMA_VERSION, RecordMetadata
from app.models.control_plane import (
    ArtifactHandoff,
    ArtifactHandoffId,
    ReleaseReadinessStatus,
    TaskId,
)
from app.models.identifiers import CorrelationId, DomainPackId, OrganizationId, RecordId, RunId
from tests.fakes.adoption import DeterministicAdoptionRepositories

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_ORGANIZATION = OrganizationId("organization-property-24")
_PACK = DomainPackId("pack-property-24")
_CORRELATION = CorrelationId("correlation-property-24")
_GATE_VALUES = ("approved", "passed", "verified")
_GATE_NAMES = tuple(MandatoryVideoGate)


@dataclass(frozen=True, slots=True)
class VideoReleaseGateCase:
    """Generated complete gate values and the one gate omitted for release."""

    case_id: int
    missing_gate: MandatoryVideoGate
    values: tuple[str, str, str, str, str, str]


@st.composite
def _video_release_gate_cases(draw: st.DrawFn) -> VideoReleaseGateCase:
    """Generate bounded gate sets with one independently omitted mandatory gate."""
    values = draw(
        st.tuples(
            st.sampled_from(_GATE_VALUES),
            st.sampled_from(_GATE_VALUES),
            st.sampled_from(_GATE_VALUES),
            st.sampled_from(_GATE_VALUES),
            st.sampled_from(_GATE_VALUES),
            st.sampled_from(_GATE_VALUES),
        )
    )
    return VideoReleaseGateCase(
        case_id=draw(st.integers(min_value=0, max_value=9_999)),
        missing_gate=draw(st.sampled_from(_GATE_NAMES)),
        values=values,
    )


def _metadata(record_id: str) -> RecordMetadata:
    """Build deterministic metadata for one generated local handoff."""
    return RecordMetadata(
        record_id=RecordId(record_id),
        organization_id=_ORGANIZATION,
        correlation_id=_CORRELATION,
        schema_version=SCHEMA_VERSION,
        version=1,
        created_at=_NOW,
        updated_at=_NOW,
    )


def _handoff(case: VideoReleaseGateCase) -> ArtifactHandoff:
    """Build a complete opaque Artifact_Handoff for the gate evaluation."""
    return ArtifactHandoff(
        metadata=_metadata(f"record-{case.case_id}"),
        handoff_id=ArtifactHandoffId(f"handoff-{case.case_id}"),
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
        approval_reference="approval-reference",
    )


def _gates(
    case: VideoReleaseGateCase, missing_gate: MandatoryVideoGate | None
) -> VideoReleaseGates:
    """Build a gate set while optionally omitting exactly one named gate."""
    values: dict[str, str | None] = dict(zip(_GATE_NAMES, case.values, strict=True))
    if missing_gate is not None:
        values[missing_gate.value] = None
    return VideoReleaseGates(
        rights=values[MandatoryVideoGate.RIGHTS.value],
        consent=values[MandatoryVideoGate.CONSENT.value],
        continuity=values[MandatoryVideoGate.CONTINUITY.value],
        media_quality=values[MandatoryVideoGate.MEDIA_QUALITY.value],
        channel=values[MandatoryVideoGate.CHANNEL.value],
        approval=values[MandatoryVideoGate.APPROVAL.value],
    )


# Feature: adoption-redesign, Property 24: Video releases fail closed on every mandatory gate
# **Validates: Requirements 9.3**
@settings(max_examples=100, deadline=None)
@example(
    case=VideoReleaseGateCase(
        case_id=0,
        missing_gate=MandatoryVideoGate.RIGHTS,
        values=("approved", "passed", "verified", "approved", "passed", "verified"),
    )
)
@example(
    case=VideoReleaseGateCase(
        case_id=1,
        missing_gate=MandatoryVideoGate.APPROVAL,
        values=("verified", "approved", "passed", "verified", "approved", "passed"),
    )
)
@given(case=_video_release_gate_cases())
def test_property_24_video_releases_fail_closed_on_every_mandatory_gate(
    case: VideoReleaseGateCase,
) -> None:
    """Omitting any mandatory video gate blocks release."""
    repositories = DeterministicAdoptionRepositories()
    service = OperationalContainmentService(
        repositories.release_decisions,
        repositories.maturity,
        repositories.audit,
        clock=lambda: _NOW,
    )
    handoff = _handoff(case)
    complete = service.evaluate_video_release(
        handoff,
        pack_id=_PACK,
        immutable_version="1.0.0",
        workflow_id=f"video.release.complete.{case.case_id}",
        gates=_gates(case, None),
    )
    assert complete.is_success and complete.value is not None
    assert complete.value.status is ReleaseReadinessStatus.ELIGIBLE
    assert complete.value.unmet_gate_references == ()

    blocked = service.evaluate_video_release(
        handoff,
        pack_id=_PACK,
        immutable_version="1.0.0",
        workflow_id=f"video.release.missing.{case.missing_gate.value}.{case.case_id}",
        gates=_gates(case, case.missing_gate),
    )

    assert blocked.is_success and blocked.value is not None
    assert blocked.value.status is ReleaseReadinessStatus.BLOCKED
    assert not blocked.value.integration_coverage_complete
    assert case.missing_gate.value in blocked.value.unmet_gate_references
    assert blocked.value in repositories.release_decisions.records()
    assert repositories.audit.records[-1].action == "video.release.blocked"
