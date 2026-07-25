import type { GeneratedJsonObject, GeneratedJsonValue } from "../api/client";
import {
  ProjectionMapper,
  type ActionReferenceView,
  type EvidenceReferenceView,
  type OpaqueReferenceView,
  type ProjectionView,
} from "./ProjectionMapper";

export const OPERATIONAL_SCREEN_KINDS = [
  "dashboard",
  "registry",
  "componentDetail",
  "activity",
  "monitoring",
  "notifications",
  "audit",
  "profile",
  "evaluation",
] as const;

export type OperationalScreenKind = (typeof OPERATIONAL_SCREEN_KINDS)[number];

export interface GeneratedFilterOptionView {
  readonly label: string;
  readonly value: string;
  readonly source: GeneratedJsonObject;
}

export interface GeneratedFilterView {
  readonly id: string;
  readonly label: string;
  readonly options: readonly GeneratedFilterOptionView[];
  readonly source: GeneratedJsonObject;
}

export interface ScreenFieldView {
  readonly key: string;
  readonly label: string;
  readonly value: string;
}

export interface ScreenSectionView {
  readonly heading: string;
  readonly fields: readonly ScreenFieldView[];
  readonly actions: readonly ActionReferenceView[];
  readonly evidence: readonly EvidenceReferenceView[];
}

export interface ScreenAlertView {
  readonly summary: string;
  readonly affectedReference: OpaqueReferenceView;
}

export interface GeneratedScreenProjectionView {
  readonly fields: ProjectionView;
  readonly status?: {
    readonly stateLabel: string;
    readonly asOf?: string;
    readonly freshness?: string;
    readonly degradedState?: string | boolean;
    readonly stale: boolean;
  };
  readonly filters: readonly GeneratedFilterView[];
  readonly sections: readonly ScreenSectionView[];
  readonly actions: readonly ActionReferenceView[];
  readonly evidence: readonly EvidenceReferenceView[];
  readonly alerts: readonly ScreenAlertView[];
}

const SCREEN_FIELD_ALLOWLIST: Readonly<Record<OperationalScreenKind, readonly string[]>> = {
  dashboard: ["title", "description", "health", "fleet_state", "approval_alert", "backlog", "common_version_impact", "summary"],
  registry: ["title", "description", "immutable_identifier", "version", "status", "provenance_reference", "compatibility_state", "aggregate_metrics", "summary"],
  componentDetail: ["title", "description", "published_contract", "version_history", "evaluation_summary", "usage_summary", "summary"],
  activity: ["title", "description", "graph_revision", "common_versions", "lifecycle", "dependency", "checkpoint", "retry", "failure", "recovery", "summary", "correlation_identifier"],
  monitoring: ["title", "description", "health", "fleet_state", "backlog", "summary"],
  notifications: ["title", "description", "priority", "status", "summary", "correlation_identifier"],
  audit: ["title", "description", "timestamp", "action_type", "target", "status", "summary", "correlation_identifier", "provenance_reference"],
  profile: ["title", "description", "identity", "usage_summary", "impact_summary", "preferences", "summary"],
  evaluation: ["title", "description", "evaluation_summary", "quality_l1", "quality_l2", "quality_l3", "gate_outcome", "summary"],
};

const SECTION_FIELD_ALLOWLIST = [
  "immutable_identifier", "version", "status", "provenance_reference", "compatibility_state", "aggregate_metrics",
  "published_contract", "version_history", "evaluation_summary", "usage_summary", "graph_revision", "common_versions",
  "lifecycle", "dependency", "checkpoint", "retry", "failure", "recovery", "health", "fleet_state", "approval_alert",
  "backlog", "common_version_impact", "priority", "timestamp", "action_type", "target", "identity", "impact_summary",
  "preferences", "quality_l1", "quality_l2", "quality_l3", "gate_outcome", "summary", "correlation_identifier",
] as const;

const FIELD_LABELS: Readonly<Record<string, string>> = {
  immutable_identifier: "Immutable identifier",
  version: "Version",
  status: "Status",
  provenance_reference: "Provenance reference",
  compatibility_state: "Compatibility",
  aggregate_metrics: "Aggregate metrics",
  published_contract: "Published contract",
  version_history: "Version history",
  evaluation_summary: "Evaluation summary",
  usage_summary: "Usage summary",
  graph_revision: "Pinned graph revision",
  common_versions: "Pinned common versions",
  lifecycle: "Lifecycle",
  dependency: "Dependency",
  checkpoint: "Checkpoint",
  retry: "Retry",
  failure: "Failure",
  recovery: "Recovery",
  health: "Health",
  fleet_state: "Fleet state",
  approval_alert: "Approval alert",
  backlog: "Backlog",
  common_version_impact: "Common-version impact",
  priority: "Priority",
  timestamp: "Timestamp",
  action_type: "Action type",
  target: "Target",
  identity: "Identity",
  impact_summary: "Impact summary",
  preferences: "Preferences",
  quality_l1: "L1 specification validation",
  quality_l2: "L2 role-rubric evaluation",
  quality_l3: "L3 baseline preference",
  gate_outcome: "Gate outcome",
  summary: "Summary",
  correlation_identifier: "Correlation identifier",
};

