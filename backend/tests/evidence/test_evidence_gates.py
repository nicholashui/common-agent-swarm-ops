"""Focused deterministic coverage for the target-local E1-E9 evidence gate runner."""

from __future__ import annotations

from dataclasses import replace

from app.evaluation.product_bar import (
    ProductBarCriterion,
    ProductBarEvidenceOutcome,
    ProductBarEvidenceService,
)
from app.evidence.fixtures import (
    FIXTURE_CORRELATION_ID,
    FIXTURE_ORGANIZATION_ID,
    NOW,
    build_target_local_evidence_fixture,
)
from app.evidence.gates import EvidenceGateRunner
from app.evidence.records import EvidenceTransition, InMemoryEvidenceGateRepository
from app.repositories.product_bar_repository import InMemoryProductBarEvidenceRepository


def _runner() -> tuple[EvidenceGateRunner, InMemoryEvidenceGateRepository]:
    gates = InMemoryEvidenceGateRepository()
    product_bar = ProductBarEvidenceService(
        InMemoryProductBarEvidenceRepository(), clock=lambda: NOW
    )
    return EvidenceGateRunner(product_bar, gates, clock=lambda: NOW), gates


def test_runner_assembles_independent_complete_target_local_records() -> None:
    """Every E1-E9 record retains source IDs, versions, hashes, commands, and references."""
    runner, repository = _runner()

    result = runner.evaluate(
        FIXTURE_ORGANIZATION_ID,
        FIXTURE_CORRELATION_ID,
        build_target_local_evidence_fixture(),
    )

    assert result.is_success and result.value is not None
    assessment = result.value
    assert assessment.production_mutated is False
    assert assessment.blocked_transitions == ()
    assert tuple(record.criterion for record in assessment.records) == tuple(ProductBarCriterion)
    assert len(repository.records()) == len(ProductBarCriterion)
    for record in assessment.records:
        assert record.outcome is ProductBarEvidenceOutcome.PASS
        assert record.local_record_ids and record.evidence_hashes
        assert record.adapter_versions and record.schema_versions
        assert record.command_result.exit_code == 0
        assert record.supporting_references and record.product_bar_evidence_id


def test_failed_e9_blocks_only_its_configured_next_transition() -> None:
    """A criterion failure does not block unrelated transitions or mutate production state."""
    runner, _ = _runner()
    snapshot = build_target_local_evidence_fixture()
    failed_claims = tuple(
        replace(claim, passed=False)
        if claim.criterion is ProductBarCriterion.E9
        else claim
        for claim in snapshot.claims
    )

    result = runner.evaluate(
        FIXTURE_ORGANIZATION_ID,
        FIXTURE_CORRELATION_ID,
        replace(snapshot, claims=failed_claims),
    )

    assert result.is_success and result.value is not None
    assessment = result.value
    failed = [
        record
        for record in assessment.records
        if record.outcome is ProductBarEvidenceOutcome.FAIL
    ]
    assert [record.criterion for record in failed] == [ProductBarCriterion.E9]
    assert assessment.blocked_transitions == (EvidenceTransition.VIDEO_RELEASE_READINESS,)
    assert assessment.production_mutated is False
