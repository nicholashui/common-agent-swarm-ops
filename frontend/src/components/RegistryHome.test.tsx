import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import React from "react";
import { renderToStaticMarkup } from "react-dom/server";

import { LOCAL_REGISTRY_LANDING } from "../lib/projections/registry-landing";
import { RegistryHome } from "./RegistryHome";

const componentDirectory = dirname(fileURLToPath(import.meta.url));

test("registry home matches ui_07 md/svg structure", () => {
  const markup = renderToStaticMarkup(<RegistryHome />);

  assert.match(markup, /Common Registry/);
  assert.match(markup, /Battle-tested, versioned, collectively improved/);
  assert.match(markup, /Trading Lab/);
  assert.match(markup, /Search agents, patterns, or describe what you need/);
  assert.match(markup, /My Contributions/);
  assert.match(markup, /Pending Proposals/);
  assert.match(markup, /Suggest New/);
  assert.match(markup, /Trading/);
  assert.match(markup, /Content/);
  assert.match(markup, /Education/);
  assert.match(markup, /Distributed/);
  assert.match(markup, /Success rate &gt; 90%/);
  assert.match(markup, /Used in my swarms/);
  assert.match(markup, /High Verification/);
  assert.match(markup, />Cards</);
  assert.match(markup, />Table</);
  assert.match(markup, /Graph viz/);
  assert.match(markup, /Common Agents/);
  assert.match(markup, /MarketSentimentAgent/);
  assert.match(markup, /ContentDirectorAgent/);
  assert.match(markup, /VerificationLoopAgent/);
  assert.match(markup, /Common v3\.0/);
  assert.match(markup, /Add to Swarm/);
  assert.match(markup, /Propose/);
  assert.match(markup, /Detail/);
  assert.match(markup, /Core Common Swarm Patterns/);
  assert.match(markup, /BIG ROWs/);
  assert.match(markup, /Self-refine until quality passes/);
  assert.match(markup, /LLM router picks next node/);
  assert.match(markup, /Instantiate in Canvas/);
  assert.match(markup, /Registry Stats/);
  assert.match(markup, /Total Commons/);
  assert.match(markup, /Your Impact/);
  assert.match(markup, /\$412/);
  assert.match(markup, /CommonReportAgent/);
  assert.match(markup, /meta-critic/);
  assert.match(markup, /Review &amp; Merge/);
  assert.match(markup, /Proposal Review/);
  assert.match(markup, /Spec Diff \(redacted\)/);
  assert.match(markup, /max_iterations/);
  assert.match(markup, /Impact Analysis/);
  assert.match(markup, /Approve &amp; Merge/);
  assert.match(markup, /Request Changes/);
  assert.match(markup, /Reject/);
  assert.doesNotMatch(markup, /tenant_id|password=|authorization:\s*bearer/i);
});

test("registry landing fixture covers agents, patterns, proposals, impact", () => {
  assert.equal(LOCAL_REGISTRY_LANDING.agents.length, 3);
  assert.equal(LOCAL_REGISTRY_LANDING.patterns.length, 3);
  assert.equal(LOCAL_REGISTRY_LANDING.stats.length, 4);
  assert.equal(LOCAL_REGISTRY_LANDING.proposals.length, 2);
  assert.ok(
    LOCAL_REGISTRY_LANDING.agents.some((agent) => agent.isNew),
  );
  assert.ok(
    LOCAL_REGISTRY_LANDING.agents.every(
      (agent) => agent.category && agent.architecture,
    ),
  );
  assert.ok(
    LOCAL_REGISTRY_LANDING.reviewDiffLines.some((line) =>
      line.includes("verification_step"),
    ),
  );
});

test("registry CSS defines hub grid, cards, review, and sidebar", async () => {
  const css = await readFile(
    resolve(componentDirectory, "../app/globals.css"),
    "utf8",
  );
  assert.match(css, /\.registry-home \{/);
  assert.match(css, /\.registry-home__agent-grid/);
  assert.match(css, /\.registry-home__pattern-grid/);
  assert.match(css, /\.registry-home__review/);
  assert.match(css, /\.registry-home__sidebar/);
  assert.match(css, /\.registry-home__diff-add/);
});
