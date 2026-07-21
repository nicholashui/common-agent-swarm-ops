# Design Document: Frontend Redesign

## Overview

Frontend_Redesign will evolve `frontend/` from its current strict TypeScript/Next.js 14.2.30 demonstration shell into a governed control-plane client. It is a presentation, observation, and command-intent layer only: Backend_Redesign remains the sole authority for identity, tenant selection, authorization, policy, governance, execution, evidence, recovery, content safety, and external navigation authority.

The design consumes only generated or schema-checked `/api/v1` contracts and authorized `/api/v1/events/stream` SSE. It never copies backend DTOs, interprets a missing field, synthesizes an action/evidence reference, fetches an untrusted URL, or treats an SSE connection as evidence of operational health. Current source findings informing this design are: the existing app has App Router entry points and a strict `tsconfig`; all 21 `ui_*.md`/`.svg` baselines exist; and the binding frontend supplement replaces the older WebSocket-first and direct-browser-import guidance with REST plus authorized SSE. Sources: [frontend package](../../../frontend/package.json), [approved frontend supplement](../../../docs/frontend_redesign/frontend_redesign.md), [VA mapping](../../../docs/frontend_redesign/va_agent_structure_mapping.md), and [backend redesign spec](../backend-redesign/requirements.md).

**Decisions and rationale.** Use Next.js App Router server components for static shell/layout and client components only where interaction, browser storage, SSE, clipboard, focus handling, or commands are required. Use a generated client behind a single transport adapter, making contract drift a build failure. Keep projections in memory by default, with explicitly allowlisted session-safe persistence only for resumable views. Treat the approved screen documents as a checked manifest, not informal design inspiration. Keep query/cache, graph, and component libraries replaceable behind small adapters; implementation may add pinned dependencies only after the generated contract and visual-baseline test approach are approved.

**Requirements trace.** Contract and projection boundaries address 1–2; the command runtime addresses 3; live synchronization and freshness address 4–5; screen renderers address 6–10 and 12; deterministic verification addresses 11. This design preserves the approved requirements as the source of truth.

## Architecture

```mermaid
flowchart LR
  U[Authenticated browser session\nHTTP-only same-site cookie] --> N[Next.js App Router shell]
  N --> G[Generated Client + Transport Adapter]
  G -->|versioned REST only| API[Backend_Redesign /api/v1]
  N --> L[Live Projection Controller]
  L -->|authorized SSE only| SSE[/api/v1/events/stream]
  API --> P[Authorized redacted projections\nAction/Evidence references]
  SSE --> E[Typed redacted operational events]
  P --> R[Projection renderer + session-safe store]
  E --> L
  R --> U
```

The deployment is same-origin: Next.js proxies `/api/v1/**` and the event stream to Backend_Redesign without reshaping bodies, adding authority fields, or exposing backend host details. The session is an HTTP-only, Secure, SameSite cookie managed by the authorized identity/session implementation; no access token is readable or persisted by browser code. Production response policy sets CSP that blocks unsafe script/eval and unapproved frames, `frame-ancestors 'none'`, `base-uri 'self'`, `object-src 'none'`, `Referrer-Policy: no-referrer`, HSTS, and `X-Content-Type-Options: nosniff`. CSP connect sources are the same-origin API only. The implementation validates this policy without embedding credentials in source.

A server-rendered `AuthenticatedShell` supplies navigation, skip link, status/live-region host, and responsive layout. A `SessionBoundary` observes only server-provided session lifecycle signals; on end, actor change, or organization change it aborts streams, clears query/memory/session-safe caches and command UI state, then prevents projection rendering until a new authorized projection arrives. It does not accept a browser-selected organization or actor.

```mermaid
sequenceDiagram
  participant V as View
  participant C as Generated client
  participant L as Live controller
  participant B as Backend_Redesign
  V->>C: generated read operation
  C->>B: /api/v1 projection request
  B-->>C: Public_Envelope(data, sequence context)
  C-->>L: validated REST snapshot
  L->>B: authorized SSE subscription from returned context
  B-->>L: redacted typed event
  alt exact scope/schema/expected sequence
    L-->>V: replace allowed incremental state; save cursor
  else duplicate, gap, denial, expiry, incompatible schema
    L-->>V: Reconnecting or Stale; discard affected incremental state
    L->>C: reload snapshot, then create a new subscription
  end
```

