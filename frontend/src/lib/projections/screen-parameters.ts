/**
 * Stored screen parameters for redesign landings.
 *
 * Presentation data lives only in projection modules (`*-landing.ts`). Pages and
 * components must read through this store (or an explicit `view` prop sourced
 * from it). Components must not embed LOCAL_* fixtures as hardcoded defaults.
 *
 * When generated /api/v1 projections exist, replace values via
 * `setScreenParameters` / `updateScreenParameters` — UI re-renders through
 * `useScreenParameters` subscribers.
 */

import {
  LOCAL_ACTIVITY_LANDING,
  type ActivityLandingView,
} from "./activity-landing";
import type { AgentDetailLandingView } from "./agent-detail-landing";
import { AGENT_DETAIL_PARAMETER_STUB } from "./agent-detail-stub";
import {
  LOCAL_API_PORTAL_LANDING,
  type ApiPortalLandingView,
} from "./api-portal-landing";
import {
  LOCAL_AUDIT_LANDING,
  type AuditLandingView,
} from "./audit-landing";
import {
  LOCAL_BLUEPRINTS_LANDING,
  type BlueprintsLandingView,
} from "./blueprints-landing";
import {
  LOCAL_CANVAS_LANDING,
  type CanvasLandingView,
} from "./canvas-landing";
import {
  LOCAL_COLLABORATION_LANDING,
  type CollaborationLandingView,
} from "./collaboration-landing";
import {
  LOCAL_COMPOSER_LANDING,
  type ComposerLandingView,
} from "./composer-landing";
import {
  LOCAL_COSTS_LANDING,
  type CostsLandingView,
} from "./costs-landing";
import {
  LOCAL_DASHBOARD_LANDING,
  type DashboardLandingView,
} from "./dashboard-landing";
import {
  LOCAL_EVAL_LANDING,
  type EvalLandingView,
} from "./eval-landing";
import {
  LOCAL_KNOWLEDGE_LANDING,
  type KnowledgeLandingView,
} from "./knowledge-landing";
import {
  LOCAL_LOGIN_LANDING,
  type LoginLandingView,
} from "./login-landing";
import {
  LOCAL_MOBILE_LANDING,
  type MobileLandingView,
} from "./mobile-landing";
import {
  LOCAL_MONITORING_LANDING,
  type MonitoringLandingView,
} from "./monitoring-landing";
import {
  LOCAL_NOTIFICATIONS_LANDING,
  type NotificationsLandingView,
} from "./notifications-landing";
import {
  LOCAL_ONBOARDING_LANDING,
  type OnboardingLandingView,
} from "./onboarding-landing";
import {
  ORG_CHART_PAYLOAD,
  type OrgChartPayload,
} from "./org-chart.generated";
import {
  AGENT_WORKFLOW_PAYLOAD,
  type AgentWorkflowPayload,
} from "./agent-workflow.generated";
import {
  LOCAL_PROFILE_LANDING,
  type ProfileLandingView,
} from "./profile-landing";
import {
  LOCAL_REGISTRY_LANDING,
  type RegistryLandingView,
} from "./registry-landing";
import {
  LOCAL_SETTINGS_LANDING,
  type SettingsLandingView,
} from "./settings-landing";
import {
  LOCAL_SPECIALS_LANDING,
  type SpecialsLandingView,
} from "./specials-landing";
import type { GeneratedJsonObject } from "../api/client";
import { LOCAL_APPROVAL_PROJECTION } from "./local-preview";

export type ScreenParameterKey =
  | "dashboard"
  | "activity"
  | "agentDetail"
  | "apiPortal"
  | "audit"
  | "blueprints"
  | "canvas"
  | "collaboration"
  | "composer"
  | "costs"
  | "eval"
  | "knowledge"
  | "login"
  | "mobile"
  | "monitoring"
  | "notifications"
  | "onboarding"
  | "orgChart"
  | "agentWorkflow"
  | "profile"
  | "registry"
  | "settings"
  | "specials"
  | "approval";

