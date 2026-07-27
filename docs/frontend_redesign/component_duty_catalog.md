# Frontend component duty catalog & control coverage

**Version:** 1.0  
**Date:** 2026-07-27  
**Scope:** `frontend/src/components/**` vs `docs/frontend_redesign/**`  
**Authority:** Browser is non-authority. Controls only submit server-authorized intents, render redacted projections, or apply local session UX.  
**Sources:** Component implementations, `frontend_redesign.md` Req 8.x, `ui_00`–`ui_20` screens, specials/pack patterns, host `/api/v1` interaction runtime.

---

## 1. Executive answer: are all buttons / inputs covered?

| Layer | Covered by redesign docs? | Notes |
|-------|---------------------------|--------|
| **Primary screen Homes** (`*Home`, Login, shells tied to `ui_00`–`ui_20`) | **Yes (screen-level)** | Each major route has a screen brief (layout, sections, primary actions) |
| **Named React component duties** for infra/primitives | **Was No → this catalog** | Shared binders, projection controls, consoles, specials |
| **Every button/input ID enumerated in redesign** | **No** | Redesign specifies *intents and rules*, not every DOM control. Implementation may add local UX controls if they obey contracts |
| **Controls that invent host authority** | **Forbidden** | No client-side approve-without-action-ref, no credential fields, no untrusted URL fetch |

### Control coverage rules (normative)

1. **Screen docs** define *what the user can do* (primary/secondary actions, filters, forms).  
2. **This catalog** defines *which component owns* each control class when not a screen.  
3. A control is **in scope** if it: loads projection, submits idempotent command, navigates in-app, filters local view, copies correlation/reference, or announces status.  
4. A control is **out of scope / prohibited** if it: stores secrets, enables production activation, fetches untrusted URLs, or bypasses eligibility.

---

## 2. Screen Homes — control coverage vs redesign

| Screen component | Redesign doc | Buttons / inputs duty covered? | Gap |
|------------------|--------------|--------------------------------|-----|
| `LoginScreen` | `ui_01_login.md` | **Yes** — credentials form, submit, errors | — |
| `DashboardHome` / `Dashboard` | `ui_02_dashboard.md` | **Yes** — health, fleet actions, pause/refresh intents | Local session pause is session-only |
| `ComposerHome` / `Composer` | `ui_03_swarm_composer.md` | **Yes** — compose, pin, draft actions | Governed stubs fail-closed |
| `CanvasHome` / `Canvas` | `ui_04_canvas.md` | **Yes** — run, node inspect, layout | Run requires host topology/run APIs |
| `AgentDetailHome` / `AgentDetail` | `ui_05_agent_detail.md` | **Yes** — tabs, propose, open registry | Mutations need action refs |
| `ActivityHome` / `Activity` | `ui_06_activity.md` | **Yes** — filters, timelines | — |
| `RegistryHome` / `Registry` | `ui_07_registry_hub.md` | **Yes** — search, facets, cards, proposals | Demo proposals removed; specials embedded |
| `SettingsHome` | `ui_08_settings.md` | **Yes** — prefs (local or authorized) | — |
| `MonitoringHome` | `ui_09_monitoring.md` | **Yes** — inspect run, freshness | — |
| `KnowledgeHome` | `ui_10_knowledge.md` | **Yes** — search; ingestion via subcomponents | Full ingest when API available |
| `EvalHome` | `ui_11_eval.md` | **Yes** — run campaign intent | — |
| `NotificationsHome` | `ui_12_notifications.md` | **Yes** — mark read (session) | — |
| `ProfileHome` | `ui_13_profile.md` | **Yes** — profile fields display/edit intents | — |
| `AuditHome` | `ui_14_audit.md` | **Yes** — search/filter audit projections | — |
| `ApiPortalHome` | `ui_15_api_portal.md` | **Yes** — portal links, try-it when authorized | — |
| `OnboardingHome` | `ui_16_onboarding.md` | **Yes** — steps, continue | — |
| `MobileHome` | `ui_17_mobile.md` | **Yes** — compact ops labels/actions | — |
| `CollaborationHome` | `ui_18_collaboration.md` | **Yes** — collab list/actions | — |
| `CostsHome` | `ui_19_costs.md` | **Yes** — cost projection filters | — |
| `BlueprintsHome` | `ui_20_blueprints.md` | **Yes** — gallery, instantiate intents | pack_spine not blueprint realization |
| Shell (`AppShell`, `AuthenticatedShell`, `ShellNavigation`) | `ui_00_menu.md` | **Yes** — nav items, workspace chrome | — |

