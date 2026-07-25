"""Host-core safety primitives for the target-only implementation."""

from app.core.boundary import (
    AdoptionApproval,
    BoundaryOperation,
    WorkspaceBoundary,
)
from app.core.configuration import (
    ComponentHealthSummary,
    ComponentStartupStatus,
    ConfigurationService,
    DependencyReadiness,
    DependencyState,
    HealthDependency,
    HealthService,
    LivenessSnapshot,
    OperationalHealthSnapshot,
    ReadinessSnapshot,
    SecretResolution,
    SecretSource,
    StartupComponent,
    StartupConfigurationStatus,
)
from app.core.decisions import ArchitectureDecision, render_architecture_decision
from app.core.errors import (
    AdoptionAuthorizationError,
    BoundaryErrorCode,
    BoundaryViolationError,
)
from app.core.retention import RetentionRepository, RetentionService

__all__ = [
    "AdoptionApproval",
    "AdoptionAuthorizationError",
    "ArchitectureDecision",
    "BoundaryErrorCode",
    "BoundaryOperation",
    "BoundaryViolationError",
    "ComponentHealthSummary",
    "ComponentStartupStatus",
    "ConfigurationService",
    "DependencyReadiness",
    "DependencyState",
    "HealthDependency",
    "HealthService",
    "LivenessSnapshot",
    "OperationalHealthSnapshot",
    "ReadinessSnapshot",
    "RetentionRepository",
    "RetentionService",
    "SecretResolution",
    "SecretSource",
    "StartupComponent",
    "StartupConfigurationStatus",
    "WorkspaceBoundary",
    "render_architecture_decision",
]
