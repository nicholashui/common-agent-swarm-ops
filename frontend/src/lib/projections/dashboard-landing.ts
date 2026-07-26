/**
 * Local dashboard landing fixture for ui_02_dashboard.md / ui_02_dashboard.svg.
 * Presentation-only until generated /api/v1 projections replace it.
 * All chrome strings live in `labels` — components must not hardcode copy.
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

export const LOCAL_DASHBOARD_LANDING: DashboardLandingView = {
  title: "Common Health & Fleet Ops",
  description:
    "Operating on a living, collectively improving commons foundation.",
  eyebrow: "DASHBOARD",
  commonHealthSectionTitle: "Common Health",
  quickActionsSectionTitle: "Quick Actions",
  freshnessLabel: "Local preview · SSE not connected",
  asOf: "local",
  stale: false,
  labels: {
    runningNow: "Running Now",
    openCanvas: "Open canvas",
    emptyFleet: "No swarms running. Start one from Common Patterns.",
    startFromPatterns: "Start from Common Patterns →",
    recentActivity: "Recent Activity",
    viewAll: "View all →",
    colTime: "Time",
    colSwarmPattern: "Swarm · Pattern",
    colCommons: "Commons",
    colStatus: "Status",
    colAction: "Action",
    insightsTitle: "Common Impact Insights",
    controlPlaneTitle: "Control-Plane Health & Freshness",
    apiHealthLabel: "API / Projection Health",
    delayedEventLabel: "Delayed-event warning",
    backlogLabel: "Queue / Run Backlog",
    approvalLabel: "Approval expiry alert",
    sseLabel: "SSE Transport",
    asOfPrefix: "as_of",
    affectedLabel: "Affected swarms",
    viewAffected: "View affected →",
    pinnedTitle: "Pinned / Favorites",
    pause: "Pause",
    viewCanvas: "View Canvas",
    progressMetaTemplate: "{progress} · elapsed {elapsed} · {costRate}",
  },
  commonHealth: [
    {
      id: "agents-active",
      label: "Common Agents Active",
      value: "87",
      detail: "versions · 142 swarms",
      trend: "↑ 4 new improvements this week",
      tone: "indigo",
      sparkline: [40, 48, 45, 58, 54, 68, 62, 78, 74, 87],
    },
    {
      id: "success-rate",
      label: "Global Success Rate",
      value: "91.4%",
      detail: "↑ 1.2%",
      trend: "Rolling 7-day aggregate",
      tone: "green",
      sparkline: [82, 84, 83, 86, 85, 88, 87, 90, 89, 91],
    },
    {
      id: "proposals",
      label: "Pending Improvement Proposals",
      value: "3",
      detail: "2 from meta-critic · 1 awaiting merge",
      trend: "Review →",
      tone: "violet",
      sparkline: [1, 1, 2, 2, 2, 3, 3, 3, 3, 3],
      href: "/registry",
    },
    {
      id: "fleet-health",
      label: "Your Fleet Health",
      value: "94%",
      detail: "12 swarms on latest commons",
      trend: "Avg success of active swarms",
      tone: "green",
      sparkline: [88, 89, 90, 90, 91, 92, 92, 93, 94, 94],
    },
    {
      id: "savings",
      label: "Est. Monthly Savings",
      value: "$412",
      detail: "from commons token efficiency",
      trend: "Commons reuse vs custom forks",
      tone: "amber",
      sparkline: [180, 210, 240, 260, 290, 320, 350, 370, 390, 412],
    },
  ],
  quickActions: [
    {
      id: "registry",
      label: "Explore Common Registry Hub",
      description: "Discover versioned agents & patterns  →",
      href: "/registry",
      primary: true,
    },
    {
      id: "compose",
      label: "Compose from Common Patterns",
      description: "Parallel · verification loop · router  →",
      href: "/composer",
    },
    {
      id: "proposals",
      label: "Review Improvement Proposals",
      description: "3 pending for commons you use  →",
      href: "/evaluations",
    },
  ],
  fleetSectionTitle: "Your Swarms Fleet Ops",
  runningSwarms: [
    {
      id: "run-trading",
      name: "TradingResearch α",
      pattern: "Parallel Indep. + Verify v1.4",
      status: "running",
      statusLabel: "Running",
      progressLabel: "8/8 on latest common",
      progressPercent: 68,
      elapsed: "12m",
      costRate: "$0.14/min",
      commonsOnLatest: "8/8 latest",
      canvasHref: "/canvas",
    },
    {
      id: "run-content",
      name: "ContentPipeline β",
      pattern: "Hierarchical Supervisor v2.0",
      status: "live",
      statusLabel: "Live",
      progressLabel: "5/5 on latest common",
      progressPercent: 41,
      elapsed: "4m",
      costRate: "$0.06/min",
      commonsOnLatest: "5/5 latest",
      canvasHref: "/canvas",
    },
  ],
  recentRuns: [
    {
      id: "recent-1",
      time: "2m",
      swarm: "TradingResearch α",
      pattern: "Parallel + Verify v1.4",
      commons: "7 · v2.1",
      status: "complete",
      statusLabel: "Complete",
      duration: "4m 12s",
      cost: "$0.38",
      actionLabel: "Replay ↻",
      actionHref: "/activity",
    },
    {
      id: "recent-2",
      time: "8m",
      swarm: "ContentPipeline β",
      pattern: "Hierarchical v2.0",
      commons: "5 · v1.8",
      status: "self_refining",
      statusLabel: "Self-Refining",
      duration: "12m 08s",
      cost: "$0.71",
      actionLabel: "Replay ↻",
      actionHref: "/activity",
    },
    {
      id: "recent-3",
      time: "1h",
      swarm: "DSE Tutor Fleet",
      pattern: "Verification Loop v1.2",
      commons: "4 · v1.2",
      status: "complete",
      statusLabel: "Complete",
      duration: "2m 47s",
      cost: "$0.19",
      actionLabel: "Replay ↻",
      actionHref: "/activity",
    },
    {
      id: "recent-4",
      time: "3h",
      swarm: "LegacyModernizer",
      pattern: "Map-Reduce + Verifier v1.1",
      commons: "3 · v2.0",
      status: "failed",
      statusLabel: "Failed",
      duration: "9m 02s",
      cost: "$0.52",
      actionLabel: "Debug →",
      actionHref: "/operations",
    },
  ],
  insightsIntro:
    "AI-generated from Ops service & meta-critic aggregate analysis.",
  insights: [
    {
      id: "insight-1",
      title: "Rollout Opportunity",
      body: "Updating CommonReportAgent v2.1 → v2.2 improves 19 active swarms by +15% latency, saves ~$47/mo.",
      tone: "opportunity",
      badge: "19 swarms",
      primaryActionLabel: "Approve Rollout",
      primaryActionHref: "/operations",
      secondaryActionLabel: "A/B Test First",
      secondaryActionHref: "/operations",
      tertiaryActionLabel: "View Diff",
      tertiaryActionHref: "/evaluations",
    },
    {
      id: "insight-2",
      title: "Collective Intelligence",
      body: "Your usage data helped improve 4 common agents this month across the ecosystem.",
      tone: "positive",
      primaryActionLabel: "View collective impact →",
      primaryActionHref: "/registry",
      secondaryActionLabel: "Open activity",
      secondaryActionHref: "/activity",
    },
  ],
  controlPlane: {
    apiHealthLabel: "Healthy",
    apiHealthTone: "healthy",
    delayedEventWarning: "0 · queue nominal",
    backlogCount: "14",
    backlogDetail: "queued runs",
    approvalExpiryAlert: "1 approval expires in 8m",
    sseLabel: "Local preview · not connected",
    sseDetail: "Last-Event-ID not validated · REST snapshot only",
    correlationId: "corr local-preview",
    affectedSummary: "3 swarms in degraded projection",
    affectedHref: "/operations",
  },
  pinned: [
    {
      id: "pin-1",
      name: "VerificationLoopAgent",
      kindLabel: "Common v3.0",
      kindTone: "common",
      href: "/registry",
    },
    {
      id: "pin-2",
      name: "Parallel Indep. v1.4",
      kindLabel: "Pattern",
      kindTone: "pattern",
      href: "/blueprints",
    },
    {
      id: "pin-3",
      name: "TradingResearch α",
      kindLabel: "Swarm",
      kindTone: "swarm",
      href: "/canvas",
    },
  ],
  footerNote:
    "Last synced commons: local preview · Contribute to the commons by running & verifying swarms · Redacted projections only — no host names or secrets shown.",
};
