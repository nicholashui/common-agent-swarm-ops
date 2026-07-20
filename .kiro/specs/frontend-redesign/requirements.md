# Requirements Document

## Introduction

Frontend_Redesign delivers the TypeScript/Next.js control-plane user interface for common-agent-swarm-ops. Frontend_Redesign consumes generated, versioned `/api/v1` REST contracts and authorized Server-Sent Events (SSE). Backend_Redesign remains the authority for identity, tenancy, authorization, governance, execution, evidence, recovery, and content safety.

## Scope and Authority

The supplied frontend-redesign document, VA mapping, backend-redesign document, and Backend_Redesign requirements are binding integration inputs. The approved scope includes the authenticated shell, dashboard, registry, composer, graph canvas, agent and pattern detail, activity, approvals, rollouts, knowledge and artifact views, evaluation, notifications, audit, VA views, and responsive mobile operations views. Settings, developer, collaboration, cost, and blueprint experiences may appear only when an authorized generated contract supports each resource or action. This specification excludes browser-accessible credential vaults, direct provider or tool access, raw artifact retrieval, browser-side external-import fetching, and browser authority over tenant, governance, policy, or execution decisions.

## Glossary

- **Frontend_Redesign**: The TypeScript/Next.js control-plane user interface specified by this document.
- **Backend_Redesign**: The versioned browser-facing control-plane façade specified by the backend-redesign specification.
- **Public_API**: The documented REST and SSE contract rooted at `/api/v1`.
- **OpenAPI_Document**: The versioned machine-readable Public_API schema at `/api/v1/openapi.json`.
- **Generated_Client**: TypeScript request functions and types generated from, or schema-checked against, OpenAPI_Document.
- **Public_Envelope**: The `data`/`meta.correlation_id` success body or redaction-safe `error` body returned by Public_API.
- **Session_Context**: The authenticated browser session from which Backend_Redesign derives organization, actor, and permission scope.
- **Authorized_Projection**: A tenant-scoped, redacted resource view returned by Public_API.
- **Protected_Field**: A field absent from an Authorized_Projection because the current Session_Context is not authorized to receive the field.
- **Opaque_Reference**: A server-issued identifier or link that conveys no authority until Backend_Redesign authorizes use of the reference.
- **Action_Reference**: A server-returned, authorized reference, label, and eligibility state for one permissible mutation, recovery, or navigation action.
- **Evidence_Reference**: A server-returned, redacted reference to evidence that the current Session_Context may view.
- **Command_Intent**: One user-requested state-changing operation.
- **Idempotency_Identity**: The stable `Idempotency-Key` assigned to one Command_Intent.
- **Terminal_Outcome**: A server-returned final Authorized_Projection or final Operational_Event for a Command_Intent.
- **Retry-After**: The public delay value returned with a Public_API rate-limit response.
- **Command_Reconciliation**: Resolution of an uncertain Command_Intent using the same Idempotency_Identity and an authorized command or resource projection.
- **REST_Snapshot**: An authoritative Authorized_Projection obtained through a Public_API read operation.
- **SSE_Subscription**: An authorized connection to `/api/v1/events/stream` for a narrow server-authorized topic set.
- **Event_Cursor**: The last applied SSE event identifier retained for one SSE_Subscription scope.
- **Expected_Event_Sequence**: The sequence immediately following the event sequence in a REST_Snapshot or the most recently applied Operational_Event for one resource and subscription scope.
- **Operational_Event**: A typed, redacted, sequence-identified event delivered through SSE_Subscription.
- **Resynchronization**: Discarding affected incremental state, loading a REST_Snapshot, and creating an SSE_Subscription from the snapshot’s returned sequence context before applying later events.
- **Projection_Freshness**: Server-provided `as_of`, freshness, and degraded-state information for an Authorized_Projection.
- **Stale_Projection**: An Authorized_Projection whose Projection_Freshness does not support a current-state assertion.
- **Freshness_Critical_Action**: An Action_Reference whose returned eligibility requires a current Authorized_Projection.
- **Correlation_Identifier**: A redaction-safe identifier that links a command, projection, event, and support evidence.
- **Common_Agent_Version**: An immutable versioned reusable agent contract.
- **Common_Pattern_Version**: An immutable versioned reusable swarm-pattern contract.
- **Swarm_Instance**: An organization-scoped composition of Common_Agent_Version and Common_Pattern_Version references.
- **Graph_Revision**: An immutable version of a Swarm_Instance graph.
- **Run_Projection**: A redacted view of a run and its pinned Graph_Revision, common versions, state, metrics, and Action_References.
- **Task_Projection**: A redacted run-scoped node state with lifecycle, dependency, checkpoint, retry, and recovery information.
- **Artifact_Projection**: A redacted, versioned artifact view with lineage, validation, rights, quality, delivery, and provenance references.
- **Quality_Evidence**: Separate server-provided L1 specification, L2 rubric, L3 baseline, critique, and gate evidence.
- **Approval_Gate**: A server-owned decision point with evidence revision, expiry, and authorized decision Action_References.
- **Rollout_Campaign**: A bounded version-release operation with target scope, criteria, approval, monitoring, and rollback projections.
- **VA_Projection**: A domain-adapter projection containing VA production metadata represented through common control-plane contracts.
- **Untrusted_Content**: User, artifact, import, event, tool-summary, or model-produced content that cannot grant authority or execute in Frontend_Redesign.
- **Import_Projection**: A redacted view of server-side artifact or knowledge import validation, quarantine, processing, indexing, rejection, archival, ownership, and retention state.
- **Operational_Screen**: An authorized dashboard, activity, canvas, approval, rollout, monitoring, notification, or mobile-operations view.
- **Supported_Mobile_Viewport**: A viewport from 320 through 767 CSS pixels wide.
- **Accessible_Live_Region**: A `role="status"`, `aria-live="polite"`, and `aria-atomic="true"` interface region.
- **Session_Safe_Cache**: Browser-stored Authorized_Projection data and Event_Cursor values that exclude credentials, tokens, Protected_Fields, raw protected content, and privileged artifact content.
- **Allowed_Action_Contract**: A server-provided authorization result that permits navigation to an externally addressed destination.

