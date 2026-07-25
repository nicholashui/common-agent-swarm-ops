"""Strict durable control-plane contracts for the browser-facing backend façade."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from types import MappingProxyType
from typing import NewType

from app.models.common import (
    CompatibilityRange,
    RecordMetadata,
    validate_semantic_version,
)
from app.models.contracts import ErrorCode, ErrorField
from app.models.identifiers import (
    ActorId,
    AgentId,
    CorrelationId,
    DomainId,
    DomainPackId,
    InvocationId,
    OrganizationId,
    RunId,
)
from app.models.redaction import RedactionSurface, redact_mapping, redact_value

AgentVersionId = NewType("AgentVersionId", str)
ApprovalGateId = NewType("ApprovalGateId", str)
ArtifactHandoffId = NewType("ArtifactHandoffId", str)
CommonPatternVersionId = NewType("CommonPatternVersionId", str)
EventId = NewType("EventId", str)
GraphRevisionId = NewType("GraphRevisionId", str)
GraphValidationId = NewType("GraphValidationId", str)
ImportId = NewType("ImportId", str)
SwarmInstanceId = NewType("SwarmInstanceId", str)
OutboxId = NewType("OutboxId", str)
VulnerabilityMigrationId = NewType("VulnerabilityMigrationId", str)
ProposalId = NewType("ProposalId", str)
RolloutCampaignId = NewType("RolloutCampaignId", str)
RunProvenanceId = NewType("RunProvenanceId", str)
TaskId = NewType("TaskId", str)
WorkItemId = NewType("WorkItemId", str)


def _required(value: str, name: str) -> None:
    if not value.strip():
        raise ValueError(f"{name} must be non-empty.")


def _timestamp(value: datetime, name: str) -> None:
    if value.tzinfo is None:
        raise ValueError(f"{name} must be timezone-aware.")


def _frozen_value(value: object) -> object:
    """Return a recursively immutable value for durable contract snapshots."""
    if isinstance(value, Mapping):
        return _frozen_mapping(value)
    if isinstance(value, (list, tuple)):
        return tuple(_frozen_value(item) for item in value)
    if isinstance(value, (set, frozenset)):
        return frozenset(_frozen_value(item) for item in value)
    return value


def _frozen_mapping(value: Mapping[str, object]) -> Mapping[str, object]:
    return MappingProxyType({key: _frozen_value(item) for key, item in value.items()})


class ContractStatus(StrEnum):
    """Mutability status for a versioned common contract."""

    DRAFT = "draft"
    PUBLISHED = "published"


class IdempotencyStatus(StrEnum):
    """The durable state of a state-changing command reservation."""

    RESERVED = "reserved"
    COMPLETED = "completed"


class CommonContractKind(StrEnum):
    """The versioned contract family addressed by a migration record."""

    AGENT = "agent"
    PATTERN = "pattern"


class WorkState(StrEnum):
    """Durable work-claim lifecycle."""

    PENDING = "pending"
    CLAIMED = "claimed"
    COMPLETE = "complete"
    FAILED = "failed"
    CANCELLED = "cancelled"
    MANUAL_RECOVERY = "manual_recovery"
    DEAD_LETTER = "dead_letter"


class TaskLifecycle(StrEnum):
    """The complete task lifecycle permitted by the public control plane."""

    IDLE = "idle"
    QUEUED = "queued"
    RUNNING = "running"
    SELF_REFINE = "self_refine"
    WAITING_FOR_CRITIQUE = "waiting_for_critique"
    BLOCKED = "blocked"
    FAILED = "failed"
    COMPLETE = "complete"


class QualityEvidenceKind(StrEnum):
    """Independently retained evidence categories; aggregate scores are not a category."""

    L1_SPECIFICATION = "l1_specification"
    L2_ROLE_RUBRIC = "l2_role_rubric"
    L3_BASELINE_PREFERENCE = "l3_baseline_preference"
    GATE = "gate"


class ApprovalGateStatus(StrEnum):
    """Control-plane approval state; only an approved gate may resume an effect."""

    PENDING = "pending"
    APPROVED = "approved"


class RolloutCampaignStatus(StrEnum):
    """The terminal and rollback-safe states of a bounded rollout campaign."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETE = "complete"
    ROLLING_BACK = "rolling_back"
    ROLLED_BACK = "rolled_back"


class DeliveryState(StrEnum):
    """Outbox delivery state after the enclosing transaction commits."""

    PENDING = "pending"
    PUBLISHED = "published"
    FAILED = "failed"


class ReplayRecoveryReason(StrEnum):
    """Durable internal classifications for a replay that requires projection recovery."""

    POLICY_DIRECTED = "policy_directed"
    SEQUENCE_GAP = "sequence_gap"
    NON_CONTIGUOUS = "non_contiguous"
    CURSOR_UNAVAILABLE = "cursor_unavailable"


class ImportScanState(StrEnum):
    """Safe import processing states."""

    QUARANTINED = "quarantined"
    ALLOWED = "allowed"
    REJECTED = "rejected"


AlertId = NewType("AlertId", str)


class AlertKind(StrEnum):
    """Configured operational conditions that can produce an operator alert."""

    READINESS_FAILURE = "readiness_failure"
    QUEUE_AGE = "queue_age"
    TERMINAL_RUN_FAILURE_RATE = "terminal_run_failure_rate"
    REPLAY_GAP = "replay_gap"
    OUTBOX_LAG = "outbox_lag"
    APPROVAL_EXPIRY = "approval_expiry"
    ROLLBACK = "rollback"


@dataclass(frozen=True, slots=True)
class OperatorAlert:
    """Append-only redaction-safe evidence of one configured degraded condition."""

    metadata: RecordMetadata
    alert_id: AlertId
    kind: AlertKind
    summary: str
    subject_reference: str | None
    detected_at: datetime
    observed_value: float | None = None
    threshold: float | None = None
    details: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _required(str(self.alert_id), "alert_id")
        _required(self.summary, "summary")
        if self.subject_reference is not None:
            _required(self.subject_reference, "subject_reference")
        if (
            not str(self.metadata.correlation_id).strip()
            and self.subject_reference is None
        ):
            raise ValueError(
                "Operator alerts require a correlation identifier or subject reference."
            )
        for value, name in (
            (self.observed_value, "observed_value"),
            (self.threshold, "threshold"),
        ):
            if value is not None and value < 0:
                raise ValueError(f"{name} must not be negative.")
        _timestamp(self.detected_at, "detected_at")
        object.__setattr__(self, "kind", AlertKind(self.kind))
        object.__setattr__(
            self, "summary", redact_value(self.summary, surface=RedactionSurface.AUDIT)
        )
        if self.subject_reference is not None:
            object.__setattr__(
                self,
                "subject_reference",
                redact_value(self.subject_reference, surface=RedactionSurface.AUDIT),
            )
        object.__setattr__(
            self,
            "details",
            redact_mapping(self.details, surface=RedactionSurface.AUDIT),
        )


@dataclass(frozen=True, slots=True)
class PublicResponse[T]:
    """Typed successful body envelope used by later response serializers."""

    data: T
    correlation_id: CorrelationId


@dataclass(frozen=True, slots=True)
class PublicError:
    """Typed public error fields, limited to safe details and a stable error code."""

    code: ErrorCode
    message: str
    correlation_id: CorrelationId
    retryable: bool = False
    fields: tuple[ErrorField, ...] = ()

    def __post_init__(self) -> None:
        _required(self.message, "message")


