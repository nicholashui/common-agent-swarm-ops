# Implementation Plan: Frontend Redesign

## Overview

Implement the governed TypeScript/Next.js control-plane client incrementally: establish generated-contract boundaries, then command/live-state runtimes and secure shared primitives, compose all approved screens, and finish with deterministic verification and visual-conformance gates.

## Tasks

- [ ] 1. Establish the generated API and authorized-projection boundary
  - [ ] 1.1 Create the pinned generated-client workflow, generated output surface, `PublicApiTransport`, and CI drift/type-check commands under `frontend/src/lib/api/` and frontend scripts; require same-origin versioned `/api/v1` generated operations only.
    - _Requirements: 1.1, 1.2, 1.3, 1.6, 10.14, 11.1, 11.13_
  - [ ] 1.2 Implement `ProjectionMapper`, allowlisted `SessionSafeCache`, `ReferenceLink`, `ActionControl`, and `EvidenceLink` so every renderer uses present generated fields and returned references only.
    - _Requirements: 1.4, 1.5, 2.1–2.9, 10.10, 10.15, 11.8, 11.12_
  - [ ]* 1.3 Write the fast-check test for **Property 1: Envelope mapping is schema-bounded and redaction-safe** in its own test file, with ≥100 runs and the required traceability comment.
    - **Validates: Requirements 1.4, 1.5**
  - [ ]* 1.4 Write the fast-check test for **Property 2: Authorized projection rendering has no client-created data or authority** using omitted-field, sensitive-sentinel, and reference-subset generators.
    - **Validates: Requirements 2.2, 2.3, 2.4, 2.7, 2.8, 2.9**
  - [ ]* 1.5 Add deterministic generated-client, mapper, redaction, correlation-copy, reference-origin, and contract-drift unit/integration tests with versioned fixtures.
    - _Requirements: 1.1–1.6, 2.3–2.9, 11.1, 11.8, 11.12_

- [ ] 2. Implement governed idempotent command handling
  - [ ] 2.1 Build `CommandCoordinator` and typed command reducer with injected UUID/clock/transport dependencies; allocate and retain one key, send it on submit/reconcile, block duplicate/programmatic invocations, and map queued, denial, rate-limit, manual-recovery, and terminal outcomes.
    - _Requirements: 3.1–3.13, 6.14, 7.4, 9.8, 12.7_
  - [ ]* 2.2 Write the fast-check test for **Property 3: A command intent has one durable idempotency identity and one pending-control owner** across duplicate, ambiguous, denial, retry, and reconciliation traces.
    - **Validates: Requirements 3.1, 3.2, 3.3, 3.5, 3.6, 3.11**
  - [ ]* 2.3 Write the fast-check test for **Property 4: Command outcomes are truthfully classified** with generated terminal, pending, rate-limit, denial, and reconciliation outcomes.
    - **Validates: Requirements 3.7, 3.8, 3.9, 3.12**
  - [ ]* 2.4 Add deterministic command integration tests for duplicate click, queued, cancellation, ambiguous transport, retry exhaustion, rate/authorization/policy/approval denial, and manual recovery.
    - _Requirements: 3.1–3.13, 11.2, 11.3_

- [ ] 3. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 4. Build ordered live projections and truthful operational status
  - [ ] 4.1 Implement `LiveProjectionController` with per-scope snapshot-first subscription state, exact schema/scope/sequence guards, cursor persistence, stale/reconnecting states, and serialized discard-and-replace resynchronization.
    - _Requirements: 4.1–4.11, 5.5, 10.11_
  - [ ] 4.2 Implement `ProjectionStatus` and stale-action gating that render server `as_of`, freshness, degradation, exact status text, named icon, alerts, and only returned refresh/reconnect controls.
    - _Requirements: 5.1–5.9, 6.15, 7.4, 10.7_
  - [ ]* 4.3 Write the fast-check test for **Property 5: Live observation begins from an authorized snapshot and scope** with arbitrary scope and authorized-topic inputs.
    - **Validates: Requirements 4.1, 4.2**
  - [ ]* 4.4 Write the fast-check test for **Property 6: Only the exact next authorized event mutates a live projection** using arbitrary noncontiguous event traces.
    - **Validates: Requirements 4.3, 4.4, 4.10, 4.11**
  - [ ]* 4.5 Write the fast-check test for **Property 7: Unsafe replay causes replacement resynchronization** for duplicate, gap, expiry, denial, bounded, and incompatible replay outcomes.
    - **Validates: Requirements 4.6, 4.7, 4.8**
  - [ ]* 4.6 Add deterministic REST/SSE ordering, replay anomaly, stale-status, unavailable-state, and freshness-critical action-blocking tests with generated-client fakes.
    - _Requirements: 4.1–4.11, 5.2–5.9, 11.4, 11.5_

