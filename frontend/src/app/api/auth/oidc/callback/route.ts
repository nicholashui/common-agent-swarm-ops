import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { buildSessionCookieOptions } from "../../../../../lib/auth/session-cookie";
import {
  exchangeOidcAuthorizationCode,
  fetchOidcIdentity,
  isOidcProvider,
  loginErrorRedirect,
  parseOidcStateCookie,
  resolveOidcProviderConfig,
  sessionClaimsFromOidcIdentity,
} from "../../../../../lib/auth/oidc";

export const dynamic = "force-dynamic";

function clearOidcStateCookie(response: NextResponse): void {
  response.cookies.set({
    name: "casops_oidc_state",
    value: "",
    httpOnly: true,
    sameSite: "lax",
    path: "/",
    secure: process.env.NODE_ENV === "production",
    maxAge: 0,
  });
}

export async function GET(request: Request): Promise<Response> {
  const url = new URL(request.url);
  const origin = url.origin;
  const providerParam = url.searchParams.get("provider");
  const code = url.searchParams.get("code");
  const returnedState = url.searchParams.get("state");
  const providerError = url.searchParams.get("error");
  const providerErrorDescription = url.searchParams.get("error_description");

  if (providerError) {
    const response = NextResponse.redirect(
      loginErrorRedirect(
        origin,
        providerErrorDescription || providerError || "SSO provider returned an error.",
      ),
    );
    clearOidcStateCookie(response);
    return response;
  }

  if (!isOidcProvider(providerParam)) {
    return NextResponse.redirect(
      loginErrorRedirect(origin, "Unknown OIDC provider in callback."),
    );
  }

  if (!code || !returnedState) {
    return NextResponse.redirect(
      loginErrorRedirect(origin, "SSO callback is missing code or state."),
    );
  }

  const cookieStore = await cookies();
  const stored = parseOidcStateCookie(cookieStore.get("casops_oidc_state")?.value);
  if (!stored || stored.provider !== providerParam || stored.state !== returnedState) {
    const response = NextResponse.redirect(
      loginErrorRedirect(origin, "SSO state validation failed. Retry sign-in."),
    );
    clearOidcStateCookie(response);
    return response;
  }

  const config = resolveOidcProviderConfig(providerParam, origin);
  if (!config) {
    const response = NextResponse.redirect(
      loginErrorRedirect(origin, `${providerParam} SSO is not configured.`),
    );
    clearOidcStateCookie(response);
    return response;
  }

  const tokenResult = await exchangeOidcAuthorizationCode(config, code);
  if (!tokenResult.ok) {
    const response = NextResponse.redirect(
      loginErrorRedirect(origin, tokenResult.error),
    );
    clearOidcStateCookie(response);
    return response;
  }

  const identityResult = await fetchOidcIdentity(
    config,
    tokenResult.accessToken,
    tokenResult.idToken,
  );
  if (!identityResult.ok) {
    const response = NextResponse.redirect(
      loginErrorRedirect(origin, identityResult.error),
    );
    clearOidcStateCookie(response);
    return response;
  }

  const claims = sessionClaimsFromOidcIdentity(identityResult.identity, true);
  const response = NextResponse.redirect(new URL("/", origin));
  response.cookies.set(buildSessionCookieOptions(claims));
  clearOidcStateCookie(response);
  return response;
}
