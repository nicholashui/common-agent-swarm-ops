"use client";

/**
 * @duty KnowledgeArtifactScreens — knowledge & artifact projection host
 * @role Compose knowledge/artifact/VA projections with SafeContent and IngestionForm.
 * @controls Delegated: ingestion fields, ActionControl, evidence/reference links.
 * @must Keep untrusted content inert; ingest only via authorized contract when present.
 * @mustnot Client-fetch import URLs or render privileged raw payloads.
 * @redesign docs/frontend_redesign/component_duty_catalog.md §3.4; ui_10_knowledge.md
 */
import React from "react";

import type { GeneratedActionReference, GeneratedJsonObject, GeneratedJsonValue } from "../lib/api/client";
import type { OperationalScreenKind } from "../lib/projections/screen-renderers";
import { mapGraphProjection } from "../lib/projections/graph-adapters";
import {
  mapArtifactProjection,
  mapVaProjection,
  type ArtifactProjectionView,
  type ReturnedFieldView,
  type ReturnedReferenceView,
  type VaAgentProjectionView,
  type VaApprovalGateView,
  type VaCritiqueProjectionView,
  type VaProjectionView,
  type VaQualityEvidenceView,
  type VaTaskProjectionView,
} from "../lib/projections/va-adapters";
import {
  ImportProjection,
  IngestionForm,
  mapImportProjection,
  mapIngestionRequirements,
  type GeneratedAuthorizedIngestionContract,
  type ImportProjectionView,
  type IngestionKind,
  type IngestionRequirements,
} from "./projection/IngestionForms";
import { ActionControl } from "./projection/ActionControl";
import { EvidenceLink } from "./projection/EvidenceLink";
import { ReferenceLink } from "./projection/ReferenceLink";
import { SafeContent } from "./projection/SafeContent";
import { OperationalScreen } from "./OperationalScreens";

export interface KnowledgeArtifactScreenProps {
  readonly kind: IngestionKind;
  readonly requirements?: IngestionRequirements;
  readonly ingestionRequirementsProjection?: GeneratedJsonObject;
  readonly importProjection?: GeneratedJsonObject;
  readonly artifactProjection?: GeneratedJsonObject;
  readonly contract?: GeneratedAuthorizedIngestionContract;
  readonly onResolveReference: (reference: GeneratedJsonObject) => void;
  readonly onSubmitted?: () => void;
}

/** Composes returned requirements, inert ingress, import state, and artifact data. */
export function KnowledgeArtifactScreen({
  kind,
  requirements,
  ingestionRequirementsProjection,
  importProjection,
  artifactProjection,
  contract,
  onResolveReference,
  onSubmitted,
}: KnowledgeArtifactScreenProps): JSX.Element {
  const returnedRequirements = requirements ?? (ingestionRequirementsProjection === undefined ? undefined : mapIngestionRequirements(ingestionRequirementsProjection));
  const returnedImport = importProjection === undefined ? undefined : mapImportProjection(importProjection);

  return <section aria-label="Knowledge and artifact projection" className="knowledge-artifact-screen">
    {returnedRequirements === undefined ? null : <IngestionForm
      contract={contract}
      kind={kind}
      onSubmitted={onSubmitted}
      requirements={returnedRequirements}
    />}
    {artifactProjection === undefined ? null : <ArtifactProjectionRenderer onResolveReference={onResolveReference} projection={artifactProjection} />}
    {returnedImport === undefined ? null : <ImportProjection onResolveReference={onResolveReference} projection={returnedImport} />}
  </section>;
}

export interface ArtifactProjectionRendererProps {
  readonly projection: GeneratedJsonObject;
  readonly onResolveReference?: (reference: GeneratedJsonObject) => void;
}

/** Displays returned artifact fields and a derived fail-closed delivery block only. */
export function ArtifactProjectionRenderer({ projection, onResolveReference }: ArtifactProjectionRendererProps): JSX.Element {
  return <ArtifactProjectionViewRenderer onResolveReference={onResolveReference} projection={mapArtifactProjection(projection)} />;
}

export interface VaProjectionScreenProps {
  readonly projection: GeneratedJsonObject;
  readonly genericKind?: OperationalScreenKind;
  readonly onAction?: (action: GeneratedActionReference) => void;
  readonly onEvidence?: (evidence: GeneratedJsonObject) => void;
  readonly onReference?: (reference: GeneratedJsonObject) => void;
  readonly onFilterChange?: (filter: GeneratedJsonObject, option: GeneratedJsonObject) => void;
}