const MAPPER = new ProjectionMapper();

/** Maps only known fields and returned references from a generated screen projection. */
export function mapGeneratedScreenProjection(
  kind: OperationalScreenKind,
  projection: GeneratedJsonObject,
): GeneratedScreenProjectionView {
  const fields = MAPPER.map(projection, SCREEN_FIELD_ALLOWLIST[kind]);
  const actions = mapActions(projection.action_references);
  return {
    fields,
    ...(mapStatus(projection) === undefined ? {} : { status: mapStatus(projection) }),
    filters: mapFilters(projection.filters),
    sections: mapSections(projection.sections),
    actions,
    evidence: mapEvidence(projection.evidence_references),
    alerts: mapAlerts(projection.alerts),
  };
}

/** Preserves the selected generated filter option so callers never submit client-created values. */
export function selectGeneratedFilterOption(
  filter: GeneratedFilterView,
  value: string,
): GeneratedJsonObject | undefined {
  return filter.options.find((option) => option.value === value)?.source;
}

function mapStatus(projection: GeneratedJsonObject): GeneratedScreenProjectionView["status"] {
  const stateLabel = stringValue(projection.state_label);
  if (stateLabel === undefined) return undefined;
  const asOf = stringValue(projection.as_of);
  const freshness = stringValue(projection.freshness);
  const degradedState = primitiveValue(projection.degraded_state);
  return {
    stateLabel,
    ...(asOf === undefined ? {} : { asOf }),
    ...(freshness === undefined ? {} : { freshness }),
    ...(typeof degradedState === "string" || typeof degradedState === "boolean" ? { degradedState } : {}),
    stale: projection.stale === true,
  };
}

function mapFilters(value: GeneratedJsonValue | undefined): readonly GeneratedFilterView[] {
  return objectList(value).flatMap((source): readonly GeneratedFilterView[] => {
    const id = stringValue(source.id);
    const label = stringValue(source.label);
    if (id === undefined || label === undefined) return [];
    const options = objectList(source.options).flatMap((option): readonly GeneratedFilterOptionView[] => {
      const optionLabel = stringValue(option.label);
      const optionValue = primitiveValue(option.value);
      if (optionLabel === undefined || optionValue === undefined) return [];
      return [{ label: optionLabel, value: String(optionValue), source: option }];
    });
    return options.length === 0 ? [] : [{ id, label, options, source }];
  });
}

function mapSections(value: GeneratedJsonValue | undefined): readonly ScreenSectionView[] {
  return objectList(value).flatMap((section): readonly ScreenSectionView[] => {
    const heading = stringValue(section.heading);
    if (heading === undefined) return [];
    const fields = MAPPER.map(section, SECTION_FIELD_ALLOWLIST);
    return [{
      heading,
      fields: toScreenFields(fields),
      actions: mapActions(section.action_references),
      evidence: mapEvidence(section.evidence_references),
    }];
  });
}

function mapAlerts(value: GeneratedJsonValue | undefined): readonly ScreenAlertView[] {
  return objectList(value).flatMap((alert): readonly ScreenAlertView[] => {
    const summary = stringValue(alert.summary);
    const reference = objectValue(alert.affected_reference);
    const affectedReference = reference === undefined ? null : MAPPER.mapOpaqueReference(reference);
    return summary === undefined || affectedReference === null ? [] : [{ summary, affectedReference }];
  });
}

function mapActions(value: GeneratedJsonValue | undefined): readonly ActionReferenceView[] {
  return objectList(value).flatMap((reference): readonly ActionReferenceView[] => {
    const mapped = MAPPER.mapActionReference(reference);
    return mapped === null ? [] : [mapped];
  });
}

function mapEvidence(value: GeneratedJsonValue | undefined): readonly EvidenceReferenceView[] {
  return objectList(value).flatMap((reference): readonly EvidenceReferenceView[] => {
    const mapped = MAPPER.mapEvidenceReference(reference, ["summary"]);
    return mapped === null ? [] : [mapped];
  });
}

function toScreenFields(fields: ProjectionView): readonly ScreenFieldView[] {
  return Object.entries(fields.fields).flatMap(([key, value]): readonly ScreenFieldView[] => {
    const displayValue = primitiveValue(value);
    const label = FIELD_LABELS[key];
    return displayValue === undefined || label === undefined ? [] : [{ key, label, value: String(displayValue) }];
  });
}

function objectList(value: GeneratedJsonValue | undefined): readonly GeneratedJsonObject[] {
  return Array.isArray(value) ? value.filter((item): item is GeneratedJsonObject => objectValue(item) !== undefined) : [];
}

function objectValue(value: GeneratedJsonValue | undefined): GeneratedJsonObject | undefined {
  return typeof value === "object" && value !== null && !Array.isArray(value) ? value as GeneratedJsonObject : undefined;
}

function stringValue(value: GeneratedJsonValue | undefined): string | undefined {
  return typeof value === "string" ? value : undefined;
}

function primitiveValue(value: GeneratedJsonValue | undefined): string | number | boolean | undefined {
  return typeof value === "string" || typeof value === "number" || typeof value === "boolean" ? value : undefined;
}
