import assert from "node:assert/strict";
import test from "node:test";

import React from "react";
import { renderToStaticMarkup } from "react-dom/server";

import type { GeneratedJsonObject } from "../lib/api/client";
import { ApprovalGateScreen, RolloutCampaignScreen } from "./ApprovalRolloutScreens";
import { Canvas } from "./Canvas";
import { KnowledgeArtifactScreen, VaProjectionScreen } from "./KnowledgeArtifactScreens";
import { Activity, Dashboard, Registry } from "./OperationalScreens";
import { ResponsiveStack } from "./ResponsiveLayout";
import { ScreenBoundary } from "./ScreenBoundary";
import {
  getScreenDefinition,
  getScreenFixture,
} from "../lib/screens/screen-manifest";

const HANDLERS = {
  onAction: (): void => undefined,
  onEvidence: (): void => undefined,
  onFilterChange: (): void => undefined,
  onReference: (): void => undefined,
};

const DASHBOARD_PROJECTION = {
  title: "Returned dashboard",
  description: "Returned fleet overview",
  state_label: "Degraded",
  as_of: "2026-03-02T12:00:00Z",
  freshness: "Delayed",
  degraded_state: "backlog",
  stale: false,
  health: "Delayed event processing",
  fleet_state: "3 agents degraded",
  approval_alert: "Approval gate expires soon",
  backlog: "12 queued runs",
  common_version_impact: "common-agent@2.1 affects 4 runs",
  action_references: [{ id: "dashboard-refresh", label: "Refresh dashboard", eligible: true, kind: "refresh" }],
  evidence_references: [{ id: "dashboard-evidence", label: "Dashboard evidence", summary: "Returned fleet evidence" }],
  alerts: [{ summary: "Returned backlog alert", affected_reference: { id: "run-backlog-1", label: "Affected run" } }],
  protected_dashboard_sentinel: "DO_NOT_RENDER_DASHBOARD",
} as const satisfies GeneratedJsonObject;

const REGISTRY_PROJECTION = {
  title: "Returned common registry",
  description: "Returned immutable component results",
  state_label: "Ready",
  as_of: "2026-03-02T12:01:00Z",
  freshness: "Fresh",
  stale: false,
  immutable_identifier: "common-agent:verifier",
  version: "1.8.0",
  status: "published",
  provenance_reference: "prov:verifier:1.8.0",
  compatibility_state: "compatible",
  aggregate_metrics: "97.1 percent success",
  filters: [{ id: "status", label: "Status", options: [{ label: "Published", value: "published", internal_filter_sentinel: "DO_NOT_SUBMIT" }] }],
  action_references: [{ id: "registry-refresh", label: "Refresh registry", eligible: true, kind: "refresh" }],
  evidence_references: [{ id: "registry-evidence", label: "Registry evidence", summary: "Returned compatibility evidence" }],
  sections: [{ heading: "Returned component", immutable_identifier: "common-agent:verifier", version: "1.8.0", provenance_reference: "prov:verifier:1.8.0", action_references: [], evidence_references: [] }],
  protected_registry_sentinel: "DO_NOT_RENDER_REGISTRY",
} as const satisfies GeneratedJsonObject;

const ACTIVITY_PROJECTION = {
  title: "Returned activity",
  description: "Returned run and task activity",
  state_label: "Running",
  as_of: "2026-03-02T12:02:00Z",
  freshness: "Fresh",
  stale: false,
  graph_revision: "graph-revision-42",
  common_versions: "verifier@1.8.0",
  lifecycle: "waiting_for_critique",
  dependency: "approval-gate-1",
  checkpoint: "checkpoint-9",
  retry: "2",
  failure: "none",
  recovery: "retry available",
  correlation_identifier: "corr-activity-42",
  action_references: [{ id: "activity-refresh", label: "Refresh activity", eligible: true, kind: "refresh" }],
  evidence_references: [{ id: "activity-evidence", label: "Activity evidence", summary: "Returned task evidence" }],
  sections: [{ heading: "Returned task", lifecycle: "waiting_for_critique", graph_revision: "graph-revision-42", common_versions: "verifier@1.8.0", action_references: [], evidence_references: [] }],
  protected_activity_sentinel: "DO_NOT_RENDER_ACTIVITY",
} as const satisfies GeneratedJsonObject;

