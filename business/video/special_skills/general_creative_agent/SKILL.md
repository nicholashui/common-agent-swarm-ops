# Special skill integration — `general_creative_agent`

**Status:** MVP integrated (2026-07-13)  
**Kind:** agent_family  
**Plan:** [`planning/special/general_creative_agent.md`](../../../planning/special/general_creative_agent.md)  
**Summary:** General creative decomposed into ideation/CD/novelty/director

## Host binding

### Agents
- `video.ideation` — SPEC 108.3KB, ALC=yes [OK]
- `video.creativedirector` — SPEC 56.5KB, ALC=yes [OK]
- `video.novelty` — SPEC 91.1KB, ALC=yes [OK]
- `video.director` — SPEC 318.4KB, ALC=yes [OK]

### Workflow DNA
- `wf_video_arch_a_viral_hook_v1` — steps=6 depth=None [OK]
- `wf_video_arch_e_ai_short_film_v1` — steps=13 depth=phased_v1 [OK]

### Host modules
- _None_

## Runtime contract

- Entry agents: `video.orchestrator` / `video.planner` when DNA-bound.
- Tools: host allow-list only; design-time vendors stay in SPEC.
- Irreversible package/publish steps require human gate.
- No second control plane (N1).

Machine manifest: `integration.json`
