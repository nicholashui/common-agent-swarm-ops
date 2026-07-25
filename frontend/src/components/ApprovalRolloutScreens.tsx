"use client";

import React from "react";

import type { GeneratedActionReference, GeneratedJsonObject, GeneratedJsonValue } from "../lib/api/client";
import {
  isApprovalDecisionActionEnabled,
  mapApprovalGateProjection,
  mapRolloutCampaignProjection,
  type ApprovalEvidenceRevisionState,
  type ApprovalGateProjectionView,
  type QualityEvidenceView,
  type RolloutCampaignProjectionView,
} from "../lib/projections/approval-rollout";
import { ActionControl } from "./projection/ActionControl";
import { EvidenceLink } from "./projection/EvidenceLink";
import { ProjectionStatus } from "./projection/ProjectionStatus";
import { ReferenceLink } from "./projection/ReferenceLink";

export interface ApprovalRolloutScreenHandlers {
  readonly onAction: (action: GeneratedActionReference) => void;
  readonly onEvidence: (evidence: GeneratedJsonObject) => void;
  readonly onReference: (reference: GeneratedJsonObject) => void;
}

export interface ApprovalGateScreenProps extends ApprovalRolloutScreenHandlers {
  readonly projection: GeneratedJsonObject;
  /** Returned by a later observation; a mismatch disables decisions until refresh. */
  readonly currentEvidenceRevision?: string;
  readonly revisionState?: ApprovalEvidenceRevisionState;
  readonly pendingActionReferenceIds?: readonly string[];
}

export interface RolloutCampaignScreenProps extends ApprovalRolloutScreenHandlers {
  readonly projection: GeneratedJsonObject;
  readonly pendingActionReferenceIds?: readonly string[];
}

/** Renders only returned approval fields, evidence references, and action references. */
export function ApprovalGateScreen({
  projection,
  currentEvidenceRevision,
  revisionState,
  pendingActionReferenceIds = [],
  onAction,
  onEvidence,
  onReference,
}: ApprovalGateScreenProps): JSX.Element {
  const approval = mapApprovalGateProjection(projection);
  const decisionFresh = approval.decisionActions.every((action) => isApprovalDecisionActionEnabled(action, approval, currentEvidenceRevision, revisionState));

  return <section aria-label="Approval gate projection" className="approval-rollout-screen approval-gate-screen">
    <header className="page-header">
      <p className="eyebrow">APPROVAL GATE</p>
      <h1>Approval gate</h1>
    </header>
    {approval.status === undefined ? null : <ProjectionStatus
      actions={withoutRecoveryActions(approval.actions)}
      onInvokeAction={onAction}
      onResolveAlert={onReference}
      projection={approval.status}
      stale={approval.stale}
    />}
    <ApprovalGateDetails approval={approval} onReference={onReference} />
    <QualityEvidencePanel evidence={approval.qualityEvidence} onEvidence={onEvidence} />
    <ReturnedActionList
      actions={approval.actions}
      disabledActionIds={new Set(approval.decisionActions.filter((action) => !decisionFresh).map((action) => action.id))}
      pendingActionReferenceIds={pendingActionReferenceIds}
      stale={approval.stale}
      onAction={onAction}
      ariaLabel="Returned approval actions"
    />
  </section>;
}

/** Renders only returned rollout state, measurements, references, and actions. */
export function RolloutCampaignScreen({
  projection,
  pendingActionReferenceIds = [],
  onAction,
  onEvidence,
  onReference,
}: RolloutCampaignScreenProps): JSX.Element {
  const rollout = mapRolloutCampaignProjection(projection);

  return <section aria-label="Rollout campaign projection" className="approval-rollout-screen rollout-campaign-screen">
    <header className="page-header">
      <p className="eyebrow">ROLLOUT CAMPAIGN</p>
      <h1>Rollout campaign</h1>
    </header>
    {rollout.status === undefined ? null : <ProjectionStatus
      actions={withoutRecoveryActions(rollout.actions)}
      onInvokeAction={onAction}
      onResolveAlert={onReference}
      projection={rollout.status}
      stale={rollout.stale}
    />}
    <RolloutDetails rollout={rollout} />
    {rollout.criterionFailed ? <section aria-label="Failed rollout criterion" className="panel rollout-campaign__failure">
      <h2>Criterion failure</h2>
      {rollout.stoppedProgressionLabel === undefined ? null : <ReturnedField label="Stopped progression" value={rollout.stoppedProgressionLabel} />}
      {rollout.rollbackStateLabel === undefined ? null : <ReturnedField label="Rollback state" value={rollout.rollbackStateLabel} />}
    </section> : null}
    <QualityEvidencePanel evidence={mapQualityEvidenceForRollout(projection)} onEvidence={onEvidence} />
    <ReturnedActionList
      actions={rollout.actions}
      pendingActionReferenceIds={pendingActionReferenceIds}
      stale={rollout.stale}
      onAction={onAction}
      ariaLabel="Returned rollout actions"
    />
  </section>;
}

/** Alias used by callers that name the resource rather than the campaign. */
export const RolloutScreen = RolloutCampaignScreen;
export const ApprovalsScreen = ApprovalGateScreen;

