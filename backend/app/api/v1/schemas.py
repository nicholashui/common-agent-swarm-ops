"""Typed, redaction-safe request and response schemas for the v1 control plane."""

from __future__ import annotations

from datetime import datetime
from typing import Literal, TypeVar

from pydantic import BaseModel, ConfigDict, Field


class StrictSchema(BaseModel):
    """Reject undeclared client fields, including identity override attempts."""

    model_config = ConfigDict(extra="forbid")


class ValidationIssueResponse(StrictSchema):
    """A stable validation issue that does not expose untrusted payload values."""

    field: str
    reason: str


ResponseData = TypeVar("ResponseData")


class PublicResponseMeta(StrictSchema):
    """Metadata included with every public success response that has a body."""

    correlation_id: str


class PublicResponse[ResponseData](StrictSchema):
    """The stable envelope for a successful public API response."""

    data: ResponseData
    meta: PublicResponseMeta


class PublicError(StrictSchema):
    """A redaction-safe typed error returned by the public API."""

    code: str
    message: str
    correlation_id: str
    retryable: bool = False
    fields: list[ValidationIssueResponse] = Field(default_factory=list)


class PublicErrorResponse(StrictSchema):
    """The stable envelope for a failed public API response."""

    error: PublicError


class AuthenticatedContextResponse(StrictSchema):
    """The identity fields established by trusted Host authentication."""

    organization_id: str
    actor_id: str
    correlation_id: str


class ActionPreviewResponse(StrictSchema):
    """A redaction-safe preview emitted before a requested executable action."""

    action_id: str
    summary: str
    intended_effect: str
    emitted_at: datetime
    rollback_preview: str | None = None
    supporting_evidence: list[str] = Field(default_factory=list)
    confidence: float | None = None
    uncertainty: str | None = None
    correction_control: str | None = None


class DefinitionRequest(StrictSchema):
    """A data-only portable workflow definition."""

    definition: dict[str, object]


class DefinitionResponse(StrictSchema):
    """The identity and validation state of one registered definition version."""

    workflow_id: str
    version: str
    engine: str
    registered_at: datetime


class DomainRegistrationRequest(StrictSchema):
    """An inline domain-pack manifest; filesystem paths are intentionally unsupported."""

    manifest: dict[str, object]


class PackAgentResponse(StrictSchema):
    """A non-active agent outcome from domain-pack registration."""

    agent_id: str | None
    status: str | None
    production_active: Literal[False] = False
    production_activation_denied: bool


class DomainRegistrationResponse(StrictSchema):
    """A typed registration outcome with only safe validation details."""

    pack_id: str | None
    status: str
    registered_at: datetime
    agents: list[PackAgentResponse]
    validation_issues: list[ValidationIssueResponse]


class RunCreateRequest(StrictSchema):
    """Select a stored definition version; tenant and actor are never client fields."""

    version: str = Field(min_length=1, max_length=100)


class RunResponse(StrictSchema):
    """A redacted durable run projection."""

    run_id: str
    workflow_id: str
    workflow_version: str
    status: str
    engine: str
    correlation_id: str
    updated_at: datetime
    output: dict[str, object] | None = None
    failure_code: str | None = None
    action_preview: ActionPreviewResponse | None = None


class DispatchRequest(StrictSchema):
    """A two-step dispatch request that requires preview acknowledgement before start."""

    run_id: str = Field(min_length=1, max_length=100)
    idempotency_key: str = Field(min_length=1, max_length=200)
    confirm: bool = False


class DispatchResponse(StrictSchema):
    """Either a no-effect preview or a confirmed dispatch result."""

    run_id: str
    status: str
    executed: bool
    preview: ActionPreviewResponse
    idempotent: bool = False
    retry_permitted: bool = False


class ApprovalGateResponse(StrictSchema):
    """A redacted, tenant-scoped approval gate previewed before a decision."""

    approval_id: str
    run_id: str
    risk_tier: str
    gate_status: str
    created_at: datetime
    action_preview: ActionPreviewResponse


class ApprovalDecisionRequest(StrictSchema):
    """A human decision without client-controlled actor or authorization context."""

    selected_value: str = Field(min_length=1, max_length=100)
    reason: str = Field(max_length=2_000)


