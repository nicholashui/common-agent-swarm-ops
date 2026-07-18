"""Property tests for sandbox isolation and exhaustive promotion gating."""

from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import dataclass
from datetime import UTC, datetime

from hypothesis import example, given, settings, strategies as st

from app.evaluation.models import (
    DEFAULT_NAMED_CHECKS,
    EvaluationCellResult,
    EvaluationCheckKind,
    EvaluationOutcome,
    EvaluationRun,
)
from app.evolution.models import (
    CanaryId,
    CanaryScope,
    CanaryState,
    ImprovementDirection,
    MetricComparison,
    PromotionApprovalId,
    PromotionDecision,
    RollbackRecordId,
    SandboxVariant,
    SandboxVariantId,
)
from app.evolution.service import EvolutionService
from app.models.common import SCHEMA_VERSION, RecordMetadata
from app.models.identifiers import (
    ActorId,
    CorrelationId,
    EvaluationResultId,
    EvaluationRunId,
    OrganizationId,
    RecordId,
)
from app.repositories.evaluation_repository import InMemoryEvaluationRepository
from app.repositories.evolution_repository import InMemoryEvolutionRepository

# Feature: generic-swarm-business-os, Property 16: Evolution variants are isolated and
# promotion is exhaustive.
# **Validates: Requirements 7.1, 7.2, 7.3, 7.6**

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_ORGANIZATION_ID = OrganizationId("org-property-16")
_ACTOR_ID = ActorId("actor-property-16")
_CORRELATION_ID = CorrelationId("property-16")
_MISSING_VARIANT_ID = SandboxVariantId("missing-variant")
_MISSING_ROLLBACK_ID = RollbackRecordId("missing-rollback")
_MISSING_CANARY_ID = CanaryId("missing-canary")
_MISSING_APPROVAL_ID = PromotionApprovalId("missing-approval")


@dataclass(frozen=True, slots=True)
class PromotionCase:
    """A bounded candidate-cardinality and promotion-condition matrix."""

    production_configuration: dict[str, object]
    sandbox_configuration: dict[str, object]
    improvement_direction: ImprovementDirection
    candidate_count: int
    requested_candidate: bool
    target_improved: bool
    safety_no_worse: bool
    compliance_no_worse: bool
    evaluation_transition_permitted: bool
    regression_checks_pass: bool
    adversarial_checks_pass: bool
    rollback_recorded: bool
    canary_approved: bool
    audit_complete: bool
    evidence_retained: bool
    human_approved: bool


@dataclass(slots=True)
class DeterministicLocalFakes:
    """Local in-memory services with a fixed clock and no active canary."""

    service: EvolutionService
    evolution: InMemoryEvolutionRepository
    evaluations: InMemoryEvaluationRepository


_SAFE_TEXT = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyz0123456789-_",
    min_size=1,
    max_size=12,
)


@st.composite
def _promotion_cases(draw: st.DrawFn) -> PromotionCase:
    """Generate every bounded candidate and promotion-gate input dimension."""
    production_configuration: dict[str, object] = {
        "workflow": {
            "name": draw(_SAFE_TEXT),
            "steps": draw(st.lists(st.integers(min_value=0, max_value=9), max_size=4)),
        },
        "roles": draw(st.lists(_SAFE_TEXT, min_size=1, max_size=3, unique=True)),
        "tool_policy": {"mode": draw(st.sampled_from(("restricted", "reviewed")))},
    }
    sandbox_configuration: dict[str, object] = {
        "workflow": {
            "name": draw(_SAFE_TEXT),
            "steps": draw(st.lists(st.integers(min_value=0, max_value=9), max_size=4)),
        },
        "roles": draw(st.lists(_SAFE_TEXT, min_size=1, max_size=3, unique=True)),
        "tool_policy": {"mode": draw(st.sampled_from(("restricted", "reviewed")))},
    }
    return PromotionCase(
        production_configuration=production_configuration,
        sandbox_configuration=sandbox_configuration,
        improvement_direction=draw(st.sampled_from(tuple(ImprovementDirection))),
        candidate_count=draw(st.sampled_from((0, 1, 2))),
        requested_candidate=draw(st.booleans()),
        target_improved=draw(st.booleans()),
        safety_no_worse=draw(st.booleans()),
        compliance_no_worse=draw(st.booleans()),
        evaluation_transition_permitted=draw(st.booleans()),
        regression_checks_pass=draw(st.booleans()),
        adversarial_checks_pass=draw(st.booleans()),
        rollback_recorded=draw(st.booleans()),
        canary_approved=draw(st.booleans()),
        audit_complete=draw(st.booleans()),
        evidence_retained=draw(st.booleans()),
        human_approved=draw(st.booleans()),
    )


