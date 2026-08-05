"""Offline Podcast / audio vertical foundation.

Episode outline + VO/sound plan. Live TTS/ElevenLabs fail-closed here.
"""

from __future__ import annotations

import re
import threading
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

ACTIVATION_POLICY: dict[str, Any] = {
    "production_audio": False,
    "live_tts": False,
    "elevenlabs": False,
    "mode": "offline_deterministic_stub",
    "note": (
        "Offline podcast structure + VO/sound plan. "
        "Live ElevenLabs/TTS requires separate Host media go-live."
    ),
}


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class PodcastOutlineRequest(StrictModel):
    topic: str = Field(min_length=1, max_length=4_000)
    duration_min: int = Field(default=15, ge=3, le=180)
    format: str = Field(default="interview", max_length=64)
    allow_live_tts: bool = False


class PodcastService:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._runs: list[dict[str, Any]] = []

    @property
    def activation_policy(self) -> dict[str, Any]:
        return dict(ACTIVATION_POLICY)

    def policy(self) -> dict[str, Any]:
        return {
            "activation_policy": self.activation_policy,
            "formats": ["interview", "solo", "narrative", "news"],
            "agent_id": "specials.podcast-agent",
            "linked_agents": [
                "video.voiceover",
                "video.sounddesign",
                "video.soundmixer",
                "video.composer",
            ],
            "note": ACTIVATION_POLICY["note"],
        }

    def outline(self, request: PodcastOutlineRequest) -> dict[str, Any]:
        if request.allow_live_tts:
            return {
                "ok": False,
                "error": (
                    "Live TTS / ElevenLabs is not enabled on this Host foundation. "
                    "Fail-closed offline outline only."
                ),
                "activation_policy": self.activation_policy,
            }
        topic = request.topic.strip()
        fmt = (request.format or "interview").strip().lower()
        minutes = request.duration_min
        segments = _segments(fmt, minutes, topic)
        payload = {
            "ok": True,
            "run_id": f"pod_{uuid4().hex[:12]}",
            "topic": topic[:500],
            "format": fmt,
            "duration_min": minutes,
            "title_options": [
                f"{topic[:60]} — cold open",
                f"Why {topic[:40]} matters now",
                f"Deep dive: {topic[:50]}",
            ],
            "segments": segments,
            "vo_plan": {
                "hosts": 1 if fmt == "solo" else 2,
                "tone": "conversational clear" if fmt != "narrative" else "storyteller",
                "stub_tool": "media.stub",
                "live_tts": False,
            },
            "sound_plan": {
                "beds": ["soft bed under intro", "sting transitions"],
                "mix_notes": ["voice primary", "music −18 LUFS under dialogue"],
                "linked_agents": ["video.sounddesign", "video.soundmixer"],
            },
            "handoff_hints": [
                "Run intent.analyze on topic before research",
                "Use research.query for fact segments",
                "Package HITL before any live VO provider",
            ],
            "activation_policy": self.activation_policy,
            "note": ACTIVATION_POLICY["note"],
        }
        with self._lock:
            self._runs.append(payload)
            if len(self._runs) > 300:
                self._runs = self._runs[-200:]
        return payload

    def recent(self, *, limit: int = 20) -> list[dict[str, Any]]:
        limit = max(1, min(limit, 100))
        with self._lock:
            return list(self._runs[-limit:])


def _segments(fmt: str, minutes: int, topic: str) -> list[dict[str, Any]]:
    if fmt == "solo":
        blueprint = [
            ("cold_open", 0.08, "Hook claim"),
            ("promise", 0.07, "What listener gets"),
            ("body", 0.55, "Main teaching / story"),
            ("takeaways", 0.15, "3 bullets"),
            ("cta", 0.15, "Subscribe / next"),
        ]
    elif fmt == "narrative":
        blueprint = [
            ("cold_open", 0.1, "Scene in media res"),
            ("setup", 0.2, "World + stakes"),
            ("turn", 0.35, "Complication"),
            ("climax", 0.2, "Payoff"),
            ("tag", 0.15, "Reflection"),
        ]
    else:
        blueprint = [
            ("cold_open", 0.08, "Provocative question"),
            ("intros", 0.1, "Hosts + guest"),
            ("act_1", 0.25, f"Context on {topic[:40]}"),
            ("act_2", 0.3, "Deep dive / debate"),
            ("act_3", 0.17, "Actionable takeaways"),
            ("outro", 0.1, "Credits + CTA"),
        ]
    out = []
    t = 0.0
    for i, (sid, frac, note) in enumerate(blueprint):
        dur = max(0.5, round(minutes * frac, 2))
        out.append(
            {
                "segment_id": sid,
                "order": i + 1,
                "start_min": round(t, 2),
                "duration_min": dur,
                "note": note,
            }
        )
        t += dur
    return out


_SERVICE: PodcastService | None = None
_LOCK = threading.Lock()


def get_podcast_service() -> PodcastService:
    global _SERVICE
    with _LOCK:
        if _SERVICE is None:
            _SERVICE = PodcastService()
        return _SERVICE


def reset_podcast_service_for_tests() -> PodcastService:
    global _SERVICE
    with _LOCK:
        _SERVICE = PodcastService()
        return _SERVICE
