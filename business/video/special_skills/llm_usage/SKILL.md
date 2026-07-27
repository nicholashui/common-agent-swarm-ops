# Special skill integration — `llm_usage`

**Status:** MVP integrated (2026-07-13)  
**Kind:** host_infra  
**Plan:** [`planning/special/llm_usage.md`](../../../planning/special/llm_usage.md)  
**Summary:** LLM usage policy via host providers + cost/latency optimizers

## Host binding

### Agents
- `video.costoptimizer` — SPEC 88.0KB, ALC=yes [OK]
- `video.latencyoptimizer` — SPEC 68.3KB, ALC=yes [OK]
- `video.router` — SPEC 263.6KB, ALC=yes [OK]

### Workflow DNA
- _None_

### Host modules
- `backend/app/infrastructure/llm/base.py` [OK]
- `backend/app/infrastructure/llm/mock_provider.py` [OK]
- `backend/app/infrastructure/llm/openai_provider.py` [OK]

## Runtime contract

- Entry agents: `video.orchestrator` / `video.planner` when DNA-bound.
- Tools: host allow-list only; design-time vendors stay in SPEC.
- Irreversible package/publish steps require human gate.
- No second control plane (N1).

Machine manifest: `integration.json`
