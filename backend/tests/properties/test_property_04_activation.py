"""Property tests for safe lifecycle and learning activation."""

from __future__ import annotations

from dataclasses import dataclass

from hypothesis import example, given, settings, strategies as st

from app.models.agents import AgentLearningContract, AgentLifecycleStatus, AgentSpec
from app.registry.activation import AgentActivationService

# Feature: generic-swarm-business-os, Property 4: Lifecycle and learning activation preserve safety
# **Validates: Requirements 2.5, 2.6, 2.7**


@dataclass(frozen=True, slots=True)
class ActivationCase:
    """A bounded activation input covering one learning-contract outcome."""

    kind: str
    suffix: int
    scope_count: int


@st.composite
def _activation_cases(draw: st.DrawFn) -> ActivationCase:
    kind = draw(
        st.sampled_from(("matched", "missing", "duplicate", "disabled_hook", "scope", "draft"))
    )
    if kind == "matched":
        scope_count = draw(st.sampled_from((1, 10)))
    elif kind == "scope":
        scope_count = draw(st.sampled_from((0, 11)))
    else:
        scope_count = 1
    return ActivationCase(
        kind=kind,
        suffix=draw(st.integers(min_value=0, max_value=9_999)),
        scope_count=scope_count,
    )


def _scopes(count: int) -> tuple[str, ...]:
    return tuple(f"scope-{index}" for index in range(count))


def _contracts(agent_id: str, case: ActivationCase) -> tuple[AgentLearningContract, ...]:
    matching_contract = AgentLearningContract(agent_id, True, _scopes(case.scope_count))
    if case.kind == "missing":
        return (AgentLearningContract(f"other-{agent_id}", True, ("scope-0",)),)
    if case.kind == "duplicate":
        return (matching_contract, matching_contract)
    if case.kind == "disabled_hook":
        return (AgentLearningContract(agent_id, False, ("scope-0",)),)
    return (matching_contract,)


@settings(max_examples=100, deadline=None)
@given(case=_activation_cases())
@example(case=ActivationCase("matched", 0, 1))
@example(case=ActivationCase("matched", 1, 10))
@example(case=ActivationCase("missing", 2, 1))
@example(case=ActivationCase("duplicate", 3, 1))
@example(case=ActivationCase("disabled_hook", 4, 1))
@example(case=ActivationCase("scope", 5, 0))
@example(case=ActivationCase("scope", 6, 11))
@example(case=ActivationCase("draft", 7, 1))
def test_learning_activation_requires_one_enabled_matching_contract_with_bounded_scopes(
    case: ActivationCase,
) -> None:
    """Valid learning contracts activate atomically; every invalid outcome preserves prior state.

    **Validates: Requirements 2.5, 2.6, 2.7**
    """
    learning_agent = AgentSpec(
        agent_id=f"sales.writer-{case.suffix}",
        status=(
            AgentLifecycleStatus.DRAFT
            if case.kind == "draft"
            else AgentLifecycleStatus.REGISTERED
        ),
        requires_learning=True,
    )
    peer_agent = AgentSpec(
        agent_id=f"sales.reviewer-{case.suffix}",
        status=AgentLifecycleStatus.REGISTERED,
    )
    agents = (learning_agent, peer_agent)

    contracts = _contracts(learning_agent.agent_id, case)
    result = AgentActivationService().activate_many(agents, contracts)

    if case.kind == "matched":
        assert result.is_success
        assert result.value == (
            learning_agent.activate_production(),
            peer_agent.activate_production(),
        )
    else:
        assert not result.is_success
        assert result.error is not None
        assert agents == (learning_agent, peer_agent)
        assert all(agent.status is not AgentLifecycleStatus.ACTIVE for agent in agents)
        assert all(not agent.production_active for agent in agents)
