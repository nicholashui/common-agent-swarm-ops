"""In-process RAG critique bus (spec critique-bus style, process-local)."""

from __future__ import annotations

import threading
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4


def _now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


class RagCritiqueBus:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._messages: list[dict[str, Any]] = []

    def publish_run(
        self,
        run: dict[str, Any],
        *,
        to_agent_ids: list[str] | None = None,
        correlation_id: str | None = None,
    ) -> list[dict[str, Any]]:
        corr = (correlation_id or "").strip() or f"rag_{uuid4().hex[:12]}"
        conf = float(run.get("confidence") or 0.0)
        escalate = bool(run.get("escalate_to_hitl"))
        if escalate or conf < 0.3:
            severity = "major"
        elif conf < 0.55:
            severity = "minor"
        else:
            severity = "nit"

        targets = list(to_agent_ids or ["video.memory", "video.citation", "video.webresearch"])
        claim = (run.get("critique") or run.get("final_answer") or "")[:400]
        out: list[dict[str, Any]] = []
        with self._lock:
            for to_id in targets:
                msg = {
                    "message_id": f"rag_crit_{uuid4().hex[:12]}",
                    "correlation_id": corr,
                    "from_id": "specials.agentic-rag-agent",
                    "to_id": to_id,
                    "critique_type": "rag_feedback",
                    "severity": severity,
                    "claim": claim,
                    "run_id": run.get("run_id"),
                    "query": run.get("query"),
                    "confidence": conf,
                    "citation_count": len(run.get("citations") or []),
                    "requires_hitl": escalate,
                    "kind": "rag_feedback",
                    "created_at": _now(),
                }
                self._messages.append(msg)
                out.append(msg)
            if len(self._messages) > 5000:
                self._messages = self._messages[-4000:]
        return out

    def list_messages(self, *, limit: int = 50) -> list[dict[str, Any]]:
        limit = max(1, min(limit, 200))
        with self._lock:
            return list(self._messages[-limit:])