No Next.js route handler is a second business API. If a route handler is required for same-origin streaming/proxy mechanics, it forwards only the generated contract request and response, preserves `Cache-Control: no-store` for session-bound data, and cannot choose a tenant, emit an invented projection, or make a command on the user’s behalf.

## Components and Interfaces

### Generated contract boundary

`src/lib/api/generated/` is the committed output of a pinned OpenAPI generation/schema-check command against `/api/v1/openapi.json`; `src/lib/api/client.ts` is the only import surface for request functions. A CI command regenerates to a temporary directory and byte-compares the result (or schema-checks an approved generated artifact), runs `tsc --noEmit`, and fails on any difference. Application code imports generated request/response types and operations; it does not define hand-written server DTO interfaces, invoke unversioned URLs, or call `fetch` for Public_API operations.

`PublicApiTransport` converts generated calls into `Result<GeneratedSuccess, PublicApiError>`: success maps only `envelope.data` and `meta.correlation_id`; error maps only code, redaction-safe message, retryability, returned retry-after, correlation identifier, and returned action reference. It deliberately has no fallback parser, error-string inspection, optimistic terminal success, or authority injection. Read retry is bounded and transport-level only; mutations never receive an automatic retry.

`ProjectionMapper` maps known generated fields into small view models and uses presence checks rather than defaults. Each screen renderer receives only its mapper output. A missing protected field removes its label, value, placeholder, control, DOM/accessibility-tree node, cache entry, and any derived presentation; generic object dumps are prohibited. `ReferenceLink` resolves an `Opaque_Reference` via its generated read operation. `ActionControl` and `EvidenceLink` require returned generated `Action_Reference` and `Evidence_Reference` inputs respectively; no ID, URL, label, eligibility, or evidence display is assembled by the client.

### Command runtime

`CommandCoordinator` accepts a returned eligible `Action_Reference`, generated request payload, and a user gesture. It creates `crypto.randomUUID()` exactly once for that `Command_Intent`, records the key before the first request, sends it as `Idempotency-Key` on every submission/reconciliation, and keys its reducer by the action reference plus idempotency identity. The initiating control remains disabled in `submitting`, `queued`, or `reconciling`; a reducer guard also rejects programmatic invocation during these states. A queued response creates only a pending reference. A terminal completion is rendered only from a returned terminal projection/event outcome.

For ambiguous transport, cancellation, retry exhaustion, rate-limit, authorization, policy, approval, or manual-recovery results, the coordinator retains the sole key and transitions to a typed status. Reconciliation uses the same generated command/status or resource read with the same key. Rate limits display the returned message and countdown but never resubmit. Denials display only the returned redaction-safe error and optional returned next action. Manual-recovery displays only returned recovery summary, correlation identifier, and escalation action. `CopyCorrelationIdentifierButton` copies only the server-returned identifier and has the exact accessible name `Copy correlation identifier`.

### Live projection and presentation components

`LiveProjectionController` owns one subscription state machine per returned resource/subscription scope: `loadingSnapshot → subscribing → live`, plus `reconnecting`, `stale`, and `resynchronizing`. It first obtains a REST snapshot and expected sequence; then it requests the narrow, server-authorized topic set and subscription context provided by the contract. It applies an event only if generated schema validation succeeds and its resource scope, schema version, and sequence exactly equal the expected value. An accepted event updates only its declared projection slice, advances the expected sequence, and stores its event ID/cursor. Duplicate, out-of-order, gapped, expired, bounded, denied, or schema-incompatible events are ignored and trigger one serialized resynchronization: discard affected incremental state and cursor, load REST, replace state, establish the returned sequence context, then create a new subscription. SSE connection state never implies execution, approval, quality, rights, provenance, or recovery state.

