# Agent Capability Status Report v1

**Generated:** 2026-07-30T04:18:07Z  
**Canonical design source:** `C:\Project\va-agent-swarm\study\agents.md` (`va-agent-swarm/study/agents.md`)  
**Implementation pack:** `business/video/agents` (non-special video agents; **114** agents)  
**VA table rows matched:** 114  
**Audit artifact:** `business/video/AGENT_CAPABILITY_AUDIT.json`

> **Honesty bar:** Design claims in `agents.md` describe a target professional multi-agent studio. This report grades **what is actually present** in the common host pack (SPEC, sources, tools, prompts, rubrics, graphs) versus those claims. Aspirational text ≠ production capability.

---

## 0. Executive answers (fleet-wide)

| # | Question | Fleet answer | Evidence snapshot |
|---|----------|--------------|-------------------|
| 1 | Responsibility in SPEC | **Mostly YES** | 114/114 agents have strong `## Responsibility` text |
| 2 | Knowledge distillation plan | **PARTIAL** | Every VA row lists Knowledge Distillation Source; SPEC embeds common structure; continuous distillation loop not fully automated |
| 3 | Sources available / how to get | **PARTIAL** | Sources folders + PROVENANCE/MAPPING common; licensed live corpora not fully acquired; median local files present |
| 4 | Self-evaluation content | **PARTIAL (design-heavy)** | agents.md Self-Quality Criteria + SPEC quality gates present; **0/114** agents have non-empty `rubrics/` files |
| 5 | Surpass human yet? | **NO** | **0** agents have validated human-surpass measurements in host. Design surpass signals are aspirational only |
| 6 | How they execute | **PARTIAL — host-orchestrated** | Graph/DNA + host adapters; **11** agents have live media tools; **0** have materialized prompt files; not free-running coding-plan agents by default |
| 7 | Skills/plugins/harness | **PARTIAL (shared pack skills)** | Pack `special_skills/` + host adapters exist; per-agent private skill install harness largely missing |
| 8 | Self-improvement mechanism | **PARTIAL** | SPEC Continuous Learning + `max_refinement_count`; closed-loop RLAIF/promote not fully productized per agent |
| 9 | Research path to improve | **PARTIAL** | Source lists + research/meta agents designed; automated research→eval→promote incomplete |
| 10 | Collaborate / instruct others | **PARTIAL** | `critique_edges` + handoff design + workflow DNA; full runtime critique bus not complete for all |
| 11 | Conflict resolve + confirm | **PARTIAL** | Design: dispute → Judge → HiTL; autonomous resolve+confirm not proven per agent |

**Average maturity score (0–11):** **6.45**  
**Cell counts (114×11):** YES=330, PARTIAL=810, NO=114

### Critical fleet deficiencies (rethink / improve)

1. **Prompts are not materialised** — `prompt_reference` exists on every agent, but **0** agents have non-empty `prompts/` content files. Execution cannot be role-faithful without real prompts.
2. **Rubrics are not materialised** — `rubric_reference` exists, but **0** agents have non-empty `rubrics/` content files. L2 craft scoring cannot run.
3. **Surpass-human claims are design fiction until measured** — do not treat agents.md “Wins ≥55% blind pairwise…” rows as current capability.
4. **Tools are mostly stubs** — only a small media subset has live adapter allowlists; most craft tools (Resolve/Nuke/Sheets/FAA…) are design text.
5. **Collab & conflict are schema-first** — edges and SPEC text exist; end-to-end CritiqueMessage bus + Judge + HiTL confirm need completion.
6. **Self-improvement is documented, not closed-loop** — refinement budgets without durable promote/reject evidence are incomplete.

---

## 1. What `agents.md` requires (VA design contract)

Every agent row in `va-agent-swarm/study/agents.md` defines eight columns:

| Column | Maps to question | Meaning |
|--------|------------------|---------|
| Responsibility | Q1 | Single craft ownership boundary |
| Knowledge Distillation Source | Q2–Q3, Q9 | Where professional knowledge comes from |
| Self-Quality Criteria | Q4 | How the agent judges its own output |
| Surpass-Human Signal | Q5 | Target human-parity/surpass metric (aspirational) |
| Accepts Critique From / Comments On | Q10–Q11 | Peer critique topology |
| Tool Access | Q6–Q7 | External tools / generators / DCC bridges |
| Architecture Pattern | Q6, Q8 | Self-Refine, ReAct, Debate, Agentic Graph, etc. |

Section **§11 Common Structure** additionally requires for *every* agent: Identity, Responsibility, Knowledge source, Tool access, Architecture pattern, Memory, Constitution/Rubric, L1 Spec / L2 Rubric / L3 Preference gates, Critique inbox, Continuous learning, Handoff contracts, HiTL escalation.

**Implication:** If an item exists only in `agents.md` but not as executable pack artifacts (`SPEC` + `prompts/` + `rubrics/` + tools + eval fixtures + host graph wiring), status is **PARTIAL** or **NO**, not YES.

---

## 2. Cross-cutting deep answers (Q1–Q11)

### Q1 — How to ensure each agent knows Responsibility (well defined in SPEC.md)

**Current state:** Strong. Pack SPECs include a `## Responsibility` section for all 114 agents (often distilled from VA tables + common structure). `agent_spec.json` also stores `role`, `va_name`, `va_id`, `va_category`.

**How to ensure (recommended control system):**

1. **Single source of truth chain:** `agents.md` row → `agent_spec.json.role` → `SPEC.md ## Responsibility` → `docs/user_guide.md` opening line (must match).
2. **Machine gate:** CI check that every agent has Responsibility ≥ N chars, contains “owns”, and does not copy another agent’s first 40 tokens.
3. **Operator test:** On Registry agent detail, show Responsibility only from SPEC; fail card generation if missing.
4. **Runtime identity injection:** Host system prompt must start with responsibility boundary + does-not-own list before tools.

### Q2 — Plan to distill professional knowledge?

**Current state: PARTIAL — yes as design, incomplete as pipeline.**

- VA table lists per-agent Knowledge Distillation Sources (award archives, books, interviews, corpora).
- SPEC common structure includes Continuous Learning / distillation language.
- Pack has `corpus/study/`, per-agent `sources/` excerpts, and shared `special_skills/`.
- Missing: licensed continuous distillation jobs, refresh cadence SLAs, quality gates on new source intake.

### Q3 — Sources present or know how to get them?

**Current state: PARTIAL.**

- Local: `sources/PROVENANCE.json`, `MAPPING.md`, `excerpts/`, sometimes `generic/` SPEC copies.
- Known-how: agents.md + mapping documents *what* to fetch; they do **not** guarantee legal acquisition, API access, or up-to-date corpora.
- Gap: many listed sources (MasterClass, DGA, WGA libraries, paid reels) are **not** fully offline-licensed in the pack.

### Q4 — Self-evaluation methods collected?

**Current state: PARTIAL (criteria designed; artifacts empty).**

- Designed: Self-Quality Criteria column + 3-layer gate (Spec→Rubric→Preference) in §11.
- Pack: `rubric_reference` IDs + occasional pack-level evals under `business/video/evals/`.
- Gap: **zero** per-agent non-empty `rubrics/` files → L2 craft scoring not executable per role.

### Q5 — Surpass human yet?

**Answer: NO for all agents.**

Design signals (e.g., “Wins ≥55% blind pairwise vs DGA cuts”) are **targets**, not measured host results. No agent has a published evidence bundle proving human-surpass under controlled evaluation in this repo.

### Q6 — How do they execute their job?

| Layer | What exists today | What does not |
|-------|-------------------|---------------|
| Host orchestration | Workflow DNA / graphs, product APIs, registry | Full CrewAI/LangGraph parity with every tool in agents.md |
| LLM calls | Host model policy fields; media providers when env enabled | Per-agent hardened system prompts on disk |
| Tools | Subset of `media.*` adapters (Sora/Veo/Runway/ElevenLabs) | Most DCC MCP bridges, Sheets, FAA, etc. |
| Coding plan agents | Special skills / specials pack designs | Per-video-agent autonomous coding agents |
| Deterministic path | Fail-closed without production flags | Always-on live generation |

**Default execution path today:** Host selects agents via roster/workflow map → runs graph node → may call allowlisted tool or local deterministic path → records evidence. **Not** “each agent independently runs a coding plan.”

### Q7 — Skills / plugins / harness for themselves?

**PARTIAL.** Shared pack skills live under `business/video/special_skills/` and specials agents under `business/specials/agents/`. Individual video agents generally do **not** own private installed plugin trees; they inherit host + pack harness.

### Q8 — Mechanism to improve themselves?

**PARTIAL.** SPEC describes continuous learning (bootstrap → expert → RLAIF → red-team → 30/60/90). `max_refinement_count` exists. Missing: durable self-improvement controller that writes new prompt/rubric versions with eval proof.

### Q9 — Know how to collect/research info to improve?

**PARTIAL.** Research/meta agents (WebResearch, BenchmarkResearch, TrendIntelligence, etc.) encode *how* in design. Operational “research → distill → eval → promote” is not complete for every craft agent.

### Q10 — Get/send instructions in collaboration?

**PARTIAL.**

- Designed: Accepts Critique From / Comments On matrix; CritiqueMessage schema; handoffs.
- Pack: `critique_edges.inputs/outputs` on `agent_spec.json`; workflow DNA nodes; orchestrator/planner entry agents.
- Gap: universal runtime bus + guaranteed delivery/ack for every agent pair.

### Q11 — Resolve conflict themselves and confirm?

**PARTIAL.** Design path: blocker/major/minor → Self-Refine → multi-agent debate / JudgeAgent → HiTL if unresolved. Host must still implement severity routing and human confirm gates as first-class APIs for all packs.

---

## 3. Per-group status

| Group | Label | Agents | Avg maturity (0–11) | Strongest area | Weakest area | Group priority actions |
|-------|-------|--------|---------------------|----------------|--------------|------------------------|
| `1-ATL` | Above-the-Line | 5 | **6.5** | 1) Responsibility well defined in SPEC.md | 5) Implementation surpasses human yet? | Materialize director/producer/screenwriter prompts+rubrics; wire greenlight HiTL; live media tools only with consent gates. |
| `2-Cam` | Camera & Lighting | 3 | **6.5** | 1) Responsibility well defined in SPEC.md | 5) Implementation surpasses human yet? | Camera-path tool adapters + safety constitution tests (esp. drone); aesthetic scoring harness. |
| `3-Edit` | Editorial & Color / Design | 10 | **6.5** | 1) Responsibility well defined in SPEC.md | 5) Implementation surpasses human yet? | Resolve/FFmpeg bridges for editor/color; Murch/12-principles rubrics as executable JSON. |
| `4-Snd` | Sound & Music | 4 | **6.5** | 1) Responsibility well defined in SPEC.md | 5) Implementation surpasses human yet? | ElevenLabs/loudness tool path; LUFS validators as L1; mix deliverable schemas. |
| `5-Perf` | Performance & Choreography | 5 | **6.3** | 1) Responsibility well defined in SPEC.md | 5) Implementation surpasses human yet? | Consent/likeness policy gates; choreography/timing rubrics; avoid unconsented voice clone activation. |
| `6-Dist` | Distribution & Marketing | 4 | **6.5** | 1) Responsibility well defined in SPEC.md | 5) Implementation surpasses human yet? | Brand/compliance validators; platform-spec checklists; marketing metrics evals. |
| `7-Edu` | Education & Domain-Expert | 14 | **6.46** | 1) Responsibility well defined in SPEC.md | 5) Implementation surpasses human yet? | Domain-fact checkers + SME HiTL; localization/accessibility rubrics first-class. |
| `8-AI` | AI-Era Specialists | 7 | **6.5** | 1) Responsibility well defined in SPEC.md | 5) Implementation surpasses human yet? | Prompt/avatar/voice-clone tools already closest to live — add red-team + deepfake gates before scale. |
| `9-Meta` | Specialist Meta-Agents | 28 | **6.5** | 1) Responsibility well defined in SPEC.md | 5) Implementation surpasses human yet? | Finish orchestrator/planner/router/judge runtime as platform spine; critique bus before craft scale-out. |
| `10-Sup` | Workflow Support | 34 | **6.37** | 1) Responsibility well defined in SPEC.md | 5) Implementation surpasses human yet? | Support agents need explicit SLAs + data contracts; many tools still design-only. |

---

## 4. Per-agent detailed status (by group)

Legend: **YES** = present/usable at pack level · **PARTIAL** = designed or incomplete · **NO** = missing / not achieved.

### 1-ATL — Above-the-Line (5 agents, avg maturity 6.5)

#### Group synthesis

- **1) Responsibility well defined in SPEC.md:** dominant **YES** (Y=5, P=0, N=0)
- **2) Plan to distill professional knowledge:** dominant **YES** (Y=5, P=0, N=0)
- **3) Sources exist / know how to obtain them:** dominant **YES** (Y=5, P=0, N=0)
- **4) Self-evaluation methods & content collected:** dominant **PARTIAL** (Y=0, P=5, N=0)
- **5) Implementation surpasses human yet?:** dominant **NO** (Y=0, P=0, N=5)
- **6) How they execute the job:** dominant **PARTIAL** (Y=0, P=5, N=0)
- **7) Skills / plugins / harness for themselves:** dominant **PARTIAL** (Y=0, P=5, N=0)
- **8) Mechanism to improve themselves:** dominant **PARTIAL** (Y=0, P=5, N=0)
- **9) Collect/research info to improve:** dominant **PARTIAL** (Y=0, P=5, N=0)
- **10) Get/send instructions to other agents:** dominant **PARTIAL** (Y=0, P=5, N=0)
- **11) Resolve conflict + confirm:** dominant **PARTIAL** (Y=0, P=5, N=0)

#### Agents

##### `video.director` — DirectorAgent

- **VA id / category:** 1 / `1-ATL`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.director.v1` / files=0  
- **Rubric ref / files:** `video.rubric.director.v1` / files=0  
- **Sources / provenance:** files=23 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Owns vision; issues shot intents, sets pacing, approves takes Host role binding: `DirectorAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Owns vision; issues shot intents, sets pacing, a…

**From `agents.md` design row:**

- Responsibility: Owns vision; issues shot intents, sets pacing, approves takes
- Knowledge distillation source: Criterion commentary; IMDb Top 250 director interviews; DGA seminars; MasterClass (Scorsese/Lynch/Gerwig)
- Self-quality criteria: Shot-intent fidelity (CLIP-T ≥0.32); story-beat coverage 100%; pacing curve matches genre prior
- Surpass-human signal (aspirational): Wins ≥55% blind pairwise vs DGA cuts (Arena)
- Accepts critique from: ScreenwriterAgent, EditorAgent, AudienceSim — JSON critique bus
- Comments on: EditorAgent, DoPAgent, ScreenwriterAgent, ComposerAgent
- Tool access (design): Sora 2 API, Veo 3.1 (Gemini API), Runway Gen-4, Kling 3.0; DaVinci Resolve via MCP
- Architecture pattern (design): Self-Refine + LLM-as-Judge (rubric: genre priors)

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1284 chars). VA source responsibility: Owns vision; issues shot intents, sets pacing, approves takes |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Criterion commentary; IMDb Top 250 director interviews; DGA seminars; MasterClass (Scorsese/Lynch/Gerwig) |
| 3) Sources exist / know how to obtain them | **YES** | 23 source files + PROVENANCE. VA listed: Criterion commentary; IMDb Top 250 director interviews; DGA seminars; MasterClass (Scorsese/Lynch/Gerwig) |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Shot-intent fidelity (CLIP-T ≥0.32); story-beat coverage 100%; pacing curve matches genre prior |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Wins ≥55% blind pairwise vs DGA cuts (Arena) |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.director.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: Self-Refine + LLM-as-Judge (rubric: genre prior… |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: ScreenwriterAgent, EditorAgent, AudienceSim — JSON critique… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.director.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.director.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.director` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.producer` — ProducerAgent / EP

- **VA id / category:** 2 / `1-ATL`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.producer.v1` / files=0  
- **Rubric ref / files:** `video.rubric.producer.v1` / files=0  
- **Sources / provenance:** files=16 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Budget, schedule, hiring, delivery; greenlights phase gates Host role binding: `ProducerAgent / EP (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Budget, schedule, hiring, delivery; greenligh…

**From `agents.md` design row:**

- Responsibility: Budget, schedule, hiring, delivery; greenlights phase gates
- Knowledge distillation source: PGA Producers Mark; Variety/Deadline budget leaks; LineProducer Excel corpora
- Self-quality criteria: On-time delivery rate; budget variance <±5%; talent satisfaction (RLHF)
- Surpass-human signal (aspirational): Beats PGA schedules at 0.6× cost with equal CSAT
- Accepts critique from: All downstream agents (escalations); HiTL gate for greenlight
- Comments on: DirectorAgent (scope creep), AllAgents (resource burn)
- Tool access (design): Google Sheets API, Airtable, Temporal/Airflow orchestration, Stripe billing
- Architecture pattern (design): Agentic Graph (LangGraph DAG) + ReAct for tool calls

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1230 chars). VA source responsibility: Budget, schedule, hiring, delivery; greenlights phase gates |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: PGA Producers Mark; Variety/Deadline budget leaks; LineProducer Excel corpora |
| 3) Sources exist / know how to obtain them | **YES** | 16 source files + PROVENANCE. VA listed: PGA Producers Mark; Variety/Deadline budget leaks; LineProducer Excel corpora |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: On-time delivery rate; budget variance <±5%; talent satisfaction (RLHF) |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Beats PGA schedules at 0.6× cost with equal CSAT |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.producer.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: Agentic Graph (LangGraph DAG) + ReAct for tool … |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: All downstream agents (escalations); HiTL gate for greenlig… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.producer.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.producer.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.producer` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.screenwriter` — ScreenwriterAgent

- **VA id / category:** 3 / `1-ATL`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.screenwriter.v1` / files=0  
- **Rubric ref / files:** `video.rubric.screenwriter.v1` / files=0  
- **Sources / provenance:** files=14 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Treatment → screenplay; dialogue; structure Host role binding: `ScreenwriterAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Treatment → screenplay; dialogue; structure ### Knowledge dist…

**From `agents.md` design row:**

- Responsibility: Treatment → screenplay; dialogue; structure
- Knowledge distillation source: Black List scripts; WGA library; McKee *Story*; Truby; Kaufman/Sorkin interviews
- Self-quality criteria: Save-the-Cat beat pass; dialogue distinctiveness (embedding distance ≥τ); rewrite delta
- Surpass-human signal (aspirational): Wins ≥50% blind read vs Black List Top-10 (WGA panel emulated)
- Accepts critique from: DirectorAgent, DramaturgAgent, StoryEditorAgent — Reflexion loop
- Comments on: DirectorAgent (logline), DialogueAgent, ConsistencyAgent
- Tool access (design): Fountain/FDX format validators; semantic embedding models (text-embedding-3-large)
- Architecture pattern (design): Reflexion (Shinn 2023) — verbal RL with episodic memory

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1245 chars). VA source responsibility: Treatment → screenplay; dialogue; structure |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Black List scripts; WGA library; McKee *Story*; Truby; Kaufman/Sorkin interviews |
| 3) Sources exist / know how to obtain them | **YES** | 14 source files + PROVENANCE. VA listed: Black List scripts; WGA library; McKee *Story*; Truby; Kaufman/Sorkin interviews |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Save-the-Cat beat pass; dialogue distinctiveness (embedding distance ≥τ); rewrite delta |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Wins ≥50% blind read vs Black List Top-10 (WGA panel emulated) |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.screenwriter.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: Reflexion (Shinn 2023) — verbal RL with epi… |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: DirectorAgent, DramaturgAgent, StoryEditorAgent — Reflexion… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.screenwriter.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.screenwriter.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.screenwriter` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.showrunner` — ShowrunnerAgent

- **VA id / category:** 4 / `1-ATL`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.showrunner.v1` / files=0  
- **Rubric ref / files:** `video.rubric.showrunner.v1` / files=0  
- **Sources / provenance:** files=11 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Cross-episode arc, writers'-room orchestration Host role binding: `ShowrunnerAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Cross-episode arc, writers'-room orchestration ### Knowledge …

**From `agents.md` design row:**

- Responsibility: Cross-episode arc, writers'-room orchestration
- Knowledge distillation source: WGA showrunner training; Sopranos/BB room transcripts; Mike Schur material
- Self-quality criteria: Arc continuity score; character-thread completion; tonal variance within bounds
- Surpass-human signal (aspirational): Series Bible coverage ≥99% across 10 eps (vs ~95% human)
- Accepts critique from: Network-Notes Agent, AudienceSim, multi-agent debate w/ ScreenwriterAgent
- Comments on: ScreenwriterAgent (arc), CastingAgent, DirectorAgent (tone)
- Tool access (design): Long-context LLM (Gemini 2.5 Pro 1M), vector-DB (Pinecone/Weaviate) for bible search
- Architecture pattern (design): Multi-agent debate (Du 2023) + MemoryAgent retrieval

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1240 chars). VA source responsibility: Cross-episode arc, writers'-room orchestration |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: WGA showrunner training; Sopranos/BB room transcripts; Mike Schur material |
| 3) Sources exist / know how to obtain them | **YES** | 11 source files + PROVENANCE. VA listed: WGA showrunner training; Sopranos/BB room transcripts; Mike Schur material |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Arc continuity score; character-thread completion; tonal variance within bounds |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Series Bible coverage ≥99% across 10 eps (vs ~95% human) |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.showrunner.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: Multi-agent debate (Du 2023) + MemoryAgent re… |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: Network-Notes Agent, AudienceSim, multi-agent debate w/ Scr… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.showrunner.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.showrunner.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.showrunner` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.casting` — CastingAgent

- **VA id / category:** 5 / `1-ATL`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.casting.v1` / files=0  
- **Rubric ref / files:** `video.rubric.casting.v1` / files=0  
- **Sources / provenance:** files=12 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Voice + likeness selection; audition simulation Host role binding: `CastingAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Voice + likeness selection; audition simulation ### Knowledge d…

**From `agents.md` design row:**

- Responsibility: Voice + likeness selection; audition simulation
- Knowledge distillation source: CSA Artios archive; SAG-AFTRA AI rider; consented voice-actor corpora
- Self-quality criteria: Character-voice fit (audience preference); consent compliance 100%
- Surpass-human signal (aspirational): Beats CSA casting in blind preference; hours vs weeks turnaround
- Accepts critique from: DirectorAgent, ShowrunnerAgent, Legal/ConsentAgent
- Comments on: VoiceCloneAgent (likeness), AvatarDesignAgent
- Tool access (design): ElevenLabs v3 voice library, HeyGen avatar catalogue, speaker-embedding similarity (Resemblyzer)
- Architecture pattern (design): LLM-as-Judge (pairwise preference on voice samples)

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1203 chars). VA source responsibility: Voice + likeness selection; audition simulation |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: CSA Artios archive; SAG-AFTRA AI rider; consented voice-actor corpora |
| 3) Sources exist / know how to obtain them | **YES** | 12 source files + PROVENANCE. VA listed: CSA Artios archive; SAG-AFTRA AI rider; consented voice-actor corpora |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Character-voice fit (audience preference); consent compliance 100% |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Beats CSA casting in blind preference; hours vs weeks turnaround |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.casting.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: LLM-as-Judge (pairwise preference on voice sampl… |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: DirectorAgent, ShowrunnerAgent, Legal/ConsentAgent; comment… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.casting.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.casting.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.casting` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

### 2-Cam — Camera & Lighting (3 agents, avg maturity 6.5)

#### Group synthesis

- **1) Responsibility well defined in SPEC.md:** dominant **YES** (Y=3, P=0, N=0)
- **2) Plan to distill professional knowledge:** dominant **YES** (Y=3, P=0, N=0)
- **3) Sources exist / know how to obtain them:** dominant **YES** (Y=3, P=0, N=0)
- **4) Self-evaluation methods & content collected:** dominant **PARTIAL** (Y=0, P=3, N=0)
- **5) Implementation surpasses human yet?:** dominant **NO** (Y=0, P=0, N=3)
- **6) How they execute the job:** dominant **PARTIAL** (Y=0, P=3, N=0)
- **7) Skills / plugins / harness for themselves:** dominant **PARTIAL** (Y=0, P=3, N=0)
- **8) Mechanism to improve themselves:** dominant **PARTIAL** (Y=0, P=3, N=0)
- **9) Collect/research info to improve:** dominant **PARTIAL** (Y=0, P=3, N=0)
- **10) Get/send instructions to other agents:** dominant **PARTIAL** (Y=0, P=3, N=0)
- **11) Resolve conflict + confirm:** dominant **PARTIAL** (Y=0, P=3, N=0)

#### Agents

##### `video.cinematographer` — CinematographerAgent (DoP)

- **VA id / category:** 6 / `2-Cam`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.cinematographer.v1` / files=0  
- **Rubric ref / files:** `video.rubric.cinematographer.v1` / files=0  
- **Sources / provenance:** files=11 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Lensing, lighting, composition, look Host role binding: `CinematographerAgent (DoP) (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Lensing, lighting, composition, look ### Knowledge distillat…

**From `agents.md` design row:**

- Responsibility: Lensing, lighting, composition, look
- Knowledge distillation source: ASC Magazine 1980–present; Deakins forum; Brown *Cinematography: Theory & Practice*; Cannes shot-libraries
- Self-quality criteria: Rule-of-thirds/leading-lines score; exposure histogram in zone; color-temp consistency
- Surpass-human signal (aspirational): Beats ASC peer-juried reels in blind aesthetic preference
- Accepts critique from: DirectorAgent, ColoristAgent, VFXSupAgent
- Comments on: DirectorAgent (visual intent), GafferAgent, ColoristAgent
- Tool access (design): Veo 3.1 (camera-path control), Runway Gen-4 (ControlNet guides), ACES color pipeline tools
- Architecture pattern (design): Self-Refine + CLIP-based aesthetic scoring

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1233 chars). VA source responsibility: Lensing, lighting, composition, look |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: ASC Magazine 1980–present; Deakins forum; Brown *Cinematography: Theory & Practice*; Cannes shot-libraries |
| 3) Sources exist / know how to obtain them | **YES** | 11 source files + PROVENANCE. VA listed: ASC Magazine 1980–present; Deakins forum; Brown *Cinematography: Theory & Practice*; Cannes shot-libraries |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Rule-of-thirds/leading-lines score; exposure histogram in zone; color-temp consistency |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Beats ASC peer-juried reels in blind aesthetic preference |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.cinematographer.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: Self-Refine + CLIP-based aesthetic scori… |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: DirectorAgent, ColoristAgent, VFXSupAgent; comments on: Dir… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.cinematographer.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.cinematographer.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.cinematographer` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.cameraoperator` — CameraOperatorAgent

- **VA id / category:** 7 / `2-Cam`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.cameraoperator.v1` / files=0  
- **Rubric ref / files:** `video.rubric.cameraoperator.v1` / files=0  
- **Sources / provenance:** files=9 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Executes framing / focus / move per DoP intent Host role binding: `CameraOperatorAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Executes framing / focus / move per DoP intent ### Knowle…

**From `agents.md` design row:**

- Responsibility: Executes framing / focus / move per DoP intent
- Knowledge distillation source: SOC archive; Steadicam workshop reels; focus-pull telemetry
- Self-quality criteria: Frame steadiness, focus-hit %, action centering
- Surpass-human signal (aspirational): Focus-pull accuracy >99% vs SOC ~97% baseline
- Accepts critique from: CinematographerAgent (per-take feedback)
- Comments on: CinematographerAgent (impractical asks)
- Tool access (design): Runway camera-path presets; Kling motion control API; virtual camera rigs (Unreal MV)
- Architecture pattern (design): ReAct (Yao 2022) — reason about framing then call renderer

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1140 chars). VA source responsibility: Executes framing / focus / move per DoP intent |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: SOC archive; Steadicam workshop reels; focus-pull telemetry |
| 3) Sources exist / know how to obtain them | **YES** | 9 source files + PROVENANCE. VA listed: SOC archive; Steadicam workshop reels; focus-pull telemetry |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Frame steadiness, focus-hit %, action centering |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Focus-pull accuracy >99% vs SOC ~97% baseline |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.cameraoperator.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: ReAct (Yao 2022) — reason about framing t… |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: CinematographerAgent (per-take feedback); comments on: Cine… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.cameraoperator.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.cameraoperator.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.cameraoperator` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.dronepilot` — DronePilotAgent

- **VA id / category:** 8 / `2-Cam`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.dronepilot.v1` / files=0  
- **Rubric ref / files:** `video.rubric.dronepilot.v1` / files=0  
- **Sources / provenance:** files=8 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Aerial cinematography (simulated or real) Host role binding: `DronePilotAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Aerial cinematography (simulated or real) ### Knowledge distillati…

**From `agents.md` design row:**

- Responsibility: Aerial cinematography (simulated or real)
- Knowledge distillation source: Philip Bloom tutorials; FAA Part 107; SkyPixel award reels
- Self-quality criteria: Path smoothness; geofence compliance 100%; horizon stability
- Surpass-human signal (aspirational): Competition-grade smoothness at 10× sortie rate; zero violations
- Accepts critique from: DoPAgent, SafetyAgent
- Comments on: DoPAgent (impossible heights), SafetyAgent (risk)
- Tool access (design): DJI Waypoint SDK (sim); Veo 3.1 aerial-mode; geofence DB (AirMap API)
- Architecture pattern (design): Constitutional AI (safety constitution: FAA rules as principles)

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1138 chars). VA source responsibility: Aerial cinematography (simulated or real) |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Philip Bloom tutorials; FAA Part 107; SkyPixel award reels |
| 3) Sources exist / know how to obtain them | **YES** | 8 source files + PROVENANCE. VA listed: Philip Bloom tutorials; FAA Part 107; SkyPixel award reels |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Path smoothness; geofence compliance 100%; horizon stability |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Competition-grade smoothness at 10× sortie rate; zero violations |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.dronepilot.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: Constitutional AI (safety constitution: FAA r… |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: DoPAgent, SafetyAgent; comments on: DoPAgent (impossible he… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.dronepilot.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.dronepilot.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.dronepilot` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

### 3-Edit — Editorial & Color / Design (10 agents, avg maturity 6.5)

#### Group synthesis

- **1) Responsibility well defined in SPEC.md:** dominant **YES** (Y=10, P=0, N=0)
- **2) Plan to distill professional knowledge:** dominant **YES** (Y=10, P=0, N=0)
- **3) Sources exist / know how to obtain them:** dominant **YES** (Y=10, P=0, N=0)
- **4) Self-evaluation methods & content collected:** dominant **PARTIAL** (Y=0, P=10, N=0)
- **5) Implementation surpasses human yet?:** dominant **NO** (Y=0, P=0, N=10)
- **6) How they execute the job:** dominant **PARTIAL** (Y=0, P=10, N=0)
- **7) Skills / plugins / harness for themselves:** dominant **PARTIAL** (Y=0, P=10, N=0)
- **8) Mechanism to improve themselves:** dominant **PARTIAL** (Y=0, P=10, N=0)
- **9) Collect/research info to improve:** dominant **PARTIAL** (Y=0, P=10, N=0)
- **10) Get/send instructions to other agents:** dominant **PARTIAL** (Y=0, P=10, N=0)
- **11) Resolve conflict + confirm:** dominant **PARTIAL** (Y=0, P=10, N=0)

