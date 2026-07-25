"""Property checks for durable asynchronous work commits and post-commit delivery."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from itertools import count
from types import TracebackType
from typing import Literal, cast

from hypothesis import given, settings, strategies as st

from app.core.command_service import (
    CommandPublication,
    CommandService,
    UnitOfWorkFactory,
    WorkCommand,
    WorkKind,
    WorkTransitionCommand,
)
from app.models.contracts import ErrorCode, ErrorDetail, RepositoryError, Result
from app.models.control_plane import (
    AuditRecord,
    OperationalEvent,
    OutboxRecord,
    WorkItem,
    WorkItemId,
    WorkState,
    WorkTransition,
)
from app.models.identifiers import CorrelationId, OrganizationId
from app.repositories.control_plane import (
    InMemoryControlPlaneDatabase,
    InMemoryControlPlaneUnitOfWork,
    InMemoryEventOutboxRepository,
    InMemoryWorkRepository,
)

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_ORGANIZATION = OrganizationId("property-8-organization")
_CORRELATION = CorrelationId("property-8-correlation")
_SAFE_SUFFIXES = st.text(alphabet="abcdefghijklmnopqrstuvwxyz0123456789", min_size=1, max_size=12)


class _FailurePoint(StrEnum):
    """The durable writes exercised by the command boundary."""

    WORK_CREATE = "work_create"
    WORK_REPLACE = "work_replace"
    TRANSITION_APPEND = "transition_append"
    AUDIT_APPEND = "audit_append"
    EVENT_APPEND = "event_append"
    OUTBOX_APPEND = "outbox_append"


_CREATION_FAILURE_POINTS = (
    _FailurePoint.WORK_CREATE,
    _FailurePoint.AUDIT_APPEND,
    _FailurePoint.EVENT_APPEND,
    _FailurePoint.OUTBOX_APPEND,
)
_TRANSITION_FAILURE_POINTS = (
    _FailurePoint.WORK_REPLACE,
    _FailurePoint.TRANSITION_APPEND,
    _FailurePoint.AUDIT_APPEND,
    _FailurePoint.EVENT_APPEND,
    _FailurePoint.OUTBOX_APPEND,
)


def _failure(point: _FailurePoint) -> ErrorDetail:
    return ErrorDetail(
        ErrorCode.REPOSITORY_UNAVAILABLE,
        f"Injected failure at {point.value}.",
        _CORRELATION,
        retryable=True,
    )


@dataclass(slots=True)
class _FailingWorkRepository:
    """Delegating work repository that can reject one transactional write."""

    delegate: InMemoryWorkRepository
    failure_point: _FailurePoint | None

    def create(self, record: WorkItem) -> Result[WorkItem, RepositoryError]:
        if self.failure_point is _FailurePoint.WORK_CREATE:
            return Result.failure(_failure(_FailurePoint.WORK_CREATE))
        return self.delegate.create(record)

    def replace(
        self, record: WorkItem, expected_work_version: int
    ) -> Result[WorkItem, RepositoryError]:
        if self.failure_point is _FailurePoint.WORK_REPLACE:
            return Result.failure(_failure(_FailurePoint.WORK_REPLACE))
        return self.delegate.replace(record, expected_work_version)

    def get(
        self, organization_id: OrganizationId, work_item_id: WorkItemId
    ) -> Result[WorkItem, RepositoryError]:
        return self.delegate.get(organization_id, work_item_id)

    def append_transition(
        self, transition: WorkTransition
    ) -> Result[WorkTransition, RepositoryError]:
        if self.failure_point is _FailurePoint.TRANSITION_APPEND:
            return Result.failure(_failure(_FailurePoint.TRANSITION_APPEND))
        return self.delegate.append_transition(transition)


@dataclass(slots=True)
class _FailingEventOutboxRepository:
    """Delegating transactional outbox that can reject any evidence or delivery write."""

    delegate: InMemoryEventOutboxRepository
    failure_point: _FailurePoint | None

    def append_audit(self, record: AuditRecord) -> Result[AuditRecord, RepositoryError]:
        if self.failure_point is _FailurePoint.AUDIT_APPEND:
            return Result.failure(_failure(_FailurePoint.AUDIT_APPEND))
        return self.delegate.append_audit(record)

    def append_event(self, record: OperationalEvent) -> Result[OperationalEvent, RepositoryError]:
        if self.failure_point is _FailurePoint.EVENT_APPEND:
            return Result.failure(_failure(_FailurePoint.EVENT_APPEND))
        return self.delegate.append_event(record)

    def append_outbox(self, record: OutboxRecord) -> Result[OutboxRecord, RepositoryError]:
        if self.failure_point is _FailurePoint.OUTBOX_APPEND:
            return Result.failure(_failure(_FailurePoint.OUTBOX_APPEND))
        return self.delegate.append_outbox(record)


class _FailureInjectingUnitOfWork:
    """Transaction wrapper that preserves the database fake's real atomic commit semantics."""

    def __init__(
        self,
        delegate: InMemoryControlPlaneUnitOfWork,
        failure_point: _FailurePoint | None,
    ) -> None:
        self._delegate = delegate
        self.work_items = _FailingWorkRepository(delegate.work_items, failure_point)
        self.events = _FailingEventOutboxRepository(delegate.events, failure_point)

    def __enter__(self) -> _FailureInjectingUnitOfWork:
        self._delegate.__enter__()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> Literal[False]:
        return self._delegate.__exit__(exc_type, exc, traceback)

    def rollback(self) -> None:
        self._delegate.rollback()


