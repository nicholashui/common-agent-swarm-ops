# Intent · Optimization · Skill Evals Host foundation (offline)

**Date:** 2026-08-05  
**Plan refs:** phase 3.3 (intent) + 3.4 (skill evals) + optimization skill packaging

## Implemented

| Surface | Path |
|---------|------|
| Intent DIA lite (6-phase scaffold) | `backend/app/intent/` + `/api/v1/intent/*` |
| Optimization recommend (prompt/cost/retention/eval) | `backend/app/optimization/` + `/api/v1/optimization/*` |
| Skill golden harness | `backend/app/skill_evals/` + `/api/v1/skill-evals/*` |
| Brief spine enrichment | `build_user_brief` attaches `intent_analysis` when safe |
| Host tools | `intent.analyze`, `optimization.recommend`, `skill_evals.run` |
| FE clients | `product-intent.ts`, `product-optimization.ts`, `product-skill-evals.ts` |

## Fail-closed

- Live LLM DIA denied  
- Live ROAS / training optimizers denied  
- Skill evals offline only (no LLM judge)

## Still missing (production)

- Full PIC / multi-agent ToM pragmatics  
- Online bandits / live ROAS  
- RAGAS-class LLM evaluation suite  
