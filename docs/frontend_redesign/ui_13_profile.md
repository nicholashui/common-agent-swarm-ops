# NN UI 13: User Profile & Preferences Spec

**UI ID:** nn_ui_13_profile  
**Version:** 1.0 (Aligned to common-agent-swarm-ops v2.1)  
**Related Main Doc Section:** Ui13  
**Date:** 2026-07-18  
**Owner:** Nicholas / Frontend Team  
**Status:** Ready for implementation

## Purpose & Goals
Personal control center for identity, automation access, preferences, and visibility into personal contribution/usage value.

## Layout & Structure
Clean profile page with sections or tabs (Account, Security, Usage & Impact, Preferences, API Tokens).

## Key Components
- Profile info + connected SSO providers.
- Personal Impact Cards: Runs contributed, improvements helped, knowledge contributed, savings generated.
- API Token Manager: Create (with scopes), list, revoke, usage logs.
- Preferences: Language, theme, default workspace, notification detailed settings, canvas defaults.
- Usage History: Personal recent activity summary with links.

## Data & API
- User profile + preferences.
- Token service (create/revoke/usage).
- Personal aggregation queries (impact, usage).
- Keycloak integration for SSO/roles.

## Interactions
- Create token → copy once + scopes selector + never shown again.
- Revoke with confirmation.
- Impact cards clickable to filtered activity or Registry views.

## Polish & Accessibility
Clean, trustworthy design for security-sensitive areas. Accessible forms and token list. Bilingual preferences.

## Wireframe Summary
Header with avatar. Sections with cards and tables. Token management with create/revoke actions prominent.

**Implementation Notes:** Token scopes must align with backend permissions. Personal impact stats reinforce value of participating in commons.


## VA-Agent-Swarm Profile Alignment

Profile data controls presentation and personal preferences only. It may show authorized contribution, review, and operational impact from the projections in [`va_agent_structure_mapping.md`](va_agent_structure_mapping.md), but it must not grant roles, reveal other users' artifacts/critique, or expose credentials/tool authority. Effective role and organization scope remain server-derived.
