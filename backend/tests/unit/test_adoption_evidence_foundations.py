"""Deterministic contract and persistence tests for adoption evidence foundations."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime

import pytest

from app.models.common import CompatibilityRange, RecordMetadata
from app.models.contracts import DomainPack, PackContract
from app.models.control_plane import (
    AgentNodeAttemptId,
    ArtifactHandoff,
    ArtifactHandoffId,
    AuditRecord,
    CompatibilityStatus,
    InvocationAssociation,
    LearningEpisodeId,
    Registration,
    RegistrationDecision,
    RegistrationId,
    ReleaseReadinessDecision,
    ReleaseReadinessDecisionId,
    ReleaseReadinessStatus,
    RetrievalRecordId,
    TaskId,
    VerificationCoverageStatus,
    VerificationRun,
    VerificationRunId,
)
from app.models.evidence import (
    LearningEpisode,
    LearningTerminalOutcome,
    Lesson,
    LessonAssessmentOutcome,
    RetrievalRecord,
)
from app.models.identifiers import (
    ActorId,
    AgentId,
    CorrelationId,
    DomainId,
    DomainPackId,
    OrganizationId,
    RecordId,
)
from tests.fakes.adoption import DeterministicAdoptionRepositories, FakeFailurePlan
from tests.fakes.provider import MockProviderAdapter, ProviderFailureMode

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_ORGANIZATION = OrganizationId("organization-adoption")
_CORRELATION = CorrelationId("correlation-adoption")


def _metadata(record_id: str, correlation_id: CorrelationId = _CORRELATION) -> RecordMetadata:
    return RecordMetadata(
        record_id=RecordId(record_id),
        organization_id=_ORGANIZATION,
        correlation_id=correlation_id,
        schema_version=1,
        version=1,
        created_at=_NOW,
        updated_at=_NOW,
    )


def _pack(
    *,
    immutable_version: str = "1.0.0",
    pack_contract_version: str = "1.0.0",
    required_alc_version: str | None = "1.0.0",
) -> DomainPack:
    return DomainPack(
        pack_id=DomainPackId("pack-adoption"),
        immutable_version=immutable_version,
        pack_contract_version=pack_contract_version,
        host_compatibility_range=CompatibilityRange.exact("1.0.0"),
        alc_compatibility_range=CompatibilityRange.exact("1.0.0"),
        content_digest=f"sha256:{immutable_version}",
        signer_id=ActorId("owner-adoption"),
        agents=(AgentId("agent-adoption"),),
        workflows=("workflow-adoption",),
        capabilities=("memory.read",),
        data_classifications=("internal",),
        evaluation_references=("evaluation:adoption",),
        required_alc_version=required_alc_version,
        asset_references=(f"asset:{immutable_version}",),
    )


def _registration(
    record_id: str,
    registration_id: str,
    *,
    immutable_version: str = "1.0.0",
    validation_result: bool = True,
    decision: RegistrationDecision = RegistrationDecision.APPROVED,
    failed_validation_categories: tuple[str, ...] = (),
) -> Registration:
    return Registration(
        metadata=_metadata(record_id),
        registration_id=RegistrationId(registration_id),
        pack_id=DomainPackId("pack-adoption"),
        immutable_version=immutable_version,
        content_digest=f"sha256:{immutable_version}",
        signer_id=ActorId("owner-adoption"),
        host_compatibility_range=CompatibilityRange.exact("1.0.0"),
        alc_compatibility_range=CompatibilityRange.exact("1.0.0"),
        validation_result=validation_result,
        decision=decision,
        compatibility_status=CompatibilityStatus.COMPATIBLE,
        asset_references=(f"asset:{immutable_version}",),
        failed_validation_categories=failed_validation_categories,
    )


def _audit(
    record_id: str, audit_id: str, *, correlation_id: CorrelationId = _CORRELATION
) -> AuditRecord:
    return AuditRecord(
        metadata=_metadata(record_id, correlation_id),
        audit_id=audit_id,
        action="adoption.denied",
        subject_reference="pack-adoption",
        outcome="denied",
        recorded_at=_NOW,
    )


def _retrieval(
    record_id: str,
    retrieval_id: str,
    *,
    attempt_id: AgentNodeAttemptId | None = None,
) -> RetrievalRecord:
    resolved_attempt_id = attempt_id or AgentNodeAttemptId("attempt-adoption")
    return RetrievalRecord(
        metadata=_metadata(record_id),
        retrieval_record_id=RetrievalRecordId(retrieval_id),
        attempt_id=resolved_attempt_id,
        organization_id=_ORGANIZATION,
        domain_id=DomainId("domain-adoption"),
        pack_version="1.0.0",
        agent_id=AgentId("agent-adoption"),
        memory_scope="agent:agent-adoption",
        retrieved_at=_NOW,
    )


def _episode(
    record_id: str,
    episode_id: str,
    *,
    attempt_id: AgentNodeAttemptId | None = None,
    blocked_for_recovery: bool = False,
) -> LearningEpisode:
    resolved_attempt_id = attempt_id or AgentNodeAttemptId("attempt-adoption")
    return LearningEpisode(
        metadata=_metadata(record_id),
        episode_id=LearningEpisodeId(episode_id),
        attempt_id=resolved_attempt_id,
        organization_id=_ORGANIZATION,
        domain_id=DomainId("domain-adoption"),
        pack_version="1.0.0",
        agent_id=AgentId("agent-adoption"),
        terminal_outcome=LearningTerminalOutcome.BLOCKED
        if blocked_for_recovery
        else LearningTerminalOutcome.COMPLETED,
        outcome_reference="outcome-reference",
        recorded_at=_NOW,
        blocked_for_recovery=blocked_for_recovery,
    )


def _release_decision(record_id: str, decision_id: str) -> ReleaseReadinessDecision:
    return ReleaseReadinessDecision(
        metadata=_metadata(record_id),
        decision_id=ReleaseReadinessDecisionId(decision_id),
        pack_id=DomainPackId("pack-adoption"),
        immutable_version="1.0.0",
        workflow_id="workflow-adoption",
        status=ReleaseReadinessStatus.ELIGIBLE,
        integration_coverage_complete=True,
        evidence_references=("verification:adoption",),
    )


def test_pack_schema_validation_and_registration_evidence_are_fail_closed() -> None:
    contract = PackContract(version="1.0.0")
    valid_pack = _pack()
    missing_alc = _pack(required_alc_version=None)

    assert contract.validate(valid_pack) == ()
    assert contract.validate(missing_alc) == ("required_alc_version",)

    registration = _registration("registration-record", "registration-1")
    assert registration.identity_key == (DomainPackId("pack-adoption"), "1.0.0")
    assert registration.validation_result
    assert registration.decision is RegistrationDecision.APPROVED
    assert registration.asset_references == ("asset:1.0.0",)

    rejected = _registration(
        "rejection-record",
        "registration-rejected",
        validation_result=False,
        decision=RegistrationDecision.REJECTED,
        failed_validation_categories=("evaluation_references",),
    )
    assert rejected.decision is RegistrationDecision.REJECTED
    assert rejected.failed_validation_categories == ("evaluation_references",)

    with pytest.raises(ValueError, match="Approved registrations"):
        _registration(
            "invalid-registration",
            "registration-invalid",
            validation_result=False,
        )


def test_immutable_registration_and_pack_version_uniqueness_are_preserved() -> None:
    repositories = DeterministicAdoptionRepositories()
    first = _registration("registration-record-1", "registration-1")
    duplicate_identity = _registration("registration-record-2", "registration-2")

    assert repositories.registrations.append(first).is_success
    conflict = repositories.registrations.append(duplicate_identity)

    assert not conflict.is_success
    assert repositories.registrations.records() == (first,)
    with pytest.raises(FrozenInstanceError):
        first.immutable_version = "2.0.0"  # type: ignore[misc]

    stored = repositories.registrations.get_by_pack_version(
        _ORGANIZATION, DomainPackId("pack-adoption"), "1.0.0"
    )
    assert stored.is_success and stored.value == first


def test_reference_only_evidence_freezes_nested_metadata_and_content_references() -> None:
    specification = {"specification_reference": "spec:adoption", "digest": "sha256:spec"}
    handoff = ArtifactHandoff(
        metadata=_metadata("handoff-record"),
        handoff_id=ArtifactHandoffId("handoff-1"),
        artifact_identity="artifact-adoption",
        artifact_version="1.0.0",
        parent_lineage=(),
        source_task_id=TaskId("task-adoption"),
        source_run_reference="run-adoption",
        brief_scope="brief:adoption",
        technical_specification=specification,
        rights_and_consent_state="approved",
        continuity_state="continuous",
        quality_control_state="passed",
        target_channels=("internal",),
        provenance_reference="provenance:adoption",
        owner_reference="owner:adoption",
        classification="internal",
        integrity_reference="sha256:artifact",
        approval_reference="approval:adoption",
    )
    lesson = Lesson(
        metadata=_metadata("lesson-record"),
        lesson_id="lesson-1",  # type: ignore[arg-type]
        organization_id=_ORGANIZATION,
        domain_id=DomainId("domain-adoption"),
        pack_version_range=CompatibilityRange.exact("1.0.0"),
        agent_id=AgentId("agent-adoption"),
        memory_scope="agent:agent-adoption",
        assessment=LessonAssessmentOutcome.PASSED,
        source_episode_references=("episode:adoption",),
        content_reference="content:lesson-adoption",
        assessed_at=_NOW,
        retrievable=True,
    )

    specification["digest"] = "sha256:changed"
    assert handoff.technical_specification is not None
    assert handoff.technical_specification["digest"] == "sha256:spec"
    assert lesson.content_reference == "content:lesson-adoption"
    assert not hasattr(lesson, "content")
    with pytest.raises(TypeError):
        handoff.technical_specification["raw_content"] = "must-not-be-stored"  # type: ignore[index]


def test_invocation_denial_audit_and_associated_evidence_propagate_correlation() -> None:
    plan = FakeFailurePlan()
    repositories = DeterministicAdoptionRepositories(plan)

    plan.fail_next_persistence("invocation.append")
    association_record = InvocationAssociation(
        metadata=_metadata("invocation-record"),
        invocation_id="invocation-adoption",  # type: ignore[arg-type]
        organization_id=_ORGANIZATION,
        domain_id=DomainId("domain-adoption"),
        pack_version="1.0.0",
        agent_id=AgentId("agent-adoption"),
        workflow_id="workflow-adoption",
        run_id="run-adoption",  # type: ignore[arg-type]
        correlation_id=_CORRELATION,
    )
    denied = repositories.invocations.append(association_record)

    assert not denied.is_success
    assert repositories.invocations.records() == ()
    denial_audit = _audit("audit-record", "audit-denial")
    assert repositories.audit.append(denial_audit).is_success
    audit_records = repositories.audit.list_for_organization(_ORGANIZATION)
    assert audit_records.is_success and audit_records.value == (denial_audit,)
    assert association_record.correlation_id == _CORRELATION
    assert denial_audit.metadata.correlation_id == _CORRELATION


def test_retrieval_and_terminal_episode_repositories_enforce_attempt_uniqueness() -> None:
    repositories = DeterministicAdoptionRepositories()
    retrieval = _retrieval("retrieval-record-1", "retrieval-1")
    episode = _episode("episode-record-1", "episode-1")

    assert repositories.retrievals.append(retrieval).is_success
    duplicate_retrieval = repositories.retrievals.append(
        _retrieval("retrieval-record-2", "retrieval-2")
    )
    assert not duplicate_retrieval.is_success
    stored_retrieval = repositories.retrievals.get_by_attempt_id(
        _ORGANIZATION, AgentNodeAttemptId("attempt-adoption")
    )
    assert stored_retrieval.is_success and stored_retrieval.value == retrieval
    assert retrieval.lesson_references == ()

    assert repositories.episodes.append(episode).is_success
    duplicate_episode = repositories.episodes.append(_episode("episode-record-2", "episode-2"))
    assert not duplicate_episode.is_success
    stored_episode = repositories.episodes.get_by_attempt_id(
        _ORGANIZATION, AgentNodeAttemptId("attempt-adoption")
    )
    assert stored_episode.is_success and stored_episode.value == episode


def test_retrieval_and_episode_persistence_failures_are_isolated_and_recoverable() -> None:
    plan = FakeFailurePlan()
    repositories = DeterministicAdoptionRepositories(plan)
    retrieval = _retrieval("retrieval-record", "retrieval-1")
    episode = _episode("episode-record", "episode-1", blocked_for_recovery=True)

    plan.fail_next_persistence("retrieval.append")
    retrieval_failure = repositories.retrievals.append(retrieval)
    assert not retrieval_failure.is_success
    assert repositories.retrievals.records() == ()

    plan.fail_next_persistence("episode.append")
    episode_failure = repositories.episodes.append(episode)
    assert not episode_failure.is_success
    assert repositories.episodes.records() == ()

    assert repositories.retrievals.append(retrieval).is_success
    assert repositories.episodes.append(episode).is_success
    assert episode.blocked_for_recovery


def test_release_decisions_are_terminal_unique_and_retain_failure_evidence() -> None:
    repositories = DeterministicAdoptionRepositories()
    eligible = _release_decision("release-record-1", "release-1")
    failed = ReleaseReadinessDecision(
        metadata=_metadata("release-record-2"),
        decision_id=ReleaseReadinessDecisionId("release-2"),
        pack_id=DomainPackId("pack-adoption"),
        immutable_version="2.0.0",
        workflow_id="workflow-adoption",
        status=ReleaseReadinessStatus.FAILED,
        integration_coverage_complete=True,
        evidence_references=("verification:adoption",),
        failure_evidence_references=("failure:provider",),
    )

    assert repositories.release_decisions.append(eligible).is_success
    assert repositories.release_decisions.append(failed).is_success
    duplicate = repositories.release_decisions.append(
        _release_decision("release-record-3", "release-3")
    )
    assert not duplicate.is_success
    assert eligible.terminal and failed.terminal
    assert failed.failure_evidence_references == ("failure:provider",)
    with pytest.raises(ValueError, match="terminal"):
        ReleaseReadinessDecision(
            metadata=_metadata("release-record-invalid"),
            decision_id=ReleaseReadinessDecisionId("release-invalid"),
            pack_id=DomainPackId("pack-adoption"),
            immutable_version="3.0.0",
            workflow_id="workflow-adoption",
            status=ReleaseReadinessStatus.ELIGIBLE,
            integration_coverage_complete=True,
            evidence_references=("verification:adoption",),
            terminal=False,
        )


def test_verification_failure_persistence_preserves_completed_coverage_on_retry() -> None:
    plan = FakeFailurePlan()
    repositories = DeterministicAdoptionRepositories(plan)
    verification = VerificationRun(
        metadata=_metadata("verification-record"),
        verification_run_id=VerificationRunId("verification-1"),
        pack_id=DomainPackId("pack-adoption"),
        immutable_version="1.0.0",
        pack_contract_version="1.0.0",
        host_contract_version="1.0.0",
        alc_version="1.0.0",
        schema_evidence_references=("schema:adoption",),
        unit_evidence_references=("unit:adoption",),
        property_evidence_references=("property:adoption",),
        integration_evidence_references=("integration:adoption",),
        coverage_status=VerificationCoverageStatus.COMPLETE,
        fixed_seed="adoption-seed",
        fixture_digest="sha256:fixtures",
        failure_evidence_references=("failure:late-step",),
    )

    plan.fail_next_persistence("verification.append")
    failure = repositories.verifications.append(verification)
    assert not failure.is_success
    assert repositories.verifications.records() == ()

    assert repositories.verifications.append(verification).is_success
    stored = repositories.verifications.records()
    assert stored == (verification,)
    assert stored[0].coverage_status is VerificationCoverageStatus.COMPLETE
    assert stored[0].failure_evidence_references == ("failure:late-step",)


def test_persistence_and_audit_failures_are_independently_configurable() -> None:
    plan = FakeFailurePlan(fail_persistence=True)
    repositories = DeterministicAdoptionRepositories(plan)
    registration = _registration("registration-record", "registration-1")
    audit = _audit("audit-record", "audit-1")

    assert not repositories.registrations.append(registration).is_success
    assert repositories.audit.append(audit).is_success

    plan.fail_persistence = False
    plan.fail_audit = True
    assert repositories.registrations.append(registration).is_success
    blocked_audit = repositories.audit.append(_audit("audit-record-2", "audit-2"))
    assert not blocked_audit.is_success
    assert repositories.registrations.records() == (registration,)

    plan.fail_audit = False
    assert repositories.audit.append(_audit("audit-record-2", "audit-2")).is_success


def test_provider_denial_remains_denied_when_its_audit_write_fails() -> None:
    plan = FakeFailurePlan(fail_audit=True)
    repositories = DeterministicAdoptionRepositories(plan)
    provider = MockProviderAdapter("provider-adoption", "text.generate")
    provider.set_failure_mode(ProviderFailureMode.UNSAFE_RESULT)

    denied = provider.invoke(
        "text.generate",
        {"input_reference": "reference:request"},
        correlation_id=_CORRELATION,
    )
    audit_failure = repositories.audit.append(_audit("audit-record", "provider-denial"))

    assert not denied.is_success
    assert denied.error is not None
    assert denied.error.correlation_id == _CORRELATION
    assert not audit_failure.is_success
    assert repositories.audit.records == ()
