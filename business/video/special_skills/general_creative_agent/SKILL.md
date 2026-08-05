# Special skill integration — `general_creative_agent`

**Status:** Host offline SSOR-lite foundation (2026-08-05)  
**Kind:** agent_family  
**Plan:** [`docs/plans/creative_complex_strategic_llm_host_foundation.md`](../../../../docs/plans/creative_complex_strategic_llm_host_foundation.md)  
**Summary:** Offline GCA SSOR-lite — multi-POV, sparse outliers (≤4), value-gate, phase_trace, integration/refinement, process-local patterns API, next-agent handoff package

## Host modules
- `backend/app/creative/`  
- `backend/app/api/v1/creative.py`  
- Tools: `creative.ideate`, `creative.patterns`  
- FE client: `frontend/src/lib/api/product-creative.ts`  

## Runtime contract
- Fail-closed: no live generation / MCTS / FAISS / NLAE / CreativeAgentFactory product  
- Offline formula: `Cr = B(N,K) · U · Q · F` (deterministic stub, not live LLM)  
- Integration: each candidate has `risks_mitigations` + `refinement_note`; phase `integration_refinement` before `output`  
- Handoff: successful ideate includes `handoff` (best candidate, prompt_steer, direction essentials, next_agents)  
- Learned patterns: `GET /api/v1/creative/patterns` + ideate `learned_patterns` are **process-local only** (not durable memory)  
- Entry: `POST /api/v1/creative/ideate`, `GET /api/v1/creative/patterns`  
- Optional request field: `domain` (`video` | `scientific` | `artistic` | `business` | `engineering` | `educational`)  
