"""Authorized HTTP routes for the domain-neutral adoption control plane."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.v1.adoption_services import AdoptionServices, get_adoption_services
from app.api.v1.dependencies import AuthenticatedRequestContext, get_authenticated_request_context
from app.api.v1.errors import PublicApiException, public_error_from_detail, require_value
from app.api.v1.schemas import (
    AdoptionArtifactHandoffRequest,
    AdoptionArtifactHandoffResponse,
    AdoptionPackRegistrationRequest,
    AdoptionPackRegistrationResponse,
    CapacityActionRequest,
    CapacityActionResponse,
    CompatibilityEvidenceRequest,
    CompatibilityEvidenceResponse,
    DataAccessDecisionRequest,
    GovernanceDecisionRequest,
    GovernanceDecisionResponse,
    InvocationSubmissionRequest,
    InvocationSubmissionResponse,
    LearningActivationRequest,
    LearningEpisodeRequest,
    LearningEpisodeResponse,
    LearningObservabilityResponse,
    LifecycleChangeRequest,
    LifecycleResponse,
    MaturityStateRequest,
    MaturityStateResponse,
    OutboundDecisionRequest,
    ProviderDecisionRequest,
    ReleaseVerificationRequest,
    ReleaseVerificationResponse,
    RetrievalRecordRequest,
    RetrievalRecordResponse,
    VerificationCheckRequest,
    VideoReleaseEvidenceRequest,
    VideoReleaseEvidenceResponse,
)
from app.evaluation.verification_suite import VerificationCheck
from app.evidence.release_evidence import ReleasePolicy, VerificationLayer
from app.memory.learning_lifecycle import ActivationEvidence
from app.models.common import SCHEMA_VERSION, CompatibilityRange, RecordMetadata, utc_now
from app.models.contracts import (
    AgentLearningContract,
    ErrorCode,
    ErrorDetail,
    Result,
)
from app.models.control_plane import (
    AgentLifecycle,
    AgentLifecycleId,
    AgentLifecycleStatus,
    AgentNodeAttemptId,
    ArtifactAvailabilityStatus,
    ArtifactHandoff,
    ArtifactHandoffId,
    AuthorizationDecision as AuthorizationDecisionRecord,
    MaturityLevel,
    RetrievalRecordId,
    TaskId,
)
from app.models.evidence import LearningTerminalOutcome
from app.models.identifiers import (
    AgentId,
    CorrelationId,
    DomainId,
    DomainPackId,
    OrganizationId,
    RunId,
    new_record_id,
)
from app.models.runs import AgentNodeAttempt, AgentNodeAttemptStatus

router = APIRouter(prefix="/adoption", tags=["adoption"])


@router.post(
    "/packs",
    response_model=AdoptionPackRegistrationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_adoption_pack(
    request: AdoptionPackRegistrationRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    services: Annotated[
        AdoptionServices,
        Depends(get_adoption_services),
    ],
) -> AdoptionPackRegistrationResponse:
    """Register a declarative pack using the trusted actor as its signer."""
    registration = require_value(
        services.register_pack(
            request.manifest,
            context.organization_id,
            context.actor_id,
            context.correlation_id,
        )
    )
    return AdoptionPackRegistrationResponse(
        registration_id=str(registration.registration_id),
        pack_id=str(registration.pack_id),
        immutable_version=registration.immutable_version,
        decision=str(registration.decision),
        compatibility_status=str(registration.compatibility_status),
        validation_result=registration.validation_result,
        policy_passed=registration.policy_passed,
        content_digest=registration.content_digest,
        correlation_id=str(registration.metadata.correlation_id),
        reproduction_references=list(registration.reproduction_references),
    )


@router.post(
    "/invocations",
    response_model=InvocationSubmissionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def submit_adoption_invocation(
    request: InvocationSubmissionRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    services: Annotated[
        AdoptionServices,
        Depends(get_adoption_services),
    ],
) -> InvocationSubmissionResponse:
    """Persist the complete invocation association before any node can start."""
    association = require_value(
        services.submit_invocation(
            context.organization_id,
            context.correlation_id,
            invocation_id=request.invocation_id,
            domain_id=request.domain_id,
            pack_id=request.pack_id,
            pack_version=request.pack_version,
            agent_id=request.agent_id,
            workflow_id=request.workflow_id,
            run_id=request.run_id,
        )
    )
    return InvocationSubmissionResponse(
        invocation_id=str(association.invocation_id),
        organization_id=str(association.organization_id),
        domain_id=str(association.domain_id),
        pack_version=association.pack_version,
        agent_id=str(association.agent_id),
        workflow_id=association.workflow_id,
        run_id=str(association.run_id),
        correlation_id=str(association.correlation_id),
        persisted=True,
    )


@router.post("/governance/data", response_model=GovernanceDecisionResponse)
async def authorize_adoption_data(
    request: DataAccessDecisionRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    services: Annotated[
        AdoptionServices,
        Depends(get_adoption_services),
    ],
) -> GovernanceDecisionResponse:
    """Authorize a memory scope and preserve a denied decision as denied."""
    decision = require_value(
        services.authorize_data(
            context.organization_id,
            context.correlation_id,
            domain_id=request.domain_id,
            pack_version=request.pack_version,
            agent_id=request.agent_id,
            memory_scope=request.memory_scope,
        )
    )
    return _governance_response(decision, request.memory_scope)


@router.post("/governance/tools", response_model=GovernanceDecisionResponse)
async def authorize_adoption_tool(
    request: GovernanceDecisionRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    services: Annotated[
        AdoptionServices,
        Depends(get_adoption_services),
    ],
) -> GovernanceDecisionResponse:
    """Authorize a declared tool identifier without accepting client authority."""
    decision = require_value(
        services.authorize_tool(
            context.organization_id,
            context.correlation_id,
            domain_id=request.domain_id,
            pack_version=request.pack_version,
            agent_id=request.agent_id,
            tool_id=request.capability,
        )
    )
    return _governance_response(decision, request.capability)


@router.post("/governance/outbound", response_model=GovernanceDecisionResponse)
async def authorize_adoption_outbound(
    request: OutboundDecisionRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    services: Annotated[
        AdoptionServices,
        Depends(get_adoption_services),
    ],
) -> GovernanceDecisionResponse:
    """Authorize an outbound destination against the registered declaration."""
    decision = require_value(
        services.authorize_outbound(
            context.organization_id,
            context.correlation_id,
            domain_id=request.domain_id,
            pack_version=request.pack_version,
            agent_id=request.agent_id,
            destination=request.destination,
        )
    )
    return _governance_response(decision, request.destination)


@router.post("/governance/providers", response_model=GovernanceDecisionResponse)
async def authorize_adoption_provider(
    request: ProviderDecisionRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    services: Annotated[
        AdoptionServices,
        Depends(get_adoption_services),
    ],
) -> GovernanceDecisionResponse:
    """Authorize a provider only when the host has a complete declaration."""
    decision = require_value(
        services.authorize_provider(
            context.organization_id,
            context.correlation_id,
            domain_id=request.domain_id,
            pack_version=request.pack_version,
            agent_id=request.agent_id,
            provider_id=request.provider_id,
            capability=request.capability,
        )
    )
    return _governance_response(decision, request.capability, request.provider_id)


@router.post(
    "/handoffs/internal",
    response_model=AdoptionArtifactHandoffResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_internal_adoption_handoff(
    request: AdoptionArtifactHandoffRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    services: Annotated[
        AdoptionServices,
        Depends(get_adoption_services),
    ],
) -> AdoptionArtifactHandoffResponse:
    """Persist an internal handoff before exposing it downstream."""
    handoff = require_value(_handoff_from_request(request, context))
    persisted = require_value(
        services.artifact_handoffs.create_internal(
            context.organization_id,
            handoff,
            correlation_id=context.correlation_id,
        )
    )
    return _handoff_response(persisted, context.correlation_id)


@router.post(
    "/handoffs/external",
    response_model=AdoptionArtifactHandoffResponse,
    status_code=status.HTTP_201_CREATED,
)
async def submit_external_adoption_handoff(
    request: AdoptionArtifactHandoffRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    services: Annotated[
        AdoptionServices,
        Depends(get_adoption_services),
    ],
) -> AdoptionArtifactHandoffResponse:
    """Submit an external handoff through its metadata-confirmation barrier."""
    handoff = require_value(_handoff_from_request(request, context))
    persisted = require_value(
        services.artifact_handoffs.submit_external(
            context.organization_id,
            handoff,
            correlation_id=context.correlation_id,
        )
    )
    return _handoff_response(persisted, context.correlation_id)


@router.get("/handoffs/available", response_model=list[AdoptionArtifactHandoffResponse])
async def list_available_adoption_handoffs(
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    services: Annotated[
        AdoptionServices,
        Depends(get_adoption_services),
    ],
) -> list[AdoptionArtifactHandoffResponse]:
    """Expose only handoffs that crossed the complete metadata barrier."""
    handoffs = require_value(
        services.artifact_handoffs.available_for_downstream(
            context.organization_id, context.correlation_id
        )
    )
    return [_handoff_response(item, context.correlation_id) for item in handoffs]


@router.post("/lifecycle/activate", response_model=LifecycleResponse)
async def evaluate_adoption_activation(
    request: LearningActivationRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    services: Annotated[
        AdoptionServices,
        Depends(get_adoption_services),
    ],
) -> LifecycleResponse:
    """Evaluate every learning activation gate and expose blocked status explicitly."""
    lifecycle = require_value(_lifecycle_from_activation(request, context))
    candidates = require_value(_alc_candidates(request, context.correlation_id))
    try:
        evidence = ActivationEvidence.from_mapping(request.evidence)
    except ValueError as error:
        raise _public_validation_result(context.correlation_id, str(error)) from error
    result = require_value(
        services.learning_lifecycle.evaluate_activation(
            lifecycle,
            candidates,
            evidence,
            correlation_id=context.correlation_id,
        )
    )
    return _lifecycle_response(result, context.correlation_id)


@router.post("/lifecycle/suspend", response_model=LifecycleResponse)
async def suspend_adoption_lifecycle(
    request: LifecycleChangeRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    services: Annotated[
        AdoptionServices,
        Depends(get_adoption_services),
    ],
) -> LifecycleResponse:
    """Suspend an active learning agent before a lifecycle-affecting change."""
    lifecycle = require_value(_lifecycle_from_change(request, context))
    result = require_value(
        services.learning_lifecycle.suspend_for_change(
            lifecycle,
            request.change_references,
            correlation_id=context.correlation_id,
        )
    )
    return _lifecycle_response(result, context.correlation_id)


@router.post("/retrievals", response_model=RetrievalRecordResponse)
async def record_adoption_retrieval(
    request: RetrievalRecordRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    services: Annotated[
        AdoptionServices,
        Depends(get_adoption_services),
    ],
) -> RetrievalRecordResponse:
    """Persist retrieval evidence before a learning-required node action."""
    attempt = require_value(_attempt_from_retrieval(request, context))
    attempt = require_value(_ensure_attempt(services, attempt, context.correlation_id))
    record = require_value(
        services.learning_lifecycle.record_retrieval(
            attempt,
            request.memory_scope,
            request.lesson_references,
            approved_filters=request.approved_filters,
            correlation_id=context.correlation_id,
        )
    )
    return RetrievalRecordResponse(
        retrieval_record_id=str(record.retrieval_record_id),
        attempt_id=str(record.attempt_id),
        agent_id=str(record.agent_id),
        memory_scope=record.memory_scope,
        lesson_references=list(record.lesson_references),
        correlation_id=str(record.metadata.correlation_id),
    )


@router.post("/episodes", response_model=LearningEpisodeResponse)
async def record_adoption_episode(
    request: LearningEpisodeRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    services: Annotated[
        AdoptionServices,
        Depends(get_adoption_services),
    ],
) -> LearningEpisodeResponse:
    """Persist exactly one immutable terminal learning episode."""
    attempt = require_value(_attempt_from_episode(request, context))
    attempt = require_value(_ensure_attempt(services, attempt, context.correlation_id))
    retrieval_id = (
        None
        if request.retrieval_record_id is None
        else RetrievalRecordId(request.retrieval_record_id)
    )
    episode = require_value(
        services.learning_lifecycle.record_terminal_episode(
            attempt,
            request.terminal_outcome,
            request.outcome_reference,
            retrieval_record_id=retrieval_id,
            evidence_references=request.evidence_references,
            correlation_id=context.correlation_id,
        )
    )
    return LearningEpisodeResponse(
        episode_id=str(episode.episode_id),
        attempt_id=str(episode.attempt_id),
        terminal_outcome=str(episode.terminal_outcome),
        outcome_reference=episode.outcome_reference,
        retrieval_record_id=(
            str(episode.retrieval_record_id) if episode.retrieval_record_id is not None else None
        ),
        evidence_references=list(episode.evidence_references),
        correlation_id=str(episode.metadata.correlation_id),
    )


@router.get("/observability/{agent_id}", response_model=LearningObservabilityResponse)
async def read_adoption_observability(
    agent_id: str,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    services: Annotated[
        AdoptionServices,
        Depends(get_adoption_services),
    ],
) -> LearningObservabilityResponse:
    """Expose aggregate learning counts without Lesson content."""
    projection = require_value(
        services.lessons.observability(
            context.organization_id,
            AgentId(agent_id),
            correlation_id=context.correlation_id,
        )
    )
    return LearningObservabilityResponse(
        agent_id=str(projection.agent_id),
        learning_episode_count=projection.learning_episode_count,
        assessed_lesson_count=projection.assessed_lesson_count,
        retrieved_lesson_reuse_count=projection.retrieved_lesson_reuse_count,
        stale_lesson_count=projection.stale_lesson_count,
        revoked_lesson_count=projection.revoked_lesson_count,
        escalation_count=projection.escalation_count,
        assessment_outcomes=dict(projection.assessment_outcomes),
        correlation_id=str(projection.metadata.correlation_id),
    )


@router.post("/compatibility", response_model=CompatibilityEvidenceResponse)
async def record_adoption_compatibility(
    request: CompatibilityEvidenceRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    services: Annotated[
        AdoptionServices,
        Depends(get_adoption_services),
    ],
) -> CompatibilityEvidenceResponse:
    """Record intersection-based compatibility evidence before activation or invocation."""
    host_range = require_value(
        _compatibility_range(request.declared_host_range, context.correlation_id)
    )
    alc_range = require_value(
        _compatibility_range(request.declared_alc_range, context.correlation_id)
    )
    result = require_value(
        services.compatibility(
            context.organization_id,
            context.correlation_id,
            pack_id=request.pack_id,
            immutable_version=request.immutable_version,
            pack_contract_version=request.pack_contract_version,
            host_range=host_range,
            alc_range=alc_range,
            supported_host_version=request.supported_host_version,
            supported_alc_version=request.supported_alc_version,
        )
    )
    return CompatibilityEvidenceResponse(
        pack_id=request.pack_id,
        immutable_version=request.immutable_version,
        status=str(result.evaluation.status),
        declared_host_intersects=result.evaluation.declared_host_intersects,
        declared_alc_intersects=result.evaluation.declared_alc_intersects,
        failure_reasons=list(result.evaluation.failure_reasons),
        evidence_reference=str(getattr(result.evidence, "evidence_reference", "compatibility")),
        correlation_id=str(context.correlation_id),
    )


@router.post("/release/verify", response_model=ReleaseVerificationResponse)
async def verify_adoption_release(
    request: ReleaseVerificationRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    services: Annotated[
        AdoptionServices,
        Depends(get_adoption_services),
    ],
) -> ReleaseVerificationResponse:
    """Run layered release checks and preserve incomplete evidence as non-allowing state."""
    checks = [_verification_check(item) for item in request.checks]
    by_layer: dict[VerificationLayer, list[VerificationCheck]] = {
        VerificationLayer.SCHEMA: [],
        VerificationLayer.UNIT: [],
        VerificationLayer.PROPERTY: [],
        VerificationLayer.INTEGRATION: [],
    }
    for check in checks:
        by_layer[check.layer].append(check)
    try:
        policy = ReleasePolicy(allow_incomplete_coverage=request.allow_incomplete_coverage)
    except ValueError as error:
        raise _public_validation_result(context.correlation_id, str(error)) from error
    bundle = require_value(
        services.verification.run(
            context.organization_id,
            context.correlation_id,
            pack_id=DomainPackId(request.pack_id),
            immutable_version=request.immutable_version,
            pack_contract_version=request.pack_contract_version,
            host_contract_version=request.host_contract_version,
            alc_version=request.alc_version,
            workflow_id=request.workflow_id,
            fixed_seed=request.fixed_seed,
            fixture_digest=request.fixture_digest,
            schema_checks=by_layer[VerificationLayer.SCHEMA],
            unit_checks=by_layer[VerificationLayer.UNIT],
            property_checks=by_layer[VerificationLayer.PROPERTY],
            integration_checks=by_layer[VerificationLayer.INTEGRATION],
            release_policy=policy,
            release_gate_references=request.release_gate_references,
            integration_coverage_complete=request.integration_coverage_complete,
            initial_vertical=request.initial_vertical,
        )
    )
    decision = bundle.release_decision
    return ReleaseVerificationResponse(
        verification_run_id=str(bundle.verification_run.verification_run_id),
        coverage_status=str(bundle.coverage_status),
        check_count=len(bundle.check_results),
        passed_check_count=sum(result.passed for result in bundle.check_results),
        failure_count=len(bundle.failure_records),
        failure_persistence_errors=list(bundle.failure_persistence_errors),
        release_decision_status=(str(decision.status) if decision is not None else None),
        unmet_gate_references=(
            list(decision.unmet_gate_references) if decision is not None else []
        ),
        failure_evidence_references=(
            list(decision.failure_evidence_references) if decision is not None else []
        ),
        correlation_id=str(context.correlation_id),
    )


@router.post("/release/video", response_model=VideoReleaseEvidenceResponse)
async def evaluate_adoption_video_release(
    request: VideoReleaseEvidenceRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    services: Annotated[
        AdoptionServices,
        Depends(get_adoption_services),
    ],
) -> VideoReleaseEvidenceResponse:
    """Persist a blocked or eligible video readiness decision without releasing media."""
    handoff = require_value(_handoff_from_request(request.handoff, context))
    decision = require_value(
        services.operational_containment.evaluate_video_release(
            handoff,
            pack_id=DomainPackId(request.pack_id),
            immutable_version=request.immutable_version,
            workflow_id=request.workflow_id,
            gates=request.gates,
            evidence_references=request.evidence_references,
            organization_id=context.organization_id,
            correlation_id=context.correlation_id,
        )
    )
    return VideoReleaseEvidenceResponse(
        decision_id=str(decision.decision_id),
        status=str(decision.status),
        artifact_released=False,
        unmet_gate_references=list(decision.unmet_gate_references),
        evidence_references=list(decision.evidence_references),
        correlation_id=str(decision.metadata.correlation_id),
    )


@router.post("/maturity", response_model=MaturityStateResponse, status_code=status.HTTP_201_CREATED)
async def report_adoption_maturity(
    request: MaturityStateRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    services: Annotated[
        AdoptionServices,
        Depends(get_adoption_services),
    ],
) -> MaturityStateResponse:
    """Persist independent per-agent maturity evidence."""
    state = require_value(
        services.operational_containment.report_maturity(
            context.organization_id,
            DomainPackId(request.pack_id),
            request.immutable_version,
            AgentId(request.agent_id),
            MaturityLevel(request.level),
            request.evidence_references,
            correlation_id=context.correlation_id,
            pack_operational=request.pack_operational,
        )
    )
    return MaturityStateResponse(
        maturity_state_id=str(state.maturity_state_id),
        pack_id=str(state.pack_id),
        immutable_version=state.immutable_version,
        agent_id=str(state.agent_id),
        level=str(state.level),
        pack_operational=state.pack_operational,
        evidence_references=list(state.evidence_references),
        correlation_id=str(state.metadata.correlation_id),
    )


@router.post("/capacity", response_model=CapacityActionResponse)
async def apply_adoption_capacity_action(
    request: CapacityActionRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    services: Annotated[
        AdoptionServices,
        Depends(get_adoption_services),
    ],
) -> CapacityActionResponse:
    """Apply only the requested policy-selected throttle or disable action."""
    result = require_value(
        services.operational_containment.apply_capacity_action(
            context.organization_id,
            DomainPackId(request.pack_id),
            request.observed_load,
            request.approved_load_limit,
            request.action,
            immutable_version=request.immutable_version,
            correlation_id=context.correlation_id,
            actor_id=context.actor_id,
            reason=request.reason,
        )
    )
    return CapacityActionResponse(
        pack_id=str(result.pack_id),
        action=str(result.action),
        operational_status=str(result.operational_status),
        observed_load=result.observed_load,
        approved_load_limit=result.approved_load_limit,
        applied=result.applied,
        disabled=result.disabled,
        maturity_agent_count=len(result.maturity_states),
        audit_recorded=result.audit_recorded,
        reason=result.reason,
        correlation_id=str(result.correlation_id),
    )


def _governance_response(
    decision: AuthorizationDecisionRecord,
    capability: str,
    provider_id: str | None = None,
) -> GovernanceDecisionResponse:
    """Project an authorization record without turning a denial into permission."""
    return GovernanceDecisionResponse(
        decision_id=str(decision.decision_id),
        domain_id=str(decision.domain_id),
        pack_version=decision.pack_version,
        agent_id=str(decision.agent_id),
        capability=provider_id or capability,
        outcome="allowed" if decision.allowed else "denied",
        allowed=decision.allowed,
        reason_code=decision.reason,
        correlation_id=str(decision.metadata.correlation_id),
    )


def _handoff_response(
    handoff: ArtifactHandoff, correlation_id: CorrelationId
) -> AdoptionArtifactHandoffResponse:
    """Project only immutable handoff references and availability barriers."""
    return AdoptionArtifactHandoffResponse(
        handoff_id=str(handoff.handoff_id),
        artifact_identity=handoff.artifact_identity,
        artifact_version=handoff.artifact_version,
        parent_lineage=list(handoff.parent_lineage),
        source_run_reference=handoff.source_run_reference,
        availability=str(handoff.availability),
        external=handoff.external,
        metadata_persisted=handoff.metadata_persisted,
        correlation_id=str(handoff.metadata.correlation_id or correlation_id),
    )


def _lifecycle_response(
    lifecycle: AgentLifecycle, correlation_id: CorrelationId
) -> LifecycleResponse:
    """Project active and non-active lifecycle outcomes without implying activation."""
    return LifecycleResponse(
        lifecycle_id=str(lifecycle.lifecycle_id),
        pack_id=str(lifecycle.pack_id),
        immutable_version=lifecycle.immutable_version,
        agent_id=str(lifecycle.agent_id),
        status=str(lifecycle.status),
        learning_required=lifecycle.learning_required,
        effective_alc_version=lifecycle.effective_alc_version,
        activation_evidence_references=list(lifecycle.activation_evidence_references),
        change_references=list(lifecycle.change_references),
        correlation_id=str(lifecycle.metadata.correlation_id or correlation_id),
    )


def _handoff_from_request(
    request: AdoptionArtifactHandoffRequest,
    context: AuthenticatedRequestContext,
) -> Result[ArtifactHandoff, ErrorDetail]:
    """Build an opaque handoff using request references and trusted record metadata."""
    try:
        now = utc_now()
        handoff = ArtifactHandoff(
            metadata=_metadata(context.organization_id, context.correlation_id, now),
            handoff_id=ArtifactHandoffId(request.handoff_id),
            artifact_identity=request.artifact_identity,
            artifact_version=request.artifact_version,
            parent_lineage=tuple(request.parent_lineage),
            source_task_id=TaskId(request.source_task_id),
            source_run_reference=request.source_run_reference,
            brief_scope=request.brief_scope,
            technical_specification=request.technical_specification,
            rights_and_consent_state=request.rights_and_consent_state,
            continuity_state=request.continuity_state,
            quality_control_state=request.quality_control_state,
            target_channels=tuple(request.target_channels),
            provenance_reference=request.provenance_reference,
            owner_reference=request.owner_reference,
            classification=request.classification,
            integrity_reference=request.integrity_reference,
            approval_reference=request.approval_reference,
            availability=ArtifactAvailabilityStatus.PENDING,
            external=False,
            metadata_persisted=False,
        )
    except (TypeError, ValueError) as error:
        return Result.failure(_validation_error(context.correlation_id, str(error)))
    return Result.success(handoff)


def _lifecycle_from_activation(
    request: LearningActivationRequest,
    context: AuthenticatedRequestContext,
) -> Result[AgentLifecycle, ErrorDetail]:
    try:
        lifecycle = AgentLifecycle(
            metadata=_metadata(context.organization_id, context.correlation_id),
            lifecycle_id=AgentLifecycleId(request.lifecycle_id),
            pack_id=DomainPackId(request.pack_id),
            immutable_version=request.immutable_version,
            agent_id=AgentId(request.agent_id),
            status=AgentLifecycleStatus.CATALOGED,
            learning_required=request.learning_required,
            effective_alc_version=request.effective_alc_version,
        )
    except (TypeError, ValueError) as error:
        return Result.failure(_validation_error(context.correlation_id, str(error)))
    return Result.success(lifecycle)


def _lifecycle_from_change(
    request: LifecycleChangeRequest,
    context: AuthenticatedRequestContext,
) -> Result[AgentLifecycle, ErrorDetail]:
    try:
        lifecycle = AgentLifecycle(
            metadata=_metadata(context.organization_id, context.correlation_id),
            lifecycle_id=AgentLifecycleId(request.lifecycle_id),
            pack_id=DomainPackId(request.pack_id),
            immutable_version=request.immutable_version,
            agent_id=AgentId(request.agent_id),
            status=AgentLifecycleStatus(request.status),
            learning_required=request.learning_required,
            effective_alc_version=request.effective_alc_version,
            activation_evidence_references=tuple(request.activation_evidence_references),
            change_references=tuple(request.change_references),
        )
    except (TypeError, ValueError) as error:
        return Result.failure(_validation_error(context.correlation_id, str(error)))
    return Result.success(lifecycle)


def _alc_candidates(
    request: LearningActivationRequest, correlation_id: CorrelationId
) -> Result[tuple[AgentLearningContract, ...], ErrorDetail]:
    candidates: list[AgentLearningContract] = []
    try:
        for raw in request.alc_candidates:
            if not isinstance(raw, Mapping):
                raise ValueError("ALC candidates must be objects.")
            candidates.append(
                AgentLearningContract(
                    agent_id=AgentId(str(raw.get("agent_id", request.agent_id))),
                    version=_required_string(raw, "version"),
                    memory_scopes=_string_values(raw, "memory_scopes"),
                    retrieval_policy=_required_string(raw, "retrieval_policy"),
                    reflection_policy=_required_string(raw, "reflection_policy"),
                    evaluation_references=_string_values(raw, "evaluation_references"),
                    retention_policy=_required_string(raw, "retention_policy"),
                    human_promotion_policy=_required_string(raw, "human_promotion_policy"),
                    content_digest=(
                        str(raw["content_digest"])
                        if raw.get("content_digest") is not None
                        else None
                    ),
                )
            )
    except (TypeError, ValueError) as error:
        return Result.failure(_validation_error(correlation_id, str(error)))
    return Result.success(tuple(candidates))


def _attempt_from_retrieval(
    request: RetrievalRecordRequest,
    context: AuthenticatedRequestContext,
) -> Result[AgentNodeAttempt, ErrorDetail]:
    try:
        status_value = AgentNodeAttemptStatus(request.status)
        reference = request.terminal_outcome_reference
        if status_value in _terminal_attempt_statuses() and reference is None:
            reference = f"terminal:{request.attempt_id}"
        attempt = AgentNodeAttempt(
            metadata=_metadata(context.organization_id, context.correlation_id),
            attempt_id=AgentNodeAttemptId(request.attempt_id),
            run_id=RunId(request.run_id),
            node_id=request.node_id,
            organization_id=str(context.organization_id),
            domain_id=DomainId(request.domain_id),
            pack_id=DomainPackId(request.pack_id),
            pack_version=request.pack_version,
            agent_id=AgentId(request.agent_id),
            workflow_id=request.workflow_id,
            status=status_value,
            terminal_outcome_reference=reference,
        )
    except (TypeError, ValueError) as error:
        return Result.failure(_validation_error(context.correlation_id, str(error)))
    return Result.success(attempt)


def _attempt_from_episode(
    request: LearningEpisodeRequest,
    context: AuthenticatedRequestContext,
) -> Result[AgentNodeAttempt, ErrorDetail]:
    try:
        status_value = AgentNodeAttemptStatus(request.status)
        reference = request.outcome_reference
        attempt = AgentNodeAttempt(
            metadata=_metadata(context.organization_id, context.correlation_id),
            attempt_id=AgentNodeAttemptId(request.attempt_id),
            run_id=RunId(request.run_id),
            node_id=request.node_id,
            organization_id=str(context.organization_id),
            domain_id=DomainId(request.domain_id),
            pack_id=DomainPackId(request.pack_id),
            pack_version=request.pack_version,
            agent_id=AgentId(request.agent_id),
            workflow_id=request.workflow_id,
            status=status_value,
            terminal_outcome_reference=reference,
            retrieval_record_reference=request.retrieval_record_id,
        )
        LearningTerminalOutcome(request.terminal_outcome)
    except (TypeError, ValueError) as error:
        return Result.failure(_validation_error(context.correlation_id, str(error)))
    return Result.success(attempt)


def _ensure_attempt(
    services: AdoptionServices,
    attempt: AgentNodeAttempt,
    correlation_id: CorrelationId,
) -> Result[AgentNodeAttempt, ErrorDetail]:
    existing = services.repositories.attempts.get_by_attempt_id(
        OrganizationId(attempt.organization_id), attempt.attempt_id
    )
    if existing.is_success and existing.value is not None:
        return Result.success(existing.value)
    if existing.error is not None and existing.error.code is not ErrorCode.NOT_FOUND:
        return Result.failure(_correlation_error(existing.error, correlation_id))
    try:
        appended = services.repositories.attempts.append(attempt)
    except Exception:
        return Result.failure(
            ErrorDetail(
                ErrorCode.REPOSITORY_UNAVAILABLE,
                "Agent node attempt persistence is unavailable.",
                correlation_id,
                retryable=True,
            )
        )
    if appended.is_success and appended.value is not None:
        return Result.success(appended.value)
    retry = services.repositories.attempts.get_by_attempt_id(
        OrganizationId(attempt.organization_id), attempt.attempt_id
    )
    if retry.is_success and retry.value is not None:
        return Result.success(retry.value)
    return Result.failure(_correlation_error(appended.error, correlation_id))


def _compatibility_range(
    value: Mapping[str, object], correlation_id: CorrelationId
) -> Result[CompatibilityRange, ErrorDetail]:
    try:
        minimum = value.get("minimum", value.get("min_version"))
        maximum = value.get("maximum", value.get("max_version"))
        include_minimum = value.get("include_minimum", True)
        include_maximum = value.get("include_maximum", True)
        if minimum is not None and not isinstance(minimum, str):
            raise ValueError("Compatibility range minimum must be a semantic version.")
        if maximum is not None and not isinstance(maximum, str):
            raise ValueError("Compatibility range maximum must be a semantic version.")
        if not isinstance(include_minimum, bool) or not isinstance(include_maximum, bool):
            raise ValueError("Compatibility range inclusivity flags must be booleans.")
        return Result.success(
            CompatibilityRange(
                minimum=minimum,
                maximum=maximum,
                include_minimum=include_minimum,
                include_maximum=include_maximum,
            )
        )
    except (TypeError, ValueError) as error:
        return Result.failure(_validation_error(correlation_id, str(error)))


def _verification_check(request: VerificationCheckRequest) -> VerificationCheck:
    return VerificationCheck(
        name=request.name,
        layer=VerificationLayer(request.layer),
        outcome=request.passed,
        evidence_reference=request.evidence_reference,
    )


def _metadata(
    organization_id: object, correlation_id: CorrelationId, timestamp: datetime | None = None
) -> RecordMetadata:
    now = timestamp if timestamp is not None else utc_now()
    return RecordMetadata(
        record_id=new_record_id(),
        organization_id=OrganizationId(str(organization_id)),
        correlation_id=correlation_id,
        schema_version=SCHEMA_VERSION,
        version=1,
        created_at=now,
        updated_at=now,
    )


def _required_string(values: Mapping[str, object], name: str) -> str:
    value = values.get(name)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} is required.")
    return value


def _string_values(values: Mapping[str, object], name: str) -> tuple[str, ...]:
    raw = values.get(name)
    if not isinstance(raw, (list, tuple)):
        raise ValueError(f"{name} is required and must be an array.")
    result = tuple(item for item in raw if isinstance(item, str) and item.strip())
    if len(result) != len(raw) or not result:
        raise ValueError(f"{name} must contain non-empty strings.")
    return result


def _terminal_attempt_statuses() -> frozenset[AgentNodeAttemptStatus]:
    return frozenset(
        {
            AgentNodeAttemptStatus.COMPLETED,
            AgentNodeAttemptStatus.FAILED,
            AgentNodeAttemptStatus.BLOCKED,
            AgentNodeAttemptStatus.RETRIED,
            AgentNodeAttemptStatus.ESCALATED,
        }
    )


def _validation_error(correlation_id: CorrelationId, message: str) -> ErrorDetail:
    return ErrorDetail(ErrorCode.VALIDATION_FAILED, message, correlation_id)


def _correlation_error(error: ErrorDetail | None, correlation_id: CorrelationId) -> ErrorDetail:
    if error is None:
        return ErrorDetail(
            ErrorCode.REPOSITORY_UNAVAILABLE,
            "Adoption persistence is unavailable.",
            correlation_id,
            retryable=True,
        )
    return ErrorDetail(error.code, error.message, correlation_id, error.retryable, error.fields)


def _public_validation_result(correlation_id: CorrelationId, message: str) -> PublicApiException:
    return PublicApiException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        error=public_error_from_detail(_validation_error(correlation_id, message)),
    )