---

## 3. Duty definitions — components previously without clear duty

Each section is the **design duty** for that component. Implementation must stay fail-closed.

### 3.1 Screen binder & shell helpers

#### `BoundScreenHome` — **Duty: screen binder**

| Field | Definition |
|-------|------------|
| **Path** | `components/screen/BoundScreenHome.tsx` |
| **Duty** | Map a serializable screen key to the correct Home, inject stored projections (`useScreenParameters`), and wire `onAction` via interaction runtime. Server pages must not pass component types as props. |
| **Controls** | None of its own; hosts Home + `InteractionStatusBar` + optional `OperationsConsole`. |
| **Inputs** | `screen: BoundScreenKey` (and agent detail route via dedicated binder). |
| **Outputs** | Rendered Home with live action bridge. |
| **Must** | Always pass real `onAction`; never leave primary actions as permanent dead stubs. |
| **Must not** | Invent action references; enable network from browser secrets. |
| **Redesign links** | `frontend_redesign.md` Req 8.1–8.3; all `ui_XX` screens as bound targets. |

#### `ScreenBoundary` — **Duty: fail-soft error boundary**

| Field | Definition |
|-------|------------|
| **Duty** | Catch render failures in a screen tree; show safe recovery UI without leaking stack internals or privileged data. |
| **Controls** | Optional “Retry” / “Back to dashboard” when authorized navigation only. |
| **Must not** | Display raw exception objects, tokens, or provider payloads. |

#### `ResponsiveLayout` (`ResponsiveStack`, `ResponsiveSplit`, `ResponsiveActionGroup`) — **Duty: layout primitives**

| Field | Definition |
|-------|------------|
| **Duty** | Provide responsive structure for screen sections and action groups without defining business authority. |
| **Controls** | None; layout wrappers only. |
| **Redesign links** | Responsive/a11y notes in `frontend_redesign.md` and `ui_17_mobile.md`. |

#### `UnavailableScreen` — **Duty: authorized unavailable state**

| Field | Definition |
|-------|------------|
| **Duty** | Render server- or session-safe “unavailable” projection: message + recovery controls only from projection. |
| **Controls** | Recovery buttons only if projection supplies them. |
| **Must not** | Fabricate health from probe endpoints for tenancy/infra disclosure. |

#### `DemoModeBanner` — **Duty: non-authority banner**

| Field | Definition |
|-------|------------|
| **Duty** | Announce local/demo/non-live projection mode so users do not treat fixtures as production authority. |
| **Controls** | Optional dismiss (session-only). |
| **Must not** | Claim production activation or live media success. |

#### `AuthenticatedShell` / `AppShell` (already yes via menu) — restated duty

| Field | Definition |
|-------|------------|
| **Duty** | Host chrome: navigation, workspace label, outlet for bound screens. |

---

### 3.2 Interaction & accessibility primitives

#### `InteractionStatusBar` — **Duty: action feedback live region**

| Field | Definition |
|-------|------------|
| **Duty** | Display `InteractionStatus` (idle/busy/success/error/info) with optional correlation id; announce via `aria-live`. |
| **Controls** | None (display-only). |
| **Inputs** | `status: InteractionStatus`. |
| **Redesign links** | Req 8.2 recovery-aware commands; a11y live regions. |

#### `OperationalAnnouncer` — **Duty: operational status transitions**

| Field | Definition |
|-------|------------|
| **Duty** | Convert operational status transitions into polite announcements without duplicating sensitive payloads. |
| **Controls** | None (or visually hidden live region only). |

#### `AccessibleDialog` — **Duty: accessible modal host**

| Field | Definition |
|-------|------------|
| **Duty** | Focus trap, restore focus, labelled dialog chrome for proposal review, approvals, confirmations. |
| **Controls** | Close/cancel always; primary action only if parent supplies authorized handler. |
| **Redesign links** | Proposal modal in `ui_07_registry_hub.md`; approval dialogs in redesign ops sections. |

