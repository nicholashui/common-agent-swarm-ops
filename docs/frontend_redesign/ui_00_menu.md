# NN UI 00: Application Menu Spec

**UI ID:** `nn_ui_00_menu`  
**Version:** 1.0 (Backend v1.2 / frontend-redesign aligned)  
**Related Main Doc Section:** Global shell; Ui2–Ui20  
**Status:** Ready for design and implementation

## Purpose
The left-hand application menu is the persistent, authenticated navigation shell for common-agent-swarm-ops. It exposes every supported frontend capability as an authorized route or action, organizes common-first swarm operations by user intent, and keeps the current workspace, projection freshness, and recovery state visible without exposing backend internals.

The browser renders only server-authorized, generated `/api/v1` navigation, action, and evidence references. A menu item is hidden when its route or action reference is absent; disabled when its projection is stale or the server reports it ineligible; and never used to infer tenant, role, resource existence, or backend capability.

## Layout and visual treatment
- **Desktop:** Fixed 264px left rail below the product header; independently scrollable navigation; compact 72px icon rail is available on user toggle.
- **Tablet/mobile:** Collapsed drawer opened from the global header. It traps focus while open, closes with Escape, restores focus to its trigger, and uses at least 44×44px action targets.
- **Light frame:** Use the shared style guide tokens: white base, `#fafaf9` surfaces, `#f5f5f4` elevated groups, `#e7e5e4` borders, `#1c1917` primary text, `#78716c` secondary text, and indigo `#4f46e5` common-resource accents.
- **Item anatomy:** Lucide icon, visible label, optional returned count/badge, current-route indicator, and accessible name matching the visible label. Color never conveys selection, lifecycle, freshness, or authorization on its own.
- **Header:** Product mark; returned workspace name; environment/demo indicator when returned; workspace switcher only when an authorized action exists.
- **Footer:** Current projection freshness, reconnecting/stale status, copyable correlation identifier when returned, profile trigger, and collapse control.

## Information architecture

| Group | Menu item | Route or capability | Visibility and behavior |
| --- | --- | --- | --- |
| **Home** | Dashboard | Fleet summary, common health, backlog, alerts, impact | Default authenticated destination; shows only returned redacted summaries and freshness. |
| **Build** | Compose | Pattern-guided swarm composition | Opens authorized composition projection; suggestions are inert data. |
|  | Swarm Canvas | Graph revisions, nodes, validation, run controls | Shows pinned versions and graph categories; actions use returned action references and idempotent intents. |
|  | Blueprints | Saved common patterns and governed templates | Visible only with an authorized blueprint projection or action. |
| **Common** | Registry Hub | Common Agent and Pattern discovery | Generated search/filter fields only; surfaces version, provenance, compatibility, and redacted metrics. |
|  | Agent & Pattern Detail | Version history, usage, evaluation, improvement proposals | Contextual child route entered from a selected registry/canvas item; never shown as an unscoped global resource. |
| **Operate** | Activity | Runs, task lifecycle, correlation timeline, recovery | Applies sequence-valid SSE observations to REST-backed projections only. |
|  | Monitoring | Health, alerts, metrics, redacted trace/evidence references | Does not expose liveness/readiness, host, queue, provider, or raw trace data. |
|  | Approvals & Rollouts | Gates, evidence, canary, A/B, promotion, rollback | Irreversible controls remain disabled for stale projections or pending commands. |
|  | Notifications | Returned alerts and actionable updates | Deep links resolve through authorized opaque references. |
|  | Costs | Returned usage, budgets, optimization and report projections | No client-created budget authority or unredacted billing data. |
| **Knowledge & Quality** | Knowledge | Collections, artifacts, imports, contributions | Imports are submitted as untrusted data; no browser fetch, embed, or execution of external URLs. |
|  | Eval & Improvement | Evaluation evidence, proposals, campaigns, comparison | Displays independent returned evidence categories; commands are server governed. |
| **Domain** | VA Production | VA templates, phases, tasks, artifacts, quality, approvals | Appears only when a returned VA projection is available; generic views omit VA-only fields. |
| **Governance** | Audit | Redacted immutable audit records and evidence references | Generated filters only; exports appear only when authorized. |
|  | Collaboration | Returned sharing, comments, workspace, and proposal-review projections | No peer authority or direct collaborative execution channel. |
| **Developer & Help** | API Portal | Generated OpenAPI reference and supported integration guidance | Interactive calls use generated contracts and current session context only. |
|  | Onboarding & Help | Tours, documentation, guided projects, feedback | Help links are static or server-authorized destinations. |
| **Account** | Settings | Returned preferences, policy summaries, defaults | Configuration controls render only from current authorized action references. |
|  | Profile | Session-safe personal preferences and contribution views | Never displays or manages tokens, credentials, or automation secrets. |

