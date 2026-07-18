"""Immutable sandbox-only evolution records."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import NewType

from app.models.common import RecordMetadata
from app.models.identifiers import ActorId, OrganizationId

SandboxVariantId = NewType("SandboxVariantId", str)
RollbackRecordId = NewType("RollbackRecordId", str)
CanaryId = NewType("CanaryId", str)
PromotionAssessmentId = NewType("PromotionAssessmentId", str)
PromotionApprovalId = NewType("PromotionApprovalId", str)


class ImprovementDirection(StrEnum):
    """Configured direction for a target metric."""

    INCREASE = "increase"
    DECREASE = "decrease"


class SandboxVariantState(StrEnum):
    """Lifecycle state of an immutable sandbox proposal."""

    DRAFT = "draft"
    UNDER_CONSIDERATION = "under_consideration"
    WITHDRAWN = "withdrawn"


class RollbackStatus(StrEnum):
    """Status of the predeclared rollback plan."""

    PLANNED = "planned"
    PERFORMED = "performed"


class CanaryState(StrEnum):
    """Explicit canary lifecycle states; approval never activates a canary."""

    APPROVED = "approved"
    ACTIVE = "active"
    STOPPED = "stopped"


class PromotionDecision(StrEnum):
    """Assessment result; this never applies a production change."""

    BLOCKED = "blocked"
    PERMITTED = "permitted"


@dataclass(frozen=True, slots=True)
class CanaryScope:
    """A narrow organization/workflow/case scope for one canary."""

    organization_id: OrganizationId
    workflow_id: str | None = None
    case_id: str | None = None

    def contains(self, requested: CanaryScope) -> bool:
        """Return whether a requested operation stays inside this approved scope."""
        return (
            self.organization_id == requested.organization_id
            and (self.workflow_id is None or self.workflow_id == requested.workflow_id)
            and (self.case_id is None or self.case_id == requested.case_id)
        )


@dataclass(frozen=True, slots=True)
class SandboxVariant:
    """Detached configuration proposal; production is referenced only by a digest."""

    metadata: RecordMetadata
    variant_id: SandboxVariantId
    production_baseline_digest: str
    sandbox_configuration_digest: str
    sandbox_configuration_json: str
    target_metric: str
    improvement_direction: ImprovementDirection
    state: SandboxVariantState


@dataclass(frozen=True, slots=True)
class RollbackRecord:
    """A predeclared rollback plan and any evidence that it was performed."""

    metadata: RecordMetadata
    rollback_record_id: RollbackRecordId
    variant_id: SandboxVariantId
    plan_digest: str
    status: RollbackStatus
    performed_at: datetime | None = None
    failure_evidence: str | None = None


@dataclass(frozen=True, slots=True)
class CanaryCriterionResult:
    """Immutable evidence outcome for one named canary criterion."""

    criterion: str
    passed: bool
    evidence_reference: str
    recorded_at: datetime


@dataclass(frozen=True, slots=True)
class CanaryRecord:
    """A human-approved canary that is inert until explicitly activated."""

    metadata: RecordMetadata
    canary_id: CanaryId
    variant_id: SandboxVariantId
    scope: CanaryScope
    criteria: tuple[str, ...]
    criterion_results: tuple[CanaryCriterionResult, ...]
    rollback_record_id: RollbackRecordId
    state: CanaryState
    approved_by: ActorId
    approved_at: datetime


@dataclass(frozen=True, slots=True)
class MetricComparison:
    """Observed baseline and candidate values for one favorable metric."""

    baseline: float
    candidate: float


@dataclass(frozen=True, slots=True)
class PromotionApprovalRecord:
    """Human approval retained separately from an assessment decision."""

    metadata: RecordMetadata
    approval_id: PromotionApprovalId
    variant_id: SandboxVariantId
    actor_id: ActorId
    reason: str
    approved_at: datetime


@dataclass(frozen=True, slots=True)
class PromotionCondition:
    """One explicitly retained promotion requirement outcome."""

    name: str
    passed: bool
    evidence_references: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class PromotionAssessment:
    """An immutable fail-closed decision record that never applies a proposal."""

    metadata: RecordMetadata
    assessment_id: PromotionAssessmentId
    candidate_variant_id: SandboxVariantId | None
    candidate_count: int
    evaluation_run_id: str | None
    target_metric: MetricComparison
    safety: MetricComparison
    compliance: MetricComparison
    conditions: tuple[PromotionCondition, ...]
    missing_or_failed_conditions: tuple[str, ...]
    decision: PromotionDecision
    production_applied: bool = False
