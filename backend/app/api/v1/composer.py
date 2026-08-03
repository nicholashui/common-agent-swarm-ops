"""Product façade: AI-first swarm composition (goal/spec in → AI picks workflow).

Human is required only when AI cannot determine a solution (requirement conflicts).
"""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, status
from pydantic import Field

from app.api.v1.dependencies import AuthenticatedRequestContext, get_authenticated_request_context
from app.api.v1.errors import PublicApiException
from app.api.v1.product_facade import ProductFacadeService, get_product_facade
from app.api.v1.schemas import PublicError, StrictSchema

router = APIRouter(prefix="/composer", tags=["composer"])


class ComposerRecommendRequest(StrictSchema):
    """Human supplies goal/spec; optional resolutions for prior open questions."""

    goal: str = Field(min_length=1, max_length=2_000)
    max_slots: int = Field(default=8, ge=3, le=12)
    human_resolutions: dict[str, str] = Field(default_factory=dict, max_length=20)


class ComposerMaterializeRequest(StrictSchema):
    """Materialize AI recommendation into a draft swarm (blocked if needs_hitl)."""

    goal: str = Field(min_length=1, max_length=2_000)
    swarm_name: str | None = Field(default=None, max_length=200)
    max_slots: int = Field(default=8, ge=3, le=12)
    human_resolutions: dict[str, str] = Field(default_factory=dict, max_length=20)


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


def _bad_request(correlation_id: str, message: str) -> None:
    raise PublicApiException(
        status_code=status.HTTP_400_BAD_REQUEST,
        error=PublicError(
            code="validation_failed",
            message=message,
            correlation_id=correlation_id,
            retryable=False,
        ),
    )


@router.post("/recommend")
async def recommend_composition(
    request: ComposerRecommendRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> dict[str, Any]:
    """AI-pick pattern + agents. Returns needs_hitl + open_questions when blocked."""
    result = facade.recommend_composition(
        organization_id=context.organization_id,
        goal=request.goal,
        max_slots=request.max_slots,
        human_resolutions=request.human_resolutions or None,
    )
    if not result.get("ok"):
        _bad_request(str(context.correlation_id), str(result.get("message") or "Recommend failed."))
    return result


@router.post("/materialize")
async def materialize_composition(
    request: ComposerMaterializeRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> dict[str, Any]:
    """AI recommend + create draft, or return needs_hitl without creating a swarm."""
    result = facade.materialize_ai_composition(
        organization_id=context.organization_id,
        actor_id=context.actor_id,
        correlation_id=context.correlation_id,
        goal=request.goal,
        swarm_name=request.swarm_name,
        max_slots=request.max_slots,
        human_resolutions=request.human_resolutions or None,
    )
    if result is None:
        _denied(
            str(context.correlation_id),
            "Could not materialize AI composition (create swarm or add members denied).",
        )
    return result
