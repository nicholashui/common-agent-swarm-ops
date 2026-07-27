# Video production activation

Updated: 2026-07-27T02:01:23Z

## What was enabled

- Pack production profile: `production/profile.json` (`enabled: true`)
- DNA / pack graphs: `production_ready: true` under `workflows/`
- Media agents: `production_activation_requested: true` + live tool allow-lists
- Host adapters: `media.sora`, `media.veo`, `media.runway`, `media.elevenlabs`

## Required environment (host)

```bash
export CASOPS_VIDEO_PRODUCTION_ENABLED=true
export CASOPS_VIDEO_MEDIA_NETWORK=true
export CASOPS_MEDIA_SORA_API_KEY=...     # or OPENAI_API_KEY
export CASOPS_MEDIA_VEO_API_KEY=...      # or GOOGLE_API_KEY
export CASOPS_MEDIA_RUNWAY_API_KEY=...   # or RUNWAY_API_KEY
export CASOPS_MEDIA_ELEVENLABS_API_KEY=... # or ELEVENLABS_API_KEY
```

See `credentials.env.example`. **Never commit real secrets.**

## Behavior

| Condition | Result |
|-----------|--------|
| Profile off or env off | Media adapters return `media_production_disabled` |
| Missing API key | `media_credentials_not_configured` |
| Enabled + key + network | Host POSTs to provider endpoint |

## Safety

- Credentials only from environment (or injected secret source in tests).
- Endpoints must be https (or localhost http for mocks).
- Inventory allows production agent fields only while profile.enabled is true.
