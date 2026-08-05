# Podcast · Screenwriting · Tech Radar · LQR Host foundation (offline)

**Date:** 2026-08-05

## Implemented

| Surface | API | Module |
|---------|-----|--------|
| Podcast outline | `/api/v1/podcast/*` | `backend/app/podcast/` |
| Screenwriting beats | `/api/v1/screenwriting/*` | `backend/app/screenwriting/` |
| Gen-video tech radar | `/api/v1/tech-radar/*` | `backend/app/tech_radar/` |
| LQR overview (archetype E) | `/api/v1/lqr/*` | `backend/app/lqr/` |

Tools: `podcast.outline`, `screenwriting.plan`, `tech_radar.advise`, `lqr.overview`  
Skills catalog + golden harness updated.

## Fail-closed

- No live TTS/ElevenLabs on podcast foundation  
- No full LLM screenplay generation  
- Live media providers stay gated; radar prefers `media.stub` offline  
- LQR is overview scaffold, not full 14-shot MCTS  

## Still missing (production)

- Live podcast production path  
- Full MCTS LQR shot loop  
- Complete Kling/DCC wiring  
