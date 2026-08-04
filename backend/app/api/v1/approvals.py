"""Versioned approval-decision route with Host-derived actor and authority."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.v1.dependencies import AuthenticatedRequestContext, get_authenticated_request_context
from app.api.v1.errors import PublicApiException, require_value
from app.api.v1.product_facade import ProductFacadeService, get_product_facade
from app.api.v1.schemas import (
    ActionPreviewResponse,
    ApprovalDecisionRequest,
    ApprovalDecisionResponse,
    ApprovalGateResponse,
    PublicError,
)
from app.api.v1.services import ControlPlaneServices, get_control_plane_services
from app.governance.approvals import ActionPreview, ApprovalGate, ApprovalSubmissionOutcome
from app.models.identifiers import ApprovalId
from fastapi import status

router = APIRouter(tags=["approvals"])


@router.get("/approvals/{approval_id}", response_model=ApprovalGateResponse)
async def read_approval_gate(
    approval_id: str,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    services: Annotated[ControlPlaneServices, Depends(get_control_plane_services)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> ApprovalGateResponse:
    """Show the redacted action preview; falls back to video package façade gates."""
    result = services.get_approval(
        context.organization_id,
        ApprovalId(approval_id),
        context.correlation_id,
    )
    if result.is_success and result.value is not None:
        return _gate_response(result.value)

    pkg = facade.get_package_approval(
        context.organization_id, approval_id, issue_action=True
    )
    if pkg is not None:
        return _package_gate_response(pkg)

    # Preserve fail-closed denial messaging for unknown ids
    return _gate_response(require_value(result))


@router.post("/approvals/{approval_id}/decision", response_model=ApprovalDecisionResponse)
async def submit_approval_decision(
    approval_id: str,
    request: ApprovalDecisionRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    services: Annotated[ControlPlaneServices, Depends(get_control_plane_services)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> ApprovalDecisionResponse:
    """Retain a decision; package façade gates accept approved/denied without action body."""
    # Prefer control-plane pending ops when present
    pending_ids = {
        str(aid) for aid in services.list_pending_approval_ids(context.organization_id)
    }
    if approval_id in pending_ids or services.get_approval(
        context.organization_id, ApprovalId(approval_id), context.correlation_id
    ).is_success:
        outcome = require_value(
            services.submit_approval(
                context.organization_id,
                context.actor_id,
                ApprovalId(approval_id),
                request.selected_value,
                request.reason,
                context.correlation_id,
            )
        )
        assert isinstance(outcome, ApprovalSubmissionOutcome)
        decision = outcome.decision
        return ApprovalDecisionResponse(
            approval_id=decision.approval_id,
            run_id=outcome.gate.run_id,
            actor_id=decision.actor_id,
            selected_value=decision.selected_value,
            reason_is_valid=decision.reason_is_valid,
            value_is_valid=decision.value_is_valid,
            resumed=outcome.resumed,
            gate_status=outcome.gate.status,
            submitted_at=decision.submitted_at,
            action_preview=_preview_response(outcome.gate.action_preview, decision.submitted_at),
        )

    # Video spine package gate (process-local façade)
    value = request.selected_value.strip().lower()
    if value in {"approve", "approved"}:
        decision_value = "approved"
    elif value in {"deny", "denied"}:
        decision_value = "denied"
    else:
        raise PublicApiException(
            status_code=status.HTTP_400_BAD_REQUEST,
            error=PublicError(
                code="validation_failed",
                message="Package decision must be approved or denied.",
                correlation_id=str(context.correlation_id),
                retryable=False,
            ),
        )
    reason = (request.reason or "").strip() or (
        "Operator decision on stub package gate"
        if decision_value == "approved"
        else "Operator denied stub package gate"
    )
    if len(reason) < 3:
        reason = f"{reason} · host"

    pkg_result = facade.decide_package_gate_host_issued(
        organization_id=context.organization_id,
        approval_id=approval_id,
        correlation_id=context.correlation_id,
        decision=decision_value,
        reason=reason[:500],
    )
    if pkg_result is None:
        raise PublicApiException(
            status_code=status.HTTP_403_FORBIDDEN,
            error=PublicError(
                code="authorization_denied",
                message="Protected resource access is not permitted.",
                correlation_id=str(context.correlation_id),
                retryable=False,
            ),
        )
    if pkg_result.get("ok") is False:
        raise PublicApiException(
            status_code=status.HTTP_400_BAD_REQUEST,
            error=PublicError(
                code="validation_failed",
                message=str(pkg_result.get("message") or "Package decision failed."),
                correlation_id=str(context.correlation_id),
                retryable=False,
            ),
        )

    now = datetime.now(UTC)
    spine = pkg_result.get("spine") if isinstance(pkg_result.get("spine"), dict) else {}
    resumed = decision_value == "approved" and str(spine.get("status")) == "completed"
    preview = ActionPreviewResponse(
        action_id=f"package:{approval_id}",
        summary="Video spine package gate (stub · not production media)",
        intended_effect=(
            "Complete stub package after human approval"
            if decision_value == "approved"
            else "Fail closed; package denied"
        ),
        emitted_at=now,
        supporting_evidence=["video_spine_package", "stub run · not production media"],
        uncertainty="Dry-run stub only",
        correction_control="Deny fails closed; rematerialize or re-run spine after changes",
    )
    return ApprovalDecisionResponse(
        approval_id=approval_id,
        run_id=str(spine.get("brief_id") or f"spine:{pkg_result.get('swarm_id')}"),
        actor_id=str(context.actor_id),
        selected_value=decision_value,
        reason_is_valid=True,
        value_is_valid=True,
        resumed=resumed,
        gate_status="resumed" if resumed else "denied",
        submitted_at=now,
        action_preview=preview,
    )


def _gate_response(gate: ApprovalGate) -> ApprovalGateResponse:
    """Project only the operator-safe gate preview and metadata."""
    return ApprovalGateResponse(
        approval_id=gate.approval_id,
        run_id=gate.run_id,
        risk_tier=gate.risk_tier,
        gate_status=gate.status,
        created_at=gate.metadata.created_at,
        action_preview=_preview_response(gate.action_preview, gate.metadata.created_at),
    )


def _package_gate_response(pkg: dict) -> ApprovalGateResponse:
    """Map façade package gate into the standard approval preview shape."""
    created_raw = pkg.get("created_at")
    if isinstance(created_raw, datetime):
        created_at = created_raw
    elif isinstance(created_raw, str) and created_raw:
        try:
            created_at = datetime.fromisoformat(created_raw.replace("Z", "+00:00"))
        except ValueError:
            created_at = datetime.now(UTC)
    else:
        created_at = datetime.now(UTC)
    actions = pkg.get("actions") if isinstance(pkg.get("actions"), list) else []
    action_id = "package_pending"
    if actions and isinstance(actions[0], dict) and actions[0].get("id"):
        action_id = str(actions[0]["id"])
    gate_status = str(pkg.get("gate_status") or "paused")
    # Normalize to values clients already understand
    if gate_status == "paused":
        status_out = "paused"
    elif gate_status in {"resumed", "completed"}:
        status_out = "resumed"
    else:
        status_out = gate_status
    return ApprovalGateResponse(
        approval_id=str(pkg.get("approval_id") or ""),
        run_id=str(pkg.get("run_id") or f"spine:{pkg.get('swarm_id')}"),
        risk_tier=str(pkg.get("risk_tier") or "tier_3_package_gate"),
        gate_status=status_out,
        created_at=created_at,
        action_preview=ActionPreviewResponse(
            action_id=action_id,
            summary=str(
                pkg.get("summary")
                or "Package gate for video spine (stub · not production media)"
            ),
            intended_effect=(
                "Human approve/deny stub package; deny fails closed; "
                "never claims production media quality"
            ),
            emitted_at=created_at,
            rollback_preview="Discard stub package; rematerialize draft if needed",
            supporting_evidence=[
                "video_spine_package",
                "stub run · not production media",
                f"swarm:{pkg.get('swarm_id')}",
            ],
            uncertainty="Process-local façade gate until Host persists approvals",
            correction_control="POST /approvals/{id}/decision with approved|denied",
        ),
    )


def _preview_response(preview: ActionPreview, emitted_at: datetime) -> ActionPreviewResponse:
    return ActionPreviewResponse(
        action_id=preview.action_id,
        summary=preview.summary,
        intended_effect=preview.intended_effect,
        emitted_at=emitted_at,
        rollback_preview=preview.rollback_preview,
        supporting_evidence=list(preview.supporting_evidence),
        confidence=preview.confidence,
        uncertainty=preview.uncertainty,
        correction_control=preview.correction_control,
    )
