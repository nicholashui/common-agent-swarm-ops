"""Property checks for directed evidence and approval-gate progression."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from typing import cast

from hypothesis import given, settings, strategies as st

from app.evidence.service import EvidenceService, GateEvaluator, GateRequirements
from app.models.common import RecordMetadata
from app.models.contracts import ErrorCode
from app.models.control_plane import (
    AgentTask,
    AgentVersionId,
    ApprovalGate,
    ApprovalGateId,
    ApprovalGateStatus,
    CritiqueRecord,
    QualityEvidence,
    QualityEvidenceKind,
    TaskId,
    TaskLifecycle,
)
from app.models.identifiers import CorrelationId, OrganizationId, RecordId
from app.repositories.control_plane import ControlPlaneUnitOfWork, InMemoryControlPlaneDatabase

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_ORGANIZATION = OrganizationId("property-12-organization")
_CORRELATION = CorrelationId("property-12-correlation")
_SAFE_VALUES = st.text(alphabet="abcdefghijklmnopqrstuvwxyz0123456789", min_size=1, max_size=12)
_DECISION_CASES = st.sampled_from(
    ("complete", "missing_value", "missing_reason", "missing_reviewer", "unauthorized")
)
_CATEGORY_VECTORS = st.tuples(
    st.tuples(st.booleans(), st.booleans()),
    st.tuples(st.booleans(), st.booleans()),
    st.tuples(st.booleans(), st.booleans()),
    st.tuples(st.booleans(), st.booleans()),
)


def _metadata(record_id: str, *, version: int = 1) -> RecordMetadata:
    return RecordMetadata(
        record_id=RecordId(record_id),
        organization_id=_ORGANIZATION,
        correlation_id=_CORRELATION,
        schema_version=1,
        version=version,
        created_at=_NOW,
        updated_at=_NOW,
    )


def _unit_of_work_factory(
    database: InMemoryControlPlaneDatabase,
) -> Callable[[], ControlPlaneUnitOfWork]:
    def factory() -> ControlPlaneUnitOfWork:
        return cast(ControlPlaneUnitOfWork, database.unit_of_work())

    return factory


def _services(database: InMemoryControlPlaneDatabase) -> tuple[EvidenceService, GateEvaluator]:
    factory = _unit_of_work_factory(database)
    return EvidenceService(factory, clock=lambda: _NOW), GateEvaluator(factory, clock=lambda: _NOW)


def _blocked_task(value: str, gate_id: ApprovalGateId) -> AgentTask:
    return AgentTask(
        metadata=_metadata(f"task-record-{value}"),
        task_id=TaskId(f"task-{value}"),
        run_reference=f"run-{value}",
        pinned_agent_version_id=AgentVersionId(f"agent-{value}"),
        dependencies=(),
        constraints={},
        approval_gate_ids=(gate_id,),
        checkpoint_reference=None,
        state=TaskLifecycle.BLOCKED,
        blocked_fields=("gate:pending",),
    )


def _critique(value: str, relationship: str) -> CritiqueRecord:
    return CritiqueRecord(
        metadata=_metadata(f"critique-record-{value}"),
        critique_id=f"critique-{value}",
        source_reference=f"agent-source-{value}",
        target_task_id=TaskId(f"target-{value}"),
        relationship_reference=relationship,
        evidence_reference=f"critique-evidence-{value}",
        submitted_at=_NOW,
    )


def _quality_evidence(value: str, kind: QualityEvidenceKind, passed: bool) -> QualityEvidence:
    return QualityEvidence(
        metadata=_metadata(f"evidence-record-{kind.value}-{value}"),
        evidence_id=f"evidence-{kind.value}-{value}",
        kind=kind,
        subject_reference=f"operation-{value}",
        passed=passed,
        evidence_reference=f"reference-{kind.value}-{value}",
        recorded_at=_NOW,
    )


def _decision_arguments(decision_case: str) -> tuple[str, str, str, bool]:
    if decision_case == "missing_value":
        return "", "reviewed", "reviewer", True
    if decision_case == "missing_reason":
        return "approve", "", "reviewer", True
    if decision_case == "missing_reviewer":
        return "approve", "reviewed", "", True
    if decision_case == "unauthorized":
        return "approve", "reviewed", "reviewer", False
    return "approve", "reviewed", "reviewer", True


# Feature: backend-redesign, Property 12
# **Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8**
@settings(max_examples=100)
@given(
    value=_SAFE_VALUES,
    relationship_published=st.booleans(),
    human_review_authorized=st.booleans(),
    category_vector=_CATEGORY_VECTORS,
    rights_and_consent_passed=st.booleans(),
    provenance_passed=st.booleans(),
    decision_case=_DECISION_CASES,
    authorization_recheck_passed=st.booleans(),
    policy_recheck_passed=st.booleans(),
)
def test_property_12_directed_evidence_and_approvals_gate_progression(
    value: str,
    relationship_published: bool,
    human_review_authorized: bool,
    category_vector: tuple[tuple[bool, bool], ...],
    rights_and_consent_passed: bool,
    provenance_passed: bool,
    decision_case: str,
    authorization_recheck_passed: bool,
    policy_recheck_passed: bool,
) -> None:
    """Only independently retained passing evidence and a valid server gate permit work."""
    database = InMemoryControlPlaneDatabase()
    evidence_service, evaluator = _services(database)
    gate_id = ApprovalGateId(f"gate-{value}")
    pending_operation = f"operation-{value}"
    task = _blocked_task(value, gate_id)
    relationship = f"agent-source-{value}->target-{value}"
    critique = _critique(value, relationship)

    with database.unit_of_work() as unit_of_work:
        assert unit_of_work.tasks.create(task).is_success
    created_gate = evidence_service.create_pending_gate(
        _ORGANIZATION,
        _metadata(f"gate-record-{value}"),
        gate_id,
        pending_operation,
    )
    assert created_gate.is_success and created_gate.value is not None
    assert created_gate.value.pending_operation_reference == pending_operation

    critique_result = evidence_service.submit_critique(
        _ORGANIZATION,
        critique,
        published_relationships=(relationship,) if relationship_published else (),
        human_review_authorized=human_review_authorized,
    )
    critique_permitted = relationship_published or human_review_authorized
    if critique_permitted:
        assert critique_result.is_success and critique_result.value == critique
        assert database._state.critiques == {critique.critique_id: critique}
    else:
        assert not critique_result.is_success
        assert critique_result.error is not None
        assert critique_result.error.code is ErrorCode.AUTHORIZATION_DENIED
        assert database._state.critiques == {}

    category_states = tuple(zip(tuple(QualityEvidenceKind), category_vector, strict=True))
    for kind, (present, passed) in category_states:
        if present:
            retained = evidence_service.retain_quality_evidence(
                _ORGANIZATION, _quality_evidence(value, kind, passed)
            )
            assert retained.is_success and retained.value is not None

    expected_missing = tuple(kind for kind, (present, _) in category_states if not present)
    expected_failed = tuple(
        kind for kind, (present, passed) in category_states if present and not passed
    )
    expected_evidence_ids = {
        f"evidence-{kind.value}-{value}" for kind, (present, _) in category_states if present
    }
    assert set(database._state.quality_evidence) == expected_evidence_ids
    assert {evidence.kind for evidence in database._state.quality_evidence.values()} == {
        kind for kind, (present, _) in category_states if present
    }

    decision, reason, reviewer, reviewer_authorized = _decision_arguments(decision_case)
    submitted_decision = evidence_service.submit_human_decision(
        _ORGANIZATION,
        _CORRELATION,
        gate_id,
        decision=decision,
        decision_reason=reason,
        reviewer_reference=reviewer,
        reviewer_authorized=reviewer_authorized,
    )
    assert submitted_decision.is_success and submitted_decision.value is not None
    decision_valid = decision_case == "complete"
    assert submitted_decision.value.accepted is decision_valid

    recheck_calls: list[str] = []

    def authorization_recheck(_: ApprovalGate) -> bool:
        recheck_calls.append("authorization")
        return authorization_recheck_passed

    def policy_recheck(_: ApprovalGate) -> bool:
        recheck_calls.append("policy")
        return policy_recheck_passed

    outcome_result = evaluator.evaluate(
        _ORGANIZATION,
        _CORRELATION,
        pending_operation,
        gate_id,
        GateRequirements(),
        rights_and_consent_passed=rights_and_consent_passed,
        provenance_passed=provenance_passed,
        authorization_recheck=authorization_recheck,
        policy_recheck=policy_recheck,
        affected_task_id=task.task_id,
    )
    assert outcome_result.is_success and outcome_result.value is not None
    outcome = outcome_result.value

    aggregate_score = sum(present and passed for _, (present, passed) in category_states)
    categories_pass = not expected_missing and not expected_failed
    ready_for_rechecks = (
        categories_pass and rights_and_consent_passed and provenance_passed and decision_valid
    )
    expected_progression = (
        ready_for_rechecks and authorization_recheck_passed and policy_recheck_passed
    )
    assert outcome.missing_evidence_kinds == expected_missing
    assert outcome.failed_evidence_kinds == expected_failed
    assert outcome.progression_permitted is expected_progression
    assert outcome.progression_permitted is (
        (aggregate_score == len(QualityEvidenceKind))
        and rights_and_consent_passed
        and provenance_passed
        and decision_valid
        and authorization_recheck_passed
        and policy_recheck_passed
    )
    assert recheck_calls == (["authorization", "policy"] if ready_for_rechecks else [])

    stored_gate = database._state.approvals[gate_id]
    assert stored_gate.status is (
        ApprovalGateStatus.APPROVED if expected_progression else ApprovalGateStatus.PENDING
    )
    stored_task = database._state.tasks[task.task_id]
    if expected_progression:
        assert stored_task.state is TaskLifecycle.IDLE
        assert stored_task.blocked_fields == ()
    else:
        assert stored_task.state is TaskLifecycle.BLOCKED
        if not categories_pass:
            assert "gate:pending" in stored_task.blocked_fields
        if not decision_valid:
            assert stored_gate.decision is None
            assert stored_gate.decision_reason is None
            assert stored_gate.reviewer_reference is None
            assert recheck_calls == []
