"""Product façade: activity feed, insights stubs, compose helpers."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query, status
from pydantic import Field

from app.api.v1.dependencies import AuthenticatedRequestContext, get_authenticated_request_context
from app.api.v1.errors import PublicApiException
from app.api.v1.product_facade import ProductFacadeService, get_product_facade
from app.api.v1.schemas import PublicError, StrictSchema
from app.api.v1.services import ControlPlaneServices, get_control_plane_services

router = APIRouter(tags=["product-ops"])


class PackageApprovalDecisionRequest(StrictSchema):
    """Decide a façade package gate (spine) without inventing control-plane authority."""

    action_reference_id: str = Field(min_length=1, max_length=100)
    decision: str = Field(min_length=1, max_length=20)
    reason: str = Field(min_length=3, max_length=500)


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


@router.get("/product-audit")
async def list_product_audit(
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
) -> dict[str, Any]:
    """Immutable product audit trail (spine steps, materialize, package decisions)."""
    items = facade.list_product_audit(context.organization_id, limit=limit)
    return {
        "items": items,
        "page": {"next_cursor": None, "limit": limit},
        "freshness": {"as_of": datetime.now(UTC).isoformat(), "state": "live"},
        "note": "Append-only audit; durable when CASOPS_PRODUCT_FACADE_PERSIST is enabled.",
        "correlation_id": str(context.correlation_id),
    }


@router.get("/package-approvals/{approval_id}")
async def read_package_approval(
    approval_id: str,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> dict[str, Any]:
    """Package gate detail for Operations / Approvals (façade spine HITL)."""
    detail = facade.get_package_approval(context.organization_id, approval_id)
    if detail is None:
        _denied(str(context.correlation_id), "Package approval not found for this organization.")
    assert detail is not None
    return detail


@router.post("/package-approvals/{approval_id}/decision")
async def decide_package_approval(
    approval_id: str,
    request: PackageApprovalDecisionRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> dict[str, Any]:
    """Approve/deny package gate via approval_id (action-gated, fail-closed)."""
    detail = facade.get_package_approval(
        context.organization_id, approval_id, issue_action=False
    )
    if detail is None:
        _denied(str(context.correlation_id), "Package approval not found for this organization.")
    assert detail is not None
    swarm_id = str(detail.get("swarm_id") or "")
    if not swarm_id:
        _bad_request(str(context.correlation_id), "Package approval has no swarm_id.")
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
