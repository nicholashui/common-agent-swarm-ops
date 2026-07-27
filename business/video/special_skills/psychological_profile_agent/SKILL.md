# Special skill integration — `psychological_profile_agent`

**Status:** MVP integrated (2026-07-13)  
**Kind:** agent_family  
**Plan:** [`planning/special/psychological_profile_agent.md`](../../../planning/special/psychological_profile_agent.md)  
**Summary:** Audience/psych signals via audiencesim + emotionalarc + retention

## Host binding

### Agents
- `video.audiencesim` — SPEC 317.5KB, ALC=yes [OK]
- `video.emotionalarc` — SPEC 115.2KB, ALC=yes [OK]
- `video.retentionoptimizer` — SPEC 272.1KB, ALC=yes [OK]

### Workflow DNA
- `wf_video_arch_a_viral_hook_v1` — steps=6 depth=None [OK]
- `wf_video_arch_b_ugc_ad_v1` — steps=11 depth=phased_v1 [OK]

### Host modules
- _None_

## Runtime contract

- Entry agents: `video.orchestrator` / `video.planner` when DNA-bound.
- Tools: host allow-list only; design-time vendors stay in SPEC.
- Irreversible package/publish steps require human gate.
- No second control plane (N1).

Machine manifest: `integration.json`
