"""Mock-provider integration coverage for shared adoption patterns."""

from __future__ import annotations

from datetime import UTC, datetime

from app.core.command_service import CommandService
from app.evaluation.verification_suite import VerificationSuite
from app.evidence.release_evidence import InMemoryReleaseEvidenceRepository, UIProjectionEvidence
from app.evidence.service import EvidenceService, GateEvaluator, GateRequirements
from app.governance.adapter_execution import (
    AuthorizedMockProviderRegistry,
    ProviderAdapterDeclaration,
    authorize_provider_adapter,
)
from app.memory.learning_lifecycle import ActivationEvidence, LearningLifecycleService
from app.memory.lesson_service import LessonAssessment, LessonService
from app.models.common import CompatibilityRange, RecordMetadata
from app.models.contracts import AgentLearningContract, DomainPack, HostContract, PackContract
from app.models.control_plane import (
    AgentLifecycle,
    AgentLifecycleId,
    AgentLifecycleStatus,
    AgentNodeAttemptId,
    AgentVersionId,
    ApprovalGateId,
    ApprovalGateStatus,
    ArtifactAvailabilityStatus,
    ArtifactHandoff,
    ArtifactHandoffId,
    CommonAgentVersion,
    CommonPatternVersion,
    CommonPatternVersionId,
    ContractStatus,
    CritiqueRecord,
    GraphRevision,
    GraphRevisionId,
    LessonId,
    QualityEvidence,
    QualityEvidenceKind,
    ReleaseReadinessStatus,
    SwarmInstance,
    SwarmInstanceId,
    TaskId,
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
    EvidenceId,
    OrganizationId,
    RecordId,
    RunId,
)
from app.models.runs import AgentNodeAttempt, AgentNodeAttemptStatus
from app.registry.admission import PackAdmission
from app.repositories.control_plane import InMemoryControlPlaneDatabase
from app.repositories.graph_repository import InMemoryGraphRepository
from app.va.service import VaDomainAdapter, VaMetadata
from app.workflows import GraphService, RegisteredReferences
from tests.fakes.adoption import DeterministicAdoptionRepositories
from tests.fakes.provider import MockProviderAdapter

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_ORGANIZATION = OrganizationId("organization-adoption-integration")
_CORRELATION = CorrelationId("correlation-adoption-integration")
_PACK_CONTRACT = PackContract(version="1.0.0")
_HOST_VERSION = "2.0.0"
_ALC_VERSION = "3.0.0"
_MEMORY_SCOPE = "agent:planner:memory"


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


def _pack(
    pack_id: str = "va-agent-swarm",
    *,
    immutable_version: str = "1.0.0",
) -> DomainPack:
    agent_id = AgentId(f"{pack_id}.planner")
    return DomainPack(
        pack_id=DomainPackId(pack_id),
        immutable_version=immutable_version,
        pack_contract_version=_PACK_CONTRACT.version,
        host_compatibility_range=CompatibilityRange.exact(_HOST_VERSION),
        alc_compatibility_range=CompatibilityRange.exact(_ALC_VERSION),
        content_digest=f"sha256:{pack_id}-{immutable_version}",
        signer_id=ActorId(f"{pack_id}.owner"),
        agents=(agent_id,),
        workflows=(f"{pack_id}.workflow",),
        capabilities=("memory.read", "text.generate"),
        data_classifications=("internal",),
        evaluation_references=(f"evaluation:{pack_id}",),
        required_alc_version=_ALC_VERSION,
        asset_references=(
            f"asset:{pack_id}:workflow@{immutable_version}#sha256:{pack_id}-{immutable_version}",
        ),
    )


def _host_contract() -> HostContract:
    return HostContract(
        version=_HOST_VERSION,
        supported_pack_range=CompatibilityRange.exact(_PACK_CONTRACT.version),
        supported_alc_range=CompatibilityRange.exact(_ALC_VERSION),
    )


def _alc(pack: DomainPack) -> AgentLearningContract:
    return AgentLearningContract(
        agent_id=pack.agents[0],
        version=_ALC_VERSION,
        memory_scopes=(_MEMORY_SCOPE,),
        retrieval_policy="enabled",
        reflection_policy="enabled",
        evaluation_references=(f"evaluation:{pack.pack_id}:alc",),
        retention_policy="retain-assessed",
        human_promotion_policy="required",
    )


