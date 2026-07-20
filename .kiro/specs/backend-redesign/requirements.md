# Requirements Document

## Introduction

Backend_Redesign delivers an additive, governed browser-facing control-plane façade for the existing common-agent-swarm-ops library. The façade makes the registry, graph composition, run operations, approvals, evaluations, knowledge contribution, rollout, and VA domain-adapter projections available through versioned contracts without transferring execution authority or protected content to the browser.

## Scope and Authority

The supplied backend-redesign brief and VA mapping are product inputs. These requirements preserve their stated outcomes and hard boundaries, while deferring unsupported implementation choices such as identity-provider vendor, queue technology, retention durations, service-level objectives, and public-registry policy to design and deployment policy.

## Glossary

- **Backend_Redesign**: The additive browser-facing control-plane façade specified by this document.
- **Browser_Client**: A frontend application that consumes Backend_Redesign contracts.
- **Public_API**: The documented REST and Server-Sent Events interface below `/api/v1`.
- **Public_API_Contract**: The versioned route, request, response, error, and event schemas exposed through Public_API.
- **OpenAPI_Document**: The machine-readable Public_API_Contract generated from implemented routes.
- **Protected_Request**: A Public_API request that requires authenticated access.
- **Trusted_Request_Context**: Server-derived organization, actor, permission, and correlation information for a Protected_Request.
- **Organization**: The tenant boundary that owns and authorizes protected resources.
- **Enumeration_Safe_Authorization_Error**: A redaction-safe authorization error whose externally observable status, code, message, and envelope do not disclose whether a protected resource exists or is visible.
- **Idempotency_Record**: The durable association of one state-changing request with an actor, key, request digest, and response reference, retained according to Deployment_Configuration.
- **Common_Agent_Version**: An immutable, published version of a reusable agent contract.
- **Common_Pattern_Version**: An immutable, published version of a reusable swarm-pattern contract.
- **Swarm_Instance**: An Organization-owned composition of version-pinned agent and pattern nodes.
- **Graph_Revision**: An immutable version of a Swarm_Instance graph.
- **Run**: One recorded execution of a Graph_Revision.
- **Work_Item**: A durable request for asynchronous execution work with a lifecycle and recovery state.
- **Agent_Task**: A Run-scoped unit of work with a pinned Common_Agent_Version, dependencies, lifecycle state, and checkpoint reference.
- **Artifact_Handoff**: An authorized, versioned artifact record that a dependent Agent_Task may consume.
- **Critique_Record**: Directed, evidence-bearing feedback between authorized agent or human-review subjects.
- **Quality_Evidence**: Separate retained results for L1 specification validation, L2 role-rubric evaluation, L3 baseline preference, and gate evaluation.
- **Approval_Gate**: A server-owned pending operation that requires a recorded human decision before further effectful work.
- **Rollout_Campaign**: A controlled release of a version to a bounded target scope with criteria, approvals, and rollback.
- **Audit_Record**: Append-only evidence of a security-relevant or state-changing action.
- **Operational_Event**: A redacted, sequenceable operational notification for an authorized Browser_Client.
- **Activity_Projection**: An authorized, redacted read model with an explicit freshness timestamp.
- **Recovery_Response**: A stable Public_API response that directs a Browser_Client to obtain a fresh projection after unavailable event replay.
- **Untrusted_Content**: Imported, retrieved, uploaded, third-party, or model-produced data that cannot grant authority or alter policy.
- **Fail_Complete_Outcome**: The prevention of further processing of affected Untrusted_Content after a configured protection fails.
- **Deployment_Configuration**: Schema-validated environment-derived operational settings.
- **VA_Domain_Adapter**: The optional domain adapter that maps VA production metadata to common-agent-swarm-ops concepts.

## Requirements

### Requirement 1: Versioned public contract

**User Story:** As a Browser_Client developer, I want one stable versioned contract, so that frontend integrations remain compatible and reviewable.

#### Acceptance Criteria

