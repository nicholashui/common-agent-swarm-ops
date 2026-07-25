"""Lock-protected local retention for immutable artifact records."""

from __future__ import annotations

from dataclasses import replace
from threading import RLock

from app.models.common import VersionedRecord
from app.models.contracts import ErrorCode, ErrorDetail, Result
from app.models.control_plane import ArtifactAvailabilityStatus, ArtifactHandoff, ArtifactHandoffId
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
        self._handoffs: dict[ArtifactHandoffId, ArtifactHandoff] = {}
        self._revoked_handoffs: set[ArtifactHandoffId] = set()
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

    def append(self, record: ArtifactHandoff) -> Result[ArtifactHandoff, ErrorDetail]:
        """Persist one complete, immutable handoff after lineage validation."""
        return self.append_handoff(record)

    def append_handoff(self, record: ArtifactHandoff) -> Result[ArtifactHandoff, ErrorDetail]:
        """Persist an opaque handoff without accepting protected artifact content."""
        with self._lock:
            validation_error = self._validate_handoff(record)
            if validation_error is not None:
                return Result.failure(validation_error)
            lineage_error = self._lineage_error(record)
            if lineage_error is not None:
                return Result.failure(lineage_error)
            if record.handoff_id in self._handoffs or not self._claim(record.metadata.record_id):
                return Result.failure(
                    self._error(
                        ErrorCode.CONFLICT,
                        "Artifact handoff already exists.",
                        record.metadata.correlation_id,
                    )
                )
            self._handoffs[record.handoff_id] = record
            return Result.success(record)

    def get(
        self, organization_id: OrganizationId, handoff_id: ArtifactHandoffId
    ) -> Result[ArtifactHandoff, ErrorDetail]:
        """Return an organization-scoped immutable handoff snapshot."""
        with self._lock:
            record = self._handoffs.get(handoff_id)
            if record is not None and handoff_id in self._revoked_handoffs:
                record = replace(record, availability=ArtifactAvailabilityStatus.REVOKED)
            return self._scoped(record, organization_id, "Artifact handoff")

    def list_for_organization(
        self, organization_id: OrganizationId
    ) -> Result[tuple[ArtifactHandoff, ...], ErrorDetail]:
        """Return handoff snapshots in insertion order within one organization."""
        with self._lock:
            return Result.success(
                tuple(
                    self._handoff_snapshot(record)
                    for record in self._handoffs.values()
                    if record.metadata.organization_id == organization_id
                )
            )

    def handoffs_for_organization(
        self, organization_id: OrganizationId
    ) -> tuple[ArtifactHandoff, ...]:
        """Return local handoff snapshots for deterministic inspection."""
        result = self.list_for_organization(organization_id)
        return result.value or ()

    def available_for_downstream(
        self, organization_id: OrganizationId
    ) -> Result[tuple[ArtifactHandoff, ...], ErrorDetail]:
        """Expose only metadata-confirmed handoffs that have not been revoked."""
        with self._lock:
            return Result.success(
                tuple(
                    self._handoff_snapshot(record)
                    for handoff_id, record in self._handoffs.items()
                    if (
                        record.metadata.organization_id == organization_id
                        and handoff_id not in self._revoked_handoffs
                        and record.availability is ArtifactAvailabilityStatus.AVAILABLE
                        and record.metadata_persisted
                    )
                )
            )

    def confirm_metadata_persistence(
        self, organization_id: OrganizationId, handoff_id: ArtifactHandoffId
    ) -> Result[ArtifactHandoff, ErrorDetail]:
        """Commit the external availability barrier after metadata persistence succeeds."""
        with self._lock:
            current = self._handoffs.get(handoff_id)
            scoped = self._scoped(current, organization_id, "Artifact handoff")
            if not scoped.is_success or scoped.value is None:
                return scoped
            if current is None:
                return Result.failure(
                    self._error(ErrorCode.NOT_FOUND, "Artifact handoff was not found.")
                )
            if not current.external:
                return Result.success(self._handoff_snapshot(current))
            if handoff_id in self._revoked_handoffs:
                return Result.failure(
                    self._error(
                        ErrorCode.INVALID_TRANSITION,
                        "A revoked artifact handoff cannot become available.",
                        current.metadata.correlation_id,
                    )
                )
            confirmed = replace(
                current,
                availability=ArtifactAvailabilityStatus.AVAILABLE,
                metadata_persisted=True,
            )
            self._handoffs[handoff_id] = confirmed
            return Result.success(confirmed)

    def revoke_availability(
        self, organization_id: OrganizationId, handoff_id: ArtifactHandoffId
    ) -> Result[ArtifactHandoff, ErrorDetail]:
        """Revoke downstream availability without mutating the retained frozen record."""
        with self._lock:
            current = self._handoffs.get(handoff_id)
            scoped = self._scoped(current, organization_id, "Artifact handoff")
            if not scoped.is_success or scoped.value is None:
                return scoped
            current = scoped.value
            self._revoked_handoffs.add(handoff_id)
            return Result.success(self._handoff_snapshot(current))

    # Short aliases keep the repository convenient for recovery workers.
    confirm_external = confirm_metadata_persistence
    revoke = revoke_availability

    def validate_lineage(self, record: ArtifactHandoff) -> Result[bool, ErrorDetail]:
        """Validate the candidate lineage against retained handoffs without persisting it."""
        with self._lock:
            error = self._validate_handoff(record) or self._lineage_error(record)
            if error is not None:
                return Result.failure(error)
            return Result.success(True)

    def _validate_handoff(self, record: ArtifactHandoff) -> ErrorDetail | None:
        """Check the metadata required for a traceable handoff."""
        required = {
            "artifact_identity": record.artifact_identity,
            "artifact_version": record.artifact_version,
            "source_task_id": record.source_task_id,
            "source_run_reference": record.source_run_reference,
            "owner_reference": record.owner_reference,
            "classification": record.classification,
            "integrity_reference": record.integrity_reference,
            "approval_reference": record.approval_reference,
            "provenance_reference": record.provenance_reference,
        }
        missing = tuple(
            name for name, value in required.items() if value is None or not str(value).strip()
        )
        if missing:
            return ErrorDetail(
                ErrorCode.VALIDATION_FAILED,
                "Artifact handoff metadata is incomplete.",
                record.metadata.correlation_id,
            )
        lineage = tuple(str(reference) for reference in record.parent_lineage)
        if len(lineage) != len(set(lineage)) or any(not reference.strip() for reference in lineage):
            return ErrorDetail(
                ErrorCode.VALIDATION_FAILED,
                "Artifact handoff lineage references are invalid.",
                record.metadata.correlation_id,
            )
        if (
            record.availability is ArtifactAvailabilityStatus.AVAILABLE
            and not record.metadata_persisted
        ):
            return ErrorDetail(
                ErrorCode.VALIDATION_FAILED,
                "Artifact handoff availability requires metadata confirmation.",
                record.metadata.correlation_id,
            )
        return None

    def _lineage_error(self, record: ArtifactHandoff) -> ErrorDetail | None:
        """Reject self-references and cycles through already-retained handoffs."""
        candidate_id = str(record.handoff_id)
        if candidate_id in record.parent_lineage:
            return ErrorDetail(
                ErrorCode.CONFLICT,
                "Artifact handoff lineage contains a cycle.",
                record.metadata.correlation_id,
            )

        graph = {
            str(handoff_id): tuple(handoff.parent_lineage)
            for handoff_id, handoff in self._handoffs.items()
            if handoff.metadata.organization_id == record.metadata.organization_id
        }
        graph[candidate_id] = tuple(record.parent_lineage)
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(node: str) -> bool:
            if node in visiting:
                return False
            if node in visited:
                return True
            visiting.add(node)
            for parent in graph.get(node, ()):
                if parent in graph and not visit(parent):
                    return False
            visiting.remove(node)
            visited.add(node)
            return True

        if not visit(candidate_id):
            return ErrorDetail(
                ErrorCode.CONFLICT,
                "Artifact handoff lineage contains a cycle.",
                record.metadata.correlation_id,
            )
        for parent in record.parent_lineage:
            retained = self._handoffs.get(ArtifactHandoffId(parent))
            if (
                retained is not None
                and retained.metadata.organization_id != record.metadata.organization_id
            ):
                return ErrorDetail(
                    ErrorCode.AUTHORIZATION_DENIED,
                    "Artifact handoff lineage crosses an organization boundary.",
                    record.metadata.correlation_id,
                )
        return None

    def _handoff_snapshot(self, record: ArtifactHandoff) -> ArtifactHandoff:
        """Return a frozen record view reflecting an independent availability revocation."""
        if record.handoff_id in self._revoked_handoffs:
            return replace(record, availability=ArtifactAvailabilityStatus.REVOKED)
        return record

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
    def _error(
        code: ErrorCode,
        message: str,
        correlation_id: CorrelationId | None = None,
    ) -> ErrorDetail:
        return ErrorDetail(code, message, correlation_id or CorrelationId("artifact-repository"))
