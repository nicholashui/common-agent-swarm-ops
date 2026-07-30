#!/usr/bin/env python3
"""Render agent_improvement_plan_v2.md — full-mark (11/11 YES) actions after v2 audit.

Grounded in agent_capability_status_v2.md + AGENT_CAPABILITY_AUDIT.json.
v1 automatable work is largely DONE; v2 centers on Q5 human baselines + harden/maintain.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_AUDIT = _ROOT / "business" / "video" / "AGENT_CAPABILITY_AUDIT.json"
_COMPLETION = _ROOT / "agent_improvement_plan_completion_v1.json"
_OUT = _ROOT / "agent_improvement_plan_v2.md"

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

# Full-mark definition + default actions (v2)
Q_META = [
    (
        "q1_responsibility",
        "Q1 Responsibility in SPEC",
        "Identity + owns/does_not_own exact, unique, injected at runtime.",
        [
            "Maintain SPEC.md ## Responsibility uniqueness CI on every edit.",
            "Keep agent_spec.does_not_own aligned with prompt System section.",
            "Sync user_guide.md opening sentence with Responsibility.",
            "L1 loader check must continue to require Responsibility block in prompt.",
        ],
    ),
    (
        "q2_knowledge_distill_plan",
        "Q2 Knowledge distillation plan",
        "Written continuous-distillation plan with owner, cadence, promotion criteria.",
        [
            "Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.",
            "Link distill outputs to memory_namespace pack.video.<agent_id>.",
            "Dry-run distill schema validation in CI for changed agents.",
        ],
    ),
    (
        "q3_sources_available",
        "Q3 Sources available / obtainable",
        "Licensed or permitted sources + re-runnable ACQUIRE SOP.",
        [
            "Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.",
            "Refresh ACQUIRE.md steps after any new corpus class.",
            "Update PROVENANCE.json hashes when excerpts change.",
            "Prefer fixture-only offline grounding until legal approval.",
        ],
    ),
    (
        "q4_self_eval",
        "Q4 Self-evaluation methods & content",
        "Executable L1 + L2 rubric + optional L3 preference with thresholds.",
        [
            "Keep rubrics/<rubric_reference>.json pass_threshold >= 85.",
            "Re-derive dimensions when agents.md Self-Quality Criteria change.",
            "Ensure golden.json still expects l1_passed + artifact.",
            "Re-run pack golden after rubric edits.",
        ],
    ),
    (
        "q5_surpass_human",
        "Q5 Surpass human (measured)",
        "Non-synthetic human baseline + agent measure + gate.met=true.",
        [
            "Confirm human_baseline_protocol.json exists and metric matches agents.md surpass signal.",
            "Clear any synthetic human trials before real sessions.",
            "Collect >=5 real human trials (0–100 or metric-native) on frozen golden inputs.",
            "Ensure agent_measurement has >=5 offline (or locked-version) trials.",
            "Run evaluate_gate; require gate.met && !synthetic for YES.",
            "Publish human_baseline_evidence.json; only then allow UI surpass language.",
            "If not_met: improve prompt/rubric/tools, re-measure agent, re-rate humans if task changed.",
        ],
    ),
    (
        "q6_execution",
        "Q6 Job execution path",
        "Host path: prompt + rubric + skill + golden/runner evidence.",
        [
            "Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).",
            "Verify PackAgentLoader.load(agent_id) succeeds offline.",
            "Keep golden.json green via PackGoldenRunner.",
            "Fail-closed on network=true/production=true without env gates.",
            "Optional: map design Tool Access to mock adapters with tests.",
        ],
    ),
    (
        "q7_skills_plugins",
        "Q7 Skills / plugins / harness",
        "Per-agent skills harness loadable by host.",
        [
            "Maintain skills/SKILL.md + integration.json + bindings.json.",
            "Validate special_skills bindings paths when used.",
            "Smoke: host loads skill without network.",
        ],
    ),
    (
        "q8_self_improve",
        "Q8 Self-improvement mechanism",
        "critique/fail → refine ≤N → re-score → promote/reject with evidence.",
        [
            "Keep max_refinement_count policy documented.",
            "Exercise force_l2_fail_once path in tests when changing runner.",
            "After improvements, re-run golden + baseline agent_measurement.",
            "Optional: durable promote of new prompt/rubric versions with evidence bundle.",
        ],
    ),
    (
        "q9_research_for_improve",
        "Q9 Research to improve",
        "Can request/consume research packs into distill + evals.",
        [
            "Use SOURCE_CATALOG + ACQUIRE for research intake.",
            "Wire research meta-agents when task needs external refresh (offline fixtures first).",
            "Map research outputs under sources/research/ with provenance.",
            "Refresh golden thresholds only with protocol change control.",
        ],
    ),
    (
        "q10_collab_instructions",
        "Q10 Collaborate / instruct others",
        "Typed send/receive with edge allowlists + ack.",
        [
            "Keep critique_edges aligned with agents.md Accepts/Comments.",
            "Prove send+receive for at least one partner edge in integration tests (spine).",
            "Include correlation_id on all critiques/handoffs.",
        ],
    ),
    (
        "q11_conflict_resolve",
        "Q11 Conflict resolve + confirm",
        "Severity routing; self-resolve when allowed; Judge/HiTL confirm when not.",
        [
            "Keep blocker → requires_hitl confirm path.",
            "Route unresolved disputes toward video.judge when on outputs allowlist.",
            "Surface confirm via product action refs only (no invented authority).",
            "Re-test after edge matrix changes.",
        ],
    ),
]


def short(s: str, n: int = 160) -> str:
    t = " ".join((s or "").split())
    return t if len(t) <= n else t[: n - 1] + "…"


def priority_rank(agent: dict) -> int:
    aid = agent.get("agent_id") or ""
    cat = agent.get("va_category") or ""
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


def remaining_actions(agent: dict) -> list[tuple[str, str, str, list[str]]]:
    """(qid, title, status, actions) — status-aware v2 actions."""
    out: list[tuple[str, str, str, list[str]]] = []
    va = agent.get("va_table") or {}
    for qid, title, _done, base in Q_META:
        st = agent["questions"][qid]["status"]
        actions: list[str] = []

        if st == "yes":
            # maintenance only
            actions = [
                f"MAINTAIN YES: {base[0]}",
                *base[1:3],
            ]
        else:
            actions = list(base)

        # Q5 specialization (primary remaining gap)
        if qid == "q5_surpass_human":
            sig = va.get("surpass_human_signal") or "craft score vs human baseline"
            actions = [
                f"PRIMARY GAP: Close Q5 for `{agent['agent_id']}` — design signal: {short(sig, 140)}",
                f"Protocol path: business/video/evals/agents/{agent['agent_id']}/human_baseline_protocol.json "
                f"(status={agent.get('baseline_status')}, gate_met={agent.get('baseline_gate_met')}, "
                f"synthetic={agent.get('baseline_gate_synthetic')})",
                "If synthetic humans present: "
                f"`python scripts/business/record_human_baseline.py --clear-synthetic --agents {agent['agent_id']}`",
                "Open rater brief if available: "
                f"business/video/evals/rater_sessions/{agent['agent_id']}/RATER_BRIEF.md",
                "Interactive session: "
                f"`python scripts/business/record_human_baseline.py --session --agent {agent['agent_id']} "
                "--rater <real_id> --evaluate`",
                "Or CSV: export template → fill ≥5 scores → "
                "`record_human_baseline.py --import-csv ... --evaluate`",
                "Re-measure agent after prompt changes: "
                f"`scaffold_human_baselines_v1.py --agent {agent['agent_id']} --measure-agent --evaluate-gate`",
                "FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.",
                "If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.",
            ]

        if qid == "q6_execution" and st == "yes":
            tools = agent.get("allowed_tools") or []
            if not tools or tools == ["media.stub"]:
                actions.append(
                    "Optional harden: replace pure media.stub with role mock adapters + unit tests."
                )
            if agent.get("live_media_tools"):
                actions.append(
                    "Harden: live media remains env-gated; offline golden must stay green without network."
                )

        if qid == "q3_sources_available" and agent.get("source_file_count", 0) < 8:
            actions.insert(
                0,
                f"Expand packaged source files from {agent.get('source_file_count')} toward ≥8 excerpts where licensed.",
            )

        out.append((qid, title, st, actions))
    return out


def main() -> int:
    data = json.loads(_AUDIT.read_text(encoding="utf-8"))
    completion = {}
    if _COMPLETION.is_file():
        try:
            completion = json.loads(_COMPLETION.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            completion = {}

    agents = data["agents"]
    n = len(agents)
    g = data["global_summary"]
    by_cat: dict[str, list] = {c: [] for c in CATEGORY_ORDER}
    for ag in agents:
        by_cat.setdefault(ag["va_category"], []).append(ag)

    yes_c = g["status_counts"]["yes"]
    part_c = g["status_counts"]["partial"]
    no_c = g["status_counts"]["no"]
    total_c = yes_c + part_c + no_c
    weighted_pct = 100.0 * (yes_c + 0.5 * part_c) / max(total_c, 1)
    strict_pct = 100.0 * yes_c / max(total_c, 1)
    plan_pct = (completion.get("complete_percent") or {}).get("plan_composite", weighted_pct)
    auto_pct = (completion.get("complete_percent") or {}).get("automatable_q_except_q5", 100.0)

    q5_partial = sum(1 for a in agents if a["questions"]["q5_surpass_human"]["status"] == "partial")
    q5_yes = sum(1 for a in agents if a["questions"]["q5_surpass_human"]["status"] == "yes")
    q5_no = sum(1 for a in agents if a["questions"]["q5_surpass_human"]["status"] == "no")

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines: list[str] = []
    a = lines.append

    a("# Agent Improvement Plan v2 — Path to Full Mark (11/11 YES)")
    a("")
    a(f"**Generated:** {now}  ")
    a("**Based on:** `agent_capability_status_v2.md` + `business/video/AGENT_CAPABILITY_AUDIT.json`  ")
    a("**Prior plan:** `agent_improvement_plan_v1.md` / `agent_improvement_plan_v1_hk.md`  ")
    a("**Design authority:** `va-agent-swarm/study/agents.md`  ")
    a(f"**Scope:** {n} non-special video pack agents  ")
    a("**Goal:** Every agent reaches **FULL MARK** = YES on all 11 questions (maturity **11.0/11**).")
    a("")
    a("> **v2 thesis:** Automatable Wave A–D work from v1 is **done**. Remaining full-mark work is almost entirely ")
    a("> **Q5 measured human baselines** (real raters, not synthetic), plus maintenance/hardening of already-green items.")
    a("")
    a("---")
    a("")
    a("## 0. Scoreboard vs full mark")
    a("")
    a("| Metric | Now | Full mark target |")
    a("|--------|----:|-----------------:|")
    a(f"| Avg maturity 0–11 | **{g['avg_maturity']}** | **11.0** |")
    a(f"| Weighted cell completion | **{weighted_pct:.2f}%** | **100%** |")
    a(f"| Strict YES cells | **{strict_pct:.2f}%** | **100%** |")
    a(f"| YES / PARTIAL / NO | {yes_c} / {part_c} / {no_c} | {n*11} / 0 / 0 |")
    a(f"| Plan composite (v1 tracker) | **{plan_pct}%** | **100%** |")
    a(f"| Automatable (ex-Q5) | **{auto_pct}%** | **100%** (already) |")
    a(f"| Q5 YES agents | **{q5_yes}/{n}** | **{n}/{n}** |")
    a("")
    a(f"**Gap math:** {part_c + no_c} cells not YES — of which **{q5_partial}** are Q5 PARTIAL and **{q5_no}** Q5 NO.")
    a(f"Closing Q5 alone lifts maturity from **{g['avg_maturity']} → 11.0** if all other Qs stay YES.")
    a("")
    a("---")
    a("")
    a("## 1. What v1 already completed (do not re-build)")
    a("")
    a("| Workstream | Evidence | Status |")
    a("|------------|----------|--------|")
    a("| P0 Artifact factories | prompts/rubrics/skills/catalogs/goldens ×114 | **DONE** |")
    a("| P1 Execution runtime | `backend/app/video/pack_runtime/` loader+runner+golden | **DONE** |")
    a("| P2 Eval / baseline kit | rubrics L1/L2/L3 + human_baseline_protocol ×114 | **DONE (protocol)** |")
    a("| P3 Critique bus | CritiqueBus edges, ack, HiTL blockers | **DONE** |")
    a("| P4 Distill / improve scaffolds | DISTILLATION_PLAN + ACQUIRE + refine loop | **DONE** |")
    a("| Q1–Q4, Q6–Q11 fleet YES | capability audit v2 | **DONE** |")
    a("| Q5 real human MET | gate.met && !synthetic | **NOT DONE** |")
    a("")
    a("---")
    a("")
    a("## 2. Full-mark definition of done (v2)")
    a("")
    a("| Q | Title | YES only when | Primary evidence |")
    a("|---|-------|---------------|------------------|")
    for qid, title, done, _ in Q_META:
        a(f"| {title.split()[0]} | {title} | {done} | See per-agent checklist |")
    a("")
    a("### Scoring rule")
    a("")
    a("- **FULL MARK agent:** 11 YES (no PARTIAL, no NO).")
    a(f"- **Fleet FULL MARK:** {n}/{n} agents at 11.0 + no synthetic surpass claims in UI.")
    a("- **Q5 special rule:** `human_baseline_protocol.json` with `gate.met=true` AND `gate.synthetic=false` AND evidence file.")
    a("")
    a("---")
    a("")
    a("## 3. Research-backed path for the remaining gap (Q5)")
    a("")
    a("Deep research inputs (same family as improvement research v1 + baseline design):")
    a("")
    a("| Source | How v2 uses it |")
    a("|--------|----------------|")
    a("| `agents.md` Surpass-Human Signal | Metric inference (win-rate, TTD, cost, κ, craft score) |")
    a("| LLM-as-Judge / pairwise arena practices | L2 rubrics + optional pairwise_win_rate gates |")
    a("| Human evaluation protocols (frozen tasks, blinding) | `human_baseline_protocol.json` procedure |")
    a("| Anthropic Agent Skills | Per-agent harness already loadable |")
    a("| Offline pack_runtime | Reproducible agent_measurement trials |")
    a("| Fail-closed product rules | No surpass UI without evidence |")
    a("")
    a("### Recommended evaluation science (per agent)")
    a("")
    a("1. **Freeze inputs** — only `evals/agents/<id>/golden.json` (or versioned twin).")
    a("2. **Human trials n≥5** — independent raters when possible; record rater_id.")
    a("3. **Agent trials n≥5** — locked runner/prompt/rubric versions.")
    a("4. **Pre-register metric** — from agents.md signal (do not change after rating starts).")
    a("5. **Gate** — higher_is_better: agent_mean≥human_mean; lower_is_better: agent_mean<human_mean; pairwise: rate≥threshold.")
    a("6. **Publish evidence** — `human_baseline_evidence.json`; claim only if met && !synthetic.")
    a("")
    a("---")
    a("")
    a("## 4. Shared workstreams v2 (fleet unlock for 11/11)")
    a("")
    a("### W0 — Protect the green (continuous)")
    a("")
    a("| ID | Action | Done when |")
    a("|----|--------|-----------|")
    a("| W0.1 | CI: pack golden spine 7/7 | pytest + `run_pack_agent_golden.py --spine` green |")
    a("| W0.2 | CI: capability audit cells no regression on Q1–4,6–11 | audit JSON gate |")
    a("| W0.3 | Ban synthetic surpass claims in UI | product checks claim_allowed_in_ui |")
    a("")
    a("### W1 — Human baseline operations (PRIMARY)")
    a("")
    a("| ID | Action | Output | Done when |")
    a("|----|--------|--------|-----------|")
    a("| W1.1 | Keep protocols current | human_baseline_protocol.json ×114 | scaffold re-runnable |")
    a("| W1.2 | Clear synthetic on spine before real sessions | clean human_baseline.trials | synthetic_any=false |")
    a("| W1.3 | Rater session packs | evals/rater_sessions/ | briefs for spine+ATL |")
    a("| W1.4 | Record real trials | CLI/CSV/session | n≥5 per agent |")
    a("| W1.5 | Evaluate gates | gate.met | non-synthetic |")
    a("| W1.6 | Dashboard | BASELINE_STATUS.md | claimable count rises |")
    a("| W1.7 | Re-audit + completion report | capability v2 + plan completion | maturity → 11 |")
    a("")
    a("### W2 — Optional hardening (not blocking 11/11 if Q5 met)")
    a("")
    a("| ID | Action | Why |")
    a("|----|--------|-----|")
    a("| W2.1 | Role mock tool adapters beyond media.stub | richer Q6 craft fidelity |")
    a("| W2.2 | Licensed corpus acquisition | deeper Q3 grounding |")
    a("| W2.3 | Durable prompt/rubric promote pipeline | stronger Q8 |")
    a("| W2.4 | Product UI action-refs for HiTL confirm | operator UX for Q11 |")
    a("")
    a("---")
    a("")
    a("## 5. Phased program to fleet full mark")
    a("")
    a("| Phase | Theme | Target | Exit criteria |")
    a("|-------|-------|--------|---------------|")
    a("| **V2-P0** | Protect green | keep 10.5 | spine golden + unit tests green |")
    a("| **V2-P1** | Spine human baselines | 7 agents Q5 YES | orchestrator…memory gate.met |")
    a("| **V2-P2** | ATL human baselines | +5 agents Q5 YES | director/producer/screenwriter/showrunner/casting |")
    a("| **V2-P3** | Core craft groups | Cam/Edit/Snd | group baselines MET |")
    a("| **V2-P4** | Long tail | Perf/Dist/Edu/AI/Sup + remaining Meta | all 114 Q5 YES |")
    a("| **V2-P5** | Full mark freeze | **11.0 × 114** | audit all YES; completion 100% |")
    a("")
    a("### Critical path")
    a("")
    a("```")
    a("baseline_status → clear synthetic spine → rate spine humans")
    a("  → evaluate_gate spine → rate ATL → core craft → long tail")
    a("    → audit_agent_capability_status → report completion 100%")
    a("```")
    a("")
    a("---")
    a("")
    a("## 6. Universal checklist v2 (every agent)")
    a("")
    a("```text")
    a("[ ] V2-U1  Q1–Q4 still YES after any SPEC edit")
    a("[ ] V2-U2  prompt + rubric + skill files still load via PackAgentLoader")
    a("[ ] V2-U3  golden.json offline pass")
    a("[ ] V2-U4  critique_edges non-empty; bus allowlist valid")
    a("[ ] V2-U5  DISTILLATION_PLAN + SOURCE_CATALOG + ACQUIRE present")
    a("[ ] V2-U6  human_baseline_protocol.json present")
    a("[ ] V2-U7  agent_measurement n>=5 (offline or locked)")
    a("[ ] V2-U8  human_baseline n>=5 REAL (synthetic=false)")
    a("[ ] V2-U9  evaluate_gate => met=true, synthetic=false")
    a("[ ] V2-U10 evidence claim_allowed_in_ui true")
    a("[ ] V2-U11 capability audit row maturity 11.0 / 11 YES")
    a("```")
    a("")
    a("---")
    a("")
    a("## 7. Actions by question (fleet rollup)")
    a("")
    for qid, title, done, actions in Q_META:
        y = sum(1 for x in agents if x["questions"][qid]["status"] == "yes")
        p = sum(1 for x in agents if x["questions"][qid]["status"] == "partial")
        no = sum(1 for x in agents if x["questions"][qid]["status"] == "no")
        a(f"### {title}")
        a("")
        a(f"- **Definition of YES:** {done}")
        a(f"- **Current:** YES={y}, PARTIAL={p}, NO={no}")
        a(f"- **Agents needing work for full mark:** {p + no} (PARTIAL counts as incomplete)")
        if y == n:
            a("- **Mode:** MAINTAIN (already fleet YES) — run maintenance actions only.")
        else:
            a("- **Mode:** CLOSE GAP — primary delivery actions below.")
        a("- **Standard actions:**")
        for act in actions:
            a(f"  - [ ] {act}")
        a("")

    a("---")
    a("")
    a("## 8. Per-group programs (v2)")
    a("")

    for cat in CATEGORY_ORDER:
        group_agents = by_cat.get(cat) or []
        if not group_agents:
            continue
        avg = round(
            sum(x["score"]["maturity_0_to_11"] for x in group_agents) / len(group_agents),
            2,
        )
        need_q5 = sum(
            1 for x in group_agents if x["questions"]["q5_surpass_human"]["status"] != "yes"
        )
        a(
            f"### {cat} — {CATEGORY_LABELS.get(cat, cat)} "
            f"({len(group_agents)} agents, avg {avg}, Q5 remaining {need_q5})"
        )
        a("")
        a("**Group milestone checklist:**")
        a(f"- [ ] All {len(group_agents)} agents pass V2-U1…U5 (maintain green)")
        a(f"- [ ] All {len(group_agents)} complete real human baselines (V2-U8…U10)")
        a(f"- [ ] Audit: every agent in group maturity **11.0**")
        a("")
        a("| Agent | Now | Gap to 11 | Band | First actions to full mark |")
        a("|-------|-----|-----------|------|------------------------------|")
        for ag in sorted(
            group_agents,
            key=lambda x: (priority_rank(x), x.get("va_id") or 999, x["agent_id"]),
        ):
            gap = round(11.0 - ag["score"]["maturity_0_to_11"], 2)
            rem = remaining_actions(ag)
            first: list[str] = []
            for qid, title, st, acts in rem:
                if st != "yes" and acts:
                    first.append(f"{title.split()[0]}: {acts[0]}")
                if len(first) >= 3:
                    break
            if not first:
                first = ["All Q YES — maintain + re-verify golden/baseline"]
            a(
                f"| `{ag['agent_id']}` | {ag['score']['maturity_0_to_11']} | {gap} | P{priority_rank(ag)} | "
                + "<br>".join(f"{i+1}. {short(x, 100)}" for i, x in enumerate(first))
                + " |"
            )
        a("")

    a("---")
    a("")
    a("## 9. Per-agent full-mark action lists")
    a("")
    a("Each section lists **all actions to hold or reach 11/11 YES**, ordered by question.")
    a("Items marked PRIMARY GAP are required for full mark today.")
    a("")

    ordered = sorted(
        agents, key=lambda x: (priority_rank(x), x.get("va_id") or 999, x["agent_id"])
    )
    for idx, ag in enumerate(ordered, start=1):
        va = ag.get("va_table") or {}
        a(
            f"### `{ag['agent_id']}` — {ag.get('va_name') or ag['agent_id']} "
            f"(now {ag['score']['maturity_0_to_11']}/11 → target 11.0)"
        )
        a("")
        a(
            f"- **Category:** `{ag.get('va_category')}` · **VA#:** {ag.get('va_id')} · "
            f"**Priority band:** P{priority_rank(ag)}"
        )
        a(
            f"- **Cells:** YES={ag['score']['yes']} PARTIAL={ag['score']['partial']} NO={ag['score']['no']}"
        )
        a(
            f"- **Prompt/rubric:** `{ag.get('prompt_reference')}` / `{ag.get('rubric_reference')}` "
            f"(files {ag.get('prompt_file_count')}/{ag.get('rubric_file_count')})"
        )
        a(
            f"- **Harness:** skill={ag.get('has_skill_harness')} golden={ag.get('has_golden_eval')} "
            f"baseline={ag.get('has_baseline_protocol')} status=`{ag.get('baseline_status')}` "
            f"gate_met={ag.get('baseline_gate_met')} synthetic={ag.get('baseline_gate_synthetic')}"
        )
        a(
            f"- **Tools:** `{', '.join(ag.get('allowed_tools') or []) or '(none)'}` · "
            f"live_media={ag.get('live_media_tools')}"
        )
        if va:
            a(f"- **Design surpass signal:** {short(va.get('surpass_human_signal', ''), 160)}")
            a(f"- **Design self-quality:** {short(va.get('self_quality_criteria', ''), 140)}")
            a(f"- **Design architecture:** {short(va.get('architecture_pattern', ''), 120)}")
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
        for qid, title, st, acts in remaining_actions(ag):
            a(f"**{title}** (now {st.upper()} → YES)")
            a("")
            for act in acts:
                a(f"- [ ] {act}")
            a("")
        a("#### Exit gate for this agent")
        a("")
        a(f"- [ ] Offline golden still passes for `{ag['agent_id']}`")
        a("- [ ] PackAgentLoader loads prompt+rubric+skill")
        a("- [ ] Real human n≥5, synthetic=false")
        a("- [ ] evaluate_gate → met=true")
        a("- [ ] human_baseline_evidence.json claim_allowed_in_ui true")
        a(
            f"- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `{ag['agent_id']}`"
        )
        a("")

    a("---")
    a("")
    a("## 10. Implementation queue (priority order)")
    a("")
    a("| Order | Band | Agent | Now | Why |")
    a("|------:|------|-------|-----|-----|")
    why = {
        0: "Spine — rate humans first; unlock collab trust",
        1: "Remaining Meta",
        2: "ATL creative authority",
        3: "Live media agents — careful baselines",
        4: "Core craft production",
        5: "Specialized craft / AI-era",
        6: "Support & long-tail",
    }
    for i, ag in enumerate(ordered, start=1):
        a(
            f"| {i} | P{priority_rank(ag)} | `{ag['agent_id']}` | "
            f"{ag['score']['maturity_0_to_11']} | {why[priority_rank(ag)]} |"
        )
    a("")
    a("---")
    a("")
    a("## 11. Operator commands (copy/paste)")
    a("")
    a("```bash")
    a("# Dashboard")
    a("python scripts/business/baseline_status.py")
    a("")
    a("# Rater packs")
    a("python scripts/business/prepare_rater_sessions_v1.py")
    a("")
    a("# Clear synthetic spine before real humans")
    a("python scripts/business/record_human_baseline.py --clear-synthetic --agents \\")
    a("  video.orchestrator video.planner video.router video.judge \\")
    a("  video.gatekeeper video.critic video.memory")
    a("")
    a("# Real session")
    a("python scripts/business/record_human_baseline.py --session \\")
    a("  --agent video.orchestrator --rater alice --evaluate")
    a("")
    a("# Spine golden regression")
    a("python scripts/business/run_pack_agent_golden.py --spine")
    a("")
    a("# Refresh audits / this plan")
    a("python scripts/business/audit_agent_capability_status.py")
    a("python scripts/business/render_agent_capability_status_v2.py")
    a("python scripts/business/report_improvement_plan_completion.py")
    a("python scripts/business/render_agent_improvement_plan_v2.py")
    a("```")
    a("")
    a("---")
    a("")
    a("## 12. Estimation (remaining)")
    a("")
    a("| Work item | Unit | Count | Notes |")
    a("|-----------|------|------:|-------|")
    a("| Real human trial sets | agent | 114 | ≥5 trials each; main cost |")
    a("| Gate evaluations | agent | 114 | automated after trials |")
    a("| Re-measure agent offline | agent | as needed | after prompt changes |")
    a("| Optional tool mocks | tool class | ~20–40 | not required for Q5 YES |")
    a("")
    a("**Calendar hint:** Spine (7) → ATL (5) → batches of 10 craft agents per rater week.")
    a("")
    a("---")
    a("")
    a("## 13. Governance (prevent fake full marks)")
    a("")
    a("1. **No Q5 YES without evidence** — audit reads gate.met && !synthetic.")
    a("2. **record_human_baseline.py refuses --synthetic** for real sessions.")
    a("3. **Golden must stay green** after any prompt/rubric change.")
    a("4. **HiTL confirms use action refs only** in product UI.")
    a("5. **Completion reports** must show claimable surpass count, not just protocol files.")
    a("")
    a("---")
    a("")
    a("## 14. Regeneration")
    a("")
    a("```bash")
    a("python scripts/business/audit_agent_capability_status.py")
    a("python scripts/business/render_agent_capability_status_v2.py")
    a("python scripts/business/render_agent_improvement_plan_v2.py")
    a("```")
    a("")
    a(
        f"Track progress: maturity **{g['avg_maturity']} → 11.0**, "
        f"weighted **{weighted_pct:.2f}% → 100%**, Q5 YES **{q5_yes} → {n}**."
    )
    a("")

    _OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {_OUT} lines={len(lines)} bytes={_OUT.stat().st_size}")
    print(f"Full mark gap: Q5 remaining {q5_partial + q5_no}/{n}; weighted {weighted_pct:.2f}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
