# Special skill integration — `video_generation_techology_should_learn_now`

**Status:** MVP integrated (2026-07-13)  
**Kind:** tech_radar  
**Plan:** [`planning/special/video_generation_techology_should_learn_now.md`](../../../planning/special/video_generation_techology_should_learn_now.md)  
**Summary:** Gen-video tech radar → prompt/benchmark/eval agents + media stubs

## Host binding

### Agents
- `video.promptengineer` — SPEC 183.0KB, ALC=yes [OK]
- `video.benchmarkresearch` — SPEC 138.2KB, ALC=yes [OK]
- `video.evaluationharness` — SPEC 262.7KB, ALC=yes [OK]

### Workflow DNA
- `wf_video_spine_v1` — steps=8 depth=None [OK]
- `wf_video_arch_e_ai_short_film_v1` — steps=13 depth=phased_v1 [OK]

### Host modules
- _None_

## Runtime contract

- Entry agents: `video.orchestrator` / `video.planner` when DNA-bound.
- Tools: host allow-list only; design-time vendors stay in SPEC.
- Irreversible package/publish steps require human gate.
- No second control plane (N1).

Machine manifest: `integration.json`
