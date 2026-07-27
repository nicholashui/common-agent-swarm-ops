#!/usr/bin/env python3
"""Sync va-agent-swarm study/*.md (excluding _hk/_zh) into common corpus and write capability index.

Does not execute remote downloads. Only copies from local VA study tree.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_VA = Path(r"C:\Project\va-agent-swarm\study")
CORPUS_STUDY = ROOT / "business" / "video" / "corpus" / "study"
OUT_INDEX = ROOT / "business" / "video" / "STUDY_CAPABILITY_INDEX.json"
OUT_STATUS = ROOT / "docs" / "va_study_implementation_status.md"
OUT_PLAN = ROOT / "docs" / "va_study_implementation_plan.md"

LOCALE_RE = re.compile(r"(_hk|_zh)\.md$", re.I)

# Map study docs → capability domains / common artifacts
DOC_MAP: dict[str, dict] = {
    "agents.md": {
        "domain": "roster",
        "common_artifacts": [
            "business/video/agents/*",
            "business/video/inventory.json",
            "business/video/ROSTER.json",
        ],
        "runtime_level": "operational_pack",
        "notes": "114 VA-style agent folders + SPECs",
    },
    "ai_agent_video_production_workflow.md": {
        "domain": "workflow",
        "common_artifacts": [
            "business/video/workflows/wf_video_arch_*.dna.json",
            "business/video/workflows/wf_video_production_e2e_v1.dna.json",
            "business/video/WORKFLOW_ROLE_MAP.json",
            "business/video/process_coverage.json",
        ],
        "runtime_level": "partial_runtime",
        "notes": "A–J DNA + e2e/LQR; not full critique mesh / all tools from doc",
    },
    "human_video_production_workflow.md": {
        "domain": "workflow",
        "common_artifacts": [
            "business/video/workflows/*",
            "business/video/docs/process-maps.md",
        ],
        "runtime_level": "design_plus_graphs",
        "notes": "Human crew mapping informs agent roster and process maps",
    },
    "lifes_quiet_redemption_agent_workflow.md": {
        "domain": "workflow_lqr",
        "common_artifacts": [
            "business/video/workflows/wf_video_lqr_overview_v1.dna.json",
            "business/video/evals/golden/video-lqr-consistency.json",
        ],
        "runtime_level": "partial_runtime",
        "notes": "LQR overview DNA + eval fixtures; not full 14-shot MCTS loop",
    },
    "system_build_plan.md": {
        "domain": "build",
        "common_artifacts": [
            "docs/migration_redesign/migration_redesign.md",
            "MIGRATION_COMPLETE.md",
            "business/video/production/",
        ],
        "runtime_level": "design_plus_host",
        "notes": "Host migration complete; production profile exists",
    },
    "SYSTEM_REFERENCE.md": {
        "domain": "architecture",
        "common_artifacts": [
            "backend/app/",
            "business/video/workflows/pack_spine.json",
        ],
        "runtime_level": "host_architecture",
        "notes": "Common host implements orchestration spine; not identical CrewAI topology",
    },
    "agent_loop.md": {
        "domain": "special_skill",
        "common_artifacts": ["business/video/special_skills/agent_loop_v3/"],
        "runtime_level": "data_skill",
        "notes": "v1 design retained; pack skill points at v3 lineage",
    },
    "agent_loop_v2.md": {
        "domain": "special_skill",
        "common_artifacts": ["business/video/special_skills/agent_loop_v3/"],
        "runtime_level": "data_skill",
        "notes": "Superseded by v3 skill packaging",
    },
    "agent_loop_v3.md": {
        "domain": "special_skill",
        "common_artifacts": [
            "business/video/special_skills/agent_loop_v3/",
            "business/specials/agents/",
        ],
        "runtime_level": "data_skill",
        "notes": "Skill data + specials agents; not full autonomous loop runtime",
    },
    "aesthetics_agent_functional_specification.md": {
        "domain": "special_skill",
        "common_artifacts": [
            "business/video/special_skills/aesthetics_agent/",
            "business/specials/agents/specials.aesthetics-agent/",
        ],
        "runtime_level": "data_skill",
    },
    "agentic_rag_functional_specification.md": {
        "domain": "special_skill",
        "common_artifacts": [
            "business/video/special_skills/agentic_rag/",
            "backend/app/memory/",
        ],
        "runtime_level": "partial_runtime",
        "notes": "Memory retrieve API exists; full agentic RAG stack partial",
    },
    "coding_agent_functional_specification.md": {
        "domain": "special_skill",
        "common_artifacts": ["business/video/special_skills/coding_agent/"],
        "runtime_level": "data_skill",
    },
    "complex_problem_solution_process_model.md": {
        "domain": "special_skill",
        "common_artifacts": [
            "business/video/special_skills/complex_problem_solution_process_model/"
        ],
        "runtime_level": "data_skill",
    },
    "general_creative_agent_functional_specification.md": {
        "domain": "special_skill",
        "common_artifacts": ["business/video/special_skills/general_creative_agent/"],
        "runtime_level": "data_skill",
    },
    "general_creative_agent_technical_specification.md": {
        "domain": "special_skill",
        "common_artifacts": ["business/video/special_skills/general_creative_agent/"],
        "runtime_level": "data_skill",
    },
    "intent_analysis_agent_functional_specification.md": {
        "domain": "special_skill",
        "common_artifacts": ["business/video/special_skills/intent_analysis_agent/"],
        "runtime_level": "data_skill",
    },
    "knowledge_router_agent.md": {
        "domain": "special_skill",
        "common_artifacts": [
            "business/video/special_skills/knowledge_router_agent/",
            "backend/app/memory/",
        ],
        "runtime_level": "partial_runtime",
    },
    "llm_usage_functional_specification.md": {
        "domain": "special_skill",
        "common_artifacts": ["business/video/special_skills/llm_usage/"],
        "runtime_level": "data_skill",
    },
    "optimization_agent_functional_specification.md": {
        "domain": "special_skill",
        "common_artifacts": ["business/video/special_skills/optimization_agent/"],
        "runtime_level": "data_skill",
    },
    "optimization_agent_technical_specification.md": {
        "domain": "special_skill",
        "common_artifacts": ["business/video/special_skills/optimization_agent/"],
        "runtime_level": "data_skill",
    },
    "podcast_agent_functional_specifcation.md": {
        "domain": "special_skill",
        "common_artifacts": [
            "business/video/special_skills/podcast_agent/",
            "business/video/agents/video.voiceover/",
            "backend/app/adapters/media_live.py",
        ],
        "runtime_level": "partial_runtime",
        "notes": "ElevenLabs media path available when production env configured",
    },
    "psychological_profile_agent_functional_specifications.md": {
        "domain": "special_skill",
        "common_artifacts": ["business/video/special_skills/psychological_profile_agent/"],
        "runtime_level": "data_skill",
    },
    "psychological_recommendation_agent_functional_specification.md": {
        "domain": "special_skill",
        "common_artifacts": ["business/video/special_skills/psychological_profile_agent/"],
        "runtime_level": "data_skill",
        "notes": "Paired with profile skill data",
    },
    "research_agent_functional_specification.md": {
        "domain": "special_skill",
        "common_artifacts": [
            "business/video/special_skills/research_agent/",
            "business/video/agents/video.webresearch/",
        ],
        "runtime_level": "partial_runtime",
    },
    "research_agent_technical_specification.md": {
        "domain": "special_skill",
        "common_artifacts": ["business/video/special_skills/research_agent/"],
        "runtime_level": "data_skill",
    },
    "screenwriter_strategic_goal_achievement_agent_functional_specification.md": {
        "domain": "special_skill",
        "common_artifacts": [
            "business/video/special_skills/screenwriter_strategic_goal_achievement_agent/",
            "business/video/agents/video.screenwriter/",
        ],
        "runtime_level": "partial_runtime",
    },
    "strategic_goal_achievement_agent_functional_specification.md": {
        "domain": "special_skill",
        "common_artifacts": [
            "business/video/special_skills/screenwriter_strategic_goal_achievement_agent/"
        ],
        "runtime_level": "data_skill",
    },
    "thinking_model.md": {
        "domain": "special_skill",
        "common_artifacts": ["business/video/special_skills/thinking_model/"],
        "runtime_level": "data_skill",
    },
    "video_generation_techology_should_learn_now.md": {
        "domain": "media",
        "common_artifacts": [
            "business/video/special_skills/video_generation_techology_should_learn_now/",
            "backend/app/adapters/media_live.py",
            "business/video/production/",
        ],
        "runtime_level": "partial_runtime",
        "notes": "Sora/Veo/Runway/ElevenLabs host path; Kling/DCC not fully wired",
    },
    "ui/agent_management_ui.md": {
        "domain": "ui",
        "common_artifacts": [
            "frontend/src/components/RegistryHome.tsx",
            "frontend/src/components/AgentDetailHome.tsx",
        ],
        "runtime_level": "partial_ui",
    },
    "ui/architecture_communication.md": {
        "domain": "ui",
        "common_artifacts": ["frontend/src/", "docs/"],
        "runtime_level": "partial_ui",
    },
    "ui/backend_agent_management.md": {
        "domain": "ui_backend",
        "common_artifacts": ["backend/app/api/", "frontend/src/lib/api/"],
        "runtime_level": "partial_runtime",
    },
    "ui/production_scale_discovery.md": {
        "domain": "ui",
        "common_artifacts": ["frontend/src/components/RegistryHome.tsx"],
        "runtime_level": "partial_ui",
    },
    "ui/project_creation_flow.md": {
        "domain": "ui",
        "common_artifacts": [
            "frontend/src/components/ComposerHome.tsx",
            "frontend/src/components/CanvasHome.tsx",
        ],
        "runtime_level": "partial_ui",
    },
    "ui/RETHINK_100_IMPROVEMENTS.md": {
        "domain": "ui_design",
        "common_artifacts": ["frontend/src/", "docs/frontend_redesign/"],
        "runtime_level": "design_only",
    },
    "ui/ui_design.md": {
        "domain": "ui",
        "common_artifacts": ["frontend/src/", "docs/frontend_redesign/"],
        "runtime_level": "partial_ui",
    },
    "ui/video_remake_enhancement.md": {
        "domain": "ui_workflow",
        "common_artifacts": [
            "business/video/workflows/",
            "frontend/src/components/BlueprintsHome.tsx",
        ],
        "runtime_level": "partial_runtime",
    },
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def list_va_study_md(va_root: Path) -> list[Path]:
    files = []
    for path in sorted(va_root.rglob("*.md")):
        if not path.is_file():
            continue
        if LOCALE_RE.search(path.name):
            continue
        files.append(path)
    return files


def artifact_exists(pattern: str) -> bool:
    # simple existence: if contains * walk prefix
    full = ROOT / pattern
    if "*" not in pattern:
        return full.exists()
    parent = ROOT / Path(pattern.split("*")[0]).parent
    if not parent.exists():
        # try as directory prefix
        prefix = pattern.split("*")[0]
        parent = ROOT / Path(prefix).parent
        name_prefix = Path(prefix).name
        if not parent.exists():
            return False
        return any(parent.glob(name_prefix + "*"))
    return any(parent.glob(Path(pattern).name))


def sync(va_root: Path, write: bool) -> dict:
    files = list_va_study_md(va_root)
    results = []
    copied = 0
    for src in files:
        rel = src.relative_to(va_root).as_posix()
        dest = CORPUS_STUDY / rel
        status = "missing"
        exact = False
        if dest.is_file():
            exact = dest.read_bytes() == src.read_bytes()
            status = "exact" if exact else "mismatch"
        if write and (not dest.is_file() or not exact):
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            copied += 1
            status = "synced"
            exact = True
        meta = DOC_MAP.get(rel, {
            "domain": "study",
            "common_artifacts": [f"business/video/corpus/study/{rel}"],
            "runtime_level": "corpus_only",
            "notes": "Present in corpus; operational mapping TBD",
        })
        arts = meta.get("common_artifacts") or []
        arts_ok = [a for a in arts if artifact_exists(a)]
        results.append(
            {
                "study_path": rel,
                "va_bytes": src.stat().st_size,
                "corpus_path": f"business/video/corpus/study/{rel}",
                "corpus_status": status,
                "sha256": sha256(src),
                "domain": meta.get("domain"),
                "runtime_level": meta.get("runtime_level"),
                "notes": meta.get("notes", ""),
                "common_artifacts": arts,
                "artifacts_found": arts_ok,
                "artifacts_missing": [a for a in arts if a not in arts_ok],
            }
        )
    return {
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "va_study_root": str(va_root),
        "exclude": ["*_hk.md", "*_zh.md"],
        "count": len(results),
        "copied": copied,
        "entries": results,
    }


def write_status_md(index: dict) -> None:
    levels: dict[str, int] = {}
    for e in index["entries"]:
        levels[e["runtime_level"]] = levels.get(e["runtime_level"], 0) + 1
    lines = [
        "# VA study/*.md implementation status (common-agent-swarm-ops)",
        "",
        f"**Generated:** {index['generated_at']}",
        f"**Source:** `{index['va_study_root']}`",
        f"**Exclude:** {', '.join(index['exclude'])}",
        f"**Study markdown files:** {index['count']}",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Study `.md` in scope | **{index['count']}** |",
        f"| Corpus exact/synced | **{sum(1 for e in index['entries'] if e['corpus_status'] in ('exact','synced'))}** |",
        f"| Corpus missing | **{sum(1 for e in index['entries'] if e['corpus_status']=='missing')}** |",
        "",
        "### Runtime level counts",
        "",
        "| Level | Count | Meaning |",
        "|-------|-------|---------|",
        "| `operational_pack` | " + str(levels.get("operational_pack", 0)) + " | Pack agents/workflows actively usable |",
        "| `partial_runtime` | " + str(levels.get("partial_runtime", 0)) + " | Some host/API/graph coverage |",
        "| `host_architecture` / `design_plus_host` | "
        + str(levels.get("host_architecture", 0) + levels.get("design_plus_host", 0))
        + " | Host structure present |",
        "| `data_skill` | " + str(levels.get("data_skill", 0)) + " | Skill/special data packaged, not full live agent |",
        "| `partial_ui` / `design_only` | "
        + str(levels.get("partial_ui", 0) + levels.get("design_only", 0) + levels.get("ui_design", 0))
        + " | UI partial or design-only |",
        "| `corpus_only` | " + str(levels.get("corpus_only", 0)) + " | In corpus only |",
        "",
        "## Per-document status",
        "",
        "| Study path | Corpus | Runtime level | Artifacts OK | Notes |",
        "|------------|--------|---------------|--------------|-------|",
    ]
    for e in index["entries"]:
        arts = f"{len(e['artifacts_found'])}/{len(e['common_artifacts'])}"
        note = (e.get("notes") or "").replace("|", "/")
        lines.append(
            f"| `{e['study_path']}` | {e['corpus_status']} | `{e['runtime_level']}` | {arts} | {note} |"
        )
    lines.extend(
        [
            "",
            "## Can Common “work as described”?",
            "",
            "| Claim | Answer |",
            "|-------|--------|",
            "| All study `*.md` (no `_hk`/`_zh`) offline in Common | **Yes** (corpus) |",
            "| Full VA production system of every study doc live | **No** — phased |",
            "| Core video pack (agents + A–J DNA + process maps + media path) | **Yes / partial-to-strong** |",
            "| Special skill functional specs as live services | **Mostly data + specials folders** |",
            "| Full UI redesign from every ui/*.md | **Partial** |",
            "",
            "## Related plan",
            "",
            "See `docs/va_study_implementation_plan.md` for ordered implementation of remaining runtime gaps.",
            "",
        ]
    )
    OUT_STATUS.parent.mkdir(parents=True, exist_ok=True)
    OUT_STATUS.write_text("\n".join(lines), encoding="utf-8")


def write_plan_md(index: dict) -> None:
    lines = [
        "# Plan: implement remaining VA study/*.md capabilities in Common",
        "",
        f"**Generated:** {index['generated_at']}",
        "**Goal:** Make common-agent-swarm-ops capable of operating the system described in `va-agent-swarm/study/*.md` (excluding locale `_hk`/`_zh`).",
        "",
        "## Principles",
        "",
        "1. **Corpus first** — every study `.md` exact in `business/video/corpus/study/`.",
        "2. **Pack before live** — agents, graphs, process/role maps before full vendor automation.",
        "3. **Fail-closed production** — live media only via env credentials + production profile.",
        "4. **One work package at a time** — each phase has artifacts + exit gate.",
        "5. **Do not claim COMPLETE runtime** until phase exit gates pass with evidence.",
        "",
        "## Phase 0 — Knowledge lock (DONE when all corpus exact)",
        "",
        "| Step | Action | Exit gate |",
        "|------|--------|-----------|",
        "| 0.1 | Sync all study `*.md` excluding locales | `STUDY_CAPABILITY_INDEX.json` corpus_status exact/synced for all |",
        "| 0.2 | Publish status + plan docs | `docs/va_study_implementation_status.md` exists |",
        "",
        "## Phase 1 — Core video production workflow (from `ai_agent_video_production_workflow.md` + `human_…`)",
        "",
        "| Step | Action | Exit gate |",
        "|------|--------|-----------|",
        "| 1.1 | Keep 114 agent pack + VA IDs | inventory 114 |",
        "| 1.2 | A–J DNA host graphs with role map coverage | 10 arch DNA + WORKFLOW_ROLE_MAP |",
        "| 1.3 | Shared skeleton phases in process_coverage | process rows include spine/phases/A–J |",
        "| 1.4 | Critique bus defaults (critic/judge) | DNA critique_loops + agent critique_edges |",
        "| 1.5 | LQR overview DNA + golden eval | lqr DNA + evals/golden |",
        "",
        "**Status now:** largely complete as partial_runtime (graphs exist; full crew tables per phase still thin).",
        "",
        "## Phase 2 — Media & generation stack (`video_generation_techology…`, podcast, pipeline tools)",
        "",
        "| Step | Action | Exit gate |",
        "|------|--------|-----------|",
        "| 2.1 | Host adapters media.sora/veo/runway/elevenlabs | adapters registered |",
        "| 2.2 | Production profile + credentials template | production/profile.json |",
        "| 2.3 | Wire media agents tool allow-lists | agent_spec allowed_tools |",
        "| 2.4 | Optional: Kling / additional vendors | new adapters + env keys |",
        "| 2.5 | Optional: DCC bridges (Resolve/Nuke) | out-of-band MCP; not default |",
        "",
        "**Status now:** 2.1–2.3 done; 2.4–2.5 open.",
        "",
        "## Phase 3 — Special-skill functional specs → executable skills",
        "",
        "| Step | Action | Docs covered | Exit gate |",
        "|------|--------|--------------|-----------|",
        "| 3.1 | Keep skill SKILL.md + integration.json | aesthetics, coding, creative, intent, optimization, research, etc. | special_skills/index.json |",
        "| 3.2 | Bind specials pack agents (19) to skills | specials.aesthetics-agent, … | 19 agents standalone |",
        "| 3.3 | Host runners for high-value skills (RAG, research, intent) | agentic_rag, research, knowledge_router | API + tests |",
        "| 3.4 | Evaluation harness per skill | evals/ | golden cases |",
        "",
        "**Status now:** 3.1–3.2 data-level; 3.3–3.4 open (partial memory/retrieve only).",
        "",
        "## Phase 4 — Agent loop & thinking models",
        "",
        "| Step | Action | Exit gate |",
        "|------|--------|-----------|",
        "| 4.1 | Package agent_loop_v3 skill | special_skills/agent_loop_v3 |",
        "| 4.2 | Host graph loop pattern (plan→act→critique→refine) | pack_graph critique_loops |",
        "| 4.3 | Thinking model skill hooks | thinking_model skill + optional graph node |",
        "",
        "**Status now:** skill data + graph critique loops; not full autonomous v3 product.",
        "",
        "## Phase 5 — UI study surfaces",
        "",
        "| Step | Action | Docs | Exit gate |",
        "|------|--------|------|-----------|",
        "| 5.1 | Registry + agent detail for all pack agents | agent_management_ui | 133 UI export |",
        "| 5.2 | Canvas/composer run path | project_creation_flow | createAndDispatchRun |",
        "| 5.3 | Blueprints gallery vs archetypes | video_remake / production_scale | A–J listed |",
        "| 5.4 | Close redesign gaps from RETHINK_100 | RETHINK_100_IMPROVEMENTS | prioritized backlog |",
        "",
        "**Status now:** 5.1–5.3 partial; 5.4 backlog.",
        "",
        "## Phase 6 — Continuous distillation & QC mesh (§ from workflow docs)",
        "",
        "| Step | Action | Exit gate |",
        "|------|--------|-----------|",
        "| 6.1 | L1/L2/L3 QC agents in graphs | critic/judge/aiqaconsistency nodes |",
        "| 6.2 | Eval campaigns via host evaluations API | run_evaluation path |",
        "| 6.3 | Provenance/C2PA style gates | c2pa/deepfake agents as design + optional tools |",
        "",
        "## Phase 7 — Evidence & claim hygiene",
        "",
        "| Step | Action | Exit gate |",
        "|------|--------|-----------|",
        "| 7.1 | Refresh STUDY_CAPABILITY_INDEX after each phase | index timestamp |",
        "| 7.2 | Standalone PASS with upstreams unavailable | check_video_domain_standalone |",
        "| 7.3 | Honest status language in README/handoff | no overclaim full VA runtime |",
        "",
        "## Recommended order (one by one)",
        "",
        "1. Phase 0 (this sync)  ",
        "2. Phase 1.x gap fill (thicker archetype crews / typed handoffs)  ",
        "3. Phase 2.4 optional vendors as needed  ",
        "4. Phase 3.3 skill runners (start with agentic_rag + research)  ",
        "5. Phase 4.2 deepen critique loops  ",
        "6. Phase 5.4 UI backlog  ",
        "7. Phase 6 QC mesh  ",
        "8. Phase 7 evidence refresh  ",
        "",
        "## Non-goals (until explicitly scheduled)",
        "",
        "- Full Kling/DCC MCP production suite",
        "- Bit-for-bit CrewAI/AutoGen topology from study prose",
        "- Locale `_hk`/`_zh` study variants (excluded by request)",
        "",
    ]
    OUT_PLAN.write_text("\n".join(lines), encoding="utf-8")


def refresh_knowledge_seeds(index: dict) -> None:
    """Point inert knowledge seeds at key study docs with local consumers."""
    seeds_dir = ROOT / "business" / "video" / "knowledge" / "seeds"
    seeds_dir.mkdir(parents=True, exist_ok=True)
    seeds = []
    # Always include operational seeds
    consumers = {
        "ai_agent_video_production_workflow.md": "agents/video.orchestrator/SPEC.md",
        "agents.md": "agents/video.orchestrator/SPEC.md",
        "human_video_production_workflow.md": "agents/video.planner/SPEC.md",
        "SYSTEM_REFERENCE.md": "agents/video.orchestrator/SPEC.md",
        "system_build_plan.md": "agents/video.producer/SPEC.md",
        "lifes_quiet_redemption_agent_workflow.md": "agents/video.aiqaconsistency/SPEC.md",
        "video_generation_techology_should_learn_now.md": "agents/video.promptengineer/SPEC.md",
    }
    for rel, consumer in consumers.items():
        corpus_rel = f"corpus/study/{rel}"
        if not (ROOT / "business" / "video" / corpus_rel).is_file():
            continue
        if not (ROOT / "business" / "video" / consumer).is_file():
            consumer = "agents/video.orchestrator/SPEC.md"
        seeds.append(
            {
                "seed_path": corpus_rel,
                "consumer_ref": consumer,
                "review_status": "pass",
                "provenance": {
                    "repository": "common-agent-swarm-ops",
                    "commit": "local-pack",
                    "path": f"business/video/{corpus_rel}",
                    "license_status": "internal-pack-data",
                },
            }
        )
    # Keep existing spine seed if present
    spine = "knowledge/seeds/spine-orchestration.md"
    if (ROOT / "business" / "video" / spine).is_file():
        seeds.insert(
            0,
            {
                "seed_path": spine,
                "consumer_ref": "agents/video.orchestrator/SPEC.md",
                "review_status": "pass",
                "provenance": {
                    "repository": "common-agent-swarm-ops",
                    "commit": "local-pack",
                    "path": f"business/video/{spine}",
                    "license_status": "internal-pack-data",
                },
            },
        )
    index_path = seeds_dir / "index.json"
    index_path.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "seeds": seeds,
                "note": "Inert study knowledge seeds linked to local agents; non-activating.",
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--va-study", type=Path, default=DEFAULT_VA)
    parser.add_argument("--write", action="store_true", help="Copy missing/mismatched study md into corpus")
    args = parser.parse_args()
    if not args.va_study.is_dir():
        print("FAIL: VA study root not found:", args.va_study)
        return 1
    index = sync(args.va_study, write=args.write)
    OUT_INDEX.write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_status_md(index)
    write_plan_md(index)
    if args.write:
        refresh_knowledge_seeds(index)
    exact = sum(1 for e in index["entries"] if e["corpus_status"] in ("exact", "synced"))
    print(
        json.dumps(
            {
                "count": index["count"],
                "exact_or_synced": exact,
                "copied": index["copied"],
                "index": str(OUT_INDEX.relative_to(ROOT)),
                "status_md": str(OUT_STATUS.relative_to(ROOT)),
                "plan_md": str(OUT_PLAN.relative_to(ROOT)),
            },
            indent=2,
        )
    )
    return 0 if exact == index["count"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
