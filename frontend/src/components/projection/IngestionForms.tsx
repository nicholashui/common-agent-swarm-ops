"use client";

/**
 * @duty IngestionForms — safe artifact/knowledge ingress UI
 * @role Collect untrusted content/import reference; submit only via authorized generated contract.
 * @controls Content field, optional URL field, submit; disabled without contract.
 * @must Mark client checks non-authoritative; show async ingest states from projection.
 * @mustnot Browser-fetch untrusted URLs; treat client validation as security.
 * @redesign docs/frontend_redesign/component_duty_catalog.md §3.3; Req 8.5; ui_10_knowledge.md
 */
import React from "react";

import type { GeneratedJsonObject, GeneratedJsonValue, GeneratedOperationId } from "../../lib/api/client";
import { ProjectionMapper, type OpaqueReferenceView } from "../../lib/projections/ProjectionMapper";
import { ReferenceLink } from "./ReferenceLink";
import { SafeContent } from "./SafeContent";

export type IngestionKind = "artifact" | "knowledge";
export type ImportState = "validating" | "quarantined" | "processing" | "indexed" | "rejected" | "archived";

export interface IngestionRequirements {
  readonly fileTypes?: readonly string[];
  readonly maximumSizeBytes?: number;
  readonly ownershipRequirement?: string;
  readonly retentionRequirement?: string;
}

export interface UntrustedContent {
  readonly value: string;
}

export interface IngestionIntent {
  readonly kind: IngestionKind;
  readonly content: UntrustedContent;
  readonly externalImportUrl?: UntrustedContent;
}

/**
 * This adapter is supplied by the generated API integration once an authorized
 * ingestion operation exists. The current generated client exposes no such
 * operation, so forms remain safely unavailable by default.
 */
export interface GeneratedAuthorizedIngestionContract {
  readonly operationId: GeneratedOperationId;
  readonly submit: (intent: IngestionIntent) => Promise<void>;
}

export interface CorrectableInputIssue {
  readonly message: string;
  readonly authority: "non-authoritative";
}

export function correctableIngestionIssue(content: string, externalImportUrl: string): CorrectableInputIssue | null {
  if (content.trim().length === 0 && externalImportUrl.trim().length === 0) {
    return { message: "Enter content or an import reference before submitting.", authority: "non-authoritative" };
  }
  if (externalImportUrl.trim().length > 0 && !isHttpUrl(externalImportUrl)) {
    return { message: "Check the external import URL format before submitting.", authority: "non-authoritative" };
  }
  return null;
}

export async function submitAuthorizedIngestion(
  contract: GeneratedAuthorizedIngestionContract | undefined,
  intent: IngestionIntent,
): Promise<boolean> {
  if (contract === undefined) return false;
  await contract.submit(intent);
  return true;
}

export interface IngestionRequirementSummaryProps {
  readonly requirements: IngestionRequirements;
}

/** Renders only the generated ingestion requirements supplied by the server. */
export function IngestionRequirementSummary({ requirements }: IngestionRequirementSummaryProps): JSX.Element {
  return <dl aria-label="Returned ingestion requirements" data-ingestion-requirements="true">
    {requirements.fileTypes === undefined ? null : <div><dt>File types</dt><dd>{requirements.fileTypes.join(", ")}</dd></div>}
    {requirements.maximumSizeBytes === undefined ? null : <div><dt>Maximum size</dt><dd>{requirements.maximumSizeBytes} bytes</dd></div>}
    {requirements.ownershipRequirement === undefined ? null : <div><dt>Ownership</dt><dd>{requirements.ownershipRequirement}</dd></div>}
    {requirements.retentionRequirement === undefined ? null : <div><dt>Retention</dt><dd>{requirements.retentionRequirement}</dd></div>}
  </dl>;
}

export interface IngestionFormProps {
  readonly kind: IngestionKind;
  readonly requirements: IngestionRequirements;
  readonly contract?: GeneratedAuthorizedIngestionContract;
  readonly onSubmitted?: () => void;
}

/**
 * A content/reference ingress form with no browser-side import request or URL
 * preview. Submission is impossible until a generated authorized contract is
 * provided.
 */
export function IngestionForm({ kind, requirements, contract, onSubmitted }: IngestionFormProps): JSX.Element {
  const [content, setContent] = React.useState("");
  const [externalImportUrl, setExternalImportUrl] = React.useState("");
  const [feedback, setFeedback] = React.useState<CorrectableInputIssue | null>(null);
  const unavailable = contract === undefined;

  const submit = async (event: React.FormEvent<HTMLFormElement>): Promise<void> => {
    event.preventDefault();
    const issue = correctableIngestionIssue(content, externalImportUrl);
    setFeedback(issue);
    if (issue !== null || unavailable) return;
    const submitted = await submitAuthorizedIngestion(contract, {
      kind,
      content: { value: content },
      ...(externalImportUrl.trim().length === 0 ? {} : { externalImportUrl: { value: externalImportUrl } }),
    });
    if (submitted) onSubmitted?.();
  };

  return <form aria-label={`${kind} ingestion`} onSubmit={submit}>
    <IngestionRequirementSummary requirements={requirements} />
    <label htmlFor={`${kind}-content`}>Content</label>
    <textarea id={`${kind}-content`} onChange={(event): void => { setContent(event.currentTarget.value); }} value={content} />
    <label htmlFor={`${kind}-external-import-url`}>External import URL</label>
    <input id={`${kind}-external-import-url`} inputMode="url" onChange={(event): void => { setExternalImportUrl(event.currentTarget.value); }} type="text" value={externalImportUrl} />
    {feedback === null ? null : <p data-feedback-authority={feedback.authority} role="status">{feedback.message}</p>}
    {unavailable ? <p role="status">Authorized ingestion is unavailable. Submission is blocked.</p> : null}
    <button disabled={unavailable} type="submit">Submit {kind}</button>
  </form>;
}