class ApprovalDecisionResponse(StrictSchema):
    """A retained decision projection that omits the potentially sensitive raw reason."""

    approval_id: str
    run_id: str
    actor_id: str
    selected_value: str
    reason_is_valid: bool
    value_is_valid: bool
    resumed: bool
    gate_status: str
    submitted_at: datetime
    action_preview: ActionPreviewResponse


class TopologyNodeResponse(StrictSchema):
    """One redaction-safe graph or linear-workflow node."""

    node_id: str
    agent_id: str
    tool_ids: list[str]


class TopologyEdgeResponse(StrictSchema):
    """One bounded topology edge."""

    source: str
    target: str
    max_traversals: int


class TopologyResponse(StrictSchema):
    """A versioned workflow topology projection."""

    workflow_id: str
    version: str
    engine: str
    pattern: str
    nodes: list[TopologyNodeResponse]
    edges: list[TopologyEdgeResponse]


class ToolEffectResponse(StrictSchema):
    """A durable effect summary that excludes raw request and adapter payloads."""

    adapter_id: str
    outcome: str
    effect_digest: str
    completed_at: datetime
    reversible: bool
    compensation_reference: str | None = None


class GraphStateResponse(StrictSchema):
    """An organization-filtered, redacted observable workflow state projection."""

    run_id: str
    status: str
    engine: str
    graph_id: str | None = None
    graph_thread_id: str | None = None
    updated_at: datetime
    failure_code: str | None = None
    tool_effects: list[ToolEffectResponse]
    action_previews: list[ActionPreviewResponse]


class OperatorEventResponse(StrictSchema):
    """A timestamped redaction-safe observation event."""

    kind: str
    recorded_at: datetime
    detail: str | None = None
    action_preview: ActionPreviewResponse | None = None


class EvaluationRunRequest(StrictSchema):
    """Configuration for one deterministic local evaluation execution."""

    configuration: dict[str, object]


class EvaluationRunResponse(StrictSchema):
    """A retained evaluation execution summary."""

    evaluation_run_id: str
    completed: bool
    transition_permitted: bool
    configuration_digest: str
    result_count: int
    completed_at: datetime


class SandboxVariantRequest(StrictSchema):
    """A detached sandbox proposal; neither mapping is applied to production."""

    production_configuration: dict[str, object]
    sandbox_configuration: dict[str, object]
    target_metric: str = Field(min_length=1, max_length=200)
    improvement_direction: Literal["increase", "decrease"]


class SandboxVariantResponse(StrictSchema):
    """A redaction-safe immutable sandbox proposal projection."""

    variant_id: str
    state: str
    target_metric: str
    improvement_direction: str
    production_baseline_digest: str
    sandbox_configuration_digest: str
    created_at: datetime


class RollbackPlanRequest(StrictSchema):
    """A declarative plan retained before canary activity."""

    rollback_plan: dict[str, object]


class RollbackRecordResponse(StrictSchema):
    """Rollback record projection without plan contents."""

    rollback_record_id: str
    variant_id: str
    status: str
    plan_digest: str
    performed_at: datetime | None = None


class PromotionApprovalRequest(StrictSchema):
    """A human promotion approval using an actor derived from request context."""

    reason: str = Field(min_length=1, max_length=1_000)


class PromotionApprovalResponse(StrictSchema):
    """The retained trusted-actor approval identity."""

    approval_id: str
    variant_id: str
    actor_id: str
    approved_at: datetime


class CanaryScopeRequest(StrictSchema):
    """Narrow scope required for an approved canary."""

    workflow_id: str | None = Field(default=None, min_length=1, max_length=200)
    case_id: str | None = Field(default=None, min_length=1, max_length=200)


class CanaryApprovalRequest(StrictSchema):
    """Approval data for an inert canary that awaits activation."""

    scope: CanaryScopeRequest
    criteria: list[str] = Field(min_length=1, max_length=50)
    rollback_record_id: str = Field(min_length=1, max_length=100)


