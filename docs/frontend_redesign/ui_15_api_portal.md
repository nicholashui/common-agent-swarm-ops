# NN UI 15: API & Developer Portal Spec

**UI ID:** nn_ui_15_api_portal  
**Version:** 1.0 (Aligned to common-agent-swarm-ops v2.1)  
**Related Main Doc Section:** Ui15  
**Date:** 2026-07-18  
**Owner:** Nicholas / Frontend Team  
**Status:** Ready for implementation

## Purpose & Goals
Enable full programmatic control, automation, and extensibility while maintaining governance.

## Layout & Structure
Portal layout: Sidebar nav (Docs, SDKs, Tokens, Webhooks, Extensibility) + main content area.

## Key Components
- Interactive API Explorer (Swagger UI or similar, authenticated).
- Code Samples: Tabs for curl, Python (common-lib), TypeScript, with copy buttons. Context-aware (e.g., "Run this swarm from pattern").
- Token Management: Create scoped tokens, usage dashboard, revoke (same as profile but more prominent here).
- Webhook Config: Create/edit endpoints for events, secret, retry policy, delivery logs.
- Extensibility Docs: Guides for custom nodes/tools, runtime adapters (Moltbot, LangGraph, etc.), contribution process for new commons.

## Data & API
- OpenAPI spec serving.
- Token service.
- Webhook CRUD + delivery logs.
- Usage stats for tokens/webhooks.

## Interactions
- "Try it" in explorer uses current auth.
- Generate snippet button copies ready-to-run code.
- Webhook test button sends sample payload.

## Polish & Accessibility
Clean developer-focused design. Syntax highlighting in samples. Accessible explorer and forms. Bilingual docs where content allows.

## Wireframe Summary
Sidebar nav. Main: Explorer or samples with copy/generate buttons. Token and webhook management sections.

**Implementation Notes:** OpenAPI must be comprehensive and up-to-date. "Common lib" Python examples are high value for users. Webhook reliability important for integrations.