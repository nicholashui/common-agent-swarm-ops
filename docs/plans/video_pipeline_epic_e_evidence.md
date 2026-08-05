# Epic E evidence — Observability & honesty

**Date:** 2026-08-04  
**Plan:** `docs/plans/video_pipeline_brief_spine_plan.md` · Epic E (G6)

## Deliverables

| # | Deliverable | Implementation |
|---|-------------|----------------|
| 1 | Dashboard / Activity show real spine runs | `list_swarms` returns `has_spine`, `spine_status`, `spine_workflow_id`; dashboard-live maps spine drafts + activity count; activity-live maps `spine`/`approval` categories |
| 2 | Explicit UI copy “stub run · not production media” | Shared `STUB_RUN_HONESTY` in `video-spine-template.ts`; used on Dashboard, Activity, Agent Workflow, Plan materialize note, Execute spine panel |
| 3 | Agent Workflow “Open spine template” | Injected Host template `video.host.wf_video_spine_v1` · DNA id `wf_video_spine_v1`; button + `?template=` deep link; canvas + dashboard quick action |
| 4 | Evidence | This file + tests below |

## Commands & results

```text
# Backend (2026-08-04)
cd backend
python -m pytest tests/unit/api/test_video_brief_spine.py tests/unit/api/test_product_facade_routes.py -q
# → 18 passed

# Frontend (2026-08-04)
cd frontend
node --import tsx --test src/lib/projections/video-spine-template.test.ts src/lib/projections/activity-live.test.ts src/lib/projections/dashboard-live.test.ts src/lib/api/product-swarms.test.ts src/lib/api/product-composer.test.ts
# → 16 passed
```

## Test names (Epic E focus)

- `test_list_swarms_exposes_spine_flags_and_activity`
- `activity live surfaces spine/package events with honesty copy`
- `live dashboard labels spine drafts with honesty copy`
- `Host product spine template matches Host DNA id`
- `spine template deep link and id helpers`

## Honesty rules retained

- No fabricated production media quality or success rates  
- Package gates never auto-approve  
- `production_ready` remains false on spine payload  

## Follow-up polish (relevant product path)

| Item | Status |
|------|--------|
| `GET /api/v1/package-approvals/{id}` + POST decision | Done |
| `GET /api/v1/swarms/{id}/artifacts/{ref}` | Done |
| Brief meta on recommend (`brief_preview`) | Done |
| Plan samples auto-fill scale/archetype | Done |
| Spine step idempotency map | Done |
| Monitoring package-gate anomalies | Done |
| Canvas Phase-1 groups | Done |
| SDD `.kiro/specs/video-pipeline-brief-spine/` | Done |
| Standard `GET/POST /approvals/{id}` package fallback | Done |
| `GET …/artifacts` list + `POST …/spine/run-to-package` | Done |
| Operations live package Approve/Deny panel | Done |
| Running list includes spine package attention | Done |
| Execute artifact handoff list panel | Done |
| `listSwarmArtifacts` + dry-run client tests | Done |
| Durable façade store (`.data/product_facade`) | Done |
| ArtifactHandoffV1 + L1 validation on spine steps | Done |
| Append-only product audit (`GET /api/v1/product-audit`) | Done |
| Spine Plan→Act→Self-Review offline L2 (planner + QC) | Done |
| Critique emit + fail-closed on loop fail | Done |
| Activation policy on spine public view | Done |
| Host AgentLoopService for fleet pack agents | Done |
| `GET /api/v1/agent-loops/inventory` + run/crew APIs | Done |
| `POST /swarms/{id}/agent-loops` member crew run | Done |
| Spine uses AgentLoopService for spine agents | Done |
| DNA workflow sequential offline loops + project memory | Done |
| `GET/POST /agent-loops/workflows…` | Done |
| Execute “Run member loops (offline)” | Done |
| Host tool registry (stub default; live gated) | Done |
| Tool invocations on each agent loop Act | Done |
| Org project memory + critique log APIs | Done |
| Fleet sample offline run API | Done |
| Durable loop memory / critiques / tool JSONL | Done |
| Bounded parallel crew (`parallel` + `max_workers`) | Done |
| `GET /agent-loops/tool-invocations` | Done |
| Execute “Run DNA spine loops (offline)” | Done |
| Durable rehydrate across fresh `AgentLoopService` instances | Done (`test_durable_loop_memory_and_tools_rehydrate_across_service_instances`) |
| Execute UI structural test (member + DNA spine offline controls) | Done |
| Tool catalog honesty (never claims live on agent-loop Act) | Done (`test_tool_catalog_never_claims_live_on_agent_loop_surface`) |
| `loop_passed` fail-closed on explicit L2 fail | Done (`test_loop_passed_fail_closed_on_l2_or_status`) |
| Parallel crew durable memory (no lost rows on rehydrate) | Done (`test_parallel_crew_durable_memory_rehydrates_all_agents`; stress 20/20) |

```text
# Backend (2026-08-05 parallel-persist fix) — twice, exit 0 both
python -m pytest tests/unit/api/test_agent_loops.py tests/unit/api/test_video_brief_spine.py -q --tb=short
# → 28 passed (×2)

# Frontend (2026-08-05)
node --import tsx --test src/lib/api/product-agent-loops.test.ts
# → 5 passed

# Parallel rehydrate stress: 20/20
# Durable rehydrate smoke (parallel crew): mem >= completed; all agent_ids; REHYDRATE_OK
# Catalog honesty: CASOPS_MEDIA_LIVE=1 still production_media=False
```

### Honest scope note

Fleet offline loops = loadable pack agents Plan→Act→Self-Review offline with **stub tools**;  
DNA workflows = sequential loops + project memory; crew may use **bounded parallel** threads (not Temporal).  
When `CASOPS_PRODUCT_FACADE_PERSIST` is enabled (default), agent-loop project memory, critiques, and tool-invocation JSONL **survive process re-init** for a shared durable store — they are **not** memory-only loss.  
**Not** included: concurrent Temporal production swarm + unrestricted live Sora/Veo for all 114.

### Persistence env

| Env | Meaning |
|-----|---------|
| `CASOPS_PRODUCT_FACADE_PERSIST` | default `1`; set `0` for memory-only |
| `CASOPS_PRODUCT_FACADE_DATA` | store directory (default `<repo>/.data/product_facade`) |

Loop durable files under the data dir: `loop_memory.json`, `loop_critiques.json`, `loop_tool_invocations.jsonl`.
