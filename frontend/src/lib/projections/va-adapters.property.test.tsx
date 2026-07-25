import assert from "node:assert/strict";
import test from "node:test";

import fc from "fast-check";
import React from "react";
import { renderToStaticMarkup } from "react-dom/server";

import { VaProjectionScreen } from "../../components/KnowledgeArtifactScreens";
import type { GeneratedJsonObject } from "../api/client";
import { mapVaProjection, type ArtifactProjectionView } from "./va-adapters";

const QUALITY_EVIDENCE_CATEGORIES = [
  "l1_specification_validation",
  "l2_role_rubric_evaluation",
  "l3_baseline_preference",
  "critique",
  "gate_outcome",
  "human_approval",
] as const;

type ArtifactMode = "complete" | "missing_delivery" | "missing_gate";

interface VaScenario {
  readonly template: string;
  readonly productionPhase: string;
  readonly commonPatternVersion: string;
  readonly agentIdentity: string;
  readonly agentScope: string;
  readonly capability: string;
  readonly policy: string;
  readonly runtimeConstraint: string;
  readonly qualityThreshold: string;
  readonly critiqueRelationship: string;
  readonly provenanceObligation: string;
  readonly publishedVersion: string;
  readonly taskId: string;
  readonly graphRevision: string;
  readonly dependency: string;
  readonly gateId: string;
  readonly lifecycle: string;
  readonly recoveryState: string;
  readonly budget: string;
  readonly checkpoint: string;
  readonly artifactVersion: string;
  readonly parentLineage: string;
  readonly specification: string;
  readonly rightsAndConsent: string;
  readonly continuity: string;
  readonly qualityControl: string;
  readonly deliveryState: string;
  readonly deliveryTarget: string;
  readonly artifactProvenance: string;
  readonly artifactMode: ArtifactMode;
  readonly critiqueState: string;
  readonly critiqueMessage: string;
  readonly critiqueEvidenceId: string;
  readonly critiqueEvidenceLabel: string;
  readonly qualityEvidenceReference: string;
  readonly qualityEvidenceValue: string;
  readonly evidenceRevision: string;
  readonly sentinel: string;
  readonly genericGraphRevision: string;
  readonly genericGovernanceStatus: string;
  readonly genericProvenance: string;
  readonly genericNodeLabel: string;
  readonly genericLifecycle: string;
}

const identifierArbitrary = fc.uuid().map((value: string): string => value.replaceAll("-", ""));
const returnedTextArbitrary = (prefix: string): fc.Arbitrary<string> =>
  identifierArbitrary.map((value: string): string => `${prefix}-${value}`);

const scenarioArbitrary: fc.Arbitrary<VaScenario> = fc.record({
  template: returnedTextArbitrary("template"),
  productionPhase: returnedTextArbitrary("phase"),
  commonPatternVersion: returnedTextArbitrary("pattern"),
  agentIdentity: returnedTextArbitrary("agent"),
  agentScope: returnedTextArbitrary("scope"),
  capability: returnedTextArbitrary("capability"),
  policy: returnedTextArbitrary("policy"),
  runtimeConstraint: returnedTextArbitrary("runtime"),
  qualityThreshold: returnedTextArbitrary("threshold"),
  critiqueRelationship: returnedTextArbitrary("critique-relationship"),
  provenanceObligation: returnedTextArbitrary("provenance-obligation"),
  publishedVersion: returnedTextArbitrary("agent-version"),
  taskId: returnedTextArbitrary("task"),
  graphRevision: returnedTextArbitrary("graph"),
  dependency: returnedTextArbitrary("dependency"),
  gateId: returnedTextArbitrary("gate"),
  lifecycle: returnedTextArbitrary("lifecycle"),
  recoveryState: returnedTextArbitrary("recovery"),
  budget: returnedTextArbitrary("budget"),
  checkpoint: returnedTextArbitrary("checkpoint"),
  artifactVersion: returnedTextArbitrary("artifact"),
  parentLineage: returnedTextArbitrary("parent"),
  specification: returnedTextArbitrary("specification"),
  rightsAndConsent: returnedTextArbitrary("rights"),
  continuity: returnedTextArbitrary("continuity"),
  qualityControl: returnedTextArbitrary("quality-control"),
  deliveryState: returnedTextArbitrary("delivery-state"),
  deliveryTarget: returnedTextArbitrary("delivery-target"),
  artifactProvenance: returnedTextArbitrary("artifact-provenance"),
  artifactMode: fc.constantFrom<ArtifactMode>("complete", "missing_delivery", "missing_gate"),
  critiqueState: returnedTextArbitrary("critique-state"),
  critiqueMessage: returnedTextArbitrary("critique-message"),
  critiqueEvidenceId: returnedTextArbitrary("critique-evidence"),
  critiqueEvidenceLabel: returnedTextArbitrary("critique-evidence-label"),
  qualityEvidenceReference: returnedTextArbitrary("quality-evidence"),
  qualityEvidenceValue: returnedTextArbitrary("quality-result"),
  evidenceRevision: returnedTextArbitrary("evidence-revision"),
  sentinel: returnedTextArbitrary("CLIENT_CREATED_SENTINEL"),
  genericGraphRevision: returnedTextArbitrary("generic-graph"),
  genericGovernanceStatus: returnedTextArbitrary("generic-governance"),
  genericProvenance: returnedTextArbitrary("generic-provenance"),
  genericNodeLabel: returnedTextArbitrary("generic-node"),
  genericLifecycle: returnedTextArbitrary("generic-lifecycle"),
});

