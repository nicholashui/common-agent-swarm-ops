import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import React from "react";
import { renderToStaticMarkup } from "react-dom/server";

import { ApplicationMenuView } from "./ShellNavigation";

const componentDirectory = dirname(fileURLToPath(import.meta.url));

test("shell navigation renders ui_00_menu product chrome and IA groups", () => {
  const markup = renderToStaticMarkup(
    <ApplicationMenuView pathname="/">
      <p>Returned main content</p>
    </ApplicationMenuView>,
  );

  assert.match(markup, /aria-label="Application menu"/);
  assert.match(markup, /common-agent-swarm-ops/);
  assert.match(markup, /Common-first control plane/);
  assert.match(markup, /Returned workspace/);
  assert.match(markup, /Authorized session scope/);
  assert.match(markup, /aria-label="Main navigation"/);
  assert.match(markup, /data-menu-group="home"/);
  assert.match(markup, /data-menu-group="build"/);
  assert.match(markup, /data-menu-group="operate"/);
  assert.match(markup, /data-menu-item="dashboard"/);
  assert.match(markup, /data-menu-item="compose"/);
  assert.match(markup, /data-menu-item="swarm-canvas"/);
  assert.match(markup, /data-menu-item="blueprints"/);
  assert.match(markup, /data-menu-item="approvals-rollouts"/);
  assert.match(markup, />Dashboard</);
  assert.match(markup, />Swarm Canvas</);
  assert.match(markup, />Approvals &amp; Rollouts</);
  assert.match(markup, /HOME/);
  assert.match(markup, /Reconnecting/);
  assert.match(markup, /Collapse menu/);
  assert.match(markup, /Returned main content/);
  assert.doesNotMatch(markup, /VA Production/);
  assert.doesNotMatch(markup, /Agent &amp; Pattern Detail/);
  assert.match(markup, /aria-expanded="true"/);
  assert.match(markup, /menu-group-toggle/);
  assert.match(markup, /aria-current="page"/);
  assert.match(markup, /href="\/composer"/);
  assert.match(markup, /href="\/canvas"/);
});

test("shell navigation shows authorized VA and correlation when returned", () => {
  const markup = renderToStaticMarkup(
    <ApplicationMenuView
      menuProjection={{
        authorizedItemIds: ["va-production"],
        workspaceName: "Acme Studio",
        workspaceScopeLabel: "org-42 scope",
        connectionStateLabel: "Live",
        connectionDetail: "Status: fresh · as_of 2026-07-26T00:00:00Z",
        correlationIdentifier: "corr-menu-1",
        environmentLabel: "demo",
      }}
      pathname="/registry/agents/agent-1"
    >
      <p>Main</p>
    </ApplicationMenuView>,
  );

  assert.match(markup, /VA Production/);
  assert.match(markup, /data-menu-item="va-production"/);
  assert.match(markup, /Agent &amp; Pattern Detail/);
  assert.match(markup, /Acme Studio/);
  assert.match(markup, /corr-menu-1/);
  assert.match(markup, />Live</);
  assert.match(markup, /demo/);
});

test("menu CSS implements 264px rail, 72px compact, and 44px mobile targets", async () => {
  const css = await readFile(
    resolve(componentDirectory, "../app/globals.css"),
    "utf8",
  );

  assert.match(css, /\.menu-workspace \{[\s\S]*?grid-template-columns: 264px/);
  assert.match(css, /\.menu-sidebar \{[\s\S]*?width: 264px/);
  assert.match(css, /\.app-shell--compact \.menu-workspace \{[\s\S]*?72px/);
  assert.match(css, /background: #fafaf9/);
  assert.match(css, /background: #4f46e5/);
  assert.match(css, /color: #1c1917/);
  assert.match(css, /color: #78716c/);
  assert.match(css, /--minimum-action-target/);
  assert.match(css, /@media \(max-width: 900px\)/);
  assert.match(css, /\.menu-sidebar--open/);
});
