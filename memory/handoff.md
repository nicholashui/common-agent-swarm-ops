# Handoff

**As of:** 2026-07-26  
**State:** Frontend screens load from stored screen parameters (no component/page hardcoded fixtures).

## Latest work

### Screen parameters (no hardcode)

- `lib/projections/screen-parameters.ts` — central store for all landing views
- `useScreenParameters` + page bindings pass `view={...}` into every `*Home`
- Homes **require** `view` prop; no `view = LOCAL_*` defaults
- Chrome copy moved into `view.labels` via `L()` / `Lfmt()` (`screen-labels.ts`)
- Login copy in `login-landing.ts`; specials/registry/profile chrome stored
- Scripts: `scripts/dehardcode-homes.mjs`, `scripts/check-label-keys.mjs`
- Guard tests: `frontend-hardcode-scan.test.ts`, `no-hardcoded-screen-defaults.test.ts`, `screen-parameters.test.ts`


### Five-doc redesign alignment (prior)

Reviewed and updated function against:

1. `docs/backend_redesign/backend_redesign.md`
2. `docs/frontend_redesign/frontend_redesign.md`
3. `docs/adoption_redesign/adoption_redesign.md`
4. `docs/migration_redesign/migration_redesign.md`
5. `docs/special_agents_redesign/agents/*.md` (19)

**Gates:** `five-doc-alignment.test.ts`, `three-doc-alignment.test.ts`, `migration-alignment.test.ts`, `specials-alignment.test.tsx` — focused suite green.

### Special agents (doc 5)

- Backend pack already complete: 19 draft `business/specials` agents, schema, source-records, validator tests (pass).
- Frontend: `lib/specials/specials-catalog.ts`, `SpecialsCatalog` mounted on Registry Hub, fail-closed draft/non-active.
- `business/specials/README.md` maps docs → agent IDs.
- Specs remain data-only: no tools, no network, no production activation.

### Prior (docs 1–4)

- Idempotency-Key on PublicApiTransport + OperatorConsole
- SSE factory `/api/v1/events/stream` + Last-Event-ID resume
- Domain pack extension slots
- Video migration PROPOSED claim + blueprints honesty

## Deferred (not frontend-completable)

- Backend OpenAPI: SSE stream, aggregate projections, generic artifact APIs (vs `/api/v1/video/*`)
- Video migration M0–M7 pack completion
- Wire live projections into every `*Home` landing
- Specials: substantive runtime (intentionally out of scope until draft → approved)

## Resume here

1. Commit uncommitted redesign + five-doc alignment when ready.
2. Flip migration claim to complete only with standalone evidence.
3. Mount pack UI extensions when host returns extension metadata.
