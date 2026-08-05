"""Offline Intent Analysis (DIA lite) for video briefs / goals.

6-phase scaffold without live LLM pragmatics stack.
"""

from __future__ import annotations

import re
import threading
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

_TOKEN = re.compile(r"[a-z0-9]+", re.I)

ACTIVATION_POLICY: dict[str, Any] = {
    "production_dia": False,
    "live_llm": False,
    "mode": "offline_deterministic_stub",
    "note": (
        "Offline DIA lite for video briefs. Not full PIC/ToM multi-agent "
        "pragmatics or live Grok speech-act stack."
    ),
}

_PURPOSE_RULES: list[tuple[str, tuple[str, ...]]] = [
    ("promote", ("ad", "promo", "sell", "launch", "ugc", "roas", "cta", "conversion")),
    ("educate", ("explain", "tutorial", "how to", "teach", "guide", "documentary")),
    ("entertain", ("story", "drama", "comedy", "wuxia", "short film", "narrative", "trailer")),
    ("inform", ("news", "announce", "update", "report", "brief")),
    ("persuade", ("convince", "pitch", "fundraising", "recruit")),
]

_SPEECH_ACTS: list[tuple[str, tuple[str, ...]]] = [
    ("request", ("please", "need", "want", "create", "make", "generate", "plan")),
    ("directive", ("must", "should", "require", "ensure", "do not")),
    ("assertive", ("is", "are", "will be", "about")),
    ("commissive", ("promise", "commit", "deliver")),
]

_ARCHETYPE_HINTS: list[tuple[str, tuple[str, ...]]] = [
    ("B", ("ugc", "ad", "product", "tiktok", "reels")),
    ("A", ("cinematic", "narrative", "film", "drama")),
    ("I", ("documentary", "interview", "research")),
    ("C", ("music", "mv", "lyric")),
    ("J", ("explainer", "tutorial", "howto")),
]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class IntentAnalyzeRequest(StrictModel):
    text: str = Field(min_length=1, max_length=20_000)
    channel: str = Field(default="video_brief", max_length=64)
    locale: str = Field(default="en", max_length=16)
    allow_live_llm: bool = False


