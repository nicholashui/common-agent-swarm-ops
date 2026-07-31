import { NextResponse } from "next/server";

import { readPublicSessionFromCookies } from "../../../../lib/auth/session-cookie";

export const dynamic = "force-dynamic";

export async function GET(): Promise<Response> {
  return NextResponse.json({
    ok: true,
    session: await readPublicSessionFromCookies(),
  });
}
