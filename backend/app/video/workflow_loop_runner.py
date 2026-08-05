"""Execute pack DNA / workflow graphs as sequential offline agent loops.

Each node with an agent_id runs Host AgentLoopService (Plan→Act→Self-Review).
Shared project memory carries opaque handoff refs between nodes.
No production media tools; fail-closed activation policy.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.video.agent_loop_service import ACTIVATION_POLICY, AgentLoopService, get_agent_loop_service
from app.video.pack_runtime.paths import AGENTS_ROOT

_SAFE_ID = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]*$")
_REPO_ROOT = Path(__file__).resolve().parents[3]
_WORKFLOWS_DIR = _REPO_ROOT / "business" / "video" / "workflows"
_DESIGN_WORKFLOWS = _REPO_ROOT / "business" / "video" / "design" / "workflows"


def _load_workflow_doc(workflow_id: str) -> dict[str, Any]:
    if not _SAFE_ID.match(workflow_id):
        raise ValueError(f"Invalid workflow_id: {workflow_id}")
    candidates = [
        _WORKFLOWS_DIR / f"{workflow_id}.dna.json",
        _DESIGN_WORKFLOWS / f"{workflow_id}.dna.json",
        _WORKFLOWS_DIR / f"{workflow_id}.json",
    ]
    for path in candidates:
        if path.is_file():
            raw = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                return raw
    raise FileNotFoundError(f"Workflow not found: {workflow_id}")


def _ordered_agent_steps(doc: dict[str, Any]) -> list[dict[str, str]]:
    """Return ordered {step_id, agent_id} from DNA steps or pack graph nodes+edges."""
    # Design DNA: steps[]
    steps = doc.get("steps")
    if isinstance(steps, list) and steps:
        out: list[dict[str, str]] = []
        for step in steps:
            if not isinstance(step, dict):
                continue
            sid = str(step.get("id") or "").strip()
            agent = str(step.get("agent") or step.get("agent_id") or "").strip()
            if sid and agent:
                out.append({"step_id": sid, "agent_id": agent})
        if out:
            return out

    # Host pack graph: nodes[] + edges[] + entry_node
    nodes = doc.get("nodes")
    if not isinstance(nodes, list) or not nodes:
        # Fallback: agent_ids list only
        ids = doc.get("agent_ids") or doc.get("common_agent_ids") or []
        if isinstance(ids, list):
            return [
                {"step_id": f"step_{i}", "agent_id": str(a)}
                for i, a in enumerate(ids)
                if str(a).strip()
            ]
        return []

    by_id: dict[str, dict[str, Any]] = {}
    for n in nodes:
        if isinstance(n, dict) and n.get("id"):
            by_id[str(n["id"])] = n

    edges = doc.get("edges") if isinstance(doc.get("edges"), list) else []
    outgoing: dict[str, list[str]] = {nid: [] for nid in by_id}
    for e in edges:
        if not isinstance(e, dict):
            continue
        fr = str(e.get("from") or e.get("source") or "")
        to = str(e.get("to") or e.get("target") or "")
        if fr in outgoing and to in by_id:
            outgoing[fr].append(to)

    entry = str(doc.get("entry_node") or "")
    if entry not in by_id and by_id:
        entry = next(iter(by_id))

    ordered: list[dict[str, str]] = []
    seen: set[str] = set()
    cursor = entry
    while cursor and cursor not in seen:
        seen.add(cursor)
        node = by_id.get(cursor) or {}
        agent = str(node.get("agent_id") or "").strip()
        if agent:
            ordered.append({"step_id": cursor, "agent_id": agent})
        nxts = outgoing.get(cursor) or []
        cursor = nxts[0] if nxts else ""
    # any orphans
    for nid, node in by_id.items():
        if nid in seen:
            continue
        agent = str(node.get("agent_id") or "").strip()
        if agent:
            ordered.append({"step_id": nid, "agent_id": agent})
    return ordered


class ProjectMemoryStore:
    """Opaque project memory for one workflow run (handoff refs + notes)."""

    def __init__(self) -> None:
        self.entries: list[dict[str, Any]] = []
        self.handoff_refs: list[str] = []

    def write(
        self,
        *,
        agent_id: str,
        step_id: str,
        summary: str,
        handoff_ref: str | None = None,
        meta: dict[str, Any] | None = None,
    ) -> None:
        rec = {
            "agent_id": agent_id,
            "step_id": step_id,
            "summary": summary[:500],
            "handoff_ref": handoff_ref,
            "meta": meta or {},
        }
        self.entries.append(rec)
        if handoff_ref:
            self.handoff_refs.append(handoff_ref)

    def context_blob(self) -> dict[str, Any]:
        return {
            "entry_count": len(self.entries),
            "handoff_refs": list(self.handoff_refs)[-32:],
            "recent": self.entries[-8:],
        }


class WorkflowLoopRunner:
    """Run a DNA/pack workflow as sequential offline agent loops + memory."""

    def __init__(self, loop_service: AgentLoopService | None = None) -> None:
        self._loops = loop_service or get_agent_loop_service()

    def list_available_workflows(self) -> list[dict[str, Any]]:
        found: dict[str, Path] = {}
        for root in (_WORKFLOWS_DIR, _DESIGN_WORKFLOWS):
            if not root.is_dir():
                continue
            for path in root.glob("*.dna.json"):
                wid = path.name.replace(".dna.json", "")
                found.setdefault(wid, path)
        items = []
        for wid, path in sorted(found.items()):
            try:
                doc = json.loads(path.read_text(encoding="utf-8"))
                steps = _ordered_agent_steps(doc) if isinstance(doc, dict) else []
            except (OSError, json.JSONDecodeError):
                steps = []
            items.append(
                {
                    "workflow_id": wid,
                    "path": str(path.relative_to(_REPO_ROOT)).replace("\\", "/"),
                    "step_count": len(steps),
                    "agent_ids": [s["agent_id"] for s in steps],
                }
            )
        return items

    def run(
        self,
        workflow_id: str,
        *,
        organization_id: str,
        goal: str,
        correlation_id: str | None = None,
        stop_on_failure: bool = True,
        max_nodes: int = 64,
    ) -> dict[str, Any]:
        corr = (correlation_id or "").strip() or f"wf_{uuid4().hex[:12]}"
        try:
            doc = _load_workflow_doc(workflow_id)
        except (OSError, ValueError, FileNotFoundError, json.JSONDecodeError) as exc:
            return {
                "ok": False,
                "error": str(exc),
                "workflow_id": workflow_id,
                "activation_policy": ACTIVATION_POLICY,
            }

        steps = _ordered_agent_steps(doc)[: max(1, min(max_nodes, 64))]
        if not steps:
            return {
                "ok": False,
                "error": "Workflow has no agent steps/nodes",
                "workflow_id": workflow_id,
                "activation_policy": ACTIVATION_POLICY,
            }

        memory = ProjectMemoryStore()
        critiques: list[dict[str, Any]] = []
        node_results: list[dict[str, Any]] = []
        passed = 0

        for step in steps:
            agent_id = step["agent_id"]
            step_id = step["step_id"]
            # Skip agents not under video pack root
            agent_dir = AGENTS_ROOT / agent_id
            if not agent_dir.is_dir():
                node_results.append(
                    {
                        "step_id": step_id,
                        "agent_id": agent_id,
                        "ok": False,
                        "skipped": True,
                        "error": "agent not in video pack inventory",
                    }
                )
                if stop_on_failure:
                    break
                continue

            row = self._loops.run(
                agent_id,
                organization_id=organization_id,
                goal=goal,
                correlation_id=f"{corr}:{step_id}",
                inputs={
                    "workflow_id": workflow_id,
                    "step_id": step_id,
                    "project_memory": memory.context_blob(),
                    "parent_assets": list(memory.handoff_refs[-8:]),
                },
            )
            ok = bool(row.get("ok"))
            if ok:
                passed += 1
            handoff_ref = f"loop:{agent_id}:{row.get('run_id') or step_id}"
            memory.write(
                agent_id=agent_id,
                step_id=step_id,
                summary=str(row.get("artifact_summary") or row.get("status") or ""),
                handoff_ref=handoff_ref,
                meta={
                    "status": row.get("status"),
                    "l2": (row.get("l2") or {}).get("score")
                    if isinstance(row.get("l2"), dict)
                    else None,
                },
            )
            for c in row.get("critiques_emitted") or []:
                if isinstance(c, dict):
                    critiques.append(c)
            node_results.append(
                {
                    "step_id": step_id,
                    "agent_id": agent_id,
                    "ok": ok,
                    "status": row.get("status"),
                    "run_id": row.get("run_id"),
                    "l2": row.get("l2"),
                    "needs_hitl": row.get("needs_hitl"),
                    "handoff_ref": handoff_ref,
                }
            )
            if stop_on_failure and not ok:
                break

        return {
            "ok": passed == len(node_results) and len(node_results) > 0,
            "workflow_id": workflow_id,
            "correlation_id": corr,
            "node_count": len(steps),
            "completed": len(node_results),
            "passed": passed,
            "failed": len(node_results) - passed,
            "nodes": node_results,
            "project_memory": memory.context_blob(),
            "critiques": critiques[-50:],
            "activation_policy": ACTIVATION_POLICY,
            "note": (
                "Sequential offline agent loops over DNA/pack graph. "
                "Not concurrent production swarm · not production media."
            ),
        }


__all__ = ["ProjectMemoryStore", "WorkflowLoopRunner", "_ordered_agent_steps"]
