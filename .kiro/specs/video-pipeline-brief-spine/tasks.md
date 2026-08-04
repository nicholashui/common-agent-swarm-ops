# Tasks — Video pipeline brief → spine

1. **REQ-1/2** Brief + Phase-1 materialize — `product_facade.materialize_ai_composition`, `video_brief_spine.build_user_brief`
2. **REQ-3/4** Spine stubs + artifacts — `apply_stub_step`, `POST …/spine/steps`, `GET …/artifacts/{ref}`
3. **REQ-5/6** Package HITL — package approvals store, decide APIs, activity
4. **REQ-7** Observability honesty — activity-live, dashboard-live
5. **REQ-8** Agent Workflow spine template — `video-spine-template.ts`
6. **Polish** Package detail on standard approvals path; list artifacts; dry-run-to-package; Ops live package panel

## Status

Wave 1–4 (A–E) + polish: **implemented** (process-local façade).