@dataclass(frozen=True, slots=True)
class IdempotencyRecord:
    """One actor/key request reservation and the response retained for a successful replay."""

    metadata: RecordMetadata
    actor_id: ActorId
    idempotency_key: str
    request_digest: str
    status: IdempotencyStatus
    response_reference: str | None = None
    response_payload: Mapping[str, object] | None = None

    def __post_init__(self) -> None:
        for value, name in (
            (str(self.actor_id), "actor_id"),
            (self.idempotency_key, "idempotency_key"),
            (self.request_digest, "request_digest"),
        ):
            _required(value, name)
        has_response = (
            self.response_reference is not None or self.response_payload is not None
        )
        if self.status is IdempotencyStatus.RESERVED and has_response:
            raise ValueError("Reserved idempotency records cannot contain a response.")
        if self.status is IdempotencyStatus.COMPLETED:
            if self.response_reference is None or self.response_payload is None:
                raise ValueError(
                    "Completed idempotency records require a response reference and payload."
                )
            _required(self.response_reference, "response_reference")
            object.__setattr__(
                self, "response_payload", _frozen_mapping(self.response_payload)
            )


@dataclass(frozen=True, slots=True)
class CommonAgentVersion:
    """A complete immutable version of a reusable agent contract."""

    metadata: RecordMetadata
    agent_version_id: AgentVersionId
    status: ContractStatus
    canonical_identity: str
    category: str
    responsibilities: tuple[str, ...]
    boundaries: tuple[str, ...]
    escalation_targets: tuple[str, ...]
    approval_authority: tuple[str, ...]
    runtime_policy: Mapping[str, object]
    tool_policy: Mapping[str, object]
    quality_rubric: Mapping[str, object]
    critique_relationships: tuple[str, ...]
    knowledge_bindings: tuple[str, ...]
    input_schema: Mapping[str, object]
    output_schema: Mapping[str, object]
    provenance_policy: Mapping[str, object]
    content_digest: str

    def __post_init__(self) -> None:
        for value, name in (
            (str(self.agent_version_id), "agent_version_id"),
            (self.canonical_identity, "canonical_identity"),
            (self.category, "category"),
            (self.content_digest, "content_digest"),
        ):
            _required(value, name)
        for name in (
            "runtime_policy",
            "tool_policy",
            "quality_rubric",
            "input_schema",
            "output_schema",
            "provenance_policy",
        ):
            object.__setattr__(self, name, _frozen_mapping(getattr(self, name)))


@dataclass(frozen=True, slots=True)
class CommonPatternVersion:
    """A complete immutable version of a reusable graph-pattern contract."""

    metadata: RecordMetadata
    pattern_version_id: CommonPatternVersionId
    status: ContractStatus
    graph_template: Mapping[str, object]
    slot_constraints: Mapping[str, object]
    compatibility_rules: Mapping[str, object]
    risk_requirements: Mapping[str, object]
    verification_requirements: Mapping[str, object]
    provenance: Mapping[str, object]
    content_digest: str

    def __post_init__(self) -> None:
        _required(str(self.pattern_version_id), "pattern_version_id")
        _required(self.content_digest, "content_digest")
        for name in (
            "graph_template",
            "slot_constraints",
            "compatibility_rules",
            "risk_requirements",
            "verification_requirements",
            "provenance",
        ):
            object.__setattr__(self, name, _frozen_mapping(getattr(self, name)))


class GraphValidationCategory(StrEnum):
    """Every independently reported graph validation category."""

    VERSION_RESOLUTION = "version_resolution"
    SCHEMA_COMPATIBILITY = "schema_compatibility"
    TOOL_POLICY = "tool_policy"
    BUDGET_POLICY = "budget_policy"
    VERIFICATION_POLICY = "verification_policy"
    ROLLBACK_POLICY = "rollback_policy"
    APPROVAL_POLICY = "approval_policy"


@dataclass(frozen=True, slots=True)
class GraphValidationCategoryResult:
    """A field-safe result for exactly one graph validation category."""

    category: GraphValidationCategory
    passed: bool
    fields: tuple[ErrorField, ...] = ()

    def __post_init__(self) -> None:
        if self.passed and self.fields:
            raise ValueError(
                "Passing validation categories cannot retain failure fields."
            )


@dataclass(frozen=True, slots=True)
class SwarmInstance:
    """Organization-owned aggregate tracking the newest immutable graph revision."""

    metadata: RecordMetadata
    swarm_instance_id: SwarmInstanceId
    current_revision: int = 0
    current_graph_revision_id: GraphRevisionId | None = None

    def __post_init__(self) -> None:
        _required(str(self.swarm_instance_id), "swarm_instance_id")
        if self.current_revision < 0:
            raise ValueError("current_revision cannot be negative.")
        if (self.current_revision == 0) != (self.current_graph_revision_id is None):
            raise ValueError(
                "Initial swarm instances must not reference a graph revision."
            )


@dataclass(frozen=True, slots=True)
class GraphRevision:
    """An immutable supplied graph composition awaiting an append-only validation record."""

    metadata: RecordMetadata
    graph_revision_id: GraphRevisionId
    swarm_instance_id: SwarmInstanceId
    revision: int
    nodes: tuple[Mapping[str, object], ...]
    edges: tuple[Mapping[str, object], ...]
    layout: Mapping[str, object]
    version_pins: Mapping[str, object]
    policies: Mapping[str, object]

    def __post_init__(self) -> None:
        _required(str(self.graph_revision_id), "graph_revision_id")
        _required(str(self.swarm_instance_id), "swarm_instance_id")
        if self.revision < 1:
            raise ValueError("Graph revisions must start at revision one.")
        object.__setattr__(
            self, "nodes", tuple(_frozen_mapping(node) for node in self.nodes)
        )
        object.__setattr__(
            self, "edges", tuple(_frozen_mapping(edge) for edge in self.edges)
        )
        object.__setattr__(self, "layout", _frozen_mapping(self.layout))
        object.__setattr__(self, "version_pins", _frozen_mapping(self.version_pins))
        object.__setattr__(self, "policies", _frozen_mapping(self.policies))


@dataclass(frozen=True, slots=True)
class GraphValidationReport:
    """Append-only validation outcome that alone determines a revision's run eligibility."""

    metadata: RecordMetadata
    graph_validation_id: GraphValidationId
    graph_revision_id: GraphRevisionId
    categories: tuple[GraphValidationCategoryResult, ...]
    eligible_for_run: bool
    workflow_definition: Mapping[str, object] | None = None
    workflow_definition_version: str | None = None
    agent_version_ids: tuple[AgentVersionId, ...] = ()
    pattern_version_ids: tuple[CommonPatternVersionId, ...] = ()

    def __post_init__(self) -> None:
        _required(str(self.graph_validation_id), "graph_validation_id")
        _required(str(self.graph_revision_id), "graph_revision_id")
        categories = tuple(result.category for result in self.categories)
        if set(categories) != set(GraphValidationCategory) or len(categories) != len(
            GraphValidationCategory
        ):
            raise ValueError(
                "Graph validation must retain one result for every category."
            )
        successful = all(result.passed for result in self.categories)
        if self.eligible_for_run != successful:
            raise ValueError(
                "Graph eligibility requires successful validation in every category."
            )
        if self.eligible_for_run:
            if self.workflow_definition is None or not self.workflow_definition_version:
                raise ValueError(
                    "Eligible graph revisions require a versioned workflow definition."
                )
            object.__setattr__(
                self, "workflow_definition", _frozen_mapping(self.workflow_definition)
            )
        elif (
            self.workflow_definition is not None
            or self.workflow_definition_version is not None
        ):
            raise ValueError(
                "Ineligible graph revisions cannot retain a workflow definition."
            )


@dataclass(frozen=True, slots=True)
class VulnerabilityMigration:
    """An immutable requirement to move from a vulnerable version to a patched target."""

    metadata: RecordMetadata
    migration_id: VulnerabilityMigrationId
    contract_kind: CommonContractKind
    source_version_id: str
    target_version_id: str
    vulnerability_reference: str

    def __post_init__(self) -> None:
        for value, name in (
            (str(self.migration_id), "migration_id"),
            (self.source_version_id, "source_version_id"),
            (self.target_version_id, "target_version_id"),
            (self.vulnerability_reference, "vulnerability_reference"),
        ):
            _required(value, name)
        if self.source_version_id == self.target_version_id:
            raise ValueError(
                "A vulnerability migration target must be a distinct version."
            )