#### Agents

##### `video.editor` — EditorAgent

- **VA id / category:** 9 / `3-Edit`  
- **Status / provider / network:** `registered` / `media_host` / network=True  
- **Tools:** `media.stub, media.runway`  
- **Prompt ref / files:** `video.prompt.editor.v1` / files=0  
- **Rubric ref / files:** `video.rubric.editor.v1` / files=0  
- **Sources / provenance:** files=21 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Assemble cut; pacing; coverage selection Host role binding: `EditorAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Assemble cut; pacing; coverage selection ### Knowledge distillation sou…

**From `agents.md` design row:**

- Responsibility: Assemble cut; pacing; coverage selection
- Knowledge distillation source: Murch *In the Blink of an Eye*; ACE Eddie winners; Sundance editing labs
- Self-quality criteria: Pacing curve matches genre; Murch "Rule of Six" score; AVD ≥ target
- Surpass-human signal (aspirational): Wins ≥55% pairwise vs ACE-credited cuts
- Accepts critique from: DirectorAgent, AudienceSim, ComposerAgent (music-cut sync)
- Comments on: DirectorAgent (over-coverage), DoPAgent (unusable takes)
- Tool access (design): DaVinci Resolve via MCP bridge; FFmpeg; EDL/XML timeline APIs
- Architecture pattern (design): Self-Refine (rubric: Murch Rule of Six)

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1139 chars). VA source responsibility: Assemble cut; pacing; coverage selection |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Murch *In the Blink of an Eye*; ACE Eddie winners; Sundance editing labs |
| 3) Sources exist / know how to obtain them | **YES** | 21 source files + PROVENANCE. VA listed: Murch *In the Blink of an Eye*; ACE Eddie winners; Sundance editing labs |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Pacing curve matches genre; Murch "Rule of Six" score; AVD ≥ target |
| 5) Implementation surpasses human yet? | **NO** | Has live-tool path but no measured human-parity benchmark results in host. Design may state aspirational surpass signals only. VA aspirational signal: Wins ≥55% pairwise vs ACE-credited cuts |
| 6) How they execute the job | **PARTIAL** | Host may invoke media tools ['media.stub', 'media.runway']; prompt/rubric refs exist but prompts/ are empty stubs for most agents. Not a free-running coding plan agent. VA architecture: Self-Refine (rubric: Murch Rule of Six) |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: DirectorAgent, AudienceSim, ComposerAgent (music-cut sync);… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.editor.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.editor.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.editor` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.colorist` — ColoristAgent

- **VA id / category:** 10 / `3-Edit`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.colorist.v1` / files=0  
- **Rubric ref / files:** `video.rubric.colorist.v1` / files=0  
- **Sources / provenance:** files=14 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Final grade; look consistency Host role binding: `ColoristAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Final grade; look consistency ### Knowledge distillation sources (historical) IC…

**From `agents.md` design row:**

- Responsibility: Final grade; look consistency
- Knowledge distillation source: ICA corpora; Sonnenfeld sessions; HPA Award grades
- Self-quality criteria: ΔE drift <2; skin-tone IT8 alignment; mood vector match
- Surpass-human signal (aspirational): Beats junior colorist in blind preference; matches senior within ΔE
- Accepts critique from: DoPAgent, DirectorAgent, AccessibilityAgent (contrast)
- Comments on: DoPAgent (mixed-temp), VFXAgent (comp-color mismatch)
- Tool access (design): DaVinci Resolve color API (MCP); ACES/OCIO pipeline; LUT generators
- Architecture pattern (design): Self-Refine + tool-use (colorimeter validation)

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1120 chars). VA source responsibility: Final grade; look consistency |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: ICA corpora; Sonnenfeld sessions; HPA Award grades |
| 3) Sources exist / know how to obtain them | **YES** | 14 source files + PROVENANCE. VA listed: ICA corpora; Sonnenfeld sessions; HPA Award grades |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: ΔE drift <2; skin-tone IT8 alignment; mood vector match |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Beats junior colorist in blind preference; matches senior within ΔE |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.colorist.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: Self-Refine + tool-use (colorimeter validation) |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: DoPAgent, DirectorAgent, AccessibilityAgent (contrast); com… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.colorist.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.colorist.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.colorist` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.vfxsupervisor` — VFXSupervisorAgent

- **VA id / category:** 11 / `3-Edit`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.vfxsupervisor.v1` / files=0  
- **Rubric ref / files:** `video.rubric.vfxsupervisor.v1` / files=0  
- **Sources / provenance:** files=10 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Plans + supervises VFX pipeline Host role binding: `VFXSupervisorAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Plans + supervises VFX pipeline ### Knowledge distillation sources (histo…

**From `agents.md` design row:**

- Responsibility: Plans + supervises VFX pipeline
- Knowledge distillation source: VES Awards; SIGGRAPH papers; Weta/DNEG talks; Foundry training
- Self-quality criteria: Shot-completion %; comp-error pixel count; CLIP-T vs plate
- Surpass-human signal (aspirational): Weta-grade QC pass rate at fraction of time
- Accepts critique from: DirectorAgent, DoPAgent, ConsistencyAgent
- Comments on: AIGeneratorAgent (artifacts), CompositorAgent
- Tool access (design): Nuke via MCP bridge; Runway Gen-4 Aleph (video-to-video); ComfyUI
- Architecture pattern (design): Agentic Graph (fan-out per shot) + LLM-as-Judge (QC rubric)

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1109 chars). VA source responsibility: Plans + supervises VFX pipeline |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: VES Awards; SIGGRAPH papers; Weta/DNEG talks; Foundry training |
| 3) Sources exist / know how to obtain them | **YES** | 10 source files + PROVENANCE. VA listed: VES Awards; SIGGRAPH papers; Weta/DNEG talks; Foundry training |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Shot-completion %; comp-error pixel count; CLIP-T vs plate |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Weta-grade QC pass rate at fraction of time |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.vfxsupervisor.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: Agentic Graph (fan-out per shot) + LLM-as-… |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: DirectorAgent, DoPAgent, ConsistencyAgent; comments on: AIG… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.vfxsupervisor.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.vfxsupervisor.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.vfxsupervisor` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.animator_2d` — AnimatorAgent (2D/3D)

- **VA id / category:** 12 / `3-Edit`  
- **Status / provider / network:** `registered` / `media_host` / network=True  
- **Tools:** `media.stub, media.runway`  
- **Prompt ref / files:** `video.prompt.animator_2d.v1` / files=0  
- **Rubric ref / files:** `video.rubric.animator_2d.v1` / files=0  
- **Sources / provenance:** files=11 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Character motion, weight, timing Host role binding: `AnimatorAgent (2D/3D) (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Character motion, weight, timing ### Knowledge distillation sources (…

**From `agents.md` design row:**

- Responsibility: Character motion, weight, timing
- Knowledge distillation source: Williams *Animator's Survival Kit*; Annie Awards; Pixar SparkShorts; Blaise lessons
- Self-quality criteria: 12-principles score; arc smoothness; lip-sync phoneme accuracy
- Surpass-human signal (aspirational): Beats junior on Annie rubric; equals senior at 5× throughput
- Accepts critique from: DirectorAgent, LipSyncAgent
- Comments on: StoryboardAgent (impossible action), DirectorAgent (timing)
- Tool access (design): Kling 3.0 motion control; Blender Python API; Cascadeur physics; Sync.so lip-sync
- Architecture pattern (design): Self-Refine (rubric: 12 principles checklist)

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1158 chars). VA source responsibility: Character motion, weight, timing |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Williams *Animator's Survival Kit*; Annie Awards; Pixar SparkShorts; Blaise lessons |
| 3) Sources exist / know how to obtain them | **YES** | 11 source files + PROVENANCE. VA listed: Williams *Animator's Survival Kit*; Annie Awards; Pixar SparkShorts; Blaise lessons |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: 12-principles score; arc smoothness; lip-sync phoneme accuracy |
| 5) Implementation surpasses human yet? | **NO** | Has live-tool path but no measured human-parity benchmark results in host. Design may state aspirational surpass signals only. VA aspirational signal: Beats junior on Annie rubric; equals senior at 5× throughput |
| 6) How they execute the job | **PARTIAL** | Host may invoke media tools ['media.stub', 'media.runway']; prompt/rubric refs exist but prompts/ are empty stubs for most agents. Not a free-running coding plan agent. VA architecture: Self-Refine (rubric: 12 principles checklist) |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: DirectorAgent, LipSyncAgent; comments on: StoryboardAgent (… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.animator_2d.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.animator_2d.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.animator_2d` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.motiongraphics` — MotionGraphicsAgent

- **VA id / category:** 13 / `3-Edit`  
- **Status / provider / network:** `registered` / `media_host` / network=True  
- **Tools:** `media.stub, media.runway`  
- **Prompt ref / files:** `video.prompt.motiongraphics.v1` / files=0  
- **Rubric ref / files:** `video.rubric.motiongraphics.v1` / files=0  
- **Sources / provenance:** files=11 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Kinetic typography, lower thirds, infographics Host role binding: `MotionGraphicsAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Kinetic typography, lower thirds, infographics ### Knowle…

**From `agents.md` design row:**

- Responsibility: Kinetic typography, lower thirds, infographics
- Knowledge distillation source: Motionographer; School of Motion; AICP Next Awards
- Self-quality criteria: Typographic hierarchy; brand compliance; readability at thumbnail
- Surpass-human signal (aspirational): Wins agency RFP shootouts on speed + on-brand fidelity
- Accepts critique from: BrandManagerAgent, AccessibilityAgent (contrast)
- Comments on: CopywriterAgent (verbosity), EditorAgent (timing)
- Tool access (design): After Effects via MCP/ExtendScript; Lottie export; Rive; brand-asset CDN
- Architecture pattern (design): ReAct — reason about brand guidelines then render

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1154 chars). VA source responsibility: Kinetic typography, lower thirds, infographics |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Motionographer; School of Motion; AICP Next Awards |
| 3) Sources exist / know how to obtain them | **YES** | 11 source files + PROVENANCE. VA listed: Motionographer; School of Motion; AICP Next Awards |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Typographic hierarchy; brand compliance; readability at thumbnail |
| 5) Implementation surpasses human yet? | **NO** | Has live-tool path but no measured human-parity benchmark results in host. Design may state aspirational surpass signals only. VA aspirational signal: Wins agency RFP shootouts on speed + on-brand fidelity |
| 6) How they execute the job | **PARTIAL** | Host may invoke media tools ['media.stub', 'media.runway']; prompt/rubric refs exist but prompts/ are empty stubs for most agents. Not a free-running coding plan agent. VA architecture: ReAct — reason about brand guidelines then render |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: BrandManagerAgent, AccessibilityAgent (contrast); comments … |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.motiongraphics.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.motiongraphics.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.motiongraphics` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.storyboard` — StoryboardAgent

- **VA id / category:** 14 / `3-Edit`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.storyboard.v1` / files=0  
- **Rubric ref / files:** `video.rubric.storyboard.v1` / files=0  
- **Sources / provenance:** files=13 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Script → shot panels Host role binding: `StoryboardAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Script → shot panels ### Knowledge distillation sources (historical) *Framed Ink* (Mate…

**From `agents.md` design row:**

- Responsibility: Script → shot panels
- Knowledge distillation source: *Framed Ink* (Mateu-Mestre); Pixar story-trust; Despretz boards
- Self-quality criteria: Shot-language fidelity; coverage completeness; staging clarity
- Surpass-human signal (aspirational): Pixar story-trust pass rate at minutes per page
- Accepts critique from: DirectorAgent, DoPAgent
- Comments on: ScriptwriterAgent (unfilmable), DirectorAgent (staging)
- Tool access (design): DALL-E 3 / Midjourney API; panel-layout templates; Fountain parser
- Architecture pattern (design): Self-Refine (director feedback loop)

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1063 chars). VA source responsibility: Script → shot panels |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: *Framed Ink* (Mateu-Mestre); Pixar story-trust; Despretz boards |
| 3) Sources exist / know how to obtain them | **YES** | 13 source files + PROVENANCE. VA listed: *Framed Ink* (Mateu-Mestre); Pixar story-trust; Despretz boards |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Shot-language fidelity; coverage completeness; staging clarity |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Pixar story-trust pass rate at minutes per page |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.storyboard.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: Self-Refine (director feedback loop) |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: DirectorAgent, DoPAgent; comments on: ScriptwriterAgent (un… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.storyboard.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.storyboard.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.storyboard` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.conceptartist` — ConceptArtistAgent

- **VA id / category:** 15 / `3-Edit`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.conceptartist.v1` / files=0  
- **Rubric ref / files:** `video.rubric.conceptartist.v1` / files=0  
- **Sources / provenance:** files=13 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Pre-pro world/character design Host role binding: `ConceptArtistAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Pre-pro world/character design ### Knowledge distillation sources (histori…

**From `agents.md` design row:**

- Responsibility: Pre-pro world/character design
- Knowledge distillation source: ArtStation top-tier; McCaig/Church reels; studio art-bibles
- Self-quality criteria: Style-bible adherence; silhouette readability; design coherence
- Surpass-human signal (aspirational): Wins art-director shootouts on iteration speed
- Accepts critique from: DirectorAgent, ProductionDesignAgent
- Comments on: StoryboardAgent (design drift)
- Tool access (design): Midjourney v7; Stable Diffusion ControlNet; Photoshop generative fill (API)
- Architecture pattern (design): Self-Refine + style-reference CLIP scoring

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1085 chars). VA source responsibility: Pre-pro world/character design |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: ArtStation top-tier; McCaig/Church reels; studio art-bibles |
| 3) Sources exist / know how to obtain them | **YES** | 13 source files + PROVENANCE. VA listed: ArtStation top-tier; McCaig/Church reels; studio art-bibles |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Style-bible adherence; silhouette readability; design coherence |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Wins art-director shootouts on iteration speed |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.conceptartist.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: Self-Refine + style-reference CLIP scoring |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: DirectorAgent, ProductionDesignAgent; comments on: Storyboa… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.conceptartist.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.conceptartist.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.conceptartist` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.productiondesign` — ProductionDesignAgent

- **VA id / category:** 16 / `3-Edit`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.productiondesign.v1` / files=0  
- **Rubric ref / files:** `video.rubric.productiondesign.v1` / files=0  
- **Sources / provenance:** files=9 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Sets, locations, world look Host role binding: `ProductionDesignAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Sets, locations, world look ### Knowledge distillation sources (historical…

**From `agents.md` design row:**

- Responsibility: Sets, locations, world look
- Knowledge distillation source: ADG Awards; AMPAS submissions; Beachler/Carter talks
- Self-quality criteria: Period accuracy; palette coherence; build feasibility
- Surpass-human signal (aspirational): Wins ADG blind comparisons on period-research depth
- Accepts critique from: DirectorAgent, DoPAgent
- Comments on: ConceptArtistAgent (style break), CostumeAgent
- Tool access (design): Unreal Engine (virtual scouting); Veo 3.1 location gen; archival image search APIs
- Architecture pattern (design): Reflexion (stores period-research corrections in memory)

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1094 chars). VA source responsibility: Sets, locations, world look |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: ADG Awards; AMPAS submissions; Beachler/Carter talks |
| 3) Sources exist / know how to obtain them | **YES** | 9 source files + PROVENANCE. VA listed: ADG Awards; AMPAS submissions; Beachler/Carter talks |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Period accuracy; palette coherence; build feasibility |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Wins ADG blind comparisons on period-research depth |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.productiondesign.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: Reflexion (stores period-research corre… |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: DirectorAgent, DoPAgent; comments on: ConceptArtistAgent (s… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.productiondesign.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.productiondesign.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.productiondesign` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.costumedesign` — CostumeDesignAgent

- **VA id / category:** 17 / `3-Edit`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.costumedesign.v1` / files=0  
- **Rubric ref / files:** `video.rubric.costumedesign.v1` / files=0  
- **Sources / provenance:** files=9 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Character-through-wardrobe Host role binding: `CostumeDesignAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Character-through-wardrobe ### Knowledge distillation sources (historical) V&A…

**From `agents.md` design row:**

- Responsibility: Character-through-wardrobe
- Knowledge distillation source: V&A archive; CDG monographs; Ruth E. Carter masterclass
- Self-quality criteria: Period/fashion accuracy; silhouette read; palette fit
- Surpass-human signal (aspirational): Beats CDG juniors on period accuracy benchmarks
- Accepts critique from: DirectorAgent, ProductionDesignAgent
- Comments on: MUAAgent (continuity break)
- Tool access (design): Fashion-history vector DB (V&A/Met API); image-gen for costume sketches; color-palette tools
- Architecture pattern (design): Self-Refine (period-accuracy rubric)

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1072 chars). VA source responsibility: Character-through-wardrobe |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: V&A archive; CDG monographs; Ruth E. Carter masterclass |
| 3) Sources exist / know how to obtain them | **YES** | 9 source files + PROVENANCE. VA listed: V&A archive; CDG monographs; Ruth E. Carter masterclass |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Period/fashion accuracy; silhouette read; palette fit |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Beats CDG juniors on period accuracy benchmarks |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.costumedesign.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: Self-Refine (period-accuracy rubric) |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: DirectorAgent, ProductionDesignAgent; comments on: MUAAgent… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.costumedesign.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.costumedesign.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.costumedesign` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.mua_makeup` — MUAAgent (Makeup/Hair/SFX)

- **VA id / category:** 18 / `3-Edit`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.mua_makeup.v1` / files=0  
- **Rubric ref / files:** `video.rubric.mua_makeup.v1` / files=0  
- **Sources / provenance:** files=10 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Talent face/hair; prosthetics Host role binding: `MUAAgent (Makeup/Hair/SFX) (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Talent face/hair; prosthetics ### Knowledge distillation sources (h…

**From `agents.md` design row:**

- Responsibility: Talent face/hair; prosthetics
- Knowledge distillation source: IATSE 706 corpora; Kazu Hiro studio refs
- Self-quality criteria: Continuity hash across takes; skin-tone realism (FID)
- Surpass-human signal (aspirational): Continuity break rate <0.5% (vs ~2% human)
- Accepts critique from: DoPAgent, ContinuityAgent
- Comments on: CostumeAgent (palette clash)
- Tool access (design): Face-landmark detectors; perceptual hash comparison; Kling face-consistency mode
- Architecture pattern (design): Constitutional AI (constitution: continuity rules)

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1058 chars). VA source responsibility: Talent face/hair; prosthetics |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: IATSE 706 corpora; Kazu Hiro studio refs |
| 3) Sources exist / know how to obtain them | **YES** | 10 source files + PROVENANCE. VA listed: IATSE 706 corpora; Kazu Hiro studio refs |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Continuity hash across takes; skin-tone realism (FID) |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Continuity break rate <0.5% (vs ~2% human) |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.mua_makeup.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: Constitutional AI (constitution: continuity r… |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: DoPAgent, ContinuityAgent; comments on: CostumeAgent (palet… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.mua_makeup.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.mua_makeup.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.mua_makeup` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

### 4-Snd — Sound & Music (4 agents, avg maturity 6.5)

#### Group synthesis

- **1) Responsibility well defined in SPEC.md:** dominant **YES** (Y=4, P=0, N=0)
- **2) Plan to distill professional knowledge:** dominant **YES** (Y=4, P=0, N=0)
- **3) Sources exist / know how to obtain them:** dominant **YES** (Y=4, P=0, N=0)
- **4) Self-evaluation methods & content collected:** dominant **PARTIAL** (Y=0, P=4, N=0)
- **5) Implementation surpasses human yet?:** dominant **NO** (Y=0, P=0, N=4)
- **6) How they execute the job:** dominant **PARTIAL** (Y=0, P=4, N=0)
- **7) Skills / plugins / harness for themselves:** dominant **PARTIAL** (Y=0, P=4, N=0)
- **8) Mechanism to improve themselves:** dominant **PARTIAL** (Y=0, P=4, N=0)
- **9) Collect/research info to improve:** dominant **PARTIAL** (Y=0, P=4, N=0)
- **10) Get/send instructions to other agents:** dominant **PARTIAL** (Y=0, P=4, N=0)
- **11) Resolve conflict + confirm:** dominant **PARTIAL** (Y=0, P=4, N=0)

#### Agents

##### `video.sounddesign` — SoundDesignAgent

- **VA id / category:** 19 / `4-Snd`  
- **Status / provider / network:** `registered` / `media_host` / network=True  
- **Tools:** `media.stub, media.elevenlabs`  
- **Prompt ref / files:** `video.prompt.sounddesign.v1` / files=0  
- **Rubric ref / files:** `video.rubric.sounddesign.v1` / files=0  
- **Sources / provenance:** files=10 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Ambience, foley, SFX Host role binding: `SoundDesignAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Ambience, foley, SFX ### Knowledge distillation sources (historical) BBC SFX library; …

**From `agents.md` design row:**

- Responsibility: Ambience, foley, SFX
- Knowledge distillation source: BBC SFX library; MPSE Golden Reel; Burtt/Lievsay notes
- Self-quality criteria: Spectral diversity; sync ≤±1 frame; loudness -23 LUFS
- Surpass-human signal (aspirational): Wins MPSE pairwise on horror/sci-fi
- Accepts critique from: DirectorAgent, MixerAgent
- Comments on: EditorAgent (FX clash), ComposerAgent (masking)
- Tool access (design): ElevenLabs Sound FX API; Freesound; FFmpeg spectral analysis; Dolby.io loudness API
- Architecture pattern (design): ReAct (search SFX lib → validate sync → mix)

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1053 chars). VA source responsibility: Ambience, foley, SFX |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: BBC SFX library; MPSE Golden Reel; Burtt/Lievsay notes |
| 3) Sources exist / know how to obtain them | **YES** | 10 source files + PROVENANCE. VA listed: BBC SFX library; MPSE Golden Reel; Burtt/Lievsay notes |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Spectral diversity; sync ≤±1 frame; loudness -23 LUFS |
| 5) Implementation surpasses human yet? | **NO** | Has live-tool path but no measured human-parity benchmark results in host. Design may state aspirational surpass signals only. VA aspirational signal: Wins MPSE pairwise on horror/sci-fi |
| 6) How they execute the job | **PARTIAL** | Host may invoke media tools ['media.stub', 'media.elevenlabs']; prompt/rubric refs exist but prompts/ are empty stubs for most agents. Not a free-running coding plan agent. VA architecture: ReAct (search SFX lib → validate sync → mix) |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: DirectorAgent, MixerAgent; comments on: EditorAgent (FX cla… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.sounddesign.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.sounddesign.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.sounddesign` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.composer` — ComposerAgent

- **VA id / category:** 20 / `4-Snd`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.composer.v1` / files=0  
- **Rubric ref / files:** `video.rubric.composer.v1` / files=0  
- **Sources / provenance:** files=16 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Original score Host role binding: `ComposerAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Original score ### Knowledge distillation sources (historical) MAESTRO + film-score corpora; AS…

**From `agents.md` design row:**

- Responsibility: Original score
- Knowledge distillation source: MAESTRO + film-score corpora; ASCAP/BMI; Zimmer/Hildur sessions
- Self-quality criteria: Cue-to-emotion alignment (valence/arousal regression); thematic recurrence
- Surpass-human signal (aspirational): Wins blind pairwise on emotional-fit vs working composers
- Accepts critique from: DirectorAgent, EditorAgent (music cuts)
- Comments on: EditorAgent (cut interrupts cue), SoundDesignAgent (mask)
- Tool access (design): Udio/Suno music gen API; MIDI toolchain; stem-separation (Demucs); loudness meter
- Architecture pattern (design): Self-Refine + Emotional-Arc validation (biosignal proxy)

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1124 chars). VA source responsibility: Original score |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: MAESTRO + film-score corpora; ASCAP/BMI; Zimmer/Hildur sessions |
| 3) Sources exist / know how to obtain them | **YES** | 16 source files + PROVENANCE. VA listed: MAESTRO + film-score corpora; ASCAP/BMI; Zimmer/Hildur sessions |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Cue-to-emotion alignment (valence/arousal regression); thematic recurrence |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Wins blind pairwise on emotional-fit vs working composers |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.composer.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: Self-Refine + Emotional-Arc validation (biosign… |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: DirectorAgent, EditorAgent (music cuts); comments on: Edito… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.composer.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.composer.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.composer` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.voiceover` — VoiceOverAgent

- **VA id / category:** 21 / `4-Snd`  
- **Status / provider / network:** `registered` / `media_host` / network=True  
- **Tools:** `media.stub, media.elevenlabs`  
- **Prompt ref / files:** `video.prompt.voiceover.v1` / files=0  
- **Rubric ref / files:** `video.rubric.voiceover.v1` / files=0  
- **Sources / provenance:** files=10 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Narration, character VO, ad reads Host role binding: `VoiceOverAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Narration, character VO, ad reads ### Knowledge distillation sources (histo…

**From `agents.md` design row:**

