#!/usr/bin/env python3
"""Export non-special pack agent org-chart trees for the Registry Org Chart UI.

Scans business/*/agents (excluding specials) and builds a hierarchical org chart:
  pack → top management (orchestrator / entry agents) → VA category departments → agents

Also records critique-edge interconnections from agent_spec.json (SPEC-aligned).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_OUT = _ROOT / "frontend" / "src" / "lib" / "projections" / "org-chart.generated.ts"

# Non-special business packs only (specials are excluded by design).
_EXCLUDED_PACKS = frozenset({"specials", "evals", "schemas", "seeds"})

# Group (department) labels follow the table-of-contents topics in the design
# corpus va-agent-swarm/study/agents.md. vaId ranges align 1:1 with each TOC topic.
_CATEGORY_LABELS: dict[str, str] = {
    "1-ATL": "Above-the-Line Agents",
    "2-Cam": "Camera & Lighting Agents",
    "3-Edit": "Editorial & Color Agents",
    "4-Snd": "Sound & Music Agents",
    "5-Perf": "Performance & Choreography Agents",
    "6-Dist": "Distribution & Marketing Agents",
    "7-Edu": "Education & Domain-Expert Agents",
    "8-AI": "AI-Era Specialist Agents",
    "9-Meta": "Specialist Meta-Agents",
    "10-Sup": "Workflow Support Agents",
}

_SAFE_ID = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]*$")


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _display_name(agent_id: str, role: str, va_name: str | None) -> str:
    if va_name and isinstance(va_name, str) and va_name.strip():
        return va_name.replace("Agent", "").strip() or va_name
    if role:
        # "OrchestratorAgent (VA Domain Pack)" → Orchestrator
        base = role.split("(")[0].strip()
        base = re.sub(r"Agent\b", "", base).strip(" /")
        if base:
            return base
    # video.orchestrator → Orchestrator
    leaf = agent_id.split(".")[-1]
    return leaf.replace("_", " ").title()


def _is_top_management(agent_id: str, entry_agents: list[str], role: str) -> bool:
    if agent_id in entry_agents:
        return True
    leaf = agent_id.rsplit(".", 1)[-1].lower()
    if leaf == "orchestrator":
        return True
    role_l = role.lower()
    return "orchestratoragent" in role_l.replace(" ", "")


def _category_sort_key(cat: str) -> tuple:
    m = re.match(r"^(\d+)", cat or "")
    if m:
        return (int(m.group(1)), cat)
    return (999, cat or "zzz")


def _load_entry_agents(pack_dir: Path, pack_id: str) -> list[str]:
    arch = pack_dir / "archetype_registry.json"
    if arch.is_file():
        try:
            data = _read_json(arch)
            entries = data.get("entry_agents") or []
            if isinstance(entries, list) and entries:
                return [str(e) for e in entries]
        except (OSError, json.JSONDecodeError, TypeError):
            pass
    # Fallback: prefer <pack>.orchestrator then <pack>.planner
    preferred = [f"{pack_id}.orchestrator", f"{pack_id}.planner"]
    return preferred


def _build_pack_group(pack_dir: Path, pack_id: str) -> dict | None:
    agents_root = pack_dir / "agents"
    if not agents_root.is_dir():
        return None

    entry_agents = _load_entry_agents(pack_dir, pack_id)
    agents: list[dict] = []
    critique_links: list[dict] = []
    seen_links: set[tuple[str, str, str]] = set()

    for agent_dir in sorted(agents_root.iterdir()):
        if not agent_dir.is_dir():
            continue
        spec_path = agent_dir / "agent_spec.json"
        if not spec_path.is_file():
            continue
        try:
            spec = _read_json(spec_path)
        except (OSError, json.JSONDecodeError):
            continue

        agent_id = str(spec.get("agent_id") or agent_dir.name)
        if not _SAFE_ID.match(agent_id):
            continue

        role = str(spec.get("role") or "")
        va_name = spec.get("va_name")
        va_category = str(spec.get("va_category") or "uncategorized")
        va_id = spec.get("va_id")
        status = str(spec.get("status") or "registered")
        top = _is_top_management(agent_id, entry_agents, role)

        agents.append(
            {
                "id": agent_id,
                "name": _display_name(agent_id, role, va_name if isinstance(va_name, str) else None),
                "role": role,
                "categoryId": va_category,
                "categoryLabel": _CATEGORY_LABELS.get(va_category, va_category),
                "vaId": va_id if isinstance(va_id, int) else None,
                "status": status,
                "isTopManagement": top,
                "href": f"/registry/agents/{agent_id}",
            }
        )

        critique = spec.get("critique_edges") or {}
        if isinstance(critique, dict):
            for src in critique.get("inputs") or []:
                key = (str(src), agent_id, "critique_in")
                if key not in seen_links:
                    seen_links.add(key)
                    critique_links.append(
                        {"fromId": str(src), "toId": agent_id, "kind": "critique_in"}
                    )
            for dst in critique.get("outputs") or []:
                key = (agent_id, str(dst), "critique_out")
                if key not in seen_links:
                    seen_links.add(key)
                    critique_links.append(
                        {"fromId": agent_id, "toId": str(dst), "kind": "critique_out"}
                    )

    if not agents:
        return None

    # Resolve top management: entry agents present in pack, else any isTopManagement, else first by id
    by_id = {a["id"]: a for a in agents}
    top_ids: list[str] = []
    for eid in entry_agents:
        if eid in by_id:
            top_ids.append(eid)
    if not top_ids:
        top_ids = [a["id"] for a in agents if a["isTopManagement"]]
    if not top_ids:
        top_ids = [sorted(by_id.keys())[0]]

    for a in agents:
        a["isTopManagement"] = a["id"] in top_ids

    # Primary top leader (orchestrator preferred)
    primary_top = top_ids[0]
    for tid in top_ids:
        if tid.endswith(".orchestrator") or "orchestrator" in tid:
            primary_top = tid
            break

    # Department nodes from categories (excluding pure top-management-only empties)
    categories_map: dict[str, list[str]] = {}
    for a in agents:
        categories_map.setdefault(a["categoryId"], []).append(a["id"])

    departments: list[dict] = []
    for cat_id in sorted(categories_map.keys(), key=_category_sort_key):
        member_ids = sorted(
            categories_map[cat_id],
            key=lambda i: (
                by_id[i]["vaId"] is None,
                by_id[i]["vaId"] if by_id[i]["vaId"] is not None else 9999,
                i,
            ),
        )
        departments.append(
            {
                "id": f"{pack_id}.dept.{cat_id}",
                "categoryId": cat_id,
                "label": _CATEGORY_LABELS.get(cat_id, cat_id),
                "memberIds": member_ids,
                "reportsTo": primary_top,
            }
        )

    # Hierarchy edges: top → departments → agents (agents report to dept; secondary top managers report to primary)
    hierarchy_edges: list[dict] = []
    for tid in top_ids:
        if tid != primary_top:
            hierarchy_edges.append(
                {"fromId": primary_top, "toId": tid, "kind": "management"}
            )
    for dept in departments:
        hierarchy_edges.append(
            {"fromId": primary_top, "toId": dept["id"], "kind": "department"}
        )
        for mid in dept["memberIds"]:
            if mid in top_ids:
                # Top managers already hang under primary; skip double-link under dept
                # but still list them in dept for membership stats.
                continue
            hierarchy_edges.append(
                {"fromId": dept["id"], "toId": mid, "kind": "member"}
            )

    return {
        "packId": pack_id,
        "label": pack_id.replace("-", " ").title(),
        "folderPath": f"business/{pack_id}",
        "primaryTopId": primary_top,
        "topManagementIds": top_ids,
        "agentCount": len(agents),
        "departmentCount": len(departments),
        "agents": sorted(agents, key=lambda a: (a["vaId"] is None, a["vaId"] or 9999, a["id"])),
        "departments": departments,
        "hierarchyEdges": hierarchy_edges,
        "critiqueEdges": critique_links,
    }


def build_org_chart_payload(business_root: Path) -> dict:
    groups: list[dict] = []
    for pack_dir in sorted(business_root.iterdir()):
        if not pack_dir.is_dir():
            continue
        pack_id = pack_dir.name
        if pack_id in _EXCLUDED_PACKS or pack_id.startswith("."):
            continue
        group = _build_pack_group(pack_dir, pack_id)
        if group:
            groups.append(group)

    return {
        "schemaVersion": "1.0",
        "source": "business/*/agents (non-special packs)",
        "packCount": len(groups),
        "agentCount": sum(g["agentCount"] for g in groups),
        "groups": groups,
    }


def _ts_escape(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace("'", "\\'")
        .replace("\n", "\\n")
        .replace("\r", "")
    )


def _emit_ts(payload: dict) -> str:
    # Emit as JSON assigned to typed const — simplest durable generator path.
    body = json.dumps(payload, indent=2, ensure_ascii=False)
    return f"""/* AUTO-GENERATED by scripts/business/export_org_chart_for_ui.py — do not edit. */
