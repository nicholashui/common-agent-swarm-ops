# VA Agent Structure Mapping

**Version:** 1.0  
**Status:** Binding frontend contract supplement  
**Date:** 2026-07-19  
**Applies to:** [`frontend_redesign.md`](frontend_redesign.md) and every `ui_*.md` specification in this directory.

## Overview

This document prevents the common-first redesign from losing the runtime, quality, provenance, and workflow controls defined by `va-agent-swarm`. It maps the VA production-domain structures to the reusable `CommonAgent`, `CommonSwarmPattern`, and `SwarmInstance` concepts used by common-agent-swarm-ops.

The common model remains domain-neutral. VA video-production fields are a versioned domain adapter, not a replacement for generic agent, graph, or governance contracts.

**Authoritative VA references:**

- `c:\Project\va-agent-swarm\study\ai_agent_video_production_workflow.md`
- `c:\Project\va-agent-swarm\study\common-agent-structure.html`
- `c:\Project\va-agent-swarm\study\ui\backend_agent_management.md`
- `c:\Project\va-agent-swarm\study\ui\architecture_communication.md`
- `c:\Project\va-agent-swarm\study\ui\agent_management_ui.md`

## Requirements

### Requirement 1.1: Complete common-agent representation

Every Common Agent view shall represent its identity, scope, capabilities, policies, runtime constraints, quality contract, critique relationships, provenance obligations, and published version.

### Requirement 1.2: Complete workflow representation

Every Swarm Instance view shall represent its revisioned graph, task/dependency/gate state, execution lifecycle, common-version provenance, budget, checkpoints, and recovery state.

### Requirement 1.3: Governed artifact handoffs

A workflow shall represent versioned artifacts and their parent lineage, technical specification, rights/consent, continuity, QC state, delivery targets, and signed provenance references.

### Requirement 1.4: Evidence-based quality and approval

The UI shall distinguish L1 specification validation, L2 role-rubric evaluation, L3 stakeholder/baseline preference, peer critique, GateKeeper/Judge outcome, and human approval evidence.

### Requirement 1.5: Safe operational observability

The UI shall show only redacted, authorized events and trace references; it shall preserve event sequence, replay context, auditability, and action recovery state without exposing secrets or raw tool authority.

## Canonical mapping

| VA source concept | Common-agent-swarm-ops concept | Required UI representation |
|---|---|---|
| `AgentDefinition` | `CommonAgentVersion.spec` | Agent detail, registry card, canvas node, API schema |
| 114-agent roster/category | Common Agent taxonomy/domain tags | Registry filters, blueprint slots, agent detail category |
| VA production template A–J | `CommonSwarmPatternVersion` | Pattern/blueprint preview, composer, canvas group |
| Production DAG/task | `SwarmInstance.graph` + run projection | Canvas nodes/edges, activity board/timeline, monitoring trace |
| Agent state/task queue | node execution state | Canvas status strip, activity, monitoring, notifications |
| Shared artifact manifest | `ArtifactProjection` | Canvas inspector, activity, audit, delivery/blueprint views |
| Critique bus | `CritiqueProjection` | Node/context panels, activity feed, notification/audit records |
| L1/L2/L3 quality gate | `EvaluationProjection` + `GateProjection` | Eval dashboard, gate drawer, agent detail, run timeline |
| GateKeeper/Judge + human decision | approval gate | Canvas/run controls, notifications, audit, mobile approval |
| C2PA/right/consent lineage | provenance and release projection | Artifact/audit detail, activity, blueprint/delivery readiness |

## Components and Interfaces

### Common Agent version contract

```ts
interface CommonAgentVersionSpec {
  id: string;
  version: string;
  canonicalName: string;
  category: string;
  description: string;
  responsibilities: readonly string[];
  outOfScope: readonly string[];
  escalationTargets: readonly string[];
  approvalAuthority: "none" | "recommend" | "gate" | "release";
  systemPromptReference: string;
  architecturePattern: "self_refine" | "reflexion" | "react" | "debate" | "constitutional" | "graph";
  modelPolicy: { primary: string; fallbacks: readonly string[] };
  tools: readonly ToolPermission[];
  qualityRubric: readonly RubricMetric[];
  acceptsCritiqueFrom: readonly string[];
  commentsOn: readonly string[];
  runtimeLimits: { maxIterations: number; maxCost: string; maxConcurrency: number; timeoutSeconds: number; maxRetries: number };
  knowledgeBindings: KnowledgeBindings;
  inputSchema: JsonSchemaReference;
  outputSchema: JsonSchemaReference;
  provenancePolicy: ProvenancePolicy;
}
```

`ToolPermission` includes identifier, purpose, access scope, allowed operation types, and audit requirement. `KnowledgeBindings` separates licensed references, RAG sources, few-shot examples, correction memory, constitutional rules, and evaluation benchmarks. The UI must render a redacted tool/result summary only; credentials and executable connection details are never UI data.

### Swarm graph, task, and lifecycle contract

```ts
interface SwarmTaskProjection {
  taskId: string;
  nodeId: string;
  agentVersion: { id: string; version: string };
  state: "idle" | "queued" | "running" | "self_refine" | "waiting_for_critique" | "blocked" | "failed" | "complete";
  iteration: number;
  retryCount: number;
  dependencies: readonly { taskId: string; condition?: string; gateId?: string }[];
  constraints: { model?: string; generationTool?: string; budgetRemaining?: string; maxCost?: string };
  checkpointReference?: string;
  metrics: Record<string, number | string>;
}
```

