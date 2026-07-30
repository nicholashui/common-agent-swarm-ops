#!/usr/bin/env python3
"""Render agent_improvement_plan_v1.md — full-mark (11/11 YES) action lists."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_AUDIT = _ROOT / "business" / "video" / "AGENT_CAPABILITY_AUDIT.json"
_OUT = _ROOT / "agent_improvement_plan_v1.md"

Q_META = [
    (
        "q1_responsibility",
        "Q1 Responsibility in SPEC",
        "Agent identity + ownership boundary is exact, unique, and injected at runtime.",
        [
            "Keep SPEC.md `## Responsibility` as single authoritative paragraph (owns / does-not-own).",
            "Sync first sentence into agent_spec.json `role` and docs/user_guide.md opening.",
            "Add `does_not_own: string[]` to agent_spec.json for boundary enforcement.",
            "CI gate: responsibility length, uniqueness vs peer first-40 tokens, required keywords.",
            "Host injects responsibility block as first system-prompt section before tools.",
        ],
    ),
    (
        "q2_knowledge_distill_plan",
        "Q2 Knowledge distillation plan",
        "Written continuous-distillation plan with owners, cadence, and promotion criteria.",
        [
            "Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.",
            "Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).",
            "Register plan in pack corpus index with next_review_at date.",
            "Link plan outputs to MemoryAgent / RAG namespace id for this agent.",
            "Automate dry-run distillation job (offline) that validates plan schema only.",
        ],
    ),
    (
        "q3_sources_available",
        "Q3 Sources available / obtainable",
        "Licensed or permitted source package + acquisition SOP that can be re-run.",
        [
            "Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.",
            "For each source: license, URL/path, acquisition method, retention, hash, owner.",
            "Store at least one usable excerpt or synthetic licensed fixture per source class.",
            "Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.",
            "Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).",
        ],
    ),
    (
        "q4_self_eval",
        "Q4 Self-evaluation methods & content",
        "Executable L1 schema + L2 rubric + L3 preference fixtures with thresholds.",
        [
            "Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.",
            "Define L1 validators (schema/codec/loudness/format) as machine checks.",
            "Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.",
            "Add golden eval fixture under business/video/evals/agents/<agent_id>/.",
            "Wire host eval harness to load rubric_reference and fail closed on missing file.",
        ],
    ),
    (
        "q5_surpass_human",
        "Q5 Surpass human (measured)",
        "Controlled evaluation shows agent meets/exceeds agents.md surpass signal vs human baseline.",
        [
            "Translate agents.md Surpass-Human Signal into measurable metric + protocol.",
            "Collect human baseline on identical golden task (N trials, frozen inputs).",
            "Run agent on same task with locked model/tool versions; store evidence bundle.",
            "Compute delta; only mark YES if metric meets signal under pre-registered protocol.",
            "Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).",
        ],
    ),
    (
        "q6_execution",
        "Q6 Job execution path",
        "Deterministic host path: prompt + tools + graph node + evidence for the craft job.",
        [
            "Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).",
            "Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).",
            "Map Tool Access column to allowlisted host adapters; stubs must declare not-production.",
            "Register agent in at least one workflow DNA / graph with I/O contracts.",
            "Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.",
        ],
    ),
    (
        "q7_skills_plugins",
        "Q7 Skills / plugins / harness",
        "Role-bound skill pack + harness entry that the host can load for this agent only.",
        [
            "Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.",
            "Bind required pack special_skills (if any) via skills/bindings.json.",
            "Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.",
            "Add capability registry entry listing skills hash + version.",
            "Smoke test: host loads skill without network unless production flags set.",
        ],
    ),
    (
        "q8_self_improve",
        "Q8 Self-improvement mechanism",
        "Closed loop: critique/fail -> refine <=N -> re-eval -> promote/reject with evidence.",
        [
            "Keep max_refinement_count and document policy in SPEC.",
            "Implement refine loop in host using prompt_reference + critique inputs.",
            "Persist improvement candidates under evidence/ with before/after scores.",
            "Promotion gate: L2 score improvement and no L1 regression.",
            "Schedule periodic improvement job (or operator-triggered) with audit log.",
        ],
    ),
    (
        "q9_research_for_improve",
        "Q9 Research to improve",
        "Agent can request/consume research packs that feed distillation and evals.",
        [
            "Define research request schema (topic, source classes, max cost, deadline).",
            "Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).",
            "Store research outputs under sources/research/ with provenance.",
            "Map research -> distillation plan update -> golden eval refresh.",
            "Add dry-run research path that works offline with fixture corpora.",
        ],
    ),
    (
        "q10_collab_instructions",
        "Q10 Collaborate / instruct others",
        "Typed send/receive of instructions and critiques with ack and routing.",
        [
            "Expand critique_edges from agents.md Accepts/Comments columns (full matrix).",
            "Implement CritiqueMessage + InstructionMessage host APIs.",
            "Prove one send and one receive path in integration test for this agent.",
            "Document collab partners in SPEC `## Collaboration Matrix`.",
            "Orchestrator/router can address agent by id with correlation identifiers.",
        ],
    ),
    (
        "q11_conflict_resolve",
        "Q11 Conflict resolve + confirm",
        "Severity routing, self-resolve when allowed, Judge/HiTL confirm when not.",
        [
            "Define conflict policy: blocker/major/minor and auto-resolve rules.",
            "Wire disputes to video.judge (or role judge) multi-agent debate.",
            "Require HiTL confirm for unresolved blockers; record decision evidence.",
            "Integration test: inject conflicting critique, assert resolve or escalate path.",
            "Surface conflict state in activity/ops UI with confirm action refs only.",
        ],
    ),
]

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

GROUP_TOOL_PRIORITY = {
    "1-ATL": [
        "media generation (shot intent preview)",
        "schedule/budget sheet adapters (producer)",
        "screenplay validators (Fountain/FDX)",
        "HiTL greenlight action refs",
    ],
    "2-Cam": [
        "camera-path / ControlNet adapters",
        "ACES/color pipeline validators",
        "drone geofence safety constitution tests",
    ],
    "3-Edit": [
        "FFmpeg / EDL timeline adapters",
        "colorimeter / LUT validators",
        "storyboard panel schema",
        "Resolve/Nuke MCP only behind approval",
    ],
    "4-Snd": [
        "ElevenLabs / loudness (LUFS) adapters",
        "stem separation mocks",
        "broadcast deliverable schema checks",
    ],
    "5-Perf": [
        "consent / likeness gates",
        "motion timing rubrics",
        "voice sample preference judges (offline fixtures)",
    ],
    "6-Dist": [
        "brand guideline checkers",
        "platform packaging validators",
        "performance marketing metric fixtures",
    ],
    "7-Edu": [
        "fact-check / citation validators",
        "WCAG / localization checks",
        "SME HiTL confirm paths",
    ],
    "8-AI": [
        "prompt optimization harness",
        "avatar/voice-clone adapters with red-team gates",
        "deepfake / safety scanners",
    ],
    "9-Meta": [
        "orchestrator graph runtime completeness",
        "router classification tests",
        "judge debate harness",
        "memory retrieve APIs",
        "critique bus as platform spine",
    ],
    "10-Sup": [
        "support SLAs + data contracts",
        "analytics event schemas",
        "archive / distribution packaging tools",
    ],
}


def short(s: str, n: int = 160) -> str:
    t = " ".join((s or "").split())
    return t if len(t) <= n else t[: n - 1] + "…"


def remaining_actions(agent: dict) -> list[tuple[str, str, list[str]]]:
    """Return (qid, title, actions) still needed for full mark."""
    out: list[tuple[str, str, list[str]]] = []
    for qid, title, _done, base_actions in Q_META:
        st = agent["questions"][qid]["status"]
        actions = list(base_actions)
        # specialize
        if qid == "q1_responsibility" and st == "yes":
            actions = [
                "Maintain YES: run uniqueness CI on every SPEC edit.",
                "Add does_not_own list if missing; keep user_guide.md in sync.",
                "Verify runtime prompt injection includes responsibility block.",
            ]
        if qid == "q3_sources_available":
            if agent.get("source_file_count", 0) < 8:
                actions.insert(
                    0,
                    f"Raise packaged sources from {agent.get('source_file_count')} to >=8 substantive files (excerpts + catalog).",
                )
            if not agent.get("has_provenance"):
                actions.insert(0, "Create sources/PROVENANCE.json.")
            if not agent.get("has_mapping"):
                actions.insert(0, "Create sources/MAPPING.md.")
        if qid == "q4_self_eval":
            actions.insert(
                0,
                f"Write rubrics content for `{agent.get('rubric_reference') or 'rubric_reference'}` (currently files={agent.get('rubric_file_count')}).",
            )
        if qid == "q5_surpass_human":
            va = agent.get("va_table") or {}
            sig = va.get("surpass_human_signal") or "(define metric from craft role)"
            actions.insert(0, f"Register surpass protocol for signal: {short(sig, 140)}")
        if qid == "q6_execution":
            actions.insert(
                0,
                f"Write prompts content for `{agent.get('prompt_reference') or 'prompt_reference'}` (currently files={agent.get('prompt_file_count')}).",
            )
            tools = agent.get("allowed_tools") or []
            if not tools or tools == ["media.stub"]:
                actions.insert(
                    1,
                    "Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).",
                )
            elif agent.get("live_media_tools"):
                actions.insert(
                    1,
                    "Keep live media tools fail-closed; add mock-mode golden path tests without network.",
                )
            arch = (agent.get("va_table") or {}).get("architecture_pattern") or ""
            if arch:
                actions.append(f"Implement pattern: {short(arch, 120)}")
        if qid == "q7_skills_plugins":
            actions.insert(
                0,
                f"Create per-agent skills harness directory for `{agent['agent_id']}`.",
            )
        if qid == "q10_collab_instructions":
            va = agent.get("va_table") or {}
            actions.insert(
                0,
                f"Encode accepts_from=`{short(va.get('accepts_critique_from',''),100)}`; comments_on=`{short(va.get('comments_on',''),100)}`.",
            )
            edges = agent.get("critique_edges") or {}
            if not edges.get("inputs") and not edges.get("outputs"):
                actions.insert(0, "Populate critique_edges.inputs/outputs (currently empty).")
        if qid == "q11_conflict_resolve":
            if not agent.get("has_conflict_resolution_text"):
                actions.insert(0, "Add SPEC conflict policy section (severity/major/minor + HiTL).")

        # still list all actions for full mark even if already yes (maintenance)
        out.append((qid, title, actions))
    return out


def priority_rank(agent: dict) -> int:
    """Lower = do first. Meta spine first, then ATL, then live-tool agents, then rest."""
    cat = agent.get("va_category") or ""
    aid = agent.get("agent_id") or ""
    if aid in {
        "video.orchestrator",
        "video.planner",
        "video.router",
        "video.judge",
        "video.gatekeeper",
        "video.critic",
        "video.memory",
    }:
        return 0
    if cat == "9-Meta":
        return 1
    if cat == "1-ATL":
        return 2
    if agent.get("live_media_tools"):
        return 3
    if cat in {"3-Edit", "4-Snd", "2-Cam"}:
        return 4
    if cat in {"8-AI", "6-Dist", "5-Perf"}:
        return 5
    return 6


def main() -> int:
    data = json.loads(_AUDIT.read_text(encoding="utf-8"))
    agents = data["agents"]
    by_cat: dict[str, list] = {c: [] for c in CATEGORY_ORDER}
    for a in agents:
        by_cat.setdefault(a["va_category"], []).append(a)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines: list[str] = []
    a = lines.append

    a("# Agent Improvement Plan v1 — Path to Full Mark (11/11 YES)")
    a("")
    a(f"**Generated:** {now}  ")
    a("**Based on:** `agent_capability_status_v1.md` + `business/video/AGENT_CAPABILITY_AUDIT.json`  ")
    a("**Design authority:** `va-agent-swarm/study/agents.md`  ")
    a(f"**Scope:** {data['agent_count']} non-special video pack agents  ")
    a("**Goal:** Every agent reaches **FULL MARK** = YES on all 11 capability questions (maturity **11.0/11**).")
    a("")
    a("> Full mark is **evidence-based**. Aspirational text in agents.md does not count. Each YES requires artifacts, tests, and (for Q5) measured evaluation.")
    a("")
    a("---")
    a("")
    a("## 0. Full-mark definition of done")
    a("")
    a("| Q | Title | YES only when | Minimum evidence artifacts |")
    a("|---|-------|---------------|----------------------------|")
    for qid, title, done, _actions in Q_META:
        a(
            f"| {title.split()[0]} | {title} | {done} | See Wave actions + per-agent checklist |"
        )
    a("")
    a("### Scoring rule")
    a("")
    a("- **FULL MARK agent:** 11 YES (no PARTIAL, no NO).")
    a("- **Fleet FULL MARK:** 114/114 agents at full mark + platform spine (critique bus, eval harness, improve loop) green.")
    a(f"- **Current fleet average maturity:** {data['global_summary']['avg_maturity']} / 11")
    a(
        f"- **Current cell mix:** YES={data['global_summary']['status_counts']['yes']}, "
        f"PARTIAL={data['global_summary']['status_counts']['partial']}, "
        f"NO={data['global_summary']['status_counts']['no']}"
    )
    a("")
    a("### Gap math (approximate work units)")
    a("")
    g = data["global_summary"]
    # Each PARTIAL/NO needs conversion
    need = g["status_counts"]["partial"] + g["status_counts"]["no"]
    a(f"- Cells still not YES: **{need}** of {data['agent_count'] * 11}")
    a(f"- Agents with zero prompt files: **{data['agent_count'] - g['agents_with_prompt_files']}** (must become 0)")
    a(f"- Agents with zero rubric files: **{data['agent_count'] - g['agents_with_rubric_files']}** (must become 0)")
    a(f"- Agents without measured human-surpass: **{data['agent_count']}** (all need Q5 protocol)")
    a("")
    a("---")
    a("")
    a("## 1. Shared platform workstreams (unlock full marks for every agent)")
    a("")
    a("These are **once-for-the-fleet** systems. Per-agent work alone cannot reach YES on Q5–Q11 without them.")
    a("")
    a("### Workstream P0 — Artifact materialization factory")
    a("")
    a("| ID | Action | Output | Done when |")
    a("|----|--------|--------|-----------|")
    a("| P0.1 | Prompt factory from agents.md + SPEC | `prompts/<prompt_reference>.md` × 114 | CI fails if missing/empty |")
    a("| P0.2 | Rubric factory from Self-Quality Criteria | `rubrics/<rubric_reference>.json` × 114 | Host eval loads file |")
    a("| P0.3 | Source catalog factory | `sources/SOURCE_CATALOG.json` × 114 | Schema validated |")
    a("| P0.4 | Golden task scaffold | `evals/agents/<id>/golden.json` × 114 | Offline dry-run passes schema |")
    a("| P0.5 | Skills harness scaffold | `skills/SKILL.md` + `integration.json` × 114 | Host can load |")
    a("| P0.6 | Audit regen gate | re-run capability audit in CI | maturity report attached to PR |")
    a("")
    a("### Workstream P1 — Execution runtime")
    a("")
    a("| ID | Action | Output | Done when |")
    a("|----|--------|--------|-----------|")
    a("| P1.1 | Agent runner loads prompt_reference | host service | unit tests per category sample |")
    a("| P1.2 | Tool allowlist registry + mock adapters | adapters for design tools | mock path works offline |")
    a("| P1.3 | Graph node binding for every agent | DNA/workflow coverage map | each agent appears in >=1 executable graph or standby invoke API |")
    a("| P1.4 | Evidence writer | correlation id, artifacts, scores | every run produces evidence bundle |")
    a("| P1.5 | Fail-closed production flags | env gates | no live provider call without keys+flags |")
    a("")
    a("### Workstream P2 — Evaluation & human baseline (Q4–Q5)")
    a("")
    a("| ID | Action | Output | Done when |")
    a("|----|--------|--------|-----------|")
    a("| P2.1 | L1 validator library | shared schema/codec/loudness checks | reusable across agents |")
    a("| P2.2 | L2 judge harness | rubric runner | score written to evidence |")
    a("| P2.3 | L3 preference / arena harness | pairwise protocol | used for surpass metrics |")
    a("| P2.4 | Human baseline capture kit | operator protocol + forms | baseline stored per agent |")
    a("| P2.5 | Surpass dashboard | per-agent metric vs signal | YES only if gate green |")
    a("")
    a("### Workstream P3 — Collaboration & conflict bus (Q10–Q11)")
    a("")
    a("| ID | Action | Output | Done when |")
    a("|----|--------|--------|-----------|")
    a("| P3.1 | CritiqueMessage + InstructionMessage APIs | host contracts | OpenAPI + tests |")
    a("| P3.2 | Expand critique_edges from agents.md matrix | agent_spec updates × 114 | matrix completeness CI |")
    a("| P3.3 | Delivery/ack routing | bus | integration tests multi-agent |")
    a("| P3.4 | Judge debate + severity policy | judge service | blocker escalates |")
    a("| P3.5 | HiTL confirm actions | action refs only | UI confirm path |")
    a("")
    a("### Workstream P4 — Distillation & self-improve (Q2–Q3, Q8–Q9)")
    a("")
    a("| ID | Action | Output | Done when |")
    a("|----|--------|--------|-----------|")
    a("| P4.1 | Distillation plan schema + jobs | offline job | dry-run fleet |")
    a("| P4.2 | Licensed source acquisition SOP | legal/ops | catalog compliance |")
    a("| P4.3 | Research request API | meta-agent wiring | offline fixtures |")
    a("| P4.4 | Refine/promote loop | max_refinement_count enforced | before/after scores |")
    a("| P4.5 | Memory namespaces per agent | memory service | retrieve tests |")
    a("")
    a("---")
    a("")
    a("## 2. Phased program to fleet full mark")
    a("")
    a("| Phase | Theme | Target maturity | Exit criteria |")
    a("|-------|-------|-----------------|---------------|")
    a("| **Phase 0** | Honesty & gates | report-only | CI audit; no false surpass claims in UI |")
    a("| **Phase 1** | Artifacts (P0) | ~8.0 avg | 114 prompts + 114 rubrics + catalogs |")
    a("| **Phase 2** | Spine runtime (P1+P3 meta) | 9-Meta agents ~10+ | orchestrator/planner/judge/router full paths |")
    a("| **Phase 3** | Craft execution (P1 tools by group) | ATL/Cam/Edit/Snd ~10 | offline golden pass per group samples |")
    a("| **Phase 4** | Collab+conflict all agents | Q10/Q11 YES fleet | matrix tests green |")
    a("| **Phase 5** | Human baselines (P2) | Q5 possible | baselines captured top 40 then remaining 74 |")
    a("| **Phase 6** | Full mark lock | **11.0 × 114** | audit all YES; evidence index complete |")
    a("")
    a("### Recommended sequence (critical path)")
    a("")
    a("```")
    a("P0 factory (prompts/rubrics/catalogs)")
    a("   -> P1 runner + mock tools")
    a("      -> 9-Meta spine (orchestrator, planner, router, judge, critic, memory)")
    a("         -> P3 critique bus")
    a("            -> craft groups ATL -> Cam/Edit/Snd -> Perf/Dist/Edu/AI -> Sup")
    a("               -> P4 distill/improve")
    a("                  -> P2 human baselines & surpass gates")
    a("                     -> FULL MARK freeze")
    a("```")
    a("")
    a("---")
    a("")
    a("## 3. Universal checklist (every agent must complete)")
    a("")
    a("Copy this as a ticket template for each `video.*` agent:")
    a("")
    a("```text")
    a("[ ] U1  SPEC Responsibility unique + does_not_own")
    a("[ ] U2  user_guide.md synced to Responsibility")
    a("[ ] U3  Knowledge Distillation Plan section + DISTILLATION_PLAN.json")
    a("[ ] U4  SOURCE_CATALOG.json + PROVENANCE + MAPPING + ACQUIRE.md")
    a("[ ] U5  prompts/<prompt_reference>.md complete")
    a("[ ] U6  rubrics/<rubric_reference>.json complete (L2 >=85 threshold)")
    a("[ ] U7  evals/agents/<id>/golden.json + offline mock run passes L1")
    a("[ ] U8  skills/SKILL.md + integration.json + harness entry")
    a("[ ] U9  allowed_tools mapped; mock adapters tested")
    a("[ ] U10 Graph/workflow binding OR invoke API binding")
    a("[ ] U11 critique_edges complete vs agents.md Accepts/Comments")
    a("[ ] U12 Collaboration Matrix section in SPEC")
    a("[ ] U13 Conflict policy section + Judge/HiTL path test")
    a("[ ] U14 Refine loop test (fail -> refine -> pass/escalate)")
    a("[ ] U15 Research request path (fixture) updates sources/research/")
    a("[ ] U16 Human baseline captured OR explicit 'not claimed' with protocol filed")
    a("[ ] U17 Surpass metric run stored; YES only if gate green")
    a("[ ] U18 Capability audit row shows 11 YES for this agent")
    a("```")
    a("")
    a("---")
    a("")
    a("## 4. Actions by capability question (fleet rollup)")
    a("")
    for qid, title, done, actions in Q_META:
        yes = sum(1 for x in agents if x["questions"][qid]["status"] == "yes")
        partial = sum(1 for x in agents if x["questions"][qid]["status"] == "partial")
        no = sum(1 for x in agents if x["questions"][qid]["status"] == "no")
        a(f"### {title}")
        a("")
        a(f"- **Definition of YES:** {done}")
        a(f"- **Current:** YES={yes}, PARTIAL={partial}, NO={no}")
        a(f"- **Agents needing work:** {partial + no} (treat PARTIAL as incomplete)")
        a("- **Standard actions to full mark:**")
        for act in actions:
            a(f"  - [ ] {act}")
        a("")

    a("---")
    a("")
    a("## 5. Per-group improvement programs")
    a("")

    for cat in CATEGORY_ORDER:
        group_agents = by_cat.get(cat) or []
        if not group_agents:
            continue
        avg = round(
            sum(x["score"]["maturity_0_to_11"] for x in group_agents) / len(group_agents),
            2,
        )
        a(f"### {cat} — {CATEGORY_LABELS.get(cat, cat)} ({len(group_agents)} agents, avg {avg})")
        a("")
        a("**Group tool/harness priorities:**")
        for t in GROUP_TOOL_PRIORITY.get(cat, []):
            a(f"- {t}")
        a("")
        a("**Group milestone checklist:**")
        a(f"- [ ] All {len(group_agents)} agents complete Universal U1–U10")
        a(f"- [ ] Group mock adapter pack tests green")
        a(f"- [ ] At least 1 multi-agent path inside group using critique bus")
        a(f"- [ ] Human baselines for group lead agents complete")
        a(f"- [ ] Audit: every agent in group maturity 11.0")
        a("")
        a("| Agent | Now | Gap to 11 | Priority band | First 5 actions |")
        a("|-------|-----|-----------|---------------|-----------------|")
        for ag in sorted(group_agents, key=lambda x: (priority_rank(x), x.get("va_id") or 999, x["agent_id"])):
            gap = round(11.0 - ag["score"]["maturity_0_to_11"], 2)
            rem = remaining_actions(ag)
            # pick highest-impact incomplete qs
            first_actions: list[str] = []
            for qid, title, acts in rem:
                st = ag["questions"][qid]["status"]
                if st != "yes" and acts:
                    first_actions.append(f"{title.split()[0]}: {acts[0]}")
                if len(first_actions) >= 5:
                    break
            if len(first_actions) < 5:
                # fill maintenance
                for qid, title, acts in rem:
                    if acts and f"{title.split()[0]}:" not in " ".join(first_actions):
                        first_actions.append(f"{title.split()[0]}: {acts[0]}")
                    if len(first_actions) >= 5:
                        break
            band = priority_rank(ag)
            a(
                f"| `{ag['agent_id']}` | {ag['score']['maturity_0_to_11']} | {gap} | P{band} | "
                + "<br>".join(f"{i+1}. {short(x, 90)}" for i, x in enumerate(first_actions[:5]))
                + " |"
            )
        a("")

    a("---")
    a("")
    a("## 6. Per-agent full-mark action lists")
    a("")
    a("Each agent section lists **all actions required for 11/11 YES**, ordered by question. Complete every checkbox.")
    a("")

    ordered = sorted(agents, key=lambda x: (priority_rank(x), x.get("va_id") or 999, x["agent_id"]))
    for ag in ordered:
        va = ag.get("va_table") or {}
        a(
            f"### `{ag['agent_id']}` — {ag.get('va_name') or ag['agent_id']} "
            f"(now {ag['score']['maturity_0_to_11']}/11 → target 11.0)"
        )
        a("")
        a(
            f"- **Category:** `{ag.get('va_category')}` · **VA#:** {ag.get('va_id')} · **Priority band:** P{priority_rank(ag)}"
        )
        a(
            f"- **Current cells:** YES={ag['score']['yes']} PARTIAL={ag['score']['partial']} NO={ag['score']['no']}"
        )
        a(
            f"- **Prompt/rubric refs:** `{ag.get('prompt_reference')}` / `{ag.get('rubric_reference')}`"
        )
        a(
            f"- **Tools now:** `{', '.join(ag.get('allowed_tools') or []) or '(none)'}` · live_media={ag.get('live_media_tools')}"
        )
        a(
            f"- **Sources now:** {ag.get('source_file_count')} files · provenance={ag.get('has_provenance')}"
        )
        if va:
            a(f"- **Design responsibility:** {short(va.get('responsibility',''), 180)}")
            a(f"- **Design knowledge sources:** {short(va.get('knowledge_distillation_source',''), 180)}")
            a(f"- **Design self-quality:** {short(va.get('self_quality_criteria',''), 160)}")
            a(f"- **Design surpass signal:** {short(va.get('surpass_human_signal',''), 160)}")
            a(f"- **Design tools:** {short(va.get('tool_access',''), 160)}")
            a(f"- **Design architecture:** {short(va.get('architecture_pattern',''), 140)}")
            a(f"- **Design accepts critique from:** {short(va.get('accepts_critique_from',''), 140)}")
            a(f"- **Design comments on:** {short(va.get('comments_on',''), 140)}")
        a("")
        a("#### Status toward full mark")
        a("")
        a("| Q | Now | Target |")
        a("|---|-----|--------|")
        for qid, title, _d, _acts in Q_META:
            st = ag["questions"][qid]["status"].upper()
            a(f"| {title} | **{st}** | **YES** |")
        a("")
        a("#### Action checklist (complete all)")
        a("")
        for qid, title, acts in remaining_actions(ag):
            st = ag["questions"][qid]["status"]
            a(f"**{title}** (now {st.upper()} → YES)")
            a("")
            for act in acts:
                a(f"- [ ] {act}")
            a("")
        a("#### Exit gate for this agent")
        a("")
        a(
            f"- [ ] Offline golden run for `{ag['agent_id']}` passes L1 + L2 threshold"
        )
        a("- [ ] Collab send/receive test green")
        a("- [ ] Conflict resolve or HiTL escalate test green")
        a("- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)")
        a("- [ ] Human baseline package filed; surpass claim only if measured gate green")
        a(
            f"- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `{ag['agent_id']}` shows maturity 11.0 and 11 YES"
        )
        a("")

    a("---")
    a("")
    a("## 7. Priority order of agents (implementation queue)")
    a("")
    a("Work top-down. Spine unlocks everyone else.")
    a("")
    a("| Order | Band | Agent | Now | Why first |")
    a("|------:|------|-------|-----|-----------|")
    for i, ag in enumerate(ordered, start=1):
        why = {
            0: "Platform spine — orchestrates, plans, routes, judges",
            1: "Meta platform capabilities",
            2: "Above-the-line creative authority",
            3: "Already has live media tools — complete harness/evals",
            4: "Core craft production path",
            5: "Specialized craft / AI-era",
            6: "Support & long-tail",
        }[priority_rank(ag)]
        a(
            f"| {i} | P{priority_rank(ag)} | `{ag['agent_id']}` | {ag['score']['maturity_0_to_11']} | {why} |"
        )
    a("")
    a("---")
    a("")
    a("## 8. Estimation model (planning aid)")
    a("")
    a("| Work item | Unit | Count | Notes |")
    a("|-----------|------|------:|-------|")
    a("| Prompt file | agent | 114 | factory + human craft review |")
    a("| Rubric file | agent | 114 | factory + craft owner signoff |")
    a("| Source catalog + acquire plan | agent | 114 | legal may serialize |")
    a("| Skills harness | agent | 114 | thin wrapper ok |")
    a("| Golden eval | agent | 114 | start with fixtures |")
    a("| Mock tool adapters | tool class | ~30–50 | shared across agents |")
    a("| Collab edge tests | agent | 114 | generate from matrix |")
    a("| Human baseline | agent | 114 | expensive; batch by group |")
    a("| Surpass measurement | agent | 114 | only after baseline |")
    a("")
    a("**Practical staging of Q5:** Do not block Phases 1–4 on surpass. File baseline protocol early; execute human studies after execution path works. Full mark requires Q5 YES — plan calendar time for human evaluation, or redefine YES as “measured parity protocol complete and target met” (never claim without data).")
    a("")
    a("---")
    a("")
    a("## 9. Governance gates (prevent fake full marks)")
    a("")
    a("1. **No YES without path:** audit script must check file existence + test names, not SPEC keywords alone (upgrade auditor).")
    a("2. **No surpass in UI** unless evidence bundle hash present.")
    a("3. **Fail-closed tools:** missing adapter => mock or error, never silent success.")
    a("4. **Action refs** for HiTL confirms (product façade discipline).")
    a("5. **PR checklist** must include capability audit delta for touched agents.")
    a("")
    a("---")
    a("")
    a("## 10. Regeneration")
    a("")
    a("```bash")
    a("python scripts/business/audit_agent_capability_status.py")
    a("python scripts/business/render_agent_capability_status_v1.py")
    a("python scripts/business/render_agent_improvement_plan_v1.py")
    a("```")
    a("")
    a("Track progress by re-auditing: maturity avg should rise from "
      f"**{data['global_summary']['avg_maturity']}** toward **11.0**.")
    a("")

    _OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {_OUT} lines={len(lines)} bytes={_OUT.stat().st_size}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
