/**
 * Same-origin session logout via Next BFF.
 * Clears the session cookie; does not invent Host authority.
 */

export type LogoutResult =
  | { readonly ok: true; readonly redirectTo: string }
  | { readonly ok: false; readonly message: string };

/**
 * POST /api/auth/logout with credentials. Caller should navigate to redirectTo.
 */
export async function logoutSession(
  fetchImpl: typeof fetch = globalThis.fetch.bind(globalThis),
): Promise<LogoutResult> {
  try {
    const response = await fetchImpl("/api/auth/logout", {
      method: "POST",
      credentials: "same-origin",
      headers: { accept: "application/json" },
    });
    if (!response.ok) {
      return { ok: false, message: "Could not sign out. Try again." };
    }
    let redirectTo = "/login";
    try {
      const body = (await response.json()) as { readonly redirectTo?: string };
      if (typeof body.redirectTo === "string" && body.redirectTo.startsWith("/")) {
        redirectTo = body.redirectTo;
      }
    } catch {
      // Default redirect is fine if body is empty.
    }
    return { ok: true, redirectTo };
  } catch {
    return { ok: false, message: "Could not sign out. Network error." };
  }
}
