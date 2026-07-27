# UI-required APIs - existence matrix and fine-tuned specs

**Document ID:** `docs/ui-required-apis-matrix.md`  
**Revision:** 2.2 (ALL product façade routes implemented)  
**Date:** 2026-07-27  

### Implementation status (rev 2.2)

All matrix product paths are implemented under `backend/app/api/v1/` (`commons`, `swarms`, `product_ops`, `product_extended`, `events` stream alias).  
Evidence: `tests/unit/api/test_product_facade_routes.py`, `test_product_extended_routes.py`.

| Wave | Status |
|------|--------|
| Commons agents/patterns/proposals/forks/playground | **Done** |
| Swarms CRUD/graph/members/pins/run/export | **Done** (run = façade queue; engine dispatch still via workflow-runs when definition registered) |
| Activity / insights / common-impact / approvals inbox | **Done** |
| SSE `GET /events/stream` | **Done** |
| Knowledge sources/sync/contributions | **Done** |
| Settings/providers/secrets/invites | **Done** |
| Finance summary/budgets/exports | **Done** |
| Audit exports/integrity | **Done** |
| Notifications / profile preferences | **Done** |
| Collaboration shares/presence | **Done** |
| Blueprints list/create/deploy/fork/import | **Done** |
| Developer tokens/webhooks + bootstrap actions | **Done** |
| Product runs cancel/replay | **Done** (`/api/v1/runs/{id}/cancel\|replay`) |
| `GET /api/v1/openapi.json` stub | **Done** (full OpenAPI regen remains a CI release step) |

**Remaining non-blocking ops hygiene (not missing HTTP APIs):** durable Postgres backing for façade stores; regenerate full OpenAPI artifact for FE generated client; optional swarm-run deep link into `create_run`+`dispatch` when a compiled definition exists.  

### Evidence sources (repo)

| Source | Used for |
|--------|----------|
| `backend/build/contracts/openapi.json` | Implemented DTO field-level contracts |
| `backend/app/api/v1/schemas.py` | Pydantic public schemas / strict extra=forbid |
| `backend/app/api/v1/*.py` | Route surface, tags, behavior |
| `frontend/src/lib/api/generated/index.ts` | FE generated operations & TS types |
| `frontend/src/lib/contracts.ts` | Operator façade (runs/approvals) |
| `frontend/src/lib/ui/interaction-runtime.ts` | Live UI -> API wiring |
| `frontend/src/lib/ui/screen-actions.ts` | Fail-closed governed stubs |
| `frontend/src/components/*Home.tsx` | Per-screen controls requiring APIs |
| `frontend/src/app/api/auth/**` | Session BFF |
| `docs/backend_redesign/backend_redesign.md` §7-10 | Product façade target surface |
| `docs/frontend_redesign/frontend_redesign.md` | Browser boundaries, command rules |
| `docs/frontend_redesign/ui_0*.md` | Screen-level fetch/mutation intent |

---

## 0. Cross-cutting contracts (normative)

### 0.1 Browser boundary

- Public Host API namespace is exclusively **`/api/v1`** (versioned).
- Browser never supplies `organization_id`, `actor_id`, or role authority in body/query; Host derives `AuthenticatedRequestContext`.
- Mutations are **server-governed, idempotent command intents** with stable **`Idempotency-Key`** (1-200 chars) for the pending user intent.
- UI disables duplicate submit; does not mint a new key after ambiguous network failure.
- SSE is **observation-only**; state changes always go through REST commands.
- Stale projections cannot invoke freshness-critical actions.

### 0.2 Response envelopes

**Implemented legacy-compatible responses** may return DTO objects directly (current OpenAPI/generated client).

**Product façade (target, backend_redesign §7):**

```json
// success
{ "data": { /* resource */ }, "meta": { "correlation_id": "..." } }

// list success (cursor)
{ "data": { "items": [], "next_cursor": null }, "meta": { "correlation_id": "...", "as_of": "..." } }

// error
{ "error": { "code": "...", "message": "...", "correlation_id": "...", "retryable": false, "fields": [] } }
```

FE transport also accepts public error with optional `action_reference` and `retry_after_seconds`.

### 0.3 Action preview vs Action reference

| Concept | Where | Shape (implemented) | Purpose |
|---------|-------|---------------------|---------|
| **ActionPreviewResponse** | Run/dispatch/approval/graph-state | `action_id`, `summary`, `intended_effect`, `emitted_at`, optional `rollback_preview`, `supporting_evidence[]`, `confidence`, `uncertainty`, `correction_control` | Redacted preview of a server-held pending effect |
| **Action reference (product)** | Projections for buttons | `{ id, label, kind?, eligible, resource_ref?, expires_at? }` | Server-issued permit that enables a specific UI control |
| **GeneratedActionReference** | FE error/follow-up | Open JSON object | Transport-level follow-up action |

**Rule:** UI may **render** a control without an action reference (discovery), but must **fail closed** on click unless a current eligible reference is present (or the control is pure local presentation / navigation).

### 0.4 Roles (product façade)

`viewer` | `operator` | `editor` | `reviewer` | `registry_maintainer` | `organization_admin`

Coarse endpoint permission + fine library tool authorization (agent x step x role x org x risk x approval).

### 0.5 Status legend

| Symbol | Meaning |
|--------|---------|
| **Exists** | Route implemented under Host or FE BFF |
| **OpenAPI** | In `openapi.json` + FE generated ops |
| **Wired** | UI calls it live today |
| **Local** | UI uses pack/local fixtures only |
| **Stub** | Fail-closed announce; no host mutation |
| **Mismatch** | Path/name differs between UI expectation and Host |
| **Missing** | Required for product UI; not implemented |

### 0.6 Durable product records (backend_redesign §6)

Every durable record: `id`, `organization_id`, `schema_version`, `version`, `created_at`, `updated_at`, `correlation_id`; optimistic concurrency on writes.

| Record | Purpose |
|--------|---------|
| `CommonAgentVersion` | Immutable agent version + metrics + tool allow-list + provenance |
| `CommonPatternVersion` | Immutable pattern/graph template |
| `SwarmInstance` | Org graph draft + pins + policy |
| `SwarmRunProjection` | Redacted run + action previews |
| `CommonProposal` | Proposal diff + evidence + review state |
| `RolloutCampaign` | Canary scope, criteria, rollback, status |
| `ActivityEvent` | Redacted operational event |
| `Contribution` | Knowledge/eval contribution candidate |

---

## 1. Existence overview matrix

### 1.1 Frontend session BFF

