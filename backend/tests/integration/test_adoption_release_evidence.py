"""Load, initial-vertical, and named security-fixture release evidence."""

from __future__ import annotations

import hashlib
from collections.abc import Iterable, Mapping
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import cast

from app.audit import AuditWriter
from app.core.ingress import (
    ImportGuard,
    ImportSubmission,
    ProtectionOutcome,
    SecurityIndicator,
    UntrustedContent,
    UntrustedContentGuard,
    UntrustedContentSource,
)
from app.evaluation.verification_suite import VerificationSuite
from app.evidence.release_evidence import (
    InMemoryReleaseEvidenceRepository,
)
from app.governance.authorization import (
    ApprovalState,
    AuthorizationContext,
    DataAccessRequest,
)
from app.governance.tool_broker import (
    BrokerDenialReason,
    HostToolBroker,
    LocalAdapterResult,
    ToolRequest,
)
from app.memory.learning_lifecycle import ActivationEvidence, LearningLifecycleService
from app.memory.lesson_service import LessonService
from app.models.audit import AuditEvent
from app.models.common import CompatibilityRange
from app.models.contracts import (
    DomainPack,
    ErrorCode,
    ErrorDetail,
    Result,
)
from app.models.control_plane import (
    AgentLifecycleStatus,
    AuditRecord,
    CompatibilityStatus,
    ImportId,
    ImportRecord,
    ReleaseReadinessStatus,
    SecurityEvidence,
    SwarmInstance,
    SwarmInstanceId,
)
from app.models.evidence import LessonAssessmentOutcome
from app.models.identifiers import (
    ActorId,
    AgentId,
    CorrelationId,
    DomainPackId,
    OrganizationId,
)
from app.registry.admission import PackAdmission
from app.registry.compatibility import CompatibilityMatrixEntry
from app.repositories.control_plane import ImportRepository, InMemoryControlPlaneDatabase
from app.va.service import VaDomainAdapter, VaMetadata
from tests.fakes.adoption import DeterministicAdoptionRepositories
from tests.integration.test_adoption_shared_patterns import (
    _PACK_CONTRACT,
    _alc,
    _common_agent,
    _graph_revision,
    _graph_service,
    _handoff,
    _host_contract,
    _lifecycle,
    _metadata,
    _pack,
    _provider,
    _run_learning_path,
    _ui_extension,
)

_NOW = datetime(2025, 1, 1, tzinfo=UTC)
_ORGANIZATION = OrganizationId("organization-adoption-integration")
_CORRELATION = CorrelationId("correlation-adoption-integration")
_LOAD_FIXED_SEED = "adoption-redesign-load-seed-v1"
_LOAD_FIXTURE_DIGEST = "sha256:adoption-redesign-load-fixtures-v1"
_INITIAL_FIXED_SEED = "adoption-redesign-initial-va-seed-v1"
_INITIAL_FIXTURE_DIGEST = "sha256:adoption-redesign-initial-va-fixtures-v1"
_SECURITY_FIXED_SEED = "adoption-redesign-security-seed-v1"
_SECURITY_FIXTURE_DIGEST = "sha256:adoption-redesign-security-fixtures-v1"


@dataclass(frozen=True, slots=True)
class _LoadEvidence:
    """Per-pack operational evidence retained by the load proof."""

    pack_id: DomainPackId
    registration_decision: str
    lifecycle_statuses: tuple[AgentLifecycleStatus, ...]
    observability_agent: AgentId
    observability_episode_count: int
    bundle_release_status: ReleaseReadinessStatus


@dataclass(frozen=True, slots=True)
class _SecurityFixture:
    """One named security denial and its release-level audit evidence."""

    label: str
    slug: str
    denied: bool
    audit: AuditRecord
    evidence_references: tuple[str, ...] = ()


