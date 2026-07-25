import assert from "node:assert/strict";
import test from "node:test";

import fc from "fast-check";
import React from "react";
import { renderToStaticMarkup } from "react-dom/server";

import { Canvas } from "../../components/Canvas";
import type { GeneratedActionReference, GeneratedJsonObject } from "../api/client";
import {
  GRAPH_RELATIONSHIPS,
  graphEdgeSemantics,
  isGraphActionDisabled,
  mapGraphProjection,
  type GraphRelationship,
} from "./graph-adapters";

const LIFECYCLE_STATES = [
  "queued",
  "running",
  "self_refine",
  "waiting_for_critique",
  "blocked",
  "failed",
  "complete",
  "cancelling",
  "cancelled",
  "manual_recovery_required",
] as const;

type LifecycleState = (typeof LIFECYCLE_STATES)[number];

type EdgeSemantics = ReturnType<typeof graphEdgeSemantics>;

const RELATIONSHIP_ORDERS: readonly (readonly GraphRelationship[])[] = [
  ["data_flow", "state_flow", "iteration"],
  ["data_flow", "iteration", "state_flow"],
  ["state_flow", "data_flow", "iteration"],
  ["state_flow", "iteration", "data_flow"],
  ["iteration", "data_flow", "state_flow"],
  ["iteration", "state_flow", "data_flow"],
];

const relationshipOrderArbitrary: fc.Arbitrary<readonly GraphRelationship[]> = fc.constantFrom(...RELATIONSHIP_ORDERS);

interface NodeScenario {
  readonly id: string;
  readonly label: string;
  readonly immutableVersion: string;
  readonly provenanceReference: string;
  readonly forkOrigin: string;
  readonly customReason: string;
  readonly lifecycle: LifecycleState;
  readonly statusDetail: string;
}

interface GraphScenario {
  readonly graphRevision: string;
  readonly common: NodeScenario;
  readonly custom: NodeScenario;
  readonly validationEligible: boolean;
  readonly runActionEligible: boolean;
  readonly runActionId: string;
  readonly runActionLabel: string;
  readonly relationships: readonly GraphRelationship[];
  readonly edgeLabels: readonly string[];
}

const identifierArbitrary = fc.uuid().map((value: string): string => value.replaceAll("-", ""));
const returnedTextArbitrary = (prefix: string): fc.Arbitrary<string> =>
  identifierArbitrary.map((value: string): string => `${prefix}-${value}`);
const lifecycleArbitrary = fc.constantFrom<LifecycleState>(...LIFECYCLE_STATES);
const nodeScenarioArbitrary: fc.Arbitrary<NodeScenario> = fc.record({
  id: identifierArbitrary,
  label: returnedTextArbitrary("node"),
  immutableVersion: returnedTextArbitrary("version"),
  provenanceReference: returnedTextArbitrary("provenance"),
  forkOrigin: returnedTextArbitrary("origin"),
  customReason: returnedTextArbitrary("reason"),
  lifecycle: lifecycleArbitrary,
  statusDetail: returnedTextArbitrary("detail"),
});

const graphScenarioArbitrary: fc.Arbitrary<GraphScenario> = fc.record({
  graphRevision: returnedTextArbitrary("graph"),
  common: nodeScenarioArbitrary,
  custom: nodeScenarioArbitrary,
  validationEligible: fc.boolean(),
  runActionEligible: fc.boolean(),
  runActionId: returnedTextArbitrary("run-action"),
  runActionLabel: returnedTextArbitrary("run-label"),
  relationships: relationshipOrderArbitrary,
  edgeLabels: fc.array(returnedTextArbitrary("edge"), { minLength: GRAPH_RELATIONSHIPS.length, maxLength: GRAPH_RELATIONSHIPS.length }),
});

const expectedSemantics: Readonly<Record<GraphRelationship, EdgeSemantics>> = {
  data_flow: { textLabel: "Data flow", lineStyle: "solid", marker: "arrow" },
  state_flow: { textLabel: "State flow", lineStyle: "dashed", marker: "state-arrow" },
  iteration: { textLabel: "Iteration", lineStyle: "dotted", marker: "loop" },
};

