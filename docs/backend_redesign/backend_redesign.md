# Backend Redesign: Common Control Plane

**Version:** 1.2  
**Status:** Proposed implementation design  
**Date:** 2026-07-19  
**Scope:** A governed, operable backend communication layer between the redesigned frontend and the existing `common-agent-swarm-ops` backend library, including the VA domain-adapter contract in [`../frontend_redesign/va_agent_structure_mapping.md`](../frontend_redesign/va_agent_structure_mapping.md).

## Platform baseline additions (v1.2)

This addendum adopts the strongest reusable control-plane practices from the generic backend design while preserving this document's Common Agent and VA domain-adapter focus. It defines the product-facing operational boundary; it does **not** replace the existing library, mandate a particular queue, vector store, or orchestration engine, or expose internal provider/runtime controls to the browser.

### Requirements 1.13–1.18

#### Requirement 1.13: Stable, documented API lifecycle

The backend shall maintain `/api/v1` as its sole browser-facing namespace, generate OpenAPI from the implemented FastAPI/Pydantic routes, and publish typed frontend client contracts from that schema. Compatible additions are additive; removal, semantic narrowing, or response-shape changes require a documented deprecation window, migration path, contract-test update, and versioned replacement.

#### Requirement 1.14: Secure ingress and untrusted-content handling

The backend shall apply request-size limits, validated content types, organization-scoped ACLs, filename/path normalization, object-storage isolation, and malware/quarantine scanning where files are accepted. Retrieved documents, imported graph data, third-party adapter responses, and model output are untrusted data: they cannot grant authority, change policy, select tools, inject a privileged URL/command, or bypass validation.

#### Requirement 1.15: Durable asynchronous execution and recovery

Long-running run, evaluation, contribution, indexing, and rollout work shall not execute in HTTP request lifetimes. Commands shall create durable, idempotent work records and auditable state transitions before dispatch. Local-inline dispatch may remain a development adapter; production dispatch must support lease/claim recovery, bounded retries, cancellation checks, dead-letter or manual-recovery handling, and redacted progress publication through the transactional outbox.

#### Requirement 1.16: Observable, readiness-aware operation

The backend shall provide separate liveness, readiness, and authenticated operational-health views; structured logs, metrics, traces, correlation IDs, and audit evidence shall connect an HTTP command to its outbox event, task/run, approval, and outcome. Readiness must report dependency state without leaking secrets or tenant data.

#### Requirement 1.17: Bounded delivery, replay, and retention

The backend shall define configured retention, replay, payload-size, and backpressure limits for events, traces, artifacts, approvals, audit evidence, idempotency records, and failed work. SSE resume shall return a deterministic bounded replay or a stable recovery response directing the client to a fresh projection; it must never silently skip a sequence gap.

#### Requirement 1.18: Safe deployment and configuration

The backend shall use environment-derived, schema-validated configuration for trusted origins, identity integration, database/object-store/queue adapters, retention, rate limits, and feature flags. Secrets remain in a secret manager or deployment environment, never in API payloads, event data, frontend configuration, or diagnostic responses. Production transport requires HTTPS, restrictive CORS, and security headers appropriate to the selected session model.

### API lifecycle and system endpoints

`/api/v1` remains the public contract root. FastAPI-generated OpenAPI is the machine-readable API source of truth; the frontend consumes generated or checked client types rather than copying DTOs by hand. The existing low-level `/workflow-runs/*` compatibility routes remain supported only through a documented compatibility matrix that maps them to façade projections and records their sunset criteria.

| Endpoint | Audience | Required behavior |
|---|---|---|
| `GET /api/v1/health/live` | platform/load balancer | Reports process liveness only; it does not contact dependencies. |
| `GET /api/v1/health/ready` | platform/load balancer | Reports whether required configured dependencies are usable: PostgreSQL and required dispatch/outbox adapters; optional services report `not_configured` rather than failing readiness. |
| `GET /api/v1/health` | authorized operations users | Returns redacted component summary, build/schema version, and readiness timestamp; it never returns connection strings, credentials, or tenant details. |
| `GET /api/v1/openapi.json` | frontend tooling/integrators | Versioned generated contract. Schema compatibility is checked in CI before a public API change is accepted. |

State-changing routes retain the existing idempotency rule. API middleware enforces authenticated route access, request/body limits, CORS origin allow-lists, request/correlation IDs, security headers, validated pagination/filter bounds, and endpoint-appropriate rate limits. Rate-limit responses use the public error envelope and `Retry-After`; throttling must not expose whether a protected resource exists.

### Execution topology, failure recovery, and scaling

The façade uses separate deployable roles even when local development runs them in one process:

| Role | Responsibility | Must not do |
|---|---|---|
| API process | Authenticate, validate, authorize, persist commands/queries, publish only committed outbox facts | Run long-lived agent, indexing, evaluation, or rollout work inline in a production request |
| Dispatcher/worker | Claim durable work, invoke existing library run/evaluation/evolution seams, checkpoint outcomes, and emit redacted progress | Reconstruct actor authority from a client payload or bypass the library tool broker/governance |
| Outbox/SSE publisher | Deliver authorized, retention-bounded operational projections and handle reconnects | Treat an SSE event as an authoritative command or audit substitute |
| Reconciler/recovery job | Detect expired leases, stuck nonterminal runs, failed projection delivery, and retention work; record a recovery decision | Auto-retry non-idempotent or approval-gated effects without a fresh policy check |

A durable work item includes organization scope, immutable command/run/task reference, attempt number, lease/claim metadata, scheduled time, cancellation state, correlation ID, and an idempotency/deduplication key. Workers use compare-and-set transitions and renew short leases while active. On crash or lease expiry, a reconciler either safely reclaims the item, marks it `manual_recovery_required`, or routes it to a dead-letter record with its redacted failure summary. Retry policy is explicit per operation: transient transport/dependency faults may use bounded exponential backoff; validation, authorization, policy, schema, rights/consent, and non-idempotent ambiguity failures do not retry automatically.

Queue/worker technology remains an adapter decision. The initial local-inline path must implement the same command, checkpoint, state-transition, outbox, cancellation, and recovery contracts as a later queue-backed adapter so browser behavior and audit evidence do not change during migration. Work categories may scale independently: run dispatch, evaluation, contribution/indexing, projection/outbox, and retention/reconciliation.