@dataclass(frozen=True, slots=True)
class RunProvenance:
    """An immutable pre-dispatch snapshot of resolved graph and common versions."""

    metadata: RecordMetadata
    run_provenance_id: RunProvenanceId
    graph_revision_id: GraphRevisionId
    workflow_definition: Mapping[str, object]
    workflow_definition_version: str
    agent_version_ids: tuple[AgentVersionId, ...]
    pattern_version_ids: tuple[CommonPatternVersionId, ...]
    source_checkpoint_reference: str | None = None
    artifact_version_references: tuple[str, ...] = ()
    source_run_provenance_id: RunProvenanceId | None = None

    def __post_init__(self) -> None:
        for value, name in (
            (str(self.run_provenance_id), "run_provenance_id"),
            (str(self.graph_revision_id), "graph_revision_id"),
            (self.workflow_definition_version, "workflow_definition_version"),
        ):
            _required(value, name)
        if self.source_run_provenance_id is not None:
            _required(str(self.source_run_provenance_id), "source_run_provenance_id")
            if self.source_run_provenance_id == self.run_provenance_id:
                raise ValueError(
                    "Replay provenance must identify a distinct source lineage."
                )
        if not self.agent_version_ids and not self.pattern_version_ids:
            raise ValueError(
                "Run provenance requires at least one resolved common version."
            )
        object.__setattr__(
            self, "workflow_definition", _frozen_mapping(self.workflow_definition)
        )


@dataclass(frozen=True, slots=True)
class WorkItem:
    """Durable request for governed asynchronous work, retained before dispatch."""

    metadata: RecordMetadata
    work_item_id: WorkItemId
    subject_reference: str
    attempt: int
    idempotency_key: str
    scheduled_at: datetime
    cancellation_requested: bool
    state: WorkState
    claim_owner: str | None = None
    claim_expires_at: datetime | None = None
    retry_classifications: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for value, name in (
            (str(self.work_item_id), "work_item_id"),
            (self.subject_reference, "subject_reference"),
            (self.idempotency_key, "idempotency_key"),
        ):
            _required(value, name)
        if self.attempt < 0:
            raise ValueError("attempt must not be negative.")
        _timestamp(self.scheduled_at, "scheduled_at")
        if self.state is WorkState.CLAIMED and (
            not self.claim_owner or self.claim_expires_at is None
        ):
            raise ValueError("Claimed work requires a claim owner and expiry.")
        if self.claim_expires_at is not None:
            _timestamp(self.claim_expires_at, "claim_expires_at")


@dataclass(frozen=True, slots=True)
class WorkTransition:
    """Append-only durable evidence of one work lifecycle transition."""

    metadata: RecordMetadata
    transition_id: str
    work_item_id: WorkItemId
    from_state: WorkState
    to_state: WorkState
    recorded_at: datetime
    reason_code: str

    def __post_init__(self) -> None:
        for value, name in (
            (self.transition_id, "transition_id"),
            (str(self.work_item_id), "work_item_id"),
            (self.reason_code, "reason_code"),
        ):
            _required(value, name)
        _timestamp(self.recorded_at, "recorded_at")


@dataclass(frozen=True, slots=True)
class AgentTask:
    """Run-scoped task planning and lifecycle state, pinned to an agent version."""

    metadata: RecordMetadata
    task_id: TaskId
    run_reference: str
    pinned_agent_version_id: AgentVersionId
    dependencies: tuple[TaskId, ...]
    constraints: Mapping[str, object]
    approval_gate_ids: tuple[ApprovalGateId, ...]
    checkpoint_reference: str | None
    state: TaskLifecycle
    retry_count: int = 0
    iteration_count: int = 0
    ineligible_for_execution: bool = False
    failure_reason: str | None = None
    blocked_fields: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for value, name in (
            (str(self.task_id), "task_id"),
            (self.run_reference, "run_reference"),
            (str(self.pinned_agent_version_id), "pinned_agent_version_id"),
        ):
            _required(value, name)
        if self.retry_count < 0 or self.iteration_count < 0:
            raise ValueError("Task counters must not be negative.")
        if self.state is TaskLifecycle.FAILED and not self.failure_reason:
            raise ValueError("Failed tasks require a machine-readable failure reason.")
        if self.blocked_fields and self.state is not TaskLifecycle.BLOCKED:
            raise ValueError("Only blocked tasks may retain blocked fields.")
        if len(self.blocked_fields) != len(set(self.blocked_fields)):
            raise ValueError("Blocked task fields must be unique.")
        for field_name in self.blocked_fields:
            _required(field_name, "blocked_field")
        object.__setattr__(self, "constraints", _frozen_mapping(self.constraints))


@dataclass(frozen=True, slots=True)
class TaskTransition:
    """Append-only optimistic task-transition evidence."""

    metadata: RecordMetadata
    transition_id: str
    task_id: TaskId
    expected_task_version: int
    from_state: TaskLifecycle
    to_state: TaskLifecycle
    recorded_at: datetime

    def __post_init__(self) -> None:
        _required(self.transition_id, "transition_id")
        _required(str(self.task_id), "task_id")
        if self.expected_task_version < 1:
            raise ValueError("expected_task_version must be positive.")
        _timestamp(self.recorded_at, "recorded_at")


class ArtifactAvailabilityStatus(StrEnum):
    """Availability barrier for an immutable Artifact_Handoff."""

    PENDING = "pending"
    AVAILABLE = "available"
    REVOKED = "revoked"


@dataclass(frozen=True, slots=True)
class ArtifactHandoff:
    """Versioned opaque artifact handoff; protected content is deliberately absent."""

    metadata: RecordMetadata
    handoff_id: ArtifactHandoffId
    artifact_identity: str
    artifact_version: str
    parent_lineage: tuple[str, ...]
    source_task_id: TaskId
    source_run_reference: str
    brief_scope: str | None
    technical_specification: Mapping[str, object] | None
    rights_and_consent_state: str | None
    continuity_state: str | None
    quality_control_state: str | None
    target_channels: tuple[str, ...]
    provenance_reference: str | None
    owner_reference: str | None = None
    classification: str | None = None
    integrity_reference: str | None = None
    approval_reference: str | None = None
    availability: ArtifactAvailabilityStatus = ArtifactAvailabilityStatus.PENDING
    external: bool = False
    metadata_persisted: bool = False

    def __post_init__(self) -> None:
        for value, name in (
            (str(self.handoff_id), "handoff_id"),
            (self.artifact_identity, "artifact_identity"),
            (self.artifact_version, "artifact_version"),
            (str(self.source_task_id), "source_task_id"),
            (self.source_run_reference, "source_run_reference"),
        ):
            _required(value, name)
        lineage = tuple(str(reference) for reference in self.parent_lineage)
        if any(not reference.strip() for reference in lineage):
            raise ValueError("Artifact handoff lineage references must be non-empty.")
        if len(lineage) != len(set(lineage)):
            raise ValueError("Artifact handoff lineage references must be unique.")
        object.__setattr__(self, "parent_lineage", lineage)
        channels = tuple(str(channel) for channel in self.target_channels)
        if any(not channel.strip() for channel in channels):
            raise ValueError("Artifact handoff target channels must be non-empty.")
        object.__setattr__(self, "target_channels", channels)
        for optional_value, name in (
            (self.owner_reference, "owner_reference"),
            (self.classification, "classification"),
            (self.integrity_reference, "integrity_reference"),
            (self.approval_reference, "approval_reference"),
            (self.provenance_reference, "provenance_reference"),
        ):
            if optional_value is not None:
                _required(optional_value, name)
        object.__setattr__(
            self, "availability", ArtifactAvailabilityStatus(self.availability)
        )
        if self.metadata_persisted and any(
            value is None
            for value in (
                self.owner_reference,
                self.classification,
                self.integrity_reference,
                self.approval_reference,
                self.provenance_reference,
            )
        ):
            raise ValueError("Confirmed handoffs require complete metadata references.")
        if self.availability is ArtifactAvailabilityStatus.AVAILABLE:
            if not self.metadata_persisted:
                raise ValueError(
                    "Artifact handoffs require metadata confirmation before availability."
                )
            if self.external and not self.metadata_persisted:
                raise ValueError(
                    "External artifact handoffs require metadata confirmation."
                )
        if self.technical_specification is not None:
            object.__setattr__(
                self,
                "technical_specification",
                _frozen_mapping(self.technical_specification),
            )