#### `IconControl` — **Duty: labelled icon button**

| Field | Definition |
|-------|------------|
| **Duty** | Icon-only button with required accessible name from `ICON_CONTROL_LABELS` / props. |
| **Controls** | One `button`. |
| **Must not** | Icon without text alternative. |

#### `GeneratedFilterBar` — **Duty: projection-driven filters**

| Field | Definition |
|-------|------------|
| **Duty** | Render filter/select controls from generated projection options; filter is presentation-only until server query contract exists. |
| **Controls** | `select` / chips from projection schema. |
| **Must not** | Invent filter dimensions not in projection/OpenAPI. |

#### `LocalDestinationPreview` — **Duty: safe local navigation preview**

| Field | Definition |
|-------|------------|
| **Duty** | Preview in-app destinations; never open untrusted external destinations without allowed-action contract. |

#### Design system modules (`design.tsx`, `DesignSystemPrimitives`) — **Duty: visual primitives**

| Field | Definition |
|-------|------------|
| **Duty** | Status badges, version pills, page headers, metric cards, empty states — pure presentation. |
| **Controls** | None required; optional links are navigation-only. |
| **Redesign links** | `common-style.html`, visual system language in redesign. |

---

### 3.3 Projection & safe content controls

#### `ActionControl` — **Duty: eligible action button**

| Field | Definition |
|-------|------------|
| **Duty** | Render one server-mapped action reference; disable when ineligible, pending, owner-disabled, or stale+freshness-critical/irreversible. |
| **Controls** | One `button` with `data-action-reference-id`. |
| **Inputs** | `ActionReferenceView`, `stale`, `pending`, `onInvoke`. |
| **Must not** | Invoke without eligibility; invent action IDs. |
| **Redesign links** | Req 8.2; Property 2 governed action visibility. |

#### `CopyCorrelationIdentifierButton` — **Duty: support copy**

| Field | Definition |
|-------|------------|
| **Duty** | Copy correlation ID for support; does not grant resource access. |
| **Controls** | Button or copy control. |
| **Redesign links** | Req 8.6. |

#### `EvidenceLink` — **Duty: opaque evidence navigation**

| Field | Definition |
|-------|------------|
| **Duty** | Link/button to server-issued evidence reference; reauth on open is host responsibility. |
| **Controls** | One button/link. |
| **Must not** | Embed raw traces or credentials. |

#### `ReferenceLink` — **Duty: opaque resource reference**

| Field | Definition |
|-------|------------|
| **Duty** | Present opaque resource IDs/links from projections only. |

#### `SafeContent` / `ExternalNavigationControl` — **Duty: inert content + gated external nav**

| Field | Definition |
|-------|------------|
| **Duty** | Render untrusted text as data; external navigation only via allowed-action contract. |
| **Controls** | Optional external nav button when contract present. |
| **Must not** | `dangerouslySetInnerHTML` of untrusted HTML; auto-navigate to import URLs. |
| **Redesign links** | Req 8.5–8.6; safe rendering. |

#### `ProjectionStatus` — **Duty: freshness / recovery strip**

| Field | Definition |
|-------|------------|
| **Duty** | Show live/delayed/reconnecting/stale/degraded/unavailable and recovery actions when projection allows. |
| **Controls** | Refresh/reconnect only if `isProjectionRecoveryAction` and eligible. |
| **Redesign links** | Req 8.3–8.4. |

#### `IngestionForms` (`IngestionForm`, summaries, mappers) — **Duty: safe artifact/knowledge ingress UI**

| Field | Definition |
|-------|------------|
| **Duty** | Collect content/import *reference* for authorized ingestion operation; client checks are non-authoritative; submit only through generated contract when available. |
| **Controls** | Textarea/content, optional URL field, submit button; disabled when no authorized ingestion operation. |
| **States** | validating, quarantined, processing, indexed, rejected, archived (display-only from projection). |
| **Must not** | Browser-fetch untrusted import URLs; treat client validation as security. |
| **Redesign links** | Req 8.5; `ui_10_knowledge.md`. |

---

### 3.4 Operational / approval / knowledge composites

#### `OperationsConsole` — **Duty: live control-plane operator panel**

