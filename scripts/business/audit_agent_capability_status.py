#!/usr/bin/env python3
"""Audit video pack agents against va-agent-swarm study/agents.md columns.

Produces structured JSON used to write agent_capability_status_v1.md.
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_AGENTS_ROOT = _ROOT / "business" / "video" / "agents"
_VA_AGENTS_MD = Path(r"C:\Project\va-agent-swarm\study\agents.md")
_CORPUS_AGENTS_MD = _ROOT / "business" / "video" / "corpus" / "study" / "agents.md"
_OUT_JSON = _ROOT / "business" / "video" / "AGENT_CAPABILITY_AUDIT.json"

CATEGORY_ORDER = [
    "1-ATL",
    "2-Cam",
    "3-Edit",
    "4-Snd",
    "5-Perf",
    "6-Dist",
    "7-Edu",
    "8-AI",
    "9-Meta",
    "10-Sup",
]

CATEGORY_LABELS = {
    "1-ATL": "Above-the-Line",
    "2-Cam": "Camera & Lighting",
    "3-Edit": "Editorial & Color / Design",
    "4-Snd": "Sound & Music",
    "5-Perf": "Performance & Choreography",
    "6-Dist": "Distribution & Marketing",
    "7-Edu": "Education & Domain-Expert",
    "8-AI": "AI-Era Specialists",
    "9-Meta": "Specialist Meta-Agents",
    "10-Sup": "Workflow Support",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def parse_agents_md(text: str) -> list[dict]:
    """Parse markdown tables that include Agent | Responsibility | Knowledge... columns."""
    rows: list[dict] = []
    # Find table rows with bold agent names
    for line in text.splitlines():
        if not line.strip().startswith("|"):
            continue
        # skip separators and headers
        if re.search(r"\|[-:\s|]+\|", line) and "Agent" not in line:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 8:
            continue
        if cells[0] in {"#", ""} or not re.match(r"^\d+$", cells[0] or ""):
            continue
        agent_cell = cells[1]
        m = re.search(r"\*\*([^*]+)\*\*", agent_cell)
        if not m:
            continue
        name = m.group(1).strip()
        # pad cells to expected width
        while len(cells) < 10:
            cells.append("")
        rows.append(
            {
                "va_id": int(cells[0]),
                "va_name": name,
                "responsibility": cells[2],
                "knowledge_distillation_source": cells[3],
                "self_quality_criteria": cells[4],
                "surpass_human_signal": cells[5],
                "accepts_critique_from": cells[6],
                "comments_on": cells[7],
                "tool_access": cells[8] if len(cells) > 8 else "",
                "architecture_pattern": cells[9] if len(cells) > 9 else "",
            }
        )
    return rows


def normalize_name(name: str) -> str:
    s = name.lower()
    s = s.replace("agent", "")
    s = re.sub(r"[^a-z0-9]+", "", s)
    return s


def audit_folder(agent_dir: Path) -> dict:
    spec_json = agent_dir / "agent_spec.json"
    data = json.loads(spec_json.read_text(encoding="utf-8"))
    md_path = agent_dir / "SPEC.md"
    md = _read(md_path) if md_path.is_file() else ""
    sources_dir = agent_dir / "sources"
    source_files = (
        [p for p in sources_dir.rglob("*") if p.is_file()]
        if sources_dir.is_dir()
        else []
    )
    source_content = [
        p
        for p in source_files
        if p.suffix.lower() in {".md", ".txt", ".json", ".svg"}
        and p.name not in {".gitkeep"}
    ]
    provenance = sources_dir / "PROVENANCE.json" if sources_dir.is_dir() else None
    mapping = sources_dir / "MAPPING.md" if sources_dir.is_dir() else None

    def nonempty_files(folder: str) -> list[Path]:
        d = agent_dir / folder
        if not d.is_dir():
            return []
        return [
            p
            for p in d.iterdir()
            if p.is_file() and p.name != ".gitkeep" and p.stat().st_size > 20
        ]

    prompt_files = nonempty_files("prompts")
    rubric_files = nonempty_files("rubrics")
    user_guide = agent_dir / "docs" / "user_guide.md"

    resp = re.search(
        r"##\s+Responsibility\s*\n+(.*?)(?=\n##\s+|\Z)", md, re.S | re.I
    )
    resp_text = resp.group(1).strip() if resp else ""
    has_common_structure = bool(
        re.search(r"Common Structure|Component Reference|Architecture Diagram", md, re.I)
    )
    has_critique_inbox = bool(re.search(r"Critique Inbox|CritiqueMessage", md, re.I))
    has_continuous_learning = bool(
        re.search(r"Continuous Learning|RLAIF|30/60/90", md, re.I)
    )
    has_quality_gate = bool(
        re.search(r"3-layer quality|Spec.?→.?Rubric|self-review|Self-Refine", md, re.I)
    )
    has_handoff = bool(re.search(r"typed handoff|handoff contract|Critique bus", md, re.I))
    has_conflict = bool(
        re.search(r"dispute|JudgeAgent|HiTL|blocker|unresolved", md, re.I)
    )
    has_tools_section = bool(re.search(r"Tool Access|allowed_tools|tool allowlist", md, re.I))
    has_knowledge_section = bool(
        re.search(r"Knowledge Distillation|Knowledge Source|retrieval|RAG", md, re.I)
    )
    has_surpass = bool(
        re.search(r"Surpass-Human|surpass human|beats human|human baseline", md, re.I)
    )
    has_vs_human_claim = bool(
        re.search(r"≥\d+%|beats |outperform|surpass", md, re.I)
    )

    # Executable signal: host-bound tools vs stub
    tools = data.get("allowed_tools") or []
    tools_s = [str(t) for t in tools]
    live_media = any(
        t.startswith("media.") and t not in {"media.stub"} for t in tools_s
    )
    only_stub = tools_s == ["media.stub"] or (not tools_s)

    return {
        "agent_id": data.get("agent_id") or agent_dir.name,
        "va_id": data.get("va_id"),
        "va_name": data.get("va_name") or "",
        "va_category": data.get("va_category") or "unknown",
        "role": data.get("role") or "",
        "status": data.get("status") or "",
        "production_activation_requested": bool(
            data.get("production_activation_requested")
        ),
        "provider": (data.get("model_policy") or {}).get("provider"),
        "network_access": bool(
            (data.get("model_policy") or {}).get("network_access")
        ),
        "allowed_tools": tools_s,
        "prompt_reference": data.get("prompt_reference") or "",
        "rubric_reference": data.get("rubric_reference") or "",
        "critique_edges": data.get("critique_edges") or {},
        "max_refinement_count": data.get("max_refinement_count"),
        "spec_bytes": len(md.encode("utf-8")),
        "responsibility_chars": len(resp_text),
        "responsibility_excerpt": resp_text[:400].replace("\n", " "),
        "has_responsibility_heading": bool(resp),
        "has_common_structure": has_common_structure,
        "has_critique_inbox": has_critique_inbox,
        "has_continuous_learning": has_continuous_learning,
        "has_quality_gate": has_quality_gate,
        "has_handoff": has_handoff,
        "has_conflict_resolution_text": has_conflict,
        "has_tools_section": has_tools_section,
        "has_knowledge_section": has_knowledge_section,
        "has_surpass_section": has_surpass,
        "has_vs_human_claim_text": has_vs_human_claim,
        "source_file_count": len(source_content),
        "has_provenance": bool(provenance and provenance.is_file()),
        "has_mapping": bool(mapping and mapping.is_file()),
        "prompt_file_count": len(prompt_files),
        "rubric_file_count": len(rubric_files),
        "has_user_guide": user_guide.is_file() and user_guide.stat().st_size > 100,
        "execution_mode_inferred": (
            "live_media_tool"
            if live_media
            else "host_orchestrated_stub_or_local"
            if only_stub
            else "tool_allowlist_present"
        ),
        "live_media_tools": live_media,
    }


def score_agent(folder: dict, va_row: dict | None) -> dict:
    """Score Q1–Q11 as yes/partial/no with evidence notes."""
    q: dict[str, dict] = {}

    # Q1 Responsibility in SPEC
    if folder["has_responsibility_heading"] and folder["responsibility_chars"] >= 120:
        q1 = "yes"
        n1 = f"SPEC has ## Responsibility ({folder['responsibility_chars']} chars)."
    elif folder["has_responsibility_heading"]:
        q1 = "partial"
        n1 = "Responsibility heading present but thin; expand against agents.md."
    else:
        q1 = "no"
        n1 = "Missing ## Responsibility heading."
    if va_row and va_row.get("responsibility"):
        n1 += f" VA source responsibility: {va_row['responsibility'][:160]}"
    q["q1_responsibility"] = {"status": q1, "notes": n1}

    # Q2 Plan to distill professional knowledge
    if folder["has_knowledge_section"] or (va_row and va_row.get("knowledge_distillation_source")):
        if folder["source_file_count"] > 5 and folder["has_knowledge_section"]:
            q2 = "yes"
        else:
            q2 = "partial"
        n2 = "Knowledge distillation planned in agents.md / SPEC."
        if va_row:
            n2 += f" Planned sources: {va_row.get('knowledge_distillation_source','')[:180]}"
    else:
        q2 = "no"
        n2 = "No clear knowledge distillation plan found."
    q["q2_knowledge_distill_plan"] = {"status": q2, "notes": n2}

    # Q3 Sources exist or known how to get
    if folder["source_file_count"] >= 8 and folder["has_provenance"]:
        q3 = "yes"
        n3 = f"{folder['source_file_count']} source files + PROVENANCE."
    elif folder["source_file_count"] > 0 or folder["has_mapping"]:
        q3 = "partial"
        n3 = f"{folder['source_file_count']} local source files; acquisition path may still be design-only (URLs/corpora not fully licensed)."
    else:
        q3 = "no"
        n3 = "No local distill sources packaged."
    if va_row:
        n3 += f" VA listed: {va_row.get('knowledge_distillation_source','')[:140]}"
    q["q3_sources_available"] = {"status": q3, "notes": n3}

    # Q4 Self-evaluation methods collected
    has_rubric_ref = bool(folder["rubric_reference"])
    if folder["rubric_file_count"] > 0 and folder["has_quality_gate"]:
        q4 = "yes"
        n4 = "Rubric files + quality-gate text present."
    elif has_rubric_ref or folder["has_quality_gate"] or (va_row and va_row.get("self_quality_criteria")):
        q4 = "partial"
        n4 = "Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing."
        if va_row:
            n4 += f" VA criteria: {va_row.get('self_quality_criteria','')[:160]}"
    else:
        q4 = "no"
        n4 = "No self-evaluation content found."
    q["q4_self_eval"] = {"status": q4, "notes": n4}

    # Q5 Surpass human yet?
    # Design may claim surpass signals; runtime has not proven this.
    if folder["live_media_tools"] and folder["production_activation_requested"]:
        # still not proven surpass
        q5 = "no"
        n5 = "Has live-tool path but no measured human-parity benchmark results in host. Design may state aspirational surpass signals only."
    else:
        q5 = "no"
        n5 = "Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes."
    if va_row and va_row.get("surpass_human_signal"):
        n5 += f" VA aspirational signal: {va_row['surpass_human_signal'][:160]}"
    q["q5_surpass_human"] = {"status": q5, "notes": n5}

    # Q6 How they execute
    if folder["live_media_tools"]:
        q6 = "partial"
        n6 = f"Host may invoke media tools {folder['allowed_tools']}; prompt/rubric refs exist but prompts/ are empty stubs for most agents. Not a free-running coding plan agent."
    elif folder["prompt_file_count"] > 0:
        q6 = "partial"
        n6 = "Defined prompt files present; execution still host-orchestrated."
    else:
        q6 = "partial"
        n6 = (
            f"Host-orchestrated / graph-driven. prompt_reference={folder['prompt_reference'] or '—'}; "
            f"provider={folder['provider']}; tools={folder['allowed_tools'] or ['(none/stub)']}. "
            "No per-agent autonomous coding-plan runner installed by default."
        )
    if va_row and va_row.get("architecture_pattern"):
        n6 += f" VA architecture: {va_row['architecture_pattern'][:140]}"
    q["q6_execution"] = {"status": q6, "notes": n6}

    # Q7 Skills / plugins / harness for themselves
    # Pack has shared special_skills, not per-agent private skill installs
    if folder["prompt_file_count"] > 0 or folder["rubric_file_count"] > 0:
        q7 = "partial"
        n7 = "Local prompts/rubrics folder exists; shared pack special_skills may apply. No dedicated per-agent plugin install harness proven."
    else:
        q7 = "partial"
        n7 = "Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present."
    q["q7_skills_plugins"] = {"status": q7, "notes": n7}

    # Q8 Improve themselves
    if folder["has_continuous_learning"] and folder["max_refinement_count"]:
        q8 = "partial"
        n8 = f"SPEC describes continuous learning; max_refinement_count={folder['max_refinement_count']}. Host RLAIF loop not fully productized per agent."
    elif folder["has_continuous_learning"] or folder["max_refinement_count"]:
        q8 = "partial"
        n8 = "Improvement described in SPEC or refinement budget present; closed-loop self-improvement not fully operational."
    else:
        q8 = "no"
        n8 = "No self-improvement mechanism found."
    q["q8_self_improve"] = {"status": q8, "notes": n8}

    # Q9 Know how to collect/research info to improve
    if folder["has_knowledge_section"] and folder["source_file_count"] > 0:
        q9 = "partial"
        n9 = "Sources + distillation text give a research path; automated research→eval→promote loop incomplete."
    else:
        q9 = "partial"
        n9 = "VA table lists knowledge sources; operational research-to-improvement pipeline incomplete."
    q["q9_research_for_improve"] = {"status": q9, "notes": n9}

    # Q10 Instruction to/from other agents
    edges = folder["critique_edges"] or {}
    has_edges = bool(edges.get("inputs") or edges.get("outputs"))
    if has_edges and folder["has_handoff"] and folder["has_critique_inbox"]:
        q10 = "partial"
        n10 = f"critique_edges + handoff/critique design present: {json.dumps(edges)}. Runtime multi-agent instruction bus partially implemented via host graphs."
    elif has_edges or folder["has_handoff"]:
        q10 = "partial"
        n10 = f"Some collab design/edges present: {json.dumps(edges)}. Full send/receive instruction protocol not fully live for all agents."
    else:
        q10 = "no"
        n10 = "No collab instruction paths found."
    if va_row:
        n10 += f" VA accepts from: {va_row.get('accepts_critique_from','')[:100]}; comments on: {va_row.get('comments_on','')[:100]}"
    q["q10_collab_instructions"] = {"status": q10, "notes": n10}

    # Q11 Conflict resolve + confirm
    if folder["has_conflict_resolution_text"] and folder["has_critique_inbox"]:
        q11 = "partial"
        n11 = "SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent."
    else:
        q11 = "partial"
        n11 = "Conflict resolution mostly design-level (JudgeAgent / HiTL). Per-agent auto-resolve+confirm incomplete."
    q["q11_conflict_resolve"] = {"status": q11, "notes": n11}

    # Aggregate deficiency suggestions
    suggestions: list[str] = []
    if q1 != "yes":
        suggestions.append(
            "Rewrite ## Responsibility to a single operator-facing paragraph + measurable owns/does-not-own boundary matching agents.md."
        )
    if folder["prompt_file_count"] == 0:
        suggestions.append(
            f"Materialize executable prompt under prompts/ implementing {folder['prompt_reference'] or 'prompt_reference'} (system + task + output schema)."
        )
    if folder["rubric_file_count"] == 0:
        suggestions.append(
            f"Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as {folder['rubric_reference'] or 'rubric_reference'}."
        )
    if folder["source_file_count"] < 5:
        suggestions.append(
            "Expand sources/ with licensed excerpts + acquisition SOP (URL, license, refresh cadence) mapped in MAPPING.md."
        )
    if q5 == "no":
        suggestions.append(
            "Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass."
        )
    if not folder["live_media_tools"] and not folder["allowed_tools"]:
        suggestions.append(
            "Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials."
        )
    if q8 in {"partial", "no"}:
        suggestions.append(
            "Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle."
        )
    if q10 in {"partial", "no"}:
        suggestions.append(
            "Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md."
        )
    if q11 in {"partial", "no"}:
        suggestions.append(
            "Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers."
        )
    if not folder["has_user_guide"]:
        suggestions.append("Keep docs/user_guide.md aligned with SPEC responsibility and operator runbook.")

    yes_count = sum(1 for v in q.values() if v["status"] == "yes")
    partial_count = sum(1 for v in q.values() if v["status"] == "partial")
    no_count = sum(1 for v in q.values() if v["status"] == "no")

    return {
        "questions": q,
        "suggestions": suggestions,
        "score": {
            "yes": yes_count,
            "partial": partial_count,
            "no": no_count,
            "maturity_0_to_11": round(yes_count + 0.5 * partial_count, 2),
        },
    }


def main() -> int:
    agents_md_path = _VA_AGENTS_MD if _VA_AGENTS_MD.is_file() else _CORPUS_AGENTS_MD
    if not agents_md_path.is_file():
        print("agents.md not found", file=sys.stderr)
        return 1

    va_rows = parse_agents_md(_read(agents_md_path))
    by_va_id = {r["va_id"]: r for r in va_rows}
    by_name = {normalize_name(r["va_name"]): r for r in va_rows}

    agents: list[dict] = []
    for agent_dir in sorted(_AGENTS_ROOT.iterdir()):
        if not (agent_dir / "agent_spec.json").is_file():
            continue
        folder = audit_folder(agent_dir)
        va_row = None
        if isinstance(folder["va_id"], int):
            va_row = by_va_id.get(folder["va_id"])
        if va_row is None and folder["va_name"]:
            va_row = by_name.get(normalize_name(folder["va_name"]))
        scored = score_agent(folder, va_row)
        agents.append(
            {
                **folder,
                "va_table": va_row,
                **scored,
            }
        )

    by_cat: dict[str, list] = defaultdict(list)
    for a in agents:
        by_cat[a["va_category"]].append(a)

    payload = {
        "schema_version": "1.0",
        "agents_md_source": str(agents_md_path),
        "pack_root": "business/video/agents",
        "agent_count": len(agents),
        "va_table_row_count": len(va_rows),
        "status_legend": {
            "yes": "Present and usable in pack/host at least at design+local artifact level",
            "partial": "Designed or partially packaged; runtime/eval/tools incomplete",
            "no": "Missing or explicitly not achieved",
        },
        "questions": {
            "q1_responsibility": "Ensure each agent knows Responsibility and it is well defined in SPEC.md",
            "q2_knowledge_distill_plan": "Plan to distill professional knowledge",
            "q3_sources_available": "Sources to distill exist or agent knows how to get them",
            "q4_self_eval": "Self-evaluation methods and related content collected",
            "q5_surpass_human": "Current implementation surpasses human",
            "q6_execution": "How they execute jobs (coding plan / LLM / prompt / other)",
            "q7_skills_plugins": "Installed skills/plugins/harness for themselves",
            "q8_self_improve": "Mechanism to improve themselves",
            "q9_research_for_improve": "How to collect/research info to improve themselves",
            "q10_collab_instructions": "Get/send instructions to other agents for collaboration",
            "q11_conflict_resolve": "Resolve conflicts themselves and confirm",
        },
        "global_summary": {
            "avg_maturity": round(
                sum(a["score"]["maturity_0_to_11"] for a in agents) / max(len(agents), 1),
                2,
            ),
            "agents_with_prompt_files": sum(1 for a in agents if a["prompt_file_count"] > 0),
            "agents_with_rubric_files": sum(1 for a in agents if a["rubric_file_count"] > 0),
            "agents_with_live_media_tools": sum(1 for a in agents if a["live_media_tools"]),
            "agents_production_activation_requested": sum(
                1 for a in agents if a["production_activation_requested"]
            ),
            "agents_responsibility_strong": sum(
                1
                for a in agents
                if a["questions"]["q1_responsibility"]["status"] == "yes"
            ),
            "status_counts": {
                "yes": sum(
                    1
                    for a in agents
                    for v in a["questions"].values()
                    if v["status"] == "yes"
                ),
                "partial": sum(
                    1
                    for a in agents
                    for v in a["questions"].values()
                    if v["status"] == "partial"
                ),
                "no": sum(
                    1
                    for a in agents
                    for v in a["questions"].values()
                    if v["status"] == "no"
                ),
            },
        },
        "groups": {
            cat: {
                "label": CATEGORY_LABELS.get(cat, cat),
                "count": len(by_cat[cat]),
                "avg_maturity": round(
                    sum(a["score"]["maturity_0_to_11"] for a in by_cat[cat])
                    / max(len(by_cat[cat]), 1),
                    2,
                ),
                "agents": by_cat[cat],
            }
            for cat in CATEGORY_ORDER
            if cat in by_cat
        },
        "agents": agents,
    }

    _OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {_OUT_JSON} agents={len(agents)} va_rows={len(va_rows)}")
    print("global", json.dumps(payload["global_summary"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
