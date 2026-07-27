# Video tools

## Local stub

| tool_id | Adapter | Notes |
|---------|---------|-------|
| `media.stub` | StubMediaAdapter | Deterministic local stub |

## Live media (production profile)

| tool_id | Provider | Credential env |
|---------|----------|----------------|
| `media.sora` | OpenAI Sora-compatible | `CASOPS_MEDIA_SORA_API_KEY` / `OPENAI_API_KEY` |
| `media.veo` | Google Veo / Generative Language | `CASOPS_MEDIA_VEO_API_KEY` / `GOOGLE_API_KEY` |
| `media.runway` | Runway | `CASOPS_MEDIA_RUNWAY_API_KEY` / `RUNWAY_API_KEY` |
| `media.elevenlabs` | ElevenLabs TTS | `CASOPS_MEDIA_ELEVENLABS_API_KEY` / `ELEVENLABS_API_KEY` |

Registered via `default_local_adapters()` → `default_live_media_adapters()`.
Network calls require `CASOPS_VIDEO_PRODUCTION_ENABLED` + pack `production/profile.json`.
