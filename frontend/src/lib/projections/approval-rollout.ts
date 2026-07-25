import type { GeneratedJsonObject, GeneratedJsonValue } from "../api/client";
import {
  ProjectionMapper,
  type ActionReferenceView,
  type EvidenceReferenceView,
  type OpaqueReferenceView,
} from "./ProjectionMapper";

export const QUALITY_EVIDENCE_CATEGORIES = [
  "l1_specification_validation",
  "l2_role_rubric_evaluation",
  "l3_baseline_preference",
  "critique",
  "gate_outcome",
  "human_approval",
] as const;

export type QualityEvidenceCategory = (typeof QUALITY_EVIDENCE_CATEGORIES)[number] | (string & {});

export interface QualityEvidenceView {
  readonly category: QualityEvidenceCategory;
  readonly reference: EvidenceReferenceView;
}

export interface ProjectionFreshnessView {
  readonly stateLabel: string;
  readonly asOf?: string;
  readonly freshness?: string;
  readonly degradedState?: string | boolean;
  readonly stale: boolean;
}

export interface ApprovalGateProjectionView {
  readonly approvalStateLabel?: string;
  readonly pendingOperation?: string;
  readonly evidenceRevision?: string;
  readonly criteria: readonly GeneratedJsonValue[];
  readonly expiry?: string;
  readonly artifactReferences: readonly OpaqueReferenceView[];
  readonly qualityEvidence: readonly QualityEvidenceView[];
  readonly actions: readonly ActionReferenceView[];
  readonly decisionActions: readonly ActionReferenceView[];
  readonly status?: ProjectionFreshnessView;
  readonly stale: boolean;
}

export interface RolloutCampaignProjectionView {
  readonly selectedVersion?: string;
  readonly targetScope?: GeneratedJsonValue;
  readonly impactSummary?: GeneratedJsonValue;
  readonly criteria: readonly GeneratedJsonValue[];
  readonly approvalStateLabel?: string;
  readonly statusLabel?: string;
  readonly rollbackReference?: GeneratedJsonValue;
  readonly outcomeMeasurements?: GeneratedJsonValue;
  readonly stoppedProgressionLabel?: string;
  readonly rollbackStateLabel?: string;
  readonly criterionFailed: boolean;
  readonly actions: readonly ActionReferenceView[];
  readonly status?: ProjectionFreshnessView;
  readonly stale: boolean;
}

export interface ApprovalEvidenceRevisionState {
  readonly projectionRevision?: string;
  readonly observedRevision?: string;
  readonly requiresRefresh: boolean;
}

const MAPPER = new ProjectionMapper();
const APPROVAL_ACTION_KINDS = new Set([
  "approve",
  "deny",
  "decision",
  "reject",
  "review",
  "request_review",
  "submit_decision",
]);

/** Maps the returned approval projection without creating decision or evidence data. */
export function mapApprovalGateProjection(projection: GeneratedJsonObject): ApprovalGateProjectionView {
  const actions = mapActionReferences(projection.action_references);
  const returnedDecisionActions = mapActionReferences(projection.decision_action_references);
  const decisionActions = hasArrayField(projection, "decision_action_references")
    ? returnedDecisionActions
    : actions.filter((action) => action.kind === undefined
      ? action.kind !== "refresh" && action.kind !== "reconnect"
      : APPROVAL_ACTION_KINDS.has(action.kind));
  const approvalStateLabel = firstString(projection, ["approval_state_label", "state_label"]);
  const stale = projection.stale === true;

  return {
    ...(approvalStateLabel === undefined ? {} : { approvalStateLabel }),
    ...(stringValue(projection.pending_operation) === undefined ? {} : { pendingOperation: stringValue(projection.pending_operation) }),
    ...(stringValue(projection.evidence_revision) === undefined ? {} : { evidenceRevision: stringValue(projection.evidence_revision) }),
    criteria: returnedValues(projection.criteria),
    ...(stringValue(projection.expiry) === undefined ? {} : { expiry: stringValue(projection.expiry) }),
    artifactReferences: mapOpaqueReferences(projection.redacted_artifact_references ?? projection.artifact_references),
    qualityEvidence: mapQualityEvidence(projection.quality_evidence_references ?? projection.quality_evidence),
    actions,
    decisionActions,
    ...(mapProjectionFreshness(projection, approvalStateLabel, stale) === undefined ? {} : { status: mapProjectionFreshness(projection, approvalStateLabel, stale) }),
    stale,
  };
}

/** Maps the returned rollout projection, including exact returned stop/rollback labels. */
export function mapRolloutCampaignProjection(projection: GeneratedJsonObject): RolloutCampaignProjectionView {
  const statusLabel = firstString(projection, ["status_label", "state_label"]);
  const approvalStateLabel = stringValue(projection.approval_state_label);
  const stale = projection.stale === true;

  return {
    ...(stringValue(projection.selected_version) === undefined ? {} : { selectedVersion: stringValue(projection.selected_version) }),
    ...(projection.target_scope === undefined ? {} : { targetScope: projection.target_scope }),
    ...(projection.impact_summary === undefined ? {} : { impactSummary: projection.impact_summary }),
    criteria: returnedValues(projection.criteria),
    ...(approvalStateLabel === undefined ? {} : { approvalStateLabel }),
    ...(statusLabel === undefined ? {} : { statusLabel }),
    ...(projection.rollback_reference === undefined ? {} : { rollbackReference: projection.rollback_reference }),
    ...(projection.outcome_measurements === undefined ? {} : { outcomeMeasurements: projection.outcome_measurements }),
    ...(stringValue(projection.stopped_progression_label) === undefined ? {} : { stoppedProgressionLabel: stringValue(projection.stopped_progression_label) }),
    ...(stringValue(projection.rollback_state_label) === undefined ? {} : { rollbackStateLabel: stringValue(projection.rollback_state_label) }),
    criterionFailed: projection.criterion_failed === true,
    actions: mapActionReferences(projection.action_references),
    ...(mapProjectionFreshness(projection, statusLabel, stale) === undefined ? {} : { status: mapProjectionFreshness(projection, statusLabel, stale) }),
    stale,
  };
}

