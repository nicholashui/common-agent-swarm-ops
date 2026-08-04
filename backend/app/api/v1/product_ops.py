"""Product façade: activity feed, insights stubs, compose helpers."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query

from app.api.v1.dependencies import AuthenticatedRequestContext, get_authenticated_request_context
from app.api.v1.product_facade import ProductFacadeService, get_product_facade
from app.api.v1.services import ControlPlaneServices, get_control_plane_services

router = APIRouter(tags=["product-ops"])


@router.get("/activity")
async def list_activity(
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
    cursor: Annotated[str | None, Query(max_length=50)] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> dict[str, Any]:
    """Organization activity feed for the Activity screen."""
    return facade.list_activity(context.organization_id, cursor=cursor, limit=limit)


@router.get("/activity/insights")
async def activity_insights(
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> dict[str, Any]:
    """KPI summary for current org activity (façade)."""
    feed = facade.list_activity(context.organization_id, limit=100)
    return {
        "event_count": len(feed["items"]),
        "categories": sorted({item["category"] for item in feed["items"]}),
        "freshness": feed["freshness"],
        "compose_action": facade.issue_compose_action(context.organization_id),
    }


@router.get("/insights/common-impact")
async def common_impact(
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> dict[str, Any]:
    """Placeholder common-version impact projection."""
    health = facade.commons_health()
    return {
        "total_agents": health["total_agents"],
        "impact": [],
        "note": "Aggregate impact requires run projections; façade returns structure only.",
        "freshness": {"as_of": health["as_of"], "state": "cached"},
        "correlation_id": str(context.correlation_id),
    }


@router.get("/approvals")
async def list_approvals_inbox(
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    services: Annotated[ControlPlaneServices, Depends(get_control_plane_services)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> dict[str, Any]:
    """Approvals inbox: Host-held pending ops + façade package gates (spine)."""
    items: list[dict[str, Any]] = []
    for approval_id in services.list_pending_approval_ids(context.organization_id):
        gate = services.get_approval(context.organization_id, approval_id, context.correlation_id)
        if gate.is_success and gate.value is not None:
            g = gate.value
            items.append(
                {
                    "approval_id": str(g.approval_id),
                    "run_id": str(g.run_id),
                    "risk_tier": g.risk_tier,
                    "gate_status": g.status,
                    "created_at": g.metadata.created_at.isoformat()
                    if hasattr(g.metadata.created_at, "isoformat")
                    else str(g.metadata.created_at),
                    "source": "control_plane",
                }
            )
        else:
            items.append(
                {
                    "approval_id": str(approval_id),
                    "gate_status": "pending",
                    "note": "Pending operation registered; load detail for preview.",
                    "source": "control_plane",
                }
            )
    for pkg in facade.list_package_approvals(context.organization_id):
        items.append(
            {
                "approval_id": pkg.get("approval_id"),
                "run_id": pkg.get("run_id"),
                "risk_tier": pkg.get("risk_tier"),
                "gate_status": pkg.get("gate_status"),
                "created_at": pkg.get("created_at"),
                "swarm_id": pkg.get("swarm_id"),
                "summary": pkg.get("summary"),
                "kind": pkg.get("kind", "video_package"),
                "source": "video_spine_package",
                "note": "stub package gate · not production media",
            }
        )
    return {
        "items": items,
        "page": {"next_cursor": None, "limit": 50},
        "freshness": {
            "as_of": datetime.now(UTC).isoformat(),
            "state": "live",
        },
        "correlation_id": str(context.correlation_id),
    }