def _fakes() -> DeterministicLocalFakes:
    """Return isolated local repositories wired to a fixed deterministic clock."""
    evolution = InMemoryEvolutionRepository()
    evaluations = InMemoryEvaluationRepository()
    return DeterministicLocalFakes(
        EvolutionService(evolution, evaluations, clock=lambda: _NOW), evolution, evaluations
    )


def _require_value[T](result_value: T | None) -> T:
    """Narrow a previously asserted successful local service result."""
    assert result_value is not None
    return result_value


def _retain_evaluation(case: PromotionCase, fakes: DeterministicLocalFakes) -> EvaluationRun:
    """Install a deterministic named-check matrix without external evaluation work."""
    outcomes = {
        EvaluationCheckKind.REGRESSION: (
            EvaluationOutcome.PASS
            if case.regression_checks_pass
            else EvaluationOutcome.FAIL
        ),
        EvaluationCheckKind.ADVERSARIAL: (
            EvaluationOutcome.PASS
            if case.adversarial_checks_pass
            else EvaluationOutcome.FAIL
        ),
    }
    run = EvaluationRun(
        metadata=RecordMetadata(
            record_id=RecordId("property-16-evaluation-record"),
            organization_id=_ORGANIZATION_ID,
            correlation_id=_CORRELATION_ID,
            schema_version=SCHEMA_VERSION,
            version=1,
            created_at=_NOW,
            updated_at=_NOW,
        ),
        evaluation_run_id=EvaluationRunId("property-16-evaluation-run"),
        configuration_digest="property-16-local-evaluation",
        task_ids=("property-16-task",),
        checks=DEFAULT_NAMED_CHECKS,
        results=tuple(
            EvaluationCellResult(
                result_id=EvaluationResultId(f"property-16-result-{index}"),
                task_id="property-16-task",
                check_name=check.name,
                check_kind=check.kind,
                blocking=check.blocking,
                outcome=outcomes.get(check.kind, EvaluationOutcome.PASS),
                recorded_at=_NOW,
                evidence_digest=f"property-16-evidence-{index}",
            )
            for index, check in enumerate(DEFAULT_NAMED_CHECKS)
        ),
        completed=True,
        transition_permitted=case.evaluation_transition_permitted,
    )
    retained = fakes.evaluations.create(run)
    assert retained.is_success
    return run


def _propose_variants(
    case: PromotionCase, fakes: DeterministicLocalFakes
) -> tuple[SandboxVariant, ...]:
    """Create only sandbox variants, considering precisely the requested cardinality."""
    proposed: list[SandboxVariant] = []
    for index in range(max(1, case.candidate_count)):
        sandbox_configuration = {
            **case.sandbox_configuration,
            "sandbox_variant_index": index,
        }
        result = fakes.service.propose(
            _ORGANIZATION_ID,
            _CORRELATION_ID,
            case.production_configuration,
            sandbox_configuration,
            "conversion_rate",
            case.improvement_direction,
        )
        assert result.is_success
        variant = _require_value(result.value)
        proposed.append(variant)
        if index < case.candidate_count:
            considered = fakes.service.consider(
                _ORGANIZATION_ID, _CORRELATION_ID, variant.variant_id
            )
            assert considered.is_success
    return tuple(proposed)


