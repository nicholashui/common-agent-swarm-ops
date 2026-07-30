#!/usr/bin/env python3
"""Materialize improvement-plan artifacts for each video pack agent.

Implements Wave A (and partial B/C scaffolds) from agent_improvement_plan_v1.md:

- prompts/<prompt_reference>.md
- rubrics/<rubric_reference>.json
- skills/SKILL.md + integration.json + bindings.json
- sources/DISTILLATION_PLAN.json, SOURCE_CATALOG.json, ACQUIRE.md
- evals/agents/<id>/golden.json (under business/video/evals/)
- agent_spec.json enrichments (does_not_own, improvement metadata)
- optional critique_edges expansion from agents.md Accepts/Comments columns

Research patterns encoded (not downloaded remote code):
- Anthropic Agent Skills (SKILL.md frontmatter + instructions) — agentskills.io / anthropics/skills
- LangGraph / CrewAI / AutoGen agentic graphs — agents.md architecture column
- Self-Refine, Reflexion, ReAct, Constitutional AI / RLAIF, LLM-as-Judge, multi-agent debate
- In-pack agent_loop_v3 special skill binding for meta spine agents
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_AGENTS = _ROOT / "business" / "video" / "agents"
_EVALS = _ROOT / "business" / "video" / "evals" / "agents"
_VA_AGENTS_MD = Path(r"C:\Project\va-agent-swarm\study\agents.md")
_CORPUS_AGENTS_MD = _ROOT / "business" / "video" / "corpus" / "study" / "agents.md"
_RESOURCES_OUT = _ROOT / "business" / "video" / "IMPROVEMENT_RESEARCH_SOURCES_v1.md"
_REPORT_OUT = _ROOT / "business" / "video" / "IMPROVEMENT_APPLY_REPORT_v1.json"

# Patterns referenced from agents.md §11 + improvement plan research
RESEARCH_PATTERNS = {
    "Self-Refine": "Madaan et al. — iterative critique/refine loop with rubric",
    "Reflexion": "Shinn et al. — verbal RL + episodic memory of failures",
    "ReAct": "Yao et al. — reason then act with tools",
    "Constitutional AI": "Bai et al. / RLAIF — principles as constitution for self-check",
    "LLM-as-Judge": "Zheng et al. — structured rubric scoring",
    "Multi-agent debate": "Du et al. — peer debate for hard disputes",
    "Agentic Graph": "LangGraph/CrewAI/AutoGen style deterministic DAG + handoffs",
    "Agent Skills": "Anthropic Agent Skills standard — SKILL.md frontmatter + harness",
    "agent_loop_v3": "In-pack special skill — orchestrator/planner/memory/judge loop",
}

SPINE_SKILL_BINDINGS = {
    "video.orchestrator": ["agent_loop_v3", "complex_problem_solution_process_model"],
    "video.planner": ["agent_loop_v3", "thinking_model"],
    "video.memory": ["agent_loop_v3", "agentic_rag"],
    "video.judge": ["agent_loop_v3"],
    "video.router": ["knowledge_router_agent", "intent_analysis_agent"],
    "video.critic": ["optimization_agent"],
    "video.gatekeeper": ["llm_usage"],
    "video.research": ["research_agent"],
    "video.webresearch": ["research_agent"],
    "video.benchmarkresearch": ["research_agent"],
    "video.screenwriter": ["screenwriter_strategic_goal_achievement_agent"],
    "video.promptengineer": ["llm_usage", "optimization_agent"],
    "video.promptoptimizer": ["optimization_agent", "llm_usage"],
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def parse_agents_md(text: str) -> dict[int, dict]:
    rows: dict[int, dict] = {}
    for line in text.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 8 or not re.match(r"^\d+$", cells[0] or ""):
            continue
        m = re.search(r"\*\*([^*]+)\*\*", cells[1])
        if not m:
            continue
        while len(cells) < 10:
            cells.append("")
        va_id = int(cells[0])
        rows[va_id] = {
            "va_id": va_id,
            "va_name": m.group(1).strip(),
            "responsibility": cells[2],
            "knowledge_distillation_source": cells[3],
            "self_quality_criteria": cells[4],
            "surpass_human_signal": cells[5],
            "accepts_critique_from": cells[6],
            "comments_on": cells[7],
            "tool_access": cells[8] if len(cells) > 8 else "",
            "architecture_pattern": cells[9] if len(cells) > 9 else "",
        }
    return rows


def normalize_name(name: str) -> str:
    s = name.lower()
    s = s.replace("agent", "")
    s = re.sub(r"[^a-z0-9]+", "", s)
    return s


def build_name_to_id(agents_root: Path) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for d in agents_root.iterdir():
        if not d.is_dir():
            continue
        spec_path = d / "agent_spec.json"
        if not spec_path.is_file():
            continue
        try:
            spec = json.loads(spec_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        aid = str(spec.get("agent_id") or d.name)
        mapping[normalize_name(aid.split(".")[-1])] = aid
        if spec.get("va_name"):
            mapping[normalize_name(str(spec["va_name"]))] = aid
        # common aliases
        role = str(spec.get("role") or "")
        role_base = role.split("(")[0].strip()
        if role_base:
            mapping[normalize_name(role_base)] = aid
    # explicit aliases from agents.md wording
    aliases = {
        "dop": "video.cinematographer",
        "producer": "video.producer",
        "ep": "video.producer",
        "audiencesim": "video.audiencesim",
        "vfxsup": "video.vfxsupervisor",
        "vfxsupervisor": "video.vfxsupervisor",
        "scriptwriter": "video.screenwriter",
        "dramaturg": "video.screenwriter",
        "storyeditor": "video.standardseditor",
        "brandmanager": "video.brand",
        "aigenerator": "video.promptengineer",
        "compositor": "video.vfxsupervisor",
        "mixer": "video.soundmixer",
        "consent": "video.legal",
        "legalconsent": "video.legal",
        "networknotes": "video.comms",
        "dialogue": "video.screenwriter",
        "consistency": "video.aiqaconsistency",
        "gaffer": "video.cinematographer",
        "safety": "video.safetyredteam",
    }
    for k, v in aliases.items():
        mapping.setdefault(k, v)
    return mapping


def extract_peer_ids(text: str, name_to_id: dict[str, str], self_id: str) -> list[str]:
    if not text:
        return []
    # split on commas / semicolons / "and" / em dash roles
    chunks = re.split(r"[,;/]|\band\b|\bw/\b|\—|\–", text)
    found: list[str] = []
    seen: set[str] = set()
    for chunk in chunks:
        # pull Agent-like tokens
        for token in re.findall(r"[A-Za-z][A-Za-z0-9&/ \-]{1,40}", chunk):
            key = normalize_name(token)
            if not key or key in {"all", "allagents", "hitl", "json", "critique", "bus"}:
                continue
            if key.startswith("all"):
                continue
            aid = name_to_id.get(key)
            if not aid:
                # try stripping trailing role words
                for suffix in ("agent", "agents"):
                    if key.endswith(suffix) and len(key) > len(suffix):
                        aid = name_to_id.get(key[: -len(suffix)])
            if aid and aid != self_id and aid not in seen:
                seen.add(aid)
                found.append(aid)
    return found


def detect_patterns(arch: str) -> list[str]:
    arch_l = (arch or "").lower()
    hits: list[str] = []
    checks = [
        ("self-refine", "Self-Refine"),
        ("self refine", "Self-Refine"),
        ("reflexion", "Reflexion"),
        ("react", "ReAct"),
        ("constitutional", "Constitutional AI"),
        ("rlaif", "Constitutional AI"),
        ("llm-as-judge", "LLM-as-Judge"),
        ("llm as judge", "LLM-as-Judge"),
        ("debate", "Multi-agent debate"),
        ("langgraph", "Agentic Graph"),
        ("crewai", "Agentic Graph"),
        ("autogen", "Agentic Graph"),
        ("agentic graph", "Agentic Graph"),
        ("dag", "Agentic Graph"),
    ]
    for needle, label in checks:
        if needle in arch_l and label not in hits:
            hits.append(label)
    if not hits:
        hits.append("Self-Refine")
        hits.append("Agent Skills")
    if "Agent Skills" not in hits:
        hits.append("Agent Skills")
    return hits


def parse_criteria_dimensions(criteria: str) -> list[dict]:
    """Split self-quality criteria into weighted dimensions."""
    raw = criteria or "Output meets role craft quality; schema valid; no policy violation"
    parts = [p.strip() for p in re.split(r"[;|]", raw) if p.strip()]
    if not parts:
        parts = [raw]
    # cap dimensions
    parts = parts[:6]
    weight = round(1.0 / len(parts), 4)
    dims = []
    for i, p in enumerate(parts):
        # extract threshold if present
        thr = None
        m = re.search(r"(≥|>=|≤|<=|<|>)\s*([0-9]+(?:\.[0-9]+)?%?)", p)
        if m:
            thr = f"{m.group(1)}{m.group(2)}"
        dims.append(
            {
                "id": f"d{i+1}",
                "name": p[:80],
                "description": p,
                "weight": weight if i < len(parts) - 1 else round(1.0 - weight * (len(parts) - 1), 4),
                "threshold_hint": thr,
                "score_min": 0,
                "score_max": 100,
            }
        )
    return dims


def does_not_own_from_responsibility(resp: str, role: str) -> list[str]:
    base = [
        "Host credential storage",
        "Silent production activation without fail-closed gates",
        "Inventing action references for irreversible mutations",
        "Owning other agents' exclusive craft outputs without handoff contract",
    ]
    # light role-specific
    r = (role + " " + resp).lower()
    if "orchestr" in r:
        base.append("Per-shot craft generation (delegates to craft agents)")
    if "judge" in r:
        base.append("Primary content generation")
    if "memory" in r:
        base.append("Final creative approval")
    if "router" in r:
        base.append("Long-running multi-step craft execution")
    return base


def write_prompt(path: Path, agent: dict, va: dict | None, patterns: list[str]) -> None:
    aid = agent["agent_id"]
    role = agent.get("role") or (va or {}).get("va_name") or aid
    resp = (va or {}).get("responsibility") or agent.get("role") or "Execute pack role faithfully."
    arch = (va or {}).get("architecture_pattern") or "Self-Refine + host graph"
    tools = (va or {}).get("tool_access") or ", ".join(agent.get("allowed_tools") or []) or "host allowlist only"
    criteria = (va or {}).get("self_quality_criteria") or "Meet L1 schema and L2 rubric >= 85"
    accepts = (va or {}).get("accepts_critique_from") or "configured critique_edges.inputs"
    comments = (va or {}).get("comments_on") or "configured critique_edges.outputs"
    knowledge = (va or {}).get("knowledge_distillation_source") or "pack sources/ excerpts"
    max_ref = agent.get("max_refinement_count") or 3
    does_not = does_not_own_from_responsibility(resp, role)

    body = f"""# Prompt — `{agent.get('prompt_reference') or aid}`