1. THE Backend_Redesign SHALL expose Browser_Client REST and event endpoints only through Public_API.
2. WHEN a Public_API route returns a successful response with a body, THE Backend_Redesign SHALL return the Public_API_Contract response envelope containing a `data` member and a `meta.correlation_id` member.
3. WHEN a Public_API route returns an error, THE Backend_Redesign SHALL return the Public_API_Contract error envelope containing an error code, redaction-safe message, correlation identifier, and retryability indicator.
4. WHEN an implemented Public_API_Contract is published, THE Backend_Redesign SHALL generate an OpenAPI_Document from the implemented routes.
5. IF OpenAPI_Document generation fails, THEN THE Backend_Redesign SHALL retain a redaction-safe warning and SHALL permit Public_API_Contract publication.
6. WHEN a proposed Public_API_Contract change removes a route or field, narrows accepted input, or changes a response meaning, THE Backend_Redesign SHALL prevent publication until the Requirement 15 compatibility lifecycle is satisfied.

### Requirement 2: Trusted organization-scoped access

**User Story:** As an Organization administrator, I want protected resources isolated by trusted request context, so that a Browser_Client cannot select another Organization or actor.

#### Acceptance Criteria

1. WHEN a Protected_Request is accepted, THE Backend_Redesign SHALL derive Trusted_Request_Context from authenticated server-side identity processing.
2. IF a Browser_Client identity, Organization, or permission value conflicts with Trusted_Request_Context, THEN THE Backend_Redesign SHALL reject the Protected_Request with an Enumeration_Safe_Authorization_Error before accessing a protected resource.
3. WHEN a Protected_Request reads, directly or indirectly modifies, streams, or aggregates a protected resource, THE Backend_Redesign SHALL apply Organization ownership and visibility authorization before returning the resource, modifying the resource, or delivering an Operational_Event.
4. IF authorization for a Protected_Request fails, THEN THE Backend_Redesign SHALL return an Enumeration_Safe_Authorization_Error without disclosing the existence, visibility, ownership, or state of the protected resource.
5. IF a state-changing Protected_Request lacks an idempotency key, THEN THE Backend_Redesign SHALL reject the Protected_Request before creating a state change.
6. WHEN a state-changing Protected_Request supplies an idempotency key, THE Backend_Redesign SHALL persist an Idempotency_Record according to Deployment_Configuration before returning a successful response.
7. WHEN an idempotency key matches an Idempotency_Record for the same actor, THE Backend_Redesign SHALL return the Public_API_Contract response identified by the stored response reference and SHALL not create an additional state change.

### Requirement 3: Immutable common registry and execution provenance

**User Story:** As a registry maintainer, I want versioned common contracts and pinned execution provenance, so that historical runs remain reproducible.

#### Acceptance Criteria

1. WHEN a Common_Agent_Version is published, THE Backend_Redesign SHALL retain canonical identity, category, responsibilities, boundaries, escalation targets, approval authority, runtime policy, tool policy, quality rubric, critique relationships, knowledge bindings, input schema, output schema, and provenance policy.
2. WHEN a Common_Pattern_Version is published, THE Backend_Redesign SHALL retain the graph template, slot constraints, compatibility rules, risk requirements, verification requirements, and provenance.
3. WHILE a Common_Agent_Version or Common_Pattern_Version has published status, THE Backend_Redesign SHALL preserve the complete versioned contract unchanged.
4. WHEN an authorized maintainer changes a published common contract, THE Backend_Redesign SHALL create a separate draft, fork, or proposal with a distinct version identifier.
5. WHILE a Common_Agent_Version or Common_Pattern_Version has draft status, THE Backend_Redesign SHALL permit authorized updates to the draft without changing a published version.
6. IF a security vulnerability is recorded for a published Common_Agent_Version or Common_Pattern_Version, THEN THE Backend_Redesign SHALL require migration to a separate patched version and SHALL preserve the published version unchanged.
7. WHEN a Run is created from a Graph_Revision, THE Backend_Redesign SHALL retain the immutable Graph_Revision identifier, versioned workflow definition, and every resolved Common_Agent_Version and Common_Pattern_Version identifier before dispatch.
8. WHEN a later graph or common-contract change occurs, THE Backend_Redesign SHALL preserve every earlier Run provenance record unchanged.

