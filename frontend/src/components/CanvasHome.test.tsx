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

test("canvas home matches ui_04 toolbar, palette, BIG ROW, and inspector", () => {
  const markup = renderToStaticMarkup(<CanvasHome />);

  assert.match(markup, /TradingResearch α/);
  assert.match(markup, /Parallel Indep\. \+ Verify v1\.4/);
  assert.match(markup, /Design/);
  assert.match(markup, /Run/);
  assert.match(markup, /Compare/);
  assert.match(markup, /12\/14 on latest common/);
  assert.match(markup, /Co-Pilot/);
  assert.match(markup, /Layout/);
  assert.match(markup, /Export/);
  assert.match(markup, /▶ Run/);
  assert.match(markup, /A\/B Test/);
  assert.match(markup, /Common/);
  assert.match(markup, /Custom/);
  assert.match(markup, /Patterns/);
  assert.match(markup, /AI Suggest Node/);
  assert.match(markup, /DataFetcher/);
  assert.match(markup, /VerifierNode/);
  assert.match(markup, /CustomReportAgent/);
  assert.match(markup, /Parallel Data &amp; Analysis \(BIG ROW\)/);
  assert.match(markup, /Update all →/);
  assert.match(markup, /Registry-linked/);
  assert.match(markup, /Graph relationship semantics|Edges/);
  assert.match(markup, /Data flow/);
  assert.match(markup, /Iteration/);
  assert.match(markup, /SELECTED NODE|DataFetcher/);
  assert.match(markup, /Returned validation/);
  assert.match(markup, /tool_policy/);
  assert.doesNotMatch(markup, /tenant_id|password=/i);
});

test("canvas landing fixture includes group, palette, and validation", () => {
  assert.equal(LOCAL_CANVAS_LANDING.groups.length, 1);
  assert.ok(LOCAL_CANVAS_LANDING.nodes.length >= 4);
  assert.ok(LOCAL_CANVAS_LANDING.edges.length >= 3);
  assert.ok(LOCAL_CANVAS_LANDING.validation.some((item) => item.category === "verification"));
  assert.ok(LOCAL_CANVAS_LANDING.palette.some((item) => item.tab === "custom"));
});

test("canvas CSS defines three-column shell and BIG ROW group", async () => {
  const css = await readFile(
    resolve(componentDirectory, "../app/globals.css"),
    "utf8",
  );
  assert.match(css, /\.canvas-home \{/);
  assert.match(css, /\.canvas-home__body \{/);
  assert.match(css, /\.canvas-home__group/);
  assert.match(css, /\.canvas-home__palette/);
  assert.match(css, /@media \(max-width: 760px\)/);
});
