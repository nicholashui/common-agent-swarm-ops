import assert from "node:assert/strict";
import test from "node:test";

import { createOperatorApi } from "../contracts";
import { createPublicApiClient } from "../api/client";

test("operator API defaults to global fetch (not a stub rejection)", async () => {
  let called = false;
  const original = globalThis.fetch;
  globalThis.fetch = (async (): Promise<Response> => {
    called = true;
    return Response.json({
      run_id: "run-1",
      workflow_id: "wf",
      workflow_version: "1",
      status: "queued",
      engine: "graph",
      correlation_id: "corr-1",
      updated_at: "2026-01-01T00:00:00Z",
      failure_code: null,
      action_preview: null,
    });
  }) as typeof fetch;
  try {
    const api = createOperatorApi();
    const run = await api.getRun("run-1");
    assert.equal(called, true);
    assert.equal(run.run_id, "run-1");
  } finally {
    globalThis.fetch = original;
  }
});

test("public API client is constructible for live UI runtime", async () => {
  const client = createPublicApiClient({
    fetchImpl: async (): Promise<Response> =>
      Response.json({
        data: { actor_id: "a1", organization_id: "o1", correlation_id: "c1" },
        meta: { correlation_id: "c1" },
      }),
  });
  const result = await client.request("read_authenticated_context_api_v1_context_get", {
    path: {},
  });
  assert.equal(result.ok, true);
  if (result.ok) {
    assert.equal(result.data.actor_id, "a1");
  }
});