| Field | Definition |
|-------|------------|
| **Duty** | Host-facing panel for inspect run, load approval, submit decision, refresh context via real `/api/v1` (through interaction runtime). |
| **Controls** | | Control | Type | Intent |
| | |---|---|---|
| | | Refresh context | button | `runtime.refreshContext` |
| | | Run id | input | local form state |
| | | Inspect run | submit | `runtime.inspectRun` |
| | | Approval id | input | local form state |
| | | Decision | select | approved/denied |
| | | Reason | textarea | decision reason |
| | | Load approval / Decide | submit | `loadApproval` / `decideApproval` |
| **Must** | Idempotent decision keys via runtime; show busy/error via `InteractionStatusBar`. |
| **Must not** | Store API keys; approve without host gate. |
| **Redesign links** | Ops UX; Req 8.2–8.4; monitoring/activity. |

#### `OperatorConsole` — **Duty: presentational operator inspection forms**

| Field | Definition |
|-------|------------|
| **Duty** | Controlled form presentation for run/approval inspection (used by OperationsConsole or tests). Same control classes as above; no direct network without injected handlers. |

#### `ApprovalRolloutScreens` (`ApprovalGateScreen`, `RolloutCampaignScreen`, …) — **Duty: approval & rollout projections**

| Field | Definition |
|-------|------------|
| **Duty** | Render approval gate / rollout campaign projections; irreversible controls disabled when stale or pending. |
| **Controls** | Approve/deny only when action refs + evidence revision present. |
| **Redesign links** | Approvals/rollouts in `frontend_redesign.md`; canvas/activity recovery. |

#### `KnowledgeArtifactScreens` — **Duty: knowledge & artifact projection host**

| Field | Definition |
|-------|------------|
| **Duty** | Compose knowledge/artifact projections, VA-conditional renderers, and safe content; attach ingestion forms when contract exists. |
| **Controls** | Delegated to `IngestionForms` + projection actions. |
| **Redesign links** | Req 8.5; `ui_10_knowledge.md`. |

#### `OperationalScreens` — **Duty: legacy named screen exports**

| Field | Definition |
|-------|------------|
| **Duty** | Compatibility exports mapping names (`Dashboard`, `Registry`, …) to projection-driven presentational screens for tests/older imports. Prefer `*Home` + `BoundScreenHome` for routes. |
| **Controls** | None inherent; delegates. |

---

### 3.5 Pack / specials

#### `SpecialsCatalog` — **Duty: specials pack catalog panel**

| Field | Definition |
|-------|------------|
| **Duty** | List draft/non-active specials agents from projection; search by id/title; never offer production activation. |
| **Controls** | | Control | Type | Intent |
| | | Search | input | local filter |
| | | Open agent | link | in-app detail when route exists |
| | | Announce-only actions | button | fail-closed if governed |
| **Must** | Show draft/disclaimer; 19-agent catalog fidelity. |
| **Must not** | Activate specials; claim production. |
| **Redesign links** | Registry hub embed; specials redesign docs (cross-pack). |

#### `DomainPackExtensionSlot` — **Duty: domain-neutral extension slot**

| Field | Definition |
|-------|------------|
| **Duty** | Host optional domain pack UI extensions without forking shell; slot content is projection-driven and non-authoritative. |
| **Controls** | None required; children supply controls under same contracts. |
| **Redesign links** | Domain-adapter completeness; adoption redesign pack slots. |

---

## 4. Master component table (duty + controls)

