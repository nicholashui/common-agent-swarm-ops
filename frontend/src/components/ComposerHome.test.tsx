import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import React from "react";
import { renderToStaticMarkup } from "react-dom/server";

import {
  LOCAL_COMPOSER_LANDING,
  buildLocalAssistantReply,
} from "../lib/projections/composer-landing";
import { getScreenParameters } from "../lib/projections/screen-parameters";
import { ComposerHome } from "./ComposerHome";

const componentDirectory = dirname(fileURLToPath(import.meta.url));

test("composer ACC home matches redesign: requirements + workflow diagram", () => {
  const markup = renderToStaticMarkup(
    <ComposerHome view={getScreenParameters("composer")} />,
  );

  assert.match(markup, />Plan</);
  assert.doesNotMatch(markup, /PLAN · ACC/);
  assert.match(markup, /Untitled AI Swarm|swarm_name|Swarm name/i);
  assert.match(markup, /Form a multi-agent work/);
  assert.match(markup, /info-tooltip|About Plan|ⓘ/);
  assert.match(markup, /AI-pick mainly/);
  assert.match(markup, /AI Swarm Architect/);
  assert.match(markup, /Requirements/);
  assert.match(markup, /Available agents \(building blocks\)/i);
  assert.match(markup, /Human exception path \(needs_hitl\)/);
  assert.match(markup, /Generated workflow/);
  assert.match(markup, /Crew workflow diagram/);
  assert.match(markup, /Accept AI → Execute/);
  assert.match(markup, /AI plan/);
  assert.match(markup, /Materialize draft/);
  assert.match(markup, /Workflow diagram/);
  assert.match(markup, /Save Draft/);
  assert.match(markup, /AI plan &amp; bind|AI plan & bind/);
  assert.match(markup, /Execute inspect/);
  assert.match(markup, /Open sample requirements|Sample requirements/);
  assert.match(markup, /composer-home__samples-trigger|aria-haspopup="dialog"/);
  assert.doesNotMatch(markup, /YouTube wuxia short/);
  assert.match(markup, /type="file"/);
  assert.match(markup, /AI pattern context/);
  assert.match(markup, /closed world|catalog/i);
  assert.doesNotMatch(markup, /tenant_id|password=/i);
});

test("composer landing and local reply helpers cover recommend flow data", () => {
  assert.ok(LOCAL_COMPOSER_LANDING.patterns.some((pattern) => pattern.recommended));
  assert.ok(LOCAL_COMPOSER_LANDING.samples.length >= 5);
  assert.ok(
    LOCAL_COMPOSER_LANDING.samples.every(
      (s) => s.body.trim().length > 20 && s.label.length > 0,
    ),
  );
  assert.ok(
    LOCAL_COMPOSER_LANDING.samples.some((s) => s.kind === "hitl_demo"),
  );
  assert.equal(
    LOCAL_COMPOSER_LANDING.goalChips.length,
    LOCAL_COMPOSER_LANDING.samples.length,
  );
  assert.equal(LOCAL_COMPOSER_LANDING.patterns.length, 4);
  const reply = buildLocalAssistantReply(
    "stricter verification",
    LOCAL_COMPOSER_LANDING.patterns,
  );
  assert.equal(reply.role, "assistant");
  assert.ok(reply.recommendation?.patternId);
  assert.match(reply.recommendation?.rationale ?? "", /stricter verification/);
});

test("composer CSS defines ACC layout and workflow diagram surface", async () => {
  const css = await readFile(
    resolve(componentDirectory, "../app/globals.css"),
    "utf8",
  );
  assert.match(css, /\.composer-home \{/);
  assert.match(css, /\.composer-home__layout/);
  assert.match(css, /\.composer-home__layout--acc/);
  assert.match(css, /\.composer-home__workflow/);
  assert.match(css, /\.composer-home__wf-canvas/);
  assert.match(css, /\.composer-home__steps/);
  assert.match(css, /\.composer-home__hitl/);
});
