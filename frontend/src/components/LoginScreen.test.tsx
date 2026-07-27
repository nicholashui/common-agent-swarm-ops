import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import React from "react";
import { renderToStaticMarkup } from "react-dom/server";

import { getScreenParameters } from "../lib/projections/screen-parameters";
import { LoginScreen } from "./LoginScreen";

const componentDirectory = dirname(fileURLToPath(import.meta.url));

test("login screen matches ui_01_login structure and identity-only boundary", () => {
  const markup = renderToStaticMarkup(
    <LoginScreen view={getScreenParameters("login")} />,
  );

  assert.match(markup, /common-agent-swarm-ops/);
  assert.match(markup, /Reusable agent swarms/);
  assert.match(markup, /v2\.0 · Common Registry Live/);
  assert.match(markup, /aria-labelledby="login-title"/);
  assert.match(markup, /Sign in to orchestrate/);
  assert.match(markup, /type="email"/);
  assert.match(markup, /type="password"/);
  assert.match(markup, /Remember this device/);
  assert.match(markup, /Forgot password\?/);
  assert.match(markup, />Sign in</);
  assert.match(markup, /or continue with/);
  assert.match(markup, /Keycloak \(Self-hosted\)/);
  assert.match(markup, />Google</);
  assert.match(markup, />GitHub</);
  assert.match(markup, /Try Demo Workspace/);
  assert.match(markup, /nicholas\.hui@local \/ NicholasAdmin1!/);
  assert.match(markup, /demo@local \/ demo/);
  assert.match(markup, /Docs/);
  assert.match(markup, /Demo available · No credit card/);
  assert.match(markup, /繁體中文/);
  assert.doesNotMatch(markup, /AuthenticatedShell|AppShell|UnavailableScreen/);
  assert.doesNotMatch(
    markup,
    /agent_id|task_id|artifact_id|critique|provenance_manifest|tenant_id/i,
  );
});

test("login and demo routes exist for session entry APIs", async () => {
  const root = resolve(componentDirectory, "..");
  const loginRoute = await readFile(
    resolve(root, "app/api/auth/login/route.ts"),
    "utf8",
  );
  const demoRoute = await readFile(
    resolve(root, "app/api/auth/demo/route.ts"),
    "utf8",
  );
  const resetRoute = await readFile(
    resolve(root, "app/api/auth/password-reset/route.ts"),
    "utf8",
  );
  const logoutRoute = await readFile(
    resolve(root, "app/api/auth/logout/route.ts"),
    "utf8",
  );
  const oidcCallback = await readFile(
    resolve(root, "app/api/auth/oidc/callback/route.ts"),
    "utf8",
  );

  assert.match(loginRoute, /verifyLocalPassword/);
  assert.match(demoRoute, /createDemoSessionClaims/);
  assert.match(resetRoute, /createPasswordResetToken/);
  assert.match(logoutRoute, /buildClearedSessionCookieOptions/);
  assert.match(oidcCallback, /exchangeOidcAuthorizationCode/);
  assert.match(oidcCallback, /sessionClaimsFromOidcIdentity/);
});

test("login CSS uses light-frame tokens and demo banner styles", async () => {
  const css = await readFile(
    resolve(componentDirectory, "../app/globals.css"),
    "utf8",
  );

  assert.match(css, /\.login-page \{/);
  assert.match(css, /#4f46e5/);
  assert.match(css, /#7c3aed/);
  assert.match(css, /\.login-demo \{/);
  assert.match(css, /\.demo-mode-banner \{/);
  assert.match(css, /\.login-reset-dialog \{/);
  assert.match(css, /linear-gradient\(90deg, #4f46e5, #7c3aed\)/);
});
