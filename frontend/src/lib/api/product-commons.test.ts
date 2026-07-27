import assert from "node:assert/strict";
import test from "node:test";

import { proposeAgentImprovement } from "./product-commons";

test("proposeAgentImprovement fetches agent actions then posts proposal", async () => {
  const calls: { url: string; method?: string }[] = [];
  const fetchImpl = async (
    input: RequestInfo | URL,
    init?: RequestInit,
  ): Promise<Response> => {
    const url = String(input);
    calls.push({ url, method: init?.method });
    if (url.includes("/proposals") && init?.method === "POST") {
      return Response.json({
        data: {
          proposal_id: "prop_test1",
          status: "submitted",
          target_id: "video.accessibility",
        },
        meta: { correlation_id: "c1" },
      });
    }
    return Response.json({
      data: {
        id: "video.accessibility",
        actions: [
          {
            id: "act_propose_1",
            label: "Propose",
            kind: "propose_improvement",
            eligible: true,
            resource_ref: "video.accessibility",
          },
        ],
      },
      meta: { correlation_id: "c0" },
    });
  };

  const result = await proposeAgentImprovement("video.accessibility", {
    fetchImpl: fetchImpl as typeof fetch,
    summary: "Test proposal",
  });
  assert.equal(result.ok, true);
  if (result.ok) {
    assert.equal(result.proposalId, "prop_test1");
    assert.equal(result.status, "submitted");
  }
  assert.equal(calls.length, 2);
  assert.match(calls[0]!.url, /\/api\/v1\/commons\/agents\/video\.accessibility$/);
  assert.match(calls[1]!.url, /\/proposals$/);
  assert.equal(calls[1]!.method, "POST");
});

test("proposeAgentImprovement fails when no eligible action", async () => {
  const fetchImpl = async (): Promise<Response> =>
    Response.json({
      data: { id: "x", actions: [] },
      meta: { correlation_id: "c" },
    });
  const result = await proposeAgentImprovement("x", {
    fetchImpl: fetchImpl as typeof fetch,
  });
  assert.equal(result.ok, false);
  if (!result.ok) {
    assert.match(result.message, /no eligible propose/i);
  }
});
