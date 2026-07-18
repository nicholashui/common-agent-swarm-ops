"""Versioned workflow-definition and domain-registration routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.v1.dependencies import AuthenticatedRequestContext, get_authenticated_request_context
from app.api.v1.errors import require_value
from app.api.v1.schemas import (
    DefinitionRequest,
    DefinitionResponse,
    DomainRegistrationRequest,
    DomainRegistrationResponse,
    PackAgentResponse,
    ValidationIssueResponse,
)
from app.api.v1.services import ControlPlaneServices, get_control_plane_services
from app.models.common import utc_now

router = APIRouter(tags=["definitions"])


@router.post(
    "/domains/register",
    response_model=DomainRegistrationResponse,
    responses={422: {"description": "Registration failed validation."}},
)
async def register_domain(
    request: DomainRegistrationRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    services: Annotated[ControlPlaneServices, Depends(get_control_plane_services)],
) -> DomainRegistrationResponse:
    """Register a pack as draft/registered only, scoped to trusted request identity."""
    result = services.register_domain(
        context.organization_id,
        context.correlation_id,
        request.manifest,
    )
    record = require_value(result)
    return DomainRegistrationResponse(
        pack_id=record.pack_id,
        status=record.status,
        registered_at=record.metadata.updated_at,
        agents=[
            PackAgentResponse(
                agent_id=agent.agent_id,
                status=agent.status,
                production_active=False,
                production_activation_denied=agent.production_activation_denied,
            )
            for agent in record.agents
        ],
        validation_issues=[
            ValidationIssueResponse(field=issue.field, reason=issue.message)
            for issue in record.validation_report.issues
        ],
    )


@router.post(
    "/workflows/definitions",
    response_model=DefinitionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_definition(
    request: DefinitionRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    services: Annotated[ControlPlaneServices, Depends(get_control_plane_services)],
) -> DefinitionResponse:
    """Validate and retain a versioned data-only definition before run creation."""
    result = services.register_definition(
        context.organization_id,
        context.correlation_id,
        request.definition,
        utc_now(),
    )
    stored = require_value(result)
    engine = stored.definition.get("engine")
    assert isinstance(engine, str)
    return DefinitionResponse(
        workflow_id=stored.workflow_id,
        version=stored.version,
        engine=engine,
        registered_at=stored.registered_at,
    )
