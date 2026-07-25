"""Focused compatibility, activation, invocation, and matrix tests."""

from __future__ import annotations

from app.models.common import CompatibilityRange
from app.models.contracts import (
    AgentLearningContract,
    Denied,
    DomainPack,
    HostContract,
    PackContract,
)
from app.models.control_plane import CompatibilityStatus
from app.models.identifiers import ActorId, AgentId, DomainPackId
from app.registry.compatibility import CompatibilityRegistry


def _host() -> HostContract:
    return HostContract(
        version="3.0.0",
        supported_pack_range=CompatibilityRange("1.0.0", "2.0.0"),
        supported_alc_range=CompatibilityRange("4.0.0", "5.0.0"),
    )


def _alc(version: str = "4.2.0") -> AgentLearningContract:
    return AgentLearningContract(
        agent_id=AgentId("researcher"),
        version=version,
        memory_scopes=("agent",),
        retrieval_policy="approved-lessons",
        reflection_policy="review-required",
        evaluation_references=("evaluation:alc",),
        retention_policy="retain-assessed",
        human_promotion_policy="required",
    )


def _pack(
    *,
    host_range: CompatibilityRange | None = None,
    alc_range: CompatibilityRange | None = None,
    evaluation_references: tuple[str, ...] = ("evaluation:pack",),
) -> DomainPack:
    return DomainPack(
        pack_id=DomainPackId("research-pack"),
        immutable_version="7.1.0",
        pack_contract_version="1.0.0",
        host_compatibility_range=host_range or CompatibilityRange("3.0.0", "3.9.0"),
        alc_compatibility_range=alc_range or CompatibilityRange("4.1.0", "4.9.0"),
        content_digest="sha256:research-pack",
        signer_id=ActorId("research-owner"),
        agents=(AgentId("researcher"),),
        workflows=("workflow:research",),
        capabilities=("search",),
        data_classifications=("public",),
        evaluation_references=evaluation_references,
        required_alc_version="4.2.0",
    )


def test_compatibility_requires_intersection_with_host_and_alc_ranges() -> None:
    registry = CompatibilityRegistry()
    pack = _pack()

    status = registry.evaluate(pack, _host(), _alc())

    assert status is CompatibilityStatus.COMPATIBLE
    evaluation = registry.evaluation_for(pack.pack_id, pack.immutable_version)
    assert evaluation is not None
    assert evaluation.declared_host_intersects
    assert evaluation.declared_alc_intersects
    assert registry.status_for(pack.pack_id, pack.immutable_version) is status

    incompatible = _pack(host_range=CompatibilityRange("6.0.0", "7.0.0"))
    assert registry.evaluate(incompatible, _host(), _alc()) is CompatibilityStatus.INCOMPATIBLE
    assert not registry.can_submit_invocation(incompatible)


def test_activation_requires_pack_contract_evaluation_references_and_compatibility() -> None:
    registry = CompatibilityRegistry()
    pack = _pack()
    registry.evaluate(pack, _host(), _alc())

    eligibility = registry.evaluate_activation_eligibility(pack, PackContract("1.0.0"))

    assert eligibility.is_eligible
    assert registry.can_activate(pack)

    missing_references = _pack(evaluation_references=())
    registry.evaluate(missing_references, _host(), _alc())
    blocked = registry.evaluate_activation_eligibility(missing_references, PackContract("1.0.0"))

    assert not blocked.is_eligible
    assert "evaluation_references" in blocked.failure_reasons
    assert not registry.can_activate(missing_references)


def test_incompatible_status_denies_activation_and_every_invocation_submission() -> None:
    registry = CompatibilityRegistry()
    pack = _pack(host_range=CompatibilityRange("9.0.0", "10.0.0"))
    registry.evaluate(pack, _host(), _alc())

    activation = registry.guard_activation(pack)
    invocation = registry.guard_invocation(pack)

    assert not activation.is_allowed
    assert not invocation.is_allowed
    assert isinstance(activation, Denied)
    assert isinstance(invocation, Denied)
    assert "compatibility" in str(activation.reason)
    assert "compatibility" in str(invocation.reason)


def test_designated_supported_combinations_are_retained_for_verification() -> None:
    registry = CompatibilityRegistry()

    recorded = registry.record_supported_combination(_host(), PackContract("1.0.0"), _alc())

    assert recorded.is_success
    assert recorded.value is not None
    assert recorded.value.status is CompatibilityStatus.COMPATIBLE
    assert registry.compatibility_matrix == (recorded.value,)
    assert registry.matrix_repository.entries() == (recorded.value,)

    duplicate = registry.record_supported_combination(_host(), PackContract("1.0.0"), _alc())
    assert not duplicate.is_success


def test_range_only_evaluation_can_supply_independent_alc_range() -> None:
    registry = CompatibilityRegistry()
    declared = CompatibilityRange("1.0.0", "2.0.0")
    supported_host = CompatibilityRange("2.0.0", "3.0.0")
    supported_alc = CompatibilityRange("4.0.0", "5.0.0")

    status = registry.evaluate(
        declared,
        supported_host,
        supported_alc,
        pack_alc_range=CompatibilityRange("4.0.0", "4.5.0"),
    )

    assert status is CompatibilityStatus.COMPATIBLE
