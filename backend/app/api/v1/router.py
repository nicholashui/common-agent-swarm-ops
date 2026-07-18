"""Versioned FastAPI router for the public Host control plane."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.v1.approvals import router as approvals_router
from app.api.v1.definitions import router as definitions_router
from app.api.v1.dependencies import (
    AuthenticatedRequestContext,
    get_authenticated_request_context,
)
from app.api.v1.evaluation import router as evaluation_router
from app.api.v1.evolution import router as evolution_router
from app.api.v1.memory import router as memory_router
from app.api.v1.runs import router as runs_router
from app.api.v1.schemas import AuthenticatedContextResponse
from app.api.v1.video import router as video_router

api_router = APIRouter()
api_router.include_router(definitions_router)
api_router.include_router(runs_router)
api_router.include_router(approvals_router)
api_router.include_router(evaluation_router)
api_router.include_router(evolution_router)
api_router.include_router(memory_router)
api_router.include_router(video_router)


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