def _admission(repositories: DeterministicAdoptionRepositories) -> PackAdmission:
    return PackAdmission(
        repositories.registrations,
        repositories.audit,
        pack_contract=_PACK_CONTRACT,
    )


def _provider(pack: DomainPack) -> tuple[MockProviderAdapter, AuthorizedMockProviderRegistry]:
    provider_id = f"{pack.pack_id}.mock-provider"
    adapter = MockProviderAdapter(provider_id, "text.generate")
    declaration = ProviderAdapterDeclaration(
        provider_id=provider_id,
        capabilities=frozenset({"text.generate"}),
        cost_limit=1,
        retention_policy="reference_only",
        residency="test-local",
        safety_policy="deny-on-unsafe",
    )
    decision = authorize_provider_adapter(adapter, declaration)
    assert decision.permitted
    registry = AuthorizedMockProviderRegistry((adapter,), {provider_id: declaration})
    assert registry.provider_ids == (provider_id,)
    assert registry.get(provider_id) is adapter
    return adapter, registry


def _lifecycle(pack: DomainPack) -> AgentLifecycle:
    return AgentLifecycle(
        metadata=_metadata(f"lifecycle:{pack.pack_id}:{pack.immutable_version}"),
        lifecycle_id=AgentLifecycleId(f"lifecycle:{pack.pack_id}:{pack.immutable_version}"),
        pack_id=pack.pack_id,
        immutable_version=pack.immutable_version,
        agent_id=pack.agents[0],
        status=AgentLifecycleStatus.CATALOGED,
        learning_required=True,
    )


def _attempt(pack: DomainPack, suffix: str = "primary") -> AgentNodeAttempt:
    return AgentNodeAttempt(
        metadata=_metadata(f"attempt-record:{pack.pack_id}:{suffix}"),
        attempt_id=AgentNodeAttemptId(f"attempt:{pack.pack_id}:{suffix}"),
        run_id=RunId(f"run:{pack.pack_id}:{suffix}"),
        node_id="planner",
        organization_id=str(_ORGANIZATION),
        domain_id=DomainId(f"{pack.pack_id}.domain"),
        pack_id=pack.pack_id,
        pack_version=pack.immutable_version,
        agent_id=pack.agents[0],
        workflow_id=pack.workflows[0],
        status=AgentNodeAttemptStatus.QUEUED,
    )


def _learning_service(
    repositories: DeterministicAdoptionRepositories,
) -> LearningLifecycleService:
    return LearningLifecycleService(
        lifecycle_repository=repositories.lifecycle,
        retrieval_repository=repositories.retrievals,
        episode_repository=repositories.episodes,
        audit_repository=repositories.audit,
        attempt_repository=repositories.attempts,
        clock=lambda: _NOW,
    )


def _activation_evidence() -> ActivationEvidence:
    return ActivationEvidence(
        approved_agent_scoped_memory=True,
        pre_action_retrieval_enabled=True,
        learning_episode_capture_enabled=True,
        reflection_evaluator_enabled=True,
        retention_policy="retain-assessed",
        required_evaluations_passed=True,
        evidence_references=("evidence:activation",),
    )


def _ui_extension(pack: DomainPack) -> UIProjectionEvidence:
    """Represent a domain-owned extension by reference, not by retained content."""
    return UIProjectionEvidence(
        metadata=_metadata(f"ui-record:{pack.pack_id}:{pack.immutable_version}"),
        projection_id=EvidenceId(f"ui-extension:{pack.pack_id}:{pack.immutable_version}"),
        projection_type="domain-extension",
        projection_digest=f"sha256:ui-extension:{pack.pack_id}:{pack.immutable_version}",
        recorded_at=_NOW,
        supporting_references=(
            f"pack:{pack.pack_id}@{pack.immutable_version}",
            f"workflow:{pack.workflows[0]}",
        ),
    )


