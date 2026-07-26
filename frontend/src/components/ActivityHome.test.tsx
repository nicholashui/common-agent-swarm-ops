import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import React from "react";
import { renderToStaticMarkup } from "react-dom/server";

import { LOCAL_ACTIVITY_LANDING } from "../lib/projections/activity-landing";
import { ActivityHome } from "./ActivityHome";

const componentDirectory = dirname(fileURLToPath(import.meta.url));

test("activity home matches ui_06 md/svg structure", () => {
  const markup = renderToStaticMarkup(<ActivityHome />);

  assert.match(markup, /Activity &amp; Ops Intelligence/);
  assert.match(markup, /Trading Lab/);
  assert.match(markup, /Search run ID, agent, error, output/);
  assert.match(markup, /Last 7 days/);
  assert.match(markup, />Board</);
  assert.match(markup, />Table</);
  assert.match(markup, />Timeline</);
  assert.match(markup, /Live Update/);
  assert.match(markup, /Common Agent \/ Version/);
  assert.match(markup, /Only outdated common versions/);
  assert.match(markup, /Contributed to commons\?/);
  assert.match(markup, /Data Ingestion/);
  assert.match(markup, /Parallel Pattern v1\.4/);
  assert.match(markup, /CommonDataFetcher/);
  assert.match(markup, /CommonCleaner/);
  assert.match(markup, /Analysis \+ Verification/);
  assert.match(markup, /Verification Loop v1\.2/);
  assert.match(markup, /CommonSentiment/);
  assert.match(markup, /VerifierNode/);
  assert.match(markup, /iter 3\/5/);
  assert.match(markup, /Synthesis \+ Report/);
  assert.match(markup, /CustomReportAgent/);
  assert.match(markup, /Replay latest/);
  assert.match(markup, /View in Canvas/);
  assert.match(markup, /Ops Intelligence/);
  assert.match(markup, /Total runs/);
  assert.match(markup, /Rollout Opportunities/);
  assert.match(markup, /CommonVerifier v1\.8/);
  assert.match(markup, /Safe to rollout to your 12 swarms/);
  assert.match(markup, /Anomaly/);
  assert.match(markup, /CommonReportAgent/);
  assert.match(markup, /Collective Improvement Impact/);
  assert.match(markup, /\$412/);
  assert.match(markup, /Bulk replay w\/ latest/);
  assert.match(markup, /Create improvement proposal/);
  assert.match(markup, /as_of 04:12Z/);
  assert.match(markup, /corr b7f2c9d0/);
  assert.match(markup, /immutable version provenance/);
  assert.doesNotMatch(markup, /tenant_id|password=|authorization:\s*bearer/i);
});

test("activity landing fixture covers board, table, timeline, insights", () => {
  assert.equal(LOCAL_ACTIVITY_LANDING.boardColumns.length, 3);
  assert.ok(
    LOCAL_ACTIVITY_LANDING.boardColumns.every(
      (column) => column.cards.length >= 2,
    ),
  );
  assert.equal(LOCAL_ACTIVITY_LANDING.tableRows.length, 4);
  assert.ok(
    LOCAL_ACTIVITY_LANDING.tableRows.every(
      (row) => row.graphRevision && row.checkpoint && row.lifecycle,
    ),
  );
  assert.equal(LOCAL_ACTIVITY_LANDING.timelineLanes.length, 3);
  assert.equal(LOCAL_ACTIVITY_LANDING.kpis.length, 3);
  assert.equal(LOCAL_ACTIVITY_LANDING.rolloutCards.length, 2);
  assert.ok(
    LOCAL_ACTIVITY_LANDING.rolloutCards.some((card) => card.tone === "anomaly"),
  );
});

test("activity CSS defines board, table, timeline, and insights layout", async () => {
  const css = await readFile(
    resolve(componentDirectory, "../app/globals.css"),
    "utf8",
  );
  assert.match(css, /\.activity-home \{/);
  assert.match(css, /\.activity-home__board/);
  assert.match(css, /\.activity-home__table/);
  assert.match(css, /\.activity-home__timeline/);
  assert.match(css, /\.activity-home__insights/);
  assert.match(css, /\.activity-home__rollout--anomaly/);
});