class CanaryCriterionRequest(StrictSchema):
    """One observed canary criterion result."""

    criterion: str = Field(min_length=1, max_length=200)
    passed: bool
    evidence_reference: str = Field(min_length=1, max_length=500)


class CanaryOperationRequest(StrictSchema):
    """A no-effect scope authorization request for an active canary."""

    scope: CanaryScopeRequest


class CanaryResponse(StrictSchema):
    """Canary lifecycle state and redaction-safe evidence counts."""

    canary_id: str
    variant_id: str
    state: str
    workflow_id: str | None
    case_id: str | None
    rollback_record_id: str
    criteria: list[str]
    criterion_result_count: int
    approved_at: datetime


class CanaryOperationResponse(StrictSchema):
    """An authorization-only response; it does not execute a variant operation."""

    canary_id: str
    permitted: bool


class MetricComparisonRequest(StrictSchema):
    """Observed baseline and candidate values for a favorable metric."""

    baseline: float
    candidate: float


class PromotionAssessmentRequest(StrictSchema):
    """All retained evidence references required for a fail-closed assessment."""

    requested_variant_id: str | None = Field(default=None, min_length=1, max_length=100)
    evaluation_run_id: str = Field(min_length=1, max_length=100)
    target_metric: MetricComparisonRequest
    safety: MetricComparisonRequest
    compliance: MetricComparisonRequest
    rollback_record_id: str = Field(min_length=1, max_length=100)
    canary_id: str = Field(min_length=1, max_length=100)
    audit_record_ids: list[str] = Field(default_factory=list, max_length=100)
    evidence_references: list[str] = Field(default_factory=list, max_length=100)
    approval_id: str = Field(min_length=1, max_length=100)


class PromotionConditionResponse(StrictSchema):
    """One retained pass/fail promotion condition."""

    name: str
    passed: bool
    evidence_references: list[str]


class PromotionAssessmentResponse(StrictSchema):
    """A fail-closed decision that explicitly reports production remained unchanged."""

    assessment_id: str
    candidate_variant_id: str | None
    candidate_count: int
    decision: str
    missing_or_failed_conditions: list[str]
    conditions: list[PromotionConditionResponse]
    production_applied: Literal[False] = False
    assessed_at: datetime


class MemoryRetrievalRequest(StrictSchema):
    """A scoped knowledge request; identities and approved scopes come from the Host."""

    query: str = Field(min_length=1, max_length=2048, pattern=r".*\S.*")
    requires_relationships: bool = False


class MemoryProvenanceResponse(StrictSchema):
    """One safe reference supporting a returned memory result."""

    evidence_id: str
    digest: str
    kind: str


class MemoryRetrievalResultResponse(StrictSchema):
    """A provenance-bearing memory result from one permitted retrieval tier."""

    tier: Literal["tier-0-semantic", "tier-1-relationship", "tier-2-synthesis"]
    content_reference: str
    source_record_ids: list[str]
    provenance: list[MemoryProvenanceResponse]
    confidence: float = Field(ge=0, le=1)


class MemoryRetrievalResponse(StrictSchema):
    """A redaction-safe scoped knowledge projection for an authenticated requester."""

    results: list[MemoryRetrievalResultResponse]
    no_knowledge: bool
    searched_tiers: list[Literal["tier-0-semantic", "tier-1-relationship", "tier-2-synthesis"]]
    correlation_id: str
    retrieved_at: datetime
    uncertainty: str | None = None
    correction_control: str


class VideoNamedCheckRequest(StrictSchema):
    """One named immutable quality or release-gate result supplied at artifact handoff."""

    name: str = Field(min_length=1, max_length=200, pattern=r".*\S.*")
    passed: bool
    evidence_reference: str = Field(min_length=1, max_length=500, pattern=r".*\S.*")


class VideoArtifactHandoffRequest(StrictSchema):
    """Data for a copy-on-write video artifact version; no source media is accepted."""

    artifact_id: str = Field(min_length=1, max_length=200, pattern=r".*\S.*")
    parent_version_ids: list[str] = Field(default_factory=list, max_length=100)
    rights_and_consent_passed: bool
    provenance_and_signoff_passed: bool
    quality_checks: list[VideoNamedCheckRequest] = Field(default_factory=list, max_length=100)
    release_checks: list[VideoNamedCheckRequest] = Field(default_factory=list, max_length=100)


