# Notifications — functional specification

**Route:** `/notifications` · **Auth:** required · **Component:** `NotificationsHome`

## Functional requirements

### FR-NTF-001 List & badge
- SHALL list projected notifications and show unread count (session read set applied).

### FR-NTF-002 Filters
- Kind filters (All/Proposals/…) SHALL filter list locally.

### FR-NTF-003 Group by
- Group-by control cycles presentation groupings (time/kind/priority/none).

### FR-NTF-004 Mark read
- Mark all / single SHALL use `local.mark_read` when bridged + update local read set.

### FR-NTF-005 Preferences
- Preference toggles + save use local.save_prefs or equivalent session feedback.

### FR-NTF-006 Item CTAs
- Governed CTAs fail closed; no secrets in payloads.

### FR-NTF-007 Help
- `/docs/notifications/{userguide,func_spec,test_scenario}.md`
