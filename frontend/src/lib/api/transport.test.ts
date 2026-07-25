import assert from "node:assert/strict";
import test from "node:test";

import { createPublicApiClient } from "./client";

const RUN_OPERATION = "read_run_api_v1_workflow_runs__run_id__get" as const;
const APPROVAL_OPERATION = "submit_approval_decision_api_v1_approvals__approval_id__decision_post" as const;

test("uses a generated same-origin operation and unwraps only public envelope data", async () => {
  let requestedPath = "";
  let requestedInit: RequestInit | undefined;
  const client = createPublicApiClient({ fetchImpl: async (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
    requestedPath = String(input);
    requestedInit = init;
    return Response.json({ data: { run_id: "run-1", status: "queued" }, meta: { correlation_id: "corr-1" }, internal_trace: "excluded" });
  } });

  const result = await client.request(RUN_OPERATION, { path: { run_id: "run 1" } });
  assert.equal(requestedPath, "/api/v1/workflow-runs/run%201");
  assert.equal(requestedInit?.credentials, "include");
  assert.equal(requestedInit?.cache, "no-store");
  assert.equal(result.ok, true);
  if (result.ok) {
    assert.equal(result.correlationId, "corr-1");
    assert.equal(result.data.run_id, "run-1");
    assert.equal("internal_trace" in result, false);
  }
});

test("maps only the approved public error fields", async () => {
  const client = createPublicApiClient({ fetchImpl: async (): Promise<Response> => Response.json({ error: { code: "rate_limited", message: "Try later.", retryable: true, correlation_id: "corr-2", retry_after: 12, action_reference: { id: "refresh" }, private_trace: "excluded" } }, { status: 429, headers: { "Retry-After": "99" } }) });
  const result = await client.request(RUN_OPERATION, { path: { run_id: "run-1" } });
  assert.deepEqual(result, { ok: false, code: "rate_limited", message: "Try later.", retryable: true, correlationId: "corr-2", retryAfterSeconds: 12, actionReference: { id: "refresh" } });
});

test("retries retryable generated reads but never retries a generated mutation", async () => {
  let readAttempts = 0;
  const readClient = createPublicApiClient({ fetchImpl: async (): Promise<Response> => {
    readAttempts += 1;
    if (readAttempts === 1) throw new TypeError("network unavailable");
    return Response.json({ data: { run_id: "run-1", status: "queued" }, meta: { correlation_id: "corr-3" } });
  } });
  const readResult = await readClient.request(RUN_OPERATION, { path: { run_id: "run-1" } });
  assert.equal(readResult.ok, true);
  assert.equal(readAttempts, 2);

  let mutationAttempts = 0;
  const mutationClient = createPublicApiClient({ fetchImpl: async (): Promise<Response> => {
    mutationAttempts += 1;
    throw new TypeError("network unavailable");
  } });
  const mutationResult = await mutationClient.request(APPROVAL_OPERATION, { path: { approval_id: "approval-1" }, body: { selected_value: "approved", reason: "Reviewed." } });
  assert.deepEqual(mutationResult, { ok: false, code: "transport_unavailable", message: "The public API request could not be completed.", retryable: true });
  assert.equal(mutationAttempts, 1);
});

test("rejects responses that are not public data and correlation envelopes", async () => {
  const client = createPublicApiClient({ fetchImpl: async (): Promise<Response> => Response.json({ run_id: "run-1" }) });
  const result = await client.request(RUN_OPERATION, { path: { run_id: "run-1" } });
  assert.deepEqual(result, { ok: false, code: "invalid_public_response", message: "The public API returned an unusable response.", retryable: false });
});
