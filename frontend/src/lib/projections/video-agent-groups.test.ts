import assert from "node:assert/strict";
import test from "node:test";

import { LOCAL_REGISTRY_LANDING } from "./registry-landing";
import {
  VIDEO_AGENT_GROUPS,
  groupAgentsByVideoCategory,
  videoGroupForCategory,
  videoGroupLabel,
} from "./video-agent-groups";

test("exactly ten video agent groups", () => {
  assert.equal(VIDEO_AGENT_GROUPS.length, 10);
  assert.deepEqual(
    VIDEO_AGENT_GROUPS.map((g) => g.id),
    [
      "1-ATL",
      "2-Cam",
      "3-Edit",
      "4-Snd",
      "5-Perf",
      "6-Dist",
      "7-Edu",
      "8-AI",
      "9-Meta",
      "10-Sup",
    ],
  );
});

test("groupAgentsByVideoCategory partitions pack video agents", () => {
  const video = LOCAL_REGISTRY_LANDING.agents.filter((a) =>
    a.id.startsWith("video."),
  );
  assert.equal(video.length, 114);
  const buckets = groupAgentsByVideoCategory(video);
  const inGroups = buckets
    .filter((b) => b.group)
    .reduce((n, b) => n + b.agents.length, 0);
  assert.equal(inGroups, 114);
  assert.equal(
    buckets.filter((b) => b.group).length,
    VIDEO_AGENT_GROUPS.filter((g) =>
      video.some((a) => a.category === g.id),
    ).length,
  );
  // Order follows 1…10
  const orders = buckets
    .filter((b) => b.group)
    .map((b) => b.group!.order);
  for (let i = 1; i < orders.length; i++) {
    assert.ok(orders[i]! >= orders[i - 1]!);
  }
});

test("videoGroupLabel and lookup", () => {
  assert.equal(videoGroupForCategory("1-ATL")?.label, "Above-the-Line");
  assert.match(videoGroupLabel("10-Sup"), /Workflow Support/);
  assert.equal(videoGroupForCategory("nope"), null);
});

test("registry landing exposes ten group facet tags", () => {
  assert.equal(LOCAL_REGISTRY_LANDING.videoGroupFacets.length, 10);
  assert.equal(LOCAL_REGISTRY_LANDING.videoGroupLabels.length, 10);
  assert.ok(LOCAL_REGISTRY_LANDING.videoGroupFacets.includes("1-ATL"));
  assert.ok(LOCAL_REGISTRY_LANDING.videoGroupFacets.includes("10-Sup"));
});