| Capability | Method / path | Exists | OpenAPI | Wired | Gap |
|------------|---------------|--------|---------|-------|-----|
| Password login | `POST /api/auth/login` | Yes (FE) | N/A | Live | None |
| Demo session | `POST /api/auth/demo` | Yes | N/A | Live | None |
| OIDC start | `GET /api/auth/oidc/start` | Yes | N/A | Live | None |
| OIDC callback | `GET /api/auth/oidc/callback` | Yes | N/A | Live | None |
| Password reset | `POST /api/auth/password-reset` | Yes | N/A | Live | None |
| Logout | `POST /api/auth/logout` | Yes | N/A | Live | None |
| Session probe | `GET /api/auth/session` | Yes | N/A | Live | None |

### 1.2 Implemented Host APIs (OpenAPI 25 paths)

| Capability | Method / path | Exists | OpenAPI | UI wiring |
|------------|---------------|--------|---------|-----------|
| Auth context | `GET /api/v1/context` | Yes | Yes | Live (`interaction-runtime`) |
| Domain pack register | `POST /api/v1/domains/register` | Yes | Yes | Not product shells |
| Workflow definition | `POST /api/v1/workflows/definitions` | Yes | Yes | Not product shells |
| Create run | `POST /api/v1/workflows/{workflow_id}/run` | Yes | Yes | Live when bridged |
| Topology | `GET /api/v1/workflows/{workflow_id}/topology` | Yes | Yes | Live when bridged |
| Dispatch | `POST /api/v1/workflow-runs/dispatch` | Yes | Yes | Live when bridged |
| Read run | `GET /api/v1/workflow-runs/{run_id}` | Yes | Yes | Live (operator API) |
| Graph state | `GET /api/v1/workflow-runs/{run_id}/graph-state` | Yes | Yes | Live |
| Run events (REST list) | `GET /api/v1/workflow-runs/{run_id}/events` | Yes | Yes | Not main SSE path |
| Approval gate | `GET /api/v1/approvals/{approval_id}` | Yes | Yes | Live |
| Approval decision | `POST /api/v1/approvals/{approval_id}/decision` | Yes | Yes | Live + Idempotency-Key |
| Evaluation | `POST /api/v1/evaluations` | Yes | Yes | Live (`eval.run_campaign`) |
| Memory retrieve | `POST /api/v1/memory/retrieve` | Yes | Yes | Live (runtime); Knowledge Home partial |
| Evolution variants/canaries/promotions | `/api/v1/evolution/*` (9 ops) | Yes | Yes | Not product-button wired (stubs) |
| Video artifacts/release | `/api/v1/video/*` (3 ops) | Yes | Yes | Not redesign shells |

### 1.3 Host routes outside current OpenAPI extract (exist in code)

| Capability | Method / path | Exists | OpenAPI FE | UI wiring |
|------------|---------------|--------|------------|-----------|
| Topic SSE | `GET /api/v1/events/{topic}/stream` | Yes | No | FE expects `/events/stream` -> **Mismatch** |
| Activity projection | `GET /api/v1/activity-projections/{subject_reference}` | Yes | No | Activity **Local** |
| VA pattern metadata | `GET /api/v1/va/patterns/{pattern_version_id}/metadata` | Yes | No | Partial adapters |
| VA action | `POST /api/v1/va/actions` | Yes | No | Not product shells |
| VA evidence | `GET /api/v1/va/runs/{run_reference}/evidence` | Yes | No | None |
| Adoption control plane | `/api/v1/adoption/*` (packs, invocations, governance, handoffs, lifecycle, ...) | Yes | No | None in shells |

### 1.4 Product façade required by UI - **Missing** (target = backend_redesign §7.1 + UI specs)

| Capability | Target path | Exists | UI today |
|------------|-------------|--------|----------|
| List agents | `GET /api/v1/commons/agents` | Missing | Local pack catalog |
| Agent version detail | `GET /api/v1/commons/agents/{id}/versions/{version}` | Missing | Local + static SPEC.md |
| Agent fork | `POST /api/v1/commons/agents/{id}/forks` | Missing | Stub |
| Agent proposal | `POST /api/v1/commons/agents/{id}/proposals` | Missing | Stub |
| List patterns | `GET /api/v1/commons/patterns` | Missing | Local |
| Pattern version | `GET /api/v1/commons/patterns/{id}/versions/{version}` | Missing | Local |
| Instantiate pattern | `POST /api/v1/commons/patterns/{id}/instantiate` | Missing | Stub |
| Pattern proposals | `POST /api/v1/commons/patterns/proposals` | Missing | Stub |
| Create swarm | `POST /api/v1/swarms` | Missing | Stub / local draft |
| Get swarm | `GET /api/v1/swarms/{id}` | Missing | Local |
| Patch graph | `PATCH /api/v1/swarms/{id}/graph` | Missing | Local preview |
| Validate swarm | `POST /api/v1/swarms/{id}/validate` | Missing | Stub |
| Start swarm run | `POST /api/v1/swarms/{id}/runs` | Missing | Partial via workflow-runs |
| Product runs | `GET/POST /api/v1/runs/{id}...` | Missing façade (compat = workflow-runs) | Mixed |
| Dashboard health | `GET /api/v1/commons/health` | Missing | Local |
| Running swarms | `GET /api/v1/swarms/running` | Missing | Local |
| Activity list | `GET /api/v1/activity` | Missing | Local |
| Activity insights | `GET /api/v1/activity/insights` | Missing | Local |
| Common impact | `GET /api/v1/insights/common-impact` | Missing | Local |
| Approvals inbox | `GET /api/v1/approvals` | Missing list | Id-entry console only |
| Multi-topic SSE | `GET /api/v1/events/stream?topics=` | Missing (topic path exists) | Mismatch |
| Knowledge sources | `POST /api/v1/knowledge/sources` etc. | Missing | Stub |
| Playground | `POST /api/v1/commons/agents/{id}/playground-runs` | Missing | Stub |
| Cancel run | `POST /api/v1/workflow-runs/{id}/cancel` or `/runs/{id}/cancel` | Missing public | Stub |
| Settings/secrets/tokens | `/api/v1/settings/*`, `/secrets`, `/developer/*` | Missing | Stub |
| Finance/audit exports | `/api/v1/finance/*`, `/audit/*` | Missing | Stub |
| Collaboration/blueprints | `/api/v1/collaboration/*`, `/blueprints/*` | Missing | Stub |

### 1.5 Path / name mismatches (fine-tune)

| UI / portal expectation | Host today | Resolution |
|-------------------------|------------|------------|
| `POST .../approvals/{id}/decide` | `POST .../decision` | Prefer **decision**; fix portal copy |
| `GET /api/v1/events/stream` | `GET /api/v1/events/{topic}/stream` | Add multi-topic stream **or** change FE |
| `POST /api/v1/swarms/{id}/run` | `POST .../workflows/{id}/run` + dispatch | Product façade §3.12 maps to library |
| Illustrative `/api/commons/*` (UI md) | Must be `/api/v1/commons/*` | Always version |