/** Renders VA data conditionally; absent VA data uses the common returned projection. */
export function VaProjectionScreen({
  projection,
  genericKind = "activity",
  onAction,
  onEvidence,
  onReference,
  onFilterChange,
}: VaProjectionScreenProps): JSX.Element {
  const vaProjection = mapVaProjection(projection);
  if (vaProjection === undefined) {
    return <GenericProjectionFallback
      kind={genericKind}
      onAction={onAction}
      onEvidence={onEvidence}
      onFilterChange={onFilterChange}
      onReference={onReference}
      projection={projection}
    />;
  }
  return <VaProjectionViewRenderer
    onAction={onAction}
    onEvidence={onEvidence}
    onReference={onReference}
    projection={vaProjection}
  />;
}

/** Alias for callers that use the domain-adapter terminology. */
export const ConditionalVaRenderer = VaProjectionScreen;
export const VAProjectionRenderer = VaProjectionScreen;

function ArtifactProjectionViewRenderer({ projection, onResolveReference }: { readonly projection: ArtifactProjectionView; readonly onResolveReference?: (reference: GeneratedJsonObject) => void }): JSX.Element {
  return <section aria-label="Returned artifact projection" className="panel artifact-projection">
    <h2>Artifact</h2>
    <ReturnedFields fields={artifactFields(projection)} />
    {projection.parentLineage.length === 0 ? null : <ReturnedReferences label="Parent lineage" references={projection.parentLineage} onResolveReference={onResolveReference} />}
    {projection.technicalSpecification.length === 0 ? null : <ReturnedFields heading="Technical specification" fields={projection.technicalSpecification} />}
    {projection.deliveryBlocked ? <p aria-live="polite" data-delivery-blocked="true" role="status">Delivery blocked</p> : null}
    {projection.deliveryBlockReasons.length === 0 ? null : <ul aria-label="Delivery block reasons" data-delivery-block-reasons="true">
      {projection.deliveryBlockReasons.map((reason) => <li key={reason}>{reason === "missing_delivery_field" ? "Required delivery data is unavailable." : "Required gate approval is unavailable."}</li>)}
    </ul>}
  </section>;
}

function VaProjectionViewRenderer({
  projection,
  onAction,
  onEvidence,
  onReference,
}: {
  readonly projection: VaProjectionView;
  readonly onAction?: (action: GeneratedActionReference) => void;
  readonly onEvidence?: (evidence: GeneratedJsonObject) => void;
  readonly onReference?: (reference: GeneratedJsonObject) => void;
}): JSX.Element {
  const metadataFields = vaMetadataFields(projection);
  return <section aria-label="VA projection" className="va-projection-screen">
    <header className="page-header">
      <p className="eyebrow">VA DOMAIN ADAPTER</p>
      <h1>Returned production projection</h1>
    </header>
    {metadataFields.length === 0 && projection.commonPatternVersion === undefined ? null : <section aria-label="Returned VA template and phase" className="panel">
      <h2>Production metadata</h2>
      <ReturnedFields fields={metadataFields} />
      {projection.commonPatternVersion === undefined ? null : <ReturnedReferences label="Common pattern version" references={[projection.commonPatternVersion]} onResolveReference={onReference} />}
    </section>}
    {projection.agents.map((agent, index) => <AgentProjection key={agent.publishedVersion ?? agent.identity ?? `agent-${index}`} projection={agent} />)}
    {projection.tasks.map((task, index) => <TaskProjection key={task.taskId ?? `task-${index}`} projection={task} />)}
    {projection.artifacts.map((artifact, index) => <ArtifactProjectionViewRenderer key={artifact.artifactVersion ?? `artifact-${index}`} onResolveReference={onReference} projection={artifact} />)}
    {projection.critiques.map((critique, index) => <CritiqueProjection key={critique.timestamp ?? `critique-${index}`} onEvidence={onEvidence} projection={critique} />)}
    {projection.qualityEvidence.length === 0 ? null : <QualityEvidenceSection evidence={projection.qualityEvidence} onEvidence={onEvidence} />}
    {projection.approvalGates.map((gate, index) => <ApprovalGateProjection key={gate.evidenceRevision ?? `approval-${index}`} gate={gate} onAction={onAction} onEvidence={onEvidence} onReference={onReference} />)}
    {projection.provenance.length === 0 ? null : <section aria-label="Returned provenance" className="panel"><h2>Provenance</h2><ReturnedFields fields={projection.provenance} /></section>}
    {projection.actions.length === 0 ? null : <section aria-label="Returned VA actions" className="responsive-action-group">{projection.actions.map((action) => <ActionControl
      action={action}
      disabledByOwner={onAction === undefined}
      key={action.id}
      onInvoke={(reference): void => onAction?.(reference)}
      stale={false}
    />)}</section>}
  </section>;
}

