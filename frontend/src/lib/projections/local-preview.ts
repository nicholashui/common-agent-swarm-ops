import type { GeneratedActionReference, GeneratedJsonObject } from "../api/client";
import type { OperationalScreenKind } from "./screen-renderers";

/** No-op handlers for local preview routes (mutations require returned action contracts). */
export const LOCAL_PREVIEW_HANDLERS = {
  onAction: (_action: GeneratedActionReference): void => undefined,
  onEvidence: (_evidence: GeneratedJsonObject): void => undefined,
  onFilterChange: (
    _filter: GeneratedJsonObject,
    _option: GeneratedJsonObject,
  ): void => undefined,
  onReference: (_reference: GeneratedJsonObject): void => undefined,
} as const;

const BASE = {
  state_label: "Ready",
  as_of: "local",
  freshness: "Local preview",
  stale: false,
  action_references: [] as const,
  evidence_references: [] as const,
  alerts: [] as const,
  filters: [] as const,
} as const;

function screen(
  kind: OperationalScreenKind,
  fields: GeneratedJsonObject,
): GeneratedJsonObject {
  return {
    ...BASE,
    title: `Local ${kind} preview`,
    description:
      "The backend projection is not connected; showing safe local preview data.",
    ...fields,
  } as const satisfies GeneratedJsonObject;
}

export const LOCAL_DASHBOARD_PROJECTION = screen("dashboard", {
  health: "Waiting for backend projection",
  fleet_state: "No live runs loaded",
  backlog: "No live run data",
  approval_alert: "No approval alerts",
  common_version_impact: "No version impact loaded",
});

export const LOCAL_REGISTRY_PROJECTION = screen("registry", {
  immutable_identifier: "local:preview-registry",
  version: "0.0.0-local",
  status: "preview",
  provenance_reference: "local:preview",
  compatibility_state: "not evaluated",
  aggregate_metrics: "No aggregate metrics",
});

export const LOCAL_COMPONENT_DETAIL_PROJECTION = screen("componentDetail", {
  published_contract: "Local preview contract",
  version_history: "No version history loaded",
  evaluation_summary: "No evaluation summary",
  usage_summary: "No usage summary",
});

export const LOCAL_ACTIVITY_PROJECTION = screen("activity", {
  graph_revision: "local-preview",
  common_versions: "none",
  lifecycle: "queued",
  dependency: "none",
  checkpoint: "none",
  retry: "0",
  failure: "none",
  recovery: "not required",
  correlation_identifier: "local-preview",
});

export const LOCAL_MONITORING_PROJECTION = screen("monitoring", {
  health: "Local preview",
  fleet_state: "No live fleet state",
  backlog: "No backlog loaded",
  summary: "Monitoring projection not connected",
});

export const LOCAL_NOTIFICATIONS_PROJECTION = screen("notifications", {
  priority: "normal",
  status: "none",
  summary: "No notifications loaded",
  correlation_identifier: "local-preview",
});

export const LOCAL_AUDIT_PROJECTION = screen("audit", {
  timestamp: "local",
  action_type: "preview",
  target: "none",
  status: "none",
  summary: "No audit records loaded",
  correlation_identifier: "local-preview",
  provenance_reference: "local:preview",
});

export const LOCAL_PROFILE_PROJECTION = screen("profile", {
  identity: "Local preview actor",
  usage_summary: "No usage loaded",
  impact_summary: "No impact loaded",
  preferences: "Preferences projection not connected",
});

export const LOCAL_EVALUATION_PROJECTION = screen("evaluation", {
  evaluation_summary: "No evaluation campaigns loaded",
  quality_l1: "not run",
  quality_l2: "not run",
  quality_l3: "not run",
  gate_outcome: "not evaluated",
});

export const LOCAL_APPROVAL_PROJECTION = {
  ...BASE,
  state_label: "Local preview",
  pending_operation: "No pending approval",
  evidence_revision: "local-preview",
  criteria: ["Awaiting authorized approval projection"],
  expiry: "local",
  redacted_artifact_references: [],
  quality_evidence_references: [],
  action_references: [],
} as const satisfies GeneratedJsonObject;

export const LOCAL_KNOWLEDGE_REQUIREMENTS = {
  file_types: ["text/markdown", "application/pdf"],
  maximum_size_bytes: 1_048_576,
  ownership_requirement: "Organization-owned or licensed (preview)",
  retention_requirement: "Preview only — retention not enforced locally",
} as const satisfies GeneratedJsonObject;

export const LOCAL_KNOWLEDGE_IMPORT_PROJECTION = {
  state: "indexed",
  opaque_references: [
    { id: "local-import", label: "Local preview import reference" },
  ],
  scan_result: "Not scanned (local preview)",
  indexing_result: "Not indexed (local preview)",
} as const satisfies GeneratedJsonObject;

export interface LocalDestinationCopy {
  readonly eyebrow: string;
  readonly title: string;
  readonly description: string;
}

/** Copy for destinations that do not yet have a dedicated projection renderer. */
export const LOCAL_DESTINATION_COPY = {
  settings: {
    eyebrow: "SETTINGS",
    title: "Settings",
    description:
      "Returned preferences and policy summaries appear here when authorized. Local preview only.",
  },
  blueprints: {
    eyebrow: "BLUEPRINTS",
    title: "Blueprints",
    description:
      "Saved common patterns and governed templates. Awaiting authorized blueprint projection.",
  },
  costs: {
    eyebrow: "COSTS",
    title: "Costs",
    description:
      "Returned usage, budgets, and optimization projections. No client-created budget authority.",
  },
  collaboration: {
    eyebrow: "COLLABORATION",
    title: "Collaboration",
    description:
      "Sharing, comments, and proposal-review projections when authorized. No peer execution channel.",
  },
  apiPortal: {
    eyebrow: "API PORTAL",
    title: "API Portal",
    description:
      "Generated OpenAPI reference and integration guidance. Interactive calls use session context only.",
  },
  onboarding: {
    eyebrow: "ONBOARDING & HELP",
    title: "Onboarding & Help",
    description:
      "Tours, documentation, and guided projects. Help links are static or server-authorized.",
  },
  mobile: {
    eyebrow: "MOBILE OPERATIONS",
    title: "Mobile companion",
    description:
      "Compact operational status labels for live, delayed, reconnecting, and recovery states.",
  },
} as const satisfies Record<string, LocalDestinationCopy>;
