"""Property checks for complete contract-breaking change evidence."""

from __future__ import annotations

from dataclasses import dataclass

from hypothesis import example, given, settings, strategies as st

from app.engines.migration import MigrationController
from app.engines.recovery import (
    ContractChangeEvidence,
    InMemoryImmutableVersionStore,
    RecoveryService,
)
from app.evaluation.migration_evidence import (
    InMemoryMigrationEvidenceRepository,
    MigrationEvidenceService,
)
from app.models.identifiers import CorrelationId
from tests.fakes.adoption import DeterministicAdoptionRepositories

_ARTIFACT_NAMES = (
    "architecture_decision_record",
    "migration_plan",
    "consumer_compatibility_evidence",
    "deprecation_window",
    "rollback_plan",
)


@dataclass(frozen=True, slots=True)
class ContractChangeCase:
    """Bounded presence vectors for the required contract-change artifacts."""

    case_id: int
    artifact_presence: tuple[bool, bool, bool, bool, bool]


@st.composite
def _contract_change_cases(draw: st.DrawFn) -> ContractChangeCase:
    """Generate complete and incomplete evidence vectors."""
    return ContractChangeCase(
        case_id=draw(st.integers(min_value=0, max_value=10_000)),
        artifact_presence=draw(
            st.tuples(
                st.booleans(),
                st.booleans(),
                st.booleans(),
                st.booleans(),
                st.booleans(),
            )
        ),
    )


def _complete_case(case_id: int) -> ContractChangeCase:
    """Build the complete-evidence boundary case."""
    return ContractChangeCase(case_id, (True, True, True, True, True))


def _incomplete_case(case_id: int, missing_index: int) -> ContractChangeCase:
    """Build an incomplete vector with exactly one required artifact absent."""
    presence = [True] * len(_ARTIFACT_NAMES)
    presence[missing_index] = False
    return ContractChangeCase(case_id, tuple(presence))  # type: ignore[arg-type]


def _evidence(case: ContractChangeCase) -> ContractChangeEvidence:
    """Build the reference-only evidence record represented by one generated vector."""
    references = tuple(
        f"{artifact}-property-21-{case.case_id}" if present else ""
        for artifact, present in zip(_ARTIFACT_NAMES, case.artifact_presence, strict=True)
    )
    return ContractChangeEvidence(
        architecture_decision_record=references[0],
        migration_plan=references[1],
        consumer_compatibility_evidence=references[2],
        deprecation_window=references[3],
        rollback_plan=references[4],
    )


def _controller() -> tuple[MigrationController, RecoveryService]:
    """Compose the public migration controller with isolated in-memory fakes."""
    migration_evidence = MigrationEvidenceService(InMemoryMigrationEvidenceRepository())
    recovery = RecoveryService(
        DeterministicAdoptionRepositories().recoveries,
        InMemoryImmutableVersionStore(),
    )
    return MigrationController(migration_evidence, recovery), recovery


# Feature: adoption-redesign, Property 21: Contract-breaking approval requires complete evidence
# **Validates: Requirements 8.6, 8.7**
@settings(max_examples=100, deadline=None)
@example(case=_complete_case(0))
@example(case=_incomplete_case(1, 0))
@example(case=_incomplete_case(2, 1))
@example(case=_incomplete_case(3, 2))
@example(case=_incomplete_case(4, 3))
@example(case=_incomplete_case(5, 4))
@given(case=_contract_change_cases())
def test_property_21_contract_breaking_approval_requires_complete_evidence(
    case: ContractChangeCase,
) -> None:
    """Approval succeeds exactly when every required artifact reference exists."""
    controller, recovery = _controller()
    correlation_id = CorrelationId(f"correlation-property-21-{case.case_id}")
    evidence = _evidence(case)
    expected_complete = all(case.artifact_presence)

    result = controller.approve_contract_change(
        correlation_id,
        evidence,
        change_id=f"contract-change-property-21-{case.case_id}",
    )

    assert result.is_success is expected_complete
    if expected_complete:
        assert result.value is not None
        assert result.value.approved
        assert result.value.evidence == evidence
    else:
        assert result.value is None
        assert result.error is not None
        assert result.error.fields
        assert {field.name for field in result.error.fields} == {
            artifact
            for artifact, present in zip(_ARTIFACT_NAMES, case.artifact_presence, strict=True)
            if not present
        }

    assert recovery.contract_decisions[-1].approved is expected_complete