export interface ScreenParameterMap {
  readonly dashboard: DashboardLandingView;
  readonly activity: ActivityLandingView;
  readonly agentDetail: AgentDetailLandingView;
  readonly apiPortal: ApiPortalLandingView;
  readonly audit: AuditLandingView;
  readonly blueprints: BlueprintsLandingView;
  readonly canvas: CanvasLandingView;
  readonly collaboration: CollaborationLandingView;
  readonly composer: ComposerLandingView;
  readonly costs: CostsLandingView;
  readonly eval: EvalLandingView;
  readonly knowledge: KnowledgeLandingView;
  readonly login: LoginLandingView;
  readonly mobile: MobileLandingView;
  readonly monitoring: MonitoringLandingView;
  readonly notifications: NotificationsLandingView;
  readonly onboarding: OnboardingLandingView;
  readonly orgChart: OrgChartPayload;
  readonly agentWorkflow: AgentWorkflowPayload;
  readonly profile: ProfileLandingView;
  readonly registry: RegistryLandingView;
  readonly settings: SettingsLandingView;
  readonly specials: SpecialsLandingView;
  readonly approval: GeneratedJsonObject;
}

/** Immutable snapshot of default stored parameters (projection modules). */
/**
 * Defaults for the parameter store.
 * agentDetail uses a lightweight stub so the shared store does not pull the
 * full pack agent catalog into every BoundScreenHome client graph (perf).
 */
export const SCREEN_PARAMETER_DEFAULTS: ScreenParameterMap = Object.freeze({
  dashboard: LOCAL_DASHBOARD_LANDING,
  activity: LOCAL_ACTIVITY_LANDING,
  agentDetail: AGENT_DETAIL_PARAMETER_STUB,
  apiPortal: LOCAL_API_PORTAL_LANDING,
  audit: LOCAL_AUDIT_LANDING,
  blueprints: LOCAL_BLUEPRINTS_LANDING,
  canvas: LOCAL_CANVAS_LANDING,
  collaboration: LOCAL_COLLABORATION_LANDING,
  composer: LOCAL_COMPOSER_LANDING,
  costs: LOCAL_COSTS_LANDING,
  eval: LOCAL_EVAL_LANDING,
  knowledge: LOCAL_KNOWLEDGE_LANDING,
  login: LOCAL_LOGIN_LANDING,
  mobile: LOCAL_MOBILE_LANDING,
  monitoring: LOCAL_MONITORING_LANDING,
  notifications: LOCAL_NOTIFICATIONS_LANDING,
  onboarding: LOCAL_ONBOARDING_LANDING,
  orgChart: ORG_CHART_PAYLOAD,
  agentWorkflow: AGENT_WORKFLOW_PAYLOAD,
  profile: LOCAL_PROFILE_LANDING,
  registry: LOCAL_REGISTRY_LANDING,
  settings: LOCAL_SETTINGS_LANDING,
  specials: LOCAL_SPECIALS_LANDING,
  approval: LOCAL_APPROVAL_PROJECTION,
});

type MutableScreenParameters = {
  -readonly [K in keyof ScreenParameterMap]: ScreenParameterMap[K];
};

let store: MutableScreenParameters = cloneDefaults();
const listeners = new Set<() => void>();

function cloneDefaults(): MutableScreenParameters {
  return { ...SCREEN_PARAMETER_DEFAULTS };
}

function notify(): void {
  for (const listener of listeners) listener();
}

/** Read current stored parameters for one screen (never invents a second source). */
export function getScreenParameters<K extends ScreenParameterKey>(
  key: K,
): ScreenParameterMap[K] {
  return store[key];
}

/** Replace one screen's parameters (e.g. after authorized REST projection load). */
export function setScreenParameters<K extends ScreenParameterKey>(
  key: K,
  value: ScreenParameterMap[K],
): void {
  store = { ...store, [key]: value };
  notify();
}

/**
 * Shallow-merge top-level fields into stored parameters.
 * Nested arrays/objects must be replaced wholesale by the caller.
 */
export function updateScreenParameters<K extends ScreenParameterKey>(
  key: K,
  patch: Partial<ScreenParameterMap[K]>,
): ScreenParameterMap[K] {
  const next = { ...store[key], ...patch } as ScreenParameterMap[K];
  setScreenParameters(key, next);
  return next;
}

/** Reset one screen or the entire store back to projection-module defaults. */
export function resetScreenParameters(key?: ScreenParameterKey): void {
  if (key === undefined) {
    store = cloneDefaults();
    notify();
    return;
  }
  setScreenParameters(key, SCREEN_PARAMETER_DEFAULTS[key]);
}

/** Snapshot of all keys (for diagnostics / tests). */
export function listScreenParameterKeys(): readonly ScreenParameterKey[] {
  return Object.keys(SCREEN_PARAMETER_DEFAULTS) as ScreenParameterKey[];
}

/** Subscribe to any parameter change (used by React bindings). */
export function subscribeScreenParameters(listener: () => void): () => void {
  listeners.add(listener);
  return (): void => {
    listeners.delete(listener);
  };
}