## Menu behavior and states
1. The menu loads its route catalog from the authenticated shell and merges static presentation labels with returned authorization, eligibility, and badge data.
2. Selecting a route loads its REST snapshot before that screen applies SSE updates. The active item is determined from the resolved route, not a client-inferred resource state.
3. A returned stale, reconnecting, delayed, degraded, unavailable, or recovery-required state is shown with text, named icon, and status badge. `Stale` disables freshness-critical child actions but does not hide safe read navigation.
4. Pending state-changing navigation (for example, instantiate, rollout, approval, or import) retains its idempotency identity and shows a command-reconciliation indicator; a second click cannot create a new command.
5. On SSE gap, replay expiry/denial, schema mismatch, or authorization change, the affected screen resynchronizes from REST before its item may show live incremental status again.
6. Collapsed mode retains named tooltips; keyboard users can traverse groups in source order; group buttons expose `aria-expanded`; and the active item uses `aria-current="page"`.

## Role, authorization, and safety rules
- Route presence, group counts, badges, child links, action labels, and eligibility come exclusively from generated authorized projections.
- Absence of an item is not rendered as an error or a hint that a protected resource exists.
- The menu stores only session-safe route preference, selected collapsed state, and authorized event cursors. It stores no access tokens, raw prompts, artifact content, tool data, or credentials.
- External destinations require a server-provided allowed-action contract. Opaque references are reauthorized when opened.
- Menu search, command palette, and quick actions submit only generated input fields and displayed returned action references.

## Responsive wireframe

```text
┌──────────────────────────────────┐
│ ◉ common-agent-swarm-ops      ‹  │
│ Workspace: Returned workspace  ▾ │
├──────────────────────────────────┤
│ HOME                             │
│ ▣ Dashboard                      │
│ BUILD                            │
│ ◇ Compose   ◫ Swarm Canvas       │
│ ▤ Blueprints                     │
│ COMMON                           │
│ ◉ Registry Hub                   │
│ OPERATE                          │
│ ◷ Activity   ◌ Monitoring         │
│ ✓ Approvals & Rollouts           │
│ ◉ Notifications   ◫ Costs         │
│ KNOWLEDGE & QUALITY               │
│ ◫ Knowledge   ✦ Eval & Improve   │
│ GOVERNANCE / DEVELOPER / ACCOUNT │
│ Audit · Collaboration · API · Help│
│ Settings · Profile               │
├──────────────────────────────────┤
│ Status: Reconnecting · as_of …   │
│ Profile                       ⚙  │
└──────────────────────────────────┘
```

## Verification checklist
- Cover every table item with an authorized, unauthorized, unavailable, stale, and mobile-drawer fixture.
- Verify hidden items expose no protected route or badge metadata; disabled items cannot invoke freshness-critical actions.
- Verify keyboard navigation, focus trap/return, visible focus, accessible names, `aria-current`, group expansion, and mobile target size.
- Verify SSE gaps force REST resynchronization before live menu/screen status resumes, and that command retries reuse one idempotency identity.
- Verify no rendered menu state contains credentials, raw protected content, provider internals, raw traces, or browser-fetched untrusted imports.

**Cross-reference:** `frontend_redesign.md`, `common-style.html`, and the individual Ui1–Ui20 specifications define each destination’s detailed view behavior.
