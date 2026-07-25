import {
  GENERATED_OPENAPI_VERSION,
  type GeneratedJsonObject,
  type GeneratedJsonValue,
} from "../api/generated";

export interface AuthorizedProjectionRecord {
  readonly schemaVersion?: string;
  readonly projection: Readonly<Record<string, GeneratedJsonValue>>;
  readonly eventCursor: string | null;
}

export interface SessionStorageLike {
  getItem(key: string): string | null;
  setItem(key: string, value: string): void;
  removeItem(key: string): void;
}

export interface SessionSafeCacheAllowlistEntry {
  readonly key: string;
  readonly projectionFields: readonly string[];
}

export interface SessionSafeCacheOptions {
  readonly sessionVersion: string;
  readonly allowlist?: readonly SessionSafeCacheAllowlistEntry[];
  /** @deprecated Use field-level allowlist entries instead. */
  readonly allowedKeys?: readonly string[];
  readonly persistence?: SessionStorageLike;
  readonly schemaVersion?: string;
}

export interface SessionSafeCache {
  clearForSessionTransition(): void;
}

const CACHE_PREFIX = "casops:session-safe-cache";
const PROHIBITED_FIELD = /credential|token|password|secret|protected|raw|prompt|tool_(argument|result)|object.storage|provider.error|queue.name|trace|artifact.*content|content.*artifact/i;

/** Stores only explicitly allowlisted generated projection fields for one session. */
export class BrowserSessionSafeCache implements SessionSafeCache {
  private readonly memory = new Map<string, AuthorizedProjectionRecord>();
  private readonly policies: ReadonlyMap<string, SessionSafeCacheAllowlistEntry>;
  private readonly schemaVersion: string;

  public constructor(private readonly options: SessionSafeCacheOptions) {
    this.schemaVersion = options.schemaVersion ?? GENERATED_OPENAPI_VERSION;
    this.policies = createPolicies(options);
  }

  public read(key: string): AuthorizedProjectionRecord | null {
    const policy = this.policyFor(key);
    return this.memory.get(key) ?? this.readPersisted(key, policy);
  }

  public write(key: string, value: AuthorizedProjectionRecord): void {
    const policy = this.policyFor(key);
    const sanitized = sanitizeRecord(value, policy, this.schemaVersion);
    this.memory.set(key, sanitized);
    this.options.persistence?.setItem(this.storageKey(key), JSON.stringify(sanitized));
  }

  public clearForSessionTransition(): void {
    this.memory.clear();
    for (const key of this.policies.keys()) this.options.persistence?.removeItem(this.storageKey(key));
  }

  private readPersisted(key: string, policy: SessionSafeCacheAllowlistEntry): AuthorizedProjectionRecord | null {
    const serialized = this.options.persistence?.getItem(this.storageKey(key));
    if (serialized === null || serialized === undefined) return null;
    try {
      const parsed: unknown = JSON.parse(serialized);
      if (!isAuthorizedProjectionRecord(parsed) || parsed.schemaVersion !== this.schemaVersion) return null;
      const sanitized = sanitizeRecord(parsed, policy, this.schemaVersion);
      this.memory.set(key, sanitized);
      return sanitized;
    } catch {
      return null;
    }
  }

  private policyFor(key: string): SessionSafeCacheAllowlistEntry {
    const policy = this.policies.get(key);
    if (policy === undefined) throw new Error(`Session cache key is not allowlisted: ${key}`);
    return policy;
  }

  private storageKey(key: string): string {
    return `${CACHE_PREFIX}:${this.options.sessionVersion}:${key}`;
  }
}

function createPolicies(options: SessionSafeCacheOptions): ReadonlyMap<string, SessionSafeCacheAllowlistEntry> {
  if (options.sessionVersion.trim().length === 0) throw new Error("Session cache requires a session version.");
  if (options.allowlist !== undefined && options.allowedKeys !== undefined) throw new Error("Configure either cache allowlist entries or deprecated allowed keys, not both.");
  const entries = options.allowlist ?? (options.allowedKeys ?? []).map((key): SessionSafeCacheAllowlistEntry => ({ key, projectionFields: [] }));
  const policies = new Map<string, SessionSafeCacheAllowlistEntry>();
  for (const entry of entries) {
    if (entry.key.trim().length === 0 || policies.has(entry.key)) throw new Error("Session cache allowlist keys must be unique non-empty values.");
    for (const field of entry.projectionFields) {
      if (field.trim().length === 0 || PROHIBITED_FIELD.test(field)) throw new Error(`Session cache field is prohibited: ${field}`);
    }
    policies.set(entry.key, { key: entry.key, projectionFields: [...new Set(entry.projectionFields)] });
  }
  return policies;
}

function sanitizeRecord(
  value: AuthorizedProjectionRecord,
  policy: SessionSafeCacheAllowlistEntry,
  schemaVersion: string,
): AuthorizedProjectionRecord {
  const projection: Record<string, GeneratedJsonValue> = {};
  for (const field of policy.projectionFields) {
    const fieldValue = value.projection[field];
    if (Object.hasOwn(value.projection, field) && fieldValue !== undefined) projection[field] = fieldValue;
  }
  return { schemaVersion, projection: Object.freeze(projection), eventCursor: value.eventCursor };
}

function isAuthorizedProjectionRecord(value: unknown): value is AuthorizedProjectionRecord {
  if (!isGeneratedJsonObject(value)) return false;
  return typeof value.schemaVersion === "string"
    && isGeneratedJsonObject(value.projection)
    && (typeof value.eventCursor === "string" || value.eventCursor === null);
}

function isGeneratedJsonObject(value: unknown): value is GeneratedJsonObject {
  if (typeof value !== "object" || value === null || Array.isArray(value)) return false;
  return Object.values(value).every(isGeneratedJsonValue);
}

function isGeneratedJsonValue(value: unknown): value is GeneratedJsonValue {
  if (value === null || typeof value === "string" || typeof value === "number" || typeof value === "boolean") return true;
  if (Array.isArray(value)) return value.every(isGeneratedJsonValue);
  return isGeneratedJsonObject(value);
}
