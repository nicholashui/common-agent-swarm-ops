"""Fail-closed per-operation production delivery-limit controls."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from threading import RLock

from app.models.common import utc_now
from app.models.operations import (
    OperationClassification,
    OperationDecision,
    OperationDecisionStatus,
    OperationGuardAssessment,
    OperationKind,
    ProductionChangeBlock,
    ProductionChangeBlockReason,
    ProhibitedOperation,
    ProhibitedOperationError,
    ProhibitedOperationReason,
    RequestedOperation,
)


class ProductionChangeBlockLatch:
    """One-way, thread-safe latch that prevents subsequent production changes."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._block: ProductionChangeBlock | None = None

    def snapshot(self) -> ProductionChangeBlock | None:
        """Return the immutable current block state, if the latch was tripped."""
        with self._lock:
            return self._block

    def trip(
        self,
        reason: ProductionChangeBlockReason,
    ) -> ProductionChangeBlock:
        """Atomically trip the latch, retaining the first fail-closed cause."""
        with self._lock:
            if self._block is None:
                self._block = ProductionChangeBlock(reason=reason, blocked_at=utc_now())
            return self._block


@dataclass(frozen=True, slots=True)
class ProhibitedErrorDeliveryResult:
    """The result of delivering a prohibited-operation response."""

    assessment: OperationGuardAssessment
    error_delivered: bool | None


class OperationGuard:
    """Classify every request operation before any production change can begin."""

    def __init__(self, latch: ProductionChangeBlockLatch | None = None) -> None:
        self._lock = RLock()
        self._latch = latch or ProductionChangeBlockLatch()

    @property
    def latch(self) -> ProductionChangeBlockLatch:
        """Expose the shared one-way production-change latch."""
        return self._latch


    def assess(self, operations: Iterable[RequestedOperation]) -> OperationGuardAssessment:
        """Atomically classify all operations before a caller starts production work."""
        with self._lock:
            return self._assess_locked(tuple(operations))

    def assess_and_deliver_prohibited_error(
        self,
        operations: Iterable[RequestedOperation],
        deliver_error: Callable[[ProhibitedOperationError], bool],
    ) -> ProhibitedErrorDeliveryResult:
        """Assess a request and trip the latch if its denial cannot be delivered.

        The evaluation, response delivery result, and latch transition share one lock.
        Therefore another caller cannot receive a production-permitting assessment
        between a failed prohibited-error delivery and the fail-closed latch trip.
        """
        with self._lock:
            assessment = self._assess_locked(tuple(operations))
            error = assessment.prohibited_error
            if error is None:
                return ProhibitedErrorDeliveryResult(assessment, None)
            try:
                delivered = deliver_error(error)
            except Exception:
                delivered = False
            if not delivered:
                assessment = OperationGuardAssessment(
                    decisions=assessment.decisions,
                    prohibited_error=error,
                    production_change_block=self._latch.trip(
                        ProductionChangeBlockReason.PROHIBITED_ERROR_DELIVERY_FAILED
                    ),
                )
            return ProhibitedErrorDeliveryResult(assessment, delivered)

    def _assess_locked(
        self,
        operations: tuple[RequestedOperation, ...],
    ) -> OperationGuardAssessment:
        classifications = tuple(self._classify(operation) for operation in operations)
        prohibited = tuple(
            ProhibitedOperation(item.operation_id, item.prohibition)
            for item in classifications
            if item.prohibition is not None
        )
        if prohibited:
            return OperationGuardAssessment(
                decisions=tuple(
                    OperationDecision(
                        classification,
                        (
                            OperationDecisionStatus.PROHIBITED
                            if classification.is_prohibited
                            else OperationDecisionStatus.CANCELLED_BY_PROHIBITED_OPERATION
                        ),
                    )
                    for classification in classifications
                ),
                prohibited_error=ProhibitedOperationError(prohibited),
            )

        block = self._latch.snapshot()
        return OperationGuardAssessment(
            decisions=tuple(
                OperationDecision(
                    classification,
                    (
                        OperationDecisionStatus.BLOCKED_BY_PRODUCTION_LATCH
                        if block is not None and operation.targets_production
                        else OperationDecisionStatus.PERMITTED
                    ),
                )
                for operation, classification in zip(operations, classifications, strict=True)
            ),
            production_change_block=block,
        )

    @staticmethod
    def _classify(operation: RequestedOperation) -> OperationClassification:
        prohibitions: list[ProhibitedOperationReason] = []
        if (
            operation.kind is OperationKind.PRODUCTION_PROMOTION
            and operation.targets_production
            and operation.automatic
        ):
            prohibitions.append(ProhibitedOperationReason.AUTOMATIC_PRODUCTION_PROMOTION)
        if operation.kind is OperationKind.HOST_CODE_REWRITE and operation.targets_production:
            prohibitions.append(ProhibitedOperationReason.PRODUCTION_HOST_CODE_REWRITE)
        if operation.kind is OperationKind.ORCHESTRATION:
            if not operation.bounded:
                prohibitions.append(ProhibitedOperationReason.UNBOUNDED_ORCHESTRATION)
            if (
                operation.recorded_authorization is None
                or not operation.recorded_authorization.is_recorded_approval
            ):
                prohibitions.append(
                    ProhibitedOperationReason.MISSING_ORCHESTRATION_AUTHORIZATION
                )
        return OperationClassification(
            operation_id=operation.operation_id,
            prohibition=prohibitions[0] if prohibitions else None,
        )
