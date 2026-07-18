"""Property tests for retained evaluation execution identity and gating."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime

from hypothesis import given, settings, strategies as st

from app.evaluation.models import (
    DEFAULT_NAMED_CHECKS,
    EvaluationCellResult,
    EvaluationOutcome,
    GoldenTask,
    NamedEvaluationCheck,
)
from app.evaluation.service import EvaluationService
from app.models.identifiers import CorrelationId, OrganizationId
from app.repositories.evaluation_repository import InMemoryEvaluationRepository

# Feature: generic-swarm-business-os, Property 18: Evaluation results preserve execution identity
# and current-blocker semantics.
# **Validates: Requirements 8.2, 8.5, 8.8**

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_ORGANIZATION_ID = OrganizationId("org-property-18")
_FIRST_CORRELATION_ID = CorrelationId("property-18-first")
_SECOND_CORRELATION_ID = CorrelationId("property-18-second")


@dataclass(frozen=True, slots=True)
class EvaluationCase:
    """Bounded matrices for a failed run followed by its repeated recovery run."""

    configuration: dict[str, object]
    first_passes: tuple[bool, ...]
    current_passes: tuple[bool, ...]


@st.composite
def _evaluation_cases(draw: st.DrawFn) -> EvaluationCase:
    """Generate same-configuration runs with blocking and non-blocking outcomes."""
    first_passes = list(
        draw(
            st.lists(
                st.booleans(),
                min_size=len(DEFAULT_NAMED_CHECKS),
                max_size=len(DEFAULT_NAMED_CHECKS),
            )
        )
    )
    blocking_indexes = tuple(
        index for index, check in enumerate(DEFAULT_NAMED_CHECKS) if check.blocking
    )
    first_passes[draw(st.sampled_from(blocking_indexes))] = False
    current_passes = tuple(
        True if check.blocking else passed
        for check, passed in zip(
            DEFAULT_NAMED_CHECKS,
            draw(
                st.lists(
                    st.booleans(),
                    min_size=len(DEFAULT_NAMED_CHECKS),
                    max_size=len(DEFAULT_NAMED_CHECKS),
                )
            ),
            strict=True,
        )
    )
    return EvaluationCase(
        configuration={
            "adapter_version": f"test-v{draw(st.integers(min_value=0, max_value=99))}",
            "suite": f"suite-{draw(st.integers(min_value=0, max_value=9_999))}",
        },
        first_passes=tuple(first_passes),
        current_passes=current_passes,
    )


def _outcome_matrix(passes: tuple[bool, ...]) -> dict[str, EvaluationOutcome]:
    """Map each named check to its deterministic pass/fail outcome."""
    return {
        check.name: EvaluationOutcome.PASS if passed else EvaluationOutcome.FAIL
        for check, passed in zip(DEFAULT_NAMED_CHECKS, passes, strict=True)
    }


def _executor(
    outcomes: Mapping[str, EvaluationOutcome],
) -> Callable[[GoldenTask, NamedEvaluationCheck], EvaluationOutcome]:
    """Return a local executor that applies the generated matrix to each task."""

    def execute(_: GoldenTask, check: NamedEvaluationCheck) -> EvaluationOutcome:
        return outcomes[check.name]

    return execute


def _assert_complete_matrix(
    run_results: tuple[EvaluationCellResult, ...],
    task_ids: tuple[str, ...],
    outcomes: Mapping[str, EvaluationOutcome],
) -> None:
    """Assert exactly one retained cell for every task and named check."""
    expected_cells = {
        (task_id, check.name) for task_id in task_ids for check in DEFAULT_NAMED_CHECKS
    }
    actual_cells = {(result.task_id, result.check_name) for result in run_results}
    assert actual_cells == expected_cells
    assert len(run_results) == len(expected_cells)
    assert all(result.outcome is outcomes[result.check_name] for result in run_results)


@settings(max_examples=100, deadline=None)
@given(case=_evaluation_cases())
def test_repeated_evaluations_preserve_identity_and_use_current_blocker_matrix(
    case: EvaluationCase,
) -> None:
    """A current all-blocking-pass execution unlocks transition after a retained failure."""
    repository = InMemoryEvaluationRepository()
    service = EvaluationService(repository, clock=lambda: _NOW)
    first_outcomes = _outcome_matrix(case.first_passes)
    current_outcomes = _outcome_matrix(case.current_passes)

    first = service.run_suite(
        _ORGANIZATION_ID,
        _FIRST_CORRELATION_ID,
        case.configuration,
        _executor(first_outcomes),
    )
    assert first.is_success and first.value is not None
    first_run = first.value
    _assert_complete_matrix(first_run.results, first_run.task_ids, first_outcomes)
    assert not first_run.transition_permitted
    assert not repository.current_transition_permitted()

    current = service.run_suite(
        _ORGANIZATION_ID,
        _SECOND_CORRELATION_ID,
        case.configuration,
        _executor(current_outcomes),
    )
    assert current.is_success and current.value is not None
    current_run = current.value
    _assert_complete_matrix(current_run.results, current_run.task_ids, current_outcomes)
    assert current_run.transition_permitted
    assert repository.current_transition_permitted()

    assert first_run.configuration_digest == current_run.configuration_digest
    assert first_run.evaluation_run_id != current_run.evaluation_run_id
    assert {result.result_id for result in first_run.results}.isdisjoint(
        result.result_id for result in current_run.results
    )
    assert repository.records() == (first_run, current_run)
