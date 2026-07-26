import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import React from "react";
import { renderToStaticMarkup } from "react-dom/server";

import { LOCAL_EVAL_LANDING } from "../lib/projections/eval-landing";
import { getScreenParameters } from "../lib/projections/screen-parameters";
import { EvalHome } from "./EvalHome";

const componentDirectory = dirname(fileURLToPath(import.meta.url));

test("eval home matches ui_11 md/svg structure", () => {
  const markup = renderToStaticMarkup(<EvalHome view={getScreenParameters("eval")} />);

  assert.match(markup, /Eval &amp; Self-Improvement Dashboard/);
  assert.match(markup, /Evidence-based L1\/L2\/L3/);
  assert.match(markup, /Search commons, proposals/);
  assert.match(markup, /Global success/);
  assert.match(markup, /Token efficiency/);
  assert.match(markup, /Verifier pass rate/);
  assert.match(markup, /Proposals merged \/mo/);
  assert.match(markup, /Held-out coverage/);
  assert.match(markup, /Score Trends \(L1 \/ L2 \/ L3\)/);
  assert.match(markup, /L1 validation/);
  assert.match(markup, /Aggregate scores never hide a failed lower-layer gate/);
  assert.match(markup, /Meta-Critic Insights/);
  assert.match(markup, /Top failure mode/);
  assert.match(markup, /Token waste hotspot/);
  assert.match(markup, /Suggested pattern change/);
  assert.match(markup, /Proposal Queue/);
  assert.match(markup, /CommonReportAgent/);
  assert.match(markup, /CommonMarketPredictor/);
  assert.match(markup, /CommonDataFetcher/);
  assert.match(markup, /CommonSentiment/);
  assert.match(markup, /Campaign Launcher/);
  assert.match(markup, /Run Batch Eval Campaign/);
  assert.match(markup, /Improvement History/);
  assert.match(markup, /A\/B/);
  assert.match(markup, /VerifierNode v2\.9/);
  assert.match(markup, /ReportAgent v3\.0 vs v2\.9/);
  assert.match(markup, /Promote winner/);
  assert.match(markup, /does not publish|canary/);
  assert.doesNotMatch(markup, /tenant_id|password=|authorization:\s*bearer/i);
});

test("eval fixture covers scorecards, proposals, history, experiments, layers", () => {
  assert.equal(LOCAL_EVAL_LANDING.scorecards.length, 5);
  assert.equal(LOCAL_EVAL_LANDING.proposals.length, 4);
  assert.equal(LOCAL_EVAL_LANDING.history.length, 2);
  assert.equal(LOCAL_EVAL_LANDING.experiments.length, 1);
  assert.equal(LOCAL_EVAL_LANDING.insights.length, 3);
  assert.match(LOCAL_EVAL_LANDING.layerNote, /L1|L2|L3/);
  assert.match(LOCAL_EVAL_LANDING.campaignNote, /does not publish/i);
  assert.match(LOCAL_EVAL_LANDING.evidenceNote, /held-out/i);
});

test("eval CSS defines scorecards, queue, campaign, and history", async () => {
  const css = await readFile(
    resolve(componentDirectory, "../app/globals.css"),
    "utf8",
  );
  assert.match(css, /\.eval-home \{/);
  assert.match(css, /\.eval-home__scorecards/);
  assert.match(css, /\.eval-home__proposals/);
  assert.match(css, /\.eval-home__campaign/);
  assert.match(css, /\.eval-home__history/);
});