def _lesson(pack: DomainPack, episode: LearningEpisode) -> Lesson:
    return Lesson(
        metadata=_metadata(f"lesson-record:{pack.pack_id}"),
        lesson_id=LessonId(f"lesson:{pack.pack_id}"),
        organization_id=_ORGANIZATION,
        domain_id=DomainId(f"{pack.pack_id}.domain"),
        pack_version_range=CompatibilityRange.exact(pack.immutable_version),
        agent_id=pack.agents[0],
        memory_scope=_MEMORY_SCOPE,
        assessment=LessonAssessmentOutcome.FAILED,
        source_episode_references=(str(episode.episode_id),),
        content_reference=f"lesson-reference:{pack.pack_id}",
        assessed_at=_NOW,
    )


def _common_agent(pack: DomainPack) -> CommonAgentVersion:
    return CommonAgentVersion(
        metadata=_metadata(f"agent-record:{pack.pack_id}"),
        agent_version_id=AgentVersionId(f"{pack.pack_id}.agent.v1"),
        status=ContractStatus.PUBLISHED,
        canonical_identity=str(pack.agents[0]),
        category="planning",
        responsibilities=("plan",),
        boundaries=("no-unapproved-release",),
        escalation_targets=("operator",),
        approval_authority=("release-gate",),
        runtime_policy={},
        tool_policy={"allow": ()},
        quality_rubric={"minimum": 0.8},
        critique_relationships=("reviewer->planner",),
        knowledge_bindings=(f"knowledge:{pack.pack_id}",),
        input_schema={"type": "object"},
        output_schema={"type": "object"},
        provenance_policy={"retain": True},
        content_digest=f"sha256:{pack.pack_id}-agent-v1",
    )


def _common_pattern(pack: DomainPack) -> CommonPatternVersion:
    return CommonPatternVersion(
        metadata=_metadata(f"pattern-record:{pack.pack_id}"),
        pattern_version_id=CommonPatternVersionId(f"{pack.pack_id}.pattern.v1"),
        status=ContractStatus.PUBLISHED,
        graph_template={"va_templates": ("campaign",)},
        slot_constraints={"required": ("planner",)},
        compatibility_rules={"va_production_phases": ("production",)},
        risk_requirements={"approval": "required"},
        verification_requirements={"verification_level": "strict"},
        provenance={"source": f"pack:{pack.pack_id}"},
        content_digest=f"sha256:{pack.pack_id}-pattern-v1",
    )


def _graph_revision(
    pack: DomainPack, agent: CommonAgentVersion, pattern: CommonPatternVersion
) -> GraphRevision:
    return GraphRevision(
        metadata=_metadata(f"graph-record:{pack.pack_id}"),
        graph_revision_id=GraphRevisionId(f"graph:{pack.pack_id}:v1"),
        swarm_instance_id=SwarmInstanceId(f"swarm:{pack.pack_id}"),
        revision=1,
        nodes=(
            {
                "id": "plan",
                "agent_version_id": str(agent.agent_version_id),
                "tool_ids": (),
                "memory_reads": ("organization",),
                "memory_writes": ("organization",),
            },
        ),
        edges=(),
        layout={"plan": {"x": 0, "y": 0}},
        version_pins={
            "agent_version_ids": [str(agent.agent_version_id)],
            "pattern_version_ids": [str(pattern.pattern_version_id)],
        },
        policies={
            "workflow_definition": {
                "id": pack.workflows[0],
                "version": pack.immutable_version,
                "owner_id": str(pack.signer_id),
                "authorization_id": "release-gate",
                "engine": "graph",
                "execution_budget": {
                    "max_node_visits": 1,
                    "max_handoffs": 0,
                    "max_wall_clock_seconds": 30,
                    "max_tool_requests": 0,
                },
                "memory": {"reads": ["organization"], "writes": ["organization"]},
                "risk_gate_ids": ["low-risk"],
                "rollback": {"plan_id": "compensate.pack", "compensation_step_ids": ["plan"]},
                "pattern": "pipeline",
                "entry_node": "plan",
                "terminal_node_ids": ["plan"],
            },
            "verification": {"verification_level": "strict"},
        },
    )


