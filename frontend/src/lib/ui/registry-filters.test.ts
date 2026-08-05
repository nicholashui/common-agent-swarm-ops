import assert from "node:assert/strict";
import test from "node:test";

import { LOCAL_REGISTRY_LANDING } from "../projections/registry-landing";
import { SPECIAL_AGENT_CATALOG } from "../specials/specials-catalog";
import {
  agentMatchesFacet,
  agentMatchesSearch,
  filterRegistryAgents,
  filterRegistryPatterns,
  filterSpecialAgents,
  toggleFacetSelection,
} from "./registry-filters";

const agents = LOCAL_REGISTRY_LANDING.agents;
const domains = LOCAL_REGISTRY_LANDING.domainFacets;

test("registry search finds orchestrator by name/id tokens", () => {
  const hits = filterRegistryAgents(agents, "orchestrator", new Set(), domains);
  assert.ok(hits.length >= 1);
  assert.ok(hits.some((agent) => /orchestrator/i.test(agent.id + agent.name)));
});

test("registry video facet returns only video pack agents", () => {
  const hits = filterRegistryAgents(agents, "", new Set(["video"]), domains);
  assert.equal(hits.length, 114);
  assert.ok(hits.every((agent) => agentMatchesFacet(agent, "video")));
});

test("registry specials facet returns only specials pack agents", () => {
  const hits = filterRegistryAgents(agents, "", new Set(["specials"]), domains);
  assert.equal(hits.length, 19);
  assert.ok(hits.every((agent) => agentMatchesFacet(agent, "specials")));
});

test("registry domain facets are OR (video+specials keeps both packs)", () => {
  const hits = filterRegistryAgents(
    agents,
    "",
    new Set(["video", "specials"]),
    domains,
  );
  assert.equal(hits.length, 133);
});

test("registry draft facet matches specials draft badges", () => {
  const hits = filterRegistryAgents(agents, "", new Set(["draft"]), domains);
  assert.ok(hits.length >= 1);
  assert.ok(hits.every((agent) => agentMatchesFacet(agent, "draft")));
});

test("registry search + facet compose", () => {
  const hits = filterRegistryAgents(
    agents,
    "video.",
    new Set(["video"]),
    domains,
  );
  assert.ok(hits.length > 0);
  assert.ok(hits.every((agent) => agent.id.startsWith("video.")));
});

test("registry multi-token search is AND", () => {
  const any = agents.find((agent) => agentMatchesSearch(agent, agent.name.split(/\s+/)[0] ?? ""));
  assert.ok(any);
  const impossible = filterRegistryAgents(
    agents,
    "zzzznope xyzzynever",
    new Set(),
    domains,
  );
  assert.equal(impossible.length, 0);
});

test("toggleFacetSelection adds and removes", () => {
  const one = toggleFacetSelection(new Set(), "video");
  assert.ok(one.has("video"));
  const none = toggleFacetSelection(one, "video");
  assert.equal(none.has("video"), false);
});

test("video group tag 1-ATL filters only that category", () => {
  const hits = filterRegistryAgents(agents, "", new Set(["1-ATL"]), domains);
  assert.ok(hits.length >= 1);
  assert.ok(hits.every((a) => a.category === "1-ATL"));
  assert.ok(hits.every((a) => a.id.startsWith("video.")));
});

test("video group tags OR across groups", () => {
  const hits = filterRegistryAgents(
    agents,
    "",
    new Set(["1-ATL", "10-Sup"]),
    domains,
  );
  assert.ok(hits.length >= 2);
  assert.ok(
    hits.every((a) => a.category === "1-ATL" || a.category === "10-Sup"),
  );
});

test("video + group tag composes", () => {
  const hits = filterRegistryAgents(
    agents,
    "",
    new Set(["video", "9-Meta"]),
    domains,
  );
  assert.ok(hits.length >= 1);
  assert.ok(hits.every((a) => a.category === "9-Meta"));
});

test("specials pack filter follows registry search", () => {
  const hits = filterSpecialAgents(
    SPECIAL_AGENT_CATALOG,
    "planner",
    new Set(),
    domains,
  );
  assert.ok(hits.length >= 1);
  assert.ok(hits.every((a) => /planner/i.test(a.agentId + a.title)));
});

test("specials pack hidden when only video domain facet is on", () => {
  const hits = filterSpecialAgents(
    SPECIAL_AGENT_CATALOG,
    "",
    new Set(["video"]),
    domains,
  );
  assert.equal(hits.length, 0);
});

test("specials pack shows on specials domain facet", () => {
  const hits = filterSpecialAgents(
    SPECIAL_AGENT_CATALOG,
    "",
    new Set(["specials"]),
    domains,
  );
  assert.equal(hits.length, SPECIAL_AGENT_CATALOG.length);
});

test("specials pack draft facet keeps drafts", () => {
  const hits = filterSpecialAgents(
    SPECIAL_AGENT_CATALOG,
    "",
    new Set(["draft"]),
    domains,
  );
  assert.equal(hits.length, SPECIAL_AGENT_CATALOG.length);
});

test("pattern search filters by name", () => {
  const hits = filterRegistryPatterns(
    LOCAL_REGISTRY_LANDING.patterns,
    "router",
  );
  assert.ok(hits.length >= 1);
  assert.ok(
    hits.every((pattern) =>
      /router/i.test(
        [pattern.id, pattern.name, pattern.whenToUse, pattern.metrics].join(" "),
      ),
    ),
  );
  const none = filterRegistryPatterns(
    LOCAL_REGISTRY_LANDING.patterns,
    "zzz-no-such-pattern",
  );
  assert.equal(none.length, 0);
});
