import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import React from "react";
import { renderToStaticMarkup } from "react-dom/server";

import {
  BLUEPRINT_SAMPLES,
  LOCAL_BLUEPRINTS_LANDING,
} from "../lib/projections/blueprints-landing";
import { BlueprintsHome } from "./BlueprintsHome";

const componentDirectory = dirname(fileURLToPath(import.meta.url));

test("blueprints home shows sample blueprints and use-sample control", () => {
  const markup = renderToStaticMarkup(
    <BlueprintsHome view={LOCAL_BLUEPRINTS_LANDING} />,
  );

  assert.match(markup, /Blueprints &amp; Templates Gallery/);
  assert.match(markup, /Show sample blueprints|Hide sample blueprints/);
  assert.match(markup, /blueprints-home__samples-icon|▦/);
  assert.match(markup, /Wuxia Short Pipeline/);
  assert.match(markup, /Trend research → script|Trend research/);
  assert.match(markup, /Social under budget/);
  assert.match(markup, /Brand spot \+ compliance/);
  assert.match(markup, /video\.judge@v1|video\.screenwriter/);
  assert.match(markup, /Deploy to Workspace|Publish Blueprint/);
  assert.match(markup, /Create Your Own Blueprint/);
  assert.doesNotMatch(markup, /tenant_id|password=|authorization:\s*bearer/i);
  assert.doesNotMatch(markup, /production-ready|114 agents active|migration complete/i);
});

test("blueprint samples are video-pack only", () => {
  assert.equal(BLUEPRINT_SAMPLES.length, 4);
  assert.ok(BLUEPRINT_SAMPLES.every((bp) => bp.pins.length > 0));
  assert.ok(
    BLUEPRINT_SAMPLES.every((bp) =>
      bp.pins.every((pin) => pin.startsWith("video.")),
    ),
  );
  assert.ok(BLUEPRINT_SAMPLES.some((bp) => bp.featured));
  assert.equal(LOCAL_BLUEPRINTS_LANDING.blueprints.length, 4);
  assert.equal(LOCAL_BLUEPRINTS_LANDING.showingSamples, true);
});

test("blueprints CSS defines gallery, cards, preview, sample control", async () => {
  const css = await readFile(
    resolve(componentDirectory, "../app/globals.css"),
    "utf8",
  );
  assert.match(css, /\.blueprints-home \{/);
  assert.match(css, /\.blueprints-home__samples-icon/);
  assert.match(css, /\.blueprints-home__sample-banner/);
});