@dataclass
class _ImportRepository:
    """Small isolated import/security repository for ingress fixtures."""

    records: dict[ImportId, ImportRecord] = field(default_factory=dict)
    security_evidence: list[SecurityEvidence] = field(default_factory=list)

    def append_import(self, record: ImportRecord) -> Result[ImportRecord, ErrorDetail]:
        self.records[record.import_id] = record
        return Result.success(record)

    def get_import(
        self, organization_id: OrganizationId, import_id: ImportId
    ) -> Result[ImportRecord, ErrorDetail]:
        record = self.records.get(import_id)
        if record is None or record.metadata.organization_id != organization_id:
            return Result.failure(
                ErrorDetail(ErrorCode.NOT_FOUND, "Import record was not found.", _CORRELATION)
            )
        return Result.success(record)

    def replace_import(self, record: ImportRecord) -> Result[ImportRecord, ErrorDetail]:
        self.records[record.import_id] = record
        return Result.success(record)

    def append_security_evidence(
        self, record: SecurityEvidence
    ) -> Result[SecurityEvidence, ErrorDetail]:
        self.security_evidence.append(record)
        return Result.success(record)


@dataclass
class _Storage:
    """Storage spy proving rejected paths never reach quarantine."""

    quarantined: list[tuple[OrganizationId, str, bytes]] = field(default_factory=list)

    def quarantine(self, organization_id: OrganizationId, reference: str, content: bytes) -> None:
        self.quarantined.append((organization_id, reference, content))

    def release(self, organization_id: OrganizationId, reference: str) -> None:
        raise AssertionError("Rejected path traversal must not be released.")

    def discard(self, organization_id: OrganizationId, reference: str) -> None:
        raise AssertionError("Rejected path traversal must not reach storage.")


@dataclass
class _AuditEventRepository:
    """Minimal isolated AuditRepository for HostToolBroker denial fixtures."""

    events: list[AuditEvent] = field(default_factory=list)

    def append(self, event: AuditEvent) -> Result[AuditEvent, ErrorDetail]:
        self.events.append(event)
        return Result.success(event)


@dataclass
class _LocalAdapter:
    """Authorized local adapter whose invocation count must stay zero on denial."""

    adapter_id: str = "crm.lookup"
    version: str = "1.0.0"
    local_only: bool = True
    invocations: list[Mapping[str, object]] = field(default_factory=list)

    def execute(self, arguments: Mapping[str, object]) -> LocalAdapterResult:
        self.invocations.append(arguments)
        return LocalAdapterResult("completed", "effect-digest", reversible=True)


@dataclass(frozen=True, slots=True)
class _Protection:
    """Deterministic protection used to classify a Lesson-poisoning attempt."""

    protection_id: str = "lesson-safety"

    def inspect(self, content: UntrustedContent) -> ProtectionOutcome:
        del content
        return ProtectionOutcome(False, (SecurityIndicator.PROMPT_INJECTION,))


def _broker_context() -> AuthorizationContext:
    allowed_tools = frozenset({"crm.lookup"})
    return AuthorizationContext(
        agent_id="security-agent",
        step_id="security-step",
        organization_id=str(_ORGANIZATION),
        actor_id="security-actor",
        correlation_id="security-correlation",
        agent_allowed_tools=allowed_tools,
        step_declared_tools=allowed_tools,
        role_allowed_tools=allowed_tools,
        organization_allowed_tools=allowed_tools,
        risk_allowed_tools=allowed_tools,
        approval_state=ApprovalState.NOT_REQUIRED,
        domain_id="security-domain",
        pack_version="1.0.0",
        supported_pack_range=CompatibilityRange.exact("1.0.0"),
        declared_memory_scopes=frozenset({"agent:security:memory"}),
        declared_tool_ids=allowed_tools,
    )


