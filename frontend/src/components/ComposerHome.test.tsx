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

test("composer home matches ui_03 md/svg structure", () => {
  const markup = renderToStaticMarkup(<ComposerHome view={getScreenParameters("composer")} />);

  assert.match(markup, /Swarm Composer/);
  assert.match(markup, /pattern-first, NL-driven/);
  assert.match(markup, /Untitled Swarm from Parallel \+ Verification/);
  assert.match(markup, /Save Draft/);
  assert.match(markup, /Load Template/);
  assert.match(markup, /Common Swarm Architect/);
  assert.match(markup, /aria-expanded="true"/);
  assert.match(markup, /daily market intelligence swarm/);
  assert.match(markup, /Parallel Independent \+ Verification Loop/);
  assert.match(markup, /Recommended for goal/);
  assert.match(markup, /DataFetcher/);
  assert.match(markup, /VerifierNode/);
  assert.match(markup, /Load into Canvas/);
  assert.match(markup, /Fork &amp; Customize/);
  assert.match(markup, /Propose as new Pattern/);
  assert.match(markup, /Regenerate/);
  assert.match(markup, /Start from blank graph instead/);
  assert.match(markup, /Save this conversation as template/);
  assert.match(markup, /Daily market intelligence/);
  assert.match(markup, /Legacy COBOL analysis swarm/);
  assert.match(markup, /Describe your goal/);
  assert.match(markup, /type="file"/);
  assert.match(markup, /Common Pattern Browser/);
  assert.match(markup, /Search patterns/);
  assert.match(markup, /All domains/);
  assert.match(markup, /Verification Loop/);
  assert.match(markup, /Dynamic Router Graph/);
  assert.match(markup, /BIG ROWs/);
  assert.match(markup, /Live Preview/);
  assert.match(markup, /Total agents \/ slots/);
  assert.match(markup, /Parallelism factor/);
  assert.match(markup, /Verification coverage/);
  assert.match(markup, /Suggest new Common Pattern from my goal/);
  assert.match(markup, /linked_common_pattern_id/);
  assert.match(markup, /Browse Patterns/);
  assert.doesNotMatch(markup, /tenant_id|password=/i);
});

test("composer landing and local reply helpers cover recommend flow data", () => {
  assert.ok(LOCAL_COMPOSER_LANDING.patterns.some((pattern) => pattern.recommended));
  assert.equal(LOCAL_COMPOSER_LANDING.goalChips.length, 5);
  assert.equal(LOCAL_COMPOSER_LANDING.patterns.length, 4);
  assert.ok(
    LOCAL_COMPOSER_LANDING.patterns.every((pattern) => pattern.previewSummary.totalSlots),
  );
  const reply = buildLocalAssistantReply("stricter verification", LOCAL_COMPOSER_LANDING.patterns);
  assert.equal(reply.role, "assistant");
  assert.ok(reply.recommendation?.patternId);
  assert.match(reply.recommendation?.rationale ?? "", /stricter verification/);
});

test("composer CSS defines two-pane layout, mini graphs, and mobile sheet", async () => {
  const css = await readFile(
    resolve(componentDirectory, "../app/globals.css"),
    "utf8",
  );
  assert.match(css, /\.composer-home \{/);
  assert.match(css, /\.composer-home__layout \{/);
  assert.match(css, /\.composer-home__mini-graph/);
  assert.match(css, /\.composer-home__fab/);
  assert.match(css, /\.composer-home__browser--open/);
  assert.match(css, /@media \(max-width: 1080px\)/);
});
