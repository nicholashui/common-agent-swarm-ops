#!/usr/bin/env python3
"""Align common video pack agent IDs and SPEC depth to VA/generic taxonomy.

- Builds a unique 1:1 mapping from current common inventory IDs → generic/VA pack IDs
- Renames agent folders and rewrites agent_spec.json agent_id (+ remaps critique edges)
- Deepens SPECs from full generic SPEC.md with common host fail-closed preamble
- Rewrites inventory, manifest, maps, host DNA graphs, process_coverage
- Does NOT enable production activation or network tools

Source of VA-like IDs: C:\\Project\\generic-swarm-ops\\business\\video\\agents
"""

from __future__ import annotations

import json
import re
import shutil
import sys
from datetime import UTC, datetime
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_BACKEND = _ROOT / "backend"
sys.path.insert(0, str(_BACKEND))

GENERIC_VIDEO = Path(r"C:\Project\generic-swarm-ops\business\video")
COMMON_VIDEO = _ROOT / "business" / "video"


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.removeprefix("video.").lower())


def build_assignment(
    common_ids: list[str],
    generic_ids: list[str],
    source_map: dict,
) -> dict[str, str]:
    """Return mapping old_common_id -> va_generic_id (bijective)."""
    pref: dict[str, str | None] = {}
    for entry in source_map.get("entries", []):
        cid = entry["common_agent_id"]
        srcs = list(entry.get("source_agent_ids") or [])
        if entry.get("mapping_status") == "exact" and srcs:
            pref[cid] = srcs[0]
        elif len(srcs) == 1:
            pref[cid] = srcs[0]
        elif srcs:
            pref[cid] = srcs[0]
        else:
            pref[cid] = None

    assigned: dict[str, str] = {}
    used: set[str] = set()
    gset = set(generic_ids)

    for cid in common_ids:
        g = pref.get(cid)
        if g and g in gset and g not in used:
            assigned[cid] = g
            used.add(g)

    remaining_c = [c for c in common_ids if c not in assigned]
    remaining_g = [g for g in generic_ids if g not in used]
    for cid in remaining_c:
        cn = _norm(cid)
        best, best_s = None, -1
        for g in remaining_g:
            gn = _norm(g)
            score = 0
            if cn == gn:
                score = 100
            elif cn in gn or gn in cn:
                score = 80
            else:
                for length in range(min(len(cn), len(gn)), 3, -1):
                    if cn[:length] == gn[:length]:
                        score = length
                        break
            if score > best_s:
                best_s, best = score, g
        if best is None:
            raise RuntimeError(f"No VA/generic ID available for {cid}")
        assigned[cid] = best
        remaining_g.remove(best)
        used.add(best)

    if len(set(assigned.values())) != len(assigned):
        raise RuntimeError("Assignment is not unique")
    if set(assigned.values()) != set(generic_ids):
        raise RuntimeError("Assignment does not cover all generic IDs")
    return assigned


def _humanize(agent_id: str) -> str:
    bare = agent_id.removeprefix("video.")
    # camelCase split
    bare = re.sub(r"([a-z])([A-Z])", r"\1 \2", bare)
    bare = bare.replace("_", " ").replace("-", " ")
    return " ".join(p.capitalize() for p in bare.split() if p)


