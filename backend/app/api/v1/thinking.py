"""Host API: offline thinking-model hooks for agent loops."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends

from app.api.v1.dependencies import AuthenticatedRequestContext, get_authenticated_request_context
from app.thinking.service import ThinkingRecommendRequest, get_thinking_service

router = APIRouter(prefix="/thinking", tags=["thinking-models"])


@router.get("/policy")
async def thinking_policy(
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
) -> dict[str, Any]:
    service = get_thinking_service()
    return {**service.policy(), "correlation_id": str(context.correlation_id)}


@router.get("/catalog")
async def thinking_catalog(
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
) -> dict[str, Any]:
    service = get_thinking_service()
    return {**service.catalog(), "correlation_id": str(context.correlation_id)}


@router.post("/recommend")
async def thinking_recommend(
    body: ThinkingRecommendRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
) -> dict[str, Any]:
    service = get_thinking_service()
    result = service.recommend(body)
    return {**result, "correlation_id": str(context.correlation_id)}
