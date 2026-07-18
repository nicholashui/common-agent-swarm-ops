"""Lock-protected local retention for immutable video artifact versions."""

from __future__ import annotations

from threading import RLock

from app.models.common import VersionedRecord
from app.models.contracts import ErrorCode, ErrorDetail, Result
from app.models.identifiers import CorrelationId, OrganizationId, RecordId
from app.video.artifacts import (
    ReleaseRequest,
    ReleaseRequestId,
    VideoArtifactVersion,
    VideoArtifactVersionId,
)


class InMemoryArtifactRepository:
    """Retain immutable artifact versions and every release-readiness request."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._versions: dict[VideoArtifactVersionId, VideoArtifactVersion] = {}
        self._requests: dict[ReleaseRequestId, ReleaseRequest] = {}
        self._record_ids: set[RecordId] = set()

    def create_version(
        self, record: VideoArtifactVersion
    ) -> Result[VideoArtifactVersion, ErrorDetail]:
        """Persist one new immutable version without modifying a parent version."""
        with self._lock:
            if record.artifact_version_id in self._versions or not self._claim(
                record.metadata.record_id
            ):
                return Result.failure(
                    self._error(ErrorCode.CONFLICT, "Artifact version already exists.")
                )
            self._versions[record.artifact_version_id] = record
            return Result.success(record)

    def get_version(
        self, organization_id: OrganizationId, artifact_version_id: VideoArtifactVersionId
    ) -> Result[VideoArtifactVersion, ErrorDetail]:
        """Return a version only when it belongs to the authenticated organization."""
        with self._lock:
            return self._scoped(
                self._versions.get(artifact_version_id),
                organization_id,
                "Artifact version",
            )

    def version_for_lineage(
        self, organization_id: OrganizationId, artifact_version_id: VideoArtifactVersionId
    ) -> VideoArtifactVersion | None:
        """Return an organization-scoped immutable parent snapshot for validation."""
        with self._lock:
            version = self._versions.get(artifact_version_id)
            if version is None or version.metadata.organization_id != organization_id:
                return None
            return version

    def create_release_request(self, record: ReleaseRequest) -> Result[ReleaseRequest, ErrorDetail]:
        """Append every readiness decision, including denied and unknown-artifact requests."""
        with self._lock:
            if record.release_request_id in self._requests or not self._claim(
                record.metadata.record_id
            ):
                return Result.failure(
                    self._error(ErrorCode.CONFLICT, "Release request already exists.")
                )
            self._requests[record.release_request_id] = record
            return Result.success(record)

    def get_release_request(
        self, organization_id: OrganizationId, release_request_id: ReleaseRequestId
    ) -> Result[ReleaseRequest, ErrorDetail]:
        """Return a retained release request only to its authenticated organization."""
        with self._lock:
            return self._scoped(
                self._requests.get(release_request_id), organization_id, "Release request"
            )

    def versions_for_organization(
        self, organization_id: OrganizationId
    ) -> tuple[VideoArtifactVersion, ...]:
        """Return immutable local version snapshots for deterministic inspection."""
        with self._lock:
            return tuple(
                record
                for record in self._versions.values()
                if record.metadata.organization_id == organization_id
            )

    def release_requests_for_organization(
        self, organization_id: OrganizationId
    ) -> tuple[ReleaseRequest, ...]:
        """Return every retained local decision within one tenant boundary."""
        with self._lock:
            return tuple(
                record
                for record in self._requests.values()
                if record.metadata.organization_id == organization_id
            )

    def _claim(self, record_id: RecordId) -> bool:
        if record_id in self._record_ids:
            return False
        self._record_ids.add(record_id)
        return True

    @staticmethod
    def _scoped[T: VersionedRecord](
        record: T | None, organization_id: OrganizationId, record_name: str
    ) -> Result[T, ErrorDetail]:
        if record is None or record.metadata.organization_id != organization_id:
            return Result.failure(
                InMemoryArtifactRepository._error(
                    ErrorCode.NOT_FOUND, f"{record_name} was not found."
                )
            )
        return Result.success(record)

    @staticmethod
    def _error(code: ErrorCode, message: str) -> ErrorDetail:
        return ErrorDetail(code, message, CorrelationId("artifact-repository"))
