"""Focused examples for independent Product-Bar evidence records."""

from __future__ import annotations

from datetime import UTC, datetime

from app.evaluation.product_bar import (
    ProductBarCommandResult,
    ProductBarCriterion,
    ProductBarEvidenceOutcome,
    ProductBarEvidenceService,
    ProductBarStatus,
)
from app.models.evidence import EvidenceReference
from app.models.identifiers import (
    CorrelationId,
    EvaluationRunId,
    EvidenceId,
    OrganizationId,
)
from app.repositories.product_bar_repository import InMemoryProductBarEvidenceRepository

NOW = datetime(2025, 1, 1, tzinfo=UTC)
ORGANIZATION_ID = OrganizationId("org-product-bar")
CORRELATION_ID = CorrelationId("product-bar-correlation")
HASH = "a" * 64


def _service() -> ProductBarEvidenceService:
    return ProductBarEvidenceService(InMemoryProductBarEvidenceRepository(), clock=lambda: NOW)


def _record(
    service: ProductBarEvidenceService,
    criterion: ProductBarCriterion,
    outcome: ProductBarEvidenceOutcome = ProductBarEvidenceOutcome.PASS,
) -> None:
    result = service.record_evidence(
        ORGANIZATION_ID,
        CORRELATION_ID,
        criterion,
        outcome,
        evaluation_run_ids=(EvaluationRunId(f"evaluation-{criterion.value}"),),
        evidence_hashes=(HASH,),
        command_results=(ProductBarCommandResult("python -m pytest -q", 0, HASH, NOW),),
        supporting_references=(EvidenceReference(EvidenceId("source"), HASH, "test"),),
    )
    assert result.is_success


def test_assessment_has_all_independent_entries_and_is_incomplete_without_e1_pass() -> None:
    """An E1 omission never permits a complete Product-Bar status."""
    service = _service()
    for criterion in ProductBarCriterion:
        if criterion is not ProductBarCriterion.E1:
            _record(service, criterion)

    assessment = service.assess(ORGANIZATION_ID, CORRELATION_ID)

    assert assessment.is_success and assessment.value is not None
    assert assessment.value.status is ProductBarStatus.INCOMPLETE
    assert tuple(entry.criterion for entry in assessment.value.entries) == tuple(
        ProductBarCriterion
    )
    e1_entry = assessment.value.entries[0]
    assert e1_entry.criterion is ProductBarCriterion.E1
    assert e1_entry.outcome is ProductBarEvidenceOutcome.FAIL
    assert not e1_entry.evidence_ids


def test_passing_local_evidence_for_each_criterion_completes_assessment() -> None:
    """Completion requires independent passing evidence for every named capability."""
    service = _service()
    for criterion in ProductBarCriterion:
        _record(service, criterion)

    assessment = service.assess(ORGANIZATION_ID, CORRELATION_ID)

    assert assessment.is_success and assessment.value is not None
    assert assessment.value.status is ProductBarStatus.COMPLETE
    assert all(
        entry.outcome is ProductBarEvidenceOutcome.PASS for entry in assessment.value.entries
    )
    assert all(len(entry.evidence_ids) == 1 for entry in assessment.value.entries)


def test_evidence_requires_a_local_source_identifier_and_sha256_hash() -> None:
    """Raw output or malformed evidence cannot be retained as Product-Bar evidence."""
    service = _service()

    missing_source = service.record_evidence(
        ORGANIZATION_ID,
        CORRELATION_ID,
        ProductBarCriterion.E1,
        ProductBarEvidenceOutcome.PASS,
        evidence_hashes=(HASH,),
    )
    malformed_hash = service.record_evidence(
        ORGANIZATION_ID,
        CORRELATION_ID,
        ProductBarCriterion.E1,
        ProductBarEvidenceOutcome.PASS,
        evaluation_run_ids=(EvaluationRunId("evaluation-e1"),),
        evidence_hashes=("not-a-hash",),
    )

    assert not missing_source.is_success
    assert missing_source.error is not None
    assert "local run or evaluation ID" in missing_source.error.message
    assert not malformed_hash.is_success
    assert malformed_hash.error is not None
    assert "SHA-256 hashes" in malformed_hash.error.message
