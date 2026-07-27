import { createHash, createHmac, randomBytes, timingSafeEqual } from "node:crypto";

export const FRONTEND_SESSION_COOKIE = "frontend_session";
export const HOST_SESSION_COOKIE = "__Host-casops-session";

export type SessionMode = "user" | "demo";

export interface LocalUserRecord {
  readonly email: string;
  readonly passwordHash: string;
  readonly workspaceLabel: string;
}

export interface SessionClaims {
  readonly v: 1;
  readonly sid: string;
  readonly mode: SessionMode;
  readonly email: string;
  readonly workspaceLabel: string;
  readonly exp: number;
  readonly iat: number;
}

export interface PublicSessionView {
  readonly authenticated: boolean;
  readonly mode: SessionMode | null;
  readonly email: string | null;
  readonly workspaceLabel: string | null;
  readonly demo: boolean;
}

export interface PasswordResetRecord {
  readonly email: string;
  readonly tokenHash: string;
  readonly exp: number;
}

/**
 * Built-in local accounts (dev / offline session entry).
 * Format: [email, password, workspaceLabel]
 * - Admin: Nicholas Hui (primary operator account)
 * - demo / ops retained for existing fixtures and demo entry
 */
const DEFAULT_LOCAL_USERS: ReadonlyArray<readonly [string, string, string]> = [
  ["nicholas.hui@local", "NicholasAdmin1!", "Admin · Nicholas Hui"],
  ["demo@local", "demo", "Demo workspace"],
  ["ops@local", "ops", "Local ops workspace"],
];

/** In-process password overrides after local resets (never secrets in cookies). */
const passwordOverrides = new Map<string, string>();
const resetTokens = new Map<string, PasswordResetRecord>();

export function normalizeEmail(email: string): string {
  return email.trim().toLowerCase();
}

export function sessionSecret(): string {
  const configured = process.env.CASOPS_SESSION_SECRET?.trim();
  if (configured && configured.length >= 16) return configured;
  return "casops-local-dev-session-secret";
}

export function hashPassword(password: string, secret = sessionSecret()): string {
  return createHmac("sha256", secret).update(password, "utf8").digest("base64url");
}

function parseConfiguredUsers(): readonly LocalUserRecord[] {
  const raw = process.env.CASOPS_LOCAL_AUTH_USERS?.trim();
  if (!raw) {
    return DEFAULT_LOCAL_USERS.map(([email, password, workspaceLabel]) => ({
      email: normalizeEmail(email),
      passwordHash: hashPassword(password),
      workspaceLabel,
    }));
  }
  return raw.split(",").flatMap((entry): readonly LocalUserRecord[] => {
    const [emailPart, passwordPart, workspacePart] = entry.split(":");
    if (!emailPart || !passwordPart) return [];
    return [
      {
        email: normalizeEmail(emailPart),
        passwordHash: hashPassword(passwordPart),
        workspaceLabel: workspacePart?.trim() || "Local workspace",
      },
    ];
  });
}

export function listLocalUsers(): readonly LocalUserRecord[] {
  const configured = parseConfiguredUsers();
  return configured.map((user) => {
    const override = passwordOverrides.get(user.email);
    if (!override) return user;
    return { ...user, passwordHash: hashPassword(override) };
  });
}

export function findLocalUser(email: string): LocalUserRecord | undefined {
  const normalized = normalizeEmail(email);
  return listLocalUsers().find((user) => user.email === normalized);
}

export function verifyLocalPassword(email: string, password: string): LocalUserRecord | null {
  const user = findLocalUser(email);
  if (!user) return null;
  const candidate = hashPassword(password);
  const expected = Buffer.from(user.passwordHash);
  const actual = Buffer.from(candidate);
  if (expected.length !== actual.length) return null;
  if (!timingSafeEqual(expected, actual)) return null;
  return user;
}

