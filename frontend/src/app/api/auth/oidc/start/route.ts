import { randomBytes } from "node:crypto";

import { NextResponse } from "next/server";

import {
  buildOidcAuthorizationUrl,
  encodeOidcStateCookie,
  isOidcProvider,
  resolveOidcProviderConfig,
} from "../../../../../lib/auth/oidc";

export const dynamic = "force-dynamic";

export async function GET(request: Request): Promise<Response> {
  const url = new URL(request.url);
  const providerParam = url.searchParams.get("provider");
  if (!isOidcProvider(providerParam)) {
    return NextResponse.json(
      { ok: false, error: "Unknown OIDC provider." },
      { status: 400 },
    );
  }

  const config = resolveOidcProviderConfig(providerParam, url.origin);
  if (!config) {
    return NextResponse.json(
      {
        ok: false,
        error: `${providerParam} SSO is not configured. Set CASOPS_* client id (and secret for callback) environment variables.`,
      },
      { status: 503 },
    );
  }

  const state = randomBytes(16).toString("base64url");
  const authorizationUrl = buildOidcAuthorizationUrl(config, state);
  const response = NextResponse.json({
    ok: true,
    authorizationUrl,
    provider: providerParam,
    redirectUri: config.redirectUri,
  });
  response.cookies.set({
    name: "casops_oidc_state",
    value: encodeOidcStateCookie(providerParam, state),
    httpOnly: true,
    sameSite: "lax",
    path: "/",
    secure: process.env.NODE_ENV === "production",
    maxAge: 600,
  });
  return response;
}
