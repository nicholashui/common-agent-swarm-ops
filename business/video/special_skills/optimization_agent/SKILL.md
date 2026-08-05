# Special skill integration — `optimization_agent`

**Status:** Host offline foundation (2026-08-05)  
**Kind:** agent_family  
**Plan:** [`docs/plans/intent_optimization_skill_evals_host_foundation.md`](../../../../docs/plans/intent_optimization_skill_evals_host_foundation.md)  
**Summary:** Offline prompt/cost/retention/eval optimization recommendations

## Host modules
- `backend/app/optimization/`  
- `backend/app/api/v1/optimization.py`  
- Tool: `optimization.recommend`  

## Runtime contract
- Fail-closed: no live ROAS training  
- Entry: `POST /api/v1/optimization/recommend`  
