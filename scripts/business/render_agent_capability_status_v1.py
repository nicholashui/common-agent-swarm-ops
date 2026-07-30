#!/usr/bin/env python3
"""Render agent_capability_status_v1.md from AGENT_CAPABILITY_AUDIT.json."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_AUDIT = _ROOT / "business" / "video" / "AGENT_CAPABILITY_AUDIT.json"
_OUT = _ROOT / "agent_capability_status_v1.md"

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


def status_cell(s: str) -> str:
    return STATUS_ICON.get(s, s.upper())


def short_note(note: str, limit: int = 220) -> str:
    n = " ".join(note.split())
    return n if len(n) <= limit else n[: limit - 1] + "…"


def main() -> int:
    data = json.loads(_AUDIT.read_text(encoding="utf-8"))
    g = data["global_summary"]
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    lines: list[str] = []
    a = lines.append

    a("# Agent Capability Status Report v1")
    a("")
    a(f"**Generated:** {now}  ")
    a(f"**Canonical design source:** `{data['agents_md_source']}` (`va-agent-swarm/study/agents.md`)  ")
    a(f"**Implementation pack:** `{data['pack_root']}` (non-special video agents; **{data['agent_count']}** agents)  ")
    a(f"**VA table rows matched:** {data['va_table_row_count']}  ")
    a(f"**Audit artifact:** `business/video/AGENT_CAPABILITY_AUDIT.json`")
    a("")
    a("> **Honesty bar:** Design claims in `agents.md` describe a target professional multi-agent studio. This report grades **what is actually present** in the common host pack (SPEC, sources, tools, prompts, rubrics, graphs) versus those claims. Aspirational text ≠ production capability.")
    a("")
    a("---")
    a("")
    a("## 0. Executive answers (fleet-wide)")
    a("")
    a("| # | Question | Fleet answer | Evidence snapshot |")
    a("|---|----------|--------------|-------------------|")
    a(
        f"| 1 | Responsibility in SPEC | **Mostly YES** | {g['agents_responsibility_strong']}/{data['agent_count']} agents have strong `## Responsibility` text |"
    )
    a(
        "| 2 | Knowledge distillation plan | **PARTIAL** | Every VA row lists Knowledge Distillation Source; SPEC embeds common structure; continuous distillation loop not fully automated |"
    )
    a(
        f"| 3 | Sources available / how to get | **PARTIAL** | Sources folders + PROVENANCE/MAPPING common; licensed live corpora not fully acquired; median local files present |"
    )
    a(
        f"| 4 | Self-evaluation content | **PARTIAL (design-heavy)** | agents.md Self-Quality Criteria + SPEC quality gates present; **{g['agents_with_rubric_files']}/{data['agent_count']}** agents have non-empty `rubrics/` files |"
    )
    a(
        f"| 5 | Surpass human yet? | **NO** | **0** agents have validated human-surpass measurements in host. Design surpass signals are aspirational only |"
    )
    a(
        f"| 6 | How they execute | **PARTIAL — host-orchestrated** | Graph/DNA + host adapters; **{g['agents_with_live_media_tools']}** agents have live media tools; **{g['agents_with_prompt_files']}** have materialized prompt files; not free-running coding-plan agents by default |"
    )
    a(
        "| 7 | Skills/plugins/harness | **PARTIAL (shared pack skills)** | Pack `special_skills/` + host adapters exist; per-agent private skill install harness largely missing |"
    )
    a(
        "| 8 | Self-improvement mechanism | **PARTIAL** | SPEC Continuous Learning + `max_refinement_count`; closed-loop RLAIF/promote not fully productized per agent |"
    )
    a(
        "| 9 | Research path to improve | **PARTIAL** | Source lists + research/meta agents designed; automated research→eval→promote incomplete |"
    )
    a(
        "| 10 | Collaborate / instruct others | **PARTIAL** | `critique_edges` + handoff design + workflow DNA; full runtime critique bus not complete for all |"
    )
    a(
        "| 11 | Conflict resolve + confirm | **PARTIAL** | Design: dispute → Judge → HiTL; autonomous resolve+confirm not proven per agent |"
    )
    a("")
    a(f"**Average maturity score (0–11):** **{g['avg_maturity']}**  ")
    a(
        f"**Cell counts (114×11):** YES={g['status_counts']['yes']}, PARTIAL={g['status_counts']['partial']}, NO={g['status_counts']['no']}"
    )
    a("")
    a("### Critical fleet deficiencies (rethink / improve)")
    a("")
    a("1. **Prompts are not materialised** — `prompt_reference` exists on every agent, but **0** agents have non-empty `prompts/` content files. Execution cannot be role-faithful without real prompts.")
    a("2. **Rubrics are not materialised** — `rubric_reference` exists, but **0** agents have non-empty `rubrics/` content files. L2 craft scoring cannot run.")
    a("3. **Surpass-human claims are design fiction until measured** — do not treat agents.md “Wins ≥55% blind pairwise…” rows as current capability.")
    a("4. **Tools are mostly stubs** — only a small media subset has live adapter allowlists; most craft tools (Resolve/Nuke/Sheets/FAA…) are design text.")
    a("5. **Collab & conflict are schema-first** — edges and SPEC text exist; end-to-end CritiqueMessage bus + Judge + HiTL confirm need completion.")
    a("6. **Self-improvement is documented, not closed-loop** — refinement budgets without durable promote/reject evidence are incomplete.")
    a("")
    a("---")
    a("")
    a("## 1. What `agents.md` requires (VA design contract)")
    a("")
    a("Every agent row in `va-agent-swarm/study/agents.md` defines eight columns:")
    a("")
    a("| Column | Maps to question | Meaning |")
    a("|--------|------------------|---------|")
    a("| Responsibility | Q1 | Single craft ownership boundary |")
    a("| Knowledge Distillation Source | Q2–Q3, Q9 | Where professional knowledge comes from |")
    a("| Self-Quality Criteria | Q4 | How the agent judges its own output |")
    a("| Surpass-Human Signal | Q5 | Target human-parity/surpass metric (aspirational) |")
    a("| Accepts Critique From / Comments On | Q10–Q11 | Peer critique topology |")
    a("| Tool Access | Q6–Q7 | External tools / generators / DCC bridges |")
    a("| Architecture Pattern | Q6, Q8 | Self-Refine, ReAct, Debate, Agentic Graph, etc. |")
    a("")
    a("Section **§11 Common Structure** additionally requires for *every* agent: Identity, Responsibility, Knowledge source, Tool access, Architecture pattern, Memory, Constitution/Rubric, L1 Spec / L2 Rubric / L3 Preference gates, Critique inbox, Continuous learning, Handoff contracts, HiTL escalation.")
    a("")
    a("**Implication:** If an item exists only in `agents.md` but not as executable pack artifacts (`SPEC` + `prompts/` + `rubrics/` + tools + eval fixtures + host graph wiring), status is **PARTIAL** or **NO**, not YES.")
    a("")
    a("---")
    a("")
    a("## 2. Cross-cutting deep answers (Q1–Q11)")
    a("")
    a("### Q1 — How to ensure each agent knows Responsibility (well defined in SPEC.md)")
    a("")
    a("**Current state:** Strong. Pack SPECs include a `## Responsibility` section for all 114 agents (often distilled from VA tables + common structure). `agent_spec.json` also stores `role`, `va_name`, `va_id`, `va_category`.")
    a("")
    a("**How to ensure (recommended control system):**")
    a("")
    a("1. **Single source of truth chain:** `agents.md` row → `agent_spec.json.role` → `SPEC.md ## Responsibility` → `docs/user_guide.md` opening line (must match).")
    a("2. **Machine gate:** CI check that every agent has Responsibility ≥ N chars, contains “owns”, and does not copy another agent’s first 40 tokens.")
    a("3. **Operator test:** On Registry agent detail, show Responsibility only from SPEC; fail card generation if missing.")
    a("4. **Runtime identity injection:** Host system prompt must start with responsibility boundary + does-not-own list before tools.")
    a("")
    a("### Q2 — Plan to distill professional knowledge?")
    a("")
    a("**Current state: PARTIAL — yes as design, incomplete as pipeline.**")
    a("")
    a("- VA table lists per-agent Knowledge Distillation Sources (award archives, books, interviews, corpora).")
    a("- SPEC common structure includes Continuous Learning / distillation language.")
    a("- Pack has `corpus/study/`, per-agent `sources/` excerpts, and shared `special_skills/`.")
    a("- Missing: licensed continuous distillation jobs, refresh cadence SLAs, quality gates on new source intake.")
    a("")
    a("### Q3 — Sources present or know how to get them?")
    a("")
    a("**Current state: PARTIAL.**")
    a("")
    a("- Local: `sources/PROVENANCE.json`, `MAPPING.md`, `excerpts/`, sometimes `generic/` SPEC copies.")
    a("- Known-how: agents.md + mapping documents *what* to fetch; they do **not** guarantee legal acquisition, API access, or up-to-date corpora.")
    a("- Gap: many listed sources (MasterClass, DGA, WGA libraries, paid reels) are **not** fully offline-licensed in the pack.")
    a("")
    a("### Q4 — Self-evaluation methods collected?")
    a("")
    a("**Current state: PARTIAL (criteria designed; artifacts empty).**")
    a("")
    a("- Designed: Self-Quality Criteria column + 3-layer gate (Spec→Rubric→Preference) in §11.")
    a("- Pack: `rubric_reference` IDs + occasional pack-level evals under `business/video/evals/`.")
    a("- Gap: **zero** per-agent non-empty `rubrics/` files → L2 craft scoring not executable per role.")
    a("")
    a("### Q5 — Surpass human yet?")
    a("")
    a("**Answer: NO for all agents.**")
    a("")
    a("Design signals (e.g., “Wins ≥55% blind pairwise vs DGA cuts”) are **targets**, not measured host results. No agent has a published evidence bundle proving human-surpass under controlled evaluation in this repo.")
    a("")
    a("### Q6 — How do they execute their job?")
    a("")
    a("| Layer | What exists today | What does not |")
    a("|-------|-------------------|---------------|")
    a("| Host orchestration | Workflow DNA / graphs, product APIs, registry | Full CrewAI/LangGraph parity with every tool in agents.md |")
    a("| LLM calls | Host model policy fields; media providers when env enabled | Per-agent hardened system prompts on disk |")
    a("| Tools | Subset of `media.*` adapters (Sora/Veo/Runway/ElevenLabs) | Most DCC MCP bridges, Sheets, FAA, etc. |")
    a("| Coding plan agents | Special skills / specials pack designs | Per-video-agent autonomous coding agents |")
    a("| Deterministic path | Fail-closed without production flags | Always-on live generation |")
    a("")
    a("**Default execution path today:** Host selects agents via roster/workflow map → runs graph node → may call allowlisted tool or local deterministic path → records evidence. **Not** “each agent independently runs a coding plan.”")
    a("")
    a("### Q7 — Skills / plugins / harness for themselves?")
    a("")
    a("**PARTIAL.** Shared pack skills live under `business/video/special_skills/` and specials agents under `business/specials/agents/`. Individual video agents generally do **not** own private installed plugin trees; they inherit host + pack harness.")
    a("")
    a("### Q8 — Mechanism to improve themselves?")
    a("")
    a("**PARTIAL.** SPEC describes continuous learning (bootstrap → expert → RLAIF → red-team → 30/60/90). `max_refinement_count` exists. Missing: durable self-improvement controller that writes new prompt/rubric versions with eval proof.")
    a("")
    a("### Q9 — Know how to collect/research info to improve?")
    a("")
    a("**PARTIAL.** Research/meta agents (WebResearch, BenchmarkResearch, TrendIntelligence, etc.) encode *how* in design. Operational “research → distill → eval → promote” is not complete for every craft agent.")
    a("")
    a("### Q10 — Get/send instructions in collaboration?")
    a("")
    a("**PARTIAL.**")
    a("")
    a("- Designed: Accepts Critique From / Comments On matrix; CritiqueMessage schema; handoffs.")
    a("- Pack: `critique_edges.inputs/outputs` on `agent_spec.json`; workflow DNA nodes; orchestrator/planner entry agents.")
    a("- Gap: universal runtime bus + guaranteed delivery/ack for every agent pair.")
    a("")
    a("### Q11 — Resolve conflict themselves and confirm?")
    a("")
    a("**PARTIAL.** Design path: blocker/major/minor → Self-Refine → multi-agent debate / JudgeAgent → HiTL if unresolved. Host must still implement severity routing and human confirm gates as first-class APIs for all packs.")
    a("")
    a("---")
    a("")
    a("## 3. Per-group status")
    a("")
    a("| Group | Label | Agents | Avg maturity (0–11) | Strongest area | Weakest area | Group priority actions |")
    a("|-------|-------|--------|---------------------|----------------|--------------|------------------------|")

    for cat, group in data["groups"].items():
        agents = group["agents"]
        # weak dimension: most NOs/partials
        dim_scores = {qk: 0.0 for qk, _ in Q_ORDER}
        for ag in agents:
            for qk, _ in Q_ORDER:
                st = ag["questions"][qk]["status"]
                dim_scores[qk] += 1.0 if st == "yes" else 0.5 if st == "partial" else 0.0
        best = max(dim_scores, key=dim_scores.get)
        worst = min(dim_scores, key=dim_scores.get)
        best_l = dict(Q_ORDER)[best]
        worst_l = dict(Q_ORDER)[worst]
        priority = {
            "1-ATL": "Materialize director/producer/screenwriter prompts+rubrics; wire greenlight HiTL; live media tools only with consent gates.",
            "2-Cam": "Camera-path tool adapters + safety constitution tests (esp. drone); aesthetic scoring harness.",
            "3-Edit": "Resolve/FFmpeg bridges for editor/color; Murch/12-principles rubrics as executable JSON.",
            "4-Snd": "ElevenLabs/loudness tool path; LUFS validators as L1; mix deliverable schemas.",
            "5-Perf": "Consent/likeness policy gates; choreography/timing rubrics; avoid unconsented voice clone activation.",
            "6-Dist": "Brand/compliance validators; platform-spec checklists; marketing metrics evals.",
            "7-Edu": "Domain-fact checkers + SME HiTL; localization/accessibility rubrics first-class.",
            "8-AI": "Prompt/avatar/voice-clone tools already closest to live — add red-team + deepfake gates before scale.",
            "9-Meta": "Finish orchestrator/planner/router/judge runtime as platform spine; critique bus before craft scale-out.",
            "10-Sup": "Support agents need explicit SLAs + data contracts; many tools still design-only.",
        }.get(cat, "Materialize prompts/rubrics; prove one golden eval.")
        a(
            f"| `{cat}` | {group['label']} | {group['count']} | **{group['avg_maturity']}** | {best_l} | {worst_l} | {priority} |"
        )

    a("")
    a("---")
    a("")
    a("## 4. Per-agent detailed status (by group)")
    a("")
    a("Legend: **YES** = present/usable at pack level · **PARTIAL** = designed or incomplete · **NO** = missing / not achieved.")
    a("")

    for cat, group in data["groups"].items():
        a(f"### {cat} — {group['label']} ({group['count']} agents, avg maturity {group['avg_maturity']})")
        a("")
        a(
            "#### Group synthesis"
        )
        a("")
        # compute group-level Q status mode
        for qk, ql in Q_ORDER:
            counts = {"yes": 0, "partial": 0, "no": 0}
            for ag in group["agents"]:
                counts[ag["questions"][qk]["status"]] += 1
            mode = max(counts, key=counts.get)
            a(
                f"- **{ql}:** dominant **{status_cell(mode)}** (Y={counts['yes']}, P={counts['partial']}, N={counts['no']})"
            )
        a("")
        a(
            "#### Agents"
        )
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
                f"- **Status / provider / network:** `{ag.get('status')}` / `{ag.get('provider')}` / network={ag.get('network_access')}  "
            )
            a(
                f"- **Tools:** `{', '.join(ag.get('allowed_tools') or []) or '(none)'}`  "
            )
            a(
                f"- **Prompt ref / files:** `{ag.get('prompt_reference') or '—'}` / files={ag.get('prompt_file_count')}  "
            )
            a(
                f"- **Rubric ref / files:** `{ag.get('rubric_reference') or '—'}` / files={ag.get('rubric_file_count')}  "
            )
            a(
                f"- **Sources / provenance:** files={ag.get('source_file_count')} · PROVENANCE={ag.get('has_provenance')} · MAPPING={ag.get('has_mapping')}  "
            )
            a(
                f"- **Critique edges:** `{json.dumps(ag.get('critique_edges') or {}, ensure_ascii=False)}`  "
            )
            a(
                f"- **Maturity:** {ag['score']['maturity_0_to_11']}/11 (Y={ag['score']['yes']} P={ag['score']['partial']} N={ag['score']['no']})  "
            )
            a(
                f"- **SPEC responsibility excerpt:** {short_note(ag.get('responsibility_excerpt') or '(missing)', 280)}"
            )
            if va:
                a("")
                a("**From `agents.md` design row:**")
                a("")
                a(f"- Responsibility: {short_note(va.get('responsibility',''), 200)}")
                a(
                    f"- Knowledge distillation source: {short_note(va.get('knowledge_distillation_source',''), 200)}"
                )
                a(
                    f"- Self-quality criteria: {short_note(va.get('self_quality_criteria',''), 200)}"
                )
                a(
                    f"- Surpass-human signal (aspirational): {short_note(va.get('surpass_human_signal',''), 180)}"
                )
                a(
                    f"- Accepts critique from: {short_note(va.get('accepts_critique_from',''), 160)}"
                )
                a(f"- Comments on: {short_note(va.get('comments_on',''), 160)}")
                a(f"- Tool access (design): {short_note(va.get('tool_access',''), 180)}")
                a(
                    f"- Architecture pattern (design): {short_note(va.get('architecture_pattern',''), 160)}"
                )

            a("")
            a("| Q | Status | Assessment |")
            a("|---|--------|------------|")
            for qk, ql in Q_ORDER:
                cell = ag["questions"][qk]
                a(
                    f"| {ql} | **{status_cell(cell['status'])}** | {short_note(cell['notes'], 260)} |"
                )

            a("")
            a("**Deficiencies & suggestions (improve):**")
            a("")
            if ag.get("suggestions"):
                for s in ag["suggestions"]:
                    a(f"- {s}")
            else:
                a("- Maintain current artifacts; add measured eval evidence before claiming higher maturity.")
            a("")
            # agent-specific rethink bullets
            a("**Rethink / raise the bar:**")
            a("")
            a(
                f"1. Freeze a **golden task** for `{ag['agent_id']}` (input brief → expected artifact schema → L1/L2 thresholds from agents.md)."
            )
            a(
                "2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose."
            )
            a(
                "3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs."
            )
            a(
                "4. Record **human baseline** on the same golden task; never claim surpass without that delta."
            )
            a("")

    a("---")
    a("")
    a("## 5. Implementation roadmap (fleet)")
    a("")
    a("### Wave A — Make responsibility & evaluation real (2–3 weeks)")
    a("")
    a("1. Generate `prompts/*.md` + `rubrics/*.json` for all 114 agents from agents.md columns + architecture patterns.")
    a("2. CI gate: forbid empty prompts/rubrics directories.")
    a("3. Golden evals for spine agents: orchestrator, planner, director, editor, critic, judge.")
    a("")
    a("### Wave B — Collaboration & conflict bus (2–4 weeks)")
    a("")
    a("1. Implement CritiqueMessage schema as host API with severity.")
    a("2. Wire `critique_edges` as enforceable routes.")
    a("3. JudgeAgent multi-agent debate + HiTL confirm for blockers.")
    a("")
    a("### Wave C — Tools & knowledge legality (ongoing)")
    a("")
    a("1. Prioritize tool adapters that unlock craft value (media already started; editor/color/sound next).")
    a("2. Source acquisition SOP: license, refresh, quarantine, hash lock.")
    a("3. Distillation loop jobs per category, starting with 9-Meta research agents.")
    a("")
    a("### Wave D — Measured quality (continuous)")
    a("")
    a("1. Human baseline capture for top 20 revenue-critical agents.")
    a("2. Publish dashboards: L1 pass rate, L2 rubric, preference win-rate vs human.")
    a("3. Only then revisit “surpass human” claims per agent.")
    a("")
    a("---")
    a("")
    a("## 6. Special notes")
    a("")
    a("- **Specials pack** (`business/specials`) is intentionally out of the video roster tables in this report; treat as shared platform skills, not video craft org nodes.")
    a("- **Production activation** for media is env-gated (`CASOPS_VIDEO_PRODUCTION_ENABLED` + credentials). Fail-closed is correct; it is not the same as craft readiness.")
    a("- **Org Chart UI** visualizes hierarchy; it does not execute agents.")
    a("")
    a("---")
    a("")
    a("## 7. Regeneration")
    a("")
    a("```bash")
    a("python scripts/business/audit_agent_capability_status.py")
    a("python scripts/business/render_agent_capability_status_v1.py")
    a("```")
    a("")
    a("Outputs:")
    a("")
    a("- `business/video/AGENT_CAPABILITY_AUDIT.json`")
    a("- `agent_capability_status_v1.md` (this file)")
    a("")

    _OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {_OUT} lines={len(lines)} bytes={_OUT.stat().st_size}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
