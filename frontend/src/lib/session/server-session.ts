import "server-only";

import { createHash } from "node:crypto";
import { cookies } from "next/headers";

import {
  FRONTEND_SESSION_COOKIE,
  HOST_SESSION_COOKIE,
  decodeSessionCookie,
  toPublicSessionView,
  type PublicSessionView,
  type SessionClaims,
  type SessionMode,
} from "../auth/local-auth";

export interface ServerSessionSignal {
  readonly state: "anonymous" | "authenticated";
  readonly version: string;
  readonly mode: SessionMode | null;
  readonly email: string | null;
  readonly workspaceLabel: string | null;
  readonly demo: boolean;
}

const SESSION_COOKIE_NAMES = [HOST_SESSION_COOKIE, FRONTEND_SESSION_COOKIE] as const;

type CookieReader = {
  get(name: string): { value: string } | undefined;
};

/**
 * Next.js 15+/16: cookies() is async (Promise<ReadonlyRequestCookies>).
 * Always await + validate so .get is never called on a Promise.
 */
async function resolveCookieStore(): Promise<CookieReader> {
  const store = await cookies();
  if (store && typeof store.get === "function") {
    return store as CookieReader;
  }
  throw new Error(
    "next/headers cookies() did not resolve to a store with .get(); stop the Next.js process, delete frontend/.next, and restart npm run dev.",
  );
}

export async function getServerSessionSignal(): Promise<ServerSessionSignal> {
  const claims = await readSessionClaims();
  if (!claims) {
    return {
      state: "anonymous",
      version: "anonymous",
      mode: null,
      email: null,
      workspaceLabel: null,
      demo: false,
    };
  }
  const publicView = toPublicSessionView(claims);
  return {
    state: "authenticated",
    version: hashSessionVersion(claims.sid),
    mode: publicView.mode,
    email: publicView.email,
    workspaceLabel: publicView.workspaceLabel,
    demo: publicView.demo,
  };
}

export async function getPublicSessionView(): Promise<PublicSessionView> {
  return toPublicSessionView(await readSessionClaims());
}

async function readSessionClaims(): Promise<SessionClaims | null> {
  const cookieStore = await resolveCookieStore();
  for (const name of SESSION_COOKIE_NAMES) {
    const value = cookieStore.get(name)?.value;
    const claims = decodeSessionCookie(value);
    if (claims) return claims;
  }
  return null;
}

function hashSessionVersion(sessionValue: string): string {
  return createHash("sha256").update(sessionValue).digest("base64url");
}