function AgentProjection({ projection }: { readonly projection: VaAgentProjectionView }): JSX.Element {
  return <section aria-label="Returned common agent contract" className="panel">
    <h2>Common agent contract</h2>
    <ReturnedFields fields={[
      ...(projection.identity === undefined ? [] : [{ key: "identity", label: "Identity", value: projection.identity }]),
      ...(projection.scope === undefined ? [] : [{ key: "scope", label: "Scope", value: projection.scope }]),
      ...(projection.publishedVersion === undefined ? [] : [{ key: "published_version", label: "Published version", value: projection.publishedVersion }]),
    ]} />
    <ReturnedStrings heading="Capabilities" values={projection.capabilities} />
    <ReturnedStrings heading="Policies" values={projection.policies} />
    <ReturnedFields heading="Runtime constraints" fields={projection.runtimeConstraints} />
    <ReturnedFields heading="Quality contract" fields={projection.qualityContract} />
    <ReturnedStrings heading="Critique relationships" values={projection.critiqueRelationships} />
    <ReturnedStrings heading="Provenance obligations" values={projection.provenanceObligations} />
  </section>;
}

function TaskProjection({ projection }: { readonly projection: VaTaskProjectionView }): JSX.Element {
  return <section aria-label="Returned task projection" className="panel">
    <h2>Task</h2>
    <ReturnedFields fields={[
      ...(projection.taskId === undefined ? [] : [{ key: "task_id", label: "Task", value: projection.taskId }]),
      ...(projection.graphRevision === undefined ? [] : [{ key: "graph_revision", label: "Graph revision", value: projection.graphRevision }]),
      ...(projection.lifecycle === undefined ? [] : [{ key: "lifecycle", label: "Lifecycle", value: projection.lifecycle }]),
      ...(projection.recoveryState === undefined ? [] : [{ key: "recovery_state", label: "Recovery state", value: projection.recoveryState }]),
      ...(projection.checkpoint === undefined ? [] : [{ key: "checkpoint", label: "Checkpoint", value: projection.checkpoint }]),
    ]} />
    <ReturnedStrings heading="Dependencies" values={projection.dependencies} />
    <ReturnedStrings heading="Gates" values={projection.gates} />
    <ReturnedFields heading="Budget" fields={projection.budget} />
    <ReturnedReferences label="Common-version provenance" references={projection.commonVersionProvenance} />
    <ReturnedFields fields={projection.details} />
  </section>;
}

function CritiqueProjection({ projection, onEvidence }: { readonly projection: VaCritiqueProjectionView; readonly onEvidence?: (evidence: GeneratedJsonObject) => void }): JSX.Element {
  return <section aria-label="Returned critique projection" className="panel">
    <h2>Critique</h2>
    <ReturnedFields fields={[
      ...(projection.critiqueState === undefined ? [] : [{ key: "critique_state", label: "Critique state", value: projection.critiqueState }]),
      ...(projection.source === undefined ? [] : [{ key: "source", label: "Source", value: projection.source }]),
      ...(projection.target === undefined ? [] : [{ key: "target", label: "Target", value: projection.target }]),
      ...(projection.timestamp === undefined ? [] : [{ key: "timestamp", label: "Timestamp", value: projection.timestamp }]),
      ...(projection.message === undefined ? [] : [{ key: "message", label: "Message", value: projection.message }]),
    ]} />
    {projection.artifactReference === undefined ? null : <ReturnedReferences label="Artifact reference" references={[projection.artifactReference]} />}
    <ReturnedFields fields={projection.details} />
    {projection.evidence.length === 0 ? null : <ul aria-label="Critique evidence">{projection.evidence.map((evidence) => <li key={evidence.id}><EvidenceLink evidence={evidence} onSelect={onEvidence} /></li>)}</ul>}
  </section>;
}

function QualityEvidenceSection({ evidence, onEvidence }: { readonly evidence: readonly VaQualityEvidenceView[]; readonly onEvidence?: (reference: GeneratedJsonObject) => void }): JSX.Element {
  return <section aria-label="Returned quality evidence" className="panel">
    <h2>Quality evidence</h2>
    <ul>{evidence.map((item, index) => <li data-evidence-category={item.category} key={`${item.category}-${index}`}>
      <strong>{item.category}</strong>
      {item.reference === undefined ? null : <EvidenceLink evidence={item.reference} onSelect={onEvidence} />}
      {item.referenceValue === undefined ? null : <SafeContent content={item.referenceValue} />}
      <ReturnedFields fields={item.details} />
    </li>)}</ul>
  </section>;
}

