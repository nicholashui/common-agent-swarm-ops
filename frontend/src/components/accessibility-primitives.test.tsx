import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import React from "react";
import { renderToStaticMarkup } from "react-dom/server";

import { AccessibleDialog } from "./AccessibleDialog";
import { IconControl, ICON_CONTROL_LABELS, getIconControlLabel } from "./IconControl";
import { formatOperationalAnnouncement, OperationalAnnouncer } from "./OperationalAnnouncer";
import { ResponsiveActionGroup, ResponsiveSplit, ResponsiveStack } from "./ResponsiveLayout";
import { CopyCorrelationIdentifierButton } from "./projection/CopyCorrelationIdentifierButton";

test("uses only the mandated accessible names for icon-only controls", () => {
  assert.deepEqual(ICON_CONTROL_LABELS, {
    refresh: "Refresh operational projection",
    reconnect: "Reconnect live updates",
    copyCorrelation: "Copy correlation identifier",
    close: "Close",
  });
  assert.equal(getIconControlLabel("reconnect"), "Reconnect live updates");

  const markup = renderToStaticMarkup(<><IconControl kind="refresh">↻</IconControl><CopyCorrelationIdentifierButton correlationIdentifier="corr-1" /></>);
  assert.match(markup, /aria-label="Refresh operational projection"/);
  assert.match(markup, /aria-label="Copy correlation identifier"/);
});

test("formats exact returned operational announcements in an atomic polite status region", () => {
  const announcement = formatOperationalAnnouncement({ resourceName: "Run alpha", stateLabel: "Stale", asOf: "2025-03-08T10:00:00Z" });
  assert.equal(announcement, "Run alpha: Stale; updated 2025-03-08T10:00:00Z");

  const markup = renderToStaticMarkup(<OperationalAnnouncer asOf="2025-03-08T10:00:00Z" resourceName="Run alpha" stateLabel="Stale" />);
  assert.match(markup, /role="status"/);
  assert.match(markup, /aria-live="polite"/);
  assert.match(markup, /aria-atomic="true"/);
});

test("renders dialog and responsive wrappers without changing supplied content", () => {
  const markup = renderToStaticMarkup(<ResponsiveStack><ResponsiveSplit primary={<p>Returned status: Stale</p>} secondary={<p>Returned evidence reference</p>} /><ResponsiveActionGroup><button type="button">Returned action</button></ResponsiveActionGroup><AccessibleDialog onClose={(): void => undefined} open title="Returned approval"><p>Returned approval state</p></AccessibleDialog></ResponsiveStack>);
  assert.match(markup, /responsive-stack/);
  assert.match(markup, /responsive-split/);
  assert.match(markup, /responsive-action-group/);
  assert.match(markup, /role="dialog"/);
  assert.match(markup, /aria-modal="true"/);
  assert.match(markup, /Returned status: Stale/);
  assert.match(markup, /Returned evidence reference/);
  assert.match(markup, /Returned approval state/);
});

test("defines minimum focus and mobile action-target tokens", async () => {
  const componentDirectory = dirname(fileURLToPath(import.meta.url));
  const css = await readFile(resolve(componentDirectory, "../app/globals.css"), "utf8");

  assert.match(css, /--focus-outline-width: 2px/);
  assert.match(css, /--focus-outline-offset: 2px/);
  assert.match(css, /outline: var\(--focus-outline-width\) solid var\(--focus-ring\); outline-offset: var\(--focus-outline-offset\)/);
  assert.match(css, /\[tabindex\]:not\(\[tabindex="-1"\]\):focus-visible/);
  assert.match(css, /@media \(min-width: 320px\) and \(max-width: 767px\) \{[\s\S]*?\.action-control, \.icon-control \{ min-width: var\(--minimum-action-target\); min-height: var\(--minimum-action-target\);/);
});
