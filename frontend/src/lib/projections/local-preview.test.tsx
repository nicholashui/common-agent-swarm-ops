import assert from "node:assert/strict";
import test from "node:test";

import React from "react";
import { renderToStaticMarkup } from "react-dom/server";

import { LocalDestinationPreview } from "../../components/LocalDestinationPreview";
import { Dashboard } from "../../components/OperationalScreens";
import {
  LOCAL_DASHBOARD_PROJECTION,
  LOCAL_DESTINATION_COPY,
  LOCAL_PREVIEW_HANDLERS,
} from "./local-preview";

test("local dashboard projection is redaction-safe and marks local freshness", () => {
  assert.equal(LOCAL_DASHBOARD_PROJECTION.freshness, "Local preview");
  assert.equal(LOCAL_DASHBOARD_PROJECTION.stale, false);
  assert.doesNotMatch(
    JSON.stringify(LOCAL_DASHBOARD_PROJECTION),
    /password|token|secret|credential/i,
  );

  const markup = renderToStaticMarkup(
    <Dashboard
      projection={LOCAL_DASHBOARD_PROJECTION}
      {...LOCAL_PREVIEW_HANDLERS}
    />,
  );
  assert.match(markup, /Local preview/);
  assert.match(markup, /Fleet health and common impact/);
});

test("local destination copy covers destinations without dedicated renderers", () => {
  const keys = Object.keys(LOCAL_DESTINATION_COPY);
  assert.deepEqual(keys.sort(), [
    "apiPortal",
    "blueprints",
    "collaboration",
    "costs",
    "mobile",
    "onboarding",
    "settings",
  ]);

  const markup = renderToStaticMarkup(
    <LocalDestinationPreview copy={LOCAL_DESTINATION_COPY.settings} />,
  );
  assert.match(markup, /Settings/);
  assert.match(markup, /Local preview/);
  assert.match(markup, /backend projection is not connected/);
});
