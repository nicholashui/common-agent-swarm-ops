"""Cynefin lite classifier for offline agent-loop v3 (adaptive Fast vs Full)."""

from __future__ import annotations

import re
from typing import Any, Literal

CynefinDomain = Literal["simple", "complicated", "complex", "chaotic"]

_TOKEN = re.compile(r"[a-z0-9]+", re.I)

_CHAOTIC = (
    "crisis",
    "emergency",
    "outage",
    "breach",
    "down",
    "incident",
    "urgent",
    "asap",
    "fire",
)
_COMPLEX = (
    "emergent",
    "uncertain",
    "explore",
    "novel",
    "research",
    "discover",
    "multi-agent",
    "orchestrat",
    "strategy",
    "tradeoff",
    "ambiguous",
    "unknown",
)
_COMPLICATED = (
    "analyze",
    "expert",
    "diagnose",
    "optimize",
    "architect",
    "design",
    "compare",
    "evaluate",
    "plan",
    "rubric",
)
_SIMPLE = (
    "format",
    "list",
    "rename",
    "copy",
    "status",
    "health",
    "echo",
    "stub",
)


def classify_cynefin(
    goal: str,
    *,
    override: str | None = None,
) -> dict[str, Any]:
    """Return domain + recommended loop intensity (offline heuristic)."""
    if override and str(override).strip().lower() in {
        "simple",
        "complicated",
        "complex",
        "chaotic",
    }:
        domain: CynefinDomain = str(override).strip().lower()  # type: ignore[assignment]
        return _pack(domain, source="override")

    g = (goal or "").strip().lower()
    tokens = set(_TOKEN.findall(g))

    def hits(words: tuple[str, ...]) -> int:
        return sum(1 for w in words if w in g or any(w in t for t in tokens))

    scores = {
        "chaotic": hits(_CHAOTIC) * 3,
        "complex": hits(_COMPLEX) * 2 + (2 if len(tokens) > 18 else 0),
        "complicated": hits(_COMPLICATED) * 2,
        "simple": hits(_SIMPLE) * 2 + (1 if len(tokens) <= 6 else 0),
    }
    # Default complicated for typical production planning goals
    if max(scores.values()) == 0:
        domain = "complicated"
        return _pack(domain, source="default", scores=scores)

    domain = max(scores, key=lambda k: scores[k])  # type: ignore[assignment]
    return _pack(domain, source="heuristic", scores=scores)


def _pack(
    domain: CynefinDomain,
    *,
    source: str,
    scores: dict[str, int] | None = None,
) -> dict[str, Any]:
    if domain in {"simple", "complicated"}:
        mode = "fast"
        reflection_depth = "light"
        max_reflection_rounds = 1
        enable_fast_path = True
    elif domain == "complex":
        mode = "full"
        reflection_depth = "deep"
        max_reflection_rounds = 2
        enable_fast_path = False
    else:  # chaotic
        mode = "full"
        reflection_depth = "deep"
        max_reflection_rounds = 3
        enable_fast_path = False
    return {
        "domain": domain,
        "mode": mode,
        "reflection_depth": reflection_depth,
        "max_reflection_rounds": max_reflection_rounds,
        "enable_fast_path": enable_fast_path,
        "source": source,
        "scores": scores or {},
        "note": "Offline Cynefin lite — not a live LLM classifier.",
    }
