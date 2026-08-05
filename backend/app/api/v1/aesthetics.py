"""Host API: offline Aesthetics Agent (Critic · Aligner · Taste-Keeper foundation)."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query, status
from pydantic import Field

from app.aesthetics.consumers import evaluate_for_consumer, list_consumers
from app.aesthetics.models import (
    AestheticCompareRequest,
    AestheticEvaluateRequest,
    AestheticProfileCreate,
    StrictModel,
)
from app.aesthetics.service import get_aesthetics_service
from app.api.v1.dependencies import AuthenticatedRequestContext, get_authenticated_request_context
from app.api.v1.errors import PublicApiException
from app.api.v1.schemas import PublicError

router = APIRouter(prefix="/aesthetics", tags=["aesthetics"])


class MemoryDecisionRequest(StrictModel):
    project_id: str = Field(default="default", max_length=200)
    artifact_ref: str = Field(min_length=1, max_length=500)
    decision: str = Field(min_length=1, max_length=32)
    note: str = Field(default="", max_length=500)


class PublishBusRequest(StrictModel):
    verdict: dict[str, Any]
    to_agent_ids: list[str] = Field(default_factory=list, max_length=32)
    correlation_id: str | None = Field(default=None, max_length=100)


class HandoffAttachRequest(StrictModel):
    handoff: dict[str, Any]
    verdict: dict[str, Any]


class ConsumerEvaluateRequest(StrictModel):
    consumer_agent_id: str = Field(min_length=1, max_length=120)
    artifact_ref: str = Field(min_length=1, max_length=500)
    media_type: str = Field(default="image", max_length=32)
    profile_id: str | None = Field(default=None, max_length=200)
    shot_intent_text: str = Field(default="", max_length=4_000)
    publish_bus: bool = True


class ProfileComposeRequest(StrictModel):
    base_profile_id: str = Field(min_length=1, max_length=200)
    overlay_profile_id: str = Field(min_length=1, max_length=200)
    new_profile_id: str = Field(min_length=1, max_length=200)
    owner: str = Field(default="local", max_length=200)
    precedence: str = Field(default="overlay", max_length=32)


def _bad(correlation_id: str, message: str) -> None:
    raise PublicApiException(
        status_code=status.HTTP_400_BAD_REQUEST,
        error=PublicError(
            code="validation_failed",
            message=message,
            correlation_id=correlation_id,
            retryable=False,
        ),
    )


def _denied(correlation_id: str, message: str) -> None:
    raise PublicApiException(
        status_code=status.HTTP_403_FORBIDDEN,
        error=PublicError(
            code="authorization_denied",
            message=message,
            correlation_id=correlation_id,
            retryable=False,
        ),
    )


@router.get("/policy")
async def aesthetics_policy(
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
) -> dict[str, Any]:
    service = get_aesthetics_service()
    return {
        "activation_policy": service.activation_policy,
        "dimensions": [
            "composition",
            "color_harmony",
            "light",
            "depth",
            "subject",
            "technical",
            "emotion",
            "style_fidelity",
            "novelty",
            "temporal",
        ],
        "modes": ["screen", "score", "align", "compare", "refine"],
        "agent_id": "specials.aesthetics-agent",
        "note": (
            "Offline Host foundation for aesthetics_agent_functional_specification. "
            "Live multimodal vision and DPO training are not enabled."
        ),
        "correlation_id": str(context.correlation_id),
    }


@router.get("/profiles")
async def list_profiles(
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
) -> dict[str, Any]:
    service = get_aesthetics_service()
    items = service.list_profiles()
    return {
        "items": items,
        "count": len(items),
        "activation_policy": service.activation_policy,
        "correlation_id": str(context.correlation_id),
    }


@router.post("/profiles")
async def upsert_profile(
    body: AestheticProfileCreate,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
) -> dict[str, Any]:
    service = get_aesthetics_service()
    profile = service.upsert_profile(body)
    return {
        "ok": True,
        "profile": profile,
        "correlation_id": str(context.correlation_id),
    }


@router.post("/profiles/compose")
async def compose_profiles(
    body: ProfileComposeRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
) -> dict[str, Any]:
    service = get_aesthetics_service()
    if body.precedence not in {"overlay", "average"}:
        _bad(str(context.correlation_id), "precedence must be overlay|average")
    result = service.compose_profiles(
        base_profile_id=body.base_profile_id,
        overlay_profile_id=body.overlay_profile_id,
        new_profile_id=body.new_profile_id,
        owner=body.owner,
        precedence=body.precedence,
    )
    return {**result, "correlation_id": str(context.correlation_id)}


@router.post("/evaluate")
async def evaluate_artifact(
    body: AestheticEvaluateRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
) -> dict[str, Any]:
    service = get_aesthetics_service()
    result = service.evaluate(body)
    if result.get("ok") is False:
        err = str(result.get("error") or "evaluate failed")
        if "not enabled" in err or "denied" in err.lower():
            _denied(str(context.correlation_id), err)
        _bad(str(context.correlation_id), err)
    return {**result, "correlation_id": str(context.correlation_id)}


@router.post("/compare")
async def compare_artifacts(
    body: AestheticCompareRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
) -> dict[str, Any]:
    service = get_aesthetics_service()
    result = service.compare(body)
    if result.get("ok") is False:
        err = str(result.get("error") or "compare failed")
        if "denied" in err.lower() or "not enabled" in err:
            _denied(str(context.correlation_id), err)
        _bad(str(context.correlation_id), err)
    return {**result, "correlation_id": str(context.correlation_id)}


@router.post("/refine")
async def refine_artifact(
    body: AestheticEvaluateRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
) -> dict[str, Any]:
    service = get_aesthetics_service()
    result = service.refine(body)
    if result.get("ok") is False:
        err = str(result.get("error") or "refine failed")
        if "not enabled" in err or "denied" in err.lower():
            _denied(str(context.correlation_id), err)
        _bad(str(context.correlation_id), err)
    return {**result, "correlation_id": str(context.correlation_id)}


@router.get("/verdicts")
async def list_verdicts(
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> dict[str, Any]:
    service = get_aesthetics_service()
    return {
        "items": service.recent_verdicts(limit=limit),
        "correlation_id": str(context.correlation_id),
    }


@router.get("/consumers")
async def aesthetics_consumers(
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
) -> dict[str, Any]:
    return {
        "items": list_consumers(),
        "count": len(list_consumers()),
        "correlation_id": str(context.correlation_id),
    }


@router.post("/consumers/evaluate")
async def aesthetics_consumer_evaluate(
    body: ConsumerEvaluateRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
) -> dict[str, Any]:
    service = get_aesthetics_service()
    result = evaluate_for_consumer(
        service,
        consumer_agent_id=body.consumer_agent_id,
        artifact_ref=body.artifact_ref,
        media_type=body.media_type,
        profile_id=body.profile_id,
        shot_intent_text=body.shot_intent_text,
        publish_bus=body.publish_bus,
    )
    if result.get("ok") is False:
        _bad(str(context.correlation_id), str(result.get("error") or "consumer failed"))
    return {**result, "correlation_id": str(context.correlation_id)}


@router.post("/bus/publish")
async def publish_aesthetic_critique(
    body: PublishBusRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
) -> dict[str, Any]:
    service = get_aesthetics_service()
    msgs = service.publish_to_bus(
        body.verdict,
        to_agent_ids=body.to_agent_ids or None,
        correlation_id=body.correlation_id or str(context.correlation_id),
    )
    return {
        "ok": True,
        "messages": msgs,
        "count": len(msgs),
        "correlation_id": str(context.correlation_id),
    }


@router.get("/bus")
async def list_aesthetic_critique_bus(
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    to_agent_id: Annotated[str | None, Query()] = None,
    artifact_ref: Annotated[str | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
) -> dict[str, Any]:
    service = get_aesthetics_service()
    return {
        "items": service.list_bus(
            to_agent_id=to_agent_id,
            artifact_ref=artifact_ref,
            limit=limit,
        ),
        "correlation_id": str(context.correlation_id),
    }


@router.post("/memory/decision")
async def record_project_decision(
    body: MemoryDecisionRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
) -> dict[str, Any]:
    service = get_aesthetics_service()
    try:
        result = service.record_decision(
            project_id=body.project_id,
            artifact_ref=body.artifact_ref,
            decision=body.decision,
            note=body.note,
        )
    except ValueError as exc:
        _bad(str(context.correlation_id), str(exc))
    return {**result, "correlation_id": str(context.correlation_id)}


@router.get("/memory/{project_id}")
async def get_project_memory(
    project_id: str,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
) -> dict[str, Any]:
    service = get_aesthetics_service()
    mem = service.project_memory(project_id, limit=limit)
    return {**mem, "correlation_id": str(context.correlation_id)}


@router.post("/handoff/attach")
async def attach_verdict_handoff(
    body: HandoffAttachRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
) -> dict[str, Any]:
    service = get_aesthetics_service()
    updated = service.attach_to_handoff(body.handoff, body.verdict)
    return {
        "ok": True,
        "handoff": updated,
        "correlation_id": str(context.correlation_id),
    }
