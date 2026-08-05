# Special skill integration — `llm_usage`

**Status:** Host offline foundation (2026-08-05)  
**Kind:** host_infra  
**Plan:** [`docs/plans/creative_complex_strategic_llm_host_foundation.md`](../../../../docs/plans/creative_complex_strategic_llm_host_foundation.md)  
**Summary:** Offline token budget ledger + mode recommend (no live billing)

## Host modules
- `backend/app/llm_usage/`  
- `backend/app/api/v1/llm_usage.py`  
- Tool: `llm_usage.record`  

## Runtime contract
- Fail-closed: offline estimates only  
- Entry: `GET /api/v1/llm-usage/policy`, `POST /record`, `POST /recommend-mode`  
