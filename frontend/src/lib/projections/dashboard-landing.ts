/**
 * Local dashboard landing fixture for ui_02_dashboard.
 * Values are presentation-only until generated /api/v1 projections replace them.
 */

export interface DashboardStatCard {
  readonly id: string;
  readonly label: string;
  readonly value: string;
  readonly detail: string;
  readonly trend: string;
  readonly tone: "indigo" | "green" | "violet" | "amber";
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
  readonly status: "running" | "paused" | "success" | "error";
  readonly progressLabel: string;
  readonly elapsed: string;
  readonly costRate: string;
  readonly commonsOnLatest: string;
  readonly canvasHref: string;
}

export interface DashboardRecentRun {
  readonly id: string;
  readonly time: string;
  readonly swarm: string;
  readonly commons: string;
  readonly status: "running" | "paused" | "success" | "error";
  readonly duration: string;
  readonly cost: string;
}

export interface DashboardImpactInsight {
  readonly id: string;
  readonly title: string;
  readonly body: string;
  readonly tone: "opportunity" | "positive";
  readonly primaryActionLabel: string;
  readonly secondaryActionLabel: string;
}

export interface DashboardLandingView {
  readonly title: string;
  readonly description: string;
  readonly freshnessLabel: string;
  readonly asOf: string;
  readonly stale: boolean;
  readonly commonHealth: readonly DashboardStatCard[];
  readonly quickActions: readonly DashboardQuickAction[];
  readonly runningSwarms: readonly DashboardRunningSwarm[];
  readonly recentRuns: readonly DashboardRecentRun[];
  readonly insights: readonly DashboardImpactInsight[];
  readonly footerNote: string;
}

export const LOCAL_DASHBOARD_LANDING: DashboardLandingView = {
  title: "Common Health & Fleet Ops",
  description:
    "Operating on a living, collectively improving commons foundation.",
  freshnessLabel: "Local preview · projection not connected",
  asOf: "local",
  stale: false,
  commonHealth: [
    {
      id: "agents-active",
      label: "Common Agents Active",
      value: "87",
      detail: "versions · 142 swarms",
      trend: "↑ 4 new improvements this week",
      tone: "indigo",
    },
    {
      id: "success-rate",
      label: "Global Success Rate",
      value: "91.4%",
      detail: "↑ 1.2%",
      trend: "Rolling 7-day aggregate",
      tone: "green",
    },
    {
      id: "proposals",
      label: "Pending Improvement Proposals",
      value: "3",
      detail: "2 from meta-critic · 1 awaiting merge",
      trend: "Review in Registry",
      tone: "violet",
    },
    {
      id: "fleet-health",
      label: "Your Fleet Health",
      value: "94%",
      detail: "12 swarms on latest commons",
      trend: "Avg success of active swarms",
      tone: "green",
    },
    {
      id: "savings",
      label: "Est. Monthly Savings",
      value: "$128",
      detail: "from token efficiency gains",
      trend: "Commons reuse vs custom forks",
      tone: "amber",
    },
  ],
  quickActions: [
    {
      id: "registry",
      label: "Explore Common Registry Hub",
      description: "Discover versioned agents, provenance, and aggregate metrics.",
      href: "/registry",
      primary: true,
    },
    {
      id: "compose",
      label: "Compose New Swarm",
      description: "Start from common patterns with guided composition.",
      href: "/composer",
    },
    {
      id: "proposals",
      label: "Review Improvement Proposals",
      description: "Inspect pending commons upgrades and evidence.",
      href: "/evaluations",
    },
    {
      id: "activity",
      label: "Open Activity",
      description: "Task lifecycle, recovery, and correlation timeline.",
      href: "/activity",
    },
  ],
  runningSwarms: [
    {
      id: "run-market",
      name: "Daily market brief",
      pattern: "Parallel + verification v1.4",
      status: "running",
      progressLabel: "3/5 agents on latest common",
      elapsed: "12m 08s",
      costRate: "$0.04/min",
      commonsOnLatest: "6 linked",
      canvasHref: "/canvas",
    },
    {
      id: "run-research",
      name: "Research digest",
      pattern: "Supervisor + specialists v2.0",
      status: "running",
      progressLabel: "5/8 agents on latest common",
      elapsed: "4m 41s",
      costRate: "$0.06/min",
      commonsOnLatest: "8 linked",
      canvasHref: "/canvas",
    },
  ],
  recentRuns: [
    {
      id: "recent-1",
      time: "local · 08:12",
      swarm: "Daily market brief",
      commons: "6 commons",
      status: "success",
      duration: "4m 12s",
      cost: "$0.38",
    },
    {
      id: "recent-2",
      time: "local · 07:55",
      swarm: "Research digest",
      commons: "8 commons",
      status: "running",
      duration: "12m 08s",
      cost: "$0.71",
    },
    {
      id: "recent-3",
      time: "local · 07:20",
      swarm: "DSE lesson planner",
      commons: "4 commons",
      status: "paused",
      duration: "2m 47s",
      cost: "$0.19",
    },
  ],
  insights: [
    {
      id: "insight-1",
      title: "Commons upgrade opportunity",
      body: "Updating CommonReportAgent v2.1 → v2.2 would improve 19 of your active swarms (+15% latency, -$47/mo est.). Local preview only until rollout projection is connected.",
      tone: "opportunity",
      primaryActionLabel: "Open approvals",
      secondaryActionLabel: "View evaluations",
    },
    {
      id: "insight-2",
      title: "Collective impact",
      body: "Your usage data helped improve 4 common agents this month — view collective impact in the registry once live projections are available.",
      tone: "positive",
      primaryActionLabel: "Open registry",
      secondaryActionLabel: "Open activity",
    },
  ],
  footerNote:
    "Last synced commons: local preview · Contribute to the commons by running & verifying swarms.",
};
