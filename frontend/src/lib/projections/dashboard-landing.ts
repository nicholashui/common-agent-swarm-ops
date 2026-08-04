/**
 * Dashboard landing types + default shell labels.
 * Live fleet data is built by `dashboard-live.ts` (Host GET /api/v1/swarms + pack catalog).
 * Do not reintroduce fabricated success rates / fake swarm rows in this file.
 */

import type { ScreenLabels } from "./screen-labels";

export type DashboardStatusTone =
  | "running"
  | "live"
  | "success"
  | "complete"
  | "paused"
  | "self_refining"
  | "error"
  | "failed";

export interface DashboardStatCard {
  readonly id: string;
  readonly label: string;
  readonly value: string;
  readonly detail: string;
  readonly trend: string;
  readonly tone: "indigo" | "green" | "violet" | "amber";
  readonly sparkline: readonly number[];
  readonly href?: string;
}

export interface DashboardQuickAction {
  readonly id: string;
  readonly label: string;
  readonly description: string;
  readonly href: string;
  readonly primary?: boolean;
}

export interface DashboardRunningSwarm {
  readonly id: string;
  readonly name: string;
  readonly pattern: string;
  readonly status: DashboardStatusTone;
  readonly statusLabel: string;
  readonly progressLabel: string;
  readonly progressPercent: number;
  readonly elapsed: string;
  readonly costRate: string;
  readonly commonsOnLatest: string;
  readonly canvasHref: string;
}

export interface DashboardRecentRun {
  readonly id: string;
  readonly time: string;
  readonly swarm: string;
  readonly pattern: string;
  readonly commons: string;
  readonly status: DashboardStatusTone;
  readonly statusLabel: string;
  readonly duration: string;
  readonly cost: string;
  readonly actionLabel: string;
  readonly actionHref: string;
}

export interface DashboardImpactInsight {
  readonly id: string;
  readonly title: string;
  readonly body: string;
  readonly tone: "opportunity" | "positive";
  readonly badge?: string;
  readonly primaryActionLabel: string;
  readonly primaryActionHref: string;
  readonly secondaryActionLabel: string;
  readonly secondaryActionHref: string;
  readonly tertiaryActionLabel?: string;
  readonly tertiaryActionHref?: string;
}

export interface DashboardControlPlaneHealth {
  readonly apiHealthLabel: string;
  readonly apiHealthTone: "healthy" | "degraded" | "stale";
  readonly delayedEventWarning: string;
  readonly backlogCount: string;
  readonly backlogDetail: string;
  readonly approvalExpiryAlert: string;
  readonly sseLabel: string;
  readonly sseDetail: string;
  readonly correlationId: string;
  readonly affectedSummary: string;
  readonly affectedHref: string;
}

export interface DashboardPinnedItem {
  readonly id: string;
  readonly name: string;
  readonly kindLabel: string;
  readonly kindTone: "common" | "pattern" | "swarm";
  readonly href: string;
}

export interface DashboardLandingView {
  readonly title: string;
  readonly description: string;
  readonly eyebrow: string;
  readonly commonHealthSectionTitle: string;
  readonly quickActionsSectionTitle: string;
  readonly freshnessLabel: string;
  readonly asOf: string;
  readonly stale: boolean;
  readonly commonHealth: readonly DashboardStatCard[];
  readonly quickActions: readonly DashboardQuickAction[];
  readonly fleetSectionTitle: string;
  readonly runningSwarms: readonly DashboardRunningSwarm[];
  readonly recentRuns: readonly DashboardRecentRun[];
  readonly insightsIntro: string;
  readonly insights: readonly DashboardImpactInsight[];
  readonly controlPlane: DashboardControlPlaneHealth;
  readonly pinned: readonly DashboardPinnedItem[];
  readonly footerNote: string;
  readonly labels: ScreenLabels;
}

/** Label shell only — BoundDashboardHome replaces fleet cards via buildLiveDashboardView. */
export const LOCAL_DASHBOARD_LANDING: DashboardLandingView = {
  title: "Common Health & Fleet Ops",
  description:
    "Live Host drafts and pack catalog. No fabricated success rates or costs.",
  eyebrow: "DASHBOARD",
  commonHealthSectionTitle: "Common Health",
  quickActionsSectionTitle: "Quick Actions",
  freshnessLabel: "Loading Host fleet…",
  asOf: "pending",
  stale: false,
  labels: {
    runningNow: "Host drafts",
    openCanvas: "Open execute",
    emptyFleet:
      "No Host swarm drafts yet. Plan → Accept AI, or Add to Swarm from Registry.",
    startFromPatterns: "Open Plan →",
    recentActivity: "Recent Host drafts",
    viewAll: "Registry →",
    colTime: "Updated",
    colSwarmPattern: "Swarm · State",
    colCommons: "Members",
    colStatus: "Status",
    colAction: "Action",
    insightsTitle: "Common Impact Insights",
    controlPlaneTitle: "Control-Plane Health & Freshness",
    apiHealthLabel: "Host / Swarm list",
    delayedEventLabel: "Event model",
    backlogLabel: "Draft count",
    approvalLabel: "Approvals",
    sseLabel: "Transport",
    asOfPrefix: "as_of",
    affectedLabel: "Fleet summary",
    viewAffected: "Open Registry →",
    pinnedTitle: "Recent drafts",
    pause: "Pause",
    viewCanvas: "View Execute",
    progressMetaTemplate: "{progress} · updated {elapsed} · {costRate}",
  },
  commonHealth: [],
  quickActions: [
    {
      id: "registry",
      label: "Explore Common Registry Hub",
      description: "Closed-world video & specials agents  →",
      href: "/registry",
      primary: true,
    },
    {
      id: "compose",
      label: "Plan a multi-agent work",
      description: "AI-pick crew · materialize draft  →",
      href: "/composer",
    },
    {
      id: "activity",
      label: "Open Activity",
      description: "Ops history when Host projects it  →",
      href: "/activity",
    },
  ],
  fleetSectionTitle: "Your Swarms Fleet Ops",
  runningSwarms: [],
  recentRuns: [],
  insightsIntro:
    "Aggregate insights appear when Host Ops/eval projections authorize them.",
  insights: [],
  controlPlane: {
    apiHealthLabel: "Checking…",
    apiHealthTone: "stale",
    delayedEventWarning: "SSE not used for this snapshot",
    backlogCount: "0",
    backlogDetail: "Host drafts listed",
    approvalExpiryAlert: "No approval projection on this view",
    sseLabel: "REST snapshot",
    sseDetail: "Awaiting GET /api/v1/swarms",
    correlationId: "corr pending",
    affectedSummary: "Loading…",
    affectedHref: "/registry",
  },
  pinned: [],
  footerNote:
    "Fleet from Host GET /api/v1/swarms when BoundDashboardHome loads · process-local drafts.",
};
