"""Durable process-local store for product façade swarms, package gates, and audit.

Default root: <repo>/.data/product_facade
Override: CASOPS_PRODUCT_FACADE_DATA=/path
Disable: CASOPS_PRODUCT_FACADE_PERSIST=0
"""

from __future__ import annotations

import json
import os
import threading
from datetime import datetime
from pathlib import Path
from typing import Any


def default_data_dir() -> Path:
    env = (os.environ.get("CASOPS_PRODUCT_FACADE_DATA") or "").strip()
    if env:
        return Path(env).expanduser().resolve()
    # backend/app/api/v1/this.py → parents[4] == repository root
    return Path(__file__).resolve().parents[4] / ".data" / "product_facade"


def persistence_enabled() -> bool:
    return (os.environ.get("CASOPS_PRODUCT_FACADE_PERSIST") or "1").strip().lower() not in {
        "0",
        "false",
        "no",
        "off",
    }


def _dt_to_iso(value: datetime | str | None) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


def _parse_dt(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    text = str(value or "")
    if not text:
        from datetime import UTC

        return datetime.now(UTC)
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        from datetime import UTC

        return datetime.now(UTC)


class ProductFacadeStore:
    """JSON + JSONL persistence under an org-agnostic local data directory."""

    def __init__(self, root: Path | None = None) -> None:
        self.root = (root or default_data_dir()).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self._swarms_path = self.root / "swarms.json"
        self._approvals_path = self.root / "package_approvals.json"
        self._activity_path = self.root / "activity.json"
        self._audit_path = self.root / "audit.jsonl"
        self._lock = threading.RLock()

    def load_state(self) -> dict[str, Any]:
        with self._lock:
            return {
                "swarms": self._read_json(self._swarms_path, default={}),
                "package_approvals": self._read_json(self._approvals_path, default={}),
                "activity": self._read_json(self._activity_path, default=[]),
            }

    def save_swarms(self, swarms: dict[str, dict[str, Any]]) -> None:
        with self._lock:
            self._write_json(self._swarms_path, swarms)

    def save_package_approvals(self, approvals: dict[str, dict[str, Any]]) -> None:
        with self._lock:
            self._write_json(self._approvals_path, approvals)

    def save_activity(self, activity: list[dict[str, Any]]) -> None:
        with self._lock:
            # Cap retained activity for local disk hygiene
            self._write_json(self._activity_path, activity[-2000:])

    def append_audit(self, record: dict[str, Any]) -> None:
        line = json.dumps(record, ensure_ascii=False, separators=(",", ":"), default=str)
        with self._lock:
            with self._audit_path.open("a", encoding="utf-8") as handle:
                handle.write(line + "\n")

    def list_audit(self, *, organization_id: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        limit = max(1, min(limit, 500))
        if not self._audit_path.is_file():
            return []
        rows: list[dict[str, Any]] = []
        with self._lock:
            try:
                text = self._audit_path.read_text(encoding="utf-8")
            except OSError:
                return []
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(row, dict):
                continue
            if organization_id and str(row.get("organization_id") or "") != organization_id:
                continue
            rows.append(row)
        return rows[-limit:]

    def _read_json(self, path: Path, *, default: Any) -> Any:
        if not path.is_file():
            return default
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return default
        return raw if raw is not None else default

    def _write_json(self, path: Path, payload: Any) -> None:
        tmp = path.with_suffix(path.suffix + ".tmp")
        data = json.dumps(payload, ensure_ascii=False, indent=2, default=str)
        tmp.write_text(data + "\n", encoding="utf-8")
        tmp.replace(path)


def serialize_swarm(record: Any) -> dict[str, Any]:
    """Convert SwarmRecord (or duck type) to JSON-safe dict."""
    return {
        "swarm_id": record.swarm_id,
        "organization_id": record.organization_id,
        "name": record.name,
        "revision": record.revision,
        "status": record.status,
        "created_at": _dt_to_iso(record.created_at),
        "updated_at": _dt_to_iso(record.updated_at),
        "pattern_ref": record.pattern_ref,
        "nodes": list(record.nodes or []),
        "edges": list(record.edges or []),
        "policy": dict(record.policy or {}),
        "members": list(record.members or []),
        "pins": list(record.pins or []),
        "last_run_id": record.last_run_id,
        "goal_summary": getattr(record, "goal_summary", None),
        "brief": getattr(record, "brief", None),
        "spine": getattr(record, "spine", None),
    }


def serialize_activity(record: Any) -> dict[str, Any]:
    return {
        "activity_id": record.activity_id,
        "organization_id": record.organization_id,
        "category": record.category,
        "severity": record.severity,
        "summary": record.summary,
        "subject_reference": record.subject_reference,
        "occurred_at": _dt_to_iso(record.occurred_at),
        "correlation_id": record.correlation_id,
        "status": record.status,
    }


__all__ = [
    "ProductFacadeStore",
    "default_data_dir",
    "persistence_enabled",
    "serialize_activity",
    "serialize_swarm",
    "_parse_dt",
]
