"""Durable, evidence-complete terminal failure processing for workflow runs."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass, replace
from datetime import datetime

from app.models.common import OptimisticTransition, RecordMetadata, utc_now
from app.models.contracts import ErrorCode, ErrorDetail, Result
from app.models.evidence import EvidenceReference
from app.models.identifiers import CorrelationId
from app.models.runs import FailureState, RunRecord, RunStatus, ToolEffect
from app.repositories.protocols import RunRepository


@dataclass(frozen=True, slots=True)
class FailureProcessingOutcome:
    """A terminal run record after durable failure obligations are processed."""

    record: RunRecord
    was_already_processed: bool = False


class FailureProcessor:
    """Persist failure evidence before declaring failure processing complete."""

    def __init__(
        self,
        repository: RunRepository,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._repository = repository
        self._clock = clock

    def process(
        self,
        run: RunRecord,
        *,
        code: str,
        evidence_references: Iterable[EvidenceReference] = (),
        completed_effects: Iterable[ToolEffect] = (),
        unstarted_step_ids: Iterable[str] = (),
        correlation_id: CorrelationId,
    ) -> Result[FailureProcessingOutcome, ErrorDetail]:
        """Fail a run, retain all available evidence, then mark processing complete.

        The first durable transition always has ``failure_processing_complete=False``.
        Therefore a storage failure after that transition leaves an operator-visible failed
        record that cannot be confused with a fully processed failure.
        """
        if not code.strip():
            return Result.failure(
                ErrorDetail(
                    ErrorCode.VALIDATION_FAILED,
                    "Failure processing requires a non-empty safe failure code.",
                    correlation_id,
                )
            )
        current_result = self._repository.get_by_run_id(
            run.metadata.organization_id, run.run_id
        )
        if not current_result.is_success:
            return Result.failure(self._with_correlation(current_result.error, correlation_id))
        current = self._required_value(current_result)
        if current.status is RunStatus.FAILED:
            if current.failure is None:
                return Result.failure(
                    ErrorDetail(
                        ErrorCode.CONFLICT,
                        "Failed runs must retain a failure state before processing can continue.",
                        correlation_id,
                    )
                )
            if current.failure.failure_processing_complete:
                return Result.success(FailureProcessingOutcome(current, was_already_processed=True))
            return self._complete(current, correlation_id)
        if current.status not in {RunStatus.DISPATCHING, RunStatus.WAITING_FOR_APPROVAL}:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.INVALID_TRANSITION,
                    "Only active runs may enter terminal failure processing.",
                    correlation_id,
                )
            )

        failure = FailureState(
            code=code,
            evidence_references=self._unique(evidence_references),
            stopped_step_ids=self._unique_nonempty(unstarted_step_ids),
            failure_processing_complete=False,
        )
        failed = replace(
            current,
            metadata=self._next_metadata(current, correlation_id),
            status=RunStatus.FAILED,
            tool_effects=self._merge_effects(current.tool_effects, completed_effects),
            failure=failure,
        )
        persisted = self._repository.transition(
            failed, self._transition_for(current, correlation_id)
        )
        if not persisted.is_success:
            return Result.failure(self._with_correlation(persisted.error, correlation_id))
        return self._complete(failed, correlation_id)

    def _complete(
        self,
        failed: RunRecord,
        correlation_id: CorrelationId,
    ) -> Result[FailureProcessingOutcome, ErrorDetail]:
        """Complete the final failure obligation only from a durably failed record."""
        if failed.failure is None:
            raise RuntimeError("Failure processing cannot complete a run without failure evidence.")
        complete_failure = replace(failed.failure, failure_processing_complete=True)
        completed = replace(
            failed,
            metadata=self._next_metadata(failed, correlation_id),
            failure=complete_failure,
        )
        persisted = self._repository.transition(
            completed, self._transition_for(failed, correlation_id)
        )
        if not persisted.is_success:
            return Result.failure(self._with_correlation(persisted.error, correlation_id))
        return Result.success(FailureProcessingOutcome(completed))

    def _next_metadata(self, record: RunRecord, correlation_id: CorrelationId) -> RecordMetadata:
        return replace(
            record.metadata,
            correlation_id=correlation_id,
            version=record.metadata.version + 1,
            updated_at=self._clock(),
        )

    @staticmethod
    def _transition_for(record: RunRecord, correlation_id: CorrelationId) -> OptimisticTransition:
        return OptimisticTransition(
            record_id=record.metadata.record_id,
            organization_id=record.metadata.organization_id,
            expected_version=record.metadata.version,
            correlation_id=correlation_id,
        )

    @staticmethod
    def _unique(values: Iterable[EvidenceReference]) -> tuple[EvidenceReference, ...]:
        return tuple(dict.fromkeys(values))

    @staticmethod
    def _unique_nonempty(values: Iterable[str]) -> tuple[str, ...]:
        return tuple(dict.fromkeys(value for value in values if value.strip()))

    @staticmethod
    def _merge_effects(
        existing: tuple[ToolEffect, ...],
        additional: Iterable[ToolEffect],
    ) -> tuple[ToolEffect, ...]:
        return tuple(dict.fromkeys((*existing, *additional)))

    @staticmethod
    def _with_correlation(
        error: ErrorDetail | None, correlation_id: CorrelationId
    ) -> ErrorDetail:
        if error is None:
            return ErrorDetail(
                ErrorCode.REPOSITORY_UNAVAILABLE,
                "Run storage is unavailable during failure processing.",
                correlation_id,
            )
        return replace(error, correlation_id=correlation_id)

    @staticmethod
    def _required_value(result: Result[RunRecord, ErrorDetail]) -> RunRecord:
        if result.value is None:
            raise RuntimeError("A successful run repository result did not contain a run record.")
        return result.value
