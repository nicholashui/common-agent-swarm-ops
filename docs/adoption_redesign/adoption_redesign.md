# Adoption Plan: self-contained video pack on `common-agent-swarm-ops`

**Status:** Proposed — implementation not started<br>
**Date:** 2026-07-20<br>
**Decision owner:** Product and architecture owners for the common host and video pack<br>
**Scope:** A safe, reusable implementation model for a domain-neutral MMA host and its checked-in video domain pack.

## 1. Executive decision

Adopt a **domain-neutral host and checked-in domain-pack** model. `common-agent-swarm-ops` remains the only control plane for many multi-agent (MMA) systems. Its `business/video/` directory becomes the self-contained, checked-in source of truth for the pinned and adapted common video pack: video roles, prompts, rubrics, workflow graphs, knowledge indexes, policies, mappings, and provenance needed for local design and validation. `va-agent-swarm` and `generic-swarm-ops` are provenance and reviewed future-update inputs only; neither is a runtime or design dependency.

This decision satisfies both non-negotiables:

| Requirement | Binding decision |
|---|---|
| Video behavior is self-contained without a second control plane | `business/video/` owns the pinned/adapted video semantics and compiles only through the common host. External VA/generic material is retained as reviewed historical provenance, never imported at runtime or required to interpret local design. |
| The common project supports dozens of MMA systems | The host remains domain-neutral: every domain uses the same versioned declarative pack contract, isolated namespaces, generic governance hooks, and common Agent Learning Contract (ALC). Video receives no custom scheduler, public API plane, or governance bypass. |

The target is not a repository merge or a second video platform. It is a controlled, provenance-preserving adaptation into a local pack that the common host validates, registers, executes, audits, and learns from through shared contracts.

## 2. Audit basis and confidence

This assessment is based on a local review performed on 2026-07-20 of the two repositories and the reference adoption plan in `generic-swarm-ops`. The reference is useful historical context; this plan prioritizes artifacts currently present in the two target repositories. No external providers, credentials, media APIs, or production environments were accessed.

| Repository / asset | Confirmed state | Audit conclusion |
|---|---|---|
| `va-agent-swarm` | A detailed specification corpus: 114 agents across 10 categories, workflow and quality designs, source material, and planned integrations. Its root contains no application package, test suite, dependency manifest, or CI implementation. | Treat as pinned historical provenance and a reviewed future-update input; adapt compatible material into the checked-in common pack rather than make it a dependency. |
| `common-agent-swarm-ops` | FastAPI host modules for registry, workflow engines, memory, governance, evaluation, evidence, and a Next.js frontend. It has property, unit, integration, and video tests. | Reuse its host capabilities, keep its contracts domain-neutral, and finish the learning lifecycle. |
| Existing `business/video` in common | 114 `registered`, non-active (`L0`) agent records and an inventory are present. `workflows/pack_spine.json` is the sole local safe stub graph; no workflow-role map or blueprint-realizing graph is present. | Treat it as an interim catalog and safe stub only, not as operational realization of the blueprint. The local pack becomes authoritative only as its pinned/adapted contents and evidence are checked in. |

## 3. Current architecture and technical-debt audit

### 3.1 Video blueprint provenance and pack-realization gaps

**Strengths**

- The blueprint defines a coherent video-production hierarchy: orchestration, artifact handoffs, quality and continuity, delivery, observability, a shared seven-stage skeleton, and ten named workflow archetypes.
- Its roster documents specialized roles, including orchestration, quality/compliance, critique, and workflow-support responsibilities, with intended quality criteria, critique relationships, tools, and patterns.
- The build guidance supports contracts before code, a deterministic vertical slice before breadth, one shared agent lifecycle, provider abstractions, and mock-only media behavior in CI.

**Gaps and risks**

- Blueprint role names and the 114 common `video.*` IDs are not interchangeable. No reviewed workflow/phase role-to-common mapping exists, and a source/document role must not force creation of a new agent.
- A roster, a source corpus, or a graph stub does not execute the blueprint. Every explicitly documented workflow family and required phase needs a safe local graph definition or a reviewed, explicit gap/deferral.
- The blueprint's external topology and provider names are reference material, not an approved runtime. Recreating a separate FastAPI, graph/event-bus, governance, or approval plane would duplicate identity, audit, retry, and approval semantics.
- Provider names and safety assumptions remain unaudited specifications; all tools stay behind host-controlled, allow-listed, mockable interfaces with no credentials or network access.

