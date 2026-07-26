import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import React from "react";
import { renderToStaticMarkup } from "react-dom/server";

import { LOCAL_API_PORTAL_LANDING } from "../lib/projections/api-portal-landing";
import { ApiPortalHome } from "./ApiPortalHome";

const componentDirectory = dirname(fileURLToPath(import.meta.url));

test("api portal home matches ui_15 md/svg structure", () => {
  const markup = renderToStaticMarkup(<ApiPortalHome />);

  assert.match(markup, /Developer \/ API Portal/);
  assert.match(markup, /Programmatic access to Registry/);
  assert.match(markup, /OpenAPI-driven docs/);
  assert.match(markup, /Search endpoints, SDK/);
  assert.match(markup, />Docs</);
  assert.match(markup, />SDKs</);
  assert.match(markup, />Tokens</);
  assert.match(markup, />Webhooks</);
  assert.match(markup, /Extensibility/);
  assert.match(markup, /REGISTRY/);
  assert.match(markup, /SWARMS/);
  assert.match(markup, /OPS/);
  assert.match(markup, /POST/);
  assert.match(markup, /\/api\/v1\/swarms\/\{id\}\/run|swarms\/\{id\}\/run/);
  assert.match(markup, /swarm:run|Requires:/);
  assert.match(markup, /Parameters/);
  assert.match(markup, /idempotency_key/);
  assert.match(markup, /curl|Copy/);
  assert.match(markup, /run_id|run-4421/);
  assert.match(markup, /pinned_commons|Try it in sandbox/);
  assert.match(markup, /View OpenAPI spec/);
  assert.match(markup, /scopes\/rate limits|server-side/);
  assert.doesNotMatch(markup, /tenant_id|password=|authorization:\s*bearer\s+[A-Za-z0-9._-]{20,}/i);
  assert.doesNotMatch(markup, /caso_sk_[a-zA-Z0-9]{16,}/);
});

test("api portal fixture covers endpoints, tokens, webhooks, VA note", () => {
  assert.ok(LOCAL_API_PORTAL_LANDING.endpoints.length >= 6);
  assert.ok(
    LOCAL_API_PORTAL_LANDING.endpoints.some((e) => e.path.includes("/run")),
  );
  assert.equal(LOCAL_API_PORTAL_LANDING.tokens.length, 2);
  assert.ok(
    LOCAL_API_PORTAL_LANDING.tokens.every((t) => t.masked.includes("••••")),
  );
  assert.equal(LOCAL_API_PORTAL_LANDING.webhooks.length, 1);
  assert.equal(LOCAL_API_PORTAL_LANDING.deliveries.length, 3);
  assert.ok(LOCAL_API_PORTAL_LANDING.schemas.includes("L1 / L2 / L3 quality gates"));
  assert.match(LOCAL_API_PORTAL_LANDING.vaNote, /adapter\/reference/i);
  assert.match(LOCAL_API_PORTAL_LANDING.safetyNote, /opaque IDs/i);
});

test("api portal CSS defines nav, explorer, tokens, and webhooks", async () => {
  const css = await readFile(
    resolve(componentDirectory, "../app/globals.css"),
    "utf8",
  );
  assert.match(css, /\.api-portal \{/);
  assert.match(css, /\.api-portal__nav/);
  assert.match(css, /\.api-portal__method/);
  assert.match(css, /\.api-portal__token-list/);
  assert.match(css, /\.api-portal__webhooks/);
});
