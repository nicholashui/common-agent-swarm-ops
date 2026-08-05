"""Thinking-model Host hooks for agent-loop cognitive profiles."""

from __future__ import annotations

import threading
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.thinking.catalog import list_models
from app.video.loop_v3.cynefin import classify_cynefin

ACTIVATION_POLICY: dict[str, Any] = {
    "live_llm_thinking": False,
    "mode": "offline_catalog_hooks",
    "note": (
        "Offline thinking-model catalog + recommendation for loop intensity. "
        "Not a full 40-model live metacognition engine."
    ),
}


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ThinkingRecommendRequest(StrictModel):
    goal: str = Field(min_length=1, max_length=4_000)
    cynefin_override: str | None = Field(default=None, max_length=32)


class ThinkingService:
    def __init__(self) -> None:
        self._lock = threading.RLock()

    @property
    def activation_policy(self) -> dict[str, Any]:
        return dict(ACTIVATION_POLICY)

    def policy(self) -> dict[str, Any]:
        return {
            "activation_policy": self.activation_policy,
            "model_count": len(list_models()),
            "note": ACTIVATION_POLICY["note"],
        }

    def catalog(self) -> dict[str, Any]:
        return {
            "items": list_models(),
            "count": len(list_models()),
            "activation_policy": self.activation_policy,
        }

    def recommend(self, request: ThinkingRecommendRequest) -> dict[str, Any]:
        cynefin = classify_cynefin(request.goal, override=request.cynefin_override)
        domain = str(cynefin.get("domain") or "complicated")
        mode = str(cynefin.get("mode") or "full")

        selected = ["cynefin", "premortem", "aar"]
        critic_modes = ["standard"]
        if domain in {"complex", "chaotic"}:
            selected.extend(["metacognition", "double_loop", "five_whys", "red_team"])
            critic_modes = ["standard", "red_team", "paul_elder"]
            enable_fast_path = False
            max_steps = 4
            reflection_style = "aar_double_loop_5whys"
        elif domain == "simple":
            selected.extend(["rpd", "dual_process"])
            enable_fast_path = True
            max_steps = 2
            reflection_style = "aar_light"
        else:
            selected.extend(["rpd", "metacognition", "paul_elder"])
            enable_fast_path = True
            max_steps = 3
            reflection_style = "aar_double_loop_lite"
            critic_modes = ["standard", "paul_elder"]

        by_id = {m["id"]: m for m in list_models()}
        models = [by_id[i] for i in selected if i in by_id]

        return {
            "ok": True,
            "goal": request.goal[:500],
            "cynefin": cynefin,
            "cognitive_profile": {
                "enable_fast_path": enable_fast_path,
                "operating_mode": mode,
                "max_steps": max_steps,
                "critic_modes": critic_modes,
                "reflection_style": reflection_style,
                "cynefin_classification": domain,
            },
            "selected_models": models,
            "activation_policy": self.activation_policy,
            "note": ACTIVATION_POLICY["note"],
        }


_SERVICE: ThinkingService | None = None
_LOCK = threading.Lock()


def get_thinking_service() -> ThinkingService:
    global _SERVICE
    with _LOCK:
        if _SERVICE is None:
            _SERVICE = ThinkingService()
        return _SERVICE


def reset_thinking_service_for_tests() -> ThinkingService:
    global _SERVICE
    with _LOCK:
        _SERVICE = ThinkingService()
        return _SERVICE