def _audit_record(
    slug: str,
    *,
    action: str = "verification.security.denial",
    outcome: str = "denied_and_audited",
    source_references: Iterable[str] = (),
) -> AuditRecord:
    return AuditRecord(
        metadata=_metadata(f"security-audit:{slug}"),
        audit_id=f"audit:security:{slug}",
        action=action,
        subject_reference=f"security-fixture:{slug}",
        outcome=outcome,
        recorded_at=_NOW,
        actor_id=ActorId("verification-security-suite"),
        reason="Named security fixture was denied before the protected effect.",
        source_references=tuple(source_references),
    )


def _load_one_pack(
    pack: DomainPack,
    admission: PackAdmission,
    repositories: DeterministicAdoptionRepositories,
    suite: VerificationSuite,
) -> _LoadEvidence:
    """Register, activate, observe, and release one isolated load-proof pack."""
    typed_pack = pack.pack_id
    registration_result = admission.register(
        pack,
        signer=pack.signer_id,
        correlation_id=CorrelationId(f"load-registration:{typed_pack}"),
        organization_id=_ORGANIZATION,
        host_contract=_host_contract(),
        alc_contract=_alc(pack),
    )
    assert registration_result.is_success and registration_result.value is not None
    registration = registration_result.value

    lifecycle_service = LearningLifecycleService(
        lifecycle_repository=repositories.lifecycle,
        retrieval_repository=repositories.retrievals,
        episode_repository=repositories.episodes,
        audit_repository=repositories.audit,
        attempt_repository=repositories.attempts,
        clock=lambda: _NOW,
    )
    active_result = lifecycle_service.evaluate_activation(
        _lifecycle(pack),
        (_alc(pack),),
        ActivationEvidence(
            approved_agent_scoped_memory=True,
            pre_action_retrieval_enabled=True,
            learning_episode_capture_enabled=True,
            reflection_evaluator_enabled=True,
            retention_policy="retain-assessed",
            required_evaluations_passed=True,
            evidence_references=(f"load:activation:{typed_pack}",),
        ),
        correlation_id=CorrelationId(f"load-activation:{typed_pack}"),
    )
    assert active_result.is_success and active_result.value is not None
    suspended_result = lifecycle_service.suspend_for_change(
        active_result.value,
        (f"load:lifecycle-change:{typed_pack}",),
        correlation_id=CorrelationId(f"load-suspend:{typed_pack}"),
    )
    assert suspended_result.is_success and suspended_result.value is not None
    reactivated_result = lifecycle_service.evaluate_activation(
        suspended_result.value,
        (_alc(pack),),
        ActivationEvidence(
            approved_agent_scoped_memory=True,
            pre_action_retrieval_enabled=True,
            learning_episode_capture_enabled=True,
            reflection_evaluator_enabled=True,
            retention_policy="retain-assessed",
            required_evaluations_passed=True,
            evidence_references=(f"load:reactivation:{typed_pack}",),
        ),
        correlation_id=CorrelationId(f"load-reactivation:{typed_pack}"),
    )
    assert reactivated_result.is_success and reactivated_result.value is not None

    observability = LessonService(
        repositories.lessons,
        repositories.retrievals,
        repositories.episodes,
        repositories.audit,
        clock=lambda: _NOW,
    ).observability(
        _ORGANIZATION,
        pack.agents[0],
        correlation_id=CorrelationId(f"load-observability:{typed_pack}"),
    )
    assert observability.is_success and observability.value is not None
    observation = observability.value

    audit = _audit_record(
        f"load-{typed_pack}",
        action="verification.load.multi_domain_pack",
        source_references=(f"pack:{typed_pack}@{pack.immutable_version}",),
    )
    bundle_result = suite.run(
        _ORGANIZATION,
        CorrelationId(f"load-release:{typed_pack}"),
        pack_id=pack.pack_id,
        immutable_version=pack.immutable_version,
        pack_contract_version=_PACK_CONTRACT.version,
        host_contract_version="2.0.0",
        alc_version="3.0.0",
        workflow_id=pack.workflows[0],
        fixed_seed=_LOAD_FIXED_SEED,
        fixture_digest=_LOAD_FIXTURE_DIGEST,
        unit_checks=(
            ("load.registration", registration.decision.value == "approved"),
            ("load.activation", reactivated_result.value.status is AgentLifecycleStatus.ACTIVE),
        ),
        integration_checks=(
            (
                "load.isolation",
                registration.metadata.organization_id == _ORGANIZATION
                and registration.pack_id == pack.pack_id,
            ),
            (
                "load.observability",
                observation.agent_id == pack.agents[0] and observation.learning_episode_count == 0,
            ),
            (
                "load.lifecycle",
                tuple(
                    item.status
                    for item in repositories.lifecycle.records()
                    if item.pack_id == pack.pack_id
                )
                == (
                    AgentLifecycleStatus.ACTIVE,
                    AgentLifecycleStatus.SUSPENDED,
                    AgentLifecycleStatus.ACTIVE,
                ),
            ),
        ),
        audits=(audit,),
        ui_projections=(_ui_extension(pack),),
        integration_coverage_complete=True,
        pack_contract=_PACK_CONTRACT,
        pack=pack,
    )
    assert bundle_result.is_success and bundle_result.value is not None
    bundle = bundle_result.value
    assert bundle.release_decision is not None
    return _LoadEvidence(
        pack_id=pack.pack_id,
        registration_decision=registration.decision.value,
        lifecycle_statuses=tuple(
            item.status for item in repositories.lifecycle.records() if item.pack_id == pack.pack_id
        ),
        observability_agent=observation.agent_id,
        observability_episode_count=observation.learning_episode_count,
        bundle_release_status=bundle.release_decision.status,
    )


