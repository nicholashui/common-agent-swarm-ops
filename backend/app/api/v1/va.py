"""Public_API routes for the optional VA translation/projection layer."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.v1.dependencies import AuthenticatedRequestContext, get_authenticated_request_context
from app.api.v1.errors import require_value
from app.api.v1.schemas import (
    ValidationIssueResponse,
    VaMetadataResponse,
    VaProductionActionRequest,
    VaProductionActionResponse,
    VaRunProjectionResponse,
)
from app.api.v1.services import ControlPlaneServices, get_control_plane_services
from app.models.control_plane import CommonPatternVersionId, RunProvenanceId
from app.va.service import (
    VaActionOutcome,
    VaMetadata,
    VaMetadataValidation,
    VaProductionAction,
    VaRunProjection,
)

router = APIRouter(prefix="/va", tags=["va-domain-adapter"])


@router.get(
    "/patterns/{pattern_version_id}/metadata",
    response_model=VaMetadataResponse,
)
async def read_va_metadata(
    pattern_version_id: str,
    template: Annotated[str, Query(min_length=1, max_length=200)],
    production_phase: Annotated[str, Query(min_length=1, max_length=200)],
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    services: Annotated[ControlPlaneServices, Depends(get_control_plane_services)],
) -> VaMetadataResponse:
    """Expose VA template/phase metadata only under the versioned Public_API."""
    validation = require_value(
        services.va_domain_adapter.validate_metadata(
            context.organization_id,
            context.correlation_id,
            VaMetadata(
                CommonPatternVersionId(pattern_version_id), template, production_phase
            ),
        )
    )
    return _metadata_response(validation)


@router.post("/actions", response_model=VaProductionActionResponse)
async def invoke_va_action(
    request: VaProductionActionRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    services: Annotated[ControlPlaneServices, Depends(get_control_plane_services)],
) -> VaProductionActionResponse:
    """Map a validated VA production action to the authorized canonical command path."""
    outcome = require_value(
        services.va_domain_adapter.invoke_action(
            context.organization_id,
            context.actor_id,
            context.correlation_id,
            VaMetadata(
                CommonPatternVersionId(request.pattern_version_id),
                request.template,
                request.production_phase,
            ),
            VaProductionAction(request.action),
            request.run_reference,
            request.idempotency_key,
        )
    )
    return _action_response(outcome)


@router.get("/runs/{run_reference}/evidence", response_model=VaRunProjectionResponse)
async def read_va_run_evidence(
    run_reference: str,
    provenance_id: Annotated[str, Query(min_length=1, max_length=200)],
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    services: Annotated[ControlPlaneServices, Depends(get_control_plane_services)],
) -> VaRunProjectionResponse:
    """Return only organization-authorized redacted common evidence for a VA run."""
    projection = require_value(
        services.va_domain_adapter.project_run(
            context.organization_id,
            context.correlation_id,
            run_reference,
            RunProvenanceId(provenance_id),
        )
    )
    return _projection_response(projection)


def _metadata_response(validation: VaMetadataValidation) -> VaMetadataResponse:
    return VaMetadataResponse(
        pattern_version_id=str(validation.metadata.pattern_version_id),
        template=validation.metadata.template,
        production_phase=validation.metadata.production_phase,
        valid=validation.valid,
        pattern_content_digest=validation.pattern_content_digest,
        validation_issues=[
            ValidationIssueResponse(field=field.name, reason=field.reason)
            for field in validation.fields
        ],
    )


def _action_response(outcome: VaActionOutcome) -> VaProductionActionResponse:
    return VaProductionActionResponse(
        metadata=_metadata_response(outcome.validation),
        canonical_command=outcome.canonical_command,
        canonical_subject_reference=outcome.canonical_subject_reference,
        work_item_id=outcome.work_item_id,
        work_state=outcome.work_state,
        replayed=outcome.replayed,
        evidence_projection_path=(
            f"/api/v1/va/runs/{outcome.canonical_subject_reference.removeprefix('run:')}"
            "/evidence"
        ),
    )


def _projection_response(projection: VaRunProjection) -> VaRunProjectionResponse:
    return VaRunProjectionResponse(
        run_reference=projection.run_reference,
        common_agent_versions=[dict(value) for value in projection.common_agent_versions],
        agent_tasks=[dict(value) for value in projection.agent_tasks],
        artifact_handoffs=[dict(value) for value in projection.artifact_handoffs],
        critique_records=[dict(value) for value in projection.critique_records],
        quality_evidence=[dict(value) for value in projection.quality_evidence],
        approval_gates=[dict(value) for value in projection.approval_gates],
        pinned_provenance=dict(projection.pinned_provenance),
    )
