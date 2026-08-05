"""Host API: offline Knowledge Router foundation."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query, status

from app.api.v1.dependencies import AuthenticatedRequestContext, get_authenticated_request_context
from app.api.v1.errors import PublicApiException
from app.api.v1.schemas import PublicError
from app.knowledge.models import KnowledgeRouteRequest
from app.knowledge.service import get_knowledge_router_service

router = APIRouter(prefix="/knowledge", tags=["knowledge-router"])


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
async def knowledge_policy(
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
) -> dict[str, Any]:
    service = get_knowledge_router_service()
    return {**service.policy(), "correlation_id": str(context.correlation_id)}


@router.post("/route")
async def knowledge_route(
    body: KnowledgeRouteRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
) -> dict[str, Any]:
    service = get_knowledge_router_service()
    result = service.route(body)
    if result.get("ok") is False:
        _denied(str(context.correlation_id), str(result.get("error") or "route denied"))
    return {**result, "correlation_id": str(context.correlation_id)}


@router.get("/routes")
async def knowledge_recent_routes(
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> dict[str, Any]:
    service = get_knowledge_router_service()
    return {
        "items": service.recent(limit=limit),
        "correlation_id": str(context.correlation_id),
    }
