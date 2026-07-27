# Special skill integration — `knowledge_router_agent`

**Status:** MVP integrated (2026-07-13)  
**Kind:** routing  
**Plan:** [`planning/special/knowledge_router_agent.md`](../../../planning/special/knowledge_router_agent.md)  
**Summary:** Knowledge routing via router_table + research agents

## Host binding

### Agents
- `video.router` — SPEC 263.6KB, ALC=yes [OK]
- `video.memory` — SPEC 293.1KB, ALC=yes [OK]
- `video.webresearch` — SPEC 147.4KB, ALC=yes [OK]

### Workflow DNA
- `wf_video_spine_v1` — steps=8 depth=None [OK]

### Host modules
- `business/video/router_table.json` [OK]
- `backend/app/domain/knowledge/retrieval.py` [OK]

## Runtime contract

- Entry agents: `video.orchestrator` / `video.planner` when DNA-bound.
- Tools: host allow-list only; design-time vendors stay in SPEC.
- Irreversible package/publish steps require human gate.
- No second control plane (N1).

Machine manifest: `integration.json`
