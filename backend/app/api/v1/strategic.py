"""Host API: offline strategic goal foundation."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query

from app.api.v1.dependencies import AuthenticatedRequestContext, get_authenticated_request_context
from app.strategic.service import StrategicPlanRequest, get_strategic_service

router = APIRouter(prefix="/strategic", tags=["strategic"])


@router.get("/policy")
async def strategic_policy(
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
) -> dict[str, Any]:
    return {**get_strategic_service().policy(), "correlation_id": str(context.correlation_id)}


@router.post("/plan")
async def strategic_plan(
    body: StrategicPlanRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
) -> dict[str, Any]:
    result = get_strategic_service().plan(body)
    return {**result, "correlation_id": str(context.correlation_id)}


@router.get("/runs")
async def strategic_runs(
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> dict[str, Any]:
    return {
        "items": get_strategic_service().recent(limit=limit),
        "correlation_id": str(context.correlation_id),
    }
