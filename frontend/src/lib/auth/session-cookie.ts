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

export function readSessionClaimsFromCookies(): SessionClaims | null {
  const store = cookies();
  const value = store.get(FRONTEND_SESSION_COOKIE)?.value;
  return decodeSessionCookie(value);
}

export function readPublicSessionFromCookies(): PublicSessionView {
  return toPublicSessionView(readSessionClaimsFromCookies());
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
