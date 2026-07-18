"""Immutable agent lifecycle and learning-contract models."""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import StrEnum


class AgentLifecycleStatus(StrEnum):
    """Lifecycle states available to a registered domain-pack agent."""

    DRAFT = "draft"
    REGISTERED = "registered"
    ACTIVE = "active"


@dataclass(frozen=True, slots=True)
class AgentSpec:
    """A domain-pack agent and its production activation state."""

    agent_id: str
    status: AgentLifecycleStatus
    requires_learning: bool = False
    allowed_tools: tuple[str, ...] = ()
    production_active: bool = False

    def activate_production(self) -> AgentSpec:
        """Return the production-active form of this already validated agent."""
        return replace(self, status=AgentLifecycleStatus.ACTIVE, production_active=True)


@dataclass(frozen=True, slots=True)
class AgentLearningContract:
    """The learning configuration required before a learning agent can activate."""

    agent_id: str
    reflect_hook_enabled: bool
    approved_memory_scopes: tuple[str, ...]
