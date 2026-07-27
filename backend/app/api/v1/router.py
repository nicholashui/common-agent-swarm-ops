"""Versioned FastAPI router for the public Host control plane."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.v1.adoption import router as adoption_router
from app.api.v1.approvals import router as approvals_router
from app.api.v1.commons import router as commons_router
from app.api.v1.definitions import router as definitions_router
from app.api.v1.dependencies import (
    AuthenticatedRequestContext,
    get_authenticated_request_context,
)
from app.api.v1.evaluation import router as evaluation_router
from app.api.v1.events import router as events_router
from app.api.v1.evolution import router as evolution_router
from app.api.v1.memory import router as memory_router
from app.api.v1.product_extended import router as product_extended_router
from app.api.v1.product_ops import router as product_ops_router
from app.api.v1.runs import router as runs_router
from app.api.v1.schemas import AuthenticatedContextResponse
from app.api.v1.swarms import router as swarms_router
from app.api.v1.va import router as va_router
from app.api.v1.video import router as video_router


def create_public_api_router() -> APIRouter:
    """Build the sole browser router with trusted context required for every route."""
    router = APIRouter(dependencies=[Depends(get_authenticated_request_context)])
    router.include_router(adoption_router)
    router.include_router(definitions_router)
    router.include_router(runs_router)
    router.include_router(approvals_router)
    router.include_router(evaluation_router)
    router.include_router(evolution_router)
    router.include_router(memory_router)
    router.include_router(events_router)
    router.include_router(video_router)
    router.include_router(va_router)
    # Product façade for redesigned UI (commons registry, swarms, activity, extended).
    router.include_router(commons_router)
    router.include_router(swarms_router)
    router.include_router(product_ops_router)
    router.include_router(product_extended_router)
    return router


api_router = create_public_api_router()


@api_router.get(
    "/context",
    response_model=AuthenticatedContextResponse,
    tags=["control-plane"],
)
async def read_authenticated_context(
    context: Annotated[
        AuthenticatedRequestContext,
        Depends(get_authenticated_request_context),
    ],
) -> AuthenticatedContextResponse:
    """Expose only the identity derived from trusted request state."""
    return AuthenticatedContextResponse(
        organization_id=context.organization_id,
        actor_id=context.actor_id,
        correlation_id=context.correlation_id,
    )
