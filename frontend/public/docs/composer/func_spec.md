# Swarm Composer — functional specification

**Route:** `/composer` · **Auth:** required · **Component:** `ComposerHome`

## Purpose
Draft swarm goals, select common patterns, submit compose intents only when host-authorized.

## Functional requirements

### FR-CMP-001 Auth
- Authenticated shell required; anonymous → `/login`.

### FR-CMP-002 Goal capture
- SHALL provide editable swarm name and goal text inputs.
- SHALL NOT store credentials in goal text fields by design (operator responsibility + no secret fields).

### FR-CMP-003 Pattern browser
- SHALL list projected common patterns.
- Selecting a pattern SHALL update selected state (`aria-pressed`).

### FR-CMP-004 Send / compose
- Primary send SHALL use interaction runtime when compose/instantiate action available.
- Without action ref, SHALL fail closed with honest message.

### FR-CMP-005 Save draft
- Save draft SHALL be session-local unless host persistence contracted.

### FR-CMP-006 Legacy Composer
- Legacy `Composer` export path SHALL obey same non-authority rules for tests/integration.

### FR-CMP-007 Help docs
- `/docs/composer/userguide.md`, `func_spec.md`, `test_scenario.md`.

## Out of scope
- Silent production activation.
- Inventing graph topology without host.