> Materialized by `scripts/business/improve_agents_from_plan_v1.py` for improvement plan Wave A.
> Patterns: {', '.join(patterns)}
> Research: Anthropic Agent Skills; Self-Refine; ReAct; LLM-as-Judge; LangGraph-style handoffs (see IMPROVEMENT_RESEARCH_SOURCES_v1.md).

## System

You are **{role}** (`{aid}`), a pack agent in the video domain swarm.

### Responsibility (owns)
{resp}

### Does not own
{chr(10).join(f'- {x}' for x in does_not)}

### Operating principles
1. Stay inside responsibility; use typed handoffs for everything else.
2. Prefer evidence and pack sources over invention.
3. Fail closed on missing credentials, missing tools, or irreversible actions without HiTL.
4. Emit structured artifacts that validate against L1 schema before self-scoring.
5. Accept peer critique; refine at most {max_ref} times; escalate blockers.

### Architecture pattern
{arch}

### Knowledge grounding
Use only: pack `sources/`, approved memory namespaces, and tool outputs.
Primary distillation sources (design): {knowledge}

## Developer

### Tools (allowlist intent)
Design tool surface: {tools}
Runtime: only host-registered `allowed_tools` from agent_spec.json. Never invent credentials.

### Collaboration
- Accepts critique from: {accepts}
- May comment on: {comments}
- Critique / instruction messages must include: from_id, to_id, severity (blocker|major|minor|nit), artifact_ref, claim, evidence_refs, correlation_id.