### Secure artifacts, knowledge, and prompt boundary

Artifact and knowledge ingestion is a governed pipeline: authorize upload or import; validate declared and detected type, size, checksum, and ownership; quarantine/scan when configured; store under an authorization-checked opaque key; extract/index asynchronously; and retain only redacted metadata in projections. Archive or deletion is a governed lifecycle action that preserves the minimum audit/provenance evidence required by policy.

Application adapters must delimit trusted instructions, published Common Agent policy, retrieved/context material, tool results, and user-provided text. Only server-held policy and validated published contracts can authorize a tool. Retrieval traces expose allowed source IDs, license/sensitivity/freshness state, and digests—not raw restricted content. Prompt-injection indicators, prohibited content, suspicious tool proposals, and mismatched artifact manifests are logged as security-relevant evidence and fail closed or require review according to policy.

### Reliability, telemetry, and retention policy

Every log, trace, metric, audit event, outbox event, task attempt, approval, and frontend error response carries a correlation ID. Traces link route → application command → repository transaction → outbox event → worker/task/run → governed tool/evaluation/approval outcome. Telemetry is redacted at source and retains no tokens, credentials, raw prompts, raw protected artifacts, or forbidden tool inputs.

The deployment configuration defines, and operations documents, measurable targets for at least the following categories:

| Category | Required measure / policy |
|---|---|
| API | request count, latency, error rate, rate-limit count, auth failure count, and OpenAPI/schema version |
| Execution | queued/running/blocked/failed/completed counts, queue age/depth, lease recovery, retry/dead-letter count, task/run duration, checkpoint/replay success |
| Governance | approval wait/expiry, denied effects, gate outcomes, rollout rollback count, and policy evaluation latency |
| Quality and knowledge | L1/L2/L3 pass/fail, evaluation duration, retrieval latency, ingestion/indexing state, contribution verification state |
| Cost and capacity | model/tool usage, cost, worker saturation, database/outbox latency, SSE connection/replay/backpressure counts |
| Retention | audit, event, trace, artifact, idempotency, approval, and dead-letter retention windows with archival/deletion owners |

Service-level objectives, alert thresholds, and retention durations are deployment policy, not browser constants. At minimum, readiness failure, persistent queue age, terminal-run failure rate, event replay gaps, outbox lag, approval expiry, and rollout rollback conditions must alert an operator. Dashboards label delayed projections with `as_of`, freshness, and degraded-state fields rather than presenting stale data as live.

### Platform delivery and verification additions

Add **Phase F — production operability** after Phase E:

1. Generate and compatibility-check OpenAPI; produce typed frontend client artifacts and a compatibility matrix for legacy run routes.
2. Add HTTP ingress controls, secure artifact/knowledge ingestion, validated configuration, rate limits, CORS/security headers, and redaction regression checks.
3. Separate API, worker/dispatcher, outbox/SSE, and reconciler responsibilities behind adapters; add leasing, cancellation, bounded retry, dead-letter/manual-recovery, and migration parity tests for local-inline versus queue-backed dispatch.
4. Add liveness/readiness/operational-health endpoints, correlated structured telemetry, dashboards/alerts, and explicit retention/replay/backpressure policies.

**Accept when:** a generated-contract diff cannot silently break the frontend; a slow or failed dependency produces a truthful readiness/degraded state; a worker crash or duplicated dispatch cannot duplicate a governed effect; malformed or hostile imports/uploads cannot escape their tenant or become authority; SSE replay either delivers an authorized contiguous bounded sequence or returns a deterministic recovery path; and operations can trace an authorized command to its durable outcome without accessing secrets or raw protected content.

Extend verification with API compatibility tests, request-limit/rate-limit tests, CORS/header tests, artifact type/path/ACL/quarantine tests, prompt-boundary/tool-authorization tests, lease-expiry and crash-recovery tests, duplicate-delivery/idempotency tests, dead-letter/manual-recovery tests, readiness degradation tests, telemetry-redaction tests, SSE gap/backpressure/retention tests, and retention/archival authorization tests.

## Overview

This document is the backend companion to [`../frontend_redesign/frontend_redesign.md`](../frontend_redesign/frontend_redesign.md). It adopts the API-first, governance-first control-plane posture in `generic-swarm-ops/backend.md`, but maps it to the code that exists in this repository.

The new layer is an **additive façade**, not a replacement for the common library. It owns browser-facing API contracts, authentication integration, tenancy, query models, durable persistence, event streaming, and frontend DTOs. It delegates domain decisions and side effects to the current library services.

```text
Redesigned frontend
       │ REST + Server-Sent Events
       ▼
Common control-plane façade (new)
       │ typed commands, queries, and frontend DTO mapping
       ▼
common-agent-swarm-ops library (existing)
       │ runs · approvals · tool broker · evaluation · evolution · validation
       ▼
PostgreSQL / outbox / object storage / engine adapters
```

The public interface remains exclusively versioned under `/api/v1`. The frontend design's illustrative `/api/commons/*` calls map to `/api/v1/commons/*`; unversioned browser APIs must not be introduced.

## 2. Product outcomes

The façade must make the Common Registry, graph composer/canvas, fleet operations, provenance, approvals, evaluations, knowledge contribution, and safe rollout screens real without exposing engines, providers, repositories, tool adapters, or credentials to the browser.

It must provide:

- a trusted request identity (`organization_id`, `actor_id`, `correlation_id`) for every protected request;
- a versioned Common Agent and Common Pattern registry with immutable published versions;
- persisted Swarm Instances whose graph nodes pin common versions or declare an explicit fork;
- controlled execution using the existing queued-run, dispatch, governance, and host-tool-broker flow;
- live, redacted SSE updates for frontend operational views;
- aggregate read models for dashboard, registry, activity, agent detail, and rollout impact;
- proposal, evaluation, approval, canary, and rollback workflows that preserve existing fail-closed controls.

## Requirements

### Requirement 1.1: Governed browser boundary

The backend shall expose the redesigned frontend only to documented `/api/v1` REST and SSE contracts, and shall not expose engines, providers, repositories, tool adapters, credentials, or client-derived authority.

### Requirement 1.2: Trusted multi-tenant identity

The backend shall derive tenant, actor, permissions, and correlation context from trusted authentication middleware and enforce organization scoping on every protected resource.

