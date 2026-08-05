import assert from "node:assert/strict";
import test from "node:test";

import {
  attachAestheticHandoff,
  compareAesthetics,
  evaluateAesthetics,
  fetchAestheticsPolicy,
} from "./product-aesthetics";

test("evaluateAesthetics posts score request and maps verdict", async () => {
  const fetchImpl = async (
    input: RequestInfo | URL,
    init?: RequestInit,
  ): Promise<Response> => {
    assert.equal(String(input), "/api/v1/aesthetics/evaluate");
    assert.equal(init?.method, "POST");
    const body = JSON.parse(String(init?.body)) as {
      artifact_ref: string;
      mode: string;
    };
    assert.equal(body.artifact_ref, "asset://x");
    assert.equal(body.mode, "score");
    return Response.json({
      ok: true,
      verdict: {
        aesthetic_quality: 0.72,
        hack_likelihood: 0.1,
        top_failing_dimensions: ["novelty"],
        actionable_critique: ["[novelty] too generic"],
        escalate_to_hitl: false,
      },
      verdict_markdown: "# Aesthetic verdict",
    });
  };
  const result = await evaluateAesthetics("asset://x", {
    fetchImpl: fetchImpl as typeof fetch,
  });
  assert.equal(result.ok, true);
  if (result.ok) {
    assert.equal(result.aestheticQuality, 0.72);
    assert.equal(result.hackLikelihood, 0.1);
    assert.deepEqual(result.topFailing, ["novelty"]);
    assert.equal(result.critiques[0], "[novelty] too generic");
    assert.equal(result.verdictMarkdown, "# Aesthetic verdict");
  }
});

test("compareAesthetics maps ranking", async () => {
  const fetchImpl = async (
    input: RequestInfo | URL,
    init?: RequestInit,
  ): Promise<Response> => {
    assert.equal(String(input), "/api/v1/aesthetics/compare");
    assert.equal(init?.method, "POST");
    return Response.json({
      ok: true,
      best_artifact_ref: "asset://a",
      ranking: [
        { artifact_ref: "asset://a", aesthetic_quality: 0.8 },
        { artifact_ref: "asset://b", aesthetic_quality: 0.5 },
      ],
    });
  };
  const result = await compareAesthetics(["asset://a", "asset://b"], {
    fetchImpl: fetchImpl as typeof fetch,
  });
  assert.equal(result.ok, true);
  if (result.ok) {
    assert.equal(result.bestArtifactRef, "asset://a");
    assert.equal(result.ranking.length, 2);
  }
});

test("fetchAestheticsPolicy maps fail-closed flags", async () => {
  const fetchImpl = async (input: RequestInfo | URL): Promise<Response> => {
    assert.equal(String(input), "/api/v1/aesthetics/policy");
    return Response.json({
      activation_policy: { live_vision: false, production_media: false },
      modes: ["score", "compare"],
    });
  };
  const result = await fetchAestheticsPolicy({
    fetchImpl: fetchImpl as typeof fetch,
  });
  assert.equal(result.ok, true);
  if (result.ok) {
    assert.equal(result.liveVision, false);
    assert.equal(result.productionMedia, false);
    assert.ok(result.modes.includes("score"));
  }
});

test("attachAestheticHandoff maps qc_status", async () => {
  const fetchImpl = async (
    input: RequestInfo | URL,
    init?: RequestInit,
  ): Promise<Response> => {
    assert.equal(String(input), "/api/v1/aesthetics/handoff/attach");
    assert.equal(init?.method, "POST");
    return Response.json({
      ok: true,
      handoff: {
        qc_status: "aesthetic_pass",
        qc_meta: { aesthetic: { agent_id: "specials.aesthetics-agent" } },
      },
    });
  };
  const result = await attachAestheticHandoff(
    { artifact_id: "a1" },
    { aesthetic_quality: 0.9, escalate_to_hitl: false },
    { fetchImpl: fetchImpl as typeof fetch },
  );
  assert.equal(result.ok, true);
  if (result.ok) {
    assert.equal(result.qcStatus, "aesthetic_pass");
  }
});
