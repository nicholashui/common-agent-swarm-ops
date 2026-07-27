# Audit — step-by-step user guide

**Screen:** Governance & Audit Trail  
**Route:** `/audit`  
**Who it’s for:** Operators reviewing append-only redacted audit projections.

---

## 1. Open Audit

1. Sign in → **GOVERNANCE** → **Audit**, or `/audit`.
2. Confirm search, filters, log table, integrity strip, and detail drawer.

---

## 2. Search

1. Type actor, action, target, correlation id, or summary text.
2. Correlation field reuses the same query filter for support lookups.

---

## 3. Filters

1. **Time range** chip cycles local ranges.
2. **Actor** chip cycles projected actors + “all”.
3. **Action type** chips toggle multi action-type filter.
4. Table rows update; select a row to open detail.

---

## 4. Row detail

1. Click a log row.
2. Read redacted summary, hashes, links.
3. Follow only opaque evidence/navigation links from the projection.

---

## 5. Export and integrity

1. **Export CSV** / **Verify integrity** require authorized compliance jobs (fail-closed).
2. Pre-built report links same rule.

---

## 6. Help

1. Help panel loads `/docs/audit/userguide.md`.
2. Audit UI never shows private tool parameters or secrets.