class VideoArtifactResponse(StrictSchema):
    """Redaction-safe immutable artifact-version projection."""

    artifact_id: str
    artifact_version_id: str
    parent_version_ids: list[str]
    created_at: datetime
    rights_and_consent_passed: bool
    provenance_and_signoff_passed: bool


class VideoReleaseConditionResponse(StrictSchema):
    """One independently evaluated release-readiness condition."""

    name: str
    passed: bool
    evidence_references: list[str]


class VideoReleaseRequestResponse(StrictSchema):
    """A retained readiness decision that expressly confirms no release occurred."""

    release_request_id: str
    artifact_version_id: str
    decision: Literal["denied", "permitted"]
    artifact_released: Literal[False] = False
    unmet_conditions: list[str]
    conditions: list[VideoReleaseConditionResponse]
    requested_at: datetime
    correlation_id: str
    action_preview: ActionPreviewResponse


class VaMetadataResponse(StrictSchema):
    """Field-safe VA metadata validation against one published common pattern."""

    pattern_version_id: str
    template: str
    production_phase: str
    valid: bool
    pattern_content_digest: str | None = None
    validation_issues: list[ValidationIssueResponse] = Field(default_factory=list)


class VaProductionActionRequest(StrictSchema):
    """A VA action whose authority and canonical command are selected by the server."""

    pattern_version_id: str = Field(min_length=1, max_length=200)
    template: str = Field(min_length=1, max_length=200)
    production_phase: str = Field(min_length=1, max_length=200)
    action: Literal["create_run", "dispatch_run", "resume_run", "evaluate_run"]
    run_reference: str = Field(min_length=1, max_length=200)
    idempotency_key: str = Field(min_length=1, max_length=200)


class VaProductionActionResponse(StrictSchema):
    """The canonical durable command produced from a valid VA action."""

    metadata: VaMetadataResponse
    canonical_command: str
    canonical_subject_reference: str
    work_item_id: str
    work_state: str
    replayed: bool
    evidence_projection_path: str


class VaRunProjectionResponse(StrictSchema):
    """Authorized redacted canonical evidence for a VA run."""

    run_reference: str
    common_agent_versions: list[dict[str, object]]
    agent_tasks: list[dict[str, object]]
    artifact_handoffs: list[dict[str, object]]
    critique_records: list[dict[str, object]]
    quality_evidence: list[dict[str, object]]
    approval_gates: list[dict[str, object]]
    pinned_provenance: dict[str, object]


class AdoptionPackRegistrationRequest(StrictSchema):
    """A declarative Domain_Pack manifest; signer identity comes from trusted context."""

    manifest: dict[str, object]


class AdoptionPackRegistrationResponse(StrictSchema):
    """A redacted immutable Pack_Contract registration projection."""

    registration_id: str
    pack_id: str
    immutable_version: str
    decision: str
    compatibility_status: str
    validation_result: bool
    policy_passed: bool
    content_digest: str
    correlation_id: str
    reproduction_references: list[str]


class InvocationSubmissionRequest(StrictSchema):
    """The complete invocation association required before a node may start."""

    invocation_id: str = Field(min_length=1, max_length=200)
    domain_id: str = Field(min_length=1, max_length=200)
    pack_id: str = Field(min_length=1, max_length=200)
    pack_version: str = Field(min_length=1, max_length=50)
    agent_id: str = Field(min_length=1, max_length=200)
    workflow_id: str = Field(min_length=1, max_length=200)
    run_id: str = Field(min_length=1, max_length=200)


class InvocationSubmissionResponse(StrictSchema):
    """Evidence that an invocation association crossed the persistence barrier."""

    invocation_id: str
    organization_id: str
    domain_id: str
    pack_version: str
    agent_id: str
    workflow_id: str
    run_id: str
    correlation_id: str
    persisted: bool


class GovernanceDecisionRequest(StrictSchema):
    """A governed capability request; all authority declarations remain Host-owned."""

    domain_id: str = Field(min_length=1, max_length=200)
    pack_version: str = Field(min_length=1, max_length=50)
    agent_id: str = Field(min_length=1, max_length=200)
    capability: str = Field(min_length=1, max_length=500)


