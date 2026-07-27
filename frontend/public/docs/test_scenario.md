# Dashboard — test scenarios

**Route:** `/`  
**Priority key:** P0 = release blocker, P1 = major, P2 = minor

---

## TS-DASH-001 Anonymous redirect (P0)

| Field | Value |
|-------|--------|
| **Given** | No valid session cookie |
| **When** | User opens `/` |
| **Then** | Redirect to `/login` |
| **Evidence** | Location is `/login`; dashboard content not shown |

---

## TS-DASH-002 Authenticated render (P0)

| Field | Value |
|-------|--------|
| **Given** | Valid session (e.g. nicholas.hui@local) |
| **When** | User opens `/` |
| **Then** | Dashboard title/description/freshness render; no crash |
| **Evidence** | Visible heading; freshness status region present |

---

## TS-DASH-003 Freshness stale indicator (P1)

| Field | Value |
|-------|--------|
| **Given** | Projection with `stale=true` |
| **When** | Dashboard renders |
| **Then** | Freshness UI indicates stale |
| **Evidence** | Stale class/label present |

---

## TS-DASH-004 Pause swarm session feedback (P1)

| Field | Value |
|-------|--------|
| **Given** | Running swarm card with pause control |
| **When** | Operator clicks pause |
| **Then** | Session feedback success/info via action bridge |
| **Evidence** | Status message mentions swarm id / pause; no invented host approval |

---

## TS-DASH-005 Insight links stay in-app (P1)

| Field | Value |
|-------|--------|
| **Given** | Insight with primary/secondary hrefs |
| **When** | User inspects links |
| **Then** | hrefs are projected relative/in-app paths |
| **Evidence** | No `javascript:` or untrusted absolute fetch URLs |

---

## TS-DASH-006 Help panel docs (P1)

| Field | Value |
|-------|--------|
| **Given** | Authenticated on `/` |
| **When** | User opens Help panel → Func spec / Test scenarios / User guide |
| **Then** | Corresponding `/docs/*.md` content loads (or soft empty if missing) |
| **Evidence** | Markdown headings visible; no HTML index fallback treated as content |

---

## TS-DASH-007 No secrets in markup (P0)

| Field | Value |
|-------|--------|
| **Given** | Dashboard rendered |
| **When** | Inspect DOM/source |
| **Then** | No password, bearer token, or raw provider payload strings |
| **Evidence** | Grep/assert does not match secret patterns |
