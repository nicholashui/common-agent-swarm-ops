import React from "react";

import type { GeneratedActionReference, GeneratedJsonObject, GeneratedJsonValue } from "../../lib/api/client";

/** A JSON-shaped value that can be rendered without interpreting it as markup. */
export type SafeContentValue = GeneratedJsonValue;

export interface SafeContentProps {
  readonly content: SafeContentValue;
  readonly as?: "span" | "pre";
}

/**
 * Renders untrusted content only as React text. It deliberately has no HTML,
 * URL, event, or media-loading escape hatch.
 */
export function SafeContent({ content, as = "span" }: SafeContentProps): JSX.Element {
  const text = inertText(content);
  return as === "pre"
    ? <pre data-safe-content="true">{text}</pre>
    : <span data-safe-content="true">{text}</span>;
}

export function inertText(content: SafeContentValue): string {
  if (typeof content === "string") return content;
  try {
    return JSON.stringify(content) ?? "";
  } catch {
    // A generated JSON value is serializable; retain a safe fallback for malformed runtime input.
    return "";
  }
}

export interface AllowedActionContract {
  readonly id: string;
  readonly label: string;
  readonly destination: string;
  readonly openInNewContext: boolean;
  readonly source: GeneratedActionReference;
}

/** Maps only a returned, explicitly allowed external-navigation contract. */
export function mapAllowedActionContract(reference: GeneratedActionReference): AllowedActionContract | null {
  const kind = stringField(reference, "kind");
  const id = stringField(reference, "id");
  const label = stringField(reference, "label");
  const destination = stringField(reference, "destination");
  const allowed = reference.allowed;
  const openInNewContext = reference.open_in_new_context;
  if (
    kind !== "external_navigation"
    || allowed !== true
    || id === null
    || label === null
    || destination === null
    || !isSafeExternalDestination(destination)
    || typeof openInNewContext !== "boolean"
  ) return null;
  return Object.freeze({ id, label, destination, openInNewContext, source: reference });
}

export interface ExternalNavigationControlProps {
  readonly action: AllowedActionContract | null;
}

/**
 * Provides an external link only from a returned Allowed_Action_Contract.
 * It never consumes arbitrary or untrusted content as a navigation target.
 */
export function ExternalNavigationControl({ action }: ExternalNavigationControlProps): JSX.Element {
  const verifiedAction = action === null ? null : mapAllowedActionContract(action.source);
  if (verifiedAction === null) return <button disabled type="button">External navigation unavailable</button>;
  return <a
    data-allowed-action-id={verifiedAction.id}
    href={verifiedAction.destination}
    {...(verifiedAction.openInNewContext ? { target: "_blank", rel: "noopener noreferrer" } : {})}
  >{verifiedAction.label}</a>;
}

function isSafeExternalDestination(destination: string): boolean {
  try {
    return new URL(destination).protocol === "https:";
  } catch {
    return false;
  }
}

function stringField(record: GeneratedJsonObject, field: string): string | null {
  const value = record[field];
  return typeof value === "string" && value.length > 0 ? value : null;
}
