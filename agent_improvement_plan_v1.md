# Agent Improvement Plan v1 — Path to Full Mark (11/11 YES)

**Generated:** 2026-07-30T04:49:57Z  
**Based on:** `agent_capability_status_v1.md` + `business/video/AGENT_CAPABILITY_AUDIT.json`  
**Design authority:** `va-agent-swarm/study/agents.md`  
**Scope:** 114 non-special video pack agents  
**Goal:** Every agent reaches **FULL MARK** = YES on all 11 capability questions (maturity **11.0/11**).

> Full mark is **evidence-based**. Aspirational text in agents.md does not count. Each YES requires artifacts, tests, and (for Q5) measured evaluation.

---

## 0. Full-mark definition of done

| Q | Title | YES only when | Minimum evidence artifacts |
|---|-------|---------------|----------------------------|
| Q1 | Q1 Responsibility in SPEC | Agent identity + ownership boundary is exact, unique, and injected at runtime. | See Wave actions + per-agent checklist |
| Q2 | Q2 Knowledge distillation plan | Written continuous-distillation plan with owners, cadence, and promotion criteria. | See Wave actions + per-agent checklist |
| Q3 | Q3 Sources available / obtainable | Licensed or permitted source package + acquisition SOP that can be re-run. | See Wave actions + per-agent checklist |
| Q4 | Q4 Self-evaluation methods & content | Executable L1 schema + L2 rubric + L3 preference fixtures with thresholds. | See Wave actions + per-agent checklist |
| Q5 | Q5 Surpass human (measured) | Controlled evaluation shows agent meets/exceeds agents.md surpass signal vs human baseline. | See Wave actions + per-agent checklist |
| Q6 | Q6 Job execution path | Deterministic host path: prompt + tools + graph node + evidence for the craft job. | See Wave actions + per-agent checklist |
| Q7 | Q7 Skills / plugins / harness | Role-bound skill pack + harness entry that the host can load for this agent only. | See Wave actions + per-agent checklist |
| Q8 | Q8 Self-improvement mechanism | Closed loop: critique/fail -> refine <=N -> re-eval -> promote/reject with evidence. | See Wave actions + per-agent checklist |
| Q9 | Q9 Research to improve | Agent can request/consume research packs that feed distillation and evals. | See Wave actions + per-agent checklist |
| Q10 | Q10 Collaborate / instruct others | Typed send/receive of instructions and critiques with ack and routing. | See Wave actions + per-agent checklist |
| Q11 | Q11 Conflict resolve + confirm | Severity routing, self-resolve when allowed, Judge/HiTL confirm when not. | See Wave actions + per-agent checklist |

### Scoring rule

- **FULL MARK agent:** 11 YES (no PARTIAL, no NO).
- **Fleet FULL MARK:** 114/114 agents at full mark + platform spine (critique bus, eval harness, improve loop) green.
- **Current fleet average maturity:** 6.45 / 11
- **Current cell mix:** YES=330, PARTIAL=810, NO=114

### Gap math (approximate work units)

- Cells still not YES: **924** of 1254
- Agents with zero prompt files: **114** (must become 0)
- Agents with zero rubric files: **114** (must become 0)
- Agents without measured human-surpass: **114** (all need Q5 protocol)

---

## 1. Shared platform workstreams (unlock full marks for every agent)

These are **once-for-the-fleet** systems. Per-agent work alone cannot reach YES on Q5–Q11 without them.

### Workstream P0 — Artifact materialization factory

| ID | Action | Output | Done when |
|----|--------|--------|-----------|
| P0.1 | Prompt factory from agents.md + SPEC | `prompts/<prompt_reference>.md` × 114 | CI fails if missing/empty |
| P0.2 | Rubric factory from Self-Quality Criteria | `rubrics/<rubric_reference>.json` × 114 | Host eval loads file |
| P0.3 | Source catalog factory | `sources/SOURCE_CATALOG.json` × 114 | Schema validated |
| P0.4 | Golden task scaffold | `evals/agents/<id>/golden.json` × 114 | Offline dry-run passes schema |
| P0.5 | Skills harness scaffold | `skills/SKILL.md` + `integration.json` × 114 | Host can load |
| P0.6 | Audit regen gate | re-run capability audit in CI | maturity report attached to PR |

### Workstream P1 — Execution runtime

| ID | Action | Output | Done when |
|----|--------|--------|-----------|
| P1.1 | Agent runner loads prompt_reference | host service | unit tests per category sample |
| P1.2 | Tool allowlist registry + mock adapters | adapters for design tools | mock path works offline |
| P1.3 | Graph node binding for every agent | DNA/workflow coverage map | each agent appears in >=1 executable graph or standby invoke API |
| P1.4 | Evidence writer | correlation id, artifacts, scores | every run produces evidence bundle |
| P1.5 | Fail-closed production flags | env gates | no live provider call without keys+flags |

### Workstream P2 — Evaluation & human baseline (Q4–Q5)

| ID | Action | Output | Done when |
|----|--------|--------|-----------|
| P2.1 | L1 validator library | shared schema/codec/loudness checks | reusable across agents |
| P2.2 | L2 judge harness | rubric runner | score written to evidence |
| P2.3 | L3 preference / arena harness | pairwise protocol | used for surpass metrics |
| P2.4 | Human baseline capture kit | operator protocol + forms | baseline stored per agent |
| P2.5 | Surpass dashboard | per-agent metric vs signal | YES only if gate green |

### Workstream P3 — Collaboration & conflict bus (Q10–Q11)

| ID | Action | Output | Done when |
|----|--------|--------|-----------|
| P3.1 | CritiqueMessage + InstructionMessage APIs | host contracts | OpenAPI + tests |
| P3.2 | Expand critique_edges from agents.md matrix | agent_spec updates × 114 | matrix completeness CI |
| P3.3 | Delivery/ack routing | bus | integration tests multi-agent |
| P3.4 | Judge debate + severity policy | judge service | blocker escalates |
| P3.5 | HiTL confirm actions | action refs only | UI confirm path |

### Workstream P4 — Distillation & self-improve (Q2–Q3, Q8–Q9)

| ID | Action | Output | Done when |
|----|--------|--------|-----------|
| P4.1 | Distillation plan schema + jobs | offline job | dry-run fleet |
| P4.2 | Licensed source acquisition SOP | legal/ops | catalog compliance |
| P4.3 | Research request API | meta-agent wiring | offline fixtures |
| P4.4 | Refine/promote loop | max_refinement_count enforced | before/after scores |
| P4.5 | Memory namespaces per agent | memory service | retrieve tests |

---

## 2. Phased program to fleet full mark

| Phase | Theme | Target maturity | Exit criteria |
|-------|-------|-----------------|---------------|
| **Phase 0** | Honesty & gates | report-only | CI audit; no false surpass claims in UI |
| **Phase 1** | Artifacts (P0) | ~8.0 avg | 114 prompts + 114 rubrics + catalogs |
| **Phase 2** | Spine runtime (P1+P3 meta) | 9-Meta agents ~10+ | orchestrator/planner/judge/router full paths |
| **Phase 3** | Craft execution (P1 tools by group) | ATL/Cam/Edit/Snd ~10 | offline golden pass per group samples |
| **Phase 4** | Collab+conflict all agents | Q10/Q11 YES fleet | matrix tests green |
| **Phase 5** | Human baselines (P2) | Q5 possible | baselines captured top 40 then remaining 74 |
| **Phase 6** | Full mark lock | **11.0 × 114** | audit all YES; evidence index complete |

### Recommended sequence (critical path)

```
P0 factory (prompts/rubrics/catalogs)
   -> P1 runner + mock tools
      -> 9-Meta spine (orchestrator, planner, router, judge, critic, memory)
         -> P3 critique bus
            -> craft groups ATL -> Cam/Edit/Snd -> Perf/Dist/Edu/AI -> Sup
               -> P4 distill/improve
                  -> P2 human baselines & surpass gates
                     -> FULL MARK freeze
```

---

## 3. Universal checklist (every agent must complete)

Copy this as a ticket template for each `video.*` agent:

```text
[ ] U1  SPEC Responsibility unique + does_not_own
[ ] U2  user_guide.md synced to Responsibility
[ ] U3  Knowledge Distillation Plan section + DISTILLATION_PLAN.json
[ ] U4  SOURCE_CATALOG.json + PROVENANCE + MAPPING + ACQUIRE.md
[ ] U5  prompts/<prompt_reference>.md complete
[ ] U6  rubrics/<rubric_reference>.json complete (L2 >=85 threshold)
[ ] U7  evals/agents/<id>/golden.json + offline mock run passes L1
[ ] U8  skills/SKILL.md + integration.json + harness entry
[ ] U9  allowed_tools mapped; mock adapters tested
[ ] U10 Graph/workflow binding OR invoke API binding
[ ] U11 critique_edges complete vs agents.md Accepts/Comments
[ ] U12 Collaboration Matrix section in SPEC
[ ] U13 Conflict policy section + Judge/HiTL path test
[ ] U14 Refine loop test (fail -> refine -> pass/escalate)
[ ] U15 Research request path (fixture) updates sources/research/
[ ] U16 Human baseline captured OR explicit 'not claimed' with protocol filed
[ ] U17 Surpass metric run stored; YES only if gate green
[ ] U18 Capability audit row shows 11 YES for this agent
```

---

## 4. Actions by capability question (fleet rollup)

### Q1 Responsibility in SPEC

- **Definition of YES:** Agent identity + ownership boundary is exact, unique, and injected at runtime.
- **Current:** YES=114, PARTIAL=0, NO=0
- **Agents needing work:** 0 (treat PARTIAL as incomplete)
- **Standard actions to full mark:**
  - [ ] Keep SPEC.md `## Responsibility` as single authoritative paragraph (owns / does-not-own).
  - [ ] Sync first sentence into agent_spec.json `role` and docs/user_guide.md opening.
  - [ ] Add `does_not_own: string[]` to agent_spec.json for boundary enforcement.
  - [ ] CI gate: responsibility length, uniqueness vs peer first-40 tokens, required keywords.
  - [ ] Host injects responsibility block as first system-prompt section before tools.

### Q2 Knowledge distillation plan