function graphProjectionFor(scenario: GraphScenario): GeneratedJsonObject {
  const nodes: readonly GeneratedJsonObject[] = [
    {
      id: scenario.common.id,
      label: scenario.common.label,
      kind: "common",
      immutable_version: scenario.common.immutableVersion,
      provenance_reference: scenario.common.provenanceReference,
      task: { lifecycle: scenario.common.lifecycle, status_detail: scenario.common.statusDetail },
    },
    {
      id: scenario.custom.id,
      label: scenario.custom.label,
      kind: "custom",
      fork_origin: scenario.custom.forkOrigin,
      custom_reason: scenario.custom.customReason,
      task: { lifecycle: scenario.custom.lifecycle, status_detail: scenario.custom.statusDetail },
    },
  ];
  const edges: readonly GeneratedJsonObject[] = scenario.relationships.map((relationship, index) => {
    const label = scenario.edgeLabels[index];
    if (label === undefined) throw new Error("Expected a generated edge label.");
    return {
      id: `${relationship}-${label}`,
      source_id: scenario.common.id,
      target_id: scenario.custom.id,
      relationship,
      label,
    };
  });
  const runAction: GeneratedActionReference = {
    id: scenario.runActionId,
    label: scenario.runActionLabel,
    eligible: scenario.runActionEligible,
    kind: "run",
  };

  return {
    graph_revision: scenario.graphRevision,
    nodes,
    edges,
    validation: { eligible: scenario.validationEligible },
    action_references: [runAction],
  };
}

function assertGraphSemantics(scenario: GraphScenario): void {
  const projection = graphProjectionFor(scenario);
  const graph = mapGraphProjection(projection);
  const commonNode = graph.nodes[0];
  const customNode = graph.nodes[1];
  const runAction = graph.actions[0];

  assert.ok(commonNode);
  assert.ok(customNode);
  assert.ok(runAction);
  assert.equal(commonNode.kind, "common");
  assert.equal(commonNode.id, scenario.common.id);
  assert.equal(commonNode.label, scenario.common.label);
  assert.equal(commonNode.immutableVersion, scenario.common.immutableVersion);
  assert.equal(commonNode.provenanceReference, scenario.common.provenanceReference);
  assert.deepEqual(commonNode.task, {
    lifecycle: scenario.common.lifecycle,
    statusDetail: scenario.common.statusDetail,
  });
  assert.equal(customNode.kind, "custom");
  assert.equal(customNode.id, scenario.custom.id);
  assert.equal(customNode.label, scenario.custom.label);
  assert.equal(customNode.forkOrigin, scenario.custom.forkOrigin);
  assert.equal(customNode.customReason, scenario.custom.customReason);
  assert.deepEqual(customNode.task, {
    lifecycle: scenario.custom.lifecycle,
    statusDetail: scenario.custom.statusDetail,
  });

  assert.equal(graph.edges.length, scenario.relationships.length);
  for (const edge of graph.edges) {
    assert.deepEqual(edge.semantics, expectedSemantics[edge.relationship]);
    assert.deepEqual(edge.semantics, graphEdgeSemantics(edge.relationship));
    assert.equal("color" in edge.semantics, false);
  }
  assert.equal(new Set(graph.edges.map((edge) => edge.semantics.textLabel)).size, scenario.relationships.length);
  assert.equal(new Set(graph.edges.map((edge) => edge.semantics.lineStyle)).size, scenario.relationships.length);
  assert.equal(new Set(graph.edges.map((edge) => edge.semantics.marker)).size, scenario.relationships.length);

  const validationIsIneligible = scenario.validationEligible === false;
  assert.equal(runAction.eligible, scenario.runActionEligible);
  assert.equal(isGraphActionDisabled(runAction, graph.validation), validationIsIneligible || !scenario.runActionEligible);

  const markup = renderToStaticMarkup(<Canvas
    projection={projection}
    commandRuntime={{
      isActionDisabled: (): boolean => false,
      submit: async (): Promise<unknown> => undefined,
    }}
  />);
  const actionMarker = `data-action-reference-id="${scenario.runActionId}"`;
  const actionMarkerIndex = markup.indexOf(actionMarker);
  assert.notEqual(actionMarkerIndex, -1);
  const buttonEndIndex = markup.indexOf(">", actionMarkerIndex);
  assert.notEqual(buttonEndIndex, -1);
  const actionButton = markup.slice(actionMarkerIndex, buttonEndIndex);
  assert.equal(actionButton.includes("disabled"), validationIsIneligible || !scenario.runActionEligible);
}

// Feature: frontend-redesign, Property 10: Graph rendering preserves semantic structure and execution eligibility
// Validates: Requirements 6.8, 6.9, 6.10, 6.11, 6.12
test("Property 10: preserves graph semantics, provenance, task state, and ineligible run blocking", (): void => {
  fc.assert(fc.property(graphScenarioArbitrary, assertGraphSemantics), { numRuns: 100 });
});
