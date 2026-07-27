# Special skill integration — `podcast_agent`

**Status:** MVP integrated (2026-07-13)  
**Kind:** agent_family  
**Plan:** [`planning/special/podcast_agent.md`](../../../planning/special/podcast_agent.md)  
**Summary:** Podcast/audio vertical via voice/sound agents + avatar DNA

## Host binding

### Agents
- `video.voiceover` — SPEC 116.4KB, ALC=yes [OK]
- `video.sounddesign` — SPEC 121.3KB, ALC=yes [OK]
- `video.soundmixer` — SPEC 161.4KB, ALC=yes [OK]
- `video.composer` — SPEC 198.6KB, ALC=yes [OK]

### Workflow DNA
- `wf_video_arch_h_ai_avatar_v1` — steps=7 depth=thin_stub_n3 [OK]

### Host modules
- _None_

## Runtime contract

- Entry agents: `video.orchestrator` / `video.planner` when DNA-bound.
- Tools: host allow-list only; design-time vendors stay in SPEC.
- Irreversible package/publish steps require human gate.
- No second control plane (N1).

Machine manifest: `integration.json`