function createVaProjection(scenario: VaScenario): GeneratedJsonObject {
  const artifact: GeneratedJsonObject = {
    artifact_version: scenario.artifactVersion,
    parent_lineage: [scenario.parentLineage],
    technical_specification: { format: scenario.specification },
    rights_and_consent_state: scenario.rightsAndConsent,
    continuity_state: scenario.continuity,
    quality_control_state: scenario.qualityControl,
    ...(scenario.artifactMode === "missing_delivery" ? {} : {
      delivery_state: scenario.deliveryState,
      delivery_targets: [scenario.deliveryTarget],
      provenance_reference: scenario.artifactProvenance,
    }),
    gate_approval: scenario.artifactMode === "missing_gate" ? "pending" : "approved",
    client_created_artifact_sentinel: scenario.sentinel,
  };

  return {
    va_projection: {
      template: scenario.template,
      production_phase: scenario.productionPhase,
      common_pattern_version: scenario.commonPatternVersion,
      common_agent_versions: [{
        canonical_identity: scenario.agentIdentity,
        boundaries: scenario.agentScope,
        responsibilities: [scenario.capability],
        tool_policy: [scenario.policy],
        runtime_policy: { max_iterations: scenario.runtimeConstraint },
        quality_rubric: { threshold: scenario.qualityThreshold },
        critique_relationships: [scenario.critiqueRelationship],
        provenance_policy: [scenario.provenanceObligation],
        agent_version_id: scenario.publishedVersion,
      }],
      agent_tasks: [{
        task_id: scenario.taskId,
        graph_revision: scenario.graphRevision,
        dependencies: [scenario.dependency],
        approval_gate_ids: [scenario.gateId],
        lifecycle_state: scenario.lifecycle,
        recovery_state: scenario.recoveryState,
        budget: { budget_remaining: scenario.budget },
        checkpoint_reference: scenario.checkpoint,
        pinned_agent_version_id: scenario.publishedVersion,
      }],
      artifact_handoffs: [artifact],
      critique_records: [{
        critique_state: scenario.critiqueState,
        source_reference: scenario.agentIdentity,
        target_task_id: scenario.taskId,
        message: scenario.critiqueMessage,
        submitted_at: scenario.evidenceRevision,
        evidence_references: [{
          id: scenario.critiqueEvidenceId,
          label: scenario.critiqueEvidenceLabel,
          summary: scenario.critiqueMessage,
        }],
      }],
      quality_evidence: QUALITY_EVIDENCE_CATEGORIES.map((category): GeneratedJsonObject => ({
        kind: category,
        evidence_reference: `${scenario.qualityEvidenceReference}-${category}`,
        passed: true,
        result: scenario.qualityEvidenceValue,
      })),
      pinned_provenance: { graph_revision_id: scenario.graphRevision },
      client_created_va_sentinel: scenario.sentinel,
    },
    client_created_projection_sentinel: scenario.sentinel,
  };
}

