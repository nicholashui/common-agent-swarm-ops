"""Per-project episodic memory for aesthetics refine / personalization (§7.4, §9.3)."""

from __future__ import annotations

import threading
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4


def _now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


class AestheticProjectMemory:
    """Accepted/rejected artifact history that can ratchet profile notes offline."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        # project_id -> list of entries
        self._by_project: dict[str, list[dict[str, Any]]] = {}

    def record(
        self,
        *,
        project_id: str,
        artifact_ref: str,
        decision: str,
        verdict: dict[str, Any] | None = None,
        note: str = "",
    ) -> dict[str, Any]:
        dec = decision.strip().lower()
        if dec not in {"accepted", "rejected", "candidate"}:
            raise ValueError("decision must be accepted|rejected|candidate")
        pid = (project_id or "default").strip() or "default"
        entry = {
            "entry_id": f"aes_mem_{uuid4().hex[:12]}",
            "project_id": pid,
            "artifact_ref": artifact_ref,
            "decision": dec,
            "aesthetic_quality": (verdict or {}).get("aesthetic_quality"),
            "profile_id": (verdict or {}).get("profile_id"),
            "top_failing_dimensions": list(
                (verdict or {}).get("top_failing_dimensions") or []
            ),
            "note": (note or "")[:500],
            "created_at": _now(),
        }
        with self._lock:
            bucket = self._by_project.setdefault(pid, [])
            bucket.append(entry)
            if len(bucket) > 1000:
                self._by_project[pid] = bucket[-800:]
        return entry

    def list_project(
        self, project_id: str, *, limit: int = 50
    ) -> list[dict[str, Any]]:
        limit = max(1, min(limit, 200))
        pid = (project_id or "default").strip() or "default"
        with self._lock:
            rows = list(self._by_project.get(pid) or [])
        return rows[-limit:]

    def summary(self, project_id: str) -> dict[str, Any]:
        rows = self.list_project(project_id, limit=500)
        accepted = [r for r in rows if r.get("decision") == "accepted"]
        rejected = [r for r in rows if r.get("decision") == "rejected"]
        return {
            "project_id": project_id,
            "total": len(rows),
            "accepted": len(accepted),
            "rejected": len(rejected),
            "candidates": len(rows) - len(accepted) - len(rejected),
            "recent": rows[-8:],
        }
