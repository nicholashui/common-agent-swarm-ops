import assert from "node:assert/strict";
import test from "node:test";

import {
  APPLICATION_MENU_GROUPS,
  APPLICATION_MENU_ITEMS,
  getApplicationMenuItem,
  isMenuItemActive,
  isMenuItemVisible,
  listApplicationMenuLabels,
  resolveApplicationMenu,
} from "./application-menu";

const EXPECTED_LABELS = [
  "Dashboard",
  "Compose",
  "Swarm Canvas",
  "Blueprints",
  "Registry Hub",
  "Agent Org Chart",
  "Agent & Pattern Detail",
  "Activity",
  "Monitoring",
  "Approvals & Rollouts",
  "Notifications",
  "Costs",
  "Knowledge",
  "Eval & Improvement",
  "VA Production",
  "Audit",
  "Collaboration",
  "API Portal",
  "Onboarding & Help",
  "Settings",
  "Profile",
] as const;

const EXPECTED_GROUPS = [
  "Home",
  "Build",
  "Common",
  "Operate",
  "Knowledge & Quality",
  "Domain",
  "Governance",
  "Developer & Help",
  "Account",
] as const;

test("application menu labels match ui_00_menu information architecture", () => {
  assert.deepEqual(listApplicationMenuLabels(), [...EXPECTED_LABELS]);
  assert.deepEqual(
    APPLICATION_MENU_GROUPS.map((group) => group.label),
    [...EXPECTED_GROUPS],
  );
  assert.equal(APPLICATION_MENU_ITEMS.length, EXPECTED_LABELS.length);
});

test("default shell hides VA and unscoped agent detail", () => {
  const menu = resolveApplicationMenu("/");
  const labels = menu.flatMap((group) => group.items.map((item) => item.label));

  assert.ok(labels.includes("Dashboard"));
  assert.ok(labels.includes("Swarm Canvas"));
  assert.ok(labels.includes("Approvals & Rollouts"));
  assert.equal(labels.includes("VA Production"), false);
  assert.equal(labels.includes("Agent & Pattern Detail"), false);
  assert.equal(
    menu.some((group) => group.id === "domain"),
    false,
  );
});

test("agent detail appears only on a scoped registry agent path", () => {
  const agentPath = "/registry/agents/common-agent.verifier";
  assert.equal(
    isMenuItemVisible(agentPath, getApplicationMenuItem("agent-pattern-detail")!, undefined),
    true,
  );
  assert.equal(
    isMenuItemVisible("/registry", getApplicationMenuItem("agent-pattern-detail")!, undefined),
    false,
  );

  const menu = resolveApplicationMenu(agentPath);
  const detail = menu
    .flatMap((group) => group.items)
    .find((item) => item.id === "agent-pattern-detail");
  assert.ok(detail);
  assert.equal(detail.active, true);
  assert.equal(detail.href, agentPath);

  const registry = menu
    .flatMap((group) => group.items)
    .find((item) => item.id === "registry-hub");
  assert.ok(registry);
  assert.equal(registry.active, false);
});

test("VA production appears only when authorized by returned projection", () => {
  const item = getApplicationMenuItem("va-production")!;
  assert.equal(isMenuItemVisible("/", item, undefined), false);
  assert.equal(
    isMenuItemVisible("/", item, { authorizedItemIds: ["va-production"] }),
    true,
  );

  const menu = resolveApplicationMenu("/", {
    authorizedItemIds: ["va-production"],
  });
  assert.ok(
    menu.some((group) =>
      group.items.some((entry) => entry.id === "va-production"),
    ),
  );
});

test("route active matching covers dashboard, canvas, and operations", () => {
  const dashboard = getApplicationMenuItem("dashboard")!;
  const canvas = getApplicationMenuItem("swarm-canvas")!;
  const compose = getApplicationMenuItem("compose")!;
  const monitoring = getApplicationMenuItem("monitoring")!;

  assert.equal(isMenuItemActive("/", dashboard), true);
  assert.equal(isMenuItemActive("/composer", dashboard), false);
  assert.equal(isMenuItemActive("/canvas", canvas), true);
  assert.equal(isMenuItemActive("/swarms/run-42/canvas", canvas), true);
  assert.equal(isMenuItemActive("/swarms/run-42", canvas), false);
  assert.equal(isMenuItemActive("/composer", compose), true);
  assert.equal(isMenuItemActive("/operations", monitoring), true);
});

test("org chart is active under /registry/org-chart and defers hub", () => {
  const orgPath = "/registry/org-chart";
  const orgItem = getApplicationMenuItem("registry-org-chart")!;
  const hub = getApplicationMenuItem("registry-hub")!;

  assert.equal(isMenuItemVisible(orgPath, orgItem, undefined), true);
  assert.equal(isMenuItemActive(orgPath, orgItem), true);
  assert.equal(isMenuItemActive(orgPath, hub), false);
  assert.equal(isMenuItemActive("/registry", hub), true);
  assert.equal(isMenuItemActive("/registry", orgItem), false);
});

test("menu item routes align with screen-manifest destinations", () => {
  const routesById: Record<string, string> = {
    dashboard: "/",
    compose: "/composer",
    "swarm-canvas": "/canvas",
    blueprints: "/blueprints",
    "registry-hub": "/registry",
    "registry-org-chart": "/registry/org-chart",
    activity: "/activity",
    monitoring: "/operations",
    "approvals-rollouts": "/operations",
    notifications: "/notifications",
    costs: "/costs",
    knowledge: "/knowledge",
    "eval-improvement": "/evaluations",
    audit: "/audit",
    collaboration: "/collaboration",
    "api-portal": "/developer/api",
    "onboarding-help": "/onboarding",
    settings: "/settings",
    profile: "/profile",
  };

  for (const [id, href] of Object.entries(routesById)) {
    assert.equal(getApplicationMenuItem(id)?.href, href, id);
  }
});
