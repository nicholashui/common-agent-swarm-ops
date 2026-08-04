import assert from "node:assert/strict";
import test from "node:test";

import {
  materializeAiComposition,
  recommendComposition,
} from "./product-composer";

test("recommendComposition maps Host AI pick payload", async () => {
  const fetchImpl = async (
    input: RequestInfo | URL,
    init?: RequestInit,
  ): Promise<Response> => {
    assert.equal(String(input), "/api/v1/composer/recommend");
    assert.equal(init?.method, "POST");
    const body = JSON.parse(String(init?.body)) as { goal: string };
    assert.match(body.goal, /wuxia/i);
    return Response.json({
      ok: true,
      mode: "ai_pick",
      goal: body.goal,
      pattern: {
        id: "hierarchical-supervisor",
        name: "Hierarchical Supervisor + Specialists",
        version_label: "pattern · 1.0",
        when_to_use: "Supervisor routes work.",
        rationale: "Default hierarchy.",
      },
      slots: [
        {
          id: "slot_0",
          agent_id: "video.orchestrator",
          label: "Orchestrator",
          role: "Orch",
          version: "video · registered",
          pack: "video",
          verified: false,
          rationale: "AI-selected",
        },
        {
          id: "slot_1",
          agent_id: "video.planner",
          label: "Planner",
          role: "Plan",
          version: "video · registered",
          pack: "video",
          verified: false,
          rationale: "AI-selected",
        },
      ],
      procedure_steps: ["1. goal"],
      note: "deterministic",
    });
  };
  const result = await recommendComposition("YouTube wuxia pipeline", {
    fetchImpl: fetchImpl as typeof fetch,
  });
  assert.equal(result.ok, true);
  if (result.ok) {
    assert.equal(result.recommendation.mode, "ai_pick");
    assert.equal(result.recommendation.slots[0]!.agentId, "video.orchestrator");
    assert.equal(
      result.recommendation.pattern?.id,
      "hierarchical-supervisor",
    );
  }
});

test("materializeAiComposition returns canvas path", async () => {
  const fetchImpl = async (
    input: RequestInfo | URL,
    init?: RequestInit,
  ): Promise<Response> => {
    assert.equal(String(input), "/api/v1/composer/materialize");
    assert.equal(init?.method, "POST");
    const body = JSON.parse(String(init?.body)) as {
      brief?: { scale_profile?: string; locale?: string };
    };
    assert.equal(body.brief?.scale_profile, "S1");
    assert.equal(body.brief?.locale, "zh-Hant");
    return Response.json({
      decision_status: "ai_resolved",
      swarm_id: "swarm_ai1",
      name: "AI crew",
      revision: 4,
      member_count: 4,
      canvas_path: "/swarms/swarm_ai1/canvas",
      brief_id: "brief_abc",
      spine_workflow_id: "wf_video_spine_v1",
      recommendation: {
        mode: "ai_pick",
        decision_status: "ai_resolved",
        goal: "test",
        pattern: { id: "p", name: "P", version_label: "1", rationale: "r" },
        slots: [{ agent_id: "video.director", label: "Director" }],
      },
    });
  };
  const result = await materializeAiComposition("test goal", {
    fetchImpl: fetchImpl as typeof fetch,
    brief: { locale: "zh-Hant", scaleProfile: "S1", archetype: "A" },
  });
  assert.equal(result.ok, true);
  if (result.ok && result.decisionStatus === "ai_resolved") {
    assert.equal(result.swarmId, "swarm_ai1");
    assert.equal(result.canvasPath, "/swarms/swarm_ai1/canvas");
    assert.equal(result.memberCount, 4);
    assert.equal(result.briefId, "brief_abc");
    assert.equal(result.spineWorkflowId, "wf_video_spine_v1");
  }
});