- [ ] 5. Implement session-safe, accessible, and inert shared UI primitives
  - [ ] 5.1 Create the App Router `AuthenticatedShell`, `SessionBoundary`, same-origin proxy/security-header configuration, and memory-only session transition cleanup that aborts streams before a new projection can render.
    - _Requirements: 2.1, 10.11–10.16, 11.13, 12.2, 12.6_
  - [ ] 5.2 Implement `AccessibleDialog`, `OperationalAnnouncer`, focus/target CSS tokens, icon-control labels, and responsive shared layout primitives without changing authorized information entitlement.
    - _Requirements: 10.1–10.9, 12.8, 12.9_
  - [ ] 5.3 Implement `SafeContent`, generated artifact/knowledge ingestion forms, non-authoritative correction feedback, and `ExternalNavigationControl` capability enforcement with no client URL sink.
    - _Requirements: 8.1–8.10, 10.16, 11.6, 11.7, 11.9_
  - [ ]* 5.4 Write the fast-check test for **Property 8: Freshness presentation is exact and safely gates actions** across health, canvas, approval, rollout, and alert projections.
    - **Validates: Requirements 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 6.15, 7.4**
  - [ ]* 5.5 Write the fast-check test for **Property 12: Artifact and import content is inert and non-authoritative** using Unicode/hostile content and external URL generators with browser-side-effect spies.
    - **Validates: Requirements 8.1, 8.4, 8.6, 8.7, 8.8**
  - [ ]* 5.6 Write the fast-check test for **Property 14: Accessible semantic information survives labels, transitions, and mobile layout** for all state unions and widths 320–767.
    - **Validates: Requirements 10.1, 10.6, 10.7, 10.8**
  - [ ]* 5.7 Write the fast-check test for **Property 15: Browser persistence and external navigation are capability-safe** across cache candidates, session transitions, and destination candidates.
    - **Validates: Requirements 10.10, 10.12, 10.13**
  - [ ]* 5.8 Add DOM/browser tests for focus trap/restoration, exact accessible names, live announcement exact-once behavior, 44×44 targets, session-clear ordering, CSP, same-origin requests, inert content, and blocked external URLs.
    - _Requirements: 8.5–8.10, 10.1–10.16, 11.6–11.10, 11.13_

