import assert from "node:assert/strict";
import test from "node:test";

import React from "react";
import { renderToStaticMarkup } from "react-dom/server";

import type { GeneratedJsonObject } from "../lib/api/client";
import {
  createApprovalEvidenceRevisionState,
  mapApprovalGateProjection,
  mapRolloutCampaignProjection,
  observeApprovalEvidenceRevisionChange,
} from "../lib/projections/approval-rollout";
import { ApprovalGateScreen, RolloutCampaignScreen } from "./ApprovalRolloutScreens";

const handlers = {
  onAction: (): void => {},
  onEvidence: (): void => {},
  onReference: (): void => {},
};

const approvalProjection = {
  state_label: "Awaiting human approval",
  pending_operation: "Promote returned version",
  evidence_revision: "evidence-revision-1",
  criteria: ["Returned criterion"],
  expiry: "2026-03-02T14:00:00Z",
  redacted_artifact_references: [{ id: "artifact-1", label: "Returned artifact" }],
  quality_evidence_references: [
    { id: "evidence-l1", label: "L1 evidence", category: "l1_specification_validation", summary: "Returned L1 result" },
    { id: "evidence-l2", label: "L2 evidence", category: "l2_role_rubric_evaluation", summary: "Returned L2 result" },
    { id: "evidence-l3", label: "L3 evidence", category: "l3_baseline_preference", summary: "Returned L3 result" },
    { id: "evidence-critique", label: "Critique evidence", category: "critique", summary: "Returned critique result" },
    { id: "evidence-gate", label: "Gate evidence", category: "gate_outcome", summary: "Returned gate result" },
    { id: "evidence-human", label: "Human approval evidence", category: "human_approval", summary: "Returned human approval result" },
  ],
  action_references: [
    { id: "decision-1", label: "Approve returned operation", eligible: true, kind: "approve", irreversible: true, freshness_critical: true },
    { id: "refresh-1", label: "Refresh approval gate", eligible: true, kind: "refresh" },
  ],
  as_of: "2026-03-02T12:00:00Z",
  freshness: "Fresh",
} as const satisfies GeneratedJsonObject;

const rolloutProjection = {
  selected_version: "common-agent@2.1",
  target_scope: "returned bounded scope",
  impact_summary: "returned impact summary",
  criteria: ["returned success criterion"],
  approval_state_label: "Approved",
  status_label: "Stopped",
  rollback_reference: "rollback-1",
  outcome_measurements: { success_rate: "returned measurement" },
  criterion_failed: true,
  stopped_progression_label: "Progression stopped by server",
  rollback_state_label: "Rollback ready",
  stale: true,
  action_references: [
    { id: "canary-1", label: "Run returned canary", eligible: true, kind: "canary", irreversible: true },
    { id: "refresh-2", label: "Refresh rollout", eligible: true, kind: "refresh" },
  ],
} as const satisfies GeneratedJsonObject;

// Requirements 7.1–7.8, 12.1, 12.5, 12.7–12.9
test("approval mapping preserves returned details, distinct evidence categories, and action origins", () => {
  const view = mapApprovalGateProjection(approvalProjection);

  assert.equal(view.approvalStateLabel, "Awaiting human approval");
  assert.equal(view.pendingOperation, "Promote returned version");
  assert.equal(view.evidenceRevision, "evidence-revision-1");
  assert.deepEqual(view.criteria, ["Returned criterion"]);
  assert.deepEqual(view.artifactReferences.map(({ id }) => id), ["artifact-1"]);
  assert.deepEqual(view.qualityEvidence.map(({ category }) => category), [
    "l1_specification_validation",
    "l2_role_rubric_evaluation",
    "l3_baseline_preference",
    "critique",
    "gate_outcome",
    "human_approval",
  ]);
  assert.deepEqual(view.decisionActions.map(({ id }) => id), ["decision-1"]);
  assert.equal(view.decisionActions[0]?.source, view.actions[0]?.source);
});

test("changed evidence revision requires a fresh matching approval projection before decision", () => {
  const initial = createApprovalEvidenceRevisionState("evidence-revision-1");
  const stale = observeApprovalEvidenceRevisionChange(initial, "evidence-revision-2");
  const projection = mapApprovalGateProjection(approvalProjection);
  const staleMarkup = renderToStaticMarkup(<ApprovalGateScreen
    {...handlers}
    currentEvidenceRevision="evidence-revision-2"
    projection={approvalProjection}
    revisionState={stale}
  />);
  assert.match(staleMarkup, /disabled=""/);
  assert.match(staleMarkup, /Approve returned operation/);

  const refreshedMarkup = renderToStaticMarkup(<ApprovalGateScreen
    {...handlers}
    currentEvidenceRevision="evidence-revision-1"
    projection={approvalProjection}
  />);
  assert.doesNotMatch(refreshedMarkup, /data-action-reference-id="decision-1" disabled=""/);
  assert.equal(projection.decisionActions[0]?.eligible, true);
});

test("approval and rollout stale projections block irreversible actions but retain returned refresh action", () => {
  const markup = renderToStaticMarkup(<RolloutCampaignScreen {...handlers} projection={rolloutProjection} />);
  const view = mapRolloutCampaignProjection(rolloutProjection);

  assert.match(markup, /Selected version/);
  assert.match(markup, /common-agent@2\.1/);
  assert.match(markup, /Progression stopped by server/);
  assert.match(markup, /Rollback ready/);
  assert.match(markup, /data-action-reference-id="canary-1" disabled=""/);
  assert.match(markup, /Refresh rollout/);
  assert.equal(view.stale, true);
  assert.equal(view.criterionFailed, true);
  assert.doesNotMatch(markup, /client-created|invented/);
});
