"""Focused RunService checks for durable queued dispatch behavior."""

from __future__ import annotations

from datetime import UTC, datetime

from app.models.common import OptimisticTransition
from app.models.contracts import ErrorCode, ErrorDetail, RepositoryError, Result
from app.models.identifiers import CorrelationId, OrganizationId, RunId
from app.models.runs import RunRecord, RunStatus, WorkflowEngineKind
from app.repositories.run_repository import InMemoryRunRepository
from app.runs.service import RunService
from app.workflows.validator import RegisteredReferences

ORG_ID = OrganizationId("org-1")
CORRELATION_ID = CorrelationId("corr-1")
NOW = datetime(2025, 1, 1, tzinfo=UTC)


def _references() -> RegisteredReferences:
    return RegisteredReferences(
        agent_ids=frozenset({"ops.planner"}),
        tool_ids=frozenset({"crm.lookup"}),
        memory_scope_ids=frozenset({"organization", "workflow"}),
        risk_gate_ids=frozenset({"low-risk"}),
        rollback_plan_ids=frozenset({"compensate.crm"}),
        authorization_ids=frozenset({"approval-1"}),
    )


def _definition() -> dict[str, object]:
    return {
        "definition_type": "workflow_dna",
        "id": "ops.onboarding",
        "version": "1.0.0",
        "owner_id": "ops.owner",
        "authorization_id": "approval-1",
        "engine": "legacy",
        "execution_budget": {
            "max_node_visits": 2,
            "max_handoffs": 1,
            "max_wall_clock_seconds": 30,
            "max_tool_requests": 2,
        },
        "memory": {"reads": ["organization"], "writes": ["workflow"]},
        "risk_gate_ids": ["low-risk"],
        "rollback": {"plan_id": "compensate.crm", "compensation_step_ids": ["step-1"]},
        "steps": [
            {
                "id": "step-1",
                "agent_id": "ops.planner",
                "tool_ids": ["crm.lookup"],
                "memory_reads": ["organization"],
                "memory_writes": ["workflow"],
            }
        ],
    }


def _service(repository: InMemoryRunRepository) -> RunService:
    return RunService(repository, _references(), clock=lambda: NOW)


def _create(service: RunService) -> RunRecord:
    created = service.create_queued_run(ORG_ID, CORRELATION_ID, _definition())
    assert created.is_success
    assert created.value is not None
    return created.value


def test_create_persists_queued_engine_before_dispatch() -> None:
    """A new run is durably queued with its selected engine before it can start."""
    repository = InMemoryRunRepository()
    service = _service(repository)

    run = _create(service)

    assert run.status is RunStatus.QUEUED
    assert run.engine is WorkflowEngineKind.LEGACY
    stored = repository.get_by_run_id(ORG_ID, run.run_id)
    assert stored.is_success and stored.value == run


def test_duplicate_dispatch_key_starts_only_once() -> None:
    """The same durable dispatch identity cannot invoke the starter twice."""
    repository = InMemoryRunRepository()
    service = _service(repository)
    run = _create(service)
    starts: list[RunId] = []

    def starter(record: RunRecord) -> None:
        starts.append(record.run_id)

    first = service.dispatch(ORG_ID, run.run_id, "dispatch-1", starter, CORRELATION_ID)
    duplicate = service.dispatch(ORG_ID, run.run_id, "dispatch-1", starter, CORRELATION_ID)

    assert first.is_success and first.value is not None
    assert duplicate.is_success and duplicate.value is not None
    assert not first.value.is_idempotent
    assert duplicate.value.is_idempotent
    assert starts == [run.run_id]


def test_failed_dispatch_is_auditable_and_retryable_only_after_requeue() -> None:
    """A dispatch failure exposes an audit/retry outcome only after queued retention."""
    repository = InMemoryRunRepository()
    service = _service(repository)
    run = _create(service)

    def fail_to_start(_record: RunRecord) -> None:
        raise RuntimeError("start failed")

    failed = service.dispatch(ORG_ID, run.run_id, "dispatch-1", fail_to_start, CORRELATION_ID)

    assert failed.is_success and failed.value is not None
    assert failed.value.record.status is RunStatus.QUEUED
    assert failed.value.record.is_dispatch_retryable
    assert failed.value.retry_permitted
    assert failed.value.dispatch_error is not None
    assert failed.value.attempt.failure_code == ErrorCode.REPOSITORY_UNAVAILABLE


