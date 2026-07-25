"""Focused deterministic EvidenceService and GateEvaluator tests for task 9.3."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from typing import cast

from app.evidence.service import EvidenceService, GateEvaluator, GateRequirements
from app.models.common import RecordMetadata
from app.models.contracts import ErrorCode
from app.models.control_plane import (
    AgentTask,
    AgentVersionId,
    ApprovalGate,
    ApprovalGateId,
    CritiqueRecord,
    QualityEvidence,
    QualityEvidenceKind,
    TaskId,
    TaskLifecycle,
)
from app.models.identifiers import CorrelationId, OrganizationId, RecordId
from app.repositories.control_plane import ControlPlaneUnitOfWork, InMemoryControlPlaneDatabase

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_ORGANIZATION = OrganizationId("evidence-service-organization")
_CORRELATION = CorrelationId("evidence-service-correlation")
_GATE_ID = ApprovalGateId("evidence-gate")
_SUBJECT = "task:evidence-subject"


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
    return (
        EvidenceService(factory, clock=lambda: _NOW),
        GateEvaluator(factory, clock=lambda: _NOW),
    )


def _evidence(kind: QualityEvidenceKind, *, passed: bool = True) -> QualityEvidence:
    return QualityEvidence(
        metadata=_metadata(f"evidence-record-{kind.value}"),
        evidence_id=f"evidence-{kind.value}",
        kind=kind,
        subject_reference=_SUBJECT,
        passed=passed,
        evidence_reference=f"reference-{kind.value}",
        recorded_at=_NOW,
    )


def _dependent_task() -> AgentTask:
    return AgentTask(
        metadata=_metadata("dependent-task-record"),
        task_id=TaskId("dependent-task"),
        run_reference="run-evidence",
        pinned_agent_version_id=AgentVersionId("agent-evidence-v1"),
        dependencies=(),
        constraints={},
        approval_gate_ids=(_GATE_ID,),
        checkpoint_reference=None,
        state=TaskLifecycle.IDLE,
    )


def _create_pending_gate(service: EvidenceService) -> None:
    created = service.create_pending_gate(
        _ORGANIZATION,
        _metadata("approval-gate-record"),
        _GATE_ID,
        "server-operation:evidence-subject",
    )
    assert created.is_success and created.value is not None


def test_unpermitted_critique_is_rejected_before_it_is_retained() -> None:
    """A source cannot deliver a critique outside a published or authorized direction."""
    database = InMemoryControlPlaneDatabase()
    service, _ = _services(database)
    critique = CritiqueRecord(
        metadata=_metadata("critique-record"),
        critique_id="critique-focused",
        source_reference="agent:untrusted",
        target_task_id=TaskId("target-task"),
        relationship_reference="agent:untrusted->target-task",
        evidence_reference="critique-evidence",
        submitted_at=_NOW,
    )

    rejected = service.submit_critique(
        _ORGANIZATION,
        critique,
        published_relationships=("agent:authorized->target-task",),
        human_review_authorized=False,
    )

    assert not rejected.is_success
    assert rejected.error is not None
    assert rejected.error.code is ErrorCode.AUTHORIZATION_DENIED
    assert database._state.critiques == {}


def test_independent_evidence_categories_are_retained_separately() -> None:
    """L1, L2, L3, and gate records remain distinct rather than becoming an aggregate."""
    database = InMemoryControlPlaneDatabase()
    service, _ = _services(database)

    for kind in QualityEvidenceKind:
        assert service.retain_quality_evidence(_ORGANIZATION, _evidence(kind)).is_success

    retained = database._state.quality_evidence
    assert set(retained) == {f"evidence-{kind.value}" for kind in QualityEvidenceKind}
    assert {evidence.kind for evidence in retained.values()} == set(QualityEvidenceKind)
    assert all(
        retained[f"evidence-{kind.value}"].evidence_reference == f"reference-{kind.value}"
        for kind in QualityEvidenceKind
    )


def test_missing_decision_value_or_reason_leaves_server_gate_pending() -> None:
    """An approval value and reason must both be recorded before the server gate advances."""
    database = InMemoryControlPlaneDatabase()
    service, _ = _services(database)
    _create_pending_gate(service)

    missing_value = service.submit_human_decision(
        _ORGANIZATION,
        _CORRELATION,
        _GATE_ID,
        decision="",
        decision_reason="reviewed",
        reviewer_reference="reviewer",
        reviewer_authorized=True,
    )
    missing_reason = service.submit_human_decision(
        _ORGANIZATION,
        _CORRELATION,
        _GATE_ID,
        decision="approve",
        decision_reason="",
        reviewer_reference="reviewer",
        reviewer_authorized=True,
    )

    assert missing_value.is_success and missing_value.value is not None
    assert not missing_value.value.accepted
    assert missing_reason.is_success and missing_reason.value is not None
    assert not missing_reason.value.accepted
    gate = database._state.approvals[_GATE_ID]
    assert gate.status.value == "pending"
    assert gate.decision is None
    assert gate.decision_reason is None


def test_pending_gate_blocks_effectful_progression_without_rechecks() -> None:
    """A pending server-owned operation cannot resume even when every evidence category passes."""
    database = InMemoryControlPlaneDatabase()
    service, evaluator = _services(database)
    _create_pending_gate(service)
    task = _dependent_task()
    with database.unit_of_work() as unit_of_work:
        assert unit_of_work.tasks.create(task).is_success
    for kind in QualityEvidenceKind:
        assert service.retain_quality_evidence(_ORGANIZATION, _evidence(kind)).is_success
    rechecks: list[str] = []

    def authorization_recheck(_: ApprovalGate) -> bool:
        rechecks.append("authorization")
        return True

    def policy_recheck(_: ApprovalGate) -> bool:
        rechecks.append("policy")
        return True

    outcome = evaluator.evaluate(
        _ORGANIZATION,
        _CORRELATION,
        _SUBJECT,
        _GATE_ID,
        GateRequirements(),
        rights_and_consent_passed=True,
        provenance_passed=True,
        authorization_recheck=authorization_recheck,
        policy_recheck=policy_recheck,
        affected_task_id=task.task_id,
    )

    assert outcome.is_success and outcome.value is not None
    assert not outcome.value.progression_permitted
    assert outcome.value.gate.status.value == "pending"
    assert rechecks == []
    stored_task = database._state.tasks[task.task_id]
    assert stored_task.state is TaskLifecycle.BLOCKED


def test_valid_retained_evidence_and_rechecks_permit_progression() -> None:
    """Only every category, a valid server gate, and current checks allow progression."""
    database = InMemoryControlPlaneDatabase()
    service, evaluator = _services(database)
    _create_pending_gate(service)
    for kind in QualityEvidenceKind:
        assert service.retain_quality_evidence(_ORGANIZATION, _evidence(kind)).is_success
    decision = service.submit_human_decision(
        _ORGANIZATION,
        _CORRELATION,
        _GATE_ID,
        decision="approve",
        decision_reason="evidence complete",
        reviewer_reference="authorized-reviewer",
        reviewer_authorized=True,
    )
    checks: list[str] = []

    def authorization_recheck(_: ApprovalGate) -> bool:
        checks.append("authorization")
        return True

    def policy_recheck(_: ApprovalGate) -> bool:
        checks.append("policy")
        return True

    outcome = evaluator.evaluate(
        _ORGANIZATION,
        _CORRELATION,
        _SUBJECT,
        _GATE_ID,
        GateRequirements(),
        rights_and_consent_passed=True,
        provenance_passed=True,
        authorization_recheck=authorization_recheck,
        policy_recheck=policy_recheck,
    )

    assert decision.is_success and decision.value is not None and decision.value.accepted
    assert outcome.is_success and outcome.value is not None
    assert outcome.value.progression_permitted
    assert outcome.value.gate.status.value == "approved"
    assert checks == ["authorization", "policy"]


def test_failed_policy_recheck_returns_gate_to_pending_without_resuming() -> None:
    """An approved human decision cannot bypass a current server policy failure."""
    database = InMemoryControlPlaneDatabase()
    service, evaluator = _services(database)
    _create_pending_gate(service)
    for kind in QualityEvidenceKind:
        assert service.retain_quality_evidence(_ORGANIZATION, _evidence(kind)).is_success
    approved = service.submit_human_decision(
        _ORGANIZATION,
        _CORRELATION,
        _GATE_ID,
        decision="approve",
        decision_reason="reviewed",
        reviewer_reference="authorized-reviewer",
        reviewer_authorized=True,
    )

    outcome = evaluator.evaluate(
        _ORGANIZATION,
        _CORRELATION,
        _SUBJECT,
        _GATE_ID,
        GateRequirements(),
        rights_and_consent_passed=True,
        provenance_passed=True,
        authorization_recheck=lambda _: True,
        policy_recheck=lambda _: False,
    )

    assert approved.is_success and approved.value is not None and approved.value.accepted
    assert outcome.is_success and outcome.value is not None
    assert not outcome.value.progression_permitted
    assert outcome.value.gate.status.value == "pending"
    assert outcome.value.gate.decision == "approve"
    assert database._state.approvals[_GATE_ID].status.value == "pending"
