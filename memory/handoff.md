# Handoff

**As of:** 2026-07-26  
**State:** ui_00–ui_15 frontend redesign landings implemented; latest is ui_15 API portal.

## Latest work

### ui_15_api_portal (current)
- Presentation API portal matches `docs/frontend_redesign/ui_15_api_portal.md` + `.svg`.
- Files: `ApiPortalHome.tsx`, `api-portal-landing.ts`, `ApiPortalHome.test.tsx`, CSS.
- Route: `/developer/api` → `ApiPortalHome`.
- Covered: Docs/SDKs/Tokens/Webhooks/Extensibility nav, OpenAPI-style endpoint list, curl/Python/TS samples, Try it / OpenAPI, masked keys, webhooks + deliveries, VA adapter note, opaque-ID safety.
- Deferred: live OpenAPI embed, real token service, webhook delivery engine.

### Uncommitted (likely)
- ui_10 through ui_15.

## Resume here

1. Dogfood `/developer/api`.
2. Commit ui_10–ui_15 when ready.
3. Next: onboarding (ui_16), mobile (ui_17), …
