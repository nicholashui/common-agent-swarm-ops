# Plan: User Brief → Phase 1 → Runnable Video Spine

**Status:** Implemented (Wave 1–3 product path)  
**Date:** 2026-08-04  
**Implemented:** 2026-08-04  

**Owner:** Product / Host / Frontend (CASOPS)  
**Related design:** `business/video/corpus/study/SYSTEM_REFERENCE.md` §6.1 · `SYSTEM_REFERENCE_hk.md` · `business/video/design/workflows/wf_video_spine_v1.dna.json`  
**Related product surfaces:** Plan (`/composer`) · Execute (`/swarms/{id}/canvas`) · Approvals (`/operations`) · Registry Agent Workflow  

---

## 1. Purpose

Turn the design-only production pipeline (starts with **用戶簡報 / USER BRIEF**, then six phases) into a **minimal, fail-closed product path**:

1. Human provides a **structured brief** (not only free text).  
2. Host binds a **Phase-1 crew** (and optional DIA).  
3. Host can run a **spine workflow** (stubs OK) with **artifact handoffs** and a **human gate** on package.

This plan **does not** implement full phases 2–6 tooling (real media gen, VO, VFX, distribution automation). Those come after the spine works.

---

## 2. Goals

| ID | Goal |
|----|------|
| G1 | **Brief is a first-class Host object** attached to a swarm draft (versioned, auditable). |
| G2 | **Plan materialize** creates a draft whose members match Phase-1 intent (orchestrator + planner + producer ± intent analysis). |
| G3 | **Spine graph** (`wf_video_spine_v1` or Host equivalent) is materializable and runnable with **stub tools**. |
| G4 | **Artifacts** flow between steps (`parsed_brief` → … → `package`) as redacted refs, not silent side effects. |
| G5 | **Package step** requires Host approval; UI shows gate on Approvals / Operations. |
| G6 | UI remains fail-closed: no invented production activation, no fake success metrics. |

---

## 3. Non-goals (this plan)

- Full 6-phase concurrent swarm with all 114 agents.  
- Real media generation, voice, music, VFX render pipelines.  
- Full production activation of `specials.intent-analysis-agent` (may ship as **parse stub** or optional bind first).  
- Replacing existing Plan samples / Operate sample toggles.  
- Changing Host identity model or multi-tenant isolation.  
- Billing / real cost projection for spine runs.

---

## 4. Current state (baseline)

| Layer | Today |
|-------|--------|
| Design | USER BRIEF → Phase 1…6 documented in SYSTEM_REFERENCE + agent SPECs |
| Pack | Most `video.*` roles exist; DIA = `specials.intent-analysis-agent` (**draft / data-only**) |
| DNA | `wf_video_spine_v1.dna.json` exists, **`production_ready: false`** |
| Plan | Free-text **goal/spec** → recommend/materialize members → draft |
| Execute | Inspect draft members; Host run still partial / fail-closed |
| Approvals | Sample gate UI; live gate needs real Host approval ids |

**Gap summary:** Brief is informal; crew pick is generic; spine not Host-runnable; artifacts not chained; package HITL not productized.

---

## 5. Target architecture (high level)

```text
┌─────────────┐     POST recommend/materialize      ┌──────────────────┐
│ Plan UI     │ ──────────────────────────────────► │ Host Product     │
│ (goal+meta) │     brief_contract + goal text      │ Façade           │
└─────────────┘                                     └────────┬─────────┘
                                                             │
                    create/update swarm draft                │
                    members = Phase-1 crew                     │
                    brief_snapshot on draft                  │
                                                             ▼
┌─────────────┐     open /swarms/{id}/canvas        ┌──────────────────┐
│ Execute UI  │ ◄────────────────────────────────── │ Swarm draft      │
│ spine steps │     run step (stub tools)           │ + graph + arts   │
└──────┬──────┘                                     └────────┬─────────┘
       │ package human_gate_required                           │
       ▼                                                       ▼
┌─────────────┐     GET/POST approvals              ┌──────────────────┐
│ Approvals   │ ◄────────────────────────────────── │ Approval gate    │
└─────────────┘                                     └──────────────────┘
```

**Fail-closed rules (must keep):**

- No step run without Host action reference / eligibility.  
- Irreversible package requires human decision.  
- Stubs never claim production media quality.  
- Pack agents stay **non-active** until Host activation policy says otherwise.

---

## 6. Proposed workstreams (implementation later)

### Epic A — Brief contract (G1)

**Deliverables**

1. **Schema (Host):** e.g. `UserBriefV1`  
   - `text` (required, non-empty)  
   - `locale` (optional, default `en` / `zh-Hant`)  
   - `scale_profile` optional (`S1`…`S5` aligned with pack)  
   - `archetype` optional (`A`…`J` or none)  
   - `constraints` optional (budget band, duration, platform)  
   - `as_of` / correlation on write  
