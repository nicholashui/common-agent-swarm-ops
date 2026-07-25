"""Property checks for exact authorized redacted event replay and projections."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from hypothesis import given, settings, strategies as st

from app.api.v1.dependencies import (
    AuthenticatedRequestContext,
    ProtectedOperation,
)
from app.api.v1.errors import PublicApiException
from app.api.v1.schemas import PublicError
from app.events.service import (
    ActivityProjectionSource,
    EventReplayPolicy,
    EventReplayService,
    FreshnessState,
    ProjectionService,
)
from app.models.common import RecordMetadata
from app.models.contracts import ErrorCode, ErrorDetail, Result
from app.models.control_plane import (
    EventId,
    EventReplayWindow,
    OperationalEvent,
    ReplayRecoveryOutcome,
    ReplayRecoveryReason,
)
from app.models.identifiers import ActorId, CorrelationId, OrganizationId, RecordId
from app.models.redaction import REDACTED, RedactionService

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_ORGANIZATION = OrganizationId("property-14-organization")
_CORRELATION = CorrelationId("property-14-correlation")
_TOPIC = "work"
_REPLAY_MODES = st.sampled_from(("contiguous", "gap", "non_contiguous", "cursor_unavailable"))
_SAFE_VALUES = st.text(alphabet="abcdefghijklmnopqrstuvwxyz0123456789", min_size=1, max_size=12)


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


@dataclass
class _VisibilityAuthorizer:
    denied_subjects: frozenset[str]
    operations: list[ProtectedOperation] = field(default_factory=list)

    def authorize(
        self, context: AuthenticatedRequestContext, operation: ProtectedOperation
    ) -> None:
        self.operations.append(operation)
        if operation.subject in self.denied_subjects:
            raise PublicApiException(
                status_code=403,
                error=PublicError(
                    code=ErrorCode.AUTHORIZATION_DENIED.value,
                    message="hidden",
                    correlation_id=str(context.correlation_id),
                ),
            )


def _context() -> AuthenticatedRequestContext:
    return AuthenticatedRequestContext(
        tenant_id=_ORGANIZATION,
        actor_id=ActorId("property-14-actor"),
        correlation_id=_CORRELATION,
        permissions=frozenset({"control_plane:*"}),
    )


def _metadata(record_id: str) -> RecordMetadata:
    return RecordMetadata(
        record_id=RecordId(record_id),
        organization_id=_ORGANIZATION,
        correlation_id=_CORRELATION,
        schema_version=1,
        version=1,
        created_at=_NOW,
        updated_at=_NOW,
    )


def _sequences(mode: str, cursor: int, count: int) -> tuple[int, ...]:
    if mode == "contiguous":
        return tuple(range(cursor + 1, cursor + count + 1))
    if mode == "gap":
        return tuple(range(cursor + 2, cursor + count + 2))
    if mode == "non_contiguous":
        return (cursor, *range(cursor + 1, cursor + count))
    return ()


def _recovery_reason(mode: str) -> ReplayRecoveryReason:
    return {
        "gap": ReplayRecoveryReason.SEQUENCE_GAP,
        "non_contiguous": ReplayRecoveryReason.NON_CONTIGUOUS,
        "cursor_unavailable": ReplayRecoveryReason.CURSOR_UNAVAILABLE,
    }[mode]


def _event(sequence: int, value: str, sensitive_sentinel: str) -> OperationalEvent:
    return OperationalEvent(
        metadata=_metadata(f"event-record-{sequence}"),
        event_id=EventId(f"event-{sequence}"),
        sequence=sequence,
        event_type="work.transitioned",
        subject_reference=f"run:{value}:{sequence}",
        occurred_at=_NOW,
        payload_schema_version=3,
        redacted_payload={
            "summary": sensitive_sentinel,
            "artifact_reference": f"artifact-{value}-{sequence}",
            "api_token": sensitive_sentinel,
            "raw_prompt": sensitive_sentinel,
        },
        topic=_TOPIC,
    )


# Feature: backend-redesign, Property 14
# **Validates: Requirements 10.3, 10.4, 10.5, 10.6, 10.7, 10.8, 17.2, 17.3**
@settings(max_examples=100)
@given(
    value=_SAFE_VALUES,
    mode=_REPLAY_MODES,
    cursor=st.integers(min_value=1, max_value=20),
    visibility_matrix=st.lists(st.booleans(), min_size=1, max_size=4),
    replay_permitted=st.booleans(),
    projection_visible=st.booleans(),
    freshness=st.sampled_from(tuple(FreshnessState)),
    delayed=st.booleans(),
    degraded=st.booleans(),
)
def test_property_14_event_replay_and_projections_are_exact_authorized_and_redacted(
    value: str,
    mode: str,
    cursor: int,
    visibility_matrix: list[bool],
    replay_permitted: bool,
    projection_visible: bool,
    freshness: FreshnessState,
    delayed: bool,
    degraded: bool,
) -> None:
    """Replay is all-or-nothing; authorized events and projections expose redacted metadata only."""
    sensitive_sentinel = f"sensitive-{value}"
    sequences = _sequences(mode, cursor, len(visibility_matrix))
    events = tuple(_event(sequence, value, sensitive_sentinel) for sequence in sequences)
    high_watermark = cursor - 1 if mode == "cursor_unavailable" else sequences[-1]
    store = _ReplayStore(EventReplayWindow(events=events, high_watermark=high_watermark))
    if events:
        denied_event_subjects = {
            f"subject:{event.subject_reference}"
            for event, visible in zip(events, visibility_matrix, strict=True)
            if not visible
        }
    else:
        denied_event_subjects = set()
    projection_subject = f"projection:{value}"
    denied_subjects = denied_event_subjects | (
        {f"subject:{projection_subject}"} if not projection_visible else set()
    )
    authorizer = _VisibilityAuthorizer(frozenset(denied_subjects))
    redactor = RedactionService((sensitive_sentinel,))
    policy = EventReplayPolicy(
        replay_permitted=replay_permitted,
        maximum_events=len(visibility_matrix),
    )

    replay = EventReplayService(
        store,
        authorizer,
        redactor,
        clock=lambda: _NOW,
        record_id_factory=lambda: RecordId("property-14-recovery-record"),
    ).replay(_context(), _TOPIC, cursor, policy)

    replay_is_available = mode == "contiguous" and replay_permitted
    replay_is_authorized = all(visibility_matrix)
    if replay_is_available and replay_is_authorized:
        assert replay.is_success and replay.value is not None
        response = replay.value
        assert response.recovery is None
        assert [delivery.sequence for delivery in response.events] == list(sequences)
        assert len(response.events) == len(set(sequences)) == len(visibility_matrix)
        assert store.outcomes == []
        assert store.replay_calls == [(_ORGANIZATION, _TOPIC, cursor, len(visibility_matrix))]
        for event, delivery in zip(events, response.events, strict=True):
            assert (
                delivery.sequence,
                delivery.event_type,
                delivery.topic,
                delivery.subject_reference,
                delivery.occurred_at,
                delivery.correlation_id,
                delivery.payload_schema_version,
            ) == (
                event.sequence,
                event.event_type,
                event.topic,
                event.subject_reference,
                event.occurred_at,
                event.metadata.correlation_id,
                event.payload_schema_version,
            )
            assert delivery.redacted_payload["artifact_reference"] == (
                f"artifact-{value}-{event.sequence}"
            )
            assert delivery.redacted_payload["summary"] == REDACTED
            assert delivery.redacted_payload["api_token"] == REDACTED
            assert delivery.redacted_payload["raw_prompt"] == REDACTED
            assert sensitive_sentinel not in repr(delivery)
    elif not replay_permitted or mode != "contiguous":
        assert replay.is_success and replay.value is not None
        response = replay.value
        assert response.events == ()
        assert response.recovery is not None and response.recovery.refresh_activity_projection
        assert len(store.outcomes) == 1
        expected_reason = (
            ReplayRecoveryReason.POLICY_DIRECTED if not replay_permitted else _recovery_reason(mode)
        )
        assert store.outcomes[0].reason is expected_reason
        assert store.outcomes[0].cursor_sequence == cursor
        assert store.replay_calls == (
            []
            if not replay_permitted
            else [(_ORGANIZATION, _TOPIC, cursor, len(visibility_matrix))]
        )
    else:
        assert not replay.is_success
        assert replay.value is None and replay.error is not None
        assert replay.error.code is ErrorCode.AUTHORIZATION_DENIED
        assert store.outcomes == []
        assert store.replay_calls == [(_ORGANIZATION, _TOPIC, cursor, len(visibility_matrix))]
        assert sensitive_sentinel not in repr(replay.error)

    projection = ProjectionService(authorizer, redactor).project(
        _context(),
        ActivityProjectionSource(
            metadata=_metadata("projection-record"),
            subject_reference=projection_subject,
            payload={
                "artifact_reference": f"artifact-{value}",
                "summary": sensitive_sentinel,
                "api_token": sensitive_sentinel,
                "raw_prompt": sensitive_sentinel,
            },
            as_of=_NOW,
            freshness=freshness,
            delayed=delayed,
            degraded=degraded,
        ),
    )
    if projection_visible:
        assert projection.is_success and projection.value is not None
        value_projection = projection.value
        assert value_projection.subject_reference == projection_subject
        assert value_projection.correlation_id == _CORRELATION
        assert value_projection.as_of == _NOW
        assert value_projection.freshness is freshness
        assert value_projection.delayed is delayed
        assert value_projection.degraded is degraded
        assert value_projection.delayed_or_degraded is (delayed or degraded)
        assert value_projection.payload["artifact_reference"] == f"artifact-{value}"
        assert value_projection.payload["summary"] == REDACTED
        assert value_projection.payload["api_token"] == REDACTED
        assert value_projection.payload["raw_prompt"] == REDACTED
        assert sensitive_sentinel not in repr(value_projection)
    else:
        assert not projection.is_success
        assert projection.value is None and projection.error is not None
        assert projection.error.code is ErrorCode.AUTHORIZATION_DENIED
        assert sensitive_sentinel not in repr(projection.error)