def _graph_service(
    database: InMemoryControlPlaneDatabase,
    pack: DomainPack,
) -> tuple[GraphService, InMemoryGraphRepository, CommonPatternVersion]:
    agent = _common_agent(pack)
    pattern = _common_pattern(pack)
    with database.unit_of_work() as unit_of_work:
        assert unit_of_work.common_contracts.append_agent_version(agent).is_success
        assert unit_of_work.common_contracts.append_pattern_version(pattern).is_success
    repository = InMemoryGraphRepository()
    references = RegisteredReferences(
        agent_ids=frozenset({agent.canonical_identity}),
        tool_ids=frozenset(),
        memory_scope_ids=frozenset({"organization"}),
        risk_gate_ids=frozenset({"low-risk"}),
        rollback_plan_ids=frozenset({"compensate.pack"}),
        authorization_ids=frozenset({"release-gate"}),
    )
    return (
        GraphService(database.unit_of_work, repository, references, clock=lambda: _NOW),
        repository,
        pattern,
    )


def _handoff(pack: DomainPack) -> ArtifactHandoff:
    return ArtifactHandoff(
        metadata=_metadata(f"handoff-record:{pack.pack_id}"),
        handoff_id=ArtifactHandoffId(f"handoff:{pack.pack_id}"),
        artifact_identity=f"artifact:{pack.pack_id}",
        artifact_version=pack.immutable_version,
        parent_lineage=(f"brief:{pack.pack_id}",),
        source_task_id=TaskId(f"task:{pack.pack_id}"),
        source_run_reference=f"run:{pack.pack_id}:primary",
        brief_scope=f"scope:{pack.pack_id}",
        technical_specification={"schema_reference": f"schema:{pack.pack_id}"},
        rights_and_consent_state="passed",
        continuity_state="passed",
        quality_control_state="passed",
        target_channels=("review",),
        provenance_reference=f"provenance:{pack.pack_id}",
        owner_reference=f"owner:{pack.pack_id}",
        classification="internal",
        integrity_reference=f"sha256:artifact:{pack.pack_id}",
        approval_reference=f"approval:{pack.pack_id}",
        availability=ArtifactAvailabilityStatus.AVAILABLE,
        metadata_persisted=True,
    )


def _run_learning_path(
    pack: DomainPack,
    repositories: DeterministicAdoptionRepositories,
    provider: MockProviderAdapter,
) -> tuple[AgentLifecycle, RetrievalRecord, LearningEpisode, Lesson]:
    learning = _learning_service(repositories)
    activation_result = learning.evaluate_activation(
        _lifecycle(pack),
        (_alc(pack),),
        _activation_evidence(),
        correlation_id=_CORRELATION,
    )
    assert activation_result.is_success and activation_result.value is not None
    active = activation_result.value
    assert active.status is AgentLifecycleStatus.ACTIVE

    attempt = _attempt(pack)

    def invoke_provider(_retrieval: RetrievalRecord) -> str:
        result = provider.invoke(
            "text.generate",
            {"input_reference": f"brief:{pack.pack_id}"},
            correlation_id=_CORRELATION,
        )
        assert result.is_success and result.value is not None
        return result.value.response_reference

    action_result = learning.execute_learning_action(
        attempt,
        _MEMORY_SCOPE,
        invoke_provider,
        lesson_references=(),
        correlation_id=_CORRELATION,
    )
    assert action_result.is_success and action_result.value is not None
    retrieval_result = repositories.retrievals.get_by_attempt_id(_ORGANIZATION, attempt.attempt_id)
    assert retrieval_result.is_success and retrieval_result.value is not None
    retrieval = retrieval_result.value
    assert retrieval.lesson_references == ()

    episode_result = learning.record_terminal_episode(
        attempt,
        LearningTerminalOutcome.COMPLETED,
        f"provider-output:{pack.pack_id}",
        evidence_references=(f"evidence:episode:{pack.pack_id}",),
        correlation_id=_CORRELATION,
    )
    assert episode_result.is_success and episode_result.value is not None
    episode = episode_result.value
    assert episode.retrieval_record_id == retrieval.retrieval_record_id

    lessons = LessonService(
        repositories.lessons,
        repositories.retrievals,
        repositories.episodes,
        repositories.audit,
        clock=lambda: _NOW,
    )
    assessed_result = lessons.assess_lesson(
        _lesson(pack, episode),
        LessonAssessment(
            format_valid=True,
            source_episode_references_valid=True,
            safety_policy_passed=True,
            domain_policy_passed=True,
            evaluation_score=1.0,
            evaluation_threshold=0.8,
            evidence_references=(f"evidence:reflection:{pack.pack_id}",),
        ),
        correlation_id=_CORRELATION,
    )
    assert assessed_result.is_success and assessed_result.value is not None
    assessed = assessed_result.value
    assert assessed.assessment is LessonAssessmentOutcome.PASSED
    assert assessed.retrievable
    retrieved = lessons.retrieve_lessons(
        _ORGANIZATION,
        DomainId(f"{pack.pack_id}.domain"),
        pack.immutable_version,
        pack.agents[0],
        _MEMORY_SCOPE,
        correlation_id=_CORRELATION,
    )
    assert retrieved.is_success and retrieved.value == (assessed,)
    assert len(provider.calls) == 1
    return active, retrieval, episode, assessed


