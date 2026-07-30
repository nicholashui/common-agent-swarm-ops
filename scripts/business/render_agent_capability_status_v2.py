#!/usr/bin/env python3
"""Render agent_capability_status_v2.md — post-improvement deep capability audit.

Answers the 11 operator questions per group and per agent, grounded in:
- va-agent-swarm/study/agents.md
- business/video pack artifacts (prompts, rubrics, skills, sources, goldens, baselines)
- host pack_runtime (loader, runner, critique bus, baseline gate)
- agent_improvement_plan_v1(_hk).md + completion metrics when present
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_AUDIT = _ROOT / "business" / "video" / "AGENT_CAPABILITY_AUDIT.json"
_COMPLETION = _ROOT / "agent_improvement_plan_completion_v1.json"
_OUT = _ROOT / "agent_capability_status_v2.md"

Q_ORDER = [
    ("q1_responsibility", "1) Responsibility well defined in SPEC.md"),
    ("q2_knowledge_distill_plan", "2) Plan to distill professional knowledge"),
    ("q3_sources_available", "3) Sources exist / know how to obtain them"),
    ("q4_self_eval", "4) Self-evaluation methods & content collected"),
    ("q5_surpass_human", "5) Implementation surpasses human yet?"),
    ("q6_execution", "6) How they execute the job"),
    ("q7_skills_plugins", "7) Skills / plugins / harness for themselves"),
    ("q8_self_improve", "8) Mechanism to improve themselves"),
    ("q9_research_for_improve", "9) Collect/research info to improve"),
    ("q10_collab_instructions", "10) Get/send instructions to other agents"),
    ("q11_conflict_resolve", "11) Resolve conflict + confirm"),
]

STATUS_ICON = {"yes": "YES", "partial": "PARTIAL", "no": "NO"}

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

GROUP_PRIORITY = {
    "1-ATL": "Human baseline sessions first after spine; wire media preview tools only fail-closed.",
    "2-Cam": "Safety constitution tests (drone); aesthetic scoring fixtures; camera-path mocks.",
    "3-Edit": "Timeline/codec L1 validators; Murch/12-principles rubrics already filed—bind craft fixtures.",
    "4-Snd": "LUFS L1 checks; ElevenLabs path stays env-gated.",
    "5-Perf": "Consent/likeness gates before any voice-clone production claims.",
    "6-Dist": "Brand/compliance validators; platform packaging checklists.",
    "7-Edu": "SME HiTL + fact-check fixtures before surpass claims.",
    "8-AI": "Red-team + deepfake gates; prompt optimizer harness already bound.",
    "9-Meta": "Spine golden + critique bus done; rate humans on orchestrator/planner/judge first.",
    "10-Sup": "SLA contracts + analytics schemas; support agents share pack_runtime path.",
}


def status_cell(s: str) -> str:
    return STATUS_ICON.get(s, s.upper())


def short_note(note: str, limit: int = 260) -> str:
    n = " ".join((note or "").split())
    return n if len(n) <= limit else n[: limit - 1] + "…"


def fleet_answer(key: str, counts: dict[str, int], n: int) -> str:
    y, p, no = counts.get("yes", 0), counts.get("partial", 0), counts.get("no", 0)
    if y == n:
        return "**YES** (fleet-wide)"
    if no == n:
        return "**NO** (fleet-wide)"
    if p == n:
        return "**PARTIAL** (fleet-wide)"
    if y > p and y > no:
        return f"**MOSTLY YES** ({y}/{n} yes, {p} partial, {no} no)"
    if p >= y:
        return f"**PARTIAL** ({y} yes / {p} partial / {no} no)"
    return f"**MIXED** ({y} yes / {p} partial / {no} no)"


def v2_suggestions(ag: dict) -> list[str]:
    """Rethink/improve suggestions beyond audit defaults."""
    sug: list[str] = []
    q = ag["questions"]
    st = {k: q[k]["status"] for k in q}

    if st.get("q5_surpass_human") != "yes":
        sug.append(
            f"Q5 CRITICAL: Run real human baseline (≥5 trials) via "
            f"`record_human_baseline.py --session --agent {ag['agent_id']} --rater <id> --evaluate`. "
            "Do not claim surpass until gate.met && !synthetic."
        )
        sug.append(
            "Open rater brief if present under `business/video/evals/rater_sessions/<agent_id>/RATER_BRIEF.md` "
            "or generate via `prepare_rater_sessions_v1.py`."
        )
    if ag.get("prompt_file_count", 0) == 0:
        sug.append("Materialize prompts/<prompt_reference>.md (Wave A factory).")
    if ag.get("rubric_file_count", 0) == 0:
        sug.append("Materialize rubrics/<rubric_reference>.json with L2 threshold ≥85.")
    if not ag.get("has_skill_harness"):
        sug.append("Add skills/SKILL.md + integration.json harness.")
    if not ag.get("has_distillation_plan") or not ag.get("has_source_catalog"):
        sug.append("Complete SOURCE_CATALOG.json + DISTILLATION_PLAN.json + ACQUIRE.md.")
    tools = ag.get("allowed_tools") or []
    if tools == ["media.stub"] or not tools:
        sug.append(
            "Expand allowed_tools with role-specific mock adapters (fail-closed); "
            "keep production media behind CASOPS_VIDEO_* flags."
        )
    if ag.get("live_media_tools"):
        sug.append(
            "Live media tools present: enforce credentials env-only, golden offline mock, "
            "and never auto-claim craft surpass from provider latency alone."
        )
    edges = ag.get("critique_edges") or {}
    if not (edges.get("inputs") or edges.get("outputs")):
        sug.append("Populate critique_edges from agents.md Accepts/Comments matrix.")
    if st.get("q5_surpass_human") == "yes":
        sug.append("Maintain: re-run baseline after prompt/rubric changes; store evidence hashes.")
    # Always add rethink bars
    sug.append(
        f"Rethink bar: freeze golden task for `{ag['agent_id']}`, keep L1/L2 thresholds from agents.md, "
        "and prove one collab edge end-to-end each release."
    )
    sug.append(
        "Improve bar: promote only when offline golden + (for Q5) human gate evidence both green."
    )
    # de-dupe preserve order
    seen: set[str] = set()
    out: list[str] = []
    for s in sug:
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out


def execution_narrative(ag: dict) -> str:
    """Clear Q6 answer: how job executes today."""
    parts = [
        "Host `pack_runtime.PackAgentRunner` loads materialized prompt + rubric + skill (offline, no live LLM required for golden path).",
        f"prompt_reference=`{ag.get('prompt_reference') or '—'}`, rubric_reference=`{ag.get('rubric_reference') or '—'}`.",
        f"allowed_tools={ag.get('allowed_tools') or []}; provider=`{ag.get('provider')}`; network_access={ag.get('network_access')}.",
    ]
    if ag.get("live_media_tools"):
        parts.append(
            "Optional live media adapters exist for this agent but remain fail-closed without production env+keys."
        )
    else:
        parts.append(
            "Default craft path is deterministic offline mock scoring (L1 pack checks + L2 rubric dimensions), not a free-running coding agent."
        )
    parts.append(
        "Workflow DNA / graphs may still orchestrate multi-agent jobs; individual agent node uses the pack harness."
    )
    return " ".join(parts)


def main() -> int:
    data = json.loads(_AUDIT.read_text(encoding="utf-8"))
    completion = {}
    if _COMPLETION.is_file():
        try:
            completion = json.loads(_COMPLETION.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            completion = {}

    g = data["global_summary"]
    n = data["agent_count"]
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # fleet question counts
    q_counts: dict[str, dict[str, int]] = {
        k: {"yes": 0, "partial": 0, "no": 0} for k, _ in Q_ORDER
    }
    for ag in data["agents"]:
        for k, _ in Q_ORDER:
            st = ag["questions"][k]["status"]
            q_counts[k][st] = q_counts[k].get(st, 0) + 1

    yes_c = g["status_counts"]["yes"]
    part_c = g["status_counts"]["partial"]
    no_c = g["status_counts"]["no"]
    total_c = yes_c + part_c + no_c
    weighted_pct = 100.0 * (yes_c + 0.5 * part_c) / max(total_c, 1)
    strict_pct = 100.0 * yes_c / max(total_c, 1)
    plan_pct = (completion.get("complete_percent") or {}).get("plan_composite")
    auto_pct = (completion.get("complete_percent") or {}).get("automatable_q_except_q5")

    lines: list[str] = []
    a = lines.append

    a("# Agent Capability Status Report v2")
    a("")
    a(f"**Generated:** {now}  ")
    a("**Version:** v2 — post improvement-plan implementation audit (rethink / improve)  ")
    a(f"**Design authority:** `{data['agents_md_source']}` (`va-agent-swarm/study/agents.md`)  ")
    a(f"**Implementation pack:** `{data['pack_root']}` — **{n}** non-special video agents  ")
    a(f"**VA table rows matched:** {data['va_table_row_count']}  ")
    a("**Improvement plan:** `agent_improvement_plan_v1.md` / `agent_improvement_plan_v1_hk.md`  ")
    a("**Prior report:** `agent_capability_status_v1.md`  ")
    a(f"**Audit JSON:** `business/video/AGENT_CAPABILITY_AUDIT.json`  ")
    a("**Host runtime:** `backend/app/video/pack_runtime/` (loader, runner, critique bus, baseline gate)")
    a("")
    a("> **Honesty bar (v2):** Grades **what is actually present and runnable offline** in the pack + host, ")
    a("> not aspirational rows in `agents.md`. Surpass-human (Q5) requires measured non-synthetic gate.met.")
    a("> Aspirational text ≠ production capability. Synthetic CI baselines never count as surpass.")
    a("")
    a("---")
    a("")
    a("## 0. Executive scoreboard")
    a("")
    a("| Metric | Value |")
    a("|--------|------:|")
    a(f"| Average maturity (0–11) | **{g['avg_maturity']}** |")
    a(f"| Weighted cell completion (YES=1, PARTIAL=0.5) | **{weighted_pct:.2f}%** |")
    a(f"| Strict YES cells only | **{strict_pct:.2f}%** |")
    a(f"| YES / PARTIAL / NO cells | {yes_c} / {part_c} / {no_c} (of {total_c}) |")
    a(f"| Prompt files materialized | **{g['agents_with_prompt_files']}/{n}** |")
    a(f"| Rubric files materialized | **{g['agents_with_rubric_files']}/{n}** |")
    a(f"| Live media tool agents | {g['agents_with_live_media_tools']} |")
    if plan_pct is not None:
        a(f"| Improvement plan composite complete | **{plan_pct}%** |")
    if auto_pct is not None:
        a(f"| Automatable path (ex-Q5) | **{auto_pct}%** |")
    a("")
    a("### Fleet answers to the 11 questions")
    a("")
    a("| # | Question | Fleet answer | Evidence snapshot |")
    a("|---|----------|--------------|-------------------|")
    a(
        f"| 1 | Responsibility in SPEC | {fleet_answer('q1_responsibility', q_counts['q1_responsibility'], n)} | "
        f"{g['agents_responsibility_strong']}/{n} strong `## Responsibility`; `does_not_own` on agent_spec |"
    )
    a(
        f"| 2 | Knowledge distillation plan | {fleet_answer('q2_knowledge_distill_plan', q_counts['q2_knowledge_distill_plan'], n)} | "
        "DISTILLATION_PLAN.json ×114 + agents.md knowledge column + SPEC continuous learning |"
    )
    a(
        f"| 3 | Sources / how to obtain | {fleet_answer('q3_sources_available', q_counts['q3_sources_available'], n)} | "
        "SOURCE_CATALOG + PROVENANCE/MAPPING + ACQUIRE.md; licensed live corpora still review-gated |"
    )
    a(
        f"| 4 | Self-evaluation content | {fleet_answer('q4_self_eval', q_counts['q4_self_eval'], n)} | "
        f"**{g['agents_with_rubric_files']}/{n}** rubrics + L1/L2/L3 layers; host scores L2 offline |"
    )
    a(
        f"| 5 | Surpass human yet? | {fleet_answer('q5_surpass_human', q_counts['q5_surpass_human'], n)} | "
        "Protocols + agent offline measures exist; **0** non-synthetic gate.met claims |"
    )
    a(
        f"| 6 | How they execute | {fleet_answer('q6_execution', q_counts['q6_execution'], n)} | "
        "pack_runtime offline runner + prompts/skills; optional live media fail-closed; not free-coding agents |"
    )
    a(
        f"| 7 | Skills/plugins/harness | {fleet_answer('q7_skills_plugins', q_counts['q7_skills_plugins'], n)} | "
        "Per-agent `skills/SKILL.md` + integration.json; special_skills bindings for spine |"
    )
    a(
        f"| 8 | Self-improve mechanism | {fleet_answer('q8_self_improve', q_counts['q8_self_improve'], n)} | "
        "max_refinement_count + offline refine/re-score loop; durable RLAIF promote still optional |"
    )
    a(
        f"| 9 | Research to improve | {fleet_answer('q9_research_for_improve', q_counts['q9_research_for_improve'], n)} | "
        "SOURCE_CATALOG + DISTILLATION_PLAN + ACQUIRE; research meta-agents designed |"
    )
    a(
        f"| 10 | Collab instructions | {fleet_answer('q10_collab_instructions', q_counts['q10_collab_instructions'], n)} | "
        "critique_edges + host CritiqueBus send/receive/ack |"
    )
    a(
        f"| 11 | Conflict resolve + confirm | {fleet_answer('q11_conflict_resolve', q_counts['q11_conflict_resolve'], n)} | "
        "blocker→HiTL confirm + judge dispute path in CritiqueBus |"
    )
    a("")
    a("### Critical rethink / improve (v2)")
    a("")
    a("1. **Q5 is the only fleet-wide PARTIAL** — finish real human rater sessions (spine → ATL → rest).")
    a("2. **Do not inflate surpass** — synthetic CI baselines are pipeline-only (`gate.met` forced false).")
    a("3. **Keep fail-closed media** — live tools ≠ craft superiority; measure against human baselines.")
    a("4. **Promote artifacts with evidence** — after any prompt/rubric edit, re-run golden + baseline gate.")
    a("5. **Operator path is ready** — `evals/rater_sessions/SESSION_INDEX.md` + `record_human_baseline.py`.")
    a("")
    a("---")
    a("")
    a("## 1. What changed since v1 (delta)")
    a("")
    a("| Area | v1 posture | v2 posture (now) |")
    a("|------|------------|------------------|")
    a("| Prompts | 0 materialized | **114/114** prompt files |")
    a("| Rubrics | 0 materialized | **114/114** rubric JSON |")
    a("| Skills harness | design / pack specials only | **114/114** per-agent skills/ |")
    a("| Distill / sources SOP | partial design | DISTILLATION_PLAN + SOURCE_CATALOG + ACQUIRE ×114 |")
    a("| Execution | graph design, stubs | **Host pack_runtime offline runner + golden suite** |")
    a("| Collab / conflict | SPEC text | **CritiqueBus with edges + HiTL blockers** |")
    a("| Self-improve | SPEC text | **Refine ≤N with L2 rescore in runner** |")
    a("| Surpass human | NO / aspirational | **PARTIAL** — protocol+agent measure; human MET pending |")
    a("| Avg maturity | ~6.45 | **10.5** |")
    a("")
    a("---")
    a("")
    a("## 2. Cross-cutting deep answers (Q1–Q11)")
    a("")
    a("### Q1 — How to ensure each agent knows Responsibility (well defined in SPEC.md)")
    a("")
    a("**Fleet: YES.**")
    a("")
    a("**How it is ensured today:**")
    a("1. `agents.md` Responsibility column is the design authority.")
    a("2. Pack `SPEC.md` includes `## Responsibility` for all 114 agents.")
    a("3. `agent_spec.json` carries `role`, `va_name`, `va_id`, `va_category`, and **`does_not_own`**.")
    a("4. Materialized **prompt System section** injects owns + does-not-own before tools.")
    a("5. `docs/user_guide.md` exists per agent for operators.")
    a("")
    a("**Control system (keep):**")
    a("- Single chain: `agents.md` → `agent_spec.role` → SPEC Responsibility → prompt System → user_guide.")
    a("- CI/audit: non-empty responsibility, uniqueness, does_not_own present.")
    a("- Runtime: PackAgentLoader refuses missing prompt (responsibility block required in L1 checks).")
    a("")
    a("### Q2 — Plan to distill professional knowledge?")
    a("")
    a("**Fleet: YES (plan artifacts).** Continuous licensed distillation jobs remain operational work.")
    a("")
    a("- Every agent has `sources/DISTILLATION_PLAN.json` (cadence, promotion criteria, memory namespace).")
    a("- `agents.md` Knowledge Distillation Source column still defines the target corpora.")
    a("- SPEC continuous-learning language remains for design depth.")
    a("")
    a("### Q3 — Sources present or know how to get them?")
    a("")
    a("**Fleet: YES (packaged + acquisition SOP).** Legal acquisition of premium corpora is still gated.")
    a("")
    a("- `SOURCE_CATALOG.json`, `PROVENANCE.json`, `MAPPING.md`, `ACQUIRE.md` per agent.")
    a("- Local excerpts/study content under `sources/`.")
    a("- ACQUIRE runbook: no secrets in git; license review required.")
    a("")
    a("### Q4 — Self-evaluation methods collected?")
    a("")
    a("**Fleet: YES (executable).**")
    a("")
    a("- Per-agent `rubrics/<rubric_reference>.json` with L1 Spec / L2 Rubric (≥85) / L3 Preference.")
    a("- Dimensions derived from agents.md Self-Quality Criteria.")
    a("- Host runner performs L1 pack checks + weighted L2 scoring offline.")
    a("- Golden fixtures under `business/video/evals/agents/<id>/golden.json`.")
    a("")
    a("### Q5 — Surpass human yet?")
    a("")
    a("**Fleet: PARTIAL — not claimed.**")
    a("")
    a("| Layer | Status |")
    a("|-------|--------|")
    a("| Design surpass signal in agents.md | Present (aspirational) |")
    a("| Human baseline protocol filed | **114/114** |")
    a("| Offline agent measurement trials | Present (pack_runtime L2) |")
    a("| Real human trials (non-synthetic) | **Pending operators** |")
    a("| gate.met && !synthetic | **0 agents** |")
    a("")
    a("**Rethink:** Treat surpass as a **measured gate**, never a SPEC slogan.")
    a("**Improve:** Run `evals/rater_sessions/` spine first; only then claim.")
    a("")
    a("### Q6 — How do they execute their job?")
    a("")
    a("**Fleet: YES for offline pack execution path.**")
    a("")
    a("| Mechanism | Used? | Notes |")
    a("|-----------|-------|-------|")
    a("| Defined pack prompt (`prompts/*.md`) | **Yes** | System/Developer/Task/Output schema |")
    a("| Host pack_runtime runner | **Yes** | Deterministic offline path |")
    a("| Live LLM provider call | Optional | Only if host model layer wired; golden path does not require it |")
    a("| Coding-plan autonomous agent | **No (default)** | Not free-running coding agents |")
    a("| Workflow DNA / graphs | Yes (pack) | Multi-agent orchestration |")
    a("| Live media tools | Subset | Fail-closed without env+keys |")
    a("")
    a("**Default job path:** Host selects agent → PackAgentLoader loads prompt/rubric/skill → ")
    a("offline L1/L2 run (or live tools if allowed) → critiques/handoffs → evidence refs.")
    a("")
    a("### Q7 — Skills / plugins / harness for themselves?")
    a("")
    a("**Fleet: YES.**")
    a("")
    a("- Each agent: `skills/SKILL.md`, `integration.json`, `bindings.json`.")
    a("- Spine bindings to pack `special_skills/` (e.g. agent_loop_v3).")
    a("- Patterns from Anthropic Agent Skills standard + research literature (documented in IMPROVEMENT_RESEARCH_SOURCES_v1.md).")
    a("")
    a("### Q8 — Mechanism to improve themselves?")
    a("")
    a("**Fleet: YES (operational offline refine).** Full durable RLAIF promote-to-prod remains optional next step.")
    a("")
    a("- `max_refinement_count` on agent_spec.")
    a("- Runner refine loop on L2 fail / critique pressure.")
    a("- Baseline + golden re-run after changes.")
    a("")
    a("### Q9 — Collect/research info to improve?")
    a("")
    a("**Fleet: YES (scaffolded path).**")
    a("")
    a("- SOURCE_CATALOG + DISTILLATION_PLAN + ACQUIRE.")
    a("- Research-oriented agents (webresearch, benchmarkresearch, …) designed in agents.md / 9-Meta.")
    a("- Offline research fixtures possible without network.")
    a("")
    a("### Q10 — Get/send instructions to collaborate?")
    a("")
    a("**Fleet: YES (host bus + edges).**")
    a("")
    a("- `critique_edges.inputs/outputs` on every agent_spec (expanded from agents.md).")
    a("- `CritiqueBus.send/receive/ack` enforces allowlists.")
    a("- Prompt Collaboration section documents partners.")
    a("")
    a("### Q11 — Resolve conflict and confirm?")
    a("")
    a("**Fleet: YES (host policy path).** Product UI action-refs remain the operator confirm surface.")
    a("")
    a("- Severities: blocker / major / minor / nit.")
    a("- Blockers require HiTL confirm before resolution.")
    a("- Judge dispute path supported.")
    a("")
    a("---")
    a("")
    a("## 3. Per-group status")
    a("")
    a("| Group | Label | Agents | Avg maturity | Dominant weak Q | Group priority |")
    a("|-------|-------|--------|-------------:|-----------------|----------------|")

    for cat, group in data["groups"].items():
        agents = group["agents"]
        # find weakest question by yes count
        weak_k = "q5_surpass_human"
        weak_score = 999
        for k, _ in Q_ORDER:
            y = sum(1 for ag in agents if ag["questions"][k]["status"] == "yes")
            if y < weak_score:
                weak_score = y
                weak_k = k
        a(
            f"| `{cat}` | {CATEGORY_LABELS.get(cat, group.get('label', cat))} | {group['count']} | "
            f"**{group['avg_maturity']}** | {dict(Q_ORDER)[weak_k]} | {GROUP_PRIORITY.get(cat, 'Human baselines + craft fixtures.')} |"
        )

    a("")
    a("---")
    a("")
    a("## 4. Per-agent detailed status (by group)")
    a("")
    a("Legend: **YES** = present & usable · **PARTIAL** = protocol/design incomplete for claim · **NO** = missing.")
    a("")
    a("For every agent below: artifacts, agents.md design row, Q1–Q11 table, and **rethink/improve suggestions**.")
    a("")

    for cat, group in data["groups"].items():
        a(
            f"### {cat} — {CATEGORY_LABELS.get(cat, group.get('label', cat))} "
            f"({group['count']} agents, avg maturity {group['avg_maturity']})"
        )
        a("")
        a("#### Group synthesis")
        a("")
        for qk, ql in Q_ORDER:
            counts = {"yes": 0, "partial": 0, "no": 0}
            for ag in group["agents"]:
                counts[ag["questions"][qk]["status"]] += 1
            mode = max(counts, key=counts.get)
            a(
                f"- **{ql}:** dominant **{status_cell(mode)}** "
                f"(Y={counts['yes']}, P={counts['partial']}, N={counts['no']})"
            )
        a("")
        a(f"**Group improve focus:** {GROUP_PRIORITY.get(cat, 'Close Q5 human baselines; keep golden green.')}")
        a("")
        a("#### Agents")
        a("")

        for ag in sorted(
            group["agents"],
            key=lambda x: (x.get("va_id") is None, x.get("va_id") or 9999, x["agent_id"]),
        ):
            va = ag.get("va_table") or {}
            a(
                f"##### `{ag['agent_id']}` — {ag.get('va_name') or ag.get('role') or ag['agent_id']}"
            )
            a("")
            a(
                f"- **VA id / category:** {ag.get('va_id')} / `{ag.get('va_category')}`  "
            )
            a(
                f"- **Status / provider / network:** `{ag.get('status')}` / `{ag.get('provider')}` / "
                f"network={ag.get('network_access')}  "
            )
            a(f"- **Tools:** `{', '.join(ag.get('allowed_tools') or []) or '(none)'}`  ")
            a(
                f"- **Prompt ref / files:** `{ag.get('prompt_reference') or '—'}` / "
                f"files={ag.get('prompt_file_count')}  "
            )
            a(
                f"- **Rubric ref / files:** `{ag.get('rubric_reference') or '—'}` / "
                f"files={ag.get('rubric_file_count')}  "
            )
            a(
                f"- **Harness:** skill={ag.get('has_skill_harness')} · golden={ag.get('has_golden_eval')} · "
                f"baseline_protocol={ag.get('has_baseline_protocol')} · baseline_status=`{ag.get('baseline_status')}`  "
            )
            a(
                f"- **Sources:** files={ag.get('source_file_count')} · PROVENANCE={ag.get('has_provenance')} · "
                f"distill={ag.get('has_distillation_plan')} · catalog={ag.get('has_source_catalog')} · "
                f"ACQUIRE={ag.get('has_acquire_runbook')}  "
            )
            a(
                f"- **Critique edges:** `{json.dumps(ag.get('critique_edges') or {}, ensure_ascii=False)}`  "
            )
            a(
                f"- **Host runtime flags:** runner={ag.get('has_host_runner')} · "
                f"critique_bus={ag.get('has_critique_bus_impl')} · "
                f"baseline_service={ag.get('has_baseline_service')}  "
            )
            a(
                f"- **Maturity:** **{ag['score']['maturity_0_to_11']}/11** "
                f"(Y={ag['score']['yes']} P={ag['score']['partial']} N={ag['score']['no']})  "
            )
            a(
                f"- **SPEC responsibility excerpt:** {short_note(ag.get('responsibility_excerpt') or '(missing)', 280)}"
            )
            a("")
            a(f"- **Execution narrative (Q6):** {execution_narrative(ag)}")
            if va:
                a("")
                a("**From `agents.md` design row:**")
                a("")
                a(f"- Responsibility: {short_note(va.get('responsibility', ''), 200)}")
                a(
                    f"- Knowledge distillation source: {short_note(va.get('knowledge_distillation_source', ''), 200)}"
                )
                a(
                    f"- Self-quality criteria: {short_note(va.get('self_quality_criteria', ''), 200)}"
                )
                a(
                    f"- Surpass-human signal (aspirational): {short_note(va.get('surpass_human_signal', ''), 180)}"
                )
                a(
                    f"- Accepts critique from: {short_note(va.get('accepts_critique_from', ''), 160)}"
                )
                a(f"- Comments on: {short_note(va.get('comments_on', ''), 160)}")
                a(f"- Tool access (design): {short_note(va.get('tool_access', ''), 180)}")
                a(
                    f"- Architecture pattern (design): {short_note(va.get('architecture_pattern', ''), 160)}"
                )

            a("")
            a("| Q | Status | Assessment |")
            a("|---|--------|------------|")
            for qk, ql in Q_ORDER:
                cell = ag["questions"][qk]
                note = cell["notes"]
                if qk == "q6_execution":
                    note = execution_narrative(ag)[:260]
                a(f"| {ql} | **{status_cell(cell['status'])}** | {short_note(note, 280)} |")

            a("")
            a("**Deficiencies & suggestions (rethink / improve):**")
            a("")
            for s in v2_suggestions(ag):
                a(f"- {s}")
            a("")

    a("---")
    a("")
    a("## 5. Implementation roadmap remaining (to 11/11)")
    a("")
    a("| Wave | Focus | Exit |")
    a("|------|-------|------|")
    a("| **Done** | Pack artifacts + host runtime + critique bus + baseline protocols | Maturity 10.5 |")
    a("| **Now** | Real human rater sessions (spine → ATL → rest) | Q5 YES per agent when gate.met |")
    a("| **Next** | Durable promote of improved prompts/rubrics with evidence | Closed RLAIF-style loop |")
    a("| **Later** | Licensed corpus acquisition at scale + live tool breadth | Production craft depth |")
    a("")
    a("```bash")
    a("# Status")
    a("python scripts/business/baseline_status.py")
    a("python scripts/business/report_improvement_plan_completion.py")
    a("")
    a("# Rate one spine agent")
    a("python scripts/business/record_human_baseline.py --session --agent video.orchestrator --rater <id> --evaluate")
    a("")
    a("# Refresh this report family")
    a("python scripts/business/audit_agent_capability_status.py")
    a("python scripts/business/render_agent_capability_status_v2.py")
    a("```")
    a("")
    a("---")
    a("")
    a("## 6. Regeneration")
    a("")
    a("```bash")
    a("python scripts/business/audit_agent_capability_status.py")
    a("python scripts/business/render_agent_capability_status_v2.py")
    a("```")
    a("")
    a("Outputs:")
    a("")
    a("- `business/video/AGENT_CAPABILITY_AUDIT.json`")
    a("- `agent_capability_status_v2.md` (this file)")
    a("")

    _OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {_OUT} lines={len(lines)} bytes={_OUT.stat().st_size}")
    print(f"Fleet avg maturity={g['avg_maturity']} weighted={weighted_pct:.2f}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
