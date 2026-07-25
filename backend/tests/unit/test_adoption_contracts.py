"""Focused tests for adoption contract declarations and command outcomes."""

from __future__ import annotations

import pytest

from app.models.common import CompatibilityRange
from app.models.contracts import (
    AgentLearningContract,
    Allowed,
    Blocked,
    Denied,
    DomainPack,
    FailedRecoverable,
    HostContract,
    PackContract,
)
from app.models.identifiers import (
    ActorId,
    AgentId,
    CorrelationAwareIdentifier,
    CorrelationId,
    DomainPackId,
    EvidenceId,
)


def test_compatibility_ranges_compare_versions_and_boundaries() -> None:
    supported = CompatibilityRange("1.0.0", "2.0.0")

    assert supported.contains("1.0.0")
    assert supported.contains("1.5.0")
    assert supported.intersects(CompatibilityRange.exact("2.0.0"))
    assert not supported.intersects(CompatibilityRange("2.0.1", "3.0.0"))

    with pytest.raises(ValueError):
        CompatibilityRange("2.0.0", "1.0.0")


def test_declarations_keep_host_pack_alc_and_domain_versions_independent() -> None:
    host = HostContract(
        version="3.0.0",
        supported_pack_range=CompatibilityRange("1.0.0", "2.0.0"),
        supported_alc_range=CompatibilityRange("4.0.0", "5.0.0"),
    )
    alc = AgentLearningContract(
        agent_id=AgentId("researcher"),
        version="4.2.0",
        memory_scopes=("agent",),
        retrieval_policy="approved-lessons",
        reflection_policy="review-required",
        evaluation_references=("eval:alc-4",),
        retention_policy="retain-assessed",
        human_promotion_policy="required",
    )
    pack = DomainPack(
        pack_id=DomainPackId("research-pack"),
        immutable_version="7.1.0",
        pack_contract_version="1.0.0",
        host_compatibility_range=CompatibilityRange("3.0.0", "3.9.0"),
        alc_compatibility_range=CompatibilityRange("4.0.0", "4.9.0"),
        content_digest="sha256:pack",
        signer_id=ActorId("research-owner"),
        agents=(AgentId("researcher"),),
        workflows=("workflow:research",),
        capabilities=("search",),
        data_classifications=("public",),
        evaluation_references=("eval:pack-7",),
        required_alc_version="4.2.0",
    )
    pack_contract = PackContract(version="1.0.0")

    assert host.api_version == "3.0.0"
    assert alc.version == "4.2.0"
    assert pack.version == "7.1.0"
    assert pack_contract.validate(pack) == ()
    assert host.supported_alc_range.contains(alc.version)
    assert pack.host_range.intersects(CompatibilityRange.exact(host.version))
    assert pack.alc_range.intersects(CompatibilityRange.exact(alc.version))


def test_allowed_requires_evidence_and_other_outcomes_are_never_authorization() -> None:
    correlation_id = CorrelationId("correlation-1")
    allowed = Allowed(
        value="registered",
        evidence=(EvidenceId("evidence-1"),),
        correlation_id=correlation_id,
    )

    assert allowed.is_allowed
    assert bool(allowed)
    assert not Denied("policy denied", correlation_id).is_allowed
    assert not Blocked("approval pending", correlation_id).is_allowed
    assert not FailedRecoverable("repository unavailable", correlation_id).is_allowed
    assert not bool(Denied("policy denied", correlation_id))

    with pytest.raises(ValueError):
        Allowed(value="unsafe", evidence=(), correlation_id=correlation_id)


def test_correlation_aware_identifier_rejects_untraceable_values() -> None:
    identifier = CorrelationAwareIdentifier("run-1", CorrelationId("correlation-1"))

    assert identifier.value == "run-1"
    assert identifier.correlation_id == CorrelationId("correlation-1")

    with pytest.raises(ValueError):
        CorrelationAwareIdentifier("", CorrelationId("correlation-1"))
