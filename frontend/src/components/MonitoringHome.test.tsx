import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import React from "react";
import { renderToStaticMarkup } from "react-dom/server";

import { LOCAL_MONITORING_LANDING } from "../lib/projections/monitoring-landing";
import { getScreenParameters } from "../lib/projections/screen-parameters";
import { MonitoringHome } from "./MonitoringHome";

const componentDirectory = dirname(fileURLToPath(import.meta.url));

test("monitoring home matches ui_09 md/svg structure", () => {
  const markup = renderToStaticMarkup(<MonitoringHome view={getScreenParameters("monitoring")} />);

  assert.match(markup, /Advanced Monitoring, Tracing &amp; Alerts/);
  assert.match(markup, /SSE seq 4421/);
  assert.match(markup, /Running swarms/);
  assert.match(markup, /Common health/);
  assert.match(markup, /Cost burn rate/);
  assert.match(markup, /Active anomalies/);
  assert.match(markup, /Alerts firing/);
  assert.match(markup, /Filters/);
  assert.match(markup, /Last 1 hour/);
  assert.match(markup, /Wuxia Short/);
  assert.match(markup, />Traces</);
  assert.match(markup, />Alerts</);
  assert.match(markup, />Metrics</);
  assert.match(markup, />Anomalies</);
  assert.match(markup, /Distributed Trace/);
  assert.match(markup, /run-4421/);
  assert.match(markup, /corr a3f9b1c2/);
  assert.match(markup, /graph rev 12/);
  assert.match(markup, /Swarm root/);
  assert.match(markup, /Parallel group/);
  assert.match(markup, /video.webresearch/);
  assert.match(markup, /video.trendintelligence/);
  assert.match(markup, /video.analyst/);
  assert.match(markup, /video.judge/);
  assert.match(markup, /iter 3 \(pass\)/);
  assert.match(markup, /Selected span/);
  assert.match(markup, /Open Agent Detail/);
  assert.match(markup, /View in Execute/);
  assert.match(markup, /task-state|critique|approval/);
  assert.doesNotMatch(markup, /tenant_id|password=|authorization:\s*bearer/i);
  assert.doesNotMatch(markup, /localhost|redis:|kubectl|readiness/i);
});

test("monitoring fixture covers fleet, trace tree, alerts, anomalies, metrics", () => {
  assert.equal(LOCAL_MONITORING_LANDING.fleet.length, 5);
  assert.equal(LOCAL_MONITORING_LANDING.tabs.length, 4);
  assert.ok(LOCAL_MONITORING_LANDING.traceTree[0]?.children?.length);
  assert.equal(LOCAL_MONITORING_LANDING.alertRules.length, 3);
  assert.ok(
    LOCAL_MONITORING_LANDING.anomalies.some((item) => item.highRisk),
  );
  assert.equal(LOCAL_MONITORING_LANDING.metricBars.length, 3);
  assert.match(LOCAL_MONITORING_LANDING.eventTypesNote, /correlation/i);
});

test("monitoring CSS defines fleet, trace tree, inspector, and anomalies", async () => {
  const css = await readFile(
    resolve(componentDirectory, "../app/globals.css"),
    "utf8",
  );
  assert.match(css, /\.monitoring-home \{/);
  assert.match(css, /\.monitoring-home__fleet/);
  assert.match(css, /\.monitoring-home__tree/);
  assert.match(css, /\.monitoring-home__inspector/);
  assert.match(css, /\.monitoring-home__anomaly--risk/);
});

test("operations console CSS uses common-style tokens", async () => {
  const css = await readFile(
    resolve(componentDirectory, "../app/globals.css"),
    "utf8",
  );
  assert.match(css, /\.operations-console \{/);
  assert.match(css, /\.operations-console__btn--primary/);
  assert.match(css, /\.operations-console__live/);
  assert.match(css, /\.operations-page/);
});
