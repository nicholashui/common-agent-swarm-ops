"""Typed, redaction-safe request and response schemas for the v1 control plane."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class StrictSchema(BaseModel):
    """Reject undeclared client fields, including identity override attempts."""

    model_config = ConfigDict(extra="forbid")


class ValidationIssueResponse(StrictSchema):
    """A stable validation issue that does not expose untrusted payload values."""

    field: str
    reason: str


class ErrorResponse(StrictSchema):
    """A correlation-bearing public control-plane error."""

    code: str
    message: str
    correlation_id: str
    retryable: bool = False
    fields: list[ValidationIssueResponse] = Field(default_factory=list)


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
    action_preview: ActionPreviewResponse
