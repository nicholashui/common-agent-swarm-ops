# Login — test scenarios

**Route:** `/login`

---

## TS-LOGIN-001 Public page loads (P0)

| Given | When | Then |
|-------|------|------|
| No session | Open `/login` | Login form renders; no redirect loop |

## TS-LOGIN-002 Valid admin login (P0)

| Given | When | Then |
|-------|------|------|
| Built-in admin user | Submit nicholas.hui@local / NicholasAdmin1! | 200/ok; cookie set; land on `/` |

## TS-LOGIN-003 Invalid password (P0)

| Given | When | Then |
|-------|------|------|
| Known email | Wrong password | Error shown; remain on login; no session |

## TS-LOGIN-004 Empty fields (P1)

| Given | When | Then |
|-------|------|------|
| Empty email or password | Submit | Client validation or 400; no session |

## TS-LOGIN-005 Demo session (P1)

| Given | When | Then |
|-------|------|------|
| Demo route available | Click demo | Demo session; dashboard with demo affordance |

## TS-LOGIN-006 Remember device (P2)

| Given | When | Then |
|-------|------|------|
| Remember checked | Login success | Cookie/session uses long TTL policy |

## TS-LOGIN-007 Password reset happy path (P1)

| Given | When | Then |
|-------|------|------|
| demo@local | Request token → consume with new password | New password verifies; old fails |

## TS-LOGIN-008 Already authenticated (P2)

| Given | When | Then |
|-------|------|------|
| Valid session | Open `/login` | Client session probe may redirect to `/` |

## TS-LOGIN-009 No secrets persisted (P0)

| Given | When | Then |
|-------|------|------|
| After failed/successful login | Inspect storage | No password strings in local/session storage |