### Requirement 4: Validated swarm composition

**User Story:** As an editor, I want graph revisions validated before execution, so that only provenance-complete and policy-compliant Swarm_Instances can run.

#### Acceptance Criteria

1. WHEN an editor creates or updates a Swarm_Instance, THE Backend_Redesign SHALL create a new Graph_Revision with the supplied nodes, edges, layout, version pins, policies, and expected revision value.
2. WHEN a Graph_Revision contains a custom agent node, THE Backend_Redesign SHALL require either a fork origin or a custom reason for the custom agent node.
3. WHEN validation is requested for a Graph_Revision, THE Backend_Redesign SHALL evaluate version resolution, schema compatibility, tool policy, budget policy, verification policy, rollback policy, and approval policy.
4. WHEN Graph_Revision validation completes, THE Backend_Redesign SHALL return a validation result for every evaluated validation category.
5. IF Graph_Revision validation fails, THEN THE Backend_Redesign SHALL return field-specific redaction-safe validation results, SHALL leave a new Run uncreated, and SHALL mark the Graph_Revision ineligible for Run creation.
6. WHEN Graph_Revision validation succeeds, THE Backend_Redesign SHALL produce a versioned workflow definition accepted by the existing common-agent-swarm-ops validation contract and SHALL mark the Graph_Revision eligible for Run creation.
7. IF a Run is requested for a Graph_Revision that has not successfully completed validation, THEN THE Backend_Redesign SHALL leave the Run uncreated.
8. IF an editor submits an expected revision value different from the current Swarm_Instance revision, THEN THE Backend_Redesign SHALL return an optimistic-version conflict and SHALL preserve the current Graph_Revision.

### Requirement 5: Durable asynchronous execution and recovery

**User Story:** As an operator, I want long-running work recorded and recoverable outside request lifetimes, so that duplicate dispatch and worker failures do not produce uncontrolled outcomes.

#### Acceptance Criteria

1. WHEN a Run, evaluation, contribution, indexing, or Rollout_Campaign execution is requested, THE Backend_Redesign SHALL create and retain a Work_Item before dispatching the requested work.
2. WHEN the Backend_Redesign dispatches a Work_Item, THE Backend_Redesign SHALL retain the Organization, immutable subject reference, attempt number, idempotency key, correlation identifier, scheduled time, cancellation state, and claim state.
3. WHEN a Work_Item transition is recorded, THE Backend_Redesign SHALL retain an auditable transition record before publishing a corresponding Operational_Event.
4. IF a worker claim expires or a worker stops before a Work_Item reaches a terminal state, THEN THE Backend_Redesign SHALL apply the configured recovery decision of safe reclaim, manual recovery, or dead-letter handling.
5. WHEN a Work_Item encounters a retryable transient failure, THE Backend_Redesign SHALL apply the configured bounded retry policy and SHALL check cancellation state before each retry attempt.
6. IF a Work_Item encounters a validation, authorization, policy, rights-or-consent, schema, or non-idempotent ambiguity failure, THEN THE Backend_Redesign SHALL record the failure as non-automatic-retryable.
7. IF a Work_Item has both a transient-failure classification and a validation-failure classification, THEN THE Backend_Redesign SHALL classify the Work_Item as non-automatic-retryable.
8. IF duplicate dispatch targets the same idempotent Work_Item, THEN THE Backend_Redesign SHALL apply the governed idempotent outcome without creating an additional state change for the Work_Item subject.

### Requirement 6: Explicit task coordination lifecycle

**User Story:** As an operator, I want task-level lifecycle and recovery state, so that graph execution can be observed and controlled without a parallel execution engine.

#### Acceptance Criteria