`ProjectionStatus` always renders returned `as_of`, freshness, degraded state, and the exact returned operational label. It pairs the label with an icon named `Status: <returned state label>` and uses text/pattern/icon rather than color alone. It renders `Stale`, not `Live`, while stale. `ActionControl` disables and blocks every returned freshness-critical or irreversible action when its projection is stale; returned refresh/reconnect actions remain available. `OperationalAnnouncer` emits exactly one polite, atomic announcement per distinct returned resource state transition: `<resource name>: <returned state label>; updated <as_of>`.

`SafeContent` renders user input, artifacts, imports, events, tool summaries, and model text exclusively as React text nodes or parsed structured fields; it never uses `dangerouslySetInnerHTML`, dynamic evaluation, inline event attributes, embedded remote resources, or external content preview. External import inputs are inert strings sent only through the generated ingestion operation. The URL is never passed to `fetch`, XHR, EventSource, WebSocket, `window.open`, router navigation, image/iframe/script/style elements, or prefetch. `ExternalNavigationControl` navigates only after it receives a returned `Allowed_Action_Contract`; it uses the exact allowed destination and safe `noopener noreferrer` behavior when opening a new context.

`AccessibleDialog` moves focus to its heading, traps focus while open, and returns focus to the invoker on close. Text-labelled controls use their visible text as their accessible name. Icon controls expose only the mandated names: `Refresh operational projection`, `Reconnect live updates`, `Copy correlation identifier`, and `Close`. CSS tokens enforce a visible 2px outline with 2px offset; action controls enforce a 44×44 CSS-pixel minimum target at 320–767px. Desktop and mobile receive the same returned status, freshness, recovery, approval, evidence, and action data; mobile changes layout and interaction density, never authorization or information entitlement.

### Screen composition and approved inventory

A typed `ScreenDefinition` manifest links each approved UI ID to its route or shell component, required generated capability key, deterministic projection fixture, Markdown behavior baseline, SVG baseline, and required viewport list. `ScreenBoundary` preserves the shell and context while a generated capability is unavailable, rendering only an unavailable-data/error state and never placeholder protected fields. It gates Settings, API portal/developer, collaboration, costs, and blueprints on an authorized generated capability. Each component is built from shared `ProjectionStatus`, `ActionControl`, `EvidenceLink`, `SafeContent`, `UnavailableState`, and responsive primitives, then adds only screen-specific visual composition from its baseline.

| UI ID | Route or shell component | Authorized projection focus |
|---|---|---|
| `ui_00_menu` | `AuthenticatedShell` | global navigation and returned navigation actions |
| `ui_01_login` | `/login` | authorized session entry only |
| `ui_02_dashboard` | `/` | health, fleet, backlog, approval, common-version impact |
| `ui_03_swarm_composer` | `/composer` | pattern discovery and authorized composition intents |
| `ui_04_canvas` | `/swarms/[swarmId]/canvas` (legacy `/canvas` redirects) | graph revision, tasks, validation, runs |
| `ui_05_agent_detail` | `/registry/agents/[agentId]` | common agent version, evaluation, usage, evidence |
| `ui_06_activity` | `/activity` | run/task timelines and redacted events |
| `ui_07_registry_hub` | `/registry` | common agent/pattern discovery and filters |
| `ui_08_settings` | `/settings` | authorized settings projections/actions only |
| `ui_09_monitoring` | `/operations` | health, alerts, freshness, recovery |
| `ui_10_knowledge` | `/knowledge` | ingestion requirements and import projections |
| `ui_11_eval` | `/evaluations` | evaluation and quality evidence |
| `ui_12_notifications` | `/notifications` | returned notifications and actions |
| `ui_13_profile` | `/profile` | authorized actor profile projection |
| `ui_14_audit` | `/audit` | redacted audit/provenance references |
| `ui_15_api_portal` | `/developer/api` | authorized developer/API projections only |
| `ui_16_onboarding` | `/onboarding` | authorized onboarding state/actions |
| `ui_17_mobile` | `/mobile` plus responsive `AuthenticatedShell` | mobile operations companion |
| `ui_18_collaboration` | `/collaboration` | authorized collaboration projection only |
| `ui_19_costs` | `/costs` | authorized cost/budget projections only |
| `ui_20_blueprints` | `/blueprints` | authorized common pattern/blueprint projections only |