def test_superseded_va_pack_retains_reproduction_contract_for_prior_invocations() -> None:
    """A successor registration does not erase the approved VA reproduction contract."""
    repositories = DeterministicAdoptionRepositories()
    admission = _admission(repositories)
    first_pack = _pack("va-agent-swarm", immutable_version="1.0.0")
    successor_pack = _pack("va-agent-swarm", immutable_version="2.0.0")

    first_result = admission.register(
        first_pack,
        signer=first_pack.signer_id,
        correlation_id=CorrelationId("correlation-va-v1"),
        organization_id=_ORGANIZATION,
        host_contract=_host_contract(),
        alc_contract=_alc(first_pack),
    )
    successor_result = admission.register(
        successor_pack,
        signer=successor_pack.signer_id,
        correlation_id=CorrelationId("correlation-va-v2"),
        organization_id=_ORGANIZATION,
        host_contract=_host_contract(),
        alc_contract=_alc(first_pack),
    )

    assert first_result.is_success and first_result.value is not None
    assert successor_result.is_success and successor_result.value is not None
    assert first_result.value.immutable_version == "1.0.0"
    assert first_result.value.decision.value == "approved"
    assert successor_result.value.reproduction_references == (
        f"registration:{first_result.value.registration_id}",
        "pack:va-agent-swarm@1.0.0",
        f"host-contract:{_HOST_VERSION}",
        f"alc:{_ALC_VERSION}",
    )
    assert repositories.registrations.records() == (
        first_result.value,
        successor_result.value,
    )


