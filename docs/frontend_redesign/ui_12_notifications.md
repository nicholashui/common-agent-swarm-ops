# NN UI 12: Notifications Center Spec

**UI ID:** nn_ui_12_notifications  
**Version:** 1.0 (Aligned to common-agent-swarm-ops v2.1)  
**Related Main Doc Section:** Ui12  
**Date:** 2026-07-18  
**Owner:** Nicholas / Frontend Team  
**Status:** Ready for implementation

## Purpose & Goals
Centralized, actionable hub for all system events so users stay in control without constant manual monitoring.

## Layout & Structure
List or kanban view (To Do / In Progress / Done or grouped by type). Filters + search. Global header bell opens this or drawer.

## Key Components
- Notification Cards/List: Rich content with embedded actions (deep links, approve buttons, "Update to latest commons").
- Grouping: By swarm, common component, or priority.
- Preferences Panel: Toggle per type + delivery method (in-app, email, Slack/Telegram, PWA push). Quiet hours/digest.
- History: Searchable full log.

## Data & API
- Notification CRUD + read/action state.
- Preference store.
- Event triggers from orchestrator/registry/eval/etc.
- Delivery logs.

## Interactions
- Click notification → deep link to relevant UI (canvas with context, proposal review, rollout impact).
- Bulk mark read or take action on grouped items.
- "Snooze this type for 24h".

## Polish & Accessibility
Clear priority indicators. Accessible list with keyboard nav. Real-time push via WS. Bilingual content where applicable.

## Wireframe Summary
Header with filters. Main list of rich actionable cards. Side or modal: Preferences. Badge count on global bell.

**Implementation Notes:** Integrate with global header bell. Actionable notifications dramatically improve ops experience. PWA push is high value for mobile.


## VA-Agent-Swarm Notification Alignment

Notifications are derived from the event contract in [`va_agent_structure_mapping.md`](va_agent_structure_mapping.md). Define payload and deep-link support for task state changes, artifact creation/QC failure, directed critique, gate ready/resolved, budget threshold, metric failure, memory/contribution outcome, tool completion/error, phase transition, rollout, and recoverable/terminal error events.

A gate notification includes criteria, affected artifacts, L1/L2/L3 status, Judge/GateKeeper evidence, expiration/assignment, and an approval link. A critique notification includes source, target, severity, evidence reference, and resolution state. Delivery channels receive redacted summaries only; user actions call an authorized server command and never embed an approval operation, secret, or raw artifact content in the notification payload.
