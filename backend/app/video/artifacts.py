"""Immutable Video_Pack artifact versions and deterministic lineage validation."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from typing import NewType

from app.models.common import RecordMetadata

VideoArtifactId = NewType("VideoArtifactId", str)
VideoArtifactVersionId = NewType("VideoArtifactVersionId", str)
ReleaseRequestId = NewType("ReleaseRequestId", str)


class ReleaseDecision(StrEnum):
    """A readiness decision; neither value causes a media release."""

    DENIED = "denied"
    PERMITTED = "permitted"


@dataclass(frozen=True, slots=True)
class NamedReleaseCheck:
    """One immutable named quality or release-gate outcome."""

    name: str
    passed: bool
    evidence_reference: str

    def __post_init__(self) -> None:
        if not self.name.strip() or not self.evidence_reference.strip():
            raise ValueError("Named release checks require a name and evidence reference.")


@dataclass(frozen=True, slots=True)
class VideoArtifactVersion:
    """A copy-on-write artifact version with immutable parent references."""

    metadata: RecordMetadata
    artifact_id: VideoArtifactId
    artifact_version_id: VideoArtifactVersionId
    parent_version_ids: tuple[VideoArtifactVersionId, ...]
    rights_and_consent_passed: bool
    provenance_and_signoff_passed: bool
    quality_checks: tuple[NamedReleaseCheck, ...]
    release_checks: tuple[NamedReleaseCheck, ...]


@dataclass(frozen=True, slots=True)
class LineageIssue:
    """A specific redaction-safe reason lineage cannot be trusted."""

    code: str
    version_id: VideoArtifactVersionId


@dataclass(frozen=True, slots=True)
class LineageValidation:
    """The complete acyclic-DAG validation result for one artifact version."""

    is_valid: bool
    issues: tuple[LineageIssue, ...]


@dataclass(frozen=True, slots=True)
class ReleaseCondition:
    """One independently evaluated gate in a retained release decision."""

    name: str
    passed: bool
    evidence_references: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ReleaseRequest:
    """An immutable readiness decision; it deliberately cannot release media."""

    metadata: RecordMetadata
    release_request_id: ReleaseRequestId
    artifact_version_id: VideoArtifactVersionId
    conditions: tuple[ReleaseCondition, ...]
    unmet_conditions: tuple[str, ...]
    decision: ReleaseDecision
    artifact_released: bool = False


class LineageValidator:
    """Validate a known immutable parent graph as an acyclic, unambiguous DAG."""

    def validate(
        self,
        artifact_version_id: VideoArtifactVersionId,
        lookup: Callable[[VideoArtifactVersionId], VideoArtifactVersion | None],
    ) -> LineageValidation:
        """Return every cycle, ambiguity, and unknown-parent condition without mutation."""
        issues: list[LineageIssue] = []
        issue_keys: set[tuple[str, VideoArtifactVersionId]] = set()
        visited: set[VideoArtifactVersionId] = set()
        visiting: set[VideoArtifactVersionId] = set()

        def add_issue(code: str, version_id: VideoArtifactVersionId) -> None:
            key = (code, version_id)
            if key not in issue_keys:
                issue_keys.add(key)
                issues.append(LineageIssue(code, version_id))

        def walk(version_id: VideoArtifactVersionId) -> None:
            if version_id in visiting:
                add_issue("lineage_cyclic", version_id)
                return
            if version_id in visited:
                return
            version = lookup(version_id)
            if version is None:
                add_issue("lineage_unknown_version", version_id)
                return
            visiting.add(version_id)
            parent_ids = version.parent_version_ids
            if len(parent_ids) != len(set(parent_ids)):
                add_issue("lineage_ambiguous_duplicate_parent", version_id)
            for parent_id in parent_ids:
                if not str(parent_id).strip():
                    add_issue("lineage_ambiguous_blank_parent", version_id)
                    continue
                walk(parent_id)
            visiting.remove(version_id)
            visited.add(version_id)

        walk(artifact_version_id)
        return LineageValidation(not issues, tuple(issues))