- Responsibility: Narration, character VO, ad reads
- Knowledge distillation source: SOVAS reels; consented voice corpora; Wolfson/Cashman coaching
- Self-quality criteria: Prosody match; pronunciation 100%; emotion tag match
- Surpass-human signal (aspirational): Beats junior VO in blind preference; matches senior on emotion
- Accepts critique from: DirectorAgent, BrandAgent
- Comments on: ScriptwriterAgent (unspeakable phrasing)
- Tool access (design): ElevenLabs v3 TTS + voice cloning; Resemble.AI; pronunciation lexicon API
- Architecture pattern (design): LLM-as-Judge (MOS scoring rubric)

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1083 chars). VA source responsibility: Narration, character VO, ad reads |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: SOVAS reels; consented voice corpora; Wolfson/Cashman coaching |
| 3) Sources exist / know how to obtain them | **YES** | 10 source files + PROVENANCE. VA listed: SOVAS reels; consented voice corpora; Wolfson/Cashman coaching |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Prosody match; pronunciation 100%; emotion tag match |
| 5) Implementation surpasses human yet? | **NO** | Has live-tool path but no measured human-parity benchmark results in host. Design may state aspirational surpass signals only. VA aspirational signal: Beats junior VO in blind preference; matches senior on emotion |
| 6) How they execute the job | **PARTIAL** | Host may invoke media tools ['media.stub', 'media.elevenlabs']; prompt/rubric refs exist but prompts/ are empty stubs for most agents. Not a free-running coding plan agent. VA architecture: LLM-as-Judge (MOS scoring rubric) |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: DirectorAgent, BrandAgent; comments on: ScriptwriterAgent (… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.voiceover.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.voiceover.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.voiceover` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.soundmixer` — SoundMixerAgent (Re-recording)

- **VA id / category:** 22 / `4-Snd`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.soundmixer.v1` / files=0  
- **Rubric ref / files:** `video.rubric.soundmixer.v1` / files=0  
- **Sources / provenance:** files=14 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Final mix; deliverables (5.1/Atmos) Host role binding: `SoundMixerAgent (Re-recording) (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Final mix; deliverables (5.1/Atmos) ### Knowledge distill…

**From `agents.md` design row:**

- Responsibility: Final mix; deliverables (5.1/Atmos)
- Knowledge distillation source: CAS Awards; Atmos specs; broadcast loudness standards
- Self-quality criteria: LUFS target; STOI ≥0.85; spec-deliverable pass
- Surpass-human signal (aspirational): CAS spec on first pass without rework
- Accepts critique from: EditorAgent, SoundDesignAgent, AccessibilityAgent
- Comments on: SoundDesignAgent (over-design), ComposerAgent (level)
- Tool access (design): Dolby Atmos Renderer API; LUFS/loudness measurement tools; DaVinci Fairlight MCP
- Architecture pattern (design): Constitutional AI (constitution: broadcast-spec rules)

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1128 chars). VA source responsibility: Final mix; deliverables (5.1/Atmos) |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: CAS Awards; Atmos specs; broadcast loudness standards |
| 3) Sources exist / know how to obtain them | **YES** | 14 source files + PROVENANCE. VA listed: CAS Awards; Atmos specs; broadcast loudness standards |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: LUFS target; STOI ≥0.85; spec-deliverable pass |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: CAS spec on first pass without rework |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.soundmixer.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: Constitutional AI (constitution: broadcast-sp… |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: EditorAgent, SoundDesignAgent, AccessibilityAgent; comments… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.soundmixer.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.soundmixer.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.soundmixer` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

### 5-Perf — Performance & Choreography (5 agents, avg maturity 6.3)

#### Group synthesis

- **1) Responsibility well defined in SPEC.md:** dominant **YES** (Y=5, P=0, N=0)
- **2) Plan to distill professional knowledge:** dominant **YES** (Y=5, P=0, N=0)
- **3) Sources exist / know how to obtain them:** dominant **YES** (Y=3, P=2, N=0)
- **4) Self-evaluation methods & content collected:** dominant **PARTIAL** (Y=0, P=5, N=0)
- **5) Implementation surpasses human yet?:** dominant **NO** (Y=0, P=0, N=5)
- **6) How they execute the job:** dominant **PARTIAL** (Y=0, P=5, N=0)
- **7) Skills / plugins / harness for themselves:** dominant **PARTIAL** (Y=0, P=5, N=0)
- **8) Mechanism to improve themselves:** dominant **PARTIAL** (Y=0, P=5, N=0)
- **9) Collect/research info to improve:** dominant **PARTIAL** (Y=0, P=5, N=0)
- **10) Get/send instructions to other agents:** dominant **PARTIAL** (Y=0, P=5, N=0)
- **11) Resolve conflict + confirm:** dominant **PARTIAL** (Y=0, P=5, N=0)

#### Agents

##### `video.choreography` — ChoreographyAgent

- **VA id / category:** 23 / `5-Perf`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.choreography.v1` / files=0  
- **Rubric ref / files:** `video.rubric.choreography.v1` / files=0  
- **Sources / provenance:** files=11 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Movement design (MVs, dance challenges) Host role binding: `ChoreographyAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Movement design (MVs, dance challenges) ### Knowledge distillation…

**From `agents.md` design row:**

- Responsibility: Movement design (MVs, dance challenges)
- Knowledge distillation source: Emmy Choreography submissions; Goebel/Moore reels; dance-notation datasets
- Self-quality criteria: Beat-sync accuracy; safety constraints; viral-pattern alignment
- Surpass-human signal (aspirational): Wins blind preference vs choreographer drafts
- Accepts critique from: DirectorAgent, MVDirectorAgent
- Comments on: DirectorAgent (un-camera-friendly staging)
- Tool access (design): Kling 3.0 motion control (reference video); Cascadeur; beat-detection (librosa)
- Architecture pattern (design): Self-Refine (rubric: beat-sync + safety)

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1124 chars). VA source responsibility: Movement design (MVs, dance challenges) |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Emmy Choreography submissions; Goebel/Moore reels; dance-notation datasets |
| 3) Sources exist / know how to obtain them | **YES** | 11 source files + PROVENANCE. VA listed: Emmy Choreography submissions; Goebel/Moore reels; dance-notation datasets |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Beat-sync accuracy; safety constraints; viral-pattern alignment |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Wins blind preference vs choreographer drafts |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.choreography.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: Self-Refine (rubric: beat-sync + safety) |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: DirectorAgent, MVDirectorAgent; comments on: DirectorAgent … |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.choreography.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.choreography.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.choreography` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.musicvideodirector` — MusicVideoDirectorAgent

- **VA id / category:** 24 / `5-Perf`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.musicvideodirector.v1` / files=0  
- **Rubric ref / files:** `video.rubric.musicvideodirector.v1` / files=0  
- **Sources / provenance:** files=7 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.0/11 (Y=2 P=8 N=1)  
- **SPEC responsibility excerpt:** Visual concept for songs Host role binding: `MusicVideoDirectorAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Visual concept for songs ### Knowledge distillation sources (historical) Di…

**From `agents.md` design row:**

- Responsibility: Visual concept for songs
- Knowledge distillation source: DirectorsLibrary; UKMVA/MTV VMA winners; Hype Williams/Spike Jonze
- Self-quality criteria: Edit-rhythm sync; lookbook coherence; artist-brief fit
- Surpass-human signal (aspirational): Wins label-blind preference vs commercial MV shortlist
- Accepts critique from: LabelA&RAgent, ArtistAgent
- Comments on: EditorAgent (cut on beat), DoPAgent
- Tool access (design): Runway Gen-4 (style-locked generation); Veo 3.1; mood-board tools (Are.na API)
- Architecture pattern (design): Multi-agent debate (with DirectorAgent + EditorAgent)

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1093 chars). VA source responsibility: Visual concept for songs |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: DirectorsLibrary; UKMVA/MTV VMA winners; Hype Williams/Spike Jonze |
| 3) Sources exist / know how to obtain them | **PARTIAL** | 7 local source files; acquisition path may still be design-only (URLs/corpora not fully licensed). VA listed: DirectorsLibrary; UKMVA/MTV VMA winners; Hype Williams/Spike Jonze |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Edit-rhythm sync; lookbook coherence; artist-brief fit |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Wins label-blind preference vs commercial MV shortlist |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.musicvideodirector.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: Multi-agent debate (with DirectorAgen… |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: LabelA&RAgent, ArtistAgent; comments on: EditorAgent (cut o… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.musicvideodirector.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.musicvideodirector.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.musicvideodirector` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.comedywriter` — ComedyWriterAgent

- **VA id / category:** 25 / `5-Perf`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.comedywriter.v1` / files=0  
- **Rubric ref / files:** `video.rubric.comedywriter.v1` / files=0  
- **Sources / provenance:** files=8 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Skits, parody, viral meme writing Host role binding: `ComedyWriterAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Skits, parody, viral meme writing ### Knowledge distillation sources (hi…

**From `agents.md` design row:**

- Responsibility: Skits, parody, viral meme writing
- Knowledge distillation source: UCB/Groundlings manuals; SNL transcripts; Schur/Fey teaching
- Self-quality criteria: Joke-density; cold-open hook strength; predicted laughs/min
- Surpass-human signal (aspirational): Beats UCB-table-read win rate on cold-reads
- Accepts critique from: AudienceSim, ShowrunnerAgent
- Comments on: ScriptwriterAgent (no joke), SocialStrategistAgent (off-trend)
- Tool access (design): Audience laugh-prediction model; trending-audio API (TikTok Creative Center)
- Architecture pattern (design): Reflexion (stores audience feedback in episodic memory)

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1122 chars). VA source responsibility: Skits, parody, viral meme writing |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: UCB/Groundlings manuals; SNL transcripts; Schur/Fey teaching |
| 3) Sources exist / know how to obtain them | **YES** | 8 source files + PROVENANCE. VA listed: UCB/Groundlings manuals; SNL transcripts; Schur/Fey teaching |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Joke-density; cold-open hook strength; predicted laughs/min |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Beats UCB-table-read win rate on cold-reads |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.comedywriter.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: Reflexion (stores audience feedback in epis… |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: AudienceSim, ShowrunnerAgent; comments on: ScriptwriterAgen… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.comedywriter.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.comedywriter.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.comedywriter` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.talent` — TalentAgent (On-camera)

- **VA id / category:** 26 / `5-Perf`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.talent.v1` / files=0  
- **Rubric ref / files:** `video.rubric.talent.v1` / files=0  
- **Sources / provenance:** files=12 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** AI-rendered performance Host role binding: `TalentAgent (On-camera) (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) AI-rendered performance ### Knowledge distillation sources (historical) Meth…

**From `agents.md` design row:**

- Responsibility: AI-rendered performance
- Knowledge distillation source: Method-acting transcripts; consented actor performance corpora
- Self-quality criteria: Emotion-target match; charisma score (audience proxy)
- Surpass-human signal (aspirational): Hold-rate matches top creators in cohort
- Accepts critique from: DirectorAgent, CastingAgent
- Comments on: DirectorAgent (impossible blocking)
- Tool access (design): HeyGen Avatar IV; Synthesia personal avatars; emotion-detection models (AffectNet)
- Architecture pattern (design): Self-Refine + emotion-regression validator

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1066 chars). VA source responsibility: AI-rendered performance |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Method-acting transcripts; consented actor performance corpora |
| 3) Sources exist / know how to obtain them | **YES** | 12 source files + PROVENANCE. VA listed: Method-acting transcripts; consented actor performance corpora |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Emotion-target match; charisma score (audience proxy) |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Hold-rate matches top creators in cohort |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.talent.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: Self-Refine + emotion-regression validator |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: DirectorAgent, CastingAgent; comments on: DirectorAgent (im… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.talent.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.talent.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.talent` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.ugccreator` — UGCCreatorAgent

- **VA id / category:** 27 / `5-Perf`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.ugccreator.v1` / files=0  
- **Rubric ref / files:** `video.rubric.ugccreator.v1` / files=0  
- **Sources / provenance:** files=7 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.0/11 (Y=2 P=8 N=1)  
- **SPEC responsibility excerpt:** Authentic-feel ads in creator voice Host role binding: `UGCCreatorAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Authentic-feel ads in creator voice ### Knowledge distillation sources (…

**From `agents.md` design row:**

- Responsibility: Authentic-feel ads in creator voice
- Knowledge distillation source: TikTok Creative Center; Alix-Earle-style benchmarks (style not identity)
- Self-quality criteria: Hook-rate ≥30%; "scripted" detector < threshold
- Surpass-human signal (aspirational): Beats paid-creator avg ROAS at 0.1× cost
- Accepts critique from: PerformanceMarketerAgent, BrandAgent
- Comments on: PerformanceMarketerAgent (wrong audience)
- Tool access (design): Veo 3.1 (portrait 9:16); ElevenLabs voice; CapCut API; TikTok Ads Manager
- Architecture pattern (design): RLAIF (reward from ROAS signal)

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1081 chars). VA source responsibility: Authentic-feel ads in creator voice |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: TikTok Creative Center; Alix-Earle-style benchmarks (style not identity) |
| 3) Sources exist / know how to obtain them | **PARTIAL** | 7 local source files; acquisition path may still be design-only (URLs/corpora not fully licensed). VA listed: TikTok Creative Center; Alix-Earle-style benchmarks (style not identity) |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Hook-rate ≥30%; "scripted" detector < threshold |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Beats paid-creator avg ROAS at 0.1× cost |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.ugccreator.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: RLAIF (reward from ROAS signal) |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: PerformanceMarketerAgent, BrandAgent; comments on: Performa… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.ugccreator.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.ugccreator.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.ugccreator` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

### 6-Dist — Distribution & Marketing (4 agents, avg maturity 6.5)

#### Group synthesis

- **1) Responsibility well defined in SPEC.md:** dominant **YES** (Y=4, P=0, N=0)
- **2) Plan to distill professional knowledge:** dominant **YES** (Y=4, P=0, N=0)
- **3) Sources exist / know how to obtain them:** dominant **YES** (Y=4, P=0, N=0)
- **4) Self-evaluation methods & content collected:** dominant **PARTIAL** (Y=0, P=4, N=0)
- **5) Implementation surpasses human yet?:** dominant **NO** (Y=0, P=0, N=4)
- **6) How they execute the job:** dominant **PARTIAL** (Y=0, P=4, N=0)
- **7) Skills / plugins / harness for themselves:** dominant **PARTIAL** (Y=0, P=4, N=0)
- **8) Mechanism to improve themselves:** dominant **PARTIAL** (Y=0, P=4, N=0)
- **9) Collect/research info to improve:** dominant **PARTIAL** (Y=0, P=4, N=0)
- **10) Get/send instructions to other agents:** dominant **PARTIAL** (Y=0, P=4, N=0)
- **11) Resolve conflict + confirm:** dominant **PARTIAL** (Y=0, P=4, N=0)

#### Agents

##### `video.socialmediastrategist` — SocialMediaStrategistAgent

- **VA id / category:** 28 / `6-Dist`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.socialmediastrategist.v1` / files=0  
- **Rubric ref / files:** `video.rubric.socialmediastrategist.v1` / files=0  
- **Sources / provenance:** files=10 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Platform-native distribution, timing, trends Host role binding: `SocialMediaStrategistAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Platform-native distribution, timing, trends ### Kno…

**From `agents.md` design row:**

- Responsibility: Platform-native distribution, timing, trends
- Knowledge distillation source: TikTok Creator Portal; Meta Marketing Science; Tubular/Sensor Tower
- Self-quality criteria: Predicted-vs-actual reach error; trend-timing latency <2h
- Surpass-human signal (aspirational): Beats agency social leads on 30-day reach lift
- Accepts critique from: AnalystAgent, BrandAgent
- Comments on: CopywriterAgent (off-platform tone), EditorAgent (wrong aspect)
- Tool access (design): Meta Graph API; TikTok Content Posting API; Buffer/Hootsuite API; Sensor Tower data
- Architecture pattern (design): ReAct (trend search → schedule → post)

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1148 chars). VA source responsibility: Platform-native distribution, timing, trends |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: TikTok Creator Portal; Meta Marketing Science; Tubular/Sensor Tower |
| 3) Sources exist / know how to obtain them | **YES** | 10 source files + PROVENANCE. VA listed: TikTok Creator Portal; Meta Marketing Science; Tubular/Sensor Tower |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Predicted-vs-actual reach error; trend-timing latency <2h |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Beats agency social leads on 30-day reach lift |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.socialmediastrategist.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: ReAct (trend search → schedule → p… |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: AnalystAgent, BrandAgent; comments on: CopywriterAgent (off… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.socialmediastrategist.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.socialmediastrategist.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.socialmediastrategist` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.copywriter` — CopywriterAgent

- **VA id / category:** 29 / `6-Dist`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.copywriter.v1` / files=0  
- **Rubric ref / files:** `video.rubric.copywriter.v1` / files=0  
- **Sources / provenance:** files=12 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Scripts, captions, hooks, headlines Host role binding: `CopywriterAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Scripts, captions, hooks, headlines ### Knowledge distillation sources (…

**From `agents.md` design row:**

- Responsibility: Scripts, captions, hooks, headlines
- Knowledge distillation source: D&AD/One Show; *Ogilvy on Advertising*; Wiebe Copyhackers
- Self-quality criteria: Reading grade; hook-curiosity score; brand-voice cosine ≥0.85
- Surpass-human signal (aspirational): Wins D&AD-style blind preference on ad briefs
- Accepts critique from: BrandAgent, PerformanceMarketerAgent
- Comments on: ScriptwriterAgent (verbosity), VOArtist (unspeakable)
- Tool access (design): Brand-voice embedding model; Hemingway readability API; A/B headline tools
- Architecture pattern (design): Self-Refine (rubric: brand-voice similarity scorer)

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1118 chars). VA source responsibility: Scripts, captions, hooks, headlines |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: D&AD/One Show; *Ogilvy on Advertising*; Wiebe Copyhackers |
| 3) Sources exist / know how to obtain them | **YES** | 12 source files + PROVENANCE. VA listed: D&AD/One Show; *Ogilvy on Advertising*; Wiebe Copyhackers |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Reading grade; hook-curiosity score; brand-voice cosine ≥0.85 |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Wins D&AD-style blind preference on ad briefs |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.copywriter.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: Self-Refine (rubric: brand-voice similarity s… |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: BrandAgent, PerformanceMarketerAgent; comments on: Scriptwr… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.copywriter.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.copywriter.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.copywriter` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.creativedirector` — CreativeDirectorAgent

- **VA id / category:** 30 / `6-Dist`  
- **Status / provider / network:** `registered` / `media_host` / network=True  
- **Tools:** `media.stub, media.sora, media.veo, media.runway`  
- **Prompt ref / files:** `video.prompt.creativedirector.v1` / files=0  
- **Rubric ref / files:** `video.rubric.creativedirector.v1` / files=0  
- **Sources / provenance:** files=10 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Campaign concept; cross-discipline taste Host role binding: `CreativeDirectorAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Campaign concept; cross-discipline taste ### Knowledge distil…

**From `agents.md` design row:**

- Responsibility: Campaign concept; cross-discipline taste
- Knowledge distillation source: Cannes Lions Grand Prix; D&AD Pencils; agency case studies
- Self-quality criteria: Concept distinctiveness (embedding novelty); award-rubric predicted score
- Surpass-human signal (aspirational): Wins Cannes-jury-emulator gold vs human shortlists
- Accepts critique from: ClientAgent, BrandAgent
- Comments on: CopywriterAgent, ArtDirectorAgent
- Tool access (design): Campaign-archive search (Cannes Lions API); Midjourney for concept viz; Figma API
- Architecture pattern (design): Multi-agent debate (panel of IdeationAgent + NoveltyAgent)

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1133 chars). VA source responsibility: Campaign concept; cross-discipline taste |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Cannes Lions Grand Prix; D&AD Pencils; agency case studies |
| 3) Sources exist / know how to obtain them | **YES** | 10 source files + PROVENANCE. VA listed: Cannes Lions Grand Prix; D&AD Pencils; agency case studies |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Concept distinctiveness (embedding novelty); award-rubric predicted score |
| 5) Implementation surpasses human yet? | **NO** | Has live-tool path but no measured human-parity benchmark results in host. Design may state aspirational surpass signals only. VA aspirational signal: Wins Cannes-jury-emulator gold vs human shortlists |
| 6) How they execute the job | **PARTIAL** | Host may invoke media tools ['media.stub', 'media.sora', 'media.veo', 'media.runway']; prompt/rubric refs exist but prompts/ are empty stubs for most agents. Not a free-running coding plan agent. VA architecture: Multi-agent debate (panel of IdeationAgent + N… |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: ClientAgent, BrandAgent; comments on: CopywriterAgent, ArtD… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.creativedirector.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.creativedirector.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.creativedirector` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.performancemarketer` — PerformanceMarketerAgent

- **VA id / category:** 31 / `6-Dist`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.performancemarketer.v1` / files=0  
- **Rubric ref / files:** `video.rubric.performancemarketer.v1` / files=0  
- **Sources / provenance:** files=10 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Optimize ads for ROAS Host role binding: `PerformanceMarketerAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Optimize ads for ROAS ### Knowledge distillation sources (historical) Meta Bl…

**From `agents.md` design row:**

- Responsibility: Optimize ads for ROAS
- Knowledge distillation source: Meta Blueprint; TikTok Ads Academy; MMM literature
- Self-quality criteria: ROAS uplift vs control; significance ≥95%
- Surpass-human signal (aspirational): Beats senior media buyer on 30-day ROAS
- Accepts critique from: AnalystAgent, FinanceAgent
- Comments on: UGCAgent (low hook), CopywriterAgent (weak CTA)
- Tool access (design): Meta Ads API; TikTok Ads API; Google Ads API; Bayesian AB testing libs
- Architecture pattern (design): RLAIF (reward = ROAS uplift signal from ad platform)

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1047 chars). VA source responsibility: Optimize ads for ROAS |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Meta Blueprint; TikTok Ads Academy; MMM literature |
| 3) Sources exist / know how to obtain them | **YES** | 10 source files + PROVENANCE. VA listed: Meta Blueprint; TikTok Ads Academy; MMM literature |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: ROAS uplift vs control; significance ≥95% |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Beats senior media buyer on 30-day ROAS |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.performancemarketer.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: RLAIF (reward = ROAS uplift signal f… |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: AnalystAgent, FinanceAgent; comments on: UGCAgent (low hook… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.performancemarketer.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.performancemarketer.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.performancemarketer` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

### 7-Edu — Education & Domain-Expert (14 agents, avg maturity 6.46)

#### Group synthesis

- **1) Responsibility well defined in SPEC.md:** dominant **YES** (Y=14, P=0, N=0)
- **2) Plan to distill professional knowledge:** dominant **YES** (Y=14, P=0, N=0)
- **3) Sources exist / know how to obtain them:** dominant **YES** (Y=13, P=1, N=0)
- **4) Self-evaluation methods & content collected:** dominant **PARTIAL** (Y=0, P=14, N=0)
- **5) Implementation surpasses human yet?:** dominant **NO** (Y=0, P=0, N=14)
- **6) How they execute the job:** dominant **PARTIAL** (Y=0, P=14, N=0)
- **7) Skills / plugins / harness for themselves:** dominant **PARTIAL** (Y=0, P=14, N=0)
- **8) Mechanism to improve themselves:** dominant **PARTIAL** (Y=0, P=14, N=0)
- **9) Collect/research info to improve:** dominant **PARTIAL** (Y=0, P=14, N=0)
- **10) Get/send instructions to other agents:** dominant **PARTIAL** (Y=0, P=14, N=0)
- **11) Resolve conflict + confirm:** dominant **PARTIAL** (Y=0, P=14, N=0)

#### Agents

##### `video.instructionaldesign` — InstructionalDesignAgent

- **VA id / category:** 32 / `7-Edu`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.instructionaldesign.v1` / files=0  
- **Rubric ref / files:** `video.rubric.instructionaldesign.v1` / files=0  
- **Sources / provenance:** files=9 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Learning objectives → script → assessment Host role binding: `InstructionalDesignAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Learning objectives → script → assessment ### Knowledge d…

**From `agents.md` design row:**

- Responsibility: Learning objectives → script → assessment
- Knowledge distillation source: ATD body of knowledge; Cathy Moore *Action Mapping*; Dirksen *Design for How People Learn*
- Self-quality criteria: Bloom-level mapping; completion ≥70%; Kirkpatrick L2 quiz ≥80%
- Surpass-human signal (aspirational): Beats ATD-credentialed ID on retention RCT
- Accepts critique from: SMEAgent, AccessibilityAgent
- Comments on: ScriptwriterAgent (no objective), AnimatorAgent (over-decoration)
- Tool access (design): LMS APIs (SCORM/xAPI); quiz generation; Bloom taxonomy classifier
- Architecture pattern (design): Self-Refine (rubric: Bloom/Kirkpatrick)

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1153 chars). VA source responsibility: Learning objectives → script → assessment |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: ATD body of knowledge; Cathy Moore *Action Mapping*; Dirksen *Design for How People Learn* |
| 3) Sources exist / know how to obtain them | **YES** | 9 source files + PROVENANCE. VA listed: ATD body of knowledge; Cathy Moore *Action Mapping*; Dirksen *Design for How People Learn* |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Bloom-level mapping; completion ≥70%; Kirkpatrick L2 quiz ≥80% |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Beats ATD-credentialed ID on retention RCT |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.instructionaldesign.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: Self-Refine (rubric: Bloom/Kirkpatri… |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: SMEAgent, AccessibilityAgent; comments on: ScriptwriterAgen… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.instructionaldesign.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.instructionaldesign.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.instructionaldesign` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.sme` — SMEAgent (Subject-Matter Expert)

- **VA id / category:** 33 / `7-Edu`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.sme.v1` / files=0  
- **Rubric ref / files:** `video.rubric.sme.v1` / files=0  
- **Sources / provenance:** files=14 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Domain accuracy in target field Host role binding: `SMEAgent (Subject-Matter Expert) (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Domain accuracy in target field ### Knowledge distillation …

**From `agents.md` design row:**

- Responsibility: Domain accuracy in target field
- Knowledge distillation source: Peer-reviewed journals; certified curricula (CFA, USMLE, AWS); expert interviews
- Self-quality criteria: Citation density; benchmark exam pass; hallucination ≤0.5%
- Surpass-human signal (aspirational): Passes same certification as human pro
- Accepts critique from: FactCheckerAgent, peer SMEAgents (debate)
- Comments on: ScriptwriterAgent (inaccuracy), MotionGraphicsAgent (mis-labels)
- Tool access (design): PubMed/arXiv/JSTOR search APIs; exam-question banks; RAG over certified corpora
- Architecture pattern (design): Multi-agent debate + RAG retrieval

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1144 chars). VA source responsibility: Domain accuracy in target field |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Peer-reviewed journals; certified curricula (CFA, USMLE, AWS); expert interviews |
| 3) Sources exist / know how to obtain them | **YES** | 14 source files + PROVENANCE. VA listed: Peer-reviewed journals; certified curricula (CFA, USMLE, AWS); expert interviews |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Citation density; benchmark exam pass; hallucination ≤0.5% |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Passes same certification as human pro |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.sme.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: Multi-agent debate + RAG retrieval |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: FactCheckerAgent, peer SMEAgents (debate); comments on: Scr… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.sme.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.sme.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.sme` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.factchecker` — FactCheckerAgent

- **VA id / category:** 34 / `7-Edu`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.factchecker.v1` / files=0  
- **Rubric ref / files:** `video.rubric.factchecker.v1` / files=0  
- **Sources / provenance:** files=9 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Source-grade every claim Host role binding: `FactCheckerAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Source-grade every claim ### Knowledge distillation sources (historical) New Yorke…

**From `agents.md` design row:**

- Responsibility: Source-grade every claim
- Knowledge distillation source: New Yorker fact-check handbook; IFCN; Snopes/PolitiFact
- Self-quality criteria: Source-grade per claim (primary > secondary); cross-source ≥2
- Surpass-human signal (aspirational): Lower correction rate than Pulitzer-tier outlets
- Accepts critique from: SMEAgent, StandardsEditorAgent
- Comments on: ScriptwriterAgent (unsourced), JournalistAgent
- Tool access (design): Web search APIs (Brave/Google); claim-extraction NER; source-quality classifier
- Architecture pattern (design): ReAct (extract claim → search → verify → grade)

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1086 chars). VA source responsibility: Source-grade every claim |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: New Yorker fact-check handbook; IFCN; Snopes/PolitiFact |
| 3) Sources exist / know how to obtain them | **YES** | 9 source files + PROVENANCE. VA listed: New Yorker fact-check handbook; IFCN; Snopes/PolitiFact |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Source-grade per claim (primary > secondary); cross-source ≥2 |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Lower correction rate than Pulitzer-tier outlets |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.factchecker.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: ReAct (extract claim → search → verify → gra… |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: SMEAgent, StandardsEditorAgent; comments on: ScriptwriterAg… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.factchecker.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.factchecker.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.factchecker` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.medicalillustrator` — MedicalIllustratorAgent

- **VA id / category:** 35 / `7-Edu`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.medicalillustrator.v1` / files=0  
- **Rubric ref / files:** `video.rubric.medicalillustrator.v1` / files=0  
- **Sources / provenance:** files=8 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Anatomy & procedure visuals Host role binding: `MedicalIllustratorAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Anatomy & procedure visuals ### Knowledge distillation sources (historic…

**From `agents.md` design row:**

- Responsibility: Anatomy & procedure visuals
- Knowledge distillation source: Netter atlas; AMI/CMI curriculum; Anatomage
- Self-quality criteria: Anatomical accuracy (detection model); AMI rubric
- Surpass-human signal (aspirational): CMI peers vote ≥pass in blind review
- Accepts critique from: SMEAgent (physician), AccessibilityAgent
- Comments on: AnimatorAgent (wrong anatomy), CopywriterAgent (mis-term)
- Tool access (design): Anatomage 3D API; DALL-E 3 (medical-prompt mode); anatomy-detection model
- Architecture pattern (design): Self-Refine (rubric: AMI scoring criteria)

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1073 chars). VA source responsibility: Anatomy & procedure visuals |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Netter atlas; AMI/CMI curriculum; Anatomage |
| 3) Sources exist / know how to obtain them | **YES** | 8 source files + PROVENANCE. VA listed: Netter atlas; AMI/CMI curriculum; Anatomage |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Anatomical accuracy (detection model); AMI rubric |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: CMI peers vote ≥pass in blind review |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.medicalillustrator.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: Self-Refine (rubric: AMI scoring crit… |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: SMEAgent (physician), AccessibilityAgent; comments on: Anim… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.medicalillustrator.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.medicalillustrator.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.medicalillustrator` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.journalist` — JournalistAgent

- **VA id / category:** 36 / `7-Edu`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.journalist.v1` / files=0  
- **Rubric ref / files:** `video.rubric.journalist.v1` / files=0  
- **Sources / provenance:** files=10 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Reporting + ethical framing Host role binding: `JournalistAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Reporting + ethical framing ### Knowledge distillation sources (historical) Puli…

**From `agents.md` design row:**

- Responsibility: Reporting + ethical framing
- Knowledge distillation source: Pulitzer/duPont/Peabody winners; SPJ Ethics; Poynter
- Self-quality criteria: Source diversity; on-record ratio; ethical-checklist pass
- Surpass-human signal (aspirational): Lower correction rate + faster file vs newsroom
- Accepts critique from: FactCheckerAgent, LegalAgent, StandardsEditorAgent
- Comments on: FactCheckerAgent, ScriptwriterAgent
- Tool access (design): Web research tools; AP Stylebook API; interview transcription (Otter); SPJ rubric
- Architecture pattern (design): Reflexion (ethical-checklist as verbal feedback)

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1095 chars). VA source responsibility: Reporting + ethical framing |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Pulitzer/duPont/Peabody winners; SPJ Ethics; Poynter |
| 3) Sources exist / know how to obtain them | **YES** | 10 source files + PROVENANCE. VA listed: Pulitzer/duPont/Peabody winners; SPJ Ethics; Poynter |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Source diversity; on-record ratio; ethical-checklist pass |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Lower correction rate + faster file vs newsroom |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.journalist.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: Reflexion (ethical-checklist as verbal feedba… |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: FactCheckerAgent, LegalAgent, StandardsEditorAgent; comment… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.journalist.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.journalist.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.journalist` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.compliance` — ComplianceAgent (Legal)

- **VA id / category:** 37 / `7-Edu`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.compliance.v1` / files=0  
- **Rubric ref / files:** `video.rubric.compliance.v1` / files=0  
- **Sources / provenance:** files=18 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** FTC, HIPAA, GDPR, IP, AI-likeness clearance Host role binding: `ComplianceAgent (Legal) (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) FTC, HIPAA, GDPR, IP, AI-likeness clearance ### Knowledg…

**From `agents.md` design row:**

- Responsibility: FTC, HIPAA, GDPR, IP, AI-likeness clearance
- Knowledge distillation source: Bar CLE; FTC guides; EU AI Act; GDPR/CCPA; SAG-AFTRA AI rider
- Self-quality criteria: 100% rule-coverage; zero post-publish takedowns
- Surpass-human signal (aspirational): Lower legal-risk than median media-counsel
- Accepts critique from: All agents (must clear gate); HumanLawyer for novel issues
- Comments on: All agents (blocking gate)
- Tool access (design): Legal-rule DB (vectorized regulations); consent-document store; C2PA verification lib
- Architecture pattern (design): Constitutional AI (constitution = compiled regulatory text)

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1143 chars). VA source responsibility: FTC, HIPAA, GDPR, IP, AI-likeness clearance |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Bar CLE; FTC guides; EU AI Act; GDPR/CCPA; SAG-AFTRA AI rider |
| 3) Sources exist / know how to obtain them | **YES** | 18 source files + PROVENANCE. VA listed: Bar CLE; FTC guides; EU AI Act; GDPR/CCPA; SAG-AFTRA AI rider |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: 100% rule-coverage; zero post-publish takedowns |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Lower legal-risk than median media-counsel |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.compliance.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: Constitutional AI (constitution = compiled re… |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: All agents (must clear gate); HumanLawyer for novel issues;… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.compliance.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.compliance.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.compliance` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.finance` — FinanceAgent

- **VA id / category:** 38 / `7-Edu`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.finance.v1` / files=0  
- **Rubric ref / files:** `video.rubric.finance.v1` / files=0  
- **Sources / provenance:** files=10 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Accurate market / earnings / token facts Host role binding: `FinanceAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Accurate market / earnings / token facts ### Knowledge distillation so…

**From `agents.md` design row:**

- Responsibility: Accurate market / earnings / token facts
- Knowledge distillation source: CFA curriculum; SEC marketing rule; Bloomberg/Refinitiv feeds
- Self-quality criteria: Numerical accuracy 100%; SEC compliance
- Surpass-human signal (aspirational): Passes CFA L3; lower retraction rate than analyst desks
- Accepts critique from: SMEAgent (econ), ComplianceAgent
- Comments on: ScriptwriterAgent (number drift), MotionGraphicsAgent (chart scale)
- Tool access (design): Bloomberg API; EDGAR/SEC filings; financial-calc validators
- Architecture pattern (design): ReAct (fetch data → validate → compose)

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1100 chars). VA source responsibility: Accurate market / earnings / token facts |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: CFA curriculum; SEC marketing rule; Bloomberg/Refinitiv feeds |
| 3) Sources exist / know how to obtain them | **YES** | 10 source files + PROVENANCE. VA listed: CFA curriculum; SEC marketing rule; Bloomberg/Refinitiv feeds |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Numerical accuracy 100%; SEC compliance |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Passes CFA L3; lower retraction rate than analyst desks |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.finance.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: ReAct (fetch data → validate → compose) |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: SMEAgent (econ), ComplianceAgent; comments on: Scriptwriter… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.finance.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.finance.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.finance` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.foodstylist` — FoodStylistAgent

