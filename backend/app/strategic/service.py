"""Offline Strategic Goal Achievement foundation.

Goal → milestones → checks → next actions. Not full OKR OS.
"""

from __future__ import annotations

import re
import threading
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

_TOKEN = re.compile(r"[a-z0-9]+", re.I)

ACTIVATION_POLICY: dict[str, Any] = {
    "production_strategy_os": False,
    "live_okr_sync": False,
    "mode": "offline_deterministic_stub",
    "note": (
        "Offline strategic goal scaffolding for video/spine goals. "
        "Not a full multi-quarter OKR control plane."
    ),
}


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class StrategicPlanRequest(StrictModel):
    goal: str = Field(min_length=1, max_length=4_000)
    horizon: str = Field(default="project", max_length=64)
    domain: str = Field(default="video", max_length=64)


class StrategicService:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._runs: list[dict[str, Any]] = []

    @property
    def activation_policy(self) -> dict[str, Any]:
        return dict(ACTIVATION_POLICY)

    def policy(self) -> dict[str, Any]:
        return {
            "activation_policy": self.activation_policy,
            "horizons": ["shot", "project", "campaign"],
            "agent_id": "specials.strategic-goal-achievement-agent",
            "linked_agents": [
                "video.planner",
                "video.producer",
                "video.orchestrator",
                "specials.screenwriter-strategic-goal-achievement-agent",
            ],
            "note": ACTIVATION_POLICY["note"],
        }

    def plan(self, request: StrategicPlanRequest) -> dict[str, Any]:
        goal = request.goal.strip()
        horizon = request.horizon.strip() or "project"
        milestones = _milestones(goal, horizon)
        risks = _risks(goal)
        krs = [
            {
                "kr_id": f"kr_{i+1}",
                "statement": m["outcome"],
                "metric": m["metric"],
                "target": m["target"],
            }
            for i, m in enumerate(milestones)
        ]
        payload = {
            "ok": True,
            "run_id": f"strat_{uuid4().hex[:12]}",
            "goal": goal[:500],
            "horizon": horizon,
            "domain": request.domain,
            "objective": f"Achieve: {goal[:200]}",
            "key_results": krs,
            "milestones": milestones,
            "risks": risks,
            "next_actions": [
                "Run intent.analyze on goal text",
                "Decompose via complex-problem.solve if multi-hop",
                "Execute spine offline loops with package HITL",
                "Record accept/reject in aesthetics memory when scoring media stubs",
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


def _milestones(goal: str, horizon: str) -> list[dict[str, Any]]:
    g = goal.lower()
    if horizon == "shot":
        return [
            {
                "id": "m1",
                "title": "Lock shot intent",
                "outcome": "Shot intent + emotion target documented",
                "metric": "intent_fields_present",
                "target": 1,
                "owner": "video.director",
            },
            {
                "id": "m2",
                "title": "Score aesthetics offline",
                "outcome": "AestheticVerdict with vector",
                "metric": "aesthetic_vector_dims",
                "target": 10,
                "owner": "specials.aesthetics-agent",
            },
        ]
    base = [
        {
            "id": "m1",
            "title": "Brief + intent",
            "outcome": "UserBriefV1 with intent_analysis",
            "metric": "brief_minted",
            "target": 1,
            "owner": "video.planner",
        },
        {
            "id": "m2",
            "title": "Spine dry-run",
            "outcome": "wf_video_spine_v1 offline handoffs",
            "metric": "spine_steps_completed",
            "target": 8,
            "owner": "video.orchestrator",
        },
        {
            "id": "m3",
            "title": "QC gates",
            "outcome": "L2 + package HITL ready",
            "metric": "package_hitl_required",
            "target": 1,
            "owner": "video.gatekeeper",
        },
    ]
    if any(k in g for k in ("series", "campaign", "multi")):
        base.append(
            {
                "id": "m4",
                "title": "Campaign coherence",
                "outcome": "Shared aesthetic profile + memory ratchet",
                "metric": "profile_version",
                "target": 1,
                "owner": "video.brandstrategist",
            }
        )
    return base


def _risks(goal: str) -> list[dict[str, str]]:
    risks = [
        {
            "risk": "Scope creep beyond offline Host",
            "mitigation": "Keep production_media false until go-live",
        },
        {
            "risk": "Success criteria vague",
            "mitigation": "Intent + strategic KRs before loops",
        },
    ]
    if any(k in goal.lower() for k in ("live", "sora", "realtime")):
        risks.append(
            {
                "risk": "Assumes live media tools",
                "mitigation": "Agent-loop Act remains stub/live_blocked",
            }
        )
    return risks


_SERVICE: StrategicService | None = None
_LOCK = threading.Lock()


def get_strategic_service() -> StrategicService:
    global _SERVICE
    with _LOCK:
        if _SERVICE is None:
            _SERVICE = StrategicService()
        return _SERVICE


def reset_strategic_service_for_tests() -> StrategicService:
    global _SERVICE
    with _LOCK:
        _SERVICE = StrategicService()
        return _SERVICE
