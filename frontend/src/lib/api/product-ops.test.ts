import assert from "node:assert/strict";
import test from "node:test";

import { fetchActivityFeed, fetchCommonsHealth } from "./product-ops";

test("fetchActivityFeed maps Host items", async () => {
  const fetchImpl = async (input: RequestInfo | URL): Promise<Response> => {
    assert.equal(String(input), "/api/v1/activity?limit=50");
    return Response.json({
      items: [
        {
          id: "act_1",
          category: "swarm",
          severity: "info",
          summary: "Draft created",
          subject_reference: "swarm_1",
          status: "recorded",
          occurred_at: "2026-06-01T12:00:00+00:00",
        },
      ],
      freshness: { as_of: "2026-06-01T12:00:00+00:00", state: "live" },
    });
  };
  const result = await fetchActivityFeed({
    fetchImpl: fetchImpl as typeof fetch,
  });
  assert.equal(result.ok, true);
  if (result.ok) {
    assert.equal(result.data.items.length, 1);
    assert.equal(result.data.items[0]!.id, "act_1");
  }
});

test("fetchCommonsHealth maps pack counts", async () => {
  const fetchImpl = async (input: RequestInfo | URL): Promise<Response> => {
    assert.equal(String(input), "/api/v1/commons/health");
    return Response.json({
      total_agents: 133,
      by_pack: { video: 114, specials: 19 },
      patterns: 3,
      as_of: "2026-06-01T12:00:00+00:00",
      state: "cached",
    });
  };
  const result = await fetchCommonsHealth({
    fetchImpl: fetchImpl as typeof fetch,
  });
  assert.equal(result.ok, true);
  if (result.ok) {
    assert.equal(result.data.total_agents, 133);
    assert.equal(result.data.by_pack.video, 114);
  }
});