- **VA id / category:** 39 / `7-Edu`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.foodstylist.v1` / files=0  
- **Rubric ref / files:** `video.rubric.foodstylist.v1` / files=0  
- **Sources / provenance:** files=8 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Camera-ready food, recipe authenticity Host role binding: `FoodStylistAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Camera-ready food, recipe authenticity ### Knowledge distillation so…

**From `agents.md` design row:**

- Responsibility: Camera-ready food, recipe authenticity
- Knowledge distillation source: James Beard archives; Spungen techniques; IACP corpora
- Self-quality criteria: Visual appetite-appeal (aesthetic regressor); recipe accuracy
- Surpass-human signal (aspirational): Wins blind preference vs editorial food stylist
- Accepts critique from: DoPAgent (lighting), DirectorAgent
- Comments on: ScriptwriterAgent (impossible recipe)
- Tool access (design): DALL-E 3 / Midjourney (food-photo gen); recipe-step parser; aesthetic scoring model
- Architecture pattern (design): Self-Refine (aesthetic regressor as rubric)

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1107 chars). VA source responsibility: Camera-ready food, recipe authenticity |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: James Beard archives; Spungen techniques; IACP corpora |
| 3) Sources exist / know how to obtain them | **YES** | 8 source files + PROVENANCE. VA listed: James Beard archives; Spungen techniques; IACP corpora |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Visual appetite-appeal (aesthetic regressor); recipe accuracy |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Wins blind preference vs editorial food stylist |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.foodstylist.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: Self-Refine (aesthetic regressor as rubric) |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: DoPAgent (lighting), DirectorAgent; comments on: Scriptwrit… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.foodstylist.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.foodstylist.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.foodstylist` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.travelcine` — TravelCineAgent

- **VA id / category:** 40 / `7-Edu`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.travelcine.v1` / files=0  
- **Rubric ref / files:** `video.rubric.travelcine.v1` / files=0  
- **Sources / provenance:** files=9 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Destination cinematography Host role binding: `TravelCineAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Destination cinematography ### Knowledge distillation sources (historical) Brando…

**From `agents.md` design row:**

- Responsibility: Destination cinematography
- Knowledge distillation source: Brandon Li/Burkard reels; NatGeo style guide; Banff Fest
- Self-quality criteria: Establishing-shot diversity; location-mood match
- Surpass-human signal (aspirational): Wins T+L preference at 0.1× sortie cost
- Accepts critique from: DirectorAgent, DronePilotAgent
- Comments on: DronePilotAgent (no-fly zone)
- Tool access (design): Veo 3.1 (location gen); Google Earth Studio; AirMap geofence; Unsplash API
- Architecture pattern (design): Self-Refine + geofence safety validator

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1038 chars). VA source responsibility: Destination cinematography |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Brandon Li/Burkard reels; NatGeo style guide; Banff Fest |
| 3) Sources exist / know how to obtain them | **YES** | 9 source files + PROVENANCE. VA listed: Brandon Li/Burkard reels; NatGeo style guide; Banff Fest |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Establishing-shot diversity; location-mood match |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Wins T+L preference at 0.1× sortie cost |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.travelcine.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: Self-Refine + geofence safety validator |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: DirectorAgent, DronePilotAgent; comments on: DronePilotAgen… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.travelcine.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.travelcine.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.travelcine` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.childrensauthor` — ChildrensAuthorAgent

- **VA id / category:** 41 / `7-Edu`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.childrensauthor.v1` / files=0  
- **Rubric ref / files:** `video.rubric.childrensauthor.v1` / files=0  
- **Sources / provenance:** files=8 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Age-appropriate story + safety Host role binding: `ChildrensAuthorAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Age-appropriate story + safety ### Knowledge distillation sources (histo…

**From `agents.md` design row:**

- Responsibility: Age-appropriate story + safety
- Knowledge distillation source: Caldecott/Geisel winners; Mo Willems/Donaldson; ECE lit
- Self-quality criteria: Lexile band match; Common-Sense-Media safety pass; rhyme score
- Surpass-human signal (aspirational): Beats Caldecott-rubric predicted score
- Accepts critique from: ChildSafetyAgent, ParentSimAgent
- Comments on: AnimatorAgent (scary), VOAgent (wrong age-tone)
- Tool access (design): Lexile analyzer API; Common Sense Media rubric; rhyme/meter tools (CMU Pronouncing Dict)
- Architecture pattern (design): Constitutional AI (child-safety constitution)

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1103 chars). VA source responsibility: Age-appropriate story + safety |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Caldecott/Geisel winners; Mo Willems/Donaldson; ECE lit |
| 3) Sources exist / know how to obtain them | **YES** | 8 source files + PROVENANCE. VA listed: Caldecott/Geisel winners; Mo Willems/Donaldson; ECE lit |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Lexile band match; Common-Sense-Media safety pass; rhyme score |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Beats Caldecott-rubric predicted score |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.childrensauthor.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: Constitutional AI (child-safety constitu… |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: ChildSafetyAgent, ParentSimAgent; comments on: AnimatorAgen… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.childrensauthor.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.childrensauthor.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.childrensauthor` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.audiobooknarrator` — AudiobookNarratorAgent

- **VA id / category:** 42 / `7-Edu`  
- **Status / provider / network:** `registered` / `media_host` / network=True  
- **Tools:** `media.stub, media.elevenlabs`  
- **Prompt ref / files:** `video.prompt.audiobooknarrator.v1` / files=0  
- **Rubric ref / files:** `video.rubric.audiobooknarrator.v1` / files=0  
- **Sources / provenance:** files=9 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Sustained character + narration Host role binding: `AudiobookNarratorAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Sustained character + narration ### Knowledge distillation sources (h…

**From `agents.md` design row:**

- Responsibility: Sustained character + narration
- Knowledge distillation source: Audie Awards; AudioFile Earphones; consented narrator corpora
- Self-quality criteria: Vocal stamina (no drift 60min); character distinction (embedding distance)
- Surpass-human signal (aspirational): Wins AudioFile blind eval at fraction of studio time
- Accepts critique from: DirectorAgent, AuthorAgent
- Comments on: VOArtistAgent (over-acting)
- Tool access (design): ElevenLabs v3 long-form TTS; Projects API (book chapters); voice-consistency monitor
- Architecture pattern (design): Self-Refine (drift detection as feedback loop)

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1110 chars). VA source responsibility: Sustained character + narration |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Audie Awards; AudioFile Earphones; consented narrator corpora |
| 3) Sources exist / know how to obtain them | **YES** | 9 source files + PROVENANCE. VA listed: Audie Awards; AudioFile Earphones; consented narrator corpora |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Vocal stamina (no drift 60min); character distinction (embedding distance) |
| 5) Implementation surpasses human yet? | **NO** | Has live-tool path but no measured human-parity benchmark results in host. Design may state aspirational surpass signals only. VA aspirational signal: Wins AudioFile blind eval at fraction of studio time |
| 6) How they execute the job | **PARTIAL** | Host may invoke media tools ['media.stub', 'media.elevenlabs']; prompt/rubric refs exist but prompts/ are empty stubs for most agents. Not a free-running coding plan agent. VA architecture: Self-Refine (drift detection as feedback loop) |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: DirectorAgent, AuthorAgent; comments on: VOArtistAgent (ove… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.audiobooknarrator.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.audiobooknarrator.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.audiobooknarrator` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.signlanguageinterpreter` — SignLanguageInterpreterAgent

- **VA id / category:** 43 / `7-Edu`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.signlanguageinterpreter.v1` / files=0  
- **Rubric ref / files:** `video.rubric.signlanguageinterpreter.v1` / files=0  
- **Sources / provenance:** files=8 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Accurate ASL/BSL interpretation Host role binding: `SignLanguageInterpreterAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Accurate ASL/BSL interpretation ### Knowledge distillation sour…

**From `agents.md` design row:**

- Responsibility: Accurate ASL/BSL interpretation
- Knowledge distillation source: RID NIC curricula; NAD corpora; Deaf-community consented data
- Self-quality criteria: Sign accuracy (Deaf-reviewer vote); facial-grammar markers
- Surpass-human signal (aspirational): Wins blind NAD-reviewer preference at scale
- Accepts critique from: DeafCommunityReviewAgent (HiTL), LinguistAgent
- Comments on: VoiceCloneAgent (no caption), AccessibilityAgent
- Tool access (design): Sign-avatar rendering (SignAll); MediaPipe pose estimation; facial-action-unit detector
- Architecture pattern (design): RLAIF (reward from Deaf-community review panel)

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1136 chars). VA source responsibility: Accurate ASL/BSL interpretation |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: RID NIC curricula; NAD corpora; Deaf-community consented data |
| 3) Sources exist / know how to obtain them | **YES** | 8 source files + PROVENANCE. VA listed: RID NIC curricula; NAD corpora; Deaf-community consented data |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Sign accuracy (Deaf-reviewer vote); facial-grammar markers |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Wins blind NAD-reviewer preference at scale |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.signlanguageinterpreter.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: RLAIF (reward from Deaf-communit… |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: DeafCommunityReviewAgent (HiTL), LinguistAgent; comments on… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.signlanguageinterpreter.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.signlanguageinterpreter.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.signlanguageinterpreter` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.localizationqa` — LocalizationQAAgent (Linguist)

- **VA id / category:** 44 / `7-Edu`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.localizationqa.v1` / files=0  
- **Rubric ref / files:** `video.rubric.localizationqa.v1` / files=0  
- **Sources / provenance:** files=8 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Translation + cultural fit Host role binding: `LocalizationQAAgent (Linguist) (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Translation + cultural fit ### Knowledge distillation sources (his…

**From `agents.md` design row:**

- Responsibility: Translation + cultural fit
- Knowledge distillation source: LISA QA model; MQM error typology; ATA cert prep
- Self-quality criteria: MQM error/1k words; cultural-flag count
- Surpass-human signal (aspirational): Beats LSP human QA on MQM at 10× speed
- Accepts critique from: NativeReviewerAgent, BrandAgent
- Comments on: VoiceCloneAgent (pronunciation), DubbingAgent
- Tool access (design): DeepL/Google Translate APIs; MQM error annotator; terminology management (memoQ API)
- Architecture pattern (design): Self-Refine (rubric: MQM scoring framework)

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1066 chars). VA source responsibility: Translation + cultural fit |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: LISA QA model; MQM error typology; ATA cert prep |
| 3) Sources exist / know how to obtain them | **YES** | 8 source files + PROVENANCE. VA listed: LISA QA model; MQM error typology; ATA cert prep |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: MQM error/1k words; cultural-flag count |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Beats LSP human QA on MQM at 10× speed |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.localizationqa.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: Self-Refine (rubric: MQM scoring framewor… |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: NativeReviewerAgent, BrandAgent; comments on: VoiceCloneAge… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.localizationqa.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.localizationqa.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.localizationqa` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.realestatephoto` — RealEstatePhotoAgent / 3D Scan

- **VA id / category:** 45 / `7-Edu`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.realestatephoto.v1` / files=0  
- **Rubric ref / files:** `video.rubric.realestatephoto.v1` / files=0  
- **Sources / provenance:** files=7 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.0/11 (Y=2 P=8 N=1)  
- **SPEC responsibility excerpt:** Wide interiors; Matterport scans Host role binding: `RealEstatePhotoAgent / 3D Scan (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Wide interiors; Matterport scans ### Knowledge distillation …

**From `agents.md` design row:**

- Responsibility: Wide interiors; Matterport scans
- Knowledge distillation source: Mike Kelley tutorials; APALA refs
- Self-quality criteria: Vertical-line straightness; HDR stack; coverage %
- Surpass-human signal (aspirational): Listing-CTR uplift vs human-shot baseline
- Accepts critique from: DoPAgent, DronePilotAgent
- Comments on: DronePilotAgent (illegal altitude)
- Tool access (design): Matterport SDK; HDR processing (Luminance HDR); lens-correction tools; Veo 3.1
- Architecture pattern (design): ReAct (assess space → generate views → validate geometry)

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1067 chars). VA source responsibility: Wide interiors; Matterport scans |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Mike Kelley tutorials; APALA refs |
| 3) Sources exist / know how to obtain them | **PARTIAL** | 7 local source files; acquisition path may still be design-only (URLs/corpora not fully licensed). VA listed: Mike Kelley tutorials; APALA refs |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Vertical-line straightness; HDR stack; coverage % |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Listing-CTR uplift vs human-shot baseline |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.realestatephoto.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: ReAct (assess space → generate views → v… |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: DoPAgent, DronePilotAgent; comments on: DronePilotAgent (il… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.realestatephoto.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.realestatephoto.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.realestatephoto` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

### 8-AI — AI-Era Specialists (7 agents, avg maturity 6.5)

#### Group synthesis

- **1) Responsibility well defined in SPEC.md:** dominant **YES** (Y=7, P=0, N=0)
- **2) Plan to distill professional knowledge:** dominant **YES** (Y=7, P=0, N=0)
- **3) Sources exist / know how to obtain them:** dominant **YES** (Y=7, P=0, N=0)
- **4) Self-evaluation methods & content collected:** dominant **PARTIAL** (Y=0, P=7, N=0)
- **5) Implementation surpasses human yet?:** dominant **NO** (Y=0, P=0, N=7)
- **6) How they execute the job:** dominant **PARTIAL** (Y=0, P=7, N=0)
- **7) Skills / plugins / harness for themselves:** dominant **PARTIAL** (Y=0, P=7, N=0)
- **8) Mechanism to improve themselves:** dominant **PARTIAL** (Y=0, P=7, N=0)
- **9) Collect/research info to improve:** dominant **PARTIAL** (Y=0, P=7, N=0)
- **10) Get/send instructions to other agents:** dominant **PARTIAL** (Y=0, P=7, N=0)
- **11) Resolve conflict + confirm:** dominant **PARTIAL** (Y=0, P=7, N=0)

#### Agents

##### `video.promptengineer` — PromptEngineerAgent / GeneratorOperator

- **VA id / category:** 46 / `8-AI`  
- **Status / provider / network:** `registered` / `media_host` / network=True  
- **Tools:** `media.stub, media.sora, media.veo, media.runway`  
- **Prompt ref / files:** `video.prompt.promptengineer.v1` / files=0  
- **Rubric ref / files:** `video.rubric.promptengineer.v1` / files=0  
- **Sources / provenance:** files=14 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Crafts prompts; steers Sora/Veo/Runway/Kling Host role binding: `PromptEngineerAgent / GeneratorOperator (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Crafts prompts; steers Sora/Veo/Runway/…

**From `agents.md` design row:**

- Responsibility: Crafts prompts; steers Sora/Veo/Runway/Kling
- Knowledge distillation source: Karen X. Cheng/Trillo public sets; r/aivideo; Runway AIFF jury notes
- Self-quality criteria: Prompt→output CLIP-T; iteration count to acceptance; seed reproducibility
- Surpass-human signal (aspirational): Target shot in ≤3 iterations vs human avg 10
- Accepts critique from: DirectorAgent, AIQAAgent
- Comments on: AIQAAgent (re-roll budget), ConsistencyAgent
- Tool access (design): Sora 2 API, Veo 3.1, Runway Gen-4/Aleph, Kling 3.0; seed/parameter registries
- Architecture pattern (design): DSPy / OPRO prompt optimization (Yang 2023)

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1156 chars). VA source responsibility: Crafts prompts; steers Sora/Veo/Runway/Kling |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Karen X. Cheng/Trillo public sets; r/aivideo; Runway AIFF jury notes |
| 3) Sources exist / know how to obtain them | **YES** | 14 source files + PROVENANCE. VA listed: Karen X. Cheng/Trillo public sets; r/aivideo; Runway AIFF jury notes |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Prompt→output CLIP-T; iteration count to acceptance; seed reproducibility |
| 5) Implementation surpasses human yet? | **NO** | Has live-tool path but no measured human-parity benchmark results in host. Design may state aspirational surpass signals only. VA aspirational signal: Target shot in ≤3 iterations vs human avg 10 |
| 6) How they execute the job | **PARTIAL** | Host may invoke media tools ['media.stub', 'media.sora', 'media.veo', 'media.runway']; prompt/rubric refs exist but prompts/ are empty stubs for most agents. Not a free-running coding plan agent. VA architecture: DSPy / OPRO prompt optimization (Yang 2023) |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: DirectorAgent, AIQAAgent; comments on: AIQAAgent (re-roll b… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.promptengineer.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.promptengineer.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.promptengineer` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.avatardesign` — AvatarDesignAgent

- **VA id / category:** 47 / `8-AI`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.avatardesign.v1` / files=0  
- **Rubric ref / files:** `video.rubric.avatardesign.v1` / files=0  
- **Sources / provenance:** files=10 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Synthetic-presenter identity Host role binding: `AvatarDesignAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Synthetic-presenter identity ### Knowledge distillation sources (historical) …

**From `agents.md` design row:**

- Responsibility: Synthetic-presenter identity
- Knowledge distillation source: Synthesia/HeyGen design docs; Hany Farid deepfake-detection; C2PA spec
- Self-quality criteria: Identity-hash consistency across shots; consent chain; C2PA signed
- Surpass-human signal (aspirational): C2PA-verifiable + Partnership-on-AI full-pass at scale
- Accepts critique from: ComplianceAgent (consent), DeepfakeDetectionAgent
- Comments on: VoiceCloneAgent (off-likeness), LipSyncAgent
- Tool access (design): HeyGen Avatar IV API; Synthesia API; C2PA signing library (c2patool); face-embedding models
- Architecture pattern (design): Constitutional AI (consent + identity constitution)

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1154 chars). VA source responsibility: Synthetic-presenter identity |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Synthesia/HeyGen design docs; Hany Farid deepfake-detection; C2PA spec |
| 3) Sources exist / know how to obtain them | **YES** | 10 source files + PROVENANCE. VA listed: Synthesia/HeyGen design docs; Hany Farid deepfake-detection; C2PA spec |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Identity-hash consistency across shots; consent chain; C2PA signed |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: C2PA-verifiable + Partnership-on-AI full-pass at scale |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.avatardesign.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: Constitutional AI (consent + identity const… |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: ComplianceAgent (consent), DeepfakeDetectionAgent; comments… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.avatardesign.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.avatardesign.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.avatardesign` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.voiceclone` — VoiceCloneAgent / LipSyncSpecialist

- **VA id / category:** 48 / `8-AI`  
- **Status / provider / network:** `registered` / `media_host` / network=True  
- **Tools:** `media.stub, media.elevenlabs`  
- **Prompt ref / files:** `video.prompt.voiceclone.v1` / files=0  
- **Rubric ref / files:** `video.rubric.voiceclone.v1` / files=0  
- **Sources / provenance:** files=10 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Voice cloning + lip-sync Host role binding: `VoiceCloneAgent / LipSyncSpecialist (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Voice cloning + lip-sync ### Knowledge distillation sources (hi…

**From `agents.md` design row:**

- Responsibility: Voice cloning + lip-sync
- Knowledge distillation source: ElevenLabs safety docs; Wav2Lip/Sync.so; Baxter lip-sync refs
- Self-quality criteria: Voice MOS ≥4.2; phoneme-viseme error <40ms; consent verified
- Surpass-human signal (aspirational): Wins blind MOS vs professional ADR
- Accepts critique from: ComplianceAgent (consent), AnimatorAgent (lip-sync gold)
- Comments on: AvatarDesignAgent (face flicker), DubbingAgent
- Tool access (design): ElevenLabs v3 cloning API; Sync.so lip-sync; Wav2Lip; consent-doc verification
- Architecture pattern (design): Self-Refine + MOS scoring model as judge

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1114 chars). VA source responsibility: Voice cloning + lip-sync |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: ElevenLabs safety docs; Wav2Lip/Sync.so; Baxter lip-sync refs |
| 3) Sources exist / know how to obtain them | **YES** | 10 source files + PROVENANCE. VA listed: ElevenLabs safety docs; Wav2Lip/Sync.so; Baxter lip-sync refs |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Voice MOS ≥4.2; phoneme-viseme error <40ms; consent verified |
| 5) Implementation surpasses human yet? | **NO** | Has live-tool path but no measured human-parity benchmark results in host. Design may state aspirational surpass signals only. VA aspirational signal: Wins blind MOS vs professional ADR |
| 6) How they execute the job | **PARTIAL** | Host may invoke media tools ['media.stub', 'media.elevenlabs']; prompt/rubric refs exist but prompts/ are empty stubs for most agents. Not a free-running coding plan agent. VA architecture: Self-Refine + MOS scoring model as judge |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: ComplianceAgent (consent), AnimatorAgent (lip-sync gold); c… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.voiceclone.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.voiceclone.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.voiceclone` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.aiqaconsistency` — AIQAConsistencyAgent

- **VA id / category:** 49 / `8-AI`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.aiqaconsistency.v1` / files=0  
- **Rubric ref / files:** `video.rubric.aiqaconsistency.v1` / files=0  
- **Sources / provenance:** files=12 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Catches frame drift, hand/face artifacts, identity breaks Host role binding: `AIQAConsistencyAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Catches frame drift, hand/face artifacts, ide…

**From `agents.md` design row:**

