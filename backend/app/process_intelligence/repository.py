"""Root-confined JSON persistence for source-traceable process artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from threading import RLock
from typing import Final

from app.core.boundary import WorkspaceBoundary
from app.core.errors import BoundaryViolationError
from app.models.contracts import ErrorCode, ErrorDetail, RepositoryError, Result
from app.models.identifiers import CorrelationId, RecordId
from app.process_intelligence.models import ProcessArtifact

_ARTIFACT_RELATIVE_ROOT: Final[Path] = Path(
    "business", "process-intelligence", "artifacts"
)


class RootConfinedProcessArtifactRepository:
    """Write artifacts only below the target-local process-intelligence business root."""

    def __init__(self, boundary: WorkspaceBoundary | None = None) -> None:
        self._boundary = boundary or WorkspaceBoundary()
        self._artifact_root = self._boundary.authorize_write(
            self._boundary.target_workspace / _ARTIFACT_RELATIVE_ROOT
        )
        self._lock = RLock()

    @property
    def artifact_root(self) -> Path:
        """Return the canonical, target-confined storage root."""
        return self._artifact_root

    def ensure_storage_root(self) -> Result[Path, RepositoryError]:
        """Create the fixed target-local artifact directory through boundary authorization."""
        with self._lock:
            try:
                self._ensure_artifact_root()
            except (BoundaryViolationError, OSError):
                return Result.failure(
                    self._error(
                        ErrorCode.REPOSITORY_UNAVAILABLE,
                        "Artifact storage is unavailable.",
                    )
                )
        return Result.success(self._artifact_root)

    def persist(self, artifact: ProcessArtifact) -> Result[ProcessArtifact, RepositoryError]:
        """Persist one immutable artifact without accepting any caller-controlled path."""
        with self._lock:
            try:
                self._ensure_artifact_root()
                artifact_path = self._artifact_path(artifact.metadata.record_id)
                if artifact_path.exists():
                    return Result.failure(
                        self._error(ErrorCode.CONFLICT, "Artifact already exists.")
                    )
                serialized = self._serialize(artifact)
                with artifact_path.open("x", encoding="utf-8") as artifact_file:
                    artifact_file.write(serialized)
            except (BoundaryViolationError, OSError, TypeError, ValueError):
                return Result.failure(
                    self._error(
                        ErrorCode.REPOSITORY_UNAVAILABLE,
                        "Artifact storage is unavailable.",
                    )
                )
        return Result.success(artifact)

    def _ensure_artifact_root(self) -> None:
        authorized_root = self._boundary.authorize_write(self._artifact_root)
        authorized_root.mkdir(parents=True, exist_ok=True)

    def _artifact_path(self, record_id: RecordId) -> Path:
        candidate = self._boundary.authorize_write(self._artifact_root / f"{record_id}.json")
        try:
            candidate.relative_to(self._artifact_root)
        except ValueError as error:
            raise OSError("Artifact path escaped the configured storage root.") from error
        return candidate

    @staticmethod
    def _serialize(artifact: ProcessArtifact) -> str:
        payload = {
            "artifact_id": artifact.metadata.record_id,
            "schema_version": artifact.metadata.schema_version,
            "version": artifact.metadata.version,
            "organization_id": artifact.metadata.organization_id,
            "correlation_id": artifact.metadata.correlation_id,
            "created_at": artifact.metadata.created_at.isoformat(),
            "updated_at": artifact.metadata.updated_at.isoformat(),
            "kind": artifact.kind.value,
            "source_log_set_id": artifact.source_log_set_id,
            "supporting_record_refs": artifact.supporting_record_refs,
            "output": artifact.output,
        }
        return json.dumps(payload, ensure_ascii=True, separators=(",", ":"), sort_keys=True)

    @staticmethod
    def _error(code: ErrorCode, message: str) -> ErrorDetail:
        return ErrorDetail(code, message, CorrelationId("process-artifact-repository"))
