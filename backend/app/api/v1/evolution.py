"""Versioned sandbox evolution and scoped-canary routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.v1.dependencies import AuthenticatedRequestContext, get_authenticated_request_context
from app.api.v1.errors import require_value
from app.api.v1.schemas import (
    CanaryApprovalRequest,
    CanaryCriterionRequest,
    CanaryOperationRequest,
    CanaryOperationResponse,
    CanaryResponse,
    MetricComparisonRequest,
    PromotionApprovalRequest,
    PromotionApprovalResponse,
    PromotionAssessmentRequest,
    PromotionAssessmentResponse,
    PromotionConditionResponse,
    RollbackPlanRequest,
    RollbackRecordResponse,
    SandboxVariantRequest,
    SandboxVariantResponse,
)
from app.api.v1.services import ControlPlaneServices, get_control_plane_services
from app.evolution.models import (
    CanaryId,
    CanaryRecord,
    CanaryScope,
    ImprovementDirection,
    MetricComparison,
    PromotionApprovalId,
    PromotionAssessment,
    RollbackRecord,
    RollbackRecordId,
    SandboxVariant,
    SandboxVariantId,
)
from app.models.identifiers import EvaluationRunId

router = APIRouter(tags=["evolution"])


@router.post(
    "/evolution/variants",
    response_model=SandboxVariantResponse,
    status_code=status.HTTP_201_CREATED,
)
async def propose_variant(
    request: SandboxVariantRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    services: Annotated[ControlPlaneServices, Depends(get_control_plane_services)],
) -> SandboxVariantResponse:
    """Create an immutable sandbox proposal with no production side effect."""
    variant = require_value(
        services.evolution_service.propose(
            context.organization_id,
            context.correlation_id,
            request.production_configuration,
            request.sandbox_configuration,
            request.target_metric,
            ImprovementDirection(request.improvement_direction),
        )
    )
    return _variant_response(variant)


@router.post("/evolution/variants/{variant_id}/consider", response_model=SandboxVariantResponse)
async def consider_variant(
    variant_id: str,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    services: Annotated[ControlPlaneServices, Depends(get_control_plane_services)],
) -> SandboxVariantResponse:
    """Mark a sandbox-only variant as a promotion candidate."""
    variant = require_value(
        services.evolution_service.consider(
            context.organization_id, context.correlation_id, SandboxVariantId(variant_id)
        )
    )
    return _variant_response(variant)


@router.post(
    "/evolution/variants/{variant_id}/rollback-plans",
    response_model=RollbackRecordResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_rollback_plan(
    variant_id: str,
    request: RollbackPlanRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    services: Annotated[ControlPlaneServices, Depends(get_control_plane_services)],
) -> RollbackRecordResponse:
    """Retain a plan that can be performed if a later canary fails."""
    record = require_value(
        services.evolution_service.create_rollback_plan(
            context.organization_id,
            context.correlation_id,
            SandboxVariantId(variant_id),
            request.rollback_plan,
        )
    )
    return _rollback_response(record)


@router.post(
    "/evolution/variants/{variant_id}/human-approvals",
    response_model=PromotionApprovalResponse,
    status_code=status.HTTP_201_CREATED,
)
async def record_human_approval(
    variant_id: str,
    request: PromotionApprovalRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    services: Annotated[ControlPlaneServices, Depends(get_control_plane_services)],
) -> PromotionApprovalResponse:
    """Record trusted actor approval before a promotion can be permitted."""
    approval = require_value(
        services.evolution_service.record_human_approval(
            context.organization_id,
            context.actor_id,
            context.correlation_id,
            SandboxVariantId(variant_id),
            request.reason,
        )
    )
    return PromotionApprovalResponse(
        approval_id=approval.approval_id,
        variant_id=approval.variant_id,
        actor_id=approval.actor_id,
        approved_at=approval.approved_at,
    )


@router.post(
    "/evolution/variants/{variant_id}/canaries",
    response_model=CanaryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def approve_canary(
    variant_id: str,
    request: CanaryApprovalRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    services: Annotated[ControlPlaneServices, Depends(get_control_plane_services)],
) -> CanaryResponse:
    """Retain a scoped approval without starting sandbox operation."""
    canary = require_value(
        services.evolution_service.approve_canary(
            context.organization_id,
            context.actor_id,
            context.correlation_id,
            SandboxVariantId(variant_id),
            CanaryScope(context.organization_id, request.scope.workflow_id, request.scope.case_id),
            request.criteria,
            RollbackRecordId(request.rollback_record_id),
        )
    )
    return _canary_response(canary)


@router.post("/evolution/canaries/{canary_id}/activate", response_model=CanaryResponse)
async def activate_canary(
    canary_id: str,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    services: Annotated[ControlPlaneServices, Depends(get_control_plane_services)],
) -> CanaryResponse:
    """Explicitly activate one already-approved canary."""
    canary = require_value(
        services.evolution_service.activate_canary(
            context.organization_id, context.correlation_id, CanaryId(canary_id)
        )
    )
    return _canary_response(canary)


@router.post("/evolution/canaries/{canary_id}/criteria", response_model=CanaryResponse)
async def record_canary_criterion(
    canary_id: str,
    request: CanaryCriterionRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    services: Annotated[ControlPlaneServices, Depends(get_control_plane_services)],
) -> CanaryResponse:
    """Retain canary evidence and perform the plan on the first failed criterion."""
    canary = require_value(
        services.evolution_service.record_canary_criterion(
            context.organization_id,
            context.correlation_id,
            CanaryId(canary_id),
            request.criterion,
            request.passed,
            request.evidence_reference,
        )
    )
    return _canary_response(canary)


@router.post(
    "/evolution/canaries/{canary_id}/operations/authorize",
    response_model=CanaryOperationResponse,
)
async def authorize_canary_operation(
    canary_id: str,
    request: CanaryOperationRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    services: Annotated[ControlPlaneServices, Depends(get_control_plane_services)],
) -> CanaryOperationResponse:
    """Authorize scope only; executing a variant operation remains outside this route."""
    require_value(
        services.evolution_service.authorize_canary_operation(
            context.organization_id,
            context.correlation_id,
            CanaryId(canary_id),
            CanaryScope(context.organization_id, request.scope.workflow_id, request.scope.case_id),
        )
    )
    return CanaryOperationResponse(canary_id=canary_id, permitted=True)


@router.post("/evolution/promotions/assess", response_model=PromotionAssessmentResponse)
async def assess_promotion(
    request: PromotionAssessmentRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    services: Annotated[ControlPlaneServices, Depends(get_control_plane_services)],
) -> PromotionAssessmentResponse:
    """Produce a fail-closed decision record; no proposal is applied by this API."""
    assessment = require_value(
        services.evolution_service.assess_promotion(
            context.organization_id,
            context.correlation_id,
            SandboxVariantId(request.requested_variant_id)
            if request.requested_variant_id is not None
            else None,
            EvaluationRunId(request.evaluation_run_id),
            _metric(request.target_metric),
            _metric(request.safety),
            _metric(request.compliance),
            RollbackRecordId(request.rollback_record_id),
            CanaryId(request.canary_id),
            request.audit_record_ids,
            request.evidence_references,
            PromotionApprovalId(request.approval_id),
        )
    )
    return _assessment_response(assessment)


def _variant_response(record: SandboxVariant) -> SandboxVariantResponse:
    return SandboxVariantResponse(
        variant_id=record.variant_id,
        state=record.state,
        target_metric=record.target_metric,
        improvement_direction=record.improvement_direction,
        production_baseline_digest=record.production_baseline_digest,
        sandbox_configuration_digest=record.sandbox_configuration_digest,
        created_at=record.metadata.created_at,
    )


def _rollback_response(record: RollbackRecord) -> RollbackRecordResponse:
    return RollbackRecordResponse(
        rollback_record_id=record.rollback_record_id,
        variant_id=record.variant_id,
        status=record.status,
        plan_digest=record.plan_digest,
        performed_at=record.performed_at,
    )


def _canary_response(record: CanaryRecord) -> CanaryResponse:
    return CanaryResponse(
        canary_id=record.canary_id,
        variant_id=record.variant_id,
        state=record.state,
        workflow_id=record.scope.workflow_id,
        case_id=record.scope.case_id,
        rollback_record_id=record.rollback_record_id,
        criteria=list(record.criteria),
        criterion_result_count=len(record.criterion_results),
        approved_at=record.approved_at,
    )


def _metric(request: MetricComparisonRequest) -> MetricComparison:
    return MetricComparison(request.baseline, request.candidate)


def _assessment_response(record: PromotionAssessment) -> PromotionAssessmentResponse:
    return PromotionAssessmentResponse(
        assessment_id=record.assessment_id,
        candidate_variant_id=record.candidate_variant_id,
        candidate_count=record.candidate_count,
        decision=record.decision,
        missing_or_failed_conditions=list(record.missing_or_failed_conditions),
        conditions=[
            PromotionConditionResponse(
                name=condition.name,
                passed=condition.passed,
                evidence_references=list(condition.evidence_references),
            )
            for condition in record.conditions
        ],
        production_applied=False,
        assessed_at=record.metadata.updated_at,
    )