function ApprovalGateProjection({ gate, onAction, onEvidence, onReference }: { readonly gate: VaApprovalGateView; readonly onAction?: (action: GeneratedActionReference) => void; readonly onEvidence?: (evidence: GeneratedJsonObject) => void; readonly onReference?: (reference: GeneratedJsonObject) => void }): JSX.Element {
  return <section aria-label={gate.unavailable ? "Approval gate unavailable" : "Returned approval gate"} className="panel" data-approval-gate-unavailable={gate.unavailable ? "true" : "false"}>
    <h2>Approval gate</h2>
    {gate.unavailable ? <p aria-live="polite" role="status">Unavailable_State</p> : null}
    <ReturnedFields fields={[
      ...(gate.state === undefined ? [] : [{ key: "state", label: "Approval state", value: gate.state }]),
      ...(gate.pendingOperation === undefined ? [] : [{ key: "pending_operation", label: "Pending operation", value: gate.pendingOperation }]),
      ...(gate.evidenceRevision === undefined ? [] : [{ key: "evidence_revision", label: "Evidence revision", value: gate.evidenceRevision }]),
    ]} />
    <ReturnedStrings heading="Criteria" values={gate.criteria} />
    <ReturnedReferences label="Artifact references" references={gate.artifactReferences} onResolveReference={onReference} />
    {gate.qualityEvidence.length === 0 ? null : <QualityEvidenceSection evidence={gate.qualityEvidence} onEvidence={onEvidence} />}
    {gate.actions.length === 0 ? null : <div aria-label="Returned approval actions" className="responsive-action-group">{gate.actions.map((action) => <ActionControl
      action={action}
      disabledByOwner={onAction === undefined || gate.unavailable}
      key={action.id}
      onInvoke={(reference): void => onAction?.(reference)}
      stale={false}
    />)}</div>}
  </section>;
}

function GenericProjectionFallback({ projection, kind, onAction, onEvidence, onFilterChange, onReference }: VaProjectionScreenProps & { readonly kind: OperationalScreenKind }): JSX.Element {
  const source = objectValue(projection.generic_projection) ?? projection;
  const graphSource = objectValue(firstPresent(source, ["graph", "graph_projection"]));
  const graph = graphSource === undefined ? undefined : mapGraphProjection(graphSource);
  const commonFields = mapCommonProjectionFields(source);
  return <section aria-label="Common projection" className="generic-projection-fallback">
    <OperationalScreen
      kind={kind}
      onAction={onAction ?? noopAction}
      onEvidence={onEvidence ?? noopReference}
      onFilterChange={onFilterChange ?? noopFilter}
      onReference={onReference ?? noopReference}
      projection={source}
    />
    {commonFields.length === 0 ? null : <ReturnedFields heading="Returned common projection" fields={commonFields} />}
    {graph === undefined ? null : <section aria-label="Returned common graph" className="panel"><h2>Common graph</h2><dl>{graph.graphRevision === undefined ? null : <div><dt>Graph revision</dt><dd>{graph.graphRevision}</dd></div>}{graph.nodes.map((node) => <div key={node.id}><dt>{node.label}</dt><dd>{node.task?.lifecycle ?? node.provenanceReference ?? node.forkOrigin ?? node.customReason}</dd></div>)}</dl></section>}
  </section>;
}

function ReturnedFields({ heading, fields }: { readonly heading?: string; readonly fields: readonly ReturnedFieldView[] }): JSX.Element | null {
  if (fields.length === 0) return null;
  return <section aria-label={heading ?? "Returned fields"}>{heading === undefined ? null : <h3>{heading}</h3>}<dl>{fields.map((field) => <div key={field.key}><dt>{field.label}</dt><dd><SafeContent content={field.value} /></dd></div>)}</dl></section>;
}

function ReturnedStrings({ heading, values }: { readonly heading: string; readonly values: readonly string[] }): JSX.Element | null {
  if (values.length === 0) return null;
  return <section aria-label={heading}><h3>{heading}</h3><ul>{values.map((value) => <li key={value}><SafeContent content={value} /></li>)}</ul></section>;
}

