"""Versioned deterministic adapter implementation shared by local tools."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from hashlib import sha256

from app.governance.adapter_execution import require_broker_invocation
from app.governance.authorization import (
    ToolInputValue,
    canonical_tool_input,
    is_safe_tool_identifier,
)
from app.governance.tool_broker import LocalAdapterResult
from app.models.runs import ToolEffect


@dataclass(frozen=True, slots=True)
class DeterministicLocalAdapter:
    """A fixed-behavior local adapter with broker-retained effect evidence."""

    adapter_id: str
    version: str
    outcome: str
    reversible: bool = True
    compensation_reference: str | None = None
    local_only: bool = field(default=True, init=False)
    _retained_effects: list[ToolEffect] = field(default_factory=list, repr=False, compare=False)

    def __post_init__(self) -> None:
        """Validate immutable registry metadata without accepting executable configuration."""
        if not is_safe_tool_identifier(self.adapter_id):
            raise ValueError("Adapter identifiers must be safe registry identifiers")
        if not self.version or not self.outcome:
            raise ValueError("Deterministic local adapters require a version and outcome")

    def execute(self, arguments: Mapping[str, ToolInputValue]) -> LocalAdapterResult:
        """Return a stable result only while called by the Host broker."""
        require_broker_invocation()
        digest_input = f"{self.adapter_id}|{self.version}|{canonical_tool_input(arguments)}"
        return LocalAdapterResult(
            outcome=self.outcome,
            effect_digest=sha256(digest_input.encode("utf-8")).hexdigest(),
            reversible=self.reversible,
            compensation_reference=self.compensation_reference,
        )

    @property
    def retained_effects(self) -> tuple[ToolEffect, ...]:
        """Expose immutable completed-effect evidence for durable run retention."""
        return tuple(self._retained_effects)

    def retain_tool_effect(self, effect: ToolEffect) -> None:
        """Retain the exact broker-created effect for this adapter invocation."""
        require_broker_invocation()
        if effect.adapter_id != self.adapter_id:
            raise ValueError("An adapter can retain only its own tool effects")
        self._retained_effects.append(effect)
