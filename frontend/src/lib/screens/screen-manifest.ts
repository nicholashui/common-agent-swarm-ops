export interface ScreenViewport {
  readonly width: number;
  readonly height: number;
}

export interface ScreenFixture {
  readonly id: string;
  readonly version: "1.0.0";
  readonly grantedCapability: ScreenCapability;
  readonly unavailableError: ScreenUnavailableError;
}

export interface ScreenUnavailableError {
  readonly code: string;
  readonly message: string;
}

export interface ScreenDefinition<TId extends ScreenId = ScreenId> {
  readonly uiId: TId;
  readonly routeOrShell: string;
  readonly module: string;
  readonly requiredCapability: ScreenCapability;
  readonly behaviorBaseline: string;
  readonly svgBaseline: string;
  readonly fixtureId: ScreenFixtureId<TId>;
  readonly viewports: readonly ScreenViewport[];
}

export const SCREEN_IDS = [
  "ui_00_menu", "ui_01_login", "ui_02_dashboard", "ui_03_swarm_composer",
  "ui_04_canvas", "ui_05_agent_detail", "ui_06_activity", "ui_07_registry_hub",
  "ui_08_settings", "ui_09_monitoring", "ui_10_knowledge", "ui_11_eval",
  "ui_12_notifications", "ui_13_profile", "ui_14_audit", "ui_15_api_portal",
  "ui_16_onboarding", "ui_17_mobile", "ui_18_collaboration", "ui_19_costs",
  "ui_20_blueprints",
] as const;

export type ScreenId = (typeof SCREEN_IDS)[number];
export type ScreenFixtureId<TId extends ScreenId = ScreenId> = `fixture.${TId}`;
export type ScreenCapability =
  | "navigation.read"
  | "session.entry"
  | "dashboard.read"
  | "swarm.composer.read"
  | "swarm.canvas.read"
  | "registry.agent.read"
  | "activity.read"
  | "registry.read"
  | "settings.read"
  | "operations.monitoring.read"
  | "knowledge.read"
  | "evaluations.read"
  | "notifications.read"
  | "profile.read"
  | "audit.read"
  | "developer.api.read"
  | "onboarding.read"
  | "mobile.operations.read"
  | "collaboration.read"
  | "costs.read"
  | "blueprints.read";

const MOBILE_VIEWPORT: ScreenViewport = { width: 390, height: 844 };
const VIEWPORTS = {
  menu: [{ width: 1440, height: 1000 }, MOBILE_VIEWPORT],
  login: [{ width: 1440, height: 1000 }, MOBILE_VIEWPORT],
  dashboard: [{ width: 1440, height: 1480 }, MOBILE_VIEWPORT],
  composer: [{ width: 1440, height: 1000 }, MOBILE_VIEWPORT],
  canvas: [{ width: 1440, height: 1000 }],
  agentDetail: [{ width: 1440, height: 1120 }, MOBILE_VIEWPORT],
  activity: [{ width: 1440, height: 1080 }, MOBILE_VIEWPORT],
  registry: [{ width: 1440, height: 1140 }, MOBILE_VIEWPORT],
  standard: [{ width: 1440, height: 1000 }, MOBILE_VIEWPORT],
  mobile: [MOBILE_VIEWPORT],
} as const satisfies Record<string, readonly ScreenViewport[]>;

const BASELINE_ROOT = "docs/frontend_redesign";

function definition<TId extends ScreenId>(
  uiId: TId,
  routeOrShell: string,
  module: string,
  requiredCapability: ScreenCapability,
  viewports: readonly ScreenViewport[],
): ScreenDefinition<TId> {
  return {
    uiId,
    routeOrShell,
    module,
    requiredCapability,
    behaviorBaseline: `${BASELINE_ROOT}/${uiId}.md`,
    svgBaseline: `${BASELINE_ROOT}/${uiId}.svg`,
    fixtureId: `fixture.${uiId}`,
    viewports,
  };
}