## Requirements

### Requirement 1: Generated and versioned client integration

**User Story:** As a Frontend_Redesign developer, I want generated public contracts, so that the user interface cannot silently diverge from Backend_Redesign.

#### Acceptance Criteria

1. WHEN continuous integration evaluates a change to OpenAPI_Document or Generated_Client, THE Frontend_Redesign SHALL generate or schema-check Generated_Client from the versioned OpenAPI_Document.
2. IF continuous integration finds that regenerated Generated_Client output differs from the committed artifact or that schema checking fails, THEN THE Frontend_Redesign SHALL fail the integration build.
3. WHEN Frontend_Redesign invokes a Public_API operation, THE Frontend_Redesign SHALL use the Generated_Client request function and generated request and response types for the operation.
4. WHEN a Public_Envelope contains successful data, THE Frontend_Redesign SHALL map only the generated successful-data fields to view state.
5. WHEN a Public_Envelope contains an error, THE Frontend_Redesign SHALL map only the returned error code, redaction-safe message, retryability, and Correlation_Identifier to view state.
6. WHILE a Public_API compatibility route remains supported, THE Frontend_Redesign SHALL render the generated Public_API projection rather than an unversioned browser contract.

### Requirement 2: Authorized and redacted tenant projections

**User Story:** As an organization user, I want authorized redacted views, so that Frontend_Redesign displays only resources and evidence available to my Session_Context.

#### Acceptance Criteria

1. WHEN Frontend_Redesign requests an Authorized_Projection, THE Frontend_Redesign SHALL use Session_Context without supplying organization, actor, or permission authority.
2. WHEN Frontend_Redesign renders an Authorized_Projection, THE Frontend_Redesign SHALL render only fields present in the Authorized_Projection received for the active Session_Context.
3. WHEN an Authorized_Projection omits a Protected_Field, THE Frontend_Redesign SHALL omit the Protected_Field value, label, placeholder, DOM node, accessibility-tree node, and client-derived fallback from the rendered view.
4. IF Public_API returns an authorization, visibility, or policy error, THEN THE Frontend_Redesign SHALL display only the returned redaction-safe error without inferring protected resource state.
5. WHEN a user selects an Opaque_Reference, THE Frontend_Redesign SHALL request the referenced projection or action through Public_API.
6. WHEN Frontend_Redesign displays a Correlation_Identifier, THE Frontend_Redesign SHALL provide a control named `Copy correlation identifier` that copies only the returned Correlation_Identifier.
7. WHEN a view renders an available command, recovery, or navigation control, THE Frontend_Redesign SHALL render only the corresponding returned Action_Reference.
8. WHEN a view renders evidence, THE Frontend_Redesign SHALL render only the corresponding returned Evidence_Reference and its returned redacted presentation fields.
9. THE Frontend_Redesign SHALL exclude credentials, access tokens, raw prompts, Protected_Fields, protected artifact content, raw tool arguments, raw tool results, object-storage locations, provider errors, queue names, and internal trace payloads from rendered projections.