### 3.2 `common-agent-swarm-ops`

**Strengths**

- The target architecture specifies a FastAPI-only public control plane, portable workflow definitions compiled to a graph engine, legacy compatibility, governance, checkpoints, audit, and evidence-driven evolution.
- Existing modules cover registry validation, activation, memory, runs, governance, graph compilation, evaluation, evidence, and versioned API routes.
- The host already exposes domain registration and has tests covering authority boundaries, manifests, activation, memory, graph budgets, migration, video inventory, release controls, and governance.
- Production activation is fail-closed: a learning-required agent needs a single matching learning contract, an enabled reflection hook, and approved memory scopes.

**Gaps and misaligned capabilities**

- The current agent-pack JSON schema is video-specific: prompt and rubric identifiers are required to begin with `video.` and its model policy permits only a local deterministic provider. It cannot yet describe arbitrary MMA systems.
- Required generic schemas referenced by the architecture (`domain-manifest` and `learning-log`) are absent from the current `business/schemas` directory.
- The activation gate validates the *presence* of an ALC but does not demonstrate mandatory episode capture, pre-action retrieval, assessed reflection, knowledge reuse, or measurable knowledge growth.
- The existing video pack is catalog-only: all inspected agents are `registered`/L0, the manifest requests no production activation, and its only present workflow uses local stub media behavior. This is correct for safety, but is not operational video autonomy.
- Video release artifacts and `/api/v1/video/*` routes are useful domain capabilities but are coupled directly into the host code. They should become pack-owned schemas and extensions behind generic artifact/release interfaces.
- The root README describes configuration synchronization, whereas `structure.md` describes an MMA host. The public documentation and release narrative need reconciliation.
- Current backend dependencies are intentionally minimal (FastAPI plus developer tools). Durable production stores, package signing, load tooling, provider clients, and observability adapters must be introduced deliberately with ADRs and locked versions.

### 3.3 Reconciliation rule

When documentation and checked-in artifacts disagree, executable code, schemas, tests, and inventories are the current-state evidence. `structure.md` remains the architecture intent. Any difference—such as the documented video workflow count versus the single workflow present—must be tracked as an explicit migration gap, not silently treated as complete.

## 4. Target architecture and ownership boundaries

```text
┌───────────────────────────────────────────────────────────────────────┐
│ common-agent-swarm-ops — universal MMA host                           │
│ FastAPI control plane · graph execution · governance · audit · ALC    │
│ registry · data isolation · generic provider protocols · evaluation   │
└──────────────────────────────┬────────────────────────────────────────┘
                               │ validates and registers immutable local pack releases
                               ▼
┌───────────────────────────────────────────────────────────────────────┐
│ business/video — checked-in, self-contained common video pack         │
│ common video.* IDs · mappings · local graphs · prompts/rubrics ·      │
│ policies · knowledge indexes · provenance · pack-specific evaluations │
└───────────────────────────────────────────────────────────────────────┘
                               ▲
                               │ reviewed, pinned provenance and future-update inputs only
                     va-agent-swarm / generic-swarm-ops
```

### 4.1 Ownership rules

| Asset | Owner and canonical location | Host responsibility |
|---|---|---|
| Pinned/adapted video roles, prompts, rubrics, workflow graphs, workflow-role mappings, critique policy | `common-agent-swarm-ops/business/video/` | Schema validation, versioned registration, execution, and audit only |
| Video knowledge indexes and provenance | `common-agent-swarm-ops/business/video/` | Enforce access, retention, redaction, and audit policies |
| External VA/generic source material | Immutable provenance metadata and reviewed import inputs | Never load it as a runtime/design dependency |
| Video tools and provider choices | Pack-local, capability-scoped configuration | Invoke only through a generic allow-listed provider protocol; default to local stubs |
| Generic lifecycle, graph compiler, authorization, audit, checkpoints, evaluation engine | Common host | Implement and version |
| ALC, event, artifact, and manifest schemas | Common host | Define compatible versions and validate packs |
| Cross-domain fixtures | Common host | Must be synthetic and contain no video business semantic content |

