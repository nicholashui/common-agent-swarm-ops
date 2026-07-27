/**
 * Full frontend hardcode scan for presentation surfaces.
 * Fails if components re-embed fixtures or pages skip the parameter store.
 */
import assert from "node:assert/strict";
import { readdir, readFile } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const srcRoot = resolve(dirname(fileURLToPath(import.meta.url)), "../..");

async function collect(
  directory: string,
  predicate: (name: string, isDir: boolean) => boolean,
): Promise<readonly string[]> {
  const entries = await readdir(directory, { withFileTypes: true });
  const files: string[] = [];
  for (const entry of entries) {
    const full = join(directory, entry.name);
    if (entry.isDirectory()) {
      if (predicate(entry.name, true)) files.push(...await collect(full, predicate));
      continue;
    }
    if (predicate(entry.name, false)) files.push(full);
  }
  return files;
}

test("scan: no *Home/Login/Specials component imports LOCAL_* fixtures", async () => {
  const files = await collect(join(srcRoot, "components"), (name, isDir) => {
    // Slim route binders under screen/ may import LOCAL_* landings intentionally.
    if (isDir) return name !== "screen";
    return (
      (name.endsWith("Home.tsx") || name === "LoginScreen.tsx" || name === "SpecialsCatalog.tsx")
      && !name.includes(".test.")
    );
  });
  assert.ok(files.length >= 19);
  for (const file of files) {
    const source = await readFile(file, "utf8");
    assert.doesNotMatch(
      source,
      /\bLOCAL_[A-Z0-9_]+\b/,
      `${file} must not reference LOCAL_* fixtures`,
    );
    assert.doesNotMatch(
      source,
      /view\s*=\s*LOCAL_/,
      `${file} must not default view to LOCAL_*`,
    );
  }
});

test("scan: presentation homes require a view prop", async () => {
  const files = await collect(join(srcRoot, "components"), (name, isDir) => {
    if (isDir) return true;
    return name.endsWith("Home.tsx") || name === "LoginScreen.tsx" || name === "SpecialsCatalog.tsx";
  });
  for (const file of files) {
    const source = await readFile(file, "utf8");
    assert.match(
      source,
      /view\s*[:}]/,
      `${file} must accept stored view parameters`,
    );
  }
});

test("scan: app pages bind store parameters for every non-auth-free route", async () => {
  const pages = await collect(join(srcRoot, "app"), (name, isDir) => {
    if (isDir) return !name.startsWith("api");
    return name === "page.tsx";
  });
  for (const page of pages) {
    const source = await readFile(page, "utf8");
    assert.match(
      source,
      /useScreenParameters|getScreenParameters|Bound\w+Home|LoginScreen|MarkdownViewerPage|DocsView/,
      `${page} must load screen parameters from the store or a bound screen home`,
    );
    assert.match(
      source,
      /view=\{|projection=\{|Bound\w+Home|LoginScreen|MarkdownViewerPage|DocsView/,
      `${page} must pass parameters into the presentation component or bind via Bound*Home`,
    );
  }
});

test("scan: homes must not declare module-level UI section label tables", async () => {
  const files = await collect(join(srcRoot, "components"), (name, isDir) => {
    if (isDir) return true;
    return name.endsWith("Home.tsx") || name === "SpecialsCatalog.tsx";
  });
  for (const file of files) {
    const source = await readFile(file, "utf8");
    // Forbid patterns like: const SECTIONS = [{ id, label }]
    assert.doesNotMatch(
      source,
      /const\s+[A-Z][A-Z0-9_]*\s*:\s*readonly\s*\{[^}]*label[^}]*\}\[\]\s*=\s*\[/,
      `${file} must not hardcode labeled section tables; put them in stored parameters`,
    );
    assert.doesNotMatch(
      source,
      /const\s+TABS\s*=/,
      `${file} must not hardcode TABS; use stored parameters`,
    );
  }
});

test("scan: hardcoded eyebrow literals reduced to parameter bindings", async () => {
  const files = await collect(join(srcRoot, "components"), (name, isDir) => {
    if (isDir) return true;
    return name.endsWith("Home.tsx");
  });
  const banned = [
    /className="eyebrow">DASHBOARD</,
    /className="eyebrow">ACTIVITY</,
    /className="eyebrow">REGISTRY HUB</,
    /className="eyebrow">COSTS</,
    /className="eyebrow">EVAL</,
    /className="eyebrow">COLLABORATION</,
    /className="eyebrow">KNOWLEDGE</,
    /className="eyebrow">MONITORING</,
    /className="eyebrow">NOTIFICATIONS</,
    /className="eyebrow">SETTINGS</,
    /className="eyebrow">COMMON AGENT DETAIL</,
    /className="eyebrow">DEVELOPER \/ API PORTAL</,
    /className="eyebrow">GOVERNANCE/,
    /className="eyebrow">BLUEPRINTS/,
    /className="eyebrow">PROFILE/,
  ];
  for (const file of files) {
    const source = await readFile(file, "utf8");
    for (const pattern of banned) {
      assert.doesNotMatch(
        source,
        pattern,
        `${file} still hardcodes an eyebrow; use view.eyebrow / stored labels`,
      );
    }
  }
});
