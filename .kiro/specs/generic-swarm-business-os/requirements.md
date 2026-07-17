# Requirements Document

## Introduction
Generic_Swarm_Business_OS is a governed multi-agent business operating system reimplemented in the Target_Workspace. The implementation prioritizes safety, auditability, correctness, efficiency, and evidence-based autonomy.

## Scope and Authority
The Target_Workspace is `C:\Project\common-agent-swarm-ops`. `structure.md` in the Target_Workspace is the authoritative architecture and product contract. The Reference_Workspace is strictly read-only reference material: it is neither an execution target nor a source of implementation truth, and unreviewed code from the Reference_Workspace must not be copied or adopted.

## Glossary
- **Generic_Swarm_Business_OS**: The system reimplemented in the Target_Workspace.
- **Target_Workspace**: `C:\Project\common-agent-swarm-ops`, the sole workspace for implementation and validation.
- **Reference_Workspace**: `C:\Project\generic-swarm-ops`, material permitted only for read-only comparison.
- **Structure_Contract**: `structure.md` in the Target_Workspace, the governing architecture and product-bar contract.
- **Host**: The domain-agnostic FastAPI control plane and shared runtime services.
- **Domain_Pack**: A domain-specific asset collection under `business/<domain_id>/`.
- **Agent_Learning_Contract**: The required learning configuration containing an agent identifier, a reflect hook, and approved memory scopes.
- **Workflow_DNA**: A portable workflow definition compiled by a Workflow_Engine.
- **Workflow_Engine**: The runtime interface that starts, executes, resumes, and cancels workflow runs.
- **Graph_Engine**: The in-process LangGraph implementation of Workflow_Engine.
- **Legacy_Engine**: The compatibility linear implementation of Workflow_Engine.
- **Run_Record**: The durable state and observable result of one workflow execution.
- **Host_Tool_Broker**: The Host service that authorizes, invokes, and audits tool calls.
- **Authorization_Intersection**: The simultaneous agent, workflow-step, role-based, and risk-policy permission check for one tool call.
- **Approval_Gate**: A paused Run_Record that requires a recorded human decision.
- **Process_Intelligence**: Analysis of permitted operational event logs into process artifacts.
- **Scoped_Memory**: Provenance-bearing information restricted to an approved workflow, organization, or agent scope.
- **Sandbox_Variant**: A non-production workflow, prompt, tool-use, role, or graph-configuration proposal.
- **Evaluation_Suite**: Golden, regression, adversarial, historical-replay, cost, latency, safety, and compliance checks.
- **Canary**: A limited, approved deployment scope with monitoring and rollback.
- **Video_Pack**: The `business/video/` Domain_Pack and its release-control assets.
- **Product_Bar**: The E1–E9 evidence criteria in the Structure_Contract.

## Requirements

### Requirement 1: Authoritative Reimplementation Boundary
**User Story:** As an implementation owner, I want a single authoritative target and architecture contract, so that reimplementation decisions remain reviewable and safe.
#### Acceptance Criteria
1. WHEN an architecture decision is recorded, THE Generic_Swarm_Business_OS SHALL identify the Target_Workspace and Structure_Contract in the architecture decision output.
2. WHEN implementation, validation, generation, a write operation, or execution is requested, THE Generic_Swarm_Business_OS SHALL perform the operation only in the Target_Workspace.
3. WHEN Reference_Workspace material is accessed, THE Generic_Swarm_Business_OS SHALL limit access to read-only comparison and SHALL perform no execution or modification in the Reference_Workspace.
4. WHEN implementation material is proposed from the Reference_Workspace, THE Generic_Swarm_Business_OS SHALL require recorded prior human approval before copying or adopting the material.
5. IF a request requires a source write, source execution, a write or execution outside the Target_Workspace, or adoption without recorded prior human approval, THEN THE Generic_Swarm_Business_OS SHALL refuse the request and leave the Target_Workspace and Reference_Workspace unchanged.