| Component | Path | Duty defined? | Primary controls | Spec / redesign anchor |
|-----------|------|---------------|------------------|------------------------|
| `LoginScreen` | `LoginScreen.tsx` | **Yes** | email/password inputs, submit | `ui_01_login.md` |
| `DashboardHome` | `DashboardHome.tsx` | **Yes** | refresh, pause, links | `ui_02_dashboard.md` |
| `Dashboard` | `Dashboard.tsx` | **Yes** | legacy | `ui_02_dashboard.md` |
| `ComposerHome` | `ComposerHome.tsx` | **Yes** | compose actions | `ui_03_swarm_composer.md` |
| `Composer` | `Composer.tsx` | **Yes** | legacy | `ui_03_swarm_composer.md` |
| `CanvasHome` | `CanvasHome.tsx` | **Yes** | run, layout | `ui_04_canvas.md` |
| `Canvas` | `Canvas.tsx` | **Yes** | legacy | `ui_04_canvas.md` |
| `AgentDetailHome` | `AgentDetailHome.tsx` | **Yes** | tabs, propose | `ui_05_agent_detail.md` |
| `AgentDetail` | `AgentDetail.tsx` | **Yes** | legacy | `ui_05_agent_detail.md` |
| `ActivityHome` | `ActivityHome.tsx` | **Yes** | filters | `ui_06_activity.md` |
| `Activity` | `Activity.tsx` | **Yes** | legacy | `ui_06_activity.md` |
| `RegistryHome` | `RegistryHome.tsx` | **Yes** | search, facets, buttons | `ui_07_registry_hub.md` |
| `Registry` | `Registry.tsx` | **Yes** | legacy | `ui_07_registry_hub.md` |
| `SettingsHome` | `SettingsHome.tsx` | **Yes** | settings fields | `ui_08_settings.md` |
| `MonitoringHome` | `MonitoringHome.tsx` | **Yes** | inspect | `ui_09_monitoring.md` |
| `KnowledgeHome` | `KnowledgeHome.tsx` | **Yes** | search | `ui_10_knowledge.md` |
| `EvalHome` | `EvalHome.tsx` | **Yes** | run campaign | `ui_11_eval.md` |
| `NotificationsHome` | `NotificationsHome.tsx` | **Yes** | mark read | `ui_12_notifications.md` |
| `ProfileHome` | `ProfileHome.tsx` | **Yes** | profile fields | `ui_13_profile.md` |
| `AuditHome` | `AuditHome.tsx` | **Yes** | filters | `ui_14_audit.md` |
| `ApiPortalHome` | `ApiPortalHome.tsx` | **Yes** | portal actions | `ui_15_api_portal.md` |
| `OnboardingHome` | `OnboardingHome.tsx` | **Yes** | continue | `ui_16_onboarding.md` |
| `MobileHome` | `MobileHome.tsx` | **Yes** | compact actions | `ui_17_mobile.md` |
| `CollaborationHome` | `CollaborationHome.tsx` | **Yes** | collab actions | `ui_18_collaboration.md` |
| `CostsHome` | `CostsHome.tsx` | **Yes** | cost filters | `ui_19_costs.md` |
| `BlueprintsHome` | `BlueprintsHome.tsx` | **Yes** | gallery actions | `ui_20_blueprints.md` |
| `AppShell` | `AppShell.tsx` | **Yes** | shell chrome | `ui_00_menu.md` + §3.1 |
| `AuthenticatedShell` | `AuthenticatedShell.tsx` | **Yes** | auth shell | `ui_00_menu.md` + §3.1 |
| `ShellNavigation` | `ShellNavigation.tsx` | **Yes** | nav links | `ui_00_menu.md` |
| `BoundScreenHome` | `screen/BoundScreenHome.tsx` | **Yes (this catalog)** | none (binder) | §3.1 |
| `ScreenBoundary` | `ScreenBoundary.tsx` | **Yes (this catalog)** | recovery | §3.1 |
| `ResponsiveLayout` | `ResponsiveLayout.tsx` | **Yes (this catalog)** | none | §3.1 |
| `UnavailableScreen` | `UnavailableScreen.tsx` | **Yes (this catalog)** | recovery | §3.1 |
| `DemoModeBanner` | `DemoModeBanner.tsx` | **Yes (this catalog)** | dismiss | §3.1 |
| `InteractionStatusBar` | `ui/InteractionStatusBar.tsx` | **Yes (this catalog)** | none (status) | §3.2 |
| `OperationalAnnouncer` | `OperationalAnnouncer.tsx` | **Yes (this catalog)** | live region | §3.2 |
| `AccessibleDialog` | `AccessibleDialog.tsx` | **Yes (this catalog)** | close/primary | §3.2 |
| `IconControl` | `IconControl.tsx` | **Yes (this catalog)** | button | §3.2 |
| `GeneratedFilterBar` | `GeneratedFilterBar.tsx` | **Yes (this catalog)** | select/filters | §3.2 |
| `LocalDestinationPreview` | `LocalDestinationPreview.tsx` | **Yes (this catalog)** | none/preview | §3.2 |
| `design` | `design.tsx` | **Yes (this catalog)** | none | §3.2 |
| `DesignSystemPrimitives` | `design/DesignSystemPrimitives.tsx` | **Yes (this catalog)** | none | §3.2 |
| `ActionControl` | `projection/ActionControl.tsx` | **Yes (this catalog)** | button | §3.3 |
| `CopyCorrelationIdentifierButton` | `projection/CopyCorrelationIdentifierButton.tsx` | **Yes (this catalog)** | button | §3.3 |
| `EvidenceLink` | `projection/EvidenceLink.tsx` | **Yes (this catalog)** | button | §3.3 |
| `ReferenceLink` | `projection/ReferenceLink.tsx` | **Yes (this catalog)** | button | §3.3 |
| `SafeContent` | `projection/SafeContent.tsx` | **Yes (this catalog)** | optional external | §3.3 |
| `ProjectionStatus` | `projection/ProjectionStatus.tsx` | **Yes (this catalog)** | refresh/reconnect | §3.3 |
| `IngestionForms` | `projection/IngestionForms.tsx` | **Yes (this catalog)** | textarea, url, submit | §3.3 |
| `OperationsConsole` | `OperationsConsole.tsx` | **Yes (this catalog)** | inputs + submits | §3.4 |
| `OperatorConsole` | `OperatorConsole.tsx` | **Yes (this catalog)** | form controls | §3.4 |
| `ApprovalRolloutScreens` | `ApprovalRolloutScreens.tsx` | **Yes (this catalog)** | approve/deny | §3.4 |
| `KnowledgeArtifactScreens` | `KnowledgeArtifactScreens.tsx` | **Yes (this catalog)** | delegated | §3.4 |
| `OperationalScreens` | `OperationalScreens.tsx` | **Yes (this catalog)** | delegated | §3.4 |
| `SpecialsCatalog` | `SpecialsCatalog.tsx` | **Yes (this catalog)** | search, links | §3.5 |
| `DomainPackExtensionSlot` | `pack/DomainPackExtensionSlot.tsx` | **Yes (this catalog)** | slot | §3.5 |

