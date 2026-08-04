import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import React from "react";
import { renderToStaticMarkup } from "react-dom/server";

import { LOCAL_CANVAS_LANDING } from "../lib/projections/canvas-landing";
import { getScreenParameters } from "../lib/projections/screen-parameters";
import { CanvasHome } from "./CanvasHome";

const componentDirectory = dirname(fileURLToPath(import.meta.url));

test("canvas orchestration board matches ui_04 redesign", () => {
  const markup = renderToStaticMarkup(
    <CanvasHome view={getScreenParameters("canvas")} />,
  );

  assert.match(markup, /Wuxia Short/);
  assert.match(markup, /Hierarchical \+ Verify/);
  assert.match(markup, /Design/);
  assert.match(markup, /Inspect/);
  assert.match(markup, /Run/);
  assert.match(markup, /Instance lifecycle|INSTANCE LIFECYCLE|Plan created workflow/i);
  assert.match(markup, /Materialized draft instance/);
  assert.match(markup, /Execute inspect \/ run board/);
  assert.match(markup, /Host run \(fail-closed\)/);
  assert.match(markup, /WORKFLOW DIAGRAM|Crew workflow/i);
  assert.match(markup, /Crew workflow/);
  assert.match(markup, /CREW MEMBERS|crew members/i);
  assert.match(markup, /Open sample instances|Sample instances|samples-trigger/i);
  assert.match(markup, /Fail-closed run/);
  assert.match(markup, /Edit in Plan/);
  assert.match(markup, /Run instance/);
  assert.match(markup, /Human board|Orchestrator agent|Host owns/i);
  assert.match(markup, /info-tooltip|About|ⓘ/);
  assert.match(markup, /RUN READINESS|Run readiness/i);
  assert.match(markup, /Validate graph/);
  assert.match(markup, /Activity/);
  assert.match(markup, /video.webresearch/);
  assert.match(markup, /video.judge/);
  assert.match(markup, /Layout/);
  assert.match(markup, /Export/);
  assert.match(markup, /Cancel/);
  assert.match(markup, />Task</);
  assert.match(markup, /Returned validation/);
  assert.doesNotMatch(markup, /tenant_id|password=/i);
});

test("canvas landing fixture includes orchestration instance meta", () => {
  assert.equal(LOCAL_CANVAS_LANDING.viewMode, "inspect");
  assert.ok(LOCAL_CANVAS_LANDING.instanceId);
  assert.equal(LOCAL_CANVAS_LANDING.groups.length, 2);
  assert.ok(LOCAL_CANVAS_LANDING.nodes.some((node) => node.kind === "supervisor"));
  assert.ok(LOCAL_CANVAS_LANDING.nodes.some((node) => node.kind === "verifier"));
  assert.equal(LOCAL_CANVAS_LANDING.inspectorTabs.length, 5);
});

test("canvas CSS defines orchestration shell", async () => {
  const css = await readFile(
    resolve(componentDirectory, "../app/globals.css"),
    "utf8",
  );
  assert.match(css, /\.canvas-home \{/);
  assert.match(css, /\.canvas-home__body--orch/);
  assert.match(css, /\.canvas-home__lifecycle/);
  assert.match(css, /\.canvas-home__workflow-panel/);
  assert.match(css, /\.workflow-diagram/);
  assert.match(css, /\.canvas-home__runbar/);
});