def _target_metric(case: PromotionCase) -> MetricComparison:
    """Return a finite strict-improvement or equality boundary comparison."""
    if case.target_improved:
        candidate = 11.0 if case.improvement_direction is ImprovementDirection.INCREASE else 9.0
    else:
        candidate = 10.0
    return MetricComparison(baseline=10.0, candidate=candidate)


def _no_worse_metric(no_worse: bool) -> MetricComparison:
    """Return a no-worse equality boundary or a strictly worse local metric."""
    return MetricComparison(baseline=10.0, candidate=10.0 if no_worse else 9.0)


def _create_supporting_records(
    case: PromotionCase,
    fakes: DeterministicLocalFakes,
    variant: SandboxVariant,
) -> tuple[RollbackRecordId, CanaryId, PromotionApprovalId]:
    """Create only requested sandbox support records; canary approval stays inert."""
    rollback_id = _MISSING_ROLLBACK_ID
    if case.rollback_recorded:
        rollback = fakes.service.create_rollback_plan(
            _ORGANIZATION_ID,
            _CORRELATION_ID,
            variant.variant_id,
            {"action": "restore-sandbox-baseline"},
        )
        assert rollback.is_success
        rollback_id = _require_value(rollback.value).rollback_record_id

    canary_id = _MISSING_CANARY_ID
    if case.canary_approved and case.rollback_recorded:
        canary = fakes.service.approve_canary(
            _ORGANIZATION_ID,
            _ACTOR_ID,
            _CORRELATION_ID,
            variant.variant_id,
            CanaryScope(_ORGANIZATION_ID, workflow_id="property-16-workflow"),
            ("property-16-criterion",),
            rollback_id,
        )
        assert canary.is_success
        canary_record = _require_value(canary.value)
        assert canary_record.state is CanaryState.APPROVED
        canary_id = canary_record.canary_id

    approval_id = _MISSING_APPROVAL_ID
    if case.human_approved:
        approval = fakes.service.record_human_approval(
            _ORGANIZATION_ID,
            _ACTOR_ID,
            _CORRELATION_ID,
            variant.variant_id,
            "Approve the isolated local sandbox assessment.",
        )
        assert approval.is_success
        approval_id = _require_value(approval.value).approval_id
    return rollback_id, canary_id, approval_id


def _expected_conditions(case: PromotionCase) -> dict[str, bool]:
    """Derive the complete fail-closed decision matrix from bounded input facts."""
    one_candidate = case.candidate_count == 1
    selected = one_candidate and case.requested_candidate
    evaluation_permitted = case.evaluation_transition_permitted
    return {
        "exactly_one_candidate": selected,
        "target_metric_strictly_improved": selected and case.target_improved,
        "safety_no_worse": case.safety_no_worse,
        "compliance_no_worse": case.compliance_no_worse,
        "named_regression_checks_pass": (
            evaluation_permitted and case.regression_checks_pass
        ),
        "named_adversarial_checks_pass": (
            evaluation_permitted and case.adversarial_checks_pass
        ),
        "rollback_plan_recorded": one_candidate and case.rollback_recorded,
        "approved_scoped_canary": (
            one_candidate and case.rollback_recorded and case.canary_approved
        ),
        "complete_audit_records": case.audit_complete,
        "evidence_retained": case.evidence_retained,
        "recorded_human_approval": one_candidate and case.human_approved,
    }


