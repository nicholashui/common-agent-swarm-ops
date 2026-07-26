import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import React from "react";
import { renderToStaticMarkup } from "react-dom/server";

import {
  AGENT_DETAIL_TABS,
  LOCAL_AGENT_DETAIL_LANDING,
} from "../lib/projections/agent-detail-landing";
import { getScreenParameters } from "../lib/projections/screen-parameters";
import { AgentDetailHome } from "./AgentDetailHome";

const componentDirectory = dirname(fileURLToPath(import.meta.url));

test("agent detail home matches ui_05 md/svg structure", () => {
  const markup = renderToStaticMarkup(
    <AgentDetailHome agentId="local-preview" view={getScreenParameters("agentDetail")} />,
  );

  assert.match(markup, /VerificationLoopAgent/);
  assert.match(markup, /Common v3\.0/);
  assert.match(markup, /31\.2k/);
  assert.match(markup, /97%/);
  assert.match(markup, /improvement velocity \+12%\/mo/);
  assert.match(markup, /Propose Improvement/);
  assert.match(markup, /A\/B Test vs newer/);
  assert.match(markup, /Fork to Custom/);
  assert.match(markup, /Pin \/ Update in swarms/);
  assert.match(markup, /Open in Registry Hub/);
  assert.match(markup, /Run Playground/);
  assert.match(markup, /History \+ Cross-Swarm Usage/);
  assert.match(markup, /Config \/ Spec/);
  assert.match(markup, /Playground/);
  assert.match(markup, /Knowledge/);
  assert.match(markup, /Ops &amp; Rollout/);
  assert.match(markup, /Used in 47 active swarms globally/);
  assert.match(markup, /View full cross-swarm impact/);
  assert.match(markup, /All swarms/);
  assert.match(markup, /Has error\?/);
  assert.match(markup, /TradingResearch α/);
  assert.match(markup, /ContentPipeline β/);
  assert.match(markup, /DSE Tutor Fleet/);
  assert.match(markup, /Replay ↻/);
  assert.match(markup, /Server-side pagination/);
  assert.match(markup, /Opaque reference: local-preview/);
  // Default tab is history — config/ops-only labels stay in fixture until selected.
  assert.doesNotMatch(markup, /tenant_id|password=|authorization:\s*bearer/i);
  assert.doesNotMatch(markup, /raw prompt|api[_-]?key/i);
});

test("agent detail fixture covers all five tabs and VA-aligned config", () => {
  assert.equal(AGENT_DETAIL_TABS.length, 5);
  assert.deepEqual(
    AGENT_DETAIL_TABS.map((tab) => tab.id),
    ["history", "config", "playground", "knowledge", "ops"],
  );
  assert.equal(LOCAL_AGENT_DETAIL_LANDING.usageRows.length, 6);
  assert.equal(LOCAL_AGENT_DETAIL_LANDING.versions.length, 4);
  assert.ok(
    LOCAL_AGENT_DETAIL_LANDING.configSummaries.some((section) =>
      section.lines.some((line) => line.includes("accepts_critique_from")),
    ),
  );
  assert.ok(
    LOCAL_AGENT_DETAIL_LANDING.configSummaries.some((section) =>
      section.lines.some((line) => line.includes("L1 structure")),
    ),
  );
  assert.ok(
    LOCAL_AGENT_DETAIL_LANDING.knowledgeSources.some(
      (source) => source.type === "correction memory",
    ),
  );
  assert.match(LOCAL_AGENT_DETAIL_LANDING.opsAlert, /Canary recommended/);
  assert.equal(LOCAL_AGENT_DETAIL_LANDING.evalScores.length, 4);
});

test("agent detail CSS defines header, tabs, table, and ops styles", async () => {
  const css = await readFile(
    resolve(componentDirectory, "../app/globals.css"),
    "utf8",
  );
  assert.match(css, /\.agent-detail \{/);
  assert.match(css, /\.agent-detail__tabs/);
  assert.match(css, /\.agent-detail__table/);
  assert.match(css, /\.agent-detail__playground/);
  assert.match(css, /\.agent-detail__ops-alert/);
  assert.match(css, /\.agent-detail__version--current/);
});
