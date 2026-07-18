"""Versioned approval-decision route with Host-derived actor and authority."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.v1.dependencies import AuthenticatedRequestContext, get_authenticated_request_context
from app.api.v1.errors import require_value
from app.api.v1.schemas import (
    ActionPreviewResponse,
    ApprovalDecisionRequest,
    ApprovalDecisionResponse,
    ApprovalGateResponse,
)
from app.api.v1.services import ControlPlaneServices, get_control_plane_services
from app.governance.approvals import ActionPreview, ApprovalGate, ApprovalSubmissionOutcome
from app.models.identifiers import ApprovalId

router = APIRouter(tags=["approvals"])


@router.get("/approvals/{approval_id}", response_model=ApprovalGateResponse)
async def read_approval_gate(
    approval_id: str,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    services: Annotated[ControlPlaneServices, Depends(get_control_plane_services)],
) -> ApprovalGateResponse:
    """Show the redacted action preview and evidence before a decision can resume an effect."""
    gate = require_value(
        services.get_approval(
            context.organization_id,
            ApprovalId(approval_id),
            context.correlation_id,
        )
    )
    return _gate_response(gate)


@router.post("/approvals/{approval_id}/decision", response_model=ApprovalDecisionResponse)
async def submit_approval_decision(
    approval_id: str,
    request: ApprovalDecisionRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    services: Annotated[ControlPlaneServices, Depends(get_control_plane_services)],
) -> ApprovalDecisionResponse:
    """Retain a decision and resume only using server-held pending operation authority."""
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
