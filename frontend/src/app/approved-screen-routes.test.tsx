import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

import React from "react";
import { renderToStaticMarkup } from "react-dom/server";

import { LoginScreen } from "../components/LoginScreen";
import {
  getScreenDefinition,
  type ScreenId,
} from "../lib/screens/screen-manifest";

interface ProtectedRouteCase {
  readonly name: string;
  readonly source: URL;
  readonly screenId: Exclude<ScreenId, "ui_01_login">;
}

const PROTECTED_ROUTE_CASES: readonly ProtectedRouteCase[] = [
  {
    name: "settings",
    source: new URL("./settings/page.tsx", import.meta.url),
    screenId: "ui_08_settings",
  },
  {
    name: "developer API portal",
    source: new URL("./developer/api/page.tsx", import.meta.url),
    screenId: "ui_15_api_portal",
  },
  {
    name: "onboarding",
    source: new URL("./onboarding/page.tsx", import.meta.url),
    screenId: "ui_16_onboarding",
  },
  {
    name: "mobile companion",
    source: new URL("./mobile/page.tsx", import.meta.url),
    screenId: "ui_17_mobile",
  },
  {
    name: "collaboration",
    source: new URL("./collaboration/page.tsx", import.meta.url),
    screenId: "ui_18_collaboration",
  },
  {
    name: "costs",
    source: new URL("./costs/page.tsx", import.meta.url),
    screenId: "ui_19_costs",
  },
  {
    name: "blueprints",
    source: new URL("./blueprints/page.tsx", import.meta.url),
    screenId: "ui_20_blueprints",
  },
];

function readSource(source: URL): string {
  return readFileSync(source, "utf8");
}

test("approved protected routes delegate to their manifest capability boundary", () => {
  for (const route of PROTECTED_ROUTE_CASES) {
    const source = readSource(route.source);
    const definition = getScreenDefinition(route.screenId);

    assert.match(source, /UnavailableScreen/);
    assert.equal(
      source.includes(`screenId="${route.screenId}"`),
      true,
      `${route.name} should select its approved screen`,
    );
    assert.match(
      source,
      /function \w+Page/,
      `${route.name} should expose a page component`,
    );
    assert.equal(definition.routeOrShell.startsWith("/"), true);
    assert.match(definition.module, /^src\/app\//);
  }
});

test("canonical canvas route preserves the opaque resource parameter and capability gate", () => {
  const source = readSource(
    new URL("./swarms/[swarmId]/canvas/page.tsx", import.meta.url),
  );

  assert.match(source, /params/);
  assert.match(source, /swarmId/);
  assert.match(source, /UnavailableScreen/);
  assert.equal(source.includes('screenId="ui_04_canvas"'), true);
  assert.equal(
    getScreenDefinition("ui_04_canvas").routeOrShell,
    "/swarms/[swarmId]/canvas",
  );
});

test("login remains a public identity-only session-entry route", () => {
  const source = readSource(new URL("./login/page.tsx", import.meta.url));
  const markup = renderToStaticMarkup(<LoginScreen />);

  assert.match(source, /LoginScreen/);
  assert.doesNotMatch(source, /AuthenticatedShell|AppShell|UnavailableScreen/);
  assert.equal(getScreenDefinition("ui_01_login").routeOrShell, "/login");
  assert.match(markup, /aria-labelledby="login-title"/);
  assert.match(markup, /<label>Email<input type="email"/);
  assert.match(markup, /<label>Password<input type="password"/);
  assert.match(markup, />Sign in<\/button>/);
});

test("legacy canvas route redirects instead of inventing a swarm identifier", () => {
  const source = readSource(new URL("./canvas/page.tsx", import.meta.url));

  assert.equal(source.includes('redirect("/")'), true);
  assert.equal(source.includes("components/Canvas"), false);
});
