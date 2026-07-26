import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import React from "react";
import { renderToStaticMarkup } from "react-dom/server";

import {
  LOCAL_SETTINGS_LANDING,
  SETTINGS_NAV,
} from "../lib/projections/settings-landing";
import { SettingsHome } from "./SettingsHome";

const componentDirectory = dirname(fileURLToPath(import.meta.url));

test("settings home matches ui_08 md/svg structure", () => {
  const markup = renderToStaticMarkup(<SettingsHome />);

  assert.match(markup, /Global Settings &amp; Configuration/);
  assert.match(markup, /Self-hosted control center/);
  assert.match(markup, /Search across settings/);
  assert.match(markup, /LLM Providers &amp; Models/);
  assert.match(markup, /Credentials &amp; Secrets Vault/);
  assert.match(markup, /Integrations/);
  assert.match(markup, /Policies &amp; Guardrails/);
  assert.match(markup, /Defaults \(Swarm \/ Common\)/);
  assert.match(markup, /UI &amp; Preferences/);
  assert.match(markup, /Workspaces &amp; Access/);
  // Default section: providers
  assert.match(markup, /xAI · Grok|xAI/);
  assert.match(markup, /OpenAI/);
  assert.match(markup, /Local \/ Ollama/);
  assert.match(markup, /Connected/);
  assert.match(markup, /Degraded/);
  assert.match(markup, /Test connection/);
  assert.match(markup, /Fetch models/);
  assert.match(markup, /Add provider/);
  assert.match(markup, /policy-approved defaults/);
  assert.doesNotMatch(markup, /sk-|api_key\s*=|password=/i);
  assert.doesNotMatch(markup, /tenant_id|authorization:\s*bearer/i);
});

test("settings fixture covers all sections and never embeds secret values", () => {
  assert.equal(SETTINGS_NAV.length, 7);
  assert.deepEqual(
    SETTINGS_NAV.map((item) => item.id),
    [
      "providers",
      "secrets",
      "integrations",
      "policies",
      "defaults",
      "ui",
      "workspaces",
    ],
  );
  assert.equal(LOCAL_SETTINGS_LANDING.providers.length, 3);
  assert.equal(LOCAL_SETTINGS_LANDING.secrets.length, 2);
  assert.ok(
    LOCAL_SETTINGS_LANDING.secrets.every(
      (secret) => secret.status.includes("value hidden"),
    ),
  );
  assert.ok(
    LOCAL_SETTINGS_LANDING.policies.some(
      (policy) => policy.label === "Version pinning policy",
    ),
  );
  assert.ok(
    LOCAL_SETTINGS_LANDING.defaults.some((item) =>
      item.label.includes("Model routing"),
    ),
  );
  assert.equal(LOCAL_SETTINGS_LANDING.members.length, 2);
  assert.match(LOCAL_SETTINGS_LANDING.vaNote, /immutable agent version/i);
  assert.match(JSON.stringify(LOCAL_SETTINGS_LANDING), /value hidden/);
  assert.doesNotMatch(
    JSON.stringify(LOCAL_SETTINGS_LANDING),
    /sk-[a-zA-Z0-9]|xai-[a-zA-Z0-9]{8,}/,
  );
});

test("settings CSS defines nav, cards, impact, and vault table", async () => {
  const css = await readFile(
    resolve(componentDirectory, "../app/globals.css"),
    "utf8",
  );
  assert.match(css, /\.settings-home \{/);
  assert.match(css, /\.settings-home__nav/);
  assert.match(css, /\.settings-home__card/);
  assert.match(css, /\.settings-home__impact/);
  assert.match(css, /\.settings-home__table/);
});