/* Non-special business packs only (specials excluded). */

export type OrgChartEdgeKind =
  | "management"
  | "department"
  | "member"
  | "critique_in"
  | "critique_out";

export interface OrgChartAgentNode {{
  readonly id: string;
  readonly name: string;
  readonly role: string;
  readonly categoryId: string;
  readonly categoryLabel: string;
  readonly vaId: number | null;
  readonly status: string;
  readonly isTopManagement: boolean;
  readonly href: string;
}}

export interface OrgChartDepartmentNode {{
  readonly id: string;
  readonly categoryId: string;
  readonly label: string;
  readonly memberIds: readonly string[];
  readonly reportsTo: string;
}}

export interface OrgChartEdge {{
  readonly fromId: string;
  readonly toId: string;
  readonly kind: OrgChartEdgeKind;
}}

export interface OrgChartPackGroup {{
  readonly packId: string;
  readonly label: string;
  readonly folderPath: string;
  readonly primaryTopId: string;
  readonly topManagementIds: readonly string[];
  readonly agentCount: number;
  readonly departmentCount: number;
  readonly agents: readonly OrgChartAgentNode[];
  readonly departments: readonly OrgChartDepartmentNode[];
  readonly hierarchyEdges: readonly OrgChartEdge[];
  readonly critiqueEdges: readonly OrgChartEdge[];
}}

export interface OrgChartPayload {{
  readonly schemaVersion: string;
  readonly source: string;
  readonly packCount: number;
  readonly agentCount: number;
  readonly groups: readonly OrgChartPackGroup[];
}}

export const ORG_CHART_PAYLOAD: OrgChartPayload = {body} as const;
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--business-dir",
        type=Path,
        default=_ROOT / "business",
        help="Business root (default: ./business)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=_OUT,
        help="Output TypeScript module path",
    )
    args = parser.parse_args()

    payload = build_org_chart_payload(args.business_dir.resolve())
    if not payload["groups"]:
        print("No non-special pack groups found.", file=sys.stderr)
        return 1

    out = args.out.resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(_emit_ts(payload), encoding="utf-8")
    print(
        f"Wrote {out.relative_to(_ROOT)} "
        f"({payload['packCount']} packs, {payload['agentCount']} agents)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
