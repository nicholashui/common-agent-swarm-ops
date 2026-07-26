import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import React from "react";
import { renderToStaticMarkup } from "react-dom/server";

import { LOCAL_BLUEPRINTS_LANDING } from "../lib/projections/blueprints-landing";
import { BlueprintsHome } from "./BlueprintsHome";

const componentDirectory = dirname(fileURLToPath(import.meta.url));

test("blueprints home matches ui_20 md/svg structure", () => {
  const markup = renderToStaticMarkup(<BlueprintsHome />);

  assert.match(markup, /Blueprints &amp; Templates Gallery/);
  assert.match(markup, /Swarm blueprint gallery|local presentation/i);
  assert.match(markup, /Publish Blueprint/);
  assert.match(markup, /Search blueprints or describe your use case/);
  assert.match(markup, /All \(24\)/);
  assert.match(markup, /Trading/);
  assert.match(markup, /Content/);
  assert.match(markup, /Education/);
  assert.match(markup, /Research/);
  assert.match(markup, /Most deployed/);
  assert.match(markup, /Highest rated/);
  assert.match(markup, /Featured/);
  assert.match(markup, /Market Intelligence Pipeline/);
  assert.match(markup, /Parallel \+ Verify v1\.4/);
  assert.match(markup, /8 Common Agents/);
  assert.match(markup, /Trading Corpus/);
  assert.match(markup, /312 deployments/);
  assert.match(markup, /Deploy to Workspace/);
  assert.match(markup, /Cinematic Content Pipeline/);
  assert.match(markup, /DSE Adaptive Tutor/);
  assert.match(markup, /Legacy Code Modernizer/);
  assert.match(markup, /β Beta|beta/);
  assert.match(markup, /Create Your Own Blueprint/);
  assert.match(markup, /Save Current Swarm as Blueprint/);
  assert.match(markup, /Import from JSON \/ YAML/);
  assert.match(markup, /Publishing requires evaluation pass/);
  assert.match(markup, /Pinned versions|DataFetcher@v2\.1/);
  assert.match(markup, /does not copy opaque tool credentials|cannot.*bypass/);
  assert.match(markup, /pack_spine|registered\/non-active|not blueprint realization/i);
  assert.doesNotMatch(markup, /tenant_id|password=|authorization:\s*bearer/i);
  assert.doesNotMatch(markup, /production-ready|114 agents active|migration complete/i);
});

test("blueprints fixture covers gallery cards, pins, and safety", () => {
  assert.equal(LOCAL_BLUEPRINTS_LANDING.blueprints.length, 4);
  assert.ok(
    LOCAL_BLUEPRINTS_LANDING.blueprints.some((bp) => bp.featured),
  );
  assert.ok(
    LOCAL_BLUEPRINTS_LANDING.blueprints.every((bp) => bp.pins.length > 0),
  );
  assert.ok(
    LOCAL_BLUEPRINTS_LANDING.blueprints.some((bp) => bp.governance === "beta"),
  );
  assert.match(LOCAL_BLUEPRINTS_LANDING.safetyNote, /new graph revision/i);
  assert.match(LOCAL_BLUEPRINTS_LANDING.publishNote, /evaluation pass/i);
  assert.match(LOCAL_BLUEPRINTS_LANDING.migrationNote, /pack_spine|non-active/i);
  const cinematic = LOCAL_BLUEPRINTS_LANDING.blueprints.find((bp) => bp.id === "cinematic");
  assert.ok(cinematic?.maturityLabel);
  assert.match(cinematic.maturityLabel, /cataloged|registered/i);
});

test("blueprints CSS defines gallery, cards, preview, and detail", async () => {
  const css = await readFile(
    resolve(componentDirectory, "../app/globals.css"),
    "utf8",
  );
  assert.match(css, /\.blueprints-home \{/);
  assert.match(css, /\.blueprints-home__card/);
  assert.match(css, /\.blueprints-home__preview/);
  assert.match(css, /\.blueprints-home__detail/);
  assert.match(css, /\.blueprints-home__create/);
});
