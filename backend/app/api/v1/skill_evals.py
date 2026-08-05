"""Host API: offline skill golden evaluation harness."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict, Field

from app.api.v1.dependencies import AuthenticatedRequestContext, get_authenticated_request_context
from app.skill_evals.harness import run_golden_suite

router = APIRouter(prefix="/skill-evals", tags=["skill-evals"])


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class SkillEvalRunRequest(StrictModel):
    skills: list[str] = Field(default_factory=list, max_length=32)


@router.get("/policy")
async def skill_evals_policy(
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
) -> dict[str, Any]:
    return {
        "skills": [
            "rag",
            "knowledge",
            "research",
            "thinking",
            "aesthetics",
            "intent",
            "optimization",
            "creative",
            "complex_problem",
            "strategic",
            "llm_usage",
            "psychology",
            "coding",
            "podcast",
            "screenwriting",
            "tech_radar",
            "lqr",
        ],
        "live_llm_judge": False,
        "note": "Offline golden harness for Host skill foundations.",
        "correlation_id": str(context.correlation_id),
    }


@router.post("/run")
async def skill_evals_run(
    body: SkillEvalRunRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
) -> dict[str, Any]:
    result = run_golden_suite(skills=body.skills or None)
    return {**result, "correlation_id": str(context.correlation_id)}
