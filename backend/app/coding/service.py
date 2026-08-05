"""Offline Coding Agent Host foundation.

Plan engineering work fail-closed: no remote installers, no arbitrary shell,
no network package installs. Returns structured task plans only.
"""

from __future__ import annotations

import re
import threading
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

_TOKEN = re.compile(r"[a-z0-9_./-]+", re.I)

ACTIVATION_POLICY: dict[str, Any] = {
    "production_autonomous_coding": False,
    "network": False,
    "remote_installers": False,
    "arbitrary_shell": False,
    "mode": "offline_plan_only",
    "note": (
        "Offline coding-agent plan surface. Does not execute shell, install "
        "packages, or write outside reviewed Host workflows."
    ),
}


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class CodingPlanRequest(StrictModel):
    goal: str = Field(min_length=1, max_length=8_000)
    area: str = Field(default="host", max_length=64)
    allow_network: bool = False
    allow_shell_exec: bool = False


class CodingService:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._runs: list[dict[str, Any]] = []

    @property
    def activation_policy(self) -> dict[str, Any]:
        return dict(ACTIVATION_POLICY)

    def policy(self) -> dict[str, Any]:
        return {
            "activation_policy": self.activation_policy,
            "agent_id": "specials coding host-infra skill",
            "allowed": ["plan", "list_touch_points", "tests_to_run"],
            "denied": ["shell_exec", "pip_install", "curl_installer", "force_push"],
            "note": ACTIVATION_POLICY["note"],
        }

    def plan(self, request: CodingPlanRequest) -> dict[str, Any]:
        if request.allow_network or request.allow_shell_exec:
            return {
                "ok": False,
                "error": (
                    "Network/shell execution is not enabled on coding Host foundation. "
                    "Plan-only fail-closed."
                ),
                "activation_policy": self.activation_policy,
            }

        goal = request.goal.strip()
        lower = goal.lower()
        touch = _touch_points(lower, request.area)
        steps = _steps(lower, touch)
        tests = _tests(lower, touch)
        risks = [
            "Do not run remote installers without human approval",
            "Keep changes surgical within project root",
            "Record evidence commands for Host skill changes",
        ]
        if any(k in lower for k in ("rm -rf", "force push", "drop table")):
            risks.insert(0, "Destructive operation mentioned — require human approval")

        payload = {
            "ok": True,
            "run_id": f"code_{uuid4().hex[:12]}",
            "goal": goal[:500],
            "area": request.area,
            "plan_steps": steps,
            "touch_points": touch,
            "suggested_tests": tests,
            "acceptance_criteria": [
                "Focused unit tests pass offline",
                "No production_media / network activation flags flipped silently",
                "Skill SKILL.md / plan doc updated if Host surface added",
            ],
            "risks": risks,
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


def _touch_points(lower: str, area: str) -> list[dict[str, str]]:
    points: list[dict[str, str]] = []
    mapping = [
        (("aesthetics", "aesthetic"), "backend/app/aesthetics/", "Aesthetics Host module"),
        (("rag", "retrieval"), "backend/app/rag/", "Agentic RAG Host module"),
        (("agent loop", "loop_v3"), "backend/app/video/loop_v3/", "Agent loop v3 cognitive"),
        (("intent",), "backend/app/intent/", "Intent DIA lite"),
        (("api", "router"), "backend/app/api/v1/", "Public API routers"),
        (("frontend", "ui", "tsx"), "frontend/src/", "Frontend product clients"),
        (("test", "pytest"), "backend/tests/unit/", "Unit tests"),
        (("skill",), "business/video/special_skills/", "Skill packaging"),
    ]
    for keys, path, note in mapping:
        if any(k in lower for k in keys):
            points.append({"path": path, "why": note})
    if not points:
        if area == "frontend":
            points.append({"path": "frontend/src/", "why": "Default frontend area"})
        else:
            points.append({"path": "backend/app/", "why": "Default Host backend area"})
            points.append({"path": "backend/tests/unit/", "why": "Add/adjust tests"})
    return points[:8]


def _steps(lower: str, touch: list[dict[str, str]]) -> list[dict[str, Any]]:
    steps = [
        {
            "step": 1,
            "action": "Clarify acceptance criteria and fail-closed boundaries",
            "phase": "spec",
        },
        {
            "step": 2,
            "action": "Locate touch points",
            "phase": "explore",
            "paths": [t["path"] for t in touch],
        },
        {
            "step": 3,
            "action": "Implement surgical change in project root only",
            "phase": "implement",
        },
        {
            "step": 4,
            "action": "Add deterministic offline unit tests",
            "phase": "test",
        },
        {
            "step": 5,
            "action": "Update skill/plan docs if Host surface changed",
            "phase": "docs",
        },
    ]
    if "refactor" in lower:
        steps.insert(
            2,
            {
                "step": 2,
                "action": "Preserve behavior with characterization tests before edit",
                "phase": "safety",
            },
        )
    # renumber
    for i, s in enumerate(steps, start=1):
        s["step"] = i
    return steps


def _tests(lower: str, touch: list[dict[str, str]]) -> list[str]:
    tests = ["python -m pytest backend/tests/unit/api -q --tb=short"]
    if any("frontend" in t["path"] for t in touch) or "frontend" in lower:
        tests.append("node --import tsx --test frontend/src/lib/api/*.test.ts")
    if "aesthetics" in lower:
        tests.append("python -m pytest backend/tests/unit/api/test_aesthetics.py -q")
    if "rag" in lower:
        tests.append("python -m pytest backend/tests/unit/api/test_rag.py -q")
    return tests


_SERVICE: CodingService | None = None
_LOCK = threading.Lock()


def get_coding_service() -> CodingService:
    global _SERVICE
    with _LOCK:
        if _SERVICE is None:
            _SERVICE = CodingService()
        return _SERVICE


def reset_coding_service_for_tests() -> CodingService:
    global _SERVICE
    with _LOCK:
        _SERVICE = CodingService()
        return _SERVICE
