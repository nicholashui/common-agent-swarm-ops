import assert from "node:assert/strict";
import test from "node:test";

import React from "react";
import { renderToStaticMarkup } from "react-dom/server";

import type { GeneratedJsonObject } from "../lib/api/client";
import {
  mapGeneratedScreenProjection,
  selectGeneratedFilterOption,
  type OperationalScreenKind,
} from "../lib/projections/screen-renderers";
import {
  Activity,
  Audit,
  CommonComponentDetail,
  Dashboard,
  Evaluation,
  Monitoring,
  Notifications,
  Profile,
  Registry,
} from "./OperationalScreens";

const action = {
  id: "action-1",
  label: "Refresh operational projection",
  eligible: true,
  kind: "refresh",
} as const satisfies GeneratedJsonObject;
const evidence = {
  id: "evidence-1",
  label: "Returned evidence",
  summary: "Returned redacted evidence summary",
} as const satisfies GeneratedJsonObject;
const filterOption = {
  label: "Queued",
  value: "queued",
  internal_filter_sentinel: "FILTER_SENTINEL",
} as const satisfies GeneratedJsonObject;

function projectionFor(kind: OperationalScreenKind): GeneratedJsonObject {
  const screenFields: Readonly<Record<OperationalScreenKind, GeneratedJsonObject>> = {
    dashboard: { health: "Delayed", fleet_state: "Degraded", approval_alert: "Approval expires", backlog: "3 queued", common_version_impact: "2 affected" },
    registry: { immutable_identifier: "agent:verifier", version: "1.8", status: "published", provenance_reference: "prov-1", compatibility_state: "compatible", aggregate_metrics: "97.1% success" },
    componentDetail: { published_contract: "Verifier contract", version_history: "v1.7, v1.8", evaluation_summary: "Passed", usage_summary: "842 swarms" },
    activity: { graph_revision: "graph-42", common_versions: "Verifier v1.8", lifecycle: "manual_recovery_required", dependency: "Gate A", checkpoint: "checkpoint-9", retry: "2", failure: "timeout", recovery: "Escalate", correlation_identifier: "corr-activity-1" },
    monitoring: { health: "Delayed", fleet_state: "Stale", backlog: "Run backlog", summary: "Replay gap detected" },
    notifications: { priority: "high", status: "unread", summary: "Gate ready", correlation_identifier: "corr-notification-1" },
    audit: { timestamp: "2026-03-02T10:00:00Z", action_type: "rollout", target: "Verifier v1.8", status: "recorded", summary: "Returned audit summary", correlation_identifier: "corr-audit-1", provenance_reference: "prov-audit-1" },
    profile: { identity: "Returned actor profile", usage_summary: "12 runs", impact_summary: "4 improvements", preferences: "Returned preferences" },
    evaluation: { evaluation_summary: "Returned evaluation", quality_l1: "passed", quality_l2: "passed", quality_l3: "baseline preferred", gate_outcome: "review required" },
  };
  return {
    title: `${kind} returned title`,
    description: `${kind} returned description`,
    state_label: "Delayed",
    as_of: "2026-03-02T12:00:00Z",
    freshness: "Delayed",
    degraded_state: "degraded",
    stale: false,
    filters: [{ id: "lifecycle", label: "Lifecycle", options: [filterOption] }],
    action_references: [action],
    evidence_references: [evidence],
    alerts: [{ summary: "Returned redacted alert", affected_reference: { id: "run-1", label: "Affected run" } }],
    sections: [{ heading: "Returned section", ...screenFields[kind], action_references: [action], evidence_references: [evidence] }],
    protected_sentinel: "PROTECTED_SENTINEL",
  };
}

const handlers = {
  onAction: (): void => {},
  onEvidence: (): void => {},
  onFilterChange: (): void => {},
  onReference: (): void => {},
};

// Requirements 5.1–5.9, 6.1–6.7, 6.17, 11.11, 12.1–12.9
const renderers: Readonly<Record<OperationalScreenKind, (projection: GeneratedJsonObject) => JSX.Element>> = {
  dashboard: (projection) => <Dashboard projection={projection} {...handlers} />,
  registry: (projection) => <Registry projection={projection} {...handlers} />,
  componentDetail: (projection) => <CommonComponentDetail projection={projection} {...handlers} />,
  activity: (projection) => <Activity projection={projection} {...handlers} />,
  monitoring: (projection) => <Monitoring projection={projection} {...handlers} />,
  notifications: (projection) => <Notifications projection={projection} {...handlers} />,
  audit: (projection) => <Audit projection={projection} {...handlers} />,
  profile: (projection) => <Profile projection={projection} {...handlers} />,
  evaluation: (projection) => <Evaluation projection={projection} {...handlers} />,
};

test("operational renderers present only allowlisted generated fields, status, references, and evidence", () => {
  for (const [kind, render] of Object.entries(renderers) as readonly [OperationalScreenKind, (projection: GeneratedJsonObject) => JSX.Element][]) {
    const markup = renderToStaticMarkup(render(projectionFor(kind)));

    assert.match(markup, /Status: Delayed/);
    assert.match(markup, /2026-03-02T12:00:00Z/);
    assert.match(markup, /data-action-reference-id="action-1"/);
    assert.match(markup, /data-evidence-reference-id="evidence-1"/);
    assert.match(markup, /Returned redacted alert/);
    assert.match(markup, /aria-label="Generated filters"/);
    assert.doesNotMatch(markup, /PROTECTED_SENTINEL|FILTER_SENTINEL/);
  }
});

test("registry and activity mapping retain returned provenance, lifecycle, and generated filter source", () => {
  const registry = mapGeneratedScreenProjection("registry", projectionFor("registry"));
  const activity = mapGeneratedScreenProjection("activity", projectionFor("activity"));
  const lifecycleFilter = registry.filters[0];
  const registrySection = registry.sections[0];
  const activitySection = activity.sections[0];
  if (lifecycleFilter === undefined || registrySection === undefined || activitySection === undefined) {
    throw new Error("Expected generated filters and sections.");
  }

  assert.deepEqual(registrySection.fields.filter(({ key }) => key === "immutable_identifier"), [{ key: "immutable_identifier", label: "Immutable identifier", value: "agent:verifier" }]);
  assert.deepEqual(registrySection.fields.filter(({ key }) => key === "provenance_reference"), [{ key: "provenance_reference", label: "Provenance reference", value: "prov-1" }]);
  assert.deepEqual(activitySection.fields.filter(({ key }) => key === "graph_revision"), [{ key: "graph_revision", label: "Pinned graph revision", value: "graph-42" }]);
  assert.deepEqual(activitySection.fields.filter(({ key }) => key === "lifecycle"), [{ key: "lifecycle", label: "Lifecycle", value: "manual_recovery_required" }]);
  assert.strictEqual(selectGeneratedFilterOption(lifecycleFilter, "queued"), filterOption);
  assert.equal(selectGeneratedFilterOption(lifecycleFilter, "client-created"), undefined);
});