function createGenericProjection(scenario: VaScenario): GeneratedJsonObject {
  return {
    graph_revision: scenario.genericGraphRevision,
    governance_status: scenario.genericGovernanceStatus,
    provenance_reference: scenario.genericProvenance,
    graph: {
      graph_revision: scenario.genericGraphRevision,
      nodes: [{
        id: `${scenario.genericGraphRevision}-node`,
        label: scenario.genericNodeLabel,
        kind: "common",
        immutable_version: scenario.commonPatternVersion,
        provenance_reference: scenario.genericProvenance,
        task: { lifecycle: scenario.genericLifecycle },
      }],
      edges: [],
    },
    client_created_projection_sentinel: scenario.sentinel,
  };
}

function assertContainsAll(markup: string, values: readonly string[]): void {
  for (const value of values) assert.equal(markup.includes(value), true, `Expected returned value ${value} in rendered markup.`);
}

function requiredItem<T>(items: readonly T[], description: string): T {
  const item = items[0];
  if (item === undefined) throw new Error(`Expected ${description}.`);
  return item;
}

function assertArtifactDelivery(scenario: VaScenario, artifact: ArtifactProjectionView, markup: string): void {
  const isBlocked = scenario.artifactMode !== "complete";
  assert.equal(artifact.deliveryBlocked, isBlocked);
  assert.deepEqual(artifact.deliveryBlockReasons, isBlocked
    ? [scenario.artifactMode === "missing_delivery" ? "missing_delivery_field" : "missing_gate_approval"]
    : []);
  assert.equal(markup.includes("data-delivery-blocked=\"true\""), isBlocked);

  if (scenario.artifactMode === "missing_delivery") {
    assert.equal(artifact.deliveryState, undefined);
    assert.equal(markup.includes(scenario.deliveryState), false);
  } else {
    assert.equal(artifact.deliveryState, scenario.deliveryState);
    assert.equal(markup.includes(scenario.deliveryState), true);
  }
}