### Requirement 1.3: Immutable common provenance

The backend shall persist immutable Common Agent/Pattern versions and record the exact graph revision and common versions used by every run.

### Requirement 1.4: Governed effects and rollouts

The backend shall route effects through existing authorization and approval services and require bounded canary scope, criteria, rollback, and approval for rollout promotion.

### Requirement 1.5: Durable operations visibility

The backend shall persist audit facts and redacted operational events, provide authorized SSE observation, and supply aggregate projections for the redesigned frontend.

### Requirement 1.6: Safe graph execution

The backend shall compile a Swarm Instance only after provenance, schema, budget, verification, rollback, and approval policy validation, then use the existing queued-run and dispatch flow.

## 3. Non-goals and hard boundaries

- The browser must never access the library directly, invoke an engine, run a tool, supply actor/tenant identity, or receive credentials, raw prompts, secrets, or unredacted tool results.
- This layer must not bypass `AuthorizationService`, `GovernanceService`, `HostToolBroker`, `EvaluationService`, `EvolutionService`, or their organization-scoped repository contracts.
- A Common version is immutable after publication. Editing creates a draft/fork/proposal; promotion is deliberate and auditable.
- SSE delivers observations only. A state-changing command is always a separately authorized, idempotent REST request.
- The initial release does not require a new orchestration engine, meta-critic, vector store, public registry, or automatic production promotion.

## 4. Current-state alignment

| Existing capability | Reuse through façade | Required addition |
|---|---|---|
| `/api/v1` FastAPI router and strict trusted context dependency | Preserve as the sole public namespace and inject its context after authentication | Authentication/session middleware and role/permission source |
| Definition validation and domain-pack registration | Validate graph-derived workflow definitions and safe common-pack manifests | Common Agent/Pattern CRUD, search, publication, and version metadata |
| Queued runs, preview/confirm dispatch, graph state, checkpoints | Execute a Swarm Instance and expose redacted run projections | Persistent run/event projections, run lists, replay and partial-replay commands |
| Tool authorization and approval gates | Perform all effectful actions through the existing authorization intersection and fresh approval reauthorization | Approval inbox, reviewer assignment, filters, and impact-oriented projections |
| Deterministic evaluations and sandbox-only evolution | Gate proposal/canary lifecycle and display evidence | Registry evaluation/usage aggregation, proposal review read models, rollout operations |
| In-memory repositories; PostgreSQL checkpoint repository | Retain existing repository protocols and optimistic transitions | PostgreSQL implementations for all product records plus transactional outbox |

The current `ControlPlaneServices` is a useful library composition root, but it is not the browser API. The façade calls its services through application adapters and replaces default in-memory stores with durable implementations in production.

## Architecture

### Layer responsibilities

| Layer | Responsibility | Must not do |
|---|---|---|
| `api/v1` routes | Authenticate dependency, validate HTTP DTOs, enforce endpoint permission, return public schema/envelope | Contain workflow policy, query SQL, or engine calls |
| Application services | Translate frontend commands/queries, coordinate transactions, map library results, emit outbox events | Accept browser-provided authority or bypass governance |
| Common-library adapters | Translate `CommonAgent`, `CommonPattern`, and `SwarmInstance` records into validated workflow definitions, run commands, approvals, evaluations, and evolution operations | Reimplement library safety rules |
| Domain library | Validate definitions/packs, run/dispatch, authorize tools, pause/resume approvals, evaluate and evolve variants | Know HTTP, cookies, frontend routes, or database tables |
| Infrastructure | PostgreSQL repositories, outbox publisher, SSE subscription, object storage, search index, engine/IdP adapters | Decide business policy |

## Components and Interfaces

### Proposed package layout

```text
backend/app/
  api/v1/
    auth.py                 # session callback/logout/context only
    commons.py              # agents, patterns, versions, proposals
    swarms.py               # instances, graph drafts, commands
    ops.py                  # health, activity, insights, rollouts
    events.py               # SSE subscriptions
    approvals.py            # extend existing detail/decision routes
  application/
    common_registry.py      # commands/queries + publication policy
    swarm_instances.py      # graph persistence + definition adapter
    fleet_ops.py            # materialized query models and rollout impact
    event_stream.py         # outbox → authorized SSE
  adapters/
    common_library.py       # existing service/record adapters
    identity.py             # IdP claims → AuthenticatedRequestContext
  repositories/
    postgres_*.py           # durable library and façade repository implementations
  projections/
    builders.py             # dashboard/activity/usage read models
  domain/                   # façade records that do not belong in the library
```

Existing modules such as `governance/`, `evaluation/`, `evolution/`, `registry/`, `repositories/protocols.py`, and the engine modules remain the safety-critical library. Add adapters first; do not move them during the frontend delivery.

### 5.3 Request lifecycle

1. Identity middleware validates a configured OIDC/session/API-key credential and derives organization, actor, permissions, locale, and correlation ID. It sets `AuthenticatedRequestContext`; a request header may supply only a syntactically validated correlation ID, never identity.
2. A route validates a narrow request DTO and checks endpoint-level permission. The application service additionally checks resource ownership and policy.
3. A command application service starts a transaction, writes immutable/domain records using optimistic concurrency, invokes the library adapter, and appends an outbox event in the same transaction.
4. The publisher sends redacted event payloads to authorized SSE subscribers. Read projections update asynchronously or transactionally, depending on the query's freshness requirement.
5. Errors use a stable public code and correlation ID. Internal causes are written to audit/log infrastructure, not returned to the browser.

### 5.4 Identity, tenancy, and authorization

Use Keycloak/OIDC for the redesigned product's self-hosted login flow, with a test-only local identity adapter. Map verified claims into the existing `AuthenticatedRequestContext` and never read tenant or actor IDs from query strings, route bodies, or frontend local storage.

Minimum roles are `viewer`, `operator`, `editor`, `reviewer`, `registry_maintainer`, and `organization_admin`. Endpoint permission is coarse-grained; library tool permission remains the existing intersection of agent, declared step, role, organization, risk, and approval state. Common resources carry a visibility (`organization`, `shared`, `public` reserved) and owners can only mutate their permitted scope.

State-changing routes require a caller-provided `Idempotency-Key`. Persist the key, actor, request digest, response reference, and expiration; a reused key with a different digest fails with `idempotency_conflict`.