---

## 2. Frontend BFF - fine-tuned specs

### 2.1 Session model

- Cookie-based session after login/demo/OIDC; `GET /api/auth/session` returns whether authenticated + display fields.
- `AuthenticatedShell` redirects unauthenticated users to `/login`.
- Host `/api/v1/*` still requires Host auth middleware when proxied; BFF session alone is not Host authority.

| Endpoint | Request | Response (conceptual) | Errors |
|----------|---------|------------------------|--------|
| `POST /api/auth/login` | `{ username, password }` | Set session cookie; ok | 401 invalid |
| `POST /api/auth/demo` | empty / demo flag | Demo session cookie | 4xx |
| `GET /api/auth/oidc/start?provider=` | query provider | Redirect URL / challenge | 4xx |
| `GET /api/auth/oidc/callback` | IdP query | Session + redirect app | 4xx |
| `POST /api/auth/password-reset?action=request\|confirm` | email / token+password | ok (no user enum) | 4xx |
| `POST /api/auth/logout` | credentials same-origin | Clear cookie | - |
| `GET /api/auth/session` | cookie | `{ session: { authenticated, email?, demo? } }` | 200 unauth shape |

---

## 3. Implemented Host APIs - field-level specs (from OpenAPI)

> Generated from `backend/build/contracts/openapi.json`.  
> UI wiring notes added after each high-traffic path group.


### `GET /api/v1/approvals/{approval_id}`

- **operationId:** `read_approval_gate_api_v1_approvals__approval_id__get`
- **summary:** Read Approval Gate
- **tags:** approvals
- **existence:** Backend **Yes** | OpenAPI **Yes** | FE generated client **Yes**
- **parameters:**
  - `approval_id` in `path` | required=True
- **response 200:** present (see OpenAPI)

---

### `POST /api/v1/approvals/{approval_id}/decision`

- **operationId:** `submit_approval_decision_api_v1_approvals__approval_id__decision_post`
- **summary:** Submit Approval Decision
- **tags:** approvals
- **existence:** Backend **Yes** | OpenAPI **Yes** | FE generated client **Yes**
- **parameters:**
  - `approval_id` in `path` | required=True
- **request body:** `ApprovalDecisionRequest`

| Field | Type |
|-------|------|
| `reason` \* | string |
| `selected_value` \* | string |

> `*` = required

- **response 200:** present (see OpenAPI)

---

### `GET /api/v1/context`

- **operationId:** `read_authenticated_context_api_v1_context_get`
- **summary:** Read Authenticated Context
- **tags:** control-plane
- **existence:** Backend **Yes** | OpenAPI **Yes** | FE generated client **Yes**
- **response 200:** present (see OpenAPI)

---

### `POST /api/v1/domains/register`

- **operationId:** `register_domain_api_v1_domains_register_post`
- **summary:** Register Domain
- **tags:** definitions
- **existence:** Backend **Yes** | OpenAPI **Yes** | FE generated client **Yes**
- **request body:** `DomainRegistrationRequest`

| Field | Type |
|-------|------|
| `manifest` \* | object |

> `*` = required

- **response 200:** present (see OpenAPI)

---

### `POST /api/v1/evaluations`

- **operationId:** `run_evaluation_api_v1_evaluations_post`
- **summary:** Run Evaluation
- **tags:** evaluation
- **existence:** Backend **Yes** | OpenAPI **Yes** | FE generated client **Yes**
- **request body:** `EvaluationRunRequest`

| Field | Type |
|-------|------|
| `configuration` \* | object |

> `*` = required

- **response 201:** present (see OpenAPI)

---

### `POST /api/v1/evolution/canaries/{canary_id}/activate`

- **operationId:** `activate_canary_api_v1_evolution_canaries__canary_id__activate_post`
- **summary:** Activate Canary
- **tags:** evolution
- **existence:** Backend **Yes** | OpenAPI **Yes** | FE generated client **Yes**
- **parameters:**
  - `canary_id` in `path` | required=True
- **response 200:** present (see OpenAPI)

---

### `POST /api/v1/evolution/canaries/{canary_id}/criteria`

- **operationId:** `record_canary_criterion_api_v1_evolution_canaries__canary_id__criteria_post`
- **summary:** Record Canary Criterion
- **tags:** evolution
- **existence:** Backend **Yes** | OpenAPI **Yes** | FE generated client **Yes**
- **parameters:**
  - `canary_id` in `path` | required=True
- **request body:** `CanaryCriterionRequest`

| Field | Type |
|-------|------|
| `criterion` \* | string |
| `evidence_reference` \* | string |
| `passed` \* | boolean |

> `*` = required

- **response 200:** present (see OpenAPI)

---

### `POST /api/v1/evolution/canaries/{canary_id}/operations/authorize`

- **operationId:** `authorize_canary_operation_api_v1_evolution_canaries__canary_id__operations_authorize_post`
- **summary:** Authorize Canary Operation
- **tags:** evolution
- **existence:** Backend **Yes** | OpenAPI **Yes** | FE generated client **Yes**
- **parameters:**
  - `canary_id` in `path` | required=True
- **request body:** `CanaryOperationRequest`

| Field | Type |
|-------|------|
| `scope` \* | CanaryScopeRequest |

> `*` = required

- **response 200:** present (see OpenAPI)

---

### `POST /api/v1/evolution/promotions/assess`

- **operationId:** `assess_promotion_api_v1_evolution_promotions_assess_post`
- **summary:** Assess Promotion
- **tags:** evolution
- **existence:** Backend **Yes** | OpenAPI **Yes** | FE generated client **Yes**
- **request body:** `PromotionAssessmentRequest`

| Field | Type |
|-------|------|
| `approval_id` \* | string |
| `audit_record_ids` | array[string] |
| `canary_id` \* | string |
| `compliance` \* | MetricComparisonRequest |
| `evaluation_run_id` \* | string |
| `evidence_references` | array[string] |
| `requested_variant_id` | string | null |
| `rollback_record_id` \* | string |
| `safety` \* | MetricComparisonRequest |
| `target_metric` \* | MetricComparisonRequest |

> `*` = required

- **response 200:** present (see OpenAPI)

---

### `POST /api/v1/evolution/variants`

- **operationId:** `propose_variant_api_v1_evolution_variants_post`
- **summary:** Propose Variant
- **tags:** evolution
- **existence:** Backend **Yes** | OpenAPI **Yes** | FE generated client **Yes**
- **request body:** `SandboxVariantRequest`

