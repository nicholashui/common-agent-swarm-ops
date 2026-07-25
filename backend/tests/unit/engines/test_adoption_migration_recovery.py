"""Deterministic migration rollback, contract approval, and recovery tests."""

from __future__ import annotations

from datetime import UTC, datetime

from app.engines.migration import MigrationController
from app.engines.recovery import (
    ContractChangeEvidence,
    InMemoryImmutableVersionStore,
    InMemoryLessonRetentionService,
    InMemoryRollbackEvidenceRepository,
    MigrationRollbackRequest,
    MigrationRollbackStatus,
    RecoveryService,
)
from app.evaluation.migration_evidence import (
    InMemoryMigrationEvidenceRepository,
    MigrationEvidenceService,
    WorkflowActivationEvidence,
    WorkflowActivationStatus,
)
from app.models.common import CompatibilityRange, RecordMetadata
from app.models.control_plane import (
    AgentNodeAttemptId,
    RecoveryActionStatus,
)
from app.models.evidence import Lesson, LessonAssessmentOutcome
from app.models.identifiers import (
    AgentId,
    CorrelationId,
    DomainId,
    DomainPackId,
    OrganizationId,
    RecordId,
)
from tests.fakes.adoption import DeterministicAdoptionRepositories, FakeFailurePlan

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_ORGANIZATION = OrganizationId("organization-migration-recovery")
_PACK = DomainPackId("va-agent-swarm")
_CORRELATION = CorrelationId("correlation-migration-recovery")


def _metadata(record_id: str) -> RecordMetadata:
    return RecordMetadata(
        record_id=RecordId(record_id),
        organization_id=_ORGANIZATION,
        correlation_id=_CORRELATION,
        schema_version=1,
        version=1,
        created_at=_NOW,
        updated_at=_NOW,
    )


def _lesson() -> Lesson:
    return Lesson(
        metadata=_metadata("lesson-record-1"),
        lesson_id="lesson-1",  # type: ignore[arg-type]
        organization_id=_ORGANIZATION,
        domain_id=DomainId("video"),
        pack_version_range=CompatibilityRange.exact("2.0.0"),
        agent_id=AgentId("agent-1"),
        memory_scope="agent:agent-1",
        assessment=LessonAssessmentOutcome.PASSED,
        source_episode_references=(str(AgentNodeAttemptId("episode-1")),),
        content_reference="lesson-content-reference",
        assessed_at=_NOW,
        retrievable=True,
    )


def _service(
    *,
    failure_plan: FakeFailurePlan | None = None,
    rollback_evidence: InMemoryRollbackEvidenceRepository | None = None,
) -> tuple[
    RecoveryService,
    DeterministicAdoptionRepositories,
    InMemoryImmutableVersionStore,
    InMemoryLessonRetentionService,
    InMemoryRollbackEvidenceRepository,
]:
    repositories = DeterministicAdoptionRepositories(failure_plan)
    versions = InMemoryImmutableVersionStore()
    versions.approve_version(_ORGANIZATION, _PACK, "2.0.0")
    retention = InMemoryLessonRetentionService()
    evidence = rollback_evidence or InMemoryRollbackEvidenceRepository()
    service = RecoveryService(
        repositories.recoveries,
        versions,
        retention,
        evidence,
        clock=lambda: _NOW,
    )
    return service, repositories, versions, retention, evidence


def test_migration_phase_retains_scope_exit_rollback_and_owner_reviews() -> None:
    """A phase cannot begin without complete scope, exit, rollback, and review evidence."""
    repository = InMemoryMigrationEvidenceRepository()
    migration_evidence = MigrationEvidenceService(repository, clock=lambda: _NOW)
    controller = MigrationController(migration_evidence)

    result = controller.start_phase(
        _CORRELATION,
        phase_id="phase-freeze",
        phase_scope=("source-baseline", "va-roster"),
        required_evidence=("source-index", "roster-mapping"),
        exit_criteria=("all-assets-dispositioned",),
        rollback_procedure="rollback-to-approved-pack",
        host_owner_review="host-review-1",
        va_owner_review="va-review-1",
    )

    assert result.is_success and result.value is not None
    assert result.value.phase_scope == ("source-baseline", "va-roster")
    assert result.value.required_evidence == ("source-index", "roster-mapping")
    assert result.value.exit_criteria == ("all-assets-dispositioned",)
    assert result.value.rollback_procedure == "rollback-to-approved-pack"
    assert result.value.host_owner_review == "host-review-1"
    assert result.value.va_owner_review == "va-review-1"
    assert repository.phases() == (result.value,)