## Data Models

Every durable record includes `id`, `organization_id`, `schema_version`, `version`, `created_at`, `updated_at`, and `correlation_id`. All versioned writes use an expected version. Timestamps are UTC RFC 3339 strings at the API boundary.

| Record | Required purpose and fields |
|---|---|
| `CommonAgentVersion` | Immutable `common_agent_id`, semantic `version`, status (`draft`, `proposed`, `active`, `deprecated`), normalized spec, I/O schemas, tool allow-list, eval rubric, knowledge subscriptions, provenance, compatibility, and aggregate metrics |
| `CommonPatternVersion` | Immutable pattern ID/version, graph template, slots/constraints, compatibility rules, risk/verification requirements, pattern metrics, and provenance |
| `SwarmInstance` | Organization-owned graph draft with linked pattern/version, nodes/edges/layout, pin/fork provenance, run policy, budgets, and optimistic revision |
| `SwarmRunProjection` | Redacted run status, engine/thread/checkpoint references, graph node/edge status, metrics, failure code, exact common versions, and action preview references |
| `CommonProposal` | Target type/id/version, proposed immutable diff, source fork/run evidence IDs, validation/evaluation evidence, state, reviewer decisions, and impact summary |
| `RolloutCampaign` | Selected version, target instances, canary scope, required approvals, criteria, rollback reference, status, and measured outcomes |
| `ActivityEvent` | Immutable, redacted event with subject reference, category, severity, topic, payload schema version, timestamp, and correlation ID |
| `Contribution` | Opt-in, provenance-preserving candidate knowledge/eval signal, verification state, owner scope, and approval/retention policy |

The façade maps these records to existing library values. A `SwarmInstance` graph must compile into a versioned workflow definition accepted by the existing `WorkflowDefinitionValidator`; compilation cannot silently relax tool, rollback, approval, or production-readiness validation.

### 6.1 Graph and provenance contract

```json
{
  "id": "swarm_01",
  "revision": 12,
  "linked_pattern": { "id": "parallel-research", "version": "1.4" },
  "nodes": [{
    "id": "verify",
    "kind": "common_agent",
    "common_agent": { "id": "research-verifier", "version": "1.8" },
    "position": { "x": 820, "y": 380 },
    "overrides": null
  }],
  "edges": [{ "id": "research-to-verify", "source": "research", "target": "verify", "kind": "data" }],
  "policy": { "cost_cap": "25.00", "requires_verification": true }
}
```

A `custom_agent` must include `forked_from` or an explicit `custom_reason`. A pinned Common version remains immutable for historical runs. Updating a node creates a new Swarm Instance revision; it never rewrites a run's provenance.

## 7. Public API contract

All successful responses use `{ "data": ..., "meta": { "correlation_id": "..." } }`. List responses add `page`/`cursor` metadata. Errors use `{ "error": { "code", "message", "correlation_id", "retryable", "fields"? } }`. Existing redacted run and approval schemas may be preserved during transition, but new endpoints use this envelope consistently.

### 7.1 Phase-1 endpoint surface

| Resource | Contract |
|---|---|
| Identity | `GET /api/v1/auth/context`, `POST /api/v1/auth/logout`, OIDC callback handled server-side; no browser API for token issuance when cookie sessions are used |
| Common agents | `GET /api/v1/commons/agents`, `GET /api/v1/commons/agents/{id}/versions/{version}`, `POST /api/v1/commons/agents/{id}/forks`, `POST /api/v1/commons/agents/{id}/proposals` |
| Common patterns | `GET /api/v1/commons/patterns`, `GET /api/v1/commons/patterns/{id}/versions/{version}`, `POST /api/v1/commons/patterns/{id}/instantiate`, `POST /api/v1/commons/patterns/proposals` |
| Swarm drafts/canvas | `POST /api/v1/swarms`, `GET /api/v1/swarms/{id}`, `PATCH /api/v1/swarms/{id}/graph`, `POST /api/v1/swarms/{id}/validate`, `POST /api/v1/swarms/{id}/runs` |
| Runs | `GET /api/v1/runs/{id}`, `GET /api/v1/runs/{id}/graph-state`, `POST /api/v1/runs/{id}/dispatch`, `POST /api/v1/runs/{id}/pause`, `POST /api/v1/runs/{id}/replay` |
| Dashboard and activity | `GET /api/v1/commons/health`, `GET /api/v1/swarms/running`, `GET /api/v1/activity`, `GET /api/v1/activity/insights`, `GET /api/v1/insights/common-impact` |
| Approvals | `GET /api/v1/approvals`, existing `GET /api/v1/approvals/{id}`, existing `POST /api/v1/approvals/{id}/decision` |
| Events | `GET /api/v1/events/stream?topics=swarm:{id},commons:health`; `Last-Event-ID` supports reconnect from a bounded retention window |

The existing `/workflow-runs/*` endpoints remain supported as low-level compatibility APIs. The redesigned UI consumes the new `/runs/*` projections, which are backed by the same run IDs and library services.

## Error Handling

Routes fail closed and return only stable, redaction-safe error codes. Validation errors include field-level corrections; authorization, visibility, approval-state, optimistic-version, idempotency, and policy violations do not reveal protected resource state. Transient database, queue, or stream failures are marked retryable only when a safe retry is supported. Every error carries the server-derived correlation ID, while detailed causes remain in structured logs and audit evidence.

### Query semantics

Registry and activity lists use cursor pagination, whitelisted sort fields, and validated filters. Registry queries support text search, tags/domains, status, minimum success rate, compatibility, recently improved, and `used_by_me`. Activity supports time range, workspace, swarm, common version, status, outdated-version flag, and provenance/contribution filters. Query results must always be scoped by organization and visibility policy before filtering or aggregation.

Dashboard/impact endpoints are read models, not live aggregation over raw run records. Their `as_of` timestamp and freshness state are explicit so the frontend can distinguish a cached projection from a live event.

### 7.3 Commands and library mappings