def test_va_graph_learning_critique_approval_and_release_use_authorized_mock_provider() -> None:
    """The VA vertical path retains each shared evidence barrier before release."""
    pack = _pack()
    adoption_repositories = DeterministicAdoptionRepositories()
    registered = _admission(adoption_repositories).register(
        pack,
        signer=pack.signer_id,
        correlation_id=_CORRELATION,
        organization_id=_ORGANIZATION,
        host_contract=_host_contract(),
        alc_contract=_alc(pack),
    )
    assert registered.is_success and registered.value is not None

    database = InMemoryControlPlaneDatabase()
    graph, graph_repository, pattern = _graph_service(database, pack)
    instance = SwarmInstance(
        metadata=_metadata(f"swarm-record:{pack.pack_id}"),
        swarm_instance_id=SwarmInstanceId(f"swarm:{pack.pack_id}"),
    )
    agent = _common_agent(pack)
    revision = _graph_revision(pack, agent, pattern)
    created = graph.create_revision(_ORGANIZATION, instance, revision, expected_revision=0)
    assert created.is_success
    graph_result = graph.validate_revision(_ORGANIZATION, revision.graph_revision_id)
    assert graph_result.is_success and graph_result.value is not None
    assert graph_result.value.eligible_for_run
    assert (
        graph_repository.latest_validation(_ORGANIZATION, revision.graph_revision_id).value
        == graph_result.value
    )

    va_adapter = VaDomainAdapter(
        database.unit_of_work,
        CommandService(database.unit_of_work, clock=lambda: _NOW),
        clock=lambda: _NOW,
    )
    metadata_result = va_adapter.validate_metadata(
        _ORGANIZATION,
        _CORRELATION,
        VaMetadata(pattern.pattern_version_id, "campaign", "production"),
    )
    assert metadata_result.is_success and metadata_result.value is not None
    assert metadata_result.value.valid

    provider, provider_registry = _provider(pack)
    registered_provider = provider_registry.get(provider.provider_id)
    assert registered_provider is provider
    active, retrieval, episode, lesson = _run_learning_path(pack, adoption_repositories, provider)

    evidence = EvidenceService(database.unit_of_work, clock=lambda: _NOW)
    critique = CritiqueRecord(
        metadata=_metadata("va-critique-record"),
        critique_id="va-critique-1",
        source_reference="va.reviewer",
        target_task_id=TaskId("task:va-agent-swarm"),
        relationship_reference="reviewer->planner",
        evidence_reference="critique:va-review",
        submitted_at=_NOW,
    )
    rejected_critique = evidence.submit_critique(
        _ORGANIZATION,
        critique,
        published_relationships=("reviewer->other",),
        human_review_authorized=False,
    )
    assert not rejected_critique.is_success
    retained_critique = evidence.submit_critique(
        _ORGANIZATION,
        critique,
        published_relationships=("reviewer->planner",),
        human_review_authorized=False,
    )
    assert retained_critique.is_success and retained_critique.value == critique

    subject_reference = "task:va-agent-swarm"
    for kind in QualityEvidenceKind:
        quality = QualityEvidence(
            metadata=_metadata(f"quality:{kind.value}"),
            evidence_id=f"quality:{kind.value}",
            kind=kind,
            subject_reference=subject_reference,
            passed=True,
            evidence_reference=f"evidence:quality:{kind.value}",
            recorded_at=_NOW,
        )
        assert evidence.retain_quality_evidence(_ORGANIZATION, quality).is_success

    gate_id = ApprovalGateId("approval:va-release")
    gate_result = evidence.create_pending_gate(
        _ORGANIZATION,
        _metadata("approval:va-release:record"),
        gate_id,
        "release:va-agent-swarm@1.0.0",
    )
    assert gate_result.is_success and gate_result.value is not None
    evaluator = GateEvaluator(database.unit_of_work, clock=lambda: _NOW)
    blocked = evaluator.evaluate(
        _ORGANIZATION,
        _CORRELATION,
        subject_reference,
        gate_id,
        GateRequirements(),
        rights_and_consent_passed=True,
        provenance_passed=True,
        authorization_recheck=lambda _: True,
        policy_recheck=lambda _: True,
    )
    assert blocked.is_success and blocked.value is not None
    assert not blocked.value.progression_permitted
    assert blocked.value.gate.status is ApprovalGateStatus.PENDING

    decision = evidence.submit_human_decision(
        _ORGANIZATION,
        _CORRELATION,
        gate_id,
        decision="approve",
        decision_reason="All retained VA release evidence passed review.",
        reviewer_reference="va-release-reviewer",
        reviewer_authorized=True,
    )
    assert decision.is_success and decision.value is not None and decision.value.accepted
    approved = evaluator.evaluate(
        _ORGANIZATION,
        _CORRELATION,
        subject_reference,
        gate_id,
        GateRequirements(),
        rights_and_consent_passed=True,
        provenance_passed=True,
        authorization_recheck=lambda _: True,
        policy_recheck=lambda _: True,
    )
    assert approved.is_success and approved.value is not None
    assert approved.value.progression_permitted
    assert approved.value.gate.status is ApprovalGateStatus.APPROVED

    release_evidence = InMemoryReleaseEvidenceRepository()
    suite = VerificationSuite(
        verification_repository=adoption_repositories.verifications,
        release_repository=adoption_repositories.release_decisions,
        evidence_repository=release_evidence,
        clock=lambda: _NOW,
    )
    release_result = suite.run(
        _ORGANIZATION,
        _CORRELATION,
        pack_id=pack.pack_id,
        immutable_version=pack.immutable_version,
        pack_contract_version=_PACK_CONTRACT.version,
        host_contract_version=_HOST_VERSION,
        alc_version=_ALC_VERSION,
        workflow_id=pack.workflows[0],
        fixed_seed="adoption-redesign-va-seed",
        fixture_digest="fixture:va-shared-patterns",
        unit_checks=(
            ("unit.provider-authorized", provider_registry.provider_ids == (provider.provider_id,)),
            ("unit.activation-active", active.status is AgentLifecycleStatus.ACTIVE),
        ),
        integration_checks=(
            ("integration.graph-compilation", graph_result.value.eligible_for_run),
            ("integration.retrieval-record", retrieval.lesson_references == ()),
            (
                "integration.learning-episode",
                episode.terminal_outcome is LearningTerminalOutcome.COMPLETED,
            ),
            (
                "integration.reflection-assessment",
                lesson.assessment is LessonAssessmentOutcome.PASSED,
            ),
            ("integration.critique-retained", retained_critique.is_success),
            ("integration.approval-gate", approved.value.progression_permitted),
            ("integration.provider-mock", len(provider.calls) == 1),
        ),
        ui_projections=(_ui_extension(pack),),
        integration_coverage_complete=True,
        initial_vertical=True,
        pack_contract=_PACK_CONTRACT,
        pack=pack,
        handoffs=(_handoff(pack),),
    )

    assert release_result.is_success and release_result.value is not None
    bundle = release_result.value
    assert bundle.release_decision is not None
    assert bundle.release_decision.status is ReleaseReadinessStatus.ELIGIBLE
    assert bundle.coverage_status.value == "complete"
    assert len(bundle.ui_projections) == 1
    assert bundle.ui_projections[0].projection_type == "domain-extension"
    stored = adoption_repositories.release_decisions.get_terminal(
        _ORGANIZATION,
        pack.pack_id,
        pack.immutable_version,
        pack.workflows[0],
    )
    assert stored.is_success and stored.value == bundle.release_decision
    assert not adoption_repositories.release_decisions.append(bundle.release_decision).is_success


