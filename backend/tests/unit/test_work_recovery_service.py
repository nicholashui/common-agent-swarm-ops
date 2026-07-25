"""Focused durable recovery tests for backend-redesign task 5.5."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from itertools import count
from typing import cast

import pytest

from app.core.command_service import CommandService, WorkTransitionCommand
from app.core.work_recovery import (
    FailureClassification,
    RecoveryAction,
    RecoveryDecision,
    WorkRecoveryPolicy,
    WorkRecoveryService,
)
from app.models.common import RecordMetadata
from app.models.control_plane import WorkItem, WorkItemId, WorkState
from app.models.identifiers import CorrelationId, OrganizationId, RecordId
from app.repositories.control_plane import (
    ControlPlaneUnitOfWork,
    InMemoryControlPlaneDatabase,
)

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_ORGANIZATION = OrganizationId("organization-recovery")
_CORRELATION = CorrelationId("correlation-recovery")


def _unit_of_work_factory(
    database: InMemoryControlPlaneDatabase,
) -> Callable[[], ControlPlaneUnitOfWork]:
    def factory() -> ControlPlaneUnitOfWork:
        return cast(ControlPlaneUnitOfWork, database.unit_of_work())

    return factory


def _claimed_work(
    work_item_id: str,
    *,
    attempt: int = 1,
    cancellation_requested: bool = False,
    expires_at: datetime = _NOW - timedelta(minutes=1),
) -> WorkItem:
    return WorkItem(
        metadata=RecordMetadata(
            record_id=RecordId(f"record-{work_item_id}"),
            organization_id=_ORGANIZATION,
            correlation_id=_CORRELATION,
            schema_version=1,
            version=1,
            created_at=_NOW,
            updated_at=_NOW,
        ),
        work_item_id=WorkItemId(work_item_id),
        subject_reference=f"run:{work_item_id}",
        attempt=attempt,
        idempotency_key=f"key-{work_item_id}",
        scheduled_at=_NOW,
        cancellation_requested=cancellation_requested,
        state=WorkState.CLAIMED,
        claim_owner="worker-1",
        claim_expires_at=expires_at,
    )


def _service(
    database: InMemoryControlPlaneDatabase,
    policy: WorkRecoveryPolicy,
) -> WorkRecoveryService:
    sequence = count(1)
    unit_of_work_factory = _unit_of_work_factory(database)
    command_service = CommandService(
        unit_of_work_factory,
        clock=lambda: _NOW,
        next_event_sequence=lambda: next(sequence),
    )
    return WorkRecoveryService(
        unit_of_work_factory,
        command_service,
        policy,
        clock=lambda: _NOW,
    )


def _store(database: InMemoryControlPlaneDatabase, work_item: WorkItem) -> None:
    with database.unit_of_work() as unit_of_work:
        assert unit_of_work.work_items.create(work_item).is_success


@pytest.mark.parametrize(
    ("decision", "expected_state", "expected_action", "dispatch_allowed"),
    (
        (RecoveryDecision.RECLAIM, WorkState.PENDING, RecoveryAction.RECLAIMED, True),
        (
            RecoveryDecision.MANUAL_RECOVERY,
            WorkState.MANUAL_RECOVERY,
            RecoveryAction.MANUAL_RECOVERY_REQUIRED,
            False,
        ),
        (RecoveryDecision.DEAD_LETTER, WorkState.DEAD_LETTER, RecoveryAction.DEAD_LETTERED, False),
    ),
)
def test_expired_claim_applies_each_validated_recovery_decision(
    decision: RecoveryDecision,
    expected_state: WorkState,
    expected_action: RecoveryAction,
    dispatch_allowed: bool,
) -> None:
    """Lease expiry retains one configured reclaim, manual, or dead-letter outcome."""
    database = InMemoryControlPlaneDatabase()
    original = _claimed_work("expired")
    _store(database, original)
    service = _service(
        database,
        WorkRecoveryPolicy(decision, RecoveryDecision.RECLAIM, 2, timedelta(seconds=30)),
    )

    recovered = service.recover_expired_claim(_ORGANIZATION, _CORRELATION, original.work_item_id)

    assert recovered.is_success and recovered.value is not None
    assert recovered.value.action is expected_action
    assert recovered.value.dispatch_allowed is dispatch_allowed
    assert recovered.value.work_item.state is expected_state
    with database.unit_of_work() as unit_of_work:
        current = unit_of_work.work_items.get(_ORGANIZATION, original.work_item_id)
        history = unit_of_work.work_items.transitions(_ORGANIZATION, original.work_item_id)
    assert current.is_success and current.value is not None
    assert current.value == recovered.value.work_item
    assert current.value.state is expected_state
    assert history.is_success and history.value is not None
    assert history.value[-1].to_state is expected_state


def test_worker_stop_uses_its_own_configured_decision() -> None:
    """A stopped owner is recovered using the worker-stop policy rather than lease policy."""
    database = InMemoryControlPlaneDatabase()
    original = _claimed_work("worker-stop", expires_at=_NOW + timedelta(minutes=5))
    _store(database, original)
    service = _service(
        database,
        WorkRecoveryPolicy(
            RecoveryDecision.RECLAIM,
            RecoveryDecision.MANUAL_RECOVERY,
            2,
            timedelta(),
        ),
    )

    recovered = service.recover_worker_stop(
        _ORGANIZATION, _CORRELATION, original.work_item_id, "worker-1"
    )

    assert recovered.is_success and recovered.value is not None
    assert recovered.value.action is RecoveryAction.MANUAL_RECOVERY_REQUIRED
    assert recovered.value.work_item.state is WorkState.MANUAL_RECOVERY


def test_transient_retry_is_bounded_and_cancellation_is_checked_before_retry() -> None:
    """Retries schedule once within policy; cancellation wins before another retry."""
    database = InMemoryControlPlaneDatabase()
    original = _claimed_work("retry")
    cancelled = _claimed_work("cancelled", cancellation_requested=True)
    _store(database, original)
    _store(database, cancelled)
    policy = WorkRecoveryPolicy(
        RecoveryDecision.RECLAIM,
        RecoveryDecision.RECLAIM,
        max_attempts=2,
        retry_delay=timedelta(seconds=30),
    )
    service = _service(database, policy)

    retry = service.handle_failure(
        _ORGANIZATION,
        _CORRELATION,
        original.work_item_id,
        (FailureClassification.TRANSIENT,),
    )
    assert retry.is_success and retry.value is not None
    assert retry.value.action is RecoveryAction.RETRY_SCHEDULED
    assert retry.value.dispatch_allowed
    assert retry.value.work_item.attempt == 2
    assert retry.value.work_item.scheduled_at == _NOW + timedelta(seconds=30)

    claim_service = CommandService(
        _unit_of_work_factory(database),
        clock=lambda: _NOW,
        next_event_sequence=lambda: 99,
    )
    reclaimed = claim_service.transition(
        _ORGANIZATION,
        _CORRELATION,
        original.work_item_id,
        retry.value.work_item.metadata.version,
        WorkTransitionCommand(
            to_state=WorkState.CLAIMED,
            reason_code="retry_claimed",
            claim_owner="worker-2",
            claim_expires_at=_NOW + timedelta(minutes=5),
        ),
    )
    assert reclaimed.is_success and reclaimed.value is not None
    exhausted = service.handle_failure(
        _ORGANIZATION,
        _CORRELATION,
        original.work_item_id,
        (FailureClassification.TRANSIENT,),
    )
    cancellation = service.handle_failure(
        _ORGANIZATION,
        _CORRELATION,
        cancelled.work_item_id,
        (FailureClassification.TRANSIENT,),
    )

    assert exhausted.is_success and exhausted.value is not None
    assert exhausted.value.action is RecoveryAction.RETRY_EXHAUSTED
    assert exhausted.value.work_item.state is WorkState.DEAD_LETTER
    assert cancellation.is_success and cancellation.value is not None
    assert cancellation.value.action is RecoveryAction.CANCELLED
    assert cancellation.value.work_item.state is WorkState.CANCELLED


@pytest.mark.parametrize(
    "terminal_classification",
    (
        FailureClassification.VALIDATION,
        FailureClassification.AUTHORIZATION,
        FailureClassification.POLICY,
        FailureClassification.RIGHTS_OR_CONSENT,
        FailureClassification.SCHEMA,
        FailureClassification.NON_IDEMPOTENT_AMBIGUITY,
    ),
)
def test_terminal_failure_classification_overrides_simultaneous_transient_failure(
    terminal_classification: FailureClassification,
) -> None:
    """Every terminal class fail-closes a combined transient classification without retry."""
    database = InMemoryControlPlaneDatabase()
    original = _claimed_work(f"terminal-{terminal_classification.value}")
    _store(database, original)
    service = _service(
        database,
        WorkRecoveryPolicy(RecoveryDecision.RECLAIM, RecoveryDecision.RECLAIM, 3, timedelta()),
    )

    recovered = service.handle_failure(
        _ORGANIZATION,
        _CORRELATION,
        original.work_item_id,
        (FailureClassification.TRANSIENT, terminal_classification),
    )

    assert recovered.is_success and recovered.value is not None
    assert recovered.value.action is RecoveryAction.NON_AUTOMATIC_RETRYABLE
    assert not recovered.value.dispatch_allowed
    assert recovered.value.work_item.state is WorkState.FAILED
    assert recovered.value.work_item.retry_classifications == (
        FailureClassification.TRANSIENT.value,
        terminal_classification.value,
    )


def test_duplicate_dispatch_replays_governed_work_without_subject_mutation() -> None:
    """A duplicate receives the existing idempotent outcome and creates no transition or event."""
    database = InMemoryControlPlaneDatabase()
    original = _claimed_work("duplicate")
    _store(database, original)
    service = _service(
        database,
        WorkRecoveryPolicy(RecoveryDecision.RECLAIM, RecoveryDecision.RECLAIM, 2, timedelta()),
    )

    duplicate = service.resolve_duplicate_dispatch(
        _ORGANIZATION, _CORRELATION, original.work_item_id
    )

    assert duplicate.is_success and duplicate.value is not None
    assert duplicate.value.action is RecoveryAction.DUPLICATE_REPLAY
    assert duplicate.value.duplicate
    assert not duplicate.value.dispatch_allowed
    assert duplicate.value.work_item == original
    with database.unit_of_work() as unit_of_work:
        current = unit_of_work.work_items.get(_ORGANIZATION, original.work_item_id)
        transitions = unit_of_work.work_items.transitions(_ORGANIZATION, original.work_item_id)
    assert current.is_success and current.value == original
    assert transitions.is_success and transitions.value == ()
