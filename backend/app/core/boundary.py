"""Fail-closed target-workspace and reference-adoption authorization."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path

from app.core.decisions import TARGET_WORKSPACE
from app.core.errors import (
    AdoptionAuthorizationError,
    BoundaryErrorCode,
    BoundaryViolationError,
)

REFERENCE_WORKSPACE = r"C:\Project\generic-swarm-ops"


class BoundaryOperation(StrEnum):
    """Operations whose filesystem scope must be authorized before use."""

    ACCESS = "access"
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"


@dataclass(frozen=True, slots=True)
class AdoptionApproval:
    """A recorded human authorization for one reference-derived adoption request."""

    record_id: str
    approved_by: str
    recorded_at: datetime
    approved: bool = True

    def is_recorded_prior_to(self, requested_at: datetime) -> bool:
        """Return whether this is a complete affirmative approval recorded in advance."""
        return (
            self.approved
            and bool(self.record_id.strip())
            and bool(self.approved_by.strip())
            and self.recorded_at.tzinfo is not None
            and self.recorded_at <= requested_at
        )


class WorkspaceBoundary:
    """Authorize paths without performing writes, copies, or execution itself."""

    def __init__(
        self,
        target_workspace: Path | str = TARGET_WORKSPACE,
        reference_workspace: Path | str | None = REFERENCE_WORKSPACE,
    ) -> None:
        self._target_workspace = self._resolve(target_workspace, "configure")
        self._reference_workspace = (
            self._resolve(reference_workspace, "configure")
            if reference_workspace is not None
            else None
        )

    @property
    def target_workspace(self) -> Path:
        """Return the canonical target root used for all mutating operations."""
        return self._target_workspace

    def authorize_access(self, path: Path | str) -> Path:
        """Allow target reads and the explicit reference read-only comparison boundary."""
        return self.authorize(BoundaryOperation.ACCESS, path)

    def authorize_write(self, path: Path | str) -> Path:
        """Allow a write only when its resolved path is contained by the target root."""
        return self.authorize(BoundaryOperation.WRITE, path)

    def authorize_execution(self, path: Path | str) -> Path:
        """Allow execution only when its resolved path is contained by the target root."""
        return self.authorize(BoundaryOperation.EXECUTE, path)

    def authorize(self, operation: BoundaryOperation | str, path: Path | str) -> Path:
        """Return an authorized canonical path or fail closed without mutating either root."""
        requested_operation = self._coerce_operation(operation)
        resolved_path = self._resolve(path, requested_operation.value)
        if self._is_within(resolved_path, self._target_workspace):
            return resolved_path
        if (
            requested_operation in {BoundaryOperation.ACCESS, BoundaryOperation.READ}
            and self._reference_workspace is not None
            and self._is_within(resolved_path, self._reference_workspace)
        ):
            return resolved_path
        if self._reference_workspace is not None and self._is_within(
            resolved_path, self._reference_workspace
        ):
            raise BoundaryViolationError(
                BoundaryErrorCode.REFERENCE_WORKSPACE_READ_ONLY,
                requested_operation.value,
                "The reference workspace permits read-only comparison only.",
            )
        raise BoundaryViolationError(
            BoundaryErrorCode.OUTSIDE_TARGET_WORKSPACE,
            requested_operation.value,
            "The requested operation is outside the target workspace.",
        )

    def authorize_adoption(
        self,
        source_path: Path | str,
        destination_path: Path | str,
        approval: AdoptionApproval | None,
        *,
        requested_at: datetime | None = None,
    ) -> tuple[Path, Path]:
        """Authorize a reference-derived adoption only after prior recorded approval.

        The method only resolves and checks paths; callers may copy material only after it
        returns successfully, so every refusal leaves both workspaces unchanged.
        """
        source = self.authorize_access(source_path)
        destination = self.authorize_write(destination_path)
        if self._reference_workspace is None or not self._is_within(
            source, self._reference_workspace
        ):
            if self._is_within(source, self._target_workspace):
                return source, destination
            raise BoundaryViolationError(
                BoundaryErrorCode.OUTSIDE_TARGET_WORKSPACE,
                "adopt",
                "Adoption source is outside the allowed workspaces.",
            )

        approval_time = requested_at or datetime.now(UTC)
        if approval is None or not approval.is_recorded_prior_to(approval_time):
            raise AdoptionAuthorizationError()
        return source, destination

    @staticmethod
    def _is_within(candidate: Path, root: Path) -> bool:
        try:
            candidate.relative_to(root)
        except ValueError:
            return False
        return True

    @staticmethod
    def _resolve(path: Path | str, operation: str) -> Path:
        try:
            return Path(path).expanduser().resolve(strict=False)
        except (OSError, RuntimeError) as error:
            raise BoundaryViolationError(
                BoundaryErrorCode.OUTSIDE_TARGET_WORKSPACE,
                operation,
                "The requested path cannot be safely resolved.",
            ) from error

    @staticmethod
    def _coerce_operation(operation: BoundaryOperation | str) -> BoundaryOperation:
        try:
            return BoundaryOperation(operation)
        except ValueError as error:
            raise BoundaryViolationError(
                BoundaryErrorCode.INVALID_OPERATION,
                str(operation),
                "The requested boundary operation is invalid.",
            ) from error
