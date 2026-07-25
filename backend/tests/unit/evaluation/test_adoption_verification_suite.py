"""Deterministic Verification_Suite schema, unit, resilience, and policy tests."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime
from typing import TypedDict

import pytest

from app.evaluation.verification_suite import VerificationSuite
from app.evidence.release_evidence import (
    InMemoryReleaseEvidenceRepository,
    ReleasePolicy,
    VerificationOutcome,
)
from app.governance.adapter_execution import (
    AuthorizedMockProviderRegistry,
    ProviderAdapterDeclaration,
    ProviderDenialReason,
    authorize_provider_adapter,
)
from app.memory.learning_lifecycle import ActivationEvidence, LearningLifecycleService
from app.memory.lesson_service import LessonAssessment, LessonService
from app.models.common import CompatibilityRange, RecordMetadata
from app.models.contracts import (
    AgentLearningContract,
    DomainPack,
    ErrorCode,
    PackContract,
)
from app.models.control_plane import (
    AgentLifecycle,
    AgentLifecycleId,
    AgentLifecycleStatus,
    ArtifactAvailabilityStatus,
    ArtifactHandoff,
    ArtifactHandoffId,
    TaskId,
    VerificationCoverageStatus,
)
from app.models.evidence import Lesson, LessonAssessmentOutcome
from app.models.identifiers import (
    ActorId,
    AgentId,
    CorrelationId,
    DomainId,
    DomainPackId,
    OrganizationId,
    RecordId,
)
from tests.fakes.adoption import DeterministicAdoptionRepositories
from tests.fakes.provider import MockProviderAdapter

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_ORGANIZATION = OrganizationId("organization-verification")
_CORRELATION = CorrelationId("correlation-verification")
_PACK_ID = DomainPackId("pack-verification")
_AGENT_ID = AgentId("agent-verification")
_PACK_CONTRACT = PackContract(version="1.0.0")


class VerificationRunArguments(TypedDict):
    """Common keyword arguments shared by deterministic suite executions."""

    pack_id: DomainPackId
    immutable_version: str
    pack_contract_version: str
    host_contract_version: str
    alc_version: str


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


def _pack(*, required_alc_version: str | None = "1.0.0") -> DomainPack:
    return DomainPack(
        pack_id=_PACK_ID,
        immutable_version="1.0.0",
        pack_contract_version="1.0.0",
        host_compatibility_range=CompatibilityRange.exact("1.0.0"),
        alc_compatibility_range=CompatibilityRange.exact("1.0.0"),
        content_digest="sha256:verification-pack",
        signer_id=ActorId("owner-verification"),
        agents=(_AGENT_ID,),
        workflows=("verification.workflow",),
        capabilities=("memory.read",),
        data_classifications=("internal",),
        evaluation_references=("evaluation:verification",),
        required_alc_version=required_alc_version,
        asset_references=("asset:verification",),
    )


def _handoff(handoff_id: str, parents: tuple[str, ...] = ()) -> ArtifactHandoff:
    return ArtifactHandoff(
        metadata=_metadata(f"record-{handoff_id}"),
        handoff_id=ArtifactHandoffId(handoff_id),
        artifact_identity="verification-artifact",
        artifact_version="1.0.0",
        parent_lineage=parents,
        source_task_id=TaskId("verification-task"),
        source_run_reference="run:verification",
        brief_scope="scope:verification",
        technical_specification={"schema_reference": "schema:verification"},
        rights_and_consent_state="approved",
        continuity_state="continuous",
        quality_control_state="passed",
        target_channels=("internal",),
        provenance_reference="provenance:verification",
        owner_reference="owner:verification",
        classification="internal",
        integrity_reference="sha256:verification-artifact",
        approval_reference="approval:verification",
        availability=ArtifactAvailabilityStatus.AVAILABLE,
        metadata_persisted=True,
    )


def _suite(
    repositories: DeterministicAdoptionRepositories | None = None,
    evidence: InMemoryReleaseEvidenceRepository | None = None,
) -> tuple[VerificationSuite, DeterministicAdoptionRepositories]:
    resolved_repositories = repositories or DeterministicAdoptionRepositories()
    return (
        VerificationSuite(
            verification_repository=resolved_repositories.verifications,
            release_repository=resolved_repositories.release_decisions,
            evidence_repository=evidence or InMemoryReleaseEvidenceRepository(),
            clock=lambda: _NOW,
        ),
        resolved_repositories,
    )


def _run_kwargs() -> VerificationRunArguments:
    return {
        "pack_id": _PACK_ID,
        "immutable_version": "1.0.0",
        "pack_contract_version": "1.0.0",
        "host_contract_version": "1.0.0",
        "alc_version": "1.0.0",
    }


def _lifecycle() -> AgentLifecycle:
    return AgentLifecycle(
        metadata=_metadata("lifecycle-input"),
        lifecycle_id=AgentLifecycleId("lifecycle-input"),
        pack_id=_PACK_ID,
        immutable_version="1.0.0",
        agent_id=_AGENT_ID,
        status=AgentLifecycleStatus.REGISTERED,
        learning_required=True,
    )


def _alc() -> AgentLearningContract:
    return AgentLearningContract(
        agent_id=_AGENT_ID,
        version="1.0.0",
        memory_scopes=(f"agent:{_AGENT_ID}",),
        retrieval_policy="enabled",
        reflection_policy="enabled",
        evaluation_references=("evaluation:alc",),
        retention_policy="retain-assessed",
        human_promotion_policy="required",
    )


def _activation_evidence(
    *, retention_policy: str | bool | None = "retain-assessed"
) -> ActivationEvidence:
    return ActivationEvidence(
        approved_agent_scoped_memory=True,
        pre_action_retrieval_enabled=True,
        learning_episode_capture_enabled=True,
        reflection_evaluator_enabled=True,
        retention_policy=retention_policy,
        required_evaluations_passed=True,
        evidence_references=("evidence:activation",),
    )


def _lesson(lesson_id: str) -> Lesson:
    return Lesson(
        metadata=_metadata(f"record-{lesson_id}"),
        lesson_id=lesson_id,  # type: ignore[arg-type]
        organization_id=_ORGANIZATION,
        domain_id=DomainId("domain-verification"),
        pack_version_range=CompatibilityRange.exact("1.0.0"),
        agent_id=_AGENT_ID,
        memory_scope=f"agent:{_AGENT_ID}",
        assessment=LessonAssessmentOutcome.FAILED,
        source_episode_references=("episode:verification",),
        content_reference=f"content:{lesson_id}",
        assessed_at=_NOW,
    )


def _provider_declaration() -> ProviderAdapterDeclaration:
    return ProviderAdapterDeclaration(
        provider_id="provider-verification",
        capability="text.generate",
        cost_limit=1,
        retention_policy="reference_only",
        residency="test-local",
        safety_policy="deny-on-unsafe",
    )


def test_verification_suite_retains_valid_pack_and_handoff_schema_results() -> None:
    """Pack_Contract and acyclic Artifact_Handoff checks become schema evidence."""
    pack = _pack()
    first = _handoff("handoff-first")
    second = _handoff("handoff-second", ("handoff-first",))
    suite, _ = _suite()

    assert _PACK_CONTRACT.validate(pack) == ()
    assert VerificationSuite.validate_pack_contract(_PACK_CONTRACT, pack)
    assert VerificationSuite.validate_artifact_handoff_lineage((first, second))

    result = suite.run(
        _ORGANIZATION,
        _CORRELATION,
        **_run_kwargs(),
        pack_contract=_PACK_CONTRACT,
        pack=pack,
        handoffs=(first, second),
        integration_coverage_complete=True,
    )

    assert result.is_success and result.value is not None
    schema_results = tuple(
        record for record in result.value.check_results if record.layer.value == "schema"
    )
    assert tuple(record.check_name for record in schema_results) == (
        "schema.pack-contract",
        "schema.artifact-handoff-lineage",
    )
    assert all(record.outcome is VerificationOutcome.PASS for record in schema_results)
    assert result.value.release_decision is not None


def test_verification_suite_rejects_invalid_pack_and_cyclic_handoff_schema_inputs() -> None:
    """Invalid schema inputs fail their checks and never become an eligible release."""
    invalid_pack = _pack(required_alc_version=None)
    cyclic = _handoff("handoff-cycle", ("handoff-cycle",))
    suite, _ = _suite()

    assert not VerificationSuite.validate_pack_contract(_PACK_CONTRACT, invalid_pack)
    assert not VerificationSuite.validate_artifact_handoff_lineage((cyclic,))

    result = suite.run(
        _ORGANIZATION,
        _CORRELATION,
        **_run_kwargs(),
        pack_contract=_PACK_CONTRACT,
        pack=invalid_pack,
        handoffs=(cyclic,),
        integration_coverage_complete=True,
    )

    assert result.is_success and result.value is not None
    assert {record.check_name for record in result.value.check_results} == {
        "schema.pack-contract",
        "schema.artifact-handoff-lineage",
    }
    assert all(record.failed for record in result.value.check_results)
    assert result.value.release_decision is None


def test_verification_unit_checks_cover_lifecycle_alc_lesson_and_provider_branches() -> None:
    """Deterministic unit outcomes cover passing and fail-closed governance branches."""
    repositories = DeterministicAdoptionRepositories()
    lifecycle_service = LearningLifecycleService(
        repositories.lifecycle,
        repositories.retrievals,
        repositories.episodes,
        clock=lambda: _NOW,
    )
    active = lifecycle_service.evaluate_activation(
        _lifecycle(),
        (_alc(),),
        _activation_evidence(),
        correlation_id=_CORRELATION,
    )
    blocked = lifecycle_service.evaluate_activation(
        _lifecycle(),
        (),
        _activation_evidence(retention_policy=None),
        correlation_id=_CORRELATION,
    )

    lesson_service = LessonService(
        repositories.lessons,
        repositories.retrievals,
        None,
        repositories.audit,
        clock=lambda: _NOW,
    )
    passed_lesson = lesson_service.assess_lesson(
        _lesson("lesson-passed"),
        LessonAssessment(
            format_valid=True,
            source_episode_references_valid=True,
            safety_policy_passed=True,
            domain_policy_passed=True,
            evaluation_score=1.0,
            evaluation_threshold=0.8,
            evidence_references=("evidence:lesson",),
        ),
        correlation_id=_CORRELATION,
    )
    failed_lesson = lesson_service.assess_lesson(
        _lesson("lesson-failed"),
        replace(
            LessonAssessment(
                format_valid=True,
                source_episode_references_valid=True,
                safety_policy_passed=True,
                domain_policy_passed=True,
                evaluation_score=1.0,
                evaluation_threshold=0.8,
            ),
            domain_policy_passed=False,
        ),
        correlation_id=_CORRELATION,
    )

    provider = MockProviderAdapter("provider-verification", "text.generate")
    declaration = _provider_declaration()
    allowed_provider = authorize_provider_adapter(provider, declaration)
    denied_provider = authorize_provider_adapter(
        provider,
        replace(declaration, safety_policy=None),
    )
    provider_registry = AuthorizedMockProviderRegistry(
        (provider,), {provider.provider_id: declaration}
    )

    assert active.is_success and active.value is not None
    assert active.value.status is AgentLifecycleStatus.ACTIVE
    assert blocked.is_success and blocked.value is not None
    assert blocked.value.status is AgentLifecycleStatus.BLOCKED
    assert passed_lesson.is_success and passed_lesson.value is not None
    assert passed_lesson.value.retrievable
    assert failed_lesson.is_success and failed_lesson.value is not None
    assert failed_lesson.value.assessment is LessonAssessmentOutcome.FAILED
    assert not failed_lesson.value.retrievable
    assert allowed_provider.permitted
    assert not denied_provider.permitted
    assert ProviderDenialReason.MISSING_SAFETY_DECLARATION in denied_provider.denied_reasons
    assert provider_registry.provider_ids == ("provider-verification",)

    suite, _ = _suite()
    verification = suite.run(
        _ORGANIZATION,
        _CORRELATION,
        **_run_kwargs(),
        unit_checks=(
            ("unit.lifecycle-active", active.value.status is AgentLifecycleStatus.ACTIVE),
            ("unit.alc-valid", len((_alc(),)) == 1),
            ("unit.lesson-passed", passed_lesson.value.retrievable),
            ("unit.provider-allow-list", allowed_provider.permitted),
        ),
        integration_coverage_complete=True,
    )

    assert verification.is_success and verification.value is not None
    assert all(record.passed for record in verification.value.check_results)


def test_verification_failure_persistence_outage_does_not_stop_remaining_checks() -> None:
    """Failure-record storage can fail while check and release evidence continue."""
    evidence = InMemoryReleaseEvidenceRepository(fail_failure_persistence=True)
    suite, _ = _suite(evidence=evidence)

    result = suite.run(
        _ORGANIZATION,
        _CORRELATION,
        **_run_kwargs(),
        integration_checks=(("integration.complete", True),),
        post_coverage_checks=(
            ("post.failure", False),
            ("post.after-failure", True),
        ),
    )

    assert result.is_success and result.value is not None
    bundle = result.value
    assert tuple(record.check_name for record in bundle.check_results) == (
        "integration.complete",
        "post.failure",
        "post.after-failure",
    )
    assert bundle.failure_records == ()
    assert len(bundle.failure_persistence_errors) == 1
    assert bundle.coverage_status is VerificationCoverageStatus.COMPLETE
    assert bundle.release_decision is not None
    assert bundle.release_decision.status.value == "failed"
    assert bundle.verification_run.integration_evidence_references


def test_post_coverage_failure_fails_release_and_preserves_completed_integration_coverage() -> None:
    """A late failure retains the successful integration evidence and fails readiness."""
    suite, _ = _suite()

    result = suite.run(
        _ORGANIZATION,
        _CORRELATION,
        **_run_kwargs(),
        integration_checks=(("integration.graph", True), ("integration.release", True)),
        post_coverage_checks=(("post.policy", False),),
    )

    assert result.is_success and result.value is not None
    bundle = result.value
    assert bundle.coverage_status is VerificationCoverageStatus.COMPLETE
    assert bundle.release_decision is not None
    assert bundle.release_decision.status.value == "failed"
    integration_results = tuple(
        record for record in bundle.check_results if record.layer.value == "integration"
    )
    assert all(record.passed for record in integration_results)
    assert bundle.verification_run.integration_evidence_references == tuple(
        str(record.evidence_id) for record in integration_results
    )
    assert bundle.failure_records[0].after_integration_coverage
    assert bundle.release_decision.failure_evidence_references


def test_pre_coverage_failure_continues_without_failed_release_decision() -> None:
    """An incomplete integration boundary keeps verification running without failing release."""
    suite, _ = _suite()

    result = suite.run(
        _ORGANIZATION,
        _CORRELATION,
        **_run_kwargs(),
        integration_checks=(("integration.incomplete", False),),
        post_coverage_checks=(("post.continued", False), ("post.completed", True)),
    )

    assert result.is_success and result.value is not None
    bundle = result.value
    assert bundle.coverage_status is VerificationCoverageStatus.INCOMPLETE
    assert bundle.release_decision is None
    assert tuple(record.check_name for record in bundle.check_results) == (
        "integration.incomplete",
        "post.continued",
        "post.completed",
    )
    assert all(not record.after_integration_coverage for record in bundle.failure_records)


def test_release_policy_authorizes_administrative_failure_without_verification_failure() -> None:
    """An explicit Release_Policy reference authorizes an administrative failed decision."""
    suite, _ = _suite()
    policy = ReleasePolicy(
        allow_administrative_failure=True,
        administrative_failure_reference="policy:verification-admin-failure",
    )

    result = suite.run(
        _ORGANIZATION,
        _CORRELATION,
        **_run_kwargs(),
        integration_checks=(("integration.complete", True),),
        release_policy=policy,
        administrative_failure=True,
    )

    assert result.is_success and result.value is not None
    assert result.value.failure_records == ()
    assert result.value.release_decision is not None
    assert result.value.release_decision.status.value == "failed"
    assert result.value.release_decision.failure_evidence_references == (
        "policy:verification-admin-failure",
    )


def test_release_policy_denies_unauthorized_administrative_failure() -> None:
    """Administrative failure cannot be smuggled into a release without policy evidence."""
    suite, repositories = _suite()

    result = suite.run(
        _ORGANIZATION,
        _CORRELATION,
        **_run_kwargs(),
        integration_checks=(("integration.complete", True),),
        administrative_failure=True,
    )

    assert not result.is_success
    assert result.error is not None
    assert result.error.code is ErrorCode.AUTHORIZATION_DENIED
    assert repositories.release_decisions.records() == ()
    with pytest.raises(ValueError, match="policy evidence reference"):
        ReleasePolicy(allow_administrative_failure=True)
