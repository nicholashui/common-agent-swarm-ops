import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import React from "react";
import { renderToStaticMarkup } from "react-dom/server";

import { LOCAL_AUDIT_LANDING } from "../lib/projections/audit-landing";
import { AuditHome } from "./AuditHome";

const componentDirectory = dirname(fileURLToPath(import.meta.url));

test("audit home matches ui_14 md/svg structure", () => {
  const markup = renderToStaticMarkup(<AuditHome />);

  assert.match(markup, /Governance &amp; Audit Trail/);
  assert.match(markup, /Tamper-evident, filterable, exportable/);
  assert.match(markup, /Search actor, action, correlation ID/);
  assert.match(markup, /Export CSV/);
  assert.match(markup, /Verify integrity/);
  assert.match(markup, /Filters/);
  assert.match(markup, /Last 24 hours/);
  assert.match(markup, /All users &amp; system/);
  assert.match(markup, /Rollout/);
  assert.match(markup, /Approval/);
  assert.match(markup, /Merge/);
  assert.match(markup, /Rollback/);
  assert.match(markup, /Config/);
  assert.match(markup, /Secret/);
  assert.match(markup, /Correlation ID/);
  assert.match(markup, /Chain verified/);
  assert.match(markup, /Hash chain intact/);
  assert.match(markup, /Immutable append-only/);
  assert.match(markup, /Timestamp \(UTC\)/);
  assert.match(markup, /04:12:31/);
  assert.match(markup, /rollback\.execute/);
  assert.match(markup, /Cursor pagination/);
  assert.match(markup, /12,480 entries/);
  assert.match(markup, /Event Detail|EVENT DETAIL/);
  assert.match(markup, /Prev hash/);
  assert.match(markup, /Entry hash/);
  assert.match(markup, /Linked context|Anomaly event/);
  assert.match(markup, /GateKeeper/);
  assert.match(markup, /Values redacted/);
  assert.match(markup, /authorized export/);
  assert.doesNotMatch(markup, /tenant_id|password=|authorization:\s*bearer/i);
  assert.doesNotMatch(markup, /sk-[a-zA-Z0-9]{8,}/);
});

test("audit fixture covers lineage fields and append-only safety", () => {
  assert.ok(LOCAL_AUDIT_LANDING.rows.length >= 6);
  assert.ok(
    LOCAL_AUDIT_LANDING.rows.some((row) => row.action === "rollback.execute"),
  );
  assert.ok(
    LOCAL_AUDIT_LANDING.rows.every(
      (row) => row.correlationId && row.prevHash && row.entryHash,
    ),
  );
  assert.ok(
    LOCAL_AUDIT_LANDING.rows.some((row) => row.graphRevision),
  );
  assert.ok(
    LOCAL_AUDIT_LANDING.rows.some((row) => row.commonVersion),
  );
  assert.match(LOCAL_AUDIT_LANDING.integrity.label, /Chain verified/i);
  assert.match(LOCAL_AUDIT_LANDING.safetyNote, /immutable/i);
  assert.doesNotMatch(
    JSON.stringify(LOCAL_AUDIT_LANDING),
    /sk-|password|api_key\s*[:=]/i,
  );
});

test("audit CSS defines filters, table, integrity, and detail drawer", async () => {
  const css = await readFile(
    resolve(componentDirectory, "../app/globals.css"),
    "utf8",
  );
  assert.match(css, /\.audit-home \{/);
  assert.match(css, /\.audit-home__filters/);
  assert.match(css, /\.audit-home__table/);
  assert.match(css, /\.audit-home__integrity/);
  assert.match(css, /\.audit-home__detail/);
});