A node is not simply green/red. The screen must distinguish queued work, active work, bounded revision, critique wait, missing-input/approval block, retryable failure, terminal failure, and completion. Replays must identify graph revision, checkpoint, input-artifact versions, and pinned common versions.

### Artifact, critique, and gate interfaces

```ts
interface ArtifactProjection {
  artifactId: string; version: string; parentAssets: readonly string[];
  briefScope: string; technicalSpec: Record<string, string>; rightsAndConsent: RightsState;
  continuityState: Record<string, string>; qcStatus: QualityGateStatus;
  targetChannels: readonly string[]; provenanceManifestReference: string;
}
interface CritiqueProjection {
  fromAgent: string; toAgent: string; severity: "blocker" | "major" | "minor" | "nit";
  artifactReference: string; rubricScore?: number; evidenceReferences: readonly string[];
  message: string; status: "open" | "addressed" | "dismissed"; timestamp: string;
}
interface QualityGateStatus {
  l1: { passed: boolean; requiredFieldsComplete: boolean };
  l2: { score: number; threshold: number; rubric: string };
  l3: { result: "parity" | "surpass" | "below_baseline"; baselineReference: string };
  gate: { id: string; state: "pending" | "approved" | "rejected"; judgeEvidence: readonly string[] };
}
```

Rights, consent, provenance, and release state are mandatory where an artifact can leave the system. Missing required artifact fields block downstream tool execution and are displayed as actionable validation failures.

## Event and API alignment

The current VA reference uses production-oriented REST and WebSocket contracts. The common control plane will retain versioned `/api/v1` contracts and map the source semantics without claiming that VA endpoints already exist here.

| VA command/event | Common control-plane equivalent | UI behavior |
|---|---|---|
| `POST /api/productions` | `POST /api/v1/swarms` then `POST /api/v1/swarms/{id}/runs` | Create graph revision, validate, preview/dispatch |
| Gate decision | `POST /api/v1/approvals/{id}/decision` | Render criteria, artifacts, evidence, comment, and resulting graph route |
| Critique submission | `POST /api/v1/runs/{id}/critiques` | Deliver directed critique to the correct node/agent and show resolution state |
| Agent retry/skip | `POST /api/v1/runs/{id}/tasks/{taskId}/retry` or `/skip` | Show eligibility, recovery reason, and immutable audit record |
| Artifact detail | `GET /api/v1/runs/{id}/artifacts/{artifactId}` | Show lineage, QC, rights, delivery, and provenance projection |
| `agent_state_change` | `run.task_state_changed` SSE event | Update node and activity state from the lifecycle union |
| `artifact_created` | `run.artifact_created` SSE event | Add a redacted artifact projection and lineage reference |
| `critique_message` | `run.critique_created` SSE event | Update critique feed, node badge, and notification |
| `gate_ready` / `gate_resolved` | `approval.requested` / `approval.resolved` SSE events | Open or resolve an approval surface with evidence |
| budget/tool/metric events | `run.budget_updated`, `run.tool_completed`, `run.metric_updated` | Update observability without exposing raw credentials or secrets |

## UI implementation rules

1. A generic screen may hide VA-specific fields for non-VA domains, but it must preserve them in data contracts and display them when present.
2. Cards can summarize; detail, canvas inspector, activity, audit, and API screens must expose drill-down references for required provenance, gate, critique, task, and artifact data.
3. All UI actions mutate a server-owned resource through an authorized command. No UI action is allowed to construct a privileged tool request, approval operation, or provenance signature.
4. Common version updates, retries, skips, gate decisions, and rollout operations always show affected graph revisions/runs and retain the prior immutable state.
5. The frontend uses server-provided, redacted event payloads. It does not infer approval, rights, quality, or provenance state from a color alone.

## Correctness Properties

### Property 1: Agent completeness

Each displayed Common Agent can be resolved to a published version containing the fields in the Common Agent version contract.

**Validates: Requirements 1.1**

### Property 2: Reproducible runs

Every rendered run node resolves to one graph revision, task state, checkpoint reference when applicable, and pinned Common versions.

**Validates: Requirements 1.2**

### Property 3: Governed artifact progression

An artifact cannot be displayed as delivery-ready unless its required handoff, QC, rights/consent, and provenance fields are present and its applicable gate is approved.

**Validates: Requirements 1.3, 1.4**

### Property 4: Redacted observability

Live updates, audit views, and replay controls show authorized summaries and references only; privileged inputs and secrets cannot enter a UI projection.

**Validates: Requirements 1.5**

## Testing Strategy

- Contract-test all Common Agent, task, artifact, critique, gate, evaluation, and event payload schemas against frontend types.
- Fixture-test a VA production template with parallel branches, a self-refine loop, a critique wait, a blocked approval, retry exhaustion, and a C2PA-signed delivery artifact.
- Test that missing manifest fields prevent task dispatch, invalid critique relationships are rejected, and an unapproved gate cannot advance a dependent task.
- Visual/accessibility-test lifecycle and quality labels so status is never communicated by color alone.
