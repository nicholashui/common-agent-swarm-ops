/**
 * Locks performance import boundaries: slim route entries must not fan-in every Home.
 */
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "../..");

async function read(rel: string): Promise<string> {
  return readFile(resolve(root, rel), "utf8");
}

test("registry page uses BoundRegistryHome not BoundScreenHome", async () => {
  const source = await read("app/registry/page.tsx");
  assert.match(source, /BoundRegistryHome/);
  assert.doesNotMatch(source, /from [\"'].*BoundScreenHome[\"']/);
});

test("activity page uses slim BoundActivityHome not BoundScreenHome", async () => {
  const source = await read("app/activity/page.tsx");
  assert.match(source, /BoundActivityHome/);
  assert.doesNotMatch(source, /from [\"'].*BoundScreenHome[\"']/);
});

test("composer page uses slim BoundComposerHome not BoundScreenHome", async () => {
  const source = await read("app/composer/page.tsx");
  assert.match(source, /BoundComposerHome/);
  assert.doesNotMatch(source, /from [\"'].*BoundScreenHome[\"']/);
});

test("BoundRegistryHome does not import pack-agents.generated or BoundScreenHome", async () => {
  const source = await read("components/screen/BoundRegistryHome.tsx");
  assert.doesNotMatch(source, /pack-agents\.generated/);
  assert.doesNotMatch(source, /BoundScreenHome/);
  assert.match(source, /LOCAL_REGISTRY_LANDING|registry-landing/);
});

test("BoundActivityHome does not import other Homes or pack-agents.generated", async () => {
  const source = await read("components/screen/BoundActivityHome.tsx");
  assert.doesNotMatch(source, /pack-agents\.generated/);
  assert.doesNotMatch(source, /from \"\.\.\/ComposerHome\"|from \"\.\.\/DashboardHome\"|from \"\.\.\/RegistryHome\"/);
  assert.doesNotMatch(source, /from \"\.\/BoundScreenHome\"/);
  assert.match(source, /ActivityHome/);
  assert.match(source, /LOCAL_ACTIVITY_LANDING|activity-landing/);
});

test("screen-parameters does not import full pack-agents.generated", async () => {
  const source = await read("lib/projections/screen-parameters.ts");
  assert.doesNotMatch(source, /pack-agents\.generated/);
  assert.doesNotMatch(source, /LOCAL_AGENT_DETAIL_LANDING/);
  assert.match(source, /AGENT_DETAIL_PARAMETER_STUB|agent-detail-stub/);
});

test("BoundScreenHome code-splits Homes via next/dynamic", async () => {
  const source = await read("components/screen/BoundScreenHome.tsx");
  assert.match(source, /next\/dynamic/);
  assert.match(source, /dynamic\(/);
  // Must not statically import ActivityHome as a top-level named import from relative path
  assert.doesNotMatch(
    source,
    /^import\s*\{\s*ActivityHome\s*\}\s*from/m,
  );
});

test("registry-landing uses slim pack catalog not full pack-agents.generated", async () => {
  const source = await read("lib/projections/registry-landing.ts");
  assert.match(source, /pack-agents-catalog\.generated/);
  assert.doesNotMatch(source, /from \"\.\/pack-agents\.generated\"/);
});
