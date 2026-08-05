import assert from "node:assert/strict";
import test from "node:test";

import {
  fetchRagPolicy,
  ingestRagDocument,
  queryAgenticRag,
} from "./product-agentic-rag";

test("queryAgenticRag maps run fields", async () => {
  const fetchImpl = async (
    input: RequestInfo | URL,
    init?: RequestInit,
  ): Promise<Response> => {
    assert.equal(String(input), "/api/v1/rag/query");
    assert.equal(init?.method, "POST");
    const body = JSON.parse(String(init?.body)) as { query: string };
    assert.equal(body.query, "memory tiers");
    return Response.json({
      ok: true,
      run: {
        final_answer: "Grounded answer",
        confidence: 0.7,
        citations: [{ chunk_id: "c1" }],
        patterns_used: ["Planning", "Tool Use"],
        reflection_triggered: false,
        escalate_to_hitl: false,
      },
    });
  };
  const result = await queryAgenticRag("memory tiers", {
    fetchImpl: fetchImpl as typeof fetch,
  });
  assert.equal(result.ok, true);
  if (result.ok) {
    assert.equal(result.answer, "Grounded answer");
    assert.equal(result.confidence, 0.7);
    assert.equal(result.citationCount, 1);
    assert.ok(result.patterns.includes("Planning"));
  }
});

test("fetchRagPolicy maps fail-closed flags", async () => {
  const fetchImpl = async (input: RequestInfo | URL): Promise<Response> => {
    assert.equal(String(input), "/api/v1/rag/policy");
    return Response.json({
      activation_policy: { live_web: false, chroma: false, lightrag: false },
      patterns: ["Reflection", "Planning"],
    });
  };
  const result = await fetchRagPolicy({ fetchImpl: fetchImpl as typeof fetch });
  assert.equal(result.ok, true);
  if (result.ok) {
    assert.equal(result.liveWeb, false);
    assert.equal(result.lightrag, false);
    assert.ok(result.patterns.includes("Planning"));
  }
});

test("ingestRagDocument posts content", async () => {
  const fetchImpl = async (
    input: RequestInfo | URL,
    init?: RequestInit,
  ): Promise<Response> => {
    assert.equal(String(input), "/api/v1/rag/ingest");
    const body = JSON.parse(String(init?.body)) as { title: string };
    assert.equal(body.title, "Doc A");
    return Response.json({ ok: true, doc_id: "doc_abc" });
  };
  const result = await ingestRagDocument("Doc A", "hello world", {
    fetchImpl: fetchImpl as typeof fetch,
  });
  assert.equal(result.ok, true);
  if (result.ok) {
    assert.equal(result.docId, "doc_abc");
  }
});