| Field | Type |
|-------|------|
| `improvement_direction` \* | string |
| `production_configuration` \* | object |
| `sandbox_configuration` \* | object |
| `target_metric` \* | string |

> `*` = required

- **response 201:** present (see OpenAPI)

---

### `POST /api/v1/evolution/variants/{variant_id}/canaries`

- **operationId:** `approve_canary_api_v1_evolution_variants__variant_id__canaries_post`
- **summary:** Approve Canary
- **tags:** evolution
- **existence:** Backend **Yes** | OpenAPI **Yes** | FE generated client **Yes**
- **parameters:**
  - `variant_id` in `path` | required=True
- **request body:** `CanaryApprovalRequest`

| Field | Type |
|-------|------|
| `criteria` \* | array[string] |
| `rollback_record_id` \* | string |
| `scope` \* | CanaryScopeRequest |

> `*` = required

- **response 201:** present (see OpenAPI)

---

### `POST /api/v1/evolution/variants/{variant_id}/consider`

- **operationId:** `consider_variant_api_v1_evolution_variants__variant_id__consider_post`
- **summary:** Consider Variant
- **tags:** evolution
- **existence:** Backend **Yes** | OpenAPI **Yes** | FE generated client **Yes**
- **parameters:**
  - `variant_id` in `path` | required=True
- **response 200:** present (see OpenAPI)

---

### `POST /api/v1/evolution/variants/{variant_id}/human-approvals`

- **operationId:** `record_human_approval_api_v1_evolution_variants__variant_id__human_approvals_post`
- **summary:** Record Human Approval
- **tags:** evolution
- **existence:** Backend **Yes** | OpenAPI **Yes** | FE generated client **Yes**
- **parameters:**
  - `variant_id` in `path` | required=True
- **request body:** `PromotionApprovalRequest`

| Field | Type |
|-------|------|
| `reason` \* | string |

> `*` = required

- **response 201:** present (see OpenAPI)

---

### `POST /api/v1/evolution/variants/{variant_id}/rollback-plans`

- **operationId:** `create_rollback_plan_api_v1_evolution_variants__variant_id__rollback_plans_post`
- **summary:** Create Rollback Plan
- **tags:** evolution
- **existence:** Backend **Yes** | OpenAPI **Yes** | FE generated client **Yes**
- **parameters:**
  - `variant_id` in `path` | required=True
- **request body:** `RollbackPlanRequest`

| Field | Type |
|-------|------|
| `rollback_plan` \* | object |

> `*` = required

- **response 201:** present (see OpenAPI)

---

### `POST /api/v1/memory/retrieve`

- **operationId:** `retrieve_memory_api_v1_memory_retrieve_post`
- **summary:** Retrieve Memory
- **tags:** memory
- **existence:** Backend **Yes** | OpenAPI **Yes** | FE generated client **Yes**
- **request body:** `MemoryRetrievalRequest`

| Field | Type |
|-------|------|
| `query` \* | string |
| `requires_relationships` | boolean |

> `*` = required

- **response 200:** present (see OpenAPI)

---

### `POST /api/v1/video/artifacts`

- **operationId:** `handoff_video_artifact_api_v1_video_artifacts_post`
- **summary:** Handoff Video Artifact
- **tags:** video
- **existence:** Backend **Yes** | OpenAPI **Yes** | FE generated client **Yes**
- **request body:** `VideoArtifactHandoffRequest`

| Field | Type |
|-------|------|
| `artifact_id` \* | string |
| `parent_version_ids` | array[string] |
| `provenance_and_signoff_passed` \* | boolean |
| `quality_checks` | array[VideoNamedCheckRequest] |
| `release_checks` | array[VideoNamedCheckRequest] |
| `rights_and_consent_passed` \* | boolean |

> `*` = required

- **response 201:** present (see OpenAPI)

---

### `POST /api/v1/video/artifacts/{artifact_version_id}/release-requests`

- **operationId:** `request_video_release_readiness_api_v1_video_artifacts__artifact_version_id__release_requests_post`
- **summary:** Request Video Release Readiness
- **tags:** video
- **existence:** Backend **Yes** | OpenAPI **Yes** | FE generated client **Yes**
- **parameters:**
  - `artifact_version_id` in `path` | required=True
- **response 201:** present (see OpenAPI)

---

### `GET /api/v1/video/release-requests/{release_request_id}`

- **operationId:** `read_video_release_request_api_v1_video_release_requests__release_request_id__get`
- **summary:** Read Video Release Request
- **tags:** video
- **existence:** Backend **Yes** | OpenAPI **Yes** | FE generated client **Yes**
- **parameters:**
  - `release_request_id` in `path` | required=True
- **response 200:** present (see OpenAPI)

---

### `POST /api/v1/workflow-runs/dispatch`

- **operationId:** `dispatch_run_api_v1_workflow_runs_dispatch_post`
- **summary:** Dispatch Run
- **tags:** runs, observation
- **existence:** Backend **Yes** | OpenAPI **Yes** | FE generated client **Yes**
- **request body:** `DispatchRequest`

| Field | Type |
|-------|------|
| `confirm` | boolean |
| `idempotency_key` \* | string |
| `run_id` \* | string |

> `*` = required

- **response 200:** present (see OpenAPI)

---

### `GET /api/v1/workflow-runs/{run_id}`

- **operationId:** `read_run_api_v1_workflow_runs__run_id__get`
- **summary:** Read Run
- **tags:** runs, observation
- **existence:** Backend **Yes** | OpenAPI **Yes** | FE generated client **Yes**
- **parameters:**
  - `run_id` in `path` | required=True
- **response 200:** present (see OpenAPI)

---

### `GET /api/v1/workflow-runs/{run_id}/events`

- **operationId:** `read_run_events_api_v1_workflow_runs__run_id__events_get`
- **summary:** Read Run Events
- **tags:** runs, observation
- **existence:** Backend **Yes** | OpenAPI **Yes** | FE generated client **Yes**
- **parameters:**
  - `run_id` in `path` | required=True
- **response 200:** present (see OpenAPI)

---

### `GET /api/v1/workflow-runs/{run_id}/graph-state`

- **operationId:** `read_graph_state_api_v1_workflow_runs__run_id__graph_state_get`
- **summary:** Read Graph State
- **tags:** runs, observation
- **existence:** Backend **Yes** | OpenAPI **Yes** | FE generated client **Yes**
- **parameters:**
  - `run_id` in `path` | required=True
- **response 200:** present (see OpenAPI)

---

### `POST /api/v1/workflows/definitions`

- **operationId:** `register_definition_api_v1_workflows_definitions_post`
- **summary:** Register Definition
- **tags:** definitions
- **existence:** Backend **Yes** | OpenAPI **Yes** | FE generated client **Yes**
- **request body:** `DefinitionRequest`

