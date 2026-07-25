"""Property checks for VA activation evidence and explicit approval."""

# The required specification comment exceeds the repository's line-length limit.
# ruff: noqa: E501
from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from hypothesis import example, given, settings, strategies as st

from app.engines.migration import MigrationController
from app.evaluation.migration_evidence import (
    InMemoryMigrationEvidenceRepository,
    MigrationEvidenceService,
    WorkflowActivationEvidence,
    WorkflowActivationStatus,
)
from app.models.identifiers import CorrelationId

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_APPROVAL_STATES = ("absent", "pending", "denied", "approved")
_MATURITY_LEVELS = ("cataloged", "registered", "active", "production-proven")


@dataclass(frozen=True, slots=True)
class VAActivationCase:
    """Bounded activation evidence and approval-state variations."""

    case_id: int
    domain_evaluations: tuple[bool, ...]
    reproducible_trace: bool
    human_approvals: tuple[bool, ...]
    maturity_level: str
    designated_approval_evaluation: bool
    approval_state: str


def _complete_case(case_id: int, approval_state: str) -> VAActivationCase:
    """Build a complete evidence vector for explicit approval edge cases."""
    return VAActivationCase(
        case_id=case_id,
        domain_evaluations=(True,),
        reproducible_trace=True,
        human_approvals=(True,),
        maturity_level="production-proven",
        designated_approval_evaluation=True,
        approval_state=approval_state,
    )


@st.composite
def _activation_cases(draw: st.DrawFn) -> VAActivationCase:
    """Generate the evidence conjunction and independent approval branches."""
    return VAActivationCase(
        case_id=draw(st.integers(min_value=0, max_value=10_000)),
        domain_evaluations=tuple(draw(st.lists(st.booleans(), min_size=0, max_size=3))),
        reproducible_trace=draw(st.booleans()),
        human_approvals=tuple(draw(st.lists(st.booleans(), min_size=0, max_size=3))),
        maturity_level=draw(st.sampled_from(_MATURITY_LEVELS)),
        designated_approval_evaluation=draw(st.booleans()),
        approval_state=draw(st.sampled_from(_APPROVAL_STATES)),
    )


def _evidence(case: VAActivationCase, workflow_id: str) -> WorkflowActivationEvidence:
    """Build the deterministic workflow evidence record under test."""
    return WorkflowActivationEvidence(
        workflow_id=workflow_id,
        domain_evaluations=case.domain_evaluations,
        reproducible_trace=case.reproducible_trace,
        human_approvals=case.human_approvals,
        maturity_level=case.maturity_level,
        designated_approval_evaluation=case.designated_approval_evaluation,
    )


def _evidence_is_complete(case: VAActivationCase) -> bool:
    """Calculate eligibility independently from the implementation property."""
    return (
        bool(case.domain_evaluations)
        and all(case.domain_evaluations)
        and case.reproducible_trace
        and bool(case.human_approvals)
        and all(case.human_approvals)
        and bool(case.maturity_level.strip())
        and case.designated_approval_evaluation
    )


# Feature: adoption-redesign, Property 17: VA activation eligibility cannot bypass evidence or approval
# **Validates: Requirements 6.5, 6.6, 6.7**
@settings(max_examples=100, deadline=None)
@example(case=_complete_case(0, "absent"))
@example(case=_complete_case(1, "pending"))
@example(case=_complete_case(2, "denied"))
@example(case=_complete_case(3, "approved"))
@given(case=_activation_cases())
def test_property_17_va_activation_requires_complete_evidence_and_approval(
    case: VAActivationCase,
) -> None:
    """Eligibility requires every gate, and active status additionally requires approval."""
    repository = InMemoryMigrationEvidenceRepository()
    evidence_service = MigrationEvidenceService(repository, clock=lambda: _NOW)
    controller = MigrationController(evidence_service)
    workflow_id = f"va-workflow-property-17-{case.case_id}"
    correlation_id = CorrelationId(f"correlation-property-17-{case.case_id}")
    evidence = _evidence(case, workflow_id)
    expected_eligible = _evidence_is_complete(case)

    eligibility = controller.evaluate_activation_eligibility(correlation_id, evidence)
    assert eligibility.is_success and eligibility.value is not None
    assert eligibility.value.status is (
        WorkflowActivationStatus.ACTIVATION_ELIGIBLE
        if expected_eligible
        else WorkflowActivationStatus.INELIGIBLE
    )
    assert eligibility.value.activation_eligible is expected_eligible

    if case.approval_state != "absent":
        approval = controller.approve_activation(
            correlation_id,
            approval_id=f"approval-property-17-{case.case_id}",
            workflow_id=workflow_id,
            reviewer_identity="va-reviewer-property-17",
            decision_reason=f"property-17-{case.approval_state}",
            approved=case.approval_state == "approved",
        )
        assert approval.is_success and approval.value is not None
        assert approval.value.approved is (case.approval_state == "approved")

    activation = evidence_service.activate_workflow(correlation_id, workflow_id)
    expected_active = expected_eligible and case.approval_state == "approved"
    assert activation.is_success is expected_active

    latest = evidence_service.latest_activation(workflow_id)
    assert latest is not None
    if expected_active:
        assert activation.value is not None
        assert activation.value.status is WorkflowActivationStatus.ACTIVE
        assert activation.value.activation_approval_id == (f"approval-property-17-{case.case_id}")
        assert latest.status is WorkflowActivationStatus.ACTIVE
    else:
        assert latest.status is not WorkflowActivationStatus.ACTIVE
