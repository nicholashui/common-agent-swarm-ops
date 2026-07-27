# Special skill integration — `screenwriter_strategic_goal_achievement_agent`

**Status:** MVP integrated (2026-07-13)  
**Kind:** agent_family  
**Plan:** [`planning/special/screenwriter_strategic_goal_achievement_agent.md`](../../../planning/special/screenwriter_strategic_goal_achievement_agent.md)  
**Summary:** Strategic screenwriting via screenwriter/narrative/showrunner

## Host binding

### Agents
- `video.screenwriter` — SPEC 234.1KB, ALC=yes [OK]
- `video.narrativearc` — SPEC 90.5KB, ALC=yes [OK]
- `video.showrunner` — SPEC 192.9KB, ALC=yes [OK]
- `video.director` — SPEC 318.4KB, ALC=yes [OK]

### Workflow DNA
- `wf_video_arch_e_ai_short_film_v1` — steps=13 depth=phased_v1 [OK]
- `wf_video_arch_j_feature_film_v1` — steps=8 depth=thin_stub_n3 [OK]

### Host modules
- _None_

## Runtime contract

- Entry agents: `video.orchestrator` / `video.planner` when DNA-bound.
- Tools: host allow-list only; design-time vendors stay in SPEC.
- Irreversible package/publish steps require human gate.
- No second control plane (N1).

Machine manifest: `integration.json`
