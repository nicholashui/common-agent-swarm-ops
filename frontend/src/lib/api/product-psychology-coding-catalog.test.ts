import assert from "node:assert/strict";
import test from "node:test";

import { planCodingWork } from "./product-coding";
import { buildPsychProfile } from "./product-psychology";
import { fetchSkillsCatalog } from "./product-skills-catalog";

test("buildPsychProfile maps cohort", async () => {
  const fetchImpl = async (input: RequestInfo | URL): Promise<Response> => {
    assert.equal(String(input), "/api/v1/psychology/profile");
    return Response.json({
      profile: {
        profile_id: "p1",
        cohort_id: "gen_z_scroll",
        emotional_target: { valence: 0.3 },
      },
    });
  };
  const result = await buildPsychProfile("tiktok ad", {
    fetchImpl: fetchImpl as typeof fetch,
  });
  assert.equal(result.ok, true);
  if (result.ok) {
    assert.equal(result.cohortId, "gen_z_scroll");
    assert.equal(result.profileId, "p1");
  }
});

test("planCodingWork maps steps", async () => {
  const fetchImpl = async (input: RequestInfo | URL): Promise<Response> => {
    assert.equal(String(input), "/api/v1/coding/plan");
    return Response.json({
      plan_steps: [{}, {}, {}],
      touch_points: [{}, {}],
      suggested_tests: ["pytest"],
    });
  };
  const result = await planCodingWork("add tests", {
    fetchImpl: fetchImpl as typeof fetch,
  });
  assert.equal(result.ok, true);
  if (result.ok) {
    assert.equal(result.stepCount, 3);
    assert.equal(result.touchCount, 2);
  }
});

test("fetchSkillsCatalog maps ids", async () => {
  const fetchImpl = async (input: RequestInfo | URL): Promise<Response> => {
    assert.equal(String(input), "/api/v1/skills/catalog");
    return Response.json({
      count: 2,
      items: [{ skill_id: "rag" }, { skill_id: "coding" }],
    });
  };
  const result = await fetchSkillsCatalog({
    fetchImpl: fetchImpl as typeof fetch,
  });
  assert.equal(result.ok, true);
  if (result.ok) {
    assert.equal(result.count, 2);
    assert.ok(result.skillIds.includes("coding"));
  }
});