def test_two_non_video_packs_reuse_registration_learning_and_ui_extension_contracts() -> None:
    """Independent non-video packs use the same host-owned contracts without video branches."""
    repositories = DeterministicAdoptionRepositories()
    admission = _admission(repositories)
    suite = VerificationSuite(
        verification_repository=repositories.verifications,
        release_repository=repositories.release_decisions,
        evidence_repository=InMemoryReleaseEvidenceRepository(),
        clock=lambda: _NOW,
    )
    packs = (_pack("research-domain"), _pack("support-domain"))

    bundles = []
    for pack in packs:
        registered = admission.register(
            pack,
            signer=pack.signer_id,
            correlation_id=CorrelationId(f"correlation:{pack.pack_id}"),
            organization_id=_ORGANIZATION,
            host_contract=_host_contract(),
            alc_contract=_alc(pack),
        )
        assert registered.is_success and registered.value is not None
        provider, provider_registry = _provider(pack)
        active, retrieval, episode, lesson = _run_learning_path(pack, repositories, provider)
        result = suite.run(
            _ORGANIZATION,
            CorrelationId(f"release:{pack.pack_id}"),
            pack_id=pack.pack_id,
            immutable_version=pack.immutable_version,
            pack_contract_version=_PACK_CONTRACT.version,
            host_contract_version=_HOST_VERSION,
            alc_version=_ALC_VERSION,
            workflow_id=pack.workflows[0],
            fixed_seed="adoption-redesign-multidomain-seed",
            fixture_digest="fixture:non-video-shared-patterns",
            integration_checks=(
                ("integration.registration", registered.value.decision.value == "approved"),
                ("integration.activation", active.status is AgentLifecycleStatus.ACTIVE),
                ("integration.retrieval", retrieval.lesson_references == ()),
                (
                    "integration.episode",
                    episode.terminal_outcome is LearningTerminalOutcome.COMPLETED,
                ),
                ("integration.lesson", lesson.retrievable),
                (
                    "integration.provider-mock",
                    provider_registry.provider_ids == (provider.provider_id,),
                ),
            ),
            ui_projections=(_ui_extension(pack),),
            integration_coverage_complete=True,
            pack_contract=_PACK_CONTRACT,
            pack=pack,
        )
        assert result.is_success and result.value is not None
        assert result.value.release_decision is not None
        assert result.value.release_decision.status is ReleaseReadinessStatus.ELIGIBLE
        bundles.append(result.value)

    assert tuple(record.pack_id for record in repositories.registrations.records()) == tuple(
        pack.pack_id for pack in packs
    )
    assert len(repositories.lifecycle.records()) == len(packs)
    assert len(repositories.retrievals.records()) == len(packs)
    assert len(repositories.episodes.records()) == len(packs)
    assert len(repositories.lessons.records()) == len(packs)
    assert len(bundles) == 2
    assert all(
        len(bundle.ui_projections) == 1
        and bundle.ui_projections[0].projection_type == "domain-extension"
        for bundle in bundles
    )
    assert len(repositories.release_decisions.records()) == 2
