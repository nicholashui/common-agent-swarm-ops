"""Focused lifecycle tests for AgentActivationService."""

from __future__ import annotations

from app.models.agents import AgentLearningContract, AgentLifecycleStatus, AgentSpec
from app.registry.activation import AgentActivationService


def _contract(
    agent_id: str,
    *,
    enabled: bool = True,
    scopes: tuple[str, ...] = ("agent",),
) -> AgentLearningContract:
    return AgentLearningContract(agent_id, enabled, scopes)


def test_registered_learning_agent_activates_with_boundary_scope_counts() -> None:
    service = AgentActivationService()
    agent = AgentSpec("sales.writer", AgentLifecycleStatus.REGISTERED, requires_learning=True)

    for scopes in (("agent",), tuple(f"scope-{index}" for index in range(10))):
        result = service.activate(agent, (_contract(agent.agent_id, scopes=scopes),))

        assert result.is_success
        assert result.value == AgentSpec(
            agent.agent_id,
            AgentLifecycleStatus.ACTIVE,
            requires_learning=True,
            production_active=True,
        )


def test_later_invalid_learning_contract_preserves_all_prior_agent_states() -> None:
    service = AgentActivationService()
    agents = (
        AgentSpec("sales.writer", AgentLifecycleStatus.REGISTERED, requires_learning=False),
        AgentSpec("sales.reviewer", AgentLifecycleStatus.REGISTERED, requires_learning=True),
    )
    initial_states = tuple(agents)
    invalid_contract_sets = (
        (),
        (_contract("sales.reviewer"), _contract("sales.reviewer")),
        (_contract("sales.reviewer", enabled=False),),
        (_contract("sales.reviewer", scopes=()),),
        (_contract("sales.reviewer", scopes=tuple(f"scope-{index}" for index in range(11))),),
    )

    for contracts in invalid_contract_sets:
        result = service.activate_many(agents, contracts)

        assert not result.is_success
        assert result.value is None
        assert result.error is not None
        assert agents == initial_states
        assert all(not agent.production_active for agent in agents)


def test_draft_agent_cannot_be_activated_in_production() -> None:
    draft = AgentSpec("sales.draft", AgentLifecycleStatus.DRAFT)

    result = AgentActivationService().activate(draft, ())

    assert not result.is_success
    assert result.error is not None
    assert draft.status is AgentLifecycleStatus.DRAFT
    assert not draft.production_active
