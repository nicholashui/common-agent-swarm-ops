"""Versioned deterministic local evaluation routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.v1.dependencies import AuthenticatedRequestContext, get_authenticated_request_context
from app.api.v1.errors import require_value
from app.api.v1.schemas import EvaluationRunRequest, EvaluationRunResponse
from app.api.v1.services import ControlPlaneServices, get_control_plane_services

router = APIRouter(tags=["evaluation"])


@router.post(
    "/evaluations",
    response_model=EvaluationRunResponse,
    status_code=status.HTTP_201_CREATED,
)
async def run_evaluation(
    request: EvaluationRunRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    services: Annotated[ControlPlaneServices, Depends(get_control_plane_services)],
) -> EvaluationRunResponse:
    """Run retained local golden tasks and named checks without external dependencies."""
    evaluation = require_value(
        services.evaluation_service.run_suite(
            context.organization_id, context.correlation_id, request.configuration
        )
    )
    return EvaluationRunResponse(
        evaluation_run_id=evaluation.evaluation_run_id,
        completed=evaluation.completed,
        transition_permitted=evaluation.transition_permitted,
        configuration_digest=evaluation.configuration_digest,
        result_count=len(evaluation.results),
        completed_at=evaluation.metadata.updated_at,
    )
