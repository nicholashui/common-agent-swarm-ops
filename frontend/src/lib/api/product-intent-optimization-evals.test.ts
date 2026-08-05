import assert from "node:assert/strict";
import test from "node:test";

import { analyzeIntent } from "./product-intent";
import { recommendOptimization } from "./product-optimization";
import { runSkillEvals } from "./product-skill-evals";

test("analyzeIntent maps primary intent", async () => {
  const fetchImpl = async (
    input: RequestInfo | URL,
    init?: RequestInit,
  ): Promise<Response> => {
    assert.equal(String(input), "/api/v1/intent/analyze");
    assert.equal(init?.method, "POST");
    return Response.json({
      primary_intent: "promote",
      recommended_archetype: "B",
      escalate_to_hitl: false,
    });
  };
  const result = await analyzeIntent("30s UGC ad", {
    fetchImpl: fetchImpl as typeof fetch,
  });
  assert.equal(result.ok, true);
  if (result.ok) {
    assert.equal(result.primaryIntent, "promote");
    assert.equal(result.archetype, "B");
  }
});

test("recommendOptimization maps suggestions", async () => {
  const fetchImpl = async (input: RequestInfo | URL): Promise<Response> => {
    assert.equal(String(input), "/api/v1/optimization/recommend");
    return Response.json({
      kind: "cost",
      suggestions: [{ title: "Prefer fast path" }, { title: "Stub tools" }],
    });
  };
  const result = await recommendOptimization("cut cost", {
    fetchImpl: fetchImpl as typeof fetch,
    kind: "cost",
  });
  assert.equal(result.ok, true);
  if (result.ok) {
    assert.equal(result.kind, "cost");
    assert.equal(result.suggestionCount, 2);
  }
});

test("runSkillEvals maps suite totals", async () => {
  const fetchImpl = async (input: RequestInfo | URL): Promise<Response> => {
    assert.equal(String(input), "/api/v1/skill-evals/run");
    return Response.json({ ok: true, passed: 7, failed: 0, total: 7 });
  };
  const result = await runSkillEvals({ fetchImpl: fetchImpl as typeof fetch });
  assert.equal(result.ok, true);
  if (result.ok) {
    assert.equal(result.passed, 7);
    assert.equal(result.failed, 0);
  }
});
