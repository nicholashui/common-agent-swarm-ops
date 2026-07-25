"""Durable command boundary for governed asynchronous work."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import datetime
from enum import StrEnum
from itertools import count

from app.models.common import SCHEMA_VERSION, RecordMetadata, utc_now
from app.models.contracts import ErrorCode, ErrorDetail, Result
from app.models.control_plane import (
    AuditRecord,
    DeliveryState,
    EventId,
    OperationalEvent,
    OutboxId,
    OutboxRecord,
    WorkItem,
    WorkItemId,
    WorkState,
    WorkTransition,
)
from app.models.identifiers import CorrelationId, OrganizationId, new_record_id
from app.repositories.control_plane import ControlPlaneUnitOfWork


class WorkKind(StrEnum):
    """The asynchronous commands governed by the common durable work boundary."""

    RUN = "run"
    EVALUATION = "evaluation"
    CONTRIBUTION = "contribution"
    INDEXING = "indexing"
    ROLLOUT = "rollout"


@dataclass(frozen=True, slots=True)
class WorkCommand:
    """Server-validated data retained before a work item becomes dispatchable."""

    kind: WorkKind
    subject_reference: str
    idempotency_key: str
    scheduled_at: datetime
    attempt: int = 0
    cancellation_requested: bool = False
    claim_owner: str | None = None
    claim_expires_at: datetime | None = None
    retry_classifications: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class WorkTransitionCommand:
    """The mutable recovery/claim state for one versioned work transition."""

    to_state: WorkState
    reason_code: str
    attempt: int | None = None
    scheduled_at: datetime | None = None
    cancellation_requested: bool | None = None
    claim_owner: str | None = None
    claim_expires_at: datetime | None = None
    retry_classifications: tuple[str, ...] | None = None


@dataclass(frozen=True, slots=True)
class CommandPublication:
    """A committed event and delivery record passed only to post-commit publishers."""

    event: OperationalEvent
    outbox: OutboxRecord


@dataclass(frozen=True, slots=True)
class CommandSubmission:
    """The durable command outcome; post-commit dispatch is deliberately best effort."""

    work_item: WorkItem
    publication: CommandPublication
    dispatch_error: ErrorDetail | None = None


DispatchCallback = Callable[[WorkItem], None]
PublicationCallback = Callable[[CommandPublication], None]
UnitOfWorkFactory = Callable[[], ControlPlaneUnitOfWork]


def _is_work_kind(value: object) -> bool:
    """Validate a runtime command value that may have crossed an untyped boundary."""
    return isinstance(value, WorkKind)


def _is_work_state(value: object) -> bool:
    """Validate a runtime transition value that may have crossed an untyped boundary."""
    return isinstance(value, WorkState)


class CommandService:
    """Persist command work and transition evidence before any external effect is invoked."""

    def __init__(
        self,
        unit_of_work_factory: UnitOfWorkFactory,
        *,
        clock: Callable[[], datetime] = utc_now,
        next_event_sequence: Callable[[], int] | None = None,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._clock = clock
        sequence = count(1)
        self._next_event_sequence = next_event_sequence or (lambda: next(sequence))

    def submit(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        command: WorkCommand,
        *,
        dispatch: DispatchCallback | None = None,
        publish: PublicationCallback | None = None,
    ) -> Result[CommandSubmission, ErrorDetail]:
        """Commit a pending work item, audit evidence, and outbox row before dispatching it."""
        invalid = self._command_error(correlation_id, command)
        if invalid is not None:
            return Result.failure(invalid)
        now = self._clock()
        work_item = WorkItem(
            metadata=self._metadata(organization_id, correlation_id, now),
            work_item_id=WorkItemId(str(new_record_id())),
            subject_reference=command.subject_reference,
            attempt=command.attempt,
            idempotency_key=command.idempotency_key,
            scheduled_at=command.scheduled_at,
            cancellation_requested=command.cancellation_requested,
            state=WorkState.PENDING,
            claim_owner=command.claim_owner,
            claim_expires_at=command.claim_expires_at,
            retry_classifications=command.retry_classifications,
        )
        if work_item.claim_owner is not None or work_item.claim_expires_at is not None:
            return Result.failure(
                self._validation_error(
                    correlation_id,
                    "New work items cannot carry a worker claim.",
                )
            )
        publication = self._creation_publication(work_item, command.kind, now)
        persisted = self._persist_new(work_item, command.kind, publication, correlation_id)
        if not persisted.is_success:
            return Result.failure(self._error(persisted.error, correlation_id))
        return Result.success(self._notify(work_item, publication, dispatch, publish))

    def submit_in_transaction(
        self,
        unit_of_work: ControlPlaneUnitOfWork,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        command: WorkCommand,
    ) -> Result[CommandSubmission, ErrorDetail]:
        """Persist work in an existing transaction; callers deliver it only after commit."""
        invalid = self._command_error(correlation_id, command)
        if invalid is not None:
            return Result.failure(invalid)
        now = self._clock()
        work_item = WorkItem(
            metadata=self._metadata(organization_id, correlation_id, now),
            work_item_id=WorkItemId(str(new_record_id())),
            subject_reference=command.subject_reference,
            attempt=command.attempt,
            idempotency_key=command.idempotency_key,
            scheduled_at=command.scheduled_at,
            cancellation_requested=command.cancellation_requested,
            state=WorkState.PENDING,
            claim_owner=command.claim_owner,
            claim_expires_at=command.claim_expires_at,
            retry_classifications=command.retry_classifications,
        )
        if work_item.claim_owner is not None or work_item.claim_expires_at is not None:
            return Result.failure(
                self._validation_error(
                    correlation_id, "New work items cannot carry a worker claim."
                )
            )
        publication = self._creation_publication(work_item, command.kind, now)
        persisted = self._persist_new_in_transaction(
            unit_of_work, work_item, command.kind, publication, correlation_id
        )
        if not persisted.is_success:
            return Result.failure(persisted.error or self._error(None, correlation_id))
        return Result.success(CommandSubmission(work_item=work_item, publication=publication))

    def deliver(
        self,
        submission: CommandSubmission,
        *,
        dispatch: DispatchCallback | None = None,
        publish: PublicationCallback | None = None,
    ) -> CommandSubmission:
        """Deliver a committed in-transaction submission through the common work boundary."""
        return self._notify(submission.work_item, submission.publication, dispatch, publish)

    def transition(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        work_item_id: WorkItemId,
        expected_work_version: int,
        command: WorkTransitionCommand,
        *,
        publish: PublicationCallback | None = None,
    ) -> Result[CommandSubmission, ErrorDetail]:
        """Atomically persist one state change with its transition, audit, and outbox evidence."""
        if expected_work_version < 1:
            return Result.failure(
                self._validation_error(correlation_id, "Expected work version must be positive.")
            )
        with self._unit_of_work_factory() as unit_of_work:
            current_result = unit_of_work.work_items.get(organization_id, work_item_id)
            if not current_result.is_success or current_result.value is None:
                return Result.failure(self._error(current_result.error, correlation_id))
            current = current_result.value
            invalid = self._transition_error(
                correlation_id, current, expected_work_version, command
            )
            if invalid is not None:
                return Result.failure(invalid)
            now = self._clock()
            updated = self._updated_work_item(current, command, now)
            transition = WorkTransition(
                metadata=self._metadata(organization_id, correlation_id, now),
                transition_id=str(new_record_id()),
                work_item_id=current.work_item_id,
                from_state=current.state,
                to_state=command.to_state,
                recorded_at=now,
                reason_code=command.reason_code,
            )
            publication = self._transition_publication(updated, transition, now)
            results = (
                unit_of_work.work_items.replace(updated, expected_work_version),
                unit_of_work.work_items.append_transition(transition),
                unit_of_work.events.append_audit(
                    self._audit(
                        updated,
                        f"work.{command.to_state}.transitioned",
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
                return Result.failure(self._error(failed, correlation_id))
        return Result.success(self._notify(updated, publication, None, publish))

    def _persist_new(
        self,
        work_item: WorkItem,
        kind: WorkKind,
        publication: CommandPublication,
        correlation_id: CorrelationId,
    ) -> Result[WorkItem, ErrorDetail]:
        with self._unit_of_work_factory() as unit_of_work:
            results = (
                unit_of_work.work_items.create(work_item),
                unit_of_work.events.append_audit(
                    self._audit(
                        work_item,
                        f"work.{kind}.created",
                        work_item.metadata.created_at,
                    )
                ),
                unit_of_work.events.append_event(publication.event),
                unit_of_work.events.append_outbox(publication.outbox),
            )
            failed = next((result.error for result in results if not result.is_success), None)
            if failed is not None:
                unit_of_work.rollback()
                return Result.failure(self._error(failed, correlation_id))
        return Result.success(work_item)

    def _persist_new_in_transaction(
        self,
        unit_of_work: ControlPlaneUnitOfWork,
        work_item: WorkItem,
        kind: WorkKind,
        publication: CommandPublication,
        correlation_id: CorrelationId,
    ) -> Result[WorkItem, ErrorDetail]:
        results = (
            unit_of_work.work_items.create(work_item),
            unit_of_work.events.append_audit(
                self._audit(work_item, f"work.{kind}.created", work_item.metadata.created_at)
            ),
            unit_of_work.events.append_event(publication.event),
            unit_of_work.events.append_outbox(publication.outbox),
        )
        failed = next((result.error for result in results if not result.is_success), None)
        if failed is not None:
            return Result.failure(self._error(failed, correlation_id))
        return Result.success(work_item)

    def _creation_publication(
        self, work_item: WorkItem, kind: WorkKind, now: datetime
    ) -> CommandPublication:
        return self._publication(
            work_item,
            event_type=f"work.{kind}.created",
            payload={
                "work_item_id": str(work_item.work_item_id),
                "kind": kind.value,
                "state": work_item.state.value,
                "attempt": work_item.attempt,
                "scheduled_at": work_item.scheduled_at.isoformat(),
                "cancellation_requested": work_item.cancellation_requested,
            },
            now=now,
        )

    def _transition_publication(
        self, work_item: WorkItem, transition: WorkTransition, now: datetime
    ) -> CommandPublication:
        return self._publication(
            work_item,
            event_type="work.transitioned",
            payload={
                "work_item_id": str(work_item.work_item_id),
                "from_state": transition.from_state.value,
                "to_state": transition.to_state.value,
                "reason_code": transition.reason_code,
                "attempt": work_item.attempt,
                "cancellation_requested": work_item.cancellation_requested,
            },
            now=now,
            correlation_id=transition.metadata.correlation_id,
        )

    def _publication(
        self,
        work_item: WorkItem,
        *,
        event_type: str,
        payload: dict[str, object],
        now: datetime,
        correlation_id: CorrelationId | None = None,
    ) -> CommandPublication:
        event_id = EventId(str(new_record_id()))
        metadata = self._metadata(
            work_item.metadata.organization_id,
            correlation_id or work_item.metadata.correlation_id,
            now,
        )
        event = OperationalEvent(
            metadata=metadata,
            event_id=event_id,
            sequence=self._next_event_sequence(),
            event_type=event_type,
            subject_reference=work_item.subject_reference,
            occurred_at=now,
            payload_schema_version=SCHEMA_VERSION,
            redacted_payload=payload,
        )
        return CommandPublication(
            event=event,
            outbox=OutboxRecord(
                metadata=self._metadata(
                    work_item.metadata.organization_id,
                    correlation_id or work_item.metadata.correlation_id,
                    now,
                ),
                outbox_id=OutboxId(str(new_record_id())),
                event_id=event_id,
                state=DeliveryState.PENDING,
                created_at=now,
            ),
        )

    def _updated_work_item(
        self, current: WorkItem, command: WorkTransitionCommand, now: datetime
    ) -> WorkItem:
        attempt = current.attempt if command.attempt is None else command.attempt
        scheduled_at = (
            current.scheduled_at if command.scheduled_at is None else command.scheduled_at
        )
        cancellation_requested = (
            current.cancellation_requested
            if command.cancellation_requested is None
            else command.cancellation_requested
        ) or command.to_state is WorkState.CANCELLED
        return replace(
            current,
            metadata=replace(
                current.metadata,
                version=current.metadata.version + 1,
                updated_at=now,
            ),
            attempt=attempt,
            scheduled_at=scheduled_at,
            cancellation_requested=cancellation_requested,
            state=command.to_state,
            claim_owner=command.claim_owner if command.to_state is WorkState.CLAIMED else None,
            claim_expires_at=(
                command.claim_expires_at if command.to_state is WorkState.CLAIMED else None
            ),
            retry_classifications=(
                current.retry_classifications
                if command.retry_classifications is None
                else command.retry_classifications
            ),
        )

    def _command_error(
        self, correlation_id: CorrelationId, command: WorkCommand
    ) -> ErrorDetail | None:
        if not _is_work_kind(command.kind):
            return self._validation_error(correlation_id, "Work kind is invalid.")
        if not command.subject_reference.strip():
            return self._validation_error(correlation_id, "Work subject reference is required.")
        if not command.idempotency_key.strip():
            return self._validation_error(
                correlation_id, "A non-empty idempotency key is required."
            )
        if command.attempt < 0:
            return self._validation_error(correlation_id, "Work attempt must not be negative.")
        if command.scheduled_at.tzinfo is None:
            return self._validation_error(correlation_id, "Work schedule must include a timezone.")
        if command.claim_owner is not None or command.claim_expires_at is not None:
            return self._validation_error(
                correlation_id, "New work items cannot carry a worker claim."
            )
        return None

    def _transition_error(
        self,
        correlation_id: CorrelationId,
        current: WorkItem,
        expected_work_version: int,
        command: WorkTransitionCommand,
    ) -> ErrorDetail | None:
        if current.metadata.version != expected_work_version:
            return ErrorDetail(
                ErrorCode.CONFLICT, "Work item changed before transition.", correlation_id
            )
        if not command.reason_code.strip():
            return self._validation_error(correlation_id, "Work transition reason is required.")
        if not _is_work_state(command.to_state):
            return self._validation_error(correlation_id, "Work transition state is invalid.")
        terminal_states = {
            WorkState.COMPLETE,
            WorkState.FAILED,
            WorkState.CANCELLED,
            WorkState.MANUAL_RECOVERY,
            WorkState.DEAD_LETTER,
        }
        if current.state in terminal_states:
            return ErrorDetail(
                ErrorCode.INVALID_TRANSITION,
                "Terminal work cannot transition again.",
                correlation_id,
            )
        allowed_states = {
            WorkState.PENDING: {WorkState.CLAIMED, WorkState.CANCELLED, WorkState.DEAD_LETTER},
            WorkState.CLAIMED: {
                WorkState.PENDING,
                WorkState.COMPLETE,
                WorkState.FAILED,
                WorkState.CANCELLED,
                WorkState.MANUAL_RECOVERY,
                WorkState.DEAD_LETTER,
            },
        }
        if command.to_state not in allowed_states.get(current.state, set()):
            return ErrorDetail(
                ErrorCode.INVALID_TRANSITION,
                "Work transition is not allowed.",
                correlation_id,
            )
        next_attempt = current.attempt if command.attempt is None else command.attempt
        if next_attempt < current.attempt:
            return self._validation_error(correlation_id, "Work attempt cannot decrease.")
        if command.scheduled_at is not None and command.scheduled_at.tzinfo is None:
            return self._validation_error(correlation_id, "Work schedule must include a timezone.")
        if current.cancellation_requested and command.to_state is not WorkState.CANCELLED:
            return ErrorDetail(
                ErrorCode.INVALID_TRANSITION,
                "Cancelled work cannot be dispatched.",
                correlation_id,
            )
        if command.to_state is WorkState.CLAIMED:
            if not command.claim_owner or command.claim_expires_at is None:
                return self._validation_error(
                    correlation_id, "Claimed work requires a worker and lease expiry."
                )
            if command.claim_expires_at.tzinfo is None:
                return self._validation_error(
                    correlation_id, "Work claim expiry must include a timezone."
                )
        elif command.claim_owner is not None or command.claim_expires_at is not None:
            return self._validation_error(
                correlation_id, "Only claimed work can carry worker claim details."
            )
        return None

    def _audit(
        self,
        work_item: WorkItem,
        action: str,
        now: datetime,
        correlation_id: CorrelationId | None = None,
    ) -> AuditRecord:
        return AuditRecord(
            metadata=self._metadata(
                work_item.metadata.organization_id,
                correlation_id or work_item.metadata.correlation_id,
                now,
            ),
            audit_id=str(new_record_id()),
            action=action,
            subject_reference=work_item.subject_reference,
            outcome=work_item.state.value,
            recorded_at=now,
        )

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

    def _notify(
        self,
        work_item: WorkItem,
        publication: CommandPublication,
        dispatch: DispatchCallback | None,
        publish: PublicationCallback | None,
    ) -> CommandSubmission:
        try:
            if dispatch is not None:
                dispatch(work_item)
            if publish is not None:
                publish(publication)
        except Exception:
            return CommandSubmission(
                work_item=work_item,
                publication=publication,
                dispatch_error=ErrorDetail(
                    ErrorCode.REPOSITORY_UNAVAILABLE,
                    "Post-commit work delivery is pending recovery.",
                    publication.event.metadata.correlation_id,
                    retryable=True,
                ),
            )
        return CommandSubmission(work_item=work_item, publication=publication)

    @staticmethod
    def _validation_error(correlation_id: CorrelationId, message: str) -> ErrorDetail:
        return ErrorDetail(ErrorCode.VALIDATION_FAILED, message, correlation_id)

    @staticmethod
    def _error(error: ErrorDetail | None, correlation_id: CorrelationId) -> ErrorDetail:
        if error is None:
            return ErrorDetail(
                ErrorCode.REPOSITORY_UNAVAILABLE,
                "Durable command storage is unavailable.",
                correlation_id,
                retryable=True,
            )
        return replace(error, correlation_id=correlation_id)