| Field | Type |
|-------|------|
| `definition` \* | object |

> `*` = required

- **response 201:** present (see OpenAPI)

---

### `POST /api/v1/workflows/{workflow_id}/run`

- **operationId:** `create_run_api_v1_workflows__workflow_id__run_post`
- **summary:** Create Run
- **tags:** runs, observation
- **existence:** Backend **Yes** | OpenAPI **Yes** | FE generated client **Yes**
- **parameters:**
  - `workflow_id` in `path` | required=True
- **request body:** `RunCreateRequest`

| Field | Type |
|-------|------|
| `version` \* | string |

> `*` = required

- **response 201:** present (see OpenAPI)

---

### `GET /api/v1/workflows/{workflow_id}/topology`

- **operationId:** `read_topology_api_v1_workflows__workflow_id__topology_get`
- **summary:** Read Topology
- **tags:** runs, observation
- **existence:** Backend **Yes** | OpenAPI **Yes** | FE generated client **Yes**
- **parameters:**
  - `workflow_id` in `path` | required=True
  - `version` in `query` | required=True
- **response 200:** present (see OpenAPI)

---



### 3.A UI wiring notes for implemented APIs

| operationId group | UI entry | Notes |
|-------------------|----------|-------|
| `read_authenticated_context_*` | Ops / runtime `refreshContext` | Required for host identity display |
| `create_run_*` / `dispatch_run_*` | `interaction-runtime` canvas.run / canvas.dispatch | Requires workflow_id; Canvas buttons often stub until action ref |
| `read_run_*` / `read_graph_state_*` | OperatorApi / ops console | Opaque run_id |
| `read_approval_gate_*` / `submit_approval_decision_*` | Ops console | Decision body: `selected_value` ∈ {approved, denied} + `reason`; header Idempotency-Key |
| `run_evaluation_*` | `eval.run_campaign` | configuration object opaque digest server-side |
| `retrieve_memory_*` | knowledge.search runtime | Results are **references**, not raw restricted content |
| `evolution/*` | Not wired to Registry/Eval buttons | Map to product proposal/rollout façade later |
| `video/*` | Not redesign shell | Domain adapter only |
| `domains/register`, `workflows/definitions` | Pack/admin tooling | Not Registry Hub |

### 3.B Compatibility: workflow-runs vs product `/runs`

| Product façade (target) | Compatibility today |
|-------------------------|---------------------|
| `GET /api/v1/runs/{id}` | `GET /api/v1/workflow-runs/{run_id}` |
| `GET /api/v1/runs/{id}/graph-state` | `GET /api/v1/workflow-runs/{run_id}/graph-state` |
| `POST /api/v1/runs/{id}/dispatch` | `POST /api/v1/workflow-runs/dispatch` body `{run_id, idempotency_key, confirm}` |
| `POST /api/v1/runs/{id}/replay` | **Missing** public command |
| `POST /api/v1/runs/{id}/cancel` | **Missing** public command |

---

## 4. Product façade APIs - complete fine-tuned specs (Missing -> implement)

Canonical paths follow **`docs/backend_redesign/backend_redesign.md` §7.1**.  
UI screen sources: `ui_03`-`ui_07`, `ui_10`, `frontend_redesign.md`.

### 4.0 Shared product types

```ts
// ActionReference - returned on projections; enables mutations
type ActionReference = {
  id: string;                 // stable action instance id
  label: string;              // button label
  kind: string;               // e.g. propose_improvement | add_to_swarm | run_swarm
  eligible: boolean;
  resource_ref?: string;      // opaque target
  expires_at?: string;        // RFC3339 optional
};

type Freshness = {
  as_of: string;              // RFC3339
  state: "live" | "cached" | "stale" | "unavailable";
};

type PageCursor = {
  next_cursor: string | null;
  limit: number;
};
```

**Command body baseline (all mutations):**

```json
{
  "action_reference_id": "act_...",
  // resource fields...
}
```

**Headers (mutations):** `Idempotency-Key: <uuid>` | `Accept: application/json` | credentials include.

**Error codes (stable):** `authorization_denied`, `validation_failed`, `not_found`, `conflict`, `idempotency_conflict`, `stale_projection`, `approval_required`, `prohibited_operation`, `rate_limited`, `unavailable`.

---

### 4.1 `GET /api/v1/commons/agents`

| | |
|--|--|
| **Purpose** | Registry Hub list/search/facets (ui_07) |
| **Auth / role** | `viewer+` | scope `registry.read` |
| **Exists** | **Missing** (UI: local pack catalog) |
| **Query** | `q?`, `domain?`, `pack?`, `status?`, `min_success?`, `used_by_me?`, `compatibility?`, `cursor?`, `limit?` (max 100) |
| **Response 200 `data`** | |

```json
{
  "items": [
    {
      "id": "video.accessibility",
      "name": "Accessibility",
      "version_label": "video | registered | schema 1.0",
      "status": "active|draft|deprecated|registered",
      "description": "plain short summary (no raw markdown dump)",
      "badges": ["video", "no-network"],
      "domains": ["video"],
      "metrics": {
        "success_rate": null,
        "avg_tokens": null,
        "latency_tier": null,
        "run_count": null
      },
      "usage": {
        "global_swarms": null,
        "my_swarms": null,
        "last_used_at": null
      },
      "actions": [
        { "id": "...", "label": "Add to Swarm", "kind": "add_to_swarm", "eligible": true },
        { "id": "...", "label": "Propose Improvement", "kind": "propose_improvement", "eligible": false }
      ]
    }
  ],
  "page": { "next_cursor": null, "limit": 36 },
  "freshness": { "as_of": "...", "state": "cached" }
}
```

| **UI consumers** | RegistryHome cards/table/graph, Composer palette, Canvas palette |
| **Must not** | Return prompts, tool credentials, unredacted eval payloads |

---

### 4.2 `GET /api/v1/commons/agents/{id}/versions/{version}`

| | |
|--|--|
| **Purpose** | Agent detail host projection (ui_05); complements static SPEC.md |
| **Auth** | `registry.read` |
| **Exists** | **Missing** |
| **Response `data`** | identity, version timeline (redacted deltas), config summaries (non-secret), aggregate metrics, usage summary, eval summary refs, knowledge source refs, **`actions[]`** |
| **UI** | AgentDetailHome tabs; playground/proposal buttons enabled only via `actions` |

Related optional reads (ui_05):

| Path | Purpose |
|------|---------|
| `GET /api/v1/commons/agents/{id}/usage` | Cross-swarm usage table |
| `GET /api/v1/commons/agents/{id}/evals` | Aggregate eval samples (refs only) |
| `GET /api/v1/commons/agents/{id}/knowledge` | Knowledge subscriptions stats |

