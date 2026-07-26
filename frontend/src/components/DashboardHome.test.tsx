import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import React from "react";
import { renderToStaticMarkup } from "react-dom/server";

import { LOCAL_DASHBOARD_LANDING } from "../lib/projections/dashboard-landing";
import { DashboardHome } from "./DashboardHome";

const componentDirectory = dirname(fileURLToPath(import.meta.url));

test("dashboard home renders ui_02 common health, fleet ops, and insights", () => {
  const markup = renderToStaticMarkup(<DashboardHome />);

  assert.match(markup, /Common Health &amp; Fleet Ops/);
  assert.match(markup, /Common Health/);
  assert.match(markup, /Common Agents Active/);
  assert.match(markup, /87/);
  assert.match(markup, /Global Success Rate/);
  assert.match(markup, /Pending Improvement Proposals/);
  assert.match(markup, /Your Fleet Health/);
  assert.match(markup, /Est\. Monthly Savings/);
  assert.match(markup, /Explore Common Registry Hub/);
  assert.match(markup, /Compose New Swarm/);
  assert.match(markup, /Running Now/);
  assert.match(markup, /Daily market brief/);
  assert.match(markup, /View Live Canvas/);
  assert.match(markup, /Recent Activity/);
  assert.match(markup, /View all activity/);
  assert.match(markup, /Common Impact Insights/);
  assert.match(markup, /Local preview/);
  assert.doesNotMatch(markup, /tenant_id|credential|password/i);
});

test("dashboard landing fixture is stable presentation data", () => {
  assert.equal(LOCAL_DASHBOARD_LANDING.commonHealth.length, 5);
  assert.equal(LOCAL_DASHBOARD_LANDING.quickActions[0]?.href, "/registry");
  assert.ok(LOCAL_DASHBOARD_LANDING.runningSwarms.length >= 1);
  assert.ok(LOCAL_DASHBOARD_LANDING.recentRuns.length >= 1);
  assert.equal(LOCAL_DASHBOARD_LANDING.insights.length, 2);
});

test("dashboard CSS includes responsive health row and light-frame cards", async () => {
  const css = await readFile(
    resolve(componentDirectory, "../app/globals.css"),
    "utf8",
  );
  assert.match(css, /\.dashboard-home \{/);
  assert.match(css, /\.dashboard-home__stats \{/);
  assert.match(css, /\.dashboard-action--primary/);
  assert.match(css, /@media \(max-width: 760px\)/);
});
