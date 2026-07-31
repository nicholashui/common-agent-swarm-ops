"""Host-owned live media adapters (Sora, Veo, Runway, ElevenLabs).

Adapters remain broker-registered as local_only host tools. Network I/O is
performed only inside the host media_production module when production flags
and credentials are present.
"""

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
from app.video.media_production import (
    ADAPTER_ID_BY_PROVIDER,
    MediaGenerationRequest,
    MediaProviderId,
    generate_media,
)

LIVE_ADAPTER_VERSION = "1.0.0"


@dataclass(frozen=True, slots=True)
class LiveMediaAdapter:
    """Host tool adapter for one live media provider."""

    provider: MediaProviderId
    adapter_id: str
    version: str = LIVE_ADAPTER_VERSION
    local_only: bool = field(default=True, init=False)
    _retained_effects: list[ToolEffect] = field(default_factory=list, repr=False, compare=False)

    def __post_init__(self) -> None:
        if not is_safe_tool_identifier(self.adapter_id):
            raise ValueError("Adapter identifiers must be safe registry identifiers")
        expected = ADAPTER_ID_BY_PROVIDER[self.provider]
        if self.adapter_id != expected:
            raise ValueError(f"Adapter id must be {expected}")

    def execute(self, arguments: Mapping[str, ToolInputValue]) -> LocalAdapterResult:
        """Invoke host media generation for this provider."""
        require_broker_invocation()
        prompt = _as_str(
            arguments.get("prompt") or arguments.get("text") or arguments.get("script")
        )
        model = _as_str(arguments.get("model")) or None
        voice_id = _as_str(arguments.get("voice_id")) or None
        duration = _as_int(arguments.get("duration_seconds") or arguments.get("duration"))
        result = generate_media(
            MediaGenerationRequest(
                prompt=prompt or " ",
                provider=self.provider,
                model=model,
                voice_id=voice_id,
                duration_seconds=duration,
            )
        )
        # Digest includes outcome so broker evidence reflects success/failure.
        digest_input = (
            f"{self.adapter_id}|{self.version}|{result.outcome}|{canonical_tool_input(arguments)}"
        )
        return LocalAdapterResult(
            outcome=result.outcome,
            effect_digest=sha256(digest_input.encode("utf-8")).hexdigest(),
            reversible=True,
            compensation_reference=result.artifact_uri,
        )

    @property
    def retained_effects(self) -> tuple[ToolEffect, ...]:
        return tuple(self._retained_effects)

    def retain_tool_effect(self, effect: ToolEffect) -> None:
        require_broker_invocation()
        if effect.adapter_id != self.adapter_id:
            raise ValueError("An adapter can retain only its own tool effects")
        self._retained_effects.append(effect)


def default_live_media_adapters() -> tuple[LiveMediaAdapter, ...]:
    """Register all supported live media provider adapters."""
    return tuple(
        LiveMediaAdapter(provider=provider, adapter_id=adapter_id)
        for provider, adapter_id in ADAPTER_ID_BY_PROVIDER.items()
    )


def _as_str(value: object) -> str:
    return value.strip() if isinstance(value, str) else ""


def _as_int(value: object) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None
