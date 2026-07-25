"""Focused validation tests for adoption control-plane model records."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime

import pytest

from app.models.common import CompatibilityRange, RecordMetadata
from app.models.control_plane import (
    AgentLifecycle,
    AgentLifecycleId,
    AgentLifecycleStatus,
    AgentNodeAttemptId,
    ArtifactAvailabilityStatus,
    ArtifactHandoff,
    ArtifactHandoffId,
    AuthorizationDecision,
    AuthorizationDecisionId,
    AuthorizationOutcome,
    CompatibilityStatus,
    InvocationAssociation,
    LearningEpisodeId,
    MaturityLevel,
    MaturityState,
    MaturityStateId,
    RecoveryAction,
    RecoveryActionId,
    RecoveryActionStatus,
    Registration,
    RegistrationDecision,
    RegistrationId,
    ReleaseReadinessDecision,
    ReleaseReadinessDecisionId,
    ReleaseReadinessStatus,
    RetrievalRecordId,
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
    InvocationId,
    OrganizationId,
    RecordId,
    RunId,
)

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_ORGANIZATION = OrganizationId("organization-adoption")
_CORRELATION = CorrelationId("correlation-adoption")


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


def test_registration_preserves_immutable_pack_identity_and_is_frozen() -> None:
    record = Registration(
        metadata=_metadata("registration-record"),
        registration_id=RegistrationId("registration-1"),
        pack_id=DomainPackId("pack-1"),
        immutable_version="1.0.0",
        content_digest="sha256:pack-1",
        signer_id=ActorId("owner-1"),
        host_compatibility_range=CompatibilityRange.exact("1.0.0"),
        alc_compatibility_range=CompatibilityRange.exact("1.0.0"),
        validation_result=True,
        decision=RegistrationDecision.APPROVED,
        compatibility_status=CompatibilityStatus.COMPATIBLE,
    )

    assert record.identity_key == (DomainPackId("pack-1"), "1.0.0")
    assert record.registration_decision is RegistrationDecision.APPROVED
    with pytest.raises(FrozenInstanceError):
        record.immutable_version = "2.0.0"  # type: ignore[misc]
    with pytest.raises(ValueError, match="reproduction contract"):
        Registration(
            metadata=_metadata("superseded-record"),
            registration_id=RegistrationId("registration-2"),
            pack_id=DomainPackId("pack-1"),
            immutable_version="1.0.0",
            content_digest="sha256:pack-1",
            signer_id=ActorId("owner-1"),
            host_compatibility_range=CompatibilityRange.exact("1.0.0"),
            alc_compatibility_range=CompatibilityRange.exact("1.0.0"),
            validation_result=True,
            decision=RegistrationDecision.APPROVED,
            superseded=True,
        )


def test_invocation_and_authorization_records_require_correlation_and_scope_identity() -> None:
    association = InvocationAssociation(
        metadata=_metadata("invocation-record"),
        invocation_id=InvocationId("invocation-1"),
        organization_id=_ORGANIZATION,
        domain_id=DomainId("domain-1"),
        pack_version="1.0.0",
        agent_id=AgentId("agent-1"),
        workflow_id="workflow-1",
        run_id=RunId("run-1"),
        correlation_id=_CORRELATION,
    )
    decision = AuthorizationDecision(
        metadata=_metadata("authorization-record"),
        decision_id=AuthorizationDecisionId("authorization-1"),
        organization_id=_ORGANIZATION,
        domain_id=DomainId("domain-1"),
        pack_version="1.0.0",
        agent_id=AgentId("agent-1"),
        capability="memory.read",
        scope={"memory_scope": "agent:agent-1"},
        outcome=AuthorizationOutcome.DENIED,
        reason="scope not declared",
    )

    assert association.run_id == RunId("run-1")
    assert not decision.allowed
    with pytest.raises(ValueError, match="correlation"):
        InvocationAssociation(
            metadata=_metadata("bad-invocation"),
            invocation_id=InvocationId("invocation-2"),
            organization_id=_ORGANIZATION,
            domain_id=DomainId("domain-1"),
            pack_version="1.0.0",
            agent_id=AgentId("agent-1"),
            workflow_id="workflow-1",
            run_id=RunId("run-1"),
            correlation_id=CorrelationId("different-correlation"),
        )


def test_artifact_handoff_available_only_after_reference_metadata_confirmation() -> None:
    handoff = ArtifactHandoff(
        metadata=_metadata("handoff-record"),
        handoff_id=ArtifactHandoffId("handoff-1"),
        artifact_identity="artifact-1",
        artifact_version="version-1",
        parent_lineage=("parent-1",),
        source_task_id="task-1",  # type: ignore[arg-type]
        source_run_reference="run-1",
        brief_scope="scope-reference",
        technical_specification={"specification_reference": "spec-1"},
        rights_and_consent_state="approved",
        continuity_state="continuous",
        quality_control_state="passed",
        target_channels=("internal",),
        provenance_reference="provenance-1",
        owner_reference="owner-1",
        classification="internal",
        integrity_reference="sha256:artifact-1",
        approval_reference="approval-1",
        availability=ArtifactAvailabilityStatus.AVAILABLE,
        metadata_persisted=True,
    )

    assert handoff.availability is ArtifactAvailabilityStatus.AVAILABLE
    with pytest.raises(TypeError):
        handoff.technical_specification["new"] = "value"  # type: ignore[index]
    with pytest.raises(ValueError, match="confirmation"):
        ArtifactHandoff(
            metadata=_metadata("pending-handoff"),
            handoff_id=ArtifactHandoffId("handoff-2"),
            artifact_identity="artifact-1",
            artifact_version="version-1",
            parent_lineage=(),
            source_task_id="task-1",  # type: ignore[arg-type]
            source_run_reference="run-1",
            brief_scope=None,
            technical_specification=None,
            rights_and_consent_state=None,
            continuity_state=None,
            quality_control_state=None,
            target_channels=("internal",),
            provenance_reference="provenance-1",
            availability=ArtifactAvailabilityStatus.AVAILABLE,
        )


def test_learning_records_allow_empty_retrieval_but_require_terminal_episode_identity() -> None:
    retrieval = RetrievalRecord(
        metadata=_metadata("retrieval-record"),
        retrieval_record_id=RetrievalRecordId("retrieval-1"),
        attempt_id=AgentNodeAttemptId("attempt-1"),
        organization_id=_ORGANIZATION,
        domain_id=DomainId("domain-1"),
        pack_version="1.0.0",
        agent_id=AgentId("agent-1"),
        memory_scope="agent:agent-1",
        retrieved_at=_NOW,
    )
    episode = LearningEpisode(
        metadata=_metadata("episode-record"),
        episode_id=LearningEpisodeId("episode-1"),
        attempt_id=AgentNodeAttemptId("attempt-1"),
        organization_id=_ORGANIZATION,
        domain_id=DomainId("domain-1"),
        pack_version="1.0.0",
        agent_id=AgentId("agent-1"),
        terminal_outcome=LearningTerminalOutcome.BLOCKED,
        outcome_reference="outcome-1",
        recorded_at=_NOW,
        retrieval_record_id=retrieval.retrieval_record_id,
        blocked_for_recovery=True,
    )

    assert retrieval.lesson_references == ()
    filters = retrieval.approved_filters
    assert filters is not None
    assert filters["memory_scope"] == "agent:agent-1"
    assert episode.terminal_outcome is LearningTerminalOutcome.BLOCKED
    with pytest.raises(TypeError):
        filters["agent_id"] = "other-agent"  # type: ignore[index]


def test_lesson_release_recovery_and_maturity_models_fail_closed() -> None:
    lesson = Lesson(
        metadata=_metadata("lesson-record"),
        lesson_id="lesson-1",  # type: ignore[arg-type]
        organization_id=_ORGANIZATION,
        domain_id=DomainId("domain-1"),
        pack_version_range=CompatibilityRange.exact("1.0.0"),
        agent_id=AgentId("agent-1"),
        memory_scope="agent:agent-1",
        assessment=LessonAssessmentOutcome.PASSED,
        source_episode_references=("episode-1",),
        content_reference="lesson-content-1",
        assessed_at=_NOW,
        retrievable=True,
    )
    recovery = RecoveryAction(
        metadata=_metadata("recovery-record"),
        recovery_action_id=RecoveryActionId("recovery-1"),
        pack_id=DomainPackId("pack-1"),
        designated_immutable_version="1.0.0",
        status=RecoveryActionStatus.RESTORED,
        approval_reference="approval-1",
        investigation_evidence_references=("investigation-1",),
        restored_immutable_version="1.0.0",
    )
    maturity = MaturityState(
        metadata=_metadata("maturity-record"),
        maturity_state_id=MaturityStateId("maturity-1"),
        pack_id=DomainPackId("pack-1"),
        immutable_version="1.0.0",
        agent_id=AgentId("agent-1"),
        level=MaturityLevel.PRODUCTION_PROVEN,
        evidence_references=("release-evidence-1",),
        pack_operational=False,
    )

    assert lesson.retrievable
    assert recovery.restored_immutable_version == "1.0.0"
    assert maturity.level is MaturityLevel.PRODUCTION_PROVEN
    assert {level.value for level in MaturityLevel} == {
        "cataloged",
        "registered",
        "active",
        "production_proven",
    }
    with pytest.raises(ValueError, match="failure evidence"):
        ReleaseReadinessDecision(
            metadata=_metadata("release-record"),
            decision_id=ReleaseReadinessDecisionId("decision-1"),
            pack_id=DomainPackId("pack-1"),
            immutable_version="1.0.0",
            workflow_id="workflow-1",
            status=ReleaseReadinessStatus.BLOCKED,
            integration_coverage_complete=False,
            evidence_references=("verification-1",),
        )
    with pytest.raises(ValueError, match="Active"):
        AgentLifecycle(
            metadata=_metadata("lifecycle-record"),
            lifecycle_id=AgentLifecycleId("lifecycle-1"),
            pack_id=DomainPackId("pack-1"),
            immutable_version="1.0.0",
            agent_id=AgentId("agent-1"),
            status=AgentLifecycleStatus.ACTIVE,
            learning_required=True,
        )