**Boundary controls**

1. `business/video/` must contain all video semantics required to design and validate its pinned pack; upstream repositories are historical provenance, not required paths or imports.
2. The video pack is declarative data and approved adapters; arbitrary package code cannot execute during registration, and it cannot create a scheduler, governance path, or public control plane outside the common host.
3. Every invocation carries `organization_id`, `domain_id`, `pack_version`, `agent_id`, `workflow_id`, `run_id`, and a correlation ID.
4. Cross-domain data access, undeclared tool IDs, undeclared outbound destinations, missing required gates, and unmapped implemented roles fail closed and create audit evidence.
5. A pack upgrade is copy-on-write: prior runs remain reproducible against the exact approved local pack and contract versions.

### 4.2 Standardized domain-pack contract

Implement an SDK-independent, JSON-schema-first package format under `common-agent-swarm-ops/business/video/`. The host supports any domain identifier; `video` is a pack value, never a hard-coded host branch.

```text
common-agent-swarm-ops/
  business/video/
    manifest.json
    inventory.json
    agents/<agent_id>/agent_spec.json
    WORKFLOW_ROLE_MAP.json
    workflow_coverage.json
    prompts/<id>.md
    rubrics/<id>.json
    workflows/<id>.dna.json
    policies/
    knowledge/index.json
    tools/adapters.json
    evals/{golden,adversarial,regression}/
    provenance/sources.json
    release.json
```

The pack manifest must contain: immutable `domain_id`, semantic `pack_version`, supported host-contract range, content digest, signer identity, declared agents and workflows, capability-scoped tool IDs, required ALC version, data classifications, evaluation suite references, workflow/mapping coverage references, and optional UI extension metadata. The host stores the manifest digest and signature result with the registration record.

### 4.3 Workflow realization and role-mapping contract

The local pack must translate the blueprint’s explicitly documented workflow families—Viral Hook Clip/Meme, UGC-Style Performance Ad, Animated Explainer, Personalized Birthday Video, AI Multi-Scene Short Film, Corporate Training Video, Music Video, AI Avatar Talking-Head, Documentary “Explained” Episode, and Feature-Length AI Film—and every required phase into a safe local executable graph definition, or record a reviewed explicit gap/deferral. The shared skeleton remains Greenlight, Pre-production packet, Production packet, Post master, Review and release pack, Distribution package, and Post-launch learning set; feature-film development and pre-production remain distinct where documented.

`workflow_role_map.json` is the human-reviewed mapping artifact for each documented role in each workflow and phase. Each record includes workflow and phase context, the source/document role, rationale, reviewer and review time, mapping status, maturity state, and activation state, and resolves to **exactly one** of: (a) one existing common `video.*` agent ID, (b) a named composite consisting only of common `video.*` IDs, or (c) a documented gap/deferral. A differing source role name never by itself requires a new agent. For an implemented mapping, the corresponding local agent `SPEC.md` must state its runtime binding, typed handoffs, critique/lead responsibilities, and refinement or escalation behavior.

A realizing graph declares phase nodes and typed artifact handoffs; lead and critic roles; bounded critique, refinement, and rollback paths; finite execution budgets; required quality and risk gates; required human approvals; and only declared, allowed tools. A roster entry, mapping row, source text, or graph stub is not graph realization. `business/video/workflows/pack_spine.json` remains the sole current safe stub; until mappings and graphs pass these gates, the pack is not operationally equivalent to the blueprint. Providers, credentials, network access, and production activation remain out of scope and fail closed.

### 4.4 Generic APIs and schemas

Version the following contracts under `/api/v1` and preserve backward compatibility within a supported major version:

