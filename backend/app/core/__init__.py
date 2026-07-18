"""Host-core safety primitives for the target-only implementation."""

from app.core.boundary import (
    AdoptionApproval,
    BoundaryOperation,
    WorkspaceBoundary,
)
from app.core.decisions import ArchitectureDecision, render_architecture_decision
from app.core.errors import (
    AdoptionAuthorizationError,
    BoundaryErrorCode,
    BoundaryViolationError,
)

__all__ = [
    "AdoptionApproval",
    "AdoptionAuthorizationError",
    "ArchitectureDecision",
    "BoundaryErrorCode",
    "BoundaryOperation",
    "BoundaryViolationError",
    "WorkspaceBoundary",
    "render_architecture_decision",
]
