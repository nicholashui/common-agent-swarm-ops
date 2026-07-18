# NN UI 17: Mobile / PWA Companion Views Spec

**UI ID:** nn_ui_17_mobile  
**Version:** 1.0 (Aligned to common-agent-swarm-ops v2.1)  
**Related Main Doc Section:** Ui17  
**Date:** 2026-07-18  
**Owner:** Nicholas / Frontend Team  
**Status:** Ready for implementation

## Purpose & Goals
Enable on-the-go monitoring, quick actions, and approvals without needing a desktop — critical for responsive ops.

## Layout & Structure
Responsive web (Tailwind) or dedicated PWA views. Bottom navigation (Dashboard, Activity, Registry, Notifications, Profile). Large tap targets. Simplified cards.

## Key Components (Read-heavy, action-oriented)
- Dashboard: Summary cards (common health, running count, critical alerts) + quick links.
- Activity Feed: Recent runs with status, common version, quick "Replay with latest" or "Update commons".
- Registry Quick Search + actions (favorite, propose improvement, add to swarm).
- Notifications: Actionable list with deep links and one-tap approve/rollback.
- Agent/Swarm quick detail: History summary, ops status, limited playground.
- Approvals: Impact summary + approve/deny with reason.

## Data & API
- Same backend APIs as desktop (optimized responses for mobile).
- PWA: Service worker for offline cache (recent activity, registry search), push notifications.
- Responsive images and components.

## Interactions
- Pull-to-refresh on feeds.
- Swipe actions on list items (mark read, quick replay).
- Bottom sheet for detail/actions instead of modals where appropriate.

## Polish & Accessibility
Touch-friendly (44px+ targets). Offline indicators. Push permission flow. High contrast. Fast load on mobile networks.

## Wireframe Summary
Bottom nav. Cards and lists optimized for vertical scrolling. Bottom sheets for actions/detail. Notification badge prominent.

**Implementation Notes:** Next.js PWA setup (manifest, service worker). Avoid heavy canvas editing on mobile (read-only mini views or deep link to desktop). Push notifications via service worker + backend. High value for real ops use.