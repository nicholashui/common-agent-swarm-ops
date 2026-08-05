# Special skill integration — `knowledge_router_agent`

**Status:** Host offline foundation (2026-08-05)  
**Kind:** routing  
**Plan:** [`docs/plans/knowledge_research_thinking_host_foundation.md`](../../../../docs/plans/knowledge_research_thinking_host_foundation.md)  
**Summary:** Offline knowledge routing to memory/RAG/aesthetics/pack destinations

## Host modules
- `backend/app/knowledge/` — keyword hybrid-lite router  
- `backend/app/api/v1/knowledge.py` — `/api/v1/knowledge/*`  
- Tool: `knowledge.route`

## Runtime contract
- Fail-closed: no live web / embedding GNN  
- Entry: `POST /api/v1/knowledge/route`  