def _assess(case: PromotionCase) -> tuple[PromotionDecision, dict[str, bool], tuple[str, ...]]:
    """Run one entirely local proposal and promotion assessment matrix cell."""
    fakes = _fakes()
    production_before = deepcopy(case.production_configuration)
    production_bytes_before = json.dumps(
        production_before, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    evaluation = _retain_evaluation(case, fakes)
    variants = _propose_variants(case, fakes)
    primary_variant = variants[0]
    rollback_id, canary_id, approval_id = _create_supporting_records(
        case, fakes, primary_variant
    )
    requested_variant_id = (
        primary_variant.variant_id if case.requested_candidate else _MISSING_VARIANT_ID
    )
    audit_record_ids = ("property-16-audit",) if case.audit_complete else ("",)
    evidence_references = (
        ("property-16-evidence",) if case.evidence_retained else ("",)
    )

    result = fakes.service.assess_promotion(
        _ORGANIZATION_ID,
        _CORRELATION_ID,
        requested_variant_id,
        evaluation.evaluation_run_id,
        _target_metric(case),
        _no_worse_metric(case.safety_no_worse),
        _no_worse_metric(case.compliance_no_worse),
        rollback_id,
        canary_id,
        audit_record_ids,
        evidence_references,
        approval_id,
    )
    assert result.is_success
    assessment = _require_value(result.value)
    expected_conditions = _expected_conditions(case)
    actual_conditions = {condition.name: condition for condition in assessment.conditions}

    assert tuple(actual_conditions) == tuple(expected_conditions)
    assert {
        name: condition.passed for name, condition in actual_conditions.items()
    } == expected_conditions
    expected_missing = tuple(name for name, passed in expected_conditions.items() if not passed)
    assert assessment.missing_or_failed_conditions == expected_missing
    assert actual_conditions["complete_audit_records"].evidence_references == audit_record_ids
    assert actual_conditions["evidence_retained"].evidence_references == evidence_references

    expected_decision = (
        PromotionDecision.PERMITTED
        if all(expected_conditions.values())
        else PromotionDecision.BLOCKED
    )
    assert assessment.decision is expected_decision
    assert assessment.production_applied is False
    assert fakes.evolution.promotion_permitted(
        _ORGANIZATION_ID, assessment.assessment_id
    ) is (expected_decision is PromotionDecision.PERMITTED)
    if not case.evidence_retained:
        continued = fakes.service.propose(
            _ORGANIZATION_ID,
            _CORRELATION_ID,
            case.production_configuration,
            {"workflow": {"name": "continued-sandbox-operation"}},
            "conversion_rate",
            case.improvement_direction,
        )
        assert continued.is_success
        assert not fakes.evolution.promotion_permitted(
            _ORGANIZATION_ID, assessment.assessment_id
        )

    assert case.production_configuration == production_before
    assert (
        json.dumps(
            case.production_configuration,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
        == production_bytes_before
    )
    return assessment.decision, expected_conditions, assessment.missing_or_failed_conditions


@settings(max_examples=100, deadline=None)
@example(
    case=PromotionCase(
        production_configuration={"workflow": {"name": "baseline", "steps": [1]}},
        sandbox_configuration={"workflow": {"name": "candidate", "steps": [2]}},
        improvement_direction=ImprovementDirection.INCREASE,
        candidate_count=1,
        requested_candidate=True,
        target_improved=True,
        safety_no_worse=True,
        compliance_no_worse=True,
        evaluation_transition_permitted=True,
        regression_checks_pass=True,
        adversarial_checks_pass=True,
        rollback_recorded=True,
        canary_approved=True,
        audit_complete=True,
        evidence_retained=False,
        human_approved=True,
    )
)
@given(case=_promotion_cases())
def test_evolution_variants_are_isolated_and_promotion_is_exhaustive(
    case: PromotionCase,
) -> None:
    """Every generated cardinality and gate combination permits only complete evidence."""
    decision, conditions, missing_conditions = _assess(case)

    if case.evidence_retained:
        return

    assert decision is PromotionDecision.BLOCKED
    assert not conditions["evidence_retained"]
    assert "evidence_retained" in missing_conditions