The graph adapter isolates the selected graph library from generated projections. It renders data-flow, state-flow, and iteration edges with distinct line styles, labels, and markers; displays immutable common versions/provenance and custom fork reason; and uses returned task lifecycle/detail, validation categories, and eligibility only. Graph mutation, run, retry, skip, cancel, replay, escalation, rollout, and VA actions all pass through `CommandCoordinator`. Canvas status remains observational; invalid validation, stale data, or absent action reference prevents invocation.

VA renderers are conditional adapters over the generic contracts: when `VA_Projection` exists they display returned template/phase, agent contract, graph/task, artifacts, critique, separate L1/L2/L3/gate/human evidence, rights/consent, delivery, provenance, and block reasons. When absent they render the generic graph/governance/provenance projection without VA-shaped placeholders. Artifact delivery is shown blocked when the returned projection reports a missing delivery field or gate. No VA action constructs a tool request, approval decision, rollout instruction, or provenance signature.

## Data Models

The authoritative wire shapes are generated from OpenAPI; the following are frontend-owned state models, not duplicated backend DTOs:

```ts
interface CommandRecord {
  readonly actionReferenceId: string;
  readonly idempotencyIdentity: string;
  readonly status: "submitting" | "queued" | "reconciling" | "rate_limited" | "denied" | "manual_recovery" | "terminal";
  readonly correlationIdentifier?: string;
  readonly retryAfterSeconds?: number;
  readonly pendingReference?: string;
}

interface LiveProjectionState<TProjection> {
  readonly projection: TProjection;
  readonly subscriptionScope: string;
  readonly expectedSequence: number;
  readonly eventCursor?: string;
  readonly connection: "loadingSnapshot" | "subscribing" | "live" | "reconnecting" | "stale" | "resynchronizing";
}

interface SessionSafeCacheRecord<TProjection> {
  readonly schemaVersion: string;
  readonly projection: TProjection;
  readonly eventCursor?: string;
  readonly savedAt: string;
}

interface ScreenDefinition {
  readonly uiId: string;
  readonly routeOrShell: string;
  readonly behaviorBaseline: string;
  readonly svgBaseline: string;
  readonly fixtureId: string;
  readonly viewports: readonly { readonly width: number; readonly height: number }[];
}
```

`CommandRecord` is in-memory and may be held in a session-safe recovery store only while it contains no credential, token, protected/raw content, or privileged artifact data. Its idempotency value is never regenerated until a terminal outcome or explicit server-authorized abandonment. `LiveProjectionState` is isolated by returned scope and resource; reducer updates are immutable, sequence guarded, and discarded on resynchronization. `SessionSafeCacheRecord` is allowlisted per generated projection and stores only render-required returned fields plus cursor; cache keys are scoped to the current session lifecycle and are erased before any actor/organization transition renders. It must never be placed in local storage, session storage, IndexedDB, or Cache Storage if it contains a token, credential, protected field, raw protected value, or privileged artifact content.

Filters, sorting, pagination, form fields, and command payloads use generated request schemas. The browser may perform non-authoritative usability validation (required format, type/size hint, inline correction) but sends exactly generated filter/content/reference values and never claims validation, authorization, scan, policy, approval, or command eligibility. All failed/error states retain only returned redaction-safe message, code, retryability, correlation ID, and returned reference/action where present.

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties bridge human-readable specifications and machine-verifiable correctness guarantees.*

**Property reflection.** The prework identifies overlapping mapper, command, live-stream, renderer, accessibility, and cache invariants. Properties 1–2 consolidate related envelope/redaction/reference requirements; properties 3–4 separate command identity from outcome rendering; properties 5–7 separate snapshot ordering, contiguous update, and recovery; properties 8–15 each cover a non-overlapping presentation/security domain. The separate properties are necessary because passing a command key invariant does not prove terminal semantics, applying a contiguous event does not prove resynchronization, and safe rendering does not prove cache or browser-navigation safety. Criteria classified as example, integration, or smoke remain in the deterministic test strategy rather than being forced into unsuitable property tests.

