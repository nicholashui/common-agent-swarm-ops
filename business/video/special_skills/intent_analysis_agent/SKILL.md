# Special skill integration — `intent_analysis_agent`

**Status:** MVP integrated (2026-07-13)  
**Kind:** selection_binding  
**Plan:** [`planning/special/intent_analysis_agent.md`](../../../planning/special/intent_analysis_agent.md)  
**Summary:** Intent analysis feeds archetype recommend-workflow + planner

## Host binding

### Agents
- `video.planner` — SPEC 553.1KB, ALC=yes [OK]
- `video.router` — SPEC 263.6KB, ALC=yes [OK]

### Workflow DNA
- `wf_video_spine_v1` — steps=8 depth=None [OK]

### Host modules
- `backend/app/domain/workflows/archetype_selector.py` [OK]
- `business/video/archetype_registry.json` [OK]
- `scripts/business/recommend_video_workflow.py` [OK]

## Runtime contract

- Entry agents: `video.orchestrator` / `video.planner` when DNA-bound.
- Tools: host allow-list only; design-time vendors stay in SPEC.
- Irreversible package/publish steps require human gate.
- No second control plane (N1).

Machine manifest: `integration.json`
