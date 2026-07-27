import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import React from "react";
import { renderToStaticMarkup } from "react-dom/server";

import { PACK_AGENT_COUNTS } from "../lib/projections/pack-agents.generated";
import { LOCAL_REGISTRY_LANDING } from "../lib/projections/registry-landing";
import { getScreenParameters } from "../lib/projections/screen-parameters";
import { RegistryHome } from "./RegistryHome";

const componentDirectory = dirname(fileURLToPath(import.meta.url));

test("registry home lists all pack agents and specials catalog", () => {
  const markup = renderToStaticMarkup(<RegistryHome view={getScreenParameters("registry")} />);

  assert.match(markup, /Common Registry/);
  assert.match(markup, /All pack agents from self-contained folders \(133:/);
  assert.match(markup, /114 video/);
  assert.match(markup, /19 specials/);
  assert.match(markup, /Special Agents Pack/);
  assert.match(markup, /specials\.aesthetics-agent/);
  assert.match(markup, /draft · non-active/);
  assert.match(markup, /Pack catalog/);
  assert.match(markup, /Search agent id, name, pack, role/);
  assert.match(markup, /My Contributions/);
  assert.match(markup, /Pending Proposals/);
  assert.match(markup, /Suggest New/);
  assert.match(markup, />video</);
  assert.match(markup, />specials</);
  assert.match(markup, />Cards</);
  assert.match(markup, />Table</);
  assert.match(markup, /Graph viz/);
  assert.match(markup, /Common Agents/);
  // Progressive window: first page of cards may not include every id (e.g. orchestrator).
  assert.match(markup, /Showing <strong>133<\/strong> of 133/);
  assert.match(markup, /Show more \(36 of 133\)/);
  assert.match(markup, /Add to Swarm/);
  assert.match(markup, /Propose/);
  assert.match(markup, /Detail/);
  assert.match(markup, /Core Common Swarm Patterns/);
  assert.match(markup, /Registry Stats/);
  assert.match(markup, /Total agents/);
  assert.match(markup, /self-contained/);
  assert.match(markup, /View agent settings/);
  assert.doesNotMatch(markup, /tenant_id|password=|authorization:\s*bearer/i);
  // Catalog still contains orchestrator even if not in the first window.
  assert.ok(
    LOCAL_REGISTRY_LANDING.agents.some(
      (a) => /orchestrator/i.test(a.id) || /orchestrator/i.test(a.name),
    ),
  );
});

test("registry landing covers all pack agents, patterns, proposals", () => {
  assert.equal(LOCAL_REGISTRY_LANDING.agents.length, PACK_AGENT_COUNTS.total);
  assert.equal(LOCAL_REGISTRY_LANDING.agents.length, 133);
  assert.equal(PACK_AGENT_COUNTS.video, 114);
  assert.equal(PACK_AGENT_COUNTS.specials, 19);
  assert.equal(LOCAL_REGISTRY_LANDING.patterns.length, 3);
  assert.equal(LOCAL_REGISTRY_LANDING.stats.length, 4);
  assert.equal(LOCAL_REGISTRY_LANDING.proposals.length, 0);
  assert.ok(
    LOCAL_REGISTRY_LANDING.agents.every(
      (agent) => agent.category && agent.architecture && agent.id.includes("."),
    ),
  );
  assert.ok(
    LOCAL_REGISTRY_LANDING.agents.some((agent) => agent.id.startsWith("video.")),
  );
  assert.ok(
    LOCAL_REGISTRY_LANDING.agents.some((agent) => agent.id.startsWith("specials.")),
  );
  assert.equal(
    LOCAL_REGISTRY_LANDING.agents.filter((a) => a.id.startsWith("video.")).length,
    114,
  );
  assert.equal(
    LOCAL_REGISTRY_LANDING.agents.filter((a) => a.id.startsWith("specials.")).length,
    19,
  );
  assert.ok(
    LOCAL_REGISTRY_LANDING.agents.every(
      (agent) =>
        !/market-sentiment|content-director|verification-loop/i.test(agent.id),
    ),
  );
  assert.ok(
    LOCAL_REGISTRY_LANDING.reviewDiffLines.some((line) =>
      line.includes("No demo proposal"),
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
  assert.match(css, /\.registry-home__result-meta/);
  assert.match(css, /\.registry-home__graph-canvas/);
});

test("registry home exposes interactive search and mode controls", () => {
  const markup = renderToStaticMarkup(
    <RegistryHome view={getScreenParameters("registry")} />,
  );
  assert.match(markup, /name="registry-search"/);
  assert.match(markup, /type="search"/);
  assert.match(markup, /Showing <strong>133<\/strong> of 133/);
  assert.match(markup, /data-registry-view="cards"/);
  assert.match(markup, /aria-pressed="true"[^>]*>Cards/);
  assert.match(markup, /registry-home__facet/);
});
