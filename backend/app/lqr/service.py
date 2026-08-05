"""Offline Life's Quiet Redemption (LQR) workflow scaffold.

Archetype E short-film overview — not full 14-shot MCTS loop.
"""

from __future__ import annotations

import threading
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

ACTIVATION_POLICY: dict[str, Any] = {
    "full_mcts_shot_loop": False,
    "production_media": False,
    "mode": "offline_overview_scaffold",
    "note": (
        "Offline LQR overview scaffold (archetype E). "
        "Not the full multi-shot MCTS production loop."
    ),
}

_LQR_PHASES: list[dict[str, str]] = [
    {
        "id": "premise",
        "title": "Quiet premise lock",
        "owner": "video.director",
        "action": "Lock redemption-without-spectacle controlling idea",
    },
    {
        "id": "treatment",
        "title": "Treatment + emotional arc",
        "owner": "video.screenwriter",
        "action": "Beat sheet via screenwriting.plan form=short",
    },
    {
        "id": "visual",
        "title": "Visual bible lite",
        "owner": "video.promptengineer",
        "action": "Creative.ideate + aesthetics profile weights",
    },
    {
        "id": "consistency",
        "title": "Consistency gates",
        "owner": "video.aiqaconsistency",
        "action": "AIQA offline checks + aesthetics temporal notes",
    },
    {
        "id": "assembly",
        "title": "Assembly + restraint edit",
        "owner": "video.editor",
        "action": "Prefer silence and held frames over spectacle",
    },
    {
        "id": "package",
        "title": "Package HITL",
        "owner": "video.gatekeeper",
        "action": "Human package gate; production_ready remains false",
    },
]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class LqrOverviewRequest(StrictModel):
    logline: str = Field(
        default="A quiet life earns redemption through small honest acts",
        max_length=4_000,
    )
    variant: str = Field(default="overview", max_length=64)


class LqrService:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._runs: list[dict[str, Any]] = []

    @property
    def activation_policy(self) -> dict[str, Any]:
        return dict(ACTIVATION_POLICY)

    def policy(self) -> dict[str, Any]:
        return {
            "activation_policy": self.activation_policy,
            "archetype": "E",
            "dna": ["wf_video_lqr_overview_v1", "wf_video_arch_e_ai_short_film_v1"],
            "phase_count": len(_LQR_PHASES),
            "note": ACTIVATION_POLICY["note"],
        }

    def overview(self, request: LqrOverviewRequest) -> dict[str, Any]:
        logline = (request.logline or "").strip() or _LQR_PHASES[0]["action"]
        phases = [
            {
                **p,
                "status": "planned",
                "offline_tools": _tools_for(p["id"]),
            }
            for p in _LQR_PHASES
        ]
        payload = {
            "ok": True,
            "run_id": f"lqr_{uuid4().hex[:12]}",
            "logline": logline[:500],
            "archetype": "E",
            "variant": request.variant,
            "phases": phases,
            "principles": [
                "Quiet over spectacle",
                "Redemption through action",
                "Consistency over novelty spam",
                "Fail-closed media until package HITL",
            ],
            "next_actions": [
                "screenwriting.plan with LQR logline",
                "psychology.profile for intimate drama cohort",
                "agent-loops crew: director, screenwriter, promptengineer",
                "Do not claim full 14-shot MCTS complete",
            ],
            "activation_policy": self.activation_policy,
            "note": ACTIVATION_POLICY["note"],
        }
        with self._lock:
            self._runs.append(payload)
            if len(self._runs) > 200:
                self._runs = self._runs[-150:]
        return payload

    def recent(self, *, limit: int = 20) -> list[dict[str, Any]]:
        limit = max(1, min(limit, 100))
        with self._lock:
            return list(self._runs[-limit:])


def _tools_for(phase_id: str) -> list[str]:
    return {
        "premise": ["intent.analyze", "strategic.plan"],
        "treatment": ["screenwriting.plan", "creative.ideate"],
        "visual": ["aesthetics.evaluate", "creative.ideate"],
        "consistency": ["aesthetics.evaluate"],
        "assembly": ["optimization.recommend"],
        "package": ["skill_evals.run"],
    }.get(phase_id, [])


_SERVICE: LqrService | None = None
_LOCK = threading.Lock()


def get_lqr_service() -> LqrService:
    global _SERVICE
    with _LOCK:
        if _SERVICE is None:
            _SERVICE = LqrService()
        return _SERVICE


def reset_lqr_service_for_tests() -> LqrService:
    global _SERVICE
    with _LOCK:
        _SERVICE = LqrService()
        return _SERVICE