| Frontend command | Façade behavior | Existing library seam |
|---|---|---|
| Create from a pattern | Resolve compatible immutable versions, create a graph revision, compile and validate it | Definition validation and registration |
| Validate/run a graph | Validate provenance, schemas, budgets, verification/approval policy; queue then preview/confirm dispatch | `create_run`, `preview_or_dispatch`, engine/checkpoint services |
| Approve an effect | Load server-held gate/operation; append decision; freshly authorize before resume | `GovernanceService.submit_decision` and `HostToolBroker` |
| Propose an improvement | Store draft diff and evidence, run static validation/evaluation; never mutate published version | Pack validation, `EvaluationService`, `EvolutionService.propose` |
| Start safe rollout | Calculate tenant-owned impact, require criteria/rollback/approval, create narrow canary | `EvolutionService` canary and rollback lifecycle |
| Contribute knowledge | Validate opt-in/provenance and queue safe ingestion; publish only after required verification | Memory/retrieval services plus a new contribution workflow |

## Correctness Properties

### Property 1: Trusted, tenant-scoped commands

Every protected command is authenticated, organization-scoped, permission-checked, idempotent where state-changing, and correlation-traceable.

**Validates: Requirements 1.1, 1.2**

### Property 2: Valid graph provenance

A graph revision compiles only when every node has valid provenance, compatible schemas, and all required verification, budget, rollback, and approval controls.

**Validates: Requirements 1.3, 1.6**

### Property 3: Immutable execution provenance

A run records immutable common versions and graph revision before dispatch; later edits cannot alter its historical projection.

**Validates: Requirements 1.3**

### Property 4: Server-held approval authority

An approval decision cannot execute a new client payload. The server-held pending operation is freshly authorized before any effect.

**Validates: Requirements 1.4**

### Property 5: Fail-closed rollout

A failed canary criterion stops the scoped rollout and invokes its rollback lifecycle; no façade command can promote an unapproved sandbox variant.

**Validates: Requirements 1.4**

### Property 6: Durable command observability

A committed state transition produces an audit record and an outbox event; delivery retries do not duplicate its external subject event.

**Validates: Requirements 1.5**

### Events, audit, and redaction

The initial live transport is **SSE**, not WebSocket. It supports the dashboard, activity, approval, canvas status, and notification requirements with simpler authentication and reconnection. Add WebSocket only for later bidirectional playground/chat features.

Topics include `commons:health`, `commons:{agent_id}`, `swarm:{swarm_id}`, `run:{run_id}`, `approvals:{organization_id}`, `activity:new`, and `rollout:{campaign_id}`. Events have an opaque sequence ID, named type, subject, redacted payload, and correlation ID. The stream authorization check runs both when connecting and before publishing each event to a subscriber.

```text
id: evt_01J...
event: run.node_status_changed
data: {"run_id":"run_01","node_id":"verify","status":"running","at":"...","correlation_id":"..."}
```

Each command writes an append-only audit event before returning success. Audit and SSE events are not interchangeable: audit contains durable security/accountability facts; SSE is a redacted, retention-bounded operational notification. A transactional outbox prevents a committed command from losing its corresponding event.

Apply the library's existing redaction discipline to every DTO and projection. Store sensitive artifacts separately with explicit retention/ACL; projections contain digests, summaries, metrics, and references only. Never log a raw authorization header, token, prompt secret, tool credential, or prohibited tool argument.

## 9. Persistence and read models

Production replaces the default in-memory repositories with PostgreSQL repositories that implement the existing protocols, preserve organization scoping, and use optimistic versions. The current organization/run/thread checkpoint identity remains unchanged.

Core tables: `organizations`, `actors`, `role_bindings`, `common_agents`, `common_agent_versions`, `common_patterns`, `common_pattern_versions`, `swarm_instances`, `swarm_graph_revisions`, `runs`, `run_common_versions`, `approval_gates`, `approval_decisions`, `evaluation_runs`, `evaluation_results`, `proposals`, `rollout_campaigns`, `rollout_targets`, `knowledge_contributions`, `audit_events`, `outbox_events`, and read-model tables for common health, usage, activity, and impact.

Use parameterized queries, tenant predicates on every read/write, unique constraints for immutable `(resource_id, version)`, and explicit retention/archival jobs. Large traces and attachments belong in object storage, referenced by content digest and authorization-checked ID. Search may begin with indexed PostgreSQL text/facets; semantic/vector search is an optional later adapter.

## 10. Delivery sequence and acceptance criteria

### Phase A — secure foundation

Implement identity middleware, session endpoints, role bindings, error/envelope middleware, PostgreSQL repository composition, audit writer, idempotency, outbox, and `/events/stream`. **Accept when:** unauthenticated access fails closed; a forged tenant/actor value cannot alter context; events reconnect; audit/outbox records are durable.

### Phase B — registry and graph drafts

Implement Common Agent/Pattern immutable versions, search/filter projections, graph revisions, pattern instantiation, graph-to-definition compilation, and validation. **Accept when:** the registry and canvas use real API data; incompatible/common-unpinned graph changes fail with actionable errors; historical graph/revision provenance remains unchanged.

### Phase C — execution, activity, and approvals

Project Swarm Instance operations to the existing queued-run/dispatch/approval flow. Add run/activity/health projections, live node events, approval inbox, and replay policy. **Accept when:** a user can create, validate, preview, dispatch, observe, and approve a swarm through the frontend without exposing raw tool authority.

### Phase D — evaluations, contributions, and safe evolution

Add proposal review, evaluation evidence, usage/impact calculations, contribution workflow, rollout campaigns, canary monitoring, and rollback projections. **Accept when:** no proposal silently changes a Common version; a rollout needs a bounded tenant scope, criteria, rollback plan, and required approval; failed criteria halt/rollback through the existing evolution lifecycle.

## Testing Strategy

- Unit-test DTO validation, graph compilation, visibility rules, idempotency, projection builders, event redaction, and adapter mappings.
- Contract-test every endpoint against generated OpenAPI/Pydantic schemas and the frontend `lib` client types.
- Integration-test PostgreSQL tenant isolation, optimistic conflicts, outbox delivery, SSE reconnect, approval reauthorization, and library repository adapters.
- Test dangerous paths: cross-tenant ID access, forged identity fields, expired/replayed approvals, invalid graph connection, out-of-budget execution, unauthorized rollout, and prohibited tool inputs.
- Run focused Python tests, `frontend` contract tests, the frontend typecheck/build, and `npm run sdd:check` before each integration milestone. Record commands, versions, and immutable evidence references in the change record.

## 12. Open decisions