const CANVAS_PROJECTION = {
  graph_revision: "graph-revision-42",
  state_label: "Running",
  nodes: [
    { id: "verifier", label: "Evidence verifier", kind: "common", immutable_version: "1.8.0", provenance_reference: "prov:verifier:1.8.0", task: { lifecycle: "waiting_for_critique", status_detail: "Returned critique is pending" } },
    { id: "writer", label: "Executive writer", kind: "custom", fork_origin: "common:writer:1.0", custom_reason: "Returned reporting vocabulary", task: { lifecycle: "running", status_detail: "Returned writer status" } },
  ],
  edges: [
    { id: "data-edge", source_id: "verifier", target_id: "writer", relationship: "data_flow", label: "Evidence" },
    { id: "state-edge", source_id: "writer", target_id: "verifier", relationship: "state_flow", label: "Ready" },
    { id: "iteration-edge", source_id: "writer", target_id: "verifier", relationship: "iteration", label: "Revise" },
  ],
  validation: {
    eligible: true,
    categories: [
      { category: "version", result: "passed" },
      { category: "schema", result: "passed" },
      { category: "tool_policy", result: "passed" },
      { category: "approval", result: "not_required" },
    ],
  },
  action_references: [
    { id: "run-graph-42", label: "Run returned graph", eligible: true, kind: "run" },
    { id: "retry-task-42", label: "Retry returned task", eligible: true, kind: "retry" },
  ],
  protected_canvas_sentinel: "DO_NOT_RENDER_CANVAS",
} as const satisfies GeneratedJsonObject;

const APPROVAL_PROJECTION = {
  state_label: "Awaiting human approval",
  pending_operation: "Promote returned version",
  evidence_revision: "evidence-revision-42",
  criteria: ["Returned criterion"],
  expiry: "2026-03-02T14:00:00Z",
  as_of: "2026-03-02T12:03:00Z",
  freshness: "Fresh",
  stale: false,
  redacted_artifact_references: [{ id: "artifact-42", label: "Returned artifact" }],
  quality_evidence_references: [
    { id: "evidence-l1-42", label: "L1 evidence", category: "l1_specification_validation", summary: "Returned L1 result" },
    { id: "evidence-l2-42", label: "L2 evidence", category: "l2_role_rubric_evaluation", summary: "Returned L2 result" },
    { id: "evidence-l3-42", label: "L3 evidence", category: "l3_baseline_preference", summary: "Returned L3 result" },
    { id: "evidence-critique-42", label: "Critique evidence", category: "critique", summary: "Returned critique result" },
    { id: "evidence-gate-42", label: "Gate evidence", category: "gate_outcome", summary: "Returned gate result" },
    { id: "evidence-human-42", label: "Human approval evidence", category: "human_approval", summary: "Returned human approval result" },
  ],
  action_references: [{ id: "approve-42", label: "Approve returned operation", eligible: true, kind: "approve", irreversible: true, freshness_critical: true }],
  protected_approval_sentinel: "DO_NOT_RENDER_APPROVAL",
} as const satisfies GeneratedJsonObject;

const ROLLOUT_PROJECTION = {
  selected_version: "common-agent@2.1",
  target_scope: "returned bounded organization scope",
  impact_summary: "returned impact summary",
  criteria: ["returned success criterion"],
  approval_state_label: "Approved",
  status_label: "Stopped",
  rollback_reference: "rollback-42",
  outcome_measurements: { success_rate: "returned measurement" },
  criterion_failed: true,
  stopped_progression_label: "Progression stopped by server",
  rollback_state_label: "Rollback ready",
  state_label: "Stale",
  as_of: "2026-03-02T12:04:00Z",
  freshness: "Expired",
  stale: true,
  action_references: [
    { id: "canary-42", label: "Run returned canary", eligible: true, kind: "canary", irreversible: true },
    { id: "rollout-refresh-42", label: "Refresh rollout", eligible: true, kind: "refresh" },
  ],
  protected_rollout_sentinel: "DO_NOT_RENDER_ROLLOUT",
} as const satisfies GeneratedJsonObject;

const KNOWLEDGE_REQUIREMENTS = {
  file_types: ["text/markdown", "application/pdf"],
  maximum_size_bytes: 1048576,
  ownership_requirement: "Organization-owned or licensed",
  retention_requirement: "Retain for 90 days",
} as const satisfies GeneratedJsonObject;

