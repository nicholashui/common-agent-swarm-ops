"""Product façade: swarm drafts, graph revisions, members, runs, exports."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, status

from app.api.v1.dependencies import AuthenticatedRequestContext, get_authenticated_request_context
from app.api.v1.errors import PublicApiException
from app.api.v1.product_facade import ProductFacadeService, get_product_facade
from app.api.v1.schemas import (
    PublicError,
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


def _denied(correlation_id: str, message: str = "Protected resource access is not permitted.") -> None:
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


def _swarm_payload(facade: ProductFacadeService, context: AuthenticatedRequestContext, swarm: Any) -> dict[str, Any]:
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
    result = facade.validate_swarm(
        context.organization_id, swarm_id, request.action_reference_id
    )
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
        _denied(str(context.correlation_id), "Run requires an eligible run_swarm action and a non-empty graph.")
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
