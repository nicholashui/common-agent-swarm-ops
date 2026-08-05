"""Process-local Pattern Store for RPD fast-path matching (no embeddings)."""

from __future__ import annotations

import re
import threading
from typing import Any
from uuid import uuid4

_TOKEN = re.compile(r"[a-z0-9]+", re.I)


def _tokens(text: str) -> set[str]:
    return {t.lower() for t in _TOKEN.findall(text or "") if len(t) > 1}


class PatternStore:
    """Token-overlap match over successful/failed loop traces."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._patterns: list[dict[str, Any]] = []

    def record(
        self,
        *,
        goal: str,
        agent_id: str,
        outcome: str,
        cynefin_domain: str,
        mode: str,
        quality_score: float,
        summary: str = "",
    ) -> dict[str, Any]:
        entry = {
            "pattern_id": f"pat_{uuid4().hex[:12]}",
            "goal": (goal or "")[:500],
            "agent_id": agent_id,
            "outcome": outcome,
            "cynefin_domain": cynefin_domain,
            "mode": mode,
            "quality_score": float(quality_score),
            "summary": (summary or "")[:400],
            "tokens": sorted(_tokens(goal)),
        }
        with self._lock:
            self._patterns.append(entry)
            if len(self._patterns) > 2000:
                self._patterns = self._patterns[-1500:]
        return {k: v for k, v in entry.items() if k != "tokens"}

    def match(
        self,
        goal: str,
        *,
        agent_id: str | None = None,
        min_score: float = 0.35,
        success_only: bool = True,
    ) -> dict[str, Any] | None:
        q = _tokens(goal)
        if not q:
            return None
        best: dict[str, Any] | None = None
        best_score = 0.0
        with self._lock:
            rows = list(self._patterns)
        for p in rows:
            if success_only and p.get("outcome") not in {"ok", "success", "passed"}:
                continue
            if agent_id and p.get("agent_id") != agent_id:
                # Prefer same agent but still allow others if score high
                agent_boost = 0.0
            else:
                agent_boost = 0.08
            pt = set(p.get("tokens") or [])
            if not pt:
                continue
            overlap = len(q & pt)
            if overlap == 0:
                continue
            score = overlap / max(1, len(q | pt)) + agent_boost
            score = min(0.99, score * 0.7 + float(p.get("quality_score") or 0) * 0.3)
            if score > best_score:
                best_score = score
                best = {k: v for k, v in p.items() if k != "tokens"}
                best["match_score"] = round(score, 4)
        if best and best_score >= min_score:
            return best
        return None

    def list_patterns(self, *, limit: int = 50) -> list[dict[str, Any]]:
        limit = max(1, min(limit, 200))
        with self._lock:
            rows = list(self._patterns[-limit:])
        return [{k: v for k, v in r.items() if k != "tokens"} for r in rows]

    def stats(self) -> dict[str, Any]:
        with self._lock:
            n = len(self._patterns)
            ok = sum(1 for p in self._patterns if p.get("outcome") in {"ok", "success", "passed"})
        return {"count": n, "successful": ok, "backend": "process_local_token_overlap"}
