# NN UI 18: Collaboration, Sharing & Multi-User Spec

**UI ID:** nn_ui_18_collaboration  
**Version:** 1.0 (Aligned to common-agent-swarm-ops v2.1 — Phase 2+)  
**Related Main Doc Section:** Ui18  
**Date:** 2026-07-18  
**Owner:** Nicholas / Frontend Team  
**Status:** Ready for implementation (Phase 2)

## Purpose & Goals
Enable team and cross-business collaboration on swarms and commons governance while preserving individual control and full auditability.

## Layout & Structure
Sharing modals/drawers + presence indicators on canvas + comment sidebars + team dashboard widgets. Real-time sync where applicable.

## Key Components
- Share Modal: Link generation with permission levels (view, comment, edit), expiration, password. Embed options (read-only canvas or activity).
- Real-time Canvas: Multiple cursors/avatars, live presence, conflict resolution (Yjs/CRDT recommended for v1 or later).
- Comments & Mentions: Threaded on nodes, proposals, or swarms. @mentions with notifications.
- Team Workspace Dashboard: Shared favorites, recent team activity, pending proposals assigned to team.
- Proposal Review Workflows: Assignment, discussion, approval chain UI.
- Public/Community Publishing (opt-in): Controls for anonymized or credited publication of commons.

## Data & API
- Permissions & sharing model.
- Real-time sync backend (Yjs + WebSocket or similar).
- Comments storage + notifications.
- Team/workspace queries.

## Interactions
- Share button everywhere (canvas, registry item, activity row) → modal.
- Canvas: See teammates' cursors and selections in real time.
- @mention in comment → notification + deep link.
- Proposal assignment → assignee gets task in notifications + dashboard.

## Polish & Accessibility
Presence avatars clear and non-intrusive. Accessible comments and modals. Conflict resolution feedback gentle. Bilingual comments where possible.

## Wireframe Summary
Canvas with presence avatars top-right. Share modal with permission toggles. Comment sidebar on selected node. Team dashboard widgets.

**Implementation Notes:** Real-time collab is advanced (Yjs + awareness protocol). Start with sharing links + comments (simpler). Auditability must never be compromised. High value for teams working on complex swarms or commons governance.