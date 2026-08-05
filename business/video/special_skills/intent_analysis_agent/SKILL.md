# Special skill integration — `intent_analysis_agent`

**Status:** Host offline foundation (2026-08-05)  
**Kind:** selection_binding  
**Plan:** [`docs/plans/intent_optimization_skill_evals_host_foundation.md`](../../../../docs/plans/intent_optimization_skill_evals_host_foundation.md)  
**Summary:** Offline DIA lite enriches UserBrief + archetype/scale hints

## Host modules
- `backend/app/intent/`  
- `backend/app/api/v1/intent.py`  
- Tool: `intent.analyze`  
- Wired into `build_user_brief` enrichment  

## Runtime contract
- Fail-closed: no live LLM DIA  
- Entry: `POST /api/v1/intent/analyze`  