export const SCREEN_DEFINITION_BY_ID: { readonly [TId in ScreenId]: ScreenDefinition<TId> } = {
  ui_00_menu: definition("ui_00_menu", "AuthenticatedShell", "src/components/AppShell.tsx", "navigation.read", VIEWPORTS.menu),
  ui_01_login: definition("ui_01_login", "/login", "src/app/login/page.tsx", "session.entry", VIEWPORTS.login),
  ui_02_dashboard: definition("ui_02_dashboard", "/", "src/app/page.tsx", "dashboard.read", VIEWPORTS.dashboard),
  ui_03_swarm_composer: definition("ui_03_swarm_composer", "/composer", "src/app/composer/page.tsx", "swarm.composer.read", VIEWPORTS.composer),
  ui_04_canvas: definition("ui_04_canvas", "/swarms/[swarmId]/canvas", "src/app/swarms/[swarmId]/canvas/page.tsx", "swarm.canvas.read", VIEWPORTS.canvas),
  ui_05_agent_detail: definition("ui_05_agent_detail", "/registry/agents/[agentId]", "src/app/registry/agents/[agentId]/page.tsx", "registry.agent.read", VIEWPORTS.agentDetail),
  ui_06_activity: definition("ui_06_activity", "/activity", "src/app/activity/page.tsx", "activity.read", VIEWPORTS.activity),
  ui_07_registry_hub: definition("ui_07_registry_hub", "/registry", "src/app/registry/page.tsx", "registry.read", VIEWPORTS.registry),
  ui_08_settings: definition("ui_08_settings", "/settings", "src/app/settings/page.tsx", "settings.read", VIEWPORTS.standard),
  ui_09_monitoring: definition("ui_09_monitoring", "/operations", "src/app/operations/page.tsx", "operations.monitoring.read", VIEWPORTS.standard),
  ui_10_knowledge: definition("ui_10_knowledge", "/knowledge", "src/app/knowledge/page.tsx", "knowledge.read", VIEWPORTS.standard),
  ui_11_eval: definition("ui_11_eval", "/evaluations", "src/app/evaluations/page.tsx", "evaluations.read", VIEWPORTS.standard),
  ui_12_notifications: definition("ui_12_notifications", "/notifications", "src/app/notifications/page.tsx", "notifications.read", VIEWPORTS.standard),
  ui_13_profile: definition("ui_13_profile", "/profile", "src/app/profile/page.tsx", "profile.read", VIEWPORTS.standard),
  ui_14_audit: definition("ui_14_audit", "/audit", "src/app/audit/page.tsx", "audit.read", VIEWPORTS.standard),
  ui_15_api_portal: definition("ui_15_api_portal", "/developer/api", "src/app/developer/api/page.tsx", "developer.api.read", VIEWPORTS.standard),
  ui_16_onboarding: definition("ui_16_onboarding", "/onboarding", "src/app/onboarding/page.tsx", "onboarding.read", VIEWPORTS.standard),
  ui_17_mobile: definition("ui_17_mobile", "/mobile", "src/app/mobile/page.tsx", "mobile.operations.read", VIEWPORTS.mobile),
  ui_18_collaboration: definition("ui_18_collaboration", "/collaboration", "src/app/collaboration/page.tsx", "collaboration.read", VIEWPORTS.standard),
  ui_19_costs: definition("ui_19_costs", "/costs", "src/app/costs/page.tsx", "costs.read", VIEWPORTS.standard),
  ui_20_blueprints: definition("ui_20_blueprints", "/blueprints", "src/app/blueprints/page.tsx", "blueprints.read", VIEWPORTS.standard),
};

export const SCREEN_DEFINITIONS: readonly ScreenDefinition[] = SCREEN_IDS.map(
  (screenId) => SCREEN_DEFINITION_BY_ID[screenId],
);

export function getScreenDefinition(screenId: ScreenId): ScreenDefinition {
  return SCREEN_DEFINITION_BY_ID[screenId];
}

function fixture<TId extends ScreenId>(
  screenId: TId,
  grantedCapability: ScreenCapability,
): ScreenFixture {
  return {
    id: `fixture.${screenId}`,
    version: "1.0.0",
    grantedCapability,
    unavailableError: {
      code: "capability_unavailable",
      message: "This authorized screen is currently unavailable.",
    },
  };
}

export const SCREEN_FIXTURE_REGISTRY: { readonly [TId in ScreenId]: ScreenFixture } = {
  ui_00_menu: fixture("ui_00_menu", "navigation.read"),
  ui_01_login: fixture("ui_01_login", "session.entry"),
  ui_02_dashboard: fixture("ui_02_dashboard", "dashboard.read"),
  ui_03_swarm_composer: fixture("ui_03_swarm_composer", "swarm.composer.read"),
  ui_04_canvas: fixture("ui_04_canvas", "swarm.canvas.read"),
  ui_05_agent_detail: fixture("ui_05_agent_detail", "registry.agent.read"),
  ui_06_activity: fixture("ui_06_activity", "activity.read"),
  ui_07_registry_hub: fixture("ui_07_registry_hub", "registry.read"),
  ui_08_settings: fixture("ui_08_settings", "settings.read"),
  ui_09_monitoring: fixture("ui_09_monitoring", "operations.monitoring.read"),
  ui_10_knowledge: fixture("ui_10_knowledge", "knowledge.read"),
  ui_11_eval: fixture("ui_11_eval", "evaluations.read"),
  ui_12_notifications: fixture("ui_12_notifications", "notifications.read"),
  ui_13_profile: fixture("ui_13_profile", "profile.read"),
  ui_14_audit: fixture("ui_14_audit", "audit.read"),
  ui_15_api_portal: fixture("ui_15_api_portal", "developer.api.read"),
  ui_16_onboarding: fixture("ui_16_onboarding", "onboarding.read"),
  ui_17_mobile: fixture("ui_17_mobile", "mobile.operations.read"),
  ui_18_collaboration: fixture("ui_18_collaboration", "collaboration.read"),
  ui_19_costs: fixture("ui_19_costs", "costs.read"),
  ui_20_blueprints: fixture("ui_20_blueprints", "blueprints.read"),
};

export function getScreenFixture(screenId: ScreenId): ScreenFixture {
  return SCREEN_FIXTURE_REGISTRY[screenId];
}
