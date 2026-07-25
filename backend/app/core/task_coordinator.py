"""Durable Agent_Task coordination over validated graph revisions."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, replace
from datetime import datetime
from itertools import count

from app.models.common import SCHEMA_VERSION, RecordMetadata, utc_now
from app.models.contracts import ErrorCode, ErrorDetail, Result
from app.models.control_plane import (
    AgentTask,
    AgentVersionId,
    ApprovalGateId,
    ApprovalGateStatus,
    AuditRecord,
    DeliveryState,
    EventId,
    GraphRevision,
    GraphRevisionId,
    OperationalEvent,
    OutboxId,
    OutboxRecord,
    RunProvenance,
    RunProvenanceId,
    TaskId,
    TaskLifecycle,
    TaskTransition,
)
from app.models.identifiers import CorrelationId, OrganizationId, new_record_id
from app.repositories.control_plane import ControlPlaneUnitOfWork
from app.repositories.graph_repository import GraphRepository


@dataclass(frozen=True, slots=True)
class TaskPublication:
    """Committed task event and delivery row ready for post-commit publication."""

    event: OperationalEvent
    outbox: OutboxRecord


@dataclass(frozen=True, slots=True)
class TaskTransitionCommand:
    """A server-validated lifecycle transition for one versioned task."""

    to_state: TaskLifecycle | str
    reason_code: str
    failure_reason: str | None = None


@dataclass(frozen=True, slots=True)
class TaskTransitionOutcome:
    """A task state outcome and its committed transition publications."""

    task: AgentTask
    publications: tuple[TaskPublication, ...]


@dataclass(frozen=True, slots=True)
class TaskPreparationOutcome:
    """All planned tasks and automatic prerequisite-queue transition publications."""

    tasks: tuple[AgentTask, ...]
    publications: tuple[TaskPublication, ...]


PublicationCallback = Callable[[TaskPublication], None]
UnitOfWorkFactory = Callable[[], ControlPlaneUnitOfWork]


@dataclass(frozen=True, slots=True)
class _TaskPlan:
    task_id: TaskId
    pinned_agent_version_id: AgentVersionId
    dependencies: tuple[TaskId, ...]
    constraints: Mapping[str, object]
    approval_gate_ids: tuple[ApprovalGateId, ...]
    checkpoint_reference: str | None


class TaskCoordinator:
    """Coordinate task lifecycle projections without owning execution or dispatch."""

    _ALLOWED_TRANSITIONS: Mapping[TaskLifecycle, frozenset[TaskLifecycle]] = {
        TaskLifecycle.IDLE: frozenset({TaskLifecycle.QUEUED, TaskLifecycle.BLOCKED}),
        TaskLifecycle.QUEUED: frozenset({TaskLifecycle.RUNNING, TaskLifecycle.BLOCKED}),
        TaskLifecycle.RUNNING: frozenset(
            {
                TaskLifecycle.SELF_REFINE,
                TaskLifecycle.WAITING_FOR_CRITIQUE,
                TaskLifecycle.BLOCKED,
                TaskLifecycle.FAILED,
                TaskLifecycle.COMPLETE,
            }
        ),
        TaskLifecycle.SELF_REFINE: frozenset(
            {TaskLifecycle.RUNNING, TaskLifecycle.BLOCKED, TaskLifecycle.FAILED}
        ),
        TaskLifecycle.WAITING_FOR_CRITIQUE: frozenset(
            {TaskLifecycle.RUNNING, TaskLifecycle.BLOCKED, TaskLifecycle.FAILED}
        ),
        TaskLifecycle.BLOCKED: frozenset({TaskLifecycle.IDLE}),
        TaskLifecycle.FAILED: frozenset(),
        TaskLifecycle.COMPLETE: frozenset(),
    }

    def __init__(
        self,
        graph_repository: GraphRepository,
        unit_of_work_factory: UnitOfWorkFactory,
        *,
        clock: Callable[[], datetime] = utc_now,
        next_event_sequence: Callable[[], int] | None = None,
    ) -> None:
        self._graph_repository = graph_repository
        self._unit_of_work_factory = unit_of_work_factory
        self._clock = clock
        sequence = count(1)
        self._next_event_sequence = next_event_sequence or (lambda: next(sequence))

    def prepare_tasks(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        graph_revision_id: GraphRevisionId,
        run_reference: str,
        *,
        publish: PublicationCallback | None = None,
    ) -> Result[TaskPreparationOutcome, ErrorDetail]:
        """Create pinned tasks only from a graph with retained successful validation."""
        if not run_reference.strip():
            return Result.failure(self._validation(correlation_id, "Run reference is required."))
        revision_result = self._graph_repository.get_revision(organization_id, graph_revision_id)
        validation_result = self._graph_repository.latest_validation(
            organization_id, graph_revision_id
        )
        revision = revision_result.value
        validation = validation_result.value
        if (
            not revision_result.is_success
            or revision is None
            or not validation_result.is_success
            or validation is None
            or not validation.eligible_for_run
        ):
            return Result.failure(
                self._validation(
                    correlation_id,
                    "A successfully validated graph revision is required before task preparation.",
                )
            )
        plans_result = self._plans_from_revision(
            revision, validation.agent_version_ids, run_reference
        )
        if not plans_result.is_success or plans_result.value is None:
            return Result.failure(
                plans_result.error or self._validation(correlation_id, "Task plan is invalid.")
            )
        plans = plans_result.value
        now = self._clock()
        with self._unit_of_work_factory() as unit_of_work:
            tasks = tuple(
                AgentTask(
                    metadata=self._metadata(organization_id, correlation_id, now),
                    task_id=plan.task_id,
                    run_reference=run_reference,
                    pinned_agent_version_id=plan.pinned_agent_version_id,
                    dependencies=plan.dependencies,
                    constraints=plan.constraints,
                    approval_gate_ids=tuple(plan.approval_gate_ids),
                    checkpoint_reference=plan.checkpoint_reference,
                    state=TaskLifecycle.IDLE,
                )
                for plan in plans
            )
            for task in tasks:
                created = unit_of_work.tasks.create(task)
                if not created.is_success:
                    unit_of_work.rollback()
                    return Result.failure(self._repository_error(created.error, correlation_id))
            queued = self._queue_satisfied_in_unit_of_work(
                unit_of_work, organization_id, correlation_id, run_reference
            )
            if not queued.is_success or queued.value is None:
                unit_of_work.rollback()
                return Result.failure(queued.error or self._repository_error(None, correlation_id))
            prepared_tasks = unit_of_work.tasks.for_run(organization_id, run_reference)
            if not prepared_tasks.is_success or prepared_tasks.value is None:
                unit_of_work.rollback()
                return Result.failure(self._repository_error(prepared_tasks.error, correlation_id))
            outcome = TaskPreparationOutcome(prepared_tasks.value, queued.value)
        self._publish(outcome.publications, publish)
        return Result.success(outcome)

    def queue_satisfied(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        run_reference: str,
        *,
        publish: PublicationCallback | None = None,
    ) -> Result[tuple[TaskPublication, ...], ErrorDetail]:
        """Queue every nonterminal task whose dependencies and approval gates are satisfied."""
        with self._unit_of_work_factory() as unit_of_work:
            queued = self._queue_satisfied_in_unit_of_work(
                unit_of_work, organization_id, correlation_id, run_reference
            )
            if not queued.is_success or queued.value is None:
                unit_of_work.rollback()
                return Result.failure(queued.error or self._repository_error(None, correlation_id))
        self._publish(queued.value, publish)
        return queued

    def transition(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        task_id: TaskId,
        expected_task_version: int,
        command: TaskTransitionCommand,
        *,
        publish: PublicationCallback | None = None,
    ) -> Result[TaskTransitionOutcome, ErrorDetail]:
        """Apply one compare-and-swap task transition and retain its audit/outbox evidence."""
        if expected_task_version < 1:
            return Result.failure(
                self._validation(correlation_id, "Expected task version must be positive.")
            )
        requested_state = command.to_state
        if not isinstance(requested_state, TaskLifecycle):
            return Result.failure(
                self._validation(correlation_id, "Task lifecycle state is invalid.")
            )
        with self._unit_of_work_factory() as unit_of_work:
            current_result = unit_of_work.tasks.get(organization_id, task_id)
            current = current_result.value
            if not current_result.is_success or current is None:
                return Result.failure(self._repository_error(current_result.error, correlation_id))
            issue = self._transition_issue(
                unit_of_work,
                organization_id,
                correlation_id,
                current,
                expected_task_version,
                command,
            )
            if issue is not None:
                return Result.failure(issue)
            target_state = requested_state
            failure_reason = command.failure_reason
            iteration_count = current.iteration_count
            if target_state is TaskLifecycle.SELF_REFINE:
                limit_result = self._limit_in_unit_of_work(
                    unit_of_work, organization_id, current, "iteration", correlation_id
                )
                if not limit_result.is_success or limit_result.value is None:
                    return Result.failure(
                        limit_result.error or self._repository_error(None, correlation_id)
                    )
                if self._exhausted(current.iteration_count, limit_result.value):
                    target_state = TaskLifecycle.FAILED
                    failure_reason = "iteration_limit_exhausted"
                else:
                    iteration_count += 1
            persisted = self._persist_transition(
                unit_of_work,
                current,
                correlation_id,
                target_state,
                command.reason_code,
                failure_reason=failure_reason,
                iteration_count=iteration_count,
            )
            if not persisted.is_success or persisted.value is None:
                unit_of_work.rollback()
                return Result.failure(
                    persisted.error or self._repository_error(None, correlation_id)
                )
            publications = [persisted.value[1]]
            if target_state in {TaskLifecycle.COMPLETE, TaskLifecycle.IDLE}:
                queued = self._queue_satisfied_in_unit_of_work(
                    unit_of_work, organization_id, correlation_id, current.run_reference
                )
                if not queued.is_success or queued.value is None:
                    unit_of_work.rollback()
                    return Result.failure(
                        queued.error or self._repository_error(None, correlation_id)
                    )
                publications.extend(queued.value)
            refreshed = unit_of_work.tasks.get(organization_id, task_id)
            if not refreshed.is_success or refreshed.value is None:
                unit_of_work.rollback()
                return Result.failure(self._repository_error(refreshed.error, correlation_id))
            outcome = TaskTransitionOutcome(refreshed.value, tuple(publications))
        self._publish(outcome.publications, publish)
        return Result.success(outcome)

    def retry_task(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        task_id: TaskId,
        expected_task_version: int,
        reason_code: str,
        *,
        publish: PublicationCallback | None = None,
    ) -> Result[TaskTransitionOutcome, ErrorDetail]:
        """Retry a nonterminal task within its pinned finite or unlimited retry budget."""
        if expected_task_version < 1 or not reason_code.strip():
            return Result.failure(
                self._validation(correlation_id, "Expected version and retry reason are required.")
            )
        with self._unit_of_work_factory() as unit_of_work:
            current_result = unit_of_work.tasks.get(organization_id, task_id)
            current = current_result.value
            if not current_result.is_success or current is None:
                return Result.failure(self._repository_error(current_result.error, correlation_id))
            if current.state not in {
                TaskLifecycle.RUNNING,
                TaskLifecycle.SELF_REFINE,
                TaskLifecycle.WAITING_FOR_CRITIQUE,
            }:
                return Result.failure(
                    ErrorDetail(
                        ErrorCode.INVALID_TRANSITION,
                        "Only active tasks can be retried.",
                        correlation_id,
                    )
                )
            if current.metadata.version != expected_task_version:
                return Result.failure(self._conflict(correlation_id))
            limit_result = self._limit_in_unit_of_work(
                unit_of_work, organization_id, current, "retry", correlation_id
            )
            if not limit_result.is_success or limit_result.value is None:
                return Result.failure(
                    limit_result.error or self._repository_error(None, correlation_id)
                )
            retry_limit = limit_result.value
            if self._exhausted(current.retry_count, retry_limit):
                persisted = self._persist_transition(
                    unit_of_work,
                    current,
                    correlation_id,
                    TaskLifecycle.FAILED,
                    "retry_limit_exhausted",
                    failure_reason="retry_limit_exhausted",
                )
                if not persisted.is_success or persisted.value is None:
                    unit_of_work.rollback()
                    return Result.failure(
                        persisted.error or self._repository_error(None, correlation_id)
                    )
                outcome = TaskTransitionOutcome(persisted.value[0], (persisted.value[1],))
            else:
                persisted = self._persist_transition(
                    unit_of_work,
                    current,
                    correlation_id,
                    TaskLifecycle.IDLE,
                    reason_code,
                    retry_count=current.retry_count + 1,
                )
                if not persisted.is_success or persisted.value is None:
                    unit_of_work.rollback()
                    return Result.failure(
                        persisted.error or self._repository_error(None, correlation_id)
                    )
                queued = self._queue_satisfied_in_unit_of_work(
                    unit_of_work, organization_id, correlation_id, current.run_reference
                )
                if not queued.is_success or queued.value is None:
                    unit_of_work.rollback()
                    return Result.failure(
                        queued.error or self._repository_error(None, correlation_id)
                    )
                refreshed = unit_of_work.tasks.get(organization_id, task_id)
                if not refreshed.is_success or refreshed.value is None:
                    unit_of_work.rollback()
                    return Result.failure(self._repository_error(refreshed.error, correlation_id))
                outcome = TaskTransitionOutcome(
                    refreshed.value, (persisted.value[1], *queued.value)
                )
        self._publish(outcome.publications, publish)
        return Result.success(outcome)

    def claim_task(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        task_id: TaskId,
        expected_task_version: int,
        *,
        publish: PublicationCallback | None = None,
    ) -> Result[TaskTransitionOutcome, ErrorDetail]:
        """Claim only a queue-eligible task; queued ineligible tasks remain unclaimable."""
        return self.transition(
            organization_id,
            correlation_id,
            task_id,
            expected_task_version,
            TaskTransitionCommand(TaskLifecycle.RUNNING, "task_claimed"),
            publish=publish,
        )

    def set_execution_eligibility(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        task_id: TaskId,
        expected_task_version: int,
        eligible_for_execution: bool,
        *,
        publish: PublicationCallback | None = None,
    ) -> Result[TaskTransitionOutcome, ErrorDetail]:
        """Retain changing claimability without moving a queued task out of `queued`."""
        if expected_task_version < 1:
            return Result.failure(
                self._validation(correlation_id, "Expected task version must be positive.")
            )
        with self._unit_of_work_factory() as unit_of_work:
            current_result = unit_of_work.tasks.get(organization_id, task_id)
            current = current_result.value
            if not current_result.is_success or current is None:
                return Result.failure(self._repository_error(current_result.error, correlation_id))
            if current.metadata.version != expected_task_version:
                return Result.failure(self._conflict(correlation_id))
            marker = not eligible_for_execution
            if current.ineligible_for_execution == marker:
                return Result.success(TaskTransitionOutcome(current, ()))
            now = self._clock()
            updated = replace(
                current,
                metadata=self._next_metadata(current.metadata, correlation_id, now),
                ineligible_for_execution=marker,
            )
            publication = self._publication(
                updated.metadata.organization_id,
                correlation_id,
                f"task:{updated.task_id}",
                "task.execution_eligibility.changed",
                {
                    "task_id": str(updated.task_id),
                    "state": updated.state.value,
                    "eligible_for_execution": eligible_for_execution,
                },
                now,
            )
            results = (
                unit_of_work.tasks.replace(updated, expected_task_version),
                unit_of_work.events.append_audit(
                    self._audit(
                        updated,
                        "task.execution_eligibility.changed",
                        updated.state.value,
                        now,
                        correlation_id,
                    )
                ),
                unit_of_work.events.append_event(publication.event),
                unit_of_work.events.append_outbox(publication.outbox),
            )
            failed = next((result.error for result in results if not result.is_success), None)
            if failed is not None:
                unit_of_work.rollback()
                return Result.failure(self._repository_error(failed, correlation_id))
            outcome = TaskTransitionOutcome(updated, (publication,))
        self._publish(outcome.publications, publish)
        return Result.success(outcome)

    def is_claimable(
        self, organization_id: OrganizationId, task_id: TaskId, correlation_id: CorrelationId
    ) -> Result[bool, ErrorDetail]:
        """Return whether a task may be sent to the governed dispatch port."""
        with self._unit_of_work_factory() as unit_of_work:
            task_result = unit_of_work.tasks.get(organization_id, task_id)
            task = task_result.value
            if not task_result.is_success or task is None:
                return Result.failure(self._repository_error(task_result.error, correlation_id))
            return Result.success(
                task.state is TaskLifecycle.QUEUED
                and not task.ineligible_for_execution
                and task.failure_reason is None
            )

    def create_replay_lineage(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        source_run_provenance_id: RunProvenanceId,
        checkpoint_reference: str,
        artifact_version_references: tuple[str, ...] = (),
        *,
        publish: PublicationCallback | None = None,
    ) -> Result[RunProvenance, ErrorDetail]:
        """Create a distinct immutable replay lineage from authorized retained provenance."""
        if not checkpoint_reference.strip() or any(
            not item.strip() for item in artifact_version_references
        ):
            return Result.failure(
                self._validation(
                    correlation_id, "Replay checkpoint and artifact references must be non-empty."
                )
            )
        now = self._clock()
        with self._unit_of_work_factory() as unit_of_work:
            source_result = unit_of_work.provenance.get(organization_id, source_run_provenance_id)
            source = source_result.value
            if not source_result.is_success or source is None:
                return Result.failure(self._repository_error(source_result.error, correlation_id))
            replay = RunProvenance(
                metadata=self._metadata(organization_id, correlation_id, now),
                run_provenance_id=RunProvenanceId(str(new_record_id())),
                graph_revision_id=source.graph_revision_id,
                workflow_definition=source.workflow_definition,
                workflow_definition_version=source.workflow_definition_version,
                agent_version_ids=source.agent_version_ids,
                pattern_version_ids=source.pattern_version_ids,
                source_checkpoint_reference=checkpoint_reference,
                artifact_version_references=(
                    artifact_version_references or source.artifact_version_references
                ),
                source_run_provenance_id=source.run_provenance_id,
            )
            publication = self._publication(
                organization_id,
                correlation_id,
                f"run_provenance:{replay.run_provenance_id}",
                "task.replay.lineage.created",
                {
                    "replay_provenance_id": str(replay.run_provenance_id),
                    "source_provenance_id": str(source.run_provenance_id),
                    "graph_revision_id": str(replay.graph_revision_id),
                    "checkpoint_reference": checkpoint_reference,
                    "artifact_version_references": replay.artifact_version_references,
                    "agent_version_ids": replay.agent_version_ids,
                    "pattern_version_ids": replay.pattern_version_ids,
                },
                now,
            )
            results = (
                unit_of_work.provenance.append(replay),
                unit_of_work.events.append_audit(
                    AuditRecord(
                        metadata=self._metadata(organization_id, correlation_id, now),
                        audit_id=str(new_record_id()),
                        action="task.replay.lineage.created",
                        subject_reference=f"run_provenance:{replay.run_provenance_id}",
                        outcome="created",
                        recorded_at=now,
                    )
                ),
                unit_of_work.events.append_event(publication.event),
                unit_of_work.events.append_outbox(publication.outbox),
            )
            failed = next((result.error for result in results if not result.is_success), None)
            if failed is not None:
                unit_of_work.rollback()
                return Result.failure(self._repository_error(failed, correlation_id))
        self._publish((publication,), publish)
        return Result.success(replay)

    def _queue_satisfied_in_unit_of_work(
        self,
        unit_of_work: ControlPlaneUnitOfWork,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        run_reference: str,
    ) -> Result[tuple[TaskPublication, ...], ErrorDetail]:
        publications: list[TaskPublication] = []
        made_progress = True
        while made_progress:
            made_progress = False
            tasks_result = unit_of_work.tasks.for_run(organization_id, run_reference)
            tasks = tasks_result.value
            if not tasks_result.is_success or tasks is None:
                return Result.failure(self._repository_error(tasks_result.error, correlation_id))
            for task in tasks:
                if (
                    task.state is not TaskLifecycle.IDLE
                    or task.ineligible_for_execution
                    or task.failure_reason is not None
                    or not self._prerequisites_satisfied(unit_of_work, organization_id, task)
                ):
                    continue
                persisted = self._persist_transition(
                    unit_of_work,
                    task,
                    correlation_id,
                    TaskLifecycle.QUEUED,
                    "prerequisites_satisfied",
                )
                if not persisted.is_success or persisted.value is None:
                    return Result.failure(
                        persisted.error or self._repository_error(None, correlation_id)
                    )
                publications.append(persisted.value[1])
                made_progress = True
        return Result.success(tuple(publications))

    def _prerequisites_satisfied(
        self,
        unit_of_work: ControlPlaneUnitOfWork,
        organization_id: OrganizationId,
        task: AgentTask,
    ) -> bool:
        for dependency_id in task.dependencies:
            dependency = unit_of_work.tasks.get(organization_id, dependency_id)
            if (
                not dependency.is_success
                or dependency.value is None
                or dependency.value.state is not TaskLifecycle.COMPLETE
            ):
                return False
        for gate_id in task.approval_gate_ids:
            gate = unit_of_work.evidence.get_approval(organization_id, gate_id)
            if (
                not gate.is_success
                or gate.value is None
                or gate.value.status is not ApprovalGateStatus.APPROVED
            ):
                return False
        return True

    def _transition_issue(
        self,
        unit_of_work: ControlPlaneUnitOfWork,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        current: AgentTask,
        expected_task_version: int,
        command: TaskTransitionCommand,
    ) -> ErrorDetail | None:
        to_state = command.to_state
        if not isinstance(to_state, TaskLifecycle):
            return self._validation(correlation_id, "Task lifecycle state is invalid.")
        if not command.reason_code.strip():
            return self._validation(correlation_id, "Task transition reason is required.")
        if current.metadata.version != expected_task_version:
            return self._conflict(correlation_id)
        if current.state not in self._ALLOWED_TRANSITIONS:
            return self._validation(correlation_id, "Stored task lifecycle state is invalid.")
        if to_state not in self._ALLOWED_TRANSITIONS[current.state]:
            return ErrorDetail(
                ErrorCode.INVALID_TRANSITION,
                "Task lifecycle transition is not allowed.",
                correlation_id,
            )
        if to_state is TaskLifecycle.QUEUED and (
            current.ineligible_for_execution
            or not self._prerequisites_satisfied(unit_of_work, organization_id, current)
        ):
            return ErrorDetail(
                ErrorCode.INVALID_TRANSITION,
                "Task prerequisites are not satisfied for queueing.",
                correlation_id,
            )
        if to_state is TaskLifecycle.RUNNING and current.ineligible_for_execution:
            return ErrorDetail(
                ErrorCode.INVALID_TRANSITION,
                "Task is currently ineligible for execution.",
                correlation_id,
            )
        if to_state is TaskLifecycle.FAILED and not command.failure_reason:
            return self._validation(
                correlation_id, "Failed tasks require a machine-readable reason."
            )
        return None

    def _persist_transition(
        self,
        unit_of_work: ControlPlaneUnitOfWork,
        current: AgentTask,
        correlation_id: CorrelationId,
        to_state: TaskLifecycle,
        reason_code: str,
        *,
        failure_reason: str | None = None,
        retry_count: int | None = None,
        iteration_count: int | None = None,
    ) -> Result[tuple[AgentTask, TaskPublication], ErrorDetail]:
        now = self._clock()
        updated = replace(
            current,
            metadata=self._next_metadata(current.metadata, correlation_id, now),
            state=to_state,
            retry_count=current.retry_count if retry_count is None else retry_count,
            iteration_count=current.iteration_count if iteration_count is None else iteration_count,
            failure_reason=failure_reason if to_state is TaskLifecycle.FAILED else None,
            blocked_fields=current.blocked_fields if to_state is TaskLifecycle.BLOCKED else (),
        )
        transition = TaskTransition(
            metadata=self._metadata(updated.metadata.organization_id, correlation_id, now),
            transition_id=str(new_record_id()),
            task_id=current.task_id,
            expected_task_version=current.metadata.version,
            from_state=current.state,
            to_state=to_state,
            recorded_at=now,
        )
        publication = self._publication(
            updated.metadata.organization_id,
            correlation_id,
            f"task:{updated.task_id}",
            "task.transitioned",
            {
                "task_id": str(updated.task_id),
                "from_state": current.state.value,
                "to_state": to_state.value,
                "reason_code": reason_code,
                "retry_count": updated.retry_count,
                "iteration_count": updated.iteration_count,
                "ineligible_for_execution": updated.ineligible_for_execution,
            },
            now,
        )
        results = (
            unit_of_work.tasks.replace(updated, current.metadata.version),
            unit_of_work.tasks.append_transition(transition),
            unit_of_work.events.append_audit(
                self._audit(updated, "task.transitioned", to_state.value, now, correlation_id)
            ),
            unit_of_work.events.append_event(publication.event),
            unit_of_work.events.append_outbox(publication.outbox),
        )
        failed = next((result.error for result in results if not result.is_success), None)
        if failed is not None:
            return Result.failure(self._repository_error(failed, correlation_id))
        return Result.success((updated, publication))

    def _limit_in_unit_of_work(
        self,
        unit_of_work: ControlPlaneUnitOfWork,
        organization_id: OrganizationId,
        task: AgentTask,
        kind: str,
        correlation_id: CorrelationId,
    ) -> Result[int, ErrorDetail]:
        agent_result = unit_of_work.common_contracts.get_agent_version(
            organization_id, task.pinned_agent_version_id
        )
        agent = agent_result.value
        if not agent_result.is_success or agent is None:
            return Result.failure(self._repository_error(agent_result.error, correlation_id))
        keys = (
            ("retry_limit", "max_retries")
            if kind == "retry"
            else (
                "iteration_limit",
                "max_iterations",
            )
        )
        for key in keys:
            if key not in agent.runtime_policy:
                continue
            value = agent.runtime_policy[key]
            if isinstance(value, bool) or not isinstance(value, int):
                return Result.failure(
                    self._validation(
                        correlation_id, f"Pinned agent {kind} limit must be an integer."
                    )
                )
            return Result.success(value)
        return Result.success(0)

    @staticmethod
    def _exhausted(count: int, limit: int) -> bool:
        """Negative limits are deliberately unlimited; zero permits no retry/iteration."""
        return limit >= 0 and count >= limit

    def _plans_from_revision(
        self,
        revision: GraphRevision,
        resolved_agent_ids: tuple[AgentVersionId, ...],
        run_reference: str,
    ) -> Result[tuple[_TaskPlan, ...], ErrorDetail]:
        node_ids: dict[str, TaskId] = {}
        raw_dependencies: dict[str, list[str]] = {}
        raw_plans: list[
            tuple[
                str,
                AgentVersionId,
                Mapping[str, object],
                tuple[ApprovalGateId, ...],
                str | None,
            ]
        ] = []
        pinned = set(resolved_agent_ids)
        for node in revision.nodes:
            node_id = node.get("id")
            agent_id = node.get("agent_version_id")
            if not isinstance(node_id, str) or not node_id.strip() or node_id in node_ids:
                return Result.failure(
                    self._validation(
                        revision.metadata.correlation_id, "Graph task node identity is invalid."
                    )
                )
            if not isinstance(agent_id, str) or AgentVersionId(agent_id) not in pinned:
                return Result.failure(
                    self._validation(
                        revision.metadata.correlation_id, "Graph task agent pin is invalid."
                    )
                )
            constraints = node.get("constraints", {})
            if not isinstance(constraints, Mapping):
                return Result.failure(
                    self._validation(
                        revision.metadata.correlation_id, "Task constraints must be a mapping."
                    )
                )
            gates = node.get("approval_gate_ids", node.get("approval_gates", ()))
            if (
                isinstance(gates, str)
                or not isinstance(gates, Sequence)
                or any(not isinstance(gate, str) or not gate.strip() for gate in gates)
            ):
                return Result.failure(
                    self._validation(
                        revision.metadata.correlation_id, "Task approval gates are invalid."
                    )
                )
            checkpoint = node.get("checkpoint_reference")
            if checkpoint is not None and (
                not isinstance(checkpoint, str) or not checkpoint.strip()
            ):
                return Result.failure(
                    self._validation(
                        revision.metadata.correlation_id, "Task checkpoint reference is invalid."
                    )
                )
            dependencies = node.get("dependencies", ())
            if (
                isinstance(dependencies, str)
                or not isinstance(dependencies, Sequence)
                or any(
                    not isinstance(dependency, str) or not dependency.strip()
                    for dependency in dependencies
                )
            ):
                return Result.failure(
                    self._validation(
                        revision.metadata.correlation_id, "Task dependencies are invalid."
                    )
                )
            gate_ids = tuple(
                ApprovalGateId(gate) for gate in gates if isinstance(gate, str)
            )
            dependency_names = tuple(
                dependency for dependency in dependencies if isinstance(dependency, str)
            )
            node_ids[node_id] = TaskId(f"{run_reference}:{node_id}")
            raw_dependencies[node_id] = list(dependency_names)
            raw_plans.append(
                (node_id, AgentVersionId(agent_id), constraints, gate_ids, checkpoint)
            )
        for edge in revision.edges:
            source = edge.get("from")
            target = edge.get("to")
            if not isinstance(source, str) or not isinstance(target, str):
                return Result.failure(
                    self._validation(
                        revision.metadata.correlation_id, "Graph task dependency edge is invalid."
                    )
                )
            if source not in node_ids or target not in node_ids or source == target:
                return Result.failure(
                    self._validation(
                        revision.metadata.correlation_id, "Graph task dependency edge is invalid."
                    )
                )
            raw_dependencies[target].append(source)
        plans: list[_TaskPlan] = []
        for node_id, agent_id, constraints, gates, checkpoint in raw_plans:
            names = raw_dependencies[node_id]
            if len(names) != len(set(names)) or any(name not in node_ids for name in names):
                return Result.failure(
                    self._validation(
                        revision.metadata.correlation_id, "Graph task dependencies are invalid."
                    )
                )
            plans.append(
                _TaskPlan(
                    task_id=node_ids[node_id],
                    pinned_agent_version_id=agent_id,
                    dependencies=tuple(node_ids[name] for name in names),
                    constraints=constraints,
                    approval_gate_ids=gates,
                    checkpoint_reference=checkpoint,
                )
            )
        return Result.success(tuple(plans))

    @staticmethod
    def _metadata(
        organization_id: OrganizationId, correlation_id: CorrelationId, now: datetime
    ) -> RecordMetadata:
        return RecordMetadata(
            record_id=new_record_id(),
            organization_id=organization_id,
            correlation_id=correlation_id,
            schema_version=SCHEMA_VERSION,
            version=1,
            created_at=now,
            updated_at=now,
        )

    @staticmethod
    def _next_metadata(
        metadata: RecordMetadata, correlation_id: CorrelationId, now: datetime
    ) -> RecordMetadata:
        return replace(
            metadata,
            correlation_id=correlation_id,
            version=metadata.version + 1,
            updated_at=now,
        )

    def _publication(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        subject_reference: str,
        event_type: str,
        payload: Mapping[str, object],
        now: datetime,
    ) -> TaskPublication:
        event_id = EventId(str(new_record_id()))
        event = OperationalEvent(
            metadata=self._metadata(organization_id, correlation_id, now),
            event_id=event_id,
            sequence=self._next_event_sequence(),
            event_type=event_type,
            subject_reference=subject_reference,
            occurred_at=now,
            payload_schema_version=SCHEMA_VERSION,
            redacted_payload=payload,
        )
        return TaskPublication(
            event=event,
            outbox=OutboxRecord(
                metadata=self._metadata(organization_id, correlation_id, now),
                outbox_id=OutboxId(str(new_record_id())),
                event_id=event_id,
                state=DeliveryState.PENDING,
                created_at=now,
            ),
        )

    @staticmethod
    def _audit(
        task: AgentTask,
        action: str,
        outcome: str,
        now: datetime,
        correlation_id: CorrelationId,
    ) -> AuditRecord:
        return AuditRecord(
            metadata=TaskCoordinator._metadata(task.metadata.organization_id, correlation_id, now),
            audit_id=str(new_record_id()),
            action=action,
            subject_reference=f"task:{task.task_id}",
            outcome=outcome,
            recorded_at=now,
        )

    @staticmethod
    def _publish(
        publications: tuple[TaskPublication, ...], publish: PublicationCallback | None
    ) -> None:
        if publish is None:
            return
        for publication in publications:
            publish(publication)

    @staticmethod
    def _validation(correlation_id: CorrelationId, message: str) -> ErrorDetail:
        return ErrorDetail(ErrorCode.VALIDATION_FAILED, message, correlation_id)

    @staticmethod
    def _conflict(correlation_id: CorrelationId) -> ErrorDetail:
        return ErrorDetail(ErrorCode.CONFLICT, "Task changed before transition.", correlation_id)

    @staticmethod
    def _repository_error(error: ErrorDetail | None, correlation_id: CorrelationId) -> ErrorDetail:
        if error is None:
            return ErrorDetail(
                ErrorCode.REPOSITORY_UNAVAILABLE,
                "Durable task storage is unavailable.",
                correlation_id,
                retryable=True,
            )
        return replace(error, correlation_id=correlation_id)
