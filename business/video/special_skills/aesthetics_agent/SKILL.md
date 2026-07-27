# Special skill integration — `aesthetics_agent`

**Status:** MVP integrated (2026-07-13)  
**Kind:** agent_family  
**Plan:** [`planning/special/aesthetics_agent.md`](../../../planning/special/aesthetics_agent.md)  
**Summary:** Visual aesthetics / look consistency via craft agents

## Host binding

### Agents
- `video.conceptartist` — SPEC 88.2KB, ALC=yes [OK]
- `video.styletransfer` — SPEC 93.4KB, ALC=yes [OK]
- `video.colorist` — SPEC 110.1KB, ALC=yes [OK]
- `video.moodboard` — SPEC 71.7KB, ALC=yes [OK]

### Workflow DNA
- `wf_video_arch_e_ai_short_film_v1` — steps=13 depth=phased_v1 [OK]
- `wf_video_spine_v1` — steps=8 depth=None [OK]

### Host modules
- _None_

## Runtime contract

- Entry agents: `video.orchestrator` / `video.planner` when DNA-bound.
- Tools: host allow-list only; design-time vendors stay in SPEC.
- Irreversible package/publish steps require human gate.
- No second control plane (N1).

Machine manifest: `integration.json`
