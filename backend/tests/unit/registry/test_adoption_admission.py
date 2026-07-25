"""Deterministic admission, audit, ownership, and onboarding tests."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace

from app.models.common import CompatibilityRange
from app.models.contracts import (
    AgentLearningContract,
    DomainPack,
    HostContract,
    PackContract,
)
from app.models.control_plane import RegistrationDecision
from app.models.identifiers import ActorId, AgentId, CorrelationId, DomainPackId
from app.registry.admission import PackAdmission, PolicyDecision, RegistrationPolicy
from app.registry.compatibility import CompatibilityRegistry
from tests.fakes.adoption import DeterministicAdoptionRepositories, FakeFailurePlan

_PACK_CONTRACT = PackContract(version="1.0.0")
_CORRELATION = CorrelationId("adoption-admission-correlation")
_HOST_VERSION = "2.0.0"
_ALC_VERSION = "3.0.0"


def _pack(
    *,
    pack_id: str = "va-agent-swarm",
    immutable_version: str = "1.0.0",
    signer_id: str = "va-agent-swarm",
    evaluation_references: tuple[str, ...] = ("evaluation:pack",),
) -> DomainPack:
    return DomainPack(
        pack_id=DomainPackId(pack_id),
        immutable_version=immutable_version,
        pack_contract_version=_PACK_CONTRACT.version,
        host_compatibility_range=CompatibilityRange.exact(_HOST_VERSION),
        alc_compatibility_range=CompatibilityRange.exact(_ALC_VERSION),
        content_digest=f"sha256:{pack_id}-{immutable_version}",
        signer_id=ActorId(signer_id),
        agents=(AgentId(f"{pack_id}.agent"),),
        workflows=(f"{pack_id}.workflow",),
        capabilities=("memory.read",),
        data_classifications=("internal",),
        evaluation_references=evaluation_references,
        required_alc_version=_ALC_VERSION,
        asset_references=(
            f"asset:{pack_id}:roles@{immutable_version}#sha256:{pack_id}-{immutable_version}",
        ),
    )


def _host_contract() -> HostContract:
    return HostContract(
        version=_HOST_VERSION,
        supported_pack_range=CompatibilityRange.exact(_PACK_CONTRACT.version),
        supported_alc_range=CompatibilityRange.exact(_ALC_VERSION),
    )


def _alc_contract(pack: DomainPack) -> AgentLearningContract:
    return AgentLearningContract(
        agent_id=pack.agents[0],
        version=_ALC_VERSION,
        memory_scopes=(f"agent:{pack.agents[0]}",),
        retrieval_policy="approved-lessons",
        reflection_policy="review-required",
        evaluation_references=("evaluation:alc",),
        retention_policy="retain-assessed",
        human_promotion_policy="required",
    )


def _admission(
    repositories: DeterministicAdoptionRepositories,
    *,
    policies: tuple[RegistrationPolicy | Callable[[DomainPack], bool | PolicyDecision], ...] = (),
) -> PackAdmission:
    return PackAdmission(
        repositories.registrations,
        repositories.audit,
        pack_contract=_PACK_CONTRACT,
        policies=policies,
    )


def _manifest(pack: DomainPack, *, executable_code: str | None = None) -> dict[str, object]:
    manifest: dict[str, object] = {
        "pack_id": str(pack.pack_id),
        "immutable_version": pack.immutable_version,
        "pack_contract_version": pack.pack_contract_version,
        "host_compatibility_range": {
            "minimum": _HOST_VERSION,
            "maximum": _HOST_VERSION,
        },
        "alc_compatibility_range": {
            "minimum": _ALC_VERSION,
            "maximum": _ALC_VERSION,
        },
        "content_digest": pack.content_digest,
        "signer_id": str(pack.signer_id),
        "agents": [str(agent_id) for agent_id in pack.agents],
        "workflows": list(pack.workflows),
        "capabilities": list(pack.capabilities),
        "data_classifications": list(pack.data_classifications),
        "evaluation_references": list(pack.evaluation_references),
        "required_alc_version": pack.required_alc_version,
        "asset_references": list(pack.asset_references),
    }
    if executable_code is not None:
        manifest["code"] = executable_code
    return manifest


def test_one_pack_contract_is_shared_by_va_and_non_video_admission() -> None:
    repositories = DeterministicAdoptionRepositories()
    admission = _admission(repositories)
    va_pack = _pack()
    non_video_pack = _pack(
        pack_id="research-domain",
        signer_id="research-owner",
    )

    va_result = admission.register(
        va_pack,
        signer=va_pack.signer_id,
        correlation_id=CorrelationId("va-admission"),
    )
    non_video_result = admission.register(
        non_video_pack,
        signer=non_video_pack.signer_id,
        correlation_id=CorrelationId("research-admission"),
    )

    assert va_result.is_success and va_result.value is not None
    assert non_video_result.is_success and non_video_result.value is not None
    assert va_result.value.decision is RegistrationDecision.APPROVED
    assert non_video_result.value.decision is RegistrationDecision.APPROVED
    assert va_result.value.signer_id == ActorId("va-agent-swarm")
    assert va_result.value.asset_references == va_pack.asset_references
    assert non_video_result.value.asset_references == non_video_pack.asset_references
    assert repositories.registrations.records() == (va_result.value, non_video_result.value)


def test_policy_rejection_writes_one_correlated_audit_record() -> None:
    repositories = DeterministicAdoptionRepositories()
    admission = _admission(
        repositories,
        policies=(
            lambda _pack: PolicyDecision(
                passed=False,
                category="media_rights_policy",
                reason="Required media rights evidence is absent.",
            ),
        ),
    )
    pack = _pack()

    result = admission.register(
        pack,
        signer=pack.signer_id,
        correlation_id=_CORRELATION,
    )

    assert not result.is_success
    assert repositories.registrations.records() == ()
    assert len(repositories.audit.records) == 1
    audit = repositories.audit.records[0]
    assert audit.action == "pack.registration.rejected"
    assert audit.subject_reference == "va-agent-swarm@1.0.0"
    assert audit.outcome == "rejected:media_rights_policy"
    assert audit.metadata.correlation_id == _CORRELATION


def test_policy_rejection_completes_when_audit_persistence_fails() -> None:
    repositories = DeterministicAdoptionRepositories(FakeFailurePlan(fail_audit=True))
    admission = _admission(
        repositories,
        policies=(lambda _pack: PolicyDecision(False, "policy_outage_case"),),
    )
    pack = _pack()

    result = admission.register(
        pack,
        signer=pack.signer_id,
        correlation_id=_CORRELATION,
    )

    assert not result.is_success
    assert repositories.registrations.records() == ()
    assert repositories.audit.records == ()


def test_executable_code_is_rejected_with_location_and_correlation_audit() -> None:
    repositories = DeterministicAdoptionRepositories()
    admission = _admission(repositories)
    pack = _pack()

    result = admission.register(
        _manifest(pack, executable_code="print('not declarative')"),
        signer=pack.signer_id,
        correlation_id=_CORRELATION,
    )

    assert not result.is_success
    assert repositories.registrations.records() == ()
    assert len(repositories.audit.records) == 1
    audit = repositories.audit.records[0]
    assert audit.action == "pack.registration.rejected.executable_code"
    assert audit.subject_reference == "va-agent-swarm@1.0.0"
    assert audit.outcome == "rejected:executable_code;code_locations=$.code"
    assert audit.metadata.correlation_id == _CORRELATION


def test_executable_code_rejection_completes_when_audit_persistence_fails() -> None:
    repositories = DeterministicAdoptionRepositories(FakeFailurePlan(fail_audit=True))
    admission = _admission(repositories)
    pack = _pack()

    result = admission.register(
        _manifest(pack, executable_code="print('not declarative')"),
        signer=pack.signer_id,
        correlation_id=_CORRELATION,
    )

    assert not result.is_success
    assert repositories.registrations.records() == ()
    assert repositories.audit.records == ()


def test_late_executable_code_detection_preserves_succeeded_va_registration() -> None:
    repositories = DeterministicAdoptionRepositories()
    admission = _admission(repositories)
    pack = _pack()
    registered = admission.register(
        pack,
        signer=pack.signer_id,
        correlation_id=_CORRELATION,
    )
    assert registered.is_success and registered.value is not None

    late_detection = admission.report_late_executable_code(
        pack.pack_id,
        pack.immutable_version,
        "$.package_code",
    )

    assert late_detection.is_success
    assert late_detection.value == registered.value
    assert registered.value.decision is RegistrationDecision.APPROVED
    assert repositories.registrations.records() == (registered.value,)


def test_successor_version_retains_prior_approval_and_reproduction_contracts() -> None:
    repositories = DeterministicAdoptionRepositories()
    admission = _admission(repositories)
    first_pack = _pack(immutable_version="1.0.0")
    successor_pack = _pack(immutable_version="2.0.0")
    host_contract = _host_contract()
    alc_contract = _alc_contract(first_pack)

    first = admission.register(
        first_pack,
        signer=first_pack.signer_id,
        correlation_id=CorrelationId("first-version"),
        host_contract=host_contract,
        alc_contract=alc_contract,
    )
    successor = admission.register(
        successor_pack,
        signer=successor_pack.signer_id,
        correlation_id=CorrelationId("successor-version"),
        host_contract=host_contract,
        alc_contract=alc_contract,
    )

    assert first.is_success and first.value is not None
    assert successor.is_success and successor.value is not None
    assert first.value.decision is RegistrationDecision.APPROVED
    assert first.value.immutable_version == "1.0.0"
    assert first.value.host_contract_version == _HOST_VERSION
    assert first.value.alc_version == _ALC_VERSION
    assert successor.value.reproduction_references == (
        f"registration:{first.value.registration_id}",
        "pack:va-agent-swarm@1.0.0",
        f"host-contract:{_HOST_VERSION}",
        f"alc:{_ALC_VERSION}",
    )
    assert repositories.registrations.records() == (first.value, successor.value)


def test_new_domain_is_activation_eligible_only_with_admission_and_evaluation_evidence() -> None:
    repositories = DeterministicAdoptionRepositories()
    admission = _admission(repositories)
    pack = _pack(pack_id="new-domain", signer_id="new-domain-owner")
    admitted = admission.register(pack, signer=pack.signer_id, correlation_id=_CORRELATION)
    assert admitted.is_success

    compatibility = CompatibilityRegistry()
    eligible = compatibility.evaluate_activation_eligibility(
        pack,
        _PACK_CONTRACT,
        host_contract=_host_contract(),
        alc_contract=_alc_contract(pack),
    )
    missing_evaluations = compatibility.evaluate_activation_eligibility(
        replace(pack, evaluation_references=()),
        _PACK_CONTRACT,
        host_contract=_host_contract(),
        alc_contract=_alc_contract(pack),
    )

    assert eligible.eligible
    assert eligible.pack_contract_valid
    assert eligible.evaluation_references_present
    assert not missing_evaluations.eligible
    assert not missing_evaluations.pack_contract_valid
    assert not missing_evaluations.evaluation_references_present
