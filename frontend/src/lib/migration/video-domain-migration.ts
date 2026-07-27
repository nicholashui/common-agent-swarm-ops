/**
 * Frontend claim surface for docs/migration_redesign/migration_redesign.md.
 *
 * Migration is pack/backend work under business/video/. The browser must not:
 * - claim the video domain is self-contained before standalone evidence,
 * - treat pack_spine as blueprint realization,
 * - imply production activation, live providers, credentials, or network paths,
 * - claim workflow maturity from agent count, catalog, mapping prose, or a stub graph.
 *
 * Migration document status is COMPLETE with evidence; frontend reports
 * self-contained offline pack while remaining fail-closed on production activation.
 */

export type MigrationDocumentStatus = "proposed" | "in_progress" | "complete";

export type PackMaturityState =
  | "cataloged"
  | "mapped"
  | "graph_validated"
  | "not_mature";

export type PackActivationState = "registered" | "non_active" | "active";

/** As-built claim constants aligned to migration_redesign measured state. */
export interface VideoDomainMigrationClaim {
  readonly documentStatus: MigrationDocumentStatus;
  readonly selfContained: boolean;
  readonly agentInventoryCount: 114;
  /** Sole current safe stub graph id — not a blueprint family realization. */
  readonly soleSafeStubGraphId: "pack_spine";
  readonly packSpineIsBlueprintRealization: false;
  readonly defaultMaturityState: PackMaturityState;
  readonly defaultActivationState: Exclude<PackActivationState, "active">;
  readonly productionActivationImplied: false;
  readonly liveProvidersEnabled: false;
  readonly networkAccessEnabled: false;
  readonly credentialsConfigured: false;
  readonly disclaimer: string;
  readonly bannerLabel: string;
}

/**
 * Normative browser claim until migration_redesign exit gates pass and the
 * document status becomes COMPLETE in the same change set as evidence.
 */
export const VIDEO_DOMAIN_MIGRATION_CLAIM: VideoDomainMigrationClaim = {
  documentStatus: "complete",
  selfContained: true,
  agentInventoryCount: 114,
  soleSafeStubGraphId: "pack_spine",
  packSpineIsBlueprintRealization: false,
  defaultMaturityState: "cataloged",
  defaultActivationState: "registered",
  // Browser never implies silent production; host requires env + credentials.
  productionActivationImplied: false,
  liveProvidersEnabled: false,
  networkAccessEnabled: false,
  credentialsConfigured: false,
  bannerLabel:
    "Video domain: COMPLETE pack · production media host-ready (env + API keys required)",
  disclaimer:
    "Pack is self-contained (migration_redesign COMPLETE). "
    + "Host registers live media adapters media.sora/veo/runway/elevenlabs; "
    + "live calls need CASOPS_VIDEO_PRODUCTION_ENABLED, CASOPS_VIDEO_MEDIA_NETWORK, and provider keys. "
    + "workflows/pack_spine.json remains the sole safe stub (not blueprint realization). "
    + "The browser never stores credentials or silently activates production.",
};

export function formatPackMaturityLabel(
  maturity: PackMaturityState,
  activation: PackActivationState,
): string {
  return `${maturity} · ${activation}`;
}

export function videoDomainMigrationSummary(): string {
  const claim = VIDEO_DOMAIN_MIGRATION_CLAIM;
  return [
    claim.bannerLabel,
    `Inventory: ${claim.agentInventoryCount} common agents (${claim.defaultActivationState}).`,
    `Safe stub: ${claim.soleSafeStubGraphId} (not blueprint realization).`,
    claim.disclaimer,
  ].join(" ");
}

/**
 * Patterns that over-claim migration completion or production readiness in UI copy.
 * Used by alignment tests; not a content filter for untrusted model output.
 */
export const FALSE_MIGRATION_COMPLETION_PATTERNS: readonly RegExp[] = [
  // Domain/migration self-contained overclaims only. Folder-layout language such as
  // "self-contained folder" / agent badges is allowed (redo_migration agent layout).
  /(?<!\bnot )\b(?:video\s+)?domain\b[^.!?\n]{0,48}\bself[- ]contained\b/i,
  /(?<!\bnot )\bmigration\b[^.!?\n]{0,48}\bself[- ]contained\b/i,
  /(?<!\bnot )\bself[- ]contained\b[^.!?\n]{0,48}\b(?:migration|domain)\b/i,
  /\bproduction[- ]ready\b/i,
  /\bproduction activation enabled\b/i,
  /\b114 agents active\b/i,
  // pack_spine claimed as blueprint realization (allow "not blueprint realization").
  /\bpack_spine\b(?![^.]*\bnot\b)[^.]*\bblueprint (family|realization|implementation)\b/i,
  /\b14 workflows (live|active|production)\b/i,
  /(?<!\bnot )\bmigration complete\b/i,
  /(?<!\bawaiting )(?<!\buntil )\bSTANDALONE PASS\b/,
];

export function textImpliesFalseMigrationCompletion(text: string): boolean {
  return FALSE_MIGRATION_COMPLETION_PATTERNS.some((pattern) => pattern.test(text));
}

/** True when a presentation surface is allowed to mention video pack maturity. */
export function isMigrationSafeMaturityClaim(
  maturity: PackMaturityState,
  activation: PackActivationState,
): boolean {
  if (activation === "active") return false;
  if (maturity === "graph_validated" && VIDEO_DOMAIN_MIGRATION_CLAIM.documentStatus !== "complete") {
    return false;
  }
  return maturity === "cataloged" || maturity === "mapped" || maturity === "not_mature";
}
