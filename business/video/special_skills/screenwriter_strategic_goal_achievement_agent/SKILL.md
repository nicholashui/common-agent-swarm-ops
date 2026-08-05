# Special skill integration — `screenwriter_strategic_goal_achievement_agent`

**Status:** Host offline foundation (2026-08-05)  
**Kind:** agent_family  
**Plan:** [`docs/plans/podcast_screen_radar_lqr_host_foundation.md`](../../../../docs/plans/podcast_screen_radar_lqr_host_foundation.md)  
**Summary:** Offline beat sheet + controlling idea + strategic milestones for screenwriting

## Host modules
- `backend/app/screenwriting/` · `/api/v1/screenwriting/*` · tool `screenwriting.plan`

## Runtime contract
- Fail-closed: not full live LLM multi-act screenplay generation  
- Entry: `POST /api/v1/screenwriting/plan`  