| Contract | Required fields and behavior |
|---|---|
| `DomainManifest` | Domain identity, version, host compatibility range, capability declarations, signatures, agent/workflow references, data classes, and deprecation metadata. |
| `AgentDefinition` | Domain-neutral role, allowed tools, risk profile, model/budget policy, prompt and rubric references, critique edges, and lifecycle state. No `video.` literals. |
| `WorkflowDefinition` | Portable graph IR with nodes, handoffs, guards, memory read/write declarations, rollback, budget, and approval requirements. |
| `AgentLearningContract` | Agent-scoped memory policy, retrieval policy, reflection policy, evaluation threshold, retention policy, and human-promotion policy. |
| `LearningEpisode` | Immutable step/run outcome: agent, inputs by reference, output/artifact references, action result, critique, evaluator score, provenance, and classification. |
| `Lesson` | Agent-scoped, versioned, assessed knowledge item with source episode references, confidence, scope, expiry/review date, reuse counter, and revocation state. |
| `RetrievalRecord` | What knowledge was retrieved before an action, ranking/filters, pack version, and whether it influenced the final decision. |
| `ImprovementProposal` | Sandbox-only prompt/rubric/tool-policy/workflow variant, evidence, evaluation results, reviewer decision, rollback reference, and promotion state. |
| `ArtifactHandoff` | Generic immutable artifact lineage, ownership, classification, integrity, approval and provenance references. The video pack adds video metadata through a pack extension schema. |

## 5. Mandatory autonomous learning design

The ALC is the mechanism that turns learning from an aspiration into an enforceable lifecycle. It is required for every agent whose `requires_learning` flag is true; the common video pack must set it for every video agent.

### 5.1 Required lifecycle

1. **Validate before registration.** The manifest, agent definition, allowed memory scopes, retention class, evaluator reference, and reflection policy must pass schema and policy checks.
2. **Retrieve before acting.** Before an agent node runs, the host records a `RetrievalRecord` after fetching approved, domain- and agent-scoped lessons. Missing permitted knowledge is a valid empty result, not a reason to bypass the record.
3. **Capture an episode after acting.** Every completed, failed, blocked, retried, or escalated agent node emits one immutable `LearningEpisode`. Sensitive payloads are stored as approved references or redacted summaries, never copied indiscriminately.
4. **Reflect and assess.** A deterministic policy decides whether a step, run, or batch triggers reflection. Reflection produces candidate lessons; an evaluator validates format, provenance, safety, domain policy, and measured utility before a lesson becomes retrievable.
5. **Measure reuse and growth.** The host links later actions to retrieved lessons and tracks usage, outcome delta, staleness, conflicts, and revocations per agent.
6. **Improve only in a sandbox.** Repeated, assessed failure may create an `ImprovementProposal`; it cannot alter a live prompt, rubric, tool policy, or workflow without evaluation evidence and the designated human approval.
7. **Expire, review, and delete safely.** Lessons must have retention/review policies. Revocation hides an item immediately, retains audit metadata, and prevents future retrieval.

### 5.2 Activation invariant

An agent cannot transition from `registered` to `active` unless all statements are true:

```text
requires_learning = false
OR
(
  one valid ALC names the agent
  AND approved agent-scoped memory exists
  AND pre-action retrieval is enabled
  AND episode capture is enabled
  AND reflection has an evaluator and retention policy
  AND its required test/evaluation suite has passed for the pack version
)
```

The host re-checks the invariant when a pack, ALC, workflow, policy, or tool capability changes. It fails the transition atomically and preserves the prior lifecycle state. A successful activation emits a signed audit event with the evaluated contract and evidence digests.

### 5.3 Measurable acceptance criteria

- **Coverage:** 100% of active learning-required agents produce a retrieval record and episode for every executed node.
- **Isolation:** an agent can retrieve only lessons approved for its organization, domain, pack version range, and memory scope.
- **Quality:** a lesson becomes active only after its configured evaluation threshold and provenance checks pass.
- **Traceability:** every active lesson has source episode references; every output can identify the lessons retrieved for it.
- **Safety:** no lesson can cause an external action, lower a risk tier, grant a tool, or change a live prompt/workflow without a separately approved sandbox promotion.
- **Operability:** the host exposes per-agent counts for episodes, validated lessons, reuse, stale/revoked items, evaluation outcomes, and escalation rate without exposing sensitive contents.

## 6. Phased migration roadmap

Each phase ends with a reviewable evidence record. Advancing requires the exit criteria, not calendar time.

