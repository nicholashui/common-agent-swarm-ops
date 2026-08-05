"""Offline psychological profile + recommendation foundation.

Audience cohort heuristics + emotional arc + retention tips.
Not live psychometrics / clinical models.
"""

from __future__ import annotations

import re
import threading
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

_TOKEN = re.compile(r"[a-z0-9]+", re.I)

ACTIVATION_POLICY: dict[str, Any] = {
    "production_psychometrics": False,
    "clinical_claims": False,
    "live_audience_panels": False,
    "mode": "offline_deterministic_stub",
    "note": (
        "Offline audience/emotion profile for video creative. "
        "Not clinical psychology, not live panel data."
    ),
}

_COHORTS: list[tuple[str, tuple[str, ...], dict[str, float]]] = [
    (
        "gen_z_scroll",
        ("tiktok", "reels", "ugc", "viral", "short"),
        {"novelty_seeking": 0.8, "pace": 0.85, "social_proof": 0.7},
    ),
    (
        "brand_buyer",
        ("brand", "product", "ad", "roas", "conversion", "cta"),
        {"clarity": 0.85, "trust": 0.8, "pace": 0.55},
    ),
    (
        "cinephile",
        ("cinematic", "film", "noir", "wuxia", "arthouse", "drama"),
        {"aesthetic_depth": 0.9, "pace": 0.4, "novelty_seeking": 0.6},
    ),
    (
        "learner",
        ("tutorial", "explain", "howto", "documentary", "edu"),
        {"clarity": 0.9, "retention_structure": 0.75, "pace": 0.5},
    ),
]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class PsychProfileRequest(StrictModel):
    brief: str = Field(min_length=1, max_length=8_000)
    locale: str = Field(default="en", max_length=16)
    platform: str = Field(default="", max_length=64)


class PsychRecommendRequest(StrictModel):
    brief: str = Field(min_length=1, max_length=8_000)
    profile_id: str | None = Field(default=None, max_length=120)
    n_hooks: int = Field(default=4, ge=1, le=10)


