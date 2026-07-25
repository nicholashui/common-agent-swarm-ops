import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

import React from "react";
import { renderToStaticMarkup } from "react-dom/server";

import {
  AccessibleDialog,
  nextDialogFocusTarget,
  restoreDialogInvokerFocus,
  type DialogFocusableElement,
} from "./AccessibleDialog";
import { IconControl } from "./IconControl";
import {
  formatOperationalAnnouncement,
  nextOperationalAnnouncement,
  OperationalAnnouncer,
} from "./OperationalAnnouncer";
import { ActionControl } from "./projection/ActionControl";
import { IngestionForm, submitAuthorizedIngestion, type IngestionIntent } from "./projection/IngestionForms";
import { ExternalNavigationControl, mapAllowedActionContract, SafeContent } from "./projection/SafeContent";
import { createPublicApiClient } from "../lib/api/client";
import { SessionTransitionCoordinator } from "../lib/session/session-runtime";

class FocusableElement implements DialogFocusableElement {
  public focusCount = 0;

  public constructor(public readonly name: string) {}

  public focus(): void {
    this.focusCount += 1;
  }
}

const INGESTION_REQUIREMENTS = {
  fileTypes: ["text/plain"],
  maximumSizeBytes: 1024,
  ownershipRequirement: "Returned owner required.",
  retentionRequirement: "Returned retention required.",
} as const;

const RETURNED_ACTION = {
  id: "approve-1",
  label: "Approve returned release",
  eligible: true,
  source: { id: "approve-1", label: "Approve returned release" },
} as const;

test("traps dialog focus at each boundary and restores the connected invoker", (): void => {
  const heading = new FocusableElement("heading");
  const firstControl = new FocusableElement("first");
  const lastControl = new FocusableElement("last");
  const focusableControls = [firstControl, lastControl];

  assert.strictEqual(nextDialogFocusTarget(focusableControls, heading, false, heading), firstControl);
  assert.strictEqual(nextDialogFocusTarget(focusableControls, firstControl, true, heading), lastControl);
  assert.strictEqual(nextDialogFocusTarget(focusableControls, lastControl, false, heading), firstControl);
  assert.strictEqual(nextDialogFocusTarget([], heading, false, heading), heading);

  const invoker = new FocusableElement("invoker");
  restoreDialogInvokerFocus(invoker, { contains: (element: FocusableElement): boolean => element === invoker });
  restoreDialogInvokerFocus(lastControl, { contains: (): boolean => false });
  assert.equal(invoker.focusCount, 1);
  assert.equal(lastControl.focusCount, 0);

  const markup = renderToStaticMarkup(<AccessibleDialog onClose={(): void => undefined} open title="Returned approval"><button type="button">Confirm returned decision</button></AccessibleDialog>);
  assert.match(markup, /role="dialog"/);
  assert.match(markup, /tabindex="-1"/);
});

