import { cookies } from "next/headers";

import {
  FRONTEND_SESSION_COOKIE,
  decodeSessionCookie,
  encodeSessionCookie,
  sessionCookieMaxAgeSeconds,
  toPublicSessionView,
  type PublicSessionView,
  type SessionClaims,
} from "./local-auth";

export async function readSessionClaimsFromCookies(): Promise<SessionClaims | null> {
  // Next.js 15+/16: cookies() is async (Promise store).
  const store = await cookies();
  if (!store || typeof store.get !== "function") {
    throw new Error(
      "next/headers cookies() did not resolve to a store with .get(); delete frontend/.next and restart npm run dev.",
    );
  }
  const value = store.get(FRONTEND_SESSION_COOKIE)?.value;
  return decodeSessionCookie(value);
}

export async function readPublicSessionFromCookies(): Promise<PublicSessionView> {
  return toPublicSessionView(await readSessionClaimsFromCookies());
}

export function buildSessionCookieOptions(claims: SessionClaims): {
  readonly name: string;
  readonly value: string;
  readonly httpOnly: true;
  readonly sameSite: "lax";
  readonly path: "/";
  readonly secure: boolean;
  readonly maxAge: number;
} {
  return {
    name: FRONTEND_SESSION_COOKIE,
    value: encodeSessionCookie(claims),
    httpOnly: true,
    sameSite: "lax",
    path: "/",
    secure: process.env.NODE_ENV === "production",
    maxAge: sessionCookieMaxAgeSeconds(claims),
  };
}

export function buildClearedSessionCookieOptions(): {
  readonly name: string;
  readonly value: string;
  readonly httpOnly: true;
  readonly sameSite: "lax";
  readonly path: "/";
  readonly secure: boolean;
  readonly maxAge: number;
} {
  return {
    name: FRONTEND_SESSION_COOKIE,
    value: "",
    httpOnly: true,
    sameSite: "lax",
    path: "/",
    secure: process.env.NODE_ENV === "production",
    maxAge: 0,
  };
}
