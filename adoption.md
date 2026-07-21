# Adoption Plan: `common-agent-swarm-ops` × `va-agent-swarm`

**Status:** Proposed — implementation not started  
**Date:** 2026-07-20  
**Decision owner:** Product and architecture owners for both repositories  
**Scope:** A safe, reusable integration model for the generic MMA host and the video-agent domain system.

## 1. Executive decision

Adopt a **host-and-domain-pack** model. `common-agent-swarm-ops` becomes the domain-agnostic control plane for many multi-agent (MMA) systems. `va-agent-swarm` remains the canonical repository for every video-specific rule, prompt, rubric, workflow definition, knowledge source, provider selection, and media-policy decision. The common host may validate, register, execute, audit, and learn from a VA pack; it must not become the source of truth for video business logic.

This decision satisfies both non-negotiables:

| Requirement | Binding decision |
|---|---|
| VA-specific logic remains in `va-agent-swarm` | Video semantics, prompts, rubrics, workflow definitions, corpora, and adapter configuration are versioned and released from VA. Common retains only generic contracts, host code, and non-semantic test fixtures. |
| The common project supports dozens of MMA systems | Every domain is integrated through a versioned, declarative pack contract, isolated data namespaces, generic governance hooks, and a common Agent Learning Contract (ALC). No domain receives a custom control plane. |

The target is not a repository merge that copies VA content into common. It is a controlled integration: VA publishes a signed, schema-valid domain package; common registers a specific package version and runs it through shared governance and learning infrastructure.

## 2. Audit basis and confidence

This assessment is based on a local review performed on 2026-07-20 of the two repositories and the reference adoption plan in `generic-swarm-ops`. The reference is useful historical context; this plan prioritizes artifacts currently present in the two target repositories. No external providers, credentials, media APIs, or production environments were accessed.

| Repository | Confirmed state | Audit conclusion |
|---|---|---|
| `va-agent-swarm` | A detailed specification corpus: 114 agents across 10 categories, workflow and quality designs, source material, and planned integrations. Its root contains no application package, test suite, dependency manifest, or CI implementation. | Preserve it as the domain authority, but give it an executable, tested domain-pack layer. |
| `common-agent-swarm-ops` | FastAPI host modules for registry, workflow engines, memory, governance, evaluation, evidence, and a Next.js frontend. It has property, unit, integration, and video tests. | Reuse its host capabilities, but remove video assumptions from generic contracts and finish the learning lifecycle. |
| Existing `business/video` in common | 114 `registered` agent records and an inventory are present, but all sampled entries are L0 and the pack contains one stub graph (`pack_spine.json`). The declared 14-workflow/corpus structure in `structure.md` is not present on disk. | Treat it as an interim catalog, not evidence of a completed migration. Reconcile or retire it only after a traceable VA-owned replacement exists. |

## 3. Current architecture and technical-debt audit

### 3.1 `va-agent-swarm`

**Strengths**

- The system reference defines a coherent video-production hierarchy: orchestration, artifact handoffs, quality and continuity, delivery, and observability.
- The roster documents 114 specialized agents, including the orchestration spine (Orchestrator, Planner, Router, Judge), quality and compliance roles, and workflow-support agents.
- Agent descriptions already identify learning sources, quality criteria, critique relationships, tools, and intended architectural patterns.
- The build plan contains sound principles: contracts before code, vertical slice before breadth, one shared agent lifecycle, deterministic inputs, provider abstractions, and mocked external media providers in CI.

**Gaps and risks**

- The repository is design-rich but has no executable host, durable state model, provider abstractions, test harness, CI gate, or deployment path.
- Its proposed stack includes platform choices that overlap the common host. Building a second FastAPI, graph, event-bus, and governance plane would create duplicate identity, audit, retry, and approval semantics.
- Learning is a stated intention per agent, not an enforceable contract: there are no per-agent episode, reflection, retrieval, promotion, or retention records.
- Multiple document versions, language variants, scripts, diagrams, and starter plans create source-drift risk. A canonical source index is required before implementation.
- Provider names and safety assumptions are specifications, not audited integrations; they must remain behind host-controlled, mockable interfaces.

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
                               │ validates and registers immutable release
                               ▼
