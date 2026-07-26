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

interface UnlockedRouteCase {
  readonly name: string;
  readonly source: URL;
  readonly screenId: Exclude<ScreenId, "ui_00_menu" | "ui_01_login">;
  readonly mustMatch: RegExp;
  readonly mustNotMatch?: RegExp;
}

const UNLOCKED_ROUTE_CASES: readonly UnlockedRouteCase[] = [
  {
    name: "dashboard",
    source: new URL("./page.tsx", import.meta.url),
    screenId: "ui_02_dashboard",
    mustMatch: /DashboardHome/,
    mustNotMatch: /UnavailableScreen/,
  },
  {
    name: "composer",
    source: new URL("./composer/page.tsx", import.meta.url),
    screenId: "ui_03_swarm_composer",
    mustMatch: /ComposerHome/,
    mustNotMatch: /UnavailableScreen/,
  },
  {
    name: "legacy canvas",
    source: new URL("./canvas/page.tsx", import.meta.url),
    screenId: "ui_04_canvas",
    mustMatch: /CanvasHome/,
    mustNotMatch: /UnavailableScreen|redirect\(/,
  },
  {
    name: "activity",
    source: new URL("./activity/page.tsx", import.meta.url),
    screenId: "ui_06_activity",
    mustMatch: /ActivityHome/,
    mustNotMatch: /UnavailableScreen/,
  },
  {
    name: "registry",
    source: new URL("./registry/page.tsx", import.meta.url),
    screenId: "ui_07_registry_hub",
    mustMatch: /RegistryHome/,
    mustNotMatch: /UnavailableScreen/,
  },
  {
    name: "settings",
    source: new URL("./settings/page.tsx", import.meta.url),
    screenId: "ui_08_settings",
    mustMatch: /SettingsHome/,
    mustNotMatch: /UnavailableScreen/,
  },
  {
    name: "operations / monitoring",
    source: new URL("./operations/page.tsx", import.meta.url),
    screenId: "ui_09_monitoring",
    mustMatch: /MonitoringHome/,
    mustNotMatch: /UnavailableScreen/,
  },
  {
    name: "knowledge",
    source: new URL("./knowledge/page.tsx", import.meta.url),
    screenId: "ui_10_knowledge",
    mustMatch: /KnowledgeHome/,
    mustNotMatch: /UnavailableScreen/,
  },
  {
    name: "evaluations",
    source: new URL("./evaluations/page.tsx", import.meta.url),
    screenId: "ui_11_eval",
    mustMatch: /EvalHome/,
    mustNotMatch: /UnavailableScreen/,
  },
  {
    name: "notifications",
    source: new URL("./notifications/page.tsx", import.meta.url),
    screenId: "ui_12_notifications",
    mustMatch: /NotificationsHome/,
    mustNotMatch: /UnavailableScreen/,
  },
  {
    name: "profile",
    source: new URL("./profile/page.tsx", import.meta.url),
    screenId: "ui_13_profile",
    mustMatch: /ProfileHome/,
    mustNotMatch: /UnavailableScreen/,
  },
  {
    name: "audit",
    source: new URL("./audit/page.tsx", import.meta.url),
    screenId: "ui_14_audit",
    mustMatch: /AuditHome/,
    mustNotMatch: /UnavailableScreen/,
  },
  {
    name: "developer API portal",
    source: new URL("./developer/api/page.tsx", import.meta.url),
    screenId: "ui_15_api_portal",
    mustMatch: /ApiPortalHome/,
    mustNotMatch: /UnavailableScreen/,
  },
  {
    name: "onboarding",
    source: new URL("./onboarding/page.tsx", import.meta.url),
    screenId: "ui_16_onboarding",
    mustMatch: /LocalDestinationPreview/,
    mustNotMatch: /UnavailableScreen/,
  },
  {
    name: "mobile companion",
    source: new URL("./mobile/page.tsx", import.meta.url),
    screenId: "ui_17_mobile",
    mustMatch: /LocalDestinationPreview/,
    mustNotMatch: /UnavailableScreen/,
  },
  {
    name: "collaboration",
    source: new URL("./collaboration/page.tsx", import.meta.url),
    screenId: "ui_18_collaboration",
    mustMatch: /LocalDestinationPreview/,
    mustNotMatch: /UnavailableScreen/,
  },
  {
    name: "costs",
    source: new URL("./costs/page.tsx", import.meta.url),
    screenId: "ui_19_costs",
    mustMatch: /LocalDestinationPreview/,
    mustNotMatch: /UnavailableScreen/,
  },
  {
    name: "blueprints",
    source: new URL("./blueprints/page.tsx", import.meta.url),
    screenId: "ui_20_blueprints",
    mustMatch: /LocalDestinationPreview/,
    mustNotMatch: /UnavailableScreen/,
  },
];

function readSource(source: URL): string {
  return readFileSync(source, "utf8");
}

test("menu destinations render local previews instead of unavailable gates", () => {
  for (const route of UNLOCKED_ROUTE_CASES) {
    const source = readSource(route.source);
    const definition = getScreenDefinition(route.screenId);

    assert.match(
      source,
      /AppShell/,
      `${route.name} should keep the authenticated shell`,
    );
    assert.match(
      source,
      route.mustMatch,
      `${route.name} should render its local destination`,
    );
    if (route.mustNotMatch) {
      assert.doesNotMatch(
        source,
        route.mustNotMatch,
        `${route.name} should not stay gated as unavailable`,
      );
    }
    assert.match(
      source,
      /function \w+Page/,
      `${route.name} should expose a page component`,
    );
    assert.equal(definition.routeOrShell.startsWith("/"), true);
    assert.match(definition.module, /^src\/app\//);
  }
});

test("canonical canvas route renders canvas while preserving the opaque resource parameter", () => {
  const source = readSource(
    new URL("./swarms/[swarmId]/canvas/page.tsx", import.meta.url),
  );

  assert.match(source, /params/);
  assert.match(source, /swarmId/);
  assert.match(source, /CanvasHome/);
  assert.doesNotMatch(source, /UnavailableScreen/);
  assert.equal(
    getScreenDefinition("ui_04_canvas").routeOrShell,
    "/swarms/[swarmId]/canvas",
  );
});

test("agent detail route renders AgentDetailHome local preview", () => {
  const source = readSource(
    new URL("./registry/agents/[agentId]/page.tsx", import.meta.url),
  );

  assert.match(source, /params/);
  assert.match(source, /agentId/);
  assert.match(source, /AgentDetailHome/);
  assert.doesNotMatch(source, /UnavailableScreen/);
  assert.equal(
    getScreenDefinition("ui_05_agent_detail").routeOrShell,
    "/registry/agents/[agentId]",
  );
});

test("login remains a public identity-only session-entry route", () => {
  const source = readSource(new URL("./login/page.tsx", import.meta.url));
  const markup = renderToStaticMarkup(<LoginScreen />);

  assert.match(source, /LoginScreen/);
  assert.doesNotMatch(source, /AuthenticatedShell|AppShell|UnavailableScreen/);
  assert.equal(getScreenDefinition("ui_01_login").routeOrShell, "/login");
  assert.match(markup, /aria-labelledby="login-title"/);
  assert.match(markup, /type="email"/);
  assert.match(markup, /type="password"/);
  assert.match(markup, />Sign in</);
  assert.match(markup, /Keycloak \(Self-hosted\)/);
  assert.match(markup, /Try Demo Workspace/);
  assert.doesNotMatch(markup, /tenant_id|actor_id|agent_id/i);
});
