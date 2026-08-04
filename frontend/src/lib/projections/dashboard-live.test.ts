import assert from "node:assert/strict";
import test from "node:test";

import { buildLiveDashboardView } from "./dashboard-live";
import { PACK_AGENT_CATALOG_COUNTS } from "./pack-agents-catalog.generated";

const NOW = Date.parse("2026-06-01T12:00:00.000Z");

test("live dashboard maps Host swarms without inventing success rates", () => {
  const view = buildLiveDashboardView(
    {
      hostReachable: true,
      loading: false,
      swarms: [
        {
          id: "swarm_live_1",
          name: "My Wuxia Draft",
          status: "draft",
          revision: 3,
          memberCount: 5,
          lastRunId: null,
          updatedAt: "2026-06-01T11:50:00.000Z",
          createdAt: "2026-06-01T10:00:00.000Z",
        },
      ],
    },
    NOW,
  );

  assert.equal(view.runningSwarms.length, 1);
  assert.equal(view.runningSwarms[0]?.name, "My Wuxia Draft");
  assert.match(view.runningSwarms[0]?.canvasHref ?? "", /\/swarms\/swarm_live_1\/canvas/);
  assert.equal(view.recentRuns[0]?.swarm, "My Wuxia Draft");
  assert.equal(view.pinned[0]?.name, "My Wuxia Draft");

  const catalogCard = view.commonHealth.find((c) => c.id === "catalog-agents");
  assert.equal(catalogCard?.value, String(PACK_AGENT_CATALOG_COUNTS.total));

  assert.equal(view.insights.length, 0);
  assert.doesNotMatch(view.footerNote + view.freshnessLabel, /91\.4%|\$412|TradingResearch/);
  assert.match(view.controlPlane.apiHealthLabel, /Reachable/i);
  assert.ok(view.quickActions.some((a) => a.id === "spine-template"));
});

test("live dashboard labels spine drafts with honesty copy", () => {
  const view = buildLiveDashboardView(
    {
      hostReachable: true,
      loading: false,
      spineActivityCount: 3,
      swarms: [
        {
          id: "swarm_spine_1",
          name: "Spine Crew",
          status: "draft",
          revision: 4,
          memberCount: 7,
          lastRunId: null,
          updatedAt: "2026-06-01T11:50:00.000Z",
          createdAt: "2026-06-01T10:00:00.000Z",
          hasSpine: true,
          spineStatus: "waiting_for_approval",
          spineWorkflowId: "wf_video_spine_v1",
        },
      ],
    },
    NOW,
  );
  assert.match(view.runningSwarms[0]?.pattern ?? "", /stub run|not production media/i);
  assert.match(view.runningSwarms[0]?.statusLabel ?? "", /Spine/i);
  assert.match(view.recentRuns[0]?.pattern ?? "", /spine/i);
  const spineCard = view.commonHealth.find((c) => c.id === "spine-drafts");
  assert.equal(spineCard?.value, "1");
  assert.match(spineCard?.detail ?? "", /not production media/i);
  assert.match(view.footerNote, /not production media/i);
  assert.match(view.controlPlane.approvalExpiryAlert, /package gate/i);
});

test("live dashboard stays empty and honest when Host is down", () => {
  const view = buildLiveDashboardView(
    {
      hostReachable: false,
      loading: false,
      hostMessage: "Could not list swarms: network",
      swarms: [],
    },
    NOW,
  );
  assert.equal(view.runningSwarms.length, 0);
  assert.equal(view.recentRuns.length, 0);
  assert.equal(view.stale, true);
  assert.match(view.controlPlane.apiHealthLabel, /Unreachable/i);
  assert.match(view.controlPlane.sseDetail, /Could not list swarms/);
});
