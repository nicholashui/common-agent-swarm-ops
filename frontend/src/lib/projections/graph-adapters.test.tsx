import assert from "node:assert/strict";
import test from "node:test";

import React from "react";
import { renderToStaticMarkup } from "react-dom/server";

import type { GeneratedJsonObject } from "../api/client";
import { Canvas } from "../../components/Canvas";
import { Composer } from "../../components/Composer";
import {
  createGraphCommandIntent,
  isGraphActionDisabled,
  mapComposerProjection,
  mapGraphProjection,
} from "./graph-adapters";

const GRAPH_PROJECTION = {
  graph_revision: "graph-r17",
  stale: true,
  nodes: [
    { id: "common-node", label: "Evidence verifier", kind: "common", immutable_version: "4.2.0", provenance_reference: "prov:agent:evidence-verifier:4.2.0", task: { lifecycle: "manual_recovery_required", status_detail: "Escalation is required" } },
    { id: "custom-node", label: "Executive writer", kind: "custom", fork_origin: "common:writer:3.0", custom_reason: "Approved reporting vocabulary", task: { lifecycle: "waiting_for_critique", status_detail: "Verifier critique pending" } },
  ],
  edges: [
    { id: "data", source_id: "common-node", target_id: "custom-node", relationship: "data_flow", label: "Evidence" },
    { id: "state", source_id: "custom-node", target_id: "common-node", relationship: "state_flow", label: "Ready" },
    { id: "iteration", source_id: "custom-node", target_id: "common-node", relationship: "iteration", label: "Revise" },
  ],
  validation: {
    eligible: false,
    categories: [
      { category: "version", result: "passed" },
      { category: "schema", result: "passed" },
      { category: "verification", result: "failed", detail: "Verifier gate is incomplete" },
      { category: "unexpected_category", result: "DO_NOT_RENDER" },
    ],
  },
  action_references: [
    { id: "run-graph", label: "Run returned graph", eligible: true, kind: "run" },
    { id: "retry-task", label: "Retry returned task", eligible: true, kind: "retry" },
    { id: "untrusted", label: "Do not render", eligible: true, kind: "invented" },
  ],
  protected_sentinel: "MUST_NOT_RENDER",
} as const satisfies GeneratedJsonObject;

const COMPOSER_PROJECTION = {
  common_patterns: [
    {
      id: "pattern-v4",
      label: "Evidence-first pattern",
      immutable_version: "4.0.0",
      provenance_reference: "prov:pattern:evidence-first:4.0.0",
      instantiation_action_reference: { id: "instantiate-pattern", label: "Instantiate returned pattern", eligible: true, kind: "instantiate" },
    },
    {
      id: "not-instantiable",
      label: "Excluded pattern action",
      immutable_version: "1.0.0",
      provenance_reference: "prov:pattern:excluded:1.0.0",
      instantiation_action_reference: { id: "not-instantiated", label: "Do not render", eligible: true, kind: "run" },
    },
  ],
} as const satisfies GeneratedJsonObject;

// Requirements 6.8–6.18, 12.1, 12.5, 12.7–12.9
// Uses deterministic generated-projection-shaped fixtures and does not issue network requests.
test("graph adapter preserves non-color edge semantics, provenance, exact task state, validation categories, and returned command references", () => {
  const graph = mapGraphProjection(GRAPH_PROJECTION);
  assert.equal(graph.statusLabel, "Stale");
  assert.deepEqual(graph.edges.map(({ relationship, semantics }) => [relationship, semantics]), [
    ["data_flow", { textLabel: "Data flow", lineStyle: "solid", marker: "arrow" }],
    ["state_flow", { textLabel: "State flow", lineStyle: "dashed", marker: "state-arrow" }],
    ["iteration", { textLabel: "Iteration", lineStyle: "dotted", marker: "loop" }],
  ]);
  assert.deepEqual(graph.nodes[0], {
    id: "common-node", label: "Evidence verifier", kind: "common", immutableVersion: "4.2.0",
    provenanceReference: "prov:agent:evidence-verifier:4.2.0",
    task: { lifecycle: "manual_recovery_required", statusDetail: "Escalation is required" },
  });
  assert.deepEqual(graph.nodes[1], {
    id: "custom-node", label: "Executive writer", kind: "custom", forkOrigin: "common:writer:3.0",
    customReason: "Approved reporting vocabulary",
    task: { lifecycle: "waiting_for_critique", statusDetail: "Verifier critique pending" },
  });
  assert.deepEqual(graph.validation.categories, [
    { category: "version", result: "passed" },
    { category: "schema", result: "passed" },
    { category: "verification", result: "failed", detail: "Verifier gate is incomplete" },
  ]);
  assert.deepEqual(graph.actions.map(({ id, kind }) => [id, kind]), [["run-graph", "run"], ["retry-task", "retry"]]);

  const run = graph.actions[0];
  const retry = graph.actions[1];
  assert.ok(run);
  assert.ok(retry);
  assert.equal(isGraphActionDisabled(run, graph.validation), true);
  assert.equal(isGraphActionDisabled(retry, graph.validation), false);
  assert.deepEqual(createGraphCommandIntent(retry, graph.graphRevision), {
    actionReferenceId: "retry-task",
    actionReference: GRAPH_PROJECTION.action_references[1],
    payload: { graphRevision: "graph-r17" },
  });
});

test("composer maps only common provenance with a returned instantiation action and canvas rendering exposes semantic text without protected fields", () => {
  const composer = mapComposerProjection(COMPOSER_PROJECTION);
  assert.equal(composer.patterns.length, 2);
  assert.equal(composer.patterns[0]?.instantiationAction?.id, "instantiate-pattern");
  assert.equal(composer.patterns[1]?.instantiationAction, undefined);

  const canvasMarkup = renderToStaticMarkup(<Canvas projection={GRAPH_PROJECTION} />);
  const composerMarkup = renderToStaticMarkup(<Composer projection={COMPOSER_PROJECTION} />);
  assert.match(canvasMarkup, /Data flow: common-node to custom-node/);
  assert.match(canvasMarkup, /State flow: custom-node to common-node/);
  assert.match(canvasMarkup, /Iteration: custom-node to common-node/);
  assert.match(canvasMarkup, /manual_recovery_required/);
  assert.match(canvasMarkup, /Escalation is required/);
  assert.match(canvasMarkup, /Stale/);
  assert.match(canvasMarkup, /data-action-reference-id="run-graph"/);
  assert.match(canvasMarkup, /data-action-reference-id="retry-task"/);
  assert.doesNotMatch(canvasMarkup, /MUST_NOT_RENDER|DO_NOT_RENDER|unexpected_category|untrusted/);
  assert.match(composerMarkup, /prov:pattern:evidence-first:4.0.0/);
  assert.match(composerMarkup, /Instantiate returned pattern/);
  assert.doesNotMatch(composerMarkup, /Do not render/);
});
