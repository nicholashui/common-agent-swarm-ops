import assert from "node:assert/strict";
import { execFile } from "node:child_process";
import { mkdtemp, readFile, rm } from "node:fs/promises";
import { promisify } from "node:util";
import { dirname, resolve } from "node:path";
import test from "node:test";
import { tmpdir } from "node:os";
import { fileURLToPath } from "node:url";

import { createPublicApiClient } from "./client";

interface Expectations { readonly fixtureVersion: string; readonly openapiVersion: string; readonly operationId: string; readonly method: string; readonly path: string; }
const API_DIR = dirname(fileURLToPath(import.meta.url));
const FRONTEND_ROOT = resolve(API_DIR, "../../..");
const FIXTURES = resolve(FRONTEND_ROOT, "src/test/fixtures/frontend-redesign/v1");
const RUN = "read_run_api_v1_workflow_runs__run_id__get" as const;
const execFileAsync = promisify(execFile);
async function fixture(path: string): Promise<unknown> { return JSON.parse(await readFile(resolve(FIXTURES, path), "utf8")) as unknown; }

test("generated client maps only versioned public-envelope fixture fields", async () => {
  const success = await fixture("public-success.json");
  const successClient = createPublicApiClient({ fetchImpl: async (): Promise<Response> => Response.json(success) });
  const successResult = await successClient.request(RUN, { path: { run_id: "run-fixture-1" } });
  assert.deepEqual(successResult, { ok: true, data: { run_id: "run-fixture-1", status: "queued" }, correlationId: "corr-fixture-1" });
  const failure = await fixture("public-error.json");
  const failureClient = createPublicApiClient({ fetchImpl: async (): Promise<Response> => Response.json(failure, { status: 429 }) });
  const failureResult = await failureClient.request(RUN, { path: { run_id: "run-fixture-1" } });
  assert.deepEqual(failureResult, { ok: false, code: "rate_limited", message: "Retry after the returned delay.", retryable: true, correlationId: "corr-fixture-2", retryAfterSeconds: 7, actionReference: { id: "refresh-fixture", label: "Refresh", eligible: true } });
});

test("versioned OpenAPI fixture deterministically generates its expected contract surface", async () => {
  const expected = await fixture("generated-client.expectations.json") as Expectations;
  const directory = await mkdtemp(resolve(tmpdir(), "frontend-generated-fixture-"));
  const output = resolve(directory, "index.ts");
  try {
    await execFileAsync(process.execPath, [resolve(FRONTEND_ROOT, "scripts/generate-api-client.mjs"), "--input", resolve(FIXTURES, "openapi.json"), "--output", output]);
    const generated = await readFile(output, "utf8");
    assert.equal(expected.fixtureVersion, "frontend-redesign/v1");
    assert.ok(generated.includes(`GENERATED_OPENAPI_VERSION = "${expected.openapiVersion}"`));
    assert.ok(generated.includes(`"${expected.operationId}": { method: "${expected.method}", path: "${expected.path}"`));
  } finally { await rm(directory, { force: true, recursive: true }); }
});
