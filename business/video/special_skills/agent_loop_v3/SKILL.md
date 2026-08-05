# Special skill integration — `agent_loop_v3`

**Status:** Host offline foundation (2026-08-05)  
**Kind:** host_loop_pattern  
**Plan:** [`docs/plans/agent_loop_v3_host_foundation.md`](../../../../docs/plans/agent_loop_v3_host_foundation.md)  
**Summary:** Cognitive agent loop (Cynefin/Premortem/AAR/critics/RPD) over pack Plan→Act→Self-Review

## Host binding

### Agents
- `video.orchestrator` — pack loop capable
- `video.planner` — pack loop capable
- `video.memory` — pack loop capable
- `video.judge` — pack loop capable
- `specials.agent-loop-creator` — draft pack + Host v3 prompts

### Workflow DNA
- `wf_video_spine_v1`

### Host modules
- `backend/app/video/agent_loop_service.py` — fleet Plan→Act→Self-Review
- `backend/app/video/loop_v3/` — offline v3 cognitive envelope
- `backend/app/api/v1/agent_loops.py` — `/api/v1/agent-loops/*`
- `backend/app/video/tool_activation.py` — Act tool registry

## Runtime contract

- Entry: `POST /api/v1/agent-loops/agents/{id}/run` (`enable_v3` default true).
- Tools: host allow-list only; Act is stub-by-default / live_blocked for media.
- Irreversible package/publish steps require human gate.
- No second control plane (N1).

Machine manifest: `integration.json`
