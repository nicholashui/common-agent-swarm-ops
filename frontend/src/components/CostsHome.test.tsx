import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import React from "react";
import { renderToStaticMarkup } from "react-dom/server";

import { LOCAL_COSTS_LANDING } from "../lib/projections/costs-landing";
import { getScreenParameters } from "../lib/projections/screen-parameters";
import { CostsHome } from "./CostsHome";

const componentDirectory = dirname(fileURLToPath(import.meta.url));

test("costs home matches ui_19 md/svg structure", () => {
  const markup = renderToStaticMarkup(<CostsHome view={getScreenParameters("costs")} />);

  assert.match(markup, /Cost &amp; Token Analytics/);
  assert.match(markup, /Token usage, cost attribution/);
  assert.match(markup, /Last 30 days/);
  assert.match(markup, /Export report/);
  assert.match(markup, /Total spend \(30d\)/);
  assert.match(markup, /Total tokens/);
  assert.match(markup, /Savings from commons/);
  assert.match(markup, /Cost \/ successful run/);
  assert.match(markup, /Budget utilization/);
  assert.match(markup, /Cost Trend/);
  assert.match(markup, /Cost by Swarm/);
  assert.match(markup, /TradingResearch α/);
  assert.match(markup, /ContentPipeline β/);
  assert.match(markup, /DSE Tutor Fleet/);
  assert.match(markup, /LegacyModernizer/);
  assert.match(markup, /Others \(4\)/);
  assert.match(markup, /Token Usage by Agent/);
  assert.match(markup, /DataFetcher v2\.1/);
  assert.match(markup, /SentimentAgent v1\.9/);
  assert.match(markup, /VerifierNode v3\.0/);
  assert.match(markup, /CustomReportAgent/);
  assert.match(markup, /CommonReportAgent v2\.2/);
  assert.match(markup, /Budget &amp; Alerts/);
  assert.match(markup, /Monthly budget/);
  assert.match(markup, /Projected end-of-month/);
  assert.match(markup, /Commons Savings Impact/);
  assert.match(markup, /What-If Simulator/);
  assert.match(markup, /Apply recommendation/);
  assert.match(markup, /Optimization Recommendations/);
  assert.match(markup, /cannot silently weaken|L1\/L2\/L3/);
  assert.doesNotMatch(markup, /tenant_id|password=|authorization:\s*bearer/i);
});

test("costs fixture covers kpis, breakdowns, budget, simulator guard", () => {
  assert.equal(LOCAL_COSTS_LANDING.kpis.length, 5);
  assert.equal(LOCAL_COSTS_LANDING.swarmBreakdown.length, 5);
  assert.equal(LOCAL_COSTS_LANDING.agentUsage.length, 4);
  assert.equal(LOCAL_COSTS_LANDING.recommendations.length, 2);
  assert.match(LOCAL_COSTS_LANDING.budget.projectedEom, /within budget/i);
  assert.match(LOCAL_COSTS_LANDING.simulator.qualityGuard, /cannot silently weaken/i);
  assert.match(LOCAL_COSTS_LANDING.safetyNote, /No client-created budget authority/i);
});

test("costs CSS defines kpis, bars, budget, and simulator", async () => {
  const css = await readFile(
    resolve(componentDirectory, "../app/globals.css"),
    "utf8",
  );
  assert.match(css, /\.costs-home \{/);
  assert.match(css, /\.costs-home__kpis/);
  assert.match(css, /\.costs-home__bars/);
  assert.match(css, /\.costs-home__budget/);
  assert.match(css, /\.costs-home__guard/);
});
