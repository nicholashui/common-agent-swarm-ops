"""FastAPI/SSE integration coverage for backend-redesign event transport."""

from __future__ import annotations

import json
from collections.abc import Iterator
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import cast

import pytest
from fastapi.testclient import TestClient
from httpx import Response

from app.api.v1.dependencies import (
    AuthenticatedRequestContext,
    ProtectedOperation,
    get_authenticated_request_context,
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
from app.main import create_app
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

# **Validates: Requirements 10.2, 10.4, 10.5, 10.6, 10.7, 17.2, 17.3**

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_ORGANIZATION = OrganizationId("events-integration-organization")
_CORRELATION = CorrelationId("events-integration-correlation")


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


def _event(sequence: int, subject_reference: str = "run:visible") -> OperationalEvent:
    return OperationalEvent(
        metadata=_metadata(f"event-{sequence}"),
        event_id=EventId(f"event-{sequence}"),
        sequence=sequence,
        event_type="work.transitioned",
        subject_reference=subject_reference,
        occurred_at=_NOW,
        payload_schema_version=3,
        redacted_payload={"summary": f"event-{sequence}"},
        topic="work",
    )


@dataclass
class _ReplayStore:
    window: EventReplayWindow
    calls: list[tuple[OrganizationId, str, int, int]] = field(default_factory=list)
    recoveries: list[ReplayRecoveryOutcome] = field(default_factory=list)

    def replay_window(
        self,
        organization_id: OrganizationId,
        topic: str,
        after_sequence: int,
        maximum_events: int,
    ) -> Result[EventReplayWindow, ErrorDetail]:
        self.calls.append((organization_id, topic, after_sequence, maximum_events))
        return Result.success(self.window)

    def append_replay_recovery(
        self, record: ReplayRecoveryOutcome
    ) -> Result[ReplayRecoveryOutcome, ErrorDetail]:
        self.recoveries.append(record)
        return Result.success(record)


@dataclass
class _ProjectionStore:
    source: ActivityProjectionSource
    calls: list[tuple[OrganizationId, str, CorrelationId]] = field(default_factory=list)

    def read(
        self,
        organization_id: OrganizationId,
        subject_reference: str,
        correlation_id: CorrelationId,
    ) -> Result[ActivityProjectionSource, ErrorDetail]:
        self.calls.append((organization_id, subject_reference, correlation_id))
        return Result.success(self.source)


@dataclass
class _Authorizer:
    denied_subjects: set[str] = field(default_factory=set)
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


@dataclass
class _ApiFixture:
    client: TestClient
    contexts: dict[str, AuthenticatedRequestContext]
    replay_store: _ReplayStore
    projection_store: _ProjectionStore
    authorizer: _Authorizer


@pytest.fixture
def api_fixture() -> Iterator[_ApiFixture]:
    """Mount the real public routes with deterministic event infrastructure."""
    contexts = {
        "current": AuthenticatedRequestContext(
            _ORGANIZATION,
            ActorId("events-integration-actor"),
            _CORRELATION,
            permissions=frozenset({"control_plane:*"}),
        )
    }
    replay_store = _ReplayStore(EventReplayWindow(events=(), high_watermark=0))
    projection_store = _ProjectionStore(
        ActivityProjectionSource(
            metadata=_metadata("projection"),
            subject_reference="run:projection",
            payload={"summary": "current"},
            as_of=_NOW,
            freshness=FreshnessState.CURRENT,
        )
    )
    authorizer = _Authorizer()
    application = create_app()
    application.state.event_replay_service = EventReplayService(
        replay_store, authorizer, clock=lambda: _NOW
    )
    application.state.event_replay_policy = EventReplayPolicy(maximum_events=2)
    application.state.activity_projection_store = projection_store
    application.state.projection_service = ProjectionService(authorizer)
    application.dependency_overrides[get_authenticated_request_context] = lambda: contexts[
        "current"
    ]
    with TestClient(application) as client:
        yield _ApiFixture(client, contexts, replay_store, projection_store, authorizer)
    application.dependency_overrides.clear()


def _safe_error(response: Response) -> tuple[int, str, str, bool]:
    payload = cast(dict[str, object], response.json())
    error = cast(dict[str, object], payload["error"])
    return (
        response.status_code,
        str(error["code"]),
        str(error["message"]),
        bool(error["retryable"]),
    )


def _frames(body: str) -> list[dict[str, object]]:
    frames: list[dict[str, object]] = []
    for raw_frame in filter(None, body.split("\n\n")):
        frame: dict[str, object] = {}
        for line in raw_frame.splitlines():
            name, value = line.split(": ", maxsplit=1)
            frame[name] = cast(object, json.loads(value)) if name == "data" else value
        frames.append(frame)
    return frames


def test_stream_topic_authorization_rejects_before_event_lookup(api_fixture: _ApiFixture) -> None:
    """An unauthorized stream topic returns the standard safe error without replay lookup."""
    api_fixture.authorizer.denied_subjects.add("topic:work")

    response = api_fixture.client.get("/api/v1/events/work/stream", headers={"Last-Event-ID": "3"})

    assert _safe_error(response) == (
        403,
        "authorization_denied",
        "You are not authorized to perform this action.",
        False,
    )
    assert api_fixture.replay_store.calls == []
    assert "data:" not in response.text


def test_stream_candidate_authorization_prevents_partial_replay(api_fixture: _ApiFixture) -> None:
    """A denied later event yields the safe error before any SSE frame is emitted."""
    api_fixture.replay_store.window = EventReplayWindow(
        events=(_event(4), _event(5, "run:hidden")), high_watermark=5
    )
    api_fixture.authorizer.denied_subjects.add("subject:run:hidden")

    response = api_fixture.client.get("/api/v1/events/work/stream", headers={"Last-Event-ID": "3"})

    assert _safe_error(response)[0:2] == (403, "authorization_denied")
    assert "id: 4" not in response.text
    assert "run:hidden" not in response.text


def test_stream_frames_exact_contiguous_replay_after_last_event_id(
    api_fixture: _ApiFixture,
) -> None:
    """SSE uses id/event/data frames for the exact bounded sequence after its cursor."""
    api_fixture.replay_store.window = EventReplayWindow(
        events=(_event(4), _event(5)), high_watermark=5
    )

    response = api_fixture.client.get("/api/v1/events/work/stream", headers={"Last-Event-ID": "3"})

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    frames = _frames(response.text)
    assert [frame["id"] for frame in frames] == ["4", "5"]
    assert [frame["event"] for frame in frames] == ["work.transitioned", "work.transitioned"]
    payloads = [cast(dict[str, object], frame["data"]) for frame in frames]
    assert [payload["sequence"] for payload in payloads] == [4, 5]
    assert all(payload["payload_schema_version"] == 3 for payload in payloads)
    assert api_fixture.replay_store.calls == [(_ORGANIZATION, "work", 3, 2)]


def test_stream_returns_recovery_frame_without_replay_event_for_sequence_gap(
    api_fixture: _ApiFixture,
) -> None:
    """A replay gap is recorded and delivered only as a client-refresh recovery response."""
    api_fixture.replay_store.window = EventReplayWindow(events=(_event(5),), high_watermark=5)

    response = api_fixture.client.get("/api/v1/events/work/stream", headers={"Last-Event-ID": "3"})

    assert response.status_code == 200
    assert _frames(response.text) == [
        {"event": "recovery", "data": {"refresh_activity_projection": True}}
    ]
    assert [outcome.reason for outcome in api_fixture.replay_store.recoveries] == [
        ReplayRecoveryReason.SEQUENCE_GAP
    ]


def test_projection_preserves_current_freshness_with_delayed_degraded_indicator(
    api_fixture: _ApiFixture,
) -> None:
    """Delayed delivery exposes degradation without changing current underlying freshness."""
    api_fixture.projection_store.source = ActivityProjectionSource(
        metadata=_metadata("delayed-projection"),
        subject_reference="run:projection",
        payload={"summary": "current"},
        as_of=_NOW,
        freshness=FreshnessState.CURRENT,
        delayed=True,
        degraded=True,
    )

    response = api_fixture.client.get("/api/v1/activity-projections/run:projection")

    assert response.status_code == 200
    payload = cast(dict[str, object], response.json())
    data = cast(dict[str, object], payload["data"])
    assert payload["meta"] == {"correlation_id": str(_CORRELATION)}
    assert data["as_of"] == "2025-01-01T00:00:00+00:00"
    assert data["freshness"] == FreshnessState.CURRENT.value
    assert data["delayed"] is True
    assert data["degraded"] is True
    assert data["delayed_or_degraded"] is True
    assert api_fixture.projection_store.calls == [(_ORGANIZATION, "run:projection", _CORRELATION)]
