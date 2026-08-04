import assert from "node:assert/strict";
import test from "node:test";

/**
 * Inventory: which product surfaces are Host-bound vs still presentation-only.
 * Keeps the team honest about remaining demo fixtures.
 */
const LIVE_HOST_BOUND = [
  "dashboard → loadLiveDashboard (swarms + commons/health + impact)",
  "activity → BoundActivityHome (GET /api/v1/activity)",
  "canvas menu → loadLiveCanvasLanding (list swarms / empty)",
  "canvas live → BoundLiveSwarmCanvas (GET /api/v1/swarms/{id})",
  "composer → recommend/materialize Host APIs (samples are UI helpers)",
  "registry → pack catalog + listSwarms + commons propose/add",
  "agent detail → pack-backed resolveAgentDetailView",
  "knowledge → GET /api/v1/knowledge/sources",
  "costs → GET /api/v1/finance/summary",
  "notifications → GET /api/v1/notifications",
  "blueprints → GET /api/v1/blueprints",
  "settings → GET /api/v1/settings/workspace",
  "profile → GET /api/v1/actors/me/preferences",
  "collaboration → presence + listSwarms",
  "monitoring/operations → running swarms + approvals inbox",
  "mobile → listSwarms + notifications",
] as const;

const STILL_PRESENTATION_OR_PARTIAL = [
  "eval → needs Host evaluation campaign projections (not wired as list feed)",
  "audit → export/integrity require action refs; no list feed on façade",
  "api portal → sample curl/docs chrome; tokens require create actions",
  "onboarding → guided chrome (not Host state)",
  "org chart / agent workflow → generated pack graphs (real pack data, not Host runs)",
] as const;

test("live Host-bound surfaces are documented", () => {
  assert.ok(LIVE_HOST_BOUND.length >= 12);
  assert.ok(STILL_PRESENTATION_OR_PARTIAL.length >= 3);
  assert.ok(
    LIVE_HOST_BOUND.every((line) => line.includes("→")),
    "each live entry should name route → source",
  );
});
