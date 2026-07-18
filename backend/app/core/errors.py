"""Typed, redaction-safe errors for host safety boundaries."""

from __future__ import annotations

from enum import StrEnum


class BoundaryErrorCode(StrEnum):
    """Stable machine-readable reasons for denying a boundary request."""

    INVALID_OPERATION = "invalid_boundary_operation"
    OUTSIDE_TARGET_WORKSPACE = "outside_target_workspace"
    REFERENCE_WORKSPACE_READ_ONLY = "reference_workspace_read_only"
    ADOPTION_APPROVAL_REQUIRED = "adoption_approval_required"


class BoundaryViolationError(PermissionError):
    """A fail-closed denial that intentionally omits an untrusted path."""

    def __init__(self, code: BoundaryErrorCode, operation: str, message: str) -> None:
        self.code = code
        self.operation = operation
        self.public_message = message
        super().__init__(f"{code}: {message}")

    def to_public_detail(self) -> dict[str, str]:
        """Return a redaction-safe error projection for API callers."""
        return {"code": self.code, "message": self.public_message}


class AdoptionAuthorizationError(BoundaryViolationError):
    """Raised when reference-derived material lacks prior human approval."""

    def __init__(
        self,
        message: str = "Recorded prior human approval is required for adoption.",
    ) -> None:
        super().__init__(
            BoundaryErrorCode.ADOPTION_APPROVAL_REQUIRED,
            "adopt",
            message,
        )
