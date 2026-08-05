"""Host API: offline General Creative Agent foundation."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query, status

from app.api.v1.dependencies import AuthenticatedRequestContext, get_authenticated_request_context
from app.api.v1.errors import PublicApiException
from app.api.v1.schemas import PublicError
from app.creative.service import CreativeIdeateRequest, get_creative_service

router = APIRouter(prefix="/creative", tags=["creative"])


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
async def creative_policy(
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
) -> dict[str, Any]:
    return {**get_creative_service().policy(), "correlation_id": str(context.correlation_id)}


@router.post("/ideate")
async def creative_ideate(
    body: CreativeIdeateRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
) -> dict[str, Any]:
    result = get_creative_service().ideate(body)
    if result.get("ok") is False:
        _denied(str(context.correlation_id), str(result.get("error") or "creative denied"))
    return {**result, "correlation_id": str(context.correlation_id)}


@router.get("/runs")
async def creative_runs(
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> dict[str, Any]:
    return {
        "items": get_creative_service().recent(limit=limit),
        "correlation_id": str(context.correlation_id),
    }


@router.get("/patterns")
async def creative_patterns(
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    limit: Annotated[int, Query(ge=1, le=50)] = 12,
) -> dict[str, Any]:
    """Lean process-local learned motifs (not full run history, not durable memory)."""
    result = get_creative_service().patterns(limit=limit)
    return {**result, "correlation_id": str(context.correlation_id)}