### Requirement 3: Idempotent state-changing commands

**User Story:** As an operator, I want command submission to survive duplicate interaction and recoverable network failure, so that Frontend_Redesign does not create a second governed effect.

#### Acceptance Criteria

1. WHEN a user initiates a Command_Intent, THE Frontend_Redesign SHALL assign exactly one Idempotency_Identity to the Command_Intent before its first submission.
2. WHEN Frontend_Redesign submits or reconciles a Command_Intent, THE Frontend_Redesign SHALL send the existing Idempotency_Identity with the authorized Public_API command.
3. WHILE a Command_Intent is pending or reconciling, THE Frontend_Redesign SHALL disable the initiating Action_Reference control.
4. WHEN Public_API accepts a Command_Intent with a queued response, THE Frontend_Redesign SHALL render the returned pending resource or run reference without presenting a terminal outcome.
5. IF a Command_Intent has an ambiguous transport outcome, THEN THE Frontend_Redesign SHALL retain the existing Idempotency_Identity and enter Command_Reconciliation.
6. IF a Command_Intent receives a rate-limit, authorization-denied, policy-denied, or Approval_Gate-denied outcome, THEN THE Frontend_Redesign SHALL retain the existing Idempotency_Identity with the Command_Intent.
7. WHEN Command_Reconciliation returns an Authorized_Projection, THE Frontend_Redesign SHALL replace the pending Command_Intent state with the returned Authorized_Projection state.
8. IF Public_API returns a rate-limit response, THEN THE Frontend_Redesign SHALL display the returned public message and returned Retry-After countdown without automatically resubmitting the Command_Intent.
9. IF Public_API returns an authorization, policy, or Approval_Gate error for a Command_Intent, THEN THE Frontend_Redesign SHALL display the returned redaction-safe error and returned Action_Reference, if present.
10. IF Public_API returns a manual-recovery or dead-letter projection, THEN THE Frontend_Redesign SHALL display the returned recovery status, failure summary, Correlation_Identifier, and returned escalation Action_Reference, if present.
11. WHEN a user retries or reconciles an unresolved Command_Intent, THE Frontend_Redesign SHALL reuse its sole retained Idempotency_Identity.
12. THE Frontend_Redesign SHALL present a Command_Intent as completed only after Public_API returns a Terminal_Outcome.

### Requirement 4: Authorized ordered SSE replay and REST resynchronization

**User Story:** As an operator, I want recoverable live projections, so that operational screens do not silently continue from an unknown state.

#### Acceptance Criteria

1. WHEN an Operational_Screen loads a live resource, THE Frontend_Redesign SHALL load a REST_Snapshot and establish its Expected_Event_Sequence before applying an Operational_Event for that resource.
2. WHEN Frontend_Redesign starts an SSE_Subscription, THE Frontend_Redesign SHALL request only server-authorized topics for the selected resource scope.
3. WHEN an SSE_Subscription receives an Operational_Event whose resource scope, generated schema version, and sequence equal the Expected_Event_Sequence, THE Frontend_Redesign SHALL apply the Operational_Event to corresponding incremental view state.
4. WHEN Frontend_Redesign applies an Operational_Event, THE Frontend_Redesign SHALL advance Expected_Event_Sequence to the immediate next sequence and retain the event identifier as Event_Cursor for the SSE_Subscription scope.
5. WHEN an SSE_Subscription disconnects, THE Frontend_Redesign SHALL display `Reconnecting` or `Stale` for each affected projection until reconnection or Resynchronization succeeds.
6. IF SSE replay is bounded, expired, denied, schema-incompatible, duplicated, out of order, or sequence-gapped, THEN THE Frontend_Redesign SHALL stop applying incremental events for the affected resource and begin Resynchronization.
7. WHEN Resynchronization begins, THE Frontend_Redesign SHALL discard the affected incremental view state and Event_Cursor.
8. WHEN Resynchronization receives a REST_Snapshot, THE Frontend_Redesign SHALL replace the affected view state and establish Expected_Event_Sequence from the returned snapshot sequence context.
9. WHEN Resynchronization establishes Expected_Event_Sequence, THE Frontend_Redesign SHALL create a new SSE_Subscription from the returned sequence context before applying a later Operational_Event.
10. THE Frontend_Redesign SHALL not apply an Operational_Event whose sequence differs from Expected_Event_Sequence.
11. THE Frontend_Redesign SHALL not infer execution, approval, quality, rights, provenance, or recovery state from SSE connection state.

