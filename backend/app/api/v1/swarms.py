"""Product façade: swarm drafts, graph revisions, members, runs, exports."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, status
from pydantic import Field

from app.api.v1.dependencies import AuthenticatedRequestContext, get_authenticated_request_context
from app.api.v1.errors import PublicApiException
from app.api.v1.product_facade import ProductFacadeService, get_product_facade
from app.api.v1.schemas import (
    PublicError,
    StrictSchema,
    SwarmCreateRequest,
    SwarmCreateResponse,
    SwarmExportRequest,
    SwarmGraphPatchRequest,
    SwarmMemberRequest,
    SwarmPinsRequest,
    SwarmRunRequest,
    SwarmValidateRequest,
)

router = APIRouter(prefix="/swarms", tags=["swarms"])


def _denied(
    correlation_id: str, message: str = "Protected resource access is not permitted."
) -> None:
    raise PublicApiException(
        status_code=status.HTTP_403_FORBIDDEN,
        error=PublicError(
            code="authorization_denied",
            message=message,
            correlation_id=correlation_id,
            retryable=False,
        ),
    )


def _conflict(correlation_id: str, message: str) -> None:
    raise PublicApiException(
        status_code=status.HTTP_409_CONFLICT,
        error=PublicError(
            code="conflict",
            message=message,
            correlation_id=correlation_id,
            retryable=False,
        ),
    )


def _swarm_payload(
    facade: ProductFacadeService, context: AuthenticatedRequestContext, swarm: Any
) -> dict[str, Any]:
    from app.api.v1.video_brief_spine import public_spine_view

    return {
        "id": swarm.swarm_id,
        "name": swarm.name,
        "revision": swarm.revision,
        "status": swarm.status,
        "pattern_ref": swarm.pattern_ref,
        "nodes": swarm.nodes,
        "edges": swarm.edges,
        "policy": swarm.policy,
        "members": swarm.members,
        "pins": swarm.pins,
        "last_run_id": swarm.last_run_id,
        "goal_summary": getattr(swarm, "goal_summary", None),
        "brief": getattr(swarm, "brief", None),
        "spine": public_spine_view(getattr(swarm, "spine", None)),
        "created_at": swarm.created_at.isoformat(),
        "updated_at": swarm.updated_at.isoformat(),
        "actions": facade.issue_swarm_actions(context.organization_id, swarm),
    }


@router.post("", response_model=SwarmCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_swarm(
    request: SwarmCreateRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> SwarmCreateResponse:
    """Create an organization-owned swarm draft."""
    action_id = request.action_reference_id
    if action_id is None:
        # Issue+consume a create_swarm action for convenience when composer has none yet.
        action_id = facade.issue_compose_action(context.organization_id)["id"]
    swarm = facade.create_swarm(
        organization_id=context.organization_id,
        actor_id=context.actor_id,
        correlation_id=context.correlation_id,
        name=request.name,
        action_reference_id=action_id,
        pattern_ref=request.pattern_ref,
        goal_summary=request.goal_summary,
        initial_graph=request.initial_graph,
    )
    if swarm is None:
        _denied(str(context.correlation_id), "Create swarm requires an eligible action reference.")
    assert swarm is not None
    return SwarmCreateResponse(
        swarm_id=swarm.swarm_id,
        revision=swarm.revision,
        status=swarm.status,
        name=swarm.name,
    )


@router.get("")
async def list_swarms(
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> dict[str, Any]:
    """List all organization-owned swarm drafts and runs (in-memory façade; lost on process restart)."""
    from datetime import UTC, datetime

    return {
        "items": facade.list_swarms(context.organization_id),
        "compose_action": facade.issue_compose_action(context.organization_id),
        "freshness": {"as_of": datetime.now(UTC).isoformat(), "state": "live"},
        "note": "Façade swarms are process-local. Restart clears drafts.",
    }


@router.get("/running")
async def list_running_swarms(
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> dict[str, Any]:
    """List swarms with queued/running façade status for dashboard fleet views."""
    from datetime import UTC, datetime

    return {
        "items": facade.list_running_swarms(context.organization_id),
        "compose_action": facade.issue_compose_action(context.organization_id),
        "freshness": {"as_of": datetime.now(UTC).isoformat(), "state": "live"},
    }


@router.get("/{swarm_id}")
async def read_swarm(
    swarm_id: str,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> dict[str, Any]:
    """Read swarm draft with graph and action references."""
    swarm = facade.get_swarm(context.organization_id, swarm_id)
    if swarm is None:
        _denied(str(context.correlation_id))
    assert swarm is not None
    return _swarm_payload(facade, context, swarm)


@router.patch("/{swarm_id}/graph")
async def patch_swarm_graph(
    swarm_id: str,
    request: SwarmGraphPatchRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> dict[str, Any]:
    """Append a graph revision with optimistic concurrency."""
    before = facade.get_swarm(context.organization_id, swarm_id)
    if before is None:
        _denied(str(context.correlation_id))
    assert before is not None
    if before.revision != request.expected_revision:
        _conflict(
            str(context.correlation_id),
            f"expected_revision {request.expected_revision} does not match current {before.revision}.",
        )
    swarm = facade.patch_graph(
        organization_id=context.organization_id,
        swarm_id=swarm_id,
        action_reference_id=request.action_reference_id,
        expected_revision=request.expected_revision,
        graph=request.graph,
    )
    if swarm is None:
        _denied(str(context.correlation_id), "Graph edit requires an eligible edit_graph action.")
    assert swarm is not None
    return {
        "swarm_id": swarm.swarm_id,
        "revision": swarm.revision,
        "validation": {"ok": True, "issues": []},
    }


@router.post("/{swarm_id}/validate")
async def validate_swarm(
    swarm_id: str,
    request: SwarmValidateRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> dict[str, Any]:
    """Validate graph provenance without executing a run."""
    result = facade.validate_swarm(context.organization_id, swarm_id, request.action_reference_id)
    if result is None:
        _denied(str(context.correlation_id), "Validate requires an eligible validate_swarm action.")
    assert result is not None
    return result


@router.post("/{swarm_id}/members")
async def add_swarm_member(
    swarm_id: str,
    request: SwarmMemberRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> dict[str, Any]:
    """Add a common agent to a swarm (Registry Add to Swarm)."""
    result = facade.add_member(
        organization_id=context.organization_id,
        swarm_id=swarm_id,
        action_reference_id=request.action_reference_id,
        agent_id=request.agent_id,
        agent_version=request.agent_version,
        pin_policy=request.pin_policy,
    )
    if result is None:
        _denied(
            str(context.correlation_id),
            "Add member requires eligible add_to_swarm action for agent or swarm.",
        )
    assert result is not None
    return result


@router.post("/{swarm_id}/pins")
async def pin_swarm_versions(
    swarm_id: str,
    request: SwarmPinsRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> dict[str, Any]:
    """Set version pins for swarm nodes."""
    result = facade.set_pins(
        organization_id=context.organization_id,
        swarm_id=swarm_id,
        action_reference_id=request.action_reference_id,
        pins=list(request.pins),
    )
    if result is None:
        _denied(str(context.correlation_id), "Pin requires an eligible pin_versions action.")
    assert result is not None
    return result


@router.post("/{swarm_id}/runs")
async def start_swarm_run(
    swarm_id: str,
    request: SwarmRunRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> dict[str, Any]:
    """Queue a façade run intent (engine dispatch remains a separate library path)."""
    result = facade.start_run(
        organization_id=context.organization_id,
        swarm_id=swarm_id,
        action_reference_id=request.action_reference_id,
        correlation_id=context.correlation_id,
    )
    if result is None:
        _denied(
            str(context.correlation_id),
            "Run requires an eligible run_swarm action and a non-empty graph.",
        )
    assert result is not None
    return result


@router.post("/{swarm_id}/exports")
async def export_swarm(
    swarm_id: str,
    request: SwarmExportRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> dict[str, Any]:
    """Create a redacted export job reference (no secrets)."""
    result = facade.export_swarm(
        context.organization_id,
        swarm_id,
        request.action_reference_id,
        request.format,
    )
    if result is None:
        _denied(str(context.correlation_id), "Export requires an eligible export_swarm action.")
    assert result is not None
    return result


class SpineStepRequest(StrictSchema):
    """Advance one video spine stub step (requires run_spine_step action)."""

    action_reference_id: str = Field(min_length=1, max_length=100)
    step_id: str | None = Field(default=None, max_length=64)
    idempotency_key: str | None = Field(default=None, max_length=100)


class PackageDecisionRequest(StrictSchema):
    """Human decision for package gate (always HITL on package)."""

    action_reference_id: str = Field(min_length=1, max_length=100)
    decision: str = Field(min_length=1, max_length=20)
    reason: str = Field(min_length=3, max_length=500)


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


@router.post("/{swarm_id}/spine/steps")
async def run_spine_step(
    swarm_id: str,
    request: SpineStepRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> dict[str, Any]:
    """Dry-run advance one spine stub step; package pauses for human approval."""
    result = facade.run_spine_step(
        organization_id=context.organization_id,
        swarm_id=swarm_id,
        action_reference_id=request.action_reference_id,
        correlation_id=context.correlation_id,
        step_id=request.step_id,
        idempotency_key=request.idempotency_key,
    )
    if result is None:
        _denied(
            str(context.correlation_id),
            "Spine step requires an eligible run_spine_step action and a known swarm.",
        )
    assert result is not None
    if result.get("ok") is False:
        _bad_request(str(context.correlation_id), str(result.get("message") or "Spine step failed."))
    return result


@router.post("/{swarm_id}/spine/package-decision")
async def decide_package(
    swarm_id: str,
    request: PackageDecisionRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> dict[str, Any]:
    """Approve or deny package gate; deny fails closed, no production media claim."""
    result = facade.decide_package_gate(
        organization_id=context.organization_id,
        swarm_id=swarm_id,
        action_reference_id=request.action_reference_id,
        correlation_id=context.correlation_id,
        decision=request.decision,
        reason=request.reason,
    )
    if result is None:
        _denied(
            str(context.correlation_id),
            "Package decision requires an eligible decide_package action.",
        )
    assert result is not None
    if result.get("ok") is False:
        _bad_request(
            str(context.correlation_id),
            str(result.get("message") or "Package decision failed."),
        )
    return result


@router.get("/{swarm_id}/artifacts/{artifact_ref}")
async def read_swarm_artifact(
    swarm_id: str,
    artifact_ref: str,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> dict[str, Any]:
    """Read a redacted stub artifact by opaque ref (not production media)."""
    art = facade.get_swarm_artifact(context.organization_id, swarm_id, artifact_ref)
    if art is None:
        _denied(
            str(context.correlation_id),
            "Artifact not found for this swarm (or spine not attached).",
        )
    assert art is not None
    return art


@router.get("/{swarm_id}/artifacts")
async def list_swarm_artifacts(
    swarm_id: str,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> dict[str, Any]:
    """List redacted spine artifact handoffs for a draft."""
    result = facade.list_swarm_artifacts(context.organization_id, swarm_id)
    if result is None:
        _denied(str(context.correlation_id))
    assert result is not None
    return result


class SpineToPackageRequest(StrictSchema):
    """Dry-run advance stub steps until package human gate."""

    action_reference_id: str = Field(min_length=1, max_length=100)
    max_steps: int = Field(default=12, ge=1, le=16)


@router.post("/{swarm_id}/spine/run-to-package")
async def run_spine_to_package(
    swarm_id: str,
    request: SpineToPackageRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> dict[str, Any]:
    """Advance stub spine until package waits for human (or terminal)."""
    result = facade.run_spine_to_package(
        organization_id=context.organization_id,
        swarm_id=swarm_id,
        action_reference_id=request.action_reference_id,
        correlation_id=context.correlation_id,
        max_steps=request.max_steps,
    )
    if result is None:
        _denied(
            str(context.correlation_id),
            "Dry-run requires eligible run_spine_to_package action and known swarm.",
        )
    assert result is not None
    if result.get("ok") is False:
        _bad_request(
            str(context.correlation_id),
            str(result.get("message") or "Spine dry-run failed."),
        )
    return result
