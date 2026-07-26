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

export function getServerSessionSignal(): ServerSessionSignal {
  const claims = readSessionClaims();
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

export function getPublicSessionView(): PublicSessionView {
  return toPublicSessionView(readSessionClaims());
}

function readSessionClaims(): SessionClaims | null {
  const cookieStore = cookies();
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
