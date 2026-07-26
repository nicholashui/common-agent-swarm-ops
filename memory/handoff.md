# Handoff

**As of:** 2026-07-26  
**State:** Video pack agent phase of `redo_migration.md` v2 complete (114 self-contained agents; no pack corpus required). Frontend action bridge from prior turn remains.

## Latest work

### Specials agents — same self-contained layout as video

- **19** `business/specials/agents/*` folders now match video setup:
  `SPEC.md`, `README.md`, `agent_spec.json`, `sources/`, `prompts/`, `rubrics/`
- Pack maps: `AGENT_SOURCE_MAP.json`, `ROSTER.json`, `MAP.md` (no `inventory.json` — specials `inventory_required: false`)
- Scripts: `build_specials_agent_folders.py`, `check_specials_agents_standalone.py`
- `agent_spec.json` unchanged (governance hash-bound); still draft / fail-closed
- Gates: specials agents standalone PASS; pack tests 9 passed; governance still fail-closed (missing risk assessments expected)

### redo_migration.md v2 — video agent phase IMPLEMENTED

- **Policy:** self-contained agents; pack `corpus/` **not** required
- **Artifacts:** `business/video/AGENT_SOURCE_MAP.json`, `ROSTER.json`, `MAP.md`, `SPEC_REVIEWS.json`, `README.md`
- **114 agents** each with `SPEC.md`, `README.md`, `sources/PROVENANCE.json`, `sources/MAPPING.md`, prompts/rubrics stubs
- **Scripts:**  
  - `scripts/business/build_common_video_agent_folders.py`  
  - `scripts/business/check_common_video_agents_standalone.py`  
- **Standalone:** `check_video_domain_standalone.py` treats missing corpus as PASS  
- **Gates green:** agents standalone, full standalone, mapping unit tests  
- **Deferred:** workflow DNA A–J, knowledge seeds, special skills, optional corpus

### Auto-detect + implement missing UI actions

- **Detection (CI):** `lib/ui/missing-implementation-scan.test.ts`
  - Every `*Home` must accept `onAction` + `ScreenUiAction`
  - `BoundScreenHome` must pass `onAction={...}` for every bound screen
  - No permanent `disabled={true}` on Homes
  - Runtime must expose run/eval/dispatch/memory/approval methods
- **Bridge:** `lib/ui/screen-actions.ts` + `use-screen-action.ts`
  - `classifyAnnounce` maps legacy stub strings → structured actions
  - `performScreenAction` executes local store, Public API, or fail-closed
- **Runtime extensions:** `createRun`, `dispatchRun`, `createAndDispatchRun`, `runEvaluation`, `loadTopology`
- **BoundScreenHome:** every screen mounts `InteractionStatusBar` + action bridge
- **Real paths:**
  - Knowledge search → `retrieve_memory`
  - Eval “Run Batch Eval Campaign” → `run_evaluation`
  - Canvas ▶ Run → create + dispatch run
  - Dashboard Pause → session patch + success feedback
  - Layout / prefs / mark-read → local real session feedback
  - Governed stubs (export, merge, deploy without action ref) → honest fail-closed error
- **Tests:** `screen-actions.test.ts`, scan tests green; Home structure tests green; `tsc --noEmit` clean

### Real UI interactions (prior)

- `createOperatorApi()` uses browser `fetch` by default
- Operations Console: inspect run, load/decide approval, context refresh
- Screen parameters store + hardcode scan gates

### Five-doc redesign + specials (prior)

- Alignment tests green; specials catalog fail-closed draft; video migration PROPOSED

## Deferred (not frontend-completable without host contracts)

- Aggregate landing projections from live `/api/v1` (replace LOCAL_* fixtures in store)
- Governed mutations that require host-returned action references
- Video pack M0–M7 graphs; specials production activation

## Resume here

1. Commit when ready (frontend action bridge + Homes + scans).
2. Point canvas/eval workflow ids at host-returned topology when available.
3. Wire live projections into `setScreenParameters` as OpenAPI expands.