2. **API:** accept brief on materialize (and optionally recommend); persist on swarm draft.  
3. **Plan UI:** keep free-text primary; add optional metadata chips (scale/archetype) without inventing Host fields that are not stored.  
4. **Tests:** reject empty brief; round-trip on draft GET.

**Acceptance**

- [x] Materialize without text fails closed.  
- [x] GET swarm returns brief snapshot (redacted if needed).  
- [x] No secrets in brief payload.

**Depends on:** nothing (start here).

---

### Epic B — Phase-1 crew materialize (G2)

**Deliverables**

1. **Closed-world Phase-1 template** (deterministic):  
   - Required: `video.orchestrator`, `video.planner`, `video.producer`  
   - Optional: `specials.intent-analysis-agent` **only if** policy allows draft bind (else planner owns “parse brief” output).  
2. **Recommend bias:** when goal looks like production brief (video domain samples), prefer Phase-1 + spine-compatible pattern over unrelated packs.  
3. **Execute:** members list shows Phase-1 roles; workflow diagram phases label “Intent & Planning” for those nodes.  
4. **Tests:** materialize fixture asserts agent ids ⊆ catalog; order documented.

**Acceptance**

- [x] Sample wuxia/brand goals produce Phase-1-capable crew (documented agent set).  
- [x] No invented agent ids.  
- [x] Draft openable on `/swarms/{id}/canvas`.

**Depends on:** Epic A (brief on draft preferred; can hard-cut if brief only in materialize body first).

---

### Epic C — Spine graph + stub run (G3, G4)

**Deliverables**

1. **Host representation** of `wf_video_spine_v1` steps (or generate graph from DNA JSON):  

   | Step | Agent (from DNA) | Stub tool | Artifact out (proposed) |
   |------|------------------|-----------|-------------------------|
   | orchestrate | video.orchestrator | audit_log | `run_context` |
   | plan | video.planner | audit_log | `parsed_brief` / plan DAG stub |
   | direct | video.director | audit_log | `creative_direction` stub |
   | screenwrite | video.screenwriter | video_script_format | `script` stub |
   | research | video.webresearch | audit_log | `research_bundle` stub |
   | media_gen | video.director | video_media_gen_stub | `media_stub` |
   | qc | video.aiqaconsistency | video_qc_stub | `qc_report` |
   | package | video.producer | video_package_stub | `package` (**gate**) |

2. **Run API:** advance one step / dispatch with eligibility + idempotency.  
3. **Execute UI:** show step status on orchestration board (queued / complete / waiting_for_approval).  
4. **Tests:** dry-run spine without network media; artifact refs present after each step.

**Acceptance**

- [x] Full spine dry-run completes to package **waiting for human** (or complete if gate mocked in test only).  
- [x] Artifacts queryable by opaque ref.  
- [x] `production_ready` remains false until explicit promotion decision (separate change).

**Depends on:** Epic B (members must include spine agents).

---

### Epic D — Package human gate (G5)

**Deliverables**

1. Host creates **approval** when package step requires human.  
2. Operations / Approvals UI loads real `approval_id` (not only sample projection).  
3. Approve → resume package / mark draft ready; Deny → fail-closed with reason.  
4. Activity feed records gate events (if activity façade already records ops).

**Acceptance**

- [x] Gate appears with real id after spine reaches package.  
- [x] Sample approval toggle remains demo-only; live path never auto-approves.  
- [x] Decision is idempotent and audited.

**Depends on:** Epic C.

---

### Epic E — Observability & honesty (G6)

**Deliverables**

1. Dashboard / Activity show **real** spine runs when present (already partially Host-bound).  
2. Explicit UI copy: “stub run · not production media”.  
3. Agent Workflow UI: optional link “Open spine template” → same DNA id as Host.  
4. Evidence: commands + test names recorded for review.

**Acceptance**

- [x] Dashboard lists spine drafts (`has_spine` / `spine_status`) with honesty copy.  
- [x] Activity maps spine + package events; KPI for spine/package.  
- [x] Agent Workflow “Open spine template” selects `wf_video_spine_v1`.  
- [x] Evidence: `docs/plans/video_pipeline_epic_e_evidence.md`.

**Depends on:** C–D for meaningful events.

---

## 7. Suggested implementation order (for later)

| Wave | Epics | Outcome for reviewers |
|------|--------|------------------------|
| **Wave 1** | A + B | Brief stored; Phase-1 draft from Plan |
| **Wave 2** | C | Spine dry-run with artifacts |
| **Wave 3** | D | Real package approval |
| **Wave 4** | E | UI honesty + Agent Workflow alignment |

**Do not** start Wave 2 media tools or full Phase 3–6 expansion before Wave 1–2 exit criteria pass.

---

## 8. Agent mapping (Phase 1 + spine only)