def test_activation_requires_complete_evidence_and_explicit_approval() -> None:
    """Eligibility alone, or a pending/denied approval, cannot activate a workflow."""
    repository = InMemoryMigrationEvidenceRepository()
    migration_evidence = MigrationEvidenceService(repository, clock=lambda: _NOW)
    controller = MigrationController(migration_evidence)
    incomplete = WorkflowActivationEvidence(
        workflow_id="va.workflow",
        domain_evaluations=(True, False),
        reproducible_trace=True,
        human_approvals=(True,),
        maturity_level="registered",
        designated_approval_evaluation=True,
    )

    ineligible = controller.evaluate_activation_eligibility(_CORRELATION, incomplete)

    assert ineligible.is_success and ineligible.value is not None
    assert ineligible.value.status is WorkflowActivationStatus.INELIGIBLE
    assert not migration_evidence.activate_workflow(_CORRELATION, "va.workflow").is_success

    complete = WorkflowActivationEvidence(
        workflow_id="va.workflow",
        domain_evaluations=(True,),
        reproducible_trace=True,
        human_approvals=(True,),
        maturity_level="activation-ready",
        designated_approval_evaluation=True,
    )
    eligible = controller.evaluate_activation_eligibility(_CORRELATION, complete)

    assert eligible.is_success and eligible.value is not None
    assert eligible.value.status is WorkflowActivationStatus.ACTIVATION_ELIGIBLE
    pending = migration_evidence.activate_workflow(_CORRELATION, "va.workflow")
    assert not pending.is_success

    denied_approval = controller.approve_activation(
        _CORRELATION,
        approval_id="approval-denied",
        workflow_id="va.workflow",
        reviewer_identity="reviewer-1",
        decision_reason="additional review required",
        approved=False,
    )
    assert denied_approval.is_success and denied_approval.value is not None
    denied_activation = migration_evidence.activate_workflow(_CORRELATION, "va.workflow")
    assert not denied_activation.is_success

    approved = controller.approve_activation(
        _CORRELATION,
        approval_id="approval-approved",
        workflow_id="va.workflow",
        reviewer_identity="reviewer-1",
        decision_reason="activation evidence approved",
    )
    activated = migration_evidence.activate_workflow(_CORRELATION, "va.workflow")

    assert approved.is_success and approved.value is not None
    assert activated.is_success and activated.value is not None
    assert activated.value.status is WorkflowActivationStatus.ACTIVE
    assert activated.value.activation_approval_id == "approval-approved"


def test_contract_change_approval_requires_every_named_artifact() -> None:
    service, _, _, _, _ = _service()
    incomplete = ContractChangeEvidence(
        architecture_decision_record="adr-1",
        migration_plan="migration-1",
        consumer_compatibility_evidence="consumer-1",
        deprecation_window="",
        rollback_plan="rollback-1",
    )

    blocked = service.approve_contract_change(_CORRELATION, incomplete)
    assessed = service.evaluate_contract_change(_CORRELATION, incomplete)

    assert not blocked.is_success
    assert blocked.error is not None
    assert "deprecation_window" in {field.name for field in blocked.error.fields}
    assert assessed.is_success and assessed.value is not None
    assert not assessed.value.approved

    complete = ContractChangeEvidence(
        architecture_decision_record="adr-1",
        migration_plan="migration-1",
        consumer_compatibility_evidence="consumer-1",
        deprecation_window="window-1",
        rollback_plan="rollback-1",
    )
    approved = service.approve_contract_change(_CORRELATION, complete, change_id="change-1")

    assert approved.is_success and approved.value is not None
    assert approved.value.approved
    assert approved.value.evidence.references == (
        "adr-1",
        "migration-1",
        "consumer-1",
        "window-1",
        "rollback-1",
    )