def test_load_proof_retains_isolation_registration_activation_observability_and_lifecycle() -> None:
    """Twenty-four concurrent registrations retain independent operational evidence."""
    repositories = DeterministicAdoptionRepositories()
    admission = PackAdmission(
        repositories.registrations,
        repositories.audit,
        pack_contract=_PACK_CONTRACT,
    )
    release_evidence = InMemoryReleaseEvidenceRepository()
    suite = VerificationSuite(
        verification_repository=repositories.verifications,
        release_repository=repositories.release_decisions,
        evidence_repository=release_evidence,
        clock=lambda: _NOW,
    )
    packs = tuple(_pack(f"load-domain-{index:02d}") for index in range(24))

    with ThreadPoolExecutor(max_workers=24) as executor:
        evidence = tuple(
            executor.map(
                lambda current_pack: _load_one_pack(current_pack, admission, repositories, suite),
                packs,
            )
        )

    assert len(evidence) == 24
    assert len({item.pack_id for item in evidence}) == 24
    assert len(repositories.registrations.records()) == 24
    assert len(repositories.lifecycle.records()) == 24 * 3
    assert len(repositories.verifications.records()) == 24
    assert len(repositories.release_decisions.records()) == 24
    assert len(release_evidence.audits()) == 24
    assert all(item.registration_decision == "approved" for item in evidence)
    assert all(item.bundle_release_status is ReleaseReadinessStatus.ELIGIBLE for item in evidence)
    assert all(item.observability_episode_count == 0 for item in evidence)
    assert all(
        item.lifecycle_statuses
        == (
            AgentLifecycleStatus.ACTIVE,
            AgentLifecycleStatus.SUSPENDED,
            AgentLifecycleStatus.ACTIVE,
        )
        for item in evidence
    )
    scoped = repositories.registrations.list_for_organization(_ORGANIZATION)
    assert scoped.is_success and scoped.value is not None and len(scoped.value) == 24
    foreign = repositories.registrations.list_for_organization(OrganizationId("foreign-org"))
    assert foreign.is_success and foreign.value == ()