1. Confirm Keycloak deployment, realm/client model, cookie domain, logout, and local-development identity adapter.
2. Decide whether shared commons are organization-to-organization grants or a later public registry; Phase A defaults to organization-private visibility.
3. Define the canonical Common Agent spec and graph compiler's exact compatibility/schema rules before accepting editable canvas drafts.
4. Establish run/event retention, trace storage classification, cost-accounting source, and SLOs for dashboard freshness.
5. Select a job runner only after local-inline dispatch and outbox semantics are proven; do not couple the browser contract to a queue implementation.

## 13. Implementation evidence

This design is based on `generic-swarm-ops/backend.md`, the existing `backend/app/api/v1` routes and `ControlPlaneServices`, governance authorization/approval services, registry validator, evaluation/evolution services, repository protocols, PostgreSQL checkpoint repository, and the frontend redesign requirements. It intentionally distinguishes capabilities already present in the common library from the browser-facing control-plane capabilities that still need implementation.


## 14. Agent communication and VA domain adapter

This section makes the control plane complete for the frontend contracts in [`../frontend_redesign/va_agent_structure_mapping.md`](../frontend_redesign/va_agent_structure_mapping.md). It adds a domain adapter that preserves VA production semantics while keeping the common library domain-neutral. The adapter translates versioned Common Agent/Pattern/Swarm data into the existing library's validated definitions, queued runs, governance gates, tool authorization, evaluations, evolution, checkpointing, and audit seams.

```text
Frontend REST/SSE client
        │ commands, queries, opaque resource IDs
        ▼
API routes and frontend DTO mappers
        │
        ▼
Agent communication application services
  ├─ CommonAgentVersion resolver
  ├─ Graph/task compiler and scheduler adapter
  ├─ Artifact handoff and provenance policy service
  ├─ Critique router and resolution service
  ├─ Quality/gate coordinator
  └─ Redacted event/outbox projector
        │
        ▼
Existing common-agent-swarm-ops library
  validation · runs · checkpoints · authorization · approvals
  tool broker · memory/retrieval · evaluation · evolution · audit
```

### Requirements 1.7–1.12

#### Requirement 1.7: Complete Common Agent execution contract

The backend shall persist and project a versioned Common Agent contract containing canonical identity, category, responsibilities, out-of-scope boundaries, escalation targets, approval authority, architecture pattern, model/fallback policy, permitted tools, quality rubric, critique relationships, runtime limits, knowledge bindings, I/O schemas, and provenance policy.

#### Requirement 1.8: Explicit task coordination lifecycle

The backend shall compile a Swarm graph into organization-scoped tasks with dependencies, optional gates, constraints, common-version pins, checkpoint/replay references, and the lifecycle `idle`, `queued`, `running`, `self_refine`, `waiting_for_critique`, `blocked`, `failed`, or `complete`.

#### Requirement 1.9: Governed artifact handoff

The backend shall validate and persist every downstream artifact handoff with identity/version, parent lineage, brief scope, technical specification, rights/consent, continuity state, QC status, target channels, and provenance-manifest reference. Missing required handoff fields shall prevent dependent task dispatch.

#### Requirement 1.10: Directed critique and quality evidence

The backend shall authorize directed peer critiques using the published Common Agent relationships, retain critique evidence and resolution state, and evaluate L1 specification validation, L2 role rubric, L3 baseline/stakeholder preference, Judge/GateKeeper evidence, and human approval as distinct records.

#### Requirement 1.11: Redacted operational communication

The backend shall publish tenant-authorized, sequenceable SSE events for task lifecycle, artifacts, critiques, quality/gates, budgets, metrics, memory/contribution outcomes, tools, phases, and recoverable errors. It shall not publish raw tool arguments/results, credentials, prompt secrets, or privileged artifacts.

#### Requirement 1.12: Domain-adapter compatibility

The backend shall map VA production templates, phases, agent taxonomy, artifact requirements, critique bus, quality gates, and provenance/release requirements to common-agent-swarm-ops records without claiming the VA reference's unversioned endpoints are deployed in this repository.

### 14.1 Application components and ownership

| Component | Owns | Delegates to existing library |
|---|---|---|
| `CommonAgentVersionService` | Immutable spec publication, compatibility, critique relationship validation, projection | Domain-pack/definition validation and tool authorization policy |
| `SwarmGraphCompiler` | Graph revision validation; node/edge/task/dependency compilation; version pinning; graph-to-definition mapping | `WorkflowDefinitionValidator` and registered-definition storage |
| `TaskCoordinationService` | Task state transitions, dependency satisfaction, retry eligibility, self-refine bounds, checkpoint/replay projection | Queued-run creation, dispatch, engine/checkpoint seams |
| `ArtifactHandoffService` | Artifact manifest validation, lineage, rights/consent/continuity/QC/provenance projection | Secure artifact storage and audit writer |
| `CritiqueService` | Source/target relationship validation, severity/evidence/resolution lifecycle, task wake-up projection | Memory/retrieval and audit writer |
| `QualityGateService` | L1/L2/L3 evidence aggregation, Judge/GateKeeper projection, human-gate readiness | `EvaluationService`, `GovernanceService`, `EvolutionService` |
| `CommunicationProjectionService` | Frontend DTOs, activity/monitoring read models, SSE/outbox redaction and topic authorization | Existing redaction and organization-scoped repositories |

No component may execute a tool directly. A task reaches a tool only after library authorization evaluates the agent allow-list, graph-declared tools, actor role, organization policy, risk policy, and approval state.

### 14.2 Common Agent, task, and artifact persistence contracts

`CommonAgentVersion.spec` must contain the mapping document's complete agent contract. Store prompt content, raw knowledge, secrets, and protected artifacts outside browser-facing projections; use reference IDs, digests, and redacted summaries in API DTOs.

Add the following durable records and organization-scoped repository protocols:

