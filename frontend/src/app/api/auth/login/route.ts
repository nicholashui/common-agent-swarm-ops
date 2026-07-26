import { NextResponse } from "next/server";

import {
  createSessionClaims,
  verifyLocalPassword,
} from "../../../../lib/auth/local-auth";
import { buildSessionCookieOptions } from "../../../../lib/auth/session-cookie";

export const dynamic = "force-dynamic";

interface LoginBody {
  readonly email?: unknown;
  readonly password?: unknown;
  readonly rememberDevice?: unknown;
}

export async function POST(request: Request): Promise<Response> {
  let body: LoginBody;
  try {
    body = (await request.json()) as LoginBody;
  } catch {
    return NextResponse.json(
      { ok: false, error: "Invalid JSON body." },
      { status: 400 },
    );
  }

  const email = typeof body.email === "string" ? body.email : "";
  const password = typeof body.password === "string" ? body.password : "";
  const rememberDevice = body.rememberDevice === true;

  if (email.trim().length === 0 || password.length === 0) {
    return NextResponse.json(
      { ok: false, error: "Email and password are required." },
      { status: 400 },
    );
  }

  const user = verifyLocalPassword(email, password);
  if (!user) {
    return NextResponse.json(
      { ok: false, error: "Invalid email or password." },
      { status: 401 },
    );
  }

  const claims = createSessionClaims({
    mode: "user",
    email: user.email,
    workspaceLabel: user.workspaceLabel,
    rememberDevice,
  });
  const cookie = buildSessionCookieOptions(claims);
  const response = NextResponse.json({
    ok: true,
    mode: claims.mode,
    email: claims.email,
    workspaceLabel: claims.workspaceLabel,
    redirectTo: "/",
  });
  response.cookies.set(cookie);
  return response;
}
