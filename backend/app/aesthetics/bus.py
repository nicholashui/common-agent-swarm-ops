"""In-process aesthetic critique bus (spec §8.2).

Publishes structured aesthetic_feedback messages. Not Redis Streams —
process-local Host foundation only.
"""

from __future__ import annotations

import threading
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4


def _now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


class AestheticCritiqueBus:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._messages: list[dict[str, Any]] = []

    def publish_verdict(
        self,
        *,
        verdict: dict[str, Any],
        to_agent_ids: list[str] | None = None,
        correlation_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """Emit aesthetic_feedback to consumer allowlist (or broadcast list)."""
        corr = (correlation_id or "").strip() or f"aes_{uuid4().hex[:12]}"
        aq = float(verdict.get("aesthetic_quality") or 0.0)
        escalate = bool(verdict.get("escalate_to_hitl"))
        if escalate or aq < 0.35:
            severity = "blocker" if aq < 0.2 else "major"
        elif aq < 0.55:
            severity = "minor"
        else:
            severity = "nit"

        targets = list(to_agent_ids or ["*"])
        out: list[dict[str, Any]] = []
        base_claim = "; ".join(
            (verdict.get("actionable_critique") or [])[:3]
        ) or f"AQ={aq}"

        with self._lock:
            for to_id in targets:
                msg = {
                    "message_id": f"aes_crit_{uuid4().hex[:12]}",
                    "correlation_id": corr,
                    "from_id": "specials.aesthetics-agent",
                    "to_id": to_id,
                    "critique_type": "aesthetic_feedback",
                    "severity": severity,
                    "claim": base_claim[:800],
                    "artifact_ref": str(verdict.get("artifact_ref") or ""),
                    "rubric_score": aq,
                    "hack_likelihood": verdict.get("hack_likelihood"),
                    "top_failing_dimensions": list(
                        verdict.get("top_failing_dimensions") or []
                    ),
                    "profile_id": verdict.get("profile_id"),
                    "requires_hitl": escalate,
                    "kind": "aesthetic_feedback",
                    "created_at": _now(),
                }
                self._messages.append(msg)
                out.append(msg)
            if len(self._messages) > 5000:
                self._messages = self._messages[-4000:]
        return out

    def list_messages(
        self,
        *,
        to_agent_id: str | None = None,
        artifact_ref: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        limit = max(1, min(limit, 200))
        with self._lock:
            rows = list(self._messages)
        if to_agent_id:
            tid = to_agent_id.strip()
            rows = [
                m
                for m in rows
                if m.get("to_id") in {tid, "*"} or m.get("to_id") == tid
            ]
        if artifact_ref:
            aref = artifact_ref.strip()
            rows = [m for m in rows if m.get("artifact_ref") == aref]
        return rows[-limit:]