| Record | Essential fields |
|---|---|
| `AgentTask` | task ID, run/graph/node IDs, pinned agent version, state, iteration, retry count, constraints, dependency IDs, gate IDs, checkpoint reference, metrics, timestamps, optimistic version |
| `TaskDependency` | source/target task IDs, condition/schema compatibility, optional gate requirement, satisfied timestamp |
| `ArtifactRecord` | artifact ID/version, parent asset IDs, source task/run, brief scope, technical spec, rights/consent state, continuity state, target channels, storage/digest reference, provenance reference |
| `CritiqueRecord` | source/target agent/task IDs, artifact reference, severity, rubric/evidence references, message digest/reference, open/addressed/dismissed state, timestamps |
| `QualityEvidence` | subject reference, L1 result, L2 score/threshold/rubric, L3 baseline/result, judge evidence, evaluation-run reference |
| `GateEvidence` | gate ID, criteria, subject/artifact references, Judge/GateKeeper evidence, reviewer assignment, expiry, human decision/comment/signature reference |
| `RunPhase` | run ID, optional adapter phase/template, sequence, entered/exited timestamps, transition evidence |

For VA-adapted records, `template_id` and production phase are optional generic metadata but, when supplied, must be validated against the published `CommonPatternVersion` adapter. VA template A–J and phases map to Pattern metadata; they do not become universal required fields.

### 14.3 Task coordination state machine

1. **Compile:** resolve a graph revision, Common Agent versions, schemas, runtime policies, required artifact inputs, dependencies, and gates. Reject unresolved versions, invalid critique relationships, incompatible schemas, missing required artifact fields, or policy-violating overrides.
2. **Plan:** produce immutable `AgentTask` and `TaskDependency` records. A planner/routing recommendation is advisory until it is validated and persisted; it cannot grant capability beyond the published agent/tool policy.
3. **Queue:** transition eligible tasks to `queued` only after dependencies and required gates are satisfied. Persist before dispatch.
4. **Execute:** invoke the existing queued-run/engine path. Project `running`, model/provider selection, redacted tool summaries, metrics, and checkpoint references.
5. **Refine or critique:** increment a bounded `self_refine` iteration only if policy permits. Directed critique can transition a task to `waiting_for_critique`; resolution returns it to a validated queue or terminal state.
6. **Block:** use `blocked` with a machine-readable reason: `missing_input`, `approval_required`, `quality_failed`, `rights_or_consent`, `budget_exhausted`, or `dependency_unresolved`.
7. **Recover:** retry only from a retryable failure and within `max_retries`; skip requires an authorized policy decision and records downstream impact. Replays create a new run/task lineage with explicit source graph, checkpoint, artifact, and common-version pins.
8. **Complete:** persist outputs/artifact handoff and quality evidence before satisfying dependent tasks or a release gate.

Task transitions use expected record versions, are audited, and emit an outbox event atomically. A client cannot directly force a task state.

### 14.4 Artifact, critique, and gate logic

Artifact handoff validation runs before a dependent tool invocation. At minimum, it checks artifact/version identity, parent lineage, brief scope, technical fields required by the target pattern, rights/consent, continuity state, QC status, target channels, and provenance-manifest reference. The validation response is redaction-safe but field-specific enough for the UI to correct missing data.

`CritiqueService` accepts a critique only if the source agent is listed in the target version's `accepts_critique_from`, the target is listed in the source version's `comments_on`, or a documented human-review policy authorizes the action. A critique retains severity (`blocker`, `major`, `minor`, `nit`), artifact and evidence references, optional rubric score, message reference, and resolution state. `blocker` or required-rubric critiques can prevent a task from continuing.

`QualityGateService` retains each layer independently:

- **L1:** schema, format, required-field, and technical-spec validation; all required checks must pass.
- **L2:** role-specific rubric score, threshold, evaluator/Judge reference, and evidence.
- **L3:** stakeholder or audience preference compared to a named baseline.
- **Gate:** GateKeeper/Judge criteria and evidence plus any required human approval.

A displayed aggregate score never overrides a failed mandatory lower layer. A release-ready artifact requires all applicable layers, rights/consent checks, provenance checks, and gate approval.


### 14.5 Extended API contract

The following routes extend the existing Phase-1 surface. All use the established response envelope, trusted identity, organization scope, redaction, audit, and idempotency rules.

| Resource | Contract | Communication rule |
|---|---|---|
| Agent contract | `GET /api/v1/commons/agents/{id}/versions/{version}/spec` | Returns a redacted published Common Agent version, including relationship/policy summaries and schema references |
| Graph tasks | `GET /api/v1/runs/{id}/tasks`, `GET /api/v1/runs/{id}/tasks/{taskId}` | Returns lifecycle, dependencies, constraints, metrics, checkpoint/replay references, and pinned versions |
| Retry/skip | `POST /api/v1/runs/{id}/tasks/{taskId}/retry`, `POST /api/v1/runs/{id}/tasks/{taskId}/skip` | Server determines eligibility; request includes an idempotency key and reason where policy requires it |
| Artifacts | `GET /api/v1/runs/{id}/artifacts`, `GET /api/v1/runs/{id}/artifacts/{artifactId}` | Returns an authorized projection of handoff, lineage, QC, rights, continuity, targets, and provenance reference |
| Critiques | `GET /api/v1/runs/{id}/critiques`, `POST /api/v1/runs/{id}/critiques`, `POST /api/v1/critiques/{id}/resolve` | Validates relationship/policy; never uses a client to choose privileged delivery authority |
| Quality | `GET /api/v1/runs/{id}/quality`, `GET /api/v1/artifacts/{id}/quality` | Returns distinct L1/L2/L3 and gate evidence rather than a flattened score |
| Gates | `GET /api/v1/approvals/{id}/evidence` | Returns authorized criteria, evidence refs, assignments, expiry, and affected subject projections before the existing decision command |
| Knowledge/memory | `GET /api/v1/commons/agents/{id}/knowledge-bindings`, `GET /api/v1/runs/{id}/retrieval-trace` | Returns source/license/freshness and redacted retrieval evidence, never raw protected corpus content |
| Router policy | `GET/PUT /api/v1/settings/router-policy` | Changes require organization-admin authorization and affect future validated tasks only |
| Domain adapter | `GET /api/v1/domain-adapters/va/templates`, `GET /api/v1/domain-adapters/va/phases` | Optional discovery metadata; does not create an unversioned VA API surface |

The VA reference's production commands map semantically as follows: create/launch production maps to create graph revision plus run/dispatch; gate decision maps to the existing approval-decision endpoint; critique submission maps to run critique; agent retry/skip map to task recovery; artifacts map to run artifact projections; router configuration maps to versioned router policy. This is a compatibility mapping, not a claim of endpoint parity.

### 14.6 SSE communication protocol

