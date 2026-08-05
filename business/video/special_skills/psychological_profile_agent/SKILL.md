# Special skill integration — `psychological_profile_agent`

**Status:** Host offline foundation (2026-08-05)  
**Kind:** agent_family  
**Plan:** [`docs/plans/psychology_coding_skills_catalog_host_foundation.md`](../../../../docs/plans/psychology_coding_skills_catalog_host_foundation.md)  
**Summary:** Offline audience cohort, emotional arc, retention levers, hook recommendations

## Host modules
- `backend/app/psychology/`  
- `backend/app/api/v1/psychology.py`  
- Tools: `psychology.profile`, `psychology.recommend`  

## Runtime contract
- Fail-closed: not clinical; no live panels  
- Entry: `POST /api/v1/psychology/profile`, `/recommend`  
