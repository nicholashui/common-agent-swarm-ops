import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import React from "react";
import { renderToStaticMarkup } from "react-dom/server";

import { LOCAL_ACTIVITY_LANDING } from "../lib/projections/activity-landing";
import { buildLiveActivityView } from "../lib/projections/activity-live";
import { ActivityHome } from "./ActivityHome";
// LOCAL_ACTIVITY_LANDING used for empty-host sample default test

const componentDirectory = dirname(fileURLToPath(import.meta.url));

test("activity home renders live Host feed projection", () => {
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
          summary: "Host draft event",
          subject_reference: "swarm_1",
          status: "recorded",
          occurred_at: "2026-06-01T12:00:00+00:00",
        },
      ],
    },
  });
  const markup = renderToStaticMarkup(<ActivityHome view={view} />);

  assert.match(markup, /Activity &amp; Ops Intelligence/);
  assert.match(markup, /Host organization/);
  assert.match(markup, /Host draft event/);
  assert.match(markup, /swarm_1/);
  assert.match(markup, /Show sample activity|Hide sample activity/);
  assert.match(markup, /Ops Intelligence/);
  assert.doesNotMatch(markup, /\$412|TradingResearch|CommonDataFetcher/);
  assert.doesNotMatch(markup, /tenant_id|password=|authorization:\s*bearer/i);
});

test("activity empty host defaults to sample data with toggle", () => {
  const empty = {
    ...LOCAL_ACTIVITY_LANDING,
    boardColumns: [],
    tableRows: [],
  };
  const markup = renderToStaticMarkup(<ActivityHome view={empty} />);
  assert.match(markup, /video\.webresearch|Wuxia Short · sample|Sample activity/i);
  assert.match(markup, /Hide sample activity|Show sample activity/);
});

test("activity landing shell has no fabricated fleet rows", () => {
  assert.equal(LOCAL_ACTIVITY_LANDING.boardColumns.length, 0);
  assert.equal(LOCAL_ACTIVITY_LANDING.tableRows.length, 0);
  assert.equal(LOCAL_ACTIVITY_LANDING.rolloutCards.length, 0);
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
});
