# Login — functional specification

**Route:** `/login`  
**Shell:** Public (no `AppShell`)  
**Purpose:** Identity-only session entry for local and optional OIDC flows.

---

## 1. Actors

| Actor | Capability |
|-------|------------|
| Anonymous visitor | Sign in, demo entry, password reset request |
| Authenticated user | May be redirected to `/` when session probe succeeds |

## 2. Functional requirements

### FR-LOGIN-001 Public access
- `/login` SHALL be reachable without an authenticated session.

### FR-LOGIN-002 Credential fields
- Screen SHALL provide email and password inputs with labels and accessible ids.
- Password field SHALL support show/hide when control is present.

### FR-LOGIN-003 Sign-in submission
- Submit SHALL POST JSON to same-origin `/api/auth/login` with email, password, rememberDevice.
- On success, session cookie SHALL be set and client SHALL navigate to `redirectTo` (default `/`).
- On 401/error, user-visible error SHALL display; password SHALL NOT be echoed into storage.

### FR-LOGIN-004 Remember device
- When checked, session TTL SHALL use long-lived claims policy from server auth module.

### FR-LOGIN-005 Demo entry
- Demo control SHALL POST `/api/auth/demo` and establish demo-mode session claims when available.

### FR-LOGIN-006 Password reset
- Reset flow SHALL use `/api/auth/password-reset` for token issue/consume.
- Reset SHALL only affect configured local users.

### FR-LOGIN-007 Locale preference
- Locale toggle SHALL persist to sessionStorage key from projection (not credentials).

### FR-LOGIN-008 SSO affordances
- SSO buttons MAY render; when unconfigured they SHALL fail closed with honest messaging.

### FR-LOGIN-009 Built-in local users (dev)
- System SHALL accept at least:
  - `nicholas.hui@local` / `NicholasAdmin1!` → workspace `Admin · Nicholas Hui`
  - `demo@local` / `demo`
  - `ops@local` / `ops`
- Users MAY be overridden via `CASOPS_LOCAL_AUTH_USERS`.

### FR-LOGIN-010 Help docs
- Login docs live under `/docs/login/*` for full-page viewer; shell help panel is not mounted on login.

## 3. Security requirements

| ID | Requirement |
|----|-------------|
| SEC-LOGIN-001 | No password in localStorage/sessionStorage. |
| SEC-LOGIN-002 | Session cookie must be signed HMAC payload. |
| SEC-LOGIN-003 | Invalid credentials return 401 without user enumeration beyond generic error. |

## 4. Out of scope

- Creating remote IdP users.
- Production secret management UI.