| Phase | Scope and implementation steps | Exit criteria and rollback |
|---|---|---|
| 0. Governance and source baseline | Freeze reviewed VA/generic provenance revisions; build a canonical local source index with hashes, owner, license/consent classification, and disposition into the common pack. Record ADRs for local ownership, the host/pack boundary, contract versions, provider policy, and no-production-activation scope. | Each source asset is retained as provenance, adapted locally, explicitly deferred, or rejected. Rollback removes only generated local indexes; upstream sources remain untouched. |
| 1. Generic contract hardening | Add neutral manifest, agent, ALC, learning, artifact, and provider schemas; remove video prefixes from generic schemas; version registration responses; implement signature/digest validation and compatibility negotiation. | A synthetic non-video pack and the local video skeleton validate without host code changes. No external source is needed at runtime or design time. |
| 2. Learning enforcement | Add lifecycle interceptors for retrieval, episode capture, reflection assessment, retention, metrics, and sandbox proposals. Persist contracts and learning records with tenant/domain/agent boundaries. Make the activation invariant authoritative. | Negative tests prove bypass attempts fail; positive tests prove individual growth and retrieval are observable. Legacy behavior remains available behind a migration feature flag. |
| 3. Local pack, role mapping, and graph inventory | Build the checked-in pack from the source index. Create the reviewed workflow-role map for every documented workflow/phase role and a workflow coverage ledger that marks each family/phase as graph-realized or explicit reviewed gap/deferral. Maintain the 114 common IDs; use existing IDs, named composites, or gaps rather than renaming source roles into new agents. | Mapping completeness and uniqueness pass; implemented mappings reference local `SPEC.md` runtime bindings and handoff/critique details. The pack remains 114 non-active registered agents; no live provider is enabled. |
| 4. Safe graph realization | Translate each documented workflow family and required phase to local common-ID graph definitions incrementally, starting with deterministic stub-only paths. Each graph declares phase nodes, typed artifact handoffs, lead/critic roles, bounded critique/refinement/rollback, finite budgets, quality/risk gates, human approvals, and allowed tools. | Deterministic offline validation proves graph-reference integrity and gate coverage. `pack_spine.json` remains the only current safe stub until a specific graph passes its gates; no graph becomes production-active. |
| 5. Controlled breadth and maturity | Complete or explicitly defer remaining workflow families across planning, generation, editorial, sound, quality, localization, distribution, analytics, and support. Promote only a workflow whose local graph, mapping, evaluations, and human review pass. | Every documented workflow/phase is graph-realized or an explicit reviewed gap; maturity records distinguish cataloged, mapped, graph-validated, and any separately approved future activation. |
| 6. Multi-domain proof | Onboard at least two synthetic or independently owned non-video packs through the same schema, registry, learning, and UI extension paths. Eliminate host branches that special-case video except generic extension loading. | Domain isolation, registration, activation, observability, and lifecycle operations pass with at least 24 concurrently registered packs in the load environment. |
| 7. Cutover and maintenance | Publish compatibility matrices, migration guides, runbooks, dashboards, deprecation schedules, incident response procedures, and local pack update policy. The checked-in common pack is the only source of current video behavior. | Completion is evidence-based, not catalog-based. Rollback remains an immutable pack-version reversion plus data-safe lesson revocation; providers, network access, and production activation remain separately out of scope. |

## 7. Video pack architectural realization

The checked-in common video pack realizes the blueprint on the shared host—not in a second orchestration platform. Source material retains its domain insight as provenance while the host remains the only executable control plane.

- **Orchestration:** encode the documented supervisor, planner, router, judge, pipeline, fan-out/fan-in, critique, and human-gate patterns as portable local workflow graphs. The host graph compiler owns execution and checkpointing.
- **Agent factory:** every implemented video role is a declarative use of the generic lifecycle. The workflow-role map records whether a documented role is one common agent, a named composite, or a gap; no source-name mismatch creates a new agent automatically.
- **Artifacts:** use the generic immutable handoff contract with pack-local extension fields for rights/consent, continuity, media quality, channel requirements, and provenance. Graphs must type each phase handoff; video release remains blocked until all required gates pass.
- **Tools:** represent media, voice, editing, research, and publishing capabilities through generic protocols. Pack configuration selects only approved allow-listed tools; host adapters enforce authorization, budgets, retries, audit, and local stub/mock mode.
- **UI:** retain video terminology in a pack extension manifest where needed. The common frontend supplies only authenticated shell, generic projections, accessibility, audit visibility, and extension slots.
- **Knowledge:** retain checked-in, classified video knowledge and provenance in `business/video/`. The host indexes approved references but never gives one domain access to another domain’s knowledge.

