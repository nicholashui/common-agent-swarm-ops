"""Host API: offline LLM usage policy ledger."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query, status

from app.api.v1.dependencies import AuthenticatedRequestContext, get_authenticated_request_context
from app.api.v1.errors import PublicApiException
from app.api.v1.schemas import PublicError
from app.llm_usage.service import LlmUsageRecordRequest, get_llm_usage_service
from pydantic import Field

from app.api.v1.schemas import StrictSchema

router = APIRouter(prefix="/llm-usage", tags=["llm-usage"])


class RecommendModeRequest(StrictSchema):
    goal: str = Field(default="", max_length=4_000)


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
async def llm_usage_policy(
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
) -> dict[str, Any]:
    return {**get_llm_usage_service().policy(), "correlation_id": str(context.correlation_id)}


@router.post("/record")
async def llm_usage_record(
    body: LlmUsageRecordRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
) -> dict[str, Any]:
    result = get_llm_usage_service().record(body)
    if result.get("ok") is False:
        _denied(str(context.correlation_id), str(result.get("error") or "denied"))
    return {**result, "correlation_id": str(context.correlation_id)}


@router.post("/recommend-mode")
async def llm_usage_recommend_mode(
    body: RecommendModeRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
) -> dict[str, Any]:
    result = get_llm_usage_service().recommend_mode(goal=body.goal)
    return {**result, "correlation_id": str(context.correlation_id)}


@router.get("/entries")
async def llm_usage_entries(
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
) -> dict[str, Any]:
    return {
        "items": get_llm_usage_service().recent(limit=limit),
        "correlation_id": str(context.correlation_id),
    }