1. WHEN a valid Graph_Revision is prepared for a Run, THE Backend_Redesign SHALL create Agent_Task records with pinned agent versions, dependencies, constraints, gates, and checkpoint references.
2. THE Backend_Redesign SHALL represent every Agent_Task with one of `idle`, `queued`, `running`, `self_refine`, `waiting_for_critique`, `blocked`, `failed`, or `complete` lifecycle states.
3. WHEN every required dependency and Approval_Gate for an Agent_Task is satisfied, THE Backend_Redesign SHALL automatically transition the Agent_Task to `queued`.
4. WHEN an Agent_Task transition is recorded, THE Backend_Redesign SHALL require the expected Agent_Task version and SHALL retain an Audit_Record and Operational_Event for the transition.
5. WHEN an Agent_Task retries or enters self-refinement, THE Backend_Redesign SHALL apply the published retry or iteration limit for the pinned Common_Agent_Version.
6. IF the pinned Common_Agent_Version has a negative published retry or iteration limit, THEN THE Backend_Redesign SHALL permit unlimited retries or iterations.
7. IF an Agent_Task reaches a non-retryable failure or an exhausted retry limit, THEN THE Backend_Redesign SHALL retain a machine-readable failure reason and SHALL prevent automatic redispatch.
8. WHEN an authorized replay is requested, THE Backend_Redesign SHALL create a new Run lineage that identifies the source graph, checkpoint, artifact versions, and common-version pins.
9. IF a queued Agent_Task later becomes ineligible for execution, THEN THE Backend_Redesign SHALL retain the Agent_Task in `queued` lifecycle state.

### Requirement 7: Governed artifact handoff

**User Story:** As a quality owner, I want artifact handoffs validated before dependent work, so that rights, quality, and provenance gaps block unsafe progression.

#### Acceptance Criteria

1. WHEN an Agent_Task creates an Artifact_Handoff, THE Backend_Redesign SHALL retain artifact identity and version, parent lineage, source task and Run, brief scope, technical specification, rights-and-consent state, continuity state, quality-control state, target channels, and provenance reference.
2. WHEN a dependent Agent_Task requires an Artifact_Handoff, THE Backend_Redesign SHALL validate only the presence of the Artifact_Handoff identity, lineage, required technical fields, rights-and-consent state, continuity state, quality-control state, target channels, and provenance reference before dispatch.
3. IF one or more required Artifact_Handoff fields are absent, THEN THE Backend_Redesign SHALL keep the dependent Agent_Task in `blocked` state, record the absent fields, and prevent dependent dispatch.
4. WHEN a Browser_Client reads an Artifact_Handoff, THE Backend_Redesign SHALL return an authorized redacted projection with artifact lineage and validation state.
5. WHEN Artifact_Handoff data reaches a downstream Agent_Task, THE Backend_Redesign SHALL provide authorized artifact references rather than protected artifact content.

### Requirement 8: Directed critique, quality, and approval evidence

**User Story:** As a reviewer, I want distinct critique, quality, and approval evidence, so that no aggregate score or client payload bypasses a required gate.

#### Acceptance Criteria

1. WHEN a Critique_Record is submitted, THE Backend_Redesign SHALL accept the Critique_Record only when the published Common_Agent_Version relationship or authorized human-review policy permits the directed critique.
2. IF a Critique_Record fails relationship or policy validation, THEN THE Backend_Redesign SHALL reject the Critique_Record before delivery to the target Agent_Task.
3. WHEN a quality evaluation completes, THE Backend_Redesign SHALL retain independent Quality_Evidence for L1 specification validation, L2 role-rubric evaluation, L3 baseline preference, and gate evaluation.
4. IF required L1 validation, L2 threshold, L3 criterion, rights-and-consent check, provenance check, or Approval_Gate fails, THEN THE Backend_Redesign SHALL block the affected dependent Agent_Task or affected Rollout_Campaign transition and SHALL retain the failed evidence.
5. WHEN a human submits an Approval_Gate decision, THE Backend_Redesign SHALL associate the decision with the server-owned pending operation and SHALL re-evaluate authorization and policy before resuming an effectful operation.
6. IF an Approval_Gate decision lacks a required decision value, decision reason, or reviewer authorization, THEN THE Backend_Redesign SHALL retain the Approval_Gate in pending state.
7. IF all applicable L1 validation, L2 threshold, L3 criterion, rights-and-consent check, provenance check, and Approval_Gate checks pass, THEN THE Backend_Redesign SHALL record passed Quality_Evidence and SHALL permit the affected transition to proceed past Requirement 8 checks.
8. WHEN the Backend_Redesign evaluates a required gate, THE Backend_Redesign SHALL use the independently retained category-specific Quality_Evidence and server-owned Approval_Gate decision for that gate.

