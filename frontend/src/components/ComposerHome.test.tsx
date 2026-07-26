import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import React from "react";
import { renderToStaticMarkup } from "react-dom/server";

import { LOCAL_COMPOSER_LANDING } from "../lib/projections/composer-landing";
import { ComposerHome } from "./ComposerHome";

const componentDirectory = dirname(fileURLToPath(import.meta.url));

test("composer home matches ui_03 chat + pattern browser structure", () => {
  const markup = renderToStaticMarkup(<ComposerHome />);

  assert.match(markup, /Swarm Composer/);
  assert.match(markup, /pattern-first, NL-driven/);
  assert.match(markup, /Untitled Swarm from Parallel \+ Verification/);
  assert.match(markup, /Save Draft/);
  assert.match(markup, /Load Template/);
  assert.match(markup, /Common Swarm Architect/);
  assert.match(markup, /daily market intelligence swarm/);
  assert.match(markup, /Parallel Independent \+ Verification Loop/);
  assert.match(markup, /Recommended for goal/);
  assert.match(markup, /DataFetcher/);
  assert.match(markup, /VerifierNode/);
  assert.match(markup, /Load into Canvas/);
  assert.match(markup, /Fork &amp; Customize/);
  assert.match(markup, /Propose as new Pattern/);
  assert.match(markup, /Daily market intelligence/);
  assert.match(markup, /Describe your goal/);
  assert.match(markup, /Common Pattern Browser/);
  assert.match(markup, /Search patterns/);
  assert.match(markup, /All domains/);
  assert.match(markup, /Hierarchical Supervisor/);
  assert.match(markup, /Instantiate in Canvas/);
  assert.doesNotMatch(markup, /tenant_id|credential|password=/i);
});

test("composer landing fixture includes recommended pattern and chips", () => {
  assert.ok(LOCAL_COMPOSER_LANDING.patterns.some((pattern) => pattern.recommended));
  assert.equal(LOCAL_COMPOSER_LANDING.goalChips.length, 4);
  assert.equal(LOCAL_COMPOSER_LANDING.messages.length, 2);
  assert.ok(LOCAL_COMPOSER_LANDING.messages[1]?.recommendation?.slots.length);
});

test("composer CSS defines two-pane light-frame layout", async () => {
  const css = await readFile(
    resolve(componentDirectory, "../app/globals.css"),
    "utf8",
  );
  assert.match(css, /\.composer-home \{/);
  assert.match(css, /\.composer-home__layout \{/);
  assert.match(css, /\.composer-home__browser/);
  assert.match(css, /@media \(max-width: 1080px\)/);
});