const KNOWLEDGE_IMPORT_PROJECTION = {
  state: "indexed",
  opaque_references: [{ id: "import-42", label: "Returned import reference" }],
  scan_result: "Returned malware scan result",
  indexing_result: "Returned index result",
  protected_import_sentinel: "DO_NOT_RENDER_IMPORT",
} as const satisfies GeneratedJsonObject;

const ARTIFACT_PROJECTION = {
  artifact_version: "artifact-42@3",
  parent_lineage: [{ id: "artifact-parent-42", label: "Returned parent artifact" }],
  technical_specification: { format: "markdown", size_bytes: 4096 },
  rights_and_consent_state: "consent verified",
  continuity_state: "continuity verified",
  quality_control_state: "quality passed",
  delivery_state: "ready",
  delivery_targets: ["returned archive"],
  provenance_reference: { id: "artifact-provenance-42", label: "Returned artifact provenance" },
  gate_approval: "pending",
  protected_artifact_sentinel: "DO_NOT_RENDER_ARTIFACT",
} as const satisfies GeneratedJsonObject;

const VA_PROJECTION = {
  va_projection: {
    template: "Returned VA template",
    production_phase: "Returned production phase",
    common_pattern_version: { id: "pattern-42", label: "Returned pattern v4" },
    common_agent_versions: [{
      canonical_identity: "Returned verifier identity",
      boundaries: "Returned verifier scope",
      responsibilities: ["Returned verification capability"],
      tool_policy: ["Returned tool policy"],
      runtime_policy: { max_iterations: "3" },
      quality_rubric: { threshold: "0.95" },
      critique_relationships: ["Returned critique relationship"],
      provenance_policy: ["Returned provenance obligation"],
      agent_version_id: "verifier@1.8.0",
    }],
    agent_tasks: [{
      task_id: "task-42",
      graph_revision: "graph-revision-42",
      dependencies: ["task-41"],
      approval_gate_ids: ["gate-42"],
      lifecycle_state: "manual_recovery_required",
      recovery_state: "Returned escalation required",
      budget: { budget_remaining: "10 credits" },
      checkpoint_reference: "checkpoint-42",
      pinned_agent_version_id: "verifier@1.8.0",
    }],
    artifact_handoffs: [{
      artifact_version: "artifact-42@3",
      parent_lineage: ["artifact-parent-42"],
      technical_specification: { format: "markdown" },
      rights_and_consent_state: "consent verified",
      continuity_state: "continuity verified",
      quality_control_state: "quality passed",
      delivery_state: "blocked",
      delivery_targets: ["returned archive"],
      provenance_reference: "artifact-provenance-42",
      gate_approval: "pending",
    }],
    critique_records: [{
      critique_state: "Returned critique pending",
      source_reference: "verifier@1.8.0",
      target_task_id: "task-42",
      message: "Returned critique message",
      submitted_at: "2026-03-02T12:05:00Z",
      evidence_references: [{ id: "va-critique-evidence-42", label: "Returned VA critique evidence", summary: "Returned critique evidence" }],
    }],
    quality_evidence: [
      { kind: "l1_specification_validation", evidence_reference: "Returned L1 result" },
      { kind: "l2_role_rubric_evaluation", evidence_reference: "Returned L2 result" },
      { kind: "l3_baseline_preference", evidence_reference: "Returned L3 result" },
      { kind: "critique", evidence_reference: "Returned critique result" },
      { kind: "gate_outcome", evidence_reference: "Returned gate result" },
      { kind: "human_approval", evidence_reference: "Returned human result" },
    ],
    approval_gates: [{
      state_label: "Approval gate unavailable",
      evidence_revision: "evidence-revision-42",
      criteria: ["Returned VA approval criterion"],
      action_references: [{ id: "va-refresh-42", label: "Refresh VA approval", eligible: true, kind: "refresh" }],
    }],
    pinned_provenance: { graph_revision_id: "graph-revision-42" },
    action_references: [{ id: "va-recover-42", label: "Recover returned VA task", eligible: true, kind: "recover" }],
  },
  protected_va_sentinel: "DO_NOT_RENDER_VA",
} as const satisfies GeneratedJsonObject;

