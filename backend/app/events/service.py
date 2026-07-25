"""Authorized, redacted publication and projection services for backend-redesign task 12.1."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import Protocol, runtime_checkable

from app.api.v1.dependencies import (
    AuthenticatedRequestContext,
    AuthorizationAction,
    AuthorizationService,
    PermissionAuthorizationService,
    ProtectedOperation,
)
from app.api.v1.errors import PublicApiException
from app.models.common import RecordMetadata
from app.models.contracts import ErrorCode, ErrorDetail, Result
from app.models.control_plane import (
    DeliveryState,
    EventReplayWindow,
    OperationalEvent,
    OutboxId,
    OutboxRecord,
    ReplayRecoveryOutcome,
    ReplayRecoveryReason,
)
from app.models.identifiers import CorrelationId, OrganizationId, RecordId, new_record_id
from app.models.redaction import RedactionService, RedactionSurface


class FreshnessState(StrEnum):
    """The independently evaluated freshness of the underlying projection data."""

    CURRENT = "current"
    STALE = "stale"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True, slots=True)
class CommittedOutboxPublication:
    """An event/outbox pair visible only after their enclosing transaction has committed."""

    outbox: OutboxRecord
    event: OperationalEvent


@dataclass(frozen=True, slots=True)
class PublishedOperationalEvent:
    """The complete, redacted metadata envelope delivered to an authorized subscriber."""

    sequence: int
    event_type: str
    topic: str
    subject_reference: str
    occurred_at: datetime
    correlation_id: CorrelationId
    payload_schema_version: int
    redacted_payload: Mapping[str, object]


@dataclass(frozen=True, slots=True)
class ActivityProjectionSource:
    """A protected read-model value before trusted-context authorization and redaction."""

    metadata: RecordMetadata
    subject_reference: str
    payload: Mapping[str, object]
    as_of: datetime
    freshness: FreshnessState
    delayed: bool = False
    degraded: bool = False

    def __post_init__(self) -> None:
        if not self.subject_reference.strip():
            raise ValueError("subject_reference must be non-empty.")
        if self.as_of.tzinfo is None:
            raise ValueError("as_of must be timezone-aware.")


@dataclass(frozen=True, slots=True)
class ActivityProjection:
    """An authorized redacted read model with explicit freshness and delivery health."""

    subject_reference: str
    correlation_id: CorrelationId
    payload: Mapping[str, object]
    as_of: datetime
    freshness: FreshnessState
    delayed: bool
    degraded: bool

    @property
    def delayed_or_degraded(self) -> bool:
        """Return the dashboard indicator without changing underlying freshness."""
        return self.delayed or self.degraded


@runtime_checkable
class CommittedOutboxStore(Protocol):
    """Read and transition only delivery records visible after transaction commit."""

    def pending(
        self, organization_id: OrganizationId
    ) -> Result[tuple[CommittedOutboxPublication, ...], ErrorDetail]: ...

    def mark_published(
        self, organization_id: OrganizationId, outbox_id: OutboxId
    ) -> Result[OutboxRecord, ErrorDetail]: ...


EventSink = Callable[[PublishedOperationalEvent], None]


@dataclass(frozen=True, slots=True)
class EventReplayPolicy:
    """Validated policy for bounded retained-event replay."""

    replay_permitted: bool = True
    maximum_events: int = 100

    def __post_init__(self) -> None:
        if self.maximum_events < 1:
            raise ValueError("maximum_events must be positive.")


@dataclass(frozen=True, slots=True)
class RecoveryResponse:
    """Stable replay response directing a client to refresh its activity projection."""

    refresh_activity_projection: bool = True


@dataclass(frozen=True, slots=True)
class EventReplayResponse:
    """A replay delivers one exact sequence or a recovery response, never both."""

    events: tuple[PublishedOperationalEvent, ...] = ()
    recovery: RecoveryResponse | None = None

    def __post_init__(self) -> None:
        if self.events and self.recovery is not None:
            raise ValueError("Replay responses cannot contain events and recovery together.")


@runtime_checkable
class EventReplayStore(Protocol):
    """Retained-event reads and append-only recovery outcomes for replay handling."""

    def replay_window(
        self,
        organization_id: OrganizationId,
        topic: str,
        after_sequence: int,
        maximum_events: int,
    ) -> Result[EventReplayWindow, ErrorDetail]: ...

    def append_replay_recovery(
        self, record: ReplayRecoveryOutcome
    ) -> Result[ReplayRecoveryOutcome, ErrorDetail]: ...


class EventReplayService:
    """Prepare an authorized exact replay before an SSE transport emits its first event."""

    def __init__(
        self,
        store: EventReplayStore,
        authorization_service: AuthorizationService | None = None,
        redactor: RedactionService | None = None,
        *,
        clock: Callable[[], datetime] = lambda: datetime.now(UTC),
        record_id_factory: Callable[[], RecordId] = new_record_id,
    ) -> None:
        self._store = store
        self._authorization_service = authorization_service or PermissionAuthorizationService()
        self._redactor = redactor or RedactionService()
        self._clock = clock
        self._record_id_factory = record_id_factory

    def replay(
        self,
        context: AuthenticatedRequestContext,
        topic: str,
        cursor_sequence: int,
        policy: EventReplayPolicy,
    ) -> Result[EventReplayResponse, ErrorDetail]:
        """Return an all-or-nothing exact replay after validating its entire bounded window."""
        if not topic.strip() or cursor_sequence < 0:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.VALIDATION_FAILED,
                    "A valid event topic and replay cursor are required.",
                    context.correlation_id,
                )
            )
        for operation in (
            ProtectedOperation(AuthorizationAction.REPLAY, "event-stream:connection"),
            ProtectedOperation(AuthorizationAction.TOPIC, f"topic:{topic}"),
        ):
            denial = self._authorize(context, operation)
            if denial is not None:
                return Result.failure(denial)

        if not policy.replay_permitted:
            return self._recover(
                context, topic, cursor_sequence, ReplayRecoveryReason.POLICY_DIRECTED
            )

        window_result = self._store.replay_window(
            context.organization_id, topic, cursor_sequence, policy.maximum_events
        )
        if not window_result.is_success or window_result.value is None:
            return Result.failure(self._store_error(context.correlation_id))
        window = window_result.value
        recovery_reason = self._recovery_reason(window, cursor_sequence, policy.maximum_events)
        if recovery_reason is not None:
            return self._recover(context, topic, cursor_sequence, recovery_reason)

        deliveries: list[PublishedOperationalEvent] = []
        for event in window.events:
            denial = self._authorize_candidate(context, topic, event)
            if denial is not None:
                return Result.failure(denial)
            deliveries.append(self._delivery(event))
        return Result.success(EventReplayResponse(events=tuple(deliveries)))

    @staticmethod
    def _recovery_reason(
        window: EventReplayWindow, cursor_sequence: int, maximum_events: int
    ) -> ReplayRecoveryReason | None:
        if cursor_sequence > window.high_watermark:
            return ReplayRecoveryReason.CURSOR_UNAVAILABLE
        expected_sequence = cursor_sequence + 1
        for event in window.events:
            if event.sequence != expected_sequence:
                if event.sequence > expected_sequence:
                    return ReplayRecoveryReason.SEQUENCE_GAP
                return ReplayRecoveryReason.NON_CONTIGUOUS
            expected_sequence += 1
        if expected_sequence <= window.high_watermark and len(window.events) < maximum_events:
            return ReplayRecoveryReason.SEQUENCE_GAP
        return None

    def _recover(
        self,
        context: AuthenticatedRequestContext,
        topic: str,
        cursor_sequence: int,
        reason: ReplayRecoveryReason,
    ) -> Result[EventReplayResponse, ErrorDetail]:
        now = self._clock()
        outcome = ReplayRecoveryOutcome(
            metadata=RecordMetadata(
                record_id=self._record_id_factory(),
                organization_id=context.organization_id,
                correlation_id=context.correlation_id,
                schema_version=1,
                version=1,
                created_at=now,
                updated_at=now,
            ),
            topic=topic,
            cursor_sequence=cursor_sequence,
            reason=reason,
            recorded_at=now,
        )
        persisted = self._store.append_replay_recovery(outcome)
        if not persisted.is_success:
            return Result.failure(self._store_error(context.correlation_id))
        return Result.success(EventReplayResponse(recovery=RecoveryResponse()))

    def _authorize_candidate(
        self,
        context: AuthenticatedRequestContext,
        requested_topic: str,
        event: OperationalEvent,
    ) -> ErrorDetail | None:
        if (
            event.metadata.organization_id != context.organization_id
            or event.topic != requested_topic
        ):
            return self._denied(context.correlation_id)
        for operation in (
            ProtectedOperation(AuthorizationAction.TOPIC, f"topic:{event.topic}"),
            ProtectedOperation(AuthorizationAction.READ, f"subject:{event.subject_reference}"),
            ProtectedOperation(AuthorizationAction.REPLAY, f"event:{event.event_id}"),
        ):
            denial = self._authorize(context, operation)
            if denial is not None:
                return denial
        return None

    def _delivery(self, event: OperationalEvent) -> PublishedOperationalEvent:
        return PublishedOperationalEvent(
            sequence=event.sequence,
            event_type=self._redactor.redact_text(
                event.event_type, surface=RedactionSurface.OPERATIONAL_EVENT
            ),
            topic=self._redactor.redact_text(
                event.topic, surface=RedactionSurface.OPERATIONAL_EVENT
            ),
            subject_reference=self._redactor.redact_text(
                event.subject_reference, surface=RedactionSurface.OPERATIONAL_EVENT
            ),
            occurred_at=event.occurred_at,
            correlation_id=event.metadata.correlation_id,
            payload_schema_version=event.payload_schema_version,
            redacted_payload=self._redactor.redact_mapping(
                event.redacted_payload, surface=RedactionSurface.OPERATIONAL_EVENT
            ),
        )

    def _authorize(
        self, context: AuthenticatedRequestContext, operation: ProtectedOperation
    ) -> ErrorDetail | None:
        try:
            self._authorization_service.authorize(context, operation)
        except PublicApiException:
            return self._denied(context.correlation_id)
        return None

    @staticmethod
    def _denied(correlation_id: CorrelationId) -> ErrorDetail:
        return ErrorDetail(
            ErrorCode.AUTHORIZATION_DENIED,
            "Operational event delivery is unavailable.",
            correlation_id,
        )

    @staticmethod
    def _store_error(correlation_id: CorrelationId) -> ErrorDetail:
        return ErrorDetail(
            ErrorCode.REPOSITORY_UNAVAILABLE,
            "Operational event delivery is temporarily unavailable.",
            correlation_id,
            retryable=True,
        )


class OutboxPublisher:
    """Deliver committed, authorized, redacted events through an injected transport sink."""

    def __init__(
        self,
        store: CommittedOutboxStore,
        sink: EventSink,
        authorization_service: AuthorizationService | None = None,
        redactor: RedactionService | None = None,
    ) -> None:
        self._store = store
        self._sink = sink
        self._authorization_service = authorization_service or PermissionAuthorizationService()
        self._redactor = redactor or RedactionService()

    def publish(
        self,
        context: AuthenticatedRequestContext,
        topic: str,
    ) -> Result[tuple[PublishedOperationalEvent, ...], ErrorDetail]:
        """Publish all committed pending events for one authorized connection and topic."""
        if not topic.strip():
            return Result.failure(
                ErrorDetail(
                    ErrorCode.VALIDATION_FAILED,
                    "An event topic is required.",
                    context.correlation_id,
                )
            )
        for operation in (
            ProtectedOperation(AuthorizationAction.TOPIC, "event-stream:connection"),
            ProtectedOperation(AuthorizationAction.TOPIC, f"topic:{topic}"),
        ):
            denial = self._authorize(context, operation)
            if denial is not None:
                return Result.failure(denial)

        candidates_result = self._store.pending(context.organization_id)
        if not candidates_result.is_success or candidates_result.value is None:
            return Result.failure(self._store_error(context.correlation_id))
        candidates = tuple(
            sorted(
                (
                    candidate
                    for candidate in candidates_result.value
                    if candidate.outbox.state is DeliveryState.PENDING
                    and candidate.event.topic == topic
                ),
                key=lambda candidate: candidate.event.sequence,
            )
        )
        deliveries: list[PublishedOperationalEvent] = []
        for candidate in candidates:
            denial = self._authorize_candidate(context, topic, candidate)
            if denial is not None:
                return Result.failure(denial)
            deliveries.append(self._delivery(candidate.event))

        try:
            for delivery in deliveries:
                self._sink(delivery)
        except Exception:
            return Result.failure(self._store_error(context.correlation_id))

        for candidate in candidates:
            persisted = self._store.mark_published(
                context.organization_id, candidate.outbox.outbox_id
            )
            if not persisted.is_success:
                return Result.failure(self._store_error(context.correlation_id))
        return Result.success(tuple(deliveries))

    def _authorize_candidate(
        self,
        context: AuthenticatedRequestContext,
        requested_topic: str,
        candidate: CommittedOutboxPublication,
    ) -> ErrorDetail | None:
        event = candidate.event
        if (
            candidate.outbox.metadata.organization_id != context.organization_id
            or event.metadata.organization_id != context.organization_id
            or candidate.outbox.event_id != event.event_id
            or event.topic != requested_topic
        ):
            return self._denied(context.correlation_id)
        for operation in (
            ProtectedOperation(AuthorizationAction.TOPIC, f"topic:{event.topic}"),
            ProtectedOperation(AuthorizationAction.READ, f"subject:{event.subject_reference}"),
            ProtectedOperation(AuthorizationAction.TOPIC, f"event:{event.event_id}"),
        ):
            denial = self._authorize(context, operation)
            if denial is not None:
                return denial
        return None

    def _delivery(self, event: OperationalEvent) -> PublishedOperationalEvent:
        return PublishedOperationalEvent(
            sequence=event.sequence,
            event_type=self._redactor.redact_text(
                event.event_type, surface=RedactionSurface.OPERATIONAL_EVENT
            ),
            topic=self._redactor.redact_text(
                event.topic, surface=RedactionSurface.OPERATIONAL_EVENT
            ),
            subject_reference=self._redactor.redact_text(
                event.subject_reference, surface=RedactionSurface.OPERATIONAL_EVENT
            ),
            occurred_at=event.occurred_at,
            correlation_id=event.metadata.correlation_id,
            payload_schema_version=event.payload_schema_version,
            redacted_payload=self._redactor.redact_mapping(
                event.redacted_payload, surface=RedactionSurface.OPERATIONAL_EVENT
            ),
        )

    def _authorize(
        self, context: AuthenticatedRequestContext, operation: ProtectedOperation
    ) -> ErrorDetail | None:
        try:
            self._authorization_service.authorize(context, operation)
        except PublicApiException:
            return self._denied(context.correlation_id)
        return None

    @staticmethod
    def _denied(correlation_id: CorrelationId) -> ErrorDetail:
        return ErrorDetail(
            ErrorCode.AUTHORIZATION_DENIED,
            "Operational event delivery is unavailable.",
            correlation_id,
        )

    @staticmethod
    def _store_error(correlation_id: CorrelationId) -> ErrorDetail:
        return ErrorDetail(
            ErrorCode.REPOSITORY_UNAVAILABLE,
            "Operational event delivery is temporarily unavailable.",
            correlation_id,
            retryable=True,
        )


class ProjectionService:
    """Return only trusted-context-authorized and redacted activity projections."""

    @staticmethod
    def apply_dashboard_state(
        source: ActivityProjectionSource, *, delayed: bool = False, degraded: bool = False
    ) -> ActivityProjectionSource:
        """Overlay delivery health while preserving the read model's independent freshness value."""
        return ActivityProjectionSource(
            metadata=source.metadata,
            subject_reference=source.subject_reference,
            payload=source.payload,
            as_of=source.as_of,
            freshness=source.freshness,
            delayed=source.delayed or delayed,
            degraded=source.degraded or degraded,
        )

    def __init__(
        self,
        authorization_service: AuthorizationService | None = None,
        redactor: RedactionService | None = None,
    ) -> None:
        self._authorization_service = authorization_service or PermissionAuthorizationService()
        self._redactor = redactor or RedactionService()

    def project(
        self,
        context: AuthenticatedRequestContext,
        source: ActivityProjectionSource,
    ) -> Result[ActivityProjection, ErrorDetail]:
        """Authorize the projection subject and preserve independent freshness/delivery state."""
        if source.metadata.organization_id != context.organization_id:
            return Result.failure(self._denied(context.correlation_id))
        try:
            self._authorization_service.authorize(
                context,
                ProtectedOperation(AuthorizationAction.READ, f"subject:{source.subject_reference}"),
            )
        except PublicApiException:
            return Result.failure(self._denied(context.correlation_id))
        return Result.success(
            ActivityProjection(
                subject_reference=self._redactor.redact_text(
                    source.subject_reference, surface=RedactionSurface.PUBLIC_RESPONSE
                ),
                correlation_id=source.metadata.correlation_id,
                payload=self._redactor.redact_mapping(
                    source.payload, surface=RedactionSurface.PUBLIC_RESPONSE
                ),
                as_of=source.as_of,
                freshness=source.freshness,
                delayed=source.delayed,
                degraded=source.degraded,
            )
        )

    @staticmethod
    def _denied(correlation_id: CorrelationId) -> ErrorDetail:
        return ErrorDetail(
            ErrorCode.AUTHORIZATION_DENIED,
            "Activity projection is unavailable.",
            correlation_id,
        )