**Duty definition coverage after this catalog: 56 / 56 Yes** (29 screen docs + 27 catalogued here).

### Implementation status (code `@duty` blocks — 2026-07-27)

**Coverage: 56 / 56 component sources with `@duty` (grep). Infra catalog (27) + screen Homes/shells/legacy aliases (29).**

#### Infra / binders / projection (prior batch)

| Component | `@duty` in source | Status |
|-----------|-------------------|--------|
| BoundScreenHome | Yes | **Completed** |
| ScreenBoundary | Yes | **Completed** |
| ResponsiveLayout | Yes | **Completed** |
| UnavailableScreen | Yes | **Completed** |
| DemoModeBanner | Yes | **Completed** |
| InteractionStatusBar | Yes | **Completed** |
| OperationalAnnouncer | Yes | **Completed** |
| AccessibleDialog | Yes | **Completed** |
| IconControl | Yes | **Completed** |
| GeneratedFilterBar | Yes | **Completed** |
| LocalDestinationPreview | Yes | **Completed** |
| design / DesignSystemPrimitives | Yes | **Completed** |
| ActionControl | Yes | **Completed** |
| CopyCorrelationIdentifierButton | Yes | **Completed** |
| EvidenceLink | Yes | **Completed** |
| ReferenceLink | Yes | **Completed** |
| SafeContent | Yes | **Completed** |
| ProjectionStatus | Yes | **Completed** |
| IngestionForms | Yes | **Completed** |
| OperationsConsole | Yes | **Completed** |
| OperatorConsole | Yes | **Completed** |
| ApprovalRolloutScreens | Yes | **Completed** |
| KnowledgeArtifactScreens | Yes | **Completed** |
| OperationalScreens | Yes | **Completed** |
| SpecialsCatalog | Yes | **Completed** |
| DomainPackExtensionSlot | Yes | **Completed** |

#### Screen Homes / shells / legacy aliases (this batch)

