import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import React from "react";
import { renderToStaticMarkup } from "react-dom/server";

import { LOCAL_CANVAS_LANDING } from "../lib/projections/canvas-landing";
import { CanvasHome } from "./CanvasHome";

const componentDirectory = dirname(fileURLToPath(import.meta.url));

test("canvas home matches ui_04 md/svg structure", () => {
  const markup = renderToStaticMarkup(<CanvasHome />);

  assert.match(markup, /TradingResearch α/);
  assert.match(markup, /Parallel Indep\. \+ Verify v1\.4/);
  assert.match(markup, /Design/);
  assert.match(markup, /Run/);
  assert.match(markup, /Compare/);
  assert.match(markup, /12\/14 on latest common/);
  assert.match(markup, /Co-Pilot/);
  // Co-Pilot menu starts collapsed; actions live in the fixture until opened.
  assert.match(markup, /aria-expanded="false"/);
  assert.doesNotMatch(markup, /Optimize tokens/);
  assert.match(markup, /Layout/);
  assert.match(markup, /Focus/);
  assert.match(markup, /Export/);
  assert.match(markup, /▶ Run/);
  assert.match(markup, /A\/B Test/);
  assert.match(markup, /AI Suggest Node/);
  assert.match(markup, /DataFetcher/);
  assert.match(markup, /VerifierNode/);
  // Custom agent appears on the board (not only Custom palette tab).
  assert.match(markup, /CustomReportAgent/);
  assert.match(markup, /Parallel Data &amp; Analysis \(BIG ROW\)/);
  assert.match(markup, /Synthesis \+ Verification/);
  assert.match(markup, /cycle ↺/);
  assert.match(markup, /Supervisor/);
  assert.match(markup, /Dynamic Router/);
  assert.match(markup, /Registry-linked|Custom — contribute back/);
  assert.match(markup, /Iteration|Data flow/);
  assert.match(markup, /Partial replay/);
  assert.match(markup, /Cancel/);
  assert.match(markup, /≡ logs/);
  assert.match(markup, /Aggregate eval/);
  assert.match(markup, /Improvement history/);
  assert.match(markup, /Update to latest safe/);
  assert.match(markup, /Pin version/);
  assert.match(markup, /Propose imp/);
  assert.match(markup, /Open Detail \(nn_ui_05\)/);
  assert.match(markup, /Live Inspector/);
  assert.match(markup, /groundedness below 0\.9/);
  assert.match(markup, />Task</);
  assert.match(markup, />Artifacts</);
  assert.match(markup, />Critique</);
  assert.match(markup, />Quality</);
  assert.match(markup, />Provenance</);
  assert.match(markup, /Returned validation/);
  assert.doesNotMatch(markup, /tenant_id|password=/i);
});

test("canvas landing fixture includes both groups and special nodes", () => {
  assert.equal(LOCAL_CANVAS_LANDING.groups.length, 2);
  assert.ok(LOCAL_CANVAS_LANDING.nodes.some((node) => node.kind === "supervisor"));
  assert.ok(LOCAL_CANVAS_LANDING.nodes.some((node) => node.kind === "router"));
  assert.ok(LOCAL_CANVAS_LANDING.nodes.some((node) => node.kind === "verifier"));
  assert.ok(LOCAL_CANVAS_LANDING.nodes.some((node) => node.kind === "custom"));
  assert.equal(LOCAL_CANVAS_LANDING.inspectorTabs.length, 5);
  assert.deepEqual(
    [...LOCAL_CANVAS_LANDING.inspectorTabs.map((tab) => tab.id)],
    ["task", "artifacts", "critique", "quality", "provenance"],
  );
  assert.ok(
    LOCAL_CANVAS_LANDING.copilotActions.includes("Optimize tokens"),
  );
  assert.ok(
    LOCAL_CANVAS_LANDING.copilotActions.includes(
      "Propose as new Common Pattern",
    ),
  );
  assert.ok(LOCAL_CANVAS_LANDING.copilotActions.length >= 3);
  assert.equal(LOCAL_CANVAS_LANDING.groups[0]?.tone, "parallel");
  assert.equal(LOCAL_CANVAS_LANDING.groups[1]?.tone, "verification");
});

test("canvas CSS defines three-column shell, overlays, and run bar", async () => {
  const css = await readFile(
    resolve(componentDirectory, "../app/globals.css"),
    "utf8",
  );
  assert.match(css, /\.canvas-home \{/);
  assert.match(css, /\.canvas-home__group--verification/);
  assert.match(css, /\.canvas-home__minimap/);
  assert.match(css, /\.canvas-home__runbar/);
  assert.match(css, /\.canvas-home__live/);
  assert.match(css, /\.canvas-home--focus/);
});
