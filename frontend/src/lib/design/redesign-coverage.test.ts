/**
 * Functional coverage gate: redesign screens ui_00–ui_20 map to presentation
 * landings (or auth/menu shells) per docs/frontend_redesign/frontend_redesign.md
 * Phase 1 static mock delivery alignment.
 */
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const appRoot = resolve(dirname(fileURLToPath(import.meta.url)), "../../app");

const REDESIGN_ROUTES: readonly {
  readonly id: string;
  readonly page: string;
  readonly mustMatch: RegExp;
}[] = [
  { id: "ui_01_login", page: "login/page.tsx", mustMatch: /LoginScreen/ },
  { id: "ui_02_dashboard", page: "page.tsx", mustMatch: /DashboardHome/ },
  {
    id: "ui_03_composer",
    page: "composer/page.tsx",
    mustMatch: /ComposerHome/,
  },
  { id: "ui_04_canvas", page: "canvas/page.tsx", mustMatch: /CanvasHome/ },
  {
    id: "ui_05_agent_detail",
    page: "registry/agents/[agentId]/page.tsx",
    mustMatch: /AgentDetailHome/,
  },
  {
    id: "ui_06_activity",
    page: "activity/page.tsx",
    mustMatch: /ActivityHome/,
  },
  {
    id: "ui_07_registry",
    page: "registry/page.tsx",
    mustMatch: /RegistryHome/,
  },
  {
    id: "ui_08_settings",
    page: "settings/page.tsx",
    mustMatch: /SettingsHome/,
  },
  {
    id: "ui_09_monitoring",
    page: "operations/page.tsx",
    mustMatch: /MonitoringHome/,
  },
  {
    id: "ui_10_knowledge",
    page: "knowledge/page.tsx",
    mustMatch: /KnowledgeHome/,
  },
  {
    id: "ui_11_eval",
    page: "evaluations/page.tsx",
    mustMatch: /EvalHome/,
  },
  {
    id: "ui_12_notifications",
    page: "notifications/page.tsx",
    mustMatch: /NotificationsHome/,
  },
  {
    id: "ui_13_profile",
    page: "profile/page.tsx",
    mustMatch: /ProfileHome/,
  },
  { id: "ui_14_audit", page: "audit/page.tsx", mustMatch: /AuditHome/ },
  {
    id: "ui_15_api_portal",
    page: "developer/api/page.tsx",
    mustMatch: /ApiPortalHome/,
  },
  {
    id: "ui_16_onboarding",
    page: "onboarding/page.tsx",
    mustMatch: /OnboardingHome/,
  },
  {
    id: "ui_17_mobile",
    page: "mobile/page.tsx",
    mustMatch: /MobileHome/,
  },
  {
    id: "ui_18_collaboration",
    page: "collaboration/page.tsx",
    mustMatch: /CollaborationHome/,
  },
  { id: "ui_19_costs", page: "costs/page.tsx", mustMatch: /CostsHome/ },
  {
    id: "ui_20_blueprints",
    page: "blueprints/page.tsx",
    mustMatch: /BlueprintsHome/,
  },
];

test("redesign ui_01–ui_20 routes render dedicated presentation landings", async () => {
  for (const route of REDESIGN_ROUTES) {
    const source = await readFile(resolve(appRoot, route.page), "utf8");
    assert.match(
      source,
      route.mustMatch,
      `${route.id} (${route.page}) should mount ${route.mustMatch}`,
    );
    assert.doesNotMatch(
      source,
      /UnavailableScreen/,
      `${route.id} must not gate as unavailable`,
    );
  }
});

test("platform contract primitives exist for redesign requirements 8.x", async () => {
  const transport = await readFile(
    resolve(appRoot, "../lib/api/transport.ts"),
    "utf8",
  );
  const live = await readFile(
    resolve(appRoot, "../lib/live/LiveProjectionController.ts"),
    "utf8",
  );
  const sse = await readFile(
    resolve(appRoot, "../lib/live/sse-subscription.ts"),
    "utf8",
  );
  const commands = await readFile(
    resolve(appRoot, "../lib/commands/CommandCoordinator.ts"),
    "utf8",
  );
  const packExtensions = await readFile(
    resolve(appRoot, "../lib/pack-extensions/types.ts"),
    "utf8",
  );

  assert.match(transport, /api\/v1|Public API|same-origin/i);
  assert.match(transport, /Idempotency-Key/);
  assert.match(live, /sequence|resynchroniz/i);
  assert.match(sse, /Last-Event-ID|last_event_id|EventSource/i);
  assert.match(sse, /\/api\/v1\/events\/stream/);
  assert.match(commands, /Idempotency-Key|idempotency/i);
  assert.match(commands, /manual_recovery/);
  assert.match(packExtensions, /PackUiExtensionManifest|domainId|slotId/);
});
