/**
 * Guardrail: Home components must not embed LOCAL_* fixtures as defaults.
 * Pages must load parameters from the store / explicit view props.
 */
import assert from "node:assert/strict";
import { readdir, readFile } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const srcRoot = resolve(dirname(fileURLToPath(import.meta.url)), "../..");

test("Home components require view prop and do not default to LOCAL_* fixtures", async () => {
  const componentsDir = join(srcRoot, "components");
  const files = (await readdir(componentsDir)).filter(
    (name) => name.endsWith("Home.tsx") || name === "SpecialsCatalog.tsx",
  );
  assert.ok(files.length >= 18);
  for (const name of files) {
    const source = await readFile(join(componentsDir, name), "utf8");
    assert.doesNotMatch(
      source,
      /view\s*=\s*LOCAL_/,
      `${name} must not default view to LOCAL_* fixture`,
    );
    assert.doesNotMatch(
      source,
      /import\s*\{[^}]*LOCAL_[A-Z0-9_]+/,
      `${name} must not import LOCAL_* fixtures into the component module`,
    );
    assert.match(
      source,
      /view\s*[:}]/,
      `${name} must accept a view parameter`,
    );
  }
});

test("app pages bind screens through useScreenParameters or explicit stored view", async () => {
  const appRoot = join(srcRoot, "app");
  async function collect(dir: string): Promise<readonly string[]> {
    const entries = await readdir(dir, { withFileTypes: true });
    const out: string[] = [];
    for (const entry of entries) {
      const full = join(dir, entry.name);
      if (entry.isDirectory()) out.push(...await collect(full));
      else if (entry.name === "page.tsx") out.push(full);
    }
    return out;
  }
  const pages = await collect(appRoot);
  const landingPages = pages.filter((path) => !path.includes(`${join("login")}${join("")}`) && !path.endsWith(join("login", "page.tsx")));
  for (const page of landingPages) {
    if (page.endsWith(join("login", "page.tsx"))) continue;
    const source = await readFile(page, "utf8");
    // Login is auth UI, not a projection landing.
    if (source.includes("LoginScreen")) continue;
    const usesStore = /useScreenParameters|getScreenParameters/.test(source);
    const usesBound = /BoundScreenHome/.test(source);
    const passesView = /view=\{/.test(source) || /projection=\{/.test(source);
    assert.ok(
      usesStore || usesBound,
      `${page} must read screen parameters from the store`,
    );
    assert.ok(
      passesView,
      `${page} must pass view/projection into the home component`,
    );
    assert.doesNotMatch(
      source,
      /<(Dashboard|Registry|Canvas|Blueprints)Home\s*\/>/,
      `${page} must not mount homes without stored parameters`,
    );
  }
});
