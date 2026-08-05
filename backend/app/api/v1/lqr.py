"""Host API: offline LQR workflow overview."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query

from app.api.v1.dependencies import AuthenticatedRequestContext, get_authenticated_request_context
from app.lqr.service import LqrOverviewRequest, get_lqr_service

router = APIRouter(prefix="/lqr", tags=["lqr"])


@router.get("/policy")
async def lqr_policy(
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
) -> dict[str, Any]:
    return {**get_lqr_service().policy(), "correlation_id": str(context.correlation_id)}


@router.post("/overview")
async def lqr_overview(
    body: LqrOverviewRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
) -> dict[str, Any]:
    result = get_lqr_service().overview(body)
    return {**result, "correlation_id": str(context.correlation_id)}


@router.get("/runs")
async def lqr_runs(
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> dict[str, Any]:
    return {
        "items": get_lqr_service().recent(limit=limit),
        "correlation_id": str(context.correlation_id),
    }