function renderOperational(
  projection: GeneratedJsonObject,
  renderer: (props: {
    projection: GeneratedJsonObject;
    onAction: typeof HANDLERS.onAction;
    onEvidence: typeof HANDLERS.onEvidence;
    onFilterChange: typeof HANDLERS.onFilterChange;
    onReference: typeof HANDLERS.onReference;
  }) => JSX.Element,
): string {
  return renderToStaticMarkup(renderer({ projection, ...HANDLERS }));
}

test("composes representative dashboard, registry, and activity projections from returned data", () => {
  const dashboardMarkup = renderOperational(DASHBOARD_PROJECTION, Dashboard);
  const registryMarkup = renderOperational(REGISTRY_PROJECTION, Registry);
  const activityMarkup = renderOperational(ACTIVITY_PROJECTION, Activity);

  assert.match(dashboardMarkup, /Fleet health and common impact/);
  assert.match(dashboardMarkup, /Delayed event processing|3 agents degraded|12 queued runs/);
  assert.match(dashboardMarkup, /data-action-reference-id="dashboard-refresh"/);
  assert.match(dashboardMarkup, /data-evidence-reference-id="dashboard-evidence"/);
  assert.match(dashboardMarkup, /Affected run/);

  assert.match(registryMarkup, /common-agent:verifier/);
  assert.match(registryMarkup, /1\.8\.0/);
  assert.match(registryMarkup, /prov:verifier:1\.8\.0/);
  assert.match(registryMarkup, /Published/);
  assert.match(registryMarkup, /data-action-reference-id="registry-refresh"/);
  assert.doesNotMatch(registryMarkup, /DO_NOT_SUBMIT/);

  assert.match(activityMarkup, /graph-revision-42/);
  assert.match(activityMarkup, /waiting_for_critique/);
  assert.match(activityMarkup, /corr-activity-42/);
  assert.match(activityMarkup, /data-evidence-reference-id="activity-evidence"/);
  assert.doesNotMatch(`${dashboardMarkup}${registryMarkup}${activityMarkup}`, /DO_NOT_RENDER_(DASHBOARD|REGISTRY|ACTIVITY)/);
});

test("composes the graph canvas with semantic relationships, returned validation, lifecycle, and actions", () => {
  const markup = renderToStaticMarkup(<Canvas projection={CANVAS_PROJECTION} />);

  assert.match(markup, /Data flow: verifier to writer/);
  assert.match(markup, /State flow: writer to verifier/);
  assert.match(markup, /Iteration: writer to verifier/);
  assert.match(markup, /Common version: 1\.8\.0/);
  assert.match(markup, /Provenance: prov:verifier:1\.8\.0/);
  assert.match(markup, /waiting_for_critique/);
  assert.match(markup, /Returned critique is pending/);
  assert.match(markup, /tool_policy.*passed/);
  assert.match(markup, /data-action-reference-id="run-graph-42"/);
  assert.match(markup, /data-action-reference-id="retry-task-42"/);
  assert.doesNotMatch(markup, /DO_NOT_RENDER_CANVAS/);
});

test("composes approval and rollout projections with distinct evidence and exact stale action behavior", () => {
  const approvalMarkup = renderToStaticMarkup(<ApprovalGateScreen {...HANDLERS} projection={APPROVAL_PROJECTION} />);
  const rolloutMarkup = renderToStaticMarkup(<RolloutCampaignScreen {...HANDLERS} projection={ROLLOUT_PROJECTION} />);

  assert.match(approvalMarkup, /Awaiting human approval/);
  assert.match(approvalMarkup, /evidence-revision-42/);
  assert.match(approvalMarkup, /Returned artifact/);
  for (const category of [
    "l1_specification_validation",
    "l2_role_rubric_evaluation",
    "l3_baseline_preference",
    "critique",
    "gate_outcome",
    "human_approval",
  ]) assert.match(approvalMarkup, new RegExp(`data-evidence-category="${category}"`));
  assert.match(approvalMarkup, /data-action-reference-id="approve-42"/);

  assert.match(rolloutMarkup, /common-agent@2\.1/);
  assert.match(rolloutMarkup, /Progression stopped by server/);
  assert.match(rolloutMarkup, /Rollback ready/);
  assert.match(rolloutMarkup, /Stale/);
  assert.match(rolloutMarkup, /data-action-reference-id="canary-42" disabled=""/);
  assert.match(rolloutMarkup, /data-action-reference-id="rollout-refresh-42"/);
  assert.doesNotMatch(`${approvalMarkup}${rolloutMarkup}`, /DO_NOT_RENDER_(APPROVAL|ROLLOUT)/);
});

