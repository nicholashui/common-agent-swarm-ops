# Dashboard — step-by-step user guide

**Screen:** Dashboard (Home)  
**Route:** `/`  
**Who it’s for:** Operators reviewing fleet health, running swarms, and recent runs.

---

## 1. Before you start

1. Open the app (default local URL: `http://127.0.0.1:3001`).
2. If you are not signed in, you are redirected to **Login**.
3. Sign in (example admin: `nicholas.hui@local` / `NicholasAdmin1!`).
4. After sign-in you land on the **Dashboard**.

---

## 2. Open the Dashboard

1. In the left menu under **HOME**, click **Dashboard**.
2. Or go directly to `/`.
3. Confirm the top of the page shows the dashboard title, description, and freshness label (e.g. live vs stale).

---

## 3. Read fleet status

1. Scan the **header freshness** line (as-of time and stale indicator if delayed).
2. Review any **status message** under the header (session feedback from actions).
3. Read **insight cards** (if shown): each has a short body and one or more links.
4. Open an insight action link only if you intend to leave the dashboard for that destination.

---

## 4. Running swarms

1. Find the **Running swarms** (or equivalent) section.
2. For each swarm card, note id/name and status.
3. To pause a swarm **in this session only**:
   - Click the pause control on that card.
   - Confirm a success/info message appears (session pause is not host production authority).
4. If pause is unavailable, the UI will fail closed with an honest message.

---

## 5. Recent runs

1. Open the **Recent runs** list/table.
2. Scan run id, status, and timing.
3. Follow any **inspect** or navigation link only when you need run detail elsewhere (e.g. Monitoring / Activity).

---

## 6. Control plane strip

1. Locate the **Control plane** section.
2. Read API health, backlog, approval alerts, and SSE/freshness labels as **projections** (display-only).
3. Use **View affected** (or similar) only when you need the linked operational screen.

---

## 7. Help for this screen

1. Top-right **Help** (`?`) opens the right help drawer for this route.
2. Top-right **Documents** (book) opens the full-page user guide.
3. Drawer tabs (all routes):
   - **User guide** → `userguide.md`
   - **Func spec** → `func_spec.md` (detailed functional requirements)
   - **Test scenarios** → `test_scenario.md` (test cases)

---

## 8. Safety notes

- Browser is **non-authority**: dashboard never invents host approvals or production activation.
- Session pause is local/session feedback unless the host returns an authorized action reference.
- Do not treat demo/local projections as live production truth without host confirmation.

---

## Appendix — user guides by screen (help panel)

Open each screen, then click top-right **Help** (`?`). The **User guide** tab loads the matching file under `public/docs`:

| Screen | Route | Doc path |
|--------|--------|----------|
| Dashboard | `/` | `/docs/userguide.md` |
| Login | `/login` | `/docs/login/userguide.md` |
| Composer | `/composer` | `/docs/composer/userguide.md` |
| Swarm Canvas | `/canvas` | `/docs/canvas/userguide.md` |
| Nested canvas | `/swarms/<id>/canvas` | `/docs/swarms/canvas/userguide.md` (fallback) |
| Blueprints | `/blueprints` | `/docs/blueprints/userguide.md` |
| Registry Hub | `/registry` | `/docs/registry/userguide.md` |
| Agent detail | `/registry/agents/<id>` | `/docs/registry/agents/userguide.md` (fallback) |
| Activity | `/activity` | `/docs/activity/userguide.md` |
| Monitoring | `/operations` | `/docs/operations/userguide.md` |
| Notifications | `/notifications` | `/docs/notifications/userguide.md` |
| Costs | `/costs` | `/docs/costs/userguide.md` |
| Knowledge | `/knowledge` | `/docs/knowledge/userguide.md` |
| Evaluations | `/evaluations` | `/docs/evaluations/userguide.md` |
| Audit | `/audit` | `/docs/audit/userguide.md` |
| Collaboration | `/collaboration` | `/docs/collaboration/userguide.md` |
| API Portal | `/developer/api` | `/docs/developer/api/userguide.md` |
| Onboarding | `/onboarding` | `/docs/onboarding/userguide.md` |
| Settings | `/settings` | `/docs/settings/userguide.md` |
| Profile | `/profile` | `/docs/profile/userguide.md` |
| Mobile | `/mobile` | `/docs/mobile/userguide.md` |
| Doc viewer | `/docs/view` | `/docs/docs/view/userguide.md` |

**Func spec** and **Test scenarios** tabs use the same folder layout with `func_spec.md` and `test_scenario.md` (22 screens each).