### Self-evaluation loop (before final emit)
1. **L1 Spec** — structural/schema/format validators must pass 100%.
2. **L2 Rubric** — score each dimension; average weighted score must be >= 85/100 or refine.
3. **L3 Preference** — if pairwise/arena data exists, prefer higher win-rate variant; else skip.
Criteria (design): {criteria}

### Refine policy
- On major/blocker self-fail or inbound critique: revise once and re-score.
- After {max_ref} failed refinements: emit `status=needs_hitl` with unresolved items.
- Never silently drop blockers.

## Task

You will receive a host task envelope:

```json
{{
  "agent_id": "{aid}",
  "correlation_id": "string",
  "goal": "string",
  "inputs": {{}},
  "constraints": {{}},
  "prior_critiques": []
}}
```

Execute the craft step for **{role}**. Use the architecture pattern above (reason → optional tool calls → self-review → emit).

## Output schema (required)

```json
{{
  "agent_id": "{aid}",
  "correlation_id": "string",
  "status": "ok | needs_refine | needs_hitl | failed",
  "artifact": {{
    "type": "string",
    "payload": {{}},
    "summary": "string"
  }},
  "l1": {{ "passed": true, "checks": [] }},
  "l2": {{ "score": 0, "dimensions": [], "passed": false }},
  "critiques_emitted": [],
  "handoffs": [],
  "evidence_refs": [],
  "refinement_count": 0,
  "notes": "string"
}}
```

