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

```text
python -m pytest tests/unit/api/test_video_brief_spine.py -q
# 18 passed — includes persist, L1 handoff, agent loop
```

### Persistence env

| Env | Meaning |
|-----|---------|
| `CASOPS_PRODUCT_FACADE_PERSIST` | default `1`; set `0` for memory-only |
| `CASOPS_PRODUCT_FACADE_DATA` | store directory (default `<repo>/.data/product_facade`) |
