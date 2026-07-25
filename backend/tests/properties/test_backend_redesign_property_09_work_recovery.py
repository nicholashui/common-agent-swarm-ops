"""Property checks for bounded, fail-closed durable work recovery."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from itertools import count
from typing import cast

from hypothesis import given, settings, strategies as st

from app.core.command_service import CommandService
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
_ORGANIZATION = OrganizationId("property-9-organization")
_CORRELATION = CorrelationId("property-9-correlation")
_SAFE_SUFFIXES = st.text(alphabet="abcdefghijklmnopqrstuvwxyz0123456789", min_size=1, max_size=12)
_RECOVERY_DECISIONS = st.sampled_from(tuple(RecoveryDecision))
_TERMINAL_CLASSIFICATIONS = st.sampled_from(
    tuple(
        classification
        for classification in FailureClassification
        if classification is not FailureClassification.TRANSIENT
    )
)
_RETRY_PLANS = st.integers(min_value=1, max_value=5).flatmap(
    lambda max_attempts: st.tuples(
        st.just(max_attempts),
        st.integers(min_value=1, max_value=max_attempts),
        st.integers(min_value=0, max_value=300),
    )
)


def _unit_of_work_factory(
    database: InMemoryControlPlaneDatabase,
) -> Callable[[], ControlPlaneUnitOfWork]:
    def factory() -> ControlPlaneUnitOfWork:
        return cast(ControlPlaneUnitOfWork, database.unit_of_work())

    return factory


def _claimed_work(
    work_item_id: str,
    *,
    attempt: int,
    cancellation_requested: bool = False,
    expires_at: datetime,
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
    event_sequences = count(1)
    unit_of_work_factory = _unit_of_work_factory(database)
    command_service = CommandService(
        unit_of_work_factory,
        clock=lambda: _NOW,
        next_event_sequence=lambda: next(event_sequences),
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


def _expected_interruption(
    decision: RecoveryDecision,
) -> tuple[WorkState, RecoveryAction, bool]:
    if decision is RecoveryDecision.RECLAIM:
        return WorkState.PENDING, RecoveryAction.RECLAIMED, True
    if decision is RecoveryDecision.MANUAL_RECOVERY:
        return WorkState.MANUAL_RECOVERY, RecoveryAction.MANUAL_RECOVERY_REQUIRED, False
    return WorkState.DEAD_LETTER, RecoveryAction.DEAD_LETTERED, False


# Feature: backend-redesign, Property 9: Work recovery is bounded and fail-closed.
# **Validates: Requirements 5.4, 5.5, 5.6, 5.7, 5.8**
@settings(max_examples=100)
@given(
    suffix=_SAFE_SUFFIXES,
    claim_expiry_seconds=st.integers(min_value=0, max_value=3600),
    claim_decision=_RECOVERY_DECISIONS,
    worker_stop_decision=_RECOVERY_DECISIONS,
    retry_plan=_RETRY_PLANS,
    cancellation_requested=st.booleans(),
    terminal_classification=_TERMINAL_CLASSIFICATIONS,
)
def test_property_9_work_recovery_is_bounded_and_fail_closed(
    suffix: str,
    claim_expiry_seconds: int,
    claim_decision: RecoveryDecision,
    worker_stop_decision: RecoveryDecision,
    retry_plan: tuple[int, int, int],
    cancellation_requested: bool,
    terminal_classification: FailureClassification,
) -> None:
    """Configured recovery is exact, bounded, and terminal classes override transient."""
    max_attempts, attempt, retry_delay_seconds = retry_plan
    policy = WorkRecoveryPolicy(
        claim_expiry_decision=claim_decision,
        worker_stop_decision=worker_stop_decision,
        max_attempts=max_attempts,
        retry_delay=timedelta(seconds=retry_delay_seconds),
    )

    expired_database = InMemoryControlPlaneDatabase()
    expired = _claimed_work(
        f"{suffix}-expired",
        attempt=attempt,
        expires_at=_NOW - timedelta(seconds=claim_expiry_seconds),
    )
    _store(expired_database, expired)
    expired_outcome = _service(expired_database, policy).recover_expired_claim(
        _ORGANIZATION,
        _CORRELATION,
        expired.work_item_id,
    )
    expected_state, expected_action, expected_dispatch = _expected_interruption(claim_decision)
    assert expired_outcome.is_success and expired_outcome.value is not None
    assert expired_outcome.value.action is expected_action
    assert expired_outcome.value.dispatch_allowed is expected_dispatch
    assert expired_outcome.value.work_item.state is expected_state

    stopped_database = InMemoryControlPlaneDatabase()
    stopped = _claimed_work(
        f"{suffix}-stopped",
        attempt=attempt,
        expires_at=_NOW + timedelta(minutes=1),
    )
    _store(stopped_database, stopped)
    stopped_outcome = _service(stopped_database, policy).recover_worker_stop(
        _ORGANIZATION,
        _CORRELATION,
        stopped.work_item_id,
        "worker-1",
    )
    expected_state, expected_action, expected_dispatch = _expected_interruption(
        worker_stop_decision
    )
    assert stopped_outcome.is_success and stopped_outcome.value is not None
    assert stopped_outcome.value.action is expected_action
    assert stopped_outcome.value.dispatch_allowed is expected_dispatch
    assert stopped_outcome.value.work_item.state is expected_state

    retry_database = InMemoryControlPlaneDatabase()
    retry_work = _claimed_work(
        f"{suffix}-retry",
        attempt=attempt,
        cancellation_requested=cancellation_requested,
        expires_at=_NOW + timedelta(minutes=1),
    )
    _store(retry_database, retry_work)
    retry_outcome = _service(retry_database, policy).handle_failure(
        _ORGANIZATION,
        _CORRELATION,
        retry_work.work_item_id,
        (FailureClassification.TRANSIENT,),
    )
    assert retry_outcome.is_success and retry_outcome.value is not None
    if cancellation_requested:
        assert retry_outcome.value.action is RecoveryAction.CANCELLED
        assert retry_outcome.value.work_item.state is WorkState.CANCELLED
        assert not retry_outcome.value.dispatch_allowed
    elif attempt >= max_attempts:
        assert retry_outcome.value.action is RecoveryAction.RETRY_EXHAUSTED
        assert retry_outcome.value.work_item.state is WorkState.DEAD_LETTER
        assert not retry_outcome.value.dispatch_allowed
    else:
        assert retry_outcome.value.action is RecoveryAction.RETRY_SCHEDULED
        assert retry_outcome.value.work_item.state is WorkState.PENDING
        assert retry_outcome.value.work_item.attempt == attempt + 1
        assert retry_outcome.value.work_item.scheduled_at == _NOW + timedelta(
            seconds=retry_delay_seconds
        )
        assert retry_outcome.value.dispatch_allowed

    terminal_database = InMemoryControlPlaneDatabase()
    terminal_work = _claimed_work(
        f"{suffix}-terminal",
        attempt=attempt,
        expires_at=_NOW + timedelta(minutes=1),
    )
    _store(terminal_database, terminal_work)
    terminal_outcome = _service(terminal_database, policy).handle_failure(
        _ORGANIZATION,
        _CORRELATION,
        terminal_work.work_item_id,
        (FailureClassification.TRANSIENT, terminal_classification),
    )
    assert terminal_outcome.is_success and terminal_outcome.value is not None
    assert terminal_outcome.value.action is RecoveryAction.NON_AUTOMATIC_RETRYABLE
    assert terminal_outcome.value.work_item.state is WorkState.FAILED
    assert not terminal_outcome.value.dispatch_allowed
    assert terminal_outcome.value.work_item.retry_classifications == (
        FailureClassification.TRANSIENT.value,
        terminal_classification.value,
    )

    duplicate_database = InMemoryControlPlaneDatabase()
    duplicate_work = _claimed_work(
        f"{suffix}-duplicate",
        attempt=attempt,
        expires_at=_NOW + timedelta(minutes=1),
    )
    _store(duplicate_database, duplicate_work)
    duplicate_outcome = _service(duplicate_database, policy).resolve_duplicate_dispatch(
        _ORGANIZATION,
        _CORRELATION,
        duplicate_work.work_item_id,
    )
    assert duplicate_outcome.is_success and duplicate_outcome.value is not None
    assert duplicate_outcome.value.action is RecoveryAction.DUPLICATE_REPLAY
    assert duplicate_outcome.value.duplicate
    assert not duplicate_outcome.value.dispatch_allowed
    assert duplicate_outcome.value.work_item == duplicate_work
    with duplicate_database.unit_of_work() as unit_of_work:
        current = unit_of_work.work_items.get(_ORGANIZATION, duplicate_work.work_item_id)
        transitions = unit_of_work.work_items.transitions(
            _ORGANIZATION,
            duplicate_work.work_item_id,
        )
    assert current.is_success and current.value == duplicate_work
    assert transitions.is_success and transitions.value == ()
