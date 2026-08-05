# Special skill integration — `research_agent`

**Status:** Host offline foundation (2026-08-05)  
**Kind:** agent_family  
**Plan:** [`docs/plans/knowledge_research_thinking_host_foundation.md`](../../../../docs/plans/knowledge_research_thinking_host_foundation.md)  
**Summary:** Offline research plan→route→RAG gather→synthesize→critic

## Host modules
- `backend/app/research/`  
- `backend/app/api/v1/research.py`  
- Tool: `research.query`  
- Depends on offline RAG + knowledge router  

## Runtime contract
- Fail-closed: no Tavily / live web  
- Entry: `POST /api/v1/research/query`  