### Property 1: Envelope mapping is schema-bounded and redaction-safe

For any generated successful or error Public_Envelope, mapping it to frontend state exposes only successful `data` and correlation fields on success, or only returned code, redaction-safe message, retryability, retry-after, correlation identifier, and returned action reference on error; no unknown or sensitive sentinel field is retained.

**Validates: Requirements 1.4, 1.5**

### Property 2: Authorized projection rendering has no client-created data or authority

For any Authorized_Projection with any subset of absent protected fields and any returned action/evidence references, rendered text, DOM/accessibility nodes, action payloads, and session-safe cache contain only present authorized fields and one-to-one returned references; absent, unknown, or sensitive fields produce no fallback, inferred state, control, evidence, or persisted value.

**Validates: Requirements 2.2, 2.3, 2.4, 2.7, 2.8, 2.9**

### Property 3: A command intent has one durable idempotency identity and one pending-control owner

For any authorized action and any sequence of duplicate submissions, ambiguous transport outcomes, denial/rate-limit outcomes, retries, and reconciliations for one Command_Intent, every transport call carries the first identity allocated before submission, and the initiating control remains blocked while the intent is submitting, queued, or reconciling.

**Validates: Requirements 3.1, 3.2, 3.3, 3.5, 3.6, 3.11**

### Property 4: Command outcomes are truthfully classified

For any command outcome sequence, a reconciliation projection replaces the pending state; rate limits display the returned delay without automatic submission; denials expose only returned safe error/action values; and completion occurs if and only if a returned Terminal_Outcome is received.

**Validates: Requirements 3.7, 3.8, 3.9, 3.12**

### Property 5: Live observation begins from an authorized snapshot and scope

For any resource scope and server-authorized topic set, the live controller does not apply an event before a REST snapshot establishes expected sequence context, and its subscription request contains no topic or scope absent from the returned authorization context.

**Validates: Requirements 4.1, 4.2**

### Property 6: Only the exact next authorized event mutates a live projection

For any live projection state and sequence of events, an event changes incremental state only when its resource scope and generated schema version match and its sequence equals Expected_Event_Sequence; every accepted event advances the sequence by one and records exactly that event cursor, while connection changes alone alter no governed projection fact.

**Validates: Requirements 4.3, 4.4, 4.10, 4.11**

### Property 7: Unsafe replay causes replacement resynchronization

For any cached incremental state and any duplicate, out-of-order, gapped, bounded, expired, denied, or schema-incompatible replay outcome, the controller stops incremental application, discards the affected incremental state and cursor, and replaces the view with the subsequent returned REST snapshot and its sequence context.

**Validates: Requirements 4.6, 4.7, 4.8**

### Property 8: Freshness presentation is exact and safely gates actions

For any health, aggregate, canvas, approval, rollout, or alert projection, the UI renders returned `as_of`, freshness, degraded state, redacted summary/reference, and exact textual status with accessible icon name; a stale projection renders `Stale`, permits a returned refresh/reconnect reference only when supplied, and blocks every returned freshness-critical or irreversible action.

**Validates: Requirements 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 6.15, 7.4**

### Property 9: Common registry, activity, and graph metadata preserve returned provenance

For any returned common-version, filter, run, task, event, graph validation category, or eligible recovery-action projection, the UI submits only generated filter values and renders only returned immutable version, provenance, lifecycle/dependency/recovery detail, redacted event summary/correlation, validation category, and corresponding action reference.

**Validates: Requirements 6.2, 6.3, 6.5, 6.6, 6.7, 6.13, 6.16**

### Property 10: Graph rendering preserves semantic structure and execution eligibility

