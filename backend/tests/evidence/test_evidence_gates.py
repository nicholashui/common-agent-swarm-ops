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
        assert record.command_result.output_digest in record.evidence_hashes
        assert any(reference.kind == "local-command" for reference in record.supporting_references)
        assert record.supporting_references and record.product_bar_evidence_id


def test_failed_e9_blocks_only_its_configured_next_transition() -> None:
    """A criterion failure does not block unrelated transitions or mutate production state."""
    runner, _ = _runner()
    snapshot = build_target_local_evidence_fixture()
    failed_claims = tuple(
        replace(claim, passed=False) if claim.criterion is ProductBarCriterion.E9 else claim
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
        record for record in assessment.records if record.outcome is ProductBarEvidenceOutcome.FAIL
    ]
    assert [record.criterion for record in failed] == [ProductBarCriterion.E9]
    assert assessment.blocked_transitions == (EvidenceTransition.VIDEO_RELEASE_READINESS,)
    assert assessment.production_mutated is False


def test_incomplete_evaluation_matrix_blocks_only_evaluation_transition() -> None:
    """A missing task/check cell cannot be masked by a passing summary flag."""
    runner, _ = _runner()
    snapshot = build_target_local_evidence_fixture()
    evaluation = snapshot.evaluations[0]
    incomplete = replace(evaluation, results=evaluation.results[:-1])

    result = runner.evaluate(
        FIXTURE_ORGANIZATION_ID,
        FIXTURE_CORRELATION_ID,
        replace(snapshot, evaluations=(incomplete,)),
    )

    assert result.is_success and result.value is not None
    failed = [
        record
        for record in result.value.records
        if record.outcome is ProductBarEvidenceOutcome.FAIL
    ]
    assert [record.criterion for record in failed] == [ProductBarCriterion.E6]
    assert result.value.blocked_transitions == (EvidenceTransition.EVALUATION_TRANSITION,)
    assert not result.value.production_mutated


def test_duplicate_video_inventory_entry_blocks_only_video_transition() -> None:
    """A report marked valid still requires a one-to-one 114-agent inventory."""
    runner, _ = _runner()
    snapshot = build_target_local_evidence_fixture()
    report = snapshot.video_inventory_reports[0]
    duplicate_inventory = (*report.inventory_agent_ids[:-1], report.inventory_agent_ids[0])

    result = runner.evaluate(
        FIXTURE_ORGANIZATION_ID,
        FIXTURE_CORRELATION_ID,
        replace(
            snapshot,
            video_inventory_reports=(replace(report, inventory_agent_ids=duplicate_inventory),),
        ),
    )

    assert result.is_success and result.value is not None
    failed = [
        record
        for record in result.value.records
        if record.outcome is ProductBarEvidenceOutcome.FAIL
    ]
    assert [record.criterion for record in failed] == [ProductBarCriterion.E9]
    assert result.value.blocked_transitions == (EvidenceTransition.VIDEO_RELEASE_READINESS,)
    assert not result.value.production_mutated