## Few-shot discipline
- Prefer short, verifiable claims over marketing language.
- Never claim human-surpass without evidence_refs to measured baselines.
- Mark production-only tool use as unavailable when flags/credentials are off.
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def write_rubric(path: Path, agent: dict, va: dict | None) -> None:
    criteria = (va or {}).get("self_quality_criteria") or "Craft quality; schema compliance; policy safety"
    dims = parse_criteria_dimensions(criteria)
    surpass = (va or {}).get("surpass_human_signal") or ""
    rubric = {
        "schema_version": "1.0",
        "rubric_id": agent.get("rubric_reference") or f"{agent['agent_id']}.rubric.v1",
        "agent_id": agent["agent_id"],
        "title": f"L2 craft rubric for {agent.get('va_name') or agent['agent_id']}",
        "pass_threshold": 85,
        "max_score": 100,
        "layers": {
            "L1_spec": {
                "description": "Machine validators: schema, format, required fields, policy allowlist",
                "must_pass": True,
            },
            "L2_rubric": {
                "description": "LLM-as-Judge or scorer against dimensions below",
                "pass_threshold": 85,
                "dimensions": dims,
            },
            "L3_preference": {
                "description": "Optional pairwise/arena preference when human or synthetic preference data exists",
                "surpass_signal_design": surpass,
                "note": "Do not claim surpass until measured baseline exists",
            },
        },
        "refine_policy": {
            "max_refinement_count": agent.get("max_refinement_count") or 3,
            "on_fail": "refine_or_escalate_hitl",
        },
        "sources": {
            "agents_md_self_quality_criteria": criteria,
            "research": ["LLM-as-Judge", "Self-Refine", "Constitutional AI"],
        },
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rubric, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_skill(
    agent_dir: Path,
    agent: dict,
    va: dict | None,
    patterns: list[str],
    bindings: list[str],
) -> None:
    skills = agent_dir / "skills"
    skills.mkdir(parents=True, exist_ok=True)
    aid = agent["agent_id"]
    name = aid.replace(".", "-")
    resp = (va or {}).get("responsibility") or agent.get("role") or aid
    skill_md = f"""---
name: {name}
description: Role harness for {aid} — {resp[:160]}
version: 1.0.0
agent_id: {aid}
---

# Skill — `{aid}`

## When to use
Load this skill when the host routes a task to `{aid}` or when composing a swarm step that requires this craft role.

## Instructions
1. Load prompt `{agent.get('prompt_reference')}` from `../prompts/`.
2. Load rubric `{agent.get('rubric_reference')}` from `../rubrics/`.
3. Ground only on `../sources/` and host memory namespaces.
4. Execute architecture patterns: {', '.join(patterns)}.
5. Emit the JSON output schema from the prompt; fail closed without tools/credentials.
6. On critique: refine ≤ max_refinement_count then escalate.

## Harness
- **Runner kind:** graph-node | tool-loop (host decides)
- **Entry:** pack agent `{aid}` via host agent runner
- **Timeouts:** host default unless agent_spec budget_policy overrides
- **Network:** only if model_policy.network_access and production flags allow

## Bindings
Shared pack special_skills (optional): {', '.join(bindings) if bindings else '(none required)'}

## Research patterns
{chr(10).join(f'- **{p}**: {RESEARCH_PATTERNS.get(p, p)}' for p in patterns)}

## Tests
- Offline golden: `business/video/evals/agents/{aid}/golden.json`
- Must not require live network for L1 pass when tools are mocked.
"""
    (skills / "SKILL.md").write_text(skill_md, encoding="utf-8")
    integration = {
        "skill_id": name,
        "agent_id": aid,
        "kind": "pack_agent_harness",
        "status": "scaffolded",
        "prompt_reference": agent.get("prompt_reference"),
        "rubric_reference": agent.get("rubric_reference"),
        "patterns": patterns,
        "bindings": bindings,
        "entrypoint": {
            "type": "host_agent_runner",
            "agent_id": aid,
        },
        "fail_closed": True,
        "generated_by": "improve_agents_from_plan_v1.py",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    (skills / "integration.json").write_text(
        json.dumps(integration, indent=2) + "\n", encoding="utf-8"
    )
    (skills / "bindings.json").write_text(
        json.dumps(
            {
                "agent_id": aid,
                "special_skills": [
                    {"skill_id": s, "path": f"business/video/special_skills/{s}/"}
                    for s in bindings
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def write_source_artifacts(agent_dir: Path, agent: dict, va: dict | None) -> None:
    sources = agent_dir / "sources"
    sources.mkdir(parents=True, exist_ok=True)
    knowledge = (va or {}).get("knowledge_distillation_source") or "pack corpus study excerpts"
    # split sources roughly on semicolons / commas
    parts = [p.strip() for p in re.split(r"[;]", knowledge) if p.strip()]
    if not parts:
        parts = [knowledge]
    catalog_entries = []
    for i, part in enumerate(parts):
        # further split long comma lists carefully — keep part as class
        catalog_entries.append(
            {
                "id": f"src_{i+1}",
                "title": part[:120],
                "description": part,
                "license_class": "unknown_review_required",
                "acquisition_method": "manual_or_licensed_api",
                "local_path_hint": "sources/excerpts/ or sources/study/",
                "refresh_sla_days": 90,
                "owner": agent["agent_id"],
                "status": "planned_or_partial",
            }
        )
    catalog = {
        "schema_version": "1.0",
        "agent_id": agent["agent_id"],
        "sources": catalog_entries,
        "note": "Legal review required before treating external corpora as production grounding.",
    }
    (sources / "SOURCE_CATALOG.json").write_text(
        json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    plan = {
        "schema_version": "1.0",
        "agent_id": agent["agent_id"],
        "plan_id": f"{agent['agent_id']}.distill.v1",
        "inputs": [e["id"] for e in catalog_entries],
        "extractors": ["markdown_excerpt", "structured_table_row"],
        "chunk_policy": {"max_chars": 2000, "overlap": 200},
        "owner": agent["agent_id"],
        "cadence": "quarterly",
        "promotion_criteria": [
            "source license approved or fixture-only",
            "excerpt hash recorded in PROVENANCE",
            "golden eval still passes L1",
        ],
        "memory_namespace": f"pack.video.{agent['agent_id']}",
        "next_review_at": "2026-10-01",
    }
    (sources / "DISTILLATION_PLAN.json").write_text(
        json.dumps(plan, indent=2) + "\n", encoding="utf-8"
    )
    acquire = f"""# Source acquisition runbook — `{agent['agent_id']}`

## Purpose
Obtain or refresh knowledge distillation sources listed in `SOURCE_CATALOG.json`.

## Rules
1. **No secrets in git.** API keys only via environment / secret manager.
2. Prefer **licensed / consented / public domain** material.
3. If license unknown: store only short fair-use design excerpts under `excerpts/` and mark `license_class=unknown_review_required`.
4. Update `PROVENANCE.json` with URL, retrieved_at, hash, and license note.
5. Re-run offline golden eval after material changes.

## Design sources (from agents.md)
{knowledge}

## Steps
1. Open `SOURCE_CATALOG.json`.
2. For each source with status planned_or_partial, document acquisition method.
3. Place fixtures under `excerpts/` or `study/`.
4. Update `MAPPING.md` with path mapping.
5. Set `next_review_at` in `DISTILLATION_PLAN.json`.
"""
    (sources / "ACQUIRE.md").write_text(acquire, encoding="utf-8")


def write_golden_eval(agent: dict, va: dict | None) -> None:
    aid = agent["agent_id"]
    out_dir = _EVALS / aid
    out_dir.mkdir(parents=True, exist_ok=True)
    golden = {
        "schema_version": "1.0",
        "agent_id": aid,
        "name": f"{aid} offline golden scaffold",
        "mode": "offline_mock",
        "input": {
            "goal": f"Execute a minimal valid task for {(va or {}).get('va_name') or aid}",
            "inputs": {"brief": "synthetic offline fixture — do not call live providers"},
            "constraints": {"network": False, "production": False},
        },
        "expect": {
            "output_status_in": ["ok", "needs_refine", "needs_hitl"],
            "l1_passed": True,
            "artifact_required": True,
        },
        "rubric_reference": agent.get("rubric_reference"),
        "prompt_reference": agent.get("prompt_reference"),
        "notes": "Scaffold from improvement plan Wave A; expand with real fixtures per craft.",
    }
    (out_dir / "golden.json").write_text(
        json.dumps(golden, indent=2) + "\n", encoding="utf-8"
    )


def enrich_agent_spec(
    spec_path: Path,
    agent: dict,
    va: dict | None,
    name_to_id: dict[str, str],
    *,
    expand_edges: bool,
) -> dict:
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    resp = (va or {}).get("responsibility") or ""
    role = str(spec.get("role") or "")
    spec["does_not_own"] = does_not_own_from_responsibility(resp, role)
    if expand_edges and va:
        inputs = extract_peer_ids(va.get("accepts_critique_from") or "", name_to_id, agent["agent_id"])
        outputs = extract_peer_ids(va.get("comments_on") or "", name_to_id, agent["agent_id"])
        edges = spec.get("critique_edges") or {"inputs": [], "outputs": []}
        # merge unique preserving existing
        def merge(a: list, b: list) -> list:
            seen = set(a)
            out = list(a)
            for x in b:
                if x not in seen:
                    seen.add(x)
                    out.append(x)
            return out

        edges["inputs"] = merge(list(edges.get("inputs") or []), inputs)
        edges["outputs"] = merge(list(edges.get("outputs") or []), outputs)
        # keep at least critic/judge defaults if empty
        if not edges["inputs"]:
            edges["inputs"] = ["video.critic"]
        if not edges["outputs"]:
            edges["outputs"] = ["video.judge"]
        spec["critique_edges"] = edges
    spec["improvement"] = {
        "plan": "agent_improvement_plan_v1.md",
        "wave": "A_artifacts",
        "prompt_materialized": True,
        "rubric_materialized": True,
        "skills_harness": True,
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "research_doc": "business/video/IMPROVEMENT_RESEARCH_SOURCES_v1.md",
    }
    # ensure refinement default
    if not spec.get("max_refinement_count"):
        spec["max_refinement_count"] = 3
    spec_path.write_text(json.dumps(spec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return spec


def write_research_doc() -> None:
    body = f"""# Improvement research sources v1

Generated: {datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}

This document records **patterns and references** used by
`scripts/business/improve_agents_from_plan_v1.py` to materialize prompts, rubrics,
skills, and distillation scaffolds for video pack agents.

> No third-party code was downloaded into the runtime path. Patterns are encoded
> as pack-local markdown/JSON artifacts under each agent folder.

## Primary design authority (local)

| Source | Use |
|--------|-----|
| `va-agent-swarm/study/agents.md` | Responsibility, knowledge sources, self-quality, surpass signals, critique topology, tools, architecture |
| `va-agent-swarm/study/agents.md` §11 Common Structure | Identity, handoffs, L1/L2/L3 gates, continuous learning, HiTL |
| `agent_capability_status_v1.md` | Gap diagnosis per agent |
| `agent_improvement_plan_v1.md` | Full-mark action lists and platform workstreams |
| `business/video/special_skills/` | Existing pack skills (agent_loop_v3, research_agent, etc.) |

## External research patterns (public literature / standards)

| Pattern | Why used | Typical mapping |
|---------|----------|-----------------|
| **Anthropic Agent Skills** ([agentskills.io](https://agentskills.io), anthropics/skills on GitHub) | Standard for `SKILL.md` frontmatter + harness folders | Every agent `skills/SKILL.md` |
| **Self-Refine** (Madaan et al.) | Iterative self-critique against rubric | Default refine loop in prompts |
| **Reflexion** (Shinn et al.) | Verbal RL + memory of failures | Planner / meta agents |
| **ReAct** (Yao et al.) | Reason → tool act loop | Tool-using craft agents |
| **Constitutional AI / RLAIF** (Bai et al.) | Principles as safety/craft constitution | Safety, drone, continuity-style agents |
| **LLM-as-Judge** (Zheng et al.) | Structured multi-dimension scoring | All `rubrics/*.json` L2 layer |
| **Multi-agent debate** (Du et al.) | Dispute resolution before HiTL | Judge + conflict path |
| **Agentic graphs** (LangGraph / CrewAI / AutoGen style) | Deterministic DAG, handoffs, retries | Orchestrator / workflow DNA |
| **MCP tool bridges** (Model Context Protocol) | Least-privilege tool access concept | agent_spec allowed_tools |

## YouTube / learning channels (operator education, not runtime deps)

Use for human craft grounding when expanding SOURCE_CATALOG (respect licenses):

- Official product channels for tools listed in agents.md (Resolve, Unreal, etc.)
- Conference talks (SIGGRAPH, NAB) referenced as distillation *targets* only
- Prefer written primary sources in pack `sources/` over ephemeral video transcripts

## xAI / Grok related notes

- Prefer **host-local prompts** in pack folders over provider-specific system prompts.
- When using Grok or other LLMs as the host model, inject the pack prompt's System section first
  (responsibility + does_not_own + fail-closed rules).
- Do not embed API keys; use env-gated production flags already in the video production profile.

## GitHub resources consulted (reference-only)

- `anthropics/skills` — Skill folder layout and SKILL.md conventions
- LangGraph / CrewAI / AutoGen documentation patterns (architecture column alignment)
- In-repo `business/video/special_skills/*/SKILL.md` + `integration.json` as local templates

## What this factory deliberately does NOT do

- Install remote plugins into production configuration without human approval
- Claim human-surpass (Q5) without measured baselines
- Enable live media/provider calls without existing fail-closed env gates
- Copy unlicensed third-party corpora into the pack

## Next research-backed upgrades (after Wave A)

1. Wire host eval harness to load `rubrics/*.json` (Wave A/P2).
2. Implement CritiqueMessage bus from expanded `critique_edges` (Wave B/P3).
3. Convert selected public workflows (e.g. LangGraph examples) into **host DNA nodes** only after review — never as a second control plane.
"""
    _RESOURCES_OUT.write_text(body, encoding="utf-8")


def improve_agent(
    agent_dir: Path,
    va_by_id: dict[int, dict],
    name_to_id: dict[str, str],
    *,
    expand_edges: bool,
    dry_run: bool,
) -> dict:
    spec_path = agent_dir / "agent_spec.json"
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    agent = {
        "agent_id": spec.get("agent_id") or agent_dir.name,
        "role": spec.get("role"),
        "va_name": spec.get("va_name"),
        "va_id": spec.get("va_id"),
        "prompt_reference": spec.get("prompt_reference"),
        "rubric_reference": spec.get("rubric_reference"),
        "allowed_tools": spec.get("allowed_tools") or [],
        "max_refinement_count": spec.get("max_refinement_count") or 3,
        "critique_edges": spec.get("critique_edges") or {},
    }
    va = None
    if isinstance(agent["va_id"], int):
        va = va_by_id.get(agent["va_id"])
    patterns = detect_patterns((va or {}).get("architecture_pattern") or "")
    bindings = list(SPINE_SKILL_BINDINGS.get(agent["agent_id"], []))
    # always bind agent_loop_v3 for meta spine-ish roles
    if agent["agent_id"].startswith("video.") and any(
        x in agent["agent_id"]
        for x in ("orchestrator", "planner", "memory", "judge", "router", "gatekeeper")
    ):
        if "agent_loop_v3" not in bindings:
            bindings.insert(0, "agent_loop_v3")

    prompt_name = (agent.get("prompt_reference") or f"{agent['agent_id']}.prompt.v1") + ".md"
    # prompt_reference already like video.prompt.orchestrator.v1 — file name = that + .md
    prompt_file = agent_dir / "prompts" / f"{agent.get('prompt_reference') or agent['agent_id'] + '.prompt.v1'}.md"
    rubric_file = agent_dir / "rubrics" / f"{agent.get('rubric_reference') or agent['agent_id'] + '.rubric.v1'}.json"

    result = {
        "agent_id": agent["agent_id"],
        "patterns": patterns,
        "bindings": bindings,
        "prompt": str(prompt_file.relative_to(_ROOT)),
        "rubric": str(rubric_file.relative_to(_ROOT)),
        "dry_run": dry_run,
    }
    if dry_run:
        return result

    write_prompt(prompt_file, agent, va, patterns)
    write_rubric(rubric_file, agent, va)
    write_skill(agent_dir, agent, va, patterns, bindings)
    write_source_artifacts(agent_dir, agent, va)
    write_golden_eval(agent, va)
    new_spec = enrich_agent_spec(
        spec_path, agent, va, name_to_id, expand_edges=expand_edges
    )
    result["critique_edges"] = new_spec.get("critique_edges")
    result["status"] = "improved"
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--only",
        nargs="*",
        help="Optional agent ids to improve (default: all video pack agents)",
    )
    parser.add_argument(
        "--priority-spine",
        action="store_true",
        help="Only P0 spine agents from improvement plan",
    )
    parser.add_argument(
        "--expand-edges",
        action="store_true",
        default=True,
        help="Merge agents.md Accepts/Comments into critique_edges (default true)",
    )
    parser.add_argument("--no-expand-edges", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    expand_edges = args.expand_edges and not args.no_expand_edges

    agents_md = _VA_AGENTS_MD if _VA_AGENTS_MD.is_file() else _CORPUS_AGENTS_MD
    if not agents_md.is_file():
        print("agents.md not found", file=sys.stderr)
        return 1

    va_by_id = parse_agents_md(_read(agents_md))
    name_to_id = build_name_to_id(_AGENTS)

    spine = {
        "video.orchestrator",
        "video.planner",
        "video.router",
        "video.judge",
        "video.gatekeeper",
        "video.critic",
        "video.memory",
    }

    targets: list[Path] = []
    for d in sorted(_AGENTS.iterdir()):
        if not (d / "agent_spec.json").is_file():
            continue
        aid = d.name
        if args.only and aid not in args.only and not any(
            aid == x or aid.endswith(x) for x in args.only
        ):
            # allow full ids only
            if aid not in set(args.only):
                continue
        if args.priority_spine and aid not in spine:
            continue
        targets.append(d)

    if not targets:
        print("No agents selected", file=sys.stderr)
        return 1

    if not args.dry_run:
        write_research_doc()

    results = []
    for i, agent_dir in enumerate(targets, start=1):
        print(f"[{i}/{len(targets)}] {agent_dir.name}", flush=True)
        try:
            results.append(
                improve_agent(
                    agent_dir,
                    va_by_id,
                    name_to_id,
                    expand_edges=expand_edges,
                    dry_run=args.dry_run,
                )
            )
        except Exception as exc:  # noqa: BLE001
            results.append({"agent_id": agent_dir.name, "status": "error", "error": str(exc)})
            print(f"  ERROR {exc}", flush=True)

    report = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "agents_md": str(agents_md),
        "count": len(results),
        "dry_run": args.dry_run,
        "results": results,
    }
    if not args.dry_run:
        _REPORT_OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote {_RESOURCES_OUT}")
        print(f"Wrote {_REPORT_OUT}")
    print(f"Improved {sum(1 for r in results if r.get('status')=='improved' or args.dry_run)}/{len(results)}")
    return 0 if all(r.get("status") != "error" for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