function assertReturnedVaDomainInformation(scenario: VaScenario): void {
  const vaProjection = createVaProjection(scenario);
  const mapped = mapVaProjection(vaProjection);
  assert.ok(mapped !== undefined);
  assert.equal(mapped.template, scenario.template);
  assert.equal(mapped.productionPhase, scenario.productionPhase);
  assert.equal(mapped.commonPatternVersion, scenario.commonPatternVersion);

  const agent = requiredItem(mapped.agents, "a returned common-agent contract");
  assert.equal(agent.identity, scenario.agentIdentity);
  assert.equal(agent.scope, scenario.agentScope);
  assert.deepEqual(agent.capabilities, [scenario.capability]);
  assert.deepEqual(agent.policies, [scenario.policy]);
  assert.equal(agent.runtimeConstraints[0]?.value, scenario.runtimeConstraint);
  assert.equal(agent.qualityContract[0]?.value, scenario.qualityThreshold);
  assert.deepEqual(agent.critiqueRelationships, [scenario.critiqueRelationship]);
  assert.deepEqual(agent.provenanceObligations, [scenario.provenanceObligation]);
  assert.equal(agent.publishedVersion, scenario.publishedVersion);

  const task = requiredItem(mapped.tasks, "a returned task projection");
  assert.equal(task.taskId, scenario.taskId);
  assert.equal(task.graphRevision, scenario.graphRevision);
  assert.deepEqual(task.dependencies, [scenario.dependency]);
  assert.deepEqual(task.gates, [scenario.gateId]);
  assert.equal(task.lifecycle, scenario.lifecycle);
  assert.equal(task.recoveryState, scenario.recoveryState);
  assert.equal(task.budget[0]?.value, scenario.budget);
  assert.equal(task.checkpoint, scenario.checkpoint);
  assert.deepEqual(task.commonVersionProvenance, [scenario.publishedVersion]);

  const artifact = requiredItem(mapped.artifacts, "a returned artifact projection");
  assert.equal(artifact.artifactVersion, scenario.artifactVersion);
  assert.deepEqual(artifact.parentLineage, [scenario.parentLineage]);
  assert.equal(artifact.technicalSpecification[0]?.value, scenario.specification);
  assert.equal(artifact.rightsAndConsent, scenario.rightsAndConsent);
  assert.equal(artifact.continuity, scenario.continuity);
  assert.equal(artifact.qualityControl, scenario.qualityControl);
  assert.deepEqual(artifact.deliveryTargets, scenario.artifactMode === "missing_delivery" ? [] : [scenario.deliveryTarget]);
  assert.equal(artifact.provenanceReference, scenario.artifactMode === "missing_delivery" ? undefined : scenario.artifactProvenance);

  const critique = requiredItem(mapped.critiques, "a returned critique projection");
  assert.equal(critique.critiqueState, scenario.critiqueState);
  assert.equal(critique.source, scenario.agentIdentity);
  assert.equal(critique.target, scenario.taskId);
  assert.equal(critique.message, scenario.critiqueMessage);
  assert.equal(critique.evidence[0]?.id, scenario.critiqueEvidenceId);

  assert.deepEqual(mapped.qualityEvidence.map(({ category }) => category), QUALITY_EVIDENCE_CATEGORIES);
  assert.equal(mapped.qualityEvidence.every(({ referenceValue }) => referenceValue === undefined), false);
  assert.equal(mapped.provenance[0]?.value, scenario.graphRevision);

  const markup = renderToStaticMarkup(<VaProjectionScreen projection={vaProjection} />);
  assertContainsAll(markup, [
    scenario.template,
    scenario.productionPhase,
    scenario.commonPatternVersion,
    scenario.agentIdentity,
    scenario.agentScope,
    scenario.capability,
    scenario.policy,
    scenario.runtimeConstraint,
    scenario.qualityThreshold,
    scenario.critiqueRelationship,
    scenario.provenanceObligation,
    scenario.publishedVersion,
    scenario.taskId,
    scenario.graphRevision,
    scenario.dependency,
    scenario.gateId,
    scenario.lifecycle,
    scenario.recoveryState,
    scenario.budget,
    scenario.checkpoint,
    scenario.artifactVersion,
    scenario.parentLineage,
    scenario.specification,
    scenario.rightsAndConsent,
    scenario.continuity,
    scenario.qualityControl,
    scenario.critiqueState,
    scenario.critiqueMessage,
    scenario.critiqueEvidenceLabel,
    scenario.qualityEvidenceReference,
    scenario.qualityEvidenceValue,
  ]);
  for (const category of QUALITY_EVIDENCE_CATEGORIES) assert.match(markup, new RegExp(`data-evidence-category=\"${category}\"`));
  assert.doesNotMatch(markup, new RegExp(scenario.sentinel));
  assertArtifactDelivery(scenario, artifact, markup);

  const genericProjection = createGenericProjection(scenario);
  assert.equal(mapVaProjection(genericProjection), undefined);
  const genericMarkup = renderToStaticMarkup(<VaProjectionScreen projection={genericProjection} />);
  assertContainsAll(genericMarkup, [
    scenario.genericGraphRevision,
    scenario.genericGovernanceStatus,
    scenario.genericProvenance,
    scenario.genericNodeLabel,
    scenario.genericLifecycle,
  ]);
  assert.doesNotMatch(genericMarkup, /VA DOMAIN ADAPTER|Returned production projection|Production metadata/);
  assert.doesNotMatch(genericMarkup, new RegExp(scenario.sentinel));
}

// Feature: frontend-redesign, Property 13: VA adapters add returned domain information without inventing state
// Validates: Requirements 9.1, 9.2, 9.3, 9.4, 9.5, 9.9
test("Property 13: preserves returned VA domain data, generic fallback, and fail-closed delivery", (): void => {
  fc.assert(fc.property(scenarioArbitrary, assertReturnedVaDomainInformation), { numRuns: 100 });
});