- Responsibility: Catches frame drift, hand/face artifacts, identity breaks
- Knowledge distillation source: VBench; EvalCrafter; FVD literature; MPC/Weta QC checklists; deepfake models
- Self-quality criteria: Per-frame artifact score; identity-hash drift; hand/finger pass
- Surpass-human signal (aspirational): Catches >95% of senior QC catches + 30% missed
- Accepts critique from: DirectorAgent, VFXSupAgent
- Comments on: GeneratorAgent (re-roll), CompositorAgent
- Tool access (design): VBench evaluation suite; hand-detector models; face-ID embedding (ArcFace); frame-diff tools
- Architecture pattern (design): Tool-use / ReAct (run detectors → flag → report)

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1182 chars). VA source responsibility: Catches frame drift, hand/face artifacts, identity breaks |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: VBench; EvalCrafter; FVD literature; MPC/Weta QC checklists; deepfake models |
| 3) Sources exist / know how to obtain them | **YES** | 12 source files + PROVENANCE. VA listed: VBench; EvalCrafter; FVD literature; MPC/Weta QC checklists; deepfake models |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Per-frame artifact score; identity-hash drift; hand/finger pass |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Catches >95% of senior QC catches + 30% missed |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.aiqaconsistency.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: Tool-use / ReAct (run detectors → flag →… |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: DirectorAgent, VFXSupAgent; comments on: GeneratorAgent (re… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.aiqaconsistency.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.aiqaconsistency.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.aiqaconsistency` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.personalizationengineer` — PersonalizationEngineerAgent

- **VA id / category:** 50 / `8-AI`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.personalizationengineer.v1` / files=0  
- **Rubric ref / files:** `video.rubric.personalizationengineer.v1` / files=0  
- **Sources / provenance:** files=12 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Variable templates (name/face/voice swap) Host role binding: `PersonalizationEngineerAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Variable templates (name/face/voice swap) ### Knowled…

**From `agents.md` design row:**

- Responsibility: Variable templates (name/face/voice swap)
- Knowledge distillation source: Idomoo case studies; DMA campaigns; MarTech lit
- Self-quality criteria: Render-success ≥99.5%; spot-check pass; privacy-audit pass
- Surpass-human signal (aspirational): Higher share-rate than top human-templated campaigns
- Accepts critique from: ComplianceAgent (GDPR/CCPA), AnalystAgent
- Comments on: TemplateDesignerAgent (fragility)
- Tool access (design): Idomoo/Pirsonal APIs; HeyGen personalization; GDPR consent-management platform
- Architecture pattern (design): ReAct (assemble template → render → validate → deliver)

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1130 chars). VA source responsibility: Variable templates (name/face/voice swap) |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Idomoo case studies; DMA campaigns; MarTech lit |
| 3) Sources exist / know how to obtain them | **YES** | 12 source files + PROVENANCE. VA listed: Idomoo case studies; DMA campaigns; MarTech lit |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Render-success ≥99.5%; spot-check pass; privacy-audit pass |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Higher share-rate than top human-templated campaigns |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.personalizationengineer.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: ReAct (assemble template → rende… |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: ComplianceAgent (GDPR/CCPA), AnalystAgent; comments on: Tem… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.personalizationengineer.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.personalizationengineer.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.personalizationengineer` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.trailereditor` — TrailerEditorAgent

- **VA id / category:** 51 / `8-AI`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.trailereditor.v1` / files=0  
- **Rubric ref / files:** `video.rubric.trailereditor.v1` / files=0  
- **Sources / provenance:** files=9 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Hook-driven trailer cuts Host role binding: `TrailerEditorAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Hook-driven trailer cuts ### Knowledge distillation sources (historical) Golden …

**From `agents.md` design row:**

- Responsibility: Hook-driven trailer cuts
- Knowledge distillation source: Golden Trailer Awards; Woollen/AV Squad reels; trailer-music libs
- Self-quality criteria: Hook-rate at 3s; rising-action curve; music-sync precision
- Surpass-human signal (aspirational): Wins Golden-Trailer-rubric blind comparison
- Accepts critique from: DirectorAgent, MusicSupervisorAgent
- Comments on: EditorAgent (over-cut), ComposerAgent (mismatch)
- Tool access (design): DaVinci Resolve (MCP); trailer-music APIs (Musicbed/Artlist); retention-curve predictor
- Architecture pattern (design): Self-Refine (retention-curve model as feedback)

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1105 chars). VA source responsibility: Hook-driven trailer cuts |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Golden Trailer Awards; Woollen/AV Squad reels; trailer-music libs |
| 3) Sources exist / know how to obtain them | **YES** | 9 source files + PROVENANCE. VA listed: Golden Trailer Awards; Woollen/AV Squad reels; trailer-music libs |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Hook-rate at 3s; rising-action curve; music-sync precision |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Wins Golden-Trailer-rubric blind comparison |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.trailereditor.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: Self-Refine (retention-curve model as feed… |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: DirectorAgent, MusicSupervisorAgent; comments on: EditorAge… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.trailereditor.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.trailereditor.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.trailereditor` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.sportsanalyst` — SportsAnalystAgent / TelestratorOp

- **VA id / category:** 52 / `8-AI`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.sportsanalyst.v1` / files=0  
- **Rubric ref / files:** `video.rubric.sportsanalyst.v1` / files=0  
- **Sources / provenance:** files=8 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Tactical breakdowns + diagrams Host role binding: `SportsAnalystAgent / TelestratorOp (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Tactical breakdowns + diagrams ### Knowledge distillation …

**From `agents.md` design row:**

- Responsibility: Tactical breakdowns + diagrams
- Knowledge distillation source: MIT Sloan papers; ESPN Stats & Info; Goldsberry analytics
- Self-quality criteria: Play-call accuracy; on-screen clarity score
- Surpass-human signal (aspirational): Beats ex-athlete on tactical-prediction
- Accepts critique from: SMEAgent (sport), JournalistAgent
- Comments on: EditorAgent (missed-replay), MotionGraphicsAgent (chart clarity)
- Tool access (design): Sports data APIs (StatsBomb, NBA Stats); telestration overlay tools; After Effects MCP
- Architecture pattern (design): ReAct (fetch play data → annotate → render overlay)

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1123 chars). VA source responsibility: Tactical breakdowns + diagrams |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: MIT Sloan papers; ESPN Stats & Info; Goldsberry analytics |
| 3) Sources exist / know how to obtain them | **YES** | 8 source files + PROVENANCE. VA listed: MIT Sloan papers; ESPN Stats & Info; Goldsberry analytics |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Play-call accuracy; on-screen clarity score |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Beats ex-athlete on tactical-prediction |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.sportsanalyst.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: ReAct (fetch play data → annotate → render… |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: SMEAgent (sport), JournalistAgent; comments on: EditorAgent… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.sportsanalyst.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.sportsanalyst.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.sportsanalyst` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

### 9-Meta — Specialist Meta-Agents (28 agents, avg maturity 6.5)

#### Group synthesis

- **1) Responsibility well defined in SPEC.md:** dominant **YES** (Y=28, P=0, N=0)
- **2) Plan to distill professional knowledge:** dominant **YES** (Y=28, P=0, N=0)
- **3) Sources exist / know how to obtain them:** dominant **YES** (Y=28, P=0, N=0)
- **4) Self-evaluation methods & content collected:** dominant **PARTIAL** (Y=0, P=28, N=0)
- **5) Implementation surpasses human yet?:** dominant **NO** (Y=0, P=0, N=28)
- **6) How they execute the job:** dominant **PARTIAL** (Y=0, P=28, N=0)
- **7) Skills / plugins / harness for themselves:** dominant **PARTIAL** (Y=0, P=28, N=0)
- **8) Mechanism to improve themselves:** dominant **PARTIAL** (Y=0, P=28, N=0)
- **9) Collect/research info to improve:** dominant **PARTIAL** (Y=0, P=28, N=0)
- **10) Get/send instructions to other agents:** dominant **PARTIAL** (Y=0, P=28, N=0)
- **11) Resolve conflict + confirm:** dominant **PARTIAL** (Y=0, P=28, N=0)

#### Agents

##### `video.orchestrator` — OrchestratorAgent

- **VA id / category:** 53 / `9-Meta`  
- **Status / provider / network:** `registered` / `media_host` / network=True  
- **Tools:** `media.stub`  
- **Prompt ref / files:** `video.prompt.orchestrator.v1` / files=0  
- **Rubric ref / files:** `video.rubric.orchestrator.v1` / files=0  
- **Sources / provenance:** files=21 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Runs CrewAI/AutoGen/LangGraph DAG; retries, timeouts, fan-out/fan-in Host role binding: `OrchestratorAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Runs CrewAI/AutoGen/LangGraph DAG; re…

**From `agents.md` design row:**

- Responsibility: Runs CrewAI/AutoGen/LangGraph DAG; retries, timeouts, fan-out/fan-in
- Knowledge distillation source: LangGraph + CrewAI + AutoGen patterns; Airflow/Temporal; PGA schedule templates
- Self-quality criteria: DAG completion ≥99.5%; SLA adherence; deadlock = 0
- Surpass-human signal (aspirational): Lower TTD than human EP at same scope
- Accepts critique from: ProducerAgent (scope), JudgeAgent (dispute), HiTL on stall
- Comments on: All agents (resource burn, retry storms)
- Tool access (design): LangGraph state machine; Temporal workflow engine; Redis (distributed locks); observability (LangSmith)
- Architecture pattern (design): Agentic Graph (LangGraph) — deterministic DAG execution

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1231 chars). VA source responsibility: Runs CrewAI/AutoGen/LangGraph DAG; retries, timeouts, fan-out/fan-in |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: LangGraph + CrewAI + AutoGen patterns; Airflow/Temporal; PGA schedule templates |
| 3) Sources exist / know how to obtain them | **YES** | 21 source files + PROVENANCE. VA listed: LangGraph + CrewAI + AutoGen patterns; Airflow/Temporal; PGA schedule templates |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: DAG completion ≥99.5%; SLA adherence; deadlock = 0 |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Lower TTD than human EP at same scope |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.orchestrator.v1; provider=media_host; tools=['media.stub']. No per-agent autonomous coding-plan runner installed by default. VA architecture: Agentic Graph (LangGraph) — deterministic DAG executi… |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: ProducerAgent (scope), JudgeAgent (dispute), HiTL on stall;… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.orchestrator.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.orchestrator.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.orchestrator` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.planner` — PlannerAgent

- **VA id / category:** 54 / `9-Meta`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.planner.v1` / files=0  
- **Rubric ref / files:** `video.rubric.planner.v1` / files=0  
- **Sources / provenance:** files=24 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Decomposes brief into phased DAG with assignments + critic gates Host role binding: `PlannerAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Decomposes brief into phased DAG with assignme…

**From `agents.md` design row:**

- Responsibility: Decomposes brief into phased DAG with assignments + critic gates
- Knowledge distillation source: PMBOK; CrewAI task graphs; phase templates
- Self-quality criteria: Plan validity (no missing gate); cost variance <10%
- Surpass-human signal (aspirational): Tighter, cheaper plans than EP first pass (blind A/B)
- Accepts critique from: ProducerAgent, FinanceAgent (budget)
- Comments on: RouterAgent (wrong pick), OrchestratorAgent
- Tool access (design): LangGraph plan-gen; cost-estimation models; Gantt/PERT tools
- Architecture pattern (design): ReAct (decompose → estimate → validate → emit DAG)

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1131 chars). VA source responsibility: Decomposes brief into phased DAG with assignments + critic gates |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: PMBOK; CrewAI task graphs; phase templates |
| 3) Sources exist / know how to obtain them | **YES** | 24 source files + PROVENANCE. VA listed: PMBOK; CrewAI task graphs; phase templates |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Plan validity (no missing gate); cost variance <10% |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Tighter, cheaper plans than EP first pass (blind A/B) |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.planner.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: ReAct (decompose → estimate → validate → emit DA… |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: ProducerAgent, FinanceAgent (budget); comments on: RouterAg… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.planner.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.planner.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.planner` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.router` — RouterAgent

- **VA id / category:** 55 / `9-Meta`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.router.v1` / files=0  
- **Rubric ref / files:** `video.rubric.router.v1` / files=0  
- **Sources / provenance:** files=22 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Picks right specialist agent (and model) for each subtask Host role binding: `RouterAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Picks right specialist agent (and model) for each subt…

**From `agents.md` design row:**

- Responsibility: Picks right specialist agent (and model) for each subtask
- Knowledge distillation source: Agent-capability registry; benchmark history (cost/quality/latency)
- Self-quality criteria: Routing accuracy ≥95% vs oracle; cost within budget
- Surpass-human signal (aspirational): Beats human producer in agent/vendor selection
- Accepts critique from: OrchestratorAgent, CostOptimizerAgent
- Comments on: PlannerAgent (bad decomposition)
- Tool access (design): Agent registry DB; benchmark leaderboard cache; pricing APIs
- Architecture pattern (design): Classifier + ReAct (match task embedding → agent capability)

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1134 chars). VA source responsibility: Picks right specialist agent (and model) for each subtask |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Agent-capability registry; benchmark history (cost/quality/latency) |
| 3) Sources exist / know how to obtain them | **YES** | 22 source files + PROVENANCE. VA listed: Agent-capability registry; benchmark history (cost/quality/latency) |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Routing accuracy ≥95% vs oracle; cost within budget |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Beats human producer in agent/vendor selection |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.router.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: Classifier + ReAct (match task embedding → agent … |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: OrchestratorAgent, CostOptimizerAgent; comments on: Planner… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.router.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.router.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.router` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.judge` — JudgeAgent

- **VA id / category:** 56 / `9-Meta`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.judge.v1` / files=0  
- **Rubric ref / files:** `video.rubric.judge.v1` / files=0  
- **Sources / provenance:** files=23 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Adjudicates disputes via multi-agent debate; scores against rubric Host role binding: `JudgeAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Adjudicates disputes via multi-agent debate; s…

**From `agents.md` design row:**

- Responsibility: Adjudicates disputes via multi-agent debate; scores against rubric
- Knowledge distillation source: Du 2023 (LLM debate); MT-Bench rubrics; guild scoring sheets
- Self-quality criteria: Inter-rater κ vs expert panel ≥0.8
- Surpass-human signal (aspirational): Higher κ than median human juror
- Accepts critique from: HiTL on overturned rulings
- Comments on: DirectorAgent, ScreenwriterAgent, any disputing pair
- Tool access (design): MT-Bench/Arena evaluation harness; rubric template engine
- Architecture pattern (design): Multi-agent debate (Du 2023) + LLM-as-Judge (Zheng 2023)

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1115 chars). VA source responsibility: Adjudicates disputes via multi-agent debate; scores against rubric |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Du 2023 (LLM debate); MT-Bench rubrics; guild scoring sheets |
| 3) Sources exist / know how to obtain them | **YES** | 23 source files + PROVENANCE. VA listed: Du 2023 (LLM debate); MT-Bench rubrics; guild scoring sheets |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Inter-rater κ vs expert panel ≥0.8 |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Higher κ than median human juror |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.judge.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: Multi-agent debate (Du 2023) + LLM-as-Judge (Zheng… |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: HiTL on overturned rulings; comments on: DirectorAgent, Scr… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.judge.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.judge.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.judge` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.gatekeeper` — GateKeeperAgent

- **VA id / category:** 57 / `9-Meta`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.gatekeeper.v1` / files=0  
- **Rubric ref / files:** `video.rubric.gatekeeper.v1` / files=0  
- **Sources / provenance:** files=15 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Phase transitions; verifies L1/L2/L3 criteria; signs C2PA Host role binding: `GateKeeperAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Phase transitions; verifies L1/L2/L3 criteria; sig…

**From `agents.md` design row:**

- Responsibility: Phase transitions; verifies L1/L2/L3 criteria; signs C2PA
- Knowledge distillation source: Stage-gate methodology; PGA Producers Mark; QMS audit
- Self-quality criteria: Zero leaked defects; sign-off SLA ≥99%
- Surpass-human signal (aspirational): Lower escaped-defect rate than human QA lead
- Accepts critique from: ComplianceAgent, AIQAConsistencyAgent
- Comments on: OrchestratorAgent (premature advance)
- Tool access (design): C2PA signing (c2patool); JSON schema validators; rubric evaluation endpoints
- Architecture pattern (design): Constitutional AI (constitution = phase-gate criteria)

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1124 chars). VA source responsibility: Phase transitions; verifies L1/L2/L3 criteria; signs C2PA |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Stage-gate methodology; PGA Producers Mark; QMS audit |
| 3) Sources exist / know how to obtain them | **YES** | 15 source files + PROVENANCE. VA listed: Stage-gate methodology; PGA Producers Mark; QMS audit |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Zero leaked defects; sign-off SLA ≥99% |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Lower escaped-defect rate than human QA lead |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.gatekeeper.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: Constitutional AI (constitution = phase-gate … |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: ComplianceAgent, AIQAConsistencyAgent; comments on: Orchest… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.gatekeeper.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.gatekeeper.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.gatekeeper` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.memory` — MemoryAgent

- **VA id / category:** 58 / `9-Meta`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.memory.v1` / files=0  
- **Rubric ref / files:** `video.rubric.memory.v1` / files=0  
- **Sources / provenance:** files=28 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Episodic + long-term project memory; retrieval for any agent Host role binding: `MemoryAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Episodic + long-term project memory; retrieval for …

**From `agents.md` design row:**

- Responsibility: Episodic + long-term project memory; retrieval for any agent
- Knowledge distillation source: Reflexion (Shinn 2023); MemGPT; vector-DB best practices
- Self-quality criteria: Retrieval precision@5 ≥0.9; freshness SLA
- Surpass-human signal (aspirational): Higher recall than producer's bible at scale
- Accepts critique from: All agents (correction events)
- Comments on: All agents (stale facts)
- Tool access (design): Pinecone/Weaviate/Qdrant vector DB; MemGPT-style hierarchical memory; embedding models
- Architecture pattern (design): Reflexion memory architecture (MemGPT extension)

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1116 chars). VA source responsibility: Episodic + long-term project memory; retrieval for any agent |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Reflexion (Shinn 2023); MemGPT; vector-DB best practices |
| 3) Sources exist / know how to obtain them | **YES** | 28 source files + PROVENANCE. VA listed: Reflexion (Shinn 2023); MemGPT; vector-DB best practices |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Retrieval precision@5 ≥0.9; freshness SLA |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Higher recall than producer's bible at scale |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.memory.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: Reflexion memory architecture (MemGPT extension) |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: All agents (correction events); comments on: All agents (st… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.memory.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.memory.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.memory` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.ideation` — IdeationAgent

- **VA id / category:** 59 / `9-Meta`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.ideation.v1` / files=0  
- **Rubric ref / files:** `video.rubric.ideation.v1` / files=0  
- **Sources / provenance:** files=16 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Divergent brainstorm of concepts, hooks, taglines Host role binding: `IdeationAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Divergent brainstorm of concepts, hooks, taglines ### Knowle…

**From `agents.md` design row:**

- Responsibility: Divergent brainstorm of concepts, hooks, taglines
- Knowledge distillation source: Cannes Grand Prix; D&AD; IDEO design-thinking; SCAMPER/de Bono
- Self-quality criteria: Idea-count; novelty (embedding distance); semantic diversity
- Surpass-human signal (aspirational): Wins agency-pitch shootouts on concept density
- Accepts critique from: CreativeDirectorAgent, NoveltyAgent
- Comments on: CopywriterAgent (derivative), DirectorAgent (unfilmable)
- Tool access (design): Embedding novelty scorer; concept clustering (UMAP); Are.na/Pinterest search
- Architecture pattern (design): Self-Refine + NoveltyAgent as critic

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1138 chars). VA source responsibility: Divergent brainstorm of concepts, hooks, taglines |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Cannes Grand Prix; D&AD; IDEO design-thinking; SCAMPER/de Bono |
| 3) Sources exist / know how to obtain them | **YES** | 16 source files + PROVENANCE. VA listed: Cannes Grand Prix; D&AD; IDEO design-thinking; SCAMPER/de Bono |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Idea-count; novelty (embedding distance); semantic diversity |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Wins agency-pitch shootouts on concept density |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.ideation.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: Self-Refine + NoveltyAgent as critic |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: CreativeDirectorAgent, NoveltyAgent; comments on: Copywrite… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.ideation.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.ideation.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.ideation` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.narrativearc` — NarrativeArcAgent

- **VA id / category:** 60 / `9-Meta`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.narrativearc.v1` / files=0  
- **Rubric ref / files:** `video.rubric.narrativearc.v1` / files=0  
- **Sources / provenance:** files=13 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** 3-act / Save-the-Cat / Hero's Journey structure Host role binding: `NarrativeArcAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) 3-act / Save-the-Cat / Hero's Journey structure ### Knowle…

**From `agents.md` design row:**