@dataclass(slots=True)
class _TransactionalOutboxFake:
    """Deterministic transaction/outbox fake with one configurable persistence failure."""

    database: InMemoryControlPlaneDatabase
    failure_point: _FailurePoint | None = None

    def unit_of_work(self) -> _FailureInjectingUnitOfWork:
        return _FailureInjectingUnitOfWork(
            self.database.unit_of_work(),
            self.failure_point,
        )


def _service(fake: _TransactionalOutboxFake) -> CommandService:
    sequences = count(1)
    return CommandService(
        cast(UnitOfWorkFactory, fake.unit_of_work),
        clock=lambda: _NOW,
        next_event_sequence=lambda: next(sequences),
    )


def _command(kind: WorkKind, suffix: str, attempt: int) -> WorkCommand:
    return WorkCommand(
        kind=kind,
        subject_reference=f"{kind.value}:subject-{suffix}",
        idempotency_key=f"key-{kind.value}-{suffix}",
        scheduled_at=_NOW + timedelta(minutes=attempt),
        attempt=attempt,
    )


def _assert_empty(database: InMemoryControlPlaneDatabase) -> None:
    assert not database._state.work_items
    assert not database._state.work_transitions
    assert not database._state.audits
    assert not database._state.events
    assert not database._state.outbox


def _assert_initial_commit(
    database: InMemoryControlPlaneDatabase,
    work_item: WorkItem,
) -> None:
    state = database._state
    assert state.work_items[work_item.work_item_id] == work_item
    assert not state.work_transitions
    assert len(state.audits) == len(state.events) == len(state.outbox) == 1
    assert all(
        record.subject_reference == work_item.subject_reference for record in state.audits.values()
    )
    assert all(
        record.subject_reference == work_item.subject_reference for record in state.events.values()
    )
    assert all(record.event_id in state.events for record in state.outbox.values())


def _record_callback(observed: list[str], marker: str) -> Callable[[object], None]:
    def callback(_: object) -> None:
        observed.append(marker)

    return callback


def _committed_dispatch_callback(
    database: InMemoryControlPlaneDatabase,
    observed: list[str],
) -> Callable[[WorkItem], None]:
    def dispatch(work_item: WorkItem) -> None:
        _assert_initial_commit(database, work_item)
        observed.append("dispatch")

    return dispatch


def _committed_publish_callback(
    database: InMemoryControlPlaneDatabase,
    observed: list[str],
) -> Callable[[CommandPublication], None]:
    def publish(publication: CommandPublication) -> None:
        work_item = next(iter(database._state.work_items.values()))
        _assert_initial_commit(database, work_item)
        assert publication.event in database._state.events.values()
        assert publication.outbox in database._state.outbox.values()
        observed.append("publish")

    return publish


def _transition_publish_callback(
    database: InMemoryControlPlaneDatabase,
    work_item_id: WorkItemId,
    observed: list[str],
) -> Callable[[CommandPublication], None]:
    def publish(publication: CommandPublication) -> None:
        state = database._state
        assert state.work_items[work_item_id].state is WorkState.CANCELLED
        assert tuple(item.to_state for item in state.work_transitions[work_item_id]) == (
            WorkState.CANCELLED,
        )
        assert len(state.audits) == len(state.events) == len(state.outbox) == 2
        assert publication.event in state.events.values()
        assert publication.outbox in state.outbox.values()
        observed.append("publish")

    return publish


