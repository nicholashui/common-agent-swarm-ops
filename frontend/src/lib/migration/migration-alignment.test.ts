/**
 * Frontend alignment gate for docs/migration_redesign/migration_redesign.md
 */
import assert from "node:assert/strict";
import { readFile, readdir } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import { LOCAL_BLUEPRINTS_LANDING } from "../projections/blueprints-landing";
import { mapPackAgentActivation } from "./pack-activation";
import {
  VIDEO_DOMAIN_MIGRATION_CLAIM,
  formatPackMaturityLabel,
  isMigrationSafeMaturityClaim,
  textImpliesFalseMigrationCompletion,
  videoDomainMigrationSummary,
} from "./video-domain-migration";

const srcRoot = resolve(dirname(fileURLToPath(import.meta.url)), "../..");

async function collectSourceFiles(directory: string): Promise<readonly string[]> {
  const entries = await readdir(directory, { withFileTypes: true });
  const files: string[] = [];
  for (const entry of entries) {
    const fullPath = join(directory, entry.name);
    if (entry.isDirectory()) {
      files.push(...await collectSourceFiles(fullPath));
      continue;
    }
    if (/\.(ts|tsx)$/.test(entry.name) && !/\.test\.(ts|tsx)$/.test(entry.name)) {
      files.push(fullPath);
    }
  }
  return files;
}

test("migration claim remains PROPOSED and fail-closed", (): void => {
  assert.equal(VIDEO_DOMAIN_MIGRATION_CLAIM.documentStatus, "proposed");
  assert.equal(VIDEO_DOMAIN_MIGRATION_CLAIM.selfContained, false);
  assert.equal(VIDEO_DOMAIN_MIGRATION_CLAIM.packSpineIsBlueprintRealization, false);
  assert.equal(VIDEO_DOMAIN_MIGRATION_CLAIM.soleSafeStubGraphId, "pack_spine");
  assert.equal(VIDEO_DOMAIN_MIGRATION_CLAIM.agentInventoryCount, 114);
  assert.equal(VIDEO_DOMAIN_MIGRATION_CLAIM.productionActivationImplied, false);
  assert.equal(VIDEO_DOMAIN_MIGRATION_CLAIM.liveProvidersEnabled, false);
  assert.match(videoDomainMigrationSummary(), /PROPOSED/);
  assert.match(videoDomainMigrationSummary(), /pack_spine/);
  assert.equal(
    formatPackMaturityLabel("cataloged", "registered"),
    "cataloged · registered",
  );
  assert.equal(isMigrationSafeMaturityClaim("cataloged", "registered"), true);
  assert.equal(isMigrationSafeMaturityClaim("graph_validated", "registered"), false);
  assert.equal(isMigrationSafeMaturityClaim("cataloged", "active"), false);
});

test("pack activation mapping denies silent production activation", (): void => {
  const denied = mapPackAgentActivation({
    agent_id: "video.creative_director",
    production_activation_denied: true,
    production_active: true,
    status: "active",
  });
  assert.equal(denied.productionActive, false);
  assert.equal(denied.productionActivationDenied, true);
  assert.equal(denied.mayOfferActivationControl, false);

  const registered = mapPackAgentActivation({
    agent_id: "video.delivery_packager",
    production_activation_denied: true,
    production_active: false,
    status: "registered",
  });
  assert.equal(registered.productionActive, false);
  assert.match(registered.activationLabel, /registered|denied|non_active/i);

  const missing = mapPackAgentActivation({});
  assert.equal(missing.productionActive, false);
  assert.equal(missing.productionActivationDenied, true);
});

test("blueprints fixture does not claim video migration completion", (): void => {
  const blobs = [
    LOCAL_BLUEPRINTS_LANDING.description,
    LOCAL_BLUEPRINTS_LANDING.safetyNote,
    LOCAL_BLUEPRINTS_LANDING.footerNote,
    LOCAL_BLUEPRINTS_LANDING.migrationNote ?? "",
    ...LOCAL_BLUEPRINTS_LANDING.blueprints.flatMap((bp) => [
      bp.name,
      bp.description,
      bp.metrics,
      ...(bp.vaHints ?? []),
      bp.maturityLabel ?? "",
    ]),
  ].join("\n");

  assert.equal(textImpliesFalseMigrationCompletion(blobs), false);
  assert.match(LOCAL_BLUEPRINTS_LANDING.migrationNote ?? "", /pack_spine|PROPOSED|non-active|not blueprint/i);
  const cinematic = LOCAL_BLUEPRINTS_LANDING.blueprints.find((bp) => bp.id === "cinematic");
  assert.ok(cinematic);
  assert.match(cinematic.maturityLabel ?? "", /cataloged|registered|non_active|non-active/i);
  assert.doesNotMatch(cinematic.description, /production[- ]ready|self-contained/i);
});

test("frontend presentation sources avoid false migration completion phrases", async () => {
  const roots = [
    resolve(srcRoot, "components"),
    resolve(srcRoot, "lib/projections"),
  ];
  for (const root of roots) {
    for (const file of await collectSourceFiles(root)) {
      const source = await readFile(file, "utf8");
      assert.equal(
        textImpliesFalseMigrationCompletion(source),
        false,
        `${file} must not claim migration/production completion`,
      );
    }
  }
});

test("components do not hard-code upstream migration source repositories as runtime deps", async () => {
  const components = await collectSourceFiles(resolve(srcRoot, "components"));
  for (const file of components) {
    const source = await readFile(file, "utf8");
    assert.doesNotMatch(source, /generic-swarm-ops|va-agent-swarm/, `${file} must not depend on upstream sources`);
  }
});
