# Handoff

**As of:** 2026-07-26  
**State:** ui_00_menu frontend implementation reviewed, corrected, and tested.

## Latest work

### ui_01_login + session entry (current)
- Login UI per ui_01_login.md/svg + local session entry APIs under `frontend/src/app/api/auth/`
- Local users: `demo@local`/`demo`, `ops@local`/`ops` (override via `CASOPS_LOCAL_AUTH_USERS`)
- Demo mode: `/api/auth/demo` + dismissible banner + Exit Demo logout
- Password reset request/confirm (dev token exposed only non-production)
- OIDC start + **callback code exchange** for Keycloak/Google/GitHub (`oidc.ts`, `/api/auth/oidc/callback`)
- Default redirect URI: `{origin}/api/auth/oidc/callback?provider=…` (override with env)
- Login shows `?error=` from failed SSO; state cookie validated before session issue
- Signed `frontend_session` httpOnly cookie; shell workspace labels from session
- Tests: `local-auth.test.ts`, `oidc.test.ts`, `LoginScreen.test.tsx` — pass

### ui_00_menu + destination unlock (prior)
- Menu shell + all destinations local preview — committed `2fbf4d4`

## Resume here

1. Dogfood `/login` → `/` dashboard → `/composer` in browser.
2. Next redesign screens: canvas (ui_04), agent detail (ui_05), activity (ui_06).
3. Wire composer recommend API + real instantiate command when contracts land.
4. Configure real OIDC env when IdP is available.
5. Unrelated untracked: `callgrok.bat`, `check_all_ui.bat`, `run_grok.bat`.

## Do not forget

- Constitution: Kiro + Claude Code only; no Gemini; no executing untrusted downloads.
- Architecture SoT: `structure.md`. Browser never owns authority.
- Video pack: 114 agents retained; spine-first activation order in `agent_implement_order_list.md`.
- `status.md` is stale relative to full platform code (still bootstrap-era wording).

## Validation checklist (when shipping)

- [ ] Focused tests for changed behavior
- [ ] `npm run sdd:check` (if SDD artifacts touched or gate required)
- [ ] `npm run sync:check` (if rules/skills/adapters changed)
- [ ] Frontend: `npm test` / typecheck / api:check as scope requires
- [ ] Backend: `pytest` as scope requires
- [ ] Update `status.md` after major work
