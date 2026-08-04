"use client";

/**
 * @duty OperationalScreens — legacy named screen exports
 * @role Map Dashboard/Registry/Activity/… names to projection-driven presentational screens.
 * @controls Delegated ActionControl, filters, evidence/reference via projection handlers.
 * @must Prefer *Home + BoundScreenHome for app routes; keep exports for tests/compat.
 * @mustnot Invent projections or actions outside generated screen views.
 * @redesign docs/frontend_redesign/component_duty_catalog.md §3.4
 */
import React from "react";

import type { GeneratedActionReference, GeneratedJsonObject } from "../lib/api/client";
import {
  mapGeneratedScreenProjection,
  type GeneratedScreenProjectionView,
  type OperationalScreenKind,
  type ScreenFieldView,
} from "../lib/projections/screen-renderers";
import { ActionControl } from "./projection/ActionControl";
import { EvidenceLink } from "./projection/EvidenceLink";
import { ProjectionStatus } from "./projection/ProjectionStatus";
import { GeneratedFilterBar } from "./GeneratedFilterBar";
import { InfoTooltip } from "./design";

export interface OperationalScreenProps {
  readonly projection: GeneratedJsonObject;
  readonly onFilterChange: (filter: GeneratedJsonObject, option: GeneratedJsonObject) => void;
  readonly onAction: (action: GeneratedActionReference) => void;
  readonly onEvidence: (evidence: GeneratedJsonObject) => void;
  readonly onReference: (reference: GeneratedJsonObject) => void;
}

interface ScreenPresentation {
  readonly eyebrow: string;
  readonly title: string;
  readonly regionLabel: string;
}

const SCREEN_PRESENTATIONS: Readonly<Record<OperationalScreenKind, ScreenPresentation>> = {
  dashboard: { eyebrow: "DASHBOARD", title: "Fleet health and common impact", regionLabel: "Dashboard projection" },
  registry: { eyebrow: "COMMON REGISTRY", title: "Versioned common components", regionLabel: "Registry projection" },
  componentDetail: { eyebrow: "COMMON COMPONENT", title: "Published component detail", regionLabel: "Common component projection" },
  activity: { eyebrow: "ACTIVITY", title: "Runs and task operations", regionLabel: "Activity projection" },
  monitoring: { eyebrow: "MONITORING", title: "Operational health and alerts", regionLabel: "Monitoring projection" },
  notifications: { eyebrow: "NOTIFICATIONS", title: "Returned operational notifications", regionLabel: "Notifications projection" },
  audit: { eyebrow: "AUDIT", title: "Authorized audit records", regionLabel: "Audit projection" },
  profile: { eyebrow: "PROFILE", title: "Authorized profile and preferences", regionLabel: "Profile projection" },
  evaluation: { eyebrow: "EVALUATION", title: "Quality and evaluation evidence", regionLabel: "Evaluation projection" },
};

export function Dashboard(props: OperationalScreenProps): JSX.Element {
  return <OperationalScreen kind="dashboard" {...props} />;
}

export function Registry(props: OperationalScreenProps): JSX.Element {
  return <OperationalScreen kind="registry" {...props} />;
}

export function CommonComponentDetail(props: OperationalScreenProps): JSX.Element {
  return <OperationalScreen kind="componentDetail" {...props} />;
}

export function Activity(props: OperationalScreenProps): JSX.Element {
  return <OperationalScreen kind="activity" {...props} />;
}

export function Monitoring(props: OperationalScreenProps): JSX.Element {
  return <OperationalScreen kind="monitoring" {...props} />;
}

export function Notifications(props: OperationalScreenProps): JSX.Element {
  return <OperationalScreen kind="notifications" {...props} />;
}

export function Audit(props: OperationalScreenProps): JSX.Element {
  return <OperationalScreen kind="audit" {...props} />;
}

export function Profile(props: OperationalScreenProps): JSX.Element {
  return <OperationalScreen kind="profile" {...props} />;
}

export function Evaluation(props: OperationalScreenProps): JSX.Element {
  return <OperationalScreen kind="evaluation" {...props} />;
}