- Responsibility: 3-act / Save-the-Cat / Hero's Journey structure
- Knowledge distillation source: Campbell; Snyder *Save the Cat*; Truby; Black List analyses
- Self-quality criteria: Beat-sheet coverage 100%; turning-point spacing; arc curve fit
- Surpass-human signal (aspirational): Beats WGA first drafts on structural rubric
- Accepts critique from: ScreenwriterAgent, DirectorAgent
- Comments on: ScreenwriterAgent (sagging middle)
- Tool access (design): Beat-sheet validator; emotional-arc plotter; structure templates
- Architecture pattern (design): Self-Refine (rubric: beat-sheet completeness)

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1106 chars). VA source responsibility: 3-act / Save-the-Cat / Hero's Journey structure |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Campbell; Snyder *Save the Cat*; Truby; Black List analyses |
| 3) Sources exist / know how to obtain them | **YES** | 13 source files + PROVENANCE. VA listed: Campbell; Snyder *Save the Cat*; Truby; Black List analyses |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Beat-sheet coverage 100%; turning-point spacing; arc curve fit |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Beats WGA first drafts on structural rubric |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.narrativearc.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: Self-Refine (rubric: beat-sheet completenes… |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: ScreenwriterAgent, DirectorAgent; comments on: Screenwriter… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.narrativearc.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.narrativearc.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.narrativearc` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.styletransfer` — StyleTransferAgent

- **VA id / category:** 61 / `9-Meta`  
- **Status / provider / network:** `registered` / `media_host` / network=True  
- **Tools:** `media.stub, media.runway, media.veo`  
- **Prompt ref / files:** `video.prompt.styletransfer.v1` / files=0  
- **Rubric ref / files:** `video.rubric.styletransfer.v1` / files=0  
- **Sources / provenance:** files=13 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Applies named aesthetic consistently across shots Host role binding: `StyleTransferAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Applies named aesthetic consistently across shots ### K…

**From `agents.md` design row:**

- Responsibility: Applies named aesthetic consistently across shots
- Knowledge distillation source: Curated style corpora; LoRA/seed registries; reference-frame banks
- Self-quality criteria: Style-similarity (CLIP/DINO) ≥0.85; cross-shot variance ≤τ
- Surpass-human signal (aspirational): Wins blind preference vs human colorist+grader
- Accepts critique from: DirectorAgent, ColoristAgent
- Comments on: GeneratorAgent (off-style)
- Tool access (design): LoRA weights per style; CLIP/DINO similarity scorer; Runway style-lock mode; ComfyUI
- Architecture pattern (design): Self-Refine (CLIP style score as feedback)

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1122 chars). VA source responsibility: Applies named aesthetic consistently across shots |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Curated style corpora; LoRA/seed registries; reference-frame banks |
| 3) Sources exist / know how to obtain them | **YES** | 13 source files + PROVENANCE. VA listed: Curated style corpora; LoRA/seed registries; reference-frame banks |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Style-similarity (CLIP/DINO) ≥0.85; cross-shot variance ≤τ |
| 5) Implementation surpasses human yet? | **NO** | Has live-tool path but no measured human-parity benchmark results in host. Design may state aspirational surpass signals only. VA aspirational signal: Wins blind preference vs human colorist+grader |
| 6) How they execute the job | **PARTIAL** | Host may invoke media tools ['media.stub', 'media.runway', 'media.veo']; prompt/rubric refs exist but prompts/ are empty stubs for most agents. Not a free-running coding plan agent. VA architecture: Self-Refine (CLIP style score as feedback) |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: DirectorAgent, ColoristAgent; comments on: GeneratorAgent (… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.styletransfer.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.styletransfer.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.styletransfer` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.worldbuilding` — WorldBuildingAgent

- **VA id / category:** 62 / `9-Meta`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.worldbuilding.v1` / files=0  
- **Rubric ref / files:** `video.rubric.worldbuilding.v1` / files=0  
- **Sources / provenance:** files=12 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Lore, rules, geography, factions, magic/tech systems Host role binding: `WorldBuildingAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Lore, rules, geography, factions, magic/tech systems…

**From `agents.md` design row:**

- Responsibility: Lore, rules, geography, factions, magic/tech systems
- Knowledge distillation source: Tolkien; *Worldbuilding* (Adams); fan-wikis; series-bible leaks
- Self-quality criteria: Internal-consistency (no contradictions); rule-completeness
- Surpass-human signal (aspirational): Lower contradiction rate than writers' bibles at 10× volume
- Accepts critique from: ShowrunnerAgent, FactCheckerAgent
- Comments on: ScreenwriterAgent (lore break), ConceptArtistAgent
- Tool access (design): Long-context LLM (Gemini 2.5 Pro); contradiction-detection model; wiki-graph DB
- Architecture pattern (design): Reflexion (contradiction corrections → episodic memory)

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1176 chars). VA source responsibility: Lore, rules, geography, factions, magic/tech systems |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Tolkien; *Worldbuilding* (Adams); fan-wikis; series-bible leaks |
| 3) Sources exist / know how to obtain them | **YES** | 12 source files + PROVENANCE. VA listed: Tolkien; *Worldbuilding* (Adams); fan-wikis; series-bible leaks |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Internal-consistency (no contradictions); rule-completeness |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Lower contradiction rate than writers' bibles at 10× volume |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.worldbuilding.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: Reflexion (contradiction corrections → epi… |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: ShowrunnerAgent, FactCheckerAgent; comments on: Screenwrite… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.worldbuilding.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.worldbuilding.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.worldbuilding` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.moodboard` — MoodBoardAgent

- **VA id / category:** 63 / `9-Meta`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.moodboard.v1` / files=0  
- **Rubric ref / files:** `video.rubric.moodboard.v1` / files=0  
- **Sources / provenance:** files=13 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Reference boards: visual, sonic, tonal Host role binding: `MoodBoardAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Reference boards: visual, sonic, tonal ### Knowledge distillation sour…

**From `agents.md` design row:**

- Responsibility: Reference boards: visual, sonic, tonal
- Knowledge distillation source: Pinterest/Are.na; lookbook archives; Spotify-Canvas
- Self-quality criteria: Reference coherence (cluster tightness); brief alignment
- Surpass-human signal (aspirational): Faster + tighter boards than art director (blind A/B)
- Accepts critique from: DirectorAgent, ProductionDesignAgent
- Comments on: ConceptArtistAgent (off-mood)
- Tool access (design): Pinterest/Are.na APIs; Spotify Canvas; CLIP clustering; Figma board generation
- Architecture pattern (design): ReAct (search → cluster → layout → validate coherence)

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1103 chars). VA source responsibility: Reference boards: visual, sonic, tonal |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Pinterest/Are.na; lookbook archives; Spotify-Canvas |
| 3) Sources exist / know how to obtain them | **YES** | 13 source files + PROVENANCE. VA listed: Pinterest/Are.na; lookbook archives; Spotify-Canvas |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Reference coherence (cluster tightness); brief alignment |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Faster + tighter boards than art director (blind A/B) |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.moodboard.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: ReAct (search → cluster → layout → validate co… |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: DirectorAgent, ProductionDesignAgent; comments on: ConceptA… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.moodboard.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.moodboard.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.moodboard` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.novelty` — NoveltyAgent / Anti-Cliché Critic

- **VA id / category:** 64 / `9-Meta`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.novelty.v1` / files=0  
- **Rubric ref / files:** `video.rubric.novelty.v1` / files=0  
- **Sources / provenance:** files=13 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Flags tropes, clichés, over-fit outputs Host role binding: `NoveltyAgent / Anti-Cliché Critic (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Flags tropes, clichés, over-fit outputs ### Knowle…

**From `agents.md` design row:**

- Responsibility: Flags tropes, clichés, over-fit outputs
- Knowledge distillation source: TV Tropes; OpenSubtitles n-gram freq; corpus-novelty embeddings
- Self-quality criteria: Cliché-hit count; novelty score vs category prior
- Surpass-human signal (aspirational): Catches more clichés than experienced script editor
- Accepts critique from: IdeationAgent, ScreenwriterAgent
- Comments on: ScreenwriterAgent (trope-stuffed), CopywriterAgent (templated)
- Tool access (design): TV Tropes scraper; n-gram frequency DB; embedding novelty scorer
- Architecture pattern (design): LLM-as-Judge (anti-cliché constitution)

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1127 chars). VA source responsibility: Flags tropes, clichés, over-fit outputs |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: TV Tropes; OpenSubtitles n-gram freq; corpus-novelty embeddings |
| 3) Sources exist / know how to obtain them | **YES** | 13 source files + PROVENANCE. VA listed: TV Tropes; OpenSubtitles n-gram freq; corpus-novelty embeddings |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Cliché-hit count; novelty score vs category prior |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Catches more clichés than experienced script editor |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.novelty.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: LLM-as-Judge (anti-cliché constitution) |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: IdeationAgent, ScreenwriterAgent; comments on: Screenwriter… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.novelty.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.novelty.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.novelty` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.emotionalarc` — EmotionalArcAgent

- **VA id / category:** 65 / `9-Meta`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.emotionalarc.v1` / files=0  
- **Rubric ref / files:** `video.rubric.emotionalarc.v1` / files=0  
- **Sources / provenance:** files=12 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Maps valence/arousal curve; suggests beats Host role binding: `EmotionalArcAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Maps valence/arousal curve; suggests beats ### Knowledge distil…

**From `agents.md` design row:**

- Responsibility: Maps valence/arousal curve; suggests beats
- Knowledge distillation source: Plutchik; affective-computing corpora; Cron *Story Genius*
- Self-quality criteria: Curve-fit to target; biosignal-proxy regression accuracy
- Surpass-human signal (aspirational): Better retention prediction than NRG test-screening cards
- Accepts critique from: DirectorAgent, EditorAgent, ComposerAgent
- Comments on: EditorAgent (flat middle), ComposerAgent (cue mismatch)
- Tool access (design): Sentiment/emotion classifiers (GoEmotions); retention-curve predictor; biosignal proxy model
- Architecture pattern (design): Self-Refine (emotional-arc curve as rubric target)

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1166 chars). VA source responsibility: Maps valence/arousal curve; suggests beats |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Plutchik; affective-computing corpora; Cron *Story Genius* |
| 3) Sources exist / know how to obtain them | **YES** | 12 source files + PROVENANCE. VA listed: Plutchik; affective-computing corpora; Cron *Story Genius* |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Curve-fit to target; biosignal-proxy regression accuracy |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Better retention prediction than NRG test-screening cards |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.emotionalarc.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: Self-Refine (emotional-arc curve as rubric … |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: DirectorAgent, EditorAgent, ComposerAgent; comments on: Edi… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.emotionalarc.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.emotionalarc.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.emotionalarc` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.webresearch` — WebResearchAgent

- **VA id / category:** 66 / `9-Meta`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.webresearch.v1` / files=0  
- **Rubric ref / files:** `video.rubric.webresearch.v1` / files=0  
- **Sources / provenance:** files=11 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Live web search, source ranking, citation extraction Host role binding: `WebResearchAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Live web search, source ranking, citation extraction #…

**From `agents.md` design row:**

- Responsibility: Live web search, source ranking, citation extraction
- Knowledge distillation source: Bing/Google/Brave APIs; Common Crawl; Perplexity patterns
- Self-quality criteria: Source-grade per claim; citation precision; recency hit
- Surpass-human signal (aspirational): Faster + more sources than newsroom researcher
- Accepts critique from: FactCheckerAgent, CitationAgent
- Comments on: ScriptwriterAgent (uncited claim)
- Tool access (design): Brave/Google Search API; Jina Reader (web→markdown); source-quality classifier
- Architecture pattern (design): ReAct (query → fetch → extract → grade → cite)

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1122 chars). VA source responsibility: Live web search, source ranking, citation extraction |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Bing/Google/Brave APIs; Common Crawl; Perplexity patterns |
| 3) Sources exist / know how to obtain them | **YES** | 11 source files + PROVENANCE. VA listed: Bing/Google/Brave APIs; Common Crawl; Perplexity patterns |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Source-grade per claim; citation precision; recency hit |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Faster + more sources than newsroom researcher |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.webresearch.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: ReAct (query → fetch → extract → grade → cit… |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: FactCheckerAgent, CitationAgent; comments on: ScriptwriterA… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.webresearch.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.webresearch.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.webresearch` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.archiveresearch` — ArchiveResearchAgent

- **VA id / category:** 67 / `9-Meta`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.archiveresearch.v1` / files=0  
- **Rubric ref / files:** `video.rubric.archiveresearch.v1` / files=0  
- **Sources / provenance:** files=11 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Historical / academic / archival deep search Host role binding: `ArchiveResearchAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Historical / academic / archival deep search ### Knowledge…

**From `agents.md` design row:**

- Responsibility: Historical / academic / archival deep search
- Knowledge distillation source: JSTOR, arXiv, PubMed, AP Archive, Getty, FOIA
- Self-quality criteria: Primary-source ratio; archive-coverage breadth
- Surpass-human signal (aspirational): Higher primary-source ratio than doc producer
- Accepts critique from: FactCheckerAgent, SMEAgent
- Comments on: ScriptwriterAgent (secondary-source reliance)
- Tool access (design): JSTOR/arXiv/PubMed APIs; Getty Images API; FOIA request tools; OCR (Tesseract)
- Architecture pattern (design): ReAct (formulate query → search archive → extract → grade source)

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1114 chars). VA source responsibility: Historical / academic / archival deep search |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: JSTOR, arXiv, PubMed, AP Archive, Getty, FOIA |
| 3) Sources exist / know how to obtain them | **YES** | 11 source files + PROVENANCE. VA listed: JSTOR, arXiv, PubMed, AP Archive, Getty, FOIA |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Primary-source ratio; archive-coverage breadth |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Higher primary-source ratio than doc producer |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.archiveresearch.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: ReAct (formulate query → search archive … |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: FactCheckerAgent, SMEAgent; comments on: ScriptwriterAgent … |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.archiveresearch.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.archiveresearch.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.archiveresearch` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.trendintelligence` — TrendIntelligenceAgent

- **VA id / category:** 68 / `9-Meta`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.trendintelligence.v1` / files=0  
- **Rubric ref / files:** `video.rubric.trendintelligence.v1` / files=0  
- **Sources / provenance:** files=10 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Detects emerging memes, sounds, formats Host role binding: `TrendIntelligenceAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Detects emerging memes, sounds, formats ### Knowledge distill…

**From `agents.md` design row:**

- Responsibility: Detects emerging memes, sounds, formats
- Knowledge distillation source: TikTok Creative Center; Trendpop; Tubular; Reddit/X firehose
- Self-quality criteria: Prediction lead time vs peak; precision/recall on trend list
- Surpass-human signal (aspirational): Earlier detection than human strategists at higher precision
- Accepts critique from: SocialStrategistAgent, CopywriterAgent
- Comments on: IdeationAgent (off-trend)
- Tool access (design): TikTok Creative Center API; Reddit/X streaming APIs; Sensor Tower; Google Trends
- Architecture pattern (design): ReAct + time-series anomaly detection

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1116 chars). VA source responsibility: Detects emerging memes, sounds, formats |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: TikTok Creative Center; Trendpop; Tubular; Reddit/X firehose |
| 3) Sources exist / know how to obtain them | **YES** | 10 source files + PROVENANCE. VA listed: TikTok Creative Center; Trendpop; Tubular; Reddit/X firehose |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Prediction lead time vs peak; precision/recall on trend list |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Earlier detection than human strategists at higher precision |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.trendintelligence.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: ReAct + time-series anomaly detection |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: SocialStrategistAgent, CopywriterAgent; comments on: Ideati… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.trendintelligence.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.trendintelligence.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.trendintelligence` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.competitorintelligence` — CompetitorIntelligenceAgent

- **VA id / category:** 69 / `9-Meta`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.competitorintelligence.v1` / files=0  
- **Rubric ref / files:** `video.rubric.competitorintelligence.v1` / files=0  
- **Sources / provenance:** files=9 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** What competitors are shipping Host role binding: `CompetitorIntelligenceAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) What competitors are shipping ### Knowledge distillation sources (…

**From `agents.md` design row:**

- Responsibility: What competitors are shipping
- Knowledge distillation source: Meta Ad Library; TikTok Top Ads; YouTube scrape; release trackers
- Self-quality criteria: Coverage % of competitor set; our-novelty vs landscape
- Surpass-human signal (aspirational): More comprehensive than agency strategy decks
- Accepts critique from: BrandAgent, CreativeDirectorAgent
- Comments on: IdeationAgent (derivative)
- Tool access (design): Meta Ad Library API; TikTok Top Ads; SimilarWeb; YouTube Data API v3
- Architecture pattern (design): ReAct (scrape competitor → classify → report gaps)

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1082 chars). VA source responsibility: What competitors are shipping |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Meta Ad Library; TikTok Top Ads; YouTube scrape; release trackers |
| 3) Sources exist / know how to obtain them | **YES** | 9 source files + PROVENANCE. VA listed: Meta Ad Library; TikTok Top Ads; YouTube scrape; release trackers |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Coverage % of competitor set; our-novelty vs landscape |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: More comprehensive than agency strategy decks |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.competitorintelligence.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: ReAct (scrape competitor → classi… |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: BrandAgent, CreativeDirectorAgent; comments on: IdeationAge… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.competitorintelligence.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.competitorintelligence.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.competitorintelligence` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.citation` — CitationAgent

- **VA id / category:** 70 / `9-Meta`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.citation.v1` / files=0  
- **Rubric ref / files:** `video.rubric.citation.v1` / files=0  
- **Sources / provenance:** files=17 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Normalizes sources; grades primary/secondary/tertiary Host role binding: `CitationAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Normalizes sources; grades primary/secondary/tertiary ##…

**From `agents.md` design row:**

- Responsibility: Normalizes sources; grades primary/secondary/tertiary
- Knowledge distillation source: Chicago, APA, AP style; SPJ grading; CRAAP test
- Self-quality criteria: Citation format 100% valid; primary % ≥target
- Surpass-human signal (aspirational): Lower error rate than newsroom copy desk
- Accepts critique from: FactCheckerAgent, JournalistAgent
- Comments on: WebResearchAgent (weak source)
- Tool access (design): Citation parsers (AnyStyle); DOI resolver; CRAAP scoring model
- Architecture pattern (design): Self-Refine (format validator + source grader as rubric)

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1088 chars). VA source responsibility: Normalizes sources; grades primary/secondary/tertiary |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Chicago, APA, AP style; SPJ grading; CRAAP test |
| 3) Sources exist / know how to obtain them | **YES** | 17 source files + PROVENANCE. VA listed: Chicago, APA, AP style; SPJ grading; CRAAP test |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Citation format 100% valid; primary % ≥target |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Lower error rate than newsroom copy desk |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.citation.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: Self-Refine (format validator + source grader a… |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: FactCheckerAgent, JournalistAgent; comments on: WebResearch… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.citation.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.citation.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.citation` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.interviewsynthesis` — InterviewSynthesisAgent

- **VA id / category:** 71 / `9-Meta`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.interviewsynthesis.v1` / files=0  
- **Rubric ref / files:** `video.rubric.interviewsynthesis.v1` / files=0  
- **Sources / provenance:** files=11 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Synthesizes practitioner interviews into data Host role binding: `InterviewSynthesisAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Synthesizes practitioner interviews into data ### Know…

**From `agents.md` design row:**

- Responsibility: Synthesizes practitioner interviews into data
- Knowledge distillation source: Otter/Rev transcripts; consent forms; SAG/WGA templates
- Self-quality criteria: Inter-coder agreement on themes; consent integrity
- Surpass-human signal (aspirational): Faster + richer theme extraction than qualitative researcher
- Accepts critique from: ResearchPIAgent (HiTL), ComplianceAgent
- Comments on: SMEAgent (mis-summarized expert)
- Tool access (design): Otter.ai/Rev API (transcription); thematic coding models; consent-management DB
- Architecture pattern (design): Reflexion (interviewer refines questions based on theme gaps)

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1145 chars). VA source responsibility: Synthesizes practitioner interviews into data |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Otter/Rev transcripts; consent forms; SAG/WGA templates |
| 3) Sources exist / know how to obtain them | **YES** | 11 source files + PROVENANCE. VA listed: Otter/Rev transcripts; consent forms; SAG/WGA templates |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Inter-coder agreement on themes; consent integrity |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Faster + richer theme extraction than qualitative researcher |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.interviewsynthesis.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: Reflexion (interviewer refines questi… |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: ResearchPIAgent (HiTL), ComplianceAgent; comments on: SMEAg… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.interviewsynthesis.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.interviewsynthesis.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.interviewsynthesis` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.benchmarkresearch` — BenchmarkResearchAgent

- **VA id / category:** 72 / `9-Meta`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.benchmarkresearch.v1` / files=0  
- **Rubric ref / files:** `video.rubric.benchmarkresearch.v1` / files=0  
- **Sources / provenance:** files=10 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Monitors VBench, EvalCrafter, MT-Bench, FVD, CLIP-T leaderboards Host role binding: `BenchmarkResearchAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Monitors VBench, EvalCrafter, MT-Ben…

**From `agents.md` design row:**

- Responsibility: Monitors VBench, EvalCrafter, MT-Bench, FVD, CLIP-T leaderboards
- Knowledge distillation source: Papers-with-Code; HuggingFace leaderboards; conference proceedings
- Self-quality criteria: Coverage of benchmarks; freshness ≤7 days
- Surpass-human signal (aspirational): Faster + broader than ML-research team
- Accepts critique from: OptimizationAgents (any)
- Comments on: All AI agents (stale baselines)
- Tool access (design): Papers-with-Code API; HuggingFace Hub API; arXiv RSS; VBench leaderboard scraper
- Architecture pattern (design): ReAct (poll leaderboards → detect change → alert)

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1135 chars). VA source responsibility: Monitors VBench, EvalCrafter, MT-Bench, FVD, CLIP-T leaderboards |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Papers-with-Code; HuggingFace leaderboards; conference proceedings |
| 3) Sources exist / know how to obtain them | **YES** | 10 source files + PROVENANCE. VA listed: Papers-with-Code; HuggingFace leaderboards; conference proceedings |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Coverage of benchmarks; freshness ≤7 days |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Faster + broader than ML-research team |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.benchmarkresearch.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: ReAct (poll leaderboards → detect chan… |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: OptimizationAgents (any); comments on: All AI agents (stale… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.benchmarkresearch.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.benchmarkresearch.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.benchmarkresearch` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.promptoptimizer` — PromptOptimizerAgent

- **VA id / category:** 73 / `9-Meta`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.promptoptimizer.v1` / files=0  
- **Rubric ref / files:** `video.rubric.promptoptimizer.v1` / files=0  
- **Sources / provenance:** files=14 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Auto-improves prompts via OPRO/APE/DSPy/Promptbreeder Host role binding: `PromptOptimizerAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Auto-improves prompts via OPRO/APE/DSPy/Promptbre…

**From `agents.md` design row:**

- Responsibility: Auto-improves prompts via OPRO/APE/DSPy/Promptbreeder
- Knowledge distillation source: OPRO (Yang 2023); APE (Zhou 2022); DSPy (Stanford); Promptbreeder (DeepMind)
- Self-quality criteria: Score uplift per iteration; convergence speed
- Surpass-human signal (aspirational): Beats hand-tuned prompts on held-out briefs
- Accepts critique from: PromptEngineerAgent, AIQAAgent
- Comments on: PromptEngineerAgent (sub-optimal seed)
- Tool access (design): DSPy framework (MIPRO optimizer); OPRO implementation; held-out eval harness
- Architecture pattern (design): DSPy compilation + OPRO meta-optimization

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1131 chars). VA source responsibility: Auto-improves prompts via OPRO/APE/DSPy/Promptbreeder |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: OPRO (Yang 2023); APE (Zhou 2022); DSPy (Stanford); Promptbreeder (DeepMind) |
| 3) Sources exist / know how to obtain them | **YES** | 14 source files + PROVENANCE. VA listed: OPRO (Yang 2023); APE (Zhou 2022); DSPy (Stanford); Promptbreeder (DeepMind) |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Score uplift per iteration; convergence speed |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Beats hand-tuned prompts on held-out briefs |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.promptoptimizer.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: DSPy compilation + OPRO meta-optimization |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: PromptEngineerAgent, AIQAAgent; comments on: PromptEngineer… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.promptoptimizer.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.promptoptimizer.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.promptoptimizer` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.costoptimizer` — CostOptimizerAgent

- **VA id / category:** 74 / `9-Meta`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.costoptimizer.v1` / files=0  
- **Rubric ref / files:** `video.rubric.costoptimizer.v1` / files=0  
- **Sources / provenance:** files=14 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Routes between models/providers for $/quality Host role binding: `CostOptimizerAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Routes between models/providers for $/quality ### Knowledge…

**From `agents.md` design row:**

- Responsibility: Routes between models/providers for $/quality
- Knowledge distillation source: Provider pricing; cost-quality frontiers; FrugalGPT patterns
- Self-quality criteria: $/successful-task; Pareto distance from frontier
- Surpass-human signal (aspirational): Lower $/quality than human CFO routing
- Accepts critique from: RouterAgent, FinanceAgent
- Comments on: RouterAgent (over-spend), GeneratorAgent (re-roll burn)
- Tool access (design): Provider pricing APIs; benchmark cost DB; FrugalGPT cascade logic
- Architecture pattern (design): ReAct (evaluate task → pick cheapest model meeting threshold)

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1116 chars). VA source responsibility: Routes between models/providers for $/quality |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Provider pricing; cost-quality frontiers; FrugalGPT patterns |
| 3) Sources exist / know how to obtain them | **YES** | 14 source files + PROVENANCE. VA listed: Provider pricing; cost-quality frontiers; FrugalGPT patterns |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: $/successful-task; Pareto distance from frontier |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Lower $/quality than human CFO routing |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.costoptimizer.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: ReAct (evaluate task → pick cheapest model… |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: RouterAgent, FinanceAgent; comments on: RouterAgent (over-s… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.costoptimizer.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.costoptimizer.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.costoptimizer` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.latencyoptimizer` — LatencyOptimizerAgent

- **VA id / category:** 75 / `9-Meta`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.latencyoptimizer.v1` / files=0  
- **Rubric ref / files:** `video.rubric.latencyoptimizer.v1` / files=0  
- **Sources / provenance:** files=11 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Parallelization, caching, speculative decoding, batching Host role binding: `LatencyOptimizerAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Parallelization, caching, speculative decodin…

**From `agents.md` design row:**

- Responsibility: Parallelization, caching, speculative decoding, batching
- Knowledge distillation source: vLLM; TensorRT-LLM; distillation; Anyscale/Ray
- Self-quality criteria: p50/p95 latency; throughput/GPU-hour
- Surpass-human signal (aspirational): Lower p95 than human-tuned pipeline
- Accepts critique from: OrchestratorAgent
- Comments on: OrchestratorAgent (serial bottleneck)
- Tool access (design): vLLM; TensorRT-LLM; Ray Serve; Redis (response cache); speculative decoding configs
- Architecture pattern (design): Tool-use profiling + automated pipeline restructuring

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1096 chars). VA source responsibility: Parallelization, caching, speculative decoding, batching |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: vLLM; TensorRT-LLM; distillation; Anyscale/Ray |
| 3) Sources exist / know how to obtain them | **YES** | 11 source files + PROVENANCE. VA listed: vLLM; TensorRT-LLM; distillation; Anyscale/Ray |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: p50/p95 latency; throughput/GPU-hour |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Lower p95 than human-tuned pipeline |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.latencyoptimizer.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: Tool-use profiling + automated pipeline… |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: OrchestratorAgent; comments on: OrchestratorAgent (serial b… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.latencyoptimizer.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.latencyoptimizer.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.latencyoptimizer` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.retentionoptimizer` — RetentionOptimizerAgent

- **VA id / category:** 76 / `9-Meta`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.retentionoptimizer.v1` / files=0  
- **Rubric ref / files:** `video.rubric.retentionoptimizer.v1` / files=0  
- **Sources / provenance:** files=15 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Tunes hook, pacing, structure for AVD/hold-rate Host role binding: `RetentionOptimizerAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Tunes hook, pacing, structure for AVD/hold-rate ### …

**From `agents.md` design row:**

- Responsibility: Tunes hook, pacing, structure for AVD/hold-rate
- Knowledge distillation source: YouTube Analytics benchmarks; TikTok retention curves; AudienceSim
- Self-quality criteria: Predicted retention vs actual; AVD lift over control
- Surpass-human signal (aspirational): Beats senior YouTube editor on AVD lift (A/B)
- Accepts critique from: EditorAgent, AudienceSimAgent
- Comments on: EditorAgent (slow opener), ScriptwriterAgent (front fluff)
- Tool access (design): YouTube Analytics API; retention-curve predictor model; A/B test framework
- Architecture pattern (design): RLAIF (reward = retention uplift from real analytics)

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1150 chars). VA source responsibility: Tunes hook, pacing, structure for AVD/hold-rate |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: YouTube Analytics benchmarks; TikTok retention curves; AudienceSim |
| 3) Sources exist / know how to obtain them | **YES** | 15 source files + PROVENANCE. VA listed: YouTube Analytics benchmarks; TikTok retention curves; AudienceSim |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Predicted retention vs actual; AVD lift over control |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Beats senior YouTube editor on AVD lift (A/B) |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.retentionoptimizer.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: RLAIF (reward = retention uplift from… |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: EditorAgent, AudienceSimAgent; comments on: EditorAgent (sl… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.retentionoptimizer.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.retentionoptimizer.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.retentionoptimizer` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.roasoptimizer` — ROASOptimizerAgent

- **VA id / category:** 77 / `9-Meta`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.roasoptimizer.v1` / files=0  
- **Rubric ref / files:** `video.rubric.roasoptimizer.v1` / files=0  
- **Sources / provenance:** files=10 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Optimizes ad creatives for performance Host role binding: `ROASOptimizerAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Optimizes ad creatives for performance ### Knowledge distillation …

**From `agents.md` design row:**

- Responsibility: Optimizes ad creatives for performance
- Knowledge distillation source: Meta Marketing Science; TikTok Ads Academy; MMM/MTA lit
- Self-quality criteria: ROAS uplift vs control; significance ≥95%
- Surpass-human signal (aspirational): Beats senior marketer at equal budget
- Accepts critique from: PerformanceMarketerAgent, AnalystAgent
- Comments on: UGCAgent (low hook), CopywriterAgent (weak CTA)
- Tool access (design): Meta Ads API (creative testing); TikTok Ads; Bayesian MMM tools (Robyn/Meridian)
- Architecture pattern (design): RLAIF (reward = real ROAS from ad platform feedback)

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1100 chars). VA source responsibility: Optimizes ad creatives for performance |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Meta Marketing Science; TikTok Ads Academy; MMM/MTA lit |
| 3) Sources exist / know how to obtain them | **YES** | 10 source files + PROVENANCE. VA listed: Meta Marketing Science; TikTok Ads Academy; MMM/MTA lit |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: ROAS uplift vs control; significance ≥95% |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Beats senior marketer at equal budget |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.roasoptimizer.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: RLAIF (reward = real ROAS from ad platform… |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: PerformanceMarketerAgent, AnalystAgent; comments on: UGCAge… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.roasoptimizer.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.roasoptimizer.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.roasoptimizer` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.accessibilityoptimizer` — AccessibilityOptimizerAgent

- **VA id / category:** 78 / `9-Meta`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.accessibilityoptimizer.v1` / files=0  
- **Rubric ref / files:** `video.rubric.accessibilityoptimizer.v1` / files=0  
- **Sources / provenance:** files=12 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** WCAG 2.2 contrast, captions, audio description, color-blind safe Host role binding: `AccessibilityOptimizerAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) WCAG 2.2 contrast, captions, au…

**From `agents.md` design row:**

- Responsibility: WCAG 2.2 contrast, captions, audio description, color-blind safe
- Knowledge distillation source: WCAG 2.2; W3C/WAI-ARIA; DCMP captioning key; Deaf/HoH guidelines
- Self-quality criteria: Conformance 100% AA, ≥90% AAA; caption WER ≤2%
- Surpass-human signal (aspirational): Catches more a11y defects than ADA-certified auditor
- Accepts critique from: AccessibilityAgent (HiTL), ComplianceAgent
- Comments on: EditorAgent (caption sync), ColoristAgent (contrast)
- Tool access (design): axe-core/Lighthouse (contrast); Whisper v4 (captioning); audio-description generator
- Architecture pattern (design): Constitutional AI (constitution = WCAG 2.2 success criteria)

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1211 chars). VA source responsibility: WCAG 2.2 contrast, captions, audio description, color-blind safe |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: WCAG 2.2; W3C/WAI-ARIA; DCMP captioning key; Deaf/HoH guidelines |
| 3) Sources exist / know how to obtain them | **YES** | 12 source files + PROVENANCE. VA listed: WCAG 2.2; W3C/WAI-ARIA; DCMP captioning key; Deaf/HoH guidelines |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Conformance 100% AA, ≥90% AAA; caption WER ≤2% |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Catches more a11y defects than ADA-certified auditor |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.accessibilityoptimizer.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: Constitutional AI (constitution =… |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: AccessibilityAgent (HiTL), ComplianceAgent; comments on: Ed… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.accessibilityoptimizer.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.accessibilityoptimizer.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.accessibilityoptimizer` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.evaluationharness` — EvaluationHarnessAgent

- **VA id / category:** 79 / `9-Meta`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.evaluationharness.v1` / files=0  
- **Rubric ref / files:** `video.rubric.evaluationharness.v1` / files=0  
- **Sources / provenance:** files=13 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Runs benchmarks (VBench, EvalCrafter, MT-Bench, FVD, CLIP-T); posts regressions Host role binding: `EvaluationHarnessAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Runs benchmarks (VBen…

**From `agents.md` design row:**

- Responsibility: Runs benchmarks (VBench, EvalCrafter, MT-Bench, FVD, CLIP-T); posts regressions
- Knowledge distillation source: Papers-with-Code; HuggingFace leaderboards; benchmark repos
- Self-quality criteria: Regression precision/recall; alert latency <1h
- Surpass-human signal (aspirational): Catches regressions faster than ML-eng rotation
- Accepts critique from: BenchmarkResearchAgent
- Comments on: All AI agents (regression alerts)
- Tool access (design): VBench suite; EvalCrafter; MT-Bench harness; CI/CD (GitHub Actions); alerting (PagerDuty)
- Architecture pattern (design): Tool-use / ReAct (run benchmark → compare → alert if regressed)

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1195 chars). VA source responsibility: Runs benchmarks (VBench, EvalCrafter, MT-Bench, FVD, CLIP-T); posts regressions |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Papers-with-Code; HuggingFace leaderboards; benchmark repos |
| 3) Sources exist / know how to obtain them | **YES** | 13 source files + PROVENANCE. VA listed: Papers-with-Code; HuggingFace leaderboards; benchmark repos |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Regression precision/recall; alert latency <1h |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Catches regressions faster than ML-eng rotation |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.evaluationharness.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: Tool-use / ReAct (run benchmark → comp… |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: BenchmarkResearchAgent; comments on: All AI agents (regress… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.evaluationharness.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.evaluationharness.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.evaluationharness` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.safetyredteam` — SafetyRedTeamAgent

- **VA id / category:** 80 / `9-Meta`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.safetyredteam.v1` / files=0  
- **Rubric ref / files:** `video.rubric.safetyredteam.v1` / files=0  
- **Sources / provenance:** files=11 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Adversarially attacks for deepfake, bias, jailbreak, defamation Host role binding: `SafetyRedTeamAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Adversarially attacks for deepfake, bias,…

**From `agents.md` design row:**

- Responsibility: Adversarially attacks for deepfake, bias, jailbreak, defamation
- Knowledge distillation source: Hany Farid benchmarks; Partnership on AI Framework; OWASP LLM Top 10
- Self-quality criteria: Attack-success kept ≤1%; taxonomy coverage
- Surpass-human signal (aspirational): Higher coverage than internal red-team rotation
- Accepts critique from: EthicsAgent (HiTL), ComplianceAgent
- Comments on: AvatarDesignAgent, VoiceCloneAgent, AllGenerators
- Tool access (design): Deepfake detectors (Farid lab models); bias probes; jailbreak prompt banks; OWASP scanner
- Architecture pattern (design): Multi-agent debate (red-team vs defender) + adversarial search

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1192 chars). VA source responsibility: Adversarially attacks for deepfake, bias, jailbreak, defamation |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Hany Farid benchmarks; Partnership on AI Framework; OWASP LLM Top 10 |
| 3) Sources exist / know how to obtain them | **YES** | 11 source files + PROVENANCE. VA listed: Hany Farid benchmarks; Partnership on AI Framework; OWASP LLM Top 10 |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Attack-success kept ≤1%; taxonomy coverage |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Higher coverage than internal red-team rotation |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.safetyredteam.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: Multi-agent debate (red-team vs defender) … |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: EthicsAgent (HiTL), ComplianceAgent; comments on: AvatarDes… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.safetyredteam.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.safetyredteam.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.safetyredteam` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

### 10-Sup — Workflow Support (34 agents, avg maturity 6.37)

#### Group synthesis

- **1) Responsibility well defined in SPEC.md:** dominant **YES** (Y=34, P=0, N=0)
- **2) Plan to distill professional knowledge:** dominant **YES** (Y=34, P=0, N=0)
- **3) Sources exist / know how to obtain them:** dominant **YES** (Y=25, P=9, N=0)
- **4) Self-evaluation methods & content collected:** dominant **PARTIAL** (Y=0, P=34, N=0)
- **5) Implementation surpasses human yet?:** dominant **NO** (Y=0, P=0, N=34)
- **6) How they execute the job:** dominant **PARTIAL** (Y=0, P=34, N=0)
- **7) Skills / plugins / harness for themselves:** dominant **PARTIAL** (Y=0, P=34, N=0)
- **8) Mechanism to improve themselves:** dominant **PARTIAL** (Y=0, P=34, N=0)
- **9) Collect/research info to improve:** dominant **PARTIAL** (Y=0, P=34, N=0)
- **10) Get/send instructions to other agents:** dominant **PARTIAL** (Y=0, P=34, N=0)
- **11) Resolve conflict + confirm:** dominant **PARTIAL** (Y=0, P=34, N=0)

#### Agents

##### `video.analyst` — AnalystAgent

- **VA id / category:** 81 / `10-Sup`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.analyst.v1` / files=0  
- **Rubric ref / files:** `video.rubric.analyst.v1` / files=0  
- **Sources / provenance:** files=12 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Aggregates business, creative, and technical performance telemetry into decision-ready reports Host role binding: `AnalystAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Aggregates busin…

**From `agents.md` design row:**

- Responsibility: Aggregates business, creative, and technical performance telemetry into decision-ready reports
- Knowledge distillation source: Platform analytics dashboards; experiment logs; evaluation-harness outputs; benchmark histories
- Self-quality criteria: KPI completeness; forecast-vs-actual variance within tolerance; insight-to-action turnaround
- Surpass-human signal (aspirational): Detects actionable performance shifts faster than human analyst rotations
- Accepts critique from: SocialMediaStrategistAgent, PerformanceMarketerAgent, EvaluationHarnessAgent
- Comments on: Campaign pacing, release timing, retention and ROAS anomalies
- Tool access (design): YouTube Analytics, Meta/TikTok Ads dashboards, BI warehouse, benchmark logs
- Architecture pattern (design): ReAct over telemetry + regression analysis

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1370 chars). VA source responsibility: Aggregates business, creative, and technical performance telemetry into decision-ready reports |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Platform analytics dashboards; experiment logs; evaluation-harness outputs; benchmark histories |
| 3) Sources exist / know how to obtain them | **YES** | 12 source files + PROVENANCE. VA listed: Platform analytics dashboards; experiment logs; evaluation-harness outputs; benchmark histories |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: KPI completeness; forecast-vs-actual variance within tolerance; insight-to-action turnaround |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Detects actionable performance shifts faster than human analyst rotations |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.analyst.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: ReAct over telemetry + regression analysis |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: SocialMediaStrategistAgent, PerformanceMarketerAgent, Evalu… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.analyst.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.analyst.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.analyst` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.audiencesim` — AudienceSimAgent

- **VA id / category:** 82 / `10-Sup`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.audiencesim.v1` / files=0  
- **Rubric ref / files:** `video.rubric.audiencesim.v1` / files=0  
- **Sources / provenance:** files=15 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Simulates audience preference, engagement, and drop-off Host role binding: `AudienceSimAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Simulates audience preference, engagement, and drop…

**From `agents.md` design row:**

- Responsibility: Simulates audience preference, engagement, and drop-off
- Knowledge distillation source: Pairwise preference datasets; retention studies; audience segmentation models
- Self-quality criteria: Preference stability across cohorts; retention-prediction accuracy; disagreement logging
- Surpass-human signal (aspirational): Predicts audience reaction earlier than conventional test-screen cycles
- Accepts critique from: DirectorAgent, EditorAgent, AnalystAgent, JudgeAgent
- Comments on: Hooks, pacing, clarity, emotional fit, trailer strength
- Tool access (design): Persona simulators, pairwise evaluation harness, retention models
- Architecture pattern (design): LLM-as-Judge + pairwise preference panel

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1230 chars). VA source responsibility: Simulates audience preference, engagement, and drop-off |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Pairwise preference datasets; retention studies; audience segmentation models |
| 3) Sources exist / know how to obtain them | **YES** | 15 source files + PROVENANCE. VA listed: Pairwise preference datasets; retention studies; audience segmentation models |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Preference stability across cohorts; retention-prediction accuracy; disagreement logging |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Predicts audience reaction earlier than conventional test-screen cycles |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.audiencesim.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: LLM-as-Judge + pairwise preference panel |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: DirectorAgent, EditorAgent, AnalystAgent, JudgeAgent; comme… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.audiencesim.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.audiencesim.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.audiencesim` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.accessibility` — AccessibilityAgent

- **VA id / category:** 83 / `10-Sup`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.accessibility.v1` / files=0  
- **Rubric ref / files:** `video.rubric.accessibility.v1` / files=0  
- **Sources / provenance:** files=14 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Owns final accessibility acceptance before release Host role binding: `AccessibilityAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Owns final accessibility acceptance before release ###…

**From `agents.md` design row:**

- Responsibility: Owns final accessibility acceptance before release
- Knowledge distillation source: WCAG 2.2, captioning and AD guidelines, Deaf/HoH review frameworks
- Self-quality criteria: Caption accuracy, AD completeness, contrast compliance, release-readiness
- Surpass-human signal (aspirational): Finds release-blocking accessibility issues before human audits do
- Accepts critique from: AccessibilityOptimizerAgent, EditorAgent, ColoristAgent, SoundMixerAgent
- Comments on: Caption sync, contrast issues, missing AD or sign-language layers
- Tool access (design): Caption validators, contrast analyzers, AD review tools
- Architecture pattern (design): Constitutional AI with accessibility constitution

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1220 chars). VA source responsibility: Owns final accessibility acceptance before release |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: WCAG 2.2, captioning and AD guidelines, Deaf/HoH review frameworks |
| 3) Sources exist / know how to obtain them | **YES** | 14 source files + PROVENANCE. VA listed: WCAG 2.2, captioning and AD guidelines, Deaf/HoH review frameworks |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Caption accuracy, AD completeness, contrast compliance, release-readiness |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Finds release-blocking accessibility issues before human audits do |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.accessibility.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: Constitutional AI with accessibility const… |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: AccessibilityOptimizerAgent, EditorAgent, ColoristAgent, So… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.accessibility.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.accessibility.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.accessibility` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.brand` — BrandAgent

