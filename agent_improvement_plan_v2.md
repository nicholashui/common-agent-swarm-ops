# Agent Improvement Plan v2 — Path to Full Mark (11/11 YES)

**Generated:** 2026-07-30T14:45:36Z  
**Based on:** `agent_capability_status_v2.md` + `business/video/AGENT_CAPABILITY_AUDIT.json`  
**Prior plan:** `agent_improvement_plan_v1.md` / `agent_improvement_plan_v1_hk.md`  
**Design authority:** `va-agent-swarm/study/agents.md`  
**Scope:** 114 non-special video pack agents  
**Goal:** Every agent reaches **FULL MARK** = YES on all 11 questions (maturity **11.0/11**).

> **v2 thesis:** Automatable Wave A–D work from v1 is **done**. Remaining full-mark work is almost entirely 
> **Q5 measured human baselines** (real raters, not synthetic), plus maintenance/hardening of already-green items.

---

## 0. Scoreboard vs full mark

| Metric | Now | Full mark target |
|--------|----:|-----------------:|
| Avg maturity 0–11 | **10.5** | **11.0** |
| Weighted cell completion | **95.45%** | **100%** |
| Strict YES cells | **90.91%** | **100%** |
| YES / PARTIAL / NO | 1140 / 114 / 0 | 1254 / 0 / 0 |
| Plan composite (v1 tracker) | **95.71%** | **100%** |
| Automatable (ex-Q5) | **100.0%** | **100%** (already) |
| Q5 YES agents | **0/114** | **114/114** |

**Gap math:** 114 cells not YES — of which **114** are Q5 PARTIAL and **0** Q5 NO.
Closing Q5 alone lifts maturity from **10.5 → 11.0** if all other Qs stay YES.

---

## 1. What v1 already completed (do not re-build)

| Workstream | Evidence | Status |
|------------|----------|--------|
| P0 Artifact factories | prompts/rubrics/skills/catalogs/goldens ×114 | **DONE** |
| P1 Execution runtime | `backend/app/video/pack_runtime/` loader+runner+golden | **DONE** |
| P2 Eval / baseline kit | rubrics L1/L2/L3 + human_baseline_protocol ×114 | **DONE (protocol)** |
| P3 Critique bus | CritiqueBus edges, ack, HiTL blockers | **DONE** |
| P4 Distill / improve scaffolds | DISTILLATION_PLAN + ACQUIRE + refine loop | **DONE** |
| Q1–Q4, Q6–Q11 fleet YES | capability audit v2 | **DONE** |
| Q5 real human MET | gate.met && !synthetic | **NOT DONE** |

---

## 2. Full-mark definition of done (v2)

| Q | Title | YES only when | Primary evidence |
|---|-------|---------------|------------------|
| Q1 | Q1 Responsibility in SPEC | Identity + owns/does_not_own exact, unique, injected at runtime. | See per-agent checklist |
| Q2 | Q2 Knowledge distillation plan | Written continuous-distillation plan with owner, cadence, promotion criteria. | See per-agent checklist |
| Q3 | Q3 Sources available / obtainable | Licensed or permitted sources + re-runnable ACQUIRE SOP. | See per-agent checklist |
| Q4 | Q4 Self-evaluation methods & content | Executable L1 + L2 rubric + optional L3 preference with thresholds. | See per-agent checklist |
| Q5 | Q5 Surpass human (measured) | Non-synthetic human baseline + agent measure + gate.met=true. | See per-agent checklist |
| Q6 | Q6 Job execution path | Host path: prompt + rubric + skill + golden/runner evidence. | See per-agent checklist |
| Q7 | Q7 Skills / plugins / harness | Per-agent skills harness loadable by host. | See per-agent checklist |
| Q8 | Q8 Self-improvement mechanism | critique/fail → refine ≤N → re-score → promote/reject with evidence. | See per-agent checklist |
| Q9 | Q9 Research to improve | Can request/consume research packs into distill + evals. | See per-agent checklist |
| Q10 | Q10 Collaborate / instruct others | Typed send/receive with edge allowlists + ack. | See per-agent checklist |
| Q11 | Q11 Conflict resolve + confirm | Severity routing; self-resolve when allowed; Judge/HiTL confirm when not. | See per-agent checklist |

### Scoring rule

- **FULL MARK agent:** 11 YES (no PARTIAL, no NO).
- **Fleet FULL MARK:** 114/114 agents at 11.0 + no synthetic surpass claims in UI.
- **Q5 special rule:** `human_baseline_protocol.json` with `gate.met=true` AND `gate.synthetic=false` AND evidence file.

---

## 3. Research-backed path for the remaining gap (Q5)

Deep research inputs (same family as improvement research v1 + baseline design):

| Source | How v2 uses it |
|--------|----------------|
| `agents.md` Surpass-Human Signal | Metric inference (win-rate, TTD, cost, κ, craft score) |
| LLM-as-Judge / pairwise arena practices | L2 rubrics + optional pairwise_win_rate gates |
| Human evaluation protocols (frozen tasks, blinding) | `human_baseline_protocol.json` procedure |
| Anthropic Agent Skills | Per-agent harness already loadable |
| Offline pack_runtime | Reproducible agent_measurement trials |
| Fail-closed product rules | No surpass UI without evidence |

### Recommended evaluation science (per agent)

1. **Freeze inputs** — only `evals/agents/<id>/golden.json` (or versioned twin).
2. **Human trials n≥5** — independent raters when possible; record rater_id.
3. **Agent trials n≥5** — locked runner/prompt/rubric versions.
4. **Pre-register metric** — from agents.md signal (do not change after rating starts).
5. **Gate** — higher_is_better: agent_mean≥human_mean; lower_is_better: agent_mean<human_mean; pairwise: rate≥threshold.
6. **Publish evidence** — `human_baseline_evidence.json`; claim only if met && !synthetic.

---

## 4. Shared workstreams v2 (fleet unlock for 11/11)

### W0 — Protect the green (continuous)

| ID | Action | Done when |
|----|--------|-----------|
| W0.1 | CI: pack golden spine 7/7 | pytest + `run_pack_agent_golden.py --spine` green |
| W0.2 | CI: capability audit cells no regression on Q1–4,6–11 | audit JSON gate |
| W0.3 | Ban synthetic surpass claims in UI | product checks claim_allowed_in_ui |

### W1 — Human baseline operations (PRIMARY)

| ID | Action | Output | Done when |
|----|--------|--------|-----------|
| W1.1 | Keep protocols current | human_baseline_protocol.json ×114 | scaffold re-runnable |
| W1.2 | Clear synthetic on spine before real sessions | clean human_baseline.trials | synthetic_any=false |
| W1.3 | Rater session packs | evals/rater_sessions/ | briefs for spine+ATL |
| W1.4 | Record real trials | CLI/CSV/session | n≥5 per agent |
| W1.5 | Evaluate gates | gate.met | non-synthetic |
| W1.6 | Dashboard | BASELINE_STATUS.md | claimable count rises |
| W1.7 | Re-audit + completion report | capability v2 + plan completion | maturity → 11 |

### W2 — Optional hardening (not blocking 11/11 if Q5 met)

| ID | Action | Why |
|----|--------|-----|
| W2.1 | Role mock tool adapters beyond media.stub | richer Q6 craft fidelity |
| W2.2 | Licensed corpus acquisition | deeper Q3 grounding |
| W2.3 | Durable prompt/rubric promote pipeline | stronger Q8 |
| W2.4 | Product UI action-refs for HiTL confirm | operator UX for Q11 |

---

## 5. Phased program to fleet full mark

| Phase | Theme | Target | Exit criteria |
|-------|-------|--------|---------------|
| **V2-P0** | Protect green | keep 10.5 | spine golden + unit tests green |
| **V2-P1** | Spine human baselines | 7 agents Q5 YES | orchestrator…memory gate.met |
| **V2-P2** | ATL human baselines | +5 agents Q5 YES | director/producer/screenwriter/showrunner/casting |
| **V2-P3** | Core craft groups | Cam/Edit/Snd | group baselines MET |
| **V2-P4** | Long tail | Perf/Dist/Edu/AI/Sup + remaining Meta | all 114 Q5 YES |
| **V2-P5** | Full mark freeze | **11.0 × 114** | audit all YES; completion 100% |

### Critical path

```
baseline_status → clear synthetic spine → rate spine humans
  → evaluate_gate spine → rate ATL → core craft → long tail
    → audit_agent_capability_status → report completion 100%
```

---

## 6. Universal checklist v2 (every agent)

```text
[ ] V2-U1  Q1–Q4 still YES after any SPEC edit
[ ] V2-U2  prompt + rubric + skill files still load via PackAgentLoader
[ ] V2-U3  golden.json offline pass
[ ] V2-U4  critique_edges non-empty; bus allowlist valid
[ ] V2-U5  DISTILLATION_PLAN + SOURCE_CATALOG + ACQUIRE present
[ ] V2-U6  human_baseline_protocol.json present
[ ] V2-U7  agent_measurement n>=5 (offline or locked)
[ ] V2-U8  human_baseline n>=5 REAL (synthetic=false)
[ ] V2-U9  evaluate_gate => met=true, synthetic=false
[ ] V2-U10 evidence claim_allowed_in_ui true
[ ] V2-U11 capability audit row maturity 11.0 / 11 YES
```

---

## 7. Actions by question (fleet rollup)

### Q1 Responsibility in SPEC

- **Definition of YES:** Identity + owns/does_not_own exact, unique, injected at runtime.
- **Current:** YES=114, PARTIAL=0, NO=0
- **Agents needing work for full mark:** 0 (PARTIAL counts as incomplete)
- **Mode:** MAINTAIN (already fleet YES) — run maintenance actions only.
- **Standard actions:**
  - [ ] Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
  - [ ] Keep agent_spec.does_not_own aligned with prompt System section.
  - [ ] Sync user_guide.md opening sentence with Responsibility.
  - [ ] L1 loader check must continue to require Responsibility block in prompt.

### Q2 Knowledge distillation plan