---

### 4.3 `POST /api/v1/commons/agents/{id}/proposals`

| | |
|--|--|
| **Purpose** | **Propose Improvement** (Registry + Agent detail) |
| **Auth** | `registry.propose` / `editor+` + eligible action ref |
| **Exists** | **Missing** -> UI message: *authorized proposal action* |
| **Headers** | `Idempotency-Key` required |
| **Body** | |

```json
{
  "action_reference_id": "act_propose_...",
  "base_version": "1.0.0",
  "summary": "string ≤ 2000",
  "diff_ref": "opaque content ref or structured patch id",
  "evidence_refs": ["run_...", "eval_..."],
  "rationale_ref": "optional"
}
```

| **Response 201** | `{ "proposal_id", "status": "submitted"|"pending_review"|"needs_changes", "target": { "agent_id", "base_version" }, "correlation_id", "actions": [] }` |
| **Rules** | Never mutates published immutable version; no production activation; maps to library validation + `EvaluationService` / evolution propose seam |
| **Library mapping** | backend_redesign §7.3 "Propose an improvement" |

---

### 4.4 `POST /api/v1/commons/agents/{id}/forks`

| | |
|--|--|
| **Purpose** | Fork to Custom / Fork & Customize |
| **Auth** | `editor+` + action ref `fork_agent` |
| **Headers** | `Idempotency-Key` |
| **Body** | `{ "action_reference_id", "label?", "visibility": "organization" }` |
| **Response 201** | `{ "fork_id", "forked_from": { "id", "version" }, "status": "draft" }` |
| **Exists** | **Missing** |

---

### 4.5 Patterns catalog

#### `GET /api/v1/commons/patterns`

| | |
|--|--|
| **Purpose** | Composer templates, Registry pattern cards (ui_03, ui_07) |
| **Query** | `q?`, `domain?`, `cursor?`, `limit?` |
| **Response item** | `id`, `name`, `version_label`, `when_to_use`, `metrics`, `graph_preview_ref`, `actions[]` (`instantiate`, `fork_pattern`, `propose_pattern`) |
| **Exists** | **Missing** |

#### `GET /api/v1/commons/patterns/{id}/versions/{version}`

Full pattern graph template (slots/constraints) redacted for canvas preview.

#### `POST /api/v1/commons/patterns/{id}/instantiate`

| | |
|--|--|
| **Purpose** | Load pattern into canvas / Add agents as wired graph |
| **Body** | `{ "action_reference_id", "swarm_id?" }` - creates/updates swarm draft |
| **Response** | `{ "swarm_id", "revision", "redirect_hint": "/swarms/{id}/canvas" }` |
| **Library** | Definition validation + registration |

#### `POST /api/v1/commons/patterns/proposals`

| | |
|--|--|
| **Purpose** | Propose as new Pattern / Contribute as pattern |
| **Body** | `{ "action_reference_id", "title", "description", "graph_ref", "evidence_refs[]" }` |
| **Exists** | **Missing** |

---

### 4.6 Swarms (composer + canvas)

#### `POST /api/v1/swarms`

| | |
|--|--|
| **Purpose** | Create swarm draft from composer "Load to Canvas" / goal |
| **Auth** | `editor+` |
| **Body** | `{ "action_reference_id", "name", "pattern_ref?", "goal_summary?", "initial_graph?" }` |
| **Response 201** | `{ "swarm_id", "revision": 1, "status": "draft" }` |
| **Exists** | **Missing** (local draft only) |

#### `GET /api/v1/swarms/{id}`

| | |
|--|--|
| **Purpose** | Canvas load; pins, policy, last run summary, **actions** (run, validate, export, share) |
| **Exists** | **Missing** |

#### `PATCH /api/v1/swarms/{id}/graph`

| | |
|--|--|
| **Purpose** | Graph node/edge/layout mutation (new revision) |
| **Headers** | `Idempotency-Key` | optimistic `If-Match: revision` or body `expected_revision` |
| **Body** | |

```json
{
  "action_reference_id": "...",
  "expected_revision": 12,
  "graph": {
    "nodes": [
      {
        "id": "verify",
        "kind": "common_agent",
        "common_agent": { "id": "research-verifier", "version": "1.8" },
        "position": { "x": 820, "y": 380 },
        "overrides": null
      }
    ],
    "edges": [
      { "id": "e1", "source": "research", "target": "verify", "kind": "data" }
    ],
    "policy": { "cost_cap": "25.00", "requires_verification": true }
  }
}
```

| **Rules** | `custom_agent` requires `forked_from` or `custom_reason`; never rewrite historical run provenance |
| **Response** | `{ "swarm_id", "revision": 13, "validation": { "ok": true, "issues": [] } }` |
| **Exists** | **Missing** |

#### `POST /api/v1/swarms/{id}/validate`

Compile graph -> workflow definition validation (tools, budget, verification, rollback, approval policy). No execution.

#### `POST /api/v1/swarms/{id}/runs`  (product "run swarm")

| | |
|--|--|
| **Purpose** | Canvas Run / portal `swarms/{id}/run` |
| **Body** | `{ "action_reference_id", "inputs_ref?", "pin_commons": true, "confirm_dispatch"?: false }` |
| **Response** | `{ "run_id", "status": "queued", "events_topics": ["run:{id}", "swarm:{swarm_id}"], "actions": [] }` |
| **Library mapping** | create_run -> preview_or_dispatch (existing workflow-runs) |
| **Exists** | **Missing** façade (compat path exists) |

#### `POST /api/v1/swarms/{id}/members` (Add to Swarm)

| | |
|--|--|
| **Purpose** | Registry **Add to Swarm / Instantiate** |
| **Body** | `{ "action_reference_id", "agent_id", "agent_version?", "pin_policy?": "exact|latest_compatible" }` |
| **Response** | `{ "swarm_id", "revision", "node_id" }` |
| **Exists** | **Missing** |

#### `POST /api/v1/swarms/{id}/pins`

| | |
|--|--|
| **Purpose** | Pin / Update commons in swarms (agent detail, canvas) |
| **Body** | `{ "action_reference_id", "pins": [{ "node_id"?, "agent_id", "version" }] }` |
| **Exists** | **Missing** |

#### `POST /api/v1/swarms/{id}/exports`

| | |
|--|--|
| **Purpose** | Canvas export |
| **Body** | `{ "action_reference_id", "format": "json|yaml" }` |
| **Response** | `{ "export_id", "download_ref", "expires_at" }` (no inline secrets) |
| **Exists** | **Missing** |

---

### 4.7 Runs product surface

