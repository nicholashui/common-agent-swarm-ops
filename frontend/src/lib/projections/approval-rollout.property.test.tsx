import assert from "node:assert/strict";
import test from "node:test";

import fc from "fast-check";
import React from "react";
import { renderToStaticMarkup } from "react-dom/server";

import { ApprovalGateScreen, RolloutCampaignScreen } from "../../components/ApprovalRolloutScreens";
import type { GeneratedActionReference, GeneratedJsonObject } from "../api/client";
import {
  isApprovalDecisionActionEnabled,
  isFreshnessCriticalActionBlocked,
  mapApprovalGateProjection,
  mapRolloutCampaignProjection,
  markApprovalGateProjectionRefreshed,
  observeApprovalEvidenceRevisionChange,
  QUALITY_EVIDENCE_CATEGORIES,
  type QualityEvidenceCategory,
} from "./approval-rollout";

const ROLLOUT_ACTION_KINDS = ["a_b", "canary", "promotion", "rollback", "review"] as const;
type RolloutActionKind = (typeof ROLLOUT_ACTION_KINDS)[number];

const NON_DECISION_ACTION_KINDS = ["a_b", "canary", "promotion", "rollback"] as const;

interface EvidenceFields {
  readonly id: string;
  readonly label: string;
  readonly summary: string;
}

const identifierArbitrary = fc.uuid().map((value: string): string => value.replaceAll("-", ""));
const returnedTextArbitrary = (prefix: string): fc.Arbitrary<string> =>
  identifierArbitrary.map((value: string): string => `${prefix}-${value}`);
const sensitiveSentinelArbitrary = identifierArbitrary.map((value: string): string => `CLIENT_CREATED_${value}`);

const evidenceCategoryArbitrary: fc.Arbitrary<readonly QualityEvidenceCategory[]> = fc
  .shuffledSubarray([...QUALITY_EVIDENCE_CATEGORIES], {
    minLength: QUALITY_EVIDENCE_CATEGORIES.length,
    maxLength: QUALITY_EVIDENCE_CATEGORIES.length,
  })
  .map((categories): readonly QualityEvidenceCategory[] => categories);

const evidenceFieldsArbitrary: fc.Arbitrary<EvidenceFields> = fc.record({
  id: identifierArbitrary,
  label: returnedTextArbitrary("evidence-label"),
  summary: returnedTextArbitrary("evidence-summary"),
});

const nonDecisionActionArbitrary: fc.Arbitrary<GeneratedActionReference> = fc.record({
  id: identifierArbitrary,
  label: returnedTextArbitrary("action-label"),
  eligible: fc.boolean(),
  kind: fc.constantFrom<RolloutActionKind>(...NON_DECISION_ACTION_KINDS),
  irreversible: fc.boolean(),
  freshness_critical: fc.boolean(),
  action_sentinel: sensitiveSentinelArbitrary,
}).map(({ id, ...reference }): GeneratedActionReference => ({
  id: `action-${id}`,
  ...reference,
}));

const returnedActionsArbitrary: fc.Arbitrary<readonly GeneratedActionReference[]> = fc
  .uniqueArray(nonDecisionActionArbitrary, {
    minLength: 1,
    maxLength: ROLLOUT_ACTION_KINDS.length,
    selector: (action: GeneratedActionReference): string => String(action.id),
  })
  .map((actions): readonly GeneratedActionReference[] => {
    const [decisionAction, ...otherActions] = actions;
    if (decisionAction === undefined) throw new Error("Expected a generated decision action.");
    return [{
      ...decisionAction,
      kind: "review",
      eligible: true,
      irreversible: true,
      freshness_critical: true,
    }, ...otherActions];
  });

