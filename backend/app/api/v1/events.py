"""FastAPI transport adapters for authorized operational-event replay and projections."""

from __future__ import annotations

import json
from collections.abc import Iterator
from typing import Annotated, NoReturn, Protocol, runtime_checkable

from fastapi import APIRouter, Depends, Header, Request, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import StreamingResponse

from app.api.v1.dependencies import AuthenticatedRequestContext, get_authenticated_request_context
from app.api.v1.errors import PublicApiException, public_success_response, require_value
from app.api.v1.schemas import PublicError
from app.events.service import (
    ActivityProjection,
    ActivityProjectionSource,
    EventReplayPolicy,
    EventReplayService,
    ProjectionService,
    PublishedOperationalEvent,
)
from app.models.contracts import ErrorCode, ErrorDetail, Result
from app.models.identifiers import CorrelationId, OrganizationId

router = APIRouter(tags=["events"])


@runtime_checkable
class ActivityProjectionStore(Protocol):
    """Load a protected projection source scoped to the trusted organization."""

    def read(
        self,
        organization_id: OrganizationId,
        subject_reference: str,
        correlation_id: CorrelationId,
    ) -> Result[ActivityProjectionSource, ErrorDetail]: ...


async def get_event_replay_service(request: Request) -> EventReplayService:
    """Return the configured replay service without accepting browser-owned dependencies."""
    service = getattr(request.app.state, "event_replay_service", None)
    if isinstance(service, EventReplayService):
        return service
    _raise_events_unavailable(request)


async def get_event_replay_policy(request: Request) -> EventReplayPolicy:
    """Return the deployment-provided bounded replay policy."""
    policy = getattr(request.app.state, "event_replay_policy", None)
    return policy if isinstance(policy, EventReplayPolicy) else EventReplayPolicy()


async def get_projection_service(request: Request) -> ProjectionService:
    """Return the configured projection service."""
    service = getattr(request.app.state, "projection_service", None)
    if isinstance(service, ProjectionService):
        return service
    _raise_events_unavailable(request)


async def get_activity_projection_store(request: Request) -> ActivityProjectionStore:
    """Return the deployment-owned projection reader."""
    store = getattr(request.app.state, "activity_projection_store", None)
    if isinstance(store, ActivityProjectionStore):
        return store
    _raise_events_unavailable(request)


@router.get("/events/{topic}/stream")
async def stream_event_replay(
    topic: str,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    replay_service: Annotated[EventReplayService, Depends(get_event_replay_service)],
    policy: Annotated[EventReplayPolicy, Depends(get_event_replay_policy)],
    last_event_id: Annotated[int | None, Header()] = None,
) -> StreamingResponse:
    """Frame an all-or-nothing authorized replay as a finite SSE response."""
    replay = require_value(replay_service.replay(context, topic, last_event_id or 0, policy))
    return StreamingResponse(
        _sse_frames(replay.events, replay.recovery is not None),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"},
    )


@router.get("/activity-projections/{subject_reference}")
async def read_activity_projection(
    subject_reference: str,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    store: Annotated[ActivityProjectionStore, Depends(get_activity_projection_store)],
    projection_service: Annotated[ProjectionService, Depends(get_projection_service)],
) -> Response:
    """Return an authorized projection with independent freshness and delivery state."""
    source = require_value(
        store.read(context.organization_id, subject_reference, context.correlation_id)
    )
    projection = require_value(projection_service.project(context, source))
    return public_success_response(_projection_payload(projection), context.correlation_id)


def _sse_frames(
    events: tuple[PublishedOperationalEvent, ...], recovery_required: bool
) -> Iterator[bytes]:
    """Yield either exact replay events or one recovery frame, never a mixture of both."""
    if recovery_required:
        yield _frame("recovery", {"refresh_activity_projection": True})
        return
    for event in events:
        yield _frame(
            str(event.event_type),
            {
                "sequence": event.sequence,
                "event_type": event.event_type,
                "topic": event.topic,
                "subject_reference": event.subject_reference,
                "occurred_at": event.occurred_at,
                "correlation_id": str(event.correlation_id),
                "payload_schema_version": event.payload_schema_version,
                "redacted_payload": event.redacted_payload,
            },
            sequence=int(event.sequence),
        )


def _frame(event_name: str, payload: object, sequence: int | None = None) -> bytes:
    """Encode one SSE message using the standard id/event/data field order."""
    lines = [] if sequence is None else [f"id: {sequence}"]
    lines.extend(
        (
            f"event: {event_name}",
            f"data: {json.dumps(jsonable_encoder(payload), separators=(',', ':'), sort_keys=True)}",
            "",
            "",
        )
    )
    return "\n".join(lines).encode()


def _projection_payload(projection: ActivityProjection) -> dict[str, object]:
    """Serialize all freshness and dashboard-delivery fields explicitly."""
    return {
        "subject_reference": projection.subject_reference,
        "correlation_id": str(projection.correlation_id),
        "payload": projection.payload,
        "as_of": projection.as_of,
        "freshness": projection.freshness,
        "delayed": projection.delayed,
        "degraded": projection.degraded,
        "delayed_or_degraded": projection.delayed_or_degraded,
    }


def _raise_events_unavailable(request: Request) -> NoReturn:
    """Fail safely when event infrastructure has not been composed yet."""
    correlation_id = getattr(request.state, "request_correlation_id", "unavailable")
    raise PublicApiException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        error=PublicError(
            code=ErrorCode.REPOSITORY_UNAVAILABLE.value,
            message="The service is temporarily unavailable.",
            correlation_id=str(correlation_id),
            retryable=True,
        ),
    )
