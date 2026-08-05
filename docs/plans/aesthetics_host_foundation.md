# Aesthetics Host foundation (offline)

**Spec:** `va-agent-swarm/study/aesthetics_agent_functional_specification.md`  
**Date:** 2026-08-05  

## Implemented

### Slice 1 — core offline Critic/Aligner/Taste-Keeper
| Surface | Path |
|---------|------|
| Critic (deterministic multi-head D1–D10) | `backend/app/aesthetics/critic.py` |
| Aligner (critique, reward, prefs, prompt steers) | `backend/app/aesthetics/aligner.py` |
| Taste-Keeper (profiles + neutral baseline) | `backend/app/aesthetics/taste_keeper.py` |
| Facade | `backend/app/aesthetics/service.py` |
| API | `GET/POST /api/v1/aesthetics/*` |
| Tests | `backend/tests/unit/api/test_aesthetics.py` |

### Slice 2 — integration foundation
| Surface | Path |
|---------|------|
| Aesthetic critique bus (`aesthetic_feedback`) | `backend/app/aesthetics/bus.py` |
| Project episodic memory (accept/reject) | `backend/app/aesthetics/memory.py` |
| Handoff `qc_status` attach (`aesthetic_pass` / `review` / `fail` / `pending_human`) | `backend/app/aesthetics/handoff.py` |
| Consumer adapters (DoP, colorist, prompt eng, …) | `backend/app/aesthetics/consumers.py` |
| Pack prompt + L2 rubric content | `business/specials/agents/specials.aesthetics-agent/prompts|rubrics` |
| Frontend client | `frontend/src/lib/api/product-aesthetics.ts` |

### Slice 3 — offline completeness
| Surface | Path |
|---------|------|
| Verdict Markdown (§7.2) | `backend/app/aesthetics/verdict_md.py` |
| Constraints soft-nudge on Critic | `critic.py` |
| Compare → real preference pairs | `aligner.preference_pairs_from_ranking` |
| Profile compose (brand ⊕ genre) | `POST /aesthetics/profiles/compose` |
| Memory accept/reject → profile ratchet | `taste_keeper.ratchet` + `record_decision` |
| Refine ≤3 iteration scaffold | `service.refine` |
| Extra consumers (food/travel/RE) | `consumers.py` |
| Host tools `aesthetics.evaluate` / `.compare` | `tool_activation.py` (STUB_TOOL_IDS) |
| FE compare / policy / handoff | `product-aesthetics.ts` |

**Modes:** `screen`, `score`, `align`, `compare`, `refine`  
**Fail-closed:** `allow_live_vision=true` → 403/denied; no network multimodal.

## Explicitly still missing (production scope)

- Live SigLIP / CLIP / VLM vision backbones  
- Real detector zoo (ΔE, flow, FID/FVD, VBench)  
- DPO / RLHF / ReFL training loops (only preference-pair scaffold)  
- Redis Streams critique-bus (in-process bus only)  
- GPU latency SLOs & autoscale  
- Consent registry / C2PA-signed profiles  
- Pack agent leave `draft` / non-empty production tools  
- Full consumer wiring inside each video agent runtime loop  

Pack `specials.aesthetics-agent` remains **draft** for activation; Host API is the executable foundation.