## 8. Testing and verification strategy

### 8.1 Required automated layers

| Layer | Scope | Required evidence |
|---|---|---|
| Schema and unit tests | Neutral contracts, digest/signature checks, lifecycle states, ALC validation, retention, lesson scoring, provider allow-lists, artifact lineage, workflow-role-map shape, and graph-reference rules. | Deterministic tests plus property-based tests for contracts and state transitions. |
| Property tests | Randomized domains, agents, scopes, event sequences, pack versions, failure/retry paths, malicious identifiers, graph edges, and mapping combinations. | Invariants for isolation, activation atomicity, lineage acyclicity, no cross-domain retrieval, no unapproved promotion, finite graph traversal, and one valid resolution per mapped role. |
| Integration tests | Local video pack registration, graph compilation, mapping-to-`SPEC.md` bindings, typed handoffs, critique blockers, approval/risk/quality gates, retrieval→episode→reflection path, and immutable release checks. | Offline, mock-only provider tests; no credentials or network use. |
| End-to-end tests | A fixed-brief local graph through a released-*readiness* decision, with UI projections and audit records. | Fixed seeds, fixture digests, a trace bundle, explicit gate outcomes, and proof that no production activation occurred. |
| Compatibility tests | Current and previous supported host/local-pack contract versions. | Consumer-driven contract suite in this repository. |
| Security tests | Tenant/domain isolation, tool namespace denial, schema/path traversal rejection, secret redaction, malicious pack rejection, lesson poisoning attempts, and provider/network denial. | Fail-closed assertions and audit-event checks. |
| Performance and load tests | Registration, retrieval, graph execution, and event fan-out with synthetic packs and stub tools. | Capacity report for at least 24 concurrently registered domains; SLOs must be approved before production. |
| Resilience tests | Provider timeout, duplicate delivery, partial persistence, restart, replay, approval loss, rollback, critique-limit exhaustion, and explicit-gap handling. | Idempotency, recovery, immutable-version, and bounded-path evidence. |

### 8.2 Test gates

Run focused backend tests first (`python -m pytest -q` with appropriate selectors), followed by type checking and linting. Run existing repository gates—`npm run sdd:check`, `npm run sync:check`, and `npm test -- --silent`—for changes that touch the common project’s automation. CI must keep provider integrations disabled by default and use approved mock adapters only.

Do not declare a workflow mature, operationally equivalent to the blueprint, or production-ready from a catalog, mapping, graph stub, or unit-test success. Promotion requires complete reviewed mapping coverage or explicit reviewed gaps; deterministic offline graph validation with valid local `video.*` references; typed handoffs; bounded critique/refinement/rollback; declared budgets/tools; required quality, risk, and human-approval gates; declared domain evaluations; a reproducible trace; no unresolved security or data-governance finding; and proof that no production activation, live provider, credential, or network path was enabled.

## 9. Long-term maintenance and reuse rules

1. **Versioning:** Use semantic versions independently for host API, pack format, ALC format, and each domain pack. A host publishes a supported pack/ALC compatibility range; a pack declares the range it requires.
2. **Change control:** Contract-breaking changes require an ADR, migration plan, consumer tests, a deprecation window, and an explicit rollback plan. Video behavior changes stay in the checked-in `business/video/` pack; upstream material is incorporated only through reviewed, provenance-preserving updates.
3. **Contribution workflow:** Use short-lived branches, conventional commits, scoped reviews, deterministic tests, and a code-owner review for host contracts, governance, and video safety/rights policies.
4. **Documentation:** Maintain a pack README, source/provenance index, architecture diagram, API contract changelog, runbook, threat model, evaluation catalog, workflow coverage ledger, workflow-role map, and current maturity matrix. Claims must distinguish cataloged, mapped, graph-validated, active, and production-proven states.
5. **Knowledge governance:** Periodically review lesson quality, stale content, retention, privacy classification, and source licenses. Revocation is an audited lifecycle action, not deletion of history.
6. **Provider governance:** Providers are optional adapters with explicit capability, cost, retention, residency, and safety declarations. Credentials remain outside source control; mock mode is mandatory in tests.
7. **Reuse bar:** A new MMA system may be added only by producing a schema-valid pack and evaluations. If onboarding requires a domain-specific host branch, first generalize the contract or reject the extension.