function ReturnedReferences({ label, references, onResolveReference }: { readonly label: string; readonly references: readonly ReturnedReferenceView[]; readonly onResolveReference?: (reference: GeneratedJsonObject) => void }): JSX.Element | null {
  if (references.length === 0) return null;
  return <section aria-label={label}><h3>{label}</h3><ul>{references.map((reference, index) => <li key={typeof reference === "string" ? `${reference}-${index}` : reference.id}>
    {typeof reference === "string" ? <SafeContent content={reference} /> : <ReferenceLink onResolve={onResolveReference ?? noopReference} reference={reference} />}
  </li>)}</ul></section>;
}

function mapCommonProjectionFields(source: GeneratedJsonObject): readonly ReturnedFieldView[] {
  const groups: readonly (readonly [string, GeneratedJsonObject | undefined, readonly string[]])[] = [
    ["common", source, ["run_reference", "graph_revision", "governance_state", "governance_status", "provenance_reference", "state_label", "lifecycle", "recovery_state"]],
    ["graph", objectValue(firstPresent(source, ["graph", "graph_projection"])), ["graph_revision", "revision", "state_label"]],
    ["task", objectValue(firstPresent(source, ["task", "task_projection"])), ["lifecycle", "lifecycle_state", "status_detail", "recovery_state", "checkpoint_reference"]],
    ["governance", objectValue(firstPresent(source, ["governance", "governance_projection"])), ["state", "status", "approval_state"]],
    ["provenance", objectValue(firstPresent(source, ["pinned_provenance", "provenance"])), ["run_provenance_id", "graph_revision_id", "workflow_definition_version", "source_checkpoint_reference"]],
  ];
  const seen = new Set<string>();
  return groups.flatMap(([group, values, keys]): readonly ReturnedFieldView[] => {
    if (values === undefined) return [];
    return keys.flatMap((key): readonly ReturnedFieldView[] => {
      const value = values[key];
      if (seen.has(key) || (typeof value !== "string" && typeof value !== "number" && typeof value !== "boolean")) return [];
      seen.add(key);
      return [{ key: `${group}.${key}`, label: key.split("_").map((part): string => `${part[0]?.toUpperCase() ?? ""}${part.slice(1)}`).join(" "), value: String(value) }];
    });
  });
}

function vaMetadataFields(projection: VaProjectionView): readonly ReturnedFieldView[] {
  return [
    ...(projection.template === undefined ? [] : [{ key: "template", label: "Template", value: projection.template }]),
    ...(projection.productionPhase === undefined ? [] : [{ key: "production_phase", label: "Production phase", value: projection.productionPhase }]),
  ];
}

function artifactFields(projection: ArtifactProjectionView): readonly ReturnedFieldView[] {
  return [
    ...(projection.artifactVersion === undefined ? [] : [{ key: "artifact_version", label: "Artifact version", value: projection.artifactVersion }]),
    ...(projection.rightsAndConsent === undefined ? [] : [{ key: "rights_and_consent", label: "Rights and consent", value: projection.rightsAndConsent }]),
    ...(projection.continuity === undefined ? [] : [{ key: "continuity", label: "Continuity", value: projection.continuity }]),
    ...(projection.qualityControl === undefined ? [] : [{ key: "quality_control", label: "Quality control", value: projection.qualityControl }]),
    ...(projection.deliveryState === undefined ? [] : [{ key: "delivery_state", label: "Delivery state", value: projection.deliveryState }]),
    ...(projection.deliveryTargets.length === 0 ? [] : [{ key: "delivery_targets", label: "Delivery targets", value: projection.deliveryTargets.join(", ") }]),
    ...(projection.provenanceReference === undefined ? [] : [{ key: "provenance_reference", label: "Provenance reference", value: returnedReferenceText(projection.provenanceReference) }]),
    ...(projection.gateApproval === undefined ? [] : [{ key: "gate_approval", label: "Gate approval", value: projection.gateApproval }]),
  ];
}

function firstPresent(source: GeneratedJsonObject, fields: readonly string[]): GeneratedJsonObject[keyof GeneratedJsonObject] | undefined {
  for (const field of fields) if (Object.hasOwn(source, field)) return source[field];
  return undefined;
}

function objectValue(value: GeneratedJsonObject[keyof GeneratedJsonObject] | undefined): GeneratedJsonObject | undefined {
  return typeof value === "object" && value !== null && !Array.isArray(value) ? value as GeneratedJsonObject : undefined;
}

function returnedReferenceText(reference: ReturnedReferenceView): string {
  return typeof reference === "string" ? reference : reference.label;
}

function noopAction(_action: GeneratedActionReference): void { return undefined; }
function noopReference(_reference: GeneratedJsonObject): void { return undefined; }
function noopFilter(_filter: GeneratedJsonObject, _option: GeneratedJsonObject): void { return undefined; }