@dataclass(frozen=True, slots=True)
class CritiqueRecord:
    """A directed critique record with evidence reference rather than raw content."""

    metadata: RecordMetadata
    critique_id: str
    source_reference: str
    target_task_id: TaskId
    relationship_reference: str
    evidence_reference: str
    submitted_at: datetime

    def __post_init__(self) -> None:
        for value, name in (
            (self.critique_id, "critique_id"),
            (self.source_reference, "source_reference"),
            (str(self.target_task_id), "target_task_id"),
            (self.relationship_reference, "relationship_reference"),
            (self.evidence_reference, "evidence_reference"),
        ):
            _required(value, name)
        _timestamp(self.submitted_at, "submitted_at")


@dataclass(frozen=True, slots=True)
class QualityEvidence:
    """Category-specific independently retained quality or gate evidence."""

    metadata: RecordMetadata
    evidence_id: str
    kind: QualityEvidenceKind
    subject_reference: str
    passed: bool
    evidence_reference: str
    recorded_at: datetime

    def __post_init__(self) -> None:
        for value, name in (
            (self.evidence_id, "evidence_id"),
            (self.subject_reference, "subject_reference"),
            (self.evidence_reference, "evidence_reference"),
        ):
            _required(value, name)
        _timestamp(self.recorded_at, "recorded_at")


@dataclass(frozen=True, slots=True)
class ApprovalGate:
    """A server-owned pending operation and its retained human decision evidence."""

    metadata: RecordMetadata
    approval_gate_id: ApprovalGateId
    pending_operation_reference: str
    status: ApprovalGateStatus
    decision: str | None = None
    decision_reason: str | None = None
    reviewer_reference: str | None = None

    def __post_init__(self) -> None:
        _required(str(self.approval_gate_id), "approval_gate_id")
        _required(self.pending_operation_reference, "pending_operation_reference")
        object.__setattr__(self, "status", ApprovalGateStatus(self.status))
        provided = (self.decision, self.decision_reason, self.reviewer_reference)
        if any(value is not None for value in provided) and not all(
            value is not None for value in provided
        ):
            raise ValueError(
                "Approval decisions require value, reason, and reviewer reference."
            )
        if self.status is ApprovalGateStatus.APPROVED and not all(
            isinstance(value, str) and value.strip() for value in provided
        ):
            raise ValueError(
                "Approved gates require a complete decision, reason, and reviewer."
            )


class ProposalSandboxState(StrEnum):
    """Sandbox transition state for an Improvement_Proposal."""

    SANDBOX = "sandbox"
    TRANSITION_FAILED = "transition_failed"


class ProposalPromotionState(StrEnum):
    """Promotion state that prevents unapproved live changes."""

    NOT_APPROVED = "not_approved"
    APPROVED = "approved"
    PROMOTED = "promoted"


@dataclass(frozen=True, slots=True)
class ImprovementProposal:
    """Immutable difference and all evidence required to assess production eligibility."""

    metadata: RecordMetadata
    proposal_id: ProposalId
    source_version_reference: str
    immutable_difference: Mapping[str, object]
    source_evidence: tuple[str, ...]
    validation_evidence: tuple[str, ...]
    evaluation_evidence: tuple[str, ...]
    reviewer_decisions: tuple[str, ...]
    approval_evidence: tuple[str, ...]
    rollback_evidence: tuple[str, ...]
    impact_summary: str
    sandbox_state: ProposalSandboxState = ProposalSandboxState.SANDBOX
    promotion_state: ProposalPromotionState = ProposalPromotionState.NOT_APPROVED
    replaced_version_reference: str | None = None
    promoted_version_reference: str | None = None
    rollback_reference: str | None = None
    sandbox_transition_failure_evidence: tuple[str, ...] = ()
    reviewer_identity: str | None = None
    reviewer_decision_timestamp: datetime | None = None
    reviewer_evidence_references: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for value, name in (
            (str(self.proposal_id), "proposal_id"),
            (self.source_version_reference, "source_version_reference"),
            (self.impact_summary, "impact_summary"),
        ):
            _required(value, name)
        object.__setattr__(
            self, "immutable_difference", _frozen_mapping(self.immutable_difference)
        )
        object.__setattr__(
            self, "sandbox_state", ProposalSandboxState(self.sandbox_state)
        )
        object.__setattr__(
            self, "promotion_state", ProposalPromotionState(self.promotion_state)
        )
        for name in (
            "source_evidence",
            "validation_evidence",
            "evaluation_evidence",
            "reviewer_decisions",
            "approval_evidence",
            "rollback_evidence",
            "sandbox_transition_failure_evidence",
            "reviewer_evidence_references",
        ):
            object.__setattr__(
                self, name, _adoption_references(getattr(self, name), name)
            )
        for optional_value, name in (
            (self.replaced_version_reference, "replaced_version_reference"),
            (self.promoted_version_reference, "promoted_version_reference"),
            (self.rollback_reference, "rollback_reference"),
            (self.reviewer_identity, "reviewer_identity"),
        ):
            if optional_value is not None:
                _required(optional_value, name)
        if self.reviewer_decision_timestamp is not None:
            _timestamp(self.reviewer_decision_timestamp, "reviewer_decision_timestamp")
        if (self.reviewer_identity is None) != (
            self.reviewer_decision_timestamp is None
        ):
            raise ValueError(
                "Reviewer identity and decision timestamp must be recorded together."
            )
        if self.promotion_state is ProposalPromotionState.APPROVED and not (
            self.reviewer_identity
            and self.reviewer_decision_timestamp is not None
            and self.reviewer_evidence_references
            and self.rollback_reference
        ):
            raise ValueError(
                "Approved proposals require designated reviewer, evidence, and rollback references."
            )
        if self.promotion_state is ProposalPromotionState.PROMOTED:
            if not self.approval_evidence or not self.replaced_version_reference:
                raise ValueError(
                    "Promoted proposals require approval and replaced-version evidence."
                )
            if not self.promoted_version_reference or not self.rollback_reference:
                raise ValueError(
                    "Promoted proposals require promoted and rollback references."
                )

    @property
    def state_transition_failure_evidence(self) -> tuple[str, ...]:
        """Expose sandbox transition failure evidence using requirement terminology."""
        return self.sandbox_transition_failure_evidence

    @property
    def reviewer_id(self) -> str | None:
        """Expose the designated reviewer identity in concise form."""
        return self.reviewer_identity

    @property
    def decision_timestamp(self) -> datetime | None:
        """Expose the retained reviewer decision timestamp."""
        return self.reviewer_decision_timestamp

    @property
    def decision_evidence_references(self) -> tuple[str, ...]:
        """Expose evidence attached to the designated reviewer decision."""
        return self.reviewer_evidence_references


