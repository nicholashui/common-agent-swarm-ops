# Dashboard — functional specification

**Screen ID:** ui_02_dashboard (conceptual)  
**Route:** `/`  
**Shell:** Authenticated (`AppShell` → login required)  
**Authority model:** Browser non-authority; mutations only via host action bridge when eligible.

---

## 1. Purpose

Provide an operational home that projects fleet health, running swarms, recent runs, insights, and control-plane status without inventing host authority.

## 2. Actors

| Actor | Access |
|-------|--------|
| Authenticated operator | Full dashboard projection |
| Anonymous | Redirect to `/login` |

## 3. Preconditions

- Valid signed session cookie (`frontend_session` / `__Host-casops-session`).
- Dashboard projection available via bound screen parameters / local fixture.

## 4. Functional requirements

### FR-DASH-001 Screen binding
- The route SHALL render `DashboardHome` through the authenticated shell.
- Anonymous access SHALL redirect to `/login`.

### FR-DASH-002 Projection display
- The screen SHALL display title, description/lede, and freshness/as-of status from the projection.
- When projection is stale, freshness UI SHALL indicate stale state.

### FR-DASH-003 Status feedback
- External `statusMessage` / interaction status SHALL be shown in an accessible live region when present.

### FR-DASH-004 Insights
- Insight cards SHALL render title, body, optional badge, and action links from projection only.
- Action hrefs SHALL be in-app or host-allowed destinations only (no invented protected URLs).

### FR-DASH-005 Running swarms
- Running swarm cards SHALL list projected swarms.
- Pause control SHALL invoke session pause via `onPause` / `local.pause_swarm` when wired.
- Pause SHALL NOT claim production host pause without host contract.

### FR-DASH-006 Recent runs
- Recent runs SHALL render projected run summaries.
- Navigation/inspect links SHALL only use projected routes/refs.

### FR-DASH-007 Control plane strip
- Control-plane cells SHALL display projected API health, backlog, approval alerts, SSE labels, correlation id.
- The UI SHALL NOT fabricate tenancy/infra probe data.

### FR-DASH-008 Help panel attachment
- Help drawer SHALL resolve `/docs/userguide.md`, `/docs/func_spec.md`, `/docs/test_scenario.md` for route `/`.

## 5. Non-functional requirements

| ID | Requirement |
|----|-------------|
| NFR-DASH-001 | No credentials in local storage from this screen. |
| NFR-DASH-002 | Fail-closed messages for governed actions without action refs. |
| NFR-DASH-003 | Accessible status regions (`aria-live`) for feedback. |

## 6. Out of scope

- Production media activation.
- Inventing host approve/deny from the dashboard.
- Direct provider network calls from the browser.