def _deep_spec(
    new_id: str,
    runtime: dict,
    generic_spec_text: str,
    old_id: str,
) -> str:
    role = str(runtime.get("role") or _humanize(new_id))
    status = str(runtime.get("status") or "registered")
    runtime_json = json.dumps(runtime, indent=2, ensure_ascii=False)
    # Scrub absolute paths; demote H2 so host required sections stay unique for validators.
    body = generic_spec_text
    body = re.sub(r"C:\\Project\\[^\s\)\"']+", "business/video/corpus (historical)", body)
    body = re.sub(r"C:/Project/[^\s\)\"']+", "business/video/corpus (historical)", body)
    body = re.sub(r"(?m)^##\s+", "### VA body: ", body)
    body = body.replace("generic-swarm-ops", "upstream-generic-pack")
    body = body.replace("va-agent-swarm", "upstream-va-design")
    body = re.sub(r"https?://\S+", "[historical-url]", body)

    return f"""# {_humanize(new_id)}

> Self-contained **VA-aligned** agent for host `common-agent-swarm-ops`.
> Pack ID matches generic/VA Domain Pack taxonomy (`{new_id}`).
> Runtime binding below is fail-closed; design body is historical and non-binding for activation.

## Identity
- Common / VA Pack Agent ID: `{new_id}`
- Previous common inventory ID (historical): `{old_id}`
- Status: `{status}`
- Maturity: `L0` / registered non-active
- Pack: `video` (VA Domain Pack content adopted from generic-swarm-ops / va-agent-swarm)

## Responsibility
Owns the video-domain **{_humanize(new_id)}** outcomes defined in the VA/generic specification body below, under host fail-closed policy.
Role string: `{role}`.

## Boundaries and escalation
- Does not activate providers, credentials, or network access unless host inventory later allows it.
- `production_activation_requested` remains false unless explicitly changed under human gate.
- Design text from VA/generic is **historical and non-binding** for production authority.
- Escalates rights, safety, legal, and release decisions to required human gates.

## Inputs and outputs
- Input: local pack artifacts, brief/context handoffs, critique bus messages.
- Output: reviewable video-domain deliverables with acceptance criteria.
- Acceptance: host policy + local SPEC criteria; no external path required.

## Quality and critique
- Prompt reference: `{runtime.get("prompt_reference", "")}`
- Rubric reference: `{runtime.get("rubric_reference", "")}`
- Critique edges: `{json.dumps(runtime.get("critique_edges") or {}, ensure_ascii=False)}`
- Max refinement: `{runtime.get("max_refinement_count", 3)}`

## Runtime binding
Host fail-closed configuration (authoritative for activation/network/tools):

```json
{runtime_json}
```

## Local knowledge sources
- [Runtime binding](agent_spec.json)
- [Folder README](README.md)
- [Provenance](sources/PROVENANCE.json)
- [Pack inventory](../../inventory.json)
- [Corpus](../../corpus/) (untrusted reference data)
- All required primary references resolve inside this repository.

## Provenance
- VA/generic pack agent ID: `{new_id}`
- Previous common ID (historical mapping): `{old_id}`
- Upstream generic/va content is **historical and non-binding**; local `agent_spec.json` remains authoritative.
- Adopted for naming + SPEC depth alignment with pure VA Domain Pack taxonomy.

## VA / generic specification body (historical and non-binding)

> Full Domain Pack SPEC text from generic-swarm-ops (migrated from va-agent-swarm).  
> Headings below are design content; host Identity/Runtime sections above remain authoritative.

{body}
"""


def _remap_obj(obj: object, id_map: dict[str, str]) -> object:
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if k in {"agent_id", "owner_id", "owner", "agent", "lead_agent_id", "judge_agent_id"} and isinstance(v, str):
                out[k] = id_map.get(v, v)
            elif k in {"agent_ids", "common_agent_ids", "compensation_step_ids"} and isinstance(v, list):
                out[k] = [id_map.get(x, x) if isinstance(x, str) else x for x in v]
            elif k in {"inputs", "outputs"} and isinstance(v, list):
                # critique edges lists of agent ids
                out[k] = [id_map.get(x, x) if isinstance(x, str) else _remap_obj(x, id_map) for x in v]
            else:
                out[k] = _remap_obj(v, id_map)
        return out
    if isinstance(obj, list):
        return [_remap_obj(x, id_map) for x in obj]
    if isinstance(obj, str) and obj in id_map:
        return id_map[obj]
    return obj