test("renders exact accessible control names and minimum mobile interaction targets", async (): Promise<void> => {
  const markup = renderToStaticMarkup(<>
    <ActionControl action={RETURNED_ACTION} onInvoke={(): void => undefined} stale={false} />
    <IconControl kind="refresh">↻</IconControl>
    <IconControl kind="reconnect">↺</IconControl>
    <IconControl kind="copyCorrelation">⧉</IconControl>
    <IconControl kind="close">×</IconControl>
  </>);
  assert.match(markup, />Approve returned release<\/button>/);
  assert.doesNotMatch(markup, /Approve returned release"/);
  assert.match(markup, /aria-label="Refresh operational projection"/);
  assert.match(markup, /aria-label="Reconnect live updates"/);
  assert.match(markup, /aria-label="Copy correlation identifier"/);
  assert.match(markup, /aria-label="Close"/);

  const css = await readFile(new URL("../app/globals.css", import.meta.url), "utf8");
  assert.match(css, /--focus-outline-width: 2px/);
  assert.match(css, /--focus-outline-offset: 2px/);
  assert.match(css, /@media \(min-width: 320px\) and \(max-width: 767px\) \{[\s\S]*?\.action-control, \.icon-control \{ min-width: var\(--minimum-action-target\); min-height: var\(--minimum-action-target\);/);
});

test("announces every changed returned operational state exactly once", (): void => {
  const live = { resourceName: "Run alpha", stateLabel: "Live", asOf: "2025-03-08T10:00:00Z" };
  const initial = nextOperationalAnnouncement(null, live);
  const repeated = nextOperationalAnnouncement(initial.transitionKey, live);
  const stale = nextOperationalAnnouncement(repeated.transitionKey, { ...live, stateLabel: "Stale", asOf: "2025-03-08T10:01:00Z" });
  const staleRepeated = nextOperationalAnnouncement(stale.transitionKey, { ...live, stateLabel: "Stale", asOf: "2025-03-08T10:02:00Z" });

  assert.equal(initial.announcement, null);
  assert.equal(repeated.announcement, null);
  assert.equal(stale.announcement, formatOperationalAnnouncement({ ...live, stateLabel: "Stale", asOf: "2025-03-08T10:01:00Z" }));
  assert.equal(staleRepeated.announcement, null);
  const markup = renderToStaticMarkup(<OperationalAnnouncer {...live} />);
  assert.match(markup, /role="status" aria-live="polite" aria-atomic="true"/);
});

test("clears session-bound state before authorizing another projection render", (): void => {
  const steps: string[] = [];
  const coordinator = new SessionTransitionCoordinator();
  coordinator.registerSseSubscription({ abort: (): void => { steps.push("abort"); } });
  coordinator.registerProjectionState({
    clearRestSnapshot: (): void => { steps.push("snapshot"); },
    clearIncrementalState: (): void => { steps.push("incremental"); },
  });
  coordinator.registerCache({ clearForSessionTransition: (): void => { steps.push("cache"); } });
  coordinator.registerCommandIntentPresentation({ clearCommandIntentPresentation: (): void => { steps.push("commands"); } });

  coordinator.beginSessionTransition();
  assert.deepEqual(steps, ["abort", "snapshot", "incremental", "cache", "commands"]);
  assert.equal(coordinator.canRenderAuthorizedProjection(), false);
  coordinator.authorizeNextProjection();
  assert.equal(coordinator.canRenderAuthorizedProjection(), true);
});

test("uses same-origin generated requests and enforces the production browser security policy", async (): Promise<void> => {
  let requestedPath = "";
  const client = createPublicApiClient({ fetchImpl: async (input: RequestInfo | URL): Promise<Response> => {
    requestedPath = String(input);
    return Response.json({ data: { run_id: "run-1", status: "queued" }, meta: { correlation_id: "corr-1" } });
  } });
  await client.request("read_run_api_v1_workflow_runs__run_id__get", { path: { run_id: "run-1" } });
  assert.equal(requestedPath, "/api/v1/workflow-runs/run-1");

  const config = await readFile(new URL("../../next.config.mjs", import.meta.url), "utf8");
  assert.match(config, /default-src 'self'; base-uri 'self'; connect-src 'self'; frame-ancestors 'none'; frame-src 'none'; object-src 'none';/);
  assert.match(config, /script-src 'self' 'unsafe-inline';/);
  assert.doesNotMatch(config, /unsafe-eval/);
  assert.match(config, /Referrer-Policy", "no-referrer/);
  assert.match(config, /Strict-Transport-Security", "max-age=63072000; includeSubDomains; preload/);
  assert.match(config, /X-Content-Type-Options", "nosniff/);
});

test("keeps external import URLs inert and blocks navigation without a returned allowed contract", async (): Promise<void> => {
  const externalImportUrl = "https://external.example/import?content=%3Cscript%3Ealert(1)%3C/script%3E";
  const markup = renderToStaticMarkup(<>
    <IngestionForm kind="knowledge" requirements={INGESTION_REQUIREMENTS} />
    <SafeContent content={{ externalImportUrl, markup: "<img src=external>" }} />
  </>);
  assert.match(markup, /Authorized ingestion is unavailable\. Submission is blocked\./);
  assert.match(markup, /data-safe-content="true"/);
  assert.doesNotMatch(markup, /<(?:script|iframe|img|object|embed)\b/i);
  assert.doesNotMatch(markup, /<[^>]+\s(?:href|src)=/i);

  const submittedIntents: IngestionIntent[] = [];
  assert.equal(await submitAuthorizedIngestion({
    operationId: "handoff_video_artifact_api_v1_video_artifacts_post",
    submit: async (intent: IngestionIntent): Promise<void> => { submittedIntents.push(intent); },
  }, { kind: "knowledge", content: { value: "returned text" }, externalImportUrl: { value: externalImportUrl } }), true);
  assert.deepEqual(submittedIntents, [{ kind: "knowledge", content: { value: "returned text" }, externalImportUrl: { value: externalImportUrl } }]);

  const blockedAction = mapAllowedActionContract({ id: "blocked", label: "Blocked", kind: "external_navigation", allowed: true, destination: "javascript:alert(1)", open_in_new_context: false });
  assert.equal(blockedAction, null);
  const blockedMarkup = renderToStaticMarkup(<ExternalNavigationControl action={blockedAction} />);
  assert.match(blockedMarkup, /disabled/);
  assert.doesNotMatch(blockedMarkup, /href=/);
});
