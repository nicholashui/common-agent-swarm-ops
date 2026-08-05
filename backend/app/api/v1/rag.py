"""Host API: offline Agentic RAG foundation."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query, status

from app.api.v1.dependencies import AuthenticatedRequestContext, get_authenticated_request_context
from app.api.v1.errors import PublicApiException
from app.api.v1.schemas import PublicError
from app.rag.models import RagIngestRequest, RagQueryRequest
from app.rag.service import get_rag_service

router = APIRouter(prefix="/rag", tags=["agentic-rag"])


def _bad(correlation_id: str, message: str) -> None:
    raise PublicApiException(
        status_code=status.HTTP_400_BAD_REQUEST,
        error=PublicError(
            code="validation_failed",
            message=message,
            correlation_id=correlation_id,
            retryable=False,
        ),
    )


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
async def rag_policy(
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
) -> dict[str, Any]:
    service = get_rag_service()
    return {**service.policy(), "correlation_id": str(context.correlation_id)}


@router.get("/index")
async def rag_index_stats(
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
) -> dict[str, Any]:
    service = get_rag_service()
    return {
        "stats": service.index_stats(),
        "documents": service.list_documents(limit=50),
        "correlation_id": str(context.correlation_id),
    }


@router.post("/ingest")
async def rag_ingest(
    body: RagIngestRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
) -> dict[str, Any]:
    service = get_rag_service()
    try:
        result = service.ingest(body)
    except ValueError as exc:
        _bad(str(context.correlation_id), str(exc))
    return {**result, "correlation_id": str(context.correlation_id)}


@router.post("/query")
async def rag_query(
    body: RagQueryRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
) -> dict[str, Any]:
    service = get_rag_service()
    result = service.query(body)
    if result.get("ok") is False:
        err = str(result.get("error") or "query failed")
        if "not enabled" in err or "Fail-closed" in err:
            _denied(str(context.correlation_id), err)
        _bad(str(context.correlation_id), err)
    return {**result, "correlation_id": str(context.correlation_id)}


@router.get("/runs")
async def rag_recent_runs(
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> dict[str, Any]:
    service = get_rag_service()
    return {
        "items": service.recent_runs(limit=limit),
        "correlation_id": str(context.correlation_id),
    }


@router.get("/bus")
async def rag_critique_bus(
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
) -> dict[str, Any]:
    service = get_rag_service()
    return {
        "items": service.list_bus(limit=limit),
        "correlation_id": str(context.correlation_id),
    }
