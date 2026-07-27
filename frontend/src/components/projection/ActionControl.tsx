"use client";

/**
 * @duty ActionControl — eligible server action button
 * @role Invoke only a mapped, server-returned action reference when eligible.
 * @controls One button with data-action-reference-id; disabled when ineligible/stale/pending.
 * @must Disable freshness-critical/irreversible actions while projection is stale.
 * @mustnot Invent action IDs or bypass eligibility.
 * @redesign docs/frontend_redesign/component_duty_catalog.md §3.3; Req 8.2
 */
import React from "react";

import type { GeneratedActionReference } from "../../lib/api/client";
import type { ActionReferenceView } from "../../lib/projections/ProjectionMapper";

export interface ActionControlProps {
  readonly action: ActionReferenceView;
  readonly stale: boolean;
  readonly pending?: boolean;
  readonly disabledByOwner?: boolean;
  readonly onInvoke: (reference: GeneratedActionReference) => void;
}

export function isActionControlDisabled(action: ActionReferenceView, stale: boolean, pending = false, disabledByOwner = false): boolean {
  const staleBlocked = stale
    && action.kind !== "refresh"
    && action.kind !== "reconnect"
    && (action.freshnessCritical === true || action.irreversible === true);
  return !action.eligible || pending || disabledByOwner || staleBlocked;
}

/** Renders and invokes only a mapped, server-returned action reference. */
export function ActionControl({ action, stale, pending, disabledByOwner, onInvoke }: ActionControlProps): JSX.Element {
  const disabled = isActionControlDisabled(action, stale, pending, disabledByOwner);
  return <button className="action-control" data-action-reference-id={action.id} disabled={disabled} onClick={(): void => {
    if (!disabled) onInvoke(action.source);
  }} type="button">{action.label}</button>;
}
