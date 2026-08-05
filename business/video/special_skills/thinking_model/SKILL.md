# Special skill integration — `thinking_model`

**Status:** Host offline foundation (2026-08-05)  
**Kind:** host_loop_pattern  
**Plan:** [`docs/plans/knowledge_research_thinking_host_foundation.md`](../../../../docs/plans/knowledge_research_thinking_host_foundation.md)  
**Summary:** Ranked thinking models configure agent-loop cognitive intensity

## Host modules
- `backend/app/thinking/` — catalog + recommend  
- `backend/app/api/v1/thinking.py`  
- Tool: `thinking.recommend`  
- Wired into `AgentLoopService` v3 defaults  

## Runtime contract
- Offline catalog hooks only (not live 40-model LLM metacognition)  
- Entry: `POST /api/v1/thinking/recommend`  