For any graph with common/custom nodes, task projections, relationship types, and validation result, common nodes expose returned immutable version/provenance, custom nodes expose returned origin/reason, task nodes expose the exact returned lifecycle/detail, relationship semantics have a non-color distinction, and an ineligible graph never permits its returned run control to invoke a command.

**Validates: Requirements 6.8, 6.9, 6.10, 6.11, 6.12**

### Property 11: Approval and rollout UI remains evidence-bound

For any approval, quality-evidence, or rollout projection, the UI presents only returned gate/rollout values and action references, keeps L1/L2/L3/critique/gate/human evidence distinct, requires a refreshed matching evidence revision before a decision is enabled, and never creates a rollout or governance action not returned by the server.

**Validates: Requirements 7.1, 7.2, 7.3, 7.5, 7.6**

### Property 12: Artifact and import content is inert and non-authoritative

For any ingestion requirements, import projection, external URL, or hostile Untrusted_Content value, the UI renders only returned type/size/owner/retention, opaque references, and redacted result fields; the URL/content invokes no browser network, navigation, embed, script, event-handler, dynamic evaluation, tool, route, approval, or command authority sink.

**Validates: Requirements 8.1, 8.4, 8.6, 8.7, 8.8**

### Property 13: VA adapters add returned domain information without inventing state

For any VA_Projection, the adapter renders only returned template/phase, agent contract, task, artifact, critique, and distinct quality fields; for any artifact missing a required delivery field or approval it renders delivery as blocked.

**Validates: Requirements 9.1, 9.2, 9.3, 9.4, 9.5, 9.9**

### Property 14: Accessible semantic information survives labels, transitions, and mobile layout

For any text-labelled control, returned operational state transition, authorized projection, and supported mobile viewport, visible control text equals its accessible name, a distinct returned state produces exactly one required live announcement and textual state label, and normalized returned status/freshness/recovery/approval/evidence/action information is equivalent between desktop and mobile renderings.

**Validates: Requirements 10.1, 10.6, 10.7, 10.8**

### Property 15: Browser persistence and external navigation are capability-safe

For any authorized projection/cache candidate, session transition, and external destination candidate, persistence contains only allowlisted session-safe projection fields/cursor and never protected/token/credential/raw/privileged values, and navigation occurs if and only if a returned Allowed_Action_Contract authorizes it.

**Validates: Requirements 10.10, 10.12, 10.13**

## Error Handling

All failures flow through typed `Result` values and generated error schemas; components do not parse free-form errors or inspect hidden HTTP/body details. The UI records correlation identifiers only when returned, makes them copyable through the mandated control, and logs client diagnostics without response bodies, credentials, tokens, raw content, or protected fields.

| Condition | State transition and user-visible behavior | Safety rule |
|---|---|---|
| Initial projection unavailable | `UnavailableState` retains screen shell/context and shows returned safe error with returned retry/reference if any | Do not render unavailable/missing fields or infer resource state. |
| Read transport failure | Bounded read retry then reconnecting/stale state; offer only returned refresh/reconnect action | Never retry a mutation through generic network retry. |
| Queued command | `queued` with returned pending resource/run reference | Do not claim completion or fabricate progress. |
| Ambiguous mutation | `reconciling` with retained key and generated reconciliation read | Never allocate a second key or duplicate command. |
| Rate limit | `rate_limited` with returned safe message/countdown | No automatic resubmission. |
| Authorization, policy, or approval denial | `denied` with returned safe error and optional returned next action | No existence/visibility inference or client bypass. |
| Manual recovery/dead letter | `manual_recovery` with returned failure summary, correlation and escalation action | Recovery is a new returned governed action only. |
| SSE disconnect | `reconnecting`, then `stale` if current state cannot be re-established | Connection status is not operational state. |
| Replay anomaly or schema mismatch | serialized `resynchronizing` flow | Drop affected incrementals/cursor before REST replacement; do not apply later events first. |
| Unsafe import/content | inline non-authoritative correction or returned ingestion result | Keep input inert; no browser-side external loading. |
| Session actor/organization change | abort controllers, clear caches/state, reset shell boundary | Clear before another projection renders. |