@dataclass(frozen=True, slots=True)
class RolloutCampaign:
    """Bounded rollout with independent evidence, criteria, outcomes, and rollback state."""

    metadata: RecordMetadata
    campaign_id: RolloutCampaignId
    proposal_id: ProposalId
    selected_version_reference: str
    target_scope: tuple[str, ...]
    evaluation_evidence_references: tuple[str, ...]
    required_approval_references: tuple[str, ...]
    success_criteria: Mapping[str, object]
    rollback_reference: str
    status: RolloutCampaignStatus
    measured_outcomes: Mapping[str, object]

    def __post_init__(self) -> None:
        for value, name in (
            (str(self.campaign_id), "campaign_id"),
            (str(self.proposal_id), "proposal_id"),
            (self.selected_version_reference, "selected_version_reference"),
            (self.rollback_reference, "rollback_reference"),
        ):
            _required(value, name)
        if not self.target_scope:
            raise ValueError("Rollout campaigns require bounded target scope.")
        object.__setattr__(self, "status", RolloutCampaignStatus(self.status))
        for name in (
            "target_scope",
            "evaluation_evidence_references",
            "required_approval_references",
        ):
            object.__setattr__(self, name, tuple(getattr(self, name)))
        object.__setattr__(
            self, "success_criteria", _frozen_mapping(self.success_criteria)
        )
        object.__setattr__(
            self, "measured_outcomes", _frozen_mapping(self.measured_outcomes)
        )


@dataclass(frozen=True, slots=True)
class AuditRecord:
    """Append-only redaction-safe action evidence written with state changes."""

    metadata: RecordMetadata
    audit_id: str
    action: str
    subject_reference: str
    outcome: str
    recorded_at: datetime
    actor_id: ActorId | None = None
    reason: str | None = None
    source_references: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for value, name in (
            (self.audit_id, "audit_id"),
            (self.action, "action"),
            (self.subject_reference, "subject_reference"),
            (self.outcome, "outcome"),
        ):
            _required(value, name)
        safe_action = redact_value(self.action, surface=RedactionSurface.AUDIT)
        safe_subject = redact_value(
            self.subject_reference, surface=RedactionSurface.AUDIT
        )
        safe_outcome = redact_value(self.outcome, surface=RedactionSurface.AUDIT)
        object.__setattr__(self, "action", safe_action)
        object.__setattr__(self, "subject_reference", safe_subject)
        object.__setattr__(self, "outcome", safe_outcome)
        if self.actor_id is not None:
            _required(str(self.actor_id), "actor_id")
        if self.reason is not None:
            _required(self.reason, "reason")
            object.__setattr__(
                self,
                "reason",
                redact_value(self.reason, surface=RedactionSurface.AUDIT),
            )
        object.__setattr__(
            self,
            "source_references",
            _adoption_references(self.source_references, "source_references"),
        )
        _timestamp(self.recorded_at, "recorded_at")

    @property
    def timestamp(self) -> datetime:
        """Expose the audit timestamp using the requirement terminology."""
        return self.recorded_at

    @property
    def revocation_reason(self) -> str | None:
        """Return the redaction-safe reason retained for a revocation audit."""
        return self.reason

    @property
    def actor(self) -> ActorId | None:
        """Expose the actor using the requirement terminology."""
        return self.actor_id

    @property
    def source_episode_references(self) -> tuple[str, ...]:
        """Expose revocation sources using the learning-evidence terminology."""
        return self.source_references


@dataclass(frozen=True, slots=True)
class OperationalEvent:
    """Redacted sequenceable event retained before public delivery."""

    metadata: RecordMetadata
    event_id: EventId
    sequence: int
    event_type: str
    subject_reference: str
    occurred_at: datetime
    payload_schema_version: int
    redacted_payload: Mapping[str, object]
    topic: str = "operational"

    def __post_init__(self) -> None:
        for value, name in (
            (str(self.event_id), "event_id"),
            (self.event_type, "event_type"),
            (self.subject_reference, "subject_reference"),
            (self.topic, "topic"),
        ):
            _required(value, name)
        if self.sequence < 1:
            raise ValueError("sequence must be positive.")
        if self.payload_schema_version < 1:
            raise ValueError("payload_schema_version must be positive.")
        _timestamp(self.occurred_at, "occurred_at")
        object.__setattr__(
            self,
            "event_type",
            redact_value(self.event_type, surface=RedactionSurface.OPERATIONAL_EVENT),
        )
        object.__setattr__(
            self,
            "subject_reference",
            redact_value(
                self.subject_reference, surface=RedactionSurface.OPERATIONAL_EVENT
            ),
        )
        object.__setattr__(
            self,
            "topic",
            redact_value(self.topic, surface=RedactionSurface.OPERATIONAL_EVENT),
        )
        object.__setattr__(
            self,
            "redacted_payload",
            redact_mapping(
                self.redacted_payload, surface=RedactionSurface.OPERATIONAL_EVENT
            ),
        )


@dataclass(frozen=True, slots=True)
class EventReplayWindow:
    """A bounded retained event window and its topic-local high-water mark."""

    events: tuple[OperationalEvent, ...]
    high_watermark: int

    def __post_init__(self) -> None:
        if self.high_watermark < 0:
            raise ValueError("high_watermark must not be negative.")
        if any(event.sequence > self.high_watermark for event in self.events):
            raise ValueError("Replay events cannot exceed the high-water mark.")


@dataclass(frozen=True, slots=True)
class ReplayRecoveryOutcome:
    """Append-only evidence that replay safely directed a client to refresh its projection."""

    metadata: RecordMetadata
    topic: str
    cursor_sequence: int
    reason: ReplayRecoveryReason
    recorded_at: datetime

    def __post_init__(self) -> None:
        _required(self.topic, "topic")
        if self.cursor_sequence < 0:
            raise ValueError("cursor_sequence must not be negative.")
        _timestamp(self.recorded_at, "recorded_at")


@dataclass(frozen=True, slots=True)
class OutboxRecord:
    """Durable delivery record written atomically with its operational event."""

    metadata: RecordMetadata
    outbox_id: OutboxId
    event_id: EventId
    state: DeliveryState
    created_at: datetime

    def __post_init__(self) -> None:
        for value, name in (
            (str(self.outbox_id), "outbox_id"),
            (str(self.event_id), "event_id"),
        ):
            _required(value, name)
        _timestamp(self.created_at, "created_at")


@dataclass(frozen=True, slots=True)
class ImportRecord:
    """Validated import metadata and opaque reference, never parsed authority-bearing content."""

    metadata: RecordMetadata
    import_id: ImportId
    declared_type: str
    detected_type: str
    size_bytes: int
    checksum: str
    normalized_storage_name: str
    scan_state: ImportScanState
    opaque_storage_reference: str | None = None

    def __post_init__(self) -> None:
        for value, name in (
            (str(self.import_id), "import_id"),
            (self.declared_type, "declared_type"),
            (self.detected_type, "detected_type"),
            (self.checksum, "checksum"),
            (self.normalized_storage_name, "normalized_storage_name"),
        ):
            _required(value, name)
        if self.size_bytes < 0:
            raise ValueError("size_bytes must not be negative.")
        if (
            self.scan_state is ImportScanState.ALLOWED
            and not self.opaque_storage_reference
        ):
            raise ValueError("Allowed imports require an opaque storage reference.")


@dataclass(frozen=True, slots=True)
class SecurityEvidence:
    """Redacted evidence of a configured untrusted-content protection outcome."""

    metadata: RecordMetadata
    security_evidence_id: str
    import_id: ImportId | None
    indicator: str
    protection: str
    passed: bool
    recorded_at: datetime

    def __post_init__(self) -> None:
        for value, name in (
            (self.security_evidence_id, "security_evidence_id"),
            (self.indicator, "indicator"),
            (self.protection, "protection"),
        ):
            _required(value, name)
        _timestamp(self.recorded_at, "recorded_at")


class SessionModel(StrEnum):
    """Deployment-owned browser authentication transport semantics."""

    BEARER_TOKEN = "bearer_token"
    COOKIE = "cookie"


