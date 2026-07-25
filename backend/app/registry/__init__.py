"""Root-confined validation and lifecycle services for domain packs."""

from app.registry.compatibility import (
    ActivationEligibility,
    ActivationGuard,
    CompatibilityEvaluation,
    CompatibilityMatrix,
    CompatibilityMatrixEntry,
    CompatibilityMatrixRepository,
    CompatibilityRegistry,
    CompatibilityService,
    DeclaredCompatibilityRanges,
    InMemoryCompatibilityMatrix,
    InMemoryCompatibilityMatrixRepository,
    InvocationGuard,
    SupportedCombination,
)
from app.registry.specials_validator import (
    AcceptedSpecialsState,
    ValidationReport,
    validate_specials_pack,
)

__all__ = [
    "AcceptedSpecialsState",
    "ActivationEligibility",
    "ActivationGuard",
    "CompatibilityEvaluation",
    "CompatibilityMatrix",
    "CompatibilityMatrixEntry",
    "CompatibilityMatrixRepository",
    "CompatibilityRegistry",
    "CompatibilityService",
    "DeclaredCompatibilityRanges",
    "InMemoryCompatibilityMatrix",
    "InMemoryCompatibilityMatrixRepository",
    "InvocationGuard",
    "SupportedCombination",
    "ValidationReport",
    "validate_specials_pack",
]