- **VA id / category:** 84 / `10-Sup`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.brand.v1` / files=0  
- **Rubric ref / files:** `video.rubric.brand.v1` / files=0  
- **Sources / provenance:** files=15 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Enforces brand voice, claims boundaries, and visual consistency Host role binding: `BrandAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Enforces brand voice, claims boundaries, and visu…

**From `agents.md` design row:**

- Responsibility: Enforces brand voice, claims boundaries, and visual consistency
- Knowledge distillation source: Brand books, approved campaigns, legal claim guardrails, tone guides
- Self-quality criteria: Brand-voice similarity, policy adherence, low deviation across assets
- Surpass-human signal (aspirational): Holds cross-channel brand consistency better than fragmented human review
- Accepts critique from: CopywriterAgent, MotionGraphicsAgent, MarketingAgent, BrandStrategistAgent
- Comments on: Voice drift, visual inconsistency, claim creep
- Tool access (design): Brand asset library, embedding similarity, style guides
- Architecture pattern (design): Self-Refine against brand constitution

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1215 chars). VA source responsibility: Enforces brand voice, claims boundaries, and visual consistency |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Brand books, approved campaigns, legal claim guardrails, tone guides |
| 3) Sources exist / know how to obtain them | **YES** | 15 source files + PROVENANCE. VA listed: Brand books, approved campaigns, legal claim guardrails, tone guides |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Brand-voice similarity, policy adherence, low deviation across assets |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Holds cross-channel brand consistency better than fragmented human review |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.brand.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: Self-Refine against brand constitution |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: CopywriterAgent, MotionGraphicsAgent, MarketingAgent, Brand… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.brand.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.brand.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.brand` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.brandstrategist` — BrandStrategistAgent

- **VA id / category:** 85 / `10-Sup`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.brandstrategist.v1` / files=0  
- **Rubric ref / files:** `video.rubric.brandstrategist.v1` / files=0  
- **Sources / provenance:** files=9 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Defines audience-value framing and positioning before script and campaign execution Host role binding: `BrandStrategistAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Defines audience-va…

**From `agents.md` design row:**

- Responsibility: Defines audience-value framing and positioning before script and campaign execution
- Knowledge distillation source: Positioning frameworks, campaign strategy decks, market research, brand architecture docs
- Self-quality criteria: Strategy coherence, differentiation strength, audience-message clarity
- Surpass-human signal (aspirational): Produces clearer brand-to-script translation than ad hoc human handoffs
- Accepts critique from: BrandAgent, ScreenwriterAgent, MarketingAgent
- Comments on: Positioning gaps, weak value proposition, misaligned audience framing
- Tool access (design): Research decks, messaging frameworks, strategy templates
- Architecture pattern (design): Multi-agent debate with BrandAgent and CreativeDirectorAgent

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1302 chars). VA source responsibility: Defines audience-value framing and positioning before script and campaign execution |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Positioning frameworks, campaign strategy decks, market research, brand architecture docs |
| 3) Sources exist / know how to obtain them | **YES** | 9 source files + PROVENANCE. VA listed: Positioning frameworks, campaign strategy decks, market research, brand architecture docs |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Strategy coherence, differentiation strength, audience-message clarity |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Produces clearer brand-to-script translation than ad hoc human handoffs |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.brandstrategist.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: Multi-agent debate with BrandAgent and C… |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: BrandAgent, ScreenwriterAgent, MarketingAgent; comments on:… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.brandstrategist.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.brandstrategist.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.brandstrategist` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.marketing` — MarketingAgent

- **VA id / category:** 86 / `10-Sup`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.marketing.v1` / files=0  
- **Rubric ref / files:** `video.rubric.marketing.v1` / files=0  
- **Sources / provenance:** files=13 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Packages content for launch, promotions, and release sequencing Host role binding: `MarketingAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Packages content for launch, promotions, and …

**From `agents.md` design row:**

- Responsibility: Packages content for launch, promotions, and release sequencing
- Knowledge distillation source: Campaign playbooks, launch calendars, media plans, asset packaging requirements
- Self-quality criteria: Metadata completeness, asset readiness, launch sequencing accuracy
- Surpass-human signal (aspirational): Ships multi-channel launch packages faster than manual campaign ops
- Accepts critique from: SocialMediaStrategistAgent, SEOAgent, CopywriterAgent, TrailerEditorAgent
- Comments on: Missing formats, weak rollout timing, incomplete promotion sets
- Tool access (design): Campaign management suites, metadata tools, release planners
- Architecture pattern (design): ReAct over launch checklists and channel requirements

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1257 chars). VA source responsibility: Packages content for launch, promotions, and release sequencing |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Campaign playbooks, launch calendars, media plans, asset packaging requirements |
| 3) Sources exist / know how to obtain them | **YES** | 13 source files + PROVENANCE. VA listed: Campaign playbooks, launch calendars, media plans, asset packaging requirements |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Metadata completeness, asset readiness, launch sequencing accuracy |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Ships multi-channel launch packages faster than manual campaign ops |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.marketing.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: ReAct over launch checklists and channel requi… |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: SocialMediaStrategistAgent, SEOAgent, CopywriterAgent, Trai… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.marketing.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.marketing.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.marketing` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.seo` — SEOAgent

- **VA id / category:** 87 / `10-Sup`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.seo.v1` / files=0  
- **Rubric ref / files:** `video.rubric.seo.v1` / files=0  
- **Sources / provenance:** files=10 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Optimizes discoverability through titles, descriptions, metadata, and search intent Host role binding: `SEOAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Optimizes discoverability throu…

**From `agents.md` design row:**

- Responsibility: Optimizes discoverability through titles, descriptions, metadata, and search intent
- Knowledge distillation source: Search ranking studies, video metadata best practices, keyword taxonomies
- Self-quality criteria: Keyword fit, metadata completeness, search-intent match
- Surpass-human signal (aspirational): Lifts discoverability faster than manual metadata tuning
- Accepts critique from: MarketingAgent, CopywriterAgent, AnalystAgent
- Comments on: Weak keywords, poor title-description fit, metadata omissions
- Tool access (design): Keyword tools, metadata APIs, ranking dashboards
- Architecture pattern (design): ReAct with search-intent validation

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1203 chars). VA source responsibility: Optimizes discoverability through titles, descriptions, metadata, and search intent |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Search ranking studies, video metadata best practices, keyword taxonomies |
| 3) Sources exist / know how to obtain them | **YES** | 10 source files + PROVENANCE. VA listed: Search ranking studies, video metadata best practices, keyword taxonomies |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Keyword fit, metadata completeness, search-intent match |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Lifts discoverability faster than manual metadata tuning |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.seo.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: ReAct with search-intent validation |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: MarketingAgent, CopywriterAgent, AnalystAgent; comments on:… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.seo.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.seo.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.seo` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.community` — CommunityAgent

- **VA id / category:** 88 / `10-Sup`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.community.v1` / files=0  
- **Rubric ref / files:** `video.rubric.community.v1` / files=0  
- **Sources / provenance:** files=13 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Captures community response and triages qualitative signals Host role binding: `CommunityAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Captures community response and triages qualitati…

**From `agents.md` design row:**

- Responsibility: Captures community response and triages qualitative signals
- Knowledge distillation source: Community moderation playbooks, sentiment datasets, escalation rules
- Self-quality criteria: Response latency, issue clustering quality, sentiment tracking accuracy
- Surpass-human signal (aspirational): Surfaces emerging audience concerns earlier than manual comment review
- Accepts critique from: AnalystAgent, SocialMediaStrategistAgent, CommsAgent
- Comments on: Confusing messaging, sentiment risks, recurring complaints
- Tool access (design): Social listening tools, moderation dashboards, clustering models
- Architecture pattern (design): Reflexion from post-launch audience feedback

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1215 chars). VA source responsibility: Captures community response and triages qualitative signals |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Community moderation playbooks, sentiment datasets, escalation rules |
| 3) Sources exist / know how to obtain them | **YES** | 13 source files + PROVENANCE. VA listed: Community moderation playbooks, sentiment datasets, escalation rules |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Response latency, issue clustering quality, sentiment tracking accuracy |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Surfaces emerging audience concerns earlier than manual comment review |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.community.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: Reflexion from post-launch audience feedback |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: AnalystAgent, SocialMediaStrategistAgent, CommsAgent; comme… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.community.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.community.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.community` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.templatedesign` — TemplateDesignAgent

- **VA id / category:** 89 / `10-Sup`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.templatedesign.v1` / files=0  
- **Rubric ref / files:** `video.rubric.templatedesign.v1` / files=0  
- **Sources / provenance:** files=8 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Designs reusable and safe personalization templates Host role binding: `TemplateDesignAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Designs reusable and safe personalization templates …

**From `agents.md` design row:**

- Responsibility: Designs reusable and safe personalization templates
- Knowledge distillation source: Variable-content design systems, dynamic layout rules, campaign template libraries
- Self-quality criteria: Merge-field robustness, layout stability, render survivability
- Surpass-human signal (aspirational): Produces reusable templates with fewer breakages than manual design variants
- Accepts critique from: PersonalizationEngineerAgent, UXAgent, CRMAgent
- Comments on: Fragile layouts, unsafe placeholder logic, merge collisions
- Tool access (design): Template engines, design systems, schema validators
- Architecture pattern (design): ReAct on template schemas and render constraints

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1202 chars). VA source responsibility: Designs reusable and safe personalization templates |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Variable-content design systems, dynamic layout rules, campaign template libraries |
| 3) Sources exist / know how to obtain them | **YES** | 8 source files + PROVENANCE. VA listed: Variable-content design systems, dynamic layout rules, campaign template libraries |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Merge-field robustness, layout stability, render survivability |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Produces reusable templates with fewer breakages than manual design variants |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.templatedesign.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: ReAct on template schemas and render cons… |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: PersonalizationEngineerAgent, UXAgent, CRMAgent; comments o… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.templatedesign.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.templatedesign.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.templatedesign` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.ux` — UXAgent

- **VA id / category:** 90 / `10-Sup`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.ux.v1` / files=0  
- **Rubric ref / files:** `video.rubric.ux.v1` / files=0  
- **Sources / provenance:** files=6 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.0/11 (Y=2 P=8 N=1)  
- **SPEC responsibility excerpt:** Reviews clarity and usability of personalized or interactive outputs Host role binding: `UXAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Reviews clarity and usability of personalized o…

**From `agents.md` design row:**

- Responsibility: Reviews clarity and usability of personalized or interactive outputs
- Knowledge distillation source: UX heuristics, accessibility criteria, usability testing patterns
- Self-quality criteria: Readability, friction-point detection, user-flow clarity
- Surpass-human signal (aspirational): Flags user confusion earlier than launch-stage support teams
- Accepts critique from: TemplateDesignAgent, PersonalizationEngineerAgent, AccessibilityAgent
- Comments on: Confusing flows, readability issues, weak interaction cues
- Tool access (design): UX review checklists, session replay, readability tools
- Architecture pattern (design): LLM-as-Judge with UX rubric

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1189 chars). VA source responsibility: Reviews clarity and usability of personalized or interactive outputs |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: UX heuristics, accessibility criteria, usability testing patterns |
| 3) Sources exist / know how to obtain them | **PARTIAL** | 6 local source files; acquisition path may still be design-only (URLs/corpora not fully licensed). VA listed: UX heuristics, accessibility criteria, usability testing patterns |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Readability, friction-point detection, user-flow clarity |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Flags user confusion earlier than launch-stage support teams |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.ux.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: LLM-as-Judge with UX rubric |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: TemplateDesignAgent, PersonalizationEngineerAgent, Accessib… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.ux.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.ux.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.ux` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.trustsafety` — TrustSafetyAgent

- **VA id / category:** 91 / `10-Sup`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.trustsafety.v1` / files=0  
- **Rubric ref / files:** `video.rubric.trustsafety.v1` / files=0  
- **Sources / provenance:** files=9 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Screens outputs for impersonation, abuse, or harmful misuse Host role binding: `TrustSafetyAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Screens outputs for impersonation, abuse, or ha…

**From `agents.md` design row:**

- Responsibility: Screens outputs for impersonation, abuse, or harmful misuse
- Knowledge distillation source: Abuse-taxonomy corpora, impersonation cases, policy rulebooks
- Self-quality criteria: Policy hit rate, abuse-risk recall, low false negatives on blocked cases
- Surpass-human signal (aspirational): Catches misuse risk earlier than generic moderation queues
- Accepts critique from: ComplianceAgent, DeepfakeDetectionAgent, SafetyRedTeamAgent
- Comments on: Harmful misuse pathways, impersonation vectors, policy gaps
- Tool access (design): Safety classifiers, abuse taxonomy DB, moderation APIs
- Architecture pattern (design): Constitutional AI for trust-and-safety policy enforcement

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1210 chars). VA source responsibility: Screens outputs for impersonation, abuse, or harmful misuse |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Abuse-taxonomy corpora, impersonation cases, policy rulebooks |
| 3) Sources exist / know how to obtain them | **YES** | 9 source files + PROVENANCE. VA listed: Abuse-taxonomy corpora, impersonation cases, policy rulebooks |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Policy hit rate, abuse-risk recall, low false negatives on blocked cases |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Catches misuse risk earlier than generic moderation queues |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.trustsafety.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: Constitutional AI for trust-and-safety polic… |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: ComplianceAgent, DeepfakeDetectionAgent, SafetyRedTeamAgent… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.trustsafety.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.trustsafety.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.trustsafety` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.crm` — CRMAgent

- **VA id / category:** 92 / `10-Sup`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.crm.v1` / files=0  
- **Rubric ref / files:** `video.rubric.crm.v1` / files=0  
- **Sources / provenance:** files=9 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Delivers audience-targeted or trigger-based campaigns through CRM systems Host role binding: `CRMAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Delivers audience-targeted or trigger-bas…

**From `agents.md` design row:**

- Responsibility: Delivers audience-targeted or trigger-based campaigns through CRM systems
- Knowledge distillation source: CRM automation flows, lifecycle marketing playbooks, audience segmentation rules
- Self-quality criteria: Audience-segment correctness, delivery readiness, trigger accuracy
- Surpass-human signal (aspirational): Executes segmentation-to-delivery flow faster than manual ops
- Accepts critique from: PersonalizationEngineerAgent, TemplateDesignAgent, AnalystAgent
- Comments on: Wrong segmentation, broken trigger timing, incomplete CRM payloads
- Tool access (design): HubSpot/Salesforce-style CRM APIs, segmentation tools
- Architecture pattern (design): ReAct over trigger and audience schemas

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1238 chars). VA source responsibility: Delivers audience-targeted or trigger-based campaigns through CRM systems |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: CRM automation flows, lifecycle marketing playbooks, audience segmentation rules |
| 3) Sources exist / know how to obtain them | **YES** | 9 source files + PROVENANCE. VA listed: CRM automation flows, lifecycle marketing playbooks, audience segmentation rules |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Audience-segment correctness, delivery readiness, trigger accuracy |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Executes segmentation-to-delivery flow faster than manual ops |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.crm.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: ReAct over trigger and audience schemas |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: PersonalizationEngineerAgent, TemplateDesignAgent, AnalystA… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.crm.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.crm.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.crm` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.legal` — LegalAgent

- **VA id / category:** 93 / `10-Sup`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.legal.v1` / files=0  
- **Rubric ref / files:** `video.rubric.legal.v1` / files=0  
- **Sources / provenance:** files=12 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Performs final legal review for novel or high-risk publication issues Host role binding: `LegalAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Performs final legal review for novel or hi…

**From `agents.md` design row:**

- Responsibility: Performs final legal review for novel or high-risk publication issues
- Knowledge distillation source: Media law references, clearance workflows, defamation/IP/privacy cases
- Self-quality criteria: Issue identification recall, sign-off completeness, escalation quality
- Surpass-human signal (aspirational): Reduces late-stage legal surprises relative to fragmented legal review
- Accepts critique from: ComplianceAgent (Legal), JournalistAgent, ProducerAgent / EP, MPAAgent
- Comments on: Novel legal risks, unclear rights, unresolved high-risk claims
- Tool access (design): Legal memo systems, rights trackers, clearance databases
- Architecture pattern (design): Human-in-the-loop escalation + constitutional review

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1254 chars). VA source responsibility: Performs final legal review for novel or high-risk publication issues |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Media law references, clearance workflows, defamation/IP/privacy cases |
| 3) Sources exist / know how to obtain them | **YES** | 12 source files + PROVENANCE. VA listed: Media law references, clearance workflows, defamation/IP/privacy cases |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Issue identification recall, sign-off completeness, escalation quality |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Reduces late-stage legal surprises relative to fragmented legal review |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.legal.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: Human-in-the-loop escalation + constitutional revi… |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: ComplianceAgent (Legal), JournalistAgent, ProducerAgent / E… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.legal.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.legal.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.legal` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.festivalstrategist` — FestivalStrategistAgent

- **VA id / category:** 94 / `10-Sup`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.festivalstrategist.v1` / files=0  
- **Rubric ref / files:** `video.rubric.festivalstrategist.v1` / files=0  
- **Sources / provenance:** files=7 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.0/11 (Y=2 P=8 N=1)  
- **SPEC responsibility excerpt:** Positions projects for festivals and submission calendars Host role binding: `FestivalStrategistAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Positions projects for festivals and submi…

**From `agents.md` design row:**

- Responsibility: Positions projects for festivals and submission calendars
- Knowledge distillation source: Festival submission guides, award-season strategies, selection histories
- Self-quality criteria: Fit-to-festival strength, package readiness, timing discipline
- Surpass-human signal (aspirational): Improves submission targeting versus generic release planning
- Accepts critique from: ProducerAgent / EP, DirectorAgent, CriticAgent
- Comments on: Weak positioning, mistimed submission plans, incomplete packages
- Tool access (design): Festival calendars, submission checklists, press-kit trackers
- Architecture pattern (design): ReAct with calendar and package validation

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1201 chars). VA source responsibility: Positions projects for festivals and submission calendars |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Festival submission guides, award-season strategies, selection histories |
| 3) Sources exist / know how to obtain them | **PARTIAL** | 7 local source files; acquisition path may still be design-only (URLs/corpora not fully licensed). VA listed: Festival submission guides, award-season strategies, selection histories |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Fit-to-festival strength, package readiness, timing discipline |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Improves submission targeting versus generic release planning |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.festivalstrategist.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: ReAct with calendar and package valid… |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: ProducerAgent / EP, DirectorAgent, CriticAgent; comments on… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.festivalstrategist.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.festivalstrategist.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.festivalstrategist` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.critic` — CriticAgent

- **VA id / category:** 95 / `10-Sup`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.critic.v1` / files=0  
- **Rubric ref / files:** `video.rubric.critic.v1` / files=0  
- **Sources / provenance:** files=25 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Simulates reviewer, press, or jury interpretation Host role binding: `CriticAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Simulates reviewer, press, or jury interpretation ### Knowledg…

**From `agents.md` design row:**

- Responsibility: Simulates reviewer, press, or jury interpretation
- Knowledge distillation source: Criticism corpora, festival-jury commentary, review archives
- Self-quality criteria: Interpretive depth, consistency, reviewer-mode diversity
- Surpass-human signal (aspirational): Provides broader qualitative coverage than ad hoc internal taste review
- Accepts critique from: DirectorAgent, AudienceSimAgent, FestivalStrategistAgent, JudgeAgent
- Comments on: Auteur read, tone mismatch, festival/press vulnerability
- Tool access (design): Review corpora, jury rubrics, qualitative scoring tools
- Architecture pattern (design): Multi-agent debate as critic panel

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1165 chars). VA source responsibility: Simulates reviewer, press, or jury interpretation |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Criticism corpora, festival-jury commentary, review archives |
| 3) Sources exist / know how to obtain them | **YES** | 25 source files + PROVENANCE. VA listed: Criticism corpora, festival-jury commentary, review archives |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Interpretive depth, consistency, reviewer-mode diversity |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Provides broader qualitative coverage than ad hoc internal taste review |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.critic.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: Multi-agent debate as critic panel |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: DirectorAgent, AudienceSimAgent, FestivalStrategistAgent, J… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.critic.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.critic.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.critic` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.lms` — LMSAgent

- **VA id / category:** 96 / `10-Sup`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.lms.v1` / files=0  
- **Rubric ref / files:** `video.rubric.lms.v1` / files=0  
- **Sources / provenance:** files=13 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Packages and deploys learning content to LMS environments Host role binding: `LMSAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Packages and deploys learning content to LMS environments…

**From `agents.md` design row:**

- Responsibility: Packages and deploys learning content to LMS environments
- Knowledge distillation source: SCORM/xAPI standards, LMS publishing workflows, completion-tracking schemas
- Self-quality criteria: Package validity, tracking integrity, deploy success rate
- Surpass-human signal (aspirational): Ships publishable learning packages faster than manual course ops
- Accepts critique from: InstructionalDesignAgent, AccessibilityAgent, LearnerSimAgent
- Comments on: Package compliance, tracking errors, learning-objective mismatch
- Tool access (design): LMS APIs, SCORM/xAPI validators, course packaging tools
- Architecture pattern (design): ReAct over LMS deployment schema

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1187 chars). VA source responsibility: Packages and deploys learning content to LMS environments |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: SCORM/xAPI standards, LMS publishing workflows, completion-tracking schemas |
| 3) Sources exist / know how to obtain them | **YES** | 13 source files + PROVENANCE. VA listed: SCORM/xAPI standards, LMS publishing workflows, completion-tracking schemas |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Package validity, tracking integrity, deploy success rate |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Ships publishable learning packages faster than manual course ops |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.lms.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: ReAct over LMS deployment schema |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: InstructionalDesignAgent, AccessibilityAgent, LearnerSimAge… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.lms.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.lms.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.lms` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.learnersim` — LearnerSimAgent

- **VA id / category:** 97 / `10-Sup`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.learnersim.v1` / files=0  
- **Rubric ref / files:** `video.rubric.learnersim.v1` / files=0  
- **Sources / provenance:** files=8 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Simulates learner behavior, confusion points, and assessment performance Host role binding: `LearnerSimAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Simulates learner behavior, confusi…

**From `agents.md` design row:**

- Responsibility: Simulates learner behavior, confusion points, and assessment performance
- Knowledge distillation source: Learner-modeling datasets, completion analytics, quiz outcome patterns
- Self-quality criteria: Friction-point prediction, completion accuracy, simulated quiz realism
- Surpass-human signal (aspirational): Predicts weak spots before live learner complaints emerge
- Accepts critique from: InstructionalDesignAgent, LMSAgent, AnalystAgent
- Comments on: Confusing content, weak assessments, low-completion pathways
- Tool access (design): Learner simulation models, assessment predictors, LMS data
- Architecture pattern (design): Audience-style simulation adapted for learning outcomes

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1233 chars). VA source responsibility: Simulates learner behavior, confusion points, and assessment performance |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Learner-modeling datasets, completion analytics, quiz outcome patterns |
| 3) Sources exist / know how to obtain them | **YES** | 8 source files + PROVENANCE. VA listed: Learner-modeling datasets, completion analytics, quiz outcome patterns |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Friction-point prediction, completion accuracy, simulated quiz realism |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Predicts weak spots before live learner complaints emerge |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.learnersim.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: Audience-style simulation adapted for learnin… |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: InstructionalDesignAgent, LMSAgent, AnalystAgent; comments … |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.learnersim.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.learnersim.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.learnersim` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.continuity` — ContinuityAgent

- **VA id / category:** 98 / `10-Sup`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.continuity.v1` / files=0  
- **Rubric ref / files:** `video.rubric.continuity.v1` / files=0  
- **Sources / provenance:** files=11 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Maintains continuity across character, prop, wardrobe, environment, and time-state Host role binding: `ContinuityAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Maintains continuity acro…

**From `agents.md` design row:**

- Responsibility: Maintains continuity across character, prop, wardrobe, environment, and time-state
- Knowledge distillation source: Continuity logs, script supervisor practices, asset manifest state tracking
- Self-quality criteria: State-drift detection, scene-to-scene consistency, manifest update correctness
- Surpass-human signal (aspirational): Catches continuity breaks earlier than end-of-post review
- Accepts critique from: CostumeDesignAgent, MUAAgent, AIQAConsistencyAgent, CinematographerAgent (DoP), GateKeeperAgent
- Comments on: Character-state drift, wardrobe and prop mismatch, time logic errors
- Tool access (design): State manifests, shot comparison tools, continuity DB
- Architecture pattern (design): Tool-use / ReAct with continuity manifest enforcement

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1314 chars). VA source responsibility: Maintains continuity across character, prop, wardrobe, environment, and time-state |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Continuity logs, script supervisor practices, asset manifest state tracking |
| 3) Sources exist / know how to obtain them | **YES** | 11 source files + PROVENANCE. VA listed: Continuity logs, script supervisor practices, asset manifest state tracking |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: State-drift detection, scene-to-scene consistency, manifest update correctness |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Catches continuity breaks earlier than end-of-post review |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.continuity.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: Tool-use / ReAct with continuity manifest enf… |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: CostumeDesignAgent, MUAAgent, AIQAConsistencyAgent, Cinemat… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.continuity.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.continuity.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.continuity` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.lipsync` — LipSyncAgent

- **VA id / category:** 99 / `10-Sup`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.lipsync.v1` / files=0  
- **Rubric ref / files:** `video.rubric.lipsync.v1` / files=0  
- **Sources / provenance:** files=10 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Validates and refines phoneme-viseme alignment as a dedicated gate Host role binding: `LipSyncAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Validates and refines phoneme-viseme alignme…

**From `agents.md` design row:**

- Responsibility: Validates and refines phoneme-viseme alignment as a dedicated gate
- Knowledge distillation source: Lip-sync research, animation timing references, viseme datasets
- Self-quality criteria: Sync error below threshold, correction specificity, low false positives
- Surpass-human signal (aspirational): Finds sync drift more precisely than general QC review
- Accepts critique from: VoiceCloneAgent / LipSyncSpecialist, AnimatorAgent, AIQAConsistencyAgent
- Comments on: Mouth-shape mismatch, frame drift in dialogue, correction priority
- Tool access (design): Phoneme-viseme aligners, frame-level sync tools
- Architecture pattern (design): Self-Refine around sync validator outputs

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1214 chars). VA source responsibility: Validates and refines phoneme-viseme alignment as a dedicated gate |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Lip-sync research, animation timing references, viseme datasets |
| 3) Sources exist / know how to obtain them | **YES** | 10 source files + PROVENANCE. VA listed: Lip-sync research, animation timing references, viseme datasets |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Sync error below threshold, correction specificity, low false positives |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Finds sync drift more precisely than general QC review |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.lipsync.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: Self-Refine around sync validator outputs |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: VoiceCloneAgent / LipSyncSpecialist, AnimatorAgent, AIQACon… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.lipsync.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.lipsync.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.lipsync` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.musicsupervisor` — MusicSupervisorAgent

- **VA id / category:** 100 / `10-Sup`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.musicsupervisor.v1` / files=0  
- **Rubric ref / files:** `video.rubric.musicsupervisor.v1` / files=0  
- **Sources / provenance:** files=7 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.0/11 (Y=2 P=8 N=1)  
- **SPEC responsibility excerpt:** Manages music fit, cue usage, rights awareness, and soundtrack packaging Host role binding: `MusicSupervisorAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Manages music fit, cue usage, …

**From `agents.md` design row:**

- Responsibility: Manages music fit, cue usage, rights awareness, and soundtrack packaging
- Knowledge distillation source: Music supervision notes, cue placement references, soundtrack release practice
- Self-quality criteria: Cue suitability, rights-awareness coverage, soundtrack-package completeness
- Surpass-human signal (aspirational): Coordinates music placements more consistently than fragmented handoffs
- Accepts critique from: ComposerAgent, TrailerEditorAgent, LabelA&RAgent, LegalAgent
- Comments on: Cue misuse, music-rights ambiguity, soundtrack cohesion issues
- Tool access (design): Music asset trackers, cue sheets, soundtrack package tools
- Architecture pattern (design): ReAct over cue sheets and rights requirements

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1269 chars). VA source responsibility: Manages music fit, cue usage, rights awareness, and soundtrack packaging |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Music supervision notes, cue placement references, soundtrack release practice |
| 3) Sources exist / know how to obtain them | **PARTIAL** | 7 local source files; acquisition path may still be design-only (URLs/corpora not fully licensed). VA listed: Music supervision notes, cue placement references, soundtrack release practice |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Cue suitability, rights-awareness coverage, soundtrack-package completeness |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Coordinates music placements more consistently than fragmented handoffs |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.musicsupervisor.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: ReAct over cue sheets and rights require… |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: ComposerAgent, TrailerEditorAgent, LabelA&RAgent, LegalAgen… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.musicsupervisor.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.musicsupervisor.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.musicsupervisor` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.labela_r` — LabelA&RAgent

- **VA id / category:** 101 / `10-Sup`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.labela_r.v1` / files=0  
- **Rubric ref / files:** `video.rubric.labela_r.v1` / files=0  
- **Sources / provenance:** files=7 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.0/11 (Y=2 P=8 N=1)  
- **SPEC responsibility excerpt:** Represents label and artist direction for music-specific workflows Host role binding: `LabelA&RAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Represents label and artist direction for m…

**From `agents.md` design row:**

