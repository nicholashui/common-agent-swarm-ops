/**
 * Browser-local workspace files for Plan (Composer) and Execute (Canvas).
 * Process-local only (localStorage when available) — not Host production media.
 */

export type WorkspaceSurface = "composer" | "canvas";

export type WorkspaceFileRecord = {
  readonly id: string;
  readonly name: string;
  readonly updatedAt: string;
  readonly payload: Readonly<Record<string, unknown>>;
};

export type WorkspaceFileStore = {
  readonly read: (key: string) => string | null;
  readonly write: (key: string, value: string) => void;
};

const STORAGE_PREFIX = "casops.workspace.files.v1.";

export function storageKeyFor(surface: WorkspaceSurface): string {
  return `${STORAGE_PREFIX}${surface}`;
}

export function memoryFileStore(
  seed: Record<string, string> = {},
): WorkspaceFileStore {
  const map = new Map(Object.entries(seed));
  return {
    read: (key) => map.get(key) ?? null,
    write: (key, value) => {
      map.set(key, value);
    },
  };
}

export function browserFileStore(): WorkspaceFileStore | null {
  if (typeof window === "undefined" || !window.localStorage) {
    return null;
  }
  return {
    read: (key) => {
      try {
        return window.localStorage.getItem(key);
      } catch {
        return null;
      }
    },
    write: (key, value) => {
      try {
        window.localStorage.setItem(key, value);
      } catch {
        /* quota / private mode — ignore */
      }
    },
  };
}

function nowIso(): string {
  return new Date().toISOString();
}

function newId(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return `wf_${crypto.randomUUID().replace(/-/g, "").slice(0, 16)}`;
  }
  return `wf_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 8)}`;
}

export function listWorkspaceFiles(
  surface: WorkspaceSurface,
  store: WorkspaceFileStore,
): WorkspaceFileRecord[] {
  const raw = store.read(storageKeyFor(surface));
  if (!raw) return [];
  try {
    const parsed = JSON.parse(raw) as { files?: unknown };
    if (!Array.isArray(parsed.files)) return [];
    return parsed.files
      .filter((row): row is WorkspaceFileRecord => {
        if (!row || typeof row !== "object") return false;
        const r = row as Record<string, unknown>;
        return (
          typeof r.id === "string" &&
          typeof r.name === "string" &&
          typeof r.updatedAt === "string" &&
          r.payload !== null &&
          typeof r.payload === "object"
        );
      })
      .map((row) => ({
        id: row.id,
        name: row.name,
        updatedAt: row.updatedAt,
        payload: { ...(row.payload as Record<string, unknown>) },
      }))
      .sort((a, b) => b.updatedAt.localeCompare(a.updatedAt));
  } catch {
    return [];
  }
}

function writeAll(
  surface: WorkspaceSurface,
  store: WorkspaceFileStore,
  files: readonly WorkspaceFileRecord[],
): void {
  store.write(
    storageKeyFor(surface),
    JSON.stringify({ files }, null, 0),
  );
}

export function getWorkspaceFile(
  surface: WorkspaceSurface,
  store: WorkspaceFileStore,
  id: string,
): WorkspaceFileRecord | null {
  return listWorkspaceFiles(surface, store).find((f) => f.id === id) ?? null;
}

export function saveWorkspaceFile(
  surface: WorkspaceSurface,
  store: WorkspaceFileStore,
  input: {
    readonly id?: string | null;
    readonly name: string;
    readonly payload: Readonly<Record<string, unknown>>;
  },
): WorkspaceFileRecord {
  const name = input.name.trim() || "Untitled";
  const files = listWorkspaceFiles(surface, store);
  const existingId = (input.id || "").trim();
  const idx = existingId
    ? files.findIndex((f) => f.id === existingId)
    : -1;
  const record: WorkspaceFileRecord = {
    id: idx >= 0 ? files[idx]!.id : newId(),
    name,
    updatedAt: nowIso(),
    payload: { ...input.payload },
  };
  const next =
    idx >= 0
      ? files.map((f, i) => (i === idx ? record : f))
      : [record, ...files];
  writeAll(surface, store, next);
  return record;
}

export function createWorkspaceFile(
  surface: WorkspaceSurface,
  store: WorkspaceFileStore,
  input: {
    readonly name?: string;
    readonly payload?: Readonly<Record<string, unknown>>;
  } = {},
): WorkspaceFileRecord {
  return saveWorkspaceFile(surface, store, {
    id: null,
    name: input.name?.trim() || "Untitled",
    payload: input.payload ?? {},
  });
}

export function deleteWorkspaceFile(
  surface: WorkspaceSurface,
  store: WorkspaceFileStore,
  id: string,
): boolean {
  const files = listWorkspaceFiles(surface, store);
  const next = files.filter((f) => f.id !== id);
  if (next.length === files.length) return false;
  writeAll(surface, store, next);
  return true;
}

export function stringField(
  payload: Readonly<Record<string, unknown>>,
  key: string,
  fallback = "",
): string {
  const v = payload[key];
  return typeof v === "string" ? v : fallback;
}