def test_approved_migration_rollback_retains_evidence_applies_alc_policy_and_restores_target() -> (
    None
):
    service, _, versions, retention, evidence = _service()
    request = MigrationRollbackRequest(
        organization_id=_ORGANIZATION,
        pack_id=_PACK,
        designated_immutable_version="2.0.0",
        approval_reference="approval-rollback-1",
        affected_lessons=(_lesson(),),
        alc_retention_policy="stale",
        evidence_references=("investigation-rollback-1",),
        rollback_id="rollback-1",
        approved=True,
    )

    result = service.rollback(_CORRELATION, request)

    assert result.is_success and result.value is not None
    assert result.value.status is MigrationRollbackStatus.RESTORED
    assert result.value.restored_immutable_version == "2.0.0"
    assert result.value.retention_records[0].lesson_reference == "lesson-1"
    assert result.value.retention_records[0].outcome.value == "stale"
    assert retention.calls == [(_PACK, "2.0.0", ("lesson-1",), "stale")]
    assert versions.current_versions[(_ORGANIZATION, _PACK)] == "2.0.0"
    assert evidence.records[-1].status is MigrationRollbackStatus.RESTORED

    retried = service.rollback(_CORRELATION, request)
    assert retried.is_success and retried.value == result.value
    assert len(versions.restore_calls) == 1
    assert len(evidence.records) == 1


def test_rollback_evidence_failure_halts_before_restore() -> None:
    rollback_evidence = InMemoryRollbackEvidenceRepository(fail_writes=True)
    service, _, versions, retention, _ = _service(rollback_evidence=rollback_evidence)
    request = MigrationRollbackRequest(
        organization_id=_ORGANIZATION,
        pack_id=_PACK,
        designated_immutable_version="2.0.0",
        approval_reference="approval-rollback-2",
        alc_retention_policy="retain",
        rollback_id="rollback-2",
        approved=True,
    )

    result = service.rollback(_CORRELATION, request)

    assert not result.is_success
    assert result.error is not None
    assert result.error.code.value == "repository_unavailable"
    assert versions.restore_calls == []
    assert retention.calls == []


def test_recovery_requires_investigation_evidence_and_completed_retry_is_idempotent() -> None:
    failure_plan = FakeFailurePlan()
    service, repositories, versions, _, _ = _service(failure_plan=failure_plan)

    missing_evidence = service.recover(
        _CORRELATION,
        organization_id=_ORGANIZATION,
        recovery_action_id="recovery-1",  # type: ignore[arg-type]
        pack_id=_PACK,
        designated_immutable_version="2.0.0",
        approval_reference="approval-recovery-1",
        investigation_evidence_references=(),
    )
    assert not missing_evidence.is_success
    assert versions.restore_calls == []

    failure_plan.fail_next_persistence("recovery.append")
    blocked = service.recover(
        _CORRELATION,
        organization_id=_ORGANIZATION,
        recovery_action_id="recovery-1",  # type: ignore[arg-type]
        pack_id=_PACK,
        designated_immutable_version="2.0.0",
        approval_reference="approval-recovery-1",
        investigation_evidence_references=("investigation-1",),
        approved=True,
    )
    assert not blocked.is_success
    assert versions.restore_calls == []
    assert repositories.recoveries.records() == ()

    restored = service.recover(
        _CORRELATION,
        organization_id=_ORGANIZATION,
        recovery_action_id="recovery-1",  # type: ignore[arg-type]
        pack_id=_PACK,
        designated_immutable_version="2.0.0",
        approval_reference="approval-recovery-1",
        investigation_evidence_references=("investigation-1",),
        approved=True,
    )

    assert restored.is_success and restored.value is not None
    assert restored.value.status is RecoveryActionStatus.RESTORED
    assert restored.value.restored_immutable_version == "2.0.0"
    assert len(versions.restore_calls) == 1

    retried = service.recover(
        _CORRELATION,
        organization_id=_ORGANIZATION,
        recovery_action_id="recovery-1",  # type: ignore[arg-type]
        pack_id=_PACK,
        designated_immutable_version="2.0.0",
        approval_reference="approval-recovery-1",
        investigation_evidence_references=("investigation-1",),
        approved=True,
    )
    assert retried.is_success and retried.value == restored.value
    assert len(versions.restore_calls) == 1


def test_migration_controller_exposes_recovery_and_fails_closed_without_composition() -> None:
    migration_evidence = MigrationEvidenceService(
        InMemoryMigrationEvidenceRepository(), clock=lambda: _NOW
    )
    unconfigured = MigrationController(migration_evidence)
    request = MigrationRollbackRequest(
        organization_id=_ORGANIZATION,
        pack_id=_PACK,
        designated_immutable_version="2.0.0",
        approval_reference="approval-controller-1",
        approved=True,
    )

    denied = unconfigured.rollback(_CORRELATION, request)
    assert not denied.is_success

    service, _, _, _, _ = _service()
    configured = MigrationController(migration_evidence, service)
    restored = configured.rollback(_CORRELATION, request)
    assert restored.is_success and restored.value is not None