class _RequeueFailingRepository(InMemoryRunRepository):
    """Reject only the queued-retention write after a durable dispatch claim."""

    def __init__(self) -> None:
        super().__init__()
        self.transition_count = 0

    def transition(
        self, record: RunRecord, transition: OptimisticTransition
    ) -> Result[RunRecord, ErrorDetail]:
        self.transition_count += 1
        if self.transition_count == 2:
            error = ErrorDetail(
                ErrorCode.REPOSITORY_UNAVAILABLE,
                "retention unavailable",
                CORRELATION_ID,
            )
            return Result.failure(error)
        return super().transition(record, transition)


def test_unretained_dispatch_failure_cannot_be_audited_or_retried() -> None:
    """A failed queued-retention write returns no outcome and rejects another dispatch."""
    repository = _RequeueFailingRepository()
    service = _service(repository)
    run = _create(service)

    def fail_to_start(_record: RunRecord) -> None:
        raise RuntimeError("start failed")

    failed = service.dispatch(ORG_ID, run.run_id, "dispatch-1", fail_to_start, CORRELATION_ID)
    retry = service.dispatch(ORG_ID, run.run_id, "dispatch-2", lambda _record: None, CORRELATION_ID)

    assert not failed.is_success
    assert failed.error is not None
    assert failed.error.code is ErrorCode.REPOSITORY_UNAVAILABLE
    assert not failed.error.retryable
    assert not retry.is_success
    assert retry.error is not None
    assert retry.error.code is ErrorCode.INVALID_TRANSITION


class _OrderingRepository(InMemoryRunRepository):
    """Record durable lifecycle writes made by the Host-owned run service."""

    def __init__(self) -> None:
        super().__init__()
        self.events: list[str] = []

    def create_queued(self, record: RunRecord) -> Result[RunRecord, RepositoryError]:
        persisted = super().create_queued(record)
        if persisted.is_success:
            self.events.append("queued-persisted")
        return persisted

    def transition(
        self, record: RunRecord, transition: OptimisticTransition
    ) -> Result[RunRecord, RepositoryError]:
        persisted = super().transition(record, transition)
        if persisted.is_success:
            attempt = record.dispatch_attempts[-1]
            self.events.append(f"transition:{record.status.value}:{attempt.status.value}")
        return persisted


def test_invalid_definition_creates_no_dispatchable_run() -> None:
    """Invalid DNA is rejected before a queued record or dispatch attempt can exist."""
    repository = InMemoryRunRepository()
    service = _service(repository)
    invalid_definition = _definition()
    invalid_definition["engine"] = "unsupported"

    created = service.create_queued_run(ORG_ID, CORRELATION_ID, invalid_definition)

    assert not created.is_success
    assert created.error is not None
    assert created.error.code is ErrorCode.VALIDATION_FAILED
    assert repository.records() == ()


def test_failed_dispatch_retains_queue_before_retry_starts() -> None:
    """A retry starts only after the failed dispatch has been durably requeued."""
    repository = _OrderingRepository()
    service = _service(repository)
    run = _create(service)
    retry_observations: list[RunStatus] = []

    def failing_starter(_record: RunRecord) -> None:
        repository.events.append("starter-failed")
        raise RuntimeError("local start failure")

    failed = service.dispatch(ORG_ID, run.run_id, "dispatch-1", failing_starter, CORRELATION_ID)

    assert failed.is_success and failed.value is not None
    assert failed.value.retry_permitted
    assert repository.events == [
        "queued-persisted",
        "transition:dispatching:started",
        "starter-failed",
        "transition:queued:failed",
    ]
    retained = repository.get_by_run_id(ORG_ID, run.run_id)
    assert retained.is_success and retained.value is not None
    assert retained.value.status is RunStatus.QUEUED
    assert retained.value.is_dispatch_retryable

    def retry_starter(record: RunRecord) -> None:
        stored = repository.get_by_run_id(ORG_ID, record.run_id)
        assert stored.is_success and stored.value is not None
        retry_observations.append(stored.value.status)
        repository.events.append("retry-starter-invoked")

    retried = service.dispatch(ORG_ID, run.run_id, "dispatch-2", retry_starter, CORRELATION_ID)

    assert retried.is_success and retried.value is not None
    assert retry_observations == [RunStatus.DISPATCHING]
    assert repository.events[-2:] == [
        "transition:dispatching:started",
        "retry-starter-invoked",
    ]
