import "server-only";

import { createHash } from "node:crypto";
import { cookies } from "next/headers";

export interface ServerSessionSignal {
  readonly state: "anonymous" | "authenticated";
  readonly version: string;
}

const SESSION_COOKIE_NAMES = ["__Host-casops-session", "frontend_session"] as const;

export function getServerSessionSignal(): ServerSessionSignal {
  const cookieStore = cookies();
  const sessionValue = SESSION_COOKIE_NAMES
    .map((name: string): string | undefined => cookieStore.get(name)?.value)
    .find((value: string | undefined): value is string => value !== undefined && value.length > 0);
  if (sessionValue === undefined) return { state: "anonymous", version: "anonymous" };
  return { state: "authenticated", version: hashSessionVersion(sessionValue) };
}

function hashSessionVersion(sessionValue: string): string {
  return createHash("sha256").update(sessionValue).digest("base64url");
}