class GovernanceDecisionResponse(StrictSchema):
    """A durable allow/deny decision that never treats denial as success authority."""

    decision_id: str
    domain_id: str
    pack_version: str
    agent_id: str
    capability: str
    outcome: Literal["allowed", "denied"]
    allowed: bool
    reason_code: str | None = None
    correlation_id: str


class DataAccessDecisionRequest(StrictSchema):
    """A memory-scope request evaluated against the registered agent declaration."""

    domain_id: str = Field(min_length=1, max_length=200)
    pack_version: str = Field(min_length=1, max_length=50)
    agent_id: str = Field(min_length=1, max_length=200)
    memory_scope: str = Field(min_length=1, max_length=500)


class OutboundDecisionRequest(StrictSchema):
    """An outbound destination request evaluated against a Host-owned allow-list."""

    domain_id: str = Field(min_length=1, max_length=200)
    pack_version: str = Field(min_length=1, max_length=50)
    agent_id: str = Field(min_length=1, max_length=200)
    destination: str = Field(min_length=1, max_length=500)


class ProviderDecisionRequest(StrictSchema):
    """A provider capability request without client-controlled declarations."""

    domain_id: str = Field(min_length=1, max_length=200)
    pack_version: str = Field(min_length=1, max_length=50)
    agent_id: str = Field(min_length=1, max_length=200)
    provider_id: str = Field(min_length=1, max_length=200)
    capability: str = Field(min_length=1, max_length=500)


class AdoptionArtifactHandoffRequest(StrictSchema):
    """Opaque Artifact_Handoff metadata; protected artifact content is not accepted."""

    handoff_id: str = Field(min_length=1, max_length=200)
    artifact_identity: str = Field(min_length=1, max_length=500)
    artifact_version: str = Field(min_length=1, max_length=100)
    parent_lineage: list[str] = Field(default_factory=list, max_length=100)
    source_task_id: str = Field(min_length=1, max_length=200)
    source_run_reference: str = Field(min_length=1, max_length=500)
    brief_scope: str | None = Field(default=None, max_length=500)
    technical_specification: dict[str, object] | None = None
    rights_and_consent_state: str | None = Field(default=None, max_length=200)
    continuity_state: str | None = Field(default=None, max_length=200)
    quality_control_state: str | None = Field(default=None, max_length=200)
    target_channels: list[str] = Field(default_factory=list, max_length=50)
    provenance_reference: str | None = Field(default=None, max_length=500)
    owner_reference: str | None = Field(default=None, max_length=500)
    classification: str | None = Field(default=None, max_length=200)
    integrity_reference: str | None = Field(default=None, max_length=500)
    approval_reference: str | None = Field(default=None, max_length=500)


class AdoptionArtifactHandoffResponse(StrictSchema):
    """A reference-only handoff projection with explicit availability state."""

    handoff_id: str
    artifact_identity: str
    artifact_version: str
    parent_lineage: list[str]
    source_run_reference: str
    availability: str
    external: bool
    metadata_persisted: bool
    correlation_id: str


class LearningActivationRequest(StrictSchema):
    """Activation evidence and exactly the candidate ALC declarations for one agent."""

    lifecycle_id: str = Field(min_length=1, max_length=200)
    pack_id: str = Field(min_length=1, max_length=200)
    immutable_version: str = Field(min_length=1, max_length=50)
    agent_id: str = Field(min_length=1, max_length=200)
    learning_required: bool
    effective_alc_version: str | None = Field(default=None, max_length=50)
    alc_candidates: list[dict[str, object]] = Field(default_factory=list, max_length=10)
    evidence: dict[str, object] = Field(default_factory=dict)


class LifecycleChangeRequest(StrictSchema):
    """References that must be retained before a lifecycle-affecting change."""

    lifecycle_id: str = Field(min_length=1, max_length=200)
    pack_id: str = Field(min_length=1, max_length=200)
    immutable_version: str = Field(min_length=1, max_length=50)
    agent_id: str = Field(min_length=1, max_length=200)
    learning_required: bool
    status: str = Field(min_length=1, max_length=50)
    effective_alc_version: str | None = Field(default=None, max_length=50)
    activation_evidence_references: list[str] = Field(default_factory=list, max_length=100)
    change_references: list[str] = Field(min_length=1, max_length=100)