export interface ImportProjectionView {
  readonly state: ImportState;
  readonly references: readonly OpaqueReferenceView[];
  readonly scanResult?: string;
  readonly indexingResult?: string;
}

/** Maps only the generated import state, opaque references, and redacted outcomes. */
export function mapImportProjection(projection: GeneratedJsonObject): ImportProjectionView | undefined {
  const state = projection.state;
  if (!isImportState(state)) return undefined;
  const references = objectList(firstPresent(projection, ["opaque_references", "references", "redacted_references"])).flatMap((reference): readonly OpaqueReferenceView[] => {
    const mapped = new ProjectionMapper().mapOpaqueReference(reference);
    return mapped === null ? [] : [mapped];
  });
  const scanResult = stringField(projection, ["scan_result", "redacted_scan_result"]);
  const indexingResult = stringField(projection, ["indexing_result", "redacted_indexing_result"]);
  return {
    state,
    references,
    ...(scanResult === undefined ? {} : { scanResult }),
    ...(indexingResult === undefined ? {} : { indexingResult }),
  };
}

/** Maps returned form requirements without supplying defaults for omitted fields. */
export function mapIngestionRequirements(projection: GeneratedJsonObject): IngestionRequirements {
  const fileTypes = stringList(firstPresent(projection, ["file_types", "fileTypes"]));
  const maximumSizeBytes = numberField(projection, ["maximum_size_bytes", "maximumSizeBytes"]);
  const ownershipRequirement = stringField(projection, ["ownership_requirement", "ownershipRequirement"]);
  const retentionRequirement = stringField(projection, ["retention_requirement", "retentionRequirement"]);
  return {
    ...(fileTypes === undefined ? {} : { fileTypes }),
    ...(maximumSizeBytes === undefined ? {} : { maximumSizeBytes }),
    ...(ownershipRequirement === undefined ? {} : { ownershipRequirement }),
    ...(retentionRequirement === undefined ? {} : { retentionRequirement }),
  };
}

export interface ImportProjectionProps {
  readonly projection: ImportProjectionView;
  readonly onResolveReference: (reference: OpaqueReferenceView["source"]) => void;
}

/** Renders exact returned import state, opaque references, and redacted outcomes. */
export function ImportProjection({ projection, onResolveReference }: ImportProjectionProps): JSX.Element {
  return <section aria-label="Returned import projection" data-import-state={projection.state}>
    <h2>Import projection</h2>
    <p>Import state: {projection.state}</p>
    {projection.references.length === 0 ? null : <ul aria-label="Returned opaque references">{projection.references.map((reference): JSX.Element => <li key={reference.id}><ReferenceLink onResolve={onResolveReference} reference={reference} /></li>)}</ul>}
    {projection.scanResult === undefined ? null : <p>Scan result: <SafeContent content={projection.scanResult} /></p>}
    {projection.indexingResult === undefined ? null : <p>Indexing result: <SafeContent content={projection.indexingResult} /></p>}
  </section>;
}

function objectList(value: GeneratedJsonValue | undefined): readonly GeneratedJsonObject[] {
  return Array.isArray(value) ? value.flatMap((item): readonly GeneratedJsonObject[] => {
    if (typeof item !== "object" || item === null || Array.isArray(item)) return [];
    return [item as GeneratedJsonObject];
  }) : [];
}

function firstPresent(source: GeneratedJsonObject, fields: readonly string[]): GeneratedJsonValue | undefined {
  for (const field of fields) if (Object.hasOwn(source, field) && source[field] !== undefined) return source[field];
  return undefined;
}

function stringField(source: GeneratedJsonObject, fields: readonly string[]): string | undefined {
  for (const field of fields) if (typeof source[field] === "string" && source[field].length > 0) return source[field] as string;
  return undefined;
}

function stringList(value: GeneratedJsonValue | undefined): readonly string[] | undefined {
  if (!Array.isArray(value)) return undefined;
  const values = value.filter((item): item is string => typeof item === "string" && item.length > 0);
  return values.length === 0 ? undefined : values;
}

function numberField(source: GeneratedJsonObject, fields: readonly string[]): number | undefined {
  for (const field of fields) if (typeof source[field] === "number" && Number.isFinite(source[field])) return source[field] as number;
  return undefined;
}

function isImportState(value: GeneratedJsonValue | undefined): value is ImportState {
  return typeof value === "string" && ["validating", "quarantined", "processing", "indexed", "rejected", "archived"].includes(value);
}

function isHttpUrl(value: string): boolean {
  try {
    const url = new URL(value);
    return url.protocol === "https:" || url.protocol === "http:";
  } catch {
    return false;
  }
}
