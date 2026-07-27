#!/usr/bin/env python3
"""Convert design-time VA/generic DNA into host-valid pack graphs under workflows/.

Output: business/video/workflows/*.dna.json that pass OperationalAssetValidator
and a host process_coverage.json referencing only those passing graphs.

Rules:
  - Common agent IDs only (already remapped in design DNA)
  - Empty tool_ids (host allow-list currently only media.stub on pack_spine)
  - Finite budgets within host maxima
  - risk_gate_ids, rollback, critique_loops, human_interrupts declared
  - production_ready always false
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_BACKEND = _ROOT / "backend"
sys.path.insert(0, str(_BACKEND))

from app.video.migration.operational_assets import OperationalAssetValidator  # noqa: E402

VIDEO = _ROOT / "business" / "video"
DESIGN = VIDEO / "design" / "workflows"
OUT = VIDEO / "workflows"
INVENTORY = VIDEO / "inventory.json"

# Host maxima from app.workflows.validator
MAX_NODES = 100
MAX_HANDOFFS = 12
MAX_WALL = 900
MAX_TOOLS = 50


def _load_common_ids() -> set[str]:
    inv = json.loads(INVENTORY.read_text(encoding="utf-8"))
    return {e["agent_id"] for e in inv["entries"] if isinstance(e.get("agent_id"), str)}


def _convert_dna(dna: dict, common_ids: set[str]) -> dict:
    steps = dna.get("steps") or []
    if not isinstance(steps, list) or not steps:
        raise ValueError(f"DNA {dna.get('id')} has no steps")

    # Cap nodes so edges (n-1) never exceed MAX_HANDOFFS
    max_nodes = min(len(steps), MAX_HANDOFFS + 1)
    steps = steps[:max_nodes]

    nodes = []
    edges = []
    agents: list[str] = []
    for index, step in enumerate(steps):
        if not isinstance(step, dict):
            continue
        sid = str(step.get("id") or f"step_{index}")
        agent = str(step.get("agent") or dna.get("owner") or "video.orchestrator")
        if agent not in common_ids:
            agent = "video.orchestrator"
        agents.append(agent)
        nodes.append(
            {
                "id": sid,
                "agent_id": agent,
                "tool_ids": [],
                "memory_reads": [],
                "memory_writes": [],
            }
        )
        # linearize for host graph: use next[0] when present, else sequential
        nxt = step.get("next")
        if isinstance(nxt, list) and nxt and isinstance(nxt[0], str):
            # only keep if target is in truncated set
            target_ids = {str(s.get("id")) for s in steps if isinstance(s, dict)}
            if nxt[0] in target_ids:
                edges.append({"from": sid, "to": nxt[0], "max_traversals": 1})
            elif index + 1 < len(steps):
                next_id = str(steps[index + 1].get("id") or f"step_{index+1}")
                edges.append({"from": sid, "to": next_id, "max_traversals": 1})
        elif index + 1 < len(steps):
            next_id = str(steps[index + 1].get("id") or f"step_{index+1}")
            edges.append({"from": sid, "to": next_id, "max_traversals": 1})

    # Dedupe edges and drop any that would exceed budget
    seen: set[tuple[str, str]] = set()
    unique_edges = []
    for edge in edges:
        key = (edge["from"], edge["to"])
        if key in seen:
            continue
        seen.add(key)
        unique_edges.append(edge)
    if len(unique_edges) > MAX_HANDOFFS:
        unique_edges = unique_edges[:MAX_HANDOFFS]

    n_nodes = len(nodes)
    n_edges = len(unique_edges)
    entry = nodes[0]["id"]
    terminal = [nodes[-1]["id"]]

    # human gate: any step with human_gate_required or irreversible
    needs_human = any(
        isinstance(s, dict) and (s.get("human_gate_required") or s.get("irreversible"))
        for s in steps
    )

    graph = {
        "definition_type": "pack_graph",
        "id": str(dna.get("id") or "wf_video_adapted"),
        "name": str(dna.get("name") or dna.get("id") or "adapted-dna"),
        "version": str(dna.get("version") or "1.0.0"),
        "owner_id": str(dna.get("owner") if dna.get("owner") in common_ids else "video.orchestrator"),
        "engine": "graph",
        "domain": "video",
        "production_ready": False,
        "pattern": "adapted_dna",
        "agent_ids": sorted(set(agents)),
        "common_agent_ids": sorted(set(agents)),
        "execution_budget": {
            "max_node_visits": max(n_nodes, 1),
            "max_handoffs": max(n_edges, 0),
            "max_wall_clock_seconds": min(60, MAX_WALL),
            "max_tool_requests": 0,
        },
        "memory": {"reads": [], "writes": []},
        "risk_gate_ids": ["video.local-safe"],
        "rollback": {
            "plan_id": f"video.rollback.{dna.get('id', 'adapted')}",
            "compensation_step_ids": [terminal[0]] if terminal else [],
        },
        "critique_loops": {
            "enabled": True,
            "max_iterations": 3,
            # VA Domain Pack IDs (match pure VA / generic taxonomy tables)
            "lead_agent_id": "video.critic",
            "judge_agent_id": "video.judge",
        },
        "human_interrupts": {
            "required": True if needs_human else False,
            "gates": [
                {
                    "id": "release_or_irreversible",
                    "when": "irreversible_or_publish",
                    "required": bool(needs_human),
                }
            ],
            "approval_authority": "host_gated",
        },
        "nodes": nodes,
        "edges": unique_edges,
        "entry_node": entry,
        "terminal_node_ids": terminal,
        "allowed_tools": [],
        "provenance": {
            "source": "design/workflows DNA adapted from generic/va",
            "historical_and_non_binding": True,
            "adapted_by": "convert_design_dna_to_host_graphs.py",
            "design_source": f"design/workflows/{dna.get('id', 'unknown')}.dna.json"
            if not str(dna.get("id", "")).endswith(".dna.json")
            else f"design/workflows/{dna.get('id')}",
        },
    }
    return graph


def main() -> int:
    common_ids = _load_common_ids()
    OUT.mkdir(parents=True, exist_ok=True)

    # Keep pack_spine.json; remove previous host DNA if re-running
    for old in OUT.glob("wf_*.dna.json"):
        old.unlink()

    written: list[dict] = []
    validator = OperationalAssetValidator(known_agent_ids=common_ids, allowed_tools=[])
    failures: list[str] = []

    for path in sorted(DESIGN.glob("*.dna.json")):
        dna = json.loads(path.read_text(encoding="utf-8"))
        graph = _convert_dna(dna, common_ids)
        out_name = path.name  # keep wf_*.dna.json
        out_path = OUT / out_name
        out_path.write_text(json.dumps(graph, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        assessment = validator.validate_workflow(
            graph, workflow_path=f"workflows/{out_name}"
        )
        ok = assessment.result == "pass"
        if not ok:
            failures.append(
                f"{out_name}: {[f.code for f in assessment.findings[:5]]}"
            )
        written.append(
            {
                "file": out_name,
                "nodes": len(graph["nodes"]),
                "edges": len(graph["edges"]),
                "agents": graph["agent_ids"],
                "valid": ok,
            }
        )

    # Host process_coverage: one process per adapted graph + pack_spine note
    processes = []
    for item in written:
        if not item["valid"]:
            continue
        processes.append(
            {
                "process_id": f"video.dna.{item['file'].replace('.dna.json', '')}",
                "representation": "pack_graph",
                "workflow_path": f"workflows/{item['file']}",
                "path": f"workflows/{item['file']}",
                "status": "adapted_host_graph",
                "agent_ids": item["agents"],
            }
        )
    # Also document pack_spine as baseline (not dna) - process validator requires
    # only passing adapted workflows from the workflows dict which is *.dna.json only.
    # So pack_spine cannot be in process_coverage for host validation.

    coverage = {
        "schema_version": "1.0",
        "host": "common-agent-swarm-ops",
        "va_only_count": 0,
        "note": (
            "Host process coverage for adapted DNA graphs (common IDs). "
            "Safe baseline remains workflows/pack_spine.json (validated separately)."
        ),
        "processes": processes,
    }
    (VIDEO / "process_coverage.json").write_text(
        json.dumps(coverage, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    report = {
        "written": len(written),
        "valid": sum(1 for w in written if w["valid"]),
        "failures": failures,
        "processes": len(processes),
    }
    print(json.dumps(report, indent=2))
    (VIDEO / "design" / "HOST_GRAPH_CONVERSION.json").write_text(
        json.dumps({"items": written, **report}, indent=2) + "\n", encoding="utf-8"
    )
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
