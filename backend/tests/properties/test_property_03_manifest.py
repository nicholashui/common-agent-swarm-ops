"""Property tests for atomic domain-pack manifest registration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypedDict

from hypothesis import given, settings, strategies as st

from app.registry.pack_validator import DomainPackValidator
from app.repositories.pack_repository import (
    DomainPackRecord,
    InMemoryPackRepository,
    PackRegistrationStatus,
)

# Feature: generic-swarm-business-os, Property 3: Domain manifest validation and
# registration are atomic.
# **Validates: Requirements 2.2, 2.3, 2.4**

_STATUSES = st.sampled_from(("draft", "registered"))


class AgentPayload(TypedDict, total=False):
    """A bounded agent entry supplied to the manifest validator."""

    agent_id: str
    status: str
    production_activation_requested: bool


class ManifestPayload(TypedDict, total=False):
    """A bounded manifest fixture supplied to the manifest validator."""

    pack_id: str
    agents: list[AgentPayload]
    production_activation_requested: bool


@dataclass(frozen=True, slots=True)
class ManifestCase:
    """A bounded manifest and its expected final registration outcome."""

    manifest: ManifestPayload
    should_register: bool
    pre_register_same_pack: bool = False


@st.composite
def _valid_agents(
    draw: st.DrawFn, minimum: int = 1, maximum: int = 100
) -> list[AgentPayload]:
    count = draw(st.integers(min_value=minimum, max_value=maximum))
    agent_numbers = draw(
        st.lists(
            st.integers(min_value=0, max_value=10_000),
            min_size=count,
            max_size=count,
            unique=True,
        )
    )
    statuses = draw(st.lists(_STATUSES, min_size=count, max_size=count))
    return [
        {"agent_id": f"agent-{number}", "status": status}
        for number, status in zip(agent_numbers, statuses, strict=True)
    ]


@st.composite
def _valid_manifest(draw: st.DrawFn) -> ManifestPayload:
    return {
        "pack_id": f"pack-{draw(st.integers(min_value=0, max_value=10_000))}",
        "agents": draw(_valid_agents()),
    }


@st.composite
def _invalid_case(draw: st.DrawFn) -> ManifestCase:
    kind = draw(
        st.sampled_from(
            ("missing_pack", "empty", "too_many", "duplicate", "status", "activation")
        )
    )
    if kind == "missing_pack":
        return ManifestCase({"agents": draw(_valid_agents())}, False)
    if kind == "empty":
        return ManifestCase({"pack_id": "pack-empty", "agents": []}, False)
    if kind == "too_many":
        too_many_agents: list[AgentPayload] = [
            {"agent_id": f"agent-{index}", "status": "draft"} for index in range(101)
        ]
        return ManifestCase({"pack_id": "pack-too-many", "agents": too_many_agents}, False)
    if kind == "duplicate":
        number = draw(st.integers(min_value=0, max_value=10_000))
        duplicate_agents: list[AgentPayload] = [
            {"agent_id": f"agent-{number}", "status": "draft"},
            {"agent_id": f"AGENT-{number}", "status": "registered"},
        ]
        return ManifestCase({"pack_id": "pack-duplicate", "agents": duplicate_agents}, False)
    if kind == "status":
        invalid_status_agents: list[AgentPayload] = [
            {"agent_id": "agent-0", "status": "active"}
        ]
        return ManifestCase(
            {"pack_id": "pack-status", "agents": invalid_status_agents},
            False,
        )
    manifest = draw(_valid_manifest())
    if draw(st.booleans()):
        manifest["production_activation_requested"] = True
    else:
        manifest["agents"][0]["production_activation_requested"] = True
    return ManifestCase(manifest, False)


@st.composite
def _manifest_cases(draw: st.DrawFn) -> ManifestCase:
    kind = draw(st.sampled_from(("valid", "existing", "invalid")))
    if kind == "invalid":
        return draw(_invalid_case())
    return ManifestCase(draw(_valid_manifest()), kind == "valid", kind == "existing")


@settings(max_examples=100, deadline=None)
@given(case=_manifest_cases())
def test_manifest_registration_is_atomic_and_never_activates_production(
    case: ManifestCase,
) -> None:
    """Only unique valid manifests register all agents; every other outcome is inactive.

    **Validates: Requirements 2.2, 2.3, 2.4**
    """
    repository = InMemoryPackRepository()
    validator = DomainPackValidator(repository)
    prior_outcomes: tuple[DomainPackRecord, ...] = ()
    if case.pre_register_same_pack:
        prior = validator.register_inline(case.manifest)
        assert prior.is_success
        assert prior.value is not None
        assert prior.value.status is PackRegistrationStatus.REGISTERED
        prior_outcomes = (prior.value,)

    result = validator.register_inline(case.manifest)

    assert result.is_success
    assert result.value is not None
    record = result.value
    assert repository.outcomes() == (*prior_outcomes, record)
    assert not record.production_active
    assert all(not agent.production_active for agent in record.agents)
    if case.should_register:
        assert record.status is PackRegistrationStatus.REGISTERED
        assert record.validation_report.is_valid
        assert len(record.agents) == len(case.manifest["agents"])
        assert all(not agent.production_activation_denied for agent in record.agents)
    else:
        assert record.status is PackRegistrationStatus.INACTIVE
        assert not record.validation_report.is_valid
        assert all(agent.production_activation_denied for agent in record.agents)
