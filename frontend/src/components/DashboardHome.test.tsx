import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import React from "react";
import { renderToStaticMarkup } from "react-dom/server";

import { LOCAL_DASHBOARD_LANDING } from "../lib/projections/dashboard-landing";
import { getScreenParameters } from "../lib/projections/screen-parameters";
import { DashboardHome } from "./DashboardHome";

const componentDirectory = dirname(fileURLToPath(import.meta.url));

test("dashboard home matches ui_02_dashboard structure from md and svg", () => {
  const markup = renderToStaticMarkup(<DashboardHome view={getScreenParameters("dashboard")} />);

  assert.match(markup, /Common Health &amp; Fleet Ops/);
  assert.match(markup, /Common Health/);
  assert.match(markup, /Common Agents Active/);
  assert.match(markup, />87</);
  assert.match(markup, /Global Success Rate/);
  assert.match(markup, /91\.4%/);
  assert.match(markup, /Pending Improvement Proposals/);
  assert.match(markup, /Your Fleet Health/);
  assert.match(markup, /\$412/);
  assert.match(markup, /dashboard-sparkline/);
  assert.match(markup, /Quick Actions/);
  assert.match(markup, /Explore Common Registry Hub/);
  assert.match(markup, /Compose from Common Patterns/);
  assert.match(markup, /Review Improvement Proposals/);
  assert.match(markup, /Your Swarms Fleet Ops/);
  assert.match(markup, /Running Now/);
  assert.match(markup, /TradingResearch α/);
  assert.match(markup, /ContentPipeline β/);
  assert.match(markup, /View Canvas/);
  assert.match(markup, />Pause</);
  assert.match(markup, /dashboard-running__bar/);
  assert.match(markup, /Recent Activity/);
  assert.match(markup, /View all →/);
  assert.match(markup, /Self-Refining/);
  assert.match(markup, /Replay ↻/);
  assert.match(markup, /Debug →/);
  assert.match(markup, /Common Impact Insights/);
  assert.match(markup, /Rollout Opportunity/);
  assert.match(markup, /Approve Rollout/);
  assert.match(markup, /A\/B Test First/);
  assert.match(markup, /View Diff/);
  assert.match(markup, /Collective Intelligence/);
  assert.match(markup, /Control-Plane Health/);
  assert.match(markup, /API \/ Projection Health/);
  assert.match(markup, /SSE Transport/);
  assert.match(markup, /Affected swarms/);
  assert.match(markup, /Pinned \/ Favorites/);
  assert.match(markup, /VerificationLoopAgent/);
  assert.match(markup, /Redacted projections only/);
  assert.doesNotMatch(markup, /tenant_id|password=|authorization:\s*bearer/i);
});

test("dashboard landing fixture covers svg sections", () => {
  assert.equal(LOCAL_DASHBOARD_LANDING.commonHealth.length, 5);
  assert.equal(LOCAL_DASHBOARD_LANDING.quickActions.length, 3);
  assert.equal(LOCAL_DASHBOARD_LANDING.quickActions[0]?.href, "/registry");
  assert.equal(LOCAL_DASHBOARD_LANDING.runningSwarms.length, 2);
  assert.equal(LOCAL_DASHBOARD_LANDING.recentRuns.length, 4);
  assert.equal(LOCAL_DASHBOARD_LANDING.insights.length, 2);
  assert.ok(LOCAL_DASHBOARD_LANDING.controlPlane.backlogCount);
  assert.equal(LOCAL_DASHBOARD_LANDING.pinned.length, 3);
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