- [ ] 6. Compose authorized operational and domain-specific screens
  - [ ] 6.1 Create the typed `ScreenDefinition` manifest, fixed fixture registry, and capability-aware `ScreenBoundary` that maps every approved UI ID to its baseline, route/shell module, fixture, and viewport list.
    - _Requirements: 12.1–12.6, 12.10, 12.11_
  - [ ] 6.2 Implement dashboard, registry, agent/pattern detail, activity, monitoring, notifications, audit, profile, and evaluation renderers from shared projection primitives and generated filters.
    - _Requirements: 5.1–5.9, 6.1–6.7, 6.17, 11.11, 12.1–12.9_
  - [ ]* 6.3 Write the fast-check test for **Property 9: Common registry, activity, and graph metadata preserve returned provenance** with arbitrary common, task, filter, event, validation, and action-reference projections.
    - **Validates: Requirements 6.2, 6.3, 6.5, 6.6, 6.7, 6.13, 6.16**
  - [ ] 6.4 Implement composer and canvas graph adapters that present non-color edge semantics, common/custom provenance, exact task state, returned validation categories, and command-backed run/recovery actions.
    - _Requirements: 6.8–6.18, 12.1, 12.5, 12.7–12.9_
  - [ ]* 6.5 Write the fast-check test for **Property 10: Graph rendering preserves semantic structure and execution eligibility** for arbitrary nodes, relation types, task states, and eligibility results.
    - **Validates: Requirements 6.8, 6.9, 6.10, 6.11, 6.12**
  - [ ] 6.6 Implement approvals, rollout, and quality-evidence views that enforce evidence-revision refresh, stale irreversible-action blocking, distinct evidence categories, and returned rollout state/action presentation.
    - _Requirements: 7.1–7.8, 12.1, 12.5, 12.7–12.9_
  - [ ]* 6.7 Write the fast-check test for **Property 11: Approval and rollout UI remains evidence-bound** using arbitrary evidence revisions, evidence categories, rollout projections, and returned actions.
    - **Validates: Requirements 7.1, 7.2, 7.3, 7.5, 7.6**
  - [ ] 6.8 Implement knowledge/artifact/import and conditional VA renderers that present only returned opaque/redacted data, exact import/rights/delivery state, blocked delivery, and generic fallback when VA data is absent.
    - _Requirements: 8.1–8.10, 9.1–9.10, 12.1, 12.5, 12.7–12.9_
  - [ ]* 6.9 Write the fast-check test for **Property 13: VA adapters add returned domain information without inventing state** for present/absent VA projections and blocked-delivery conditions.
    - **Validates: Requirements 9.1, 9.2, 9.3, 9.4, 9.5, 9.9**
  - [ ] 6.10 Implement the remaining capability-gated approved routes—settings, developer API portal, onboarding, mobile companion, collaboration, costs, and blueprints—and register the legacy `/canvas` redirect.
    - _Requirements: 12.1–12.9_
  - [ ]* 6.11 Add deterministic screen composition tests for representative dashboard, registry, activity, canvas, approval, rollout, artifact/knowledge, VA, capability-unavailable, and mobile projections.
    - _Requirements: 5.9, 6.1–6.18, 7.1–7.8, 8.1–8.10, 9.1–9.10, 10.8, 11.11, 12.2–12.9_

- [ ] 7. Automate full inventory, visual, and immutable-evidence verification
  - [ ] 7.1 Implement the manifest verifier to produce exactly 21 complete inventory records and fail on missing baseline Markdown/SVG, route/shell, fixture, capability mapping, or viewport evidence.
    - _Requirements: 12.1–12.11_
  - [ ] 7.2 Implement deterministic per-viewport screenshot capture and SVG-baseline raster/visual comparison with fixed fonts, assets, fixture values, and mismatch artifacts.
    - _Requirements: 11.14, 12.3, 12.4, 12.9–12.11_
  - [ ] 7.3 Add frontend CI evidence output that immutably records executed command, fixture version, result, screenshot, and visual-comparison artifact for every verification run.
    - _Requirements: 11.14, 12.10, 12.11_
  - [ ]* 7.4 Add focused automated tests for manifest count/completeness, visual mismatch failure, CI evidence metadata, and all deterministic verification fixture scenarios.
    - _Requirements: 11.1–11.14, 12.10, 12.11_

- [ ] 8. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional test tasks; each property task uses fast-check with at least 100 runs and its mandated traceability comment.
- Run focused frontend tests with `npm test -- --silent` where supported, then `npm run typecheck`, `npm run build`, `npm run sdd:check`, and `npm run sync:check`; record commands and results as evidence.
- Each coding step builds on the generated-contract boundary and shared runtimes; no screen may introduce ungenerated DTOs, client authority, external URL loading, or a direct mutation path.

## Task Dependency Graph

```json
{"waves":[{"id":0,"tasks":["1.1","5.1","6.1"]},{"id":1,"tasks":["1.2"]},{"id":2,"tasks":["1.3","1.4","1.5","2.1","4.1","5.2","5.3"]},{"id":3,"tasks":["2.2","2.3","2.4","4.2","4.3","4.4","4.5","4.6","5.4","5.5","5.6","5.7","5.8","6.2","6.4","6.6","6.8","6.10"]},{"id":4,"tasks":["6.3","6.5","6.7","6.9","6.11"]},{"id":5,"tasks":["7.1","7.2","7.3"]},{"id":6,"tasks":["7.4"]}]}
```
