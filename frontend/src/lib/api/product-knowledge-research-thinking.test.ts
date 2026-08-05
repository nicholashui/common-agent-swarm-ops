import assert from "node:assert/strict";
import test from "node:test";

import { routeKnowledge } from "./product-knowledge";
import { queryResearch } from "./product-research";
import { recommendThinking } from "./product-thinking";

test("routeKnowledge maps primary destination", async () => {
  const fetchImpl = async (
    input: RequestInfo | URL,
    init?: RequestInit,
  ): Promise<Response> => {
    assert.equal(String(input), "/api/v1/knowledge/route");
    assert.equal(init?.method, "POST");
    return Response.json({
      primary: "rag",
      confidence: 0.8,
      suggested_agent_ids: ["video.memory"],
    });
  };
  const result = await routeKnowledge("explain retrieval", {
    fetchImpl: fetchImpl as typeof fetch,
  });
  assert.equal(result.ok, true);
  if (result.ok) {
    assert.equal(result.primary, "rag");
    assert.equal(result.confidence, 0.8);
  }
});

test("queryResearch maps brief findings", async () => {
  const fetchImpl = async (input: RequestInfo | URL): Promise<Response> => {
    assert.equal(String(input), "/api/v1/research/query");
    return Response.json({
      ok: true,
      confidence: 0.6,
      citations: [{ chunk_id: "c1" }],
      brief: { findings: "Grounded offline findings" },
      escalate_to_hitl: false,
    });
  };
  const result = await queryResearch("memory tiers", {
    fetchImpl: fetchImpl as typeof fetch,
  });
  assert.equal(result.ok, true);
  if (result.ok) {
    assert.equal(result.citationCount, 1);
    assert.match(result.findings, /Grounded/);
  }
});

test("recommendThinking maps cognitive profile", async () => {
  const fetchImpl = async (input: RequestInfo | URL): Promise<Response> => {
    assert.equal(String(input), "/api/v1/thinking/recommend");
    return Response.json({
      ok: true,
      cognitive_profile: { operating_mode: "full", max_steps: 4 },
      selected_models: [{ id: "cynefin" }, { id: "premortem" }],
    });
  };
  const result = await recommendThinking("complex research", {
    fetchImpl: fetchImpl as typeof fetch,
  });
  assert.equal(result.ok, true);
  if (result.ok) {
    assert.equal(result.operatingMode, "full");
    assert.equal(result.maxSteps, 4);
    assert.ok(result.modelIds.includes("cynefin"));
  }
});
