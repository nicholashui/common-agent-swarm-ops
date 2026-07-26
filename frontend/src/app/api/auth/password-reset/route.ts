import { NextResponse } from "next/server";

import {
  consumePasswordResetToken,
  createPasswordResetToken,
  normalizeEmail,
} from "../../../../lib/auth/local-auth";

export const dynamic = "force-dynamic";

interface ResetRequestBody {
  readonly email?: unknown;
}

interface ResetConfirmBody {
  readonly token?: unknown;
  readonly password?: unknown;
}

export async function POST(request: Request): Promise<Response> {
  const url = new URL(request.url);
  const action = url.searchParams.get("action") ?? "request";

  let body: ResetRequestBody & ResetConfirmBody;
  try {
    body = (await request.json()) as ResetRequestBody & ResetConfirmBody;
  } catch {
    return NextResponse.json(
      { ok: false, error: "Invalid JSON body." },
      { status: 400 },
    );
  }

  if (action === "confirm") {
    const token = typeof body.token === "string" ? body.token : "";
    const password = typeof body.password === "string" ? body.password : "";
    if (!token || password.length < 4) {
      return NextResponse.json(
        { ok: false, error: "Reset token and a password of at least 4 characters are required." },
        { status: 400 },
      );
    }
    const accepted = consumePasswordResetToken(token, password);
    if (!accepted) {
      return NextResponse.json(
        { ok: false, error: "Reset token is invalid or expired." },
        { status: 400 },
      );
    }
    return NextResponse.json({
      ok: true,
      message: "Password updated. Sign in with your new password.",
    });
  }

  const email = typeof body.email === "string" ? normalizeEmail(body.email) : "";
  if (!email) {
    return NextResponse.json(
      { ok: false, error: "Email is required." },
      { status: 400 },
    );
  }

  // Always return the same public message (no user enumeration).
  const created = createPasswordResetToken(email);
  const payload: {
    ok: true;
    message: string;
    devResetToken?: string;
  } = {
    ok: true,
    message:
      "If that account exists, password reset instructions were issued for local session entry.",
  };
  if (created && process.env.NODE_ENV !== "production") {
    payload.devResetToken = created.token;
  }
  return NextResponse.json(payload);
}
