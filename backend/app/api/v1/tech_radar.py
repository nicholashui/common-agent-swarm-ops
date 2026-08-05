"""Host API: offline video-gen tech radar."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends

from app.api.v1.dependencies import AuthenticatedRequestContext, get_authenticated_request_context
from app.tech_radar.service import TechRadarAdviseRequest, get_tech_radar_service

router = APIRouter(prefix="/tech-radar", tags=["tech-radar"])


@router.get("/policy")
async def tech_radar_policy(
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
) -> dict[str, Any]:
    return {
        **get_tech_radar_service().policy(),
        "correlation_id": str(context.correlation_id),
    }


@router.get("/catalog")
async def tech_radar_catalog(
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
) -> dict[str, Any]:
    result = get_tech_radar_service().catalog()
    return {**result, "correlation_id": str(context.correlation_id)}


@router.post("/advise")
async def tech_radar_advise(
    body: TechRadarAdviseRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
) -> dict[str, Any]:
    result = get_tech_radar_service().advise(body)
    return {**result, "correlation_id": str(context.correlation_id)}
