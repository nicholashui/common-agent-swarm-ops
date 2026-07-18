# NN UI 01: Login Page Spec

**UI ID:** nn_ui_01_login  
**Version:** 1.0 (Aligned to common-agent-swarm-ops v2.0 redesign)  
**Related Main Doc Section:** Ui1 + post-login flow  
**Date:** 2026-07-18  
**Owner:** Nicholas / Frontend Team  
**Status:** Ready for implementation / Figma handoff

## Purpose & Goals
- Secure, frictionless entry point into the common-agent-swarm-ops platform.
- Emphasize the "common" and professional ops nature of the product.
- Support self-hosted Keycloak OIDC + simple auth.
- Low-friction demo access for new users to experience Common Registry and sample swarms immediately.
- Bilingual-ready (EN primary + 繁體中文 toggle).

## Layout & Structure (Desktop-first, responsive)

**Full-viewport centered card on dark gradient/grid background** (subtle tech feel, not busy).

- **Top-left (persistent branding):** Logo (stylized swarm/node icon or "NN" monogram) + "common-agent-swarm-ops" wordmark. Tagline below in smaller text: "Reusable agent swarms • Collective improvement • Production ops".
- **Center Card (max-w-md or ~420px, elevated with subtle glass/shadow):**
  - Header inside card: "Sign in to orchestrate swarms" (or "Access Common Registry & Ops").
  - Auth form.
  - Divider or section for SSO / Enterprise.
  - Footer links inside or below card: Docs, GitHub, Status, Language (EN / 繁體中文).
- **Bottom subtle:** "Demo available • No credit card" or version/build info.
- **Mobile (< md):** Card takes ~90% width, vertical stack, logo centered or top.

**Visual Treatment:** Dark slate background (#0f172a), card bg #1e2937 with border or subtle gradient. Accent indigo/violet on primary buttons and "Common" highlights. High contrast text.

## Components & Variants

1. **Branding Header**
   - Logo + product name (link to marketing site or /).
   - Optional: Small "v2.0 • Common Registry Live" badge.

2. **Auth Form (Email/Password or Magic Link)**
   - Email input (shadcn Input + label).
   - Password input (with show/hide toggle).
   - "Sign in" primary button (full width, shadcn Button variant="default" size="lg").
   - "Forgot password?" link (opens modal or routes to reset flow — future).
   - Checkbox: "Remember this device" (localStorage + longer session).
   - Loading state: Button shows spinner + "Signing in...".

3. **SSO / Enterprise Section**
   - Text: "Or continue with".
   - Buttons (outline or secondary):
     - "Keycloak (Self-hosted)" — primary enterprise path, triggers OIDC flow.
     - "Google", "GitHub" (if configured).
   - For orgs: "Enterprise SSO" that opens Keycloak realm selector or direct redirect.

4. **Demo Access (Prominent but secondary)**
   - Large secondary button or card below form: "Try Demo Workspace" (no login).
     - On click: Creates ephemeral demo session with preloaded Common Registry, sample Trading Swarm, Content Pipeline, and DSE Tutor examples. Redirects to Dashboard with "Demo" banner (dismissible, shows "Exit demo" that clears session).
   - Subtext: "Explore Common Agents, Patterns & live ops without setup".

5. **Error / Feedback States**
   - shadcn Alert or Sonner toast for invalid credentials, network error, account locked, etc.
   - Inline field errors (red border + helper text).

6. **Language Toggle**
   - Subtle select or buttons in card footer or global header. Persists preference. All labels, placeholders, errors translated. Prompts in composer later respect user language.

## Data, State & API Needs

**No heavy data on load** (static page).

**On submit:**
- POST /auth/login (or next-auth / Keycloak endpoint).
- Success: Set session (JWT or cookie), redirect to last business/workspace or /dashboard. Store "lastBusinessId" in localStorage or user prefs.
- On OIDC success: Handle callback, create/link user, redirect.

**Client State (Zustand or context):**
- `isDemoMode`, `demoSessionData` (if demo).
- Theme preference (dark default, respects system but product is dark-first).
- Language preference.

**Backend Expectations:**
- Keycloak realm per business/workspace or single realm with groups.
- Optional magic link / passwordless.
- Rate limiting + audit on login attempts.
- Demo mode: Backend seeds ephemeral data or uses read-only demo tenant.

## Interactions & User Flows

**Primary Flow (Returning User):**
1. Arrive → see form.
2. Enter creds or click Keycloak → authenticated → Dashboard (with Common Health overview prominent).

**Demo Flow (New / Curious User):**
1. Click "Try Demo Workspace".
2. Loading state ( "Preparing Common Registry & sample swarms..." — shows progress of seeding common agents/patterns).
3. Redirect to Dashboard with demo banner: "You are in Demo mode. Common Agents & Patterns are preloaded. Run swarms safely. [Exit Demo]".
4. All Registry, Canvas, Activity read/write in demo tenant (reset on exit or 24h).

**Error Recovery:**
- Wrong password: Shake form or inline error + "Reset password" link.
- OIDC failure: Clear error toast + retry button.

**Keyboard:**
- Enter submits form.
- Tab navigation full.
- Cmd/Ctrl + K not active here (global command palette loads post-login).

## Accessibility, i18n & Polish

- Full ARIA labels, roles, focus management.
- High contrast (WCAG AA+).
- Screen reader friendly (logo alt, form labels, button descriptions).
- i18n: All strings in translation keys. Chinese fonts loaded. Right-to-left ready if needed later.
- Performance: Instant load, no heavy JS on initial render. Code-split auth logic.
- Security: No sensitive data in localStorage except session tokens (httpOnly cookies preferred). CSP headers.

## Open Questions / Implementation Notes

- Exact Keycloak client config / redirect URIs (dev vs prod).
- Demo seeding script (which Common Agents/Patterns to preload — suggest core 8–10 from redesign).
- Magic link support priority?
- "Remember me" duration (7d vs 30d).
- Post-demo conversion nudge ( "Create free account to save your swarms & contribute to commons" — non-intrusive banner after 3 runs).

## Wireframe / Visual References (Text Description)

```
[Logo + common-agent-swarm-ops          ]

          ┌──────────────────────────────┐
          │  Sign in to orchestrate      │
          │  reusable agent swarms       │
          │                              │
          │  Email                       │
          │  [________________________]  │
          │  Password                    │
          │  [________________________]  │
          │  [ Sign in ]                 │
          │  Forgot password?            │
          │  ───────── or ─────────      │
          │  [ Keycloak (Self-hosted) ]  │
          │  [ Google ] [ GitHub ]       │
          │                              │
          │  Try Demo Workspace →        │
          │  (Explore Common Registry)   │
          └──────────────────────────────┘

[Language] [Docs] [GitHub] [Status]
```

**Figma / Dev Handoff Notes:** Use shadcn/ui primitives throughout. Primary button uses indigo accent. Demo button uses violet or outline variant to differentiate. Subtle animated grid or node particles in background optional (Framer Motion, low perf impact).

**Dependencies:** next-auth or @react-oauth, sonner for toasts, lucide-react icons.

This spec is self-contained for a developer or AI coding agent (Cursor/Kiro) to implement the page + auth flow integration. Cross-reference main `frontend_redesign.md` for global design system, color tokens, and component library.