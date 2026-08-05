"""Offline LLM usage policy + budget ledger (no live provider calls)."""

from __future__ import annotations

import threading
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

ACTIVATION_POLICY: dict[str, Any] = {
    "live_provider_billing": False,
    "network": False,
    "mode": "offline_policy_ledger",
    "note": (
        "Offline LLM usage policy + estimated token ledger for Host runs. "
        "Does not call providers or pull live invoices."
    ),
}


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class LlmUsageRecordRequest(StrictModel):
    operation: str = Field(min_length=1, max_length=120)
    estimated_input_tokens: int = Field(default=0, ge=0, le=2_000_000)
    estimated_output_tokens: int = Field(default=0, ge=0, le=2_000_000)
    agent_id: str = Field(default="host", max_length=120)
    offline: bool = True


class LlmUsageService:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._entries: list[dict[str, Any]] = []
        self._budget_tokens = 200_000

    @property
    def activation_policy(self) -> dict[str, Any]:
        return dict(ACTIVATION_POLICY)

    def policy(self) -> dict[str, Any]:
        with self._lock:
            used = sum(
                int(e.get("estimated_input_tokens") or 0)
                + int(e.get("estimated_output_tokens") or 0)
                for e in self._entries
            )
        return {
            "activation_policy": self.activation_policy,
            "budget_tokens": self._budget_tokens,
            "used_tokens_estimate": used,
            "remaining_tokens_estimate": max(0, self._budget_tokens - used),
            "default_provider": "local_deterministic",
            "network_access": False,
            "agent_id": "specials.llm-usage",
            "note": ACTIVATION_POLICY["note"],
        }

    def record(self, request: LlmUsageRecordRequest) -> dict[str, Any]:
        if not request.offline:
            return {
                "ok": False,
                "error": "Live provider usage recording is not enabled on Host foundation.",
                "activation_policy": self.activation_policy,
            }
        entry = {
            "entry_id": f"llm_{uuid4().hex[:12]}",
            "operation": request.operation,
            "agent_id": request.agent_id,
            "estimated_input_tokens": request.estimated_input_tokens,
            "estimated_output_tokens": request.estimated_output_tokens,
            "total_estimate": request.estimated_input_tokens + request.estimated_output_tokens,
            "offline": True,
        }
        with self._lock:
            self._entries.append(entry)
            if len(self._entries) > 2000:
                self._entries = self._entries[-1500:]
            used = sum(
                int(e.get("total_estimate") or 0) for e in self._entries
            )
        return {
            "ok": True,
            "entry": entry,
            "budget_tokens": self._budget_tokens,
            "used_tokens_estimate": used,
            "within_budget": used <= self._budget_tokens,
            "activation_policy": self.activation_policy,
        }

    def recommend_mode(self, *, goal: str = "") -> dict[str, Any]:
        """Suggest cheap vs deep mode from offline budget headroom."""
        with self._lock:
            used = sum(int(e.get("total_estimate") or 0) for e in self._entries)
        remaining = max(0, self._budget_tokens - used)
        if remaining < 20_000:
            mode = "minimal"
            note = "Budget low — prefer fast path, screen modes, top_k small"
        elif remaining < 80_000:
            mode = "balanced"
            note = "Prefer offline stubs; avoid deep multi-crew unless needed"
        else:
            mode = "thorough"
            note = "Headroom available for multi-step loops within offline policy"
        g = (goal or "").lower()
        if any(k in g for k in ("asap", "cheap", "draft")):
            mode = "minimal"
        return {
            "ok": True,
            "mode": mode,
            "remaining_tokens_estimate": remaining,
            "note": note,
            "activation_policy": self.activation_policy,
        }

    def recent(self, *, limit: int = 50) -> list[dict[str, Any]]:
        limit = max(1, min(limit, 200))
        with self._lock:
            return list(self._entries[-limit:])


_SERVICE: LlmUsageService | None = None
_LOCK = threading.Lock()


def get_llm_usage_service() -> LlmUsageService:
    global _SERVICE
    with _LOCK:
        if _SERVICE is None:
            _SERVICE = LlmUsageService()
        return _SERVICE


def reset_llm_usage_service_for_tests() -> LlmUsageService:
    global _SERVICE
    with _LOCK:
        _SERVICE = LlmUsageService()
        return _SERVICE
