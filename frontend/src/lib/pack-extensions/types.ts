/**
 * Domain-neutral pack UI extension contract (adoption_redesign §7 UI).
 *
 * The common frontend supplies only authenticated shell, generic projections,
 * accessibility, audit visibility, and extension slots. Domain terminology
 * (including video) arrives only via pack-owned extension metadata returned by
 * the host — never as hard-coded host branches.
 */

export interface PackUiExtensionPanel {
  readonly panelId: string;
  readonly title: string;
  /** Inert, redacted summary text only. */
  readonly summary?: string;
  /** Opaque server-issued reference identifiers for deep links. */
  readonly referenceIds?: readonly string[];
}

/**
 * Optional UI extension metadata from a domain pack manifest projection.
 * `domainId` is a pack value (e.g. "video", "synthetic-a"); it is never a
 * host code branch selector.
 */
export interface PackUiExtensionManifest {
  readonly domainId: string;
  readonly packVersion: string;
  readonly slotId: string;
  readonly title: string;
  readonly panels?: readonly PackUiExtensionPanel[];
}

export type PackExtensionSlotId =
  | "shell.nav"
  | "shell.banner"
  | "registry.detail"
  | "canvas.inspector"
  | "knowledge.panel"
  | "operations.panel";

export function isPackUiExtensionManifest(value: unknown): value is PackUiExtensionManifest {
  if (typeof value !== "object" || value === null || Array.isArray(value)) return false;
  const record = value as Record<string, unknown>;
  return typeof record.domainId === "string"
    && record.domainId.trim().length > 0
    && typeof record.packVersion === "string"
    && record.packVersion.trim().length > 0
    && typeof record.slotId === "string"
    && record.slotId.trim().length > 0
    && typeof record.title === "string"
    && record.title.trim().length > 0;
}

/** Filters to extensions for one slot; host remains domain-neutral. */
export function extensionsForSlot(
  extensions: readonly PackUiExtensionManifest[],
  slotId: string,
): readonly PackUiExtensionManifest[] {
  return extensions.filter((extension) => extension.slotId === slotId);
}
