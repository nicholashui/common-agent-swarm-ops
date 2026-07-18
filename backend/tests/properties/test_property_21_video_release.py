"""Property tests for complete fail-closed Video_Pack release decisions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from hypothesis import example, given, settings, strategies as st

from app.models.common import SCHEMA_VERSION, RecordMetadata
from app.models.identifiers import CorrelationId, OrganizationId, RecordId
from app.repositories.artifact_repository import InMemoryArtifactRepository
from app.video.artifacts import (
    NamedReleaseCheck,
    ReleaseDecision,
    VideoArtifactId,
    VideoArtifactVersion,
    VideoArtifactVersionId,
)
from app.video.release import ReleaseService, VideoBlockerProvider

# Feature: generic-swarm-business-os, Property 21: Video release is a complete fail-closed
# gate.
# **Validates: Requirements 9.4, 9.5**

_ORGANIZATION_ID = OrganizationId("org-property-21")
_CORRELATION_ID = CorrelationId("property-21")
_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_TARGET_VERSION_ID = VideoArtifactVersionId("property-21-target")
_PARENT_VERSION_ID = VideoArtifactVersionId("property-21-parent")
_UNKNOWN_VERSION_ID = VideoArtifactVersionId("property-21-unknown")


@dataclass(frozen=True, slots=True)
class VideoReleaseCase:
    """One bounded lineage and complete release-gate combination."""

    lineage: str
    rights_and_consent_passed: bool
    provenance_passed: bool
    signoff_passed: bool
    quality_state: str
    release_state: str
    has_unresolved_blocker: bool


class StaticBlockers(VideoBlockerProvider):
    """Return a bounded local blocker set without accessing an external system."""

    def __init__(self, has_unresolved_blocker: bool) -> None:
        self._blockers = ("compliance-property-21",) if has_unresolved_blocker else ()

    def unresolved_for(
        self, organization_id: OrganizationId, artifact_version_id: VideoArtifactVersionId
    ) -> tuple[str, ...]:
        """Return only the configured deterministic unresolved blocker identifiers."""
        del organization_id, artifact_version_id
        return self._blockers


def _metadata(record_id: str) -> RecordMetadata:
    """Build a stable local record envelope for one immutable artifact version."""
    return RecordMetadata(
        RecordId(record_id),
        _ORGANIZATION_ID,
        _CORRELATION_ID,
        SCHEMA_VERSION,
        1,
        _NOW,
        _NOW,
    )


def _checks(kind: str, state: str) -> tuple[NamedReleaseCheck, ...]:
    """Build a bounded named-check set, including explicit missing and failed states."""
    if state == "missing":
        return ()
    return (NamedReleaseCheck(f"{kind}-check", state == "passed", f"{kind}-evidence"),)


def _version(
    version_id: VideoArtifactVersionId,
    parent_version_ids: tuple[VideoArtifactVersionId, ...],
    case: VideoReleaseCase,
) -> VideoArtifactVersion:
    """Build an immutable version with each requested release-gate outcome."""
    return VideoArtifactVersion(
        _metadata(f"record-{version_id}"),
        VideoArtifactId("property-21-video"),
        version_id,
        parent_version_ids,
        case.rights_and_consent_passed,
        case.provenance_passed and case.signoff_passed,
        _checks("quality", case.quality_state),
        _checks("release", case.release_state),
    )


def _persist_case_version(
    repository: InMemoryArtifactRepository, case: VideoReleaseCase
) -> VideoArtifactVersionId:
    """Persist a real local DAG, cycle, ambiguous graph, or unknown-version request target."""
    if case.lineage == "unknown_artifact":
        return _UNKNOWN_VERSION_ID
    records: tuple[VideoArtifactVersion, ...]
    if case.lineage == "valid":
        parent = _version(_PARENT_VERSION_ID, (), case)
        target = _version(_TARGET_VERSION_ID, (_PARENT_VERSION_ID,), case)
        records = (parent, target)
    elif case.lineage == "cyclic":
        parent = _version(_PARENT_VERSION_ID, (_TARGET_VERSION_ID,), case)
        target = _version(_TARGET_VERSION_ID, (_PARENT_VERSION_ID,), case)
        records = (parent, target)
    elif case.lineage == "ambiguous":
        target = _version(_TARGET_VERSION_ID, (_PARENT_VERSION_ID, _PARENT_VERSION_ID), case)
        parent = _version(_PARENT_VERSION_ID, (), case)
        records = (parent, target)
    else:
        target = _version(_TARGET_VERSION_ID, (_UNKNOWN_VERSION_ID,), case)
        records = (target,)
    for record in records:
        assert repository.create_version(record).is_success
    return _TARGET_VERSION_ID


def _expected_conditions(case: VideoReleaseCase) -> dict[str, bool]:
    """Calculate every named condition independently of the service under test."""
    blockers_clear = not case.has_unresolved_blocker
    if case.lineage == "unknown_artifact":
        return {
            "artifact_version_known": False,
            "immutable_acyclic_known_lineage": False,
            "rights_and_consent": False,
            "provenance_and_signoff": False,
            "named_quality_checks_present": False,
            "named_release_checks_present": False,
            "no_unresolved_blockers": blockers_clear,
        }
    quality_present = case.quality_state != "missing"
    release_present = case.release_state != "missing"
    conditions = {
        "artifact_version_known": True,
        "immutable_acyclic_known_lineage": case.lineage == "valid",
        "rights_and_consent": case.rights_and_consent_passed,
        "provenance_and_signoff": case.provenance_passed and case.signoff_passed,
        "named_quality_checks_present": quality_present,
        "named_release_checks_present": release_present,
    }
    if quality_present:
        conditions["quality:quality-check"] = case.quality_state == "passed"
    if release_present:
        conditions["release:release-check"] = case.release_state == "passed"
    conditions["no_unresolved_blockers"] = blockers_clear
    return conditions


_RELEASE_CASES = st.builds(
    VideoReleaseCase,
    lineage=st.sampled_from(("valid", "cyclic", "ambiguous", "unknown_parent", "unknown_artifact")),
    rights_and_consent_passed=st.booleans(),
    provenance_passed=st.booleans(),
    signoff_passed=st.booleans(),
    quality_state=st.sampled_from(("missing", "failed", "passed")),
    release_state=st.sampled_from(("missing", "failed", "passed")),
    has_unresolved_blocker=st.booleans(),
)


@settings(max_examples=100, deadline=None)
@example(VideoReleaseCase("valid", True, True, True, "passed", "passed", False))
@example(VideoReleaseCase("cyclic", True, True, True, "passed", "passed", False))
@example(VideoReleaseCase("unknown_parent", True, True, True, "passed", "passed", False))
@example(VideoReleaseCase("unknown_artifact", True, True, True, "passed", "passed", True))
@example(VideoReleaseCase("valid", False, False, False, "failed", "failed", True))
@given(case=_RELEASE_CASES)
def test_video_release_is_a_complete_fail_closed_gate(case: VideoReleaseCase) -> None:
    """Only a complete known acyclic gate set permits a retained local decision.

    **Validates: Requirements 9.4, 9.5**
    """
    repository = InMemoryArtifactRepository()
    service = ReleaseService(
        repository, StaticBlockers(case.has_unresolved_blocker), clock=lambda: _NOW
    )
    artifact_version_id = _persist_case_version(repository, case)
    expected_conditions = _expected_conditions(case)
    request_count_before = len(repository.release_requests_for_organization(_ORGANIZATION_ID))

    result = service.request_release(_ORGANIZATION_ID, _CORRELATION_ID, artifact_version_id)

    assert result.is_success and result.value is not None
    request = result.value
    actual_conditions = {condition.name: condition.passed for condition in request.conditions}
    assert actual_conditions == expected_conditions
    expected_unmet = tuple(name for name, passed in expected_conditions.items() if not passed)
    assert request.unmet_conditions == expected_unmet
    expected_decision = ReleaseDecision.PERMITTED if not expected_unmet else ReleaseDecision.DENIED
    assert request.decision is expected_decision
    assert request.artifact_released is False
    assert (
        len(repository.release_requests_for_organization(_ORGANIZATION_ID))
        == request_count_before + 1
    )
    retained = repository.get_release_request(_ORGANIZATION_ID, request.release_request_id)
    assert retained.is_success and retained.value == request
    if request.decision is ReleaseDecision.DENIED:
        assert set(request.unmet_conditions) == {
            name for name, passed in expected_conditions.items() if not passed
        }