| Component | `@duty` in source | Status |
|-----------|-------------------|--------|
| LoginScreen | Yes | **Completed** |
| AppShell | Yes | **Completed** |
| AuthenticatedShell | Yes | **Completed** |
| ShellNavigation | Yes | **Completed** |
| DashboardHome | Yes | **Completed** |
| Dashboard | Yes | **Completed** |
| ComposerHome | Yes | **Completed** |
| Composer | Yes | **Completed** |
| CanvasHome | Yes | **Completed** |
| Canvas | Yes | **Completed** |
| AgentDetailHome | Yes | **Completed** |
| AgentDetail | Yes | **Completed** |
| ActivityHome | Yes | **Completed** |
| Activity | Yes | **Completed** |
| RegistryHome | Yes | **Completed** |
| Registry | Yes | **Completed** |
| SettingsHome | Yes | **Completed** |
| MonitoringHome | Yes | **Completed** |
| KnowledgeHome | Yes | **Completed** |
| EvalHome | Yes | **Completed** |
| NotificationsHome | Yes | **Completed** |
| ProfileHome | Yes | **Completed** |
| AuditHome | Yes | **Completed** |
| ApiPortalHome | Yes | **Completed** |
| OnboardingHome | Yes | **Completed** |
| MobileHome | Yes | **Completed** |
| CollaborationHome | Yes | **Completed** |
| CostsHome | Yes | **Completed** |
| BlueprintsHome | Yes | **Completed** |

**ALL_COMPONENT_DUTIES_COMPLETE**

---

## 5. Button / input coverage checklist (implementation standard)

| Control class | Required behavior | Owner |
|---------------|-------------------|--------|
| Primary mutate button | Disabled when busy/stale/ineligible; idempotent key via runtime | Screen Home / `ActionControl` / OperationsConsole |
| Secondary local button | Session-only feedback; no host authority | Homes via `onAction` / `classifyAnnounce` |
| Search/filter input | Local filter or authorized query params only | Homes / `GeneratedFilterBar` / `SpecialsCatalog` |
| Textarea content | Untrusted data; no execute | `IngestionForms`, operator reason fields |
| External URL field | Non-authoritative format check; server evaluates | `IngestionForms` |
| Copy correlation | Clipboard only | `CopyCorrelationIdentifierButton` / status bar |
| Nav link | In-app routes; external only if allowed-action | `SafeContent`, Homes |
| Dialog primary | Focus restore; cancel always available | `AccessibleDialog` + parent |

---

## 6. Gaps remaining (honest)

| Gap | Severity | Follow-up |
|-----|----------|-----------|
| Not every screen doc lists every DOM `id` for every button | Low | Optional per-screen control appendix |
| Full ingestion API may be absent in generated client | Medium | Forms stay unavailable until contract exists (already designed) |
| Specials deep duty also in specials redesign | Low | Cross-link maintained; this catalog is FE redesign home |
| Legacy modules (`Dashboard`, `Registry`, …) vs `*Home` | Low | Prefer Homes; keep legacy for compatibility |
| Host-backed mutations without action refs | By design | Buttons call `governed.fail_closed` or local-only handlers — never invent authority |

### Control implementation status (2026-07-27)

| Check | Result |
|-------|--------|
| Dead `<button>` (no onClick/submit) in `components/**` | **0** |
| Unbound text `<input>` / `<textarea>` / `<select>` (no value/onChange) | **0** |
| Homes accept `onAction` + `ScreenUiAction` | **Yes** (scan test) |
| `BoundScreenHome` wires bridge for all screens | **Yes** |
| Local filters/chips/zoom/group-by | **Wired** (presentation-only) |
| Governed primary CTAs without host refs | **Fail-closed via classifyAnnounce** |
| `npm run typecheck` | **pass** |
| `npm test` (frontend suite) | **251 pass** |

**ALL_BUTTON_INPUT_CONTROLS_COMPLETE** (within fail-closed browser non-authority contract)

---

## 7. Traceability

| Artifact | Role |
|----------|------|
| `docs/frontend_redesign/ui_00`–`ui_20` | Screen duties |
| `docs/frontend_redesign/frontend_redesign.md` | Cross-cutting contracts |
| **This file** | Component duties + control ownership for previously undefined modules |
| `frontend/src/components/**` | Implementation |
| `frontend/src/lib/ui/interaction-runtime.ts` / `screen-actions.ts` | Action bridge |

---

*End of component duty catalog v1.0.*
