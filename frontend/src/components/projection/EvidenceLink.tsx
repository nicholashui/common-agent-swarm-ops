"use client";

/**
 * @duty EvidenceLink — opaque evidence control
 * @role Present server-returned evidence identity; optional select invokes host handler.
 * @controls Span (read-only) or button when onSelect provided.
 * @must Use data-evidence-reference-id from projection only.
 * @mustnot Embed raw traces, credentials, or object-store paths.
 * @redesign docs/frontend_redesign/component_duty_catalog.md §3.3
 */
import React from "react";

import type { EvidenceReferenceView, GeneratedEvidenceReference } from "../../lib/projections/ProjectionMapper";

export interface EvidenceLinkProps {
  readonly evidence: EvidenceReferenceView;
  readonly onSelect?: (reference: GeneratedEvidenceReference) => void;
}

/** Presents only server-returned evidence identity and redacted presentation fields. */
export function EvidenceLink({ evidence, onSelect }: EvidenceLinkProps): JSX.Element {
  const summary = evidence.presentation.fields.summary;
  if (onSelect === undefined) return <span data-evidence-reference-id={evidence.id}>{evidence.label}{typeof summary === "string" ? `: ${summary}` : ""}</span>;
  return <button data-evidence-reference-id={evidence.id} onClick={(): void => onSelect(evidence.source)} type="button">
    {evidence.label}{typeof summary === "string" ? `: ${summary}` : ""}
  </button>;
}
