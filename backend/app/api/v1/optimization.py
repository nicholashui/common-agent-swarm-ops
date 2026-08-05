"""Host API: offline Optimization Agent foundation."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query, status

from app.api.v1.dependencies import AuthenticatedRequestContext, get_authenticated_request_context
from app.api.v1.errors import PublicApiException
from app.api.v1.schemas import PublicError
from app.optimization.service import OptimizeRequest, get_optimization_service

router = APIRouter(prefix="/optimization", tags=["optimization"])


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
async def optimization_policy(
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
) -> dict[str, Any]:
    service = get_optimization_service()
    return {**service.policy(), "correlation_id": str(context.correlation_id)}


@router.post("/recommend")
async def optimization_recommend(
    body: OptimizeRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
) -> dict[str, Any]:
    service = get_optimization_service()
    result = service.optimize(body)
    if result.get("ok") is False:
        _denied(str(context.correlation_id), str(result.get("error") or "optimization denied"))
    return {**result, "correlation_id": str(context.correlation_id)}


@router.get("/runs")
async def optimization_runs(
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> dict[str, Any]:
    service = get_optimization_service()
    return {
        "items": service.recent(limit=limit),
        "correlation_id": str(context.correlation_id),
    }
