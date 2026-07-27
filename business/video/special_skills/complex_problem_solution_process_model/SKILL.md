# Special skill integration — `complex_problem_solution_process_model`

**Status:** MVP integrated (2026-07-13)  
**Kind:** process_model  
**Plan:** [`planning/special/complex_problem_solution_process_model.md`](../../../planning/special/complex_problem_solution_process_model.md)  
**Summary:** Complex problem process → planner decomposition + gates

## Host binding

### Agents
- `video.planner` — SPEC 553.1KB, ALC=yes [OK]
- `video.orchestrator` — SPEC 472.9KB, ALC=yes [OK]
- `video.judge` — SPEC 246.7KB, ALC=yes [OK]
- `video.gatekeeper` — SPEC 235.8KB, ALC=yes [OK]

### Workflow DNA
- `wf_video_spine_v1` — steps=8 depth=None [OK]
- `wf_video_production_e2e_v1` — steps=9 depth=thin_stub_n3 [OK]

### Host modules
- `backend/app/domain/workflows/archetype_selector.py` [OK]

## Runtime contract

- Entry agents: `video.orchestrator` / `video.planner` when DNA-bound.
- Tools: host allow-list only; design-time vendors stay in SPEC.
- Irreversible package/publish steps require human gate.
- No second control plane (N1).

Machine manifest: `integration.json`