class LifecycleResponse(StrictSchema):
    """A lifecycle evidence projection that makes non-active outcomes explicit."""

    lifecycle_id: str
    pack_id: str
    immutable_version: str
    agent_id: str
    status: str
    learning_required: bool
    effective_alc_version: str | None
    activation_evidence_references: list[str]
    change_references: list[str]
    correlation_id: str


class RetrievalRecordRequest(StrictSchema):
    """A pre-action retrieval evidence request for one immutable node attempt."""

    attempt_id: str = Field(min_length=1, max_length=200)
    run_id: str = Field(min_length=1, max_length=200)
    node_id: str = Field(min_length=1, max_length=200)
    domain_id: str = Field(min_length=1, max_length=200)
    pack_id: str = Field(min_length=1, max_length=200)
    pack_version: str = Field(min_length=1, max_length=50)
    agent_id: str = Field(min_length=1, max_length=200)
    workflow_id: str = Field(min_length=1, max_length=200)
    status: str = Field(min_length=1, max_length=50)
    terminal_outcome_reference: str | None = Field(default=None, max_length=500)
    memory_scope: str = Field(min_length=1, max_length=500)
    lesson_references: list[str] = Field(default_factory=list, max_length=100)
    approved_filters: dict[str, object] | None = None


class RetrievalRecordResponse(StrictSchema):
    """Redaction-safe retrieval evidence with references but no Lesson content."""

    retrieval_record_id: str
    attempt_id: str
    agent_id: str
    memory_scope: str
    lesson_references: list[str]
    correlation_id: str


class LearningEpisodeRequest(StrictSchema):
    """A terminal Agent_Node_Attempt outcome captured exactly once."""

    attempt_id: str = Field(min_length=1, max_length=200)
    run_id: str = Field(min_length=1, max_length=200)
    node_id: str = Field(min_length=1, max_length=200)
    domain_id: str = Field(min_length=1, max_length=200)
    pack_id: str = Field(min_length=1, max_length=200)
    pack_version: str = Field(min_length=1, max_length=50)
    agent_id: str = Field(min_length=1, max_length=200)
    workflow_id: str = Field(min_length=1, max_length=200)
    status: str = Field(min_length=1, max_length=50)
    terminal_outcome: str = Field(min_length=1, max_length=50)
    outcome_reference: str = Field(min_length=1, max_length=500)
    retrieval_record_id: str | None = Field(default=None, max_length=200)
    evidence_references: list[str] = Field(default_factory=list, max_length=100)


class LearningEpisodeResponse(StrictSchema):
    """Immutable terminal learning evidence projection."""

    episode_id: str
    attempt_id: str
    terminal_outcome: str
    outcome_reference: str
    retrieval_record_id: str | None
    evidence_references: list[str]
    correlation_id: str


class LearningObservabilityResponse(StrictSchema):
    """Per-agent counts only; no Lesson bodies or sensitive learning content."""

    agent_id: str
    learning_episode_count: int
    assessed_lesson_count: int
    retrieved_lesson_reuse_count: int
    stale_lesson_count: int
    revoked_lesson_count: int
    escalation_count: int
    assessment_outcomes: dict[str, int]
    correlation_id: str


class CompatibilityEvidenceRequest(StrictSchema):
    """Independent declared and supported contract ranges for one matrix entry."""

    pack_id: str = Field(min_length=1, max_length=200)
    immutable_version: str = Field(min_length=1, max_length=50)
    pack_contract_version: str = Field(min_length=1, max_length=50)
    declared_host_range: dict[str, object]
    declared_alc_range: dict[str, object]
    supported_host_version: str = Field(min_length=1, max_length=50)
    supported_alc_version: str = Field(min_length=1, max_length=50)


