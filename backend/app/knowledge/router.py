"""Offline hybrid-lite knowledge routing (metadata keywords → destination)."""

from __future__ import annotations

import re
from typing import Any

from app.knowledge.models import ACTIVATION_POLICY, Destination

_TOKEN = re.compile(r"[a-z0-9]+", re.I)

# Destination keyword packs (training-free bootstrap)
_RULES: list[tuple[Destination, tuple[str, ...], list[str], float]] = [
    (
        "aesthetics",
        ("aesthetic", "composition", "color grade", "lookbook", "visual quality", "taste"),
        ["specials.aesthetics-agent", "video.colorist", "video.cinematographer"],
        0.85,
    ),
    (
        "rag",
        (
            "retrieve",
            "citation",
            "evidence",
            "corpus",
            "document",
            "knowledge base",
            "what is",
            "how does",
            "explain",
        ),
        ["specials.agentic-rag-agent", "video.citation", "video.memory"],
        0.8,
    ),
    (
        "memory",
        ("memory", "lesson", "previous run", "project memory", "handoff", "what we learned"),
        ["video.memory"],
        0.78,
    ),
    (
        "agent_loop",
        ("loop", "plan act", "self-review", "cynefin", "replan", "orchestrat"),
        ["specials.agent-loop-creator", "video.orchestrator", "video.planner"],
        0.75,
    ),
    (
        "pack_agent",
        ("screenplay", "shot list", "storyboard", "director", "producer", "cast", "script"),
        ["video.director", "video.screenwriter", "video.planner"],
        0.72,
    ),
]


def route_knowledge(
    query: str,
    *,
    requester_agent_id: str = "video.memory",
    intent_hint: str = "",
) -> dict[str, Any]:
    text = f"{query} {intent_hint}".strip().lower()
    scores: dict[Destination, float] = {}
    hits: dict[Destination, list[str]] = {}

    for dest, keywords, _agents, base in _RULES:
        matched = [k for k in keywords if k in text]
        if matched:
            scores[dest] = base + 0.03 * min(3, len(matched))
            hits[dest] = matched

    # Requester bias
    req = (requester_agent_id or "").lower()
    if "aesthetic" in req or "color" in req or "cine" in req:
        scores["aesthetics"] = max(scores.get("aesthetics", 0.0), 0.7)
    if "research" in req or "citation" in req or "archive" in req:
        scores["rag"] = max(scores.get("rag", 0.0), 0.72)
    if "memory" in req:
        scores["memory"] = max(scores.get("memory", 0.0), 0.7)

    if not scores:
        scores["rag"] = 0.55
        hits["rag"] = ["default_fallback"]

    ordered = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    primary = ordered[0][0]
    secondary = [d for d, _ in ordered[1:4]]
    conf = min(0.95, ordered[0][1])

    agents: list[str] = []
    for dest, _kw, agent_ids, _b in _RULES:
        if dest == primary or dest in secondary[:1]:
            agents.extend(agent_ids)
    agents = list(dict.fromkeys(agents))[:8]

    rationale = [
        f"primary={primary} score={conf:.2f}",
        f"keyword_hits={hits.get(primary) or []}",
        f"requester={requester_agent_id}",
    ]
    if secondary:
        rationale.append(f"secondary={secondary}")

    context_hints = [
        f"Prefer destination '{primary}' first",
        "Fail-closed: no live web / embedding GNN on Host foundation",
    ]
    if primary == "rag":
        context_hints.append("Use POST /api/v1/rag/query for offline grounded answer")
    if primary == "memory":
        context_hints.append("Use POST /api/v1/memory/retrieve for scoped memory")
    if primary == "aesthetics":
        context_hints.append("Use POST /api/v1/aesthetics/evaluate for D1–D10 vector")

    return {
        "query": query,
        "primary": primary,
        "secondary": secondary,
        "confidence": round(conf, 4),
        "rationale": rationale,
        "suggested_agent_ids": agents,
        "context_hints": context_hints,
        "activation_policy": dict(ACTIVATION_POLICY),
        "note": ACTIVATION_POLICY["note"],
        "ok": True,
    }