┌───────────────────────────────────────────────────────────────────────┐
│ va-agent-swarm — canonical Video Domain Pack                          │
│ agents · prompts · rubrics · workflows · knowledge · video policies   │
│ adapter configuration · video-specific evaluations and UI extensions  │
└───────────────────────────────────────────────────────────────────────┘
```

### 4.1 Ownership rules

| Asset | Owner and canonical location | Host responsibility |
|---|---|---|
| Video agent roles, prompts, rubrics, workflow graphs, critique policy | VA domain package | Schema validation and versioned registration only |
| Video knowledge corpus and provenance | VA domain package or VA-managed storage | Enforce access, retention, redaction, and audit policies |
| Video tools and provider choices | VA adapter configuration | Invoke only through a generic allow-listed provider protocol |
| Generic lifecycle, graph compiler, authorization, audit, checkpoints, evaluation engine | Common host | Implement and version |
| ALC, event, artifact, and manifest schemas | Common host | Define compatible versions; validate packs |
| Cross-domain fixtures | Common host | Must be synthetic and contain no VA business semantic content |

**Boundary controls**

1. Common must not import VA source documents, prompts, rubrics, media strategies, or knowledge corpora into its canonical business tree.
2. VA packs must be declarative data and approved adapters; arbitrary package code cannot execute inside the host registration path.
3. Every invocation carries `organization_id`, `domain_id`, `pack_version`, `agent_id`, `workflow_id`, `run_id`, and a correlation ID.
4. Cross-domain data access, undeclared tool IDs, and undeclared outbound destinations fail closed and create audit evidence.
5. A pack upgrade is copy-on-write: prior runs remain reproducible against the exact approved pack and contract versions.

### 4.2 Standardized domain-pack contract

Implement an SDK-independent, JSON-schema-first package format in VA. The host should support any domain identifier; `video` is a value, never a hard-coded branch.

```text
va-agent-swarm/
  domain-pack/
    manifest.json
    agents/<agent_id>/agent.json
    prompts/<id>.md
    rubrics/<id>.json
    workflows/<id>.dna.json
    policies/
    knowledge/index.json
    tools/adapters.json
    evals/{golden,adversarial,regression}/
    ui/extension-manifest.json
    provenance/sources.json
    release.json