Use the existing `/api/v1/events/stream` transport with topic authorization and `Last-Event-ID` replay. Events include `id`, `type`, `occurred_at`, `organization_id`-scoped subject references, `correlation_id`, `payload_schema_version`, and a redacted payload.

| Event type | Minimal redacted payload |
|---|---|
| `run.task_state_changed` | run/task/node IDs, state, previous state, iteration, retry count, blocked reason, timestamp |
| `run.task_dependency_satisfied` | run/task/dependency IDs, condition/gate reference, timestamp |
| `run.artifact_created` / `run.artifact_updated` | run/task/artifact ID/version, producer version, QC/provenance summary, thumbnail/reference when authorized |
| `run.critique_created` / `run.critique_resolved` | critique ID, source/target task/agent refs, severity, status, artifact/evidence refs |
| `run.quality_updated` | subject ref, L1 pass, L2 score/threshold, L3 result, gate state |
| `approval.requested` / `approval.resolved` | approval ID, run/task/artifact refs, risk tier, state, expiry, decision reference |
| `run.budget_updated` / `run.metric_updated` | run/task ref, budget/cost or named metric/threshold/assessment |
| `run.tool_completed` | run/task ref, adapter ID, authorized outcome summary, duration, reversible flag, effect digest |
| `run.retrieval_completed` / `contribution.updated` | agent/run ref, retrieval/contribution summary, freshness/verification state |
| `run.phase_changed` | run ref, adapter phase/template metadata, previous/current phase |
| `run.error` | subject ref, stable code, retryable flag, recovery action reference, correlation ID |

SSE cannot carry raw agent prompts, tool parameters, tool output bodies, credential material, protected source documents, private critiques, or artifact bytes. The event publisher checks resource visibility at delivery time, not only at connection time. Audit records are append-only authoritative evidence; SSE events are redacted operational projections and may be retention-bounded.

### 14.7 Repository and projection additions

Implement organization-scoped PostgreSQL repositories for `AgentTask`, `TaskDependency`, `ArtifactRecord`, `CritiqueRecord`, `QualityEvidence`, `GateEvidence`, and `RunPhase`. Use foreign keys/references to durable Common Agent versions, graph revisions, runs, and existing approval/evaluation records. Add indexes for `(organization_id, run_id, state)`, dependency readiness, artifact lineage, critique target/status, quality gate state, event topic/sequence, and audit correlation ID.

Projection builders produce the exact read models needed by the frontend:

- **Canvas:** graph revision, node task state/lifecycle, dependencies/gates, metrics, artifacts, critiques, quality, and selected-node inspector data.
- **Agent detail/registry:** complete agent contract, runtime policy summary, relationship graph, benchmark/evaluation history, usage, and version provenance.
- **Activity/monitoring:** lifecycle/event timeline, retries, dependency waits, artifact lineage, critique backlog, quality/gate state, budget, metrics, and recovery eligibility.
- **Knowledge/evaluation:** source/license/freshness, retrieval trace, correction/benchmark association, L1/L2/L3 evidence, and proposal readiness.
- **Audit/notifications/mobile:** stable evidence references and high-risk summaries without privileged payload data.

### 14.8 Library adapter rules

`SwarmGraphCompiler` must convert only validated graph data into a workflow definition. It maps graph nodes to library-compatible agent/step identifiers, declared tool allow-lists, risk tiers, rollback requirements, required approvals, and references. It must reject any graph attempting to inject a tool identifier, credential, URL, executable instruction, raw endpoint, or authority not present in the published Common Agent/Pattern and organization policy.

`TaskCoordinationService` uses the library's run/dispatch path and checkpoints; it does not implement a parallel execution engine. `CritiqueService` stores and projects critique messages, then maps eligible resolution to a new validated task attempt or memory/retrieval input. `QualityGateService` invokes the existing evaluation/evolution services for retained evidence and uses `GovernanceService` for any effectful approval/resume. `ArtifactHandoffService` sends only authorized references into downstream task context.

### 14.9 Additional correctness properties

### Property 7: Complete agent contract projection

Every agent configuration, registry card, canvas node, and task projection resolves to a published Common Agent version with the required contract or returns a redaction-safe compatibility error.

**Validates: Requirements 1.7, 1.12**

### Property 8: Controlled lifecycle transition

A task can transition only through the coordination state machine with an expected version, satisfied dependencies/gates, policy-allowed retry/refinement, append-only audit evidence, and a corresponding outbox event.

**Validates: Requirements 1.8, 1.11**

### Property 9: Blocking artifact handoff

A dependent task cannot dispatch when its required artifact handoff fails identity, lineage, technical, rights/consent, continuity, QC, target, or provenance validation.

**Validates: Requirements 1.9**

### Property 10: Authorized critique and gate resolution

A critique is deliverable only through an allowed peer/human relationship, and a quality/gate decision cannot advance an effect until mandatory L1/L2/L3 and approval requirements are satisfied.

**Validates: Requirements 1.10**

### Property 11: Safe live communication

Every SSE event is organization-authorized, redacted, sequenceable, and traceable to a correlation/audit record; reconnecting cannot grant access to a different organization or hidden subject.

**Validates: Requirements 1.11**

### 14.10 Delivery increment and verification additions

Add **Phase E — agent communication adapter** after the existing foundation/registry/run work:

1. Persist Common Agent execution fields and graph task/dependency revisions.
2. Build task lifecycle, artifact handoff, critique, L1/L2/L3, and gate-evidence services with read projections.
3. Add the extended REST routes and redacted SSE event publisher.
4. Add a VA fixture pattern with parallel tasks, self-refine, critique wait, blocked approval, retry exhaustion, artifact handoff, and signed delivery provenance.

**Accept when:** the updated canvas, agent detail, activity, monitoring, knowledge, evaluation, notifications, audit, API portal, and blueprint UIs can retrieve the required projections and receive their live state through versioned contracts; no fixture can bypass tool authorization, artifact validation, quality gates, approval, tenant isolation, or redaction.

Extend the test strategy with contract tests for all new DTO/event schemas; property/integration tests for lifecycle transitions, dependency/gate eligibility, missing artifact fields, forbidden critique relationships, L1/L2/L3 failure precedence, event authorization/redaction, and replay provenance; and PostgreSQL transaction/outbox tests proving the audit/event atomicity of every command.