export function createSessionClaims(
  input: {
    readonly mode: SessionMode;
    readonly email: string;
    readonly workspaceLabel: string;
    readonly rememberDevice?: boolean;
  },
  nowMs = Date.now(),
): SessionClaims {
  const ttlMs = input.rememberDevice ? 7 * 24 * 60 * 60 * 1000 : 12 * 60 * 60 * 1000;
  return {
    v: 1,
    sid: randomBytes(16).toString("base64url"),
    mode: input.mode,
    email: normalizeEmail(input.email),
    workspaceLabel: input.workspaceLabel,
    iat: Math.floor(nowMs / 1000),
    exp: Math.floor((nowMs + ttlMs) / 1000),
  };
}

export function createDemoSessionClaims(nowMs = Date.now()): SessionClaims {
  return createSessionClaims(
    {
      mode: "demo",
      email: "demo@local",
      workspaceLabel: "Demo workspace",
      rememberDevice: false,
    },
    nowMs,
  );
}

function signPayload(payload: string, secret = sessionSecret()): string {
  return createHmac("sha256", secret).update(payload, "utf8").digest("base64url");
}

export function encodeSessionCookie(claims: SessionClaims, secret = sessionSecret()): string {
  const payload = Buffer.from(JSON.stringify(claims), "utf8").toString("base64url");
  return `${payload}.${signPayload(payload, secret)}`;
}

export function decodeSessionCookie(
  value: string | undefined | null,
  secret = sessionSecret(),
  nowMs = Date.now(),
): SessionClaims | null {
  if (!value) return null;
  const [payload, signature] = value.split(".");
  if (!payload || !signature) return null;
  const expected = signPayload(payload, secret);
  const left = Buffer.from(signature);
  const right = Buffer.from(expected);
  if (left.length !== right.length || !timingSafeEqual(left, right)) return null;
  try {
    const parsed: unknown = JSON.parse(Buffer.from(payload, "base64url").toString("utf8"));
    if (!isSessionClaims(parsed)) return null;
    if (parsed.exp * 1000 <= nowMs) return null;
    return parsed;
  } catch {
    return null;
  }
}

function isSessionClaims(value: unknown): value is SessionClaims {
  if (typeof value !== "object" || value === null) return false;
  const record = value as Record<string, unknown>;
  return (
    record.v === 1 &&
    typeof record.sid === "string" &&
    (record.mode === "user" || record.mode === "demo") &&
    typeof record.email === "string" &&
    typeof record.workspaceLabel === "string" &&
    typeof record.exp === "number" &&
    typeof record.iat === "number"
  );
}

export function toPublicSessionView(claims: SessionClaims | null): PublicSessionView {
  if (!claims) {
    return {
      authenticated: false,
      mode: null,
      email: null,
      workspaceLabel: null,
      demo: false,
    };
  }
  return {
    authenticated: true,
    mode: claims.mode,
    email: claims.email,
    workspaceLabel: claims.workspaceLabel,
    demo: claims.mode === "demo",
  };
}

export function createPasswordResetToken(
  email: string,
  nowMs = Date.now(),
): { readonly token: string; readonly exp: number } | null {
  const user = findLocalUser(email);
  if (!user) return null;
  const token = randomBytes(24).toString("base64url");
  const exp = nowMs + 30 * 60 * 1000;
  resetTokens.set(token, {
    email: user.email,
    tokenHash: createHash("sha256").update(token).digest("hex"),
    exp,
  });
  return { token, exp };
}

export function consumePasswordResetToken(
  token: string,
  newPassword: string,
  nowMs = Date.now(),
): boolean {
  const record = resetTokens.get(token);
  resetTokens.delete(token);
  if (!record || record.exp <= nowMs) return false;
  if (newPassword.trim().length < 4) return false;
  passwordOverrides.set(record.email, newPassword);
  return true;
}

export function clearLocalAuthStateForTests(): void {
  passwordOverrides.clear();
  resetTokens.clear();
}

export function sessionCookieMaxAgeSeconds(claims: SessionClaims): number {
  return Math.max(60, claims.exp - claims.iat);
}

export function demoSeedSummary(): readonly string[] {
  return [
    "Common Registry preview agents",
    "Sample Trading Swarm pattern",
    "Content Pipeline pattern",
    "DSE Tutor pattern",
    "Activity and monitoring local projections",
  ];
}