# Feature: backend-redesign, Property 8
# Durable work transitions commit before dispatch/publication.
# **Validates: Requirements 5.1, 5.2, 5.3, 10.1**
@settings(max_examples=100, deadline=None)
@given(suffix=_SAFE_SUFFIXES, attempt=st.integers(min_value=0, max_value=3))
def test_property_8_durable_work_transitions_commit_before_dispatch_or_publication(
    suffix: str,
    attempt: int,
) -> None:
    """Every work kind is all-or-nothing at every durable write and visible only post-commit."""
    for kind in WorkKind:
        command = _command(kind, suffix, attempt)

        for failure_point in _CREATION_FAILURE_POINTS:
            failed_fake = _TransactionalOutboxFake(
                InMemoryControlPlaneDatabase(),
                failure_point,
            )
            failed_callbacks: list[str] = []
            failed = _service(failed_fake).submit(
                _ORGANIZATION,
                _CORRELATION,
                command,
                dispatch=_record_callback(failed_callbacks, "dispatch"),
                publish=_record_callback(failed_callbacks, "publish"),
            )

            assert not failed.is_success
            assert failed_callbacks == []
            _assert_empty(failed_fake.database)

        committed_fake = _TransactionalOutboxFake(InMemoryControlPlaneDatabase())
        committed_callbacks: list[str] = []
        created = _service(committed_fake).submit(
            _ORGANIZATION,
            _CORRELATION,
            command,
            dispatch=_committed_dispatch_callback(committed_fake.database, committed_callbacks),
            publish=_committed_publish_callback(committed_fake.database, committed_callbacks),
        )

        assert created.is_success and created.value is not None
        initial = created.value.work_item
        assert initial.metadata.organization_id == _ORGANIZATION
        assert initial.metadata.correlation_id == _CORRELATION
        assert initial.attempt == attempt
        assert initial.idempotency_key == command.idempotency_key
        assert initial.scheduled_at == command.scheduled_at
        assert not initial.cancellation_requested
        assert initial.claim_owner is None
        assert committed_callbacks == ["dispatch", "publish"]
        _assert_initial_commit(committed_fake.database, initial)

        for failure_point in _TRANSITION_FAILURE_POINTS:
            transition_fake = _TransactionalOutboxFake(InMemoryControlPlaneDatabase())
            transition_service = _service(transition_fake)
            baseline = transition_service.submit(_ORGANIZATION, _CORRELATION, command)
            assert baseline.is_success and baseline.value is not None
            baseline_item = baseline.value.work_item
            transition_fake.failure_point = failure_point
            failed_callbacks = []

            failed = transition_service.transition(
                _ORGANIZATION,
                _CORRELATION,
                baseline_item.work_item_id,
                baseline_item.metadata.version,
                WorkTransitionCommand(
                    to_state=WorkState.CANCELLED,
                    reason_code="operator_cancelled",
                    cancellation_requested=True,
                ),
                publish=_record_callback(failed_callbacks, "publish"),
            )

            assert not failed.is_success
            assert failed_callbacks == []
            _assert_initial_commit(transition_fake.database, baseline_item)
            assert (
                transition_fake.database._state.work_items[baseline_item.work_item_id]
                == baseline_item
            )

        transition_fake = _TransactionalOutboxFake(InMemoryControlPlaneDatabase())
        transition_service = _service(transition_fake)
        baseline = transition_service.submit(_ORGANIZATION, _CORRELATION, command)
        assert baseline.is_success and baseline.value is not None
        baseline_item = baseline.value.work_item
        transition_callbacks: list[str] = []
        transitioned = transition_service.transition(
            _ORGANIZATION,
            _CORRELATION,
            baseline_item.work_item_id,
            baseline_item.metadata.version,
            WorkTransitionCommand(
                to_state=WorkState.CANCELLED,
                reason_code="operator_cancelled",
                cancellation_requested=True,
            ),
            publish=_transition_publish_callback(
                transition_fake.database,
                baseline_item.work_item_id,
                transition_callbacks,
            ),
        )

        assert transitioned.is_success and transitioned.value is not None
        assert transitioned.value.work_item.state is WorkState.CANCELLED
        assert transitioned.value.work_item.cancellation_requested
        assert transition_callbacks == ["publish"]