- Responsibility: Represents label and artist direction for music-specific workflows
- Knowledge distillation source: A&R playbooks, label release notes, artist brief archives
- Self-quality criteria: Artist-fit quality, release positioning, feedback turnaround
- Surpass-human signal (aspirational): Aligns music creative faster than disconnected stakeholder threads
- Accepts critique from: MusicVideoDirectorAgent, MusicSupervisorAgent, LabelDigitalAgent
- Comments on: Artist-direction drift, release mismatch, packaging weakness
- Tool access (design): Repertoire systems, release trackers, artist brief tools
- Architecture pattern (design): Multi-agent debate with music stakeholders

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1206 chars). VA source responsibility: Represents label and artist direction for music-specific workflows |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: A&R playbooks, label release notes, artist brief archives |
| 3) Sources exist / know how to obtain them | **PARTIAL** | 7 local source files; acquisition path may still be design-only (URLs/corpora not fully licensed). VA listed: A&R playbooks, label release notes, artist brief archives |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Artist-fit quality, release positioning, feedback turnaround |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Aligns music creative faster than disconnected stakeholder threads |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.labela_r.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: Multi-agent debate with music stakeholders |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: MusicVideoDirectorAgent, MusicSupervisorAgent, LabelDigital… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.labela_r.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.labela_r.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.labela_r` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.labeldigital` — LabelDigitalAgent

- **VA id / category:** 102 / `10-Sup`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.labeldigital.v1` / files=0  
- **Rubric ref / files:** `video.rubric.labeldigital.v1` / files=0  
- **Sources / provenance:** files=7 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.0/11 (Y=2 P=8 N=1)  
- **SPEC responsibility excerpt:** Runs label-side digital rollout, metadata, and channel packaging Host role binding: `LabelDigitalAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Runs label-side digital rollout, metadata…

**From `agents.md` design row:**

- Responsibility: Runs label-side digital rollout, metadata, and channel packaging
- Knowledge distillation source: Digital music release operations, metadata schemas, distribution platform requirements
- Self-quality criteria: Metadata completeness, rollout timing, channel readiness
- Surpass-human signal (aspirational): Delivers cleaner label-side packages than ad hoc release ops
- Accepts critique from: MusicVideoDirectorAgent, SocialMediaStrategistAgent, MarketingAgent
- Comments on: Missing metadata, release timing issues, asset-version confusion
- Tool access (design): Digital release systems, channel dashboards, metadata tools
- Architecture pattern (design): ReAct on release package requirements

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1230 chars). VA source responsibility: Runs label-side digital rollout, metadata, and channel packaging |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Digital music release operations, metadata schemas, distribution platform requirements |
| 3) Sources exist / know how to obtain them | **PARTIAL** | 7 local source files; acquisition path may still be design-only (URLs/corpora not fully licensed). VA listed: Digital music release operations, metadata schemas, distribution platform requirements |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Metadata completeness, rollout timing, channel readiness |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Delivers cleaner label-side packages than ad hoc release ops |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.labeldigital.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: ReAct on release package requirements |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: MusicVideoDirectorAgent, SocialMediaStrategistAgent, Market… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.labeldigital.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.labeldigital.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.labeldigital` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.deepfakedetection` — DeepfakeDetectionAgent

- **VA id / category:** 103 / `10-Sup`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.deepfakedetection.v1` / files=0  
- **Rubric ref / files:** `video.rubric.deepfakedetection.v1` / files=0  
- **Sources / provenance:** files=8 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Detects synthetic identity, voice, and provenance deception risks Host role binding: `DeepfakeDetectionAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Detects synthetic identity, voice, …

**From `agents.md` design row:**

- Responsibility: Detects synthetic identity, voice, and provenance deception risks
- Knowledge distillation source: Deepfake forensics corpora, synthetic-media benchmarks, identity-risk studies
- Self-quality criteria: Forensic recall, false-negative control, provenance-validation accuracy
- Surpass-human signal (aspirational): Catches deceptive synthetic markers that generic QC misses
- Accepts critique from: AvatarDesignAgent, VoiceCloneAgent, TrustSafetyAgent, SafetyRedTeamAgent
- Comments on: Identity anomalies, provenance holes, deceptive synthesis patterns
- Tool access (design): Forensic models, face/voice anomaly detectors, provenance validators
- Architecture pattern (design): Tool-use / ReAct with forensic scoring

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1258 chars). VA source responsibility: Detects synthetic identity, voice, and provenance deception risks |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Deepfake forensics corpora, synthetic-media benchmarks, identity-risk studies |
| 3) Sources exist / know how to obtain them | **YES** | 8 source files + PROVENANCE. VA listed: Deepfake forensics corpora, synthetic-media benchmarks, identity-risk studies |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Forensic recall, false-negative control, provenance-validation accuracy |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Catches deceptive synthetic markers that generic QC misses |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.deepfakedetection.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: Tool-use / ReAct with forensic scoring |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: AvatarDesignAgent, VoiceCloneAgent, TrustSafetyAgent, Safet… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.deepfakedetection.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.deepfakedetection.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.deepfakedetection` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.comms` — CommsAgent

- **VA id / category:** 104 / `10-Sup`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.comms.v1` / files=0  
- **Rubric ref / files:** `video.rubric.comms.v1` / files=0  
- **Sources / provenance:** files=8 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Coordinates external messaging, disclosure, and public-response posture Host role binding: `CommsAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Coordinates external messaging, disclosur…

**From `agents.md` design row:**

- Responsibility: Coordinates external messaging, disclosure, and public-response posture
- Knowledge distillation source: Crisis communication guides, disclosure standards, PR playbooks
- Self-quality criteria: Message consistency, disclosure completeness, escalation quality
- Surpass-human signal (aspirational): Produces faster aligned responses than fragmented stakeholder messaging
- Accepts critique from: MarketingAgent, CommunityAgent, LegalAgent, BrandAgent
- Comments on: Disclosure gaps, inconsistent external messaging, weak response framing
- Tool access (design): Comms calendars, approval workflows, response templates
- Architecture pattern (design): ReAct with approval chains

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1212 chars). VA source responsibility: Coordinates external messaging, disclosure, and public-response posture |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Crisis communication guides, disclosure standards, PR playbooks |
| 3) Sources exist / know how to obtain them | **YES** | 8 source files + PROVENANCE. VA listed: Crisis communication guides, disclosure standards, PR playbooks |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Message consistency, disclosure completeness, escalation quality |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Produces faster aligned responses than fragmented stakeholder messaging |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.comms.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: ReAct with approval chains |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: MarketingAgent, CommunityAgent, LegalAgent, BrandAgent; com… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.comms.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.comms.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.comms` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.archiveproducer` — ArchiveProducerAgent

- **VA id / category:** 105 / `10-Sup`  
- **Status / provider / network:** `registered` / `media_host` / network=True  
- **Tools:** `media.stub, media.sora, media.veo, media.runway`  
- **Prompt ref / files:** `video.prompt.archiveproducer.v1` / files=0  
- **Rubric ref / files:** `video.rubric.archiveproducer.v1` / files=0  
- **Sources / provenance:** files=7 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.0/11 (Y=2 P=8 N=1)  
- **SPEC responsibility excerpt:** Packages archival materials and source assets for reuse-heavy or documentary workflows Host role binding: `ArchiveProducerAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Packages archiva…

**From `agents.md` design row:**

- Responsibility: Packages archival materials and source assets for reuse-heavy or documentary workflows
- Knowledge distillation source: Archive production notes, source curation practices, provenance preservation standards
- Self-quality criteria: Source package completeness, rights coverage, provenance preservation
- Surpass-human signal (aspirational): Assembles reusable archival packages more cleanly than manual gather-and-sort workflows
- Accepts critique from: ArchiveResearchAgent, JournalistAgent, LegalAgent
- Comments on: Missing archival context, weak source packaging, rights gaps
- Tool access (design): Archive asset managers, metadata systems, provenance logs
- Architecture pattern (design): ReAct over archival manifests

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1285 chars). VA source responsibility: Packages archival materials and source assets for reuse-heavy or documentary workflows |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Archive production notes, source curation practices, provenance preservation standards |
| 3) Sources exist / know how to obtain them | **PARTIAL** | 7 local source files; acquisition path may still be design-only (URLs/corpora not fully licensed). VA listed: Archive production notes, source curation practices, provenance preservation standards |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Source package completeness, rights coverage, provenance preservation |
| 5) Implementation surpasses human yet? | **NO** | Has live-tool path but no measured human-parity benchmark results in host. Design may state aspirational surpass signals only. VA aspirational signal: Assembles reusable archival packages more cleanly than manual gather-and-sort workflows |
| 6) How they execute the job | **PARTIAL** | Host may invoke media tools ['media.stub', 'media.sora', 'media.veo', 'media.runway']; prompt/rubric refs exist but prompts/ are empty stubs for most agents. Not a free-running coding plan agent. VA architecture: ReAct over archival manifests |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: ArchiveResearchAgent, JournalistAgent, LegalAgent; comments… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.archiveproducer.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.archiveproducer.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.archiveproducer` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.standardseditor` — StandardsEditorAgent

- **VA id / category:** 106 / `10-Sup`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.standardseditor.v1` / files=0  
- **Rubric ref / files:** `video.rubric.standardseditor.v1` / files=0  
- **Sources / provenance:** files=8 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Enforces editorial standards, sourcing discipline, and corrections policy Host role binding: `StandardsEditorAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Enforces editorial standards,…

**From `agents.md` design row:**

- Responsibility: Enforces editorial standards, sourcing discipline, and corrections policy
- Knowledge distillation source: Newsroom standards manuals, corrections policies, attribution standards
- Self-quality criteria: Standards-compliance rate, attribution accuracy, corrections readiness
- Surpass-human signal (aspirational): Reduces standards drift better than late-stage copy edits
- Accepts critique from: JournalistAgent, FactCheckerAgent, CorrectionsAgent, LegalAgent
- Comments on: Weak attribution, standards violations, correction policy gaps
- Tool access (design): Editorial checklists, attribution validators, standards DB
- Architecture pattern (design): Constitutional AI with editorial standards constitution

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1258 chars). VA source responsibility: Enforces editorial standards, sourcing discipline, and corrections policy |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Newsroom standards manuals, corrections policies, attribution standards |
| 3) Sources exist / know how to obtain them | **YES** | 8 source files + PROVENANCE. VA listed: Newsroom standards manuals, corrections policies, attribution standards |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Standards-compliance rate, attribution accuracy, corrections readiness |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Reduces standards drift better than late-stage copy edits |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.standardseditor.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: Constitutional AI with editorial standar… |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: JournalistAgent, FactCheckerAgent, CorrectionsAgent, LegalA… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.standardseditor.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.standardseditor.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.standardseditor` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.ethics` — EthicsAgent

- **VA id / category:** 107 / `10-Sup`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.ethics.v1` / files=0  
- **Rubric ref / files:** `video.rubric.ethics.v1` / files=0  
- **Sources / provenance:** files=10 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Reviews ethical risk, disclosure sufficiency, fairness, and social impact Host role binding: `EthicsAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Reviews ethical risk, disclosure suffi…

**From `agents.md` design row:**

- Responsibility: Reviews ethical risk, disclosure sufficiency, fairness, and social impact
- Knowledge distillation source: Ethics frameworks, synthetic-media disclosure guidance, fairness audits
- Self-quality criteria: Ethical issue recall, mitigation clarity, escalation precision
- Surpass-human signal (aspirational): Surfaces release risks earlier than reactive ethics review
- Accepts critique from: StandardsEditorAgent, ComplianceAgent (Legal), TrustSafetyAgent, SafetyRedTeamAgent
- Comments on: Disclosure insufficiency, fairness concerns, sensitive-content risk
- Tool access (design): Ethics review templates, risk matrices, disclosure checklists
- Architecture pattern (design): Multi-agent debate + constitutional review

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1257 chars). VA source responsibility: Reviews ethical risk, disclosure sufficiency, fairness, and social impact |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Ethics frameworks, synthetic-media disclosure guidance, fairness audits |
| 3) Sources exist / know how to obtain them | **YES** | 10 source files + PROVENANCE. VA listed: Ethics frameworks, synthetic-media disclosure guidance, fairness audits |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Ethical issue recall, mitigation clarity, escalation precision |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Surfaces release risks earlier than reactive ethics review |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.ethics.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: Multi-agent debate + constitutional review |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: StandardsEditorAgent, ComplianceAgent (Legal), TrustSafetyA… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.ethics.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.ethics.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.ethics` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.channelmanager` — ChannelManagerAgent

- **VA id / category:** 108 / `10-Sup`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.channelmanager.v1` / files=0  
- **Rubric ref / files:** `video.rubric.channelmanager.v1` / files=0  
- **Sources / provenance:** files=7 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.0/11 (Y=2 P=8 N=1)  
- **SPEC responsibility excerpt:** Manages episodic or platform channel operations for cadence and metadata readiness Host role binding: `ChannelManagerAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Manages episodic or p…

**From `agents.md` design row:**

- Responsibility: Manages episodic or platform channel operations for cadence and metadata readiness
- Knowledge distillation source: Channel publishing playbooks, metadata standards, scheduling ops
- Self-quality criteria: Publishing readiness, cadence stability, metadata completeness
- Surpass-human signal (aspirational): Improves publishing discipline over manual channel operations
- Accepts critique from: SocialMediaStrategistAgent, SEOAgent, AnalystAgent, MarketingAgent
- Comments on: Release readiness gaps, metadata omissions, schedule slippage
- Tool access (design): CMS/channel dashboards, scheduler tools, metadata validators
- Architecture pattern (design): ReAct with publishing runbooks

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1243 chars). VA source responsibility: Manages episodic or platform channel operations for cadence and metadata readiness |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Channel publishing playbooks, metadata standards, scheduling ops |
| 3) Sources exist / know how to obtain them | **PARTIAL** | 7 local source files; acquisition path may still be design-only (URLs/corpora not fully licensed). VA listed: Channel publishing playbooks, metadata standards, scheduling ops |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Publishing readiness, cadence stability, metadata completeness |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Improves publishing discipline over manual channel operations |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.channelmanager.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: ReAct with publishing runbooks |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: SocialMediaStrategistAgent, SEOAgent, AnalystAgent, Marketi… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.channelmanager.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.channelmanager.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.channelmanager` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.corrections` — CorrectionsAgent

- **VA id / category:** 109 / `10-Sup`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.corrections.v1` / files=0  
- **Rubric ref / files:** `video.rubric.corrections.v1` / files=0  
- **Sources / provenance:** files=11 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Coordinates post-publication fixes and correction disclosures Host role binding: `CorrectionsAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Coordinates post-publication fixes and correc…

**From `agents.md` design row:**

- Responsibility: Coordinates post-publication fixes and correction disclosures
- Knowledge distillation source: Corrections workflows, retraction and update policies, version tracking
- Self-quality criteria: Correction turnaround, version replacement accuracy, notice completeness
- Surpass-human signal (aspirational): Resolves post-release issues faster than unstructured incident handling
- Accepts critique from: StandardsEditorAgent, FactCheckerAgent, ChannelManagerAgent
- Comments on: Unclosed correction loops, incomplete notices, stale versions
- Tool access (design): Version-control systems, publishing tools, correction trackers
- Architecture pattern (design): ReAct over correction and replacement workflows

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1237 chars). VA source responsibility: Coordinates post-publication fixes and correction disclosures |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Corrections workflows, retraction and update policies, version tracking |
| 3) Sources exist / know how to obtain them | **YES** | 11 source files + PROVENANCE. VA listed: Corrections workflows, retraction and update policies, version tracking |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Correction turnaround, version replacement accuracy, notice completeness |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Resolves post-release issues faster than unstructured incident handling |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.corrections.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: ReAct over correction and replacement workfl… |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: StandardsEditorAgent, FactCheckerAgent, ChannelManagerAgent… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.corrections.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.corrections.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.corrections` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.mpa` — MPAAgent

- **VA id / category:** 110 / `10-Sup`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.mpa.v1` / files=0  
- **Rubric ref / files:** `video.rubric.mpa.v1` / files=0  
- **Sources / provenance:** files=30 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Prepares rating-related packaging and release-readiness inputs for feature workflows Host role binding: `MPAAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Prepares rating-related packag…

**From `agents.md` design row:**

- Responsibility: Prepares rating-related packaging and release-readiness inputs for feature workflows
- Knowledge distillation source: Rating submission references, content advisories, theatrical packaging rules
- Self-quality criteria: Rating-package completeness, advisory clarity, escalation quality
- Surpass-human signal (aspirational): Prepares cleaner feature-release classification packages than manual prep
- Accepts critique from: ProducerAgent / EP, LegalAgent, EthicsAgent
- Comments on: Missing advisories, incomplete rating prep, unclear classification support
- Tool access (design): Submission packages, advisory templates, classification checklists
- Architecture pattern (design): Human-in-the-loop with structured packaging support

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1280 chars). VA source responsibility: Prepares rating-related packaging and release-readiness inputs for feature workflows |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Rating submission references, content advisories, theatrical packaging rules |
| 3) Sources exist / know how to obtain them | **YES** | 30 source files + PROVENANCE. VA listed: Rating submission references, content advisories, theatrical packaging rules |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Rating-package completeness, advisory clarity, escalation quality |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Prepares cleaner feature-release classification packages than manual prep |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.mpa.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: Human-in-the-loop with structured packaging support |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: ProducerAgent / EP, LegalAgent, EthicsAgent; comments on: M… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.mpa.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.mpa.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.mpa` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.sales` — SalesAgent

- **VA id / category:** 111 / `10-Sup`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.sales.v1` / files=0  
- **Rubric ref / files:** `video.rubric.sales.v1` / files=0  
- **Sources / provenance:** files=8 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Handles buyer-facing sales packaging for distributors and outlets Host role binding: `SalesAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Handles buyer-facing sales packaging for distri…

**From `agents.md` design row:**

- Responsibility: Handles buyer-facing sales packaging for distributors and outlets
- Knowledge distillation source: Rights windowing playbooks, market package examples, buyer materials
- Self-quality criteria: Buyer-package completeness, rights clarity, market-fit packaging
- Surpass-human signal (aspirational): Produces sales-ready release packets faster than manual assembly
- Accepts critique from: ProducerAgent / EP, DistributorAgent, MarketingAgent
- Comments on: Missing buyer info, weak positioning, incomplete rights summaries
- Tool access (design): Rights systems, package builders, buyer CRM
- Architecture pattern (design): ReAct over buyer package requirements

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1189 chars). VA source responsibility: Handles buyer-facing sales packaging for distributors and outlets |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Rights windowing playbooks, market package examples, buyer materials |
| 3) Sources exist / know how to obtain them | **YES** | 8 source files + PROVENANCE. VA listed: Rights windowing playbooks, market package examples, buyer materials |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Buyer-package completeness, rights clarity, market-fit packaging |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Produces sales-ready release packets faster than manual assembly |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.sales.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: ReAct over buyer package requirements |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: ProducerAgent / EP, DistributorAgent, MarketingAgent; comme… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.sales.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.sales.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.sales` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.distributor` — DistributorAgent

- **VA id / category:** 112 / `10-Sup`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.distributor.v1` / files=0  
- **Rubric ref / files:** `video.rubric.distributor.v1` / files=0  
- **Sources / provenance:** files=12 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.5/11 (Y=3 P=7 N=1)  
- **SPEC responsibility excerpt:** Manages downstream delivery to buyers, platforms, and territories Host role binding: `DistributorAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Manages downstream delivery to buyers, pl…

**From `agents.md` design row:**

- Responsibility: Manages downstream delivery to buyers, platforms, and territories
- Knowledge distillation source: Distribution specs, outlet requirements, package handoff workflows
- Self-quality criteria: Outlet-spec compliance, handoff completeness, territorial routing accuracy
- Surpass-human signal (aspirational): Reduces delivery-spec mismatches relative to fragmented delivery ops
- Accepts critique from: SalesAgent, ArchiveMasterAgent, SoundMixerAgent, ColoristAgent
- Comments on: Spec mismatches, incomplete outlet packages, routing errors
- Tool access (design): Delivery management systems, outlet spec DB, packaging validators
- Architecture pattern (design): ReAct over distribution specification matrices

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1242 chars). VA source responsibility: Manages downstream delivery to buyers, platforms, and territories |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Distribution specs, outlet requirements, package handoff workflows |
| 3) Sources exist / know how to obtain them | **YES** | 12 source files + PROVENANCE. VA listed: Distribution specs, outlet requirements, package handoff workflows |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Outlet-spec compliance, handoff completeness, territorial routing accuracy |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Reduces delivery-spec mismatches relative to fragmented delivery ops |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.distributor.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: ReAct over distribution specification matric… |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: SalesAgent, ArchiveMasterAgent, SoundMixerAgent, ColoristAg… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.distributor.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.distributor.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.distributor` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.awardsstrategist` — AwardsStrategistAgent

- **VA id / category:** 113 / `10-Sup`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.awardsstrategist.v1` / files=0  
- **Rubric ref / files:** `video.rubric.awardsstrategist.v1` / files=0  
- **Sources / provenance:** files=6 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.0/11 (Y=2 P=8 N=1)  
- **SPEC responsibility excerpt:** Plans awards submissions and campaign timing Host role binding: `AwardsStrategistAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Plans awards submissions and campaign timing ### Knowledg…

**From `agents.md` design row:**

- Responsibility: Plans awards submissions and campaign timing
- Knowledge distillation source: Awards calendars, campaign playbooks, category positioning histories
- Self-quality criteria: Submission readiness, category fit, timeline precision
- Surpass-human signal (aspirational): Improves awards-timing discipline over generic release planning
- Accepts critique from: ProducerAgent / EP, CriticAgent, MarketingAgent
- Comments on: Weak campaign timing, poor category fit, incomplete submission assets
- Tool access (design): Awards calendars, campaign trackers, submission checklists
- Architecture pattern (design): ReAct with awards timeline optimization

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1163 chars). VA source responsibility: Plans awards submissions and campaign timing |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Awards calendars, campaign playbooks, category positioning histories |
| 3) Sources exist / know how to obtain them | **PARTIAL** | 6 local source files; acquisition path may still be design-only (URLs/corpora not fully licensed). VA listed: Awards calendars, campaign playbooks, category positioning histories |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Submission readiness, category fit, timeline precision |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Improves awards-timing discipline over generic release planning |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.awardsstrategist.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: ReAct with awards timeline optimization |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: ProducerAgent / EP, CriticAgent, MarketingAgent; comments o… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.awardsstrategist.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.awardsstrategist.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.awardsstrategist` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

##### `video.archivemaster` — ArchiveMasterAgent

- **VA id / category:** 114 / `10-Sup`  
- **Status / provider / network:** `registered` / `local_deterministic` / network=False  
- **Tools:** `(none)`  
- **Prompt ref / files:** `video.prompt.archivemaster.v1` / files=0  
- **Rubric ref / files:** `video.rubric.archivemaster.v1` / files=0  
- **Sources / provenance:** files=7 · PROVENANCE=True · MAPPING=True  
- **Critique edges:** `{"inputs": ["video.critic"], "outputs": ["video.judge"]}`  
- **Maturity:** 6.0/11 (Y=2 P=8 N=1)  
- **SPEC responsibility excerpt:** Produces archive-grade masters and preservation packages Host role binding: `ArchiveMasterAgent (VA Domain Pack)`. Design-time VA table content below is historical and non-binding for activation. ### Responsibility (from VA table) Produces archive-grade masters and preservation …

**From `agents.md` design row:**

- Responsibility: Produces archive-grade masters and preservation packages
- Knowledge distillation source: Preservation standards, checksum workflows, archive metadata practice
- Self-quality criteria: Checksum integrity, preservation metadata completeness, archive package validity
- Surpass-human signal (aspirational): Delivers more reliable archive packages than late-stage export-only workflows
- Accepts critique from: DistributorAgent, ColoristAgent, SoundMixerAgent, GateKeeperAgent
- Comments on: Incomplete preservation bundles, archive-spec violations, metadata gaps
- Tool access (design): Archive mastering tools, checksum utilities, preservation metadata systems
- Architecture pattern (design): Tool-use / ReAct with preservation validation

| Q | Status | Assessment |
|---|--------|------------|
| 1) Responsibility well defined in SPEC.md | **YES** | SPEC has ## Responsibility (1267 chars). VA source responsibility: Produces archive-grade masters and preservation packages |
| 2) Plan to distill professional knowledge | **YES** | Knowledge distillation planned in agents.md / SPEC. Planned sources: Preservation standards, checksum workflows, archive metadata practice |
| 3) Sources exist / know how to obtain them | **PARTIAL** | 7 local source files; acquisition path may still be design-only (URLs/corpora not fully licensed). VA listed: Preservation standards, checksum workflows, archive metadata practice |
| 4) Self-evaluation methods & content collected | **PARTIAL** | Criteria designed (agents.md / SPEC / rubric_reference) but executable rubric files largely missing. VA criteria: Checksum integrity, preservation metadata completeness, archive package validity |
| 5) Implementation surpasses human yet? | **NO** | Not surpassing humans in implementation terms. Design-time surpass signals are aspirational targets, not validated outcomes. VA aspirational signal: Delivers more reliable archive packages than late-stage export-only workflows |
| 6) How they execute the job | **PARTIAL** | Host-orchestrated / graph-driven. prompt_reference=video.prompt.archivemaster.v1; provider=local_deterministic; tools=['(none/stub)']. No per-agent autonomous coding-plan runner installed by default. VA architecture: Tool-use / ReAct with preservation validat… |
| 7) Skills / plugins / harness for themselves | **PARTIAL** | Relies on pack-level special_skills + host adapters; per-agent private skill/plugin install not present. |
| 8) Mechanism to improve themselves | **PARTIAL** | SPEC describes continuous learning; max_refinement_count=3. Host RLAIF loop not fully productized per agent. |
| 9) Collect/research info to improve | **PARTIAL** | Sources + distillation text give a research path; automated research→eval→promote loop incomplete. |
| 10) Get/send instructions to other agents | **PARTIAL** | critique_edges + handoff/critique design present: {"inputs": ["video.critic"], "outputs": ["video.judge"]}. Runtime multi-agent instruction bus partially implemented via host graphs. VA accepts from: DistributorAgent, ColoristAgent, SoundMixerAgent, GateKeepe… |
| 11) Resolve conflict + confirm | **PARTIAL** | SPEC/common structure describes dispute→Judge→HiTL. Autonomous conflict resolution + confirmation not fully proven in host for each agent. |

**Deficiencies & suggestions (improve):**

- Materialize executable prompt under prompts/ implementing video.prompt.archivemaster.v1 (system + task + output schema).
- Materialize rubric under rubrics/ from VA Self-Quality Criteria; wire to host eval harness as video.rubric.archivemaster.v1.
- Replace aspirational surpass claims with measured benchmarks (blind pairwise / CSAT / rubric) stored as eval fixtures; do not claim human-surpass until gates pass.
- Define least-privilege tool allowlist and host adapter tests; keep fail-closed without credentials.
- Implement closed-loop improvement: critique → refine ≤N → judge → promote/reject with evidence bundle.
- Implement typed CritiqueMessage + handoff schema end-to-end on host graphs; publish accepts_from/comments_on matrix from agents.md.
- Add conflict policy: severity routing (blocker/major/minor), JudgeAgent debate, HiTL confirm for unresolved blockers.

**Rethink / raise the bar:**

1. Freeze a **golden task** for `video.archivemaster` (input brief → expected artifact schema → L1/L2 thresholds from agents.md).
2. Check in **prompt v1 + rubric v1** with deterministic unit tests (schema + fixture), not only SPEC prose.
3. Prove **one collaboration edge** end-to-end (send critique → receive → refine or escalate) with evidence IDs.
4. Record **human baseline** on the same golden task; never claim surpass without that delta.

---

## 5. Implementation roadmap (fleet)

### Wave A — Make responsibility & evaluation real (2–3 weeks)

1. Generate `prompts/*.md` + `rubrics/*.json` for all 114 agents from agents.md columns + architecture patterns.
2. CI gate: forbid empty prompts/rubrics directories.
3. Golden evals for spine agents: orchestrator, planner, director, editor, critic, judge.

### Wave B — Collaboration & conflict bus (2–4 weeks)

1. Implement CritiqueMessage schema as host API with severity.
2. Wire `critique_edges` as enforceable routes.
3. JudgeAgent multi-agent debate + HiTL confirm for blockers.

### Wave C — Tools & knowledge legality (ongoing)

1. Prioritize tool adapters that unlock craft value (media already started; editor/color/sound next).
2. Source acquisition SOP: license, refresh, quarantine, hash lock.
3. Distillation loop jobs per category, starting with 9-Meta research agents.

### Wave D — Measured quality (continuous)

1. Human baseline capture for top 20 revenue-critical agents.
2. Publish dashboards: L1 pass rate, L2 rubric, preference win-rate vs human.
3. Only then revisit “surpass human” claims per agent.

---

## 6. Special notes

- **Specials pack** (`business/specials`) is intentionally out of the video roster tables in this report; treat as shared platform skills, not video craft org nodes.
- **Production activation** for media is env-gated (`CASOPS_VIDEO_PRODUCTION_ENABLED` + credentials). Fail-closed is correct; it is not the same as craft readiness.
- **Org Chart UI** visualizes hierarchy; it does not execute agents.

---

## 7. Regeneration

```bash
python scripts/business/audit_agent_capability_status.py
python scripts/business/render_agent_capability_status_v1.py
```

Outputs:

- `business/video/AGENT_CAPABILITY_AUDIT.json`
- `agent_capability_status_v1.md` (this file)