@dataclass(frozen=True, slots=True)
class DeploymentConfiguration:
    """Validated deployment policy containing secret references, never secret values."""

    metadata: RecordMetadata
    configuration_id: str
    trusted_origins: tuple[str, ...]
    identity_integration: str
    persistence_adapter: str
    dispatch_adapter: str
    retention_policies: Mapping[str, object]
    rate_limits: Mapping[str, object]
    feature_flags: Mapping[str, object]
    secret_references: tuple[str, ...]
    production_transport_enabled: bool
    session_model: SessionModel = SessionModel.BEARER_TOKEN
    work_recovery_policy: Mapping[str, object] = field(
        default_factory=lambda: {
            "claim_expiry_decision": "dead_letter",
            "worker_stop_decision": "dead_letter",
            "max_attempts": 1,
            "retry_delay_seconds": 0,
        }
    )

    def __post_init__(self) -> None:
        for value, name in (
            (self.configuration_id, "configuration_id"),
            (self.identity_integration, "identity_integration"),
            (self.persistence_adapter, "persistence_adapter"),
            (self.dispatch_adapter, "dispatch_adapter"),
        ):
            _required(value, name)
        if self.production_transport_enabled and not self.trusted_origins:
            raise ValueError(
                "Production transport requires at least one trusted origin."
            )
        for name in (
            "retention_policies",
            "rate_limits",
            "feature_flags",
            "work_recovery_policy",
        ):
            object.__setattr__(self, name, _frozen_mapping(getattr(self, name)))


# Adoption control-plane durable records
RegistrationId = NewType("RegistrationId", str)
AuthorizationDecisionId = NewType("AuthorizationDecisionId", str)
AgentLifecycleId = NewType("AgentLifecycleId", str)
WorkflowActivationId = NewType("WorkflowActivationId", str)
MigrationPhaseId = NewType("MigrationPhaseId", str)
SourceIndexEntryId = NewType("SourceIndexEntryId", str)
VerificationRunId = NewType("VerificationRunId", str)
ReleaseReadinessDecisionId = NewType("ReleaseReadinessDecisionId", str)
RecoveryActionId = NewType("RecoveryActionId", str)
MaturityStateId = NewType("MaturityStateId", str)
RetrievalRecordId = NewType("RetrievalRecordId", str)
LearningEpisodeId = NewType("LearningEpisodeId", str)
LessonId = NewType("LessonId", str)
AgentNodeAttemptId = NewType("AgentNodeAttemptId", str)


def _validate_adoption_metadata(metadata: RecordMetadata) -> None:
    """Validate trace and version fields required by new durable evidence records."""
    _required(str(metadata.record_id), "metadata.record_id")
    _required(str(metadata.organization_id), "metadata.organization_id")
    _required(str(metadata.correlation_id), "metadata.correlation_id")
    if metadata.schema_version < 1 or metadata.version < 1:
        raise ValueError("Durable record schema and version values must be positive.")
    _timestamp(metadata.created_at, "metadata.created_at")
    _timestamp(metadata.updated_at, "metadata.updated_at")


def _adoption_references(
    values: tuple[str, ...], name: str, *, required: bool = False
) -> tuple[str, ...]:
    references = tuple(str(value) for value in values)
    if required and not references:
        raise ValueError(f"{name} requires at least one reference.")
    if any(not value.strip() for value in references):
        raise ValueError(f"{name} references must be non-empty.")
    if len(references) != len(set(references)):
        raise ValueError(f"{name} references must be unique.")
    return references


class RegistrationDecision(StrEnum):
    """The immutable admission decision for a Domain_Pack version."""

    APPROVED = "approved"
    REJECTED = "rejected"


class CompatibilityStatus(StrEnum):
    """Recorded intersection result for independently versioned contracts."""

    COMPATIBLE = "compatible"
    INCOMPATIBLE = "incompatible"
    NOT_EVALUATED = "not_evaluated"


@dataclass(frozen=True, slots=True)
class Registration:
    """Immutable admission evidence for one content-addressed pack version."""

    metadata: RecordMetadata
    registration_id: RegistrationId
    pack_id: DomainPackId
    immutable_version: str
    content_digest: str
    signer_id: ActorId
    host_compatibility_range: CompatibilityRange
    alc_compatibility_range: CompatibilityRange
    validation_result: bool
    decision: RegistrationDecision
    asset_references: tuple[str, ...] = ()
    failed_validation_categories: tuple[str, ...] = ()
    policy_passed: bool = True
    compatibility_status: CompatibilityStatus = CompatibilityStatus.NOT_EVALUATED
    host_contract_version: str | None = None
    alc_version: str | None = None
    reproduction_references: tuple[str, ...] = ()
    superseded: bool = False

    def __post_init__(self) -> None:
        _validate_adoption_metadata(self.metadata)
        _required(str(self.registration_id), "registration_id")
        _required(str(self.pack_id), "pack_id")
        validate_semantic_version(self.immutable_version, "immutable_version")
        _required(self.content_digest, "content_digest")
        _required(str(self.signer_id), "signer_id")
        object.__setattr__(self, "decision", RegistrationDecision(self.decision))
        object.__setattr__(
            self, "compatibility_status", CompatibilityStatus(self.compatibility_status)
        )
        object.__setattr__(
            self,
            "asset_references",
            _adoption_references(self.asset_references, "asset_references"),
        )
        object.__setattr__(
            self,
            "failed_validation_categories",
            _adoption_references(
                self.failed_validation_categories, "failed_validation_categories"
            ),
        )
        object.__setattr__(
            self,
            "reproduction_references",
            _adoption_references(
                self.reproduction_references, "reproduction_references"
            ),
        )
        for value, name in (
            (self.host_contract_version, "host_contract_version"),
            (self.alc_version, "alc_version"),
        ):
            if value is not None:
                validate_semantic_version(value, name)
        if self.decision is RegistrationDecision.APPROVED and (
            not self.validation_result
            or not self.policy_passed
            or self.failed_validation_categories
        ):
            raise ValueError(
                "Approved registrations require complete validation and policy success."
            )
        if (
            self.decision is RegistrationDecision.REJECTED
            and self.validation_result
            and self.policy_passed
        ):
            raise ValueError(
                "Rejected registrations require a failed validation or policy decision."
            )
        if self.superseded and (
            self.host_contract_version is None or self.alc_version is None
        ):
            raise ValueError(
                "Superseded registrations require reproduction contract versions."
            )

    @property
    def identity_key(self) -> tuple[DomainPackId, str]:
        """Return the immutable uniqueness key for a pack registration."""
        return self.pack_id, self.immutable_version

    @property
    def registration_decision(self) -> RegistrationDecision:
        """Compatibility alias for callers using the long field name."""
        return self.decision


@dataclass(frozen=True, slots=True)
class InvocationAssociation:
    """Correlation-bearing association persisted before any node can start."""

    metadata: RecordMetadata
    invocation_id: InvocationId
    organization_id: OrganizationId
    domain_id: DomainId
    pack_version: str
    agent_id: AgentId
    workflow_id: str
    run_id: RunId
    correlation_id: CorrelationId

    def __post_init__(self) -> None:
        _validate_adoption_metadata(self.metadata)
        for value, name in (
            (str(self.invocation_id), "invocation_id"),
            (str(self.organization_id), "organization_id"),
            (str(self.domain_id), "domain_id"),
            (self.pack_version, "pack_version"),
            (str(self.agent_id), "agent_id"),
            (self.workflow_id, "workflow_id"),
            (str(self.run_id), "run_id"),
            (str(self.correlation_id), "correlation_id"),
        ):
            _required(value, name)
        validate_semantic_version(self.pack_version, "pack_version")
        if self.organization_id != self.metadata.organization_id:
            raise ValueError("Invocation organization must match record metadata.")
        if self.correlation_id != self.metadata.correlation_id:
            raise ValueError("Invocation correlation must match record metadata.")