class PsychologyService:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._profiles: dict[str, dict[str, Any]] = {}
        self._runs: list[dict[str, Any]] = []

    @property
    def activation_policy(self) -> dict[str, Any]:
        return dict(ACTIVATION_POLICY)

    def policy(self) -> dict[str, Any]:
        return {
            "activation_policy": self.activation_policy,
            "agent_id": "specials.psychological-profile-agent",
            "linked_agents": [
                "video.audiencesim",
                "video.emotionalarc",
                "video.retentionoptimizer",
            ],
            "note": ACTIVATION_POLICY["note"],
        }

    def profile(self, request: PsychProfileRequest) -> dict[str, Any]:
        brief = request.brief.strip()
        lower = brief.lower()
        platform = (request.platform or "").strip().lower()
        cohort_id, traits = _match_cohort(lower, platform)
        emotional_arc = _emotional_arc(lower, cohort_id)
        profile_id = f"psych_{uuid4().hex[:10]}"
        profile = {
            "profile_id": profile_id,
            "cohort_id": cohort_id,
            "locale": request.locale,
            "platform": platform or _infer_platform(lower),
            "traits": traits,
            "emotional_arc": emotional_arc,
            "emotional_target": {
                "valence": emotional_arc["peak_valence"],
                "arousal": emotional_arc["peak_arousal"],
            },
            "retention_levers": _retention_levers(cohort_id),
            "activation_policy": self.activation_policy,
            "note": ACTIVATION_POLICY["note"],
        }
        with self._lock:
            self._profiles[profile_id] = profile
            if len(self._profiles) > 500:
                # drop oldest arbitrarily
                for k in list(self._profiles.keys())[:100]:
                    self._profiles.pop(k, None)
        return {"ok": True, "profile": profile}

    def recommend(self, request: PsychRecommendRequest) -> dict[str, Any]:
        brief = request.brief.strip()
        profile: dict[str, Any] | None = None
        if request.profile_id:
            with self._lock:
                profile = self._profiles.get(request.profile_id)
        if profile is None:
            built = self.profile(
                PsychProfileRequest(brief=brief, platform="")
            )
            profile = built["profile"]

        hooks = _hooks(brief, str(profile.get("cohort_id") or ""), request.n_hooks)
        payload = {
            "ok": True,
            "run_id": f"preco_{uuid4().hex[:12]}",
            "profile_id": profile.get("profile_id"),
            "cohort_id": profile.get("cohort_id"),
            "hooks": hooks,
            "emotional_target": profile.get("emotional_target"),
            "creative_guidance": [
                "Align aesthetics emotional_target with profile peak",
                "Front-load hook matching cohort pace trait",
                "Use intent.analyze + creative.ideate before script",
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


def _match_cohort(lower: str, platform: str) -> tuple[str, dict[str, float]]:
    text = f"{lower} {platform}"
    best = "gen_z_scroll"
    best_score = 0
    best_traits: dict[str, float] = {"novelty_seeking": 0.5, "pace": 0.5}
    for cid, keys, traits in _COHORTS:
        score = sum(1 for k in keys if k in text)
        if score > best_score:
            best_score = score
            best = cid
            best_traits = dict(traits)
    return best, best_traits


def _infer_platform(lower: str) -> str:
    if "tiktok" in lower or "reels" in lower:
        return "short_form"
    if "youtube" in lower:
        return "youtube"
    if "cinema" in lower or "film" in lower:
        return "long_form"
    return "general"


def _emotional_arc(lower: str, cohort: str) -> dict[str, Any]:
    if any(k in lower for k in ("noir", "tragic", "dark")):
        return {
            "shape": "descent_then_resolve",
            "beats": ["setup_tension", "deepen", "turn", "release"],
            "peak_valence": -0.25,
            "peak_arousal": 0.7,
        }
    if cohort == "gen_z_scroll":
        return {
            "shape": "spike_early",
            "beats": ["hook", "value", "twist", "cta"],
            "peak_valence": 0.35,
            "peak_arousal": 0.8,
        }
    if cohort == "learner":
        return {
            "shape": "steady_climb",
            "beats": ["promise", "teach", "example", "recap"],
            "peak_valence": 0.2,
            "peak_arousal": 0.45,
        }
    return {
        "shape": "classic_arc",
        "beats": ["setup", "conflict", "climax", "resolution"],
        "peak_valence": 0.15,
        "peak_arousal": 0.6,
    }


def _retention_levers(cohort: str) -> list[str]:
    base = ["pattern interrupt every 8–12s", "clear progress signals"]
    if cohort == "gen_z_scroll":
        return ["0–1s visual hook", "captions on", "loopable ending"] + base
    if cohort == "brand_buyer":
        return ["problem→product in 5s", "social proof beat", "single CTA"] + base
    if cohort == "cinephile":
        return ["authored tone consistency", "payoff delayed but earned"] + base
    return ["chapter cards", "recap micro-beats"] + base


def _hooks(brief: str, cohort: str, n: int) -> list[dict[str, Any]]:
    seeds = {
        "gen_z_scroll": [
            "cold open on unexpected motion",
            "text-on-screen question in first frame",
            "sound design stinger before face",
            "duet-style reaction cut",
        ],
        "brand_buyer": [
            "pain-point freeze frame",
            "before/after smash cut",
            "testimonial face + product in same shot",
            "countdown urgency without spam",
        ],
        "cinephile": [
            "single practical light character entrance",
            "motif object return in final beat",
            "silence before music",
            "match cut across time",
        ],
        "learner": [
            "promise outcome in 3 words",
            "step counter overlay",
            "mistake-then-fix micro story",
            "checklist payoff",
        ],
    }
    pool = seeds.get(cohort) or seeds["gen_z_scroll"]
    out = []
    for i, seed in enumerate(pool[:n]):
        out.append(
            {
                "hook_id": f"hook_{i+1}",
                "line": seed,
                "ties_to_brief": brief[:80],
                "cohort": cohort,
            }
        )
    return out


_SERVICE: PsychologyService | None = None
_LOCK = threading.Lock()


def get_psychology_service() -> PsychologyService:
    global _SERVICE
    with _LOCK:
        if _SERVICE is None:
            _SERVICE = PsychologyService()
        return _SERVICE


def reset_psychology_service_for_tests() -> PsychologyService:
    global _SERVICE
    with _LOCK:
        _SERVICE = PsychologyService()
        return _SERVICE
