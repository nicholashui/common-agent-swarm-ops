"""Offline Optimization Agent foundation (prompt/cost/retention lite)."""

from __future__ import annotations

import re
import threading
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

_TOKEN = re.compile(r"[a-z0-9]+", re.I)

ACTIVATION_POLICY: dict[str, Any] = {
    "production_optimizer": False,
    "live_roas": False,
    "live_training": False,
    "mode": "offline_deterministic_stub",
    "note": (
        "Offline optimization recommendations for Host loops/prompts. "
        "Not live ROAS training or continuous online bandits."
    ),
}

OptKind = Literal["prompt", "cost", "retention", "eval", "auto"]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class OptimizeRequest(StrictModel):
    goal: str = Field(min_length=1, max_length=4_000)
    kind: OptKind = "auto"
    current_metrics: dict[str, float] = Field(default_factory=dict)
    allow_live_training: bool = False


class OptimizationService:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._runs: list[dict[str, Any]] = []

    @property
    def activation_policy(self) -> dict[str, Any]:
        return dict(ACTIVATION_POLICY)

    def policy(self) -> dict[str, Any]:
        return {
            "activation_policy": self.activation_policy,
            "kinds": ["prompt", "cost", "retention", "eval", "auto"],
            "agent_id": "specials.optimization-agent",
            "note": ACTIVATION_POLICY["note"],
        }

    def optimize(self, request: OptimizeRequest) -> dict[str, Any]:
        if request.allow_live_training:
            return {
                "ok": False,
                "error": (
                    "Live training / ROAS optimizers are not enabled. "
                    "Fail-closed offline recommendations only."
                ),
                "activation_policy": self.activation_policy,
            }

        goal = request.goal.strip()
        lower = goal.lower()
        kind = request.kind
        if kind == "auto":
            kind = _infer_kind(lower)

        suggestions = _suggestions(kind, lower, request.current_metrics)
        score = _priority_score(kind, request.current_metrics)

        payload = {
            "ok": True,
            "run_id": f"opt_{uuid4().hex[:12]}",
            "kind": kind,
            "goal": goal[:500],
            "suggestions": suggestions,
            "priority_score": score,
            "apply_order": [s["id"] for s in suggestions],
            "activation_policy": self.activation_policy,
            "note": ACTIVATION_POLICY["note"],
            "linked_agents": _linked_agents(kind),
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


def _infer_kind(lower: str) -> str:
    if any(k in lower for k in ("prompt", "steer", "wording", "rewrite")):
        return "prompt"
    if any(k in lower for k in ("cost", "budget", "token", "latency", "cheap")):
        return "cost"
    if any(k in lower for k in ("retention", "watch", "hook", "drop-off", "ctr")):
        return "retention"
    if any(k in lower for k in ("eval", "rubric", "golden", "metric", "score")):
        return "eval"
    return "prompt"


def _linked_agents(kind: str) -> list[str]:
    return {
        "prompt": ["video.promptoptimizer", "video.promptengineer"],
        "cost": ["video.costoptimizer", "video.producer"],
        "retention": ["video.retentionoptimizer", "video.editor"],
        "eval": ["video.evaluationharness", "video.judge"],
    }.get(kind, ["video.promptoptimizer"])


def _priority_score(kind: str, metrics: dict[str, float]) -> float:
    base = 0.55
    if kind == "cost" and float(metrics.get("token_spend", 0) or 0) > 1000:
        base = 0.8
    if kind == "retention" and float(metrics.get("hook_rate", 1) or 1) < 0.3:
        base = 0.85
    if kind == "eval" and float(metrics.get("l2_pass_rate", 1) or 1) < 0.7:
        base = 0.75
    return round(base, 4)


def _suggestions(kind: str, lower: str, metrics: dict[str, float]) -> list[dict[str, Any]]:
    if kind == "cost":
        return [
            {
                "id": "cost_fast_path",
                "title": "Prefer Cynefin simple/fast path when goal is routine",
                "action": "thinking.recommend + enable_fast_path on agent loops",
                "impact": "lower",
            },
            {
                "id": "cost_stub_tools",
                "title": "Keep Act on stub tools until package gate",
                "action": "Do not set CASOPS_MEDIA_LIVE for exploratory loops",
                "impact": "high",
            },
            {
                "id": "cost_top_k",
                "title": "Reduce RAG top_k for screen mode",
                "action": "POST /rag/query with top_k=4 for screening",
                "impact": "medium",
            },
        ]
    if kind == "retention":
        return [
            {
                "id": "ret_hook_first_3s",
                "title": "Front-load visual hook in first 3s",
                "action": "Brief: explicit hook beat + aesthetics screen mode on thumbnails",
                "impact": "high",
            },
            {
                "id": "ret_pacing",
                "title": "Add mid-cut novelty every 8–12s",
                "action": "Planner todo + aesthetics novelty dimension check",
                "impact": "medium",
            },
            {
                "id": "ret_cta",
                "title": "Clarify CTA only after value moment",
                "action": "Screenwriter beat sheet: value → CTA",
                "impact": "medium",
            },
        ]
    if kind == "eval":
        return [
            {
                "id": "eval_golden_skills",
                "title": "Run offline skill golden harness",
                "action": "POST /api/v1/skill-evals/run",
                "impact": "high",
            },
            {
                "id": "eval_l2_fail_closed",
                "title": "Keep loop_passed fail-closed on L2",
                "action": "Do not treat status=ok as pass when L2 fail",
                "impact": "high",
            },
            {
                "id": "eval_citations",
                "title": "Require citations on research/RAG steps",
                "action": "Research escalate_to_hitl when no citations",
                "impact": "medium",
            },
        ]
    # prompt default
    out = [
        {
            "id": "prompt_intent",
            "title": "Run intent analysis before prompt expansion",
            "action": "POST /api/v1/intent/analyze → use shot_intent_text",
            "impact": "high",
        },
        {
            "id": "prompt_aesthetics_steer",
            "title": "Use aesthetics prompt_steer_hints after score",
            "action": "POST /aesthetics/evaluate mode=refine",
            "impact": "medium",
        },
        {
            "id": "prompt_constraints",
            "title": "Encode aspect ratio / duration as hard constraints",
            "action": "UserBrief constraints + aesthetics constraints fields",
            "impact": "medium",
        },
    ]
    if "generic" in lower or "slop" in lower:
        out.insert(
            0,
            {
                "id": "prompt_anti_slop",
                "title": "Add novelty + style_fidelity anti-slop language",
                "action": "Aesthetics novelty/style_fidelity steers in prompt",
                "impact": "high",
            },
        )
    return out


_SERVICE: OptimizationService | None = None
_LOCK = threading.Lock()


def get_optimization_service() -> OptimizationService:
    global _SERVICE
    with _LOCK:
        if _SERVICE is None:
            _SERVICE = OptimizationService()
        return _SERVICE


def reset_optimization_service_for_tests() -> OptimizationService:
    global _SERVICE
    with _LOCK:
        _SERVICE = OptimizationService()
        return _SERVICE
