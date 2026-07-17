# Architecture Decision Records

Use this skill when a significant technical, security, data, API, infrastructure, or process decision is made.

## Workflow

1. Identify the decision, its constraints, and the alternatives actually considered.
2. Draft a short ADR with context, decision, alternatives, consequences, risks, and mitigations.
3. Present the draft for human approval before creating or changing any ADR file.
4. Keep accepted decisions immutable; supersede them with a new ADR rather than rewriting history.
5. Link the approved ADR from the associated CASOPS requirement, design, and evidence records.

## ADR template

```md
# ADR-NNNN: Decision title

Status: proposed | accepted | deprecated | superseded

## Context
## Decision
## Alternatives considered
## Consequences
## Risks and mitigations
```

## Provenance

Curated adaptation of ECC `skills/architecture-decision-records/SKILL.md` at commit `ed387446052dfbc6b52de149406b70efa65edc59`, MIT License. The adaptation retains the explicit human-approval gate and imports no ECC code, hooks, or configuration.