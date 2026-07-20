# NN UI 08: Global Settings & Configuration Spec

**UI ID:** nn_ui_08_settings  
**Version:** 1.0 (Aligned to common-agent-swarm-ops v2.1 complete inventory)  
**Related Main Doc Section:** Ui8  
**Date:** 2026-07-18  
**Owner:** Nicholas / Frontend Team  
**Status:** Ready for implementation

## Purpose & Goals
Provide a single, comprehensive control center for configuring the entire platform — LLM providers, secrets, integrations, policies, defaults, and workspace governance. This UI is essential for self-hosted production use and safe commons evolution.

## Layout & Structure
Tabbed or left-nav + content area (desktop). Mobile: Accordion or segmented views.

**Sections/Tabs:**
1. LLM Providers & Models
2. Credentials & Secrets Vault
3. Integrations
4. Policies & Guardrails
5. Defaults (Workflow/Swarm/Common)
6. UI & Preferences
7. Workspaces & Access Control

Each section uses forms with validation, test buttons, and impact warnings (e.g., "This change affects 14 running swarms").

## Key Components
- Provider cards with connection test + model list fetch.
- Secrets manager: Add/Edit form (never shows value after save), reveal on demand with audit log, scoped to business/global.
- Integration cards with health status (green/yellow/red) and configure modal.
- Policy toggles/sliders with "Affects X swarms" live preview.
- Workspace member table with role assignment and invite flow (Keycloak integration).
- shadcn Form + Dialog + Table + Badge (for health/status).

## Data & API
- GET/POST/PUT for providers, secrets (encrypted), integrations, policies, defaults, workspaces.
- Test endpoints for connections.
- Real-time health checks via WS or polling.
- Impact analysis queries (affected swarms/commons when changing policies or defaults).

## Interactions
- Test connection → success toast or error with details.
- Change policy with high impact → confirmation modal showing affected swarms + "Apply only to my swarms" option.
- Secrets: Add → value hidden forever after; "Rotate" action.
- Workspace: Invite flow opens Keycloak-like user picker or email invite.

## Polish & Accessibility
Dark theme, high contrast status, full keyboard nav, bilingual labels, ARIA for forms and status. Loading skeletons per section. Optimistic updates where safe.

## Wireframe Summary
Left nav (Providers | Secrets | Integrations | Policies | Defaults | UI | Workspaces). Main area shows active section form/cards with test/impact elements. Top header with search across settings.

**Implementation Notes:** Integrate deeply with Keycloak for auth/roles. Use secure patterns for secrets (never store plaintext in frontend). Impact analysis is key for safe commons governance.


## VA-Agent-Swarm Settings Alignment

Settings must configure only policy-approved defaults referenced by [`va_agent_structure_mapping.md`](va_agent_structure_mapping.md): model routing/quality-cost rules, tool scopes, runtime retry/concurrency/budget limits, artifact retention/rights policies, provenance requirements, and gate/notification defaults. Workspace settings cannot override an immutable agent version, a required approval, or tool authorization for a live run.