### Requirement 2: Universal Host and Domain Packs
**User Story:** As a platform owner, I want a domain-agnostic Host with isolated Domain_Packs, so that new domains do not require control-plane forks.
#### Acceptance Criteria
1. THE Generic_Swarm_Business_OS SHALL provide shared Host control-plane, governance, security, evaluation, evolution, and frontend-shell behavior without branching by domain identifier.
2. WHEN a Domain_Pack manifest is validated, THE Generic_Swarm_Business_OS SHALL accept the manifest only when the manifest has one unique pack identifier and from 1 through 100 agents with unique agent identifiers and draft or registered status.
3. WHEN a valid Domain_Pack manifest is registered, THE Generic_Swarm_Business_OS SHALL load every Domain_Pack agent without production activation.
4. IF a Domain_Pack manifest lacks a unique pack identifier, contains fewer than 1 or more than 100 agents, contains duplicate agent identifiers, contains an agent outside draft or registered status, or requests production activation, THEN THE Generic_Swarm_Business_OS SHALL mark the Domain_Pack inactive and reject production activation for every Domain_Pack agent.
5. WHILE a Domain_Pack agent has draft status, THE Generic_Swarm_Business_OS SHALL deny production activation for the Domain_Pack agent.
6. WHERE a Domain_Pack agent requires learning, WHEN the Agent_Learning_Contract has an exactly matching agent identifier, an enabled reflect hook, and from 1 through 10 approved memory scopes, THE Generic_Swarm_Business_OS SHALL activate the Domain_Pack agent.
7. WHERE a Domain_Pack agent requires learning, IF the Agent_Learning_Contract lacks an exactly matching agent identifier, an enabled reflect hook, fewer than 1 approved memory scope, or more than 10 approved memory scopes, THEN THE Generic_Swarm_Business_OS SHALL deny the entire activation and preserve the Domain_Pack agent state.

### Requirement 3: Process Intelligence and Provenance-Bearing Memory
**User Story:** As an operations analyst, I want the system to learn from permitted evidence, so that operational improvements trace to real work.
#### Acceptance Criteria
1. WHEN permitted operational event logs are ingested, THE Generic_Swarm_Business_OS SHALL create each Process_Intelligence artifact with the source log-set identifier and references to supporting records.
2. WHEN the Generic_Swarm_Business_OS stores a high-impact Scoped_Memory record, THE Generic_Swarm_Business_OS SHALL record the writer and provenance and restrict retrieval and use to the approved scope.
3. IF a high-impact Scoped_Memory write lacks provenance, THEN THE Generic_Swarm_Business_OS SHALL deny the write and record an audit event for the denial.
4. WHEN the Generic_Swarm_Business_OS records an audit event for a high-impact Scoped_Memory write, THE Generic_Swarm_Business_OS SHALL use either the primary audit service or an available alternative logging mechanism.
5. IF neither the primary audit service nor an alternative logging mechanism can record an audit event for a high-impact Scoped_Memory write, THEN THE Generic_Swarm_Business_OS SHALL block high-impact Scoped_Memory writes indefinitely, including during critical operations and system recovery operations, until audit logging is restored.
6. WHEN the Host or an authorized agent requests knowledge for a response or action, THE Generic_Swarm_Business_OS SHALL perform semantic retrieval before every other retrieval method and return provenance for every permitted result.
7. IF semantic retrieval and subsequent permitted retrieval methods produce no result within the requester scope, THEN THE Generic_Swarm_Business_OS SHALL return no knowledge and prevent disclosure of out-of-scope knowledge for authorized and unauthorized requesters.

