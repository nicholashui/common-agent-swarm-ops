import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import React from "react";
import { renderToStaticMarkup } from "react-dom/server";

import { LOCAL_MOBILE_LANDING } from "../lib/projections/mobile-landing";
import { getScreenParameters } from "../lib/projections/screen-parameters";
import { MobileHome } from "./MobileHome";

const componentDirectory = dirname(fileURLToPath(import.meta.url));

test("mobile home matches ui_17 md/svg structure", () => {
  const markup = renderToStaticMarkup(<MobileHome view={getScreenParameters("mobile")} />);

  assert.match(markup, /9:41/);
  assert.match(markup, /caso/);
  assert.match(markup, /Video Studio/);
  assert.match(markup, /Live · 6 running · 92% success/);
  assert.match(markup, /Running/);
  assert.match(markup, /Cost burn/);
  assert.match(markup, /Your Swarms/);
  assert.match(markup, /See all/);
  assert.match(markup, /Wuxia Short/);
  assert.match(markup, /Parallel \+ Verify v1\.4/);
  assert.match(markup, /Brand Spot/);
  assert.match(markup, /Hierarchical v2\.0/);
  assert.match(markup, /Execute|Canvas/);
  assert.match(markup, /Notifications/);
  assert.match(markup, /Approval gate/);
  assert.match(markup, /video.editor v3\.0/);
  assert.match(markup, /Approve/);
  assert.match(markup, /Review/);
  assert.match(markup, /Error spike/);
  assert.match(markup, /Quick Actions/);
  assert.match(markup, /Browse Commons/);
  assert.match(markup, /Plan Swarm/);
  assert.match(markup, />Home</);
  assert.match(markup, />Activity</);
  assert.match(markup, /Plan|Open Plan/);
  assert.match(markup, /Registry/);
  assert.match(markup, />More</);
  assert.match(markup, /server-issued IDs|redacted/);
  assert.doesNotMatch(markup, /tenant_id|password=|authorization:\s*bearer/i);
});

test("mobile fixture covers tabs data and high-risk signals", () => {
  assert.equal(LOCAL_MOBILE_LANDING.runningSwarms.length, 2);
  assert.equal(LOCAL_MOBILE_LANDING.notifications.length, 3);
  assert.ok(
    LOCAL_MOBILE_LANDING.notifications.some((n) => n.kind === "gate"),
  );
  assert.ok(
    LOCAL_MOBILE_LANDING.activity.some((a) => /blocked|self_refine/i.test(a.lifecycle)),
  );
  assert.equal(LOCAL_MOBILE_LANDING.registryHits.length, 2);
  assert.match(LOCAL_MOBILE_LANDING.safetyNote, /L1\/L2\/L3|rollback/i);
});

test("mobile CSS defines device frame, 44px targets, and bottom nav", async () => {
  const css = await readFile(
    resolve(componentDirectory, "../app/globals.css"),
    "utf8",
  );
  assert.match(css, /\.mobile-home \{/);
  assert.match(css, /\.mobile-home__device/);
  assert.match(css, /\.mobile-home__nav/);
  assert.match(css, /min-height: 44px/);
  assert.match(css, /\.mobile-home__sheet/);
});