### Requirement 5: Truthful health, freshness, and alert presentation

**User Story:** As an authorized operations user, I want truthful operational status, so that Frontend_Redesign does not present delayed or degraded projections as live.

#### Acceptance Criteria

1. WHEN an authorized Operational_Screen requests operational health, THE Frontend_Redesign SHALL use the generated `/api/v1/health` contract.
2. WHEN an Operational_Screen renders a health or aggregate projection, THE Frontend_Redesign SHALL render the returned `as_of`, freshness, and degraded-state values.
3. WHEN an Operational_Screen renders live, delayed, reconnecting, degraded, unavailable, stale, or recovery-required state, THE Frontend_Redesign SHALL render the exact returned state label and an icon with accessible name `Status: <returned state label>` independent of color.
4. WHILE an Operational_Screen displays a Stale_Projection, THE Frontend_Redesign SHALL disable every returned Freshness_Critical_Action and block invocation of each disabled action.
5. WHILE an Operational_Screen displays a Stale_Projection, THE Frontend_Redesign SHALL render `Stale` rather than `Live` for the affected projection.
6. WHEN an Operational_Screen displays a Stale_Projection, THE Frontend_Redesign SHALL provide a returned refresh or reconnect Action_Reference when Public_API supplies one.
7. WHEN a health or alert projection identifies a delayed event, queue or run backlog, Approval_Gate expiry, replay gap, outbox lag, or Rollout_Campaign rollback, THE Frontend_Redesign SHALL display the returned redacted summary and affected Opaque_Reference.
8. THE Frontend_Redesign SHALL exclude liveness and readiness endpoint data from every Operational_Screen.

### Requirement 6: Common registry, dashboard, activity, and graph views

**User Story:** As a swarm operator and editor, I want common-first discovery, fleet views, and graph-native composition, so that I can evaluate and operate versioned reusable components with complete provenance.

#### Acceptance Criteria

1. WHEN the dashboard loads an Authorized_Projection, THE Frontend_Redesign SHALL display the returned redacted common-component health, fleet state, approval alert, backlog, and common-version impact summaries.
2. WHEN a registry result represents a Common_Agent_Version or Common_Pattern_Version, THE Frontend_Redesign SHALL display the returned immutable identifier, version, status, provenance reference, compatibility state, and aggregate metrics.
3. WHEN a user filters the registry or activity view, THE Frontend_Redesign SHALL submit only generated Public_API filter values.
4. WHEN an agent or pattern detail view loads, THE Frontend_Redesign SHALL display the returned published contract, version history, evaluation summary, usage summary, and Evidence_References.
5. WHEN an activity view loads a Run_Projection, THE Frontend_Redesign SHALL display the returned pinned Graph_Revision and Common_Agent_Version or Common_Pattern_Version references.
6. WHEN an activity view loads a Task_Projection, THE Frontend_Redesign SHALL display the returned lifecycle, dependency, checkpoint, retry, failure, and recovery information.
7. WHEN an activity view applies an authorized Operational_Event, THE Frontend_Redesign SHALL add only the returned redacted summary and Correlation_Identifier to the activity timeline.
8. WHEN a Graph_Revision renders node relationships, THE Frontend_Redesign SHALL distinguish returned data-flow, state-flow, and iteration relationships without color as the only distinction.
9. WHEN a graph contains a Common_Agent_Version or Common_Pattern_Version, THE Frontend_Redesign SHALL display its returned immutable version and provenance reference on the graph representation.
10. WHEN a graph contains a custom agent, THE Frontend_Redesign SHALL display the returned fork origin or custom reason.
11. WHEN a Graph_Revision renders a task node, THE Frontend_Redesign SHALL display the corresponding returned Task_Projection lifecycle state and redacted status detail.
12. IF graph validation returns an ineligible result, THEN THE Frontend_Redesign SHALL disable the returned run Action_Reference and block invocation of a run command.
13. WHEN a Run_Projection exposes retry, skip, cancel, replay, or escalation eligibility, THE Frontend_Redesign SHALL render only the corresponding returned Action_Reference.
14. WHEN a user invokes a graph mutation or run action, THE Frontend_Redesign SHALL submit the returned Action_Reference as a Command_Intent.
15. WHILE a graph canvas has a Stale_Projection, THE Frontend_Redesign SHALL render `Stale` rather than asserting that a task, Approval_Gate, or Rollout_Campaign is live.
16. WHEN graph validation returns category results, THE Frontend_Redesign SHALL display only the returned version, schema, tool-policy, budget, verification, rollback, and approval category results.
17. WHEN a Task_Projection has lifecycle `queued`, `running`, `self_refine`, `waiting_for_critique`, `blocked`, `failed`, `complete`, `cancelling`, `cancelled`, or `manual_recovery_required`, THE Frontend_Redesign SHALL render the exact lifecycle label and returned redacted status detail.
18. WHEN a user selects a Common_Pattern_Version for composition, THE Frontend_Redesign SHALL request only the returned server-authorized instantiation Action_Reference.