| Design name | Pack / specials ID | Role in this plan |
|-------------|--------------------|-------------------|
| USER BRIEF | (human input) | Epic A |
| IntentAnalysisAgent (DIA) | `specials.intent-analysis-agent` | Optional bind; else planner parses |
| PlannerAgent | `video.planner` | Phase 1 + spine `plan` |
| ProducerAgent | `video.producer` | Phase 1 + spine `package` |
| Orchestrator | `video.orchestrator` | Spine owner / materialize hub |
| DirectorAgent | `video.director` | Spine `direct` / media stub |
| ScreenwriterAgent | `video.screenwriter` | Spine `screenwrite` |
| Research | `video.webresearch` | Spine `research` |
| AIQA / QC | `video.aiqaconsistency` | Spine `qc` |

Costume / full pre-prod / full post / distribution agents: **out of Wave 1–3**.

---

## 9. API / contract sketch (for review, not final OpenAPI)

### 9.1 Materialize (extend existing)

`POST /api/v1/composer/materialize`

```json
{
  "goal": "…",
  "brief": {
    "locale": "zh-Hant",
    "scale_profile": "S1",
    "archetype": "A",
    "constraints": { "max_duration_sec": 90 }
  },
  "human_resolutions": {}
}
```

Response (existing fields plus):

```json
{
  "swarm_id": "…",
  "canvas_path": "/swarms/…/canvas",
  "brief_id": "…",
  "spine_workflow_id": "wf_video_spine_v1"
}
```

### 9.2 Swarm read (extend)

`GET /api/v1/swarms/{id}` includes `brief`, `members`, optional `spine` progress + artifact refs.

### 9.3 Run step (new or existing runs façade)

- Fail-closed without action ref.  
- Returns next step status + artifact refs + optional `approval_id`.

*Exact shapes to be locked in SDD/OpenAPI before coding.*

---

## 10. UI changes (later)

| Screen | Change |
|--------|--------|
| Plan | Optional scale/archetype controls; brief meta sent on materialize |
| Execute | Spine stepper / node status; artifact list; package waiting state |
| Approvals | Live gate for package; keep ▦ sample separate |
| Agent Workflow | Link or badge for `wf_video_spine_v1` |

No new top-level menu item required for Wave 1–3.

---

## 11. Testing strategy (later)

| Type | Scope |
|------|--------|
| Unit | Brief validation; Phase-1 member set; DNA → Host graph mapping |
| Integration | Materialize → GET swarm → run spine steps (in-memory Host) |
| UI | Plan materialize path; Execute shows waiting_for_approval; samples still fail-closed |
| Policy | No network installers; dry-run spine without external media |

---

## 12. Risks and decisions for reviewer

| Risk / decision | Options | Recommendation |
|-----------------|---------|----------------|
| DIA not production-ready | (a) Bind draft specials agent (b) Planner emits `parsed_brief` only | **(b) for Wave 1**; optional DIA in Wave 2 |
| Spine DNA vs Host graph | (a) Import DNA JSON (b) Hardcode Host template | **(a)** single source `wf_video_spine_v1.dna.json` |
| Promote `production_ready` | When? | **Not in this plan** — separate go-live review |
| Full Phase 3–6 | When? | After Wave 3 exit criteria |

---

## 13. Exit criteria (plan complete when later implemented)

Wave 1–3 done when:

1. User can paste a production brief in Plan (with optional scale/archetype).  
2. Materialize creates draft with Phase-1 (+ spine-capable) members and stored brief.  
3. Execute can dry-run spine stubs to package.  
4. Package opens a **real** Host approval.  
5. Approve/deny is audited; deny fails closed.  
6. Docs + tests evidence recorded; no fake “production complete” claims.

---

## 14. Open questions (please answer in review)

1. **Locale default** for brief: `en` only, or bilingual `zh-Hant` first-class?  
2. **DIA in Wave 1:** skip bind entirely, or allow non-active specials member for display only?  
3. **Package gate:** always HITL, or only when `scale_profile ≥ S2`? (DNA currently human_gate on package.)  
4. **Should Plan samples auto-fill scale/archetype** when loading wuxia/social samples?  
5. **Persistence:** keep process-local façade for drafts, or require DB for brief/artifacts in Wave 2?

---

## 15. Review checklist

- [ ] Goals G1–G6 accepted  
- [ ] Non-goals accepted  
- [ ] Wave order accepted  
- [ ] Open questions answered  
- [ ] Ready for SDD (requirements/design/tasks) before coding  

---

## 16. Next step after approval

1. Freeze open-question answers in this doc.  
2. Author SDD under `.kiro/specs/` (or project template): requirements → design → tasks → trace.  
3. Implement **Wave 1 (A+B)** only; stop for demo/review before Wave 2.

**This document is plan-only. No code changes are implied by accepting the doc structure; implementation starts only after explicit approval of Waves and open questions.**
