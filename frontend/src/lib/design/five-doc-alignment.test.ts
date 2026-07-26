/**
 * Consolidated gate for redesign docs 1–5 as they bind frontend function:
 * backend_redesign, frontend_redesign, adoption_redesign, migration_redesign,
 * special_agents_redesign.
 */
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import { SPECIAL_AGENT_CATALOG_COUNT, isSpecialsCatalogFailClosed } from "../specials/specials-catalog";
import { VIDEO_DOMAIN_MIGRATION_CLAIM } from "../migration/video-domain-migration";

const srcRoot = resolve(dirname(fileURLToPath(import.meta.url)), "../..");

test("1 backend_redesign: transport stays /api/v1 + idempotent headers", async () => {
  const transport = await readFile(resolve(srcRoot, "lib/api/transport.ts"), "utf8");
  assert.match(transport, /\/api\/v1/);
  assert.match(transport, /Idempotency-Key/);
  assert.match(transport, /executeWithOptions/);
});

test("2 frontend_redesign: command + SSE recovery primitives", async () => {
  const commands = await readFile(resolve(srcRoot, "lib/commands/CommandCoordinator.ts"), "utf8");
  const sse = await readFile(resolve(srcRoot, "lib/live/sse-subscription.ts"), "utf8");
  const live = await readFile(resolve(srcRoot, "lib/live/LiveProjectionController.ts"), "utf8");
  assert.match(commands, /Idempotency-Key/);
  assert.match(commands, /manual_recovery/);
  assert.match(sse, /\/api\/v1\/events\/stream/);
  assert.match(sse, /last_event_id|Last-Event-ID/i);
  assert.match(live, /resynchronize|expectedSequence/);
});

test("3 adoption_redesign: domain-neutral pack extension slots exist", async () => {
  const types = await readFile(resolve(srcRoot, "lib/pack-extensions/types.ts"), "utf8");
  const slot = await readFile(resolve(srcRoot, "components/pack/DomainPackExtensionSlot.tsx"), "utf8");
  assert.match(types, /PackUiExtensionManifest/);
  assert.doesNotMatch(types, /\/api\/v1\/video\//);
  assert.doesNotMatch(slot, /if\s*\(.*video/i);
});

test("4 migration_redesign: video claim remains PROPOSED fail-closed", (): void => {
  assert.equal(VIDEO_DOMAIN_MIGRATION_CLAIM.documentStatus, "proposed");
  assert.equal(VIDEO_DOMAIN_MIGRATION_CLAIM.selfContained, false);
  assert.equal(VIDEO_DOMAIN_MIGRATION_CLAIM.packSpineIsBlueprintRealization, false);
  assert.equal(VIDEO_DOMAIN_MIGRATION_CLAIM.productionActivationImplied, false);
});

test("5 special_agents_redesign: catalog is exact draft pack presentation", (): void => {
  assert.equal(SPECIAL_AGENT_CATALOG_COUNT, 19);
  assert.equal(isSpecialsCatalogFailClosed(), true);
});