### Requirement 9: Proposal and controlled rollout lifecycle

**User Story:** As a release owner, I want changes proposed, evaluated, and released through a bounded campaign, so that published common contracts cannot change silently.

#### Acceptance Criteria

1. WHEN an improvement proposal is submitted, THE Backend_Redesign SHALL retain the proposed immutable difference, source evidence, validation evidence, evaluation evidence, reviewer decisions, and impact summary.
2. WHEN an improvement proposal is created, THE Backend_Redesign SHALL preserve the referenced published Common_Agent_Version or Common_Pattern_Version unchanged.
3. WHEN a Rollout_Campaign is created, THE Backend_Redesign SHALL retain the selected version, bounded target scope, required approvals, success criteria, rollback reference, status, and measured outcomes for each success criterion.
4. WHEN a Rollout_Campaign starts, THE Backend_Redesign SHALL require the configured evaluation evidence, approval evidence, bounded target scope, success criteria, and rollback reference.
5. IF a Rollout_Campaign criterion fails, THEN THE Backend_Redesign SHALL stop all further Rollout_Campaign progression, invoke the retained rollback lifecycle, retain the criterion evidence, and SHALL not permit a manual override.
6. IF a proposal lacks required validation, evaluation, approval, or rollback evidence, THEN THE Backend_Redesign SHALL retain the proposal outside production rollout.
7. WHILE a Rollout_Campaign performs its retained rollback lifecycle, WHEN a request to create a separate Rollout_Campaign is received, THE Backend_Redesign SHALL validate the separate Rollout_Campaign required start conditions before creating the separate Rollout_Campaign.

### Requirement 10: Redacted operational events and projections

**User Story:** As an operator, I want authorized live updates and trustworthy read models, so that I can monitor work without receiving protected data or silently missing history.

#### Acceptance Criteria

1. WHEN a state-changing transaction commits, THE Backend_Redesign SHALL retain an Audit_Record and an Operational_Event delivery record in the same committed outcome.
2. WHEN a Browser_Client connects to an event stream or requests an Operational_Event, THE Backend_Redesign SHALL authorize the requested topic and Operational_Event subject using the current Trusted_Request_Context before delivering an Operational_Event.
3. WHEN the Backend_Redesign publishes an Operational_Event, THE Backend_Redesign SHALL include a sequence identifier, event type, subject reference, occurrence timestamp, correlation identifier, payload schema version, and redacted payload.
4. WHEN a Browser_Client resumes an event stream from a retained sequence identifier, an authorized contiguous bounded sequence beginning immediately after the sequence identifier is available, and configured event-replay policy permits replay, THE Backend_Redesign SHALL deliver exactly that authorized contiguous bounded sequence without omission or duplication.
5. IF a Browser_Client resume request cannot produce an authorized contiguous bounded sequence or configured event-replay policy directs recovery, THEN THE Backend_Redesign SHALL return a Recovery_Response without delivering a replay event and SHALL retain the sequence-gap or recovery outcome.
6. IF a Browser_Client is unauthorized to receive any requested Operational_Event in an event replay sequence, THEN THE Backend_Redesign SHALL reject the event replay request with an Enumeration_Safe_Authorization_Error before delivering an Operational_Event.
7. WHEN a Browser_Client reads an Activity_Projection, THE Backend_Redesign SHALL include an `as_of` timestamp and a freshness state.
8. WHEN an Operational_Event or Activity_Projection contains tool, artifact, model, retrieval, approval, or error information, THE Backend_Redesign SHALL provide only authorized redacted summaries and references.

