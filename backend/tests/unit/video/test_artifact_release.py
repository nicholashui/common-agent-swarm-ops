"""Focused local examples for immutable artifact and release-readiness controls."""

from __future__ import annotations

from datetime import UTC, datetime

from app.models.common import RecordMetadata
from app.models.identifiers import CorrelationId, OrganizationId, RecordId
from app.repositories.artifact_repository import InMemoryArtifactRepository
from app.video.artifacts import (
    LineageValidator,
    NamedReleaseCheck,
    ReleaseDecision,
    VideoArtifactId,
    VideoArtifactVersion,
    VideoArtifactVersionId,
)
from app.video.release import ReleaseService, VideoBlockerProvider

ORG_ID = OrganizationId("video-org")
CORRELATION_ID = CorrelationId("video-correlation")
TIMESTAMP = datetime(2025, 1, 1, tzinfo=UTC)


class StaticBlockers(VideoBlockerProvider):
    """A trusted deterministic blocker source used only for local decision tests."""

    def __init__(self, blockers: tuple[str, ...] = ()) -> None:
        self._blockers = blockers

    def unresolved_for(
        self, organization_id: OrganizationId, artifact_version_id: VideoArtifactVersionId
    ) -> tuple[str, ...]:
        del organization_id, artifact_version_id
        return self._blockers


def _version(version_id: str, parents: tuple[str, ...] = ()) -> VideoArtifactVersion:
    """Build a static record for isolated lineage checks."""
    metadata = RecordMetadata(
        RecordId(f"record-{version_id}"), ORG_ID, CORRELATION_ID, 1, 1, TIMESTAMP, TIMESTAMP
    )
    return VideoArtifactVersion(
        metadata,
        VideoArtifactId("campaign-video"),
        VideoArtifactVersionId(version_id),
        tuple(VideoArtifactVersionId(parent) for parent in parents),
        True,
        True,
        (NamedReleaseCheck("sharpness", True, "quality-1"),),
        (NamedReleaseCheck("brand-review", True, "gate-1"),),
    )


def test_lineage_validator_reports_every_unknown_and_cyclic_parent() -> None:
    """Cycles and unknown parents are visible, not silently treated as releasable lineage."""
    records = {
        VideoArtifactVersionId("version-a"): _version("version-a", ("version-b",)),
        VideoArtifactVersionId("version-b"): _version("version-b", ("version-a", "missing")),
    }

    validation = LineageValidator().validate(VideoArtifactVersionId("version-a"), records.get)

    assert not validation.is_valid
    assert {issue.code for issue in validation.issues} == {
        "lineage_cyclic",
        "lineage_unknown_version",
    }


def test_release_requests_are_retained_and_fail_closed_for_every_unmet_gate() -> None:
    """A denied local readiness decision retains gate failures and never releases media."""
    repository = InMemoryArtifactRepository()
    service = ReleaseService(repository, StaticBlockers(("compliance-7",)), lambda: TIMESTAMP)
    created = service.create_artifact_version(
        ORG_ID,
        CORRELATION_ID,
        "campaign-video",
        (),
        False,
        False,
        (NamedReleaseCheck("sharpness", False, "quality-1"),),
        (NamedReleaseCheck("brand-review", False, "gate-1"),),
    )
    assert created.is_success and created.value is not None

    decision = service.request_release(ORG_ID, CORRELATION_ID, created.value.artifact_version_id)

    assert decision.is_success and decision.value is not None
    retained = decision.value
    assert retained.decision is ReleaseDecision.DENIED
    assert retained.artifact_released is False
    assert set(retained.unmet_conditions) == {
        "rights_and_consent",
        "provenance_and_signoff",
        "quality:sharpness",
        "release:brand-review",
        "no_unresolved_blockers",
    }
    assert repository.get_release_request(ORG_ID, retained.release_request_id).is_success


def test_passing_readiness_decision_is_non_releasing_and_versions_are_append_only() -> None:
    """A permitted result is a safe decision record while parent and child remain immutable."""
    repository = InMemoryArtifactRepository()
    service = ReleaseService(repository, clock=lambda: TIMESTAMP)
    parent = service.create_artifact_version(
        ORG_ID,
        CORRELATION_ID,
        "campaign-video",
        (),
        True,
        True,
        (NamedReleaseCheck("sharpness", True, "quality-1"),),
        (NamedReleaseCheck("brand-review", True, "gate-1"),),
    )
    assert parent.is_success and parent.value is not None
    child = service.create_artifact_version(
        ORG_ID,
        CORRELATION_ID,
        "campaign-video",
        (parent.value.artifact_version_id,),
        True,
        True,
        (NamedReleaseCheck("sharpness", True, "quality-2"),),
        (NamedReleaseCheck("brand-review", True, "gate-2"),),
    )
    assert child.is_success and child.value is not None

    decision = service.request_release(ORG_ID, CORRELATION_ID, child.value.artifact_version_id)

    assert decision.is_success and decision.value is not None
    assert decision.value.decision is ReleaseDecision.PERMITTED
    assert decision.value.artifact_released is False
    assert parent.value.parent_version_ids == ()
    assert child.value.parent_version_ids == (parent.value.artifact_version_id,)
    assert len(repository.versions_for_organization(ORG_ID)) == 2
