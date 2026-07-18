"""Fail-closed, atomic production activation for domain-pack agents."""

from __future__ import annotations

from collections.abc import Iterable, Sequence

from app.models.agents import AgentLearningContract, AgentLifecycleStatus, AgentSpec
from app.models.contracts import ErrorCode, ErrorDetail, ErrorField, Result
from app.models.identifiers import CorrelationId, new_correlation_id


class AgentActivationService:
    """Evaluate production activation only after every required contract is valid."""

    def activate(
        self,
        agent: AgentSpec,
        learning_contracts: Iterable[AgentLearningContract],
        *,
        correlation_id: CorrelationId | None = None,
    ) -> Result[AgentSpec, ErrorDetail]:
        """Activate one agent or deny it without changing the supplied agent state."""
        result = self.activate_many(
            (agent,),
            learning_contracts,
            correlation_id=correlation_id,
        )
        if result.is_success:
            activated_agents = result.value
            assert activated_agents is not None
            return Result.success(activated_agents[0])
        error = result.error
        assert error is not None
        return Result.failure(error)

    def activate_many(
        self,
        agents: Sequence[AgentSpec],
        learning_contracts: Iterable[AgentLearningContract],
        *,
        correlation_id: CorrelationId | None = None,
    ) -> Result[tuple[AgentSpec, ...], ErrorDetail]:
        """Atomically activate agents, preserving every prior state when any check fails."""
        effective_correlation_id = correlation_id or new_correlation_id()
        prior_agents = tuple(agents)
        contracts = tuple(learning_contracts)

        for index, agent in enumerate(prior_agents):
            issue = self._activation_issue(agent, contracts, index)
            if issue is not None:
                return Result.failure(
                    ErrorDetail(
                        code=ErrorCode.INVALID_TRANSITION,
                        message="Production activation was denied; agent state is unchanged.",
                        correlation_id=effective_correlation_id,
                        fields=(issue,),
                    )
                )

        return Result.success(tuple(agent.activate_production() for agent in prior_agents))

    @staticmethod
    def _activation_issue(
        agent: AgentSpec,
        contracts: tuple[AgentLearningContract, ...],
        index: int,
    ) -> ErrorField | None:
        field_prefix = f"agents[{index}]"
        if agent.status is AgentLifecycleStatus.DRAFT:
            return ErrorField(
                f"{field_prefix}.status",
                "draft agents cannot be production active",
            )
        if agent.status is not AgentLifecycleStatus.REGISTERED:
            return ErrorField(
                f"{field_prefix}.status",
                "only registered agents can transition to production active",
            )
        if not agent.requires_learning:
            return None

        matching_contracts = tuple(
            contract
            for contract in contracts
            if isinstance(contract, AgentLearningContract) and contract.agent_id == agent.agent_id
        )
        if len(matching_contracts) != 1:
            return ErrorField(
                f"{field_prefix}.learning_contract",
                "exactly one learning contract must name this agent",
            )

        contract = matching_contracts[0]
        if contract.reflect_hook_enabled is not True:
            return ErrorField(
                f"{field_prefix}.learning_contract.reflect_hook_enabled",
                "the learning contract reflect hook must be enabled",
            )
        scopes = contract.approved_memory_scopes
        if not isinstance(scopes, tuple) or not 1 <= len(scopes) <= 10:
            return ErrorField(
                f"{field_prefix}.learning_contract.approved_memory_scopes",
                "the learning contract must define from 1 through 10 approved memory scopes",
            )
        return None
