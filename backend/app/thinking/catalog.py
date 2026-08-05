"""Ranked thinking-model catalog (thinking_model.md lite for Host loops)."""

from __future__ import annotations

from typing import Any

# High-priority models only (scores ~8–10 from study ranking)
THINKING_MODELS: list[dict[str, Any]] = [
    {
        "id": "cynefin",
        "name": "Cynefin Framework",
        "rank": 1,
        "score": 10.0,
        "phases": ["phase0", "phase1"],
        "use_when": "Need adaptive Fast vs Full loop intensity by context type",
    },
    {
        "id": "premortem",
        "name": "Premortem Analysis",
        "rank": 2,
        "score": 10.0,
        "phases": ["phase0"],
        "use_when": "Proactive risk before committing plan",
    },
    {
        "id": "aar",
        "name": "After-Action Review",
        "rank": 3,
        "score": 9.5,
        "phases": ["phase4"],
        "use_when": "Structured reflection at termination/milestone",
    },
    {
        "id": "double_loop",
        "name": "Double-Loop Learning",
        "rank": 4,
        "score": 9.5,
        "phases": ["phase4"],
        "use_when": "Question governing variables after tactical fixes",
    },
    {
        "id": "rpd",
        "name": "Recognition-Primed Decision",
        "rank": 5,
        "score": 9.5,
        "phases": ["phase1"],
        "use_when": "Fast path from similar successful patterns",
    },
    {
        "id": "dual_process",
        "name": "Dual Process (System 1/2)",
        "rank": 8,
        "score": 9.0,
        "phases": ["phase1"],
        "use_when": "Switch fast recognition vs slow deliberative ReAct",
    },
    {
        "id": "metacognition",
        "name": "Metacognition Cycle",
        "rank": 7,
        "score": 9.0,
        "phases": ["phase1"],
        "use_when": "Monitor bias, mode fit, progress mid-loop",
    },
    {
        "id": "five_whys",
        "name": "5 Whys / Fishbone",
        "rank": 6,
        "score": 9.0,
        "phases": ["phase4"],
        "use_when": "Root-cause on persistent failures",
    },
    {
        "id": "red_team",
        "name": "Red Team Thinking",
        "rank": 12,
        "score": 8.0,
        "phases": ["phase0", "phase3"],
        "use_when": "Adversarial critique of plan/output",
    },
    {
        "id": "paul_elder",
        "name": "Paul-Elder Critical Thinking",
        "rank": 9,
        "score": 8.5,
        "phases": ["phase1", "phase3"],
        "use_when": "Rigor checklist on thought and verification",
    },
]


def list_models() -> list[dict[str, Any]]:
    return list(THINKING_MODELS)
