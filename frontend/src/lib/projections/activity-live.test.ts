import assert from "node:assert/strict";
import test from "node:test";

import { buildLiveActivityView } from "./activity-live";

test("activity live maps Host feed rows without inventing costs", () => {
  const view = buildLiveActivityView({
    hostReachable: true,
    eventCount: 1,
    categories: ["swarm"],
    feed: {
      items: [
        {
          id: "act_1",
          category: "swarm",
          severity: "info",
          summary: "Materialized draft",
          subject_reference: "swarm_abc",
          status: "recorded",
          occurred_at: "2026-06-01T12:34:00+00:00",
          correlation_id: "corr-1",
        },
      ],
      freshness: { as_of: "2026-06-01T12:34:00+00:00", state: "live" },
    },
  });
  assert.equal(view.tableRows.length, 1);
  assert.equal(view.tableRows[0]?.swarm, "swarm_abc");
  assert.equal(view.boardColumns.length, 1);
  assert.equal(view.rolloutCards.length, 0);
  assert.doesNotMatch(view.collectiveImpact, /\$412/);
});

test("activity live is empty when Host is down", () => {
  const view = buildLiveActivityView({
    hostReachable: false,
    hostMessage: "down",
    feed: null,
  });
  assert.equal(view.tableRows.length, 0);
  assert.equal(view.boardColumns.length, 0);
  assert.match(view.description, /down/);
});
