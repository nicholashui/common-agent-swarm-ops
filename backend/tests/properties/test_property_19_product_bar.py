"""Property tests for independently complete Product-Bar evidence."""

from __future__ import annotations

from datetime import UTC, datetime

from hypothesis import example, given, settings, strategies as st

from app.evaluation.product_bar import (
    ProductBarCriterion,
    ProductBarEvidenceOutcome,
    ProductBarEvidenceService,
    ProductBarStatus,
)
from app.models.identifiers import CorrelationId, EvaluationRunId, OrganizationId
from app.repositories.product_bar_repository import InMemoryProductBarEvidenceRepository

# Feature: generic-swarm-business-os, Property 19: Product-bar evidence is independently
# complete.
# **Validates: Requirements 8.6**

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_ORGANIZATION_ID = OrganizationId("org-property-19")
_CORRELATION_ID = CorrelationId("corr-property-19")
_HASH = "a" * 64
_OUTCOMES = tuple(ProductBarEvidenceOutcome)


def _evidence_matrices(
) -> st.SearchStrategy[dict[ProductBarCriterion, ProductBarEvidenceOutcome | None]]:
    """Generate all E1-E9 omission, pass, and fail combinations."""
    state = st.one_of(st.none(), st.sampled_from(_OUTCOMES))
    return st.fixed_dictionaries({criterion: state for criterion in ProductBarCriterion})


def _record(
    service: ProductBarEvidenceService,
    criterion: ProductBarCriterion,
    outcome: ProductBarEvidenceOutcome,
) -> None:
    """Retain one valid local record for an observed criterion result."""
    result = service.record_evidence(
        _ORGANIZATION_ID,
        _CORRELATION_ID,
        criterion,
        outcome,
        evaluation_run_ids=(EvaluationRunId(f"evaluation-property-19-{criterion.value}"),),
        evidence_hashes=(_HASH,),
    )
    assert result.is_success and result.value is not None


@settings(max_examples=100, deadline=None, derandomize=True)
@example({criterion: None for criterion in ProductBarCriterion})
@example({criterion: ProductBarEvidenceOutcome.PASS for criterion in ProductBarCriterion})
@given(outcomes=_evidence_matrices())
def test_product_bar_entries_are_independent_for_every_omission_result_matrix(
    outcomes: dict[ProductBarCriterion, ProductBarEvidenceOutcome | None],
) -> None:
    """Every capability is assessed independently from its own omitted/pass/fail evidence."""
    service = ProductBarEvidenceService(
        InMemoryProductBarEvidenceRepository(),
        clock=lambda: _NOW,
    )
    for criterion, outcome in outcomes.items():
        if outcome is not None:
            _record(service, criterion, outcome)

    assessed = service.assess(_ORGANIZATION_ID, _CORRELATION_ID)

    assert assessed.is_success and assessed.value is not None
    assessment = assessed.value
    entries = {entry.criterion: entry for entry in assessment.entries}
    assert tuple(entry.criterion for entry in assessment.entries) == tuple(ProductBarCriterion)
    assert set(entries) == set(ProductBarCriterion)

    for criterion, outcome in outcomes.items():
        entry = entries[criterion]
        expected_outcome = (
            ProductBarEvidenceOutcome.PASS
            if outcome is ProductBarEvidenceOutcome.PASS
            else ProductBarEvidenceOutcome.FAIL
        )
        assert entry.outcome is expected_outcome
        assert len(entry.evidence_ids) == (0 if outcome is None else 1)

    expected_status = (
        ProductBarStatus.COMPLETE
        if all(outcome is ProductBarEvidenceOutcome.PASS for outcome in outcomes.values())
        else ProductBarStatus.INCOMPLETE
    )
    assert assessment.status is expected_status
    if outcomes[ProductBarCriterion.E1] is not ProductBarEvidenceOutcome.PASS:
        assert assessment.status is ProductBarStatus.INCOMPLETE