function ApprovalGateDetails({ approval, onReference }: { readonly approval: ApprovalGateProjectionView; readonly onReference: (reference: GeneratedJsonObject) => void }): JSX.Element {
  return <section aria-label="Returned approval gate details" className="panel approval-gate__details">
    <h2>Returned approval details</h2>
    {approval.approvalStateLabel === undefined ? null : <ReturnedField label="Approval state" value={approval.approvalStateLabel} />}
    {approval.pendingOperation === undefined ? null : <ReturnedField label="Pending operation" value={approval.pendingOperation} />}
    {approval.evidenceRevision === undefined ? null : <ReturnedField label="Evidence revision" value={approval.evidenceRevision} />}
    {approval.expiry === undefined ? null : <ReturnedField label="Expiry" value={approval.expiry} />}
    {approval.criteria.length === 0 ? null : <ReturnedValues label="Criteria" values={approval.criteria} />}
    {approval.artifactReferences.length === 0 ? null : <div><h3>Redacted artifact references</h3><ul>{approval.artifactReferences.map((reference) => <li key={reference.id}><ReferenceLink onResolve={onReference} reference={reference} /></li>)}</ul></div>}
  </section>;
}

function RolloutDetails({ rollout }: { readonly rollout: RolloutCampaignProjectionView }): JSX.Element {
  return <section aria-label="Returned rollout details" className="panel rollout-campaign__details">
    <h2>Returned rollout details</h2>
    {rollout.selectedVersion === undefined ? null : <ReturnedField label="Selected version" value={rollout.selectedVersion} />}
    {rollout.approvalStateLabel === undefined ? null : <ReturnedField label="Approval state" value={rollout.approvalStateLabel} />}
    {rollout.statusLabel === undefined ? null : <ReturnedField label="Status" value={rollout.statusLabel} />}
    {rollout.targetScope === undefined ? null : <ReturnedField label="Bounded target scope" value={returnedValueText(rollout.targetScope)} />}
    {rollout.impactSummary === undefined ? null : <ReturnedField label="Impact summary" value={returnedValueText(rollout.impactSummary)} />}
    {rollout.criteria.length === 0 ? null : <ReturnedValues label="Criteria" values={rollout.criteria} />}
    {rollout.rollbackReference === undefined ? null : <ReturnedField label="Rollback reference" value={returnedValueText(rollout.rollbackReference)} />}
    {rollout.outcomeMeasurements === undefined ? null : <ReturnedField label="Outcome measurements" value={returnedValueText(rollout.outcomeMeasurements)} />}
  </section>;
}

function QualityEvidencePanel({ evidence, onEvidence }: { readonly evidence: readonly QualityEvidenceView[]; readonly onEvidence: (evidence: GeneratedJsonObject) => void }): JSX.Element | null {
  if (evidence.length === 0) return null;
  return <section aria-label="Quality evidence by category" className="panel quality-evidence-panel">
    <h2>Quality evidence</h2>
    <ul>{evidence.map(({ category, reference }) => <li data-evidence-category={category} key={reference.id}>
      <span className="quality-evidence-panel__category">{category}</span>
      <EvidenceLink evidence={reference} onSelect={onEvidence} />
    </li>)}</ul>
  </section>;
}

function ReturnedActionList({
  actions,
  disabledActionIds = new Set<string>(),
  pendingActionReferenceIds,
  stale,
  onAction,
  ariaLabel,
}: {
  readonly actions: readonly ApprovalGateProjectionView["actions"][number][];
  readonly disabledActionIds?: ReadonlySet<string>;
  readonly pendingActionReferenceIds: readonly string[];
  readonly stale: boolean;
  readonly onAction: (action: GeneratedActionReference) => void;
  readonly ariaLabel: string;
}): JSX.Element | null {
  if (actions.length === 0) return null;
  return <div aria-label={ariaLabel} className="responsive-action-group approval-rollout-screen__actions" role="group">
    {actions.map((action) => <ActionControl
      action={action}
      disabledByOwner={disabledActionIds.has(action.id)}
      key={action.id}
      onInvoke={onAction}
      pending={pendingActionReferenceIds.includes(action.id)}
      stale={stale}
    />)}
  </div>;
}

function ReturnedValues({ label, values }: { readonly label: string; readonly values: readonly GeneratedJsonValue[] }): JSX.Element {
  return <div><h3>{label}</h3><ul>{values.map((value, index) => <li key={`${label}-${index}`}>{returnedValueText(value)}</li>)}</ul></div>;
}

function ReturnedField({ label, value }: { readonly label: string; readonly value: string }): JSX.Element {
  return <dl><div><dt>{label}</dt><dd>{value}</dd></div></dl>;
}

function withoutRecoveryActions<TAction extends { readonly kind?: string }>(actions: readonly TAction[]): readonly TAction[] {
  return actions.filter((action) => action.kind !== "refresh" && action.kind !== "reconnect");
}

function mapQualityEvidenceForRollout(projection: GeneratedJsonObject): readonly QualityEvidenceView[] {
  return mapApprovalGateProjection(projection).qualityEvidence;
}

function returnedValueText(value: GeneratedJsonValue): string {
  if (typeof value === "string") return value;
  if (typeof value === "number" || typeof value === "boolean") return String(value);
  return JSON.stringify(value);
}