### Requirement 11: Secure ingress and untrusted-content boundaries

**User Story:** As a security owner, I want inbound content treated as untrusted, so that content cannot escape organization boundaries or acquire operational authority.

#### Acceptance Criteria

1. WHEN a Browser_Client submits a Public_API request, THE Backend_Redesign SHALL validate the request size, content type, route fields, pagination bounds, filter bounds, and endpoint rate limit before processing the request.
2. IF a Public_API request fails request size, content type, route field, pagination bound, filter bound, or endpoint rate-limit validation, THEN THE Backend_Redesign SHALL reject the request before processing the request.
3. WHEN the Backend_Redesign accepts a file or import, THE Backend_Redesign SHALL validate declared type, detected type, size, checksum, Organization ownership, and normalized storage name before processing the file or import.
4. IF a file or import fails declared-type, detected-type, size, checksum, Organization-ownership, or normalized-storage-name validation, THEN THE Backend_Redesign SHALL reject the file or import before storage or further processing.
5. WHERE file scanning is configured, WHEN the Backend_Redesign accepts a file or import, THE Backend_Redesign SHALL quarantine the file or import until the configured scan records an allowed result.
6. WHEN a configured file scan records an allowed result for a quarantined file or import, THE Backend_Redesign SHALL release the file or import from quarantine.
7. WHEN the Backend_Redesign stores an accepted file or import, THE Backend_Redesign SHALL associate the stored content with an authorization-checked opaque reference.
8. WHEN the Backend_Redesign processes Untrusted_Content, THE Backend_Redesign SHALL prevent Untrusted_Content from granting authority, selecting a tool, changing policy, bypassing validation, or supplying privileged executable instructions.
9. IF Untrusted_Content attempts to grant authority, select a tool, change policy, bypass validation, or supply privileged executable instructions, THEN THE Backend_Redesign SHALL apply a Fail_Complete_Outcome to the affected Untrusted_Content.
10. WHEN configured security policy detects a prompt-injection indicator, prohibited content indicator, suspicious tool proposal, or artifact-manifest mismatch, THE Backend_Redesign SHALL retain security evidence.
11. WHEN the Backend_Redesign processes Untrusted_Content under configured protections, THE Backend_Redesign SHALL require every configured protection against Untrusted_Content to succeed before further processing.
12. IF any configured protection against Untrusted_Content fails, THEN THE Backend_Redesign SHALL retain security evidence and SHALL apply a Fail_Complete_Outcome.

### Requirement 12: Operational health, correlation, and retention

**User Story:** As a platform operator, I want redaction-safe health and traceability with bounded operational data, so that degraded service is visible and recoverable.

#### Acceptance Criteria

1. WHEN a liveness view is requested, THE Backend_Redesign SHALL return process liveness without contacting any dependency.
2. WHEN a readiness view is requested, THE Backend_Redesign SHALL report the usable or unavailable state of each required configured dependency and the `not_configured` state of each optional unconfigured dependency.
3. WHEN an authorized operational-health view is requested, THE Backend_Redesign SHALL return a redacted component summary, build version, schema version, and readiness timestamp.
4. IF an authorized operational-health view cannot provide a redacted component summary, build version, schema version, or readiness timestamp, THEN THE Backend_Redesign SHALL reject the operational-health view request.
5. WHEN a Protected_Request creates a command, event, Work_Item, Run, Approval_Gate, or outcome, THE Backend_Redesign SHALL associate the same correlation identifier across the resulting records.
6. WHEN the Backend_Redesign writes a log, trace, metric, Audit_Record, Operational_Event, or error response, THE Backend_Redesign SHALL exclude credentials, tokens, raw prompts, protected artifacts, and prohibited tool inputs.
7. WHEN Deployment_Configuration is loaded, THE Backend_Redesign SHALL validate Deployment_Configuration before applying the configured retention, replay, payload-size, and backpressure policies for operational events, Audit_Records, traces, artifacts, approvals, Idempotency_Records, and failed Work_Items.
8. WHEN a configured retention policy expires a record category, THE Backend_Redesign SHALL apply the configured archival or deletion lifecycle and SHALL retain authorization or provenance evidence only when the applicable policy requires the evidence.