### Requirement 4: Portable, Bounded Workflow Execution
**User Story:** As an operator, I want portable workflows executed within bounded orchestration, so that multi-agent work remains controllable.
#### Acceptance Criteria
1. WHEN a valid Workflow_DNA or permitted pack graph is selected, THE Generic_Swarm_Business_OS SHALL create a queued Run_Record and execute the selected definition through a Workflow_Engine.
2. IF a workflow definition is invalid, THEN THE Generic_Swarm_Business_OS SHALL reject the definition without starting a Run_Record execution.
3. IF a workflow execution fails, times out, is interrupted, or enters an ambiguous execution state, THEN THE Generic_Swarm_Business_OS SHALL set the Run_Record status to failed, preserve all available failure evidence and completed tool effects, stop every unstarted step, and expose the Run_Record to operators.
4. WHILE failure handling is incomplete, THE Generic_Swarm_Business_OS SHALL keep the Run_Record in failed status and prevent the Run_Record from being considered fully failure-processed until failure evidence, completed tool effects, unstarted-step termination, and operator observability are complete.
5. WHERE Graph_Engine is selected, THE Generic_Swarm_Business_OS SHALL enforce a maximum of 100 graph-node visits, 12 agent handoffs, 900 seconds of wall-clock execution, and 50 tool requests for each Run_Record.
6. WHILE the dual-engine migration gates remain unsatisfied, THE Generic_Swarm_Business_OS SHALL keep the Legacy_Engine available.
7. WHEN the dual-engine migration gates become satisfied, THE Generic_Swarm_Business_OS SHALL make the Legacy_Engine unavailable immediately, including during an active Legacy_Engine execution.
8. WHEN dual-engine migration gates are evaluated, THE Generic_Swarm_Business_OS SHALL require both engines, multi-specialist handoffs, an operator-visible node graph and interrupt, a video spine through stubs and its release gate, denial of cross-organization resume, and a fail-closed tool allow-list.
9. WHEN a workflow execution completes without failure or interruption, THE Generic_Swarm_Business_OS SHALL set the Run_Record status to completed and preserve completed tool effects.

### Requirement 5: Fail-Closed Security and Governance
**User Story:** As a risk owner, I want actions constrained by deterministic controls, so that untrusted model output cannot exceed approved authority.
#### Acceptance Criteria
1. WHEN an agent requests a tool call, THE Generic_Swarm_Business_OS SHALL evaluate every Authorization_Intersection constraint before tool invocation.
2. WHEN every Authorization_Intersection constraint passes for a requested tool call, THE Generic_Swarm_Business_OS SHALL invoke the requested tool call.
3. IF one or more Authorization_Intersection constraints fail for a requested tool call, THEN THE Generic_Swarm_Business_OS SHALL deny the requested tool call, record an audit event, and produce no tool invocation or tool effect.
4. IF an audit event for a denied tool call cannot be recorded, THEN THE Generic_Swarm_Business_OS SHALL continue to deny the requested tool call and produce no tool invocation or tool effect.
5. WHEN a later distinct tool call is requested, THE Generic_Swarm_Business_OS SHALL evaluate the later distinct tool call independently against every Authorization_Intersection constraint.
6. WHEN a workflow reaches a critical or irreversible action, THE Generic_Swarm_Business_OS SHALL pause the Run_Record at an Approval_Gate before producing the action effect.
7. WHEN a human records an Approval_Gate decision, THE Generic_Swarm_Business_OS SHALL record the submitted decision reason and selected decision value with the decision.
8. IF a recorded Approval_Gate decision reason contains fewer than 1 or more than 1,000 characters, THEN THE Generic_Swarm_Business_OS SHALL retain the recorded decision, mark the decision reason invalid, and keep the Run_Record paused.
9. IF a recorded Approval_Gate decision value is neither approval nor denial, THEN THE Generic_Swarm_Business_OS SHALL retain the submitted decision reason, require a human to select approval or denial, and keep the Run_Record paused.
10. WHEN a human records an Approval_Gate denial with a decision reason containing from 1 through 1,000 characters, THE Generic_Swarm_Business_OS SHALL keep the Run_Record paused.
11. WHEN a human records an Approval_Gate approval with a decision reason containing from 1 through 1,000 characters, THE Generic_Swarm_Business_OS SHALL re-evaluate every Authorization_Intersection constraint before producing the action effect.