class IntentService:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._runs: list[dict[str, Any]] = []

    @property
    def activation_policy(self) -> dict[str, Any]:
        return dict(ACTIVATION_POLICY)

    def policy(self) -> dict[str, Any]:
        return {
            "activation_policy": self.activation_policy,
            "phases": [
                "context",
                "purpose",
                "surface",
                "pragmatic",
                "hidden_agenda",
                "judgment",
                "synthesis",
            ],
            "agent_id": "specials.intent-analysis-agent",
            "note": ACTIVATION_POLICY["note"],
        }

    def analyze(self, request: IntentAnalyzeRequest) -> dict[str, Any]:
        if request.allow_live_llm:
            return {
                "ok": False,
                "error": (
                    "Live LLM DIA is not enabled. "
                    "Fail-closed offline intent analysis only."
                ),
                "activation_policy": self.activation_policy,
            }

        text = request.text.strip()
        lower = text.lower()
        tokens = set(_TOKEN.findall(lower))
        run_id = f"intent_{uuid4().hex[:12]}"

        # Phase 0 context
        context = {
            "channel": request.channel,
            "locale": request.locale,
            "length_chars": len(text),
            "token_estimate": len(tokens),
            "looks_like_video_brief": any(
                k in lower
                for k in ("video", "shot", "script", "youtube", "tiktok", "film", "ad")
            ),
        }

        # Phase 1 purpose
        purpose_scores: dict[str, int] = {}
        for name, keys in _PURPOSE_RULES:
            purpose_scores[name] = sum(1 for k in keys if k in lower)
        purpose = max(purpose_scores, key=lambda k: purpose_scores[k])
        if purpose_scores[purpose] == 0:
            purpose = "entertain" if context["looks_like_video_brief"] else "inform"

        # Phase 2 surface
        surface = {
            "literal_summary": re.sub(r"\s+", " ", text)[:280],
            "entities_guess": sorted(
                t for t in tokens if len(t) > 4 and t not in {"video", "about", "with", "from"}
            )[:12],
            "constraints_found": _extract_constraints(lower),
        }

        # Phase 3 pragmatic / speech acts
        acts = []
        for act, keys in _SPEECH_ACTS:
            if any(k in lower for k in keys):
                acts.append(act)
        if not acts:
            acts = ["request"]
        pragmatic = {
            "speech_acts": acts,
            "grice_risks": _grice_risks(lower),
            "urgency": "high" if any(k in lower for k in ("asap", "urgent", "today")) else "normal",
        }

        # Phase 4 hidden agenda lite
        hidden = {
            "possible_implicatures": _implicatures(lower, purpose),
            "multi_angles": [
                f"Creator intent: {purpose}",
                "Audience: inferred from channel keywords",
                "Commercial pressure: present" if purpose == "promote" else "Commercial pressure: low",
            ],
            "confidence": 0.55 if purpose_scores.get(purpose, 0) else 0.4,
        }

        # Phase 5 judgment
        ethical_flags: list[str] = []
        if any(k in lower for k in ("scam", "deceive", "fake news", "deepfake without disclosure")):
            ethical_flags.append("possible_harmful_deception")
        judgment = {
            "clarity": min(1.0, 0.4 + 0.05 * min(12, len(tokens))),
            "specificity": min(1.0, 0.3 + 0.1 * len(surface["constraints_found"])),
            "ethical_flags": ethical_flags,
            "escalate_to_hitl": bool(ethical_flags) or len(text) < 20,
        }

        # Phase 6 synthesis + product actions
        archetype = "A"
        for arch, keys in _ARCHETYPE_HINTS:
            if any(k in lower for k in keys):
                archetype = arch
                break
        emotional = _emotion_target(lower, purpose)
        synthesis = {
            "primary_intent": purpose,
            "recommended_archetype": archetype,
            "recommended_scale": _scale_hint(lower),
            "emotional_target": emotional,
            "shot_intent_text": surface["literal_summary"][:400],
            "actions": [
                "Materialize UserBriefV1 with extracted constraints",
                f"Prefer archetype {archetype} DNA if available",
                "Run offline knowledge.route + research.query for research steps",
                "Attach aesthetics emotional_target when scoring frames",
            ],
            "brief_enrichment": {
                "purpose": purpose,
                "archetype_hint": archetype,
                "constraints": surface["constraints_found"],
                "emotional_target": emotional,
            },
        }

        payload = {
            "ok": True,
            "run_id": run_id,
            "phases": {
                "context": context,
                "purpose": {"label": purpose, "scores": purpose_scores},
                "surface": surface,
                "pragmatic": pragmatic,
                "hidden_agenda": hidden,
                "judgment": judgment,
                "synthesis": synthesis,
            },
            "primary_intent": purpose,
            "recommended_archetype": archetype,
            "emotional_target": emotional,
            "escalate_to_hitl": judgment["escalate_to_hitl"],
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


def _extract_constraints(lower: str) -> list[str]:
    found: list[str] = []
    for pat, label in (
        (r"\b(\d+)\s*s(ec(ond)?s?)?\b", "duration"),
        (r"\b(9:16|16:9|1:1|2\.39:1)\b", "aspect_ratio"),
        (r"\b(hdr|sdr|4k|1080p|720p)\b", "deliverable"),
        (r"\b(zh-hant|zh-hans|english|cantonese|mandarin)\b", "locale_lang"),
        (r"\b(no music|no logos|brand safe)\b", "content_constraint"),
    ):
        if re.search(pat, lower):
            found.append(label)
    return found


def _grice_risks(lower: str) -> list[str]:
    risks: list[str] = []
    if len(lower) < 40:
        risks.append("quantity_too_little")
    if lower.count("maybe") + lower.count(" somehow") > 2:
        risks.append("manner_vague")
    if "ignore" in lower and "brief" in lower:
        risks.append("relation_risk")
    return risks


def _implicatures(lower: str, purpose: str) -> list[str]:
    out = [f"Stated purpose class: {purpose}"]
    if "viral" in lower or "algorithm" in lower:
        out.append("Implicature: platform growth / engagement optimization")
    if "brand" in lower or "client" in lower:
        out.append("Implicature: external stakeholder approval required")
    if "cheap" in lower or "budget" in lower or "fast" in lower:
        out.append("Implicature: cost/time constraints dominate quality")
    return out


def _emotion_target(lower: str, purpose: str) -> dict[str, float]:
    valence = 0.1
    arousal = 0.4
    if any(k in lower for k in ("noir", "horror", "tragic", "sad", "dark")):
        valence = -0.4
        arousal = 0.55
    if any(k in lower for k in ("comedy", "fun", "upbeat", "happy")):
        valence = 0.5
        arousal = 0.6
    if purpose == "promote":
        arousal = max(arousal, 0.65)
        valence = max(valence, 0.2)
    return {"valence": valence, "arousal": arousal}


def _scale_hint(lower: str) -> str:
    if any(k in lower for k in ("feature", "series", "season")):
        return "S5"
    if any(k in lower for k in ("campaign", "multi", "pack")):
        return "S3"
    if any(k in lower for k in ("15s", "30s", "short", "reel", "tiktok")):
        return "S1"
    return "S2"


_SERVICE: IntentService | None = None
_LOCK = threading.Lock()


def get_intent_service() -> IntentService:
    global _SERVICE
    with _LOCK:
        if _SERVICE is None:
            _SERVICE = IntentService()
        return _SERVICE


def reset_intent_service_for_tests() -> IntentService:
    global _SERVICE
    with _LOCK:
        _SERVICE = IntentService()
        return _SERVICE
