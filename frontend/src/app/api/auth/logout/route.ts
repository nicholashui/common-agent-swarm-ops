import { NextResponse } from "next/server";

import { buildClearedSessionCookieOptions } from "../../../../lib/auth/session-cookie";

export const dynamic = "force-dynamic";

export async function POST(): Promise<Response> {
  const response = NextResponse.json({
    ok: true,
    redirectTo: "/login",
  });
  response.cookies.set(buildClearedSessionCookieOptions());
  return response;
}
