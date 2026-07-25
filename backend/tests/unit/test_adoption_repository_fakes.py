"""Focused checks for adoption repository constraints and provider fakes."""

from __future__ import annotations

from datetime import UTC, datetime

from app.models.common import CompatibilityRange, RecordMetadata
from app.models.control_plane import (
    AgentNodeAttemptId,
    ArtifactHandoff,
    ArtifactHandoffId,
    AuditRecord,
    LearningEpisodeId,
    Registration,
    RegistrationDecision,
    RegistrationId,
    ReleaseReadinessDecision,
    ReleaseReadinessDecisionId,
    ReleaseReadinessStatus,
    RetrievalRecordId,
)
from app.models.evidence import LearningEpisode, LearningTerminalOutcome, RetrievalRecord
from app.models.identifiers import (
    ActorId,
    AgentId,
    CorrelationId,
    DomainId,
    DomainPackId,
    OrganizationId,
    RecordId,
)
from tests.fakes.adoption import (
    DeterministicAdoptionRepositories,
    FakeFailurePlan,
)
from tests.fakes.provider import MockProviderAdapter, ProviderFailureMode

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


def _registration(record_id: str, registration_id: str, version: str = "1.0.0") -> Registration:
    return Registration(
        metadata=_metadata(record_id),
        registration_id=RegistrationId(registration_id),
        pack_id=DomainPackId("pack-adoption"),
        immutable_version=version,
        content_digest=f"sha256:{version}",
        signer_id=ActorId("owner-adoption"),
        host_compatibility_range=CompatibilityRange.exact("1.0.0"),
        alc_compatibility_range=CompatibilityRange.exact("1.0.0"),
        validation_result=True,
        decision=RegistrationDecision.APPROVED,
    )


def _retrieval(record_id: str, retrieval_id: str) -> RetrievalRecord:
    return RetrievalRecord(
        metadata=_metadata(record_id),
        retrieval_record_id=RetrievalRecordId(retrieval_id),
        attempt_id=AgentNodeAttemptId("attempt-adoption"),
        organization_id=_ORGANIZATION,
        domain_id=DomainId("domain-adoption"),
        pack_version="1.0.0",
        agent_id=AgentId("agent-adoption"),
        memory_scope="agent:agent-adoption",
        retrieved_at=_NOW,
    )


def _episode(record_id: str, episode_id: str) -> LearningEpisode:
    return LearningEpisode(
        metadata=_metadata(record_id),
        episode_id=LearningEpisodeId(episode_id),
        attempt_id=AgentNodeAttemptId("attempt-adoption"),
        organization_id=_ORGANIZATION,
        domain_id=DomainId("domain-adoption"),
        pack_version="1.0.0",
        agent_id=AgentId("agent-adoption"),
        terminal_outcome=LearningTerminalOutcome.COMPLETED,
        outcome_reference="outcome-reference",
        recorded_at=_NOW,
    )


def _handoff(record_id: str, handoff_id: str, parent_lineage: tuple[str, ...]) -> ArtifactHandoff:
    return ArtifactHandoff(
        metadata=_metadata(record_id),
        handoff_id=ArtifactHandoffId(handoff_id),
        artifact_identity="artifact-adoption",
        artifact_version="1.0.0",
        parent_lineage=parent_lineage,
        source_task_id="task-adoption",  # type: ignore[arg-type]
        source_run_reference="run-adoption",
        brief_scope=None,
        technical_specification=None,
        rights_and_consent_state=None,
        continuity_state=None,
        quality_control_state=None,
        target_channels=("internal",),
        provenance_reference="provenance-reference",
    )


def test_registration_uniqueness_is_pack_version_scoped_and_append_only() -> None:
    repositories = DeterministicAdoptionRepositories()
    first = _registration("registration-record-1", "registration-1")
    duplicate = _registration("registration-record-2", "registration-2")

    assert repositories.registrations.append(first).is_success
    conflict = repositories.registrations.append(duplicate)

    assert not conflict.is_success
    assert repositories.registrations.records() == (first,)


def test_retrieval_and_terminal_episode_are_unique_per_attempt() -> None:
    repositories = DeterministicAdoptionRepositories()
    retrieval = _retrieval("retrieval-record-1", "retrieval-1")
    episode = _episode("episode-record-1", "episode-1")

    assert repositories.retrievals.append(retrieval).is_success
    assert not repositories.retrievals.append(
        _retrieval("retrieval-record-2", "retrieval-2")
    ).is_success
    assert repositories.episodes.append(episode).is_success
    assert not repositories.episodes.append(_episode("episode-record-2", "episode-2")).is_success


def test_release_decisions_are_terminal_and_unique_for_a_workflow_version() -> None:
    repositories = DeterministicAdoptionRepositories()
    decision = ReleaseReadinessDecision(
        metadata=_metadata("release-record-1"),
        decision_id=ReleaseReadinessDecisionId("release-1"),
        pack_id=DomainPackId("pack-adoption"),
        immutable_version="1.0.0",
        workflow_id="workflow-adoption",
        status=ReleaseReadinessStatus.ELIGIBLE,
        integration_coverage_complete=True,
        evidence_references=("verification-1",),
    )

    assert repositories.release_decisions.append(decision).is_success
    duplicate = repositories.release_decisions.append(decision)
    stored = repositories.release_decisions.get_terminal(
        _ORGANIZATION, DomainPackId("pack-adoption"), "1.0.0", "workflow-adoption"
    )

    assert not duplicate.is_success
    assert stored.is_success and stored.value == decision


def test_persistence_and_audit_failures_are_independently_configurable() -> None:
    plan = FakeFailurePlan(fail_persistence=True)
    repositories = DeterministicAdoptionRepositories(plan)
    registration = _registration("registration-record-1", "registration-1")

    assert not repositories.registrations.append(registration).is_success
    plan.fail_persistence = False
    assert repositories.registrations.append(registration).is_success

    audit = AuditRecord(
        metadata=_metadata("audit-record-1"),
        audit_id="audit-1",
        action="registration.reject",
        subject_reference="pack-adoption",
        outcome="rejected",
        recorded_at=_NOW,
    )
    plan.fail_audit = True
    assert not repositories.audit.append(audit).is_success
    plan.fail_audit = False
    assert repositories.audit.append(audit).is_success


def test_handoff_cycle_is_rejected_and_pending_handoff_is_not_available() -> None:
    repositories = DeterministicAdoptionRepositories()
    parent = _handoff("handoff-record-1", "parent", ("child",))
    child = _handoff("handoff-record-2", "child", ("parent",))

    assert repositories.handoffs.append(parent).is_success
    assert not repositories.handoffs.append(child).is_success
    available = repositories.handoffs.available_for_downstream(_ORGANIZATION)

    assert available.is_success and available.value == ()


def test_mock_provider_is_deterministic_and_fails_closed() -> None:
    provider = MockProviderAdapter("provider-adoption", "text.generate")
    first = provider.invoke("text.generate", {"input_reference": "ref-1"})
    second = provider.invoke("text.generate", {"input_reference": "ref-1"})

    assert first.is_success and second.is_success
    assert first.value == second.value
    assert len(provider.calls) == 2

    provider.set_failure_mode(ProviderFailureMode.UNSAFE_RESULT)
    denied = provider.invoke("text.generate", {"input_reference": "ref-2"})

    assert not denied.is_success
    assert len(provider.calls) == 2