```

The pack manifest must contain: immutable `domain_id`, semantic `pack_version`, supported host-contract range, content digest, signer identity, declared agents and workflows, capability-scoped tool IDs, required ALC version, data classifications, evaluation suite references, and optional UI extension metadata. The host stores the manifest digest and signature result with the registration record.

### 4.3 Generic APIs and schemas

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
| `ArtifactHandoff` | Generic immutable artifact lineage, ownership, classification, integrity, approval and provenance references. VA adds video metadata through a pack extension schema. |

## 5. Mandatory autonomous learning design

The ALC is the mechanism that turns learning from an aspiration into an enforceable lifecycle. It is required for every agent whose `requires_learning` flag is true; the VA package must set it for every video agent.

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
| 0. Governance and source baseline | Freeze a named VA source revision; build a canonical source index with hashes, owner, license/consent classification, and mapping to pack assets. Record ADRs for ownership, the host/pack boundary, contract versions, and provider policy. | Every VA asset has a disposition: retained in VA, generated metadata, deferred, or rejected. Rollback is deletion of only newly generated indexes; VA sources remain untouched. |
| 1. Generic contract hardening | Add neutral manifest, agent, ALC, learning, artifact, and provider schemas; remove video prefixes from generic schemas; version registration responses; implement signature/digest validation and compatibility negotiation. | A synthetic non-video pack and an empty VA skeleton both validate without host code changes. No VA content is copied to common. |
| 2. Learning enforcement | Add lifecycle interceptors for retrieval, episode capture, reflection assessment, retention, metrics, and sandbox proposals. Persist contracts and learning records with tenant/domain/agent boundaries. Make the activation invariant authoritative. | Negative tests prove bypass attempts fail; positive tests prove individual growth and retrieval are observable. Legacy behavior remains available behind a migration feature flag. |
| 3. VA package construction | Create VA’s declarative `domain-pack/` from the canonical source index. Build a one-to-one roster map for all 114 agents; attach prompts, rubrics, critique edges, policies, tool declarations, and ALC configurations. Preserve all original study assets and provenance. | Package validation confirms 114 mapped agents with no orphan source entries. Pack remains `registered`; no live media provider is enabled. |
| 4. Vertical video spine | Implement a deterministic brief-to-artifact path using the VA orchestration, research, creative, media-stub, compliance, and delivery roles. Use mock providers, immutable artifact handoffs, critique gates, and human approval. | Repeated runs are reproducible; compliance/rights blockers halt execution; each participating agent has ALC evidence. Rollback selects the prior pack version and disables the new workflow. |
| 5. Controlled breadth | Migrate remaining VA workflow families in priority order: planning, generation, editorial, sound, quality, localization, distribution, analytics, and support. Keep every agent registered even when not yet active. Promote a workflow only after its domain evaluation pack passes. | Full roster is retained; every agent is at least cataloged and mapped, while each production workflow has an approved maturity level and explicit known limitations. |
| 6. Multi-domain proof | Onboard at least two synthetic or independently owned non-video packs through the same schema, registry, learning, and UI extension paths. Eliminate host branches that special-case video except generic extension loading. | Domain isolation, registration, activation, observability, and lifecycle operations pass with at least 24 concurrently registered packs in the load environment. |
| 7. Cutover and maintenance | Publish supported platform/pack compatibility matrices, migration guides, runbooks, dashboards, deprecation schedules, and incident response procedures. Make VA package releases the only source for video behavior. | Production approval is based on evidence, not catalog completion. Rollback remains an immutable pack-version reversion plus data-safe lesson revocation. |

## 7. VA architectural redesign

VA should be rebuilt as a domain package on the shared host—not as a second orchestration platform. This retains its unique business design while replacing its weak executable core with the host’s tested lifecycle.

- **Orchestration:** encode VA’s supervisor, planner, router, judge, pipeline, fan-out/fan-in, critique, and human-gate patterns as portable workflow graphs. The host graph compiler owns execution and checkpointing.
- **Agent factory:** every VA agent is a declarative instance of the generic lifecycle. Its differences are domain-owned configuration—prompt, rubric, tools, knowledge scopes, critique edges, budgets, and evaluators—not bespoke loops.
- **Artifacts:** use the generic immutable handoff contract with VA extension fields for rights/consent, continuity, media quality, channel requirements, and provenance. Video release stays blocked until all required gates pass.
- **Tools:** represent media, voice, editing, research, and publishing providers through generic capability protocols. VA selects approved providers by configuration; host adapters enforce authorization, budget, retries, audit, and mock mode.
- **UI:** retain VA screens and terminology in VA’s extension manifest. The common frontend supplies only authenticated shell, generic projections, accessibility, audit visibility, and extension slots.
- **Knowledge:** retain VA source materials and curated domain knowledge in VA. The host indexes only approved, classified references and never gives one domain access to another domain’s knowledge.

## 8. Testing and verification strategy

### 8.1 Required automated layers

| Layer | Scope | Required evidence |
|---|---|---|
| Schema and unit tests | Neutral contracts, digest/signature checks, lifecycle states, ALC validation, retention, lesson scoring, provider allow-lists, artifact lineage. | Deterministic tests plus property-based tests for contracts and state transitions. |
| Property tests | Randomized domains, agents, scopes, event sequences, pack versions, failure/retry paths, and malicious identifiers. | Invariants for isolation, activation atomicity, lineage acyclicity, no cross-domain retrieval, and no unapproved promotion. |
| Integration tests | VA pack registration, host graph compilation, retrieval→episode→reflection path, critique blockers, approval gates, and immutable release checks. | Mock-only provider tests; no credentials or network use. |
| End-to-end tests | The vertical VA spine from a fixed brief through a released-*readiness* decision, with UI projections and audit records. | Fixed seeds, fixture digests, screenshots where applicable, and a trace bundle. |
| Compatibility tests | Current and previous supported host/VA pack contract versions. | Consumer-driven contract suite in both repositories. |
| Security tests | Tenant/domain isolation, tool namespace denial, schema/path traversal rejection, secret redaction, malicious pack rejection, and lesson poisoning attempts. | Fail-closed assertions and audit-event checks. |
| Performance and load tests | Registration, retrieval, graph execution, and event fan-out with synthetic packs and stub tools. | Capacity report for at least 24 concurrently registered domains; SLOs must be approved before production. |
| Resilience tests | Provider timeout, duplicate delivery, partial persistence, restart, replay, approval loss, and rollback. | Idempotency, recovery, and immutable-version evidence. |

### 8.2 Test gates

Run focused backend tests first (`python -m pytest -q` with appropriate selectors), followed by type checking and linting. Run existing repository gates—`npm run sdd:check`, `npm run sync:check`, and `npm test -- --silent`—for changes that touch the common project’s automation. CI must keep provider integrations disabled by default and use approved mock adapters only.

Do not declare a workflow production-ready from unit-test success alone. Promotion requires its declared domain evaluations, human approval where policy requires it, a reproducible trace, and no unresolved security or data-governance finding.

## 9. Long-term maintenance and reuse rules

1. **Versioning:** Use semantic versions independently for host API, pack format, ALC format, and each domain pack. A host publishes a supported pack/ALC compatibility range; a pack declares the range it requires.
2. **Change control:** Contract-breaking changes require an ADR, migration plan, consumer tests, a deprecation window, and an explicit rollback plan. Domain behavior changes stay in the domain repository.
3. **Contribution workflow:** Use short-lived branches, conventional commits, scoped reviews, deterministic tests, and a code-owner review for host contracts, governance, and VA safety/rights policies.
4. **Documentation:** Maintain a pack README, source/provenance index, architecture diagram, API contract changelog, runbook, threat model, evaluation catalog, and a current maturity matrix. Documentation claims must distinguish cataloged, registered, active, and production-proven agents.
5. **Knowledge governance:** Periodically review lesson quality, stale content, retention, privacy classification, and source licenses. Revocation is an audited lifecycle action, not deletion of history.
6. **Provider governance:** Providers are optional adapters with explicit capability, cost, retention, residency, and safety declarations. Credentials remain outside source control; mock mode is mandatory in tests.
7. **Reuse bar:** A new MMA system may be added only by producing a schema-valid pack and evaluations. If onboarding requires a domain-specific host branch, first generalize the contract or reject the extension.

## 10. Risk register and mitigation

| Risk | Preventive control | Recovery plan |
|---|---|---|
| VA logic leaks into common and makes it non-reusable | Canonical ownership rules, source index, CI checks for disallowed VA paths/content, neutral host schemas. | Revert the host change; restore VA-owned package artifact by digest. |
| Loss of VA source semantics during conversion | One-to-one source-to-pack map, review by domain owners, immutable original source revision, evaluation coverage. | Rebuild affected pack assets from the frozen VA source and rerun mapping checks. |
| Dual control planes diverge | One FastAPI public control plane; VA graphs compile into the host; no VA-local scheduler or governance bypass. | Disable new workflow and route to the prior approved host definition. |
| “Learning” creates unsafe self-modification | ALC activation gate, assessed lessons, sandbox-only proposals, human promotion, provenance and rollback. | Revoke lessons/proposals, restore prior agent/pack version, investigate audit trail. |
| Cross-domain or cross-tenant knowledge disclosure | Mandatory identity namespace filters, least-privilege retrieval, redaction and security property tests. | Disable affected retrieval scope, revoke session access, preserve forensic evidence. |
| Provider cost, outage, or unsafe output | Capability allow-lists, budgets, mock providers, circuit breakers, human gates, content/release controls. | Fail closed, enqueue recoverable work, use approved fallback or pause. |
| Catalog is mistaken for live capability | Maturity matrix and evidence gates separate L0 catalog, L1 registered, L2 active, and production-proven status. | Correct release notes/dashboard; block promotion until the stated evidence exists. |
| Contract incompatibility breaks packs | Semver compatibility negotiation, consumer contract tests, deprecation windows, immutable package versions. | Pin host to last compatible pack or pack to last compatible host; execute documented migration. |
| Performance collapses with many MMA systems | Isolation, bounded queues and budgets, load testing with 24+ synthetic packs, capacity SLOs, observability. | Throttle or disable low-priority packs and scale only after capacity evidence is reviewed. |

## 11. Implementation checklist and approval gates

Before any code migration, approve these decisions: the host/pack boundary, which VA revision is canonical, the first vertical workflow, data classifications, required approvers, compatibility policy, and target SLOs. Then execute phases 0–7 in order.

No phase may claim completion without: passing focused tests, an evidence record, updated source mapping/maturity status, and review by both host and VA owners. No external provider, credential, production migration, deletion, or activation should occur without explicit approval.

## 12. Definition of successful adoption

Adoption is successful when the common repository can register and operate multiple unrelated domain packs without domain-specific host code; VA retains the canonical video domain package and its full 114-agent source mapping; every active VA agent has enforceable, auditable individual knowledge acquisition; and every production workflow is traceable, governed, reproducible, and reversible. Cataloging agents alone is not completion.
