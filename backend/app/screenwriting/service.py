"""Offline screenwriting strategic goal foundation.

Beat sheet + narrative arc from goal. Not full screenplay generation LLM.
"""

from __future__ import annotations

import re
import threading
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

ACTIVATION_POLICY: dict[str, Any] = {
    "production_screenplay_llm": False,
    "live_generation": False,
    "mode": "offline_deterministic_stub",
    "note": (
        "Offline screenwriting beat sheet + arc plan. "
        "Not full multi-act LLM screenplay generation."
    ),
}


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ScreenplayPlanRequest(StrictModel):
    logline_or_goal: str = Field(min_length=1, max_length=8_000)
    form: str = Field(default="short", max_length=32)
    genre: str = Field(default="", max_length=80)


class ScreenwritingService:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._runs: list[dict[str, Any]] = []

    @property
    def activation_policy(self) -> dict[str, Any]:
        return dict(ACTIVATION_POLICY)

    def policy(self) -> dict[str, Any]:
        return {
            "activation_policy": self.activation_policy,
            "forms": ["short", "feature", "episode", "ad"],
            "agent_id": "specials.screenwriter-strategic-goal-achievement-agent",
            "linked_agents": [
                "video.screenwriter",
                "video.narrativearc",
                "video.showrunner",
                "video.director",
            ],
            "note": ACTIVATION_POLICY["note"],
        }

    def plan(self, request: ScreenplayPlanRequest) -> dict[str, Any]:
        goal = request.logline_or_goal.strip()
        form = (request.form or "short").strip().lower()
        genre = (request.genre or "").strip() or _guess_genre(goal)
        beats = _beats(form, goal, genre)
        theme = _theme(goal)
        payload = {
            "ok": True,
            "run_id": f"scr_{uuid4().hex[:12]}",
            "goal": goal[:500],
            "form": form,
            "genre": genre,
            "controlling_idea": theme,
            "protagonist_want": _want(goal),
            "protagonist_need": "truth / connection / courage (offline default)",
            "beats": beats,
            "sequence_goals": [
                {"seq": b["beat_id"], "dramatic_question": b["question"]} for b in beats
            ],
            "strategic_milestones": [
                "Lock logline + controlling idea",
                "Approve beat sheet (HITL for feature)",
                "Scene cards offline",
                "Dialogue pass after structure lock",
            ],
            "next_actions": [
                "POST /strategic/plan for production milestones",
                "POST /creative/ideate for visual set pieces",
                "POST /psychology/profile for audience arc",
                "Agent-loop video.screenwriter offline",
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


def _guess_genre(text: str) -> str:
    t = text.lower()
    for g, keys in (
        ("thriller", ("thriller", "chase", "spy")),
        ("romance", ("love", "romance")),
        ("comedy", ("comedy", "funny")),
        ("drama", ("drama", "family", "grief")),
        ("noir", ("noir", "crime")),
        ("wuxia", ("wuxia", "martial")),
    ):
        if any(k in t for k in keys):
            return g
    return "drama"


def _theme(goal: str) -> str:
    g = goal.lower()
    if "redemption" in g:
        return "Redemption is earned through honest action, not words"
    if "love" in g:
        return "Love requires vulnerability under pressure"
    return f"Truth about change emerges through conflict around: {goal[:80]}"


def _want(goal: str) -> str:
    m = re.search(r"\b(wants?|seeks?|must)\s+([^.;]+)", goal, re.I)
    if m:
        return m.group(0)[:120]
    return "Achieve the stated goal against resistance"


def _beats(form: str, goal: str, genre: str) -> list[dict[str, Any]]:
    if form == "ad":
        raw = [
            ("hook", "Interrupt scroll / open loop"),
            ("problem", "Audience pain visible"),
            ("turn", "Product as bridge"),
            ("proof", "Demo / social proof"),
            ("cta", "Single clear ask"),
        ]
    elif form == "feature":
        raw = [
            ("opening_image", "World before change"),
            ("catalyst", "Inciting incident"),
            ("debate", "Hesitation"),
            ("break_into_2", "Commit to journey"),
            ("midpoint", "False victory/defeat"),
            ("all_is_lost", "Low point"),
            ("break_into_3", "Final plan"),
            ("finale", "Climax + new world"),
        ]
    else:
        raw = [
            ("cold_open", "In media res tension"),
            ("setup", "Want + obstacle"),
            ("turn", "First major cost"),
            ("mid", "Reversal"),
            ("climax", "Decisive action"),
            ("button", "Image that lands theme"),
        ]
    out = []
    for i, (bid, q) in enumerate(raw):
        out.append(
            {
                "beat_id": bid,
                "order": i + 1,
                "question": q,
                "genre_note": f"{genre}: keep intent fidelity to {goal[:60]}",
            }
        )
    return out


_SERVICE: ScreenwritingService | None = None
_LOCK = threading.Lock()


def get_screenwriting_service() -> ScreenwritingService:
    global _SERVICE
    with _LOCK:
        if _SERVICE is None:
            _SERVICE = ScreenwritingService()
        return _SERVICE


def reset_screenwriting_service_for_tests() -> ScreenwritingService:
    global _SERVICE
    with _LOCK:
        _SERVICE = ScreenwritingService()
        return _SERVICE
