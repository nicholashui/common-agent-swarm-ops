"""Barrier-controlled local integration coverage for evaluation and sandbox evolution."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from fastapi.testclient import TestClient

from app.api.v1.dependencies import AuthenticatedRequestContext, get_authenticated_request_context
from app.api.v1.services import ControlPlaneServices, get_control_plane_services
from app.evaluation.models import EvaluationCheckKind, EvaluationOutcome, EvaluationRun
from app.evaluation.product_bar import (
    ProductBarCriterion,
    ProductBarEvidenceOutcome,
    ProductBarEvidenceService,
    ProductBarStatus,
)
from app.evaluation.service import EvaluationService
from app.evolution.models import (
    CanaryId,
    CanaryScope,
    CanaryState,
    ImprovementDirection,
    MetricComparison,
    PromotionApprovalId,
    PromotionAssessment,
    PromotionDecision,
    RollbackRecordId,
    RollbackStatus,
    SandboxVariant,
    SandboxVariantId,
)
from app.evolution.service import EvolutionService
from app.main import create_app
from app.models.contracts import ErrorDetail, Result
from app.models.identifiers import ActorId, CorrelationId, EvaluationRunId, OrganizationId
from app.repositories.evaluation_repository import InMemoryEvaluationRepository
from app.repositories.evolution_repository import InMemoryEvolutionRepository
from app.repositories.product_bar_repository import InMemoryProductBarEvidenceRepository

NOW = datetime(2025, 1, 1, tzinfo=UTC)
ORGANIZATION_ID = OrganizationId("org-evaluation-evolution")
CORRELATION_ID = CorrelationId("evaluation-evolution-integration")
ACTOR_ID = ActorId("local-approver")
MISSING_ROLLBACK_ID = RollbackRecordId("missing-rollback")
MISSING_CANARY_ID = CanaryId("missing-canary")
MISSING_APPROVAL_ID = PromotionApprovalId("missing-approval")


@dataclass(frozen=True, slots=True)
class LocalFakes:
    """Fixed-clock in-memory services; they invoke no networked or live resources."""

    evaluations: InMemoryEvaluationRepository
    evolution: InMemoryEvolutionRepository
    evaluation_service: EvaluationService
    evolution_service: EvolutionService


def _local_fakes() -> LocalFakes:
    evaluations = InMemoryEvaluationRepository()
    evolution = InMemoryEvolutionRepository()
    return LocalFakes(
        evaluations,
        evolution,
        EvaluationService(evaluations, clock=lambda: NOW),
        EvolutionService(evolution, evaluations, clock=lambda: NOW),
    )


def _successful_evaluation(fakes: LocalFakes) -> EvaluationRun:
    result = fakes.evaluation_service.run_suite(
        ORGANIZATION_ID,
        CORRELATION_ID,
        {"suite": "local-integration", "adapter_version": "local-1"},
    )
    assert result.is_success and result.value is not None
    assert result.value.transition_permitted
    return result.value


def _single_candidate(fakes: LocalFakes) -> SandboxVariant:
    proposed = fakes.evolution_service.propose(
        ORGANIZATION_ID,
        CORRELATION_ID,
        {"workflow": "production-baseline"},
        {"workflow": "sandbox-candidate"},
        "quality",
        ImprovementDirection.INCREASE,
    )
    assert proposed.is_success and proposed.value is not None
    considered = fakes.evolution_service.consider(
        ORGANIZATION_ID, CORRELATION_ID, proposed.value.variant_id
    )
    assert considered.is_success and considered.value is not None
    return considered.value


def _complete_candidate_support(
    fakes: LocalFakes, variant: SandboxVariant
) -> tuple[RollbackRecordId, CanaryId, PromotionApprovalId]:
    rollback = fakes.evolution_service.create_rollback_plan(
        ORGANIZATION_ID,
        CORRELATION_ID,
        variant.variant_id,
        {"action": "restore-local-baseline"},
    )
    assert rollback.is_success and rollback.value is not None
    canary = fakes.evolution_service.approve_canary(
        ORGANIZATION_ID,
        ACTOR_ID,
        CORRELATION_ID,
        variant.variant_id,
        CanaryScope(ORGANIZATION_ID, workflow_id="local-workflow"),
        ("quality",),
        rollback.value.rollback_record_id,
    )
    assert canary.is_success and canary.value is not None
    approval = fakes.evolution_service.record_human_approval(
        ORGANIZATION_ID,
        ACTOR_ID,
        CORRELATION_ID,
        variant.variant_id,
        "Approve the isolated local assessment.",
    )
    assert approval.is_success and approval.value is not None
    return (
        rollback.value.rollback_record_id,
        canary.value.canary_id,
        approval.value.approval_id,
    )


def _assess(
    fakes: LocalFakes,
    evaluation: EvaluationRun,
    requested_variant_id: SandboxVariantId | None,
    rollback_id: RollbackRecordId = MISSING_ROLLBACK_ID,
    canary_id: CanaryId = MISSING_CANARY_ID,
    approval_id: PromotionApprovalId = MISSING_APPROVAL_ID,
    evidence_references: tuple[str, ...] = ("local-evidence",),
) -> Result[PromotionAssessment, ErrorDetail]:
    return fakes.evolution_service.assess_promotion(
        ORGANIZATION_ID,
        CORRELATION_ID,
        requested_variant_id,
        evaluation.evaluation_run_id,
        MetricComparison(10.0, 11.0),
        MetricComparison(10.0, 10.0),
        MetricComparison(10.0, 10.0),
        rollback_id,
        canary_id,
        ("local-audit",),
        evidence_references,
        approval_id,
    )


def test_blocking_failure_latches_the_transition_barrier_while_nonblocking_checks_finish() -> None:
    """A failed blocker immediately closes the current barrier without aborting later checks."""
    fakes = _local_fakes()
    executions: list[tuple[str, EvaluationCheckKind, bool]] = []

    def executor(task_id: str, check_kind: EvaluationCheckKind) -> EvaluationOutcome:
        executions.append(
            (task_id, check_kind, fakes.evaluations.current_transition_permitted())
        )
        if task_id == "golden-001" and check_kind is EvaluationCheckKind.REGRESSION:
            return EvaluationOutcome.FAIL
        return EvaluationOutcome.PASS

    result = fakes.evaluation_service.run_suite(
        ORGANIZATION_ID,
        CORRELATION_ID,
        {"suite": "barrier-in-progress"},
        lambda task, check: executor(task.task_id, check.kind),
    )

    assert result.is_success and result.value is not None
    failed_index = next(
        index
        for index, execution in enumerate(executions)
        if execution[:2] == ("golden-001", EvaluationCheckKind.REGRESSION)
    )
    assert not result.value.transition_permitted
    assert not fakes.evaluations.current_transition_permitted()
    assert len(result.value.results) == len(result.value.task_ids) * len(result.value.checks)
    assert all(not permitted for _, _, permitted in executions[failed_index + 1 :])
    assert any(
        not cell.blocking and cell.outcome is EvaluationOutcome.PASS
        for cell in result.value.results
    )


def test_product_bar_without_e1_pass_is_incomplete_even_when_other_entries_pass() -> None:
    """Independent Product-Bar entries cannot imply a missing E1 pass."""
    service = ProductBarEvidenceService(
        InMemoryProductBarEvidenceRepository(), clock=lambda: NOW
    )
    for criterion in tuple(ProductBarCriterion)[1:]:
        recorded = service.record_evidence(
            ORGANIZATION_ID,
            CORRELATION_ID,
            criterion,
            ProductBarEvidenceOutcome.PASS,
            evaluation_run_ids=(EvaluationRunId(f"local-{criterion.value}"),),
            evidence_hashes=("a" * 64,),
        )
        assert recorded.is_success

    assessment = service.assess(ORGANIZATION_ID, CORRELATION_ID)

    assert assessment.is_success and assessment.value is not None
    assert assessment.value.status is ProductBarStatus.INCOMPLETE
    e1_entry = next(
        entry
        for entry in assessment.value.entries
        if entry.criterion is ProductBarCriterion.E1
    )
    assert e1_entry.outcome is ProductBarEvidenceOutcome.FAIL
    assert not e1_entry.evidence_ids


def test_promotion_assessment_blocks_zero_and_multiple_candidates() -> None:
    """Promotion requires exactly one requested sandbox candidate in the local repository."""
    zero_fakes = _local_fakes()
    zero_evaluation = _successful_evaluation(zero_fakes)
    zero_assessment = _assess(zero_fakes, zero_evaluation, None)
    assert zero_assessment.is_success and zero_assessment.value is not None
    assert zero_assessment.value.candidate_count == 0
    assert zero_assessment.value.decision is PromotionDecision.BLOCKED
    assert "exactly_one_candidate" in zero_assessment.value.missing_or_failed_conditions

    multiple_fakes = _local_fakes()
    multiple_evaluation = _successful_evaluation(multiple_fakes)
    first = _single_candidate(multiple_fakes)
    _single_candidate(multiple_fakes)
    multiple_assessment = _assess(multiple_fakes, multiple_evaluation, first.variant_id)
    assert multiple_assessment.is_success and multiple_assessment.value is not None
    assert multiple_assessment.value.candidate_count == 2
    assert multiple_assessment.value.decision is PromotionDecision.BLOCKED
    assert "exactly_one_candidate" in multiple_assessment.value.missing_or_failed_conditions
    assert multiple_assessment.value.production_applied is False


def test_evidence_retention_failure_blocks_promotion_but_allows_sandbox_work() -> None:
    """Missing promotion evidence never prevents subsequent non-promotion sandbox proposals."""
    fakes = _local_fakes()
    evaluation = _successful_evaluation(fakes)
    candidate = _single_candidate(fakes)
    rollback_id, canary_id, approval_id = _complete_candidate_support(fakes, candidate)

    assessment = _assess(
        fakes,
        evaluation,
        candidate.variant_id,
        rollback_id,
        canary_id,
        approval_id,
        evidence_references=(),
    )

    assert assessment.is_success and assessment.value is not None
    assert assessment.value.decision is PromotionDecision.BLOCKED
    assert assessment.value.missing_or_failed_conditions == ("evidence_retained",)
    assert assessment.value.production_applied is False
    continued = fakes.evolution_service.propose(
        ORGANIZATION_ID,
        CORRELATION_ID,
        {"workflow": "production-baseline"},
        {"workflow": "continued-sandbox-work"},
        "quality",
        ImprovementDirection.INCREASE,
    )
    assert continued.is_success and continued.value is not None
    assert continued.value.state.value == "draft"


def test_delayed_local_canary_activation_then_failure_stops_and_rolls_back() -> None:
    """Approval is inert until local activation; a failed criterion retains rollback evidence."""
    fakes = _local_fakes()
    candidate = _single_candidate(fakes)
    rollback_id, canary_id, _ = _complete_candidate_support(fakes, candidate)

    before_activation = fakes.evolution_service.authorize_canary_operation(
        ORGANIZATION_ID,
        CORRELATION_ID,
        canary_id,
        CanaryScope(ORGANIZATION_ID, workflow_id="local-workflow"),
    )
    assert not before_activation.is_success
    approved = fakes.evolution.get_canary(ORGANIZATION_ID, canary_id)
    assert approved.is_success and approved.value is not None
    assert approved.value.state is CanaryState.APPROVED

    activated = fakes.evolution_service.activate_canary(ORGANIZATION_ID, CORRELATION_ID, canary_id)
    assert activated.is_success and activated.value is not None
    assert activated.value.state is CanaryState.ACTIVE
    authorized = fakes.evolution_service.authorize_canary_operation(
        ORGANIZATION_ID,
        CORRELATION_ID,
        canary_id,
        CanaryScope(ORGANIZATION_ID, workflow_id="local-workflow"),
    )
    assert authorized.is_success and authorized.value is True

    stopped = fakes.evolution_service.record_canary_criterion(
        ORGANIZATION_ID,
        CORRELATION_ID,
        canary_id,
        "quality",
        False,
        "local-failure-evidence",
    )
    assert stopped.is_success and stopped.value is not None
    assert stopped.value.state is CanaryState.STOPPED
    assert stopped.value.criterion_results[-1].evidence_reference == "local-failure-evidence"
    rollback = fakes.evolution.get_rollback(ORGANIZATION_ID, rollback_id)
    assert rollback.is_success and rollback.value is not None
    assert rollback.value.status is RollbackStatus.PERFORMED
    assert rollback.value.failure_evidence == "local-failure-evidence"


def test_single_fully_evidenced_candidate_is_permitted_without_production_mutation() -> None:
    """A complete local assessment permits the transition decision only, never an apply action."""
    fakes = _local_fakes()
    evaluation = _successful_evaluation(fakes)
    candidate = _single_candidate(fakes)
    rollback_id, canary_id, approval_id = _complete_candidate_support(fakes, candidate)

    assessment = _assess(
        fakes,
        evaluation,
        candidate.variant_id,
        rollback_id,
        canary_id,
        approval_id,
    )

    assert assessment.is_success and assessment.value is not None
    assert assessment.value.decision is PromotionDecision.PERMITTED
    assert not assessment.value.missing_or_failed_conditions
    assert assessment.value.production_applied is False
    assert fakes.evolution.promotion_permitted(
        ORGANIZATION_ID, assessment.value.assessment_id
    )


def test_versioned_evolution_api_derives_tenancy_from_trusted_context() -> None:
    """A foreign authenticated tenant cannot select a local sandbox variant by path ID."""
    application = create_app()
    services = ControlPlaneServices()
    contexts: dict[str, AuthenticatedRequestContext] = {
        "current": AuthenticatedRequestContext(
            tenant_id=OrganizationId("org-api-owner"),
            actor_id=ActorId("owner"),
            correlation_id=CorrelationId("owner-correlation"),
        )
    }
    application.dependency_overrides[get_authenticated_request_context] = (
        lambda: contexts["current"]
    )
    application.dependency_overrides[get_control_plane_services] = lambda: services

    try:
        with TestClient(application) as client:
            created = client.post(
                "/api/v1/evolution/variants",
                json={
                    "production_configuration": {"workflow": "owner-production"},
                    "sandbox_configuration": {"workflow": "owner-sandbox"},
                    "target_metric": "quality",
                    "improvement_direction": "increase",
                },
            )
            assert created.status_code == 201
            variant_id = str(created.json()["variant_id"])

            contexts["current"] = AuthenticatedRequestContext(
                tenant_id=OrganizationId("org-api-foreign"),
                actor_id=ActorId("foreign"),
                correlation_id=CorrelationId("foreign-correlation"),
            )
            foreign_consider = client.post(f"/api/v1/evolution/variants/{variant_id}/consider")
            assert foreign_consider.status_code == 404
            assert foreign_consider.json()["detail"]["code"] == "not_found"

            unversioned = client.post(f"/evolution/variants/{variant_id}/consider")
            assert unversioned.status_code == 404
    finally:
        application.dependency_overrides.clear()

    owner_variant = services.evolution_repository.get_variant(
        OrganizationId("org-api-owner"), SandboxVariantId(variant_id)
    )
    assert owner_variant.is_success and owner_variant.value is not None
    assert owner_variant.value.state.value == "draft"