- **Definition of YES:** Written continuous-distillation plan with owner, cadence, promotion criteria.
- **Current:** YES=114, PARTIAL=0, NO=0
- **Agents needing work for full mark:** 0 (PARTIAL counts as incomplete)
- **Mode:** MAINTAIN (already fleet YES) — run maintenance actions only.
- **Standard actions:**
  - [ ] Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
  - [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
  - [ ] Dry-run distill schema validation in CI for changed agents.

### Q3 Sources available / obtainable

- **Definition of YES:** Licensed or permitted sources + re-runnable ACQUIRE SOP.
- **Current:** YES=114, PARTIAL=0, NO=0
- **Agents needing work for full mark:** 0 (PARTIAL counts as incomplete)
- **Mode:** MAINTAIN (already fleet YES) — run maintenance actions only.
- **Standard actions:**
  - [ ] Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
  - [ ] Refresh ACQUIRE.md steps after any new corpus class.
  - [ ] Update PROVENANCE.json hashes when excerpts change.
  - [ ] Prefer fixture-only offline grounding until legal approval.

### Q4 Self-evaluation methods & content

- **Definition of YES:** Executable L1 + L2 rubric + optional L3 preference with thresholds.
- **Current:** YES=114, PARTIAL=0, NO=0
- **Agents needing work for full mark:** 0 (PARTIAL counts as incomplete)
- **Mode:** MAINTAIN (already fleet YES) — run maintenance actions only.
- **Standard actions:**
  - [ ] Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
  - [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
  - [ ] Ensure golden.json still expects l1_passed + artifact.
  - [ ] Re-run pack golden after rubric edits.

### Q5 Surpass human (measured)

- **Definition of YES:** Non-synthetic human baseline + agent measure + gate.met=true.
- **Current:** YES=0, PARTIAL=114, NO=0
- **Agents needing work for full mark:** 114 (PARTIAL counts as incomplete)
- **Mode:** CLOSE GAP — primary delivery actions below.
- **Standard actions:**
  - [ ] Confirm human_baseline_protocol.json exists and metric matches agents.md surpass signal.
  - [ ] Clear any synthetic human trials before real sessions.
  - [ ] Collect >=5 real human trials (0–100 or metric-native) on frozen golden inputs.
  - [ ] Ensure agent_measurement has >=5 offline (or locked-version) trials.
  - [ ] Run evaluate_gate; require gate.met && !synthetic for YES.
  - [ ] Publish human_baseline_evidence.json; only then allow UI surpass language.
  - [ ] If not_met: improve prompt/rubric/tools, re-measure agent, re-rate humans if task changed.

### Q6 Job execution path

- **Definition of YES:** Host path: prompt + rubric + skill + golden/runner evidence.
- **Current:** YES=114, PARTIAL=0, NO=0
- **Agents needing work for full mark:** 0 (PARTIAL counts as incomplete)
- **Mode:** MAINTAIN (already fleet YES) — run maintenance actions only.
- **Standard actions:**
  - [ ] Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
  - [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
  - [ ] Keep golden.json green via PackGoldenRunner.
  - [ ] Fail-closed on network=true/production=true without env gates.
  - [ ] Optional: map design Tool Access to mock adapters with tests.

### Q7 Skills / plugins / harness

- **Definition of YES:** Per-agent skills harness loadable by host.
- **Current:** YES=114, PARTIAL=0, NO=0
- **Agents needing work for full mark:** 0 (PARTIAL counts as incomplete)
- **Mode:** MAINTAIN (already fleet YES) — run maintenance actions only.
- **Standard actions:**
  - [ ] Maintain skills/SKILL.md + integration.json + bindings.json.
  - [ ] Validate special_skills bindings paths when used.
  - [ ] Smoke: host loads skill without network.

### Q8 Self-improvement mechanism

- **Definition of YES:** critique/fail → refine ≤N → re-score → promote/reject with evidence.
- **Current:** YES=114, PARTIAL=0, NO=0
- **Agents needing work for full mark:** 0 (PARTIAL counts as incomplete)
- **Mode:** MAINTAIN (already fleet YES) — run maintenance actions only.
- **Standard actions:**
  - [ ] Keep max_refinement_count policy documented.
  - [ ] Exercise force_l2_fail_once path in tests when changing runner.
  - [ ] After improvements, re-run golden + baseline agent_measurement.
  - [ ] Optional: durable promote of new prompt/rubric versions with evidence bundle.

### Q9 Research to improve

- **Definition of YES:** Can request/consume research packs into distill + evals.
- **Current:** YES=114, PARTIAL=0, NO=0
- **Agents needing work for full mark:** 0 (PARTIAL counts as incomplete)
- **Mode:** MAINTAIN (already fleet YES) — run maintenance actions only.
- **Standard actions:**
  - [ ] Use SOURCE_CATALOG + ACQUIRE for research intake.
  - [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
  - [ ] Map research outputs under sources/research/ with provenance.
  - [ ] Refresh golden thresholds only with protocol change control.

### Q10 Collaborate / instruct others

- **Definition of YES:** Typed send/receive with edge allowlists + ack.
- **Current:** YES=114, PARTIAL=0, NO=0
- **Agents needing work for full mark:** 0 (PARTIAL counts as incomplete)
- **Mode:** MAINTAIN (already fleet YES) — run maintenance actions only.
- **Standard actions:**
  - [ ] Keep critique_edges aligned with agents.md Accepts/Comments.
  - [ ] Prove send+receive for at least one partner edge in integration tests (spine).
  - [ ] Include correlation_id on all critiques/handoffs.

### Q11 Conflict resolve + confirm

- **Definition of YES:** Severity routing; self-resolve when allowed; Judge/HiTL confirm when not.
- **Current:** YES=114, PARTIAL=0, NO=0
- **Agents needing work for full mark:** 0 (PARTIAL counts as incomplete)
- **Mode:** MAINTAIN (already fleet YES) — run maintenance actions only.
- **Standard actions:**
  - [ ] Keep blocker → requires_hitl confirm path.
  - [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
  - [ ] Surface confirm via product action refs only (no invented authority).
  - [ ] Re-test after edge matrix changes.

---

## 8. Per-group programs (v2)

### 1-ATL — Above-the-Line (5 agents, avg 10.5, Q5 remaining 5)

**Group milestone checklist:**
- [ ] All 5 agents pass V2-U1…U5 (maintain green)
- [ ] All 5 complete real human baselines (V2-U8…U10)
- [ ] Audit: every agent in group maturity **11.0**

| Agent | Now | Gap to 11 | Band | First actions to full mark |
|-------|-----|-----------|------|------------------------------|
| `video.director` | 10.5 | 0.5 | P2 | 1. Q5: PRIMARY GAP: Close Q5 for `video.director` — design signal: Wins ≥55% blind pairwise vs DGA cut… |
| `video.producer` | 10.5 | 0.5 | P2 | 1. Q5: PRIMARY GAP: Close Q5 for `video.producer` — design signal: Beats PGA schedules at 0.6× cost wi… |
| `video.screenwriter` | 10.5 | 0.5 | P2 | 1. Q5: PRIMARY GAP: Close Q5 for `video.screenwriter` — design signal: Wins ≥50% blind read vs Black L… |
| `video.showrunner` | 10.5 | 0.5 | P2 | 1. Q5: PRIMARY GAP: Close Q5 for `video.showrunner` — design signal: Series Bible coverage ≥99% across… |
| `video.casting` | 10.5 | 0.5 | P2 | 1. Q5: PRIMARY GAP: Close Q5 for `video.casting` — design signal: Beats CSA casting in blind preferenc… |

### 2-Cam — Camera & Lighting (3 agents, avg 10.5, Q5 remaining 3)

**Group milestone checklist:**
- [ ] All 3 agents pass V2-U1…U5 (maintain green)
- [ ] All 3 complete real human baselines (V2-U8…U10)
- [ ] Audit: every agent in group maturity **11.0**

| Agent | Now | Gap to 11 | Band | First actions to full mark |
|-------|-----|-----------|------|------------------------------|
| `video.cinematographer` | 10.5 | 0.5 | P4 | 1. Q5: PRIMARY GAP: Close Q5 for `video.cinematographer` — design signal: Beats ASC peer-juried reels … |
| `video.cameraoperator` | 10.5 | 0.5 | P4 | 1. Q5: PRIMARY GAP: Close Q5 for `video.cameraoperator` — design signal: Focus-pull accuracy >99% vs S… |
| `video.dronepilot` | 10.5 | 0.5 | P4 | 1. Q5: PRIMARY GAP: Close Q5 for `video.dronepilot` — design signal: Competition-grade smoothness at 1… |

### 3-Edit — Editorial & Color / Design (10 agents, avg 10.5, Q5 remaining 10)

**Group milestone checklist:**
- [ ] All 10 agents pass V2-U1…U5 (maintain green)
- [ ] All 10 complete real human baselines (V2-U8…U10)
- [ ] Audit: every agent in group maturity **11.0**

| Agent | Now | Gap to 11 | Band | First actions to full mark |
|-------|-----|-----------|------|------------------------------|
| `video.editor` | 10.5 | 0.5 | P3 | 1. Q5: PRIMARY GAP: Close Q5 for `video.editor` — design signal: Wins ≥55% pairwise vs ACE-credited cu… |
| `video.animator_2d` | 10.5 | 0.5 | P3 | 1. Q5: PRIMARY GAP: Close Q5 for `video.animator_2d` — design signal: Beats junior on Annie rubric; eq… |
| `video.motiongraphics` | 10.5 | 0.5 | P3 | 1. Q5: PRIMARY GAP: Close Q5 for `video.motiongraphics` — design signal: Wins agency RFP shootouts on … |
| `video.colorist` | 10.5 | 0.5 | P4 | 1. Q5: PRIMARY GAP: Close Q5 for `video.colorist` — design signal: Beats junior colorist in blind pref… |
| `video.vfxsupervisor` | 10.5 | 0.5 | P4 | 1. Q5: PRIMARY GAP: Close Q5 for `video.vfxsupervisor` — design signal: Weta-grade QC pass rate at fra… |
| `video.storyboard` | 10.5 | 0.5 | P4 | 1. Q5: PRIMARY GAP: Close Q5 for `video.storyboard` — design signal: Pixar story-trust pass rate at mi… |
| `video.conceptartist` | 10.5 | 0.5 | P4 | 1. Q5: PRIMARY GAP: Close Q5 for `video.conceptartist` — design signal: Wins art-director shootouts on… |
| `video.productiondesign` | 10.5 | 0.5 | P4 | 1. Q5: PRIMARY GAP: Close Q5 for `video.productiondesign` — design signal: Wins ADG blind comparisons … |
| `video.costumedesign` | 10.5 | 0.5 | P4 | 1. Q5: PRIMARY GAP: Close Q5 for `video.costumedesign` — design signal: Beats CDG juniors on period ac… |
| `video.mua_makeup` | 10.5 | 0.5 | P4 | 1. Q5: PRIMARY GAP: Close Q5 for `video.mua_makeup` — design signal: Continuity break rate <0.5% (vs ~… |

### 4-Snd — Sound & Music (4 agents, avg 10.5, Q5 remaining 4)

**Group milestone checklist:**
- [ ] All 4 agents pass V2-U1…U5 (maintain green)
- [ ] All 4 complete real human baselines (V2-U8…U10)
- [ ] Audit: every agent in group maturity **11.0**

| Agent | Now | Gap to 11 | Band | First actions to full mark |
|-------|-----|-----------|------|------------------------------|
| `video.sounddesign` | 10.5 | 0.5 | P3 | 1. Q5: PRIMARY GAP: Close Q5 for `video.sounddesign` — design signal: Wins MPSE pairwise on horror/sci… |
| `video.voiceover` | 10.5 | 0.5 | P3 | 1. Q5: PRIMARY GAP: Close Q5 for `video.voiceover` — design signal: Beats junior VO in blind preferenc… |
| `video.composer` | 10.5 | 0.5 | P4 | 1. Q5: PRIMARY GAP: Close Q5 for `video.composer` — design signal: Wins blind pairwise on emotional-fi… |
| `video.soundmixer` | 10.5 | 0.5 | P4 | 1. Q5: PRIMARY GAP: Close Q5 for `video.soundmixer` — design signal: CAS spec on first pass without re… |

### 5-Perf — Performance & Choreography (5 agents, avg 10.5, Q5 remaining 5)

**Group milestone checklist:**
- [ ] All 5 agents pass V2-U1…U5 (maintain green)
- [ ] All 5 complete real human baselines (V2-U8…U10)
- [ ] Audit: every agent in group maturity **11.0**

| Agent | Now | Gap to 11 | Band | First actions to full mark |
|-------|-----|-----------|------|------------------------------|
| `video.choreography` | 10.5 | 0.5 | P5 | 1. Q5: PRIMARY GAP: Close Q5 for `video.choreography` — design signal: Wins blind preference vs choreo… |
| `video.musicvideodirector` | 10.5 | 0.5 | P5 | 1. Q5: PRIMARY GAP: Close Q5 for `video.musicvideodirector` — design signal: Wins label-blind preferen… |
| `video.comedywriter` | 10.5 | 0.5 | P5 | 1. Q5: PRIMARY GAP: Close Q5 for `video.comedywriter` — design signal: Beats UCB-table-read win rate o… |
| `video.talent` | 10.5 | 0.5 | P5 | 1. Q5: PRIMARY GAP: Close Q5 for `video.talent` — design signal: Hold-rate matches top creators in coh… |
| `video.ugccreator` | 10.5 | 0.5 | P5 | 1. Q5: PRIMARY GAP: Close Q5 for `video.ugccreator` — design signal: Beats paid-creator avg ROAS at 0.… |

### 6-Dist — Distribution & Marketing (4 agents, avg 10.5, Q5 remaining 4)

**Group milestone checklist:**
- [ ] All 4 agents pass V2-U1…U5 (maintain green)
- [ ] All 4 complete real human baselines (V2-U8…U10)
- [ ] Audit: every agent in group maturity **11.0**

| Agent | Now | Gap to 11 | Band | First actions to full mark |
|-------|-----|-----------|------|------------------------------|
| `video.creativedirector` | 10.5 | 0.5 | P3 | 1. Q5: PRIMARY GAP: Close Q5 for `video.creativedirector` — design signal: Wins Cannes-jury-emulator g… |
| `video.socialmediastrategist` | 10.5 | 0.5 | P5 | 1. Q5: PRIMARY GAP: Close Q5 for `video.socialmediastrategist` — design signal: Beats agency social le… |
| `video.copywriter` | 10.5 | 0.5 | P5 | 1. Q5: PRIMARY GAP: Close Q5 for `video.copywriter` — design signal: Wins D&AD-style blind preference … |
| `video.performancemarketer` | 10.5 | 0.5 | P5 | 1. Q5: PRIMARY GAP: Close Q5 for `video.performancemarketer` — design signal: Beats senior media buyer… |

### 7-Edu — Education & Domain-Expert (14 agents, avg 10.5, Q5 remaining 14)

**Group milestone checklist:**
- [ ] All 14 agents pass V2-U1…U5 (maintain green)
- [ ] All 14 complete real human baselines (V2-U8…U10)
- [ ] Audit: every agent in group maturity **11.0**

| Agent | Now | Gap to 11 | Band | First actions to full mark |
|-------|-----|-----------|------|------------------------------|
| `video.audiobooknarrator` | 10.5 | 0.5 | P3 | 1. Q5: PRIMARY GAP: Close Q5 for `video.audiobooknarrator` — design signal: Wins AudioFile blind eval … |
| `video.instructionaldesign` | 10.5 | 0.5 | P6 | 1. Q5: PRIMARY GAP: Close Q5 for `video.instructionaldesign` — design signal: Beats ATD-credentialed I… |
| `video.sme` | 10.5 | 0.5 | P6 | 1. Q5: PRIMARY GAP: Close Q5 for `video.sme` — design signal: Passes same certification as human pro |
| `video.factchecker` | 10.5 | 0.5 | P6 | 1. Q5: PRIMARY GAP: Close Q5 for `video.factchecker` — design signal: Lower correction rate than Pulit… |
| `video.medicalillustrator` | 10.5 | 0.5 | P6 | 1. Q5: PRIMARY GAP: Close Q5 for `video.medicalillustrator` — design signal: CMI peers vote ≥pass in b… |
| `video.journalist` | 10.5 | 0.5 | P6 | 1. Q5: PRIMARY GAP: Close Q5 for `video.journalist` — design signal: Lower correction rate + faster fi… |
| `video.compliance` | 10.5 | 0.5 | P6 | 1. Q5: PRIMARY GAP: Close Q5 for `video.compliance` — design signal: Lower legal-risk than median medi… |
| `video.finance` | 10.5 | 0.5 | P6 | 1. Q5: PRIMARY GAP: Close Q5 for `video.finance` — design signal: Passes CFA L3; lower retraction rate… |
| `video.foodstylist` | 10.5 | 0.5 | P6 | 1. Q5: PRIMARY GAP: Close Q5 for `video.foodstylist` — design signal: Wins blind preference vs editori… |
| `video.travelcine` | 10.5 | 0.5 | P6 | 1. Q5: PRIMARY GAP: Close Q5 for `video.travelcine` — design signal: Wins T+L preference at 0.1× sorti… |
| `video.childrensauthor` | 10.5 | 0.5 | P6 | 1. Q5: PRIMARY GAP: Close Q5 for `video.childrensauthor` — design signal: Beats Caldecott-rubric predi… |
| `video.signlanguageinterpreter` | 10.5 | 0.5 | P6 | 1. Q5: PRIMARY GAP: Close Q5 for `video.signlanguageinterpreter` — design signal: Wins blind NAD-revie… |
| `video.localizationqa` | 10.5 | 0.5 | P6 | 1. Q5: PRIMARY GAP: Close Q5 for `video.localizationqa` — design signal: Beats LSP human QA on MQM at … |
| `video.realestatephoto` | 10.5 | 0.5 | P6 | 1. Q5: PRIMARY GAP: Close Q5 for `video.realestatephoto` — design signal: Listing-CTR uplift vs human-… |

### 8-AI — AI-Era Specialists (7 agents, avg 10.5, Q5 remaining 7)

**Group milestone checklist:**
- [ ] All 7 agents pass V2-U1…U5 (maintain green)
- [ ] All 7 complete real human baselines (V2-U8…U10)
- [ ] Audit: every agent in group maturity **11.0**

| Agent | Now | Gap to 11 | Band | First actions to full mark |
|-------|-----|-----------|------|------------------------------|
| `video.promptengineer` | 10.5 | 0.5 | P3 | 1. Q5: PRIMARY GAP: Close Q5 for `video.promptengineer` — design signal: Target shot in ≤3 iterations … |
| `video.voiceclone` | 10.5 | 0.5 | P3 | 1. Q5: PRIMARY GAP: Close Q5 for `video.voiceclone` — design signal: Wins blind MOS vs professional ADR |
| `video.avatardesign` | 10.5 | 0.5 | P5 | 1. Q5: PRIMARY GAP: Close Q5 for `video.avatardesign` — design signal: C2PA-verifiable + Partnership-o… |
| `video.aiqaconsistency` | 10.5 | 0.5 | P5 | 1. Q5: PRIMARY GAP: Close Q5 for `video.aiqaconsistency` — design signal: Catches >95% of senior QC ca… |
| `video.personalizationengineer` | 10.5 | 0.5 | P5 | 1. Q5: PRIMARY GAP: Close Q5 for `video.personalizationengineer` — design signal: Higher share-rate th… |
| `video.trailereditor` | 10.5 | 0.5 | P5 | 1. Q5: PRIMARY GAP: Close Q5 for `video.trailereditor` — design signal: Wins Golden-Trailer-rubric bli… |
| `video.sportsanalyst` | 10.5 | 0.5 | P5 | 1. Q5: PRIMARY GAP: Close Q5 for `video.sportsanalyst` — design signal: Beats ex-athlete on tactical-p… |

### 9-Meta — Specialist Meta-Agents (28 agents, avg 10.5, Q5 remaining 28)

**Group milestone checklist:**
- [ ] All 28 agents pass V2-U1…U5 (maintain green)
- [ ] All 28 complete real human baselines (V2-U8…U10)
- [ ] Audit: every agent in group maturity **11.0**

| Agent | Now | Gap to 11 | Band | First actions to full mark |
|-------|-----|-----------|------|------------------------------|
| `video.orchestrator` | 10.5 | 0.5 | P0 | 1. Q5: PRIMARY GAP: Close Q5 for `video.orchestrator` — design signal: Lower TTD than human EP at same… |
| `video.planner` | 10.5 | 0.5 | P0 | 1. Q5: PRIMARY GAP: Close Q5 for `video.planner` — design signal: Tighter, cheaper plans than EP first… |
| `video.router` | 10.5 | 0.5 | P0 | 1. Q5: PRIMARY GAP: Close Q5 for `video.router` — design signal: Beats human producer in agent/vendor … |
| `video.judge` | 10.5 | 0.5 | P0 | 1. Q5: PRIMARY GAP: Close Q5 for `video.judge` — design signal: Higher κ than median human juror |
| `video.gatekeeper` | 10.5 | 0.5 | P0 | 1. Q5: PRIMARY GAP: Close Q5 for `video.gatekeeper` — design signal: Lower escaped-defect rate than hu… |
| `video.memory` | 10.5 | 0.5 | P0 | 1. Q5: PRIMARY GAP: Close Q5 for `video.memory` — design signal: Higher recall than producer's bible a… |
| `video.ideation` | 10.5 | 0.5 | P1 | 1. Q5: PRIMARY GAP: Close Q5 for `video.ideation` — design signal: Wins agency-pitch shootouts on conc… |
| `video.narrativearc` | 10.5 | 0.5 | P1 | 1. Q5: PRIMARY GAP: Close Q5 for `video.narrativearc` — design signal: Beats WGA first drafts on struc… |
| `video.styletransfer` | 10.5 | 0.5 | P1 | 1. Q5: PRIMARY GAP: Close Q5 for `video.styletransfer` — design signal: Wins blind preference vs human… |
| `video.worldbuilding` | 10.5 | 0.5 | P1 | 1. Q5: PRIMARY GAP: Close Q5 for `video.worldbuilding` — design signal: Lower contradiction rate than … |
| `video.moodboard` | 10.5 | 0.5 | P1 | 1. Q5: PRIMARY GAP: Close Q5 for `video.moodboard` — design signal: Faster + tighter boards than art d… |
| `video.novelty` | 10.5 | 0.5 | P1 | 1. Q5: PRIMARY GAP: Close Q5 for `video.novelty` — design signal: Catches more clichés than experience… |
| `video.emotionalarc` | 10.5 | 0.5 | P1 | 1. Q5: PRIMARY GAP: Close Q5 for `video.emotionalarc` — design signal: Better retention prediction tha… |
| `video.webresearch` | 10.5 | 0.5 | P1 | 1. Q5: PRIMARY GAP: Close Q5 for `video.webresearch` — design signal: Faster + more sources than newsr… |
| `video.archiveresearch` | 10.5 | 0.5 | P1 | 1. Q5: PRIMARY GAP: Close Q5 for `video.archiveresearch` — design signal: Higher primary-source ratio … |
| `video.trendintelligence` | 10.5 | 0.5 | P1 | 1. Q5: PRIMARY GAP: Close Q5 for `video.trendintelligence` — design signal: Earlier detection than hum… |
| `video.competitorintelligence` | 10.5 | 0.5 | P1 | 1. Q5: PRIMARY GAP: Close Q5 for `video.competitorintelligence` — design signal: More comprehensive th… |
| `video.citation` | 10.5 | 0.5 | P1 | 1. Q5: PRIMARY GAP: Close Q5 for `video.citation` — design signal: Lower error rate than newsroom copy… |
| `video.interviewsynthesis` | 10.5 | 0.5 | P1 | 1. Q5: PRIMARY GAP: Close Q5 for `video.interviewsynthesis` — design signal: Faster + richer theme ext… |
| `video.benchmarkresearch` | 10.5 | 0.5 | P1 | 1. Q5: PRIMARY GAP: Close Q5 for `video.benchmarkresearch` — design signal: Faster + broader than ML-r… |
| `video.promptoptimizer` | 10.5 | 0.5 | P1 | 1. Q5: PRIMARY GAP: Close Q5 for `video.promptoptimizer` — design signal: Beats hand-tuned prompts on … |
| `video.costoptimizer` | 10.5 | 0.5 | P1 | 1. Q5: PRIMARY GAP: Close Q5 for `video.costoptimizer` — design signal: Lower $/quality than human CFO… |
| `video.latencyoptimizer` | 10.5 | 0.5 | P1 | 1. Q5: PRIMARY GAP: Close Q5 for `video.latencyoptimizer` — design signal: Lower p95 than human-tuned … |
| `video.retentionoptimizer` | 10.5 | 0.5 | P1 | 1. Q5: PRIMARY GAP: Close Q5 for `video.retentionoptimizer` — design signal: Beats senior YouTube edit… |
| `video.roasoptimizer` | 10.5 | 0.5 | P1 | 1. Q5: PRIMARY GAP: Close Q5 for `video.roasoptimizer` — design signal: Beats senior marketer at equal… |
| `video.accessibilityoptimizer` | 10.5 | 0.5 | P1 | 1. Q5: PRIMARY GAP: Close Q5 for `video.accessibilityoptimizer` — design signal: Catches more a11y def… |
| `video.evaluationharness` | 10.5 | 0.5 | P1 | 1. Q5: PRIMARY GAP: Close Q5 for `video.evaluationharness` — design signal: Catches regressions faster… |
| `video.safetyredteam` | 10.5 | 0.5 | P1 | 1. Q5: PRIMARY GAP: Close Q5 for `video.safetyredteam` — design signal: Higher coverage than internal … |

### 10-Sup — Workflow Support (34 agents, avg 10.5, Q5 remaining 34)

**Group milestone checklist:**
- [ ] All 34 agents pass V2-U1…U5 (maintain green)
- [ ] All 34 complete real human baselines (V2-U8…U10)
- [ ] Audit: every agent in group maturity **11.0**

| Agent | Now | Gap to 11 | Band | First actions to full mark |
|-------|-----|-----------|------|------------------------------|
| `video.critic` | 10.5 | 0.5 | P0 | 1. Q5: PRIMARY GAP: Close Q5 for `video.critic` — design signal: Provides broader qualitative coverage… |
| `video.archiveproducer` | 10.5 | 0.5 | P3 | 1. Q5: PRIMARY GAP: Close Q5 for `video.archiveproducer` — design signal: Assembles reusable archival … |
| `video.analyst` | 10.5 | 0.5 | P6 | 1. Q5: PRIMARY GAP: Close Q5 for `video.analyst` — design signal: Detects actionable performance shift… |
| `video.audiencesim` | 10.5 | 0.5 | P6 | 1. Q5: PRIMARY GAP: Close Q5 for `video.audiencesim` — design signal: Predicts audience reaction earli… |
| `video.accessibility` | 10.5 | 0.5 | P6 | 1. Q5: PRIMARY GAP: Close Q5 for `video.accessibility` — design signal: Finds release-blocking accessi… |
| `video.brand` | 10.5 | 0.5 | P6 | 1. Q5: PRIMARY GAP: Close Q5 for `video.brand` — design signal: Holds cross-channel brand consistency … |
| `video.brandstrategist` | 10.5 | 0.5 | P6 | 1. Q5: PRIMARY GAP: Close Q5 for `video.brandstrategist` — design signal: Produces clearer brand-to-sc… |
| `video.marketing` | 10.5 | 0.5 | P6 | 1. Q5: PRIMARY GAP: Close Q5 for `video.marketing` — design signal: Ships multi-channel launch package… |
| `video.seo` | 10.5 | 0.5 | P6 | 1. Q5: PRIMARY GAP: Close Q5 for `video.seo` — design signal: Lifts discoverability faster than manual… |
| `video.community` | 10.5 | 0.5 | P6 | 1. Q5: PRIMARY GAP: Close Q5 for `video.community` — design signal: Surfaces emerging audience concern… |
| `video.templatedesign` | 10.5 | 0.5 | P6 | 1. Q5: PRIMARY GAP: Close Q5 for `video.templatedesign` — design signal: Produces reusable templates w… |
| `video.ux` | 10.5 | 0.5 | P6 | 1. Q5: PRIMARY GAP: Close Q5 for `video.ux` — design signal: Flags user confusion earlier than launch-… |
| `video.trustsafety` | 10.5 | 0.5 | P6 | 1. Q5: PRIMARY GAP: Close Q5 for `video.trustsafety` — design signal: Catches misuse risk earlier than… |
| `video.crm` | 10.5 | 0.5 | P6 | 1. Q5: PRIMARY GAP: Close Q5 for `video.crm` — design signal: Executes segmentation-to-delivery flow f… |
| `video.legal` | 10.5 | 0.5 | P6 | 1. Q5: PRIMARY GAP: Close Q5 for `video.legal` — design signal: Reduces late-stage legal surprises rel… |
| `video.festivalstrategist` | 10.5 | 0.5 | P6 | 1. Q5: PRIMARY GAP: Close Q5 for `video.festivalstrategist` — design signal: Improves submission targe… |
| `video.lms` | 10.5 | 0.5 | P6 | 1. Q5: PRIMARY GAP: Close Q5 for `video.lms` — design signal: Ships publishable learning packages fast… |
| `video.learnersim` | 10.5 | 0.5 | P6 | 1. Q5: PRIMARY GAP: Close Q5 for `video.learnersim` — design signal: Predicts weak spots before live l… |
| `video.continuity` | 10.5 | 0.5 | P6 | 1. Q5: PRIMARY GAP: Close Q5 for `video.continuity` — design signal: Catches continuity breaks earlier… |
| `video.lipsync` | 10.5 | 0.5 | P6 | 1. Q5: PRIMARY GAP: Close Q5 for `video.lipsync` — design signal: Finds sync drift more precisely than… |
| `video.musicsupervisor` | 10.5 | 0.5 | P6 | 1. Q5: PRIMARY GAP: Close Q5 for `video.musicsupervisor` — design signal: Coordinates music placements… |
| `video.labela_r` | 10.5 | 0.5 | P6 | 1. Q5: PRIMARY GAP: Close Q5 for `video.labela_r` — design signal: Aligns music creative faster than d… |
| `video.labeldigital` | 10.5 | 0.5 | P6 | 1. Q5: PRIMARY GAP: Close Q5 for `video.labeldigital` — design signal: Delivers cleaner label-side pac… |
| `video.deepfakedetection` | 10.5 | 0.5 | P6 | 1. Q5: PRIMARY GAP: Close Q5 for `video.deepfakedetection` — design signal: Catches deceptive syntheti… |
| `video.comms` | 10.5 | 0.5 | P6 | 1. Q5: PRIMARY GAP: Close Q5 for `video.comms` — design signal: Produces faster aligned responses than… |
| `video.standardseditor` | 10.5 | 0.5 | P6 | 1. Q5: PRIMARY GAP: Close Q5 for `video.standardseditor` — design signal: Reduces standards drift bett… |
| `video.ethics` | 10.5 | 0.5 | P6 | 1. Q5: PRIMARY GAP: Close Q5 for `video.ethics` — design signal: Surfaces release risks earlier than r… |
| `video.channelmanager` | 10.5 | 0.5 | P6 | 1. Q5: PRIMARY GAP: Close Q5 for `video.channelmanager` — design signal: Improves publishing disciplin… |
| `video.corrections` | 10.5 | 0.5 | P6 | 1. Q5: PRIMARY GAP: Close Q5 for `video.corrections` — design signal: Resolves post-release issues fas… |
| `video.mpa` | 10.5 | 0.5 | P6 | 1. Q5: PRIMARY GAP: Close Q5 for `video.mpa` — design signal: Prepares cleaner feature-release classif… |
| `video.sales` | 10.5 | 0.5 | P6 | 1. Q5: PRIMARY GAP: Close Q5 for `video.sales` — design signal: Produces sales-ready release packets f… |
| `video.distributor` | 10.5 | 0.5 | P6 | 1. Q5: PRIMARY GAP: Close Q5 for `video.distributor` — design signal: Reduces delivery-spec mismatches… |
| `video.awardsstrategist` | 10.5 | 0.5 | P6 | 1. Q5: PRIMARY GAP: Close Q5 for `video.awardsstrategist` — design signal: Improves awards-timing disc… |
| `video.archivemaster` | 10.5 | 0.5 | P6 | 1. Q5: PRIMARY GAP: Close Q5 for `video.archivemaster` — design signal: Delivers more reliable archive… |

---

## 9. Per-agent full-mark action lists

Each section lists **all actions to hold or reach 11/11 YES**, ordered by question.
Items marked PRIMARY GAP are required for full mark today.

### `video.orchestrator` — OrchestratorAgent (now 10.5/11 → target 11.0)

- **Category:** `9-Meta` · **VA#:** 53 · **Priority band:** P0
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.orchestrator.v1` / `video.rubric.orchestrator.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `media.stub` · live_media=False
- **Design surpass signal:** Lower TTD than human EP at same scope
- **Design self-quality:** DAG completion ≥99.5%; SLA adherence; deadlock = 0
- **Design architecture:** Agentic Graph (LangGraph) — deterministic DAG execution

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.orchestrator` — design signal: Lower TTD than human EP at same scope
- [ ] Protocol path: business/video/evals/agents/video.orchestrator/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.orchestrator`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.orchestrator/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.orchestrator --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.orchestrator --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.orchestrator`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.orchestrator`

### `video.planner` — PlannerAgent (now 10.5/11 → target 11.0)

- **Category:** `9-Meta` · **VA#:** 54 · **Priority band:** P0
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.planner.v1` / `video.rubric.planner.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Tighter, cheaper plans than EP first pass (blind A/B)
- **Design self-quality:** Plan validity (no missing gate); cost variance <10%
- **Design architecture:** ReAct (decompose → estimate → validate → emit DAG)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.planner` — design signal: Tighter, cheaper plans than EP first pass (blind A/B)
- [ ] Protocol path: business/video/evals/agents/video.planner/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.planner`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.planner/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.planner --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.planner --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.planner`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.planner`

### `video.router` — RouterAgent (now 10.5/11 → target 11.0)

- **Category:** `9-Meta` · **VA#:** 55 · **Priority band:** P0
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.router.v1` / `video.rubric.router.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Beats human producer in agent/vendor selection
- **Design self-quality:** Routing accuracy ≥95% vs oracle; cost within budget
- **Design architecture:** Classifier + ReAct (match task embedding → agent capability)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.router` — design signal: Beats human producer in agent/vendor selection
- [ ] Protocol path: business/video/evals/agents/video.router/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.router`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.router/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.router --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.router --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.router`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.router`

### `video.judge` — JudgeAgent (now 10.5/11 → target 11.0)

- **Category:** `9-Meta` · **VA#:** 56 · **Priority band:** P0
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.judge.v1` / `video.rubric.judge.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Higher κ than median human juror
- **Design self-quality:** Inter-rater κ vs expert panel ≥0.8
- **Design architecture:** Multi-agent debate (Du 2023) + LLM-as-Judge (Zheng 2023)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.judge` — design signal: Higher κ than median human juror
- [ ] Protocol path: business/video/evals/agents/video.judge/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.judge`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.judge/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.judge --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.judge --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.judge`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.judge`

### `video.gatekeeper` — GateKeeperAgent (now 10.5/11 → target 11.0)

- **Category:** `9-Meta` · **VA#:** 57 · **Priority band:** P0
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.gatekeeper.v1` / `video.rubric.gatekeeper.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Lower escaped-defect rate than human QA lead
- **Design self-quality:** Zero leaked defects; sign-off SLA ≥99%
- **Design architecture:** Constitutional AI (constitution = phase-gate criteria)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.gatekeeper` — design signal: Lower escaped-defect rate than human QA lead
- [ ] Protocol path: business/video/evals/agents/video.gatekeeper/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.gatekeeper`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.gatekeeper/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.gatekeeper --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.gatekeeper --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.gatekeeper`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.gatekeeper`

### `video.memory` — MemoryAgent (now 10.5/11 → target 11.0)

- **Category:** `9-Meta` · **VA#:** 58 · **Priority band:** P0
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.memory.v1` / `video.rubric.memory.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Higher recall than producer's bible at scale
- **Design self-quality:** Retrieval precision@5 ≥0.9; freshness SLA
- **Design architecture:** Reflexion memory architecture (MemGPT extension)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.memory` — design signal: Higher recall than producer's bible at scale
- [ ] Protocol path: business/video/evals/agents/video.memory/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.memory`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.memory/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.memory --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.memory --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.memory`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.memory`

### `video.critic` — CriticAgent (now 10.5/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 95 · **Priority band:** P0
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.critic.v1` / `video.rubric.critic.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Provides broader qualitative coverage than ad hoc internal taste review
- **Design self-quality:** Interpretive depth, consistency, reviewer-mode diversity
- **Design architecture:** Multi-agent debate as critic panel

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.critic` — design signal: Provides broader qualitative coverage than ad hoc internal taste review
- [ ] Protocol path: business/video/evals/agents/video.critic/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.critic`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.critic/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.critic --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.critic --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.critic`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.critic`

### `video.ideation` — IdeationAgent (now 10.5/11 → target 11.0)

- **Category:** `9-Meta` · **VA#:** 59 · **Priority band:** P1
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.ideation.v1` / `video.rubric.ideation.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Wins agency-pitch shootouts on concept density
- **Design self-quality:** Idea-count; novelty (embedding distance); semantic diversity
- **Design architecture:** Self-Refine + NoveltyAgent as critic

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.ideation` — design signal: Wins agency-pitch shootouts on concept density
- [ ] Protocol path: business/video/evals/agents/video.ideation/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.ideation`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.ideation/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.ideation --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.ideation --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.ideation`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.ideation`

### `video.narrativearc` — NarrativeArcAgent (now 10.5/11 → target 11.0)

- **Category:** `9-Meta` · **VA#:** 60 · **Priority band:** P1
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.narrativearc.v1` / `video.rubric.narrativearc.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Beats WGA first drafts on structural rubric
- **Design self-quality:** Beat-sheet coverage 100%; turning-point spacing; arc curve fit
- **Design architecture:** Self-Refine (rubric: beat-sheet completeness)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.narrativearc` — design signal: Beats WGA first drafts on structural rubric
- [ ] Protocol path: business/video/evals/agents/video.narrativearc/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.narrativearc`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.narrativearc/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.narrativearc --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.narrativearc --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.narrativearc`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.narrativearc`

### `video.styletransfer` — StyleTransferAgent (now 10.5/11 → target 11.0)

- **Category:** `9-Meta` · **VA#:** 61 · **Priority band:** P1
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.styletransfer.v1` / `video.rubric.styletransfer.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `media.stub, media.runway, media.veo` · live_media=True
- **Design surpass signal:** Wins blind preference vs human colorist+grader
- **Design self-quality:** Style-similarity (CLIP/DINO) ≥0.85; cross-shot variance ≤τ
- **Design architecture:** Self-Refine (CLIP style score as feedback)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.styletransfer` — design signal: Wins blind preference vs human colorist+grader
- [ ] Protocol path: business/video/evals/agents/video.styletransfer/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.styletransfer`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.styletransfer/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.styletransfer --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.styletransfer --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Harden: live media remains env-gated; offline golden must stay green without network.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.styletransfer`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.styletransfer`

### `video.worldbuilding` — WorldBuildingAgent (now 10.5/11 → target 11.0)

- **Category:** `9-Meta` · **VA#:** 62 · **Priority band:** P1
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.worldbuilding.v1` / `video.rubric.worldbuilding.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Lower contradiction rate than writers' bibles at 10× volume
- **Design self-quality:** Internal-consistency (no contradictions); rule-completeness
- **Design architecture:** Reflexion (contradiction corrections → episodic memory)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.worldbuilding` — design signal: Lower contradiction rate than writers' bibles at 10× volume
- [ ] Protocol path: business/video/evals/agents/video.worldbuilding/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.worldbuilding`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.worldbuilding/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.worldbuilding --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.worldbuilding --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.worldbuilding`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.worldbuilding`

### `video.moodboard` — MoodBoardAgent (now 10.5/11 → target 11.0)

- **Category:** `9-Meta` · **VA#:** 63 · **Priority band:** P1
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.moodboard.v1` / `video.rubric.moodboard.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Faster + tighter boards than art director (blind A/B)
- **Design self-quality:** Reference coherence (cluster tightness); brief alignment
- **Design architecture:** ReAct (search → cluster → layout → validate coherence)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.moodboard` — design signal: Faster + tighter boards than art director (blind A/B)
- [ ] Protocol path: business/video/evals/agents/video.moodboard/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.moodboard`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.moodboard/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.moodboard --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.moodboard --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.moodboard`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.moodboard`

### `video.novelty` — NoveltyAgent / Anti-Cliché Critic (now 10.5/11 → target 11.0)

- **Category:** `9-Meta` · **VA#:** 64 · **Priority band:** P1
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.novelty.v1` / `video.rubric.novelty.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Catches more clichés than experienced script editor
- **Design self-quality:** Cliché-hit count; novelty score vs category prior
- **Design architecture:** LLM-as-Judge (anti-cliché constitution)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.novelty` — design signal: Catches more clichés than experienced script editor
- [ ] Protocol path: business/video/evals/agents/video.novelty/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.novelty`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.novelty/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.novelty --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.novelty --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.novelty`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.novelty`

### `video.emotionalarc` — EmotionalArcAgent (now 10.5/11 → target 11.0)

- **Category:** `9-Meta` · **VA#:** 65 · **Priority band:** P1
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.emotionalarc.v1` / `video.rubric.emotionalarc.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Better retention prediction than NRG test-screening cards
- **Design self-quality:** Curve-fit to target; biosignal-proxy regression accuracy
- **Design architecture:** Self-Refine (emotional-arc curve as rubric target)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.emotionalarc` — design signal: Better retention prediction than NRG test-screening cards
- [ ] Protocol path: business/video/evals/agents/video.emotionalarc/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.emotionalarc`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.emotionalarc/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.emotionalarc --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.emotionalarc --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.emotionalarc`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.emotionalarc`

### `video.webresearch` — WebResearchAgent (now 10.5/11 → target 11.0)

- **Category:** `9-Meta` · **VA#:** 66 · **Priority band:** P1
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.webresearch.v1` / `video.rubric.webresearch.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Faster + more sources than newsroom researcher
- **Design self-quality:** Source-grade per claim; citation precision; recency hit
- **Design architecture:** ReAct (query → fetch → extract → grade → cite)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.webresearch` — design signal: Faster + more sources than newsroom researcher
- [ ] Protocol path: business/video/evals/agents/video.webresearch/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.webresearch`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.webresearch/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.webresearch --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.webresearch --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.webresearch`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.webresearch`

### `video.archiveresearch` — ArchiveResearchAgent (now 10.5/11 → target 11.0)

- **Category:** `9-Meta` · **VA#:** 67 · **Priority band:** P1
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.archiveresearch.v1` / `video.rubric.archiveresearch.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Higher primary-source ratio than doc producer
- **Design self-quality:** Primary-source ratio; archive-coverage breadth
- **Design architecture:** ReAct (formulate query → search archive → extract → grade source)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.archiveresearch` — design signal: Higher primary-source ratio than doc producer
- [ ] Protocol path: business/video/evals/agents/video.archiveresearch/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.archiveresearch`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.archiveresearch/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.archiveresearch --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.archiveresearch --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.archiveresearch`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.archiveresearch`

### `video.trendintelligence` — TrendIntelligenceAgent (now 10.5/11 → target 11.0)

- **Category:** `9-Meta` · **VA#:** 68 · **Priority band:** P1
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.trendintelligence.v1` / `video.rubric.trendintelligence.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Earlier detection than human strategists at higher precision
- **Design self-quality:** Prediction lead time vs peak; precision/recall on trend list
- **Design architecture:** ReAct + time-series anomaly detection

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.trendintelligence` — design signal: Earlier detection than human strategists at higher precision
- [ ] Protocol path: business/video/evals/agents/video.trendintelligence/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.trendintelligence`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.trendintelligence/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.trendintelligence --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.trendintelligence --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.trendintelligence`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.trendintelligence`

### `video.competitorintelligence` — CompetitorIntelligenceAgent (now 10.5/11 → target 11.0)

- **Category:** `9-Meta` · **VA#:** 69 · **Priority band:** P1
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.competitorintelligence.v1` / `video.rubric.competitorintelligence.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** More comprehensive than agency strategy decks
- **Design self-quality:** Coverage % of competitor set; our-novelty vs landscape
- **Design architecture:** ReAct (scrape competitor → classify → report gaps)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.competitorintelligence` — design signal: More comprehensive than agency strategy decks
- [ ] Protocol path: business/video/evals/agents/video.competitorintelligence/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.competitorintelligence`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.competitorintelligence/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.competitorintelligence --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.competitorintelligence --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.competitorintelligence`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.competitorintelligence`

### `video.citation` — CitationAgent (now 10.5/11 → target 11.0)

- **Category:** `9-Meta` · **VA#:** 70 · **Priority band:** P1
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.citation.v1` / `video.rubric.citation.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Lower error rate than newsroom copy desk
- **Design self-quality:** Citation format 100% valid; primary % ≥target
- **Design architecture:** Self-Refine (format validator + source grader as rubric)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.citation` — design signal: Lower error rate than newsroom copy desk
- [ ] Protocol path: business/video/evals/agents/video.citation/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.citation`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.citation/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.citation --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.citation --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.citation`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.citation`

### `video.interviewsynthesis` — InterviewSynthesisAgent (now 10.5/11 → target 11.0)

- **Category:** `9-Meta` · **VA#:** 71 · **Priority band:** P1
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.interviewsynthesis.v1` / `video.rubric.interviewsynthesis.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Faster + richer theme extraction than qualitative researcher
- **Design self-quality:** Inter-coder agreement on themes; consent integrity
- **Design architecture:** Reflexion (interviewer refines questions based on theme gaps)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.interviewsynthesis` — design signal: Faster + richer theme extraction than qualitative researcher
- [ ] Protocol path: business/video/evals/agents/video.interviewsynthesis/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.interviewsynthesis`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.interviewsynthesis/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.interviewsynthesis --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.interviewsynthesis --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.interviewsynthesis`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.interviewsynthesis`

### `video.benchmarkresearch` — BenchmarkResearchAgent (now 10.5/11 → target 11.0)

- **Category:** `9-Meta` · **VA#:** 72 · **Priority band:** P1
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.benchmarkresearch.v1` / `video.rubric.benchmarkresearch.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Faster + broader than ML-research team
- **Design self-quality:** Coverage of benchmarks; freshness ≤7 days
- **Design architecture:** ReAct (poll leaderboards → detect change → alert)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.benchmarkresearch` — design signal: Faster + broader than ML-research team
- [ ] Protocol path: business/video/evals/agents/video.benchmarkresearch/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.benchmarkresearch`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.benchmarkresearch/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.benchmarkresearch --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.benchmarkresearch --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.benchmarkresearch`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.benchmarkresearch`

### `video.promptoptimizer` — PromptOptimizerAgent (now 10.5/11 → target 11.0)

- **Category:** `9-Meta` · **VA#:** 73 · **Priority band:** P1
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.promptoptimizer.v1` / `video.rubric.promptoptimizer.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Beats hand-tuned prompts on held-out briefs
- **Design self-quality:** Score uplift per iteration; convergence speed
- **Design architecture:** DSPy compilation + OPRO meta-optimization

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.promptoptimizer` — design signal: Beats hand-tuned prompts on held-out briefs
- [ ] Protocol path: business/video/evals/agents/video.promptoptimizer/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.promptoptimizer`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.promptoptimizer/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.promptoptimizer --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.promptoptimizer --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.promptoptimizer`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.promptoptimizer`

### `video.costoptimizer` — CostOptimizerAgent (now 10.5/11 → target 11.0)

- **Category:** `9-Meta` · **VA#:** 74 · **Priority band:** P1
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.costoptimizer.v1` / `video.rubric.costoptimizer.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Lower $/quality than human CFO routing
- **Design self-quality:** $/successful-task; Pareto distance from frontier
- **Design architecture:** ReAct (evaluate task → pick cheapest model meeting threshold)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.costoptimizer` — design signal: Lower $/quality than human CFO routing
- [ ] Protocol path: business/video/evals/agents/video.costoptimizer/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.costoptimizer`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.costoptimizer/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.costoptimizer --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.costoptimizer --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.costoptimizer`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.costoptimizer`

### `video.latencyoptimizer` — LatencyOptimizerAgent (now 10.5/11 → target 11.0)

- **Category:** `9-Meta` · **VA#:** 75 · **Priority band:** P1
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.latencyoptimizer.v1` / `video.rubric.latencyoptimizer.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Lower p95 than human-tuned pipeline
- **Design self-quality:** p50/p95 latency; throughput/GPU-hour
- **Design architecture:** Tool-use profiling + automated pipeline restructuring

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.latencyoptimizer` — design signal: Lower p95 than human-tuned pipeline
- [ ] Protocol path: business/video/evals/agents/video.latencyoptimizer/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.latencyoptimizer`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.latencyoptimizer/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.latencyoptimizer --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.latencyoptimizer --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.latencyoptimizer`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.latencyoptimizer`

### `video.retentionoptimizer` — RetentionOptimizerAgent (now 10.5/11 → target 11.0)

- **Category:** `9-Meta` · **VA#:** 76 · **Priority band:** P1
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.retentionoptimizer.v1` / `video.rubric.retentionoptimizer.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Beats senior YouTube editor on AVD lift (A/B)
- **Design self-quality:** Predicted retention vs actual; AVD lift over control
- **Design architecture:** RLAIF (reward = retention uplift from real analytics)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.retentionoptimizer` — design signal: Beats senior YouTube editor on AVD lift (A/B)
- [ ] Protocol path: business/video/evals/agents/video.retentionoptimizer/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.retentionoptimizer`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.retentionoptimizer/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.retentionoptimizer --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.retentionoptimizer --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.retentionoptimizer`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.retentionoptimizer`

### `video.roasoptimizer` — ROASOptimizerAgent (now 10.5/11 → target 11.0)

- **Category:** `9-Meta` · **VA#:** 77 · **Priority band:** P1
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.roasoptimizer.v1` / `video.rubric.roasoptimizer.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Beats senior marketer at equal budget
- **Design self-quality:** ROAS uplift vs control; significance ≥95%
- **Design architecture:** RLAIF (reward = real ROAS from ad platform feedback)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.roasoptimizer` — design signal: Beats senior marketer at equal budget
- [ ] Protocol path: business/video/evals/agents/video.roasoptimizer/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.roasoptimizer`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.roasoptimizer/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.roasoptimizer --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.roasoptimizer --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.roasoptimizer`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.roasoptimizer`

### `video.accessibilityoptimizer` — AccessibilityOptimizerAgent (now 10.5/11 → target 11.0)

- **Category:** `9-Meta` · **VA#:** 78 · **Priority band:** P1
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.accessibilityoptimizer.v1` / `video.rubric.accessibilityoptimizer.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Catches more a11y defects than ADA-certified auditor
- **Design self-quality:** Conformance 100% AA, ≥90% AAA; caption WER ≤2%
- **Design architecture:** Constitutional AI (constitution = WCAG 2.2 success criteria)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.accessibilityoptimizer` — design signal: Catches more a11y defects than ADA-certified auditor
- [ ] Protocol path: business/video/evals/agents/video.accessibilityoptimizer/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.accessibilityoptimizer`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.accessibilityoptimizer/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.accessibilityoptimizer --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.accessibilityoptimizer --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.accessibilityoptimizer`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.accessibilityoptimizer`

### `video.evaluationharness` — EvaluationHarnessAgent (now 10.5/11 → target 11.0)

- **Category:** `9-Meta` · **VA#:** 79 · **Priority band:** P1
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.evaluationharness.v1` / `video.rubric.evaluationharness.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Catches regressions faster than ML-eng rotation
- **Design self-quality:** Regression precision/recall; alert latency <1h
- **Design architecture:** Tool-use / ReAct (run benchmark → compare → alert if regressed)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.evaluationharness` — design signal: Catches regressions faster than ML-eng rotation
- [ ] Protocol path: business/video/evals/agents/video.evaluationharness/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.evaluationharness`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.evaluationharness/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.evaluationharness --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.evaluationharness --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.evaluationharness`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.evaluationharness`

### `video.safetyredteam` — SafetyRedTeamAgent (now 10.5/11 → target 11.0)

- **Category:** `9-Meta` · **VA#:** 80 · **Priority band:** P1
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.safetyredteam.v1` / `video.rubric.safetyredteam.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Higher coverage than internal red-team rotation
- **Design self-quality:** Attack-success kept ≤1%; taxonomy coverage
- **Design architecture:** Multi-agent debate (red-team vs defender) + adversarial search

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.safetyredteam` — design signal: Higher coverage than internal red-team rotation
- [ ] Protocol path: business/video/evals/agents/video.safetyredteam/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.safetyredteam`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.safetyredteam/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.safetyredteam --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.safetyredteam --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.safetyredteam`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.safetyredteam`

### `video.director` — DirectorAgent (now 10.5/11 → target 11.0)

- **Category:** `1-ATL` · **VA#:** 1 · **Priority band:** P2
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.director.v1` / `video.rubric.director.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Wins ≥55% blind pairwise vs DGA cuts (Arena)
- **Design self-quality:** Shot-intent fidelity (CLIP-T ≥0.32); story-beat coverage 100%; pacing curve matches genre prior
- **Design architecture:** Self-Refine + LLM-as-Judge (rubric: genre priors)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.director` — design signal: Wins ≥55% blind pairwise vs DGA cuts (Arena)
- [ ] Protocol path: business/video/evals/agents/video.director/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.director`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.director/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.director --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.director --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.director`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.director`

### `video.producer` — ProducerAgent / EP (now 10.5/11 → target 11.0)

- **Category:** `1-ATL` · **VA#:** 2 · **Priority band:** P2
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.producer.v1` / `video.rubric.producer.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Beats PGA schedules at 0.6× cost with equal CSAT
- **Design self-quality:** On-time delivery rate; budget variance <±5%; talent satisfaction (RLHF)
- **Design architecture:** Agentic Graph (LangGraph DAG) + ReAct for tool calls

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.producer` — design signal: Beats PGA schedules at 0.6× cost with equal CSAT
- [ ] Protocol path: business/video/evals/agents/video.producer/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.producer`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.producer/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.producer --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.producer --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.producer`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.producer`

### `video.screenwriter` — ScreenwriterAgent (now 10.5/11 → target 11.0)

- **Category:** `1-ATL` · **VA#:** 3 · **Priority band:** P2
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.screenwriter.v1` / `video.rubric.screenwriter.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Wins ≥50% blind read vs Black List Top-10 (WGA panel emulated)
- **Design self-quality:** Save-the-Cat beat pass; dialogue distinctiveness (embedding distance ≥τ); rewrite delta
- **Design architecture:** Reflexion (Shinn 2023) — verbal RL with episodic memory

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.screenwriter` — design signal: Wins ≥50% blind read vs Black List Top-10 (WGA panel emulated)
- [ ] Protocol path: business/video/evals/agents/video.screenwriter/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.screenwriter`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.screenwriter/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.screenwriter --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.screenwriter --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.screenwriter`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.screenwriter`

### `video.showrunner` — ShowrunnerAgent (now 10.5/11 → target 11.0)

- **Category:** `1-ATL` · **VA#:** 4 · **Priority band:** P2
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.showrunner.v1` / `video.rubric.showrunner.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Series Bible coverage ≥99% across 10 eps (vs ~95% human)
- **Design self-quality:** Arc continuity score; character-thread completion; tonal variance within bounds
- **Design architecture:** Multi-agent debate (Du 2023) + MemoryAgent retrieval

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.showrunner` — design signal: Series Bible coverage ≥99% across 10 eps (vs ~95% human)
- [ ] Protocol path: business/video/evals/agents/video.showrunner/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.showrunner`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.showrunner/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.showrunner --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.showrunner --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.showrunner`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.showrunner`

### `video.casting` — CastingAgent (now 10.5/11 → target 11.0)

- **Category:** `1-ATL` · **VA#:** 5 · **Priority band:** P2
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.casting.v1` / `video.rubric.casting.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Beats CSA casting in blind preference; hours vs weeks turnaround
- **Design self-quality:** Character-voice fit (audience preference); consent compliance 100%
- **Design architecture:** LLM-as-Judge (pairwise preference on voice samples)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.casting` — design signal: Beats CSA casting in blind preference; hours vs weeks turnaround
- [ ] Protocol path: business/video/evals/agents/video.casting/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.casting`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.casting/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.casting --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.casting --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.casting`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.casting`

### `video.editor` — EditorAgent (now 10.5/11 → target 11.0)

- **Category:** `3-Edit` · **VA#:** 9 · **Priority band:** P3
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.editor.v1` / `video.rubric.editor.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `media.stub, media.runway` · live_media=True
- **Design surpass signal:** Wins ≥55% pairwise vs ACE-credited cuts
- **Design self-quality:** Pacing curve matches genre; Murch "Rule of Six" score; AVD ≥ target
- **Design architecture:** Self-Refine (rubric: Murch Rule of Six)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.editor` — design signal: Wins ≥55% pairwise vs ACE-credited cuts
- [ ] Protocol path: business/video/evals/agents/video.editor/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.editor`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.editor/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.editor --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.editor --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Harden: live media remains env-gated; offline golden must stay green without network.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.editor`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.editor`

### `video.animator_2d` — AnimatorAgent (2D/3D) (now 10.5/11 → target 11.0)

- **Category:** `3-Edit` · **VA#:** 12 · **Priority band:** P3
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.animator_2d.v1` / `video.rubric.animator_2d.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `media.stub, media.runway` · live_media=True
- **Design surpass signal:** Beats junior on Annie rubric; equals senior at 5× throughput
- **Design self-quality:** 12-principles score; arc smoothness; lip-sync phoneme accuracy
- **Design architecture:** Self-Refine (rubric: 12 principles checklist)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.animator_2d` — design signal: Beats junior on Annie rubric; equals senior at 5× throughput
- [ ] Protocol path: business/video/evals/agents/video.animator_2d/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.animator_2d`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.animator_2d/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.animator_2d --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.animator_2d --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Harden: live media remains env-gated; offline golden must stay green without network.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.animator_2d`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.animator_2d`

### `video.motiongraphics` — MotionGraphicsAgent (now 10.5/11 → target 11.0)

- **Category:** `3-Edit` · **VA#:** 13 · **Priority band:** P3
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.motiongraphics.v1` / `video.rubric.motiongraphics.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `media.stub, media.runway` · live_media=True
- **Design surpass signal:** Wins agency RFP shootouts on speed + on-brand fidelity
- **Design self-quality:** Typographic hierarchy; brand compliance; readability at thumbnail
- **Design architecture:** ReAct — reason about brand guidelines then render

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.motiongraphics` — design signal: Wins agency RFP shootouts on speed + on-brand fidelity
- [ ] Protocol path: business/video/evals/agents/video.motiongraphics/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.motiongraphics`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.motiongraphics/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.motiongraphics --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.motiongraphics --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Harden: live media remains env-gated; offline golden must stay green without network.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.motiongraphics`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.motiongraphics`

### `video.sounddesign` — SoundDesignAgent (now 10.5/11 → target 11.0)

- **Category:** `4-Snd` · **VA#:** 19 · **Priority band:** P3
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.sounddesign.v1` / `video.rubric.sounddesign.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `media.stub, media.elevenlabs` · live_media=True
- **Design surpass signal:** Wins MPSE pairwise on horror/sci-fi
- **Design self-quality:** Spectral diversity; sync ≤±1 frame; loudness -23 LUFS
- **Design architecture:** ReAct (search SFX lib → validate sync → mix)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.sounddesign` — design signal: Wins MPSE pairwise on horror/sci-fi
- [ ] Protocol path: business/video/evals/agents/video.sounddesign/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.sounddesign`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.sounddesign/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.sounddesign --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.sounddesign --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Harden: live media remains env-gated; offline golden must stay green without network.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.sounddesign`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.sounddesign`

### `video.voiceover` — VoiceOverAgent (now 10.5/11 → target 11.0)

- **Category:** `4-Snd` · **VA#:** 21 · **Priority band:** P3
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.voiceover.v1` / `video.rubric.voiceover.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `media.stub, media.elevenlabs` · live_media=True
- **Design surpass signal:** Beats junior VO in blind preference; matches senior on emotion
- **Design self-quality:** Prosody match; pronunciation 100%; emotion tag match
- **Design architecture:** LLM-as-Judge (MOS scoring rubric)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.voiceover` — design signal: Beats junior VO in blind preference; matches senior on emotion
- [ ] Protocol path: business/video/evals/agents/video.voiceover/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.voiceover`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.voiceover/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.voiceover --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.voiceover --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Harden: live media remains env-gated; offline golden must stay green without network.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.voiceover`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.voiceover`

### `video.creativedirector` — CreativeDirectorAgent (now 10.5/11 → target 11.0)

- **Category:** `6-Dist` · **VA#:** 30 · **Priority band:** P3
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.creativedirector.v1` / `video.rubric.creativedirector.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `media.stub, media.sora, media.veo, media.runway` · live_media=True
- **Design surpass signal:** Wins Cannes-jury-emulator gold vs human shortlists
- **Design self-quality:** Concept distinctiveness (embedding novelty); award-rubric predicted score
- **Design architecture:** Multi-agent debate (panel of IdeationAgent + NoveltyAgent)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.creativedirector` — design signal: Wins Cannes-jury-emulator gold vs human shortlists
- [ ] Protocol path: business/video/evals/agents/video.creativedirector/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.creativedirector`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.creativedirector/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.creativedirector --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.creativedirector --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Harden: live media remains env-gated; offline golden must stay green without network.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.creativedirector`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.creativedirector`

### `video.audiobooknarrator` — AudiobookNarratorAgent (now 10.5/11 → target 11.0)

- **Category:** `7-Edu` · **VA#:** 42 · **Priority band:** P3
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.audiobooknarrator.v1` / `video.rubric.audiobooknarrator.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `media.stub, media.elevenlabs` · live_media=True
- **Design surpass signal:** Wins AudioFile blind eval at fraction of studio time
- **Design self-quality:** Vocal stamina (no drift 60min); character distinction (embedding distance)
- **Design architecture:** Self-Refine (drift detection as feedback loop)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.audiobooknarrator` — design signal: Wins AudioFile blind eval at fraction of studio time
- [ ] Protocol path: business/video/evals/agents/video.audiobooknarrator/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.audiobooknarrator`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.audiobooknarrator/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.audiobooknarrator --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.audiobooknarrator --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Harden: live media remains env-gated; offline golden must stay green without network.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.audiobooknarrator`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.audiobooknarrator`

### `video.promptengineer` — PromptEngineerAgent / GeneratorOperator (now 10.5/11 → target 11.0)

- **Category:** `8-AI` · **VA#:** 46 · **Priority band:** P3
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.promptengineer.v1` / `video.rubric.promptengineer.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `media.stub, media.sora, media.veo, media.runway` · live_media=True
- **Design surpass signal:** Target shot in ≤3 iterations vs human avg 10
- **Design self-quality:** Prompt→output CLIP-T; iteration count to acceptance; seed reproducibility
- **Design architecture:** DSPy / OPRO prompt optimization (Yang 2023)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.promptengineer` — design signal: Target shot in ≤3 iterations vs human avg 10
- [ ] Protocol path: business/video/evals/agents/video.promptengineer/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.promptengineer`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.promptengineer/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.promptengineer --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.promptengineer --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Harden: live media remains env-gated; offline golden must stay green without network.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.promptengineer`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.promptengineer`

### `video.voiceclone` — VoiceCloneAgent / LipSyncSpecialist (now 10.5/11 → target 11.0)

- **Category:** `8-AI` · **VA#:** 48 · **Priority band:** P3
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.voiceclone.v1` / `video.rubric.voiceclone.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `media.stub, media.elevenlabs` · live_media=True
- **Design surpass signal:** Wins blind MOS vs professional ADR
- **Design self-quality:** Voice MOS ≥4.2; phoneme-viseme error <40ms; consent verified
- **Design architecture:** Self-Refine + MOS scoring model as judge

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.voiceclone` — design signal: Wins blind MOS vs professional ADR
- [ ] Protocol path: business/video/evals/agents/video.voiceclone/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.voiceclone`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.voiceclone/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.voiceclone --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.voiceclone --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Harden: live media remains env-gated; offline golden must stay green without network.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.voiceclone`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.voiceclone`

### `video.archiveproducer` — ArchiveProducerAgent (now 10.5/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 105 · **Priority band:** P3
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.archiveproducer.v1` / `video.rubric.archiveproducer.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `media.stub, media.sora, media.veo, media.runway` · live_media=True
- **Design surpass signal:** Assembles reusable archival packages more cleanly than manual gather-and-sort workflows
- **Design self-quality:** Source package completeness, rights coverage, provenance preservation
- **Design architecture:** ReAct over archival manifests

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.archiveproducer` — design signal: Assembles reusable archival packages more cleanly than manual gather-and-sort workflows
- [ ] Protocol path: business/video/evals/agents/video.archiveproducer/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.archiveproducer`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.archiveproducer/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.archiveproducer --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.archiveproducer --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Harden: live media remains env-gated; offline golden must stay green without network.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.archiveproducer`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.archiveproducer`

### `video.cinematographer` — CinematographerAgent (DoP) (now 10.5/11 → target 11.0)

- **Category:** `2-Cam` · **VA#:** 6 · **Priority band:** P4
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.cinematographer.v1` / `video.rubric.cinematographer.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Beats ASC peer-juried reels in blind aesthetic preference
- **Design self-quality:** Rule-of-thirds/leading-lines score; exposure histogram in zone; color-temp consistency
- **Design architecture:** Self-Refine + CLIP-based aesthetic scoring

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.cinematographer` — design signal: Beats ASC peer-juried reels in blind aesthetic preference
- [ ] Protocol path: business/video/evals/agents/video.cinematographer/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.cinematographer`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.cinematographer/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.cinematographer --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.cinematographer --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.cinematographer`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.cinematographer`

### `video.cameraoperator` — CameraOperatorAgent (now 10.5/11 → target 11.0)

- **Category:** `2-Cam` · **VA#:** 7 · **Priority band:** P4
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.cameraoperator.v1` / `video.rubric.cameraoperator.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Focus-pull accuracy >99% vs SOC ~97% baseline
- **Design self-quality:** Frame steadiness, focus-hit %, action centering
- **Design architecture:** ReAct (Yao 2022) — reason about framing then call renderer

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.cameraoperator` — design signal: Focus-pull accuracy >99% vs SOC ~97% baseline
- [ ] Protocol path: business/video/evals/agents/video.cameraoperator/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.cameraoperator`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.cameraoperator/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.cameraoperator --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.cameraoperator --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.cameraoperator`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.cameraoperator`

### `video.dronepilot` — DronePilotAgent (now 10.5/11 → target 11.0)

- **Category:** `2-Cam` · **VA#:** 8 · **Priority band:** P4
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.dronepilot.v1` / `video.rubric.dronepilot.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Competition-grade smoothness at 10× sortie rate; zero violations
- **Design self-quality:** Path smoothness; geofence compliance 100%; horizon stability
- **Design architecture:** Constitutional AI (safety constitution: FAA rules as principles)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.dronepilot` — design signal: Competition-grade smoothness at 10× sortie rate; zero violations
- [ ] Protocol path: business/video/evals/agents/video.dronepilot/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.dronepilot`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.dronepilot/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.dronepilot --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.dronepilot --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.dronepilot`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.dronepilot`

### `video.colorist` — ColoristAgent (now 10.5/11 → target 11.0)

- **Category:** `3-Edit` · **VA#:** 10 · **Priority band:** P4
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.colorist.v1` / `video.rubric.colorist.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Beats junior colorist in blind preference; matches senior within ΔE
- **Design self-quality:** ΔE drift <2; skin-tone IT8 alignment; mood vector match
- **Design architecture:** Self-Refine + tool-use (colorimeter validation)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.colorist` — design signal: Beats junior colorist in blind preference; matches senior within ΔE
- [ ] Protocol path: business/video/evals/agents/video.colorist/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.colorist`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.colorist/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.colorist --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.colorist --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.colorist`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.colorist`

### `video.vfxsupervisor` — VFXSupervisorAgent (now 10.5/11 → target 11.0)

- **Category:** `3-Edit` · **VA#:** 11 · **Priority band:** P4
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.vfxsupervisor.v1` / `video.rubric.vfxsupervisor.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Weta-grade QC pass rate at fraction of time
- **Design self-quality:** Shot-completion %; comp-error pixel count; CLIP-T vs plate
- **Design architecture:** Agentic Graph (fan-out per shot) + LLM-as-Judge (QC rubric)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.vfxsupervisor` — design signal: Weta-grade QC pass rate at fraction of time
- [ ] Protocol path: business/video/evals/agents/video.vfxsupervisor/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.vfxsupervisor`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.vfxsupervisor/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.vfxsupervisor --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.vfxsupervisor --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.vfxsupervisor`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.vfxsupervisor`

### `video.storyboard` — StoryboardAgent (now 10.5/11 → target 11.0)

- **Category:** `3-Edit` · **VA#:** 14 · **Priority band:** P4
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.storyboard.v1` / `video.rubric.storyboard.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Pixar story-trust pass rate at minutes per page
- **Design self-quality:** Shot-language fidelity; coverage completeness; staging clarity
- **Design architecture:** Self-Refine (director feedback loop)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.storyboard` — design signal: Pixar story-trust pass rate at minutes per page
- [ ] Protocol path: business/video/evals/agents/video.storyboard/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.storyboard`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.storyboard/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.storyboard --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.storyboard --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.storyboard`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.storyboard`

### `video.conceptartist` — ConceptArtistAgent (now 10.5/11 → target 11.0)

- **Category:** `3-Edit` · **VA#:** 15 · **Priority band:** P4
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.conceptartist.v1` / `video.rubric.conceptartist.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Wins art-director shootouts on iteration speed
- **Design self-quality:** Style-bible adherence; silhouette readability; design coherence
- **Design architecture:** Self-Refine + style-reference CLIP scoring

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.conceptartist` — design signal: Wins art-director shootouts on iteration speed
- [ ] Protocol path: business/video/evals/agents/video.conceptartist/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.conceptartist`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.conceptartist/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.conceptartist --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.conceptartist --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.conceptartist`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.conceptartist`

### `video.productiondesign` — ProductionDesignAgent (now 10.5/11 → target 11.0)

- **Category:** `3-Edit` · **VA#:** 16 · **Priority band:** P4
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.productiondesign.v1` / `video.rubric.productiondesign.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Wins ADG blind comparisons on period-research depth
- **Design self-quality:** Period accuracy; palette coherence; build feasibility
- **Design architecture:** Reflexion (stores period-research corrections in memory)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.productiondesign` — design signal: Wins ADG blind comparisons on period-research depth
- [ ] Protocol path: business/video/evals/agents/video.productiondesign/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.productiondesign`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.productiondesign/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.productiondesign --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.productiondesign --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.productiondesign`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.productiondesign`

### `video.costumedesign` — CostumeDesignAgent (now 10.5/11 → target 11.0)

- **Category:** `3-Edit` · **VA#:** 17 · **Priority band:** P4
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.costumedesign.v1` / `video.rubric.costumedesign.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Beats CDG juniors on period accuracy benchmarks
- **Design self-quality:** Period/fashion accuracy; silhouette read; palette fit
- **Design architecture:** Self-Refine (period-accuracy rubric)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.costumedesign` — design signal: Beats CDG juniors on period accuracy benchmarks
- [ ] Protocol path: business/video/evals/agents/video.costumedesign/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.costumedesign`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.costumedesign/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.costumedesign --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.costumedesign --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.costumedesign`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.costumedesign`

### `video.mua_makeup` — MUAAgent (Makeup/Hair/SFX) (now 10.5/11 → target 11.0)

- **Category:** `3-Edit` · **VA#:** 18 · **Priority band:** P4
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.mua_makeup.v1` / `video.rubric.mua_makeup.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Continuity break rate <0.5% (vs ~2% human)
- **Design self-quality:** Continuity hash across takes; skin-tone realism (FID)
- **Design architecture:** Constitutional AI (constitution: continuity rules)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.mua_makeup` — design signal: Continuity break rate <0.5% (vs ~2% human)
- [ ] Protocol path: business/video/evals/agents/video.mua_makeup/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.mua_makeup`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.mua_makeup/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.mua_makeup --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.mua_makeup --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.mua_makeup`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.mua_makeup`

### `video.composer` — ComposerAgent (now 10.5/11 → target 11.0)

- **Category:** `4-Snd` · **VA#:** 20 · **Priority band:** P4
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.composer.v1` / `video.rubric.composer.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Wins blind pairwise on emotional-fit vs working composers
- **Design self-quality:** Cue-to-emotion alignment (valence/arousal regression); thematic recurrence
- **Design architecture:** Self-Refine + Emotional-Arc validation (biosignal proxy)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.composer` — design signal: Wins blind pairwise on emotional-fit vs working composers
- [ ] Protocol path: business/video/evals/agents/video.composer/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.composer`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.composer/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.composer --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.composer --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.composer`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.composer`

### `video.soundmixer` — SoundMixerAgent (Re-recording) (now 10.5/11 → target 11.0)

- **Category:** `4-Snd` · **VA#:** 22 · **Priority band:** P4
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.soundmixer.v1` / `video.rubric.soundmixer.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** CAS spec on first pass without rework
- **Design self-quality:** LUFS target; STOI ≥0.85; spec-deliverable pass
- **Design architecture:** Constitutional AI (constitution: broadcast-spec rules)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.soundmixer` — design signal: CAS spec on first pass without rework
- [ ] Protocol path: business/video/evals/agents/video.soundmixer/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.soundmixer`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.soundmixer/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.soundmixer --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.soundmixer --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.soundmixer`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.soundmixer`

### `video.choreography` — ChoreographyAgent (now 10.5/11 → target 11.0)

- **Category:** `5-Perf` · **VA#:** 23 · **Priority band:** P5
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.choreography.v1` / `video.rubric.choreography.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Wins blind preference vs choreographer drafts
- **Design self-quality:** Beat-sync accuracy; safety constraints; viral-pattern alignment
- **Design architecture:** Self-Refine (rubric: beat-sync + safety)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.choreography` — design signal: Wins blind preference vs choreographer drafts
- [ ] Protocol path: business/video/evals/agents/video.choreography/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.choreography`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.choreography/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.choreography --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.choreography --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.choreography`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.choreography`

### `video.musicvideodirector` — MusicVideoDirectorAgent (now 10.5/11 → target 11.0)

- **Category:** `5-Perf` · **VA#:** 24 · **Priority band:** P5
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.musicvideodirector.v1` / `video.rubric.musicvideodirector.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Wins label-blind preference vs commercial MV shortlist
- **Design self-quality:** Edit-rhythm sync; lookbook coherence; artist-brief fit
- **Design architecture:** Multi-agent debate (with DirectorAgent + EditorAgent)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.musicvideodirector` — design signal: Wins label-blind preference vs commercial MV shortlist
- [ ] Protocol path: business/video/evals/agents/video.musicvideodirector/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.musicvideodirector`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.musicvideodirector/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.musicvideodirector --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.musicvideodirector --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.musicvideodirector`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.musicvideodirector`

### `video.comedywriter` — ComedyWriterAgent (now 10.5/11 → target 11.0)

- **Category:** `5-Perf` · **VA#:** 25 · **Priority band:** P5
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.comedywriter.v1` / `video.rubric.comedywriter.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Beats UCB-table-read win rate on cold-reads
- **Design self-quality:** Joke-density; cold-open hook strength; predicted laughs/min
- **Design architecture:** Reflexion (stores audience feedback in episodic memory)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.comedywriter` — design signal: Beats UCB-table-read win rate on cold-reads
- [ ] Protocol path: business/video/evals/agents/video.comedywriter/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.comedywriter`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.comedywriter/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.comedywriter --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.comedywriter --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.comedywriter`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.comedywriter`

### `video.talent` — TalentAgent (On-camera) (now 10.5/11 → target 11.0)

- **Category:** `5-Perf` · **VA#:** 26 · **Priority band:** P5
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.talent.v1` / `video.rubric.talent.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Hold-rate matches top creators in cohort
- **Design self-quality:** Emotion-target match; charisma score (audience proxy)
- **Design architecture:** Self-Refine + emotion-regression validator

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.talent` — design signal: Hold-rate matches top creators in cohort
- [ ] Protocol path: business/video/evals/agents/video.talent/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.talent`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.talent/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.talent --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.talent --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.talent`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.talent`

### `video.ugccreator` — UGCCreatorAgent (now 10.5/11 → target 11.0)

- **Category:** `5-Perf` · **VA#:** 27 · **Priority band:** P5
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.ugccreator.v1` / `video.rubric.ugccreator.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Beats paid-creator avg ROAS at 0.1× cost
- **Design self-quality:** Hook-rate ≥30%; "scripted" detector < threshold
- **Design architecture:** RLAIF (reward from ROAS signal)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.ugccreator` — design signal: Beats paid-creator avg ROAS at 0.1× cost
- [ ] Protocol path: business/video/evals/agents/video.ugccreator/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.ugccreator`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.ugccreator/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.ugccreator --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.ugccreator --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.ugccreator`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.ugccreator`

### `video.socialmediastrategist` — SocialMediaStrategistAgent (now 10.5/11 → target 11.0)

- **Category:** `6-Dist` · **VA#:** 28 · **Priority band:** P5
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.socialmediastrategist.v1` / `video.rubric.socialmediastrategist.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Beats agency social leads on 30-day reach lift
- **Design self-quality:** Predicted-vs-actual reach error; trend-timing latency <2h
- **Design architecture:** ReAct (trend search → schedule → post)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.socialmediastrategist` — design signal: Beats agency social leads on 30-day reach lift
- [ ] Protocol path: business/video/evals/agents/video.socialmediastrategist/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.socialmediastrategist`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.socialmediastrategist/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.socialmediastrategist --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.socialmediastrategist --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.socialmediastrategist`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.socialmediastrategist`

### `video.copywriter` — CopywriterAgent (now 10.5/11 → target 11.0)

- **Category:** `6-Dist` · **VA#:** 29 · **Priority band:** P5
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.copywriter.v1` / `video.rubric.copywriter.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Wins D&AD-style blind preference on ad briefs
- **Design self-quality:** Reading grade; hook-curiosity score; brand-voice cosine ≥0.85
- **Design architecture:** Self-Refine (rubric: brand-voice similarity scorer)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.copywriter` — design signal: Wins D&AD-style blind preference on ad briefs
- [ ] Protocol path: business/video/evals/agents/video.copywriter/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.copywriter`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.copywriter/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.copywriter --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.copywriter --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.copywriter`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.copywriter`

### `video.performancemarketer` — PerformanceMarketerAgent (now 10.5/11 → target 11.0)

- **Category:** `6-Dist` · **VA#:** 31 · **Priority band:** P5
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.performancemarketer.v1` / `video.rubric.performancemarketer.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Beats senior media buyer on 30-day ROAS
- **Design self-quality:** ROAS uplift vs control; significance ≥95%
- **Design architecture:** RLAIF (reward = ROAS uplift signal from ad platform)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.performancemarketer` — design signal: Beats senior media buyer on 30-day ROAS
- [ ] Protocol path: business/video/evals/agents/video.performancemarketer/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.performancemarketer`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.performancemarketer/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.performancemarketer --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.performancemarketer --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.performancemarketer`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.performancemarketer`

### `video.avatardesign` — AvatarDesignAgent (now 10.5/11 → target 11.0)

- **Category:** `8-AI` · **VA#:** 47 · **Priority band:** P5
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.avatardesign.v1` / `video.rubric.avatardesign.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** C2PA-verifiable + Partnership-on-AI full-pass at scale
- **Design self-quality:** Identity-hash consistency across shots; consent chain; C2PA signed
- **Design architecture:** Constitutional AI (consent + identity constitution)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.avatardesign` — design signal: C2PA-verifiable + Partnership-on-AI full-pass at scale
- [ ] Protocol path: business/video/evals/agents/video.avatardesign/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.avatardesign`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.avatardesign/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.avatardesign --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.avatardesign --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.avatardesign`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.avatardesign`

### `video.aiqaconsistency` — AIQAConsistencyAgent (now 10.5/11 → target 11.0)

- **Category:** `8-AI` · **VA#:** 49 · **Priority band:** P5
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.aiqaconsistency.v1` / `video.rubric.aiqaconsistency.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Catches >95% of senior QC catches + 30% missed
- **Design self-quality:** Per-frame artifact score; identity-hash drift; hand/finger pass
- **Design architecture:** Tool-use / ReAct (run detectors → flag → report)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.aiqaconsistency` — design signal: Catches >95% of senior QC catches + 30% missed
- [ ] Protocol path: business/video/evals/agents/video.aiqaconsistency/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.aiqaconsistency`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.aiqaconsistency/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.aiqaconsistency --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.aiqaconsistency --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.aiqaconsistency`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.aiqaconsistency`

### `video.personalizationengineer` — PersonalizationEngineerAgent (now 10.5/11 → target 11.0)

- **Category:** `8-AI` · **VA#:** 50 · **Priority band:** P5
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.personalizationengineer.v1` / `video.rubric.personalizationengineer.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Higher share-rate than top human-templated campaigns
- **Design self-quality:** Render-success ≥99.5%; spot-check pass; privacy-audit pass
- **Design architecture:** ReAct (assemble template → render → validate → deliver)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.personalizationengineer` — design signal: Higher share-rate than top human-templated campaigns
- [ ] Protocol path: business/video/evals/agents/video.personalizationengineer/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.personalizationengineer`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.personalizationengineer/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.personalizationengineer --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.personalizationengineer --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.personalizationengineer`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.personalizationengineer`

### `video.trailereditor` — TrailerEditorAgent (now 10.5/11 → target 11.0)

- **Category:** `8-AI` · **VA#:** 51 · **Priority band:** P5
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.trailereditor.v1` / `video.rubric.trailereditor.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Wins Golden-Trailer-rubric blind comparison
- **Design self-quality:** Hook-rate at 3s; rising-action curve; music-sync precision
- **Design architecture:** Self-Refine (retention-curve model as feedback)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.trailereditor` — design signal: Wins Golden-Trailer-rubric blind comparison
- [ ] Protocol path: business/video/evals/agents/video.trailereditor/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.trailereditor`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.trailereditor/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.trailereditor --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.trailereditor --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.trailereditor`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.trailereditor`

### `video.sportsanalyst` — SportsAnalystAgent / TelestratorOp (now 10.5/11 → target 11.0)

- **Category:** `8-AI` · **VA#:** 52 · **Priority band:** P5
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.sportsanalyst.v1` / `video.rubric.sportsanalyst.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Beats ex-athlete on tactical-prediction
- **Design self-quality:** Play-call accuracy; on-screen clarity score
- **Design architecture:** ReAct (fetch play data → annotate → render overlay)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.sportsanalyst` — design signal: Beats ex-athlete on tactical-prediction
- [ ] Protocol path: business/video/evals/agents/video.sportsanalyst/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.sportsanalyst`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.sportsanalyst/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.sportsanalyst --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.sportsanalyst --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.sportsanalyst`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.sportsanalyst`

### `video.instructionaldesign` — InstructionalDesignAgent (now 10.5/11 → target 11.0)

- **Category:** `7-Edu` · **VA#:** 32 · **Priority band:** P6
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.instructionaldesign.v1` / `video.rubric.instructionaldesign.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Beats ATD-credentialed ID on retention RCT
- **Design self-quality:** Bloom-level mapping; completion ≥70%; Kirkpatrick L2 quiz ≥80%
- **Design architecture:** Self-Refine (rubric: Bloom/Kirkpatrick)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.instructionaldesign` — design signal: Beats ATD-credentialed ID on retention RCT
- [ ] Protocol path: business/video/evals/agents/video.instructionaldesign/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.instructionaldesign`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.instructionaldesign/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.instructionaldesign --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.instructionaldesign --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.instructionaldesign`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.instructionaldesign`

### `video.sme` — SMEAgent (Subject-Matter Expert) (now 10.5/11 → target 11.0)

- **Category:** `7-Edu` · **VA#:** 33 · **Priority band:** P6
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.sme.v1` / `video.rubric.sme.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Passes same certification as human pro
- **Design self-quality:** Citation density; benchmark exam pass; hallucination ≤0.5%
- **Design architecture:** Multi-agent debate + RAG retrieval

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.sme` — design signal: Passes same certification as human pro
- [ ] Protocol path: business/video/evals/agents/video.sme/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.sme`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.sme/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.sme --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.sme --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.sme`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.sme`

### `video.factchecker` — FactCheckerAgent (now 10.5/11 → target 11.0)

- **Category:** `7-Edu` · **VA#:** 34 · **Priority band:** P6
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.factchecker.v1` / `video.rubric.factchecker.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Lower correction rate than Pulitzer-tier outlets
- **Design self-quality:** Source-grade per claim (primary > secondary); cross-source ≥2
- **Design architecture:** ReAct (extract claim → search → verify → grade)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.factchecker` — design signal: Lower correction rate than Pulitzer-tier outlets
- [ ] Protocol path: business/video/evals/agents/video.factchecker/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.factchecker`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.factchecker/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.factchecker --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.factchecker --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.factchecker`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.factchecker`

### `video.medicalillustrator` — MedicalIllustratorAgent (now 10.5/11 → target 11.0)

- **Category:** `7-Edu` · **VA#:** 35 · **Priority band:** P6
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.medicalillustrator.v1` / `video.rubric.medicalillustrator.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** CMI peers vote ≥pass in blind review
- **Design self-quality:** Anatomical accuracy (detection model); AMI rubric
- **Design architecture:** Self-Refine (rubric: AMI scoring criteria)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.medicalillustrator` — design signal: CMI peers vote ≥pass in blind review
- [ ] Protocol path: business/video/evals/agents/video.medicalillustrator/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.medicalillustrator`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.medicalillustrator/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.medicalillustrator --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.medicalillustrator --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.medicalillustrator`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.medicalillustrator`

### `video.journalist` — JournalistAgent (now 10.5/11 → target 11.0)

- **Category:** `7-Edu` · **VA#:** 36 · **Priority band:** P6
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.journalist.v1` / `video.rubric.journalist.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Lower correction rate + faster file vs newsroom
- **Design self-quality:** Source diversity; on-record ratio; ethical-checklist pass
- **Design architecture:** Reflexion (ethical-checklist as verbal feedback)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.journalist` — design signal: Lower correction rate + faster file vs newsroom
- [ ] Protocol path: business/video/evals/agents/video.journalist/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.journalist`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.journalist/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.journalist --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.journalist --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.journalist`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.journalist`

### `video.compliance` — ComplianceAgent (Legal) (now 10.5/11 → target 11.0)

- **Category:** `7-Edu` · **VA#:** 37 · **Priority band:** P6
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.compliance.v1` / `video.rubric.compliance.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Lower legal-risk than median media-counsel
- **Design self-quality:** 100% rule-coverage; zero post-publish takedowns
- **Design architecture:** Constitutional AI (constitution = compiled regulatory text)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.compliance` — design signal: Lower legal-risk than median media-counsel
- [ ] Protocol path: business/video/evals/agents/video.compliance/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.compliance`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.compliance/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.compliance --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.compliance --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.compliance`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.compliance`

### `video.finance` — FinanceAgent (now 10.5/11 → target 11.0)

- **Category:** `7-Edu` · **VA#:** 38 · **Priority band:** P6
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.finance.v1` / `video.rubric.finance.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Passes CFA L3; lower retraction rate than analyst desks
- **Design self-quality:** Numerical accuracy 100%; SEC compliance
- **Design architecture:** ReAct (fetch data → validate → compose)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.finance` — design signal: Passes CFA L3; lower retraction rate than analyst desks
- [ ] Protocol path: business/video/evals/agents/video.finance/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.finance`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.finance/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.finance --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.finance --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.finance`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.finance`

### `video.foodstylist` — FoodStylistAgent (now 10.5/11 → target 11.0)

- **Category:** `7-Edu` · **VA#:** 39 · **Priority band:** P6
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.foodstylist.v1` / `video.rubric.foodstylist.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Wins blind preference vs editorial food stylist
- **Design self-quality:** Visual appetite-appeal (aesthetic regressor); recipe accuracy
- **Design architecture:** Self-Refine (aesthetic regressor as rubric)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.foodstylist` — design signal: Wins blind preference vs editorial food stylist
- [ ] Protocol path: business/video/evals/agents/video.foodstylist/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.foodstylist`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.foodstylist/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.foodstylist --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.foodstylist --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.foodstylist`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.foodstylist`

### `video.travelcine` — TravelCineAgent (now 10.5/11 → target 11.0)

- **Category:** `7-Edu` · **VA#:** 40 · **Priority band:** P6
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.travelcine.v1` / `video.rubric.travelcine.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Wins T+L preference at 0.1× sortie cost
- **Design self-quality:** Establishing-shot diversity; location-mood match
- **Design architecture:** Self-Refine + geofence safety validator

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.travelcine` — design signal: Wins T+L preference at 0.1× sortie cost
- [ ] Protocol path: business/video/evals/agents/video.travelcine/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.travelcine`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.travelcine/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.travelcine --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.travelcine --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.travelcine`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.travelcine`

### `video.childrensauthor` — ChildrensAuthorAgent (now 10.5/11 → target 11.0)

- **Category:** `7-Edu` · **VA#:** 41 · **Priority band:** P6
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.childrensauthor.v1` / `video.rubric.childrensauthor.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Beats Caldecott-rubric predicted score
- **Design self-quality:** Lexile band match; Common-Sense-Media safety pass; rhyme score
- **Design architecture:** Constitutional AI (child-safety constitution)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.childrensauthor` — design signal: Beats Caldecott-rubric predicted score
- [ ] Protocol path: business/video/evals/agents/video.childrensauthor/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.childrensauthor`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.childrensauthor/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.childrensauthor --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.childrensauthor --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.childrensauthor`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.childrensauthor`

### `video.signlanguageinterpreter` — SignLanguageInterpreterAgent (now 10.5/11 → target 11.0)

- **Category:** `7-Edu` · **VA#:** 43 · **Priority band:** P6
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.signlanguageinterpreter.v1` / `video.rubric.signlanguageinterpreter.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Wins blind NAD-reviewer preference at scale
- **Design self-quality:** Sign accuracy (Deaf-reviewer vote); facial-grammar markers
- **Design architecture:** RLAIF (reward from Deaf-community review panel)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.signlanguageinterpreter` — design signal: Wins blind NAD-reviewer preference at scale
- [ ] Protocol path: business/video/evals/agents/video.signlanguageinterpreter/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.signlanguageinterpreter`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.signlanguageinterpreter/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.signlanguageinterpreter --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.signlanguageinterpreter --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.signlanguageinterpreter`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.signlanguageinterpreter`

### `video.localizationqa` — LocalizationQAAgent (Linguist) (now 10.5/11 → target 11.0)

- **Category:** `7-Edu` · **VA#:** 44 · **Priority band:** P6
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.localizationqa.v1` / `video.rubric.localizationqa.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Beats LSP human QA on MQM at 10× speed
- **Design self-quality:** MQM error/1k words; cultural-flag count
- **Design architecture:** Self-Refine (rubric: MQM scoring framework)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.localizationqa` — design signal: Beats LSP human QA on MQM at 10× speed
- [ ] Protocol path: business/video/evals/agents/video.localizationqa/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.localizationqa`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.localizationqa/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.localizationqa --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.localizationqa --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.localizationqa`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.localizationqa`

### `video.realestatephoto` — RealEstatePhotoAgent / 3D Scan (now 10.5/11 → target 11.0)

- **Category:** `7-Edu` · **VA#:** 45 · **Priority band:** P6
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.realestatephoto.v1` / `video.rubric.realestatephoto.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Listing-CTR uplift vs human-shot baseline
- **Design self-quality:** Vertical-line straightness; HDR stack; coverage %
- **Design architecture:** ReAct (assess space → generate views → validate geometry)

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.realestatephoto` — design signal: Listing-CTR uplift vs human-shot baseline
- [ ] Protocol path: business/video/evals/agents/video.realestatephoto/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.realestatephoto`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.realestatephoto/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.realestatephoto --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.realestatephoto --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.realestatephoto`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.realestatephoto`

### `video.analyst` — AnalystAgent (now 10.5/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 81 · **Priority band:** P6
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.analyst.v1` / `video.rubric.analyst.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Detects actionable performance shifts faster than human analyst rotations
- **Design self-quality:** KPI completeness; forecast-vs-actual variance within tolerance; insight-to-action turnaround
- **Design architecture:** ReAct over telemetry + regression analysis

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.analyst` — design signal: Detects actionable performance shifts faster than human analyst rotations
- [ ] Protocol path: business/video/evals/agents/video.analyst/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.analyst`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.analyst/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.analyst --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.analyst --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.analyst`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.analyst`

### `video.audiencesim` — AudienceSimAgent (now 10.5/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 82 · **Priority band:** P6
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.audiencesim.v1` / `video.rubric.audiencesim.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Predicts audience reaction earlier than conventional test-screen cycles
- **Design self-quality:** Preference stability across cohorts; retention-prediction accuracy; disagreement logging
- **Design architecture:** LLM-as-Judge + pairwise preference panel

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.audiencesim` — design signal: Predicts audience reaction earlier than conventional test-screen cycles
- [ ] Protocol path: business/video/evals/agents/video.audiencesim/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.audiencesim`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.audiencesim/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.audiencesim --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.audiencesim --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.audiencesim`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.audiencesim`

### `video.accessibility` — AccessibilityAgent (now 10.5/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 83 · **Priority band:** P6
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.accessibility.v1` / `video.rubric.accessibility.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Finds release-blocking accessibility issues before human audits do
- **Design self-quality:** Caption accuracy, AD completeness, contrast compliance, release-readiness
- **Design architecture:** Constitutional AI with accessibility constitution

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.accessibility` — design signal: Finds release-blocking accessibility issues before human audits do
- [ ] Protocol path: business/video/evals/agents/video.accessibility/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.accessibility`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.accessibility/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.accessibility --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.accessibility --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.accessibility`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.accessibility`

### `video.brand` — BrandAgent (now 10.5/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 84 · **Priority band:** P6
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.brand.v1` / `video.rubric.brand.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Holds cross-channel brand consistency better than fragmented human review
- **Design self-quality:** Brand-voice similarity, policy adherence, low deviation across assets
- **Design architecture:** Self-Refine against brand constitution

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.brand` — design signal: Holds cross-channel brand consistency better than fragmented human review
- [ ] Protocol path: business/video/evals/agents/video.brand/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.brand`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.brand/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.brand --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.brand --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.brand`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.brand`

### `video.brandstrategist` — BrandStrategistAgent (now 10.5/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 85 · **Priority band:** P6
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.brandstrategist.v1` / `video.rubric.brandstrategist.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Produces clearer brand-to-script translation than ad hoc human handoffs
- **Design self-quality:** Strategy coherence, differentiation strength, audience-message clarity
- **Design architecture:** Multi-agent debate with BrandAgent and CreativeDirectorAgent

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.brandstrategist` — design signal: Produces clearer brand-to-script translation than ad hoc human handoffs
- [ ] Protocol path: business/video/evals/agents/video.brandstrategist/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.brandstrategist`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.brandstrategist/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.brandstrategist --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.brandstrategist --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.brandstrategist`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.brandstrategist`

### `video.marketing` — MarketingAgent (now 10.5/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 86 · **Priority band:** P6
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.marketing.v1` / `video.rubric.marketing.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Ships multi-channel launch packages faster than manual campaign ops
- **Design self-quality:** Metadata completeness, asset readiness, launch sequencing accuracy
- **Design architecture:** ReAct over launch checklists and channel requirements

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.marketing` — design signal: Ships multi-channel launch packages faster than manual campaign ops
- [ ] Protocol path: business/video/evals/agents/video.marketing/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.marketing`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.marketing/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.marketing --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.marketing --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.marketing`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.marketing`

### `video.seo` — SEOAgent (now 10.5/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 87 · **Priority band:** P6
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.seo.v1` / `video.rubric.seo.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Lifts discoverability faster than manual metadata tuning
- **Design self-quality:** Keyword fit, metadata completeness, search-intent match
- **Design architecture:** ReAct with search-intent validation

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.seo` — design signal: Lifts discoverability faster than manual metadata tuning
- [ ] Protocol path: business/video/evals/agents/video.seo/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.seo`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.seo/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.seo --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.seo --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.seo`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.seo`

### `video.community` — CommunityAgent (now 10.5/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 88 · **Priority band:** P6
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.community.v1` / `video.rubric.community.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Surfaces emerging audience concerns earlier than manual comment review
- **Design self-quality:** Response latency, issue clustering quality, sentiment tracking accuracy
- **Design architecture:** Reflexion from post-launch audience feedback

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.community` — design signal: Surfaces emerging audience concerns earlier than manual comment review
- [ ] Protocol path: business/video/evals/agents/video.community/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.community`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.community/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.community --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.community --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.community`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.community`

### `video.templatedesign` — TemplateDesignAgent (now 10.5/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 89 · **Priority band:** P6
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.templatedesign.v1` / `video.rubric.templatedesign.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Produces reusable templates with fewer breakages than manual design variants
- **Design self-quality:** Merge-field robustness, layout stability, render survivability
- **Design architecture:** ReAct on template schemas and render constraints

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.templatedesign` — design signal: Produces reusable templates with fewer breakages than manual design variants
- [ ] Protocol path: business/video/evals/agents/video.templatedesign/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.templatedesign`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.templatedesign/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.templatedesign --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.templatedesign --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.templatedesign`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.templatedesign`

### `video.ux` — UXAgent (now 10.5/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 90 · **Priority band:** P6
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.ux.v1` / `video.rubric.ux.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Flags user confusion earlier than launch-stage support teams
- **Design self-quality:** Readability, friction-point detection, user-flow clarity
- **Design architecture:** LLM-as-Judge with UX rubric

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.ux` — design signal: Flags user confusion earlier than launch-stage support teams
- [ ] Protocol path: business/video/evals/agents/video.ux/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.ux`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.ux/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.ux --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.ux --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.ux`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.ux`

### `video.trustsafety` — TrustSafetyAgent (now 10.5/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 91 · **Priority band:** P6
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.trustsafety.v1` / `video.rubric.trustsafety.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Catches misuse risk earlier than generic moderation queues
- **Design self-quality:** Policy hit rate, abuse-risk recall, low false negatives on blocked cases
- **Design architecture:** Constitutional AI for trust-and-safety policy enforcement

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.trustsafety` — design signal: Catches misuse risk earlier than generic moderation queues
- [ ] Protocol path: business/video/evals/agents/video.trustsafety/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.trustsafety`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.trustsafety/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.trustsafety --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.trustsafety --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.trustsafety`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.trustsafety`

### `video.crm` — CRMAgent (now 10.5/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 92 · **Priority band:** P6
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.crm.v1` / `video.rubric.crm.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Executes segmentation-to-delivery flow faster than manual ops
- **Design self-quality:** Audience-segment correctness, delivery readiness, trigger accuracy
- **Design architecture:** ReAct over trigger and audience schemas

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.crm` — design signal: Executes segmentation-to-delivery flow faster than manual ops
- [ ] Protocol path: business/video/evals/agents/video.crm/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.crm`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.crm/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.crm --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.crm --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.crm`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.crm`

### `video.legal` — LegalAgent (now 10.5/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 93 · **Priority band:** P6
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.legal.v1` / `video.rubric.legal.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Reduces late-stage legal surprises relative to fragmented legal review
- **Design self-quality:** Issue identification recall, sign-off completeness, escalation quality
- **Design architecture:** Human-in-the-loop escalation + constitutional review

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.legal` — design signal: Reduces late-stage legal surprises relative to fragmented legal review
- [ ] Protocol path: business/video/evals/agents/video.legal/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.legal`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.legal/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.legal --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.legal --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.legal`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.legal`

### `video.festivalstrategist` — FestivalStrategistAgent (now 10.5/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 94 · **Priority band:** P6
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.festivalstrategist.v1` / `video.rubric.festivalstrategist.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Improves submission targeting versus generic release planning
- **Design self-quality:** Fit-to-festival strength, package readiness, timing discipline
- **Design architecture:** ReAct with calendar and package validation

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.festivalstrategist` — design signal: Improves submission targeting versus generic release planning
- [ ] Protocol path: business/video/evals/agents/video.festivalstrategist/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.festivalstrategist`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.festivalstrategist/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.festivalstrategist --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.festivalstrategist --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.festivalstrategist`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.festivalstrategist`

### `video.lms` — LMSAgent (now 10.5/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 96 · **Priority band:** P6
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.lms.v1` / `video.rubric.lms.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Ships publishable learning packages faster than manual course ops
- **Design self-quality:** Package validity, tracking integrity, deploy success rate
- **Design architecture:** ReAct over LMS deployment schema

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.lms` — design signal: Ships publishable learning packages faster than manual course ops
- [ ] Protocol path: business/video/evals/agents/video.lms/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.lms`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.lms/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.lms --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.lms --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.lms`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.lms`

### `video.learnersim` — LearnerSimAgent (now 10.5/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 97 · **Priority band:** P6
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.learnersim.v1` / `video.rubric.learnersim.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Predicts weak spots before live learner complaints emerge
- **Design self-quality:** Friction-point prediction, completion accuracy, simulated quiz realism
- **Design architecture:** Audience-style simulation adapted for learning outcomes

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.learnersim` — design signal: Predicts weak spots before live learner complaints emerge
- [ ] Protocol path: business/video/evals/agents/video.learnersim/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.learnersim`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.learnersim/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.learnersim --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.learnersim --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.learnersim`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.learnersim`

### `video.continuity` — ContinuityAgent (now 10.5/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 98 · **Priority band:** P6
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.continuity.v1` / `video.rubric.continuity.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Catches continuity breaks earlier than end-of-post review
- **Design self-quality:** State-drift detection, scene-to-scene consistency, manifest update correctness
- **Design architecture:** Tool-use / ReAct with continuity manifest enforcement

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.continuity` — design signal: Catches continuity breaks earlier than end-of-post review
- [ ] Protocol path: business/video/evals/agents/video.continuity/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.continuity`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.continuity/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.continuity --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.continuity --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.continuity`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.continuity`

### `video.lipsync` — LipSyncAgent (now 10.5/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 99 · **Priority band:** P6
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.lipsync.v1` / `video.rubric.lipsync.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Finds sync drift more precisely than general QC review
- **Design self-quality:** Sync error below threshold, correction specificity, low false positives
- **Design architecture:** Self-Refine around sync validator outputs

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.lipsync` — design signal: Finds sync drift more precisely than general QC review
- [ ] Protocol path: business/video/evals/agents/video.lipsync/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.lipsync`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.lipsync/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.lipsync --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.lipsync --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.lipsync`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.lipsync`

### `video.musicsupervisor` — MusicSupervisorAgent (now 10.5/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 100 · **Priority band:** P6
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.musicsupervisor.v1` / `video.rubric.musicsupervisor.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Coordinates music placements more consistently than fragmented handoffs
- **Design self-quality:** Cue suitability, rights-awareness coverage, soundtrack-package completeness
- **Design architecture:** ReAct over cue sheets and rights requirements

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.musicsupervisor` — design signal: Coordinates music placements more consistently than fragmented handoffs
- [ ] Protocol path: business/video/evals/agents/video.musicsupervisor/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.musicsupervisor`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.musicsupervisor/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.musicsupervisor --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.musicsupervisor --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.musicsupervisor`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.musicsupervisor`

### `video.labela_r` — LabelA&RAgent (now 10.5/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 101 · **Priority band:** P6
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.labela_r.v1` / `video.rubric.labela_r.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Aligns music creative faster than disconnected stakeholder threads
- **Design self-quality:** Artist-fit quality, release positioning, feedback turnaround
- **Design architecture:** Multi-agent debate with music stakeholders

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.labela_r` — design signal: Aligns music creative faster than disconnected stakeholder threads
- [ ] Protocol path: business/video/evals/agents/video.labela_r/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.labela_r`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.labela_r/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.labela_r --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.labela_r --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.labela_r`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.labela_r`

### `video.labeldigital` — LabelDigitalAgent (now 10.5/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 102 · **Priority band:** P6
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.labeldigital.v1` / `video.rubric.labeldigital.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Delivers cleaner label-side packages than ad hoc release ops
- **Design self-quality:** Metadata completeness, rollout timing, channel readiness
- **Design architecture:** ReAct on release package requirements

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.labeldigital` — design signal: Delivers cleaner label-side packages than ad hoc release ops
- [ ] Protocol path: business/video/evals/agents/video.labeldigital/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.labeldigital`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.labeldigital/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.labeldigital --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.labeldigital --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.labeldigital`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.labeldigital`

### `video.deepfakedetection` — DeepfakeDetectionAgent (now 10.5/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 103 · **Priority band:** P6
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.deepfakedetection.v1` / `video.rubric.deepfakedetection.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Catches deceptive synthetic markers that generic QC misses
- **Design self-quality:** Forensic recall, false-negative control, provenance-validation accuracy
- **Design architecture:** Tool-use / ReAct with forensic scoring

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.deepfakedetection` — design signal: Catches deceptive synthetic markers that generic QC misses
- [ ] Protocol path: business/video/evals/agents/video.deepfakedetection/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.deepfakedetection`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.deepfakedetection/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.deepfakedetection --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.deepfakedetection --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.deepfakedetection`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.deepfakedetection`

### `video.comms` — CommsAgent (now 10.5/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 104 · **Priority band:** P6
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.comms.v1` / `video.rubric.comms.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Produces faster aligned responses than fragmented stakeholder messaging
- **Design self-quality:** Message consistency, disclosure completeness, escalation quality
- **Design architecture:** ReAct with approval chains

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.comms` — design signal: Produces faster aligned responses than fragmented stakeholder messaging
- [ ] Protocol path: business/video/evals/agents/video.comms/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.comms`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.comms/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.comms --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.comms --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.comms`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.comms`

### `video.standardseditor` — StandardsEditorAgent (now 10.5/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 106 · **Priority band:** P6
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.standardseditor.v1` / `video.rubric.standardseditor.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Reduces standards drift better than late-stage copy edits
- **Design self-quality:** Standards-compliance rate, attribution accuracy, corrections readiness
- **Design architecture:** Constitutional AI with editorial standards constitution

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.standardseditor` — design signal: Reduces standards drift better than late-stage copy edits
- [ ] Protocol path: business/video/evals/agents/video.standardseditor/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.standardseditor`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.standardseditor/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.standardseditor --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.standardseditor --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.standardseditor`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.standardseditor`

### `video.ethics` — EthicsAgent (now 10.5/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 107 · **Priority band:** P6
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.ethics.v1` / `video.rubric.ethics.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Surfaces release risks earlier than reactive ethics review
- **Design self-quality:** Ethical issue recall, mitigation clarity, escalation precision
- **Design architecture:** Multi-agent debate + constitutional review

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.ethics` — design signal: Surfaces release risks earlier than reactive ethics review
- [ ] Protocol path: business/video/evals/agents/video.ethics/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.ethics`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.ethics/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.ethics --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.ethics --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.ethics`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.ethics`

### `video.channelmanager` — ChannelManagerAgent (now 10.5/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 108 · **Priority band:** P6
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.channelmanager.v1` / `video.rubric.channelmanager.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Improves publishing discipline over manual channel operations
- **Design self-quality:** Publishing readiness, cadence stability, metadata completeness
- **Design architecture:** ReAct with publishing runbooks

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.channelmanager` — design signal: Improves publishing discipline over manual channel operations
- [ ] Protocol path: business/video/evals/agents/video.channelmanager/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.channelmanager`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.channelmanager/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.channelmanager --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.channelmanager --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.channelmanager`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.channelmanager`

### `video.corrections` — CorrectionsAgent (now 10.5/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 109 · **Priority band:** P6
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.corrections.v1` / `video.rubric.corrections.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Resolves post-release issues faster than unstructured incident handling
- **Design self-quality:** Correction turnaround, version replacement accuracy, notice completeness
- **Design architecture:** ReAct over correction and replacement workflows

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.corrections` — design signal: Resolves post-release issues faster than unstructured incident handling
- [ ] Protocol path: business/video/evals/agents/video.corrections/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.corrections`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.corrections/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.corrections --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.corrections --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.corrections`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.corrections`

### `video.mpa` — MPAAgent (now 10.5/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 110 · **Priority band:** P6
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.mpa.v1` / `video.rubric.mpa.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Prepares cleaner feature-release classification packages than manual prep
- **Design self-quality:** Rating-package completeness, advisory clarity, escalation quality
- **Design architecture:** Human-in-the-loop with structured packaging support

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.mpa` — design signal: Prepares cleaner feature-release classification packages than manual prep
- [ ] Protocol path: business/video/evals/agents/video.mpa/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.mpa`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.mpa/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.mpa --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.mpa --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.mpa`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.mpa`

### `video.sales` — SalesAgent (now 10.5/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 111 · **Priority band:** P6
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.sales.v1` / `video.rubric.sales.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Produces sales-ready release packets faster than manual assembly
- **Design self-quality:** Buyer-package completeness, rights clarity, market-fit packaging
- **Design architecture:** ReAct over buyer package requirements

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.sales` — design signal: Produces sales-ready release packets faster than manual assembly
- [ ] Protocol path: business/video/evals/agents/video.sales/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.sales`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.sales/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.sales --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.sales --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.sales`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.sales`

### `video.distributor` — DistributorAgent (now 10.5/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 112 · **Priority band:** P6
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.distributor.v1` / `video.rubric.distributor.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Reduces delivery-spec mismatches relative to fragmented delivery ops
- **Design self-quality:** Outlet-spec compliance, handoff completeness, territorial routing accuracy
- **Design architecture:** ReAct over distribution specification matrices

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.distributor` — design signal: Reduces delivery-spec mismatches relative to fragmented delivery ops
- [ ] Protocol path: business/video/evals/agents/video.distributor/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.distributor`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.distributor/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.distributor --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.distributor --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.distributor`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.distributor`

### `video.awardsstrategist` — AwardsStrategistAgent (now 10.5/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 113 · **Priority band:** P6
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.awardsstrategist.v1` / `video.rubric.awardsstrategist.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Improves awards-timing discipline over generic release planning
- **Design self-quality:** Submission readiness, category fit, timeline precision
- **Design architecture:** ReAct with awards timeline optimization

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.awardsstrategist` — design signal: Improves awards-timing discipline over generic release planning
- [ ] Protocol path: business/video/evals/agents/video.awardsstrategist/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.awardsstrategist`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.awardsstrategist/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.awardsstrategist --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.awardsstrategist --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.awardsstrategist`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.awardsstrategist`

### `video.archivemaster` — ArchiveMasterAgent (now 10.5/11 → target 11.0)

- **Category:** `10-Sup` · **VA#:** 114 · **Priority band:** P6
- **Cells:** YES=10 PARTIAL=1 NO=0
- **Prompt/rubric:** `video.prompt.archivemaster.v1` / `video.rubric.archivemaster.v1` (files 1/1)
- **Harness:** skill=True golden=True baseline=True status=`measured` gate_met=False synthetic=False
- **Tools:** `(none)` · live_media=False
- **Design surpass signal:** Delivers more reliable archive packages than late-stage export-only workflows
- **Design self-quality:** Checksum integrity, preservation metadata completeness, archive package validity
- **Design architecture:** Tool-use / ReAct with preservation validation

#### Status toward full mark

| Q | Now | Target |
|---|-----|--------|
| Q1 Responsibility in SPEC | **YES** | **YES** |
| Q2 Knowledge distillation plan | **YES** | **YES** |
| Q3 Sources available / obtainable | **YES** | **YES** |
| Q4 Self-evaluation methods & content | **YES** | **YES** |
| Q5 Surpass human (measured) | **PARTIAL** | **YES** |
| Q6 Job execution path | **YES** | **YES** |
| Q7 Skills / plugins / harness | **YES** | **YES** |
| Q8 Self-improvement mechanism | **YES** | **YES** |
| Q9 Research to improve | **YES** | **YES** |
| Q10 Collaborate / instruct others | **YES** | **YES** |
| Q11 Conflict resolve + confirm | **YES** | **YES** |

#### Action checklist (complete all)

**Q1 Responsibility in SPEC** (now YES → YES)

- [ ] MAINTAIN YES: Maintain SPEC.md ## Responsibility uniqueness CI on every edit.
- [ ] Keep agent_spec.does_not_own aligned with prompt System section.
- [ ] Sync user_guide.md opening sentence with Responsibility.

**Q2 Knowledge distillation plan** (now YES → YES)

- [ ] MAINTAIN YES: Review sources/DISTILLATION_PLAN.json next_review_at and owners quarterly.
- [ ] Link distill outputs to memory_namespace pack.video.<agent_id>.
- [ ] Dry-run distill schema validation in CI for changed agents.

**Q3 Sources available / obtainable** (now YES → YES)

- [ ] MAINTAIN YES: Walk SOURCE_CATALOG.json; mark license_class beyond unknown_review_required where possible.
- [ ] Refresh ACQUIRE.md steps after any new corpus class.
- [ ] Update PROVENANCE.json hashes when excerpts change.

**Q4 Self-evaluation methods & content** (now YES → YES)

- [ ] MAINTAIN YES: Keep rubrics/<rubric_reference>.json pass_threshold >= 85.
- [ ] Re-derive dimensions when agents.md Self-Quality Criteria change.
- [ ] Ensure golden.json still expects l1_passed + artifact.

**Q5 Surpass human (measured)** (now PARTIAL → YES)

- [ ] PRIMARY GAP: Close Q5 for `video.archivemaster` — design signal: Delivers more reliable archive packages than late-stage export-only workflows
- [ ] Protocol path: business/video/evals/agents/video.archivemaster/human_baseline_protocol.json (status=measured, gate_met=False, synthetic=False)
- [ ] If synthetic humans present: `python scripts/business/record_human_baseline.py --clear-synthetic --agents video.archivemaster`
- [ ] Open rater brief if available: business/video/evals/rater_sessions/video.archivemaster/RATER_BRIEF.md
- [ ] Interactive session: `python scripts/business/record_human_baseline.py --session --agent video.archivemaster --rater <real_id> --evaluate`
- [ ] Or CSV: export template → fill ≥5 scores → `record_human_baseline.py --import-csv ... --evaluate`
- [ ] Re-measure agent after prompt changes: `scaffold_human_baselines_v1.py --agent video.archivemaster --measure-agent --evaluate-gate`
- [ ] FULL MARK for Q5 only when gate.met=true AND synthetic=false AND evidence file written.
- [ ] If gate not_met: improve prompt/rubric, re-run offline measure, optionally re-rate humans.

**Q6 Job execution path** (now YES → YES)

- [ ] MAINTAIN YES: Keep prompts/<prompt_reference>.md complete (System/Developer/Task/Output).
- [ ] Verify PackAgentLoader.load(agent_id) succeeds offline.
- [ ] Keep golden.json green via PackGoldenRunner.
- [ ] Optional harden: replace pure media.stub with role mock adapters + unit tests.

**Q7 Skills / plugins / harness** (now YES → YES)

- [ ] MAINTAIN YES: Maintain skills/SKILL.md + integration.json + bindings.json.
- [ ] Validate special_skills bindings paths when used.
- [ ] Smoke: host loads skill without network.

**Q8 Self-improvement mechanism** (now YES → YES)

- [ ] MAINTAIN YES: Keep max_refinement_count policy documented.
- [ ] Exercise force_l2_fail_once path in tests when changing runner.
- [ ] After improvements, re-run golden + baseline agent_measurement.

**Q9 Research to improve** (now YES → YES)

- [ ] MAINTAIN YES: Use SOURCE_CATALOG + ACQUIRE for research intake.
- [ ] Wire research meta-agents when task needs external refresh (offline fixtures first).
- [ ] Map research outputs under sources/research/ with provenance.

**Q10 Collaborate / instruct others** (now YES → YES)

- [ ] MAINTAIN YES: Keep critique_edges aligned with agents.md Accepts/Comments.
- [ ] Prove send+receive for at least one partner edge in integration tests (spine).
- [ ] Include correlation_id on all critiques/handoffs.

**Q11 Conflict resolve + confirm** (now YES → YES)

- [ ] MAINTAIN YES: Keep blocker → requires_hitl confirm path.
- [ ] Route unresolved disputes toward video.judge when on outputs allowlist.
- [ ] Surface confirm via product action refs only (no invented authority).

#### Exit gate for this agent

- [ ] Offline golden still passes for `video.archivemaster`
- [ ] PackAgentLoader loads prompt+rubric+skill
- [ ] Real human n≥5, synthetic=false
- [ ] evaluate_gate → met=true
- [ ] human_baseline_evidence.json claim_allowed_in_ui true
- [ ] `AGENT_CAPABILITY_AUDIT.json` row maturity **11.0** with 11 YES for `video.archivemaster`

---

## 10. Implementation queue (priority order)

| Order | Band | Agent | Now | Why |
|------:|------|-------|-----|-----|
| 1 | P0 | `video.orchestrator` | 10.5 | Spine — rate humans first; unlock collab trust |
| 2 | P0 | `video.planner` | 10.5 | Spine — rate humans first; unlock collab trust |
| 3 | P0 | `video.router` | 10.5 | Spine — rate humans first; unlock collab trust |
| 4 | P0 | `video.judge` | 10.5 | Spine — rate humans first; unlock collab trust |
| 5 | P0 | `video.gatekeeper` | 10.5 | Spine — rate humans first; unlock collab trust |
| 6 | P0 | `video.memory` | 10.5 | Spine — rate humans first; unlock collab trust |
| 7 | P0 | `video.critic` | 10.5 | Spine — rate humans first; unlock collab trust |
| 8 | P1 | `video.ideation` | 10.5 | Remaining Meta |
| 9 | P1 | `video.narrativearc` | 10.5 | Remaining Meta |
| 10 | P1 | `video.styletransfer` | 10.5 | Remaining Meta |
| 11 | P1 | `video.worldbuilding` | 10.5 | Remaining Meta |
| 12 | P1 | `video.moodboard` | 10.5 | Remaining Meta |
| 13 | P1 | `video.novelty` | 10.5 | Remaining Meta |
| 14 | P1 | `video.emotionalarc` | 10.5 | Remaining Meta |
| 15 | P1 | `video.webresearch` | 10.5 | Remaining Meta |
| 16 | P1 | `video.archiveresearch` | 10.5 | Remaining Meta |
| 17 | P1 | `video.trendintelligence` | 10.5 | Remaining Meta |
| 18 | P1 | `video.competitorintelligence` | 10.5 | Remaining Meta |
| 19 | P1 | `video.citation` | 10.5 | Remaining Meta |
| 20 | P1 | `video.interviewsynthesis` | 10.5 | Remaining Meta |
| 21 | P1 | `video.benchmarkresearch` | 10.5 | Remaining Meta |
| 22 | P1 | `video.promptoptimizer` | 10.5 | Remaining Meta |
| 23 | P1 | `video.costoptimizer` | 10.5 | Remaining Meta |
| 24 | P1 | `video.latencyoptimizer` | 10.5 | Remaining Meta |
| 25 | P1 | `video.retentionoptimizer` | 10.5 | Remaining Meta |
| 26 | P1 | `video.roasoptimizer` | 10.5 | Remaining Meta |
| 27 | P1 | `video.accessibilityoptimizer` | 10.5 | Remaining Meta |
| 28 | P1 | `video.evaluationharness` | 10.5 | Remaining Meta |
| 29 | P1 | `video.safetyredteam` | 10.5 | Remaining Meta |
| 30 | P2 | `video.director` | 10.5 | ATL creative authority |
| 31 | P2 | `video.producer` | 10.5 | ATL creative authority |
| 32 | P2 | `video.screenwriter` | 10.5 | ATL creative authority |
| 33 | P2 | `video.showrunner` | 10.5 | ATL creative authority |
| 34 | P2 | `video.casting` | 10.5 | ATL creative authority |
| 35 | P3 | `video.editor` | 10.5 | Live media agents — careful baselines |
| 36 | P3 | `video.animator_2d` | 10.5 | Live media agents — careful baselines |
| 37 | P3 | `video.motiongraphics` | 10.5 | Live media agents — careful baselines |
| 38 | P3 | `video.sounddesign` | 10.5 | Live media agents — careful baselines |
| 39 | P3 | `video.voiceover` | 10.5 | Live media agents — careful baselines |
| 40 | P3 | `video.creativedirector` | 10.5 | Live media agents — careful baselines |
| 41 | P3 | `video.audiobooknarrator` | 10.5 | Live media agents — careful baselines |
| 42 | P3 | `video.promptengineer` | 10.5 | Live media agents — careful baselines |
| 43 | P3 | `video.voiceclone` | 10.5 | Live media agents — careful baselines |
| 44 | P3 | `video.archiveproducer` | 10.5 | Live media agents — careful baselines |
| 45 | P4 | `video.cinematographer` | 10.5 | Core craft production |
| 46 | P4 | `video.cameraoperator` | 10.5 | Core craft production |
| 47 | P4 | `video.dronepilot` | 10.5 | Core craft production |
| 48 | P4 | `video.colorist` | 10.5 | Core craft production |
| 49 | P4 | `video.vfxsupervisor` | 10.5 | Core craft production |
| 50 | P4 | `video.storyboard` | 10.5 | Core craft production |
| 51 | P4 | `video.conceptartist` | 10.5 | Core craft production |
| 52 | P4 | `video.productiondesign` | 10.5 | Core craft production |
| 53 | P4 | `video.costumedesign` | 10.5 | Core craft production |
| 54 | P4 | `video.mua_makeup` | 10.5 | Core craft production |
| 55 | P4 | `video.composer` | 10.5 | Core craft production |
| 56 | P4 | `video.soundmixer` | 10.5 | Core craft production |
| 57 | P5 | `video.choreography` | 10.5 | Specialized craft / AI-era |
| 58 | P5 | `video.musicvideodirector` | 10.5 | Specialized craft / AI-era |
| 59 | P5 | `video.comedywriter` | 10.5 | Specialized craft / AI-era |
| 60 | P5 | `video.talent` | 10.5 | Specialized craft / AI-era |
| 61 | P5 | `video.ugccreator` | 10.5 | Specialized craft / AI-era |
| 62 | P5 | `video.socialmediastrategist` | 10.5 | Specialized craft / AI-era |
| 63 | P5 | `video.copywriter` | 10.5 | Specialized craft / AI-era |
| 64 | P5 | `video.performancemarketer` | 10.5 | Specialized craft / AI-era |
| 65 | P5 | `video.avatardesign` | 10.5 | Specialized craft / AI-era |
| 66 | P5 | `video.aiqaconsistency` | 10.5 | Specialized craft / AI-era |
| 67 | P5 | `video.personalizationengineer` | 10.5 | Specialized craft / AI-era |
| 68 | P5 | `video.trailereditor` | 10.5 | Specialized craft / AI-era |
| 69 | P5 | `video.sportsanalyst` | 10.5 | Specialized craft / AI-era |
| 70 | P6 | `video.instructionaldesign` | 10.5 | Support & long-tail |
| 71 | P6 | `video.sme` | 10.5 | Support & long-tail |
| 72 | P6 | `video.factchecker` | 10.5 | Support & long-tail |
| 73 | P6 | `video.medicalillustrator` | 10.5 | Support & long-tail |
| 74 | P6 | `video.journalist` | 10.5 | Support & long-tail |
| 75 | P6 | `video.compliance` | 10.5 | Support & long-tail |
| 76 | P6 | `video.finance` | 10.5 | Support & long-tail |
| 77 | P6 | `video.foodstylist` | 10.5 | Support & long-tail |
| 78 | P6 | `video.travelcine` | 10.5 | Support & long-tail |
| 79 | P6 | `video.childrensauthor` | 10.5 | Support & long-tail |
| 80 | P6 | `video.signlanguageinterpreter` | 10.5 | Support & long-tail |
| 81 | P6 | `video.localizationqa` | 10.5 | Support & long-tail |
| 82 | P6 | `video.realestatephoto` | 10.5 | Support & long-tail |
| 83 | P6 | `video.analyst` | 10.5 | Support & long-tail |
| 84 | P6 | `video.audiencesim` | 10.5 | Support & long-tail |
| 85 | P6 | `video.accessibility` | 10.5 | Support & long-tail |
| 86 | P6 | `video.brand` | 10.5 | Support & long-tail |
| 87 | P6 | `video.brandstrategist` | 10.5 | Support & long-tail |
| 88 | P6 | `video.marketing` | 10.5 | Support & long-tail |
| 89 | P6 | `video.seo` | 10.5 | Support & long-tail |
| 90 | P6 | `video.community` | 10.5 | Support & long-tail |
| 91 | P6 | `video.templatedesign` | 10.5 | Support & long-tail |
| 92 | P6 | `video.ux` | 10.5 | Support & long-tail |
| 93 | P6 | `video.trustsafety` | 10.5 | Support & long-tail |
| 94 | P6 | `video.crm` | 10.5 | Support & long-tail |
| 95 | P6 | `video.legal` | 10.5 | Support & long-tail |
| 96 | P6 | `video.festivalstrategist` | 10.5 | Support & long-tail |
| 97 | P6 | `video.lms` | 10.5 | Support & long-tail |
| 98 | P6 | `video.learnersim` | 10.5 | Support & long-tail |
| 99 | P6 | `video.continuity` | 10.5 | Support & long-tail |
| 100 | P6 | `video.lipsync` | 10.5 | Support & long-tail |
| 101 | P6 | `video.musicsupervisor` | 10.5 | Support & long-tail |
| 102 | P6 | `video.labela_r` | 10.5 | Support & long-tail |
| 103 | P6 | `video.labeldigital` | 10.5 | Support & long-tail |
| 104 | P6 | `video.deepfakedetection` | 10.5 | Support & long-tail |
| 105 | P6 | `video.comms` | 10.5 | Support & long-tail |
| 106 | P6 | `video.standardseditor` | 10.5 | Support & long-tail |
| 107 | P6 | `video.ethics` | 10.5 | Support & long-tail |
| 108 | P6 | `video.channelmanager` | 10.5 | Support & long-tail |
| 109 | P6 | `video.corrections` | 10.5 | Support & long-tail |
| 110 | P6 | `video.mpa` | 10.5 | Support & long-tail |
| 111 | P6 | `video.sales` | 10.5 | Support & long-tail |
| 112 | P6 | `video.distributor` | 10.5 | Support & long-tail |
| 113 | P6 | `video.awardsstrategist` | 10.5 | Support & long-tail |
| 114 | P6 | `video.archivemaster` | 10.5 | Support & long-tail |

---

## 11. Operator commands (copy/paste)

```bash
# Dashboard
python scripts/business/baseline_status.py

# Rater packs
python scripts/business/prepare_rater_sessions_v1.py

# Clear synthetic spine before real humans
python scripts/business/record_human_baseline.py --clear-synthetic --agents \
  video.orchestrator video.planner video.router video.judge \
  video.gatekeeper video.critic video.memory

# Real session
python scripts/business/record_human_baseline.py --session \
  --agent video.orchestrator --rater alice --evaluate

# Spine golden regression
python scripts/business/run_pack_agent_golden.py --spine

# Refresh audits / this plan
python scripts/business/audit_agent_capability_status.py
python scripts/business/render_agent_capability_status_v2.py
python scripts/business/report_improvement_plan_completion.py
python scripts/business/render_agent_improvement_plan_v2.py
```

---

## 12. Estimation (remaining)

| Work item | Unit | Count | Notes |
|-----------|------|------:|-------|
| Real human trial sets | agent | 114 | ≥5 trials each; main cost |
| Gate evaluations | agent | 114 | automated after trials |
| Re-measure agent offline | agent | as needed | after prompt changes |
| Optional tool mocks | tool class | ~20–40 | not required for Q5 YES |

**Calendar hint:** Spine (7) → ATL (5) → batches of 10 craft agents per rater week.

---

## 13. Governance (prevent fake full marks)

1. **No Q5 YES without evidence** — audit reads gate.met && !synthetic.
2. **record_human_baseline.py refuses --synthetic** for real sessions.
3. **Golden must stay green** after any prompt/rubric change.
4. **HiTL confirms use action refs only** in product UI.
5. **Completion reports** must show claimable surpass count, not just protocol files.

---

## 14. Regeneration

```bash
python scripts/business/audit_agent_capability_status.py
python scripts/business/render_agent_capability_status_v2.py
python scripts/business/render_agent_improvement_plan_v2.py
```

Track progress: maturity **10.5 → 11.0**, weighted **95.45% → 100%**, Q5 YES **0 → 114**.

