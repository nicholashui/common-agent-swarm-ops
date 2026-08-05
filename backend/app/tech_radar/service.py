"""Offline video-generation tech radar foundation.

Catalog of providers/modes with Host honesty (stub vs live-gated).
"""

from __future__ import annotations

import threading
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.video.tool_activation import LIVE_TOOL_IDS, STUB_TOOL_IDS, media_live_enabled

ACTIVATION_POLICY: dict[str, Any] = {
    "production_media": False,
    "auto_enable_live": False,
    "mode": "offline_radar",
    "note": (
        "Offline gen-video tech radar. Live providers remain gated; "
        "agent-loop Act stays stub/live_blocked."
    ),
}

_PROVIDERS: list[dict[str, Any]] = [
    {
        "id": "sora",
        "tool_id": "media.sora",
        "category": "text_to_video",
        "learn_now": True,
        "host_status": "live_gated",
    },
    {
        "id": "veo",
        "tool_id": "media.veo",
        "category": "text_to_video",
        "learn_now": True,
        "host_status": "live_gated",
    },
    {
        "id": "runway",
        "tool_id": "media.runway",
        "category": "image_to_video",
        "learn_now": True,
        "host_status": "live_gated",
    },
    {
        "id": "kling",
        "tool_id": "media.kling",
        "category": "text_to_video",
        "learn_now": False,
        "host_status": "not_fully_wired",
    },
    {
        "id": "elevenlabs",
        "tool_id": "media.elevenlabs",
        "category": "tts_voice",
        "learn_now": True,
        "host_status": "live_gated",
    },
    {
        "id": "media_stub",
        "tool_id": "media.stub",
        "category": "offline_stub",
        "learn_now": True,
        "host_status": "always_available",
    },
]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class TechRadarAdviseRequest(StrictModel):
    goal: str = Field(min_length=1, max_length=4_000)
    prefer_offline: bool = True


class TechRadarService:
    def __init__(self) -> None:
        self._lock = threading.RLock()

    @property
    def activation_policy(self) -> dict[str, Any]:
        pol = dict(ACTIVATION_POLICY)
        pol["media_live_env"] = media_live_enabled()
        return pol

    def policy(self) -> dict[str, Any]:
        return {
            "activation_policy": self.activation_policy,
            "provider_count": len(_PROVIDERS),
            "agent_id": "video_generation_tech_radar skill",
            "linked_agents": [
                "video.promptengineer",
                "video.benchmarkresearch",
                "video.evaluationharness",
            ],
            "note": ACTIVATION_POLICY["note"],
        }

    def catalog(self) -> dict[str, Any]:
        live_env = media_live_enabled()
        items = []
        for p in _PROVIDERS:
            tid = p["tool_id"]
            items.append(
                {
                    **p,
                    "in_live_tool_ids": tid in LIVE_TOOL_IDS,
                    "in_stub_tool_ids": tid in STUB_TOOL_IDS,
                    "agent_loop_active_mode": (
                        "stub"
                        if tid in STUB_TOOL_IDS and tid not in LIVE_TOOL_IDS
                        else "live_blocked"
                        if tid in LIVE_TOOL_IDS
                        else "unknown"
                    ),
                    "media_live_env": live_env,
                }
            )
        return {
            "ok": True,
            "items": items,
            "count": len(items),
            "activation_policy": self.activation_policy,
        }

    def advise(self, request: TechRadarAdviseRequest) -> dict[str, Any]:
        g = request.goal.lower()
        picks: list[str] = []
        if any(k in g for k in ("voice", "tts", "podcast", "narrat")):
            picks.append("elevenlabs")
        if any(k in g for k in ("image to video", "i2v", "runway")):
            picks.append("runway")
        if any(k in g for k in ("sora",)):
            picks.append("sora")
        if any(k in g for k in ("veo", "google")):
            picks.append("veo")
        if not picks:
            picks = ["media_stub", "sora", "veo"]
        if request.prefer_offline or not media_live_enabled():
            recommended = "media_stub"
            rationale = (
                "Prefer offline media.stub for loops; live providers remain "
                "activation-gated even if CASOPS_MEDIA_LIVE=1 on Act surface."
            )
        else:
            recommended = picks[0]
            rationale = "Live env noted; still use Host media_production brokers, not agent-loop Act."
        return {
            "ok": True,
            "goal": request.goal[:500],
            "recommended_provider_id": recommended,
            "candidates": picks,
            "rationale": rationale,
            "prompt_tips": [
                "Keep shot intent + constraints explicit",
                "Score outputs with aesthetics.evaluate offline",
                "Benchmark with evaluation harness golden cases",
            ],
            "activation_policy": self.activation_policy,
            "note": ACTIVATION_POLICY["note"],
        }


_SERVICE: TechRadarService | None = None
_LOCK = threading.Lock()


def get_tech_radar_service() -> TechRadarService:
    global _SERVICE
    with _LOCK:
        if _SERVICE is None:
            _SERVICE = TechRadarService()
        return _SERVICE


def reset_tech_radar_service_for_tests() -> TechRadarService:
    global _SERVICE
    with _LOCK:
        _SERVICE = TechRadarService()
        return _SERVICE
