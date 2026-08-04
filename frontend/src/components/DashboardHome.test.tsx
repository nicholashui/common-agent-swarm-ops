import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import React from "react";
import { renderToStaticMarkup } from "react-dom/server";

import { LOCAL_DASHBOARD_LANDING } from "../lib/projections/dashboard-landing";
import { buildLiveDashboardView } from "../lib/projections/dashboard-live";
import { PACK_AGENT_CATALOG_COUNTS } from "../lib/projections/pack-agents-catalog.generated";
import { DashboardHome } from "./DashboardHome";

const componentDirectory = dirname(fileURLToPath(import.meta.url));
const NOW = Date.parse("2026-06-01T12:00:00.000Z");

test("dashboard home renders live Host fleet projection", () => {
  const view = buildLiveDashboardView(
    {
      hostReachable: true,
      loading: false,
      swarms: [
        {
          id: "swarm_a",
          name: "Live Plan Draft",
          status: "draft",
          revision: 2,
          memberCount: 4,
          lastRunId: null,
          updatedAt: "2026-06-01T11:55:00.000Z",
          createdAt: "2026-06-01T11:00:00.000Z",
        },
      ],
    },
    NOW,
  );
  const markup = renderToStaticMarkup(<DashboardHome view={view} />);

  assert.match(markup, /Common Health &amp; Fleet Ops/);
  assert.match(markup, /Common Health/);
  assert.match(markup, /Pack agents \(catalog\)/);
  assert.match(markup, new RegExp(String(PACK_AGENT_CATALOG_COUNTS.total)));
  assert.match(markup, /Host swarm drafts/);
  assert.match(markup, /dashboard-sparkline/);
  assert.match(markup, /Quick Actions/);
  assert.match(markup, /Explore Common Registry Hub/);
  assert.match(markup, /Plan a multi-agent work/);
  assert.match(markup, /Your Swarms Fleet Ops/);
  assert.match(markup, /Host drafts/);
  assert.match(markup, /Live Plan Draft/);
  assert.match(markup, /View Execute/);
  assert.match(markup, /dashboard-running__bar/);
  assert.match(markup, /Recent Host drafts/);
  assert.match(markup, /Open Execute/);
  assert.match(markup, /Common Impact Insights/);
  assert.match(markup, /No Host insight projections/);
  assert.match(markup, /Control-Plane Health/);
  assert.match(markup, /Host \/ Swarm list/);
  assert.match(markup, /REST snapshot/);
  assert.match(markup, /Recent drafts/);
  assert.doesNotMatch(markup, /91\.4%|\$412|Wuxia Short|Brand Spot|Rollout Opportunity/);
  assert.doesNotMatch(markup, /tenant_id|password=|authorization:\s*bearer/i);
});

test("dashboard empty shell has no fabricated fleet rows", () => {
  assert.equal(LOCAL_DASHBOARD_LANDING.runningSwarms.length, 0);
  assert.equal(LOCAL_DASHBOARD_LANDING.recentRuns.length, 0);
  assert.equal(LOCAL_DASHBOARD_LANDING.insights.length, 0);
  assert.equal(LOCAL_DASHBOARD_LANDING.quickActions[0]?.href, "/registry");
});

test("dashboard CSS covers health row, control plane, and mobile scroll", async () => {
  const css = await readFile(
    resolve(componentDirectory, "../app/globals.css"),
    "utf8",
  );
  assert.match(css, /\.dashboard-home \{/);
  assert.match(css, /\.dashboard-sparkline/);
  assert.match(css, /\.dashboard-control \{/);
  assert.match(css, /\.dashboard-pinned/);
  assert.match(css, /scroll-snap-type: x mandatory/);
  assert.match(css, /@media \(max-width: 760px\)/);
});
