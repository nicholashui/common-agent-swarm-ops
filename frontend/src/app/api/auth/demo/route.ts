import { NextResponse } from "next/server";

import {
  createDemoSessionClaims,
  demoSeedSummary,
} from "../../../../lib/auth/local-auth";
import { buildSessionCookieOptions } from "../../../../lib/auth/session-cookie";

export const dynamic = "force-dynamic";

export async function POST(): Promise<Response> {
  const claims = createDemoSessionClaims();
  const cookie = buildSessionCookieOptions(claims);
  const response = NextResponse.json({
    ok: true,
    mode: claims.mode,
    email: claims.email,
    workspaceLabel: claims.workspaceLabel,
    seed: demoSeedSummary(),
    redirectTo: "/",
    message: "Preparing Common Registry & sample swarms...",
  });
  response.cookies.set(cookie);
  return response;
}