def test_fixed_seed_initial_va_vertical_retains_trace_digests_audits_ui_and_release_output() -> (
    None
):
    """The initial VA path emits reproducible release evidence before full coverage."""
    pack = _pack("va-agent-swarm")
    repositories = DeterministicAdoptionRepositories()
    registered = PackAdmission(
        repositories.registrations,
        repositories.audit,
        pack_contract=_PACK_CONTRACT,
    ).register(
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
        metadata=_metadata("initial-va-swarm-record"),
        swarm_instance_id=SwarmInstanceId("swarm:va-agent-swarm"),
    )
    revision = _graph_revision(pack, _common_agent(pack), pattern)
    assert graph.create_revision(_ORGANIZATION, instance, revision, expected_revision=0).is_success
    graph_result = graph.validate_revision(_ORGANIZATION, revision.graph_revision_id)
    assert graph_result.is_success and graph_result.value is not None
    assert graph_result.value.eligible_for_run
    assert graph_repository.latest_validation(_ORGANIZATION, revision.graph_revision_id).value == (
        graph_result.value
    )

    from app.core.command_service import CommandService

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
    active, retrieval, episode, lesson = _run_learning_path(pack, repositories, provider)
    assert active.status is AgentLifecycleStatus.ACTIVE
    assert retrieval.lesson_references == ()
    assert episode.episode_id is not None
    assert lesson.assessment is LessonAssessmentOutcome.PASSED
    assert provider_registry.get(provider.provider_id) is provider

    audits = (
        _audit_record(
            "initial-va-trace",
            action="verification.initial_va.trace",
            source_references=(
                f"graph:{revision.graph_revision_id}",
                f"retrieval:{retrieval.retrieval_record_id}",
                f"episode:{episode.episode_id}",
            ),
        ),
        _audit_record(
            "initial-va-release-gates",
            action="verification.initial_va.release_gates",
            source_references=("approval:va-initial-vertical", "provider:authorized-mock"),
        ),
    )
    compatibility = CompatibilityMatrixEntry(
        pack_contract_version=_PACK_CONTRACT.version,
        host_contract_version="2.0.0",
        alc_version="3.0.0",
        status=CompatibilityStatus.COMPATIBLE,
        pack_id=pack.pack_id,
        immutable_version=pack.immutable_version,
        evidence_reference="compatibility:va-agent-swarm:1.0.0",
    )
    release_evidence = InMemoryReleaseEvidenceRepository()
    suite = VerificationSuite(
        verification_repository=repositories.verifications,
        release_repository=repositories.release_decisions,
        evidence_repository=release_evidence,
        clock=lambda: _NOW,
    )
    result = suite.run(
        _ORGANIZATION,
        CorrelationId("initial-va-release"),
        pack_id=pack.pack_id,
        immutable_version=pack.immutable_version,
        pack_contract_version=_PACK_CONTRACT.version,
        host_contract_version="2.0.0",
        alc_version="3.0.0",
        workflow_id=pack.workflows[0],
        fixed_seed=_INITIAL_FIXED_SEED,
        fixture_digest=_INITIAL_FIXTURE_DIGEST,
        unit_checks=(
            (
                "initial-va.provider-authorized",
                provider_registry.provider_ids == (provider.provider_id,),
            ),
            ("initial-va.activation", active.status is AgentLifecycleStatus.ACTIVE),
            ("initial-va.metadata", metadata_result.value.valid),
        ),
        property_checks=(("initial-va.fixed-seed-trace", True),),
        integration_checks=(
            ("initial-va.graph-compilation", graph_result.value.eligible_for_run),
            ("initial-va.retrieval-record", retrieval.lesson_references == ()),
            (
                "initial-va.learning-episode",
                episode.retrieval_record_id == retrieval.retrieval_record_id,
            ),
            (
                "initial-va.reflection-assessment",
                lesson.assessment is LessonAssessmentOutcome.PASSED,
            ),
            ("initial-va.authorized-provider", len(provider.calls) == 1),
        ),
        compatibility_results=(compatibility,),
        audits=audits,
        ui_projections=(_ui_extension(pack),),
        integration_coverage_complete=False,
        initial_vertical=True,
        pack_contract=_PACK_CONTRACT,
        pack=pack,
        handoffs=(_handoff(pack),),
    )

    assert result.is_success and result.value is not None
    bundle = result.value
    assert bundle.coverage_status.value == "incomplete"
    assert bundle.verification_run.fixed_seed == _INITIAL_FIXED_SEED
    assert bundle.verification_run.fixture_digest == _INITIAL_FIXTURE_DIGEST
    assert bundle.compatibility_results[0].status is CompatibilityStatus.COMPATIBLE
    assert len(bundle.audit_records) == 2
    assert len(bundle.ui_projections) == 1
    assert bundle.ui_projections[0].projection_type == "domain-extension"
    assert bundle.release_decision is not None
    assert bundle.release_decision.status is ReleaseReadinessStatus.ELIGIBLE
    assert not bundle.release_decision.integration_coverage_complete
    assert all(
        check.fixed_seed == _INITIAL_FIXED_SEED and check.fixture_digest == _INITIAL_FIXTURE_DIGEST
        for check in bundle.check_results
    )
    assert len(release_evidence.check_results()) == len(bundle.check_results)
    stored = repositories.release_decisions.get_terminal(
        _ORGANIZATION,
        pack.pack_id,
        pack.immutable_version,
        pack.workflows[0],
    )
    assert stored.is_success and stored.value == bundle.release_decision


