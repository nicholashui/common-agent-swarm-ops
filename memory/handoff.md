# Handoff

**As of:** 2026-07-27  
**State:** VA study `*.md` (no `_hk`/`_zh`) all in corpus; capability index + phased plan published. Runtime partial vs full study prose.

## Latest work

### VA study/*.md capability lock + plan (2026-07-27)

- All **37** study markdowns (exclude locale) exact in `business/video/corpus/study/`
- Index: `business/video/STUDY_CAPABILITY_INDEX.json`
- Status: `docs/va_study_implementation_status.md`
- Plan (one-by-one phases 0–7): `docs/va_study_implementation_plan.md`
- Script: `scripts/business/sync_va_study_md.py --write`
- Knowledge seeds linked to key study docs

### Production / live media activation (2026-07-27)

- Host: `app/video/media_production.py`, `app/adapters/media_live.py` (`media.sora|veo|runway|elevenlabs`)
- Pack: `business/video/production/profile.json` enabled; DNA `production_ready: true`; 12 media agents activated with tools
- Credentials: env-only (`credentials.env.example`); never committed
- Flags: `CASOPS_VIDEO_PRODUCTION_ENABLED` + `CASOPS_VIDEO_MEDIA_NETWORK`
- Script: `scripts/business/enable_video_production.py --write`
- Gates: agents PASS, STANDALONE PASS, media unit tests 6/6 (+ blockers)

### Official redesign COMPLETE closeout (2026-07-27)

- Script: `scripts/business/close_migration_redesign_complete.py`
- Artifacts: `WORKFLOW_ROLE_MAP.json` (212 entries), `workflow_coverage.json` (14 families), knowledge/special_skills indexes
- Evidence: `docs/migration_redesign/evidence/MIGRATION_COMPLETE_EVIDENCE.*`
- Docs: `migration_redesign.md` → COMPLETE; root `MIGRATION_COMPLETE.md`
- UI: `documentStatus: complete`, `selfContained: true`, still fail-closed on production activation
- Gates: agents standalone PASS, full STANDALONE PASS, FE migration/five-doc tests PASS
- Residuals (explicit): live media stubs, DNA production_ready false, not full FE→API coverage

### Adopt remaining generic assets → common better than generic (2026-07-27)

- Script: `scripts/business/adopt_generic_remaining_assets.py`
- Copied: `graphs/`, `tools/`, `evals/`, design DNA, missing policies, docs maps
- Agent source depth: **114/114** with `sources/excerpts` + `sources/study` (**924** files)
- Process coverage: host **27** VA process_id rows; design catalog **33** (`design/process_coverage_va.json`)
- UI: `pack-process.generated.ts` + Registry stats/impact rows
- Record: `business/video/ADOPTION_GENERIC_REMAINING.json`
- Gates: agents standalone PASS, full STANDALONE PASS; FE typecheck + registry/migration tests PASS

### Pure VA Domain Pack content, naming, SPEC depth, Agent IDs (2026-07-27)

- **Agent IDs ≈ VA tables:** exact match generic pack IDs **114/114** (e.g. `video.creativedirector`, `video.compliance`, `video.planner`)
- **SPEC depth:** avg **~124 KB** (generic ~123 KB); Identity table with `va_id`/category/upstream name; lifted VA table sections; full generic body under Provenance
- **agent_spec metadata:** `va_id`, `va_name`, `va_category` on all 114; critique edges default to `video.critic` / `video.judge`
- **Host DNA:** 14/14 valid; critique loops use VA `video.critic` + `video.judge` (not legacy coordinator IDs)
- **Runtime fix:** `COMPLIANCE_AGENT_ID = video.compliance` (aligned to pack_spine)
- **UI export:** 133 agents (114+19), sample starts with VA IDs
- Scripts: `align_video_ids_to_va_taxonomy.py`, `rebuild_va_aligned_specs_valid.py`, `convert_design_dna_to_host_graphs.py`
- Docs: `docs/va_taxonomy_alignment_notes.md`, `docs/va_implementation_comparison_report.md` updated
- **Gates:** agents standalone PASS, specials PASS, full STANDALONE PASS (`--network-disabled --upstreams-unavailable`), blocker unit tests 3 passed

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
