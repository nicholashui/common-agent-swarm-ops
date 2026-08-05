import assert from "node:assert/strict";
import test from "node:test";

import { solveComplexProblem } from "./product-complex-problem";
import { ideateCreative, listCreativePatterns } from "./product-creative";
import { planStrategicGoal } from "./product-strategic";

test("ideateCreative maps candidates and SSOR-lite summary", async () => {
  const fetchImpl = async (
    input: RequestInfo | URL,
    init?: RequestInit,
  ): Promise<Response> => {
    assert.equal(String(input), "/api/v1/creative/ideate");
    assert.equal(init?.method, "POST");
    const sent = JSON.parse(String(init?.body ?? "{}")) as { brief?: string };
    assert.equal(sent.brief, "brief");
    return Response.json({
      candidates: [
        {
          candidate_id: "gca_1",
          overall_cr: 0.42,
          outlier_count: 2,
          outlier_dimensions: ["audience_first", "visual_grammar"],
        },
        { candidate_id: "gca_2", overall_cr: 0.31, outlier_count: 1 },
        { candidate_id: "gca_3", overall_cr: 0.28, outlier_count: 3 },
      ],
      best_candidate_id: "gca_1",
      domain: "video",
      phase_trace: [
        { phase: "multi_pov_mapping" },
        { phase: "integration_refinement" },
        { phase: "output" },
      ],
      learned_patterns: [{ seed_motif: "prior motif", scope: "process_local" }],
      creative_direction: { logline: "A short piece" },
      handoff: {
        best_candidate_id: "gca_1",
        concept: "best concept",
        prompt_steer: "emphasize motif",
        overall_cr: 0.42,
        next_agents: ["video.director", "video.screenwriter"],
        creative_direction: { logline: "A short piece", domain: "video" },
      },
    });
  };
  const result = await ideateCreative("brief", {
    fetchImpl: fetchImpl as typeof fetch,
  });
  assert.equal(result.ok, true);
  if (result.ok) {
    assert.equal(result.candidateCount, 3);
    assert.equal(result.bestId, "gca_1");
    assert.equal(result.logline, "A short piece");
    assert.equal(result.domain, "video");
    assert.equal(result.topOverallCr, 0.42);
    assert.equal(result.topOutlierCount, 2);
    assert.equal(result.hasPhaseTrace, true);
    assert.equal(result.learnedPatternCount, 1);
    assert.equal(result.handoffBestId, "gca_1");
    assert.equal(result.handoffPromptSteer, "emphasize motif");
    assert.equal(result.handoffNextAgentCount, 2);
  }
});

test("listCreativePatterns maps process-local motifs", async () => {
  const fetchImpl = async (input: RequestInfo | URL): Promise<Response> => {
    assert.match(String(input), /\/api\/v1\/creative\/patterns/);
    return Response.json({
      ok: true,
      count: 1,
      scope: "process_local",
      items: [{ seed_motif: "kinetic montage", scope: "process_local" }],
    });
  };
  const result = await listCreativePatterns({
    fetchImpl: fetchImpl as typeof fetch,
  });
  assert.equal(result.ok, true);
  if (result.ok) {
    assert.equal(result.count, 1);
    assert.equal(result.scope, "process_local");
    assert.deepEqual(result.motifs, ["kinetic montage"]);
  }
});

test("solveComplexProblem maps plan", async () => {
  const fetchImpl = async (input: RequestInfo | URL): Promise<Response> => {
    assert.equal(String(input), "/api/v1/complex-problem/solve");
    return Response.json({
      plan: [{}, {}],
      recommended_option: "A_sequential",
      gates: [{}],
    });
  };
  const result = await solveComplexProblem("ship spine", {
    fetchImpl: fetchImpl as typeof fetch,
  });
  assert.equal(result.ok, true);
  if (result.ok) {
    assert.equal(result.planSteps, 2);
    assert.equal(result.recommendedOption, "A_sequential");
  }
});

test("planStrategicGoal maps milestones", async () => {
  const fetchImpl = async (input: RequestInfo | URL): Promise<Response> => {
    assert.equal(String(input), "/api/v1/strategic/plan");
    return Response.json({
      milestones: [{}, {}, {}],
      key_results: [{}, {}],
      objective: "Achieve: X",
    });
  };
  const result = await planStrategicGoal("X", {
    fetchImpl: fetchImpl as typeof fetch,
  });
  assert.equal(result.ok, true);
  if (result.ok) {
    assert.equal(result.milestoneCount, 3);
    assert.equal(result.krCount, 2);
  }
});
