"""Versioned FastAPI router for the public Host control plane."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.v1.adoption import router as adoption_router
from app.api.v1.aesthetics import router as aesthetics_router
from app.api.v1.agent_loops import router as agent_loops_router
from app.api.v1.coding import router as coding_router
from app.api.v1.complex_problem import router as complex_problem_router
from app.api.v1.creative import router as creative_router
from app.api.v1.intent import router as intent_router
from app.api.v1.knowledge import router as knowledge_router
from app.api.v1.llm_usage import router as llm_usage_router
from app.api.v1.lqr import router as lqr_router
from app.api.v1.optimization import router as optimization_router
from app.api.v1.podcast import router as podcast_router
from app.api.v1.psychology import router as psychology_router
from app.api.v1.rag import router as rag_router
from app.api.v1.research import router as research_router
from app.api.v1.screenwriting import router as screenwriting_router
from app.api.v1.skill_evals import router as skill_evals_router
from app.api.v1.skills_catalog import router as skills_catalog_router
from app.api.v1.strategic import router as strategic_router
from app.api.v1.tech_radar import router as tech_radar_router
from app.api.v1.thinking import router as thinking_router
from app.api.v1.approvals import router as approvals_router
from app.api.v1.commons import router as commons_router
from app.api.v1.composer import router as composer_router
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
    router.include_router(composer_router)
    router.include_router(swarms_router)
    router.include_router(agent_loops_router)
    router.include_router(aesthetics_router)
    router.include_router(rag_router)
    router.include_router(knowledge_router)
    router.include_router(research_router)
    router.include_router(thinking_router)
    router.include_router(intent_router)
    router.include_router(optimization_router)
    router.include_router(creative_router)
    router.include_router(complex_problem_router)
    router.include_router(strategic_router)
    router.include_router(llm_usage_router)
    router.include_router(psychology_router)
    router.include_router(coding_router)
    router.include_router(podcast_router)
    router.include_router(screenwriting_router)
    router.include_router(tech_radar_router)
    router.include_router(lqr_router)
    router.include_router(skills_catalog_router)
    router.include_router(skill_evals_router)
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