class CompatibilityEvidenceResponse(StrictSchema):
    """Recorded compatibility status and its designated evidence reference."""

    pack_id: str
    immutable_version: str
    status: str
    declared_host_intersects: bool
    declared_alc_intersects: bool
    failure_reasons: list[str]
    evidence_reference: str
    correlation_id: str


class VerificationCheckRequest(StrictSchema):
    """One deterministic named verification result; raw command output is not accepted."""

    name: str = Field(min_length=1, max_length=200)
    layer: Literal["schema", "unit", "property", "integration"]
    passed: bool
    evidence_reference: str | None = Field(default=None, max_length=500)


class ReleaseVerificationRequest(StrictSchema):
    """Layered release evidence input containing references and deterministic outcomes only."""

    pack_id: str = Field(min_length=1, max_length=200)
    immutable_version: str = Field(min_length=1, max_length=50)
    pack_contract_version: str = Field(min_length=1, max_length=50)
    host_contract_version: str = Field(min_length=1, max_length=50)
    alc_version: str = Field(min_length=1, max_length=50)
    workflow_id: str = Field(min_length=1, max_length=200)
    fixed_seed: str = Field(min_length=1, max_length=200)
    fixture_digest: str = Field(min_length=1, max_length=500)
    checks: list[VerificationCheckRequest] = Field(default_factory=list, max_length=500)
    integration_coverage_complete: bool | None = None
    initial_vertical: bool = False
    allow_incomplete_coverage: bool = False
    release_gate_references: list[str] = Field(default_factory=list, max_length=100)


class ReleaseVerificationResponse(StrictSchema):
    """Redacted verification and release-readiness evidence projection."""

    verification_run_id: str
    coverage_status: str
    check_count: int
    passed_check_count: int
    failure_count: int
    failure_persistence_errors: list[str]
    release_decision_status: str | None
    unmet_gate_references: list[str]
    failure_evidence_references: list[str]
    correlation_id: str


class VideoReleaseEvidenceRequest(StrictSchema):
    """A metadata-only handoff and six independent release gates."""

    handoff: AdoptionArtifactHandoffRequest
    pack_id: str = Field(min_length=1, max_length=200)
    immutable_version: str = Field(min_length=1, max_length=50)
    workflow_id: str = Field(min_length=1, max_length=200)
    gates: dict[str, object] = Field(default_factory=dict)
    evidence_references: list[str] = Field(default_factory=list, max_length=100)


class VideoReleaseEvidenceResponse(StrictSchema):
    """Release readiness evidence that cannot imply an artifact release effect."""

    decision_id: str
    status: str
    artifact_released: Literal[False] = False
    unmet_gate_references: list[str]
    evidence_references: list[str]
    correlation_id: str


class MaturityStateRequest(StrictSchema):
    """An independently attributable per-agent maturity evidence record."""

    pack_id: str = Field(min_length=1, max_length=200)
    immutable_version: str = Field(min_length=1, max_length=50)
    agent_id: str = Field(min_length=1, max_length=200)
    level: Literal["cataloged", "registered", "active", "production_proven"]
    evidence_references: list[str] = Field(default_factory=list, max_length=100)
    pack_operational: bool = True


class MaturityStateResponse(StrictSchema):
    """Maturity evidence with operational status kept independent from pack status."""

    maturity_state_id: str
    pack_id: str
    immutable_version: str
    agent_id: str
    level: str
    pack_operational: bool
    evidence_references: list[str]
    correlation_id: str


class CapacityActionRequest(StrictSchema):
    """A policy-selected throttle or disable action at a capacity boundary."""

    pack_id: str = Field(min_length=1, max_length=200)
    immutable_version: str | None = Field(default=None, max_length=50)
    observed_load: float = Field(ge=0)
    approved_load_limit: float = Field(ge=0)
    action: Literal["throttle", "disable"]
    reason: str = Field(min_length=1, max_length=500)


class CapacityActionResponse(StrictSchema):
    """Operational containment result retaining independent maturity evidence."""

    pack_id: str
    action: str
    operational_status: str
    observed_load: float
    approved_load_limit: float
    applied: bool
    disabled: bool
    maturity_agent_count: int
    audit_recorded: bool | None
    reason: str | None
    correlation_id: str