The error boundary must be screen-local where possible so an unavailable detail panel does not erase previously authorized navigation or a separate projection. It receives a sanitized error view model only. All user-facing timing uses `Retry-After` returned by Public_API; retry timing, exponential backoff, and fetch implementation remain internal bounded transport details and never imply authority.

## Testing Strategy

Testing uses three complementary layers. Pure mappers, reducers, sanitizers, cache allowlists, and capability gates have unit/property coverage; browser interactions, focus, EventSource sequencing, and component composition have deterministic integration coverage; full screen manifests, baseline layout, generated-client drift, and build guarantees run in CI. No test uses a real backend, identity provider, browser external URL, or production session.

**Contract and fixture discipline.** Store versioned OpenAPI fixtures, generated-client output, and redacted Public_Envelope fixtures under `frontend/src/test/fixtures/`. Test adapters use a generated-client fake—not hand-written endpoint DTOs—and fixed REST/SSE traces with deterministic clocks/UUID injection. Contract CI regenerates/schema-checks the client from the fixture, byte-compares committed output, then type-checks. A source-level guard fails direct `fetch`/unversioned API invocations outside the transport/proxy module, forbidden liveness/readiness use, `dangerouslySetInnerHTML`, dynamic evaluation, arbitrary `window.open`, and prohibited browser persistence writes.

**Property tests.** Use the maintained `fast-check` library, pinned to an exact lockfile-resolved version when implementation dependencies are approved. Implement exactly one property-based test per Property 1–15, each with at least 100 runs and a preceding traceability comment in this exact form: `Feature: frontend-redesign, Property N: <property title>`. Generators must include omitted-field/sensitive sentinels, Unicode/hostile strings, zero/large retry delays, arbitrary action/evidence subsets, all lifecycle/import/status unions, noncontiguous event traces, session transitions, and mobile widths 320–767. Browser side effects use injected spies/fakes so PBT proves application logic without network activity.

**Unit and integration tests.** Table-driven tests cover exact lifecycle/import labels, queued/manual-recovery/criterion-failure states, all mandated icon names, focus CSS tokens, and safe form feedback. DOM/browser tests cover dialog focus trap/restoration, clipboard contents, stale action blocking, no URL sinks, session-clear-before-render ordering, SSE snapshot/subscription/resynchronization ordering, and generated operation usage. Accessibility checks assert semantic roles, accessible names, textual state independent of color, focus visibility, live-region exact-once announcements, and 44×44px targets. Integration fixtures explicitly cover every Requirement 11 scenario: duplicate click, queued command, ambiguous transport, rate limit, authorization/policy/approval denial, cancellation, retry exhaustion, manual recovery, connection/replay variants, ingress states, redaction, untrusted content, and named projection views.

**Screen inventory and visual conformance.** The `ScreenDefinition` manifest is the single test input for Requirement 12. A manifest verifier produces exactly 21 results, each including the UI ID, checked `docs/frontend_redesign/ui_*.md`, matching `.svg`, route/shell module, deterministic fixture, and every viewport explicitly specified by that screen document (with 320–767 coverage for operations views). For each result, browser tests assert required semantic regions/control order and capture a deterministic fixture screenshot at every listed viewport. A visual comparator rasterizes the approved SVG baseline to the declared viewport and compares it to the screenshot using approved deterministic font/assets and dynamic-data fixture values; any meaningful placement/order mismatch is reported with artifacts and fails CI. Missing mapping, fixture, SVG/Markdown baseline, viewport evidence, or visual mismatch is a build failure.

**Execution gates.** During implementation run focused frontend tests (`npm test -- --silent` where supported), `npm run typecheck`, and a production `npm run build` from `frontend/`; run the root `npm run sdd:check` and `npm run sync:check` for workspace governance. The current root SDD gate targets the bootstrap spec rather than this feature, so frontend design validation also uses Markdown/spec diagnostics and the dedicated screen-manifest/contract checks described above. Record command, fixture version, outcome, and generated visual artifacts as immutable evidence; passing tests support but do not replace the backend’s authorization, governance, and recovery authority.