### Requirement 6: Durable, Observable, Human-Centered Operations
**User Story:** As an operator, I want durable runs and clear controls, so that I can understand, correct, and recover workflow activity.
#### Acceptance Criteria
1. WHEN a workflow run is created, THE Generic_Swarm_Business_OS SHALL assign a unique run identifier and persist the selected Workflow_Engine and queued status before dispatch.
2. IF run dispatch fails, THEN THE Generic_Swarm_Business_OS SHALL retain the queued Run_Record before enabling a dispatch audit event, a later dispatch retry, or both.
3. IF the Generic_Swarm_Business_OS cannot retain the queued Run_Record after dispatch failure, THEN THE Generic_Swarm_Business_OS SHALL prevent dispatch-audit recording and later dispatch retry.
4. WHERE Graph_Engine uses a configured Postgres database, WHEN the Host restarts and an organization-scoped checkpoint exists for the Run_Record, THE Generic_Swarm_Business_OS SHALL resume the Run_Record only from that organization-scoped checkpoint.
5. WHEN the Generic_Swarm_Business_OS displays a recommendation, action, Approval_Gate, or failure, THE Generic_Swarm_Business_OS SHALL display one or more of supporting evidence, confidence in the inclusive range from 0 through 1, an uncertainty statement, a correction control, the run identifier, and a timestamp.
6. WHEN the Generic_Swarm_Business_OS displays an executable action, THE Generic_Swarm_Business_OS SHALL display an action preview before action execution.

### Requirement 7: Sandboxed Evolution
**User Story:** As a business owner, I want improvement proposals isolated from production, so that optimization cannot silently change live operations.
#### Acceptance Criteria
1. WHEN the Generic_Swarm_Business_OS proposes an improvement, THE Generic_Swarm_Business_OS SHALL create a Sandbox_Variant and leave production workflows, graphs, prompts, roles, and tool-use configurations unchanged.
2. WHEN a Sandbox_Variant is considered for promotion, THE Generic_Swarm_Business_OS SHALL require strictly improved target metrics in the configured improvement direction, no-worse safety results, no-worse compliance results, passing named regression checks, passing named adversarial checks, a rollback plan, an approved scoped Canary, complete audit records, and recorded human approval.
3. IF a Sandbox_Variant promotion condition is missing or fails, THEN THE Generic_Swarm_Business_OS SHALL block promotion and retain evidence for the missing or failed condition.
4. WHEN no Sandbox_Variant is under consideration for promotion, THE Generic_Swarm_Business_OS SHALL block production promotion.
5. WHEN exactly one Sandbox_Variant is under consideration for promotion and the Sandbox_Variant meets every promotion condition in Acceptance Criterion 2, THE Generic_Swarm_Business_OS SHALL permit production promotion.
6. WHEN more than one Sandbox_Variant is under consideration for promotion, THE Generic_Swarm_Business_OS SHALL block production promotion.
7. IF evidence retention for a blocked Sandbox_Variant promotion fails, THEN THE Generic_Swarm_Business_OS SHALL continue non-promotion operations while keeping production promotion blocked.
8. WHEN a Sandbox_Variant receives Canary approval while no Canary is active, THE Generic_Swarm_Business_OS SHALL retain the approval and wait for Canary activation before operating the Sandbox_Variant.
9. WHEN a Sandbox_Variant receives Canary approval while the approved Canary is active, THE Generic_Swarm_Business_OS SHALL operate the Sandbox_Variant only in the approved Canary scope.
10. IF a Canary criterion fails, THEN THE Generic_Swarm_Business_OS SHALL stop the Canary, perform the rollback plan, and retain the Canary evidence.