interface ApprovalRolloutScenario {
  readonly initialEvidenceRevision: string;
  readonly changedEvidenceRevision: string;
  readonly approvalProjection: GeneratedJsonObject;
  readonly refreshedApprovalProjection: GeneratedJsonObject;
  readonly rolloutProjection: GeneratedJsonObject;
  readonly approvalActions: readonly GeneratedActionReference[];
  readonly rolloutActions: readonly GeneratedActionReference[];
  readonly evidenceCategories: readonly QualityEvidenceCategory[];
  readonly evidenceReferences: readonly GeneratedJsonObject[];
  readonly approvalValues: readonly string[];
  readonly rolloutValues: readonly string[];
  readonly criterionFailed: boolean;
  readonly rolloutStale: boolean;
  readonly sentinel: string;
}

const scenarioArbitrary: fc.Arbitrary<ApprovalRolloutScenario> = fc.record({
  initialEvidenceRevision: identifierArbitrary,
  changedEvidenceRevision: identifierArbitrary,
  approvalStateLabel: returnedTextArbitrary("approval-state"),
  pendingOperation: returnedTextArbitrary("pending-operation"),
  expiry: returnedTextArbitrary("expiry"),
  approvalCriterion: returnedTextArbitrary("approval-criterion"),
  selectedVersion: returnedTextArbitrary("selected-version"),
  targetScope: returnedTextArbitrary("target-scope"),
  impactSummary: returnedTextArbitrary("impact-summary"),
  rolloutCriterion: returnedTextArbitrary("rollout-criterion"),
  rolloutApprovalState: returnedTextArbitrary("rollout-approval"),
  rolloutStatus: returnedTextArbitrary("rollout-status"),
  rollbackReference: returnedTextArbitrary("rollback-reference"),
  outcomeMeasurements: returnedTextArbitrary("outcome-measurement"),
  stoppedProgressionLabel: returnedTextArbitrary("stopped-progression"),
  rollbackStateLabel: returnedTextArbitrary("rollback-state"),
  asOf: returnedTextArbitrary("as-of"),
  freshness: returnedTextArbitrary("freshness"),
  artifactId: identifierArbitrary,
  artifactLabel: returnedTextArbitrary("artifact-label"),
  approvalActions: returnedActionsArbitrary,
  rolloutActions: returnedActionsArbitrary,
  evidenceCategories: evidenceCategoryArbitrary,
  evidenceFields: fc.array(evidenceFieldsArbitrary, {
    minLength: QUALITY_EVIDENCE_CATEGORIES.length,
    maxLength: QUALITY_EVIDENCE_CATEGORIES.length,
  }),
  criterionFailed: fc.boolean(),
  rolloutStale: fc.boolean(),
  sentinel: sensitiveSentinelArbitrary,
})
  .filter(({ initialEvidenceRevision, changedEvidenceRevision }): boolean => initialEvidenceRevision !== changedEvidenceRevision)
  .map((seed): ApprovalRolloutScenario => {
    const evidenceReferences = seed.evidenceCategories.map((category, index): GeneratedJsonObject => {
      const fields = seed.evidenceFields[index];
      if (fields === undefined) throw new Error("Expected generated evidence fields for every category.");
      return {
        id: `evidence-${fields.id}`,
        label: fields.label,
        category,
        summary: fields.summary,
        evidence_sentinel: seed.sentinel,
      };
    });
    const approvalActions = seed.approvalActions;
    const rolloutActions = seed.rolloutActions;
    const approvalValues = [
      seed.approvalStateLabel,
      seed.pendingOperation,
      seed.initialEvidenceRevision,
      seed.expiry,
      seed.approvalCriterion,
      seed.artifactLabel,
      ...seed.evidenceFields.flatMap(({ label, summary }): readonly string[] => [label, summary]),
      ...approvalActions.map(({ label }): string => String(label)),
    ];
    const rolloutValues = [
      seed.selectedVersion,
      seed.targetScope,
      seed.impactSummary,
      seed.rolloutCriterion,
      seed.rolloutApprovalState,
      seed.rolloutStatus,
      seed.rollbackReference,
      seed.outcomeMeasurements,
      ...(seed.criterionFailed ? [seed.stoppedProgressionLabel, seed.rollbackStateLabel] : []),
      ...rolloutActions.map(({ label }): string => String(label)),
    ];
    const approvalProjection = {
      state_label: seed.approvalStateLabel,
      pending_operation: seed.pendingOperation,
      evidence_revision: seed.initialEvidenceRevision,
      criteria: [seed.approvalCriterion],
      expiry: seed.expiry,
      redacted_artifact_references: [{ id: `artifact-${seed.artifactId}`, label: seed.artifactLabel }],
      quality_evidence_references: evidenceReferences,
      action_references: approvalActions,
      as_of: seed.asOf,
      freshness: seed.freshness,
      client_created_approval_sentinel: seed.sentinel,
    } satisfies GeneratedJsonObject;
    const refreshedApprovalProjection = {
      ...approvalProjection,
      evidence_revision: seed.changedEvidenceRevision,
    } satisfies GeneratedJsonObject;
    const rolloutProjection = {
      selected_version: seed.selectedVersion,
      target_scope: seed.targetScope,
      impact_summary: seed.impactSummary,
      criteria: [seed.rolloutCriterion],
      approval_state_label: seed.rolloutApprovalState,
      status_label: seed.rolloutStatus,
      rollback_reference: seed.rollbackReference,
      outcome_measurements: seed.outcomeMeasurements,
      criterion_failed: seed.criterionFailed,
      stopped_progression_label: seed.stoppedProgressionLabel,
      rollback_state_label: seed.rollbackStateLabel,
      action_references: rolloutActions,
      as_of: seed.asOf,
      freshness: seed.freshness,
      stale: seed.rolloutStale,
      client_created_rollout_sentinel: seed.sentinel,
    } satisfies GeneratedJsonObject;

    return {
      initialEvidenceRevision: seed.initialEvidenceRevision,
      changedEvidenceRevision: seed.changedEvidenceRevision,
      approvalProjection,
      refreshedApprovalProjection,
      rolloutProjection,
      approvalActions,
      rolloutActions,
      evidenceCategories: seed.evidenceCategories,
      evidenceReferences,
      approvalValues,
      rolloutValues,
      criterionFailed: seed.criterionFailed,
      rolloutStale: seed.rolloutStale,
      sentinel: seed.sentinel,
    };
  });