def _malicious_domain_pack_fixture(
    repositories: DeterministicAdoptionRepositories,
) -> _SecurityFixture:
    """Reject executable content in a Domain_Pack and retain the admission audit."""
    pack = _pack("malicious-domain-pack")
    manifest = {
        "pack_id": str(pack.pack_id),
        "immutable_version": pack.immutable_version,
        "pack_contract_version": _PACK_CONTRACT.version,
        "host_compatibility_range": {
            "minimum": "2.0.0",
            "maximum": "2.0.0",
            "include_minimum": True,
            "include_maximum": True,
        },
        "alc_compatibility_range": {
            "minimum": "3.0.0",
            "maximum": "3.0.0",
            "include_minimum": True,
            "include_maximum": True,
        },
        "content_digest": pack.content_digest,
        "signer_id": str(pack.signer_id),
        "agents": [str(agent) for agent in pack.agents],
        "workflows": list(pack.workflows),
        "capabilities": list(pack.capabilities),
        "data_classifications": list(pack.data_classifications),
        "evaluation_references": list(pack.evaluation_references),
        "required_alc_version": pack.required_alc_version,
        "asset_references": list(pack.asset_references),
        "runtime": "python",
    }
    result = PackAdmission(
        repositories.registrations,
        repositories.audit,
        pack_contract=_PACK_CONTRACT,
    ).register(
        manifest,
        signer=pack.signer_id,
        correlation_id=CorrelationId("security-malicious-pack"),
        organization_id=_ORGANIZATION,
        host_contract=_host_contract(),
        alc_contract=_alc(pack),
    )
    assert not result.is_success
    assert result.error is not None and result.error.code is ErrorCode.VALIDATION_FAILED
    assert repositories.registrations.records() == ()
    assert len(repositories.audit.records) == 1
    audit = repositories.audit.records[0]
    assert audit.action == "pack.registration.rejected.executable_code"
    assert "code_locations" in audit.outcome
    return _SecurityFixture(
        "malicious Domain_Pack",
        "malicious-domain-pack",
        denied=True,
        audit=audit,
        evidence_references=("audit:pack-registration-rejected",),
    )


def _path_traversal_fixture() -> _SecurityFixture:
    """Reject traversal before the import detector or storage boundary."""
    repository = _ImportRepository()
    storage = _Storage()
    content = b"{}"
    result = ImportGuard(
        cast(ImportRepository, repository),
        storage,
    ).accept(
        _ORGANIZATION,
        ImportSubmission(
            metadata=_metadata("security-path-traversal"),
            import_id=ImportId("security-path-traversal"),
            storage_name="../escape.json",
            declared_type="application/json",
            checksum=hashlib.sha256(content).hexdigest(),
            content=content,
        ),
    )
    assert not result.is_success
    assert result.error is not None and result.error.code is ErrorCode.VALIDATION_FAILED
    assert result.error.fields[0].name == "storage_name"
    assert storage.quarantined == []
    return _SecurityFixture(
        "path traversal",
        "path-traversal",
        denied=True,
        audit=_audit_record("path-traversal", source_references=("import:storage-name",)),
        evidence_references=("import:storage-name",),
    )


