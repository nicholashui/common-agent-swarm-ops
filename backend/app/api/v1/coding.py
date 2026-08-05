"""Host API: offline coding-agent plan-only foundation."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query, status

from app.api.v1.dependencies import AuthenticatedRequestContext, get_authenticated_request_context
from app.api.v1.errors import PublicApiException
from app.api.v1.schemas import PublicError
from app.coding.service import CodingPlanRequest, get_coding_service

router = APIRouter(prefix="/coding", tags=["coding"])


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
async def coding_policy(
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
) -> dict[str, Any]:
    return {**get_coding_service().policy(), "correlation_id": str(context.correlation_id)}


@router.post("/plan")
async def coding_plan(
    body: CodingPlanRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
) -> dict[str, Any]:
    result = get_coding_service().plan(body)
    if result.get("ok") is False:
        _denied(str(context.correlation_id), str(result.get("error") or "coding denied"))
    return {**result, "correlation_id": str(context.correlation_id)}


@router.get("/runs")
async def coding_runs(
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> dict[str, Any]:
    return {
        "items": get_coding_service().recent(limit=limit),
        "correlation_id": str(context.correlation_id),
    }
