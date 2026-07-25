import assert from "node:assert/strict";
import test from "node:test";
import { mkdir, mkdtemp, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { dirname, resolve } from "node:path";

import { checkSourcePolicy } from "./check-source-policy.mjs";

async function fixture(files) {
  const root = await mkdtemp(resolve(tmpdir(), "frontend-source-policy-"));
  await Promise.all(Object.entries(files).map(async ([path, source]) => {
    const target = resolve(root, path);
    await mkdir(dirname(target), { recursive: true });
    await writeFile(target, source, "utf8");
  }));
  return root;
}

test("source policy accepts generated transport and rejects every prohibited browser boundary", async () => {
  const root = await fixture({
    "src/lib/api/transport.ts": "fetch('/api/v1/runs');",
    "src/safe.ts": "const endpoint = '/api/v1/runs';",
    "src/unsafe.ts": "fetch('/api/runs'); '/api/v1/health/live'; dangerouslySetInnerHTML; eval('x'); new Function('x'); window.open('https://example.test'); localStorage.setItem('token', 'x');",
  });
  try {
    const violations = await checkSourcePolicy(root);
    assert.deepEqual(violations.map(({ rule }) => rule), ["direct-fetch", "unversioned-public-api", "liveness-readiness", "dangerously-set-inner-html", "dynamic-evaluation", "dynamic-evaluation", "arbitrary-window-open", "browser-persistence-write"]);
    assert.ok(violations.every(({ path }) => path === "src/unsafe.ts"));
  } finally { await rm(root, { force: true, recursive: true }); }
});
