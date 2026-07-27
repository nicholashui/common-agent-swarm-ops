# Special skill integration — `lifes_quiet_redemption_agent_workflow`

**Status:** MVP integrated (2026-07-13)  
**Kind:** dna_workflow  
**Plan:** [`planning/special/lifes_quiet_redemption_agent_workflow.md`](../../../planning/special/lifes_quiet_redemption_agent_workflow.md)  
**Summary:** LQR worked example → archetype E + LQR DNA family

## Host binding

### Agents
- `video.director` — SPEC 318.4KB, ALC=yes [OK]
- `video.screenwriter` — SPEC 234.1KB, ALC=yes [OK]
- `video.promptengineer` — SPEC 183.0KB, ALC=yes [OK]
- `video.aiqaconsistency` — SPEC 146.4KB, ALC=yes [OK]
- `video.editor` — SPEC 257.4KB, ALC=yes [OK]

### Workflow DNA
- `wf_video_arch_e_ai_short_film_v1` — steps=13 depth=phased_v1 [OK]
- `wf_video_lqr_overview_v1` — steps=6 depth=thin_stub_n3 [OK]

### Host modules
- _None_

## Runtime contract

- Entry agents: `video.orchestrator` / `video.planner` when DNA-bound.
- Tools: host allow-list only; design-time vendors stay in SPEC.
- Irreversible package/publish steps require human gate.
- No second control plane (N1).

Machine manifest: `integration.json`
