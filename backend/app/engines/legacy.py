"""Bounded, linear, Host-owned compatibility execution for legacy workflows."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, replace
from time import monotonic
from typing import Protocol, TypeVar

from app.engines.migration import (
    LegacyEngineRetirement,
    LegacyExecutionAvailability,
    LegacyExecutionLease,
)
from app.models.common import OptimisticTransition, RecordMetadata, utc_now
from app.models.contracts import ErrorCode, ErrorDetail, Result
from app.models.evidence import EvidenceReference
from app.models.identifiers import CorrelationId, OrganizationId, RunId
from app.models.runs import RunRecord, RunStatus, ToolEffect, WorkflowEngineKind
from app.repositories.protocols import RunRepository
from app.runs.failure_processing import FailureProcessor

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class LegacyStep:
    """One already-validated linear WorkflowDNA step."""

    step_id: str
    agent_id: str
    declared_tool_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class LegacyStepResult:
    """Safe completed effect evidence returned by a Host-owned step executor."""

    effects: tuple[ToolEffect, ...] = ()


class LegacyStepExecutor(Protocol):
    """Narrow executor seam; implementations must invoke tools through the Host broker."""

    def execute(self, run: RunRecord, step: LegacyStep) -> LegacyStepResult:
        """Run one step and return only completed, durable-effect candidates."""


class LegacyExecutionError(RuntimeError):
    """A safe execution failure with any completed-effect evidence that remains available."""

    def __init__(
        self,
        code: str,
        *,
        effects: tuple[ToolEffect, ...] = (),
        evidence_references: tuple[EvidenceReference, ...] = (),
    ) -> None:
        super().__init__(code)
        self.code = code
        self.effects = effects
        self.evidence_references = evidence_references


class AmbiguousEffectError(LegacyExecutionError):
    """Signal that a step may have produced an effect whose outcome is not certain."""

    def __init__(
        self,
        *,
        effects: tuple[ToolEffect, ...] = (),
        evidence_references: tuple[EvidenceReference, ...] = (),
    ) -> None:
        super().__init__(
            "ambiguous_effect",
            effects=effects,
            evidence_references=evidence_references,
        )


@dataclass(frozen=True, slots=True)
class LegacyExecutionOutcome:
    """The persisted terminal result of one bounded legacy execution attempt."""

    record: RunRecord
    completed: bool


@dataclass(frozen=True, slots=True)
class _ExecutionBudget:
    """Legacy limits extracted from a previously validated definition."""

    max_node_visits: int
    max_wall_clock_seconds: int
    max_tool_requests: int


class LegacyEngine:
    """Execute validated legacy DNA linearly without resuming ambiguous work."""

    def __init__(
        self,
        repository: RunRepository,
        step_executor: LegacyStepExecutor,
        failure_processor: FailureProcessor | None = None,
        monotonic_clock: Callable[[], float] = monotonic,
        legacy_execution_availability: LegacyExecutionAvailability | None = None,
    ) -> None:
        self._repository = repository
        self._step_executor = step_executor
        self._failure_processor = failure_processor or FailureProcessor(repository)
        self._monotonic_clock = monotonic_clock
        self._legacy_execution_availability = legacy_execution_availability

    def execute(
        self,
        organization_id: OrganizationId,
        run_id: RunId,
        definition: Mapping[str, object],
        correlation_id: CorrelationId,
    ) -> Result[LegacyExecutionOutcome, ErrorDetail]:
        """Execute one active legacy run once, terminalizing every failure safely."""
        current_result = self._repository.get_by_run_id(organization_id, run_id)
        if not current_result.is_success:
            return Result.failure(self._with_correlation(current_result.error, correlation_id))
        current = self._required_value(current_result)
        if current.engine is not WorkflowEngineKind.LEGACY:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.INVALID_TRANSITION,
                    "A non-legacy run cannot execute through LegacyEngine.",
                    correlation_id,
                )
            )
        if current.status is not RunStatus.DISPATCHING:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.INVALID_TRANSITION,
                    "LegacyEngine executes only an actively dispatched run once.",
                    correlation_id,
                )
            )
        lease: LegacyExecutionLease | None = None
        if self._legacy_execution_availability is not None:
            started = self._legacy_execution_availability.begin_legacy_execution(
                organization_id, run_id, correlation_id
            )
            if not started.is_success:
                return Result.failure(self._with_correlation(started.error, correlation_id))
            if started.value is None:
                raise RuntimeError("Legacy execution admission succeeded without a lease.")
            lease = started.value
        parsed = self._parse_definition(current, definition)
        if isinstance(parsed, ErrorDetail):
            return self._fail(
                current,
                parsed.message,
                (),
                self._candidate_step_ids(definition),
                correlation_id,
            )
        steps, budget = parsed
        if current.tool_effects:
            return self._fail(
                current,
                "legacy_resume_ambiguous",
                (),
                tuple(step.step_id for step in steps),
                correlation_id,
            )
        declared_tool_requests = sum(len(step.declared_tool_ids) for step in steps)
        if declared_tool_requests > budget.max_tool_requests:
            return self._fail(
                current,
                "legacy_tool_budget_exceeded",
                (),
                tuple(step.step_id for step in steps),
                correlation_id,
            )

        started_at = self._monotonic_clock()
        for index, step in enumerate(steps):
            retirement_evidence = self._retirement_evidence(lease)
            if retirement_evidence:
                return self._fail(
                    current,
                    "legacy_engine_retired",
                    (),
                    tuple(candidate.step_id for candidate in steps[index:]),
                    correlation_id,
                    retirement_evidence,
                )
            if index >= budget.max_node_visits:
                return self._fail(
                    current,
                    "legacy_node_budget_exceeded",
                    (),
                    tuple(candidate.step_id for candidate in steps[index:]),
                    correlation_id,
                )
            if self._monotonic_clock() - started_at > budget.max_wall_clock_seconds:
                return self._fail(
                    current,
                    "legacy_timeout",
                    (),
                    tuple(candidate.step_id for candidate in steps[index:]),
                    correlation_id,
                )
            try:
                result = self._step_executor.execute(current, step)
            except LegacyExecutionError as error:
                return self._fail(
                    current,
                    error.code,
                    error.effects,
                    tuple(candidate.step_id for candidate in steps[index + 1 :]),
                    correlation_id,
                    error.evidence_references,
                )
            except Exception:
                return self._fail(
                    current,
                    "legacy_step_failed",
                    (),
                    tuple(candidate.step_id for candidate in steps[index + 1 :]),
                    correlation_id,
                )
            retirement_evidence = self._retirement_evidence(lease)
            if retirement_evidence:
                return self._fail(
                    current,
                    "legacy_engine_retired",
                    result.effects,
                    tuple(candidate.step_id for candidate in steps[index + 1 :]),
                    correlation_id,
                    retirement_evidence,
                )
            validation_error = self._validate_effects(result.effects, step, budget)
            if validation_error is not None:
                return self._fail(
                    current,
                    validation_error,
                    result.effects,
                    tuple(candidate.step_id for candidate in steps[index + 1 :]),
                    correlation_id,
                )
            if result.effects:
                persisted = self._persist_effects(current, result.effects, correlation_id)
                if not persisted.is_success:
                    return self._fail(
                        current,
                        "legacy_effect_persistence_ambiguous",
                        result.effects,
                        tuple(candidate.step_id for candidate in steps[index + 1 :]),
                        correlation_id,
                    )
                current = self._required_value(persisted)
            if self._monotonic_clock() - started_at > budget.max_wall_clock_seconds:
                return self._fail(
                    current,
                    "legacy_timeout",
                    (),
                    tuple(candidate.step_id for candidate in steps[index + 1 :]),
                    correlation_id,
                )
        retirement_evidence = self._retirement_evidence(lease)
        if retirement_evidence:
            return self._fail(
                current,
                "legacy_engine_retired",
                (),
                (),
                correlation_id,
                retirement_evidence,
            )
        completed = self._complete(current, correlation_id)
        if not completed.is_success:
            return Result.failure(self._with_correlation(completed.error, correlation_id))
        terminal_record = self._required_value(completed)
        return Result.success(LegacyExecutionOutcome(terminal_record, completed=True))

    @staticmethod
    def _retirement_evidence(
        lease: LegacyExecutionLease | None,
    ) -> tuple[EvidenceReference, ...]:
        if lease is None or lease.retirement_evidence is None:
            return ()
        return (LegacyEngineRetirement.retirement_reference(lease.retirement_evidence),)

    def _fail(
        self,
        current: RunRecord,
        code: str,
        effects: Sequence[ToolEffect],
        unstarted_step_ids: Sequence[str],
        correlation_id: CorrelationId,
        evidence_references: Sequence[EvidenceReference] = (),
    ) -> Result[LegacyExecutionOutcome, ErrorDetail]:
        """Use durable failure processing rather than retrying any failed or ambiguous step."""
        failed = self._failure_processor.process(
            current,
            code=code,
            completed_effects=effects,
            evidence_references=evidence_references,
            unstarted_step_ids=unstarted_step_ids,
            correlation_id=correlation_id,
        )
        if not failed.is_success:
            return Result.failure(self._with_correlation(failed.error, correlation_id))
        return Result.success(
            LegacyExecutionOutcome(self._required_value(failed).record, completed=False)
        )

    def _persist_effects(
        self,
        current: RunRecord,
        effects: Sequence[ToolEffect],
        correlation_id: CorrelationId,
    ) -> Result[RunRecord, ErrorDetail]:
        """Append completed effects before this engine is permitted to start another step."""
        updated = replace(
            current,
            metadata=self._next_metadata(current, correlation_id),
            tool_effects=tuple(dict.fromkeys((*current.tool_effects, *effects))),
        )
        persisted = self._repository.transition(
            updated, self._transition_for(current, correlation_id)
        )
        if not persisted.is_success:
            return Result.failure(self._with_correlation(persisted.error, correlation_id))
        return persisted

    def _complete(
        self, current: RunRecord, correlation_id: CorrelationId
    ) -> Result[RunRecord, ErrorDetail]:
        """Terminally complete an uninterrupted run without changing its retained effects."""
        completed = replace(
            current,
            metadata=self._next_metadata(current, correlation_id),
            status=RunStatus.COMPLETED,
        )
        persisted = self._repository.transition(
            completed, self._transition_for(current, correlation_id)
        )
        if not persisted.is_success:
            return Result.failure(self._with_correlation(persisted.error, correlation_id))
        return persisted

    def _parse_definition(
        self,
        run: RunRecord,
        definition: Mapping[str, object],
    ) -> tuple[tuple[LegacyStep, ...], _ExecutionBudget] | ErrorDetail:
        """Defensively bind raw DNA to its queued record before executing a step."""
        if (
            definition.get("definition_type") != "workflow_dna"
            or definition.get("engine") != WorkflowEngineKind.LEGACY.value
            or definition.get("id") != run.workflow_definition_id
            or definition.get("version") != run.workflow_definition_version
            or self._definition_digest(definition) != run.workflow_definition_digest
        ):
            return self._definition_error(run)
        raw_budget = definition.get("execution_budget")
        if not isinstance(raw_budget, Mapping):
            return self._definition_error(run)
        max_node_visits = raw_budget.get("max_node_visits")
        max_wall_clock_seconds = raw_budget.get("max_wall_clock_seconds")
        max_tool_requests = raw_budget.get("max_tool_requests")
        if (
            not isinstance(max_node_visits, int)
            or isinstance(max_node_visits, bool)
            or not isinstance(max_wall_clock_seconds, int)
            or isinstance(max_wall_clock_seconds, bool)
            or not isinstance(max_tool_requests, int)
            or isinstance(max_tool_requests, bool)
        ):
            return self._definition_error(run)
        if not (
            1 <= max_node_visits <= 100
            and 1 <= max_wall_clock_seconds <= 900
            and 0 <= max_tool_requests <= 50
        ):
            return self._definition_error(run)
        raw_steps = definition.get("steps")
        if not isinstance(raw_steps, list) or not 1 <= len(raw_steps) <= 100:
            return self._definition_error(run)
        steps: list[LegacyStep] = []
        for raw_step in raw_steps:
            if not isinstance(raw_step, Mapping):
                return self._definition_error(run)
            step_id = raw_step.get("id")
            agent_id = raw_step.get("agent_id")
            tool_ids = raw_step.get("tool_ids")
            if (
                not isinstance(step_id, str)
                or not step_id
                or not isinstance(agent_id, str)
                or not agent_id
                or not isinstance(tool_ids, list)
                or not all(isinstance(tool_id, str) and tool_id for tool_id in tool_ids)
                or len(tool_ids) != len(set(tool_ids))
            ):
                return self._definition_error(run)
            steps.append(LegacyStep(step_id, agent_id, tuple(tool_ids)))
        if len({step.step_id for step in steps}) != len(steps):
            return self._definition_error(run)
        return tuple(steps), _ExecutionBudget(
            max_node_visits=max_node_visits,
            max_wall_clock_seconds=max_wall_clock_seconds,
            max_tool_requests=max_tool_requests,
        )

    @staticmethod
    def _validate_effects(
        effects: object,
        step: LegacyStep,
        budget: _ExecutionBudget,
    ) -> str | None:
        if not isinstance(effects, tuple) or not all(
            isinstance(effect, ToolEffect) for effect in effects
        ):
            return "legacy_step_result_invalid"
        if len(effects) > len(step.declared_tool_ids):
            return "legacy_undeclared_tool_effect"
        if any(effect.adapter_id not in step.declared_tool_ids for effect in effects):
            return "legacy_undeclared_tool_effect"
        if len(effects) > budget.max_tool_requests:
            return "legacy_tool_budget_exceeded"
        return None

    @staticmethod
    def _candidate_step_ids(definition: Mapping[str, object]) -> tuple[str, ...]:
        raw_steps = definition.get("steps")
        if not isinstance(raw_steps, list):
            return ()
        return tuple(
            step_id
            for raw_step in raw_steps
            if isinstance(raw_step, Mapping)
            and isinstance((step_id := raw_step.get("id")), str)
            and step_id
        )

    @staticmethod
    def _definition_digest(definition: Mapping[str, object]) -> str:
        try:
            normalized = json.dumps(dict(definition), sort_keys=True, separators=(",", ":"))
        except (TypeError, ValueError):
            return ""
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    @staticmethod
    def _definition_error(run: RunRecord) -> ErrorDetail:
        return ErrorDetail(
            ErrorCode.VALIDATION_FAILED,
            "invalid_legacy_definition",
            run.metadata.correlation_id,
        )

    def _next_metadata(
        self, record: RunRecord, correlation_id: CorrelationId
    ) -> RecordMetadata:
        return replace(
            record.metadata,
            correlation_id=correlation_id,
            version=record.metadata.version + 1,
            updated_at=utc_now(),
        )

    @staticmethod
    def _transition_for(
        record: RunRecord, correlation_id: CorrelationId
    ) -> OptimisticTransition:
        return OptimisticTransition(
            record_id=record.metadata.record_id,
            organization_id=record.metadata.organization_id,
            expected_version=record.metadata.version,
            correlation_id=correlation_id,
        )

    @staticmethod
    def _with_correlation(
        error: ErrorDetail | None, correlation_id: CorrelationId
    ) -> ErrorDetail:
        if error is None:
            return ErrorDetail(
                ErrorCode.REPOSITORY_UNAVAILABLE,
                "Run storage is unavailable during legacy execution.",
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
    def _required_value(result: Result[T, ErrorDetail]) -> T:
        if result.value is None:
            raise RuntimeError("A successful result did not contain its expected value.")
        return result.value
