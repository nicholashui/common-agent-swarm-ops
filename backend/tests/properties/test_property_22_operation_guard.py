"""Property tests for atomic multi-operation production delivery limits."""

from __future__ import annotations

from datetime import UTC, datetime

from hypothesis import given, settings, strategies as st

from app.governance.operation_guard import OperationGuard
from app.models.operations import (
    OperationDecisionStatus,
    OperationKind,
    ProhibitedOperationReason,
    RecordedAuthorization,
    RequestedOperation,
)

# Feature: generic-swarm-business-os, Property 22: Multi-operation production guard is atomic
# yet isolates safe operations.
# **Validates: Requirements 10.3, 10.4, 10.6**

_AUTHORIZATION = RecordedAuthorization("approval-22", datetime(2025, 1, 1, tzinfo=UTC))
_SAFE_VARIANTS = (
    "production_other",
    "manual_promotion",
    "nonproduction_rewrite",
    "authorized_orchestration",
)
_SAFE_VARIANT_LIST = st.lists(st.sampled_from(_SAFE_VARIANTS), min_size=1, max_size=4)
_PROHIBITED_REASON_LIST = st.lists(
    st.sampled_from(tuple(ProhibitedOperationReason)), min_size=1, max_size=4
)


def _safe_operation(operation_id: str, variant: str) -> RequestedOperation:
    if variant == "production_other":
        return RequestedOperation(operation_id, OperationKind.OTHER, targets_production=True)
    if variant == "manual_promotion":
        return RequestedOperation(operation_id, OperationKind.PRODUCTION_PROMOTION, True, False)
    if variant == "nonproduction_rewrite":
        return RequestedOperation(operation_id, OperationKind.HOST_CODE_REWRITE)
    if variant == "authorized_orchestration":
        return RequestedOperation(
            operation_id,
            OperationKind.ORCHESTRATION,
            targets_production=True,
            recorded_authorization=_AUTHORIZATION,
        )
    raise AssertionError(f"Unexpected safe operation variant: {variant}")


def _prohibited_operation(
    operation_id: str, reason: ProhibitedOperationReason
) -> RequestedOperation:
    if reason is ProhibitedOperationReason.AUTOMATIC_PRODUCTION_PROMOTION:
        return RequestedOperation(operation_id, OperationKind.PRODUCTION_PROMOTION, True, True)
    if reason is ProhibitedOperationReason.PRODUCTION_HOST_CODE_REWRITE:
        return RequestedOperation(operation_id, OperationKind.HOST_CODE_REWRITE, True)
    if reason is ProhibitedOperationReason.UNBOUNDED_ORCHESTRATION:
        return RequestedOperation(
            operation_id,
            OperationKind.ORCHESTRATION,
            bounded=False,
            recorded_authorization=_AUTHORIZATION,
        )
    return RequestedOperation(operation_id, OperationKind.ORCHESTRATION)


@settings(max_examples=100, deadline=None)
@given(
    safe_variants=_SAFE_VARIANT_LIST,
    prohibited_reasons=_PROHIBITED_REASON_LIST,
    prohibited_first=st.booleans(),
)
def test_mixed_requests_are_atomic_and_report_each_prohibited_operation(
    safe_variants: list[str],
    prohibited_reasons: list[ProhibitedOperationReason],
    prohibited_first: bool,
) -> None:
    """Any prohibition cancels every safe operation while retaining each typed denial."""
    safe_operations = tuple(
        _safe_operation(f"safe-{index}", variant)
        for index, variant in enumerate(safe_variants)
    )
    prohibited_operations = tuple(
        _prohibited_operation(f"prohibited-{index}", reason)
        for index, reason in enumerate(prohibited_reasons)
    )
    operations = (
        (*prohibited_operations, *safe_operations)
        if prohibited_first
        else (*safe_operations, *prohibited_operations)
    )

    assessment = OperationGuard().assess(operations)

    assert assessment.production_changes_blocked
    assert not assessment.permits_any_operation
    assert assessment.prohibited_error is not None
    assert tuple(
        (item.operation_id, item.reason)
        for item in assessment.prohibited_error.prohibited_operations
    ) == tuple(
        (operation.operation_id, reason)
        for operation, reason in zip(prohibited_operations, prohibited_reasons, strict=True)
    )
    assert tuple(decision.status for decision in assessment.decisions) == tuple(
        (
            OperationDecisionStatus.PROHIBITED
            if operation.operation_id.startswith("prohibited-")
            else OperationDecisionStatus.CANCELLED_BY_PROHIBITED_OPERATION
        )
        for operation in operations
    )


@settings(max_examples=100, deadline=None)
@given(error_message=st.text(min_size=1, max_size=32))
def test_safe_operation_errors_do_not_prevent_authorized_production_eligibility(
    error_message: str,
) -> None:
    """A later error from a separate safe operation does not become a guard prohibition."""
    authorized_production = RequestedOperation(
        "authorized-production",
        OperationKind.ORCHESTRATION,
        targets_production=True,
        recorded_authorization=_AUTHORIZATION,
    )
    separate_safe_operation = RequestedOperation("safe-error", OperationKind.OTHER)
    downstream_error = RuntimeError(error_message)

    assessment = OperationGuard().assess((authorized_production, separate_safe_operation))

    assert str(downstream_error) == error_message
    assert assessment.prohibited_error is None
    assert assessment.permits_any_operation
    assert tuple(decision.status for decision in assessment.decisions) == (
        OperationDecisionStatus.PERMITTED,
        OperationDecisionStatus.PERMITTED,
    )


@settings(max_examples=100, deadline=None)
@given(
    reason=st.sampled_from(tuple(ProhibitedOperationReason)),
    delivery_mode=st.sampled_from(("returns_false", "raises")),
)
def test_failed_prohibited_error_delivery_latches_later_production_changes(
    reason: ProhibitedOperationReason,
    delivery_mode: str,
) -> None:
    """Undelivered typed denials permanently block later production changes."""
    guard = OperationGuard()

    def deliver_error(_: object) -> bool:
        if delivery_mode == "raises":
            raise RuntimeError("delivery failed")
        return False

    delivery = guard.assess_and_deliver_prohibited_error(
        (_prohibited_operation("prohibited", reason),), deliver_error
    )
    later = guard.assess(
        (
            RequestedOperation("later-production", OperationKind.OTHER, targets_production=True),
            RequestedOperation("later-nonproduction", OperationKind.OTHER),
        )
    )

    assert delivery.error_delivered is False
    assert delivery.assessment.production_changes_blocked
    assert delivery.assessment.production_change_block is not None
    assert tuple(decision.status for decision in later.decisions) == (
        OperationDecisionStatus.BLOCKED_BY_PRODUCTION_LATCH,
        OperationDecisionStatus.PERMITTED,
    )
