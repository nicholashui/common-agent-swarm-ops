"""Host API: offline complex-problem process foundation."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query

from app.api.v1.dependencies import AuthenticatedRequestContext, get_authenticated_request_context
from app.complex_problem.service import ComplexProblemRequest, get_complex_problem_service

router = APIRouter(prefix="/complex-problem", tags=["complex-problem"])


@router.get("/policy")
async def complex_problem_policy(
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
) -> dict[str, Any]:
    return {
        **get_complex_problem_service().policy(),
        "correlation_id": str(context.correlation_id),
    }


@router.post("/solve")
async def complex_problem_solve(
    body: ComplexProblemRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
) -> dict[str, Any]:
    result = get_complex_problem_service().solve(body)
    return {**result, "correlation_id": str(context.correlation_id)}


@router.get("/runs")
async def complex_problem_runs(
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> dict[str, Any]:
    return {
        "items": get_complex_problem_service().recent(limit=limit),
        "correlation_id": str(context.correlation_id),
    }
