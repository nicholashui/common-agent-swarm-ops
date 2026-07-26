/**
 * Cross-doc frontend alignment gate for:
 * - docs/backend_redesign/backend_redesign.md
 * - docs/frontend_redesign/frontend_redesign.md
 * - docs/adoption_redesign/adoption_redesign.md
 */
import assert from "node:assert/strict";
import { readFile, readdir } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

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
    if (/\.(ts|tsx)$/.test(entry.name) && !entry.name.endsWith(".test.ts") && !entry.name.endsWith(".test.tsx")) {
      files.push(fullPath);
    }
  }
  return files;
}

test("backend + frontend redesign: no WebSocket browser transport", async () => {
  const files = await collectSourceFiles(srcRoot);
  for (const file of files) {
    const source = await readFile(file, "utf8");
    assert.doesNotMatch(source, /\bWebSocket\b|\bws:\/\/|\bwss:\/\//, `${file} must not use WebSocket`);
  }
});

test("backend + frontend redesign: public API base path remains /api/v1", async () => {
  const generated = await readFile(resolve(srcRoot, "lib/api/generated/index.ts"), "utf8");
  const transport = await readFile(resolve(srcRoot, "lib/api/transport.ts"), "utf8");
  const contracts = await readFile(resolve(srcRoot, "lib/contracts.ts"), "utf8");
  assert.match(generated, /GENERATED_API_BASE_PATH = "\/api\/v1"/);
  assert.match(transport, /\/api\/v1/);
  assert.match(contracts, /\/api\/v1\//);
});

test("frontend redesign 8.2/8.3: command + SSE recovery primitives are present", async () => {
  const commands = await readFile(resolve(srcRoot, "lib/commands/CommandCoordinator.ts"), "utf8");
  const live = await readFile(resolve(srcRoot, "lib/live/LiveProjectionController.ts"), "utf8");
  const sse = await readFile(resolve(srcRoot, "lib/live/sse-subscription.ts"), "utf8");
  assert.match(commands, /Idempotency-Key/);
  assert.match(commands, /manual_recovery/);
  assert.match(live, /resynchronize|expectedSequence/);
  assert.match(sse, /last_event_id|Last-Event-ID/i);
  assert.match(sse, /\/api\/v1\/events\/stream/);
});

test("adoption redesign: host UI extension slots are domain-neutral", async () => {
  const types = await readFile(resolve(srcRoot, "lib/pack-extensions/types.ts"), "utf8");
  const slot = await readFile(resolve(srcRoot, "components/pack/DomainPackExtensionSlot.tsx"), "utf8");
  assert.match(types, /PackUiExtensionManifest/);
  assert.match(types, /domainId/);
  assert.match(types, /slotId/);
  assert.doesNotMatch(types, /video\.\*|\/api\/v1\/video/);
  assert.doesNotMatch(slot, /\/api\/v1\/video/);
  // Video may appear only as an example pack value, not a host branch.
  assert.doesNotMatch(slot, /if\s*\(.*video/i);
});

test("adoption redesign: component tree does not hard-code video control-plane routes", async () => {
  const componentsRoot = resolve(srcRoot, "components");
  const files = await collectSourceFiles(componentsRoot);
  for (const file of files) {
    const source = await readFile(file, "utf8");
    assert.doesNotMatch(
      source,
      /\/api\/v1\/video\//,
      `${file} must not hard-code video control-plane routes (pack extension only)`,
    );
  }
});
