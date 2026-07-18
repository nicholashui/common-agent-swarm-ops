"""Deterministic evaluation-suite execution with retained current-run gating."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable, Mapping
from datetime import datetime

from app.evaluation.golden_tasks import GoldenTaskLoader
from app.evaluation.models import (
    DEFAULT_NAMED_CHECKS,
    EvaluationCellResult,
    EvaluationOutcome,
    EvaluationRun,
    GoldenTask,
    NamedEvaluationCheck,
)
from app.models.common import SCHEMA_VERSION, RecordMetadata, utc_now
from app.models.contracts import ErrorCode, ErrorDetail, Result
from app.models.identifiers import (
    CorrelationId,
    EvaluationResultId,
    EvaluationRunId,
    OrganizationId,
    new_record_id,
)
from app.repositories.evaluation_repository import InMemoryEvaluationRepository

EvaluationExecutor = Callable[[GoldenTask, NamedEvaluationCheck], EvaluationOutcome]


class EvaluationService:
    """Run every named deterministic check for every retained golden task."""

    def __init__(
        self,
        repository: InMemoryEvaluationRepository,
        loader: GoldenTaskLoader | None = None,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._repository = repository
        self._loader = loader if loader is not None else GoldenTaskLoader()
        self._clock = clock

    def run_suite(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        configuration: Mapping[str, object],
        executor: EvaluationExecutor | None = None,
    ) -> Result[EvaluationRun, ErrorDetail]:
        """Retain every task/check result while evaluating all non-blocking cells."""
        try:
            tasks = self._loader.load()
            configuration_digest = self._configuration_digest(configuration)
        except ValueError as error:
            return Result.failure(
                ErrorDetail(ErrorCode.VALIDATION_FAILED, str(error), correlation_id)
            )
        run = self._new_run(organization_id, correlation_id, tasks, configuration_digest)
        started = self._repository.create(run)
        if not started.is_success:
            return Result.failure(self._repository_error(started.error, correlation_id))
        evaluator = executor if executor is not None else self._default_executor
        for task in tasks:
            for check in DEFAULT_NAMED_CHECKS:
                result = self._new_result(task, check, evaluator(task, check))
                recorded = self._repository.append_result(
                    organization_id, run.evaluation_run_id, result, correlation_id
                )
                if not recorded.is_success:
                    return Result.failure(self._repository_error(recorded.error, correlation_id))
                run = self._require_value(recorded)
        completed = self._repository.complete(
            organization_id, run.evaluation_run_id, correlation_id, self._clock()
        )
        if not completed.is_success:
            return Result.failure(self._repository_error(completed.error, correlation_id))
        return Result.success(self._require_value(completed))

    def _new_run(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        tasks: tuple[GoldenTask, ...],
        configuration_digest: str,
    ) -> EvaluationRun:
        timestamp = self._clock()
        return EvaluationRun(
            metadata=RecordMetadata(
                record_id=new_record_id(),
                organization_id=organization_id,
                correlation_id=correlation_id,
                schema_version=SCHEMA_VERSION,
                version=1,
                created_at=timestamp,
                updated_at=timestamp,
            ),
            evaluation_run_id=EvaluationRunId(str(new_record_id())),
            configuration_digest=configuration_digest,
            task_ids=tuple(task.task_id for task in tasks),
            checks=DEFAULT_NAMED_CHECKS,
            results=(),
            completed=False,
            transition_permitted=False,
        )

    def _new_result(
        self,
        task: GoldenTask,
        check: NamedEvaluationCheck,
        outcome: EvaluationOutcome,
    ) -> EvaluationCellResult:
        timestamp = self._clock()
        digest_source = f"{task.task_id}:{check.name}:{outcome.value}"
        return EvaluationCellResult(
            result_id=EvaluationResultId(str(new_record_id())),
            task_id=task.task_id,
            check_name=check.name,
            check_kind=check.kind,
            blocking=check.blocking,
            outcome=outcome,
            recorded_at=timestamp,
            evidence_digest=hashlib.sha256(digest_source.encode("utf-8")).hexdigest(),
        )

    @staticmethod
    def _default_executor(task: GoldenTask, _: NamedEvaluationCheck) -> EvaluationOutcome:
        """Use fixture-owned expected outcomes without any network or provider call."""
        return task.expected_outcome

    @staticmethod
    def _configuration_digest(configuration: Mapping[str, object]) -> str:
        try:
            canonical = json.dumps(
                configuration, sort_keys=True, separators=(",", ":"), ensure_ascii=True
            )
        except (TypeError, ValueError) as error:
            raise ValueError("Evaluation configuration must be JSON serializable.") from error
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    @staticmethod
    def _repository_error(error: ErrorDetail | None, correlation_id: CorrelationId) -> ErrorDetail:
        if error is None:
            return ErrorDetail(
                ErrorCode.REPOSITORY_UNAVAILABLE,
                "Evaluation storage failed.",
                correlation_id,
            )
        return ErrorDetail(
            error.code,
            error.message,
            correlation_id,
            retryable=error.retryable,
            fields=error.fields,
        )

    @staticmethod
    def _require_value(result: Result[EvaluationRun, ErrorDetail]) -> EvaluationRun:
        if result.value is None:
            raise RuntimeError("Successful evaluation repository result had no value.")
        return result.value
