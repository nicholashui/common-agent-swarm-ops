import assert from "node:assert/strict";
import test from "node:test";

import { fetchLqrOverview } from "./product-lqr";
import { outlinePodcast } from "./product-podcast";
import { planScreenplay } from "./product-screenwriting";
import { adviseTechRadar } from "./product-tech-radar";

test("outlinePodcast maps segments", async () => {
  const fetchImpl = async (input: RequestInfo | URL): Promise<Response> => {
    assert.equal(String(input), "/api/v1/podcast/outline");
    return Response.json({
      segments: [{}, {}, {}],
      vo_plan: { live_tts: false },
      title_options: ["A", "B"],
    });
  };
  const r = await outlinePodcast("topic", { fetchImpl: fetchImpl as typeof fetch });
  assert.equal(r.ok, true);
  if (r.ok) {
    assert.equal(r.segmentCount, 3);
    assert.equal(r.liveTts, false);
  }
});

test("planScreenplay maps beats", async () => {
  const fetchImpl = async (input: RequestInfo | URL): Promise<Response> => {
    assert.equal(String(input), "/api/v1/screenwriting/plan");
    return Response.json({
      beats: [{}, {}],
      controlling_idea: "truth",
      genre: "drama",
    });
  };
  const r = await planScreenplay("logline", { fetchImpl: fetchImpl as typeof fetch });
  assert.equal(r.ok, true);
  if (r.ok) {
    assert.equal(r.beatCount, 2);
    assert.equal(r.genre, "drama");
  }
});

test("adviseTechRadar maps recommendation", async () => {
  const fetchImpl = async (input: RequestInfo | URL): Promise<Response> => {
    assert.equal(String(input), "/api/v1/tech-radar/advise");
    return Response.json({
      recommended_provider_id: "media_stub",
      candidates: ["media_stub", "sora"],
    });
  };
  const r = await adviseTechRadar("stub video", {
    fetchImpl: fetchImpl as typeof fetch,
  });
  assert.equal(r.ok, true);
  if (r.ok) {
    assert.equal(r.recommended, "media_stub");
  }
});

test("fetchLqrOverview maps phases", async () => {
  const fetchImpl = async (input: RequestInfo | URL): Promise<Response> => {
    assert.equal(String(input), "/api/v1/lqr/overview");
    return Response.json({
      phases: [{}, {}, {}, {}, {}, {}],
      archetype: "E",
      principles: ["quiet"],
    });
  };
  const r = await fetchLqrOverview({ fetchImpl: fetchImpl as typeof fetch });
  assert.equal(r.ok, true);
  if (r.ok) {
    assert.equal(r.phaseCount, 6);
    assert.equal(r.archetype, "E");
  }
});
