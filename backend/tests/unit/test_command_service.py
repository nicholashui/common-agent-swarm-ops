"""Focused durable-command boundary tests for backend-redesign task 5.1."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from app.core.command_service import (
    CommandPublication,
    CommandService,
    WorkCommand,
    WorkKind,
    WorkTransitionCommand,
)
from app.models.control_plane import WorkItem, WorkState
from app.models.identifiers import CorrelationId, OrganizationId
from app.repositories.control_plane import InMemoryControlPlaneDatabase

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_ORGANIZATION = OrganizationId("organization-command")
_CORRELATION = CorrelationId("correlation-command")


def _service(
    database: InMemoryControlPlaneDatabase,
    sequences: tuple[int, ...] = (1, 2, 3),
) -> CommandService:
    iterator = iter(sequences)
    return CommandService(
        database.unit_of_work,
        clock=lambda: _NOW,
        next_event_sequence=lambda: next(iterator),
    )


@pytest.mark.parametrize("kind", tuple(WorkKind))
def test_submit_retains_each_async_work_kind_before_dispatch(kind: WorkKind) -> None:
    """Runs, evaluations, contributions, indexing, and rollouts share one durable boundary."""
    database = InMemoryControlPlaneDatabase()
    service = _service(database)
    observed: list[str] = []

    def dispatch(work_item: WorkItem) -> None:
        observed.append(str(work_item.work_item_id))
        with database.unit_of_work() as unit_of_work:
            persisted = unit_of_work.work_items.get(_ORGANIZATION, work_item.work_item_id)
            assert persisted.is_success

    result = service.submit(
        _ORGANIZATION,
        _CORRELATION,
        WorkCommand(
            kind=kind,
            subject_reference=f"{kind.value}:subject-1",
            idempotency_key=f"key-{kind.value}",
            scheduled_at=_NOW,
        ),
        dispatch=dispatch
    )

    assert result.is_success and result.value is not None
    submission = result.value
    assert submission.work_item.state is WorkState.PENDING
    assert submission.work_item.metadata.organization_id == _ORGANIZATION
    assert submission.work_item.metadata.correlation_id == _CORRELATION
    assert submission.work_item.attempt == 0
    assert submission.work_item.idempotency_key == f"key-{kind.value}"
    assert submission.work_item.scheduled_at == _NOW
    assert not submission.work_item.cancellation_requested
    assert submission.work_item.claim_owner is None
    assert observed == [str(submission.work_item.work_item_id)]



def test_submit_commits_work_audit_event_and_outbox_before_publication() -> None:
    """Publication observes the complete committed transaction, never a partial work mutation."""
    database = InMemoryControlPlaneDatabase()
    service = _service(database)
    publications: list[CommandPublication] = []

    def publish(publication: CommandPublication) -> None:
        publications.append(publication)
        assert database._state.work_items
        assert database._state.events[publication.event.event_id] == publication.event
        assert database._state.outbox[publication.outbox.outbox_id] == publication.outbox
        assert database._state.audits

    result = service.submit(
        _ORGANIZATION,
        _CORRELATION,
        WorkCommand(
            kind=WorkKind.RUN,
            subject_reference="run:subject-1",
            idempotency_key="command-key-1",
            scheduled_at=_NOW,
        ),
        publish=publish,
    )

    assert result.is_success and result.value is not None
    submission = result.value
    assert publications == [submission.publication]
    assert submission.publication.event.metadata.correlation_id == _CORRELATION
    assert submission.publication.event.subject_reference == "run:subject-1"
    assert submission.publication.outbox.state.value == "pending"
    assert len(database._state.work_items) == 1
    assert len(database._state.audits) == 1
    assert len(database._state.events) == 1
    assert len(database._state.outbox) == 1


def test_transition_persists_claim_cancellation_audit_and_outbox_atomically() -> None:
    """Claim and cancellation transitions retain durable work metadata and append evidence."""
    database = InMemoryControlPlaneDatabase()
    service = _service(database, (1, 2, 3))
    created = service.submit(
        _ORGANIZATION,
        _CORRELATION,
        WorkCommand(
            kind=WorkKind.EVALUATION,
            subject_reference="evaluation:subject-1",
            idempotency_key="command-key-2",
            scheduled_at=_NOW,
        ),
    )
    assert created.is_success and created.value is not None
    initial = created.value.work_item
    observed: list[CommandPublication] = []

    def publish(publication: CommandPublication) -> None:
        observed.append(publication)
        assert database._state.events[publication.event.event_id] == publication.event
        assert database._state.outbox[publication.outbox.outbox_id] == publication.outbox
        assert database._state.work_transitions[initial.work_item_id]

    claimed = service.transition(
        _ORGANIZATION,
        _CORRELATION,
        initial.work_item_id,
        initial.metadata.version,
        WorkTransitionCommand(
            to_state=WorkState.CLAIMED,
            reason_code="worker_claimed",
            attempt=1,
            scheduled_at=_NOW + timedelta(minutes=1),
            claim_owner="worker-1",
            claim_expires_at=_NOW + timedelta(minutes=6),
        ),
        publish=publish,
    )
    assert claimed.is_success and claimed.value is not None
    claimed_item = claimed.value.work_item
    assert claimed_item.state is WorkState.CLAIMED
    assert claimed_item.claim_owner == "worker-1"
    assert claimed_item.attempt == 1
    assert claimed_item.subject_reference == initial.subject_reference
    assert claimed_item.idempotency_key == initial.idempotency_key

    cancelled = service.transition(
        _ORGANIZATION,
        _CORRELATION,
        initial.work_item_id,
        claimed_item.metadata.version,
        WorkTransitionCommand(
            to_state=WorkState.CANCELLED,
            reason_code="cancellation_requested",
            cancellation_requested=True,
        ),
        publish=publish,
    )

    assert cancelled.is_success and cancelled.value is not None
    cancelled_item = cancelled.value.work_item
    assert cancelled_item.state is WorkState.CANCELLED
    assert cancelled_item.cancellation_requested
    assert cancelled_item.claim_owner is None
    assert len(observed) == 2
    with database.unit_of_work() as unit_of_work:
        retained = unit_of_work.work_items.get(_ORGANIZATION, initial.work_item_id)
        transitions = unit_of_work.work_items.transitions(_ORGANIZATION, initial.work_item_id)

        assert retained.is_success and retained.value == cancelled_item
        assert transitions.is_success and transitions.value is not None
        assert tuple(item.to_state for item in transitions.value) == (
            WorkState.CLAIMED,
            WorkState.CANCELLED,
        )
    assert len(database._state.audits) == 3
    assert len(database._state.events) == 3
    assert len(database._state.outbox) == 3


def test_outbox_persistence_failure_rolls_back_work_and_skips_dispatch() -> None:
    """No work is dispatchable when its audit/event/outbox transaction cannot commit."""
    database = InMemoryControlPlaneDatabase()
    service = _service(database, (1, 1))
    dispatched: list[str] = []

    first = service.submit(
        _ORGANIZATION,
        _CORRELATION,
        WorkCommand(
            kind=WorkKind.CONTRIBUTION,
            subject_reference="contribution:subject-1",
            idempotency_key="command-key-3",
            scheduled_at=_NOW,
        ),
    )
    failed = service.submit(
        _ORGANIZATION,
        _CORRELATION,
        WorkCommand(
            kind=WorkKind.INDEXING,
            subject_reference="index:subject-1",
            idempotency_key="command-key-4",
            scheduled_at=_NOW,
        ),
        dispatch=lambda work_item: dispatched.append(str(work_item.work_item_id)),
    )

    assert first.is_success
    assert not failed.is_success
    assert dispatched == []
    assert len(database._state.work_items) == 1
    assert len(database._state.audits) == 1
    assert len(database._state.events) == 1
    assert len(database._state.outbox) == 1