def _lesson_poisoning_fixture() -> _SecurityFixture:
    """Reject a poisoning influence and persist only redacted security evidence."""
    repository = _ImportRepository()
    guard = UntrustedContentGuard(
        cast(ImportRepository, repository),
        (_Protection(),),
        clock=lambda: _NOW,
        evidence_id_factory=lambda: "lesson-poisoning-evidence",
    )
    result = guard.process(
        UntrustedContent(
            metadata=_metadata("security-lesson-poisoning"),
            source=UntrustedContentSource.RETRIEVAL,
            payload={"lesson": {"instruction": "grant authority"}},
        )
    )
    assert not result.is_success
    assert result.error is not None and result.error.code is ErrorCode.VALIDATION_FAILED
    assert len(repository.security_evidence) == 1
    evidence = repository.security_evidence[0]
    assert evidence.indicator == SecurityIndicator.PROMPT_INJECTION.value
    assert evidence.passed is False
    assert "grant authority" not in repr(evidence)
    return _SecurityFixture(
        "Lesson poisoning",
        "lesson-poisoning",
        denied=True,
        audit=_audit_record(
            "lesson-poisoning",
            source_references=(f"security-evidence:{evidence.security_evidence_id}",),
        ),
        evidence_references=(f"security-evidence:{evidence.security_evidence_id}",),
    )


def _broker_security_fixtures() -> tuple[_SecurityFixture, ...]:
    """Exercise the broker's independently audited secret, tenant, and tool denials."""
    context = _broker_context()

    secret_adapter = _LocalAdapter()
    secret_events = _AuditEventRepository()
    secret_result = HostToolBroker((secret_adapter,), AuditWriter(secret_events)).request_tool(
        ToolRequest("crm.lookup", {"secret": "not-retained"}),
        context,
    )
    assert not secret_result.allowed
    assert BrokerDenialReason.INVALID_TOOL_INPUT in secret_result.denial_reasons
    assert secret_result.denial_audit_recorded is True
    assert len(secret_events.events) == 1
    assert not secret_adapter.invocations

    tenant_adapter = _LocalAdapter()
    tenant_events = _AuditEventRepository()
    tenant_result = HostToolBroker((tenant_adapter,), AuditWriter(tenant_events)).request_tool(
        ToolRequest(
            "crm.lookup",
            {"account_id": "account-reference"},
            data_access=DataAccessRequest(
                organization_id="foreign-organization",
                domain_id="security-domain",
                pack_version="1.0.0",
                agent_id="security-agent",
                memory_scope="agent:security:memory",
            ),
        ),
        context,
    )
    assert not tenant_result.allowed
    assert tenant_result.denial_audit_recorded is True
    assert not tenant_adapter.invocations
    assert len(tenant_events.events) == 1

    tool_adapter = _LocalAdapter()
    tool_events = _AuditEventRepository()
    tool_result = HostToolBroker((tool_adapter,), AuditWriter(tool_events)).request_tool(
        ToolRequest("undeclared.tool", {"account_id": "account-reference"}),
        context,
    )
    assert not tool_result.allowed
    assert BrokerDenialReason.LOCAL_ADAPTER_NOT_ALLOWLISTED in tool_result.denial_reasons
    assert tool_result.denial_audit_recorded is True
    assert not tool_adapter.invocations
    assert len(tool_events.events) == 1

    return (
        _SecurityFixture(
            "secret disclosure",
            "secret-disclosure",
            denied=True,
            audit=_audit_record(
                "secret-disclosure",
                source_references=(f"audit-event:{secret_events.events[0].audit_event_id}",),
            ),
            evidence_references=(f"audit-event:{secret_events.events[0].audit_event_id}",),
        ),
        _SecurityFixture(
            "cross-tenant access",
            "cross-tenant-access",
            denied=True,
            audit=_audit_record(
                "cross-tenant-access",
                source_references=(f"audit-event:{tenant_events.events[0].audit_event_id}",),
            ),
            evidence_references=(f"audit-event:{tenant_events.events[0].audit_event_id}",),
        ),
        _SecurityFixture(
            "undeclared-tool access",
            "undeclared-tool-access",
            denied=True,
            audit=_audit_record(
                "undeclared-tool-access",
                source_references=(f"audit-event:{tool_events.events[0].audit_event_id}",),
            ),
            evidence_references=(f"audit-event:{tool_events.events[0].audit_event_id}",),
        ),
    )


