"""Host API: offline screenwriting strategic foundation."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query

from app.api.v1.dependencies import AuthenticatedRequestContext, get_authenticated_request_context
from app.screenwriting.service import ScreenplayPlanRequest, get_screenwriting_service

router = APIRouter(prefix="/screenwriting", tags=["screenwriting"])


@router.get("/policy")
async def screenwriting_policy(
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
) -> dict[str, Any]:
    return {
        **get_screenwriting_service().policy(),
        "correlation_id": str(context.correlation_id),
    }


@router.post("/plan")
async def screenwriting_plan(
    body: ScreenplayPlanRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
) -> dict[str, Any]:
    result = get_screenwriting_service().plan(body)
    return {**result, "correlation_id": str(context.correlation_id)}


@router.get("/runs")
async def screenwriting_runs(
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> dict[str, Any]:
    return {
        "items": get_screenwriting_service().recent(limit=limit),
        "correlation_id": str(context.correlation_id),
    }
