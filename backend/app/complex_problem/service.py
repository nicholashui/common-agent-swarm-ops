"""Offline Complex Problem Solution Process Model foundation.

Decompose → options → gates → plan. Not full autonomous CPS solver.
"""

from __future__ import annotations

import re
import threading
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

_TOKEN = re.compile(r"[a-z0-9]+", re.I)

ACTIVATION_POLICY: dict[str, Any] = {
    "production_cps": False,
    "live_solver": False,
    "mode": "offline_deterministic_stub",
    "note": (
        "Offline complex-problem process scaffold for planner/orchestrator. "
        "Not a full automated CPS/MCTS solver."
    ),
}


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ComplexProblemRequest(StrictModel):
    problem: str = Field(min_length=1, max_length=8_000)
    context: str = Field(default="", max_length=4_000)
    max_steps: int = Field(default=6, ge=3, le=16)


class ComplexProblemService:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._runs: list[dict[str, Any]] = []

    @property
    def activation_policy(self) -> dict[str, Any]:
        return dict(ACTIVATION_POLICY)

    def policy(self) -> dict[str, Any]:
        return {
            "activation_policy": self.activation_policy,
            "stages": [
                "frame",
                "decompose",
                "options",
                "gates",
                "plan",
                "verify",
            ],
            "agent_id": "specials.complex-problem-solution-process-model",
            "linked_agents": [
                "video.planner",
                "video.orchestrator",
                "video.judge",
                "video.gatekeeper",
            ],
            "note": ACTIVATION_POLICY["note"],
        }

    def solve(self, request: ComplexProblemRequest) -> dict[str, Any]:
        problem = request.problem.strip()
        ctx = (request.context or "").strip()
        tokens = list(dict.fromkeys(_TOKEN.findall(problem.lower())))[:20]

        frame = {
            "problem_statement": problem[:500],
            "context": ctx[:300],
            "success_criteria": [
                "Clear sub-problems with owners",
                "Gates defined before irreversible steps",
                "HITL on package / production media",
            ],
            "constraints": _constraints(problem),
        }

        subproblems = _decompose(problem, tokens, request.max_steps)
        options = [
            {
                "option_id": "A_sequential",
                "label": "Sequential spine with stop_on_failure",
                "pros": ["simpler coordination", "clear audit trail"],
                "cons": ["slower wall-clock"],
            },
            {
                "option_id": "B_parallel_research",
                "label": "Parallel research branches then join",
                "pros": ["faster discovery"],
                "cons": ["merge conflicts need judge"],
            },
            {
                "option_id": "C_fast_path",
                "label": "Cynefin simple + RPD fast path when pattern matches",
                "pros": ["token efficient"],
                "cons": ["risk under-deliberation on novel goals"],
            },
        ]
        recommended = "B_parallel_research" if "research" in problem.lower() else "A_sequential"

        gates = [
            {
                "gate_id": "g_intent",
                "when": "before plan commit",
                "check": "intent.analyze primary_intent present",
            },
            {
                "gate_id": "g_l2",
                "when": "after each agent loop",
                "check": "L2 pass or HITL",
            },
            {
                "gate_id": "g_package",
                "when": "package step",
                "check": "human package approval never auto",
            },
        ]

        plan = [
            {
                "step": i + 1,
                "subproblem_id": sp["id"],
                "action": sp["action"],
                "owner": sp["owner"],
                "gate_after": "g_l2",
            }
            for i, sp in enumerate(subproblems)
        ]

        payload = {
            "ok": True,
            "run_id": f"cps_{uuid4().hex[:12]}",
            "frame": frame,
            "subproblems": subproblems,
            "options": options,
            "recommended_option": recommended,
            "gates": gates,
            "plan": plan,
            "verify_checklist": [
                "Every subproblem has owner agent",
                "Irreversible steps gated",
                "Fail-closed production_media",
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


def _constraints(problem: str) -> list[str]:
    p = problem.lower()
    out = ["offline Host defaults"]
    if any(k in p for k in ("budget", "cheap", "cost")):
        out.append("cost-sensitive")
    if any(k in p for k in ("live", "sora", "veo", "production")):
        out.append("production_media requires go-live review")
    return out


def _decompose(problem: str, tokens: list[str], max_steps: int) -> list[dict[str, Any]]:
    base = [
        ("sp_frame", "Frame goal + success criteria", "video.planner", "intent.analyze"),
        ("sp_research", "Gather evidence / references", "video.webresearch", "research.query"),
        ("sp_ideate", "Generate creative options", "video.ideation", "creative.ideate"),
        ("sp_plan", "Build executable plan / spine", "video.planner", "agent_loop.run"),
        ("sp_make", "Produce artifacts offline stubs", "video.director", "pack_loop"),
        ("sp_qc", "QC + aesthetics + package gate", "video.gatekeeper", "aesthetics.evaluate"),
    ]
    # Filter research if not relevant
    if "research" not in problem.lower() and "reference" not in problem.lower():
        base = [b for b in base if b[0] != "sp_research"]
    out = []
    for i, (sid, action, owner, tool) in enumerate(base[:max_steps]):
        out.append(
            {
                "id": sid,
                "action": action,
                "owner": owner,
                "suggested_tool": tool,
                "keywords": tokens[:5],
            }
        )
    return out


_SERVICE: ComplexProblemService | None = None
_LOCK = threading.Lock()


def get_complex_problem_service() -> ComplexProblemService:
    global _SERVICE
    with _LOCK:
        if _SERVICE is None:
            _SERVICE = ComplexProblemService()
        return _SERVICE


def reset_complex_problem_service_for_tests() -> ComplexProblemService:
    global _SERVICE
    with _LOCK:
        _SERVICE = ComplexProblemService()
        return _SERVICE