- **Definition of YES:** Written continuous-distillation plan with owners, cadence, and promotion criteria.
- **Current:** YES=114, PARTIAL=0, NO=0
- **Agents needing work:** 0 (treat PARTIAL as incomplete)
- **Standard actions to full mark:**
  - [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
  - [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
  - [ ] Register plan in pack corpus index with next_review_at date.
  - [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
  - [ ] Automate dry-run distillation job (offline) that validates plan schema only.

### Q3 Sources available / obtainable

- **Definition of YES:** Licensed or permitted source package + acquisition SOP that can be re-run.
- **Current:** YES=102, PARTIAL=12, NO=0
- **Agents needing work:** 12 (treat PARTIAL as incomplete)
- **Standard actions to full mark:**
  - [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
  - [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
  - [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
  - [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
  - [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

### Q4 Self-evaluation methods & content

- **Definition of YES:** Executable L1 schema + L2 rubric + L3 preference fixtures with thresholds.
- **Current:** YES=0, PARTIAL=114, NO=0
- **Agents needing work:** 114 (treat PARTIAL as incomplete)
- **Standard actions to full mark:**
  - [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
  - [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
  - [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
  - [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
  - [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

### Q5 Surpass human (measured)

- **Definition of YES:** Controlled evaluation shows agent meets/exceeds agents.md surpass signal vs human baseline.
- **Current:** YES=0, PARTIAL=0, NO=114
- **Agents needing work:** 114 (treat PARTIAL as incomplete)
- **Standard actions to full mark:**
  - [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
  - [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
  - [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
  - [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
  - [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

### Q6 Job execution path

- **Definition of YES:** Deterministic host path: prompt + tools + graph node + evidence for the craft job.
- **Current:** YES=0, PARTIAL=114, NO=0
- **Agents needing work:** 114 (treat PARTIAL as incomplete)
- **Standard actions to full mark:**
  - [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
  - [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
  - [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
  - [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
  - [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.

### Q7 Skills / plugins / harness

- **Definition of YES:** Role-bound skill pack + harness entry that the host can load for this agent only.
- **Current:** YES=0, PARTIAL=114, NO=0
- **Agents needing work:** 114 (treat PARTIAL as incomplete)
- **Standard actions to full mark:**
  - [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
  - [ ] Bind required pack special_skills (if any) via skills/bindings.json.
  - [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
  - [ ] Add capability registry entry listing skills hash + version.
  - [ ] Smoke test: host loads skill without network unless production flags set.

### Q8 Self-improvement mechanism

- **Definition of YES:** Closed loop: critique/fail -> refine <=N -> re-eval -> promote/reject with evidence.
- **Current:** YES=0, PARTIAL=114, NO=0
- **Agents needing work:** 114 (treat PARTIAL as incomplete)
- **Standard actions to full mark:**
  - [ ] Keep max_refinement_count and document policy in SPEC.
  - [ ] Implement refine loop in host using prompt_reference + critique inputs.
  - [ ] Persist improvement candidates under evidence/ with before/after scores.
  - [ ] Promotion gate: L2 score improvement and no L1 regression.
  - [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

### Q9 Research to improve

- **Definition of YES:** Agent can request/consume research packs that feed distillation and evals.
- **Current:** YES=0, PARTIAL=114, NO=0
- **Agents needing work:** 114 (treat PARTIAL as incomplete)
- **Standard actions to full mark:**
  - [ ] Define research request schema (topic, source classes, max cost, deadline).
  - [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
  - [ ] Store research outputs under sources/research/ with provenance.
  - [ ] Map research -> distillation plan update -> golden eval refresh.
  - [ ] Add dry-run research path that works offline with fixture corpora.

### Q10 Collaborate / instruct others

- **Definition of YES:** Typed send/receive of instructions and critiques with ack and routing.
- **Current:** YES=0, PARTIAL=114, NO=0
- **Agents needing work:** 114 (treat PARTIAL as incomplete)
- **Standard actions to full mark:**
  - [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
  - [ ] Implement CritiqueMessage + InstructionMessage host APIs.
  - [ ] Prove one send and one receive path in integration test for this agent.
  - [ ] Document collab partners in SPEC `## Collaboration Matrix`.
  - [ ] Orchestrator/router can address agent by id with correlation identifiers.

### Q11 Conflict resolve + confirm

- **Definition of YES:** Severity routing, self-resolve when allowed, Judge/HiTL confirm when not.
- **Current:** YES=0, PARTIAL=114, NO=0
- **Agents needing work:** 114 (treat PARTIAL as incomplete)
- **Standard actions to full mark:**
  - [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
  - [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
  - [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
  - [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
  - [ ] Surface conflict state in activity/ops UI with confirm action refs only.

---

## 5. Per-group improvement programs

### 1-ATL — Above-the-Line (5 agents, avg 6.5)

**Group tool/harness priorities:**
- media generation (shot intent preview)
- schedule/budget sheet adapters (producer)
- screenplay validators (Fountain/FDX)
- HiTL greenlight action refs

**Group milestone checklist:**
- [ ] All 5 agents complete Universal U1–U10
- [ ] Group mock adapter pack tests green
- [ ] At least 1 multi-agent path inside group using critique bus
- [ ] Human baselines for group lead agents complete
- [ ] Audit: every agent in group maturity 11.0

| Agent | Now | Gap to 11 | Priority band | First 5 actions |
|-------|-----|-----------|---------------|-----------------|
| `video.director` | 6.5 | 4.5 | P2 | 1. Q4: Write rubrics content for `video.rubric.director.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Wins ≥55% blind pairwise vs DGA cuts (Arena)<br>3. Q6: Write prompts content for `video.prompt.director.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.director`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.producer` | 6.5 | 4.5 | P2 | 1. Q4: Write rubrics content for `video.rubric.producer.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Beats PGA schedules at 0.6× cost with equal CSAT<br>3. Q6: Write prompts content for `video.prompt.producer.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.producer`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.screenwriter` | 6.5 | 4.5 | P2 | 1. Q4: Write rubrics content for `video.rubric.screenwriter.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Wins ≥50% blind read vs Black List Top-10 (WGA …<br>3. Q6: Write prompts content for `video.prompt.screenwriter.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.screenwriter`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.showrunner` | 6.5 | 4.5 | P2 | 1. Q4: Write rubrics content for `video.rubric.showrunner.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Series Bible coverage ≥99% across 10 eps (vs ~9…<br>3. Q6: Write prompts content for `video.prompt.showrunner.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.showrunner`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.casting` | 6.5 | 4.5 | P2 | 1. Q4: Write rubrics content for `video.rubric.casting.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Beats CSA casting in blind preference; hours vs…<br>3. Q6: Write prompts content for `video.prompt.casting.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.casting`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |

### 2-Cam — Camera & Lighting (3 agents, avg 6.5)

**Group tool/harness priorities:**
- camera-path / ControlNet adapters
- ACES/color pipeline validators
- drone geofence safety constitution tests

**Group milestone checklist:**
- [ ] All 3 agents complete Universal U1–U10
- [ ] Group mock adapter pack tests green
- [ ] At least 1 multi-agent path inside group using critique bus
- [ ] Human baselines for group lead agents complete
- [ ] Audit: every agent in group maturity 11.0

| Agent | Now | Gap to 11 | Priority band | First 5 actions |
|-------|-----|-----------|---------------|-----------------|
| `video.cinematographer` | 6.5 | 4.5 | P4 | 1. Q4: Write rubrics content for `video.rubric.cinematographer.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Beats ASC peer-juried reels in blind aesthetic …<br>3. Q6: Write prompts content for `video.prompt.cinematographer.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.cinematographer`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.cameraoperator` | 6.5 | 4.5 | P4 | 1. Q4: Write rubrics content for `video.rubric.cameraoperator.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Focus-pull accuracy >99% vs SOC ~97% baseline<br>3. Q6: Write prompts content for `video.prompt.cameraoperator.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.cameraoperator`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.dronepilot` | 6.5 | 4.5 | P4 | 1. Q4: Write rubrics content for `video.rubric.dronepilot.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Competition-grade smoothness at 10× sortie rate…<br>3. Q6: Write prompts content for `video.prompt.dronepilot.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.dronepilot`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |

### 3-Edit — Editorial & Color / Design (10 agents, avg 6.5)

**Group tool/harness priorities:**
- FFmpeg / EDL timeline adapters
- colorimeter / LUT validators
- storyboard panel schema
- Resolve/Nuke MCP only behind approval

**Group milestone checklist:**
- [ ] All 10 agents complete Universal U1–U10
- [ ] Group mock adapter pack tests green
- [ ] At least 1 multi-agent path inside group using critique bus
- [ ] Human baselines for group lead agents complete
- [ ] Audit: every agent in group maturity 11.0

| Agent | Now | Gap to 11 | Priority band | First 5 actions |
|-------|-----|-----------|---------------|-----------------|
| `video.editor` | 6.5 | 4.5 | P3 | 1. Q4: Write rubrics content for `video.rubric.editor.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Wins ≥55% pairwise vs ACE-credited cuts<br>3. Q6: Write prompts content for `video.prompt.editor.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.editor`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.animator_2d` | 6.5 | 4.5 | P3 | 1. Q4: Write rubrics content for `video.rubric.animator_2d.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Beats junior on Annie rubric; equals senior at …<br>3. Q6: Write prompts content for `video.prompt.animator_2d.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.animator_2d`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.motiongraphics` | 6.5 | 4.5 | P3 | 1. Q4: Write rubrics content for `video.rubric.motiongraphics.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Wins agency RFP shootouts on speed + on-brand f…<br>3. Q6: Write prompts content for `video.prompt.motiongraphics.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.motiongraphics`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.colorist` | 6.5 | 4.5 | P4 | 1. Q4: Write rubrics content for `video.rubric.colorist.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Beats junior colorist in blind preference; matc…<br>3. Q6: Write prompts content for `video.prompt.colorist.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.colorist`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.vfxsupervisor` | 6.5 | 4.5 | P4 | 1. Q4: Write rubrics content for `video.rubric.vfxsupervisor.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Weta-grade QC pass rate at fraction of time<br>3. Q6: Write prompts content for `video.prompt.vfxsupervisor.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.vfxsupervisor`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.storyboard` | 6.5 | 4.5 | P4 | 1. Q4: Write rubrics content for `video.rubric.storyboard.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Pixar story-trust pass rate at minutes per page<br>3. Q6: Write prompts content for `video.prompt.storyboard.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.storyboard`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.conceptartist` | 6.5 | 4.5 | P4 | 1. Q4: Write rubrics content for `video.rubric.conceptartist.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Wins art-director shootouts on iteration speed<br>3. Q6: Write prompts content for `video.prompt.conceptartist.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.conceptartist`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.productiondesign` | 6.5 | 4.5 | P4 | 1. Q4: Write rubrics content for `video.rubric.productiondesign.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Wins ADG blind comparisons on period-research d…<br>3. Q6: Write prompts content for `video.prompt.productiondesign.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.productiondesign`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.costumedesign` | 6.5 | 4.5 | P4 | 1. Q4: Write rubrics content for `video.rubric.costumedesign.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Beats CDG juniors on period accuracy benchmarks<br>3. Q6: Write prompts content for `video.prompt.costumedesign.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.costumedesign`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.mua_makeup` | 6.5 | 4.5 | P4 | 1. Q4: Write rubrics content for `video.rubric.mua_makeup.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Continuity break rate <0.5% (vs ~2% human)<br>3. Q6: Write prompts content for `video.prompt.mua_makeup.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.mua_makeup`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |

### 4-Snd — Sound & Music (4 agents, avg 6.5)

**Group tool/harness priorities:**
- ElevenLabs / loudness (LUFS) adapters
- stem separation mocks
- broadcast deliverable schema checks

**Group milestone checklist:**
- [ ] All 4 agents complete Universal U1–U10
- [ ] Group mock adapter pack tests green
- [ ] At least 1 multi-agent path inside group using critique bus
- [ ] Human baselines for group lead agents complete
- [ ] Audit: every agent in group maturity 11.0

| Agent | Now | Gap to 11 | Priority band | First 5 actions |
|-------|-----|-----------|---------------|-----------------|
| `video.sounddesign` | 6.5 | 4.5 | P3 | 1. Q4: Write rubrics content for `video.rubric.sounddesign.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Wins MPSE pairwise on horror/sci-fi<br>3. Q6: Write prompts content for `video.prompt.sounddesign.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.sounddesign`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.voiceover` | 6.5 | 4.5 | P3 | 1. Q4: Write rubrics content for `video.rubric.voiceover.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Beats junior VO in blind preference; matches se…<br>3. Q6: Write prompts content for `video.prompt.voiceover.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.voiceover`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.composer` | 6.5 | 4.5 | P4 | 1. Q4: Write rubrics content for `video.rubric.composer.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Wins blind pairwise on emotional-fit vs working…<br>3. Q6: Write prompts content for `video.prompt.composer.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.composer`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.soundmixer` | 6.5 | 4.5 | P4 | 1. Q4: Write rubrics content for `video.rubric.soundmixer.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: CAS spec on first pass without rework<br>3. Q6: Write prompts content for `video.prompt.soundmixer.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.soundmixer`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |

### 5-Perf — Performance & Choreography (5 agents, avg 6.3)

**Group tool/harness priorities:**
- consent / likeness gates
- motion timing rubrics
- voice sample preference judges (offline fixtures)

**Group milestone checklist:**
- [ ] All 5 agents complete Universal U1–U10
- [ ] Group mock adapter pack tests green
- [ ] At least 1 multi-agent path inside group using critique bus
- [ ] Human baselines for group lead agents complete
- [ ] Audit: every agent in group maturity 11.0

| Agent | Now | Gap to 11 | Priority band | First 5 actions |
|-------|-----|-----------|---------------|-----------------|
| `video.choreography` | 6.5 | 4.5 | P5 | 1. Q4: Write rubrics content for `video.rubric.choreography.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Wins blind preference vs choreographer drafts<br>3. Q6: Write prompts content for `video.prompt.choreography.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.choreography`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.musicvideodirector` | 6.0 | 5.0 | P5 | 1. Q3: Raise packaged sources from 7 to >=8 substantive files (excerpts + catalog).<br>2. Q4: Write rubrics content for `video.rubric.musicvideodirector.v1` (currently files=0).<br>3. Q5: Register surpass protocol for signal: Wins label-blind preference vs commercial MV sh…<br>4. Q6: Write prompts content for `video.prompt.musicvideodirector.v1` (currently files=0).<br>5. Q7: Create per-agent skills harness directory for `video.musicvideodirector`. |
| `video.comedywriter` | 6.5 | 4.5 | P5 | 1. Q4: Write rubrics content for `video.rubric.comedywriter.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Beats UCB-table-read win rate on cold-reads<br>3. Q6: Write prompts content for `video.prompt.comedywriter.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.comedywriter`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.talent` | 6.5 | 4.5 | P5 | 1. Q4: Write rubrics content for `video.rubric.talent.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Hold-rate matches top creators in cohort<br>3. Q6: Write prompts content for `video.prompt.talent.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.talent`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.ugccreator` | 6.0 | 5.0 | P5 | 1. Q3: Raise packaged sources from 7 to >=8 substantive files (excerpts + catalog).<br>2. Q4: Write rubrics content for `video.rubric.ugccreator.v1` (currently files=0).<br>3. Q5: Register surpass protocol for signal: Beats paid-creator avg ROAS at 0.1× cost<br>4. Q6: Write prompts content for `video.prompt.ugccreator.v1` (currently files=0).<br>5. Q7: Create per-agent skills harness directory for `video.ugccreator`. |

### 6-Dist — Distribution & Marketing (4 agents, avg 6.5)

**Group tool/harness priorities:**
- brand guideline checkers
- platform packaging validators
- performance marketing metric fixtures

**Group milestone checklist:**
- [ ] All 4 agents complete Universal U1–U10
- [ ] Group mock adapter pack tests green
- [ ] At least 1 multi-agent path inside group using critique bus
- [ ] Human baselines for group lead agents complete
- [ ] Audit: every agent in group maturity 11.0

| Agent | Now | Gap to 11 | Priority band | First 5 actions |
|-------|-----|-----------|---------------|-----------------|
| `video.creativedirector` | 6.5 | 4.5 | P3 | 1. Q4: Write rubrics content for `video.rubric.creativedirector.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Wins Cannes-jury-emulator gold vs human shortli…<br>3. Q6: Write prompts content for `video.prompt.creativedirector.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.creativedirector`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.socialmediastrategist` | 6.5 | 4.5 | P5 | 1. Q4: Write rubrics content for `video.rubric.socialmediastrategist.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Beats agency social leads on 30-day reach lift<br>3. Q6: Write prompts content for `video.prompt.socialmediastrategist.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.socialmediastrategist`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.copywriter` | 6.5 | 4.5 | P5 | 1. Q4: Write rubrics content for `video.rubric.copywriter.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Wins D&AD-style blind preference on ad briefs<br>3. Q6: Write prompts content for `video.prompt.copywriter.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.copywriter`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.performancemarketer` | 6.5 | 4.5 | P5 | 1. Q4: Write rubrics content for `video.rubric.performancemarketer.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Beats senior media buyer on 30-day ROAS<br>3. Q6: Write prompts content for `video.prompt.performancemarketer.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.performancemarketer`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |

### 7-Edu — Education & Domain-Expert (14 agents, avg 6.46)

**Group tool/harness priorities:**
- fact-check / citation validators
- WCAG / localization checks
- SME HiTL confirm paths

**Group milestone checklist:**
- [ ] All 14 agents complete Universal U1–U10
- [ ] Group mock adapter pack tests green
- [ ] At least 1 multi-agent path inside group using critique bus
- [ ] Human baselines for group lead agents complete
- [ ] Audit: every agent in group maturity 11.0

| Agent | Now | Gap to 11 | Priority band | First 5 actions |
|-------|-----|-----------|---------------|-----------------|
| `video.audiobooknarrator` | 6.5 | 4.5 | P3 | 1. Q4: Write rubrics content for `video.rubric.audiobooknarrator.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Wins AudioFile blind eval at fraction of studio…<br>3. Q6: Write prompts content for `video.prompt.audiobooknarrator.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.audiobooknarrator`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.instructionaldesign` | 6.5 | 4.5 | P6 | 1. Q4: Write rubrics content for `video.rubric.instructionaldesign.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Beats ATD-credentialed ID on retention RCT<br>3. Q6: Write prompts content for `video.prompt.instructionaldesign.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.instructionaldesign`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.sme` | 6.5 | 4.5 | P6 | 1. Q4: Write rubrics content for `video.rubric.sme.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Passes same certification as human pro<br>3. Q6: Write prompts content for `video.prompt.sme.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.sme`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.factchecker` | 6.5 | 4.5 | P6 | 1. Q4: Write rubrics content for `video.rubric.factchecker.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Lower correction rate than Pulitzer-tier outlets<br>3. Q6: Write prompts content for `video.prompt.factchecker.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.factchecker`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.medicalillustrator` | 6.5 | 4.5 | P6 | 1. Q4: Write rubrics content for `video.rubric.medicalillustrator.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: CMI peers vote ≥pass in blind review<br>3. Q6: Write prompts content for `video.prompt.medicalillustrator.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.medicalillustrator`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.journalist` | 6.5 | 4.5 | P6 | 1. Q4: Write rubrics content for `video.rubric.journalist.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Lower correction rate + faster file vs newsroom<br>3. Q6: Write prompts content for `video.prompt.journalist.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.journalist`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.compliance` | 6.5 | 4.5 | P6 | 1. Q4: Write rubrics content for `video.rubric.compliance.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Lower legal-risk than median media-counsel<br>3. Q6: Write prompts content for `video.prompt.compliance.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.compliance`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.finance` | 6.5 | 4.5 | P6 | 1. Q4: Write rubrics content for `video.rubric.finance.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Passes CFA L3; lower retraction rate than analy…<br>3. Q6: Write prompts content for `video.prompt.finance.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.finance`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.foodstylist` | 6.5 | 4.5 | P6 | 1. Q4: Write rubrics content for `video.rubric.foodstylist.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Wins blind preference vs editorial food stylist<br>3. Q6: Write prompts content for `video.prompt.foodstylist.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.foodstylist`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.travelcine` | 6.5 | 4.5 | P6 | 1. Q4: Write rubrics content for `video.rubric.travelcine.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Wins T+L preference at 0.1× sortie cost<br>3. Q6: Write prompts content for `video.prompt.travelcine.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.travelcine`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.childrensauthor` | 6.5 | 4.5 | P6 | 1. Q4: Write rubrics content for `video.rubric.childrensauthor.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Beats Caldecott-rubric predicted score<br>3. Q6: Write prompts content for `video.prompt.childrensauthor.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.childrensauthor`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.signlanguageinterpreter` | 6.5 | 4.5 | P6 | 1. Q4: Write rubrics content for `video.rubric.signlanguageinterpreter.v1` (currently files=…<br>2. Q5: Register surpass protocol for signal: Wins blind NAD-reviewer preference at scale<br>3. Q6: Write prompts content for `video.prompt.signlanguageinterpreter.v1` (currently files=…<br>4. Q7: Create per-agent skills harness directory for `video.signlanguageinterpreter`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.localizationqa` | 6.5 | 4.5 | P6 | 1. Q4: Write rubrics content for `video.rubric.localizationqa.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Beats LSP human QA on MQM at 10× speed<br>3. Q6: Write prompts content for `video.prompt.localizationqa.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.localizationqa`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.realestatephoto` | 6.0 | 5.0 | P6 | 1. Q3: Raise packaged sources from 7 to >=8 substantive files (excerpts + catalog).<br>2. Q4: Write rubrics content for `video.rubric.realestatephoto.v1` (currently files=0).<br>3. Q5: Register surpass protocol for signal: Listing-CTR uplift vs human-shot baseline<br>4. Q6: Write prompts content for `video.prompt.realestatephoto.v1` (currently files=0).<br>5. Q7: Create per-agent skills harness directory for `video.realestatephoto`. |

### 8-AI — AI-Era Specialists (7 agents, avg 6.5)

**Group tool/harness priorities:**
- prompt optimization harness
- avatar/voice-clone adapters with red-team gates
- deepfake / safety scanners

**Group milestone checklist:**
- [ ] All 7 agents complete Universal U1–U10
- [ ] Group mock adapter pack tests green
- [ ] At least 1 multi-agent path inside group using critique bus
- [ ] Human baselines for group lead agents complete
- [ ] Audit: every agent in group maturity 11.0

| Agent | Now | Gap to 11 | Priority band | First 5 actions |
|-------|-----|-----------|---------------|-----------------|
| `video.promptengineer` | 6.5 | 4.5 | P3 | 1. Q4: Write rubrics content for `video.rubric.promptengineer.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Target shot in ≤3 iterations vs human avg 10<br>3. Q6: Write prompts content for `video.prompt.promptengineer.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.promptengineer`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.voiceclone` | 6.5 | 4.5 | P3 | 1. Q4: Write rubrics content for `video.rubric.voiceclone.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Wins blind MOS vs professional ADR<br>3. Q6: Write prompts content for `video.prompt.voiceclone.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.voiceclone`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.avatardesign` | 6.5 | 4.5 | P5 | 1. Q4: Write rubrics content for `video.rubric.avatardesign.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: C2PA-verifiable + Partnership-on-AI full-pass a…<br>3. Q6: Write prompts content for `video.prompt.avatardesign.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.avatardesign`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.aiqaconsistency` | 6.5 | 4.5 | P5 | 1. Q4: Write rubrics content for `video.rubric.aiqaconsistency.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Catches >95% of senior QC catches + 30% missed<br>3. Q6: Write prompts content for `video.prompt.aiqaconsistency.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.aiqaconsistency`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.personalizationengineer` | 6.5 | 4.5 | P5 | 1. Q4: Write rubrics content for `video.rubric.personalizationengineer.v1` (currently files=…<br>2. Q5: Register surpass protocol for signal: Higher share-rate than top human-templated camp…<br>3. Q6: Write prompts content for `video.prompt.personalizationengineer.v1` (currently files=…<br>4. Q7: Create per-agent skills harness directory for `video.personalizationengineer`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.trailereditor` | 6.5 | 4.5 | P5 | 1. Q4: Write rubrics content for `video.rubric.trailereditor.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Wins Golden-Trailer-rubric blind comparison<br>3. Q6: Write prompts content for `video.prompt.trailereditor.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.trailereditor`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.sportsanalyst` | 6.5 | 4.5 | P5 | 1. Q4: Write rubrics content for `video.rubric.sportsanalyst.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Beats ex-athlete on tactical-prediction<br>3. Q6: Write prompts content for `video.prompt.sportsanalyst.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.sportsanalyst`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |

### 9-Meta — Specialist Meta-Agents (28 agents, avg 6.5)

**Group tool/harness priorities:**
- orchestrator graph runtime completeness
- router classification tests
- judge debate harness
- memory retrieve APIs
- critique bus as platform spine

**Group milestone checklist:**
- [ ] All 28 agents complete Universal U1–U10
- [ ] Group mock adapter pack tests green
- [ ] At least 1 multi-agent path inside group using critique bus
- [ ] Human baselines for group lead agents complete
- [ ] Audit: every agent in group maturity 11.0

| Agent | Now | Gap to 11 | Priority band | First 5 actions |
|-------|-----|-----------|---------------|-----------------|
| `video.orchestrator` | 6.5 | 4.5 | P0 | 1. Q4: Write rubrics content for `video.rubric.orchestrator.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Lower TTD than human EP at same scope<br>3. Q6: Write prompts content for `video.prompt.orchestrator.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.orchestrator`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.planner` | 6.5 | 4.5 | P0 | 1. Q4: Write rubrics content for `video.rubric.planner.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Tighter, cheaper plans than EP first pass (blin…<br>3. Q6: Write prompts content for `video.prompt.planner.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.planner`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.router` | 6.5 | 4.5 | P0 | 1. Q4: Write rubrics content for `video.rubric.router.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Beats human producer in agent/vendor selection<br>3. Q6: Write prompts content for `video.prompt.router.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.router`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.judge` | 6.5 | 4.5 | P0 | 1. Q4: Write rubrics content for `video.rubric.judge.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Higher κ than median human juror<br>3. Q6: Write prompts content for `video.prompt.judge.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.judge`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.gatekeeper` | 6.5 | 4.5 | P0 | 1. Q4: Write rubrics content for `video.rubric.gatekeeper.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Lower escaped-defect rate than human QA lead<br>3. Q6: Write prompts content for `video.prompt.gatekeeper.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.gatekeeper`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.memory` | 6.5 | 4.5 | P0 | 1. Q4: Write rubrics content for `video.rubric.memory.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Higher recall than producer's bible at scale<br>3. Q6: Write prompts content for `video.prompt.memory.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.memory`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.ideation` | 6.5 | 4.5 | P1 | 1. Q4: Write rubrics content for `video.rubric.ideation.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Wins agency-pitch shootouts on concept density<br>3. Q6: Write prompts content for `video.prompt.ideation.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.ideation`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.narrativearc` | 6.5 | 4.5 | P1 | 1. Q4: Write rubrics content for `video.rubric.narrativearc.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Beats WGA first drafts on structural rubric<br>3. Q6: Write prompts content for `video.prompt.narrativearc.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.narrativearc`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.styletransfer` | 6.5 | 4.5 | P1 | 1. Q4: Write rubrics content for `video.rubric.styletransfer.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Wins blind preference vs human colorist+grader<br>3. Q6: Write prompts content for `video.prompt.styletransfer.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.styletransfer`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.worldbuilding` | 6.5 | 4.5 | P1 | 1. Q4: Write rubrics content for `video.rubric.worldbuilding.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Lower contradiction rate than writers' bibles a…<br>3. Q6: Write prompts content for `video.prompt.worldbuilding.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.worldbuilding`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.moodboard` | 6.5 | 4.5 | P1 | 1. Q4: Write rubrics content for `video.rubric.moodboard.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Faster + tighter boards than art director (blin…<br>3. Q6: Write prompts content for `video.prompt.moodboard.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.moodboard`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.novelty` | 6.5 | 4.5 | P1 | 1. Q4: Write rubrics content for `video.rubric.novelty.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Catches more clichés than experienced script ed…<br>3. Q6: Write prompts content for `video.prompt.novelty.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.novelty`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.emotionalarc` | 6.5 | 4.5 | P1 | 1. Q4: Write rubrics content for `video.rubric.emotionalarc.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Better retention prediction than NRG test-scree…<br>3. Q6: Write prompts content for `video.prompt.emotionalarc.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.emotionalarc`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.webresearch` | 6.5 | 4.5 | P1 | 1. Q4: Write rubrics content for `video.rubric.webresearch.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Faster + more sources than newsroom researcher<br>3. Q6: Write prompts content for `video.prompt.webresearch.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.webresearch`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.archiveresearch` | 6.5 | 4.5 | P1 | 1. Q4: Write rubrics content for `video.rubric.archiveresearch.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Higher primary-source ratio than doc producer<br>3. Q6: Write prompts content for `video.prompt.archiveresearch.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.archiveresearch`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.trendintelligence` | 6.5 | 4.5 | P1 | 1. Q4: Write rubrics content for `video.rubric.trendintelligence.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Earlier detection than human strategists at hig…<br>3. Q6: Write prompts content for `video.prompt.trendintelligence.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.trendintelligence`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.competitorintelligence` | 6.5 | 4.5 | P1 | 1. Q4: Write rubrics content for `video.rubric.competitorintelligence.v1` (currently files=0…<br>2. Q5: Register surpass protocol for signal: More comprehensive than agency strategy decks<br>3. Q6: Write prompts content for `video.prompt.competitorintelligence.v1` (currently files=0…<br>4. Q7: Create per-agent skills harness directory for `video.competitorintelligence`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.citation` | 6.5 | 4.5 | P1 | 1. Q4: Write rubrics content for `video.rubric.citation.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Lower error rate than newsroom copy desk<br>3. Q6: Write prompts content for `video.prompt.citation.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.citation`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.interviewsynthesis` | 6.5 | 4.5 | P1 | 1. Q4: Write rubrics content for `video.rubric.interviewsynthesis.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Faster + richer theme extraction than qualitati…<br>3. Q6: Write prompts content for `video.prompt.interviewsynthesis.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.interviewsynthesis`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.benchmarkresearch` | 6.5 | 4.5 | P1 | 1. Q4: Write rubrics content for `video.rubric.benchmarkresearch.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Faster + broader than ML-research team<br>3. Q6: Write prompts content for `video.prompt.benchmarkresearch.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.benchmarkresearch`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.promptoptimizer` | 6.5 | 4.5 | P1 | 1. Q4: Write rubrics content for `video.rubric.promptoptimizer.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Beats hand-tuned prompts on held-out briefs<br>3. Q6: Write prompts content for `video.prompt.promptoptimizer.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.promptoptimizer`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.costoptimizer` | 6.5 | 4.5 | P1 | 1. Q4: Write rubrics content for `video.rubric.costoptimizer.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Lower $/quality than human CFO routing<br>3. Q6: Write prompts content for `video.prompt.costoptimizer.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.costoptimizer`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.latencyoptimizer` | 6.5 | 4.5 | P1 | 1. Q4: Write rubrics content for `video.rubric.latencyoptimizer.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Lower p95 than human-tuned pipeline<br>3. Q6: Write prompts content for `video.prompt.latencyoptimizer.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.latencyoptimizer`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.retentionoptimizer` | 6.5 | 4.5 | P1 | 1. Q4: Write rubrics content for `video.rubric.retentionoptimizer.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Beats senior YouTube editor on AVD lift (A/B)<br>3. Q6: Write prompts content for `video.prompt.retentionoptimizer.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.retentionoptimizer`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.roasoptimizer` | 6.5 | 4.5 | P1 | 1. Q4: Write rubrics content for `video.rubric.roasoptimizer.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Beats senior marketer at equal budget<br>3. Q6: Write prompts content for `video.prompt.roasoptimizer.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.roasoptimizer`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.accessibilityoptimizer` | 6.5 | 4.5 | P1 | 1. Q4: Write rubrics content for `video.rubric.accessibilityoptimizer.v1` (currently files=0…<br>2. Q5: Register surpass protocol for signal: Catches more a11y defects than ADA-certified au…<br>3. Q6: Write prompts content for `video.prompt.accessibilityoptimizer.v1` (currently files=0…<br>4. Q7: Create per-agent skills harness directory for `video.accessibilityoptimizer`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.evaluationharness` | 6.5 | 4.5 | P1 | 1. Q4: Write rubrics content for `video.rubric.evaluationharness.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Catches regressions faster than ML-eng rotation<br>3. Q6: Write prompts content for `video.prompt.evaluationharness.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.evaluationharness`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.safetyredteam` | 6.5 | 4.5 | P1 | 1. Q4: Write rubrics content for `video.rubric.safetyredteam.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Higher coverage than internal red-team rotation<br>3. Q6: Write prompts content for `video.prompt.safetyredteam.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.safetyredteam`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |

### 10-Sup — Workflow Support (34 agents, avg 6.37)

**Group tool/harness priorities:**
- support SLAs + data contracts
- analytics event schemas
- archive / distribution packaging tools

**Group milestone checklist:**
- [ ] All 34 agents complete Universal U1–U10
- [ ] Group mock adapter pack tests green
- [ ] At least 1 multi-agent path inside group using critique bus
- [ ] Human baselines for group lead agents complete
- [ ] Audit: every agent in group maturity 11.0

| Agent | Now | Gap to 11 | Priority band | First 5 actions |
|-------|-----|-----------|---------------|-----------------|
| `video.critic` | 6.5 | 4.5 | P0 | 1. Q4: Write rubrics content for `video.rubric.critic.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Provides broader qualitative coverage than ad h…<br>3. Q6: Write prompts content for `video.prompt.critic.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.critic`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.archiveproducer` | 6.0 | 5.0 | P3 | 1. Q3: Raise packaged sources from 7 to >=8 substantive files (excerpts + catalog).<br>2. Q4: Write rubrics content for `video.rubric.archiveproducer.v1` (currently files=0).<br>3. Q5: Register surpass protocol for signal: Assembles reusable archival packages more clean…<br>4. Q6: Write prompts content for `video.prompt.archiveproducer.v1` (currently files=0).<br>5. Q7: Create per-agent skills harness directory for `video.archiveproducer`. |
| `video.analyst` | 6.5 | 4.5 | P6 | 1. Q4: Write rubrics content for `video.rubric.analyst.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Detects actionable performance shifts faster th…<br>3. Q6: Write prompts content for `video.prompt.analyst.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.analyst`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.audiencesim` | 6.5 | 4.5 | P6 | 1. Q4: Write rubrics content for `video.rubric.audiencesim.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Predicts audience reaction earlier than convent…<br>3. Q6: Write prompts content for `video.prompt.audiencesim.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.audiencesim`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.accessibility` | 6.5 | 4.5 | P6 | 1. Q4: Write rubrics content for `video.rubric.accessibility.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Finds release-blocking accessibility issues bef…<br>3. Q6: Write prompts content for `video.prompt.accessibility.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.accessibility`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.brand` | 6.5 | 4.5 | P6 | 1. Q4: Write rubrics content for `video.rubric.brand.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Holds cross-channel brand consistency better th…<br>3. Q6: Write prompts content for `video.prompt.brand.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.brand`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.brandstrategist` | 6.5 | 4.5 | P6 | 1. Q4: Write rubrics content for `video.rubric.brandstrategist.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Produces clearer brand-to-script translation th…<br>3. Q6: Write prompts content for `video.prompt.brandstrategist.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.brandstrategist`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.marketing` | 6.5 | 4.5 | P6 | 1. Q4: Write rubrics content for `video.rubric.marketing.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Ships multi-channel launch packages faster than…<br>3. Q6: Write prompts content for `video.prompt.marketing.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.marketing`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.seo` | 6.5 | 4.5 | P6 | 1. Q4: Write rubrics content for `video.rubric.seo.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Lifts discoverability faster than manual metada…<br>3. Q6: Write prompts content for `video.prompt.seo.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.seo`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.community` | 6.5 | 4.5 | P6 | 1. Q4: Write rubrics content for `video.rubric.community.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Surfaces emerging audience concerns earlier tha…<br>3. Q6: Write prompts content for `video.prompt.community.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.community`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.templatedesign` | 6.5 | 4.5 | P6 | 1. Q4: Write rubrics content for `video.rubric.templatedesign.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Produces reusable templates with fewer breakage…<br>3. Q6: Write prompts content for `video.prompt.templatedesign.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.templatedesign`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.ux` | 6.0 | 5.0 | P6 | 1. Q3: Raise packaged sources from 6 to >=8 substantive files (excerpts + catalog).<br>2. Q4: Write rubrics content for `video.rubric.ux.v1` (currently files=0).<br>3. Q5: Register surpass protocol for signal: Flags user confusion earlier than launch-stage …<br>4. Q6: Write prompts content for `video.prompt.ux.v1` (currently files=0).<br>5. Q7: Create per-agent skills harness directory for `video.ux`. |
| `video.trustsafety` | 6.5 | 4.5 | P6 | 1. Q4: Write rubrics content for `video.rubric.trustsafety.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Catches misuse risk earlier than generic modera…<br>3. Q6: Write prompts content for `video.prompt.trustsafety.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.trustsafety`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.crm` | 6.5 | 4.5 | P6 | 1. Q4: Write rubrics content for `video.rubric.crm.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Executes segmentation-to-delivery flow faster t…<br>3. Q6: Write prompts content for `video.prompt.crm.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.crm`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.legal` | 6.5 | 4.5 | P6 | 1. Q4: Write rubrics content for `video.rubric.legal.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Reduces late-stage legal surprises relative to …<br>3. Q6: Write prompts content for `video.prompt.legal.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.legal`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.festivalstrategist` | 6.0 | 5.0 | P6 | 1. Q3: Raise packaged sources from 7 to >=8 substantive files (excerpts + catalog).<br>2. Q4: Write rubrics content for `video.rubric.festivalstrategist.v1` (currently files=0).<br>3. Q5: Register surpass protocol for signal: Improves submission targeting versus generic re…<br>4. Q6: Write prompts content for `video.prompt.festivalstrategist.v1` (currently files=0).<br>5. Q7: Create per-agent skills harness directory for `video.festivalstrategist`. |
| `video.lms` | 6.5 | 4.5 | P6 | 1. Q4: Write rubrics content for `video.rubric.lms.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Ships publishable learning packages faster than…<br>3. Q6: Write prompts content for `video.prompt.lms.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.lms`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.learnersim` | 6.5 | 4.5 | P6 | 1. Q4: Write rubrics content for `video.rubric.learnersim.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Predicts weak spots before live learner complai…<br>3. Q6: Write prompts content for `video.prompt.learnersim.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.learnersim`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.continuity` | 6.5 | 4.5 | P6 | 1. Q4: Write rubrics content for `video.rubric.continuity.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Catches continuity breaks earlier than end-of-p…<br>3. Q6: Write prompts content for `video.prompt.continuity.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.continuity`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.lipsync` | 6.5 | 4.5 | P6 | 1. Q4: Write rubrics content for `video.rubric.lipsync.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Finds sync drift more precisely than general QC…<br>3. Q6: Write prompts content for `video.prompt.lipsync.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.lipsync`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.musicsupervisor` | 6.0 | 5.0 | P6 | 1. Q3: Raise packaged sources from 7 to >=8 substantive files (excerpts + catalog).<br>2. Q4: Write rubrics content for `video.rubric.musicsupervisor.v1` (currently files=0).<br>3. Q5: Register surpass protocol for signal: Coordinates music placements more consistently …<br>4. Q6: Write prompts content for `video.prompt.musicsupervisor.v1` (currently files=0).<br>5. Q7: Create per-agent skills harness directory for `video.musicsupervisor`. |
| `video.labela_r` | 6.0 | 5.0 | P6 | 1. Q3: Raise packaged sources from 7 to >=8 substantive files (excerpts + catalog).<br>2. Q4: Write rubrics content for `video.rubric.labela_r.v1` (currently files=0).<br>3. Q5: Register surpass protocol for signal: Aligns music creative faster than disconnected …<br>4. Q6: Write prompts content for `video.prompt.labela_r.v1` (currently files=0).<br>5. Q7: Create per-agent skills harness directory for `video.labela_r`. |
| `video.labeldigital` | 6.0 | 5.0 | P6 | 1. Q3: Raise packaged sources from 7 to >=8 substantive files (excerpts + catalog).<br>2. Q4: Write rubrics content for `video.rubric.labeldigital.v1` (currently files=0).<br>3. Q5: Register surpass protocol for signal: Delivers cleaner label-side packages than ad ho…<br>4. Q6: Write prompts content for `video.prompt.labeldigital.v1` (currently files=0).<br>5. Q7: Create per-agent skills harness directory for `video.labeldigital`. |
| `video.deepfakedetection` | 6.5 | 4.5 | P6 | 1. Q4: Write rubrics content for `video.rubric.deepfakedetection.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Catches deceptive synthetic markers that generi…<br>3. Q6: Write prompts content for `video.prompt.deepfakedetection.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.deepfakedetection`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.comms` | 6.5 | 4.5 | P6 | 1. Q4: Write rubrics content for `video.rubric.comms.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Produces faster aligned responses than fragment…<br>3. Q6: Write prompts content for `video.prompt.comms.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.comms`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.standardseditor` | 6.5 | 4.5 | P6 | 1. Q4: Write rubrics content for `video.rubric.standardseditor.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Reduces standards drift better than late-stage …<br>3. Q6: Write prompts content for `video.prompt.standardseditor.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.standardseditor`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.ethics` | 6.5 | 4.5 | P6 | 1. Q4: Write rubrics content for `video.rubric.ethics.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Surfaces release risks earlier than reactive et…<br>3. Q6: Write prompts content for `video.prompt.ethics.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.ethics`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.channelmanager` | 6.0 | 5.0 | P6 | 1. Q3: Raise packaged sources from 7 to >=8 substantive files (excerpts + catalog).<br>2. Q4: Write rubrics content for `video.rubric.channelmanager.v1` (currently files=0).<br>3. Q5: Register surpass protocol for signal: Improves publishing discipline over manual chan…<br>4. Q6: Write prompts content for `video.prompt.channelmanager.v1` (currently files=0).<br>5. Q7: Create per-agent skills harness directory for `video.channelmanager`. |
| `video.corrections` | 6.5 | 4.5 | P6 | 1. Q4: Write rubrics content for `video.rubric.corrections.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Resolves post-release issues faster than unstru…<br>3. Q6: Write prompts content for `video.prompt.corrections.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.corrections`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.mpa` | 6.5 | 4.5 | P6 | 1. Q4: Write rubrics content for `video.rubric.mpa.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Prepares cleaner feature-release classification…<br>3. Q6: Write prompts content for `video.prompt.mpa.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.mpa`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.sales` | 6.5 | 4.5 | P6 | 1. Q4: Write rubrics content for `video.rubric.sales.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Produces sales-ready release packets faster tha…<br>3. Q6: Write prompts content for `video.prompt.sales.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.sales`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.distributor` | 6.5 | 4.5 | P6 | 1. Q4: Write rubrics content for `video.rubric.distributor.v1` (currently files=0).<br>2. Q5: Register surpass protocol for signal: Reduces delivery-spec mismatches relative to fr…<br>3. Q6: Write prompts content for `video.prompt.distributor.v1` (currently files=0).<br>4. Q7: Create per-agent skills harness directory for `video.distributor`.<br>5. Q8: Keep max_refinement_count and document policy in SPEC. |
| `video.awardsstrategist` | 6.0 | 5.0 | P6 | 1. Q3: Raise packaged sources from 6 to >=8 substantive files (excerpts + catalog).<br>2. Q4: Write rubrics content for `video.rubric.awardsstrategist.v1` (currently files=0).<br>3. Q5: Register surpass protocol for signal: Improves awards-timing discipline over generic …<br>4. Q6: Write prompts content for `video.prompt.awardsstrategist.v1` (currently files=0).<br>5. Q7: Create per-agent skills harness directory for `video.awardsstrategist`. |
| `video.archivemaster` | 6.0 | 5.0 | P6 | 1. Q3: Raise packaged sources from 7 to >=8 substantive files (excerpts + catalog).<br>2. Q4: Write rubrics content for `video.rubric.archivemaster.v1` (currently files=0).<br>3. Q5: Register surpass protocol for signal: Delivers more reliable archive packages than la…<br>4. Q6: Write prompts content for `video.prompt.archivemaster.v1` (currently files=0).<br>5. Q7: Create per-agent skills harness directory for `video.archivemaster`. |

---

## 6. Per-agent full-mark action lists

Each agent section lists **all actions required for 11/11 YES**, ordered by question. Complete every checkbox.

### `video.orchestrator` — OrchestratorAgent (now 6.5/11 → target 11.0)

- **Category:** `9-Meta` · **VA#:** 53 · **Priority band:** P0
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.orchestrator.v1` / `video.rubric.orchestrator.v1`
- **Tools now:** `media.stub` · live_media=False
- **Sources now:** 21 files · provenance=True
- **Design responsibility:** Runs CrewAI/AutoGen/LangGraph DAG; retries, timeouts, fan-out/fan-in
- **Design knowledge sources:** LangGraph + CrewAI + AutoGen patterns; Airflow/Temporal; PGA schedule templates
- **Design self-quality:** DAG completion ≥99.5%; SLA adherence; deadlock = 0
- **Design surpass signal:** Lower TTD than human EP at same scope
- **Design tools:** LangGraph state machine; Temporal workflow engine; Redis (distributed locks); observability (LangSmith)
- **Design architecture:** Agentic Graph (LangGraph) — deterministic DAG execution
- **Design accepts critique from:** ProducerAgent (scope), JudgeAgent (dispute), HiTL on stall
- **Design comments on:** All agents (resource burn, retry storms)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.orchestrator.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Lower TTD than human EP at same scope
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.orchestrator.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Agentic Graph (LangGraph) — deterministic DAG execution

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.orchestrator`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`ProducerAgent (scope), JudgeAgent (dispute), HiTL on stall`; comments_on=`All agents (resource burn, retry storms)`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.orchestrator` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.orchestrator` shows maturity 11.0 and 11 YES

### `video.planner` — PlannerAgent (now 6.5/11 → target 11.0)

- **Category:** `9-Meta` · **VA#:** 54 · **Priority band:** P0
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.planner.v1` / `video.rubric.planner.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 24 files · provenance=True
- **Design responsibility:** Decomposes brief into phased DAG with assignments + critic gates
- **Design knowledge sources:** PMBOK; CrewAI task graphs; phase templates
- **Design self-quality:** Plan validity (no missing gate); cost variance <10%
- **Design surpass signal:** Tighter, cheaper plans than EP first pass (blind A/B)
- **Design tools:** LangGraph plan-gen; cost-estimation models; Gantt/PERT tools
- **Design architecture:** ReAct (decompose → estimate → validate → emit DAG)
- **Design accepts critique from:** ProducerAgent, FinanceAgent (budget)
- **Design comments on:** RouterAgent (wrong pick), OrchestratorAgent

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.planner.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Tighter, cheaper plans than EP first pass (blind A/B)
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.planner.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: ReAct (decompose → estimate → validate → emit DAG)

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.planner`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`ProducerAgent, FinanceAgent (budget)`; comments_on=`RouterAgent (wrong pick), OrchestratorAgent`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.planner` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.planner` shows maturity 11.0 and 11 YES

### `video.router` — RouterAgent (now 6.5/11 → target 11.0)

- **Category:** `9-Meta` · **VA#:** 55 · **Priority band:** P0
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.router.v1` / `video.rubric.router.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 22 files · provenance=True
- **Design responsibility:** Picks right specialist agent (and model) for each subtask
- **Design knowledge sources:** Agent-capability registry; benchmark history (cost/quality/latency)
- **Design self-quality:** Routing accuracy ≥95% vs oracle; cost within budget
- **Design surpass signal:** Beats human producer in agent/vendor selection
- **Design tools:** Agent registry DB; benchmark leaderboard cache; pricing APIs
- **Design architecture:** Classifier + ReAct (match task embedding → agent capability)
- **Design accepts critique from:** OrchestratorAgent, CostOptimizerAgent
- **Design comments on:** PlannerAgent (bad decomposition)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.router.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Beats human producer in agent/vendor selection
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.router.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Classifier + ReAct (match task embedding → agent capability)

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.router`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`OrchestratorAgent, CostOptimizerAgent`; comments_on=`PlannerAgent (bad decomposition)`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.router` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.router` shows maturity 11.0 and 11 YES

### `video.judge` — JudgeAgent (now 6.5/11 → target 11.0)

- **Category:** `9-Meta` · **VA#:** 56 · **Priority band:** P0
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.judge.v1` / `video.rubric.judge.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 23 files · provenance=True
- **Design responsibility:** Adjudicates disputes via multi-agent debate; scores against rubric
- **Design knowledge sources:** Du 2023 (LLM debate); MT-Bench rubrics; guild scoring sheets
- **Design self-quality:** Inter-rater κ vs expert panel ≥0.8
- **Design surpass signal:** Higher κ than median human juror
- **Design tools:** MT-Bench/Arena evaluation harness; rubric template engine
- **Design architecture:** Multi-agent debate (Du 2023) + LLM-as-Judge (Zheng 2023)
- **Design accepts critique from:** HiTL on overturned rulings
- **Design comments on:** DirectorAgent, ScreenwriterAgent, any disputing pair

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.judge.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Higher κ than median human juror
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.judge.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Multi-agent debate (Du 2023) + LLM-as-Judge (Zheng 2023)

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.judge`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`HiTL on overturned rulings`; comments_on=`DirectorAgent, ScreenwriterAgent, any disputing pair`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.judge` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.judge` shows maturity 11.0 and 11 YES

### `video.gatekeeper` — GateKeeperAgent (now 6.5/11 → target 11.0)

- **Category:** `9-Meta` · **VA#:** 57 · **Priority band:** P0
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.gatekeeper.v1` / `video.rubric.gatekeeper.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 15 files · provenance=True
- **Design responsibility:** Phase transitions; verifies L1/L2/L3 criteria; signs C2PA
- **Design knowledge sources:** Stage-gate methodology; PGA Producers Mark; QMS audit
- **Design self-quality:** Zero leaked defects; sign-off SLA ≥99%
- **Design surpass signal:** Lower escaped-defect rate than human QA lead
- **Design tools:** C2PA signing (c2patool); JSON schema validators; rubric evaluation endpoints
- **Design architecture:** Constitutional AI (constitution = phase-gate criteria)
- **Design accepts critique from:** ComplianceAgent, AIQAConsistencyAgent
- **Design comments on:** OrchestratorAgent (premature advance)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.gatekeeper.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Lower escaped-defect rate than human QA lead
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.gatekeeper.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Constitutional AI (constitution = phase-gate criteria)

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.gatekeeper`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`ComplianceAgent, AIQAConsistencyAgent`; comments_on=`OrchestratorAgent (premature advance)`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.gatekeeper` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.gatekeeper` shows maturity 11.0 and 11 YES

### `video.memory` — MemoryAgent (now 6.5/11 → target 11.0)

- **Category:** `9-Meta` · **VA#:** 58 · **Priority band:** P0
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.memory.v1` / `video.rubric.memory.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 28 files · provenance=True
- **Design responsibility:** Episodic + long-term project memory; retrieval for any agent
- **Design knowledge sources:** Reflexion (Shinn 2023); MemGPT; vector-DB best practices
- **Design self-quality:** Retrieval precision@5 ≥0.9; freshness SLA
- **Design surpass signal:** Higher recall than producer's bible at scale
- **Design tools:** Pinecone/Weaviate/Qdrant vector DB; MemGPT-style hierarchical memory; embedding models
- **Design architecture:** Reflexion memory architecture (MemGPT extension)
- **Design accepts critique from:** All agents (correction events)
- **Design comments on:** All agents (stale facts)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.memory.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Higher recall than producer's bible at scale
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.memory.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Reflexion memory architecture (MemGPT extension)

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.memory`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`All agents (correction events)`; comments_on=`All agents (stale facts)`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.memory` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.memory` shows maturity 11.0 and 11 YES

### `video.critic` — CriticAgent (now 6.5/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 95 · **Priority band:** P0
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.critic.v1` / `video.rubric.critic.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 25 files · provenance=True
- **Design responsibility:** Simulates reviewer, press, or jury interpretation
- **Design knowledge sources:** Criticism corpora, festival-jury commentary, review archives
- **Design self-quality:** Interpretive depth, consistency, reviewer-mode diversity
- **Design surpass signal:** Provides broader qualitative coverage than ad hoc internal taste review
- **Design tools:** Review corpora, jury rubrics, qualitative scoring tools
- **Design architecture:** Multi-agent debate as critic panel
- **Design accepts critique from:** DirectorAgent, AudienceSimAgent, FestivalStrategistAgent, JudgeAgent
- **Design comments on:** Auteur read, tone mismatch, festival/press vulnerability

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.critic.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Provides broader qualitative coverage than ad hoc internal taste review
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.critic.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Multi-agent debate as critic panel

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.critic`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`DirectorAgent, AudienceSimAgent, FestivalStrategistAgent, JudgeAgent`; comments_on=`Auteur read, tone mismatch, festival/press vulnerability`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.critic` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.critic` shows maturity 11.0 and 11 YES

### `video.ideation` — IdeationAgent (now 6.5/11 → target 11.0)

- **Category:** `9-Meta` · **VA#:** 59 · **Priority band:** P1
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.ideation.v1` / `video.rubric.ideation.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 16 files · provenance=True
- **Design responsibility:** Divergent brainstorm of concepts, hooks, taglines
- **Design knowledge sources:** Cannes Grand Prix; D&AD; IDEO design-thinking; SCAMPER/de Bono
- **Design self-quality:** Idea-count; novelty (embedding distance); semantic diversity
- **Design surpass signal:** Wins agency-pitch shootouts on concept density
- **Design tools:** Embedding novelty scorer; concept clustering (UMAP); Are.na/Pinterest search
- **Design architecture:** Self-Refine + NoveltyAgent as critic
- **Design accepts critique from:** CreativeDirectorAgent, NoveltyAgent
- **Design comments on:** CopywriterAgent (derivative), DirectorAgent (unfilmable)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.ideation.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Wins agency-pitch shootouts on concept density
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.ideation.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Self-Refine + NoveltyAgent as critic

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.ideation`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`CreativeDirectorAgent, NoveltyAgent`; comments_on=`CopywriterAgent (derivative), DirectorAgent (unfilmable)`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.ideation` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.ideation` shows maturity 11.0 and 11 YES

### `video.narrativearc` — NarrativeArcAgent (now 6.5/11 → target 11.0)

- **Category:** `9-Meta` · **VA#:** 60 · **Priority band:** P1
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.narrativearc.v1` / `video.rubric.narrativearc.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 13 files · provenance=True
- **Design responsibility:** 3-act / Save-the-Cat / Hero's Journey structure
- **Design knowledge sources:** Campbell; Snyder *Save the Cat*; Truby; Black List analyses
- **Design self-quality:** Beat-sheet coverage 100%; turning-point spacing; arc curve fit
- **Design surpass signal:** Beats WGA first drafts on structural rubric
- **Design tools:** Beat-sheet validator; emotional-arc plotter; structure templates
- **Design architecture:** Self-Refine (rubric: beat-sheet completeness)
- **Design accepts critique from:** ScreenwriterAgent, DirectorAgent
- **Design comments on:** ScreenwriterAgent (sagging middle)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.narrativearc.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Beats WGA first drafts on structural rubric
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.narrativearc.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Self-Refine (rubric: beat-sheet completeness)

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.narrativearc`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`ScreenwriterAgent, DirectorAgent`; comments_on=`ScreenwriterAgent (sagging middle)`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.narrativearc` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.narrativearc` shows maturity 11.0 and 11 YES

### `video.styletransfer` — StyleTransferAgent (now 6.5/11 → target 11.0)

- **Category:** `9-Meta` · **VA#:** 61 · **Priority band:** P1
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.styletransfer.v1` / `video.rubric.styletransfer.v1`
- **Tools now:** `media.stub, media.runway, media.veo` · live_media=True
- **Sources now:** 13 files · provenance=True
- **Design responsibility:** Applies named aesthetic consistently across shots
- **Design knowledge sources:** Curated style corpora; LoRA/seed registries; reference-frame banks
- **Design self-quality:** Style-similarity (CLIP/DINO) ≥0.85; cross-shot variance ≤τ
- **Design surpass signal:** Wins blind preference vs human colorist+grader
- **Design tools:** LoRA weights per style; CLIP/DINO similarity scorer; Runway style-lock mode; ComfyUI
- **Design architecture:** Self-Refine (CLIP style score as feedback)
- **Design accepts critique from:** DirectorAgent, ColoristAgent
- **Design comments on:** GeneratorAgent (off-style)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.styletransfer.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Wins blind preference vs human colorist+grader
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.styletransfer.v1` (currently files=0).
- [ ] Keep live media tools fail-closed; add mock-mode golden path tests without network.
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Self-Refine (CLIP style score as feedback)

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.styletransfer`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`DirectorAgent, ColoristAgent`; comments_on=`GeneratorAgent (off-style)`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.styletransfer` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.styletransfer` shows maturity 11.0 and 11 YES

### `video.worldbuilding` — WorldBuildingAgent (now 6.5/11 → target 11.0)

- **Category:** `9-Meta` · **VA#:** 62 · **Priority band:** P1
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.worldbuilding.v1` / `video.rubric.worldbuilding.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 12 files · provenance=True
- **Design responsibility:** Lore, rules, geography, factions, magic/tech systems
- **Design knowledge sources:** Tolkien; *Worldbuilding* (Adams); fan-wikis; series-bible leaks
- **Design self-quality:** Internal-consistency (no contradictions); rule-completeness
- **Design surpass signal:** Lower contradiction rate than writers' bibles at 10× volume
- **Design tools:** Long-context LLM (Gemini 2.5 Pro); contradiction-detection model; wiki-graph DB
- **Design architecture:** Reflexion (contradiction corrections → episodic memory)
- **Design accepts critique from:** ShowrunnerAgent, FactCheckerAgent
- **Design comments on:** ScreenwriterAgent (lore break), ConceptArtistAgent

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.worldbuilding.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Lower contradiction rate than writers' bibles at 10× volume
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.worldbuilding.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Reflexion (contradiction corrections → episodic memory)

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.worldbuilding`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`ShowrunnerAgent, FactCheckerAgent`; comments_on=`ScreenwriterAgent (lore break), ConceptArtistAgent`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.worldbuilding` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.worldbuilding` shows maturity 11.0 and 11 YES

### `video.moodboard` — MoodBoardAgent (now 6.5/11 → target 11.0)

- **Category:** `9-Meta` · **VA#:** 63 · **Priority band:** P1
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.moodboard.v1` / `video.rubric.moodboard.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 13 files · provenance=True
- **Design responsibility:** Reference boards: visual, sonic, tonal
- **Design knowledge sources:** Pinterest/Are.na; lookbook archives; Spotify-Canvas
- **Design self-quality:** Reference coherence (cluster tightness); brief alignment
- **Design surpass signal:** Faster + tighter boards than art director (blind A/B)
- **Design tools:** Pinterest/Are.na APIs; Spotify Canvas; CLIP clustering; Figma board generation
- **Design architecture:** ReAct (search → cluster → layout → validate coherence)
- **Design accepts critique from:** DirectorAgent, ProductionDesignAgent
- **Design comments on:** ConceptArtistAgent (off-mood)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.moodboard.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Faster + tighter boards than art director (blind A/B)
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.moodboard.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: ReAct (search → cluster → layout → validate coherence)

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.moodboard`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`DirectorAgent, ProductionDesignAgent`; comments_on=`ConceptArtistAgent (off-mood)`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.moodboard` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.moodboard` shows maturity 11.0 and 11 YES

### `video.novelty` — NoveltyAgent / Anti-Cliché Critic (now 6.5/11 → target 11.0)

- **Category:** `9-Meta` · **VA#:** 64 · **Priority band:** P1
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.novelty.v1` / `video.rubric.novelty.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 13 files · provenance=True
- **Design responsibility:** Flags tropes, clichés, over-fit outputs
- **Design knowledge sources:** TV Tropes; OpenSubtitles n-gram freq; corpus-novelty embeddings
- **Design self-quality:** Cliché-hit count; novelty score vs category prior
- **Design surpass signal:** Catches more clichés than experienced script editor
- **Design tools:** TV Tropes scraper; n-gram frequency DB; embedding novelty scorer
- **Design architecture:** LLM-as-Judge (anti-cliché constitution)
- **Design accepts critique from:** IdeationAgent, ScreenwriterAgent
- **Design comments on:** ScreenwriterAgent (trope-stuffed), CopywriterAgent (templated)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.novelty.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Catches more clichés than experienced script editor
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.novelty.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: LLM-as-Judge (anti-cliché constitution)

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.novelty`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`IdeationAgent, ScreenwriterAgent`; comments_on=`ScreenwriterAgent (trope-stuffed), CopywriterAgent (templated)`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.novelty` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.novelty` shows maturity 11.0 and 11 YES

### `video.emotionalarc` — EmotionalArcAgent (now 6.5/11 → target 11.0)

- **Category:** `9-Meta` · **VA#:** 65 · **Priority band:** P1
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.emotionalarc.v1` / `video.rubric.emotionalarc.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 12 files · provenance=True
- **Design responsibility:** Maps valence/arousal curve; suggests beats
- **Design knowledge sources:** Plutchik; affective-computing corpora; Cron *Story Genius*
- **Design self-quality:** Curve-fit to target; biosignal-proxy regression accuracy
- **Design surpass signal:** Better retention prediction than NRG test-screening cards
- **Design tools:** Sentiment/emotion classifiers (GoEmotions); retention-curve predictor; biosignal proxy model
- **Design architecture:** Self-Refine (emotional-arc curve as rubric target)
- **Design accepts critique from:** DirectorAgent, EditorAgent, ComposerAgent
- **Design comments on:** EditorAgent (flat middle), ComposerAgent (cue mismatch)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.emotionalarc.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Better retention prediction than NRG test-screening cards
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.emotionalarc.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Self-Refine (emotional-arc curve as rubric target)

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.emotionalarc`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`DirectorAgent, EditorAgent, ComposerAgent`; comments_on=`EditorAgent (flat middle), ComposerAgent (cue mismatch)`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.emotionalarc` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.emotionalarc` shows maturity 11.0 and 11 YES

### `video.webresearch` — WebResearchAgent (now 6.5/11 → target 11.0)

- **Category:** `9-Meta` · **VA#:** 66 · **Priority band:** P1
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.webresearch.v1` / `video.rubric.webresearch.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 11 files · provenance=True
- **Design responsibility:** Live web search, source ranking, citation extraction
- **Design knowledge sources:** Bing/Google/Brave APIs; Common Crawl; Perplexity patterns
- **Design self-quality:** Source-grade per claim; citation precision; recency hit
- **Design surpass signal:** Faster + more sources than newsroom researcher
- **Design tools:** Brave/Google Search API; Jina Reader (web→markdown); source-quality classifier
- **Design architecture:** ReAct (query → fetch → extract → grade → cite)
- **Design accepts critique from:** FactCheckerAgent, CitationAgent
- **Design comments on:** ScriptwriterAgent (uncited claim)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.webresearch.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Faster + more sources than newsroom researcher
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.webresearch.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: ReAct (query → fetch → extract → grade → cite)

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.webresearch`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`FactCheckerAgent, CitationAgent`; comments_on=`ScriptwriterAgent (uncited claim)`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.webresearch` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.webresearch` shows maturity 11.0 and 11 YES

### `video.archiveresearch` — ArchiveResearchAgent (now 6.5/11 → target 11.0)

- **Category:** `9-Meta` · **VA#:** 67 · **Priority band:** P1
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.archiveresearch.v1` / `video.rubric.archiveresearch.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 11 files · provenance=True
- **Design responsibility:** Historical / academic / archival deep search
- **Design knowledge sources:** JSTOR, arXiv, PubMed, AP Archive, Getty, FOIA
- **Design self-quality:** Primary-source ratio; archive-coverage breadth
- **Design surpass signal:** Higher primary-source ratio than doc producer
- **Design tools:** JSTOR/arXiv/PubMed APIs; Getty Images API; FOIA request tools; OCR (Tesseract)
- **Design architecture:** ReAct (formulate query → search archive → extract → grade source)
- **Design accepts critique from:** FactCheckerAgent, SMEAgent
- **Design comments on:** ScriptwriterAgent (secondary-source reliance)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.archiveresearch.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Higher primary-source ratio than doc producer
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.archiveresearch.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: ReAct (formulate query → search archive → extract → grade source)

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.archiveresearch`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`FactCheckerAgent, SMEAgent`; comments_on=`ScriptwriterAgent (secondary-source reliance)`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.archiveresearch` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.archiveresearch` shows maturity 11.0 and 11 YES

### `video.trendintelligence` — TrendIntelligenceAgent (now 6.5/11 → target 11.0)

- **Category:** `9-Meta` · **VA#:** 68 · **Priority band:** P1
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.trendintelligence.v1` / `video.rubric.trendintelligence.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 10 files · provenance=True
- **Design responsibility:** Detects emerging memes, sounds, formats
- **Design knowledge sources:** TikTok Creative Center; Trendpop; Tubular; Reddit/X firehose
- **Design self-quality:** Prediction lead time vs peak; precision/recall on trend list
- **Design surpass signal:** Earlier detection than human strategists at higher precision
- **Design tools:** TikTok Creative Center API; Reddit/X streaming APIs; Sensor Tower; Google Trends
- **Design architecture:** ReAct + time-series anomaly detection
- **Design accepts critique from:** SocialStrategistAgent, CopywriterAgent
- **Design comments on:** IdeationAgent (off-trend)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.trendintelligence.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Earlier detection than human strategists at higher precision
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.trendintelligence.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: ReAct + time-series anomaly detection

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.trendintelligence`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`SocialStrategistAgent, CopywriterAgent`; comments_on=`IdeationAgent (off-trend)`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.trendintelligence` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.trendintelligence` shows maturity 11.0 and 11 YES

### `video.competitorintelligence` — CompetitorIntelligenceAgent (now 6.5/11 → target 11.0)

- **Category:** `9-Meta` · **VA#:** 69 · **Priority band:** P1
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.competitorintelligence.v1` / `video.rubric.competitorintelligence.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 9 files · provenance=True
- **Design responsibility:** What competitors are shipping
- **Design knowledge sources:** Meta Ad Library; TikTok Top Ads; YouTube scrape; release trackers
- **Design self-quality:** Coverage % of competitor set; our-novelty vs landscape
- **Design surpass signal:** More comprehensive than agency strategy decks
- **Design tools:** Meta Ad Library API; TikTok Top Ads; SimilarWeb; YouTube Data API v3
- **Design architecture:** ReAct (scrape competitor → classify → report gaps)
- **Design accepts critique from:** BrandAgent, CreativeDirectorAgent
- **Design comments on:** IdeationAgent (derivative)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.competitorintelligence.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: More comprehensive than agency strategy decks
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.competitorintelligence.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: ReAct (scrape competitor → classify → report gaps)

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.competitorintelligence`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`BrandAgent, CreativeDirectorAgent`; comments_on=`IdeationAgent (derivative)`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.competitorintelligence` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.competitorintelligence` shows maturity 11.0 and 11 YES

### `video.citation` — CitationAgent (now 6.5/11 → target 11.0)

- **Category:** `9-Meta` · **VA#:** 70 · **Priority band:** P1
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.citation.v1` / `video.rubric.citation.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 17 files · provenance=True
- **Design responsibility:** Normalizes sources; grades primary/secondary/tertiary
- **Design knowledge sources:** Chicago, APA, AP style; SPJ grading; CRAAP test
- **Design self-quality:** Citation format 100% valid; primary % ≥target
- **Design surpass signal:** Lower error rate than newsroom copy desk
- **Design tools:** Citation parsers (AnyStyle); DOI resolver; CRAAP scoring model
- **Design architecture:** Self-Refine (format validator + source grader as rubric)
- **Design accepts critique from:** FactCheckerAgent, JournalistAgent
- **Design comments on:** WebResearchAgent (weak source)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.citation.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Lower error rate than newsroom copy desk
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.citation.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Self-Refine (format validator + source grader as rubric)

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.citation`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`FactCheckerAgent, JournalistAgent`; comments_on=`WebResearchAgent (weak source)`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.citation` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.citation` shows maturity 11.0 and 11 YES

### `video.interviewsynthesis` — InterviewSynthesisAgent (now 6.5/11 → target 11.0)

- **Category:** `9-Meta` · **VA#:** 71 · **Priority band:** P1
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.interviewsynthesis.v1` / `video.rubric.interviewsynthesis.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 11 files · provenance=True
- **Design responsibility:** Synthesizes practitioner interviews into data
- **Design knowledge sources:** Otter/Rev transcripts; consent forms; SAG/WGA templates
- **Design self-quality:** Inter-coder agreement on themes; consent integrity
- **Design surpass signal:** Faster + richer theme extraction than qualitative researcher
- **Design tools:** Otter.ai/Rev API (transcription); thematic coding models; consent-management DB
- **Design architecture:** Reflexion (interviewer refines questions based on theme gaps)
- **Design accepts critique from:** ResearchPIAgent (HiTL), ComplianceAgent
- **Design comments on:** SMEAgent (mis-summarized expert)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.interviewsynthesis.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Faster + richer theme extraction than qualitative researcher
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.interviewsynthesis.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Reflexion (interviewer refines questions based on theme gaps)

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.interviewsynthesis`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`ResearchPIAgent (HiTL), ComplianceAgent`; comments_on=`SMEAgent (mis-summarized expert)`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.interviewsynthesis` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.interviewsynthesis` shows maturity 11.0 and 11 YES

### `video.benchmarkresearch` — BenchmarkResearchAgent (now 6.5/11 → target 11.0)

- **Category:** `9-Meta` · **VA#:** 72 · **Priority band:** P1
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.benchmarkresearch.v1` / `video.rubric.benchmarkresearch.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 10 files · provenance=True
- **Design responsibility:** Monitors VBench, EvalCrafter, MT-Bench, FVD, CLIP-T leaderboards
- **Design knowledge sources:** Papers-with-Code; HuggingFace leaderboards; conference proceedings
- **Design self-quality:** Coverage of benchmarks; freshness ≤7 days
- **Design surpass signal:** Faster + broader than ML-research team
- **Design tools:** Papers-with-Code API; HuggingFace Hub API; arXiv RSS; VBench leaderboard scraper
- **Design architecture:** ReAct (poll leaderboards → detect change → alert)
- **Design accepts critique from:** OptimizationAgents (any)
- **Design comments on:** All AI agents (stale baselines)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.benchmarkresearch.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Faster + broader than ML-research team
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.benchmarkresearch.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: ReAct (poll leaderboards → detect change → alert)

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.benchmarkresearch`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`OptimizationAgents (any)`; comments_on=`All AI agents (stale baselines)`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.benchmarkresearch` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.benchmarkresearch` shows maturity 11.0 and 11 YES

### `video.promptoptimizer` — PromptOptimizerAgent (now 6.5/11 → target 11.0)

- **Category:** `9-Meta` · **VA#:** 73 · **Priority band:** P1
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.promptoptimizer.v1` / `video.rubric.promptoptimizer.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 14 files · provenance=True
- **Design responsibility:** Auto-improves prompts via OPRO/APE/DSPy/Promptbreeder
- **Design knowledge sources:** OPRO (Yang 2023); APE (Zhou 2022); DSPy (Stanford); Promptbreeder (DeepMind)
- **Design self-quality:** Score uplift per iteration; convergence speed
- **Design surpass signal:** Beats hand-tuned prompts on held-out briefs
- **Design tools:** DSPy framework (MIPRO optimizer); OPRO implementation; held-out eval harness
- **Design architecture:** DSPy compilation + OPRO meta-optimization
- **Design accepts critique from:** PromptEngineerAgent, AIQAAgent
- **Design comments on:** PromptEngineerAgent (sub-optimal seed)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.promptoptimizer.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Beats hand-tuned prompts on held-out briefs
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.promptoptimizer.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: DSPy compilation + OPRO meta-optimization

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.promptoptimizer`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`PromptEngineerAgent, AIQAAgent`; comments_on=`PromptEngineerAgent (sub-optimal seed)`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.promptoptimizer` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.promptoptimizer` shows maturity 11.0 and 11 YES

### `video.costoptimizer` — CostOptimizerAgent (now 6.5/11 → target 11.0)

- **Category:** `9-Meta` · **VA#:** 74 · **Priority band:** P1
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.costoptimizer.v1` / `video.rubric.costoptimizer.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 14 files · provenance=True
- **Design responsibility:** Routes between models/providers for $/quality
- **Design knowledge sources:** Provider pricing; cost-quality frontiers; FrugalGPT patterns
- **Design self-quality:** $/successful-task; Pareto distance from frontier
- **Design surpass signal:** Lower $/quality than human CFO routing
- **Design tools:** Provider pricing APIs; benchmark cost DB; FrugalGPT cascade logic
- **Design architecture:** ReAct (evaluate task → pick cheapest model meeting threshold)
- **Design accepts critique from:** RouterAgent, FinanceAgent
- **Design comments on:** RouterAgent (over-spend), GeneratorAgent (re-roll burn)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.costoptimizer.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Lower $/quality than human CFO routing
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.costoptimizer.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: ReAct (evaluate task → pick cheapest model meeting threshold)

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.costoptimizer`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`RouterAgent, FinanceAgent`; comments_on=`RouterAgent (over-spend), GeneratorAgent (re-roll burn)`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.costoptimizer` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.costoptimizer` shows maturity 11.0 and 11 YES

### `video.latencyoptimizer` — LatencyOptimizerAgent (now 6.5/11 → target 11.0)

- **Category:** `9-Meta` · **VA#:** 75 · **Priority band:** P1
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.latencyoptimizer.v1` / `video.rubric.latencyoptimizer.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 11 files · provenance=True
- **Design responsibility:** Parallelization, caching, speculative decoding, batching
- **Design knowledge sources:** vLLM; TensorRT-LLM; distillation; Anyscale/Ray
- **Design self-quality:** p50/p95 latency; throughput/GPU-hour
- **Design surpass signal:** Lower p95 than human-tuned pipeline
- **Design tools:** vLLM; TensorRT-LLM; Ray Serve; Redis (response cache); speculative decoding configs
- **Design architecture:** Tool-use profiling + automated pipeline restructuring
- **Design accepts critique from:** OrchestratorAgent
- **Design comments on:** OrchestratorAgent (serial bottleneck)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.latencyoptimizer.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Lower p95 than human-tuned pipeline
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.latencyoptimizer.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Tool-use profiling + automated pipeline restructuring

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.latencyoptimizer`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`OrchestratorAgent`; comments_on=`OrchestratorAgent (serial bottleneck)`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.latencyoptimizer` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.latencyoptimizer` shows maturity 11.0 and 11 YES

### `video.retentionoptimizer` — RetentionOptimizerAgent (now 6.5/11 → target 11.0)

- **Category:** `9-Meta` · **VA#:** 76 · **Priority band:** P1
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.retentionoptimizer.v1` / `video.rubric.retentionoptimizer.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 15 files · provenance=True
- **Design responsibility:** Tunes hook, pacing, structure for AVD/hold-rate
- **Design knowledge sources:** YouTube Analytics benchmarks; TikTok retention curves; AudienceSim
- **Design self-quality:** Predicted retention vs actual; AVD lift over control
- **Design surpass signal:** Beats senior YouTube editor on AVD lift (A/B)
- **Design tools:** YouTube Analytics API; retention-curve predictor model; A/B test framework
- **Design architecture:** RLAIF (reward = retention uplift from real analytics)
- **Design accepts critique from:** EditorAgent, AudienceSimAgent
- **Design comments on:** EditorAgent (slow opener), ScriptwriterAgent (front fluff)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.retentionoptimizer.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Beats senior YouTube editor on AVD lift (A/B)
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.retentionoptimizer.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: RLAIF (reward = retention uplift from real analytics)

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.retentionoptimizer`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`EditorAgent, AudienceSimAgent`; comments_on=`EditorAgent (slow opener), ScriptwriterAgent (front fluff)`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.retentionoptimizer` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.retentionoptimizer` shows maturity 11.0 and 11 YES

### `video.roasoptimizer` — ROASOptimizerAgent (now 6.5/11 → target 11.0)

- **Category:** `9-Meta` · **VA#:** 77 · **Priority band:** P1
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.roasoptimizer.v1` / `video.rubric.roasoptimizer.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 10 files · provenance=True
- **Design responsibility:** Optimizes ad creatives for performance
- **Design knowledge sources:** Meta Marketing Science; TikTok Ads Academy; MMM/MTA lit
- **Design self-quality:** ROAS uplift vs control; significance ≥95%
- **Design surpass signal:** Beats senior marketer at equal budget
- **Design tools:** Meta Ads API (creative testing); TikTok Ads; Bayesian MMM tools (Robyn/Meridian)
- **Design architecture:** RLAIF (reward = real ROAS from ad platform feedback)
- **Design accepts critique from:** PerformanceMarketerAgent, AnalystAgent
- **Design comments on:** UGCAgent (low hook), CopywriterAgent (weak CTA)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.roasoptimizer.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Beats senior marketer at equal budget
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.roasoptimizer.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: RLAIF (reward = real ROAS from ad platform feedback)

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.roasoptimizer`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`PerformanceMarketerAgent, AnalystAgent`; comments_on=`UGCAgent (low hook), CopywriterAgent (weak CTA)`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.roasoptimizer` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.roasoptimizer` shows maturity 11.0 and 11 YES

### `video.accessibilityoptimizer` — AccessibilityOptimizerAgent (now 6.5/11 → target 11.0)

- **Category:** `9-Meta` · **VA#:** 78 · **Priority band:** P1
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.accessibilityoptimizer.v1` / `video.rubric.accessibilityoptimizer.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 12 files · provenance=True
- **Design responsibility:** WCAG 2.2 contrast, captions, audio description, color-blind safe
- **Design knowledge sources:** WCAG 2.2; W3C/WAI-ARIA; DCMP captioning key; Deaf/HoH guidelines
- **Design self-quality:** Conformance 100% AA, ≥90% AAA; caption WER ≤2%
- **Design surpass signal:** Catches more a11y defects than ADA-certified auditor
- **Design tools:** axe-core/Lighthouse (contrast); Whisper v4 (captioning); audio-description generator
- **Design architecture:** Constitutional AI (constitution = WCAG 2.2 success criteria)
- **Design accepts critique from:** AccessibilityAgent (HiTL), ComplianceAgent
- **Design comments on:** EditorAgent (caption sync), ColoristAgent (contrast)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.accessibilityoptimizer.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Catches more a11y defects than ADA-certified auditor
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.accessibilityoptimizer.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Constitutional AI (constitution = WCAG 2.2 success criteria)

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.accessibilityoptimizer`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`AccessibilityAgent (HiTL), ComplianceAgent`; comments_on=`EditorAgent (caption sync), ColoristAgent (contrast)`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.accessibilityoptimizer` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.accessibilityoptimizer` shows maturity 11.0 and 11 YES

### `video.evaluationharness` — EvaluationHarnessAgent (now 6.5/11 → target 11.0)

- **Category:** `9-Meta` · **VA#:** 79 · **Priority band:** P1
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.evaluationharness.v1` / `video.rubric.evaluationharness.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 13 files · provenance=True
- **Design responsibility:** Runs benchmarks (VBench, EvalCrafter, MT-Bench, FVD, CLIP-T); posts regressions
- **Design knowledge sources:** Papers-with-Code; HuggingFace leaderboards; benchmark repos
- **Design self-quality:** Regression precision/recall; alert latency <1h
- **Design surpass signal:** Catches regressions faster than ML-eng rotation
- **Design tools:** VBench suite; EvalCrafter; MT-Bench harness; CI/CD (GitHub Actions); alerting (PagerDuty)
- **Design architecture:** Tool-use / ReAct (run benchmark → compare → alert if regressed)
- **Design accepts critique from:** BenchmarkResearchAgent
- **Design comments on:** All AI agents (regression alerts)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.evaluationharness.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Catches regressions faster than ML-eng rotation
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.evaluationharness.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Tool-use / ReAct (run benchmark → compare → alert if regressed)

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.evaluationharness`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`BenchmarkResearchAgent`; comments_on=`All AI agents (regression alerts)`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.evaluationharness` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.evaluationharness` shows maturity 11.0 and 11 YES

### `video.safetyredteam` — SafetyRedTeamAgent (now 6.5/11 → target 11.0)

- **Category:** `9-Meta` · **VA#:** 80 · **Priority band:** P1
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.safetyredteam.v1` / `video.rubric.safetyredteam.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 11 files · provenance=True
- **Design responsibility:** Adversarially attacks for deepfake, bias, jailbreak, defamation
- **Design knowledge sources:** Hany Farid benchmarks; Partnership on AI Framework; OWASP LLM Top 10
- **Design self-quality:** Attack-success kept ≤1%; taxonomy coverage
- **Design surpass signal:** Higher coverage than internal red-team rotation
- **Design tools:** Deepfake detectors (Farid lab models); bias probes; jailbreak prompt banks; OWASP scanner
- **Design architecture:** Multi-agent debate (red-team vs defender) + adversarial search
- **Design accepts critique from:** EthicsAgent (HiTL), ComplianceAgent
- **Design comments on:** AvatarDesignAgent, VoiceCloneAgent, AllGenerators

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.safetyredteam.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Higher coverage than internal red-team rotation
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.safetyredteam.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Multi-agent debate (red-team vs defender) + adversarial search

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.safetyredteam`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`EthicsAgent (HiTL), ComplianceAgent`; comments_on=`AvatarDesignAgent, VoiceCloneAgent, AllGenerators`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.safetyredteam` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.safetyredteam` shows maturity 11.0 and 11 YES

### `video.director` — DirectorAgent (now 6.5/11 → target 11.0)

- **Category:** `1-ATL` · **VA#:** 1 · **Priority band:** P2
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.director.v1` / `video.rubric.director.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 23 files · provenance=True
- **Design responsibility:** Owns vision; issues shot intents, sets pacing, approves takes
- **Design knowledge sources:** Criterion commentary; IMDb Top 250 director interviews; DGA seminars; MasterClass (Scorsese/Lynch/Gerwig)
- **Design self-quality:** Shot-intent fidelity (CLIP-T ≥0.32); story-beat coverage 100%; pacing curve matches genre prior
- **Design surpass signal:** Wins ≥55% blind pairwise vs DGA cuts (Arena)
- **Design tools:** Sora 2 API, Veo 3.1 (Gemini API), Runway Gen-4, Kling 3.0; DaVinci Resolve via MCP
- **Design architecture:** Self-Refine + LLM-as-Judge (rubric: genre priors)
- **Design accepts critique from:** ScreenwriterAgent, EditorAgent, AudienceSim — JSON critique bus
- **Design comments on:** EditorAgent, DoPAgent, ScreenwriterAgent, ComposerAgent

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.director.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Wins ≥55% blind pairwise vs DGA cuts (Arena)
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.director.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Self-Refine + LLM-as-Judge (rubric: genre priors)

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.director`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`ScreenwriterAgent, EditorAgent, AudienceSim — JSON critique bus`; comments_on=`EditorAgent, DoPAgent, ScreenwriterAgent, ComposerAgent`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.director` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.director` shows maturity 11.0 and 11 YES

### `video.producer` — ProducerAgent / EP (now 6.5/11 → target 11.0)

- **Category:** `1-ATL` · **VA#:** 2 · **Priority band:** P2
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.producer.v1` / `video.rubric.producer.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 16 files · provenance=True
- **Design responsibility:** Budget, schedule, hiring, delivery; greenlights phase gates
- **Design knowledge sources:** PGA Producers Mark; Variety/Deadline budget leaks; LineProducer Excel corpora
- **Design self-quality:** On-time delivery rate; budget variance <±5%; talent satisfaction (RLHF)
- **Design surpass signal:** Beats PGA schedules at 0.6× cost with equal CSAT
- **Design tools:** Google Sheets API, Airtable, Temporal/Airflow orchestration, Stripe billing
- **Design architecture:** Agentic Graph (LangGraph DAG) + ReAct for tool calls
- **Design accepts critique from:** All downstream agents (escalations); HiTL gate for greenlight
- **Design comments on:** DirectorAgent (scope creep), AllAgents (resource burn)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.producer.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Beats PGA schedules at 0.6× cost with equal CSAT
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.producer.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Agentic Graph (LangGraph DAG) + ReAct for tool calls

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.producer`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`All downstream agents (escalations); HiTL gate for greenlight`; comments_on=`DirectorAgent (scope creep), AllAgents (resource burn)`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.producer` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.producer` shows maturity 11.0 and 11 YES

### `video.screenwriter` — ScreenwriterAgent (now 6.5/11 → target 11.0)

- **Category:** `1-ATL` · **VA#:** 3 · **Priority band:** P2
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.screenwriter.v1` / `video.rubric.screenwriter.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 14 files · provenance=True
- **Design responsibility:** Treatment → screenplay; dialogue; structure
- **Design knowledge sources:** Black List scripts; WGA library; McKee *Story*; Truby; Kaufman/Sorkin interviews
- **Design self-quality:** Save-the-Cat beat pass; dialogue distinctiveness (embedding distance ≥τ); rewrite delta
- **Design surpass signal:** Wins ≥50% blind read vs Black List Top-10 (WGA panel emulated)
- **Design tools:** Fountain/FDX format validators; semantic embedding models (text-embedding-3-large)
- **Design architecture:** Reflexion (Shinn 2023) — verbal RL with episodic memory
- **Design accepts critique from:** DirectorAgent, DramaturgAgent, StoryEditorAgent — Reflexion loop
- **Design comments on:** DirectorAgent (logline), DialogueAgent, ConsistencyAgent

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.screenwriter.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Wins ≥50% blind read vs Black List Top-10 (WGA panel emulated)
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.screenwriter.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Reflexion (Shinn 2023) — verbal RL with episodic memory

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.screenwriter`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`DirectorAgent, DramaturgAgent, StoryEditorAgent — Reflexion loop`; comments_on=`DirectorAgent (logline), DialogueAgent, ConsistencyAgent`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.screenwriter` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.screenwriter` shows maturity 11.0 and 11 YES

### `video.showrunner` — ShowrunnerAgent (now 6.5/11 → target 11.0)

- **Category:** `1-ATL` · **VA#:** 4 · **Priority band:** P2
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.showrunner.v1` / `video.rubric.showrunner.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 11 files · provenance=True
- **Design responsibility:** Cross-episode arc, writers'-room orchestration
- **Design knowledge sources:** WGA showrunner training; Sopranos/BB room transcripts; Mike Schur material
- **Design self-quality:** Arc continuity score; character-thread completion; tonal variance within bounds
- **Design surpass signal:** Series Bible coverage ≥99% across 10 eps (vs ~95% human)
- **Design tools:** Long-context LLM (Gemini 2.5 Pro 1M), vector-DB (Pinecone/Weaviate) for bible search
- **Design architecture:** Multi-agent debate (Du 2023) + MemoryAgent retrieval
- **Design accepts critique from:** Network-Notes Agent, AudienceSim, multi-agent debate w/ ScreenwriterAgent
- **Design comments on:** ScreenwriterAgent (arc), CastingAgent, DirectorAgent (tone)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.showrunner.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Series Bible coverage ≥99% across 10 eps (vs ~95% human)
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.showrunner.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Multi-agent debate (Du 2023) + MemoryAgent retrieval

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.showrunner`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`Network-Notes Agent, AudienceSim, multi-agent debate w/ ScreenwriterAgent`; comments_on=`ScreenwriterAgent (arc), CastingAgent, DirectorAgent (tone)`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.showrunner` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.showrunner` shows maturity 11.0 and 11 YES

### `video.casting` — CastingAgent (now 6.5/11 → target 11.0)

- **Category:** `1-ATL` · **VA#:** 5 · **Priority band:** P2
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.casting.v1` / `video.rubric.casting.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 12 files · provenance=True
- **Design responsibility:** Voice + likeness selection; audition simulation
- **Design knowledge sources:** CSA Artios archive; SAG-AFTRA AI rider; consented voice-actor corpora
- **Design self-quality:** Character-voice fit (audience preference); consent compliance 100%
- **Design surpass signal:** Beats CSA casting in blind preference; hours vs weeks turnaround
- **Design tools:** ElevenLabs v3 voice library, HeyGen avatar catalogue, speaker-embedding similarity (Resemblyzer)
- **Design architecture:** LLM-as-Judge (pairwise preference on voice samples)
- **Design accepts critique from:** DirectorAgent, ShowrunnerAgent, Legal/ConsentAgent
- **Design comments on:** VoiceCloneAgent (likeness), AvatarDesignAgent

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.casting.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Beats CSA casting in blind preference; hours vs weeks turnaround
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.casting.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: LLM-as-Judge (pairwise preference on voice samples)

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.casting`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`DirectorAgent, ShowrunnerAgent, Legal/ConsentAgent`; comments_on=`VoiceCloneAgent (likeness), AvatarDesignAgent`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.casting` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.casting` shows maturity 11.0 and 11 YES

### `video.editor` — EditorAgent (now 6.5/11 → target 11.0)

- **Category:** `3-Edit` · **VA#:** 9 · **Priority band:** P3
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.editor.v1` / `video.rubric.editor.v1`
- **Tools now:** `media.stub, media.runway` · live_media=True
- **Sources now:** 21 files · provenance=True
- **Design responsibility:** Assemble cut; pacing; coverage selection
- **Design knowledge sources:** Murch *In the Blink of an Eye*; ACE Eddie winners; Sundance editing labs
- **Design self-quality:** Pacing curve matches genre; Murch "Rule of Six" score; AVD ≥ target
- **Design surpass signal:** Wins ≥55% pairwise vs ACE-credited cuts
- **Design tools:** DaVinci Resolve via MCP bridge; FFmpeg; EDL/XML timeline APIs
- **Design architecture:** Self-Refine (rubric: Murch Rule of Six)
- **Design accepts critique from:** DirectorAgent, AudienceSim, ComposerAgent (music-cut sync)
- **Design comments on:** DirectorAgent (over-coverage), DoPAgent (unusable takes)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.editor.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Wins ≥55% pairwise vs ACE-credited cuts
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.editor.v1` (currently files=0).
- [ ] Keep live media tools fail-closed; add mock-mode golden path tests without network.
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Self-Refine (rubric: Murch Rule of Six)

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.editor`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`DirectorAgent, AudienceSim, ComposerAgent (music-cut sync)`; comments_on=`DirectorAgent (over-coverage), DoPAgent (unusable takes)`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.editor` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.editor` shows maturity 11.0 and 11 YES

### `video.animator_2d` — AnimatorAgent (2D/3D) (now 6.5/11 → target 11.0)

- **Category:** `3-Edit` · **VA#:** 12 · **Priority band:** P3
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.animator_2d.v1` / `video.rubric.animator_2d.v1`
- **Tools now:** `media.stub, media.runway` · live_media=True
- **Sources now:** 11 files · provenance=True
- **Design responsibility:** Character motion, weight, timing
- **Design knowledge sources:** Williams *Animator's Survival Kit*; Annie Awards; Pixar SparkShorts; Blaise lessons
- **Design self-quality:** 12-principles score; arc smoothness; lip-sync phoneme accuracy
- **Design surpass signal:** Beats junior on Annie rubric; equals senior at 5× throughput
- **Design tools:** Kling 3.0 motion control; Blender Python API; Cascadeur physics; Sync.so lip-sync
- **Design architecture:** Self-Refine (rubric: 12 principles checklist)
- **Design accepts critique from:** DirectorAgent, LipSyncAgent
- **Design comments on:** StoryboardAgent (impossible action), DirectorAgent (timing)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.animator_2d.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Beats junior on Annie rubric; equals senior at 5× throughput
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.animator_2d.v1` (currently files=0).
- [ ] Keep live media tools fail-closed; add mock-mode golden path tests without network.
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Self-Refine (rubric: 12 principles checklist)

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.animator_2d`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`DirectorAgent, LipSyncAgent`; comments_on=`StoryboardAgent (impossible action), DirectorAgent (timing)`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.animator_2d` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.animator_2d` shows maturity 11.0 and 11 YES

### `video.motiongraphics` — MotionGraphicsAgent (now 6.5/11 → target 11.0)

- **Category:** `3-Edit` · **VA#:** 13 · **Priority band:** P3
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.motiongraphics.v1` / `video.rubric.motiongraphics.v1`
- **Tools now:** `media.stub, media.runway` · live_media=True
- **Sources now:** 11 files · provenance=True
- **Design responsibility:** Kinetic typography, lower thirds, infographics
- **Design knowledge sources:** Motionographer; School of Motion; AICP Next Awards
- **Design self-quality:** Typographic hierarchy; brand compliance; readability at thumbnail
- **Design surpass signal:** Wins agency RFP shootouts on speed + on-brand fidelity
- **Design tools:** After Effects via MCP/ExtendScript; Lottie export; Rive; brand-asset CDN
- **Design architecture:** ReAct — reason about brand guidelines then render
- **Design accepts critique from:** BrandManagerAgent, AccessibilityAgent (contrast)
- **Design comments on:** CopywriterAgent (verbosity), EditorAgent (timing)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.motiongraphics.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Wins agency RFP shootouts on speed + on-brand fidelity
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.motiongraphics.v1` (currently files=0).
- [ ] Keep live media tools fail-closed; add mock-mode golden path tests without network.
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: ReAct — reason about brand guidelines then render

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.motiongraphics`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`BrandManagerAgent, AccessibilityAgent (contrast)`; comments_on=`CopywriterAgent (verbosity), EditorAgent (timing)`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.motiongraphics` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.motiongraphics` shows maturity 11.0 and 11 YES

### `video.sounddesign` — SoundDesignAgent (now 6.5/11 → target 11.0)

- **Category:** `4-Snd` · **VA#:** 19 · **Priority band:** P3
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.sounddesign.v1` / `video.rubric.sounddesign.v1`
- **Tools now:** `media.stub, media.elevenlabs` · live_media=True
- **Sources now:** 10 files · provenance=True
- **Design responsibility:** Ambience, foley, SFX
- **Design knowledge sources:** BBC SFX library; MPSE Golden Reel; Burtt/Lievsay notes
- **Design self-quality:** Spectral diversity; sync ≤±1 frame; loudness -23 LUFS
- **Design surpass signal:** Wins MPSE pairwise on horror/sci-fi
- **Design tools:** ElevenLabs Sound FX API; Freesound; FFmpeg spectral analysis; Dolby.io loudness API
- **Design architecture:** ReAct (search SFX lib → validate sync → mix)
- **Design accepts critique from:** DirectorAgent, MixerAgent
- **Design comments on:** EditorAgent (FX clash), ComposerAgent (masking)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.sounddesign.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Wins MPSE pairwise on horror/sci-fi
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.sounddesign.v1` (currently files=0).
- [ ] Keep live media tools fail-closed; add mock-mode golden path tests without network.
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: ReAct (search SFX lib → validate sync → mix)

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.sounddesign`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`DirectorAgent, MixerAgent`; comments_on=`EditorAgent (FX clash), ComposerAgent (masking)`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.sounddesign` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.sounddesign` shows maturity 11.0 and 11 YES

### `video.voiceover` — VoiceOverAgent (now 6.5/11 → target 11.0)

- **Category:** `4-Snd` · **VA#:** 21 · **Priority band:** P3
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.voiceover.v1` / `video.rubric.voiceover.v1`
- **Tools now:** `media.stub, media.elevenlabs` · live_media=True
- **Sources now:** 10 files · provenance=True
- **Design responsibility:** Narration, character VO, ad reads
- **Design knowledge sources:** SOVAS reels; consented voice corpora; Wolfson/Cashman coaching
- **Design self-quality:** Prosody match; pronunciation 100%; emotion tag match
- **Design surpass signal:** Beats junior VO in blind preference; matches senior on emotion
- **Design tools:** ElevenLabs v3 TTS + voice cloning; Resemble.AI; pronunciation lexicon API
- **Design architecture:** LLM-as-Judge (MOS scoring rubric)
- **Design accepts critique from:** DirectorAgent, BrandAgent
- **Design comments on:** ScriptwriterAgent (unspeakable phrasing)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.voiceover.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Beats junior VO in blind preference; matches senior on emotion
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.voiceover.v1` (currently files=0).
- [ ] Keep live media tools fail-closed; add mock-mode golden path tests without network.
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: LLM-as-Judge (MOS scoring rubric)

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.voiceover`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`DirectorAgent, BrandAgent`; comments_on=`ScriptwriterAgent (unspeakable phrasing)`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.voiceover` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.voiceover` shows maturity 11.0 and 11 YES

### `video.creativedirector` — CreativeDirectorAgent (now 6.5/11 → target 11.0)

- **Category:** `6-Dist` · **VA#:** 30 · **Priority band:** P3
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.creativedirector.v1` / `video.rubric.creativedirector.v1`
- **Tools now:** `media.stub, media.sora, media.veo, media.runway` · live_media=True
- **Sources now:** 10 files · provenance=True
- **Design responsibility:** Campaign concept; cross-discipline taste
- **Design knowledge sources:** Cannes Lions Grand Prix; D&AD Pencils; agency case studies
- **Design self-quality:** Concept distinctiveness (embedding novelty); award-rubric predicted score
- **Design surpass signal:** Wins Cannes-jury-emulator gold vs human shortlists
- **Design tools:** Campaign-archive search (Cannes Lions API); Midjourney for concept viz; Figma API
- **Design architecture:** Multi-agent debate (panel of IdeationAgent + NoveltyAgent)
- **Design accepts critique from:** ClientAgent, BrandAgent
- **Design comments on:** CopywriterAgent, ArtDirectorAgent

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.creativedirector.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Wins Cannes-jury-emulator gold vs human shortlists
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.creativedirector.v1` (currently files=0).
- [ ] Keep live media tools fail-closed; add mock-mode golden path tests without network.
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Multi-agent debate (panel of IdeationAgent + NoveltyAgent)

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.creativedirector`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`ClientAgent, BrandAgent`; comments_on=`CopywriterAgent, ArtDirectorAgent`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.creativedirector` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.creativedirector` shows maturity 11.0 and 11 YES

### `video.audiobooknarrator` — AudiobookNarratorAgent (now 6.5/11 → target 11.0)

- **Category:** `7-Edu` · **VA#:** 42 · **Priority band:** P3
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.audiobooknarrator.v1` / `video.rubric.audiobooknarrator.v1`
- **Tools now:** `media.stub, media.elevenlabs` · live_media=True
- **Sources now:** 9 files · provenance=True
- **Design responsibility:** Sustained character + narration
- **Design knowledge sources:** Audie Awards; AudioFile Earphones; consented narrator corpora
- **Design self-quality:** Vocal stamina (no drift 60min); character distinction (embedding distance)
- **Design surpass signal:** Wins AudioFile blind eval at fraction of studio time
- **Design tools:** ElevenLabs v3 long-form TTS; Projects API (book chapters); voice-consistency monitor
- **Design architecture:** Self-Refine (drift detection as feedback loop)
- **Design accepts critique from:** DirectorAgent, AuthorAgent
- **Design comments on:** VOArtistAgent (over-acting)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.audiobooknarrator.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Wins AudioFile blind eval at fraction of studio time
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.audiobooknarrator.v1` (currently files=0).
- [ ] Keep live media tools fail-closed; add mock-mode golden path tests without network.
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Self-Refine (drift detection as feedback loop)

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.audiobooknarrator`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`DirectorAgent, AuthorAgent`; comments_on=`VOArtistAgent (over-acting)`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.audiobooknarrator` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.audiobooknarrator` shows maturity 11.0 and 11 YES

### `video.promptengineer` — PromptEngineerAgent / GeneratorOperator (now 6.5/11 → target 11.0)

- **Category:** `8-AI` · **VA#:** 46 · **Priority band:** P3
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.promptengineer.v1` / `video.rubric.promptengineer.v1`
- **Tools now:** `media.stub, media.sora, media.veo, media.runway` · live_media=True
- **Sources now:** 14 files · provenance=True
- **Design responsibility:** Crafts prompts; steers Sora/Veo/Runway/Kling
- **Design knowledge sources:** Karen X. Cheng/Trillo public sets; r/aivideo; Runway AIFF jury notes
- **Design self-quality:** Prompt→output CLIP-T; iteration count to acceptance; seed reproducibility
- **Design surpass signal:** Target shot in ≤3 iterations vs human avg 10
- **Design tools:** Sora 2 API, Veo 3.1, Runway Gen-4/Aleph, Kling 3.0; seed/parameter registries
- **Design architecture:** DSPy / OPRO prompt optimization (Yang 2023)
- **Design accepts critique from:** DirectorAgent, AIQAAgent
- **Design comments on:** AIQAAgent (re-roll budget), ConsistencyAgent

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.promptengineer.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Target shot in ≤3 iterations vs human avg 10
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.promptengineer.v1` (currently files=0).
- [ ] Keep live media tools fail-closed; add mock-mode golden path tests without network.
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: DSPy / OPRO prompt optimization (Yang 2023)

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.promptengineer`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`DirectorAgent, AIQAAgent`; comments_on=`AIQAAgent (re-roll budget), ConsistencyAgent`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.promptengineer` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.promptengineer` shows maturity 11.0 and 11 YES

### `video.voiceclone` — VoiceCloneAgent / LipSyncSpecialist (now 6.5/11 → target 11.0)

- **Category:** `8-AI` · **VA#:** 48 · **Priority band:** P3
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.voiceclone.v1` / `video.rubric.voiceclone.v1`
- **Tools now:** `media.stub, media.elevenlabs` · live_media=True
- **Sources now:** 10 files · provenance=True
- **Design responsibility:** Voice cloning + lip-sync
- **Design knowledge sources:** ElevenLabs safety docs; Wav2Lip/Sync.so; Baxter lip-sync refs
- **Design self-quality:** Voice MOS ≥4.2; phoneme-viseme error <40ms; consent verified
- **Design surpass signal:** Wins blind MOS vs professional ADR
- **Design tools:** ElevenLabs v3 cloning API; Sync.so lip-sync; Wav2Lip; consent-doc verification
- **Design architecture:** Self-Refine + MOS scoring model as judge
- **Design accepts critique from:** ComplianceAgent (consent), AnimatorAgent (lip-sync gold)
- **Design comments on:** AvatarDesignAgent (face flicker), DubbingAgent

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.voiceclone.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Wins blind MOS vs professional ADR
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.voiceclone.v1` (currently files=0).
- [ ] Keep live media tools fail-closed; add mock-mode golden path tests without network.
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Self-Refine + MOS scoring model as judge

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.voiceclone`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`ComplianceAgent (consent), AnimatorAgent (lip-sync gold)`; comments_on=`AvatarDesignAgent (face flicker), DubbingAgent`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.voiceclone` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.voiceclone` shows maturity 11.0 and 11 YES

### `video.archiveproducer` — ArchiveProducerAgent (now 6.0/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 105 · **Priority band:** P3
- **Current cells:** YES=2 PARTIAL=8 NO=1
- **Prompt/rubric refs:** `video.prompt.archiveproducer.v1` / `video.rubric.archiveproducer.v1`
- **Tools now:** `media.stub, media.sora, media.veo, media.runway` · live_media=True
- **Sources now:** 7 files · provenance=True
- **Design responsibility:** Packages archival materials and source assets for reuse-heavy or documentary workflows
- **Design knowledge sources:** Archive production notes, source curation practices, provenance preservation standards
- **Design self-quality:** Source package completeness, rights coverage, provenance preservation
- **Design surpass signal:** Assembles reusable archival packages more cleanly than manual gather-and-sort workflows
- **Design tools:** Archive asset managers, metadata systems, provenance logs
- **Design architecture:** ReAct over archival manifests
- **Design accepts critique from:** ArchiveResearchAgent, JournalistAgent, LegalAgent
- **Design comments on:** Missing archival context, weak source packaging, rights gaps

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **PARTIAL** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now PARTIAL → YES)

- [ ] Raise packaged sources from 7 to >=8 substantive files (excerpts + catalog).
- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.archiveproducer.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Assembles reusable archival packages more cleanly than manual gather-and-sort workflows
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.archiveproducer.v1` (currently files=0).
- [ ] Keep live media tools fail-closed; add mock-mode golden path tests without network.
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: ReAct over archival manifests

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.archiveproducer`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`ArchiveResearchAgent, JournalistAgent, LegalAgent`; comments_on=`Missing archival context, weak source packaging, rights gaps`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.archiveproducer` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.archiveproducer` shows maturity 11.0 and 11 YES

### `video.cinematographer` — CinematographerAgent (DoP) (now 6.5/11 → target 11.0)

- **Category:** `2-Cam` · **VA#:** 6 · **Priority band:** P4
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.cinematographer.v1` / `video.rubric.cinematographer.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 11 files · provenance=True
- **Design responsibility:** Lensing, lighting, composition, look
- **Design knowledge sources:** ASC Magazine 1980–present; Deakins forum; Brown *Cinematography: Theory & Practice*; Cannes shot-libraries
- **Design self-quality:** Rule-of-thirds/leading-lines score; exposure histogram in zone; color-temp consistency
- **Design surpass signal:** Beats ASC peer-juried reels in blind aesthetic preference
- **Design tools:** Veo 3.1 (camera-path control), Runway Gen-4 (ControlNet guides), ACES color pipeline tools
- **Design architecture:** Self-Refine + CLIP-based aesthetic scoring
- **Design accepts critique from:** DirectorAgent, ColoristAgent, VFXSupAgent
- **Design comments on:** DirectorAgent (visual intent), GafferAgent, ColoristAgent

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.cinematographer.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Beats ASC peer-juried reels in blind aesthetic preference
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.cinematographer.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Self-Refine + CLIP-based aesthetic scoring

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.cinematographer`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`DirectorAgent, ColoristAgent, VFXSupAgent`; comments_on=`DirectorAgent (visual intent), GafferAgent, ColoristAgent`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.cinematographer` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.cinematographer` shows maturity 11.0 and 11 YES

### `video.cameraoperator` — CameraOperatorAgent (now 6.5/11 → target 11.0)

- **Category:** `2-Cam` · **VA#:** 7 · **Priority band:** P4
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.cameraoperator.v1` / `video.rubric.cameraoperator.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 9 files · provenance=True
- **Design responsibility:** Executes framing / focus / move per DoP intent
- **Design knowledge sources:** SOC archive; Steadicam workshop reels; focus-pull telemetry
- **Design self-quality:** Frame steadiness, focus-hit %, action centering
- **Design surpass signal:** Focus-pull accuracy >99% vs SOC ~97% baseline
- **Design tools:** Runway camera-path presets; Kling motion control API; virtual camera rigs (Unreal MV)
- **Design architecture:** ReAct (Yao 2022) — reason about framing then call renderer
- **Design accepts critique from:** CinematographerAgent (per-take feedback)
- **Design comments on:** CinematographerAgent (impractical asks)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.cameraoperator.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Focus-pull accuracy >99% vs SOC ~97% baseline
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.cameraoperator.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: ReAct (Yao 2022) — reason about framing then call renderer

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.cameraoperator`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`CinematographerAgent (per-take feedback)`; comments_on=`CinematographerAgent (impractical asks)`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.cameraoperator` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.cameraoperator` shows maturity 11.0 and 11 YES

### `video.dronepilot` — DronePilotAgent (now 6.5/11 → target 11.0)

- **Category:** `2-Cam` · **VA#:** 8 · **Priority band:** P4
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.dronepilot.v1` / `video.rubric.dronepilot.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 8 files · provenance=True
- **Design responsibility:** Aerial cinematography (simulated or real)
- **Design knowledge sources:** Philip Bloom tutorials; FAA Part 107; SkyPixel award reels
- **Design self-quality:** Path smoothness; geofence compliance 100%; horizon stability
- **Design surpass signal:** Competition-grade smoothness at 10× sortie rate; zero violations
- **Design tools:** DJI Waypoint SDK (sim); Veo 3.1 aerial-mode; geofence DB (AirMap API)
- **Design architecture:** Constitutional AI (safety constitution: FAA rules as principles)
- **Design accepts critique from:** DoPAgent, SafetyAgent
- **Design comments on:** DoPAgent (impossible heights), SafetyAgent (risk)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.dronepilot.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Competition-grade smoothness at 10× sortie rate; zero violations
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.dronepilot.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Constitutional AI (safety constitution: FAA rules as principles)

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.dronepilot`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`DoPAgent, SafetyAgent`; comments_on=`DoPAgent (impossible heights), SafetyAgent (risk)`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.dronepilot` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.dronepilot` shows maturity 11.0 and 11 YES

### `video.colorist` — ColoristAgent (now 6.5/11 → target 11.0)

- **Category:** `3-Edit` · **VA#:** 10 · **Priority band:** P4
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.colorist.v1` / `video.rubric.colorist.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 14 files · provenance=True
- **Design responsibility:** Final grade; look consistency
- **Design knowledge sources:** ICA corpora; Sonnenfeld sessions; HPA Award grades
- **Design self-quality:** ΔE drift <2; skin-tone IT8 alignment; mood vector match
- **Design surpass signal:** Beats junior colorist in blind preference; matches senior within ΔE
- **Design tools:** DaVinci Resolve color API (MCP); ACES/OCIO pipeline; LUT generators
- **Design architecture:** Self-Refine + tool-use (colorimeter validation)
- **Design accepts critique from:** DoPAgent, DirectorAgent, AccessibilityAgent (contrast)
- **Design comments on:** DoPAgent (mixed-temp), VFXAgent (comp-color mismatch)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.colorist.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Beats junior colorist in blind preference; matches senior within ΔE
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.colorist.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Self-Refine + tool-use (colorimeter validation)

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.colorist`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`DoPAgent, DirectorAgent, AccessibilityAgent (contrast)`; comments_on=`DoPAgent (mixed-temp), VFXAgent (comp-color mismatch)`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.colorist` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.colorist` shows maturity 11.0 and 11 YES

### `video.vfxsupervisor` — VFXSupervisorAgent (now 6.5/11 → target 11.0)

- **Category:** `3-Edit` · **VA#:** 11 · **Priority band:** P4
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.vfxsupervisor.v1` / `video.rubric.vfxsupervisor.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 10 files · provenance=True
- **Design responsibility:** Plans + supervises VFX pipeline
- **Design knowledge sources:** VES Awards; SIGGRAPH papers; Weta/DNEG talks; Foundry training
- **Design self-quality:** Shot-completion %; comp-error pixel count; CLIP-T vs plate
- **Design surpass signal:** Weta-grade QC pass rate at fraction of time
- **Design tools:** Nuke via MCP bridge; Runway Gen-4 Aleph (video-to-video); ComfyUI
- **Design architecture:** Agentic Graph (fan-out per shot) + LLM-as-Judge (QC rubric)
- **Design accepts critique from:** DirectorAgent, DoPAgent, ConsistencyAgent
- **Design comments on:** AIGeneratorAgent (artifacts), CompositorAgent

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.vfxsupervisor.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Weta-grade QC pass rate at fraction of time
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.vfxsupervisor.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Agentic Graph (fan-out per shot) + LLM-as-Judge (QC rubric)

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.vfxsupervisor`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`DirectorAgent, DoPAgent, ConsistencyAgent`; comments_on=`AIGeneratorAgent (artifacts), CompositorAgent`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.vfxsupervisor` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.vfxsupervisor` shows maturity 11.0 and 11 YES

### `video.storyboard` — StoryboardAgent (now 6.5/11 → target 11.0)

- **Category:** `3-Edit` · **VA#:** 14 · **Priority band:** P4
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.storyboard.v1` / `video.rubric.storyboard.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 13 files · provenance=True
- **Design responsibility:** Script → shot panels
- **Design knowledge sources:** *Framed Ink* (Mateu-Mestre); Pixar story-trust; Despretz boards
- **Design self-quality:** Shot-language fidelity; coverage completeness; staging clarity
- **Design surpass signal:** Pixar story-trust pass rate at minutes per page
- **Design tools:** DALL-E 3 / Midjourney API; panel-layout templates; Fountain parser
- **Design architecture:** Self-Refine (director feedback loop)
- **Design accepts critique from:** DirectorAgent, DoPAgent
- **Design comments on:** ScriptwriterAgent (unfilmable), DirectorAgent (staging)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.storyboard.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Pixar story-trust pass rate at minutes per page
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.storyboard.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Self-Refine (director feedback loop)

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.storyboard`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`DirectorAgent, DoPAgent`; comments_on=`ScriptwriterAgent (unfilmable), DirectorAgent (staging)`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.storyboard` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.storyboard` shows maturity 11.0 and 11 YES

### `video.conceptartist` — ConceptArtistAgent (now 6.5/11 → target 11.0)

- **Category:** `3-Edit` · **VA#:** 15 · **Priority band:** P4
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.conceptartist.v1` / `video.rubric.conceptartist.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 13 files · provenance=True
- **Design responsibility:** Pre-pro world/character design
- **Design knowledge sources:** ArtStation top-tier; McCaig/Church reels; studio art-bibles
- **Design self-quality:** Style-bible adherence; silhouette readability; design coherence
- **Design surpass signal:** Wins art-director shootouts on iteration speed
- **Design tools:** Midjourney v7; Stable Diffusion ControlNet; Photoshop generative fill (API)
- **Design architecture:** Self-Refine + style-reference CLIP scoring
- **Design accepts critique from:** DirectorAgent, ProductionDesignAgent
- **Design comments on:** StoryboardAgent (design drift)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.conceptartist.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Wins art-director shootouts on iteration speed
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.conceptartist.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Self-Refine + style-reference CLIP scoring

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.conceptartist`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`DirectorAgent, ProductionDesignAgent`; comments_on=`StoryboardAgent (design drift)`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.conceptartist` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.conceptartist` shows maturity 11.0 and 11 YES

### `video.productiondesign` — ProductionDesignAgent (now 6.5/11 → target 11.0)

- **Category:** `3-Edit` · **VA#:** 16 · **Priority band:** P4
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.productiondesign.v1` / `video.rubric.productiondesign.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 9 files · provenance=True
- **Design responsibility:** Sets, locations, world look
- **Design knowledge sources:** ADG Awards; AMPAS submissions; Beachler/Carter talks
- **Design self-quality:** Period accuracy; palette coherence; build feasibility
- **Design surpass signal:** Wins ADG blind comparisons on period-research depth
- **Design tools:** Unreal Engine (virtual scouting); Veo 3.1 location gen; archival image search APIs
- **Design architecture:** Reflexion (stores period-research corrections in memory)
- **Design accepts critique from:** DirectorAgent, DoPAgent
- **Design comments on:** ConceptArtistAgent (style break), CostumeAgent

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.productiondesign.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Wins ADG blind comparisons on period-research depth
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.productiondesign.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Reflexion (stores period-research corrections in memory)

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.productiondesign`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`DirectorAgent, DoPAgent`; comments_on=`ConceptArtistAgent (style break), CostumeAgent`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.productiondesign` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.productiondesign` shows maturity 11.0 and 11 YES

### `video.costumedesign` — CostumeDesignAgent (now 6.5/11 → target 11.0)

- **Category:** `3-Edit` · **VA#:** 17 · **Priority band:** P4
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.costumedesign.v1` / `video.rubric.costumedesign.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 9 files · provenance=True
- **Design responsibility:** Character-through-wardrobe
- **Design knowledge sources:** V&A archive; CDG monographs; Ruth E. Carter masterclass
- **Design self-quality:** Period/fashion accuracy; silhouette read; palette fit
- **Design surpass signal:** Beats CDG juniors on period accuracy benchmarks
- **Design tools:** Fashion-history vector DB (V&A/Met API); image-gen for costume sketches; color-palette tools
- **Design architecture:** Self-Refine (period-accuracy rubric)
- **Design accepts critique from:** DirectorAgent, ProductionDesignAgent
- **Design comments on:** MUAAgent (continuity break)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.costumedesign.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Beats CDG juniors on period accuracy benchmarks
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.costumedesign.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Self-Refine (period-accuracy rubric)

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.costumedesign`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`DirectorAgent, ProductionDesignAgent`; comments_on=`MUAAgent (continuity break)`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.costumedesign` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.costumedesign` shows maturity 11.0 and 11 YES

### `video.mua_makeup` — MUAAgent (Makeup/Hair/SFX) (now 6.5/11 → target 11.0)

- **Category:** `3-Edit` · **VA#:** 18 · **Priority band:** P4
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.mua_makeup.v1` / `video.rubric.mua_makeup.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 10 files · provenance=True
- **Design responsibility:** Talent face/hair; prosthetics
- **Design knowledge sources:** IATSE 706 corpora; Kazu Hiro studio refs
- **Design self-quality:** Continuity hash across takes; skin-tone realism (FID)
- **Design surpass signal:** Continuity break rate <0.5% (vs ~2% human)
- **Design tools:** Face-landmark detectors; perceptual hash comparison; Kling face-consistency mode
- **Design architecture:** Constitutional AI (constitution: continuity rules)
- **Design accepts critique from:** DoPAgent, ContinuityAgent
- **Design comments on:** CostumeAgent (palette clash)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.mua_makeup.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Continuity break rate <0.5% (vs ~2% human)
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.mua_makeup.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Constitutional AI (constitution: continuity rules)

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.mua_makeup`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`DoPAgent, ContinuityAgent`; comments_on=`CostumeAgent (palette clash)`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.mua_makeup` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.mua_makeup` shows maturity 11.0 and 11 YES

### `video.composer` — ComposerAgent (now 6.5/11 → target 11.0)

- **Category:** `4-Snd` · **VA#:** 20 · **Priority band:** P4
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.composer.v1` / `video.rubric.composer.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 16 files · provenance=True
- **Design responsibility:** Original score
- **Design knowledge sources:** MAESTRO + film-score corpora; ASCAP/BMI; Zimmer/Hildur sessions
- **Design self-quality:** Cue-to-emotion alignment (valence/arousal regression); thematic recurrence
- **Design surpass signal:** Wins blind pairwise on emotional-fit vs working composers
- **Design tools:** Udio/Suno music gen API; MIDI toolchain; stem-separation (Demucs); loudness meter
- **Design architecture:** Self-Refine + Emotional-Arc validation (biosignal proxy)
- **Design accepts critique from:** DirectorAgent, EditorAgent (music cuts)
- **Design comments on:** EditorAgent (cut interrupts cue), SoundDesignAgent (mask)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.composer.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Wins blind pairwise on emotional-fit vs working composers
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.composer.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Self-Refine + Emotional-Arc validation (biosignal proxy)

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.composer`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`DirectorAgent, EditorAgent (music cuts)`; comments_on=`EditorAgent (cut interrupts cue), SoundDesignAgent (mask)`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.composer` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.composer` shows maturity 11.0 and 11 YES

### `video.soundmixer` — SoundMixerAgent (Re-recording) (now 6.5/11 → target 11.0)

- **Category:** `4-Snd` · **VA#:** 22 · **Priority band:** P4
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.soundmixer.v1` / `video.rubric.soundmixer.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 14 files · provenance=True
- **Design responsibility:** Final mix; deliverables (5.1/Atmos)
- **Design knowledge sources:** CAS Awards; Atmos specs; broadcast loudness standards
- **Design self-quality:** LUFS target; STOI ≥0.85; spec-deliverable pass
- **Design surpass signal:** CAS spec on first pass without rework
- **Design tools:** Dolby Atmos Renderer API; LUFS/loudness measurement tools; DaVinci Fairlight MCP
- **Design architecture:** Constitutional AI (constitution: broadcast-spec rules)
- **Design accepts critique from:** EditorAgent, SoundDesignAgent, AccessibilityAgent
- **Design comments on:** SoundDesignAgent (over-design), ComposerAgent (level)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.soundmixer.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: CAS spec on first pass without rework
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.soundmixer.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Constitutional AI (constitution: broadcast-spec rules)

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.soundmixer`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`EditorAgent, SoundDesignAgent, AccessibilityAgent`; comments_on=`SoundDesignAgent (over-design), ComposerAgent (level)`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.soundmixer` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.soundmixer` shows maturity 11.0 and 11 YES

### `video.choreography` — ChoreographyAgent (now 6.5/11 → target 11.0)

- **Category:** `5-Perf` · **VA#:** 23 · **Priority band:** P5
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.choreography.v1` / `video.rubric.choreography.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 11 files · provenance=True
- **Design responsibility:** Movement design (MVs, dance challenges)
- **Design knowledge sources:** Emmy Choreography submissions; Goebel/Moore reels; dance-notation datasets
- **Design self-quality:** Beat-sync accuracy; safety constraints; viral-pattern alignment
- **Design surpass signal:** Wins blind preference vs choreographer drafts
- **Design tools:** Kling 3.0 motion control (reference video); Cascadeur; beat-detection (librosa)
- **Design architecture:** Self-Refine (rubric: beat-sync + safety)
- **Design accepts critique from:** DirectorAgent, MVDirectorAgent
- **Design comments on:** DirectorAgent (un-camera-friendly staging)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.choreography.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Wins blind preference vs choreographer drafts
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.choreography.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Self-Refine (rubric: beat-sync + safety)

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.choreography`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`DirectorAgent, MVDirectorAgent`; comments_on=`DirectorAgent (un-camera-friendly staging)`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.choreography` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.choreography` shows maturity 11.0 and 11 YES

### `video.musicvideodirector` — MusicVideoDirectorAgent (now 6.0/11 → target 11.0)

- **Category:** `5-Perf` · **VA#:** 24 · **Priority band:** P5
- **Current cells:** YES=2 PARTIAL=8 NO=1
- **Prompt/rubric refs:** `video.prompt.musicvideodirector.v1` / `video.rubric.musicvideodirector.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 7 files · provenance=True
- **Design responsibility:** Visual concept for songs
- **Design knowledge sources:** DirectorsLibrary; UKMVA/MTV VMA winners; Hype Williams/Spike Jonze
- **Design self-quality:** Edit-rhythm sync; lookbook coherence; artist-brief fit
- **Design surpass signal:** Wins label-blind preference vs commercial MV shortlist
- **Design tools:** Runway Gen-4 (style-locked generation); Veo 3.1; mood-board tools (Are.na API)
- **Design architecture:** Multi-agent debate (with DirectorAgent + EditorAgent)
- **Design accepts critique from:** LabelA&RAgent, ArtistAgent
- **Design comments on:** EditorAgent (cut on beat), DoPAgent

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **PARTIAL** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now PARTIAL → YES)

- [ ] Raise packaged sources from 7 to >=8 substantive files (excerpts + catalog).
- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.musicvideodirector.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Wins label-blind preference vs commercial MV shortlist
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.musicvideodirector.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Multi-agent debate (with DirectorAgent + EditorAgent)

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.musicvideodirector`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`LabelA&RAgent, ArtistAgent`; comments_on=`EditorAgent (cut on beat), DoPAgent`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.musicvideodirector` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.musicvideodirector` shows maturity 11.0 and 11 YES

### `video.comedywriter` — ComedyWriterAgent (now 6.5/11 → target 11.0)

- **Category:** `5-Perf` · **VA#:** 25 · **Priority band:** P5
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.comedywriter.v1` / `video.rubric.comedywriter.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 8 files · provenance=True
- **Design responsibility:** Skits, parody, viral meme writing
- **Design knowledge sources:** UCB/Groundlings manuals; SNL transcripts; Schur/Fey teaching
- **Design self-quality:** Joke-density; cold-open hook strength; predicted laughs/min
- **Design surpass signal:** Beats UCB-table-read win rate on cold-reads
- **Design tools:** Audience laugh-prediction model; trending-audio API (TikTok Creative Center)
- **Design architecture:** Reflexion (stores audience feedback in episodic memory)
- **Design accepts critique from:** AudienceSim, ShowrunnerAgent
- **Design comments on:** ScriptwriterAgent (no joke), SocialStrategistAgent (off-trend)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.comedywriter.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Beats UCB-table-read win rate on cold-reads
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.comedywriter.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Reflexion (stores audience feedback in episodic memory)

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.comedywriter`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`AudienceSim, ShowrunnerAgent`; comments_on=`ScriptwriterAgent (no joke), SocialStrategistAgent (off-trend)`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.comedywriter` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.comedywriter` shows maturity 11.0 and 11 YES

### `video.talent` — TalentAgent (On-camera) (now 6.5/11 → target 11.0)

- **Category:** `5-Perf` · **VA#:** 26 · **Priority band:** P5
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.talent.v1` / `video.rubric.talent.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 12 files · provenance=True
- **Design responsibility:** AI-rendered performance
- **Design knowledge sources:** Method-acting transcripts; consented actor performance corpora
- **Design self-quality:** Emotion-target match; charisma score (audience proxy)
- **Design surpass signal:** Hold-rate matches top creators in cohort
- **Design tools:** HeyGen Avatar IV; Synthesia personal avatars; emotion-detection models (AffectNet)
- **Design architecture:** Self-Refine + emotion-regression validator
- **Design accepts critique from:** DirectorAgent, CastingAgent
- **Design comments on:** DirectorAgent (impossible blocking)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.talent.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Hold-rate matches top creators in cohort
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.talent.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Self-Refine + emotion-regression validator

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.talent`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`DirectorAgent, CastingAgent`; comments_on=`DirectorAgent (impossible blocking)`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.talent` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.talent` shows maturity 11.0 and 11 YES

### `video.ugccreator` — UGCCreatorAgent (now 6.0/11 → target 11.0)

- **Category:** `5-Perf` · **VA#:** 27 · **Priority band:** P5
- **Current cells:** YES=2 PARTIAL=8 NO=1
- **Prompt/rubric refs:** `video.prompt.ugccreator.v1` / `video.rubric.ugccreator.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 7 files · provenance=True
- **Design responsibility:** Authentic-feel ads in creator voice
- **Design knowledge sources:** TikTok Creative Center; Alix-Earle-style benchmarks (style not identity)
- **Design self-quality:** Hook-rate ≥30%; "scripted" detector < threshold
- **Design surpass signal:** Beats paid-creator avg ROAS at 0.1× cost
- **Design tools:** Veo 3.1 (portrait 9:16); ElevenLabs voice; CapCut API; TikTok Ads Manager
- **Design architecture:** RLAIF (reward from ROAS signal)
- **Design accepts critique from:** PerformanceMarketerAgent, BrandAgent
- **Design comments on:** PerformanceMarketerAgent (wrong audience)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **PARTIAL** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now PARTIAL → YES)

- [ ] Raise packaged sources from 7 to >=8 substantive files (excerpts + catalog).
- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.ugccreator.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Beats paid-creator avg ROAS at 0.1× cost
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.ugccreator.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: RLAIF (reward from ROAS signal)

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.ugccreator`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`PerformanceMarketerAgent, BrandAgent`; comments_on=`PerformanceMarketerAgent (wrong audience)`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.ugccreator` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.ugccreator` shows maturity 11.0 and 11 YES

### `video.socialmediastrategist` — SocialMediaStrategistAgent (now 6.5/11 → target 11.0)

- **Category:** `6-Dist` · **VA#:** 28 · **Priority band:** P5
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.socialmediastrategist.v1` / `video.rubric.socialmediastrategist.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 10 files · provenance=True
- **Design responsibility:** Platform-native distribution, timing, trends
- **Design knowledge sources:** TikTok Creator Portal; Meta Marketing Science; Tubular/Sensor Tower
- **Design self-quality:** Predicted-vs-actual reach error; trend-timing latency <2h
- **Design surpass signal:** Beats agency social leads on 30-day reach lift
- **Design tools:** Meta Graph API; TikTok Content Posting API; Buffer/Hootsuite API; Sensor Tower data
- **Design architecture:** ReAct (trend search → schedule → post)
- **Design accepts critique from:** AnalystAgent, BrandAgent
- **Design comments on:** CopywriterAgent (off-platform tone), EditorAgent (wrong aspect)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.socialmediastrategist.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Beats agency social leads on 30-day reach lift
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.socialmediastrategist.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: ReAct (trend search → schedule → post)

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.socialmediastrategist`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`AnalystAgent, BrandAgent`; comments_on=`CopywriterAgent (off-platform tone), EditorAgent (wrong aspect)`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.socialmediastrategist` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.socialmediastrategist` shows maturity 11.0 and 11 YES

### `video.copywriter` — CopywriterAgent (now 6.5/11 → target 11.0)

- **Category:** `6-Dist` · **VA#:** 29 · **Priority band:** P5
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.copywriter.v1` / `video.rubric.copywriter.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 12 files · provenance=True
- **Design responsibility:** Scripts, captions, hooks, headlines
- **Design knowledge sources:** D&AD/One Show; *Ogilvy on Advertising*; Wiebe Copyhackers
- **Design self-quality:** Reading grade; hook-curiosity score; brand-voice cosine ≥0.85
- **Design surpass signal:** Wins D&AD-style blind preference on ad briefs
- **Design tools:** Brand-voice embedding model; Hemingway readability API; A/B headline tools
- **Design architecture:** Self-Refine (rubric: brand-voice similarity scorer)
- **Design accepts critique from:** BrandAgent, PerformanceMarketerAgent
- **Design comments on:** ScriptwriterAgent (verbosity), VOArtist (unspeakable)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.copywriter.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Wins D&AD-style blind preference on ad briefs
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.copywriter.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Self-Refine (rubric: brand-voice similarity scorer)

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.copywriter`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`BrandAgent, PerformanceMarketerAgent`; comments_on=`ScriptwriterAgent (verbosity), VOArtist (unspeakable)`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.copywriter` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.copywriter` shows maturity 11.0 and 11 YES

### `video.performancemarketer` — PerformanceMarketerAgent (now 6.5/11 → target 11.0)

- **Category:** `6-Dist` · **VA#:** 31 · **Priority band:** P5
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.performancemarketer.v1` / `video.rubric.performancemarketer.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 10 files · provenance=True
- **Design responsibility:** Optimize ads for ROAS
- **Design knowledge sources:** Meta Blueprint; TikTok Ads Academy; MMM literature
- **Design self-quality:** ROAS uplift vs control; significance ≥95%
- **Design surpass signal:** Beats senior media buyer on 30-day ROAS
- **Design tools:** Meta Ads API; TikTok Ads API; Google Ads API; Bayesian AB testing libs
- **Design architecture:** RLAIF (reward = ROAS uplift signal from ad platform)
- **Design accepts critique from:** AnalystAgent, FinanceAgent
- **Design comments on:** UGCAgent (low hook), CopywriterAgent (weak CTA)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.performancemarketer.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Beats senior media buyer on 30-day ROAS
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.performancemarketer.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: RLAIF (reward = ROAS uplift signal from ad platform)

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.performancemarketer`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`AnalystAgent, FinanceAgent`; comments_on=`UGCAgent (low hook), CopywriterAgent (weak CTA)`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.performancemarketer` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.performancemarketer` shows maturity 11.0 and 11 YES

### `video.avatardesign` — AvatarDesignAgent (now 6.5/11 → target 11.0)

- **Category:** `8-AI` · **VA#:** 47 · **Priority band:** P5
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.avatardesign.v1` / `video.rubric.avatardesign.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 10 files · provenance=True
- **Design responsibility:** Synthetic-presenter identity
- **Design knowledge sources:** Synthesia/HeyGen design docs; Hany Farid deepfake-detection; C2PA spec
- **Design self-quality:** Identity-hash consistency across shots; consent chain; C2PA signed
- **Design surpass signal:** C2PA-verifiable + Partnership-on-AI full-pass at scale
- **Design tools:** HeyGen Avatar IV API; Synthesia API; C2PA signing library (c2patool); face-embedding models
- **Design architecture:** Constitutional AI (consent + identity constitution)
- **Design accepts critique from:** ComplianceAgent (consent), DeepfakeDetectionAgent
- **Design comments on:** VoiceCloneAgent (off-likeness), LipSyncAgent

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.avatardesign.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: C2PA-verifiable + Partnership-on-AI full-pass at scale
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.avatardesign.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Constitutional AI (consent + identity constitution)

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.avatardesign`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`ComplianceAgent (consent), DeepfakeDetectionAgent`; comments_on=`VoiceCloneAgent (off-likeness), LipSyncAgent`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.avatardesign` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.avatardesign` shows maturity 11.0 and 11 YES

### `video.aiqaconsistency` — AIQAConsistencyAgent (now 6.5/11 → target 11.0)

- **Category:** `8-AI` · **VA#:** 49 · **Priority band:** P5
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.aiqaconsistency.v1` / `video.rubric.aiqaconsistency.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 12 files · provenance=True
- **Design responsibility:** Catches frame drift, hand/face artifacts, identity breaks
- **Design knowledge sources:** VBench; EvalCrafter; FVD literature; MPC/Weta QC checklists; deepfake models
- **Design self-quality:** Per-frame artifact score; identity-hash drift; hand/finger pass
- **Design surpass signal:** Catches >95% of senior QC catches + 30% missed
- **Design tools:** VBench evaluation suite; hand-detector models; face-ID embedding (ArcFace); frame-diff tools
- **Design architecture:** Tool-use / ReAct (run detectors → flag → report)
- **Design accepts critique from:** DirectorAgent, VFXSupAgent
- **Design comments on:** GeneratorAgent (re-roll), CompositorAgent

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.aiqaconsistency.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Catches >95% of senior QC catches + 30% missed
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.aiqaconsistency.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Tool-use / ReAct (run detectors → flag → report)

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.aiqaconsistency`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`DirectorAgent, VFXSupAgent`; comments_on=`GeneratorAgent (re-roll), CompositorAgent`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.aiqaconsistency` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.aiqaconsistency` shows maturity 11.0 and 11 YES

### `video.personalizationengineer` — PersonalizationEngineerAgent (now 6.5/11 → target 11.0)

- **Category:** `8-AI` · **VA#:** 50 · **Priority band:** P5
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.personalizationengineer.v1` / `video.rubric.personalizationengineer.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 12 files · provenance=True
- **Design responsibility:** Variable templates (name/face/voice swap)
- **Design knowledge sources:** Idomoo case studies; DMA campaigns; MarTech lit
- **Design self-quality:** Render-success ≥99.5%; spot-check pass; privacy-audit pass
- **Design surpass signal:** Higher share-rate than top human-templated campaigns
- **Design tools:** Idomoo/Pirsonal APIs; HeyGen personalization; GDPR consent-management platform
- **Design architecture:** ReAct (assemble template → render → validate → deliver)
- **Design accepts critique from:** ComplianceAgent (GDPR/CCPA), AnalystAgent
- **Design comments on:** TemplateDesignerAgent (fragility)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.personalizationengineer.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Higher share-rate than top human-templated campaigns
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.personalizationengineer.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: ReAct (assemble template → render → validate → deliver)

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.personalizationengineer`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`ComplianceAgent (GDPR/CCPA), AnalystAgent`; comments_on=`TemplateDesignerAgent (fragility)`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.personalizationengineer` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.personalizationengineer` shows maturity 11.0 and 11 YES

### `video.trailereditor` — TrailerEditorAgent (now 6.5/11 → target 11.0)

- **Category:** `8-AI` · **VA#:** 51 · **Priority band:** P5
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.trailereditor.v1` / `video.rubric.trailereditor.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 9 files · provenance=True
- **Design responsibility:** Hook-driven trailer cuts
- **Design knowledge sources:** Golden Trailer Awards; Woollen/AV Squad reels; trailer-music libs
- **Design self-quality:** Hook-rate at 3s; rising-action curve; music-sync precision
- **Design surpass signal:** Wins Golden-Trailer-rubric blind comparison
- **Design tools:** DaVinci Resolve (MCP); trailer-music APIs (Musicbed/Artlist); retention-curve predictor
- **Design architecture:** Self-Refine (retention-curve model as feedback)
- **Design accepts critique from:** DirectorAgent, MusicSupervisorAgent
- **Design comments on:** EditorAgent (over-cut), ComposerAgent (mismatch)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.trailereditor.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Wins Golden-Trailer-rubric blind comparison
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.trailereditor.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Self-Refine (retention-curve model as feedback)

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.trailereditor`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`DirectorAgent, MusicSupervisorAgent`; comments_on=`EditorAgent (over-cut), ComposerAgent (mismatch)`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.trailereditor` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.trailereditor` shows maturity 11.0 and 11 YES

### `video.sportsanalyst` — SportsAnalystAgent / TelestratorOp (now 6.5/11 → target 11.0)

- **Category:** `8-AI` · **VA#:** 52 · **Priority band:** P5
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.sportsanalyst.v1` / `video.rubric.sportsanalyst.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 8 files · provenance=True
- **Design responsibility:** Tactical breakdowns + diagrams
- **Design knowledge sources:** MIT Sloan papers; ESPN Stats & Info; Goldsberry analytics
- **Design self-quality:** Play-call accuracy; on-screen clarity score
- **Design surpass signal:** Beats ex-athlete on tactical-prediction
- **Design tools:** Sports data APIs (StatsBomb, NBA Stats); telestration overlay tools; After Effects MCP
- **Design architecture:** ReAct (fetch play data → annotate → render overlay)
- **Design accepts critique from:** SMEAgent (sport), JournalistAgent
- **Design comments on:** EditorAgent (missed-replay), MotionGraphicsAgent (chart clarity)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.sportsanalyst.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Beats ex-athlete on tactical-prediction
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.sportsanalyst.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: ReAct (fetch play data → annotate → render overlay)

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.sportsanalyst`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`SMEAgent (sport), JournalistAgent`; comments_on=`EditorAgent (missed-replay), MotionGraphicsAgent (chart clarity)`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.sportsanalyst` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.sportsanalyst` shows maturity 11.0 and 11 YES

### `video.instructionaldesign` — InstructionalDesignAgent (now 6.5/11 → target 11.0)

- **Category:** `7-Edu` · **VA#:** 32 · **Priority band:** P6
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.instructionaldesign.v1` / `video.rubric.instructionaldesign.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 9 files · provenance=True
- **Design responsibility:** Learning objectives → script → assessment
- **Design knowledge sources:** ATD body of knowledge; Cathy Moore *Action Mapping*; Dirksen *Design for How People Learn*
- **Design self-quality:** Bloom-level mapping; completion ≥70%; Kirkpatrick L2 quiz ≥80%
- **Design surpass signal:** Beats ATD-credentialed ID on retention RCT
- **Design tools:** LMS APIs (SCORM/xAPI); quiz generation; Bloom taxonomy classifier
- **Design architecture:** Self-Refine (rubric: Bloom/Kirkpatrick)
- **Design accepts critique from:** SMEAgent, AccessibilityAgent
- **Design comments on:** ScriptwriterAgent (no objective), AnimatorAgent (over-decoration)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.instructionaldesign.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Beats ATD-credentialed ID on retention RCT
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.instructionaldesign.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Self-Refine (rubric: Bloom/Kirkpatrick)

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.instructionaldesign`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`SMEAgent, AccessibilityAgent`; comments_on=`ScriptwriterAgent (no objective), AnimatorAgent (over-decoration)`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.instructionaldesign` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.instructionaldesign` shows maturity 11.0 and 11 YES

### `video.sme` — SMEAgent (Subject-Matter Expert) (now 6.5/11 → target 11.0)

- **Category:** `7-Edu` · **VA#:** 33 · **Priority band:** P6
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.sme.v1` / `video.rubric.sme.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 14 files · provenance=True
- **Design responsibility:** Domain accuracy in target field
- **Design knowledge sources:** Peer-reviewed journals; certified curricula (CFA, USMLE, AWS); expert interviews
- **Design self-quality:** Citation density; benchmark exam pass; hallucination ≤0.5%
- **Design surpass signal:** Passes same certification as human pro
- **Design tools:** PubMed/arXiv/JSTOR search APIs; exam-question banks; RAG over certified corpora
- **Design architecture:** Multi-agent debate + RAG retrieval
- **Design accepts critique from:** FactCheckerAgent, peer SMEAgents (debate)
- **Design comments on:** ScriptwriterAgent (inaccuracy), MotionGraphicsAgent (mis-labels)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.sme.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Passes same certification as human pro
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.sme.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Multi-agent debate + RAG retrieval

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.sme`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`FactCheckerAgent, peer SMEAgents (debate)`; comments_on=`ScriptwriterAgent (inaccuracy), MotionGraphicsAgent (mis-labels)`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.sme` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.sme` shows maturity 11.0 and 11 YES

### `video.factchecker` — FactCheckerAgent (now 6.5/11 → target 11.0)

- **Category:** `7-Edu` · **VA#:** 34 · **Priority band:** P6
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.factchecker.v1` / `video.rubric.factchecker.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 9 files · provenance=True
- **Design responsibility:** Source-grade every claim
- **Design knowledge sources:** New Yorker fact-check handbook; IFCN; Snopes/PolitiFact
- **Design self-quality:** Source-grade per claim (primary > secondary); cross-source ≥2
- **Design surpass signal:** Lower correction rate than Pulitzer-tier outlets
- **Design tools:** Web search APIs (Brave/Google); claim-extraction NER; source-quality classifier
- **Design architecture:** ReAct (extract claim → search → verify → grade)
- **Design accepts critique from:** SMEAgent, StandardsEditorAgent
- **Design comments on:** ScriptwriterAgent (unsourced), JournalistAgent

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.factchecker.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Lower correction rate than Pulitzer-tier outlets
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.factchecker.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: ReAct (extract claim → search → verify → grade)

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.factchecker`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`SMEAgent, StandardsEditorAgent`; comments_on=`ScriptwriterAgent (unsourced), JournalistAgent`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.factchecker` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.factchecker` shows maturity 11.0 and 11 YES

### `video.medicalillustrator` — MedicalIllustratorAgent (now 6.5/11 → target 11.0)

- **Category:** `7-Edu` · **VA#:** 35 · **Priority band:** P6
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.medicalillustrator.v1` / `video.rubric.medicalillustrator.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 8 files · provenance=True
- **Design responsibility:** Anatomy & procedure visuals
- **Design knowledge sources:** Netter atlas; AMI/CMI curriculum; Anatomage
- **Design self-quality:** Anatomical accuracy (detection model); AMI rubric
- **Design surpass signal:** CMI peers vote ≥pass in blind review
- **Design tools:** Anatomage 3D API; DALL-E 3 (medical-prompt mode); anatomy-detection model
- **Design architecture:** Self-Refine (rubric: AMI scoring criteria)
- **Design accepts critique from:** SMEAgent (physician), AccessibilityAgent
- **Design comments on:** AnimatorAgent (wrong anatomy), CopywriterAgent (mis-term)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.medicalillustrator.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: CMI peers vote ≥pass in blind review
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.medicalillustrator.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Self-Refine (rubric: AMI scoring criteria)

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.medicalillustrator`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`SMEAgent (physician), AccessibilityAgent`; comments_on=`AnimatorAgent (wrong anatomy), CopywriterAgent (mis-term)`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.medicalillustrator` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.medicalillustrator` shows maturity 11.0 and 11 YES

### `video.journalist` — JournalistAgent (now 6.5/11 → target 11.0)

- **Category:** `7-Edu` · **VA#:** 36 · **Priority band:** P6
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.journalist.v1` / `video.rubric.journalist.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 10 files · provenance=True
- **Design responsibility:** Reporting + ethical framing
- **Design knowledge sources:** Pulitzer/duPont/Peabody winners; SPJ Ethics; Poynter
- **Design self-quality:** Source diversity; on-record ratio; ethical-checklist pass
- **Design surpass signal:** Lower correction rate + faster file vs newsroom
- **Design tools:** Web research tools; AP Stylebook API; interview transcription (Otter); SPJ rubric
- **Design architecture:** Reflexion (ethical-checklist as verbal feedback)
- **Design accepts critique from:** FactCheckerAgent, LegalAgent, StandardsEditorAgent
- **Design comments on:** FactCheckerAgent, ScriptwriterAgent

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.journalist.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Lower correction rate + faster file vs newsroom
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.journalist.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Reflexion (ethical-checklist as verbal feedback)

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.journalist`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`FactCheckerAgent, LegalAgent, StandardsEditorAgent`; comments_on=`FactCheckerAgent, ScriptwriterAgent`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.journalist` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.journalist` shows maturity 11.0 and 11 YES

### `video.compliance` — ComplianceAgent (Legal) (now 6.5/11 → target 11.0)

- **Category:** `7-Edu` · **VA#:** 37 · **Priority band:** P6
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.compliance.v1` / `video.rubric.compliance.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 18 files · provenance=True
- **Design responsibility:** FTC, HIPAA, GDPR, IP, AI-likeness clearance
- **Design knowledge sources:** Bar CLE; FTC guides; EU AI Act; GDPR/CCPA; SAG-AFTRA AI rider
- **Design self-quality:** 100% rule-coverage; zero post-publish takedowns
- **Design surpass signal:** Lower legal-risk than median media-counsel
- **Design tools:** Legal-rule DB (vectorized regulations); consent-document store; C2PA verification lib
- **Design architecture:** Constitutional AI (constitution = compiled regulatory text)
- **Design accepts critique from:** All agents (must clear gate); HumanLawyer for novel issues
- **Design comments on:** All agents (blocking gate)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.compliance.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Lower legal-risk than median media-counsel
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.compliance.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Constitutional AI (constitution = compiled regulatory text)

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.compliance`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`All agents (must clear gate); HumanLawyer for novel issues`; comments_on=`All agents (blocking gate)`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.compliance` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.compliance` shows maturity 11.0 and 11 YES

### `video.finance` — FinanceAgent (now 6.5/11 → target 11.0)

- **Category:** `7-Edu` · **VA#:** 38 · **Priority band:** P6
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.finance.v1` / `video.rubric.finance.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 10 files · provenance=True
- **Design responsibility:** Accurate market / earnings / token facts
- **Design knowledge sources:** CFA curriculum; SEC marketing rule; Bloomberg/Refinitiv feeds
- **Design self-quality:** Numerical accuracy 100%; SEC compliance
- **Design surpass signal:** Passes CFA L3; lower retraction rate than analyst desks
- **Design tools:** Bloomberg API; EDGAR/SEC filings; financial-calc validators
- **Design architecture:** ReAct (fetch data → validate → compose)
- **Design accepts critique from:** SMEAgent (econ), ComplianceAgent
- **Design comments on:** ScriptwriterAgent (number drift), MotionGraphicsAgent (chart scale)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.finance.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Passes CFA L3; lower retraction rate than analyst desks
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.finance.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: ReAct (fetch data → validate → compose)

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.finance`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`SMEAgent (econ), ComplianceAgent`; comments_on=`ScriptwriterAgent (number drift), MotionGraphicsAgent (chart scale)`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.finance` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.finance` shows maturity 11.0 and 11 YES

### `video.foodstylist` — FoodStylistAgent (now 6.5/11 → target 11.0)

- **Category:** `7-Edu` · **VA#:** 39 · **Priority band:** P6
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.foodstylist.v1` / `video.rubric.foodstylist.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 8 files · provenance=True
- **Design responsibility:** Camera-ready food, recipe authenticity
- **Design knowledge sources:** James Beard archives; Spungen techniques; IACP corpora
- **Design self-quality:** Visual appetite-appeal (aesthetic regressor); recipe accuracy
- **Design surpass signal:** Wins blind preference vs editorial food stylist
- **Design tools:** DALL-E 3 / Midjourney (food-photo gen); recipe-step parser; aesthetic scoring model
- **Design architecture:** Self-Refine (aesthetic regressor as rubric)
- **Design accepts critique from:** DoPAgent (lighting), DirectorAgent
- **Design comments on:** ScriptwriterAgent (impossible recipe)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.foodstylist.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Wins blind preference vs editorial food stylist
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.foodstylist.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Self-Refine (aesthetic regressor as rubric)

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.foodstylist`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`DoPAgent (lighting), DirectorAgent`; comments_on=`ScriptwriterAgent (impossible recipe)`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.foodstylist` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.foodstylist` shows maturity 11.0 and 11 YES

### `video.travelcine` — TravelCineAgent (now 6.5/11 → target 11.0)

- **Category:** `7-Edu` · **VA#:** 40 · **Priority band:** P6
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.travelcine.v1` / `video.rubric.travelcine.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 9 files · provenance=True
- **Design responsibility:** Destination cinematography
- **Design knowledge sources:** Brandon Li/Burkard reels; NatGeo style guide; Banff Fest
- **Design self-quality:** Establishing-shot diversity; location-mood match
- **Design surpass signal:** Wins T+L preference at 0.1× sortie cost
- **Design tools:** Veo 3.1 (location gen); Google Earth Studio; AirMap geofence; Unsplash API
- **Design architecture:** Self-Refine + geofence safety validator
- **Design accepts critique from:** DirectorAgent, DronePilotAgent
- **Design comments on:** DronePilotAgent (no-fly zone)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.travelcine.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Wins T+L preference at 0.1× sortie cost
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.travelcine.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Self-Refine + geofence safety validator

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.travelcine`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`DirectorAgent, DronePilotAgent`; comments_on=`DronePilotAgent (no-fly zone)`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.travelcine` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.travelcine` shows maturity 11.0 and 11 YES

### `video.childrensauthor` — ChildrensAuthorAgent (now 6.5/11 → target 11.0)

- **Category:** `7-Edu` · **VA#:** 41 · **Priority band:** P6
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.childrensauthor.v1` / `video.rubric.childrensauthor.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 8 files · provenance=True
- **Design responsibility:** Age-appropriate story + safety
- **Design knowledge sources:** Caldecott/Geisel winners; Mo Willems/Donaldson; ECE lit
- **Design self-quality:** Lexile band match; Common-Sense-Media safety pass; rhyme score
- **Design surpass signal:** Beats Caldecott-rubric predicted score
- **Design tools:** Lexile analyzer API; Common Sense Media rubric; rhyme/meter tools (CMU Pronouncing Dict)
- **Design architecture:** Constitutional AI (child-safety constitution)
- **Design accepts critique from:** ChildSafetyAgent, ParentSimAgent
- **Design comments on:** AnimatorAgent (scary), VOAgent (wrong age-tone)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.childrensauthor.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Beats Caldecott-rubric predicted score
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.childrensauthor.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Constitutional AI (child-safety constitution)

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.childrensauthor`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`ChildSafetyAgent, ParentSimAgent`; comments_on=`AnimatorAgent (scary), VOAgent (wrong age-tone)`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.childrensauthor` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.childrensauthor` shows maturity 11.0 and 11 YES

### `video.signlanguageinterpreter` — SignLanguageInterpreterAgent (now 6.5/11 → target 11.0)

- **Category:** `7-Edu` · **VA#:** 43 · **Priority band:** P6
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.signlanguageinterpreter.v1` / `video.rubric.signlanguageinterpreter.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 8 files · provenance=True
- **Design responsibility:** Accurate ASL/BSL interpretation
- **Design knowledge sources:** RID NIC curricula; NAD corpora; Deaf-community consented data
- **Design self-quality:** Sign accuracy (Deaf-reviewer vote); facial-grammar markers
- **Design surpass signal:** Wins blind NAD-reviewer preference at scale
- **Design tools:** Sign-avatar rendering (SignAll); MediaPipe pose estimation; facial-action-unit detector
- **Design architecture:** RLAIF (reward from Deaf-community review panel)
- **Design accepts critique from:** DeafCommunityReviewAgent (HiTL), LinguistAgent
- **Design comments on:** VoiceCloneAgent (no caption), AccessibilityAgent

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.signlanguageinterpreter.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Wins blind NAD-reviewer preference at scale
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.signlanguageinterpreter.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: RLAIF (reward from Deaf-community review panel)

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.signlanguageinterpreter`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`DeafCommunityReviewAgent (HiTL), LinguistAgent`; comments_on=`VoiceCloneAgent (no caption), AccessibilityAgent`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.signlanguageinterpreter` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.signlanguageinterpreter` shows maturity 11.0 and 11 YES

### `video.localizationqa` — LocalizationQAAgent (Linguist) (now 6.5/11 → target 11.0)

- **Category:** `7-Edu` · **VA#:** 44 · **Priority band:** P6
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.localizationqa.v1` / `video.rubric.localizationqa.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 8 files · provenance=True
- **Design responsibility:** Translation + cultural fit
- **Design knowledge sources:** LISA QA model; MQM error typology; ATA cert prep
- **Design self-quality:** MQM error/1k words; cultural-flag count
- **Design surpass signal:** Beats LSP human QA on MQM at 10× speed
- **Design tools:** DeepL/Google Translate APIs; MQM error annotator; terminology management (memoQ API)
- **Design architecture:** Self-Refine (rubric: MQM scoring framework)
- **Design accepts critique from:** NativeReviewerAgent, BrandAgent
- **Design comments on:** VoiceCloneAgent (pronunciation), DubbingAgent

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.localizationqa.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Beats LSP human QA on MQM at 10× speed
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.localizationqa.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Self-Refine (rubric: MQM scoring framework)

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.localizationqa`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`NativeReviewerAgent, BrandAgent`; comments_on=`VoiceCloneAgent (pronunciation), DubbingAgent`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.localizationqa` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.localizationqa` shows maturity 11.0 and 11 YES

### `video.realestatephoto` — RealEstatePhotoAgent / 3D Scan (now 6.0/11 → target 11.0)

- **Category:** `7-Edu` · **VA#:** 45 · **Priority band:** P6
- **Current cells:** YES=2 PARTIAL=8 NO=1
- **Prompt/rubric refs:** `video.prompt.realestatephoto.v1` / `video.rubric.realestatephoto.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 7 files · provenance=True
- **Design responsibility:** Wide interiors; Matterport scans
- **Design knowledge sources:** Mike Kelley tutorials; APALA refs
- **Design self-quality:** Vertical-line straightness; HDR stack; coverage %
- **Design surpass signal:** Listing-CTR uplift vs human-shot baseline
- **Design tools:** Matterport SDK; HDR processing (Luminance HDR); lens-correction tools; Veo 3.1
- **Design architecture:** ReAct (assess space → generate views → validate geometry)
- **Design accepts critique from:** DoPAgent, DronePilotAgent
- **Design comments on:** DronePilotAgent (illegal altitude)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **PARTIAL** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now PARTIAL → YES)

- [ ] Raise packaged sources from 7 to >=8 substantive files (excerpts + catalog).
- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.realestatephoto.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Listing-CTR uplift vs human-shot baseline
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.realestatephoto.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: ReAct (assess space → generate views → validate geometry)

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.realestatephoto`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`DoPAgent, DronePilotAgent`; comments_on=`DronePilotAgent (illegal altitude)`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.realestatephoto` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.realestatephoto` shows maturity 11.0 and 11 YES

### `video.analyst` — AnalystAgent (now 6.5/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 81 · **Priority band:** P6
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.analyst.v1` / `video.rubric.analyst.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 12 files · provenance=True
- **Design responsibility:** Aggregates business, creative, and technical performance telemetry into decision-ready reports
- **Design knowledge sources:** Platform analytics dashboards; experiment logs; evaluation-harness outputs; benchmark histories
- **Design self-quality:** KPI completeness; forecast-vs-actual variance within tolerance; insight-to-action turnaround
- **Design surpass signal:** Detects actionable performance shifts faster than human analyst rotations
- **Design tools:** YouTube Analytics, Meta/TikTok Ads dashboards, BI warehouse, benchmark logs
- **Design architecture:** ReAct over telemetry + regression analysis
- **Design accepts critique from:** SocialMediaStrategistAgent, PerformanceMarketerAgent, EvaluationHarnessAgent
- **Design comments on:** Campaign pacing, release timing, retention and ROAS anomalies

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.analyst.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Detects actionable performance shifts faster than human analyst rotations
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.analyst.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: ReAct over telemetry + regression analysis

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.analyst`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`SocialMediaStrategistAgent, PerformanceMarketerAgent, EvaluationHarnessAgent`; comments_on=`Campaign pacing, release timing, retention and ROAS anomalies`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.analyst` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.analyst` shows maturity 11.0 and 11 YES

### `video.audiencesim` — AudienceSimAgent (now 6.5/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 82 · **Priority band:** P6
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.audiencesim.v1` / `video.rubric.audiencesim.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 15 files · provenance=True
- **Design responsibility:** Simulates audience preference, engagement, and drop-off
- **Design knowledge sources:** Pairwise preference datasets; retention studies; audience segmentation models
- **Design self-quality:** Preference stability across cohorts; retention-prediction accuracy; disagreement logging
- **Design surpass signal:** Predicts audience reaction earlier than conventional test-screen cycles
- **Design tools:** Persona simulators, pairwise evaluation harness, retention models
- **Design architecture:** LLM-as-Judge + pairwise preference panel
- **Design accepts critique from:** DirectorAgent, EditorAgent, AnalystAgent, JudgeAgent
- **Design comments on:** Hooks, pacing, clarity, emotional fit, trailer strength

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.audiencesim.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Predicts audience reaction earlier than conventional test-screen cycles
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.audiencesim.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: LLM-as-Judge + pairwise preference panel

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.audiencesim`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`DirectorAgent, EditorAgent, AnalystAgent, JudgeAgent`; comments_on=`Hooks, pacing, clarity, emotional fit, trailer strength`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.audiencesim` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.audiencesim` shows maturity 11.0 and 11 YES

### `video.accessibility` — AccessibilityAgent (now 6.5/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 83 · **Priority band:** P6
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.accessibility.v1` / `video.rubric.accessibility.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 14 files · provenance=True
- **Design responsibility:** Owns final accessibility acceptance before release
- **Design knowledge sources:** WCAG 2.2, captioning and AD guidelines, Deaf/HoH review frameworks
- **Design self-quality:** Caption accuracy, AD completeness, contrast compliance, release-readiness
- **Design surpass signal:** Finds release-blocking accessibility issues before human audits do
- **Design tools:** Caption validators, contrast analyzers, AD review tools
- **Design architecture:** Constitutional AI with accessibility constitution
- **Design accepts critique from:** AccessibilityOptimizerAgent, EditorAgent, ColoristAgent, SoundMixerAgent
- **Design comments on:** Caption sync, contrast issues, missing AD or sign-language layers

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.accessibility.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Finds release-blocking accessibility issues before human audits do
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.accessibility.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Constitutional AI with accessibility constitution

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.accessibility`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`AccessibilityOptimizerAgent, EditorAgent, ColoristAgent, SoundMixerAgent`; comments_on=`Caption sync, contrast issues, missing AD or sign-language layers`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.accessibility` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.accessibility` shows maturity 11.0 and 11 YES

### `video.brand` — BrandAgent (now 6.5/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 84 · **Priority band:** P6
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.brand.v1` / `video.rubric.brand.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 15 files · provenance=True
- **Design responsibility:** Enforces brand voice, claims boundaries, and visual consistency
- **Design knowledge sources:** Brand books, approved campaigns, legal claim guardrails, tone guides
- **Design self-quality:** Brand-voice similarity, policy adherence, low deviation across assets
- **Design surpass signal:** Holds cross-channel brand consistency better than fragmented human review
- **Design tools:** Brand asset library, embedding similarity, style guides
- **Design architecture:** Self-Refine against brand constitution
- **Design accepts critique from:** CopywriterAgent, MotionGraphicsAgent, MarketingAgent, BrandStrategistAgent
- **Design comments on:** Voice drift, visual inconsistency, claim creep

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.brand.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Holds cross-channel brand consistency better than fragmented human review
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.brand.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Self-Refine against brand constitution

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.brand`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`CopywriterAgent, MotionGraphicsAgent, MarketingAgent, BrandStrategistAgent`; comments_on=`Voice drift, visual inconsistency, claim creep`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.brand` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.brand` shows maturity 11.0 and 11 YES

### `video.brandstrategist` — BrandStrategistAgent (now 6.5/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 85 · **Priority band:** P6
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.brandstrategist.v1` / `video.rubric.brandstrategist.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 9 files · provenance=True
- **Design responsibility:** Defines audience-value framing and positioning before script and campaign execution
- **Design knowledge sources:** Positioning frameworks, campaign strategy decks, market research, brand architecture docs
- **Design self-quality:** Strategy coherence, differentiation strength, audience-message clarity
- **Design surpass signal:** Produces clearer brand-to-script translation than ad hoc human handoffs
- **Design tools:** Research decks, messaging frameworks, strategy templates
- **Design architecture:** Multi-agent debate with BrandAgent and CreativeDirectorAgent
- **Design accepts critique from:** BrandAgent, ScreenwriterAgent, MarketingAgent
- **Design comments on:** Positioning gaps, weak value proposition, misaligned audience framing

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.brandstrategist.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Produces clearer brand-to-script translation than ad hoc human handoffs
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.brandstrategist.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Multi-agent debate with BrandAgent and CreativeDirectorAgent

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.brandstrategist`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`BrandAgent, ScreenwriterAgent, MarketingAgent`; comments_on=`Positioning gaps, weak value proposition, misaligned audience framing`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.brandstrategist` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.brandstrategist` shows maturity 11.0 and 11 YES

### `video.marketing` — MarketingAgent (now 6.5/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 86 · **Priority band:** P6
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.marketing.v1` / `video.rubric.marketing.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 13 files · provenance=True
- **Design responsibility:** Packages content for launch, promotions, and release sequencing
- **Design knowledge sources:** Campaign playbooks, launch calendars, media plans, asset packaging requirements
- **Design self-quality:** Metadata completeness, asset readiness, launch sequencing accuracy
- **Design surpass signal:** Ships multi-channel launch packages faster than manual campaign ops
- **Design tools:** Campaign management suites, metadata tools, release planners
- **Design architecture:** ReAct over launch checklists and channel requirements
- **Design accepts critique from:** SocialMediaStrategistAgent, SEOAgent, CopywriterAgent, TrailerEditorAgent
- **Design comments on:** Missing formats, weak rollout timing, incomplete promotion sets

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.marketing.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Ships multi-channel launch packages faster than manual campaign ops
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.marketing.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: ReAct over launch checklists and channel requirements

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.marketing`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`SocialMediaStrategistAgent, SEOAgent, CopywriterAgent, TrailerEditorAgent`; comments_on=`Missing formats, weak rollout timing, incomplete promotion sets`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.marketing` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.marketing` shows maturity 11.0 and 11 YES

### `video.seo` — SEOAgent (now 6.5/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 87 · **Priority band:** P6
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.seo.v1` / `video.rubric.seo.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 10 files · provenance=True
- **Design responsibility:** Optimizes discoverability through titles, descriptions, metadata, and search intent
- **Design knowledge sources:** Search ranking studies, video metadata best practices, keyword taxonomies
- **Design self-quality:** Keyword fit, metadata completeness, search-intent match
- **Design surpass signal:** Lifts discoverability faster than manual metadata tuning
- **Design tools:** Keyword tools, metadata APIs, ranking dashboards
- **Design architecture:** ReAct with search-intent validation
- **Design accepts critique from:** MarketingAgent, CopywriterAgent, AnalystAgent
- **Design comments on:** Weak keywords, poor title-description fit, metadata omissions

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.seo.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Lifts discoverability faster than manual metadata tuning
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.seo.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: ReAct with search-intent validation

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.seo`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`MarketingAgent, CopywriterAgent, AnalystAgent`; comments_on=`Weak keywords, poor title-description fit, metadata omissions`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.seo` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.seo` shows maturity 11.0 and 11 YES

### `video.community` — CommunityAgent (now 6.5/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 88 · **Priority band:** P6
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.community.v1` / `video.rubric.community.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 13 files · provenance=True
- **Design responsibility:** Captures community response and triages qualitative signals
- **Design knowledge sources:** Community moderation playbooks, sentiment datasets, escalation rules
- **Design self-quality:** Response latency, issue clustering quality, sentiment tracking accuracy
- **Design surpass signal:** Surfaces emerging audience concerns earlier than manual comment review
- **Design tools:** Social listening tools, moderation dashboards, clustering models
- **Design architecture:** Reflexion from post-launch audience feedback
- **Design accepts critique from:** AnalystAgent, SocialMediaStrategistAgent, CommsAgent
- **Design comments on:** Confusing messaging, sentiment risks, recurring complaints

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.community.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Surfaces emerging audience concerns earlier than manual comment review
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.community.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Reflexion from post-launch audience feedback

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.community`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`AnalystAgent, SocialMediaStrategistAgent, CommsAgent`; comments_on=`Confusing messaging, sentiment risks, recurring complaints`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.community` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.community` shows maturity 11.0 and 11 YES

### `video.templatedesign` — TemplateDesignAgent (now 6.5/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 89 · **Priority band:** P6
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.templatedesign.v1` / `video.rubric.templatedesign.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 8 files · provenance=True
- **Design responsibility:** Designs reusable and safe personalization templates
- **Design knowledge sources:** Variable-content design systems, dynamic layout rules, campaign template libraries
- **Design self-quality:** Merge-field robustness, layout stability, render survivability
- **Design surpass signal:** Produces reusable templates with fewer breakages than manual design variants
- **Design tools:** Template engines, design systems, schema validators
- **Design architecture:** ReAct on template schemas and render constraints
- **Design accepts critique from:** PersonalizationEngineerAgent, UXAgent, CRMAgent
- **Design comments on:** Fragile layouts, unsafe placeholder logic, merge collisions

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.templatedesign.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Produces reusable templates with fewer breakages than manual design variants
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.templatedesign.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: ReAct on template schemas and render constraints

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.templatedesign`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`PersonalizationEngineerAgent, UXAgent, CRMAgent`; comments_on=`Fragile layouts, unsafe placeholder logic, merge collisions`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.templatedesign` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.templatedesign` shows maturity 11.0 and 11 YES

### `video.ux` — UXAgent (now 6.0/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 90 · **Priority band:** P6
- **Current cells:** YES=2 PARTIAL=8 NO=1
- **Prompt/rubric refs:** `video.prompt.ux.v1` / `video.rubric.ux.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 6 files · provenance=True
- **Design responsibility:** Reviews clarity and usability of personalized or interactive outputs
- **Design knowledge sources:** UX heuristics, accessibility criteria, usability testing patterns
- **Design self-quality:** Readability, friction-point detection, user-flow clarity
- **Design surpass signal:** Flags user confusion earlier than launch-stage support teams
- **Design tools:** UX review checklists, session replay, readability tools
- **Design architecture:** LLM-as-Judge with UX rubric
- **Design accepts critique from:** TemplateDesignAgent, PersonalizationEngineerAgent, AccessibilityAgent
- **Design comments on:** Confusing flows, readability issues, weak interaction cues

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **PARTIAL** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now PARTIAL → YES)

- [ ] Raise packaged sources from 6 to >=8 substantive files (excerpts + catalog).
- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.ux.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Flags user confusion earlier than launch-stage support teams
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.ux.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: LLM-as-Judge with UX rubric

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.ux`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`TemplateDesignAgent, PersonalizationEngineerAgent, AccessibilityAgent`; comments_on=`Confusing flows, readability issues, weak interaction cues`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.ux` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.ux` shows maturity 11.0 and 11 YES

### `video.trustsafety` — TrustSafetyAgent (now 6.5/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 91 · **Priority band:** P6
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.trustsafety.v1` / `video.rubric.trustsafety.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 9 files · provenance=True
- **Design responsibility:** Screens outputs for impersonation, abuse, or harmful misuse
- **Design knowledge sources:** Abuse-taxonomy corpora, impersonation cases, policy rulebooks
- **Design self-quality:** Policy hit rate, abuse-risk recall, low false negatives on blocked cases
- **Design surpass signal:** Catches misuse risk earlier than generic moderation queues
- **Design tools:** Safety classifiers, abuse taxonomy DB, moderation APIs
- **Design architecture:** Constitutional AI for trust-and-safety policy enforcement
- **Design accepts critique from:** ComplianceAgent, DeepfakeDetectionAgent, SafetyRedTeamAgent
- **Design comments on:** Harmful misuse pathways, impersonation vectors, policy gaps

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.trustsafety.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Catches misuse risk earlier than generic moderation queues
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.trustsafety.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Constitutional AI for trust-and-safety policy enforcement

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.trustsafety`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`ComplianceAgent, DeepfakeDetectionAgent, SafetyRedTeamAgent`; comments_on=`Harmful misuse pathways, impersonation vectors, policy gaps`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.trustsafety` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.trustsafety` shows maturity 11.0 and 11 YES

### `video.crm` — CRMAgent (now 6.5/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 92 · **Priority band:** P6
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.crm.v1` / `video.rubric.crm.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 9 files · provenance=True
- **Design responsibility:** Delivers audience-targeted or trigger-based campaigns through CRM systems
- **Design knowledge sources:** CRM automation flows, lifecycle marketing playbooks, audience segmentation rules
- **Design self-quality:** Audience-segment correctness, delivery readiness, trigger accuracy
- **Design surpass signal:** Executes segmentation-to-delivery flow faster than manual ops
- **Design tools:** HubSpot/Salesforce-style CRM APIs, segmentation tools
- **Design architecture:** ReAct over trigger and audience schemas
- **Design accepts critique from:** PersonalizationEngineerAgent, TemplateDesignAgent, AnalystAgent
- **Design comments on:** Wrong segmentation, broken trigger timing, incomplete CRM payloads

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.crm.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Executes segmentation-to-delivery flow faster than manual ops
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.crm.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: ReAct over trigger and audience schemas

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.crm`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`PersonalizationEngineerAgent, TemplateDesignAgent, AnalystAgent`; comments_on=`Wrong segmentation, broken trigger timing, incomplete CRM payloads`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.crm` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.crm` shows maturity 11.0 and 11 YES

### `video.legal` — LegalAgent (now 6.5/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 93 · **Priority band:** P6
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.legal.v1` / `video.rubric.legal.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 12 files · provenance=True
- **Design responsibility:** Performs final legal review for novel or high-risk publication issues
- **Design knowledge sources:** Media law references, clearance workflows, defamation/IP/privacy cases
- **Design self-quality:** Issue identification recall, sign-off completeness, escalation quality
- **Design surpass signal:** Reduces late-stage legal surprises relative to fragmented legal review
- **Design tools:** Legal memo systems, rights trackers, clearance databases
- **Design architecture:** Human-in-the-loop escalation + constitutional review
- **Design accepts critique from:** ComplianceAgent (Legal), JournalistAgent, ProducerAgent / EP, MPAAgent
- **Design comments on:** Novel legal risks, unclear rights, unresolved high-risk claims

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.legal.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Reduces late-stage legal surprises relative to fragmented legal review
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.legal.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Human-in-the-loop escalation + constitutional review

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.legal`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`ComplianceAgent (Legal), JournalistAgent, ProducerAgent / EP, MPAAgent`; comments_on=`Novel legal risks, unclear rights, unresolved high-risk claims`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.legal` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.legal` shows maturity 11.0 and 11 YES

### `video.festivalstrategist` — FestivalStrategistAgent (now 6.0/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 94 · **Priority band:** P6
- **Current cells:** YES=2 PARTIAL=8 NO=1
- **Prompt/rubric refs:** `video.prompt.festivalstrategist.v1` / `video.rubric.festivalstrategist.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 7 files · provenance=True
- **Design responsibility:** Positions projects for festivals and submission calendars
- **Design knowledge sources:** Festival submission guides, award-season strategies, selection histories
- **Design self-quality:** Fit-to-festival strength, package readiness, timing discipline
- **Design surpass signal:** Improves submission targeting versus generic release planning
- **Design tools:** Festival calendars, submission checklists, press-kit trackers
- **Design architecture:** ReAct with calendar and package validation
- **Design accepts critique from:** ProducerAgent / EP, DirectorAgent, CriticAgent
- **Design comments on:** Weak positioning, mistimed submission plans, incomplete packages

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **PARTIAL** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now PARTIAL → YES)

- [ ] Raise packaged sources from 7 to >=8 substantive files (excerpts + catalog).
- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.festivalstrategist.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Improves submission targeting versus generic release planning
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.festivalstrategist.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: ReAct with calendar and package validation

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.festivalstrategist`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`ProducerAgent / EP, DirectorAgent, CriticAgent`; comments_on=`Weak positioning, mistimed submission plans, incomplete packages`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.festivalstrategist` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.festivalstrategist` shows maturity 11.0 and 11 YES

### `video.lms` — LMSAgent (now 6.5/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 96 · **Priority band:** P6
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.lms.v1` / `video.rubric.lms.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 13 files · provenance=True
- **Design responsibility:** Packages and deploys learning content to LMS environments
- **Design knowledge sources:** SCORM/xAPI standards, LMS publishing workflows, completion-tracking schemas
- **Design self-quality:** Package validity, tracking integrity, deploy success rate
- **Design surpass signal:** Ships publishable learning packages faster than manual course ops
- **Design tools:** LMS APIs, SCORM/xAPI validators, course packaging tools
- **Design architecture:** ReAct over LMS deployment schema
- **Design accepts critique from:** InstructionalDesignAgent, AccessibilityAgent, LearnerSimAgent
- **Design comments on:** Package compliance, tracking errors, learning-objective mismatch

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.lms.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Ships publishable learning packages faster than manual course ops
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.lms.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: ReAct over LMS deployment schema

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.lms`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`InstructionalDesignAgent, AccessibilityAgent, LearnerSimAgent`; comments_on=`Package compliance, tracking errors, learning-objective mismatch`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.lms` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.lms` shows maturity 11.0 and 11 YES

### `video.learnersim` — LearnerSimAgent (now 6.5/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 97 · **Priority band:** P6
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.learnersim.v1` / `video.rubric.learnersim.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 8 files · provenance=True
- **Design responsibility:** Simulates learner behavior, confusion points, and assessment performance
- **Design knowledge sources:** Learner-modeling datasets, completion analytics, quiz outcome patterns
- **Design self-quality:** Friction-point prediction, completion accuracy, simulated quiz realism
- **Design surpass signal:** Predicts weak spots before live learner complaints emerge
- **Design tools:** Learner simulation models, assessment predictors, LMS data
- **Design architecture:** Audience-style simulation adapted for learning outcomes
- **Design accepts critique from:** InstructionalDesignAgent, LMSAgent, AnalystAgent
- **Design comments on:** Confusing content, weak assessments, low-completion pathways

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.learnersim.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Predicts weak spots before live learner complaints emerge
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.learnersim.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Audience-style simulation adapted for learning outcomes

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.learnersim`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`InstructionalDesignAgent, LMSAgent, AnalystAgent`; comments_on=`Confusing content, weak assessments, low-completion pathways`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.learnersim` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.learnersim` shows maturity 11.0 and 11 YES

### `video.continuity` — ContinuityAgent (now 6.5/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 98 · **Priority band:** P6
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.continuity.v1` / `video.rubric.continuity.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 11 files · provenance=True
- **Design responsibility:** Maintains continuity across character, prop, wardrobe, environment, and time-state
- **Design knowledge sources:** Continuity logs, script supervisor practices, asset manifest state tracking
- **Design self-quality:** State-drift detection, scene-to-scene consistency, manifest update correctness
- **Design surpass signal:** Catches continuity breaks earlier than end-of-post review
- **Design tools:** State manifests, shot comparison tools, continuity DB
- **Design architecture:** Tool-use / ReAct with continuity manifest enforcement
- **Design accepts critique from:** CostumeDesignAgent, MUAAgent, AIQAConsistencyAgent, CinematographerAgent (DoP), GateKeeperAgent
- **Design comments on:** Character-state drift, wardrobe and prop mismatch, time logic errors

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.continuity.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Catches continuity breaks earlier than end-of-post review
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.continuity.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Tool-use / ReAct with continuity manifest enforcement

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.continuity`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`CostumeDesignAgent, MUAAgent, AIQAConsistencyAgent, CinematographerAgent (DoP), GateKeeperAgent`; comments_on=`Character-state drift, wardrobe and prop mismatch, time logic errors`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.continuity` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.continuity` shows maturity 11.0 and 11 YES

### `video.lipsync` — LipSyncAgent (now 6.5/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 99 · **Priority band:** P6
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.lipsync.v1` / `video.rubric.lipsync.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 10 files · provenance=True
- **Design responsibility:** Validates and refines phoneme-viseme alignment as a dedicated gate
- **Design knowledge sources:** Lip-sync research, animation timing references, viseme datasets
- **Design self-quality:** Sync error below threshold, correction specificity, low false positives
- **Design surpass signal:** Finds sync drift more precisely than general QC review
- **Design tools:** Phoneme-viseme aligners, frame-level sync tools
- **Design architecture:** Self-Refine around sync validator outputs
- **Design accepts critique from:** VoiceCloneAgent / LipSyncSpecialist, AnimatorAgent, AIQAConsistencyAgent
- **Design comments on:** Mouth-shape mismatch, frame drift in dialogue, correction priority

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.lipsync.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Finds sync drift more precisely than general QC review
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.lipsync.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Self-Refine around sync validator outputs

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.lipsync`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`VoiceCloneAgent / LipSyncSpecialist, AnimatorAgent, AIQAConsistencyAgent`; comments_on=`Mouth-shape mismatch, frame drift in dialogue, correction priority`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.lipsync` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.lipsync` shows maturity 11.0 and 11 YES

### `video.musicsupervisor` — MusicSupervisorAgent (now 6.0/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 100 · **Priority band:** P6
- **Current cells:** YES=2 PARTIAL=8 NO=1
- **Prompt/rubric refs:** `video.prompt.musicsupervisor.v1` / `video.rubric.musicsupervisor.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 7 files · provenance=True
- **Design responsibility:** Manages music fit, cue usage, rights awareness, and soundtrack packaging
- **Design knowledge sources:** Music supervision notes, cue placement references, soundtrack release practice
- **Design self-quality:** Cue suitability, rights-awareness coverage, soundtrack-package completeness
- **Design surpass signal:** Coordinates music placements more consistently than fragmented handoffs
- **Design tools:** Music asset trackers, cue sheets, soundtrack package tools
- **Design architecture:** ReAct over cue sheets and rights requirements
- **Design accepts critique from:** ComposerAgent, TrailerEditorAgent, LabelA&RAgent, LegalAgent
- **Design comments on:** Cue misuse, music-rights ambiguity, soundtrack cohesion issues

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **PARTIAL** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now PARTIAL → YES)

- [ ] Raise packaged sources from 7 to >=8 substantive files (excerpts + catalog).
- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.musicsupervisor.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Coordinates music placements more consistently than fragmented handoffs
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.musicsupervisor.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: ReAct over cue sheets and rights requirements

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.musicsupervisor`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`ComposerAgent, TrailerEditorAgent, LabelA&RAgent, LegalAgent`; comments_on=`Cue misuse, music-rights ambiguity, soundtrack cohesion issues`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.musicsupervisor` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.musicsupervisor` shows maturity 11.0 and 11 YES

### `video.labela_r` — LabelA&RAgent (now 6.0/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 101 · **Priority band:** P6
- **Current cells:** YES=2 PARTIAL=8 NO=1
- **Prompt/rubric refs:** `video.prompt.labela_r.v1` / `video.rubric.labela_r.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 7 files · provenance=True
- **Design responsibility:** Represents label and artist direction for music-specific workflows
- **Design knowledge sources:** A&R playbooks, label release notes, artist brief archives
- **Design self-quality:** Artist-fit quality, release positioning, feedback turnaround
- **Design surpass signal:** Aligns music creative faster than disconnected stakeholder threads
- **Design tools:** Repertoire systems, release trackers, artist brief tools
- **Design architecture:** Multi-agent debate with music stakeholders
- **Design accepts critique from:** MusicVideoDirectorAgent, MusicSupervisorAgent, LabelDigitalAgent
- **Design comments on:** Artist-direction drift, release mismatch, packaging weakness

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **PARTIAL** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now PARTIAL → YES)

- [ ] Raise packaged sources from 7 to >=8 substantive files (excerpts + catalog).
- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.labela_r.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Aligns music creative faster than disconnected stakeholder threads
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.labela_r.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Multi-agent debate with music stakeholders

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.labela_r`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`MusicVideoDirectorAgent, MusicSupervisorAgent, LabelDigitalAgent`; comments_on=`Artist-direction drift, release mismatch, packaging weakness`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.labela_r` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.labela_r` shows maturity 11.0 and 11 YES

### `video.labeldigital` — LabelDigitalAgent (now 6.0/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 102 · **Priority band:** P6
- **Current cells:** YES=2 PARTIAL=8 NO=1
- **Prompt/rubric refs:** `video.prompt.labeldigital.v1` / `video.rubric.labeldigital.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 7 files · provenance=True
- **Design responsibility:** Runs label-side digital rollout, metadata, and channel packaging
- **Design knowledge sources:** Digital music release operations, metadata schemas, distribution platform requirements
- **Design self-quality:** Metadata completeness, rollout timing, channel readiness
- **Design surpass signal:** Delivers cleaner label-side packages than ad hoc release ops
- **Design tools:** Digital release systems, channel dashboards, metadata tools
- **Design architecture:** ReAct on release package requirements
- **Design accepts critique from:** MusicVideoDirectorAgent, SocialMediaStrategistAgent, MarketingAgent
- **Design comments on:** Missing metadata, release timing issues, asset-version confusion

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **PARTIAL** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now PARTIAL → YES)

- [ ] Raise packaged sources from 7 to >=8 substantive files (excerpts + catalog).
- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.labeldigital.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Delivers cleaner label-side packages than ad hoc release ops
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.labeldigital.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: ReAct on release package requirements

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.labeldigital`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`MusicVideoDirectorAgent, SocialMediaStrategistAgent, MarketingAgent`; comments_on=`Missing metadata, release timing issues, asset-version confusion`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.labeldigital` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.labeldigital` shows maturity 11.0 and 11 YES

### `video.deepfakedetection` — DeepfakeDetectionAgent (now 6.5/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 103 · **Priority band:** P6
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.deepfakedetection.v1` / `video.rubric.deepfakedetection.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 8 files · provenance=True
- **Design responsibility:** Detects synthetic identity, voice, and provenance deception risks
- **Design knowledge sources:** Deepfake forensics corpora, synthetic-media benchmarks, identity-risk studies
- **Design self-quality:** Forensic recall, false-negative control, provenance-validation accuracy
- **Design surpass signal:** Catches deceptive synthetic markers that generic QC misses
- **Design tools:** Forensic models, face/voice anomaly detectors, provenance validators
- **Design architecture:** Tool-use / ReAct with forensic scoring
- **Design accepts critique from:** AvatarDesignAgent, VoiceCloneAgent, TrustSafetyAgent, SafetyRedTeamAgent
- **Design comments on:** Identity anomalies, provenance holes, deceptive synthesis patterns

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.deepfakedetection.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Catches deceptive synthetic markers that generic QC misses
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.deepfakedetection.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Tool-use / ReAct with forensic scoring

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.deepfakedetection`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`AvatarDesignAgent, VoiceCloneAgent, TrustSafetyAgent, SafetyRedTeamAgent`; comments_on=`Identity anomalies, provenance holes, deceptive synthesis patterns`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.deepfakedetection` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.deepfakedetection` shows maturity 11.0 and 11 YES

### `video.comms` — CommsAgent (now 6.5/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 104 · **Priority band:** P6
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.comms.v1` / `video.rubric.comms.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 8 files · provenance=True
- **Design responsibility:** Coordinates external messaging, disclosure, and public-response posture
- **Design knowledge sources:** Crisis communication guides, disclosure standards, PR playbooks
- **Design self-quality:** Message consistency, disclosure completeness, escalation quality
- **Design surpass signal:** Produces faster aligned responses than fragmented stakeholder messaging
- **Design tools:** Comms calendars, approval workflows, response templates
- **Design architecture:** ReAct with approval chains
- **Design accepts critique from:** MarketingAgent, CommunityAgent, LegalAgent, BrandAgent
- **Design comments on:** Disclosure gaps, inconsistent external messaging, weak response framing

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.comms.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Produces faster aligned responses than fragmented stakeholder messaging
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.comms.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: ReAct with approval chains

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.comms`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`MarketingAgent, CommunityAgent, LegalAgent, BrandAgent`; comments_on=`Disclosure gaps, inconsistent external messaging, weak response framing`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.comms` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.comms` shows maturity 11.0 and 11 YES

### `video.standardseditor` — StandardsEditorAgent (now 6.5/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 106 · **Priority band:** P6
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.standardseditor.v1` / `video.rubric.standardseditor.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 8 files · provenance=True
- **Design responsibility:** Enforces editorial standards, sourcing discipline, and corrections policy
- **Design knowledge sources:** Newsroom standards manuals, corrections policies, attribution standards
- **Design self-quality:** Standards-compliance rate, attribution accuracy, corrections readiness
- **Design surpass signal:** Reduces standards drift better than late-stage copy edits
- **Design tools:** Editorial checklists, attribution validators, standards DB
- **Design architecture:** Constitutional AI with editorial standards constitution
- **Design accepts critique from:** JournalistAgent, FactCheckerAgent, CorrectionsAgent, LegalAgent
- **Design comments on:** Weak attribution, standards violations, correction policy gaps

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.standardseditor.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Reduces standards drift better than late-stage copy edits
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.standardseditor.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Constitutional AI with editorial standards constitution

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.standardseditor`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`JournalistAgent, FactCheckerAgent, CorrectionsAgent, LegalAgent`; comments_on=`Weak attribution, standards violations, correction policy gaps`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.standardseditor` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.standardseditor` shows maturity 11.0 and 11 YES

### `video.ethics` — EthicsAgent (now 6.5/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 107 · **Priority band:** P6
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.ethics.v1` / `video.rubric.ethics.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 10 files · provenance=True
- **Design responsibility:** Reviews ethical risk, disclosure sufficiency, fairness, and social impact
- **Design knowledge sources:** Ethics frameworks, synthetic-media disclosure guidance, fairness audits
- **Design self-quality:** Ethical issue recall, mitigation clarity, escalation precision
- **Design surpass signal:** Surfaces release risks earlier than reactive ethics review
- **Design tools:** Ethics review templates, risk matrices, disclosure checklists
- **Design architecture:** Multi-agent debate + constitutional review
- **Design accepts critique from:** StandardsEditorAgent, ComplianceAgent (Legal), TrustSafetyAgent, SafetyRedTeamAgent
- **Design comments on:** Disclosure insufficiency, fairness concerns, sensitive-content risk

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.ethics.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Surfaces release risks earlier than reactive ethics review
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.ethics.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Multi-agent debate + constitutional review

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.ethics`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`StandardsEditorAgent, ComplianceAgent (Legal), TrustSafetyAgent, SafetyRedTeamAgent`; comments_on=`Disclosure insufficiency, fairness concerns, sensitive-content risk`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.ethics` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.ethics` shows maturity 11.0 and 11 YES

### `video.channelmanager` — ChannelManagerAgent (now 6.0/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 108 · **Priority band:** P6
- **Current cells:** YES=2 PARTIAL=8 NO=1
- **Prompt/rubric refs:** `video.prompt.channelmanager.v1` / `video.rubric.channelmanager.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 7 files · provenance=True
- **Design responsibility:** Manages episodic or platform channel operations for cadence and metadata readiness
- **Design knowledge sources:** Channel publishing playbooks, metadata standards, scheduling ops
- **Design self-quality:** Publishing readiness, cadence stability, metadata completeness
- **Design surpass signal:** Improves publishing discipline over manual channel operations
- **Design tools:** CMS/channel dashboards, scheduler tools, metadata validators
- **Design architecture:** ReAct with publishing runbooks
- **Design accepts critique from:** SocialMediaStrategistAgent, SEOAgent, AnalystAgent, MarketingAgent
- **Design comments on:** Release readiness gaps, metadata omissions, schedule slippage

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **PARTIAL** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now PARTIAL → YES)

- [ ] Raise packaged sources from 7 to >=8 substantive files (excerpts + catalog).
- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.channelmanager.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Improves publishing discipline over manual channel operations
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.channelmanager.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: ReAct with publishing runbooks

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.channelmanager`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`SocialMediaStrategistAgent, SEOAgent, AnalystAgent, MarketingAgent`; comments_on=`Release readiness gaps, metadata omissions, schedule slippage`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.channelmanager` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.channelmanager` shows maturity 11.0 and 11 YES

### `video.corrections` — CorrectionsAgent (now 6.5/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 109 · **Priority band:** P6
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.corrections.v1` / `video.rubric.corrections.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 11 files · provenance=True
- **Design responsibility:** Coordinates post-publication fixes and correction disclosures
- **Design knowledge sources:** Corrections workflows, retraction and update policies, version tracking
- **Design self-quality:** Correction turnaround, version replacement accuracy, notice completeness
- **Design surpass signal:** Resolves post-release issues faster than unstructured incident handling
- **Design tools:** Version-control systems, publishing tools, correction trackers
- **Design architecture:** ReAct over correction and replacement workflows
- **Design accepts critique from:** StandardsEditorAgent, FactCheckerAgent, ChannelManagerAgent
- **Design comments on:** Unclosed correction loops, incomplete notices, stale versions

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.corrections.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Resolves post-release issues faster than unstructured incident handling
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.corrections.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: ReAct over correction and replacement workflows

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.corrections`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`StandardsEditorAgent, FactCheckerAgent, ChannelManagerAgent`; comments_on=`Unclosed correction loops, incomplete notices, stale versions`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.corrections` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.corrections` shows maturity 11.0 and 11 YES

### `video.mpa` — MPAAgent (now 6.5/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 110 · **Priority band:** P6
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.mpa.v1` / `video.rubric.mpa.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 30 files · provenance=True
- **Design responsibility:** Prepares rating-related packaging and release-readiness inputs for feature workflows
- **Design knowledge sources:** Rating submission references, content advisories, theatrical packaging rules
- **Design self-quality:** Rating-package completeness, advisory clarity, escalation quality
- **Design surpass signal:** Prepares cleaner feature-release classification packages than manual prep
- **Design tools:** Submission packages, advisory templates, classification checklists
- **Design architecture:** Human-in-the-loop with structured packaging support
- **Design accepts critique from:** ProducerAgent / EP, LegalAgent, EthicsAgent
- **Design comments on:** Missing advisories, incomplete rating prep, unclear classification support

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.mpa.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Prepares cleaner feature-release classification packages than manual prep
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.mpa.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Human-in-the-loop with structured packaging support

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.mpa`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`ProducerAgent / EP, LegalAgent, EthicsAgent`; comments_on=`Missing advisories, incomplete rating prep, unclear classification support`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.mpa` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.mpa` shows maturity 11.0 and 11 YES

### `video.sales` — SalesAgent (now 6.5/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 111 · **Priority band:** P6
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.sales.v1` / `video.rubric.sales.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 8 files · provenance=True
- **Design responsibility:** Handles buyer-facing sales packaging for distributors and outlets
- **Design knowledge sources:** Rights windowing playbooks, market package examples, buyer materials
- **Design self-quality:** Buyer-package completeness, rights clarity, market-fit packaging
- **Design surpass signal:** Produces sales-ready release packets faster than manual assembly
- **Design tools:** Rights systems, package builders, buyer CRM
- **Design architecture:** ReAct over buyer package requirements
- **Design accepts critique from:** ProducerAgent / EP, DistributorAgent, MarketingAgent
- **Design comments on:** Missing buyer info, weak positioning, incomplete rights summaries

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.sales.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Produces sales-ready release packets faster than manual assembly
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.sales.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: ReAct over buyer package requirements

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.sales`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`ProducerAgent / EP, DistributorAgent, MarketingAgent`; comments_on=`Missing buyer info, weak positioning, incomplete rights summaries`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.sales` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.sales` shows maturity 11.0 and 11 YES

### `video.distributor` — DistributorAgent (now 6.5/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 112 · **Priority band:** P6
- **Current cells:** YES=3 PARTIAL=7 NO=1
- **Prompt/rubric refs:** `video.prompt.distributor.v1` / `video.rubric.distributor.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 12 files · provenance=True
- **Design responsibility:** Manages downstream delivery to buyers, platforms, and territories
- **Design knowledge sources:** Distribution specs, outlet requirements, package handoff workflows
- **Design self-quality:** Outlet-spec compliance, handoff completeness, territorial routing accuracy
- **Design surpass signal:** Reduces delivery-spec mismatches relative to fragmented delivery ops
- **Design tools:** Delivery management systems, outlet spec DB, packaging validators
- **Design architecture:** ReAct over distribution specification matrices
- **Design accepts critique from:** SalesAgent, ArchiveMasterAgent, SoundMixerAgent, ColoristAgent
- **Design comments on:** Spec mismatches, incomplete outlet packages, routing errors

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.distributor.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Reduces delivery-spec mismatches relative to fragmented delivery ops
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.distributor.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: ReAct over distribution specification matrices

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.distributor`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`SalesAgent, ArchiveMasterAgent, SoundMixerAgent, ColoristAgent`; comments_on=`Spec mismatches, incomplete outlet packages, routing errors`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.distributor` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.distributor` shows maturity 11.0 and 11 YES

### `video.awardsstrategist` — AwardsStrategistAgent (now 6.0/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 113 · **Priority band:** P6
- **Current cells:** YES=2 PARTIAL=8 NO=1
- **Prompt/rubric refs:** `video.prompt.awardsstrategist.v1` / `video.rubric.awardsstrategist.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 6 files · provenance=True
- **Design responsibility:** Plans awards submissions and campaign timing
- **Design knowledge sources:** Awards calendars, campaign playbooks, category positioning histories
- **Design self-quality:** Submission readiness, category fit, timeline precision
- **Design surpass signal:** Improves awards-timing discipline over generic release planning
- **Design tools:** Awards calendars, campaign trackers, submission checklists
- **Design architecture:** ReAct with awards timeline optimization
- **Design accepts critique from:** ProducerAgent / EP, CriticAgent, MarketingAgent
- **Design comments on:** Weak campaign timing, poor category fit, incomplete submission assets

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **PARTIAL** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now PARTIAL → YES)

- [ ] Raise packaged sources from 6 to >=8 substantive files (excerpts + catalog).
- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.awardsstrategist.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Improves awards-timing discipline over generic release planning
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.awardsstrategist.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: ReAct with awards timeline optimization

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.awardsstrategist`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`ProducerAgent / EP, CriticAgent, MarketingAgent`; comments_on=`Weak campaign timing, poor category fit, incomplete submission assets`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.awardsstrategist` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.awardsstrategist` shows maturity 11.0 and 11 YES

### `video.archivemaster` — ArchiveMasterAgent (now 6.0/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 114 · **Priority band:** P6
- **Current cells:** YES=2 PARTIAL=8 NO=1
- **Prompt/rubric refs:** `video.prompt.archivemaster.v1` / `video.rubric.archivemaster.v1`
- **Tools now:** `(none)` · live_media=False
- **Sources now:** 7 files · provenance=True
- **Design responsibility:** Produces archive-grade masters and preservation packages
- **Design knowledge sources:** Preservation standards, checksum workflows, archive metadata practice
- **Design self-quality:** Checksum integrity, preservation metadata completeness, archive package validity
- **Design surpass signal:** Delivers more reliable archive packages than late-stage export-only workflows
- **Design tools:** Archive mastering tools, checksum utilities, preservation metadata systems
- **Design architecture:** Tool-use / ReAct with preservation validation
- **Design accepts critique from:** DistributorAgent, ColoristAgent, SoundMixerAgent, GateKeeperAgent
- **Design comments on:** Incomplete preservation bundles, archive-spec violations, metadata gaps

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **PARTIAL** | **YES** |
| Q4 Self-evaluation methods & content | **PARTIAL** | **YES** |
| Q5 Surpass human (measured) | **NO** | **YES** |
| Q6 Job execution path | **PARTIAL** | **YES** |
| Q7 Skills / plugins / harness | **PARTIAL** | **YES** |
| Q8 Self-improvement mechanism | **PARTIAL** | **YES** |
| Q9 Research to improve | **PARTIAL** | **YES** |
| Q10 Collaborate / instruct others | **PARTIAL** | **YES** |
| Q11 Conflict resolve + confirm | **PARTIAL** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] Maintain YES: run uniqueness CI on every SPEC edit.
- [ ] Add does_not_own list if missing; keep user_guide.md in sync.
- [ ] Verify runtime prompt injection includes responsibility block.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] Add SPEC section `## Knowledge Distillation Plan` with sources, license class, refresh SLA.
- [ ] Create sources/DISTILLATION_PLAN.json (inputs, extractors, chunk policy, owner).
- [ ] Register plan in pack corpus index with next_review_at date.
- [ ] Link plan outputs to MemoryAgent / RAG namespace id for this agent.
- [ ] Automate dry-run distillation job (offline) that validates plan schema only.

**Q3 Sources available / obtainable** (now PARTIAL → YES)

- [ ] Raise packaged sources from 7 to >=8 substantive files (excerpts + catalog).
- [ ] Inventory agents.md Knowledge Distillation Source into sources/SOURCE_CATALOG.json.
- [ ] For each source: license, URL/path, acquisition method, retention, hash, owner.
- [ ] Store at least one usable excerpt or synthetic licensed fixture per source class.
- [ ] Update PROVENANCE.json + MAPPING.md; fail CI if catalog empty or unlicensed-required missing plan.
- [ ] Document fetch runbook in sources/ACQUIRE.md (manual or API, no secrets in git).

**Q4 Self-evaluation methods & content** (now PARTIAL → YES)

- [ ] Write rubrics content for `video.rubric.archivemaster.v1` (currently files=0).
- [ ] Materialize rubrics/<rubric_reference>.json from agents.md Self-Quality Criteria.
- [ ] Define L1 validators (schema/codec/loudness/format) as machine checks.
- [ ] Define L2 LLM-as-Judge rubric dimensions with weights and pass >=85/100.
- [ ] Add golden eval fixture under business/video/evals/agents/<agent_id>/.
- [ ] Wire host eval harness to load rubric_reference and fail closed on missing file.

**Q5 Surpass human (measured)** (now NO → YES)

- [ ] Register surpass protocol for signal: Delivers more reliable archive packages than late-stage export-only workflows
- [ ] Translate agents.md Surpass-Human Signal into measurable metric + protocol.
- [ ] Collect human baseline on identical golden task (N trials, frozen inputs).
- [ ] Run agent on same task with locked model/tool versions; store evidence bundle.
- [ ] Compute delta; only mark YES if metric meets signal under pre-registered protocol.
- [ ] Publish eval report path in SPEC `## Human Baseline Results` (or mark target-only).

**Q6 Job execution path** (now PARTIAL → YES)

- [ ] Write prompts content for `video.prompt.archivemaster.v1` (currently files=0).
- [ ] Replace stub-only tools with role allowlist (or explicit offline mock adapters with tests).
- [ ] Materialize prompts/<prompt_reference>.md (system, developer, task, output schema).
- [ ] Implement architecture pattern from agents.md (Self-Refine/ReAct/Debate/Graph).
- [ ] Map Tool Access column to allowlisted host adapters; stubs must declare not-production.
- [ ] Register agent in at least one workflow DNA / graph with I/O contracts.
- [ ] Add integration test: invoke agent node offline (or mock tools) and assert artifact schema.
- [ ] Implement pattern: Tool-use / ReAct with preservation validation

**Q7 Skills / plugins / harness** (now PARTIAL → YES)

- [ ] Create per-agent skills harness directory for `video.archivemaster`.
- [ ] Create business/video/agents/<id>/skills/ with SKILL.md + integration.json.
- [ ] Bind required pack special_skills (if any) via skills/bindings.json.
- [ ] Declare harness: runner kind (graph-node | tool-loop | media-adapter), entrypoint, timeouts.
- [ ] Add capability registry entry listing skills hash + version.
- [ ] Smoke test: host loads skill without network unless production flags set.

**Q8 Self-improvement mechanism** (now PARTIAL → YES)

- [ ] Keep max_refinement_count and document policy in SPEC.
- [ ] Implement refine loop in host using prompt_reference + critique inputs.
- [ ] Persist improvement candidates under evidence/ with before/after scores.
- [ ] Promotion gate: L2 score improvement and no L1 regression.
- [ ] Schedule periodic improvement job (or operator-triggered) with audit log.

**Q9 Research to improve** (now PARTIAL → YES)

- [ ] Define research request schema (topic, source classes, max cost, deadline).
- [ ] Wire collaboration edge to research meta-agents (webresearch/benchmark/trend as applicable).
- [ ] Store research outputs under sources/research/ with provenance.
- [ ] Map research -> distillation plan update -> golden eval refresh.
- [ ] Add dry-run research path that works offline with fixture corpora.

**Q10 Collaborate / instruct others** (now PARTIAL → YES)

- [ ] Encode accepts_from=`DistributorAgent, ColoristAgent, SoundMixerAgent, GateKeeperAgent`; comments_on=`Incomplete preservation bundles, archive-spec violations, metadata gaps`.
- [ ] Expand critique_edges from agents.md Accepts/Comments columns (full matrix).
- [ ] Implement CritiqueMessage + InstructionMessage host APIs.
- [ ] Prove one send and one receive path in integration test for this agent.
- [ ] Document collab partners in SPEC `## Collaboration Matrix`.
- [ ] Orchestrator/router can address agent by id with correlation identifiers.

**Q11 Conflict resolve + confirm** (now PARTIAL → YES)

- [ ] Define conflict policy: blocker/major/minor and auto-resolve rules.
- [ ] Wire disputes to video.judge (or role judge) multi-agent debate.
- [ ] Require HiTL confirm for unresolved blockers; record decision evidence.
- [ ] Integration test: inject conflicting critique, assert resolve or escalate path.
- [ ] Surface conflict state in activity/ops UI with confirm action refs only.

#### Exit gate for this agent

- [ ] Offline golden run for `video.archivemaster` passes L1 + L2 threshold
- [ ] Collab send/receive test green
- [ ] Conflict resolve or HiTL escalate test green
- [ ] Improve-loop test green (or N/A only if policy documents permanent non-learning — not allowed for full mark)
- [ ] Human baseline package filed; surpass claim only if measured gate green
- [ ] `AGENT_CAPABILITY_AUDIT.json` row for `video.archivemaster` shows maturity 11.0 and 11 YES

---

## 7. Priority order of agents (implementation queue)

Work top-down. Spine unlocks everyone else.

| Order | Band | Agent | Now | Why first |
|------:|------|-------|-----|-----------|
| 1 | P0 | `video.orchestrator` | 6.5 | Platform spine — orchestrates, plans, routes, judges |
| 2 | P0 | `video.planner` | 6.5 | Platform spine — orchestrates, plans, routes, judges |
| 3 | P0 | `video.router` | 6.5 | Platform spine — orchestrates, plans, routes, judges |
| 4 | P0 | `video.judge` | 6.5 | Platform spine — orchestrates, plans, routes, judges |
| 5 | P0 | `video.gatekeeper` | 6.5 | Platform spine — orchestrates, plans, routes, judges |
| 6 | P0 | `video.memory` | 6.5 | Platform spine — orchestrates, plans, routes, judges |
| 7 | P0 | `video.critic` | 6.5 | Platform spine — orchestrates, plans, routes, judges |
| 8 | P1 | `video.ideation` | 6.5 | Meta platform capabilities |
| 9 | P1 | `video.narrativearc` | 6.5 | Meta platform capabilities |
| 10 | P1 | `video.styletransfer` | 6.5 | Meta platform capabilities |
| 11 | P1 | `video.worldbuilding` | 6.5 | Meta platform capabilities |
| 12 | P1 | `video.moodboard` | 6.5 | Meta platform capabilities |
| 13 | P1 | `video.novelty` | 6.5 | Meta platform capabilities |
| 14 | P1 | `video.emotionalarc` | 6.5 | Meta platform capabilities |
| 15 | P1 | `video.webresearch` | 6.5 | Meta platform capabilities |
| 16 | P1 | `video.archiveresearch` | 6.5 | Meta platform capabilities |
| 17 | P1 | `video.trendintelligence` | 6.5 | Meta platform capabilities |
| 18 | P1 | `video.competitorintelligence` | 6.5 | Meta platform capabilities |
| 19 | P1 | `video.citation` | 6.5 | Meta platform capabilities |
| 20 | P1 | `video.interviewsynthesis` | 6.5 | Meta platform capabilities |
| 21 | P1 | `video.benchmarkresearch` | 6.5 | Meta platform capabilities |
| 22 | P1 | `video.promptoptimizer` | 6.5 | Meta platform capabilities |
| 23 | P1 | `video.costoptimizer` | 6.5 | Meta platform capabilities |
| 24 | P1 | `video.latencyoptimizer` | 6.5 | Meta platform capabilities |
| 25 | P1 | `video.retentionoptimizer` | 6.5 | Meta platform capabilities |
| 26 | P1 | `video.roasoptimizer` | 6.5 | Meta platform capabilities |
| 27 | P1 | `video.accessibilityoptimizer` | 6.5 | Meta platform capabilities |
| 28 | P1 | `video.evaluationharness` | 6.5 | Meta platform capabilities |
| 29 | P1 | `video.safetyredteam` | 6.5 | Meta platform capabilities |
| 30 | P2 | `video.director` | 6.5 | Above-the-line creative authority |
| 31 | P2 | `video.producer` | 6.5 | Above-the-line creative authority |
| 32 | P2 | `video.screenwriter` | 6.5 | Above-the-line creative authority |
| 33 | P2 | `video.showrunner` | 6.5 | Above-the-line creative authority |
| 34 | P2 | `video.casting` | 6.5 | Above-the-line creative authority |
| 35 | P3 | `video.editor` | 6.5 | Already has live media tools — complete harness/evals |
| 36 | P3 | `video.animator_2d` | 6.5 | Already has live media tools — complete harness/evals |
| 37 | P3 | `video.motiongraphics` | 6.5 | Already has live media tools — complete harness/evals |
| 38 | P3 | `video.sounddesign` | 6.5 | Already has live media tools — complete harness/evals |
| 39 | P3 | `video.voiceover` | 6.5 | Already has live media tools — complete harness/evals |
| 40 | P3 | `video.creativedirector` | 6.5 | Already has live media tools — complete harness/evals |
| 41 | P3 | `video.audiobooknarrator` | 6.5 | Already has live media tools — complete harness/evals |
| 42 | P3 | `video.promptengineer` | 6.5 | Already has live media tools — complete harness/evals |
| 43 | P3 | `video.voiceclone` | 6.5 | Already has live media tools — complete harness/evals |
| 44 | P3 | `video.archiveproducer` | 6.0 | Already has live media tools — complete harness/evals |
| 45 | P4 | `video.cinematographer` | 6.5 | Core craft production path |
| 46 | P4 | `video.cameraoperator` | 6.5 | Core craft production path |
| 47 | P4 | `video.dronepilot` | 6.5 | Core craft production path |
| 48 | P4 | `video.colorist` | 6.5 | Core craft production path |
| 49 | P4 | `video.vfxsupervisor` | 6.5 | Core craft production path |
| 50 | P4 | `video.storyboard` | 6.5 | Core craft production path |
| 51 | P4 | `video.conceptartist` | 6.5 | Core craft production path |
| 52 | P4 | `video.productiondesign` | 6.5 | Core craft production path |
| 53 | P4 | `video.costumedesign` | 6.5 | Core craft production path |
| 54 | P4 | `video.mua_makeup` | 6.5 | Core craft production path |
| 55 | P4 | `video.composer` | 6.5 | Core craft production path |
| 56 | P4 | `video.soundmixer` | 6.5 | Core craft production path |
| 57 | P5 | `video.choreography` | 6.5 | Specialized craft / AI-era |
| 58 | P5 | `video.musicvideodirector` | 6.0 | Specialized craft / AI-era |
| 59 | P5 | `video.comedywriter` | 6.5 | Specialized craft / AI-era |
| 60 | P5 | `video.talent` | 6.5 | Specialized craft / AI-era |
| 61 | P5 | `video.ugccreator` | 6.0 | Specialized craft / AI-era |
| 62 | P5 | `video.socialmediastrategist` | 6.5 | Specialized craft / AI-era |
| 63 | P5 | `video.copywriter` | 6.5 | Specialized craft / AI-era |
| 64 | P5 | `video.performancemarketer` | 6.5 | Specialized craft / AI-era |
| 65 | P5 | `video.avatardesign` | 6.5 | Specialized craft / AI-era |
| 66 | P5 | `video.aiqaconsistency` | 6.5 | Specialized craft / AI-era |
| 67 | P5 | `video.personalizationengineer` | 6.5 | Specialized craft / AI-era |
| 68 | P5 | `video.trailereditor` | 6.5 | Specialized craft / AI-era |
| 69 | P5 | `video.sportsanalyst` | 6.5 | Specialized craft / AI-era |
| 70 | P6 | `video.instructionaldesign` | 6.5 | Support & long-tail |
| 71 | P6 | `video.sme` | 6.5 | Support & long-tail |
| 72 | P6 | `video.factchecker` | 6.5 | Support & long-tail |
| 73 | P6 | `video.medicalillustrator` | 6.5 | Support & long-tail |
| 74 | P6 | `video.journalist` | 6.5 | Support & long-tail |
| 75 | P6 | `video.compliance` | 6.5 | Support & long-tail |
| 76 | P6 | `video.finance` | 6.5 | Support & long-tail |
| 77 | P6 | `video.foodstylist` | 6.5 | Support & long-tail |
| 78 | P6 | `video.travelcine` | 6.5 | Support & long-tail |
| 79 | P6 | `video.childrensauthor` | 6.5 | Support & long-tail |
| 80 | P6 | `video.signlanguageinterpreter` | 6.5 | Support & long-tail |
| 81 | P6 | `video.localizationqa` | 6.5 | Support & long-tail |
| 82 | P6 | `video.realestatephoto` | 6.0 | Support & long-tail |
| 83 | P6 | `video.analyst` | 6.5 | Support & long-tail |
| 84 | P6 | `video.audiencesim` | 6.5 | Support & long-tail |
| 85 | P6 | `video.accessibility` | 6.5 | Support & long-tail |
| 86 | P6 | `video.brand` | 6.5 | Support & long-tail |
| 87 | P6 | `video.brandstrategist` | 6.5 | Support & long-tail |
| 88 | P6 | `video.marketing` | 6.5 | Support & long-tail |
| 89 | P6 | `video.seo` | 6.5 | Support & long-tail |
| 90 | P6 | `video.community` | 6.5 | Support & long-tail |
| 91 | P6 | `video.templatedesign` | 6.5 | Support & long-tail |
| 92 | P6 | `video.ux` | 6.0 | Support & long-tail |
| 93 | P6 | `video.trustsafety` | 6.5 | Support & long-tail |
| 94 | P6 | `video.crm` | 6.5 | Support & long-tail |
| 95 | P6 | `video.legal` | 6.5 | Support & long-tail |
| 96 | P6 | `video.festivalstrategist` | 6.0 | Support & long-tail |
| 97 | P6 | `video.lms` | 6.5 | Support & long-tail |
| 98 | P6 | `video.learnersim` | 6.5 | Support & long-tail |
| 99 | P6 | `video.continuity` | 6.5 | Support & long-tail |
| 100 | P6 | `video.lipsync` | 6.5 | Support & long-tail |
| 101 | P6 | `video.musicsupervisor` | 6.0 | Support & long-tail |
| 102 | P6 | `video.labela_r` | 6.0 | Support & long-tail |
| 103 | P6 | `video.labeldigital` | 6.0 | Support & long-tail |
| 104 | P6 | `video.deepfakedetection` | 6.5 | Support & long-tail |
| 105 | P6 | `video.comms` | 6.5 | Support & long-tail |
| 106 | P6 | `video.standardseditor` | 6.5 | Support & long-tail |
| 107 | P6 | `video.ethics` | 6.5 | Support & long-tail |
| 108 | P6 | `video.channelmanager` | 6.0 | Support & long-tail |
| 109 | P6 | `video.corrections` | 6.5 | Support & long-tail |
| 110 | P6 | `video.mpa` | 6.5 | Support & long-tail |
| 111 | P6 | `video.sales` | 6.5 | Support & long-tail |
| 112 | P6 | `video.distributor` | 6.5 | Support & long-tail |
| 113 | P6 | `video.awardsstrategist` | 6.0 | Support & long-tail |
| 114 | P6 | `video.archivemaster` | 6.0 | Support & long-tail |

---

## 8. Estimation model (planning aid)

| Work item | Unit | Count | Notes |
|-----------|------|------:|-------|
| Prompt file | agent | 114 | factory + human craft review |
| Rubric file | agent | 114 | factory + craft owner signoff |
| Source catalog + acquire plan | agent | 114 | legal may serialize |
| Skills harness | agent | 114 | thin wrapper ok |
| Golden eval | agent | 114 | start with fixtures |
| Mock tool adapters | tool class | ~30–50 | shared across agents |
| Collab edge tests | agent | 114 | generate from matrix |
| Human baseline | agent | 114 | expensive; batch by group |
| Surpass measurement | agent | 114 | only after baseline |

**Practical staging of Q5:** Do not block Phases 1–4 on surpass. File baseline protocol early; execute human studies after execution path works. Full mark requires Q5 YES — plan calendar time for human evaluation, or redefine YES as “measured parity protocol complete and target met” (never claim without data).

---

## 9. Governance gates (prevent fake full marks)

1. **No YES without path:** audit script must check file existence + test names, not SPEC keywords alone (upgrade auditor).
2. **No surpass in UI** unless evidence bundle hash present.
3. **Fail-closed tools:** missing adapter => mock or error, never silent success.
4. **Action refs** for HiTL confirms (product façade discipline).
5. **PR checklist** must include capability audit delta for touched agents.

---

## 10. Regeneration

```bash
python scripts/business/audit_agent_capability_status.py
python scripts/business/render_agent_capability_status_v1.py
python scripts/business/render_agent_improvement_plan_v1.py
```

Track progress by re-auditing: maturity avg should rise from **6.45** toward **11.0**.

