"""Final deterministic, target-local Product-Bar evidence checks."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.adapters.base import DeterministicLocalAdapter
from app.adapters.local import LOCAL_ADAPTER_VERSION, default_local_adapters
from app.evaluation.models import DEFAULT_NAMED_CHECKS
from app.evaluation.product_bar import ProductBarCriterion, ProductBarEvidenceOutcome
from app.evidence.fixtures import (
    FIXTURE_CORRELATION_ID,
    FIXTURE_ORGANIZATION_ID,
    NOW,
    build_target_local_evidence_fixture,
)
from app.evidence.gates import EvidenceGateRunner
from app.evidence.records import (
    CRITERION_TRANSITIONS,
    EvidenceGateAssessment,
    InMemoryEvidenceGateRepository,
)
from app.governance.operation_guard import OperationGuard
from app.main import API_V1_PREFIX, create_app
from app.models.operations import (
    OperationDecisionStatus,
    OperationKind,
    ProhibitedOperationReason,
    RecordedAuthorization,
    RequestedOperation,
)
from app.repositories.product_bar_repository import InMemoryProductBarEvidenceRepository


def _runner() -> EvidenceGateRunner:
    """Create an isolated runner that retains evidence in this test process only."""
    from app.evaluation.product_bar import ProductBarEvidenceService

    return EvidenceGateRunner(
        ProductBarEvidenceService(InMemoryProductBarEvidenceRepository(), clock=lambda: NOW),
        InMemoryEvidenceGateRepository(),
        clock=lambda: NOW,
    )


def _failure_criteria(assessment: EvidenceGateAssessment) -> set[ProductBarCriterion]:
    """Return failed criteria from the concrete immutable assessment."""
    records = assessment.records
    return {
        record.criterion for record in records if record.outcome is ProductBarEvidenceOutcome.FAIL
    }


@pytest.mark.parametrize(
    ("criterion", "claim_name"),
    (
        (ProductBarCriterion.E1, "operator-path"),
        (ProductBarCriterion.E2, "durable-controls-restart"),
        (ProductBarCriterion.E3, "adapter-audit-effect"),
        (ProductBarCriterion.E4, None),
        (ProductBarCriterion.E5, "sandbox-canary-rollback"),
        (ProductBarCriterion.E6, "automatic-promotion-blocked"),
        (ProductBarCriterion.E7, "frontend-forms"),
        (ProductBarCriterion.E8, "postgres-recovery"),
        (ProductBarCriterion.E9, "release-denial-cases"),
    ),
)
def test_each_product_bar_criterion_has_independent_local_evidence(
    criterion: ProductBarCriterion, claim_name: str | None
) -> None:
    """Changing one criterion's source blocks only that criterion's next transition."""
    snapshot = build_target_local_evidence_fixture()
    changed_snapshot = (
        replace(snapshot, process_artifacts=())
        if criterion is ProductBarCriterion.E4
        else replace(
            snapshot,
            claims=tuple(
                replace(claim, passed=False)
                if claim.criterion is criterion and claim.name == claim_name
                else claim
                for claim in snapshot.claims
            ),
        )
    )

    result = _runner().evaluate(FIXTURE_ORGANIZATION_ID, FIXTURE_CORRELATION_ID, changed_snapshot)

    assert result.is_success and result.value is not None
    assessment = result.value
    assert _failure_criteria(assessment) == {criterion}
    assert assessment.blocked_transitions == (CRITERION_TRANSITIONS[criterion],)
    assert not assessment.production_mutated


def test_complete_product_bar_retains_reproducible_named_local_results() -> None:
    """The complete fixture retains all named checks without production side effects."""
    snapshot = build_target_local_evidence_fixture()
    first = _runner().evaluate(FIXTURE_ORGANIZATION_ID, FIXTURE_CORRELATION_ID, snapshot)
    second = _runner().evaluate(FIXTURE_ORGANIZATION_ID, FIXTURE_CORRELATION_ID, snapshot)

    assert first.is_success and first.value is not None
    assert second.is_success and second.value is not None
    for assessment in (first.value, second.value):
        assert tuple(record.criterion for record in assessment.records) == tuple(
            ProductBarCriterion
        )
        assert all(
            record.outcome is ProductBarEvidenceOutcome.PASS for record in assessment.records
        )
        assert assessment.blocked_transitions == ()
        assert not assessment.production_mutated
        assert all(not promotion.production_applied for promotion in snapshot.promotion_assessments)
        assert all(not request.artifact_released for request in snapshot.release_requests)

    expected_check_names = {check.name for check in DEFAULT_NAMED_CHECKS}
    evaluation = snapshot.evaluations[0]
    assert len(evaluation.task_ids) == 20
    assert {result.check_name for result in evaluation.results} == expected_check_names
    assert len(evaluation.results) == len(evaluation.task_ids) * len(DEFAULT_NAMED_CHECKS)
    assert all(claim.passed for claim in snapshot.claims)
    assert all(adapter.version == LOCAL_ADAPTER_VERSION for adapter in snapshot.adapter_versions)


@pytest.mark.parametrize("number", range(1, 23))
def test_all_twenty_two_property_contracts_are_present_and_linked(number: int) -> None:
    """Every specified property remains an executable, requirement-linked Hypothesis test."""
    property_path = Path(__file__).parents[1] / "properties" / f"test_property_{number:02d}_"
    matches = tuple(property_path.parent.glob(f"{property_path.name}*.py"))

    assert len(matches) == 1
    source = matches[0].read_text(encoding="utf-8")
    assert f"Property {number}:" in source
    assert "Feature: generic-swarm-business-os" in source
    assert "**Validates: Requirements" in source
    assert "max_examples=100" in source


def test_public_surface_is_v1_only_and_adapters_are_deterministic_local_stubs() -> None:
    """The Host exposes no unversioned control plane and registers no live adapters."""
    application = create_app()
    with TestClient(application) as client:
        assert all(
            getattr(route, "path", "").startswith(f"{API_V1_PREFIX}/")
            for route in application.routes
        )
        assert client.get("/docs").status_code == 404
        assert client.get("/workflow-runs/unversioned").status_code == 404

    adapters = default_local_adapters()
    assert adapters
    assert all(isinstance(adapter, DeterministicLocalAdapter) for adapter in adapters)
    assert all(
        adapter.local_only and adapter.version == LOCAL_ADAPTER_VERSION for adapter in adapters
    )
    assert {adapter.adapter_id for adapter in adapters} >= {"media.stub", "crm.lookup"}


def test_all_unsafe_operations_are_rejected_without_permitting_production_work() -> None:
    """Prohibited automatic, rewrite, unbounded, and unauthorized work remains fail-closed."""
    authorization = RecordedAuthorization("approval-local", NOW)
    operations = (
        RequestedOperation("automatic-promotion", OperationKind.PRODUCTION_PROMOTION, True, True),
        RequestedOperation("host-rewrite", OperationKind.HOST_CODE_REWRITE, True),
        RequestedOperation(
            "unbounded-orchestration",
            OperationKind.ORCHESTRATION,
            bounded=False,
            recorded_authorization=authorization,
        ),
        RequestedOperation("unrecorded-orchestration", OperationKind.ORCHESTRATION),
    )

    assessment = OperationGuard().assess(operations)

    assert assessment.production_changes_blocked
    assert not assessment.permits_any_operation
    assert assessment.prohibited_error is not None
    assert assessment.prohibited_error.code == "prohibited_operation"
    assert tuple(decision.status for decision in assessment.decisions) == (
        OperationDecisionStatus.PROHIBITED,
    ) * len(operations)
    assert tuple(item.reason for item in assessment.prohibited_error.prohibited_operations) == (
        ProhibitedOperationReason.AUTOMATIC_PRODUCTION_PROMOTION,
        ProhibitedOperationReason.PRODUCTION_HOST_CODE_REWRITE,
        ProhibitedOperationReason.UNBOUNDED_ORCHESTRATION,
        ProhibitedOperationReason.MISSING_ORCHESTRATION_AUTHORIZATION,
    )