### Requirement 7: Evidence-based approvals and rollouts

**User Story:** As a reviewer or release owner, I want evidence-bound decision and rollout views, so that Frontend_Redesign cannot bypass server governance.

#### Acceptance Criteria

1. WHEN an Approval_Gate is projected, THE Frontend_Redesign SHALL display only the returned pending operation, evidence revision, criteria, expiry, redacted artifact references, Quality_Evidence references, and decision Action_References.
2. WHEN a Quality_Evidence projection is displayed, THE Frontend_Redesign SHALL distinguish returned L1 specification validation, L2 role-rubric evaluation, L3 baseline preference, critique, gate outcome, and human approval evidence.
3. IF an Approval_Gate evidence revision changes before a decision submission, THEN THE Frontend_Redesign SHALL require a fresh Approval_Gate projection before enabling the decision Action_Reference.
4. WHILE an Approval_Gate or Rollout_Campaign projection is stale, THE Frontend_Redesign SHALL disable and block invocation of every irreversible Freshness_Critical_Action.
5. WHEN a Rollout_Campaign projection loads, THE Frontend_Redesign SHALL display only the returned selected version, bounded target scope, impact summary, criteria, approval state, rollback reference, status, and outcome measurements.
6. WHEN a Rollout_Campaign exposes an A/B, canary, promotion, rollback, or review action, THE Frontend_Redesign SHALL render only the corresponding returned Action_Reference.
7. WHEN a rollout criterion fails, THE Frontend_Redesign SHALL display the returned stopped progression and rollback state.
8. THE Frontend_Redesign SHALL not create an Approval_Gate decision, rollout target scope, success criterion, rollback instruction, policy override, or evidence from client-derived data.

### Requirement 8: Safe artifact, knowledge, and import experience

**User Story:** As a contributor, I want safe artifact and knowledge ingress views, so that imported content cannot become browser authority or bypass server validation.

#### Acceptance Criteria

1. WHEN an artifact or knowledge form loads, THE Frontend_Redesign SHALL display the returned file type, size, ownership, and retention requirements.
2. WHEN a user submits an artifact or import reference, THE Frontend_Redesign SHALL submit the content or reference only through a generated authorized ingestion contract.
3. WHEN an Import_Projection changes state, THE Frontend_Redesign SHALL display only the returned `validating`, `quarantined`, `processing`, `indexed`, `rejected`, or `archived` state.
4. WHEN an artifact or knowledge view renders an Import_Projection, THE Frontend_Redesign SHALL display only returned Opaque_References and redacted scan or indexing results.
5. WHEN a user enters an external import URL, THE Frontend_Redesign SHALL submit the external import URL as Untrusted_Content to Public_API.
6. WHEN an external import URL is present in Untrusted_Content, THE Frontend_Redesign SHALL perform no browser network request, navigation, embedded-resource load, or script load to the external import URL.
7. WHEN Frontend_Redesign renders Untrusted_Content, THE Frontend_Redesign SHALL render Untrusted_Content as inert text or structured data without executable markup, event handlers, scripts, dynamic code evaluation, or embedded remote content.
8. THE Frontend_Redesign SHALL not convert Untrusted_Content into a tool request, privileged URL, client-side route authority, approval operation, or executable command.
9. WHEN a client-side artifact or knowledge check detects a correctable input issue, THE Frontend_Redesign SHALL present the result as non-authoritative feedback.

