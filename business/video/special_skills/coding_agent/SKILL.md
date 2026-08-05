# Special skill integration — `coding_agent`

**Status:** Host offline foundation (2026-08-05)  
**Kind:** host_infra  
**Plan:** [`docs/plans/psychology_coding_skills_catalog_host_foundation.md`](../../../../docs/plans/psychology_coding_skills_catalog_host_foundation.md)  
**Summary:** Offline engineering plan-only (touch points, steps, tests) — no shell/network exec

## Host modules
- `backend/app/coding/`  
- `backend/app/api/v1/coding.py`  
- Tool: `coding.plan`  

## Runtime contract
- Fail-closed: no arbitrary shell, remote installers, network  
- Entry: `POST /api/v1/coding/plan`  
