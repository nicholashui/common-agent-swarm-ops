#!/usr/bin/env python3
"""Adopt remaining generic-swarm-ops VA pack assets that common still lacks.

Goals (make common strictly better than generic for VA implementation):
  1. graphs/, tools/, evals/ data trees
  2. Per-agent sources/excerpts + sources/study (offline VA depth)
  3. Expand host process_coverage to VA process_id breadth (DNA-linked rows)
  4. Full design process catalog (incl. pack_doc rows) under design/
  5. Refresh PROCESSES.md + pack README note
  6. Never enable production_ready, network tools, or overwrite fail-closed agent_spec
"""

from __future__ import annotations

import json
import re
import shutil
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VIDEO = ROOT / "business" / "video"
GENERIC = Path(r"C:\Project\generic-swarm-ops\business\video")
GENERIC_ROOT = Path(r"C:\Project\generic-swarm-ops")


def _copy_tree(src: Path, dest: Path) -> int:
    if not src.exists():
        return 0
    n = 0
    for path in src.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(src)
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        n += 1
    return n


def _copy_agent_source_depth() -> dict[str, int]:
    """Copy excerpts/ and study/ under each matching agent sources/."""
    agents = VIDEO / "agents"
    gen_agents = GENERIC / "agents"
    stats = {"agents": 0, "files": 0, "skipped": 0}
    if not gen_agents.is_dir():
        return stats
    for agent_dir in sorted(agents.iterdir()):
        if not agent_dir.is_dir():
            continue
        gdir = gen_agents / agent_dir.name
        if not gdir.is_dir():
            stats["skipped"] += 1
            continue
        sources = agent_dir / "sources"
        sources.mkdir(parents=True, exist_ok=True)
        copied = 0
        for sub in ("excerpts", "study"):
            src = gdir / "sources" / sub
            if src.is_dir():
                copied += _copy_tree(src, sources / sub)
        # also copy any top-level source md/json besides MAPPING/PROVENANCE we keep
        for path in gdir.glob("sources/*"):
            if path.is_file() and path.name not in {"MAPPING.md", "PROVENANCE.json"}:
                target = sources / path.name
                if not target.exists():
                    shutil.copy2(path, target)
                    copied += 1
        if copied:
            stats["agents"] += 1
            stats["files"] += copied
            # Extend PROVENANCE if present
            prov = sources / "PROVENANCE.json"
            if prov.is_file():
                try:
                    data = json.loads(prov.read_text(encoding="utf-8"))
                except json.JSONDecodeError:
                    data = {}
                if not isinstance(data, dict):
                    data = {}
                data.setdefault("generic_source_depth", {})
                data["generic_source_depth"] = {
                    "excerpts": (sources / "excerpts").is_dir(),
                    "study": (sources / "study").is_dir(),
                    "adopted_at": datetime.now(UTC).isoformat(),
                    "upstream": "generic-swarm-ops/business/video/agents",
                }
                prov.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return stats