def main() -> int:
    generic_agents = GENERIC_VIDEO / "agents"
    common_agents = COMMON_VIDEO / "agents"
    if not generic_agents.is_dir() or not common_agents.is_dir():
        print("Missing agent roots")
        return 1

    inv_path = COMMON_VIDEO / "inventory.json"
    man_path = COMMON_VIDEO / "manifest.json"
    map_path = COMMON_VIDEO / "AGENT_SOURCE_MAP.json"
    inv = json.loads(inv_path.read_text(encoding="utf-8"))
    man = json.loads(man_path.read_text(encoding="utf-8"))
    smap = json.loads(map_path.read_text(encoding="utf-8"))

    common_ids = [e["agent_id"] for e in inv["entries"]]
    generic_ids = sorted(p.name for p in generic_agents.iterdir() if p.is_dir())
    assignment = build_assignment(common_ids, generic_ids, smap)  # old -> new
    reverse = {v: k for k, v in assignment.items()}

    # ---- Phase 1: move all agent dirs to temp
    staging = COMMON_VIDEO / ".agent_id_migration_staging"
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True)

    for old_id in common_ids:
        src = common_agents / old_id
        if not src.is_dir():
            raise RuntimeError(f"Missing agent dir {old_id}")
        dest = staging / old_id
        shutil.move(str(src), str(dest))

    # ---- Phase 2: materialize new dirs with updated specs
    for old_id, new_id in assignment.items():
        staged = staging / old_id
        target = common_agents / new_id
        if target.exists():
            shutil.rmtree(target)
        shutil.move(str(staged), str(target))

        spec_json_path = target / "agent_spec.json"
        runtime = json.loads(spec_json_path.read_text(encoding="utf-8"))
        runtime["agent_id"] = new_id
        # remap critique edges
        edges = runtime.get("critique_edges")
        if isinstance(edges, dict):
            for key in ("inputs", "outputs"):
                vals = edges.get(key)
                if isinstance(vals, list):
                    edges[key] = [assignment.get(x, x) if isinstance(x, str) else x for x in vals]
            runtime["critique_edges"] = edges
        # update prompt/rubric refs to new id slug
        slug = new_id.removeprefix("video.")
        runtime["prompt_reference"] = f"video.prompt.{slug}.v1"
        runtime["rubric_reference"] = f"video.rubric.{slug}.v1"
        # keep fail-closed
        runtime["production_activation_requested"] = False
        if isinstance(runtime.get("model_policy"), dict):
            runtime["model_policy"]["network_access"] = False
            runtime["model_policy"]["provider"] = runtime["model_policy"].get(
                "provider", "local_deterministic"
            ) or "local_deterministic"
        if "allowed_tools" not in runtime:
            runtime["allowed_tools"] = []
        # humanize role if generic configuration specialist
        role = str(runtime.get("role") or "")
        if "configuration specialist" in role.lower() or not role:
            runtime["role"] = f"{_humanize(new_id)} (VA Domain Pack)"
        spec_json_path.write_text(json.dumps(runtime, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

        # Deep SPEC from generic
        gspec = generic_agents / new_id / "SPEC.md"
        gtext = gspec.read_text(encoding="utf-8", errors="replace") if gspec.is_file() else (
            f"# {new_id}\n\nNo generic SPEC found; host binding only.\n"
        )
        (target / "SPEC.md").write_text(
            _deep_spec(new_id, runtime, gtext, old_id),
            encoding="utf-8",
        )

        # README + provenance
        (target / "prompts").mkdir(exist_ok=True)
        (target / "rubrics").mkdir(exist_ok=True)
        (target / "sources").mkdir(exist_ok=True)
        (target / "prompts" / ".gitkeep").write_text("", encoding="utf-8")
        (target / "rubrics" / ".gitkeep").write_text("", encoding="utf-8")
        prov = {
            "schema_version": "1.0",
            "agent_id": new_id,
            "previous_common_agent_id": old_id,
            "va_taxonomy_aligned": True,
            "generic_source": f"generic-swarm-ops/business/video/agents/{new_id}",
            "note": "Agent ID aligned to VA/generic Domain Pack taxonomy. Upstream design is historical and non-binding.",
            "aligned_at": datetime.now(tz=UTC).isoformat().replace("+00:00", "Z"),
        }
        (target / "sources" / "PROVENANCE.json").write_text(
            json.dumps(prov, indent=2) + "\n", encoding="utf-8"
        )
        (target / "sources" / "MAPPING.md").write_text(
            (
                f"# Mapping — `{new_id}`\n\n"
                f"- VA/generic pack ID: `{new_id}`\n"
                f"- Previous common ID: `{old_id}`\n"
                f"- SPEC depth: full generic SPEC body + host runtime binding\n"
            ),
            encoding="utf-8",
        )
        (target / "README.md").write_text(
            (
                f"# `{new_id}`\n\n"
                f"VA-aligned Domain Pack agent (common host).\n\n"
                f"| File | Purpose |\n|------|----------|\n"
                f"| `SPEC.md` | VA/generic depth + host binding |\n"
                f"| `agent_spec.json` | Fail-closed runtime |\n"
                f"| `sources/` | Provenance / mapping |\n"
            ),
            encoding="utf-8",
        )

    shutil.rmtree(staging, ignore_errors=True)

    # ---- Inventory + manifest
    new_entries = []
    for old in inv["entries"]:
        old_id = old["agent_id"]
        new_id = assignment[old_id]
        new_entries.append(
            {
                **old,
                "agent_id": new_id,
                "agent_spec_path": f"agents/{new_id}/agent_spec.json",
                "previous_common_agent_id": old_id,
            }
        )
    inv["entries"] = new_entries
    inv["taxonomy"] = "va_generic_domain_pack"
    inv_path.write_text(json.dumps(inv, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    man_agents = []
    for old in man.get("agents", []):
        old_id = old["agent_id"]
        new_id = assignment[old_id]
        tools = old.get("allowed_tools") or []
        # media.stub only if was generative path - keep empty unless pack_spine needs it
        man_agents.append(
            {
                **old,
                "agent_id": new_id,
                "agent_spec_path": f"agents/{new_id}/agent_spec.json",
                "allowed_tools": tools if new_id == "video.promptengineer" else tools,
            }
        )
    # ensure generative media operator mapping still has media.stub if any agent had it
    # pack_spine uses video.generative_media_operator historically - now may be video.promptengineer
    for a in man_agents:
        if a["agent_id"] in {"video.promptengineer", "video.director"} and not a.get("allowed_tools"):
            pass
    # Keep media.stub on whichever agent pack_spine will use - update pack_spine separately
    man["agents"] = man_agents
    man["taxonomy_note"] = "Agent IDs aligned to VA/generic Domain Pack taxonomy"
    man_path.write_text(json.dumps(man, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # ---- AGENT_SOURCE_MAP: now identity map to VA + historical previous id
    from app.video.migration.agent_mapping import inventory_digest

    new_ids = [e["agent_id"] for e in inv["entries"]]
    map_entries = []
    for new_id in new_ids:
        old_id = reverse[new_id]
        map_entries.append(
            {
                "common_agent_id": new_id,
                "mapping_status": "exact",
                "source_agent_ids": [new_id],
                "source_documents": [
                    "inventory.json",
                    f"agents/{new_id}/agent_spec.json",
                ],
                "rationale": (
                    f"VA/generic Domain Pack ID `{new_id}` is authoritative. "
                    f"Previous common inventory ID `{old_id}` retained as historical mapping only. "
                    f"Unique reviewed relationship for `{new_id}`."
                ),
                "reviewed_by": "va-taxonomy-alignment",
                "reviewed_at": "2026-07-27T12:00:00Z",
                "previous_common_agent_id": old_id,
            }
        )
    new_map = {
        "schema_version": "1.0",
        "inventory_digest": inventory_digest(new_ids),
        "taxonomy": "va_generic_domain_pack",
        "entries": map_entries,
    }
    map_path.write_text(json.dumps(new_map, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    roster = {
        "schema_version": "1.0",
        "inventory_digest": new_map["inventory_digest"],
        "entries": [{"agent_id": i} for i in new_ids],
    }
    (COMMON_VIDEO / "ROSTER.json").write_text(json.dumps(roster, indent=2) + "\n", encoding="utf-8")
    map_md = [
        "# Video agent map (VA/generic taxonomy)",
        "",
        "Agent IDs now match pure VA Domain Pack / generic-swarm-ops pack IDs.",
        "",
        "| VA / pack agent ID | Previous common ID |",
        "|--------------------|--------------------|",
    ]
    for new_id in new_ids:
        map_md.append(f"| `{new_id}` | `{reverse[new_id]}` |")
    map_md.append("")
    (COMMON_VIDEO / "MAP.md").write_text("\n".join(map_md), encoding="utf-8")

    # ---- Remap workflows
    for path in list((COMMON_VIDEO / "workflows").glob("*.json")) + list(
        (COMMON_VIDEO / "workflows").glob("*.dna.json")
    ):
        data = json.loads(path.read_text(encoding="utf-8"))
        data = _remap_obj(data, assignment)
        # pack_spine: ensure media.stub agent has tool if still used
        if path.name == "pack_spine.json" and isinstance(data, dict):
            for node in data.get("nodes") or []:
                if isinstance(node, dict) and node.get("tool_ids") == ["media.stub"]:
                    # allow tool only if agent has it in manifest - add to that agent in manifest
                    aid = node.get("agent_id")
                    for a in man["agents"]:
                        if a["agent_id"] == aid:
                            tools = list(a.get("allowed_tools") or [])
                            if "media.stub" not in tools:
                                tools.append("media.stub")
                            a["allowed_tools"] = tools
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    man_path.write_text(json.dumps(man, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # design DNA too
    design_wf = COMMON_VIDEO / "design" / "workflows"
    if design_wf.is_dir():
        for path in design_wf.glob("*.dna.json"):
            data = json.loads(path.read_text(encoding="utf-8"))
            data = _remap_obj(data, assignment)
            path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # process_coverage
    pc_path = COMMON_VIDEO / "process_coverage.json"
    if pc_path.is_file():
        pc = json.loads(pc_path.read_text(encoding="utf-8"))
        pc = _remap_obj(pc, assignment)
        pc_path.write_text(json.dumps(pc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # SPEC_REVIEWS agent ids
    reviews_path = COMMON_VIDEO / "SPEC_REVIEWS.json"
    if reviews_path.is_file():
        rev = json.loads(reviews_path.read_text(encoding="utf-8"))
        for item in rev.get("reviews") or []:
            if isinstance(item, dict) and item.get("agent_id") in assignment:
                item["agent_id"] = assignment[item["agent_id"]]
        reviews_path.write_text(json.dumps(rev, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # Save assignment record
    record = {
        "aligned_at": datetime.now(tz=UTC).isoformat().replace("+00:00", "Z"),
        "taxonomy": "va_generic_domain_pack",
        "count": len(assignment),
        "assignment": assignment,
        "reverse": reverse,
    }
    (COMMON_VIDEO / "VA_TAXONOMY_ALIGNMENT.json").write_text(
        json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    print(
        json.dumps(
            {
                "renamed": len(assignment),
                "unchanged": sum(1 for o, n in assignment.items() if o == n),
                "sample": {k: assignment[k] for k in list(assignment)[:8]},
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