### Requirement 8: Evaluation and Product-Bar Evidence
**User Story:** As a quality owner, I want reproducible evidence for every operational capability, so that product claims are testable.
#### Acceptance Criteria
1. THE Generic_Swarm_Business_OS SHALL retain at least 20 golden JSON tasks and run regression, adversarial, and historical-replay evaluations against the retained golden JSON tasks.
2. WHEN an Evaluation_Suite run completes, THE Generic_Swarm_Business_OS SHALL retain a pass or fail result for every evaluated task and named check.
3. WHEN a blocking Evaluation_Suite check fails during evaluation, THE Generic_Swarm_Business_OS SHALL immediately block the next configured transition, including a transition already in progress, and retain the evaluation result.
4. WHILE a blocking Evaluation_Suite check has failed, THE Generic_Swarm_Business_OS SHALL continue every non-blocking Evaluation_Suite check to completion.
5. WHEN every blocking Evaluation_Suite check passes, THE Generic_Swarm_Business_OS SHALL permit the next configured transition regardless of previous blocking failures or other system state.
6. WHEN Product_Bar evidence is evaluated, THE Generic_Swarm_Business_OS SHALL present independent pass or fail evidence for every named Product_Bar capability.
7. IF Product_Bar evidence does not include an E1 pass result, THEN THE Generic_Swarm_Business_OS SHALL mark the Product_Bar incomplete.
8. WHEN an Evaluation_Suite run repeats an exactly identical golden JSON task with an exactly identical configuration, THE Generic_Swarm_Business_OS SHALL preserve the original result and retain the repeated run as a separate result.

### Requirement 9: Video Pack Safety and Delivery Controls
**User Story:** As a video-domain owner, I want the Video_Pack governed by host controls, so that artifacts cannot bypass quality, rights, or provenance gates.
#### Acceptance Criteria
1. THE Generic_Swarm_Business_OS SHALL retain exactly 114 Video_Pack agents and one inventory entry for every Video_Pack agent.
2. THE Generic_Swarm_Business_OS SHALL provide an end-to-end Video_Pack spine using stub media tools without external resource access.
3. WHEN a Video_Pack blocker, including a ComplianceAgent blocker, is detected, THE Generic_Swarm_Business_OS SHALL prevent new graph steps in fewer than 5 seconds and preserve and display the graph state until the blocker is resolved.
4. WHEN a video artifact is requested for release and immutable version lineage is acyclic, every named release gate and quality check passes, and no blocker remains unresolved, THE Generic_Swarm_Business_OS SHALL release the video artifact.
5. IF immutable version lineage is cyclic, ambiguous, or unknown, a named release gate or quality check fails, or a blocker remains unresolved, THEN THE Generic_Swarm_Business_OS SHALL deny release, display every unmet condition, and retain release-request data.

### Requirement 10: Explicit Delivery Limits
**User Story:** As a sponsor, I want honest implementation boundaries, so that delivery does not claim unsupported autonomy or services.
#### Acceptance Criteria
1. THE Generic_Swarm_Business_OS SHALL expose only FastAPI paths matching `/api/v1/*` as public control-plane paths and SHALL execute Graph_Engine in the same Host process.
2. THE Generic_Swarm_Business_OS SHALL use local adapters for Product_Bar operations without a live external SaaS or media dependency.
3. WHEN a request contains one or more operations, THE Generic_Swarm_Business_OS SHALL evaluate each requested operation individually for automatic production promotion, a production Host-code rewrite, unbounded orchestration, or orchestration without recorded authorization regardless of request authorization status.
4. IF any requested operation is automatic production promotion, a production Host-code rewrite, unbounded orchestration, or orchestration, including read-only orchestration, without recorded authorization, THEN THE Generic_Swarm_Business_OS SHALL return a prohibited-operation error and leave production unchanged.
5. IF delivery of a prohibited-operation error fails, THEN THE Generic_Swarm_Business_OS SHALL block production changes.
6. WHEN an authorized request does not require a prohibited operation and a separate non-prohibited operation returns an error, THE Generic_Swarm_Business_OS SHALL permit the authorized production change.

## Approval
- **Status:** Draft requirements created for review.
- **Scope decision:** Reimplementation occurs only in `C:\Project\common-agent-swarm-ops`; `C:\Project\generic-swarm-ops` remains read-only comparison material and is not executed, modified, copied as unreviewed code, or adopted as the source of implementation truth.
- **Authority decision:** `C:\Project\common-agent-swarm-ops\structure.md` governs architecture and product-bar intent; these requirements are the implementation-facing acceptance baseline.
- **Review resolution:** Review refinements were incorporated where compatible. Suggested relaxations that conflict with the Structure_Contract's validation, provenance, authorization, or sandbox rules are resolved in favor of the stricter authoritative contract.
- **Unresolved question:** None. This requirements phase is ready for user review or advancement to design.
