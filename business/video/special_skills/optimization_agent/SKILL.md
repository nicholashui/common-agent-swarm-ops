# Special skill integration — `optimization_agent`

**Status:** MVP integrated (2026-07-13)  
**Kind:** agent_family  
**Plan:** [`planning/special/optimization_agent.md`](../../../planning/special/optimization_agent.md)  
**Summary:** Optimization family (prompt/cost/retention/ROAS/eval)

## Host binding

### Agents
- `video.promptoptimizer` — SPEC 80.6KB, ALC=yes [OK]
- `video.costoptimizer` — SPEC 88.0KB, ALC=yes [OK]
- `video.retentionoptimizer` — SPEC 272.1KB, ALC=yes [OK]
- `video.roasoptimizer` — SPEC 63.3KB, ALC=yes [OK]
- `video.evaluationharness` — SPEC 262.7KB, ALC=yes [OK]

### Workflow DNA
- `wf_video_arch_b_ugc_ad_v1` — steps=11 depth=phased_v1 [OK]

### Host modules
- `backend/app/domain/evaluations/evaluators.py` [OK]

## Runtime contract

- Entry agents: `video.orchestrator` / `video.planner` when DNA-bound.
- Tools: host allow-list only; design-time vendors stay in SPEC.
- Irreversible package/publish steps require human gate.
- No second control plane (N1).

Machine manifest: `integration.json`
