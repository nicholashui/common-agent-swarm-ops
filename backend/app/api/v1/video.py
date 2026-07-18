"""Authenticated, local-only versioned Video_Pack artifact and release routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.v1.dependencies import AuthenticatedRequestContext, get_authenticated_request_context
from app.api.v1.errors import require_value
from app.api.v1.schemas import (
    ActionPreviewResponse,
    VideoArtifactHandoffRequest,
    VideoArtifactResponse,
    VideoReleaseConditionResponse,
    VideoReleaseRequestResponse,
)
from app.api.v1.services import ControlPlaneServices, get_control_plane_services
from app.video.artifacts import (
    NamedReleaseCheck,
    ReleaseRequest,
    VideoArtifactVersion,
    VideoArtifactVersionId,
)

router = APIRouter(prefix="/video", tags=["video"])


@router.post(
    "/artifacts",
    response_model=VideoArtifactResponse,
    status_code=status.HTTP_201_CREATED,
)
async def handoff_video_artifact(
    request: VideoArtifactHandoffRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    services: Annotated[ControlPlaneServices, Depends(get_control_plane_services)],
) -> VideoArtifactResponse:
    """Retain a new immutable artifact version without invoking a media provider."""
    version = require_value(
        services.video_release_service.create_artifact_version(
            context.organization_id,
            context.correlation_id,
            request.artifact_id,
            tuple(VideoArtifactVersionId(value) for value in request.parent_version_ids),
            request.rights_and_consent_passed,
            request.provenance_and_signoff_passed,
            tuple(
                NamedReleaseCheck(check.name, check.passed, check.evidence_reference)
                for check in request.quality_checks
            ),
            tuple(
                NamedReleaseCheck(check.name, check.passed, check.evidence_reference)
                for check in request.release_checks
            ),
        )
    )
    return _artifact_response(version)


@router.post(
    "/artifacts/{artifact_version_id}/release-requests",
    response_model=VideoReleaseRequestResponse,
    status_code=status.HTTP_201_CREATED,
)
async def request_video_release_readiness(
    artifact_version_id: str,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    services: Annotated[ControlPlaneServices, Depends(get_control_plane_services)],
) -> VideoReleaseRequestResponse:
    """Evaluate and retain release readiness locally; no artifact is released."""
    decision = require_value(
        services.video_release_service.request_release(
            context.organization_id,
            context.correlation_id,
            VideoArtifactVersionId(artifact_version_id),
        )
    )
    return _release_response(decision)


@router.get("/release-requests/{release_request_id}", response_model=VideoReleaseRequestResponse)
async def read_video_release_request(
    release_request_id: str,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    services: Annotated[ControlPlaneServices, Depends(get_control_plane_services)],
) -> VideoReleaseRequestResponse:
    """Return one tenant-scoped retained readiness decision without executing a release."""
    decision = require_value(
        services.video_release_service.get_release_request(
            context.organization_id, context.correlation_id, release_request_id
        )
    )
    return _release_response(decision)


def _artifact_response(version: VideoArtifactVersion) -> VideoArtifactResponse:
    """Project immutable artifact metadata without exposing any source media payload."""
    return VideoArtifactResponse(
        artifact_id=str(version.artifact_id),
        artifact_version_id=str(version.artifact_version_id),
        parent_version_ids=[str(value) for value in version.parent_version_ids],
        created_at=version.metadata.created_at,
        rights_and_consent_passed=version.rights_and_consent_passed,
        provenance_and_signoff_passed=version.provenance_and_signoff_passed,
    )


def _release_response(decision: ReleaseRequest) -> VideoReleaseRequestResponse:
    """Return all retained gate outcomes plus a no-effect action preview."""
    return VideoReleaseRequestResponse(
        release_request_id=str(decision.release_request_id),
        artifact_version_id=str(decision.artifact_version_id),
        decision=decision.decision.value,
        artifact_released=False,
        unmet_conditions=list(decision.unmet_conditions),
        conditions=[
            VideoReleaseConditionResponse(
                name=item.name,
                passed=item.passed,
                evidence_references=list(item.evidence_references),
            )
            for item in decision.conditions
        ],
        requested_at=decision.metadata.created_at,
        action_preview=ActionPreviewResponse(
            action_id=f"release-request:{decision.release_request_id}",
            summary="Validate retained local video release gates.",
            intended_effect=("A readiness decision is stored; no video artifact is released."),
            emitted_at=decision.metadata.created_at,
            confidence=1.0,
            uncertainty=(
                "This control plane does not invoke media providers or release artifacts."
            ),
            correction_control="Resolve every reported gate and submit a new readiness request.",
        ),
    )
