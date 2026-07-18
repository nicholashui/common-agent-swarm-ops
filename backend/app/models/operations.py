"""Typed operation-request contracts for production-change governance."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class OperationKind(StrEnum):
    """Operation categories evaluated by the delivery-limit guard."""

    PRODUCTION_PROMOTION = "production_promotion"
    HOST_CODE_REWRITE = "host_code_rewrite"
    ORCHESTRATION = "orchestration"
    OTHER = "other"


class ProhibitedOperationReason(StrEnum):
    """Stable, redaction-safe reasons that an operation is prohibited."""

    AUTOMATIC_PRODUCTION_PROMOTION = "automatic_production_promotion"
    PRODUCTION_HOST_CODE_REWRITE = "production_host_code_rewrite"
    UNBOUNDED_ORCHESTRATION = "unbounded_orchestration"
    MISSING_ORCHESTRATION_AUTHORIZATION = "missing_orchestration_authorization"


class OperationDecisionStatus(StrEnum):
    """The operation-specific result of a guard evaluation."""

    PERMITTED = "permitted"
    PROHIBITED = "prohibited"
    CANCELLED_BY_PROHIBITED_OPERATION = "cancelled_by_prohibited_operation"
    BLOCKED_BY_PRODUCTION_LATCH = "blocked_by_production_latch"


class ProductionChangeBlockReason(StrEnum):
    """Irreversible reasons a production-change latch has been tripped."""

    PROHIBITED_ERROR_DELIVERY_FAILED = "prohibited_error_delivery_failed"


@dataclass(frozen=True, slots=True)
class RecordedAuthorization:
    """A human authorization record required before orchestration may proceed."""

    record_id: str
    recorded_at: datetime
    approved: bool = True

    @property
    def is_recorded_approval(self) -> bool:
        """Return whether this is a complete affirmative recorded authorization."""
        return (
            self.approved
            and bool(self.record_id.strip())
            and self.recorded_at.tzinfo is not None
        )


@dataclass(frozen=True, slots=True)
class RequestedOperation:
    """One independently classified request operation.

    Authorization for ordinary safe operations is enforced by the Host tool broker.
    This guard uses ``recorded_authorization`` only for the delivery-limit rule that
    forbids every unrecorded orchestration request, including read-only work.
    """

    operation_id: str
    kind: OperationKind
    targets_production: bool = False
    automatic: bool = False
    bounded: bool = True
    recorded_authorization: RecordedAuthorization | None = None


@dataclass(frozen=True, slots=True)
class OperationClassification:
    """The prohibited-operation result for one requested operation."""

    operation_id: str
    prohibition: ProhibitedOperationReason | None = None

    @property
    def is_prohibited(self) -> bool:
        """Return whether this operation matches a delivery-limit prohibition."""
        return self.prohibition is not None


@dataclass(frozen=True, slots=True)
class ProhibitedOperation:
    """A safe-to-return summary of one prohibited requested operation."""

    operation_id: str
    reason: ProhibitedOperationReason


@dataclass(frozen=True, slots=True)
class ProhibitedOperationError:
    """The redaction-safe response required when a request contains a prohibition."""

    prohibited_operations: tuple[ProhibitedOperation, ...]
    code: str = "prohibited_operation"
    message: str = "The request contains one or more prohibited operations."

    def __post_init__(self) -> None:
        if not self.prohibited_operations:
            raise ValueError("A prohibited-operation error requires a prohibited operation.")

    def to_public_detail(self) -> dict[str, object]:
        """Return a serializable response without untrusted operation payloads."""
        return {
            "code": self.code,
            "message": self.message,
            "operations": tuple(
                {"operation_id": item.operation_id, "reason": item.reason}
                for item in self.prohibited_operations
            ),
        }


@dataclass(frozen=True, slots=True)
class ProductionChangeBlock:
    """Immutable evidence that the one-way production safety latch was tripped."""

    reason: ProductionChangeBlockReason
    blocked_at: datetime


@dataclass(frozen=True, slots=True)
class OperationDecision:
    """The execution eligibility of a single operation after request evaluation."""

    classification: OperationClassification
    status: OperationDecisionStatus


@dataclass(frozen=True, slots=True)
class OperationGuardAssessment:
    """An atomic request assessment with independent per-operation decisions."""

    decisions: tuple[OperationDecision, ...]
    prohibited_error: ProhibitedOperationError | None = None
    production_change_block: ProductionChangeBlock | None = None

    @property
    def permits_any_operation(self) -> bool:
        """Return whether any requested operation remains eligible for handling."""
        return any(
            decision.status is OperationDecisionStatus.PERMITTED
            for decision in self.decisions
        )

    @property
    def production_changes_blocked(self) -> bool:
        """Return whether this request must not make a production change."""
        return self.prohibited_error is not None or self.production_change_block is not None
