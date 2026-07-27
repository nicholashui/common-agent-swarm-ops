# Monitoring / Operations — step-by-step user guide

**Screen:** Monitoring (Advanced ops)  
**Route:** `/operations`  
**Who it’s for:** Operators reviewing fleet cards, traces, alerts, and recovery labels.

---

## 1. Open Monitoring

1. Sign in → **OPERATE** → **Monitoring**, or `/operations`.
2. Confirm live fleet cards, search, filters, and tabs (e.g. Traces / Alerts).

---

## 2. Search

1. Use the search box to filter traces/alerts locally by label/text.
2. Clear search to restore the full projection list.

---

## 3. Sidebar filters

1. Click each filter control (environment, severity, window, service, …).
2. Each click **cycles** local filter values.
3. Status announces the selected value (presentation filter).

---

## 4. Tabs

1. Switch **Traces**, **Alerts**, or other projected tabs.
2. Trace tree: click nodes to select; expand evidence when offered.
3. Evidence/expand without host projection fails closed honestly.

---

## 5. Alerts and recovery

1. Review alert rules table.
2. **New Rule** / **Test notify** require authorized ops actions.
3. Anomaly cards: **Rollback** / **Investigate** fail closed without host recovery refs.

---

## 6. Help

1. Help panel binds to `/operations` → `/docs/operations/userguide.md`.
2. Full-page documents use the same path convention.

---

## 7. Safety notes

- No fabricated infrastructure probes for tenancy disclosure.
- High-risk anomaly content stays redacted; no secrets in UI.
