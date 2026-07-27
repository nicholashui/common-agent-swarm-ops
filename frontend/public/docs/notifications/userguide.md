# Notifications — step-by-step user guide

**Screen:** Notifications Center  
**Route:** `/notifications`  
**Who it’s for:** Operators triaging proposals, rollouts, gates, and anomalies notices.

---

## 1. Open Notifications

1. Sign in → **OPERATE** → **Notifications**, or `/notifications`.
2. Note the unread badge count on the title.

---

## 2. Search and filters

1. Search notification title/body/meta.
2. Click filter chips (All, Proposals, Rollouts, Gates, Anomalies, …).
3. Active filter is pressed; list updates.

---

## 3. Group by

1. Click **Group by** to cycle time / kind / priority / none.
2. Layout of sections updates for local presentation.

---

## 4. Mark read

1. **Mark all read** marks every item read in session and reports via status.
2. Per-item actions may mark single ids read.
3. Session mark-read is not host ACL unless contracted.

---

## 5. Item actions

1. Open a notification card.
2. Primary/secondary actions either navigate in-app or fail closed for governed host commands.
3. Payloads never embed secrets or raw approval ops.

---

## 6. Preferences

1. Toggle notify-about and channel checkboxes.
2. **Save preferences** stores session preference summary.
3. **Snooze type** is local presentation only.

---

## 7. Help

1. **Help** → this guide.
2. Prefer host-authorized notification policies in production deployments.