### Requirement 9: VA domain-adapter representation

**User Story:** As a VA-domain operator, I want VA production structures represented through the common control plane, so that VA workflows retain lifecycle, quality, artifact, approval, and provenance semantics.

#### Acceptance Criteria

1. WHEN a VA_Projection is present, THE Frontend_Redesign SHALL display the returned VA template and production-phase metadata with its Common_Pattern_Version reference.
2. WHEN a VA_Projection contains a Common_Agent_Version contract, THE Frontend_Redesign SHALL display the returned identity, scope, capabilities, policies, runtime constraints, quality contract, critique relationships, provenance obligations, and published version.
3. WHEN a VA_Projection contains a Task_Projection, THE Frontend_Redesign SHALL display the returned graph revision, dependencies, gates, lifecycle, budget, checkpoint, common-version provenance, and recovery state.
4. WHEN a VA_Projection contains an Artifact_Projection, THE Frontend_Redesign SHALL display the returned artifact version, parent lineage, technical specification, rights and consent state, continuity state, quality-control state, delivery targets, and provenance reference.
5. WHEN a VA_Projection contains critique or quality information, THE Frontend_Redesign SHALL display the returned critique status and separate Quality_Evidence categories.
6. WHEN a VA_Projection contains an Approval_Gate, THE Frontend_Redesign SHALL apply Requirement 7 approval presentation and command rules.
7. WHERE a Swarm_Instance has no VA_Projection, THE Frontend_Redesign SHALL render the returned common graph, task, governance, and provenance projection without VA-specific fields.
8. WHEN a user invokes a VA production action, THE Frontend_Redesign SHALL submit the corresponding returned Action_Reference as a Command_Intent.
9. WHEN an Artifact_Projection lacks a required delivery field or gate approval, THE Frontend_Redesign SHALL display the returned artifact as blocked from delivery.

### Requirement 10: Accessible, responsive, and session-safe operations

**User Story:** As an operator using desktop, mobile, keyboard, or assistive technology, I want accessible operational views, so that I can understand and safely act on authorized control-plane state.

#### Acceptance Criteria

1. WHEN Frontend_Redesign renders a text-labelled interactive control, THE Frontend_Redesign SHALL expose its visible text as its programmatic accessible name.
2. WHEN Frontend_Redesign renders an icon-only refresh, reconnect, copy-correlation, or close control, THE Frontend_Redesign SHALL expose the exact accessible name `Refresh operational projection`, `Reconnect live updates`, `Copy correlation identifier`, or `Close` respectively.
3. WHEN keyboard focus moves to an interactive control, THE Frontend_Redesign SHALL render a visible focus indicator with a minimum 2 CSS-pixel outline and 2 CSS-pixel offset.
4. WHEN a dialog opens, THE Frontend_Redesign SHALL move keyboard focus to the dialog heading and retain keyboard focus within the dialog until the dialog closes.
5. WHEN a dialog closes, THE Frontend_Redesign SHALL return keyboard focus to the control that opened the dialog.
6. WHEN an Operational_Screen receives a changed returned status, THE Frontend_Redesign SHALL announce `<resource name>: <returned state label>; updated <as_of>` exactly once through an Accessible_Live_Region.
7. WHEN Frontend_Redesign represents a lifecycle, freshness, quality, approval, or recovery state, THE Frontend_Redesign SHALL provide the returned textual state independent of color.
8. WHEN a Supported_Mobile_Viewport renders an Operational_Screen, THE Frontend_Redesign SHALL expose the same returned status, freshness, recovery, approval, Evidence_Reference, and Action_Reference information available in the corresponding desktop view.
9. WHEN a Supported_Mobile_Viewport renders an interactive Action_Reference control, THE Frontend_Redesign SHALL provide a target area of at least 44 by 44 CSS pixels.
10. WHEN Frontend_Redesign stores a recoverable view cache, THE Frontend_Redesign SHALL store only the Authorized_Projection fields and Event_Cursor required to render the active session or resume its authorized SSE_Subscription.
11. WHEN Session_Context ends, changes organization, or changes actor, THE Frontend_Redesign SHALL clear the Session_Safe_Cache before rendering another Authorized_Projection.
12. THE Frontend_Redesign SHALL not persist access tokens, tool credentials, Protected_Fields, raw protected data, or privileged artifact content in browser local storage, session storage, IndexedDB, or cache storage.
13. WHEN a user follows an externally addressed destination, THE Frontend_Redesign SHALL require a returned Allowed_Action_Contract before navigation.