| Method / path | Purpose | Maps from / Exists |
|---------------|---------|-------------------|
| `GET /api/v1/runs/{id}` | Run projection | Compat: workflow-runs GET **Exists** |
| `GET /api/v1/runs/{id}/graph-state` | Node/edge status + previews | Compat **Exists** |
| `POST /api/v1/runs/{id}/dispatch` | Confirm dispatch | Compat body form **Exists** |
| `POST /api/v1/runs/{id}/pause` | Pause | **Missing** |
| `POST /api/v1/runs/{id}/replay` | Full/partial replay | **Missing** (Canvas stub) |
| `POST /api/v1/runs/{id}/cancel` | Cancel | **Missing** (Canvas stub) |

**Cancel body:** `{ "action_reference_id", "reason?" }` -> `{ "run_id", "status": "cancelling"|"cancelled" }`  
Statuses include VA/backend recovery set: `queued`, `running`, `self_refine`, `waiting_for_critique`, `blocked`, `failed`, `complete`, `cancelling`, `cancelled`, `manual_recovery_required`.

---

### 4.8 Dashboard & activity

| Method / path | Purpose | Query | Exists |
|---------------|---------|-------|--------|
| `GET /api/v1/commons/health` | Dashboard common health | - | Missing |
| `GET /api/v1/swarms/running` | Fleet running | `cursor?` | Missing |
| `GET /api/v1/activity` | Activity feed | time, swarm, status, common_version, outdated, cursor | Missing |
| `GET /api/v1/activity/insights` | KPIs/charts | same filters | Missing |
| `GET /api/v1/insights/common-impact` | Impact of common versions | version ids | Missing |
| `GET /api/v1/activity-projections/{subject_reference}` | Single subject projection | - | **Exists** (not OpenAPI FE) |

**Activity item projection:** subject refs, category, severity, redacted summary, common versions used, status, timestamps, correlation_id, **actions** (replay, open canvas, create proposal).

---

### 4.9 Approvals inbox

| Method / path | Purpose | Exists |
|---------------|---------|--------|
| `GET /api/v1/approvals` | Inbox list for reviewers | Missing |
| `GET /api/v1/approvals/{id}` | Gate detail | **Exists** |
| `POST /api/v1/approvals/{id}/decision` | Decide | **Exists** |

**List item:** `approval_id`, `run_id`, `risk_tier`, `gate_status`, `created_at`, `action_preview`, `actions[]`.  
**Decision request (implemented):** `{ "selected_value": "approved"|"denied", "reason": string≤2000 }` + **Idempotency-Key**.  
**Rule:** Decision cannot attach a new client effect payload; server re-authorizes held operation.

---

### 4.10 Events / SSE

#### Target product: `GET /api/v1/events/stream?topics=`

| | |
|--|--|
| **Query** | `topics` comma-separated: `commons:health`, `commons:{agent_id}`, `swarm:{id}`, `run:{id}`, `approvals:{org}`, `activity:new`, `rollout:{id}` |
| **Headers** | `Last-Event-ID` optional |
| **Auth** | On connect **and** per event publish |
| **Event frame** | `id`, `event`, `data` JSON redacted |
| **Exists** | **Mismatch** - backend has `GET /api/v1/events/{topic}/stream` |
| **UI** | `frontend/src/lib/live/sse-subscription.ts` hard-requires `/api/v1/events/stream` |

**Fine-tune decision (implement one):**

1. **Preferred:** Add `GET /api/v1/events/stream` multi-topic alias that fans in authorized topics.  
2. Or change FE to open one stream per topic using existing path.

SSE never executes commands.

---

### 4.11 Evolution / rollout (product mapping to existing library APIs)

Product UI wants rollout/A/B; library already has:

| Product intent | Existing Host API | UI today |
|----------------|-------------------|----------|
| Propose sandbox variant | `POST /api/v1/evolution/variants` | Stub |
| Consider variant | `POST .../variants/{id}/consider` | Stub |
| Rollback plan | `POST .../rollback-plans` | Stub |
| Human promotion approval | `POST .../human-approvals` | Stub |
| Approve canary | `POST .../canaries` | Stub |
| Activate canary | `POST .../canaries/{id}/activate` | Stub |
| Record criterion | `POST .../criteria` | Stub |
| Authorize canary op | `POST .../operations/authorize` | Stub |
| Assess promotion | `POST .../promotions/assess` | Stub |

**Product façade (optional thin):**  
`POST /api/v1/rollouts` / `PUT /api/v1/evolution/rollouts/{id}` wrapping the above with ActionReferences and impact projection (`GET /api/v1/rollouts/{id}/impact`).

**SandboxVariantRequest (implemented):**

| Field | Type |
|-------|------|
| `production_configuration` * | object |
| `sandbox_configuration` * | object |
| `target_metric` * | string |
| `improvement_direction` * | `increase` \| `decrease` |

**CanaryApprovalRequest:** `scope` {workflow_id?, case_id?}, `criteria[]`, `rollback_record_id`.  
**Rule:** Failed criterion stops rollout + rollback lifecycle; no silent production apply.

---

### 4.12 Knowledge

| Method / path | Purpose | Exists |
|---------------|---------|--------|
| `POST /api/v1/memory/retrieve` | Retrieval | **Yes** (wire Knowledge Home fully) |
| `POST /api/v1/knowledge/sources` | Add source | Missing |
| `POST /api/v1/knowledge/sources/{id}/sync` | Git/sync job | Missing |
| `POST /api/v1/knowledge/contributions` | Distill/contribute | Missing |

**Retrieve request (implemented):** `{ "query": string, "requires_relationships"?: bool }`  
**Retrieve response:** `results[]` with `tier`, `content_reference`, `source_record_ids`, `provenance[]`, `confidence`; `no_knowledge`; `searched_tiers`; `correction_control`.

**Add source body (spec):**  
`{ "action_reference_id", "type": "upload|url|git", "display_name", "uri?", "retention_class?" }`  
Server owns malware/size/type validation; browser never treats URL as executable.

---

### 4.13 Playground

#### `POST /api/v1/commons/agents/{id}/playground-runs`

| | |
|--|--|
| **Purpose** | Agent detail Playground test (ui_05) |
| **Body** | `{ "action_reference_id", "prompt_ref_or_text", "model_override?", "enable_tools": false, "swarm_context_ref?", "stream": true }` |
| **Rules** | No production activation; host budget/tool policy; return redacted transcript refs + metrics |
| **Exists** | **Missing** |
| **UI today** | Stub: playground requires authorized playground action |

---

### 4.14 Settings, secrets, developer platform