def _workflow_agent_ids(workflow_path: Path) -> list[str]:
    if not workflow_path.is_file():
        return ["video.orchestrator"]
    try:
        data = json.loads(workflow_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ["video.orchestrator"]
    ids: list[str] = []
    if isinstance(data.get("agent_ids"), list):
        ids = [str(x) for x in data["agent_ids"] if isinstance(x, str)]
    elif isinstance(data.get("nodes"), list):
        for node in data["nodes"]:
            if isinstance(node, dict) and isinstance(node.get("agent_id"), str):
                ids.append(node["agent_id"])
            elif isinstance(node, dict) and isinstance(node.get("agent"), str):
                ids.append(node["agent"])
    ids = sorted(set(ids))
    return ids or ["video.orchestrator"]


def _rel_host_path(generic_path: str) -> str | None:
    """Map generic process path → host-relative workflow path under video/."""
    name = Path(generic_path.replace("\\", "/")).name
    if name.endswith(".dna.json"):
        candidate = VIDEO / "workflows" / name
        if candidate.is_file():
            return f"workflows/{name}"
    # pack docs stay design-only
    if "docs/" in generic_path.replace("\\", "/"):
        return None
    return None


def expand_process_coverage() -> dict:
    """Build host process_coverage with VA process_id breadth over host-valid DNA graphs."""
    gen = json.loads((GENERIC / "process_coverage.json").read_text(encoding="utf-8"))
    gen_processes = gen.get("processes") if isinstance(gen, dict) else []
    host_rows: list[dict] = []
    design_rows: list[dict] = []

    for raw in gen_processes or []:
        if not isinstance(raw, dict):
            continue
        process_id = str(raw.get("process_id") or "")
        gpath = str(raw.get("path") or "")
        host_rel = _rel_host_path(gpath)
        design_row = {
            "process_id": process_id,
            "representation": raw.get("representation", "dna"),
            "path": gpath,
            "status": raw.get("status", "design"),
            "historical_and_non_binding": True,
        }
        design_rows.append(design_row)
        if host_rel is None:
            continue
        agent_ids = _workflow_agent_ids(VIDEO / host_rel)
        host_rows.append(
            {
                "process_id": process_id,
                "representation": "pack_graph",
                "workflow_path": host_rel,
                "path": host_rel,
                "status": "adapted_host_graph",
                "agent_ids": agent_ids,
                "va_process_id": process_id,
            }
        )

    # Ensure every host DNA workflow appears at least once
    seen_paths = {r["workflow_path"] for r in host_rows}
    for dna in sorted((VIDEO / "workflows").glob("*.dna.json")):
        rel = f"workflows/{dna.name}"
        if rel in seen_paths:
            continue
        host_rows.append(
            {
                "process_id": f"video.dna.{dna.stem}",
                "representation": "pack_graph",
                "workflow_path": rel,
                "path": rel,
                "status": "adapted_host_graph",
                "agent_ids": _workflow_agent_ids(dna),
            }
        )

    host_doc = {
        "schema_version": "1.0",
        "host": "common-agent-swarm-ops",
        "va_only_count": 0,
        "note": (
            "Host process coverage expanded to VA process_id breadth from generic. "
            "Each DNA-linked process references a host-valid pack_graph under workflows/. "
            "pack_doc rows live only in design/process_coverage_va.json. "
            "Safe baseline remains workflows/pack_spine.json."
        ),
        "processes": host_rows,
        "provenance": {
            "source": "generic-swarm-ops/business/video/process_coverage.json",
            "adapted_at": datetime.now(UTC).isoformat(),
            "production_ready": False,
        },
    }
    design_doc = {
        "schema_version": "1.0",
        "wave": 5,
        "va_only_count": 0,
        "note": "Full VA/generic process catalog (historical design). Host gate uses process_coverage.json.",
        "processes": design_rows,
        "provenance": gen.get("provenance") if isinstance(gen, dict) else {},
    }

    (VIDEO / "process_coverage.json").write_text(
        json.dumps(host_doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    design_dir = VIDEO / "design"
    design_dir.mkdir(parents=True, exist_ok=True)
    (design_dir / "process_coverage_va.json").write_text(
        json.dumps(design_doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return {"host_processes": len(host_rows), "design_processes": len(design_rows)}


def rewrite_processes_md(host_count: int, design_count: int) -> None:
    lines = [
        "# Video pack processes (common-agent-swarm-ops)",
        "",
        "Host-authoritative index: `process_coverage.json` (pack_graph rows only).",
        "Full VA design catalog: `design/process_coverage_va.json` (includes pack_doc rows).",
        "",
        f"- Host process rows: **{host_count}**",
        f"- Design process rows: **{design_count}**",
        "- DNA workflows: `workflows/*.dna.json` (adapted, `production_ready: false`)",
        "- Safe baseline: `workflows/pack_spine.json`",
        "- Graphs (design): `graphs/`",
        "- Tool stubs (docs): `tools/`",
        "- Eval fixtures: `evals/`",
        "",
        "All process agent_ids use pure VA Domain Pack taxonomy (aligned with generic).",
        "",
    ]
    (VIDEO / "PROCESSES.md").write_text("\n".join(lines), encoding="utf-8")


def adopt_pack_trees() -> dict[str, int]:
    counts: dict[str, int] = {}
    for name in ("graphs", "tools", "evals", "ui"):
        counts[name] = _copy_tree(GENERIC / name, VIDEO / name)
    # refresh docs that generic has (process maps / deep modules)
    for name in ("process-maps.md", "deep-spec-modules.md"):
        src = GENERIC / "docs" / name
        if src.is_file():
            dest = VIDEO / "docs" / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            counts[f"docs/{name}"] = 1
    # policies from generic if missing
    gpol = GENERIC / "policies"
    if gpol.is_dir():
        n = 0
        for path in gpol.rglob("*"):
            if not path.is_file():
                continue
            rel = path.relative_to(gpol)
            target = VIDEO / "policies" / rel
            if not target.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, target)
                n += 1
        counts["policies_new"] = n
    # native DNA into design/workflows already; re-copy generic DNA for fidelity
    counts["design_dna"] = _copy_tree(GENERIC / "workflows", VIDEO / "design" / "workflows")
    return counts


def update_readme_snippet() -> None:
    readme = VIDEO / "README.md"
    if not readme.is_file():
        return
    text = readme.read_text(encoding="utf-8", errors="replace")
    banner = (
        "\n## VA pack parity (beyond generic)\n\n"
        "- Agent IDs: pure VA/generic taxonomy (114/114).\n"
        "- Host DNA graphs + expanded process_coverage (VA process_id breadth).\n"
        "- Design catalog: `design/process_coverage_va.json` (full generic 33-style index).\n"
        "- Offline depth: per-agent `sources/excerpts` + `sources/study`.\n"
        "- Pack trees: `graphs/`, `tools/`, `evals/` (data-only; non-activating).\n"
        "- Specials pack: 19 self-contained agents (generic has no specials pack).\n"
        "- UI: Registry export of 133 agents.\n"
        "- Fail-closed: production_ready false; no live media providers.\n"
    )
    if "VA pack parity (beyond generic)" in text:
        text = re.sub(
            r"\n## VA pack parity \(beyond generic\)\n.*?(?=\n## |\Z)",
            banner + "\n",
            text,
            count=1,
            flags=re.S,
        )
    else:
        text = text.rstrip() + "\n" + banner
    readme.write_text(text, encoding="utf-8")


def write_adoption_record(payload: dict) -> None:
    path = VIDEO / "ADOPTION_GENERIC_REMAINING.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    if not GENERIC.exists():
        print("FAIL: generic video pack not found at", GENERIC)
        return 1

    trees = adopt_pack_trees()
    sources = _copy_agent_source_depth()
    proc = expand_process_coverage()
    rewrite_processes_md(proc["host_processes"], proc["design_processes"])
    update_readme_snippet()

    record = {
        "adopted_at": datetime.now(UTC).isoformat(),
        "generic_root": str(GENERIC_ROOT),
        "trees": trees,
        "agent_source_depth": sources,
        "process_coverage": proc,
        "production_activation": False,
        "goal": "common surpasses generic for VA implementation (content + host + UI + specials)",
    }
    write_adoption_record(record)
    print(json.dumps(record, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