### Requirement 11: Deterministic contract, resilience, security, accessibility, and view verification

**User Story:** As a release owner, I want deterministic frontend verification, so that integration regressions cannot silently weaken governed control-plane behavior.

#### Acceptance Criteria

1. WHEN continuous integration runs frontend contract verification, THE Frontend_Redesign SHALL use fixed OpenAPI_Document fixtures and fail on a Generated_Client compatibility or generated-artifact mismatch.
2. WHEN continuous integration runs command verification, THE Frontend_Redesign SHALL use deterministic Public_API fixtures for duplicate interaction, queued command, ambiguous transport, rate limit, authorization denial, policy denial, Approval_Gate denial, cancellation, retry exhaustion, and manual recovery.
3. WHEN command verification exercises an ambiguous or retry outcome, THE Frontend_Redesign SHALL verify that every submission and reconciliation for one Command_Intent contains the same Idempotency_Identity.
4. WHEN continuous integration runs SSE verification, THE Frontend_Redesign SHALL use deterministic REST_Snapshot and Operational_Event fixtures for connection, authorized contiguous replay, bounded replay, replay expiry, replay denial, schema mismatch, duplicated event, out-of-order event, and sequence gap.
5. WHEN SSE verification supplies an event whose sequence differs from Expected_Event_Sequence, THE Frontend_Redesign SHALL verify Resynchronization replaces incremental state with a REST_Snapshot before a later Operational_Event is applied.
6. WHEN continuous integration runs ingress verification, THE Frontend_Redesign SHALL use deterministic fixtures for type, size, ownership, retention, quarantine, indexing, rejection, redacted error, and external import URL outcomes.
7. WHEN external import URL verification runs, THE Frontend_Redesign SHALL verify that no browser fetch, XMLHttpRequest, WebSocket, navigation, embedded-resource load, or script load targets the supplied URL.
8. WHEN continuous integration runs redaction verification, THE Frontend_Redesign SHALL verify that each absent Protected_Field is absent from rendered text, DOM nodes, accessibility-tree nodes, client cache, and Action_Reference payloads.
9. WHEN continuous integration runs untrusted-content verification, THE Frontend_Redesign SHALL verify that representative Untrusted_Content produces no executable markup, event handler, dynamic code evaluation, external navigation, or action authority.
10. WHEN continuous integration runs accessibility verification, THE Frontend_Redesign SHALL verify the exact accessible names, focus transitions, focus indicator, Accessible_Live_Region announcement, textual state labels, and 44 by 44 CSS-pixel mobile action targets in Requirement 10.
11. WHEN continuous integration runs projection-view verification, THE Frontend_Redesign SHALL render deterministic representative generated Authorized_Projections for dashboard, registry, activity, graph canvas, approvals, rollouts, artifacts and knowledge, and VA views.
12. WHEN projection-view verification renders a control or evidence item, THE Frontend_Redesign SHALL verify that the rendered item originated from a returned Action_Reference or Evidence_Reference.

## Review Notes

- **Binding integration decisions:** Frontend_Redesign consumes only generated `/api/v1` REST contracts and authorized SSE; mutations are server-authorized idempotent commands; SSE is an observation transport; tenant, policy, governance, evidence, and recovery decisions remain server-owned.
- **Explicitly deferred decisions:** The UI component library, query-cache library, graph library, authentication session implementation, generated-client tool, retry timing, mobile offline policy, and individual delivery phases remain design decisions, provided these requirements are met.
- **Review focus:** Confirm the initial route priority among the approved views and that Backend_Redesign publishes the generated projections, Action_References, Evidence_References, freshness fields, and sequence contexts required here.
