"use client";

/**
 * @duty ProjectionStatus — freshness / recovery strip
 * @role Show live/stale/degraded/unavailable labels; expose only refresh/reconnect actions.
 * @controls ActionControl for recovery actions; ReferenceLink for alert targets.
 * @must Filter actions via isProjectionRecoveryAction; show as_of/freshness text.
 * @mustnot Claim live state when stale; invent recovery without action refs.
 * @redesign docs/frontend_redesign/component_duty_catalog.md §3.3; Req 8.3–8.4
 */
import React from "react";

import type { GeneratedActionReference } from "../../lib/api/client";
import type { ActionReferenceView, OpaqueReferenceView } from "../../lib/projections/ProjectionMapper";
import { ActionControl } from "./ActionControl";
import { ReferenceLink } from "./ReferenceLink";

export interface ProjectionStatusData {
  readonly stateLabel: string;
  readonly asOf?: string;
  readonly freshness?: string;
  readonly degradedState?: string | boolean;
}

export interface ProjectionAlert {
  readonly summary: string;
  readonly affectedReference: OpaqueReferenceView;
}

export interface UnavailableProjectionStatus {
  readonly message: string;
}

export interface ProjectionStatusProps {
  readonly projection: ProjectionStatusData;
  readonly stale: boolean;
  readonly actions: readonly ActionReferenceView[];
  readonly alerts?: readonly ProjectionAlert[];
  readonly unavailable?: UnavailableProjectionStatus;
  readonly onInvokeAction: (reference: GeneratedActionReference) => void;
  readonly onResolveAlert: (reference: OpaqueReferenceView["source"]) => void;
}

/** Returns only server-returned recovery actions that this status region may expose. */
export function isProjectionRecoveryAction(action: ActionReferenceView): boolean {
  return action.kind === "refresh" || action.kind === "reconnect";
}

function displayStateLabel(projection: ProjectionStatusData, stale: boolean): string {
  return stale ? "Stale" : projection.stateLabel;
}

function StatusActions({ actions, stale, onInvokeAction }: Pick<ProjectionStatusProps, "actions" | "stale" | "onInvokeAction">): JSX.Element | null {
  const recoveryActions = actions.filter(isProjectionRecoveryAction);
  if (recoveryActions.length === 0) return null;
  return <div className="responsive-action-group projection-status__actions">
    {recoveryActions.map((action) => <ActionControl action={action} key={action.id} onInvoke={onInvokeAction} stale={stale} />)}
  </div>;
}

/** Renders exact server freshness data and never fabricates a status or recovery control. */
export function ProjectionStatus({ projection, stale, actions, alerts = [], unavailable, onInvokeAction, onResolveAlert }: ProjectionStatusProps): JSX.Element {
  if (unavailable !== undefined) {
    return <section aria-label="Operational status unavailable" className="projection-status projection-status--unavailable" role="status">
      <p>{unavailable.message}</p>
      <StatusActions actions={actions} onInvokeAction={onInvokeAction} stale={stale} />
    </section>;
  }

  const stateLabel = displayStateLabel(projection, stale);
  return <section className="projection-status">
    <div className="projection-status__state">
      <span aria-label={`Status: ${stateLabel}`} role="img">●</span>
      <span>{stateLabel}</span>
    </div>
    <dl className="projection-status__freshness">
      {projection.asOf === undefined ? null : <div><dt>As of</dt><dd><time dateTime={projection.asOf}>{projection.asOf}</time></dd></div>}
      {projection.freshness === undefined ? null : <div><dt>Freshness</dt><dd>{projection.freshness}</dd></div>}
      {projection.degradedState === undefined ? null : <div><dt>Degraded state</dt><dd>{String(projection.degradedState)}</dd></div>}
    </dl>
    {alerts.length === 0 ? null : <ul className="projection-status__alerts">
      {alerts.map((alert) => <li key={alert.affectedReference.id}>
        <p>{alert.summary}</p>
        <ReferenceLink onResolve={onResolveAlert} reference={alert.affectedReference} />
      </li>)}
    </ul>}
    <StatusActions actions={actions} onInvokeAction={onInvokeAction} stale={stale} />
  </section>;
}
