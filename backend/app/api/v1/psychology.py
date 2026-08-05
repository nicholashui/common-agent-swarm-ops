"""Host API: offline psychology profile / recommendation."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query

from app.api.v1.dependencies import AuthenticatedRequestContext, get_authenticated_request_context
from app.psychology.service import (
    PsychProfileRequest,
    PsychRecommendRequest,
    get_psychology_service,
)

router = APIRouter(prefix="/psychology", tags=["psychology"])


@router.get("/policy")
async def psychology_policy(
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
) -> dict[str, Any]:
    return {
        **get_psychology_service().policy(),
        "correlation_id": str(context.correlation_id),
    }


@router.post("/profile")
async def psychology_profile(
    body: PsychProfileRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
) -> dict[str, Any]:
    result = get_psychology_service().profile(body)
    return {**result, "correlation_id": str(context.correlation_id)}


@router.post("/recommend")
async def psychology_recommend(
    body: PsychRecommendRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
) -> dict[str, Any]:
    result = get_psychology_service().recommend(body)
    return {**result, "correlation_id": str(context.correlation_id)}


@router.get("/runs")
async def psychology_runs(
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> dict[str, Any]:
    return {
        "items": get_psychology_service().recent(limit=limit),
        "correlation_id": str(context.correlation_id),
    }
