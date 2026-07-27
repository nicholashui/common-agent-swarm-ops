# Login — step-by-step user guide

**Screen:** Login  
**Route:** `/login`  
**Who it’s for:** Anyone opening the console (public entry).

---

## 1. Open Login

1. Go to `/login`, or open any protected screen while signed out (you will be redirected here).
2. Confirm you see the product name, title, email and password fields.

---

## 2. Choose language (optional)

1. Use the language control if shown (e.g. English / 繁體中文).
2. Preference is stored in session storage only (not credentials).

---

## 3. Sign in with a local account

1. Enter **Email** (login identifier).
2. Enter **Password**.
3. Optionally check **Remember this device** (longer session cookie TTL).
4. Click **Sign in**.
5. On success you are redirected to the Dashboard (`/`).
6. On failure, read the error message, correct credentials, and try again.

### Built-in local accounts (development)

| Role / label | Email | Password |
|--------------|--------|----------|
| Admin · Nicholas Hui | `nicholas.hui@local` | `NicholasAdmin1!` |
| Demo | `demo@local` | `demo` |
| Ops | `ops@local` | `ops` |

> Passwords are for local/dev session entry only. Do not reuse production secrets.

---

## 4. Demo workspace (optional)

1. Click **Try Demo Workspace** (if shown).
2. A demo session is issued; you land on the dashboard with a demo banner.
3. Demo is still a signed session; it does not enable production media activation.

---

## 5. Forgot password (local reset)

1. Click **Forgot password?**.
2. Enter the account email and request a reset token (local flow).
3. Paste the issued token and choose a new password.
4. Confirm reset, then sign in with the new password.

---

## 6. SSO buttons

1. Keycloak / Google / GitHub buttons may appear for host-configured OIDC.
2. If SSO is not configured, the UI fails closed with an honest unavailable message.
3. Do not expect SSO to work without deployment configuration.

---

## 7. After login

1. You must stay authenticated to open shell screens (Dashboard, Registry, etc.).
2. To leave the session, use logout when available (or clear the session cookie).
3. Opening `/login` while already signed in may redirect you back to `/`.

---

## 8. Safety notes

- Credentials are posted only to same-origin `/api/auth/*` routes.
- The browser never stores passwords in localStorage.
- Login is identity/session entry only; it does not grant invented host mutations.
