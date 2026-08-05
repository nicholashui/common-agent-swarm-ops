# Special skill integration — `complex_problem_solution_process_model`

**Status:** Host offline foundation (2026-08-05)  
**Kind:** process_model  
**Plan:** [`docs/plans/creative_complex_strategic_llm_host_foundation.md`](../../../../docs/plans/creative_complex_strategic_llm_host_foundation.md)  
**Summary:** Offline decompose → options → gates → plan for planner/orchestrator

## Host modules
- `backend/app/complex_problem/`  
- `backend/app/api/v1/complex_problem.py`  
- Tool: `complex_problem.solve`  

## Runtime contract
- Fail-closed offline process scaffold  
- Entry: `POST /api/v1/complex-problem/solve`  