function renderedActionIds(markup: string): ReadonlySet<string> {
  return new Set([...markup.matchAll(/data-action-reference-id="([^"]+)"/g)].map((match): string => match[1] ?? ""));
}

function renderedActionButtons(markup: string, actionId: string): readonly string[] {
  const escapedId = actionId.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  return [...markup.matchAll(new RegExp(`<button[^>]*data-action-reference-id="${escapedId}"[^>]*>`, "g"))]
    .map((match): string => match[0]);
}

function assertReturnedValues(markup: string, values: readonly string[]): void {
  for (const value of values) assert.match(markup, new RegExp(value));
}

function assertOnlyReturnedActions(markup: string, actions: readonly GeneratedActionReference[]): void {
  const returnedIds = new Set(actions.map((action): string => String(action.id)));
  assert.deepEqual(renderedActionIds(markup), returnedIds);
  for (const action of actions) {
    assert.match(markup, new RegExp(String(action.label)));
    assert.ok(ROLLOUT_ACTION_KINDS.includes(String(action.kind) as RolloutActionKind));
  }
}

// Feature: frontend-redesign, Property 11: Approval and rollout UI remains evidence-bound
// Validates: Requirements 7.1, 7.2, 7.3, 7.5, 7.6
test("Property 11: approval and rollout projections remain evidence-bound", (): void => {
  fc.assert(fc.property(scenarioArbitrary, (scenario): void => {
    const initialApproval = mapApprovalGateProjection(scenario.approvalProjection);
    const refreshedApproval = mapApprovalGateProjection(scenario.refreshedApprovalProjection);
    const rollout = mapRolloutCampaignProjection(scenario.rolloutProjection);

    assert.deepEqual(initialApproval.qualityEvidence.map(({ category }) => category), scenario.evidenceCategories);
    assert.equal(new Set(initialApproval.qualityEvidence.map(({ category }) => category)).size, QUALITY_EVIDENCE_CATEGORIES.length);
    for (const [index, evidence] of initialApproval.qualityEvidence.entries()) {
      const source = scenario.evidenceReferences[index];
      assert.ok(source !== undefined);
      assert.strictEqual(evidence.reference.source, source);
    }
    for (const action of scenario.approvalActions) {
      const mapped = initialApproval.actions.find(({ id }) => id === action.id);
      assert.ok(mapped !== undefined);
      assert.strictEqual(mapped.source, action);
    }
    for (const action of scenario.rolloutActions) {
      const mapped = rollout.actions.find(({ id }) => id === action.id);
      assert.ok(mapped !== undefined);
      assert.strictEqual(mapped.source, action);
    }

    const changedRevisionState = observeApprovalEvidenceRevisionChange(
      { projectionRevision: scenario.initialEvidenceRevision, requiresRefresh: false },
      scenario.changedEvidenceRevision,
    );
    const staleMarkup = renderToStaticMarkup(<ApprovalGateScreen
      currentEvidenceRevision={scenario.changedEvidenceRevision}
      onAction={(): void => undefined}
      onEvidence={(): void => undefined}
      onReference={(): void => undefined}
      projection={scenario.approvalProjection}
      revisionState={changedRevisionState}
    />);
    const staleDecisionAction = scenario.approvalActions[0];
    assert.ok(staleDecisionAction !== undefined);
    assert.equal(isApprovalDecisionActionEnabled(
      initialApproval.decisionActions[0]!,
      initialApproval,
      scenario.changedEvidenceRevision,
      changedRevisionState,
    ), false);
    for (const button of renderedActionButtons(staleMarkup, String(staleDecisionAction.id))) {
      assert.match(button, /disabled=""/);
    }

    const refreshedRevisionState = markApprovalGateProjectionRefreshed(changedRevisionState, scenario.changedEvidenceRevision);
    const refreshedMarkup = renderToStaticMarkup(<ApprovalGateScreen
      currentEvidenceRevision={scenario.changedEvidenceRevision}
      onAction={(): void => undefined}
      onEvidence={(): void => undefined}
      onReference={(): void => undefined}
      projection={scenario.refreshedApprovalProjection}
      revisionState={refreshedRevisionState}
    />);
    assert.equal(isApprovalDecisionActionEnabled(
      refreshedApproval.decisionActions[0]!,
      refreshedApproval,
      scenario.changedEvidenceRevision,
      refreshedRevisionState,
    ), true);
    for (const button of renderedActionButtons(refreshedMarkup, String(staleDecisionAction.id))) {
      assert.doesNotMatch(button, /disabled=""/);
    }

    const approvalMarkup = renderToStaticMarkup(<ApprovalGateScreen
      onAction={(): void => undefined}
      onEvidence={(): void => undefined}
      onReference={(): void => undefined}
      projection={scenario.approvalProjection}
    />);
    const rolloutMarkup = renderToStaticMarkup(<RolloutCampaignScreen
      onAction={(): void => undefined}
      onEvidence={(): void => undefined}
      onReference={(): void => undefined}
      projection={scenario.rolloutProjection}
    />);
    assertOnlyReturnedActions(approvalMarkup, scenario.approvalActions);
    assertOnlyReturnedActions(rolloutMarkup, scenario.rolloutActions);
    assertReturnedValues(approvalMarkup, scenario.approvalValues);
    assertReturnedValues(rolloutMarkup, scenario.rolloutValues);
    for (const category of scenario.evidenceCategories) {
      assert.match(approvalMarkup, new RegExp(`data-evidence-category="${category}"`));
    }
    assert.doesNotMatch(`${approvalMarkup}${rolloutMarkup}`, new RegExp(scenario.sentinel));

    for (const action of scenario.rolloutActions) {
      const expectedDisabled = !action.eligible || isFreshnessCriticalActionBlocked(
        rollout.actions.find(({ id }) => id === action.id)!,
        scenario.rolloutStale,
      );
      for (const button of renderedActionButtons(rolloutMarkup, String(action.id))) {
        assert.equal(button.includes('disabled=""'), expectedDisabled);
      }
    }
  }), { numRuns: 100 });
});
