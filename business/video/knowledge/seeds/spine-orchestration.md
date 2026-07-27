# Video spine orchestration seed

**Provenance:** Wave 2 · `adoption.md` §5.1 · va `SYSTEM_REFERENCE.md` orchestration spine  
**Scope:** domain `video` · agents `video.orchestrator`, `video.planner`

## Rules

1. Every executable video process enters via **orchestrator** and/or **planner**.
2. Media generation in CI uses **stubs only** (`video_media_gen_stub`).
3. Package/publish steps require a **human gate**.
4. ALC: active agents must have agent-scoped memory + reflect hooks.

## Retrieval note

Index this seed for spine agents pre-act (Tier-0). Not a substitute for full 68-chapter corpus (later waves).
