"""Focused deterministic examples for the retained local evaluation suite."""

from __future__ import annotations

from datetime import UTC, datetime

from app.evaluation.golden_tasks import GoldenTaskLoader
from app.evaluation.models import EvaluationCheckKind, EvaluationOutcome
from app.evaluation.service import EvaluationService
from app.models.identifiers import CorrelationId, OrganizationId
from app.repositories.evaluation_repository import InMemoryEvaluationRepository

NOW = datetime(2025, 1, 1, tzinfo=UTC)
ORGANIZATION_ID = OrganizationId("org-evaluation")
CORRELATION_ID = CorrelationId("evaluation-correlation")


def test_golden_task_loader_retains_at_least_twenty_deterministic_tasks() -> None:
    """The committed local corpus has unique, sorted JSON task identities."""
    tasks = GoldenTaskLoader().load()

    assert len(tasks) >= 20
    assert tuple(task.task_id for task in tasks) == tuple(sorted(task.task_id for task in tasks))
    assert len({task.task_id for task in tasks}) == len(tasks)
    assert all(task.expected_outcome is EvaluationOutcome.PASS for task in tasks)


def test_repeated_identical_execution_retains_distinct_full_named_result_matrices() -> None:
    """Repeated task/configuration inputs never overwrite earlier suite evidence."""
    repository = InMemoryEvaluationRepository()
    service = EvaluationService(repository, clock=lambda: NOW)
    configuration = {"adapter_version": "1.0.0", "suite": "baseline"}

    first = service.run_suite(ORGANIZATION_ID, CORRELATION_ID, configuration)
    second = service.run_suite(ORGANIZATION_ID, CORRELATION_ID, configuration)

    assert first.is_success and second.is_success
    assert first.value is not None and second.value is not None
    assert first.value.evaluation_run_id != second.value.evaluation_run_id
    assert first.value.configuration_digest == second.value.configuration_digest
    assert len(first.value.results) == len(first.value.task_ids) * len(first.value.checks)
    assert len(second.value.results) == len(second.value.task_ids) * len(second.value.checks)
    assert {result.result_id for result in first.value.results}.isdisjoint(
        result.result_id for result in second.value.results
    )
    assert {result.check_kind for result in first.value.results} == set(EvaluationCheckKind)
    assert first.value.transition_permitted
    assert second.value.transition_permitted
    assert repository.current_transition_permitted()
    assert len(repository.records()) == 2


def test_current_blocking_failure_latches_transition_while_nonblocking_checks_complete() -> None:
    """A current blocker is retained immediately and does not stop non-blocking checks."""
    repository = InMemoryEvaluationRepository()
    service = EvaluationService(repository, clock=lambda: NOW)

    def fail_one_blocker(task_id: str, check_kind: EvaluationCheckKind) -> EvaluationOutcome:
        if task_id == "golden-001" and check_kind is EvaluationCheckKind.REGRESSION:
            return EvaluationOutcome.FAIL
        return EvaluationOutcome.PASS

    failed = service.run_suite(
        ORGANIZATION_ID,
        CORRELATION_ID,
        {"suite": "failure-case"},
        lambda task, check: fail_one_blocker(task.task_id, check.kind),
    )

    assert failed.is_success and failed.value is not None
    assert failed.value.completed
    assert not failed.value.transition_permitted
    assert not repository.current_transition_permitted()
    assert len(failed.value.results) == len(failed.value.task_ids) * len(failed.value.checks)
    assert any(
        result.task_id == "golden-001"
        and result.check_kind is EvaluationCheckKind.REGRESSION
        and result.outcome is EvaluationOutcome.FAIL
        for result in failed.value.results
    )
    assert all(
        result.outcome is EvaluationOutcome.PASS
        for result in failed.value.results
        if not result.blocking
    )

    passing = service.run_suite(ORGANIZATION_ID, CORRELATION_ID, {"suite": "recovery-case"})

    assert passing.is_success and passing.value is not None
    assert passing.value.transition_permitted
    assert repository.current_transition_permitted()
    assert len(repository.records()) == 2