## 10. Risk register and mitigation

| Risk | Preventive control | Recovery plan |
|---|---|---|
| Local video semantics leak into generic host contracts | Canonical ownership rules, neutral host schemas, and review for host branches. | Revert the host change; restore the prior local pack artifact by digest. |
| Loss or misuse of upstream source semantics during adaptation | Reviewed source-to-pack and workflow-role maps, immutable provenance, evaluation coverage, and explicit gaps rather than forced matches. | Rebuild affected local pack assets from the pinned source and rerun mapping/graph checks. |
| Dual control planes diverge | One FastAPI public control plane; local video graphs compile into the host; no pack-local scheduler or governance bypass. | Disable the affected graph and restore the prior approved local definition. |
| Blueprint is mistaken for implemented capability | Require workflow/phase coverage, reviewed mappings, graph-reference integrity, deterministic offline validation, and maturity evidence; `pack_spine.json` is labelled as the sole safe stub. | Correct documentation/dashboard claims; retain explicit gaps and block maturity or activation. |
| Graph omits a required gate, handoff, or bounded path | Validate phase nodes, typed handoffs, lead/critic assignments, budgets, tools, quality/risk/human gates, critique/refinement bounds, and rollback. | Fail closed, mark the workflow incomplete, and revert the graph version. |
| “Learning” creates unsafe self-modification | ALC activation gate, assessed lessons, sandbox-only proposals, human promotion, provenance and rollback. | Revoke lessons/proposals, restore prior agent/pack version, investigate audit trail. |
| Cross-domain or cross-tenant knowledge disclosure | Mandatory identity namespace filters, least-privilege retrieval, redaction and security property tests. | Disable affected retrieval scope, revoke session access, preserve forensic evidence. |
| Provider cost, outage, unsafe output, or unintended activation | Capability allow-lists, finite budgets, local stubs/mocks, circuit breakers, human gates, and no-production-activation evidence. | Fail closed, enqueue recoverable work, pause; never substitute a live provider. |
| Contract incompatibility breaks packs | Semver compatibility negotiation, consumer contract tests, deprecation windows, immutable package versions. | Pin host to last compatible pack or pack to last compatible host; execute documented migration. |
| Performance collapses with many MMA systems | Isolation, bounded queues and budgets, load testing with 24+ synthetic packs, capacity SLOs, observability. | Throttle or disable low-priority packs and scale only after capacity evidence is reviewed. |

## 11. Implementation checklist and approval gates

Before any implementation migration, approve these decisions: the host/pack boundary; the pinned provenance revisions; the first workflow family; data classifications; required approvers; compatibility policy; target SLOs; the workflow-role-map review criteria; and no-production-activation evidence criteria. Then execute phases 0–7 in order.

No phase may claim completion without passing focused tests, an immutable evidence record, updated source/mapping/graph/maturity status, and review by the designated host and video-pack owners. A workflow cannot claim maturity merely because agents are cataloged: it also needs complete reviewed role mapping or explicit gaps, graph-reference integrity, deterministic offline graph validation, and gate evidence. No external provider, credential, network access, production migration, deletion, or activation may occur without explicit approval.

## 12. Definition of successful adoption

Adoption is successful when the common repository can register and operate multiple unrelated domain packs without domain-specific host code; `business/video/` is the checked-in self-contained source of truth for the pinned/adapted pack and its complete 114-agent source mapping; every active video agent has enforceable, auditable individual knowledge acquisition; and every documented video workflow family and required phase is backed by a reviewed local graph or explicit reviewed gap. Any graph counted as mature is traceable, governed, reproducible, reversible, mapping-complete, reference-integral, deterministically validated offline, and evidenced as non-production-active. Cataloging agents, retaining source prose, or keeping `pack_spine.json` alone is not completion.
