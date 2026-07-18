"""Typed, redaction-safe error-contract unit tests."""

from datetime import UTC, datetime

from app.core.errors import AdoptionAuthorizationError, BoundaryErrorCode, BoundaryViolationError
from app.governance.operation_guard import OperationGuard
from app.models.operations import (
    OperationDecisionStatus,
    OperationKind,
    ProhibitedOperationError,
    ProhibitedOperationReason,
    RecordedAuthorization,
    RequestedOperation,
)


def test_boundary_error_types_expose_stable_redacted_details() -> None:
    """Boundary exceptions retain machine-readable codes without public operation data."""
    error = BoundaryViolationError(BoundaryErrorCode.INVALID_OPERATION, "unknown", "Invalid.")
    approval_error = AdoptionAuthorizationError()

    assert isinstance(error, PermissionError)
    assert error.to_public_detail() == {
        "code": BoundaryErrorCode.INVALID_OPERATION,
        "message": "Invalid.",
    }
    assert "operation" not in error.to_public_detail()
    assert isinstance(approval_error, BoundaryViolationError)
    assert approval_error.code is BoundaryErrorCode.ADOPTION_APPROVAL_REQUIRED
    assert approval_error.operation == "adopt"


def test_prohibited_operation_errors_are_typed_and_failed_delivery_blocks_production() -> None:
    """Every delivery-limit denial returns the typed response and fails closed on delivery loss."""
    authorization = RecordedAuthorization("approval-1", datetime.now(UTC))
    cases = (
        (
            RequestedOperation("auto", OperationKind.PRODUCTION_PROMOTION, True, True),
            ProhibitedOperationReason.AUTOMATIC_PRODUCTION_PROMOTION,
        ),
        (
            RequestedOperation("rewrite", OperationKind.HOST_CODE_REWRITE, True),
            ProhibitedOperationReason.PRODUCTION_HOST_CODE_REWRITE,
        ),
        (
            RequestedOperation(
                "unbounded",
                OperationKind.ORCHESTRATION,
                bounded=False,
                recorded_authorization=authorization,
            ),
            ProhibitedOperationReason.UNBOUNDED_ORCHESTRATION,
        ),
        (
            RequestedOperation("read-only", OperationKind.ORCHESTRATION),
            ProhibitedOperationReason.MISSING_ORCHESTRATION_AUTHORIZATION,
        ),
    )
    for operation, reason in cases:
        assessment = OperationGuard().assess((operation,))
        assert isinstance(assessment.prohibited_error, ProhibitedOperationError)
        assert assessment.prohibited_error.to_public_detail()["operations"] == (
            {"operation_id": operation.operation_id, "reason": reason},
        )
        assert assessment.decisions[0].status is OperationDecisionStatus.PROHIBITED

    guard = OperationGuard()
    delivery = guard.assess_and_deliver_prohibited_error((cases[0][0],), lambda _: False)
    later = guard.assess(
        (RequestedOperation("safe", OperationKind.OTHER, targets_production=True),)
    )
    assert delivery.error_delivered is False
    assert delivery.assessment.production_changes_blocked
    assert later.decisions[0].status is OperationDecisionStatus.BLOCKED_BY_PRODUCTION_LATCH