class AuthorizationOutcome(StrEnum):
    """Fail-closed authorization result retained with its decision evidence."""

    ALLOWED = "allowed"
    DENIED = "denied"


@dataclass(frozen=True, slots=True)
class AuthorizationDecision:
    """Immutable authorization evidence with references instead of protected content."""

    metadata: RecordMetadata
    decision_id: AuthorizationDecisionId
    organization_id: OrganizationId
    domain_id: DomainId
    pack_version: str
    agent_id: AgentId
    capability: str
    scope: Mapping[str, object]
    outcome: AuthorizationOutcome
    reason: str | None = None
    evidence_references: tuple[str, ...] = ()
    recorded_at: datetime | None = None

    def __post_init__(self) -> None:
        _validate_adoption_metadata(self.metadata)
        for value, name in (
            (str(self.decision_id), "decision_id"),
            (str(self.organization_id), "organization_id"),
            (str(self.domain_id), "domain_id"),
            (self.pack_version, "pack_version"),
            (str(self.agent_id), "agent_id"),
            (self.capability, "capability"),
        ):
            _required(value, name)
        validate_semantic_version(self.pack_version, "pack_version")
        if self.organization_id != self.metadata.organization_id:
            raise ValueError("Authorization organization must match record metadata.")
        object.__setattr__(self, "scope", _frozen_mapping(self.scope))
        object.__setattr__(self, "outcome", AuthorizationOutcome(self.outcome))
        object.__setattr__(
            self,
            "evidence_references",
            _adoption_references(self.evidence_references, "evidence_references"),
        )
        if self.outcome is AuthorizationOutcome.DENIED:
            _required(self.reason or "", "reason")
        elif self.reason is not None:
            _required(self.reason, "reason")
        if self.recorded_at is not None:
            _timestamp(self.recorded_at, "recorded_at")

    @property
    def allowed(self) -> bool:
        """Return whether this decision authorizes the requested action."""
        return self.outcome is AuthorizationOutcome.ALLOWED


class AgentLifecycleStatus(StrEnum):
    """Lifecycle states for one agent declaration and its effective ALC."""

    CATALOGED = "cataloged"
    REGISTERED = "registered"
    ACTIVATION_ELIGIBLE = "activation_eligible"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    BLOCKED = "blocked"


@dataclass(frozen=True, slots=True)
class AgentLifecycle:
    """Immutable lifecycle evidence that makes learning activation explicit."""

    metadata: RecordMetadata
    lifecycle_id: AgentLifecycleId
    pack_id: DomainPackId
    immutable_version: str
    agent_id: AgentId
    status: AgentLifecycleStatus
    learning_required: bool
    effective_alc_version: str | None = None
    activation_evidence_references: tuple[str, ...] = ()
    change_references: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _validate_adoption_metadata(self.metadata)
        for value, name in (
            (str(self.lifecycle_id), "lifecycle_id"),
            (str(self.pack_id), "pack_id"),
            (self.immutable_version, "immutable_version"),
            (str(self.agent_id), "agent_id"),
        ):
            _required(value, name)
        validate_semantic_version(self.immutable_version, "immutable_version")
        if self.effective_alc_version is not None:
            validate_semantic_version(
                self.effective_alc_version, "effective_alc_version"
            )
        object.__setattr__(self, "status", AgentLifecycleStatus(self.status))
        for name in ("activation_evidence_references", "change_references"):
            object.__setattr__(
                self, name, _adoption_references(getattr(self, name), name)
            )
        if self.status is AgentLifecycleStatus.ACTIVE and self.learning_required:
            if self.effective_alc_version is None:
                raise ValueError(
                    "Active learning-required agents require exactly one effective ALC."
                )
            if not self.activation_evidence_references:
                raise ValueError(
                    "Active learning-required agents require activation evidence."
                )


class WorkflowActivationStatus(StrEnum):
    """Release lifecycle state for a workflow version."""

    CATALOGED = "cataloged"
    REGISTERED = "registered"
    ACTIVATION_ELIGIBLE = "activation_eligible"
    ACTIVE = "active"
    BLOCKED = "blocked"


@dataclass(frozen=True, slots=True)
class WorkflowActivation:
    """Immutable workflow activation decision guarded by eligibility and approval."""

    metadata: RecordMetadata
    activation_id: WorkflowActivationId
    pack_id: DomainPackId
    immutable_version: str
    workflow_id: str
    status: WorkflowActivationStatus
    activation_eligible: bool
    explicit_activation_approval: bool = False
    compatibility_status: CompatibilityStatus = CompatibilityStatus.NOT_EVALUATED
    evidence_references: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _validate_adoption_metadata(self.metadata)
        for value, name in (
            (str(self.activation_id), "activation_id"),
            (str(self.pack_id), "pack_id"),
            (self.immutable_version, "immutable_version"),
            (self.workflow_id, "workflow_id"),
        ):
            _required(value, name)
        validate_semantic_version(self.immutable_version, "immutable_version")
        object.__setattr__(self, "status", WorkflowActivationStatus(self.status))
        object.__setattr__(
            self, "compatibility_status", CompatibilityStatus(self.compatibility_status)
        )
        object.__setattr__(
            self,
            "evidence_references",
            _adoption_references(self.evidence_references, "evidence_references"),
        )
        if self.status is WorkflowActivationStatus.ACTIVE and (
            not self.activation_eligible
            or not self.explicit_activation_approval
            or self.compatibility_status is CompatibilityStatus.INCOMPATIBLE
        ):
            raise ValueError(
                "Active workflows require eligibility, approval, and compatibility."
            )
        if self.activation_eligible and self.status not in {
            WorkflowActivationStatus.ACTIVATION_ELIGIBLE,
            WorkflowActivationStatus.ACTIVE,
        }:
            raise ValueError(
                "Activation eligibility must be represented by an eligible status."
            )


class MigrationPhaseStatus(StrEnum):
    """Evidence-gated migration phase state."""

    PLANNED = "planned"
    RUNNING = "running"
    COMPLETE = "complete"
    ROLLED_BACK = "rolled_back"


@dataclass(frozen=True, slots=True)
class MigrationPhase:
    """Immutable migration phase scope, gates, reviews, and rollback procedure."""

    metadata: RecordMetadata
    phase_id: MigrationPhaseId
    phase_scope: tuple[str, ...]
    required_evidence_references: tuple[str, ...]
    exit_criteria_references: tuple[str, ...]
    rollback_procedure_reference: str
    host_owner_review_reference: str
    va_owner_review_reference: str
    status: MigrationPhaseStatus = MigrationPhaseStatus.PLANNED

    def __post_init__(self) -> None:
        _validate_adoption_metadata(self.metadata)
        _required(str(self.phase_id), "phase_id")
        _required(self.rollback_procedure_reference, "rollback_procedure_reference")
        _required(self.host_owner_review_reference, "host_owner_review_reference")
        _required(self.va_owner_review_reference, "va_owner_review_reference")
        object.__setattr__(self, "status", MigrationPhaseStatus(self.status))
        for name in (
            "phase_scope",
            "required_evidence_references",
            "exit_criteria_references",
        ):
            object.__setattr__(
                self,
                name,
                _adoption_references(getattr(self, name), name, required=True),
            )


@dataclass(frozen=True, slots=True)
class SourceIndexEntry:
    """Immutable inventory evidence for one source asset and its disposition."""

    metadata: RecordMetadata
    entry_id: SourceIndexEntryId
    asset_reference: str
    asset_hash: str
    owner_reference: str
    license_or_consent_classification: str
    disposition: str

    def __post_init__(self) -> None:
        _validate_adoption_metadata(self.metadata)
        for value, name in (
            (str(self.entry_id), "entry_id"),
            (self.asset_reference, "asset_reference"),
            (self.asset_hash, "asset_hash"),
            (self.owner_reference, "owner_reference"),
            (
                self.license_or_consent_classification,
                "license_or_consent_classification",
            ),
            (self.disposition, "disposition"),
        ):
            _required(value, name)