| Method / path | Purpose | UI | Exists |
|---------------|---------|-----|--------|
| `GET/PUT /api/v1/settings/workspace` | Workspace prefs | Settings | Missing |
| `POST /api/v1/settings/providers` | Add/test provider | Settings | Missing |
| `POST /api/v1/settings/providers/{id}/test` | Test connection | Settings | Missing |
| `POST /api/v1/settings/providers/{id}/models:fetch` | Fetch models | Settings | Missing |
| `POST /api/v1/secrets` | Create secret (value once) | Settings | Missing |
| `POST /api/v1/secrets/{id}/rotate` | Rotate | Settings | Missing |
| `POST /api/v1/secrets/{id}/reveal` | Audited reveal | Settings | Missing |
| `POST /api/v1/workspace/invites` | Invite member | Settings | Missing |
| `POST /api/v1/developer/tokens` | API key show-once | API Portal | Missing |
| `POST /api/v1/developer/webhooks` | Webhook endpoint | API Portal | Missing |
| `GET /api/v1/openapi.json` | Contract | tooling | Platform (backend_redesign health table) |

**Secret rule:** raw value never returned after create; only `secret_id` + metadata.

---

### 4.15 Finance, audit, notifications, profile

| Method / path | Purpose | Exists |
|---------------|---------|--------|
| `GET /api/v1/finance/summary` | Costs landing | Missing |
| `POST /api/v1/finance/budgets` | Set budget | Missing |
| `POST /api/v1/finance/exports` | Export report | Missing |
| `POST /api/v1/audit/exports` | CSV/JSON export job | Missing |
| `POST /api/v1/audit/integrity-checks` | Verify integrity | Missing |
| `GET /api/v1/notifications` | Inbox | Missing |
| `POST /api/v1/notifications/mark-read` | Mark read | Missing (local only) |
| `PUT /api/v1/actors/me/preferences` | Profile prefs | Missing (local only) |

Exports return **job id + download ref**, not unbounded inline payloads.

---

### 4.16 Collaboration & blueprints

| Method / path | Purpose | Exists |
|---------------|---------|--------|
| `POST /api/v1/collaboration/shares` | Share resource | Missing |
| `GET /api/v1/collaboration/presence` | Presence | Missing |
| `GET/POST /api/v1/blueprints` | Catalog / create | Missing |
| `POST /api/v1/blueprints/{id}/deploy` | Deploy | Missing |
| `POST /api/v1/blueprints/{id}/forks` | Fork | Missing |
| `POST /api/v1/blueprints/import` | Import JSON/YAML | Missing |

Deploy must never activate production agents from catalog stubs alone (UI already fail-closed).

---

### 4.17 Composer recommend (optional Phase 2)

ui_03 mentions `POST /api/composer/recommend` streaming suggestions.  
**Normative product path:** `POST /api/v1/composer/recommendations`  

| Body | `{ "action_reference_id?", "goal": string, "constraints?" }` |
| Response / stream | Inert structured `{ pattern_id, agent_slots[], est_metrics, graph_suggestion_ref, rationale }` |
| Rules | Observation only; "Load to Canvas" is separate instantiate action |

**Exists:** **Missing**

---

## 5. UI control -> API mapping (complete)

| UI surface | Control | Required API | Exists | Wiring |
|------------|---------|--------------|--------|--------|
| Login | Submit credentials | FE `/api/auth/login` | Yes | Live |
| Registry | Search/list cards | `GET /commons/agents` | No | Local |
| Registry | Add to Swarm | `POST /swarms/{id}/members` | No | Stub |
| Registry | Propose Improvement | `POST /commons/agents/{id}/proposals` | No | Stub |
| Registry | Fork pattern | `POST /commons/patterns/{id}/forks` | No | Stub |
| Registry | Governance merge | Proposal review + approvals | Partial | Stub |
| Agent detail | View SPEC | Static `/docs/agents/.../SPEC.md` | Yes static | Live markdown |
| Agent detail | Propose Improvement | proposals API | No | Stub |
| Agent detail | A/B / rollout | evolution/canary or rollouts façade | Partial library | Stub |
| Agent detail | Fork | agent forks | No | Stub |
| Agent detail | Pin/update swarms | pins API | No | Stub |
| Agent detail | Playground | playground-runs | No | Stub |
| Agent detail | Replay latest | runs replay | No | Stub |
| Composer | Save draft host | `POST /swarms` | No | Local/stub |
| Composer | Load template | patterns list + instantiate | No | Stub |
| Composer | Compose send | `POST /swarms` + graph | No | Stub |
| Canvas | Load graph | `GET /swarms/{id}` | No | Local |
| Canvas | Mutate graph | `PATCH /swarms/{id}/graph` | No | Preview/stub |
| Canvas | Run | `POST /swarms/{id}/runs` -> library run/dispatch | Partial | Mixed |
| Canvas | Cancel | runs cancel | No | Stub |
| Canvas | Export | swarms export | No | Stub |
| Activity | Feed | `GET /activity` | No | Local |
| Activity | Live | SSE stream | Mismatch | Partial |
| Knowledge | Search | memory/retrieve | Yes | Partial |
| Knowledge | Add/sync/contribute | knowledge/* | No | Stub |
| Eval | Run campaign | evaluations | Yes | Partial |
| Eval | Approve merge | human-approvals / proposals | Partial | Stub |
| Ops console | Approval decide | approvals decision | Yes | Live |
| Settings | Providers/secrets | settings/* secrets/* | No | Stub |
| Costs | Budget/export | finance/* | No | Stub |
| Audit | Export/verify | audit/* | No | Stub |
| API Portal | Tokens/webhooks | developer/* | No | Stub |
| Blueprints | Deploy/fork | blueprints/* | No | Stub |
| Collaboration | Share | collaboration/* | No | Stub |

---

## 6. Delivery phases (acceptance)

Aligned with backend_redesign §10 + frontend Phase 1-2:

| Phase | APIs | Accept when |
|-------|------|-------------|
| **A** | Auth context, SSE align, envelopes, idempotency | Unauth fails; stream reconnect; correlation IDs |
| **B** | commons agents/patterns + swarm graph drafts | Registry + Canvas use real API data |
| **C** | swarm runs, activity, approvals inbox, replay/cancel | User can create->validate->dispatch->observe->approve |
| **D** | proposals, eval evidence, contributions, rollouts | No silent common mutation; canary fail-closed |

---

## 7. Regenerating this document

```bash
python scripts/tmp_generate_api_specs_md.py   # OpenAPI field tables
python scripts/tmp_assemble_ui_api_matrix.py  # assemble full matrix
```

Or re-run after OpenAPI contract release updates.

---

*End of fine-tuned matrix. Prefer Host-returned ActionReferences over UI invention. Existing `/workflow-runs/*` remain compatibility APIs; product UI should converge on `/commons/*`, `/swarms/*`, `/runs/*`, `/activity`, `/events/stream` as implemented.*
