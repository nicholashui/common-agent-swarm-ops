"""Focused acceptance tests for backend-redesign task 12.1 event and projection services."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from app.api.v1.dependencies import (
    AuthenticatedRequestContext,
    AuthorizationAction,
    ProtectedOperation,
)
from app.api.v1.errors import PublicApiException
from app.api.v1.schemas import PublicError
from app.events.service import (
    ActivityProjectionSource,
    CommittedOutboxPublication,
    EventReplayPolicy,
    EventReplayService,
    FreshnessState,
    OutboxPublisher,
    ProjectionService,
    PublishedOperationalEvent,
)
from app.models.common import RecordMetadata
from app.models.contracts import ErrorCode, ErrorDetail, Result
from app.models.control_plane import (
    DeliveryState,
    EventId,
    EventReplayWindow,
    OperationalEvent,
    OutboxId,
    OutboxRecord,
    ReplayRecoveryOutcome,
    ReplayRecoveryReason,
)
from app.models.identifiers import ActorId, CorrelationId, OrganizationId, RecordId
from app.models.redaction import REDACTED, RedactionService

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_ORGANIZATION = OrganizationId("events-organization")
_FOREIGN_ORGANIZATION = OrganizationId("events-foreign")
_CORRELATION = CorrelationId("events-correlation")


def _metadata(record_id: str, organization_id: OrganizationId = _ORGANIZATION) -> RecordMetadata:
    return RecordMetadata(
        record_id=RecordId(record_id), organization_id=organization_id,
        correlation_id=_CORRELATION, schema_version=1, version=1,
        created_at=_NOW, updated_at=_NOW,
    )


@dataclass
class _CommittedStore:
    publications: tuple[CommittedOutboxPublication, ...]
    marked: list[OutboxId] = field(default_factory=list)
    pending_calls: int = 0

    def pending(
        self, organization_id: OrganizationId
    ) -> Result[tuple[CommittedOutboxPublication, ...], ErrorDetail]:
        self.pending_calls += 1
        if organization_id != _ORGANIZATION:
            return Result.failure(
                ErrorDetail(ErrorCode.AUTHORIZATION_DENIED, "hidden", _CORRELATION)
            )
        return Result.success(self.publications)

    def mark_published(
        self, organization_id: OrganizationId, outbox_id: OutboxId
    ) -> Result[OutboxRecord, ErrorDetail]:
        if organization_id != _ORGANIZATION:
            return Result.failure(
                ErrorDetail(ErrorCode.AUTHORIZATION_DENIED, "hidden", _CORRELATION)
            )
        self.marked.append(outbox_id)
        for publication in self.publications:
            if publication.outbox.outbox_id == outbox_id:
                return Result.success(publication.outbox)
        return Result.failure(ErrorDetail(ErrorCode.NOT_FOUND, "hidden", _CORRELATION))


@dataclass
class _RecordingAuthorizer:
    denied_subject: str | None = None
    operations: list[ProtectedOperation] = field(default_factory=list)

    def authorize(
        self, context: AuthenticatedRequestContext, operation: ProtectedOperation
    ) -> None:
        self.operations.append(operation)
        if operation.subject == self.denied_subject:
            raise PublicApiException(
                status_code=403,
                error=PublicError(
                    code=ErrorCode.AUTHORIZATION_DENIED.value,
                    message="hidden",
                    correlation_id=str(context.correlation_id),
                ),
            )


def _context(organization_id: OrganizationId = _ORGANIZATION) -> AuthenticatedRequestContext:
    return AuthenticatedRequestContext(
        tenant_id=organization_id,
        actor_id=ActorId("events-actor"),
        correlation_id=_CORRELATION,
        permissions=frozenset({"control_plane:*"}),
    )


def _publication(
    *,
    outbox_id: str = "outbox-1",
    state: DeliveryState = DeliveryState.PENDING,
    topic: str = "work",
) -> CommittedOutboxPublication:
    event = OperationalEvent(
        metadata=_metadata("event-record"), event_id=EventId("event-1"), sequence=1,
        event_type="work.transitioned", subject_reference="run:1", occurred_at=_NOW,
        payload_schema_version=3,
        redacted_payload={"raw_prompt": "private", "summary": "deployment-secret"}, topic=topic,
    )
    return CommittedOutboxPublication(
        outbox=OutboxRecord(
            metadata=_metadata("outbox-record"), outbox_id=OutboxId(outbox_id),
            event_id=event.event_id, state=state, created_at=_NOW,
        ), event=event,
    )


def test_outbox_publisher_delivers_only_committed_pending_events_with_full_safe_metadata() -> None:
    """A committed pending pair is authorized, redacted, delivered, and marked after delivery."""
    committed = _publication()
    already_published = _publication(outbox_id="outbox-2", state=DeliveryState.PUBLISHED)
    store = _CommittedStore((committed, already_published))
    authorizer = _RecordingAuthorizer()
    delivered: list[PublishedOperationalEvent] = []

    result = OutboxPublisher(
        store, delivered.append, authorizer, RedactionService(("deployment-secret",))
    ).publish(_context(), "work")

    assert result.is_success and result.value is not None
    assert result.value == tuple(delivered)
    assert len(delivered) == 1
    event = delivered[0]
    assert (
        event.sequence, event.event_type, event.topic, event.subject_reference,
        event.occurred_at, event.correlation_id, event.payload_schema_version,
    ) == (1, "work.transitioned", "work", "run:1", _NOW, _CORRELATION, 3)
    assert event.redacted_payload["raw_prompt"] == REDACTED
    assert event.redacted_payload["summary"] == REDACTED
    assert store.pending_calls == 1
    assert store.marked == [OutboxId("outbox-1")]
    assert [operation.subject for operation in authorizer.operations] == [
        "event-stream:connection", "topic:work", "topic:work", "subject:run:1", "event:event-1",
    ]


def test_outbox_publisher_rejects_unauthorized_event_subject_before_any_delivery() -> None:
    """Every candidate subject is checked under current trusted context before sink delivery."""
    store = _CommittedStore((_publication(),))
    authorizer = _RecordingAuthorizer(denied_subject="subject:run:1")
    delivered: list[PublishedOperationalEvent] = []

    result = OutboxPublisher(store, delivered.append, authorizer).publish(_context(), "work")

    assert not result.is_success
    assert result.error is not None and result.error.code is ErrorCode.AUTHORIZATION_DENIED
    assert delivered == []
    assert store.marked == []
    assert "private" not in repr(result.error)


def test_projection_service_returns_redacted_current_data_with_delayed_indicator() -> None:
    """Delayed delivery does not overwrite an independently current underlying freshness state."""
    source = ActivityProjectionSource(
        metadata=_metadata("projection-record"), subject_reference="run:1",
        payload={"artifact_reference": "artifact-1", "token": "secret", "raw_prompt": "private"},
        as_of=_NOW, freshness=FreshnessState.CURRENT, delayed=True,
    )
    authorizer = _RecordingAuthorizer()

    result = ProjectionService(authorizer).project(_context(), source)

    assert result.is_success and result.value is not None
    projection = result.value
    assert projection.as_of == _NOW
    assert projection.freshness is FreshnessState.CURRENT
    assert projection.delayed and not projection.degraded and projection.delayed_or_degraded
    assert projection.payload["artifact_reference"] == "artifact-1"
    assert projection.payload["token"] == REDACTED
    assert projection.payload["raw_prompt"] == REDACTED
    assert authorizer.operations == [
        ProtectedOperation(AuthorizationAction.READ, "subject:run:1")
    ]


def test_projection_service_applies_dashboard_degradation_without_changing_freshness() -> None:
    """A delayed dashboard overlays delivery health without converting current data to stale."""
    source = ActivityProjectionSource(
        metadata=_metadata("projection-overlay"), subject_reference="run:1",
        payload={}, as_of=_NOW, freshness=FreshnessState.CURRENT,
    )

    overlaid = ProjectionService.apply_dashboard_state(source, delayed=True, degraded=True)
    result = ProjectionService(_RecordingAuthorizer()).project(_context(), overlaid)

    assert result.is_success and result.value is not None
    assert result.value.as_of == _NOW
    assert result.value.freshness is FreshnessState.CURRENT
    assert result.value.delayed and result.value.degraded
    assert result.value.delayed_or_degraded


def test_projection_service_denies_foreign_sources_without_exposing_payload() -> None:
    """Cross-organization projections share the safe authorization outcome and omit data."""
    source = ActivityProjectionSource(
        metadata=_metadata("foreign-projection", _FOREIGN_ORGANIZATION),
        subject_reference="run:secret", payload={"protected_artifact": "private"},
        as_of=_NOW, freshness=FreshnessState.STALE, degraded=True,
    )

    result = ProjectionService(_RecordingAuthorizer()).project(_context(), source)

    assert not result.is_success
    assert result.value is None and result.error is not None
    assert result.error.code is ErrorCode.AUTHORIZATION_DENIED
    assert "private" not in repr(result.error)


@dataclass
class _ReplayStore:
    window: EventReplayWindow
    outcomes: list[ReplayRecoveryOutcome] = field(default_factory=list)
    replay_calls: list[tuple[OrganizationId, str, int, int]] = field(default_factory=list)

    def replay_window(
        self,
        organization_id: OrganizationId,
        topic: str,
        after_sequence: int,
        maximum_events: int,
    ) -> Result[EventReplayWindow, ErrorDetail]:
        self.replay_calls.append((organization_id, topic, after_sequence, maximum_events))
        return Result.success(self.window)

    def append_replay_recovery(
        self, record: ReplayRecoveryOutcome
    ) -> Result[ReplayRecoveryOutcome, ErrorDetail]:
        self.outcomes.append(record)
        return Result.success(record)


def _replay_event(sequence: int, *, subject_reference: str = "run:1") -> OperationalEvent:
    return OperationalEvent(
        metadata=_metadata(f"replay-event-{sequence}"),
        event_id=EventId(f"replay-event-{sequence}"),
        sequence=sequence,
        event_type="work.transitioned",
        subject_reference=subject_reference,
        occurred_at=_NOW,
        payload_schema_version=3,
        redacted_payload={"summary": f"event-{sequence}"},
        topic="work",
    )


def test_event_replay_returns_only_the_contiguous_bounded_sequence_after_cursor() -> None:
    """Replay prepares exactly the first authorized contiguous bounded events after a cursor."""
    store = _ReplayStore(
        EventReplayWindow(events=(_replay_event(4), _replay_event(5)), high_watermark=6)
    )
    authorizer = _RecordingAuthorizer()

    result = EventReplayService(store, authorizer, clock=lambda: _NOW).replay(
        _context(), "work", 3, EventReplayPolicy(maximum_events=2)
    )

    assert result.is_success and result.value is not None
    assert result.value.recovery is None
    assert [event.sequence for event in result.value.events] == [4, 5]
    assert store.replay_calls == [(_ORGANIZATION, "work", 3, 2)]
    assert store.outcomes == []


def test_event_replay_records_a_gap_and_returns_recovery_without_events() -> None:
    """A missing sequence is retained and directs the client to refresh before replay delivery."""
    store = _ReplayStore(EventReplayWindow(events=(_replay_event(5),), high_watermark=5))

    result = EventReplayService(store, _RecordingAuthorizer(), clock=lambda: _NOW).replay(
        _context(), "work", 3, EventReplayPolicy(maximum_events=3)
    )

    assert result.is_success and result.value is not None
    assert result.value.events == ()
    assert result.value.recovery is not None
    assert result.value.recovery.refresh_activity_projection
    assert len(store.outcomes) == 1
    assert store.outcomes[0].reason is ReplayRecoveryReason.SEQUENCE_GAP
    assert store.outcomes[0].cursor_sequence == 3


def test_event_replay_records_policy_directed_recovery_without_reading_events() -> None:
    """Configured recovery policy prevents a replay event from being prepared or delivered."""
    store = _ReplayStore(EventReplayWindow(events=(_replay_event(4),), high_watermark=4))

    result = EventReplayService(store, _RecordingAuthorizer(), clock=lambda: _NOW).replay(
        _context(), "work", 3, EventReplayPolicy(replay_permitted=False)
    )

    assert result.is_success and result.value is not None
    assert result.value.events == () and result.value.recovery is not None
    assert store.replay_calls == []
    assert [outcome.reason for outcome in store.outcomes] == [
        ReplayRecoveryReason.POLICY_DIRECTED
    ]


def test_event_replay_rejects_an_unauthorized_candidate_without_partial_replay() -> None:
    """A later denied candidate returns the enumeration-safe error before any replay response."""
    store = _ReplayStore(
        EventReplayWindow(
            events=(_replay_event(4), _replay_event(5, subject_reference="run:hidden")),
            high_watermark=5,
        )
    )
    authorizer = _RecordingAuthorizer(denied_subject="subject:run:hidden")

    result = EventReplayService(store, authorizer, clock=lambda: _NOW).replay(
        _context(), "work", 3, EventReplayPolicy(maximum_events=3)
    )

    assert not result.is_success
    assert result.value is None and result.error is not None
    assert result.error.code is ErrorCode.AUTHORIZATION_DENIED
    assert store.outcomes == []
    assert "hidden" not in repr(result.error)