def test_named_security_fixtures_retain_separate_denial_and_audit_release_results() -> None:
    """Every required malicious fixture is denied and independently represented."""
    repositories = DeterministicAdoptionRepositories()
    fixtures = (
        _malicious_domain_pack_fixture(repositories),
        _path_traversal_fixture(),
        _lesson_poisoning_fixture(),
        *_broker_security_fixtures(),
    )
    assert tuple(fixture.slug for fixture in fixtures) == (
        "malicious-domain-pack",
        "path-traversal",
        "lesson-poisoning",
        "secret-disclosure",
        "cross-tenant-access",
        "undeclared-tool-access",
    )
    valid_pack = _pack("security-fixture-proof")
    release_evidence = InMemoryReleaseEvidenceRepository()
    suite = VerificationSuite(
        verification_repository=repositories.verifications,
        release_repository=repositories.release_decisions,
        evidence_repository=release_evidence,
        clock=lambda: _NOW,
    )
    checks = tuple(
        (
            f"security.{fixture.slug}.denial-and-audit",
            fixture.denied
            and bool(fixture.audit.audit_id)
            and bool(fixture.audit.source_references or fixture.evidence_references),
        )
        for fixture in fixtures
    )
    result = suite.run(
        _ORGANIZATION,
        CorrelationId("security-fixture-release"),
        pack_id=valid_pack.pack_id,
        immutable_version=valid_pack.immutable_version,
        pack_contract_version=_PACK_CONTRACT.version,
        host_contract_version="2.0.0",
        alc_version="3.0.0",
        workflow_id=valid_pack.workflows[0],
        fixed_seed=_SECURITY_FIXED_SEED,
        fixture_digest=_SECURITY_FIXTURE_DIGEST,
        schema_checks=(("schema.named-security-fixtures", True),),
        integration_checks=checks,
        audits=tuple(fixture.audit for fixture in fixtures),
        integration_coverage_complete=True,
        pack_contract=_PACK_CONTRACT,
        pack=valid_pack,
    )

    assert result.is_success and result.value is not None
    bundle = result.value
    assert bundle.release_decision is not None
    assert bundle.release_decision.status is ReleaseReadinessStatus.ELIGIBLE
    assert len(bundle.audit_records) == len(fixtures) == 6
    assert len({audit.audit_id for audit in bundle.audit_records}) == 6
    assert (
        len(
            {
                check.check_name
                for check in bundle.check_results
                if check.layer.value == "integration"
            }
        )
        == 6
    )
    assert all(check.passed for check in bundle.check_results)
    assert all(
        check.fixed_seed == _SECURITY_FIXED_SEED
        and check.fixture_digest == _SECURITY_FIXTURE_DIGEST
        for check in bundle.check_results
    )
    assert all("not-retained" not in repr(audit) for audit in bundle.audit_records)
    assert all("grant authority" not in repr(audit) for audit in bundle.audit_records)
    assert len(release_evidence.audits()) == 6
