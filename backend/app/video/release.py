"""Fail-closed local-only Video_Pack release-readiness decisions."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from datetime import datetime

from app.models.common import SCHEMA_VERSION, RecordMetadata, utc_now
from app.models.contracts import ErrorCode, ErrorDetail, Result
from app.models.identifiers import CorrelationId, OrganizationId, new_record_id
from app.repositories.artifact_repository import InMemoryArtifactRepository
from app.video.artifacts import (
    LineageValidator,
    NamedReleaseCheck,
    ReleaseCondition,
    ReleaseDecision,
    ReleaseRequest,
    ReleaseRequestId,
    VideoArtifactId,
    VideoArtifactVersion,
    VideoArtifactVersionId,
)


class VideoBlockerProvider:
    """Trusted local source of unresolved Video_Pack blocker identifiers."""

    def unresolved_for(
        self, organization_id: OrganizationId, artifact_version_id: VideoArtifactVersionId
    ) -> tuple[str, ...]:
        """Return redaction-safe blockers that must deny the decision."""
        return ()


class RunOutputBlockerProvider(VideoBlockerProvider):
    """Resolve retained unresolved blocker events without contacting external services."""

    def __init__(self, records: Callable[[], Sequence[object]]) -> None:
        self._records = records

    def unresolved_for(
        self, organization_id: OrganizationId, artifact_version_id: VideoArtifactVersionId
    ) -> tuple[str, ...]:
        """Read local run projections; artifacts never control their own blocker state."""
        del artifact_version_id
        blocker_ids: set[str] = set()
        for record in self._records():
            metadata = getattr(record, "metadata", None)
            output = getattr(record, "output", None)
            if getattr(metadata, "organization_id", None) != organization_id:
                continue
            if not isinstance(output, Mapping):
                continue
            events = output.get("video_blocker_events", ())
            if not isinstance(events, list | tuple):
                continue
            for event in events:
                if isinstance(event, Mapping) and event.get("status") == "unresolved":
                    blocker_id = event.get("blocker_id")
                    if isinstance(blocker_id, str) and blocker_id.strip():
                        blocker_ids.add(blocker_id)
        return tuple(sorted(blocker_ids))


class ReleaseService:
    """Create immutable versions and retain complete release-readiness decisions."""

    def __init__(
        self,
        repository: InMemoryArtifactRepository,
        blocker_provider: VideoBlockerProvider | None = None,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._repository = repository
        self._blocker_provider = blocker_provider or VideoBlockerProvider()
        self._clock = clock
        self._lineage_validator = LineageValidator()

    def create_artifact_version(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        artifact_id: str,
        parent_version_ids: tuple[VideoArtifactVersionId, ...],
        rights_and_consent_passed: bool,
        provenance_and_signoff_passed: bool,
        quality_checks: Sequence[object],
        release_checks: Sequence[object],
    ) -> Result[VideoArtifactVersion, ErrorDetail]:
        """Store a copy-on-write version; parent records remain untouched."""
        if not artifact_id.strip():
            return Result.failure(
                self._validation("Artifact identifiers must be non-empty.", correlation_id)
            )
        try:
            normalized_quality = self._checks(quality_checks)
            normalized_release = self._checks(release_checks)
        except ValueError as error:
            return Result.failure(self._validation(str(error), correlation_id))
        record = VideoArtifactVersion(
            self._metadata(organization_id, correlation_id),
            VideoArtifactId(artifact_id),
            VideoArtifactVersionId(str(new_record_id())),
            parent_version_ids,
            rights_and_consent_passed,
            provenance_and_signoff_passed,
            normalized_quality,
            normalized_release,
        )
        persisted = self._repository.create_version(record)
        return self._repository_failure(persisted, correlation_id)

    def request_release(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        artifact_version_id: VideoArtifactVersionId,
    ) -> Result[ReleaseRequest, ErrorDetail]:
        """Retain a full decision but never release an artifact or call a media provider."""
        version = self._repository.version_for_lineage(organization_id, artifact_version_id)
        blockers = self._blocker_provider.unresolved_for(organization_id, artifact_version_id)
        conditions = self._conditions(organization_id, artifact_version_id, version, blockers)
        unmet = tuple(condition.name for condition in conditions if not condition.passed)
        record = ReleaseRequest(
            self._metadata(organization_id, correlation_id),
            ReleaseRequestId(str(new_record_id())),
            artifact_version_id,
            conditions,
            unmet,
            ReleaseDecision.PERMITTED if not unmet else ReleaseDecision.DENIED,
        )
        persisted = self._repository.create_release_request(record)
        return self._repository_failure(persisted, correlation_id)

    def get_release_request(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        release_request_id: str,
    ) -> Result[ReleaseRequest, ErrorDetail]:
        """Read an immutable decision through tenant-scoped repository access."""
        result = self._repository.get_release_request(
            organization_id, ReleaseRequestId(release_request_id)
        )
        return self._repository_failure(result, correlation_id)

    def _conditions(
        self,
        organization_id: OrganizationId,
        artifact_version_id: VideoArtifactVersionId,
        version: VideoArtifactVersion | None,
        blockers: tuple[str, ...],
    ) -> tuple[ReleaseCondition, ...]:
        if version is None:
            return (
                ReleaseCondition("artifact_version_known", False, (str(artifact_version_id),)),
                ReleaseCondition("immutable_acyclic_known_lineage", False, ()),
                ReleaseCondition("rights_and_consent", False, ()),
                ReleaseCondition("provenance_and_signoff", False, ()),
                ReleaseCondition("named_quality_checks_present", False, ()),
                ReleaseCondition("named_release_checks_present", False, ()),
                ReleaseCondition("no_unresolved_blockers", not blockers, blockers),
            )
        lineage = self._lineage_validator.validate(
            artifact_version_id,
            lambda version_id: self._repository.version_for_lineage(organization_id, version_id),
        )
        lineage_references = tuple(str(issue.version_id) for issue in lineage.issues)
        conditions: list[ReleaseCondition] = [
            ReleaseCondition("artifact_version_known", True, (str(artifact_version_id),)),
            ReleaseCondition(
                "immutable_acyclic_known_lineage", lineage.is_valid, lineage_references
            ),
            ReleaseCondition("rights_and_consent", version.rights_and_consent_passed),
            ReleaseCondition("provenance_and_signoff", version.provenance_and_signoff_passed),
            ReleaseCondition(
                "named_quality_checks_present",
                bool(version.quality_checks),
                tuple(check.evidence_reference for check in version.quality_checks),
            ),
            ReleaseCondition(
                "named_release_checks_present",
                bool(version.release_checks),
                tuple(check.evidence_reference for check in version.release_checks),
            ),
        ]
        conditions.extend(
            ReleaseCondition(f"quality:{check.name}", check.passed, (check.evidence_reference,))
            for check in version.quality_checks
        )
        conditions.extend(
            ReleaseCondition(f"release:{check.name}", check.passed, (check.evidence_reference,))
            for check in version.release_checks
        )
        conditions.append(ReleaseCondition("no_unresolved_blockers", not blockers, blockers))
        return tuple(conditions)

    @staticmethod
    def _checks(values: Sequence[object]) -> tuple[NamedReleaseCheck, ...]:
        checks = tuple(value for value in values if isinstance(value, NamedReleaseCheck))
        if len(checks) != len(values):
            raise ValueError("Release checks must use immutable named check records.")
        names = tuple(check.name for check in checks)
        if len(names) != len(set(names)):
            raise ValueError("Release check names must be unique within each gate type.")
        return checks

    def _metadata(
        self, organization_id: OrganizationId, correlation_id: CorrelationId
    ) -> RecordMetadata:
        recorded_at = self._clock()
        return RecordMetadata(
            new_record_id(),
            organization_id,
            correlation_id,
            SCHEMA_VERSION,
            1,
            recorded_at,
            recorded_at,
        )

    @staticmethod
    def _validation(message: str, correlation_id: CorrelationId) -> ErrorDetail:
        return ErrorDetail(ErrorCode.VALIDATION_FAILED, message, correlation_id)

    @staticmethod
    def _repository_failure[T](
        result: Result[T, ErrorDetail], correlation_id: CorrelationId
    ) -> Result[T, ErrorDetail]:
        if result.is_success:
            return result
        error = result.error
        if error is None:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.REPOSITORY_UNAVAILABLE,
                    "Video artifact storage is unavailable.",
                    correlation_id,
                )
            )
        return Result.failure(
            ErrorDetail(error.code, error.message, correlation_id, error.retryable, error.fields)
        )
