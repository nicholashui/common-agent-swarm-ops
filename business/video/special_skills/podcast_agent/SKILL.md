# Special skill integration — `podcast_agent`

**Status:** Host offline foundation (2026-08-05)  
**Kind:** agent_family  
**Plan:** [`docs/plans/podcast_screen_radar_lqr_host_foundation.md`](../../../../docs/plans/podcast_screen_radar_lqr_host_foundation.md)  
**Summary:** Offline episode outline, VO/sound plan; live TTS fail-closed

## Host modules
- `backend/app/podcast/` · `/api/v1/podcast/*` · tool `podcast.outline`

## Runtime contract
- Fail-closed: no live ElevenLabs/TTS on this surface  
- Entry: `POST /api/v1/podcast/outline`  
