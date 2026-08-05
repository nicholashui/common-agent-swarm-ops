"""Host API: offline Research Agent foundation."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query, status

from app.api.v1.dependencies import AuthenticatedRequestContext, get_authenticated_request_context
from app.api.v1.errors import PublicApiException
from app.api.v1.schemas import PublicError
from app.research.service import ResearchQueryRequest, get_research_service

router = APIRouter(prefix="/research", tags=["research"])


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
async def research_policy(
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
) -> dict[str, Any]:
    service = get_research_service()
    return {**service.policy(), "correlation_id": str(context.correlation_id)}


@router.post("/query")
async def research_query(
    body: ResearchQueryRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
) -> dict[str, Any]:
    service = get_research_service()
    result = service.query(body)
    if result.get("ok") is False:
        _denied(str(context.correlation_id), str(result.get("error") or "research denied"))
    return {**result, "correlation_id": str(context.correlation_id)}


@router.get("/runs")
async def research_runs(
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> dict[str, Any]:
    service = get_research_service()
    return {
        "items": service.recent(limit=limit),
        "correlation_id": str(context.correlation_id),
    }