test("composes knowledge and artifact projections with returned ingress state and fail-closed delivery", () => {
  const markup = renderToStaticMarkup(<KnowledgeArtifactScreen
    artifactProjection={ARTIFACT_PROJECTION}
    importProjection={KNOWLEDGE_IMPORT_PROJECTION}
    kind="knowledge"
    onResolveReference={HANDLERS.onReference}
    requirements={undefined}
    ingestionRequirementsProjection={KNOWLEDGE_REQUIREMENTS}
  />);

  assert.match(markup, /text\/markdown, application\/pdf/);
  assert.match(markup, /1048576 bytes/);
  assert.match(markup, /Organization-owned or licensed/);
  assert.match(markup, /indexed/);
  assert.match(markup, /Returned import reference/);
  assert.match(markup, /Returned malware scan result/);
  assert.match(markup, /artifact-42@3/);
  assert.match(markup, /consent verified/);
  assert.match(markup, /Delivery blocked/);
  assert.match(markup, /Required gate approval is unavailable/);
  assert.doesNotMatch(markup, /DO_NOT_RENDER_(IMPORT|ARTIFACT)/);
});

test("composes returned VA domain data, quality categories, approval availability, and recovery action", () => {
  const markup = renderToStaticMarkup(<VaProjectionScreen {...HANDLERS} projection={VA_PROJECTION} />);

  assert.match(markup, /Returned VA template/);
  assert.match(markup, /Returned production phase/);
  assert.match(markup, /Returned pattern v4/);
  assert.match(markup, /Returned verifier identity/);
  assert.match(markup, /manual_recovery_required/);
  assert.match(markup, /Returned escalation required/);
  assert.match(markup, /Delivery blocked/);
  assert.match(markup, /Approval gate unavailable/);
  for (const category of [
    "l1_specification_validation",
    "l2_role_rubric_evaluation",
    "l3_baseline_preference",
    "critique",
    "gate_outcome",
    "human_approval",
  ]) assert.match(markup, new RegExp(`data-evidence-category="${category}"`));
  assert.match(markup, /data-action-reference-id="va-recover-42"/);
  assert.doesNotMatch(markup, /DO_NOT_RENDER_VA/);
});

test("capability-unavailable composition keeps shell context and suppresses protected screen content", () => {
  const definition = getScreenDefinition("ui_15_api_portal");
  const fixture = getScreenFixture("ui_15_api_portal");
  const markup = renderToStaticMarkup(<ScreenBoundary
    capabilities={[]}
    definition={definition}
    shell={<header>Returned authorized shell</header>}
    unavailableState={{ error: fixture.unavailableError }}
  >
    <div>Protected developer API projection</div>
  </ScreenBoundary>);

  assert.match(markup, /Returned authorized shell/);
  assert.match(markup, /Screen unavailable/);
  assert.match(markup, /This authorized screen is currently unavailable\./);
  assert.doesNotMatch(markup, /Protected developer API projection/);
});

test("mobile projection preserves returned status, evidence, and action information at the supported viewport", () => {
  const mobileDefinition = getScreenDefinition("ui_17_mobile");
  assert.deepEqual(mobileDefinition.viewports, [{ width: 390, height: 844 }]);
  assert.ok(mobileDefinition.viewports[0]!.width >= 320 && mobileDefinition.viewports[0]!.width <= 767);

  const markup = renderToStaticMarkup(<ResponsiveStack className="mobile-projection">
    <Dashboard projection={DASHBOARD_PROJECTION} {...HANDLERS} />
  </ResponsiveStack>);

  assert.match(markup, /mobile-projection/);
  assert.match(markup, /Status: Degraded/);
  assert.match(markup, /2026-03-02T12:00:00Z/);
  assert.match(markup, /Delayed/);
  assert.match(markup, /data-action-reference-id="dashboard-refresh"/);
  assert.match(markup, /data-evidence-reference-id="dashboard-evidence"/);
  assert.doesNotMatch(markup, /DO_NOT_RENDER_DASHBOARD/);
});