/** Creates revision state from the projection that is currently rendered. */
export function createApprovalEvidenceRevisionState(projectionRevision?: string): ApprovalEvidenceRevisionState {
  return {
    ...(projectionRevision === undefined ? {} : { projectionRevision }),
    requiresRefresh: false,
  };
}

/** Marks a gate stale when a returned evidence revision changes before its refresh. */
export function observeApprovalEvidenceRevisionChange(
  state: ApprovalEvidenceRevisionState,
  observedRevision: string,
): ApprovalEvidenceRevisionState {
  return {
    ...state,
    observedRevision,
    requiresRefresh: state.projectionRevision !== observedRevision,
  };
}

/** Accepts a fresh projection only when it matches the observed revision. */
export function markApprovalGateProjectionRefreshed(
  state: ApprovalEvidenceRevisionState,
  projectionRevision: string,
): ApprovalEvidenceRevisionState {
  const matchesObservedRevision = state.observedRevision === undefined || state.observedRevision === projectionRevision;
  return {
    projectionRevision,
    ...(state.observedRevision === undefined ? {} : { observedRevision: state.observedRevision }),
    requiresRefresh: !matchesObservedRevision,
  };
}

export function isApprovalGateProjectionFresh(
  projection: ApprovalGateProjectionView,
  expectedEvidenceRevision?: string,
  revisionState?: ApprovalEvidenceRevisionState,
): boolean {
  if (projection.stale) return false;
  if (expectedEvidenceRevision !== undefined && projection.evidenceRevision !== expectedEvidenceRevision) return false;
  return revisionState?.requiresRefresh !== true;
}

/** Decision actions require a fresh matching gate as well as returned eligibility. */
export function isApprovalDecisionActionEnabled(
  action: ActionReferenceView,
  projection: ApprovalGateProjectionView,
  expectedEvidenceRevision?: string,
  revisionState?: ApprovalEvidenceRevisionState,
): boolean {
  return action.eligible && isApprovalGateProjectionFresh(projection, expectedEvidenceRevision, revisionState);
}

/** Uses the same stale-action rule as ActionControl for non-decision rollout actions. */
export function isFreshnessCriticalActionBlocked(action: ActionReferenceView, stale: boolean): boolean {
  return stale
    && action.kind !== "refresh"
    && action.kind !== "reconnect"
    && (action.freshnessCritical === true || action.irreversible === true);
}

function mapProjectionFreshness(
  projection: GeneratedJsonObject,
  stateLabel: string | undefined,
  stale: boolean,
): ProjectionFreshnessView | undefined {
  if (stateLabel === undefined) return undefined;
  const asOf = stringValue(projection.as_of);
  const freshness = stringValue(projection.freshness);
  const degradedState = projection.degraded_state;
  return {
    stateLabel,
    ...(asOf === undefined ? {} : { asOf }),
    ...(freshness === undefined ? {} : { freshness }),
    ...(typeof degradedState === "string" || typeof degradedState === "boolean" ? { degradedState } : {}),
    stale,
  };
}

function mapQualityEvidence(value: GeneratedJsonValue | undefined): readonly QualityEvidenceView[] {
  return objectList(value).flatMap((source): readonly QualityEvidenceView[] => {
    const category = stringValue(source.category) ?? stringValue(source.evidence_category) ?? stringValue(source.kind);
    const evidenceSource = objectValue(source.evidence_reference) ?? source;
    const reference = MAPPER.mapEvidenceReference(evidenceSource, ["summary"]);
    if (category === undefined || reference === null) return [];
    return [{ category, reference }];
  });
}

function mapActionReferences(value: GeneratedJsonValue | undefined): readonly ActionReferenceView[] {
  return objectList(value).flatMap((source): readonly ActionReferenceView[] => {
    const action = MAPPER.mapActionReference(source);
    return action === null ? [] : [action];
  });
}

function mapOpaqueReferences(value: GeneratedJsonValue | undefined): readonly OpaqueReferenceView[] {
  return objectList(value).flatMap((source): readonly OpaqueReferenceView[] => {
    const reference = MAPPER.mapOpaqueReference(source);
    return reference === null ? [] : [reference];
  });
}

function returnedValues(value: GeneratedJsonValue | undefined): readonly GeneratedJsonValue[] {
  if (value === undefined) return [];
  return Array.isArray(value) ? value : [value];
}

function objectList(value: GeneratedJsonValue | undefined): readonly GeneratedJsonObject[] {
  return Array.isArray(value)
    ? value.filter((item): item is GeneratedJsonObject => objectValue(item) !== undefined)
    : [];
}

function objectValue(value: GeneratedJsonValue | undefined): GeneratedJsonObject | undefined {
  return typeof value === "object" && value !== null && !Array.isArray(value) ? value as GeneratedJsonObject : undefined;
}

function hasArrayField(projection: GeneratedJsonObject, key: string): boolean {
  return Array.isArray(projection[key]);
}

function firstString(projection: GeneratedJsonObject, keys: readonly string[]): string | undefined {
  for (const key of keys) {
    const value = stringValue(projection[key]);
    if (value !== undefined) return value;
  }
  return undefined;
}

function stringValue(value: GeneratedJsonValue | undefined): string | undefined {
  return typeof value === "string" ? value : undefined;
}