class VerificationCoverageStatus(StrEnum):
    """Integration coverage state used by release decisions."""

    INCOMPLETE = "incomplete"
    COMPLETE = "complete"


@dataclass(frozen=True, slots=True)
class VerificationRun:
    """Immutable verification evidence for a stated pack and contract version set."""

    metadata: RecordMetadata
    verification_run_id: VerificationRunId
    pack_id: DomainPackId
    immutable_version: str
    pack_contract_version: str
    host_contract_version: str
    alc_version: str
    schema_evidence_references: tuple[str, ...]
    unit_evidence_references: tuple[str, ...]
    property_evidence_references: tuple[str, ...]
    integration_evidence_references: tuple[str, ...]
    coverage_status: VerificationCoverageStatus
    fixed_seed: str
    fixture_digest: str
    failure_evidence_references: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _validate_adoption_metadata(self.metadata)
        for value, name in (
            (str(self.verification_run_id), "verification_run_id"),
            (str(self.pack_id), "pack_id"),
            (self.immutable_version, "immutable_version"),
            (self.pack_contract_version, "pack_contract_version"),
            (self.host_contract_version, "host_contract_version"),
            (self.alc_version, "alc_version"),
            (self.fixed_seed, "fixed_seed"),
            (self.fixture_digest, "fixture_digest"),
        ):
            _required(value, name)
        for name in (
            "immutable_version",
            "pack_contract_version",
            "host_contract_version",
            "alc_version",
        ):
            validate_semantic_version(getattr(self, name), name)
        object.__setattr__(
            self, "coverage_status", VerificationCoverageStatus(self.coverage_status)
        )
        for name in (
            "schema_evidence_references",
            "unit_evidence_references",
            "property_evidence_references",
            "integration_evidence_references",
            "failure_evidence_references",
        ):
            object.__setattr__(
                self, name, _adoption_references(getattr(self, name), name)
            )


class ReleaseReadinessStatus(StrEnum):
    """Terminal readiness outcome retained for one release evaluation."""

    ELIGIBLE = "eligible"
    BLOCKED = "blocked"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class ReleaseReadinessDecision:
    """Immutable release decision that never mutates the version it evaluates."""

    metadata: RecordMetadata
    decision_id: ReleaseReadinessDecisionId
    pack_id: DomainPackId
    immutable_version: str
    workflow_id: str
    status: ReleaseReadinessStatus
    integration_coverage_complete: bool
    evidence_references: tuple[str, ...]
    unmet_gate_references: tuple[str, ...] = ()
    failure_evidence_references: tuple[str, ...] = ()
    terminal: bool = True

    def __post_init__(self) -> None:
        _validate_adoption_metadata(self.metadata)
        for value, name in (
            (str(self.decision_id), "decision_id"),
            (str(self.pack_id), "pack_id"),
            (self.immutable_version, "immutable_version"),
            (self.workflow_id, "workflow_id"),
        ):
            _required(value, name)
        validate_semantic_version(self.immutable_version, "immutable_version")
        object.__setattr__(self, "status", ReleaseReadinessStatus(self.status))
        object.__setattr__(
            self,
            "evidence_references",
            _adoption_references(
                self.evidence_references, "evidence_references", required=True
            ),
        )
        for name in ("unmet_gate_references", "failure_evidence_references"):
            object.__setattr__(
                self, name, _adoption_references(getattr(self, name), name)
            )
        if not self.terminal:
            raise ValueError("Release readiness decisions must be terminal records.")
        if self.status is not ReleaseReadinessStatus.ELIGIBLE and not (
            self.unmet_gate_references or self.failure_evidence_references
        ):
            raise ValueError(
                "Blocked or failed release decisions require failure evidence."
            )


class RecoveryActionStatus(StrEnum):
    """Evidence-gated recovery state."""

    APPROVED = "approved"
    HALTED = "halted"
    RESTORED = "restored"


@dataclass(frozen=True, slots=True)
class RecoveryAction:
    """Immutable, target-exact restoration evidence for one approved recovery."""

    metadata: RecordMetadata
    recovery_action_id: RecoveryActionId
    pack_id: DomainPackId
    designated_immutable_version: str
    status: RecoveryActionStatus
    approval_reference: str
    investigation_evidence_references: tuple[str, ...]
    restored_immutable_version: str | None = None

    def __post_init__(self) -> None:
        _validate_adoption_metadata(self.metadata)
        for value, name in (
            (str(self.recovery_action_id), "recovery_action_id"),
            (str(self.pack_id), "pack_id"),
            (self.designated_immutable_version, "designated_immutable_version"),
            (self.approval_reference, "approval_reference"),
        ):
            _required(value, name)
        validate_semantic_version(
            self.designated_immutable_version, "designated_immutable_version"
        )
        object.__setattr__(self, "status", RecoveryActionStatus(self.status))
        _required(self.approval_reference, "approval_reference")
        object.__setattr__(
            self,
            "investigation_evidence_references",
            _adoption_references(
                self.investigation_evidence_references,
                "investigation_evidence_references",
            ),
        )
        if self.restored_immutable_version is not None:
            validate_semantic_version(
                self.restored_immutable_version, "restored_immutable_version"
            )
        if self.status is RecoveryActionStatus.RESTORED:
            if not self.investigation_evidence_references:
                raise ValueError(
                    "Restored recovery actions require prior-version investigation evidence."
                )
            if self.restored_immutable_version != self.designated_immutable_version:
                raise ValueError(
                    "Recovery must restore the designated immutable version."
                )


class MaturityLevel(StrEnum):
    """Distinct operational evidence levels for one agent."""

    CATALOGED = "cataloged"
    REGISTERED = "registered"
    ACTIVE = "active"
    PRODUCTION_PROVEN = "production_proven"


@dataclass(frozen=True, slots=True)
class MaturityState:
    """Independent maturity evidence retained per agent and immutable pack version."""

    metadata: RecordMetadata
    maturity_state_id: MaturityStateId
    pack_id: DomainPackId
    immutable_version: str
    agent_id: AgentId
    level: MaturityLevel
    evidence_references: tuple[str, ...]
    pack_operational: bool = True

    def __post_init__(self) -> None:
        _validate_adoption_metadata(self.metadata)
        for value, name in (
            (str(self.maturity_state_id), "maturity_state_id"),
            (str(self.pack_id), "pack_id"),
            (self.immutable_version, "immutable_version"),
            (str(self.agent_id), "agent_id"),
        ):
            _required(value, name)
        validate_semantic_version(self.immutable_version, "immutable_version")
        object.__setattr__(self, "level", MaturityLevel(self.level))
        object.__setattr__(
            self,
            "evidence_references",
            _adoption_references(
                self.evidence_references, "evidence_references", required=True
            ),
        )

    @property
    def identity_key(self) -> tuple[DomainPackId, str, AgentId]:
        """Return the independent per-agent maturity key."""
        return self.pack_id, self.immutable_version, self.agent_id


# Specification terminology aliases retain the repository's CamelCase API.
Registration_Record = Registration
Improvement_Proposal = ImprovementProposal
Invocation_Association = InvocationAssociation
Authorization_Decision = AuthorizationDecision
Artifact_Handoff = ArtifactHandoff
Agent_Lifecycle = AgentLifecycle
Workflow_Activation = WorkflowActivation
Migration_Phase = MigrationPhase
Source_Index_Entry = SourceIndexEntry
Verification_Run = VerificationRun
Release_Readiness_Decision = ReleaseReadinessDecision
Recovery_Action = RecoveryAction
Maturity_State = MaturityState
