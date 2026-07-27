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
  resolveAgentDetailView,
} from "../lib/projections/agent-detail-landing";
import { getPackAgent, PACK_AGENT_COUNTS } from "../lib/projections/pack-agents.generated";
import { AgentDetailHome } from "./AgentDetailHome";

const componentDirectory = dirname(fileURLToPath(import.meta.url));

test("agent detail home shows pack agent settings (no demo VerificationLoop)", () => {
  const view = resolveAgentDetailView("video.orchestrator");
  const markup = renderToStaticMarkup(
    <AgentDetailHome agentId="video.orchestrator" view={view} />,
  );

  assert.match(markup, /Orchestrator|video\.orchestrator/i);
  assert.match(markup, /PACK AGENT DETAIL|VIDEO AGENT DETAIL/i);
  assert.match(markup, /Propose Improvement/);
  assert.match(markup, /Open in Registry Hub/);
  assert.match(markup, /Spec \/ Config/);
  assert.match(markup, /History \+ Cross-Swarm Usage/);
  assert.match(markup, /Opaque reference: video\.orchestrator/);
  assert.match(markup, /business\/video\/agents/);
  assert.match(markup, /Agent SPEC|Loading document/);
  assert.doesNotMatch(markup, /VerificationLoopAgent/);
  assert.doesNotMatch(markup, /MarketSentimentAgent/);
  assert.doesNotMatch(markup, /tenant_id|password=|authorization:\s*bearer/i);
});

test("agent detail resolves every pack agent id", () => {
  assert.equal(PACK_AGENT_COUNTS.total, 133);
  assert.equal(PACK_AGENT_COUNTS.video, 114);
  assert.equal(PACK_AGENT_COUNTS.specials, 19);
  const video = getPackAgent("video.creativedirector");
  const special = getPackAgent("specials.aesthetics-agent");
  assert.ok(video);
  assert.ok(special);
  const videoView = resolveAgentDetailView("video.creativedirector");
  const specialView = resolveAgentDetailView("specials.aesthetics-agent");
  assert.match(videoView.agentName, /Creative\s*Director|Creativedirector/i);
  assert.match(specialView.agentName, /Aesthetics/i);
  assert.ok(videoView.configSummaries.some((s) => s.id === "runtime"));
  assert.ok(specialView.configSummaries.some((s) => s.id === "model"));
  assert.equal(videoView.specDocPath, "/docs/agents/video.creativedirector/SPEC.md");
  assert.equal(
    specialView.specDocPath,
    "/docs/agents/specials.aesthetics-agent/SPEC.md",
  );
  // Plain summary — not raw markdown heading dump
  assert.doesNotMatch(videoView.insightStrip, /###\s/);
  assert.doesNotMatch(videoView.insightStrip, /^#\s/m);
});

test("agent detail tabs remain five; Spec/Config first; default landing pack-backed", () => {
  assert.equal(AGENT_DETAIL_TABS.length, 5);
  assert.deepEqual(
    AGENT_DETAIL_TABS.map((tab) => tab.id),
    ["config", "history", "playground", "knowledge", "ops"],
  );
  assert.doesNotMatch(LOCAL_AGENT_DETAIL_LANDING.agentName, /VerificationLoop/);
  assert.ok(LOCAL_AGENT_DETAIL_LANDING.configSummaries.length >= 1);
  assert.ok(
    LOCAL_AGENT_DETAIL_LANDING.configSummaries.some((section) =>
      section.lines.some((line) => line.includes("agent_id:") || line.includes("network_access")),
    ),
  );
});

test("agent detail CSS defines header, tabs, table, markdown, and ops styles", async () => {
  const css = await readFile(
    resolve(componentDirectory, "../app/globals.css"),
    "utf8",
  );
  assert.match(css, /\.agent-detail/);
  assert.match(css, /\.agent-detail__tabs/);
  assert.match(css, /\.agent-detail__table/);
  assert.match(css, /\.agent-detail__markdown-panel/);
  assert.match(css, /\.agent-detail__md/);
});