### Requirement 13: Safe deployment configuration

**User Story:** As a deployment owner, I want validated operational configuration and protected transport, so that environment changes do not leak secrets or weaken public access controls.

#### Acceptance Criteria

1. WHEN Backend_Redesign starts, THE Backend_Redesign SHALL validate Deployment_Configuration for trusted origins, identity integration, persistence adapters, dispatch adapters, retention policies, rate limits, and feature flags.
2. IF Deployment_Configuration contains an invalid cross-component configuration, THEN THE Backend_Redesign SHALL prevent startup of the affected component and SHALL record a redaction-safe configuration error without including configuration secrets.
3. WHEN Backend_Redesign reads a secret, THE Backend_Redesign SHALL successfully obtain the secret from the deployment environment or configured secret manager.
4. IF a required Deployment_Configuration secret is unavailable from the deployment environment and the configured secret manager, THEN THE Backend_Redesign SHALL fail the affected startup or operation safely and SHALL record a redaction-safe error without including the secret value.
5. WHEN Backend_Redesign creates a Public_API response, Operational_Event, Browser_Client configuration value, or diagnostic response, THE Backend_Redesign SHALL exclude deployment secrets.
6. WHERE a production transport configuration is enabled, THE Backend_Redesign SHALL require HTTPS.
7. WHERE a production transport configuration is enabled, THE Backend_Redesign SHALL apply the configured restrictive cross-origin policy and session-model-appropriate security headers.
8. WHEN a Public_API rate limit is reached, THE Backend_Redesign SHALL return the Public_API error envelope with a `Retry-After` value and a redaction-safe rate-limit response independent of protected-resource existence.

### Requirement 14: VA domain-adapter compatibility

**User Story:** As a VA-domain user, I want VA production concepts represented through the common control plane, so that VA workflows preserve production semantics without creating a separate unversioned backend.

#### Acceptance Criteria

1. WHEN VA_Domain_Adapter data is requested, THE Backend_Redesign SHALL expose VA template and phase metadata only through Public_API.
2. WHEN VA_Domain_Adapter metadata includes a template or production phase, THE Backend_Redesign SHALL validate the metadata against the referenced published Common_Pattern_Version.
3. IF VA_Domain_Adapter metadata fails validation against the referenced published Common_Pattern_Version, THEN THE Backend_Redesign SHALL return redaction-safe validation results and SHALL prevent the metadata from being used for a VA production action.
4. WHEN a VA_Domain_Adapter Run is projected, THE Backend_Redesign SHALL provide authorized redacted projections for Common_Agent_Version contracts, Agent_Task lifecycle and dependencies, Artifact_Handoff lineage, Critique_Record state, Quality_Evidence, Approval_Gate evidence, and pinned provenance.
5. WHERE a Swarm_Instance does not use VA_Domain_Adapter metadata, THE Backend_Redesign SHALL permit the Swarm_Instance to use the same common graph, task, governance, and provenance contracts without VA-specific fields.
6. WHEN a Browser_Client invokes a VA production action, THE Backend_Redesign SHALL map the action to the corresponding authorized Public_API command and SHALL preserve the resulting immutable graph, task, artifact, approval, and Run evidence.

### Requirement 15: Contract lifecycle and compatibility

**User Story:** As a Browser_Client developer, I want generated and compatible contracts, so that the redesigned frontend can migrate without copying schemas or silently losing supported run behavior.

#### Acceptance Criteria