export function OperationalScreen({
  projection,
  onAction,
  onEvidence,
  onFilterChange,
  onReference,
  kind,
}: OperationalScreenProps & { readonly kind: OperationalScreenKind }): JSX.Element {
  const view = mapGeneratedScreenProjection(kind, projection);
  const presentation = SCREEN_PRESENTATIONS[kind];
  const title = textField(view, "title");
  const description = textField(view, "description");
  const directFields = fieldsExcept(view, ["title", "description"]);

  return <section aria-label={presentation.regionLabel} className="operational-screen">
    <header className="page-header">
      <div>
        <p className="eyebrow">{presentation.eyebrow}</p>
        <div className="page-title-row">
          <h1>{presentation.title}</h1>
          {description === undefined ? null : (
            <InfoTooltip label="About this screen" text={description} />
          )}
        </div>
        {title === undefined ? null : <p className="operational-screen__projection-title">{title}</p>}
      </div>
    </header>
    <GeneratedFilterBar filters={view.filters} onFilterChange={onFilterChange} />
    {view.status === undefined ? null : <ProjectionStatus
      actions={view.actions}
      alerts={view.alerts}
      onInvokeAction={onAction}
      onResolveAlert={onReference}
      projection={view.status}
      stale={view.status.stale}
    />}
    <FieldList fields={directFields} />
    {view.actions.length === 0 ? null : <ActionList actions={view.actions} onAction={onAction} stale={view.status?.stale ?? false} />}
    {view.evidence.length === 0 ? null : <section aria-label="Returned evidence" className="panel operational-screen__evidence">
      <h2>Evidence</h2>
      <ul>{view.evidence.map((evidence) => <li key={evidence.id}><EvidenceLink evidence={evidence} onSelect={onEvidence} /></li>)}</ul>
    </section>}
    <div className="operational-screen__sections">{view.sections.map((section) => <section className="panel" key={section.heading}>
      <h2>{section.heading}</h2>
      <FieldList fields={section.fields} />
      <ActionList actions={section.actions} onAction={onAction} stale={view.status?.stale ?? false} />
      {section.evidence.length === 0 ? null : <ul className="operational-screen__evidence-list">{section.evidence.map((evidence) => <li key={evidence.id}><EvidenceLink evidence={evidence} onSelect={onEvidence} /></li>)}</ul>}
    </section>)}</div>
  </section>;
}

function FieldList({ fields }: { readonly fields: readonly ScreenFieldView[] }): JSX.Element | null {
  if (fields.length === 0) return null;
  return <section aria-label="Returned projection fields" className="panel operational-screen__fields">
    <dl>{fields.map((field) => <div key={field.key}><dt>{field.label}</dt><dd>{field.value}</dd></div>)}</dl>
  </section>;
}

function ActionList({
  actions,
  onAction,
  stale,
}: {
  readonly actions: GeneratedScreenProjectionView["actions"];
  readonly onAction: (action: GeneratedActionReference) => void;
  readonly stale: boolean;
}): JSX.Element | null {
  if (actions.length === 0) return null;
  return <div aria-label="Returned actions" className="responsive-action-group operational-screen__actions">
    {actions.map((action) => <ActionControl action={action} key={action.id} onInvoke={onAction} stale={stale} />)}
  </div>;
}

function textField(view: GeneratedScreenProjectionView, key: string): string | undefined {
  const value = view.fields.fields[key];
  return typeof value === "string" ? value : undefined;
}

function fieldsExcept(view: GeneratedScreenProjectionView, excluded: readonly string[]): readonly ScreenFieldView[] {
  return Object.entries(view.fields.fields).flatMap(([key, value]): readonly ScreenFieldView[] => {
    if (excluded.includes(key) || (typeof value !== "string" && typeof value !== "number" && typeof value !== "boolean")) return [];
    const labels: Readonly<Record<string, string>> = {
      health: "Health", fleet_state: "Fleet state", approval_alert: "Approval alert", backlog: "Backlog",
      common_version_impact: "Common-version impact", summary: "Summary", immutable_identifier: "Immutable identifier",
      version: "Version", status: "Status", provenance_reference: "Provenance reference", compatibility_state: "Compatibility",
      aggregate_metrics: "Aggregate metrics", published_contract: "Published contract", version_history: "Version history",
      evaluation_summary: "Evaluation summary", usage_summary: "Usage summary", graph_revision: "Pinned graph revision",
      common_versions: "Pinned common versions", lifecycle: "Lifecycle", dependency: "Dependency", checkpoint: "Checkpoint",
      retry: "Retry", failure: "Failure", recovery: "Recovery", correlation_identifier: "Correlation identifier",
      priority: "Priority", timestamp: "Timestamp", action_type: "Action type", target: "Target", identity: "Identity",
      impact_summary: "Impact summary", preferences: "Preferences", quality_l1: "L1 specification validation",
      quality_l2: "L2 role-rubric evaluation", quality_l3: "L3 baseline preference", gate_outcome: "Gate outcome",
    };
    const label = labels[key];
    return label === undefined ? [] : [{ key, label, value: String(value) }];
  });
}
