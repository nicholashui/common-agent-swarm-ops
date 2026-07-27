# Swarm Composer — step-by-step user guide

**Screen:** Compose  
**Route:** `/composer`  
**Who it’s for:** Operators drafting swarm goals and selecting common patterns.

---

## 1. Open Composer

1. Sign in.
2. Left menu **BUILD** → **Compose**, or open `/composer`.
3. Confirm the composer layout: goal area, pattern browser, and action controls.

---

## 2. Name the swarm draft

1. Locate the swarm name field (header or draft title).
2. Type a clear draft name.
3. Name is local presentation until a host compose action exists.

---

## 3. Describe the goal

1. In the main composer/goal text area, describe what the swarm should do.
2. Be specific (inputs, quality bars, outputs).
3. Keep secrets out of the goal text (no API keys, tokens, or PII dumps).

---

## 4. Browse common patterns

1. Open the **Pattern browser** (side panel or list).
2. Click a pattern card to select it (pressed/selected state).
3. Read pattern name, when-to-use notes, and metrics.
4. Selection is local until you submit an authorized instantiate/compose intent.

---

## 5. Send / recommend

1. Click **Send** (or equivalent primary compose control).
2. If a host action reference is available, the app submits through the interaction runtime.
3. If not, you receive a **fail-closed** message: compose requires an authorized action reference.
4. Read the status bar / composer status for confirmation or errors.

---

## 6. Save draft (local)

1. Click **Save draft** if present.
2. Expect a session-local confirmation (not durable host authority unless contracted).

---

## 7. Navigate away

1. **Close** returns to dashboard or prior shell route when linked.
2. Unsaved draft text may be lost on refresh unless host persistence exists.

---

## 8. Help

1. Top-right **Help** opens this guide for `/composer`.
2. **Documents** opens the full-page viewer for the same content.

---

## 9. Safety notes

- Pattern instantiate/run requires host eligibility; the browser does not invent action IDs.
- Composer never enables production providers by itself.
