"use client";

/**
 * @duty ReferenceLink — opaque resource reference button
 * @role Expose only server-returned opaque references for host resolve handlers.
 * @controls One button with data-opaque-reference-id.
 * @must Call onResolve with projection source only; never construct URLs/IDs client-side.
 * @mustnot Navigate to untrusted destinations from opaque ids alone.
 * @redesign docs/frontend_redesign/component_duty_catalog.md §3.3
 */
import React from "react";

import type { GeneratedOpaqueReference, OpaqueReferenceView } from "../../lib/projections/ProjectionMapper";

export interface ReferenceLinkProps {
  readonly reference: OpaqueReferenceView;
  /** Must resolve the returned reference through a generated Public API read operation. */
  readonly onResolve: (reference: GeneratedOpaqueReference) => void;
}

/** Never constructs a URL or identifier; selection exposes only the returned opaque reference. */
export function ReferenceLink({ reference, onResolve }: ReferenceLinkProps): JSX.Element {
  return <button data-opaque-reference-id={reference.id} onClick={(): void => onResolve(reference.source)} type="button">
    {reference.label}
  </button>;
}
