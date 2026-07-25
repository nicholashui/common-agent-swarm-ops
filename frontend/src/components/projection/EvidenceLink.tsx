"use client";

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