1. WHEN the OpenAPI_Document changes, THE Backend_Redesign SHALL generate or update typed Browser_Client contract artifacts from the OpenAPI_Document.
2. IF a proposed Public_API_Contract change removes a route or field, narrows accepted input, or changes response meaning, THEN THE Backend_Redesign SHALL require a documented deprecation window, versioned replacement contract, migration record, and updated compatibility check before publication and SHALL permit publication when those conditions are satisfied regardless of whether a `/workflow-runs/*` compatibility route is actively supported.
3. WHILE an existing `/workflow-runs/*` compatibility route remains supported, THE Backend_Redesign SHALL maintain a documented mapping from the compatibility route to its Public_API projection and documented sunset criteria.
4. WHEN an existing `/workflow-runs/*` compatibility route reaches its documented sunset criteria, THE Backend_Redesign SHALL provide the documented mapping and sunset criteria with the related migration record to the documented manual retention process after support ends.

### Requirement 16: Governed library delegation

**User Story:** As a security owner, I want the façade to delegate governed work through the existing library, so that browser commands cannot create a parallel path around authorization, validation, approval, or tool controls.

#### Acceptance Criteria

1. WHEN a validated command creates, dispatches, resumes, evaluates, evolves, or retrieves a run-related resource, THE Backend_Redesign SHALL delegate the governed operation through the corresponding existing common-agent-swarm-ops library service.
2. WHEN a Run requires an effectful tool operation, THE Backend_Redesign SHALL delegate the operation through the corresponding existing common-agent-swarm-ops library service using server-held identity, Organization, policy, and published Common_Agent_Version data.
3. IF a graph, adapter response, or Untrusted_Content supplies a tool identifier, credential, URL, executable instruction, or authority that is not present in both the published common contract and Organization policy, THEN THE Backend_Redesign SHALL reject the supplied value before dispatch.
4. IF the Backend_Redesign cannot validate whether a tool identifier is present in both the published common contract and Organization policy, THEN THE Backend_Redesign SHALL reject the tool identifier before dispatch.
5. WHEN a graph, adapter response, or Untrusted_Content supplies a tool identifier that is present in both the published common contract and Organization policy, THE Backend_Redesign SHALL permit the tool identifier to proceed to governed dispatch.
6. WHEN any dispatch adapter type, including a local-inline dispatch adapter, dispatches a governed operation, THE Backend_Redesign SHALL delegate the governed operation through the corresponding existing common-agent-swarm-ops library service and SHALL preserve all applicable existing common-agent-swarm-ops library governance contracts, including authorization, validation, approval, tool-broker, command, state-transition, cancellation, recovery, and Operational_Event contracts.

### Requirement 17: Actionable operational alerting

**User Story:** As a platform operator, I want configured degraded conditions to produce traceable alerts, so that operational failures receive timely investigation without exposing protected data.

#### Acceptance Criteria

1. WHEN a configured readiness failure, Work_Item queue-age condition, terminal Run failure-rate condition, event replay-gap condition, outbox-lag condition, Approval_Gate expiry condition, or Rollout_Campaign rollback condition is detected, THE Backend_Redesign SHALL retain a redaction-safe operator alert with the associated correlation identifier or operational subject reference.
2. WHEN a dashboard projection represents delayed or degraded data, THE Backend_Redesign SHALL include the projection `as_of` timestamp, freshness state, and degraded-state indicator.
3. WHEN a dashboard projection delivery is delayed and the underlying data satisfies the configured current freshness state, THE Backend_Redesign SHALL report the underlying data freshness state and SHALL include the delayed or degraded-state indicator.

## Approval

- **Status:** Draft requirements created for review.
- **Scope decision:** Backend_Redesign is an additive browser-facing façade over the existing common-agent-swarm-ops library. The façade does not expose engines, repositories, providers, tool adapters, credentials, raw prompts, or client-derived authority to Browser_Client code.
- **Deferred design decisions:** The identity-provider implementation, session model, queue technology, storage adapters, shared-registry policy, retention durations, service-level objectives, and deployment alert thresholds remain design or deployment-policy decisions.
- **Review focus:** Confirm that the requirement set captures the intended public endpoint surface and whether the initial release requires any explicit quantitative limits beyond Deployment_Configuration.
