"""Lock-protected local retention for immutable evaluation executions."""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from threading import RLock

from app.evaluation.models import EvaluationCellResult, EvaluationRun
from app.models.common import OptimisticTransition, RecordMetadata
from app.models.contracts import ErrorCode, ErrorDetail, RepositoryError, Result
from app.models.identifiers import CorrelationId, EvaluationRunId, OrganizationId, RecordId


class InMemoryEvaluationRepository:
    """Atomically records evaluation cells and the current guarded-transition state."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._runs: dict[EvaluationRunId, EvaluationRun] = {}
        self._record_ids: dict[RecordId, EvaluationRunId] = {}
        self._current_run_id: EvaluationRunId | None = None
        self._current_transition_permitted = False

    def create(self, record: EvaluationRun) -> Result[EvaluationRun, RepositoryError]:
        """Retain a new, distinct suite execution before recording its cells."""
        with self._lock:
            if (
                record.evaluation_run_id in self._runs
                or record.metadata.record_id in self._record_ids
            ):
                return Result.failure(
                    self._error(
                        ErrorCode.CONFLICT,
                        "Evaluation run already exists.",
                    )
                )
            self._runs[record.evaluation_run_id] = record
            self._record_ids[record.metadata.record_id] = record.evaluation_run_id
            self._current_run_id = record.evaluation_run_id
            self._current_transition_permitted = False
            return Result.success(record)

    def get(
        self, organization_id: OrganizationId, record_id: RecordId
    ) -> Result[EvaluationRun, RepositoryError]:
        """Return one evaluation execution only in its owning organization."""
        with self._lock:
            run_id = self._record_ids.get(record_id)
            run = self._runs.get(run_id) if run_id is not None else None
            return self._scoped_record(organization_id, run)

    def transition(
        self, record: EvaluationRun, transition: OptimisticTransition
    ) -> Result[EvaluationRun, RepositoryError]:
        """Provide the standard versioned-repository compare-and-swap seam."""
        with self._lock:
            current = self._runs.get(record.evaluation_run_id)
            if not self._matches_transition(current, record, transition):
                return Result.failure(
                    self._error(
                        ErrorCode.CONFLICT,
                        "Evaluation transition conflicts.",
                    )
                )
            self._runs[record.evaluation_run_id] = record
            if self._current_run_id == record.evaluation_run_id:
                self._current_transition_permitted = (
                    record.completed and record.transition_permitted
                )
            return Result.success(record)


    def append_result(
        self,
        organization_id: OrganizationId,
        evaluation_run_id: EvaluationRunId,
        result: EvaluationCellResult,
        correlation_id: CorrelationId,
    ) -> Result[EvaluationRun, RepositoryError]:
        """Atomically retain one task/check result and latch any current failure."""
        with self._lock:
            current = self._runs.get(evaluation_run_id)
            if current is None or current.metadata.organization_id != organization_id:
                return Result.failure(
                    self._error(ErrorCode.NOT_FOUND, "Evaluation run was not found.")
                )
            if current.completed:
                return Result.failure(
                    self._error(ErrorCode.INVALID_TRANSITION, "Evaluation run is already complete.")
                )
            cell_key = (result.task_id, result.check_name)
            if any((item.task_id, item.check_name) == cell_key for item in current.results):
                return Result.failure(
                    self._error(ErrorCode.CONFLICT, "Evaluation task/check result already exists.")
                )
            updated = replace(
                current,
                metadata=self._next_metadata(current.metadata, correlation_id, result.recorded_at),
                results=(*current.results, result),
                transition_permitted=False,
            )
            self._runs[evaluation_run_id] = updated
            if self._current_run_id == evaluation_run_id:
                # This assignment occurs under the same lock as result retention.
                self._current_transition_permitted = False
            return Result.success(updated)

    def complete(
        self,
        organization_id: OrganizationId,
        evaluation_run_id: EvaluationRunId,
        correlation_id: CorrelationId,
        completed_at: datetime,
    ) -> Result[EvaluationRun, RepositoryError]:
        """Complete only a full matrix and atomically publish its current gate result."""
        with self._lock:
            current = self._runs.get(evaluation_run_id)
            if current is None or current.metadata.organization_id != organization_id:
                return Result.failure(
                    self._error(ErrorCode.NOT_FOUND, "Evaluation run was not found.")
                )
            if current.completed:
                return Result.failure(
                    self._error(ErrorCode.INVALID_TRANSITION, "Evaluation run is already complete.")
                )
            expected_cells = {
                (task_id, check.name) for task_id in current.task_ids for check in current.checks
            }
            actual_cells = {(result.task_id, result.check_name) for result in current.results}
            if actual_cells != expected_cells:
                return Result.failure(
                    self._error(ErrorCode.VALIDATION_FAILED, "Evaluation matrix is incomplete.")
                )
            transition_permitted = all(
                not result.blocking or result.outcome.value == "pass"
                for result in current.results
            )
            updated = replace(
                current,
                metadata=self._next_metadata(current.metadata, correlation_id, completed_at),
                completed=True,
                transition_permitted=transition_permitted,
            )
            self._runs[evaluation_run_id] = updated
            if self._current_run_id == evaluation_run_id:
                self._current_transition_permitted = transition_permitted
            return Result.success(updated)

    def current_transition_permitted(self) -> bool:
        """Return the lock-protected gate for the latest completed evaluation execution."""
        with self._lock:
            return self._current_transition_permitted

    def records(self) -> tuple[EvaluationRun, ...]:
        """Return immutable execution snapshots for deterministic inspection."""
        with self._lock:
            return tuple(self._runs.values())

    @staticmethod
    def _next_metadata(
        metadata: RecordMetadata, correlation_id: CorrelationId, updated_at: datetime
    ) -> RecordMetadata:
        return replace(
            metadata,
            correlation_id=correlation_id,
            version=metadata.version + 1,
            updated_at=updated_at,
        )

    @staticmethod
    def _matches_transition(
        current: EvaluationRun | None,
        record: EvaluationRun,
        transition: OptimisticTransition,
    ) -> bool:
        return (
            current is not None
            and current.metadata.record_id == transition.record_id
            and current.metadata.organization_id == transition.organization_id
            and current.metadata.version == transition.expected_version
            and record.metadata.record_id == transition.record_id
            and record.metadata.organization_id == transition.organization_id
            and record.metadata.version == transition.expected_version + 1
        )

    def _scoped_record(
        self, organization_id: OrganizationId, record: EvaluationRun | None
    ) -> Result[EvaluationRun, RepositoryError]:
        if record is None or record.metadata.organization_id != organization_id:
            return Result.failure(self._error(ErrorCode.NOT_FOUND, "Evaluation run was not found."))
        return Result.success(record)

    @staticmethod
    def _error(code: ErrorCode, message: str) -> ErrorDetail:
        return ErrorDetail(code, message, CorrelationId("evaluation-repository"))
