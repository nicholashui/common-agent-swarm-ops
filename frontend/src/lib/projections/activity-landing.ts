/**
 * Local Activity & Ops Intelligence fixture for ui_06_activity.md / .svg.
 * Presentation-only until generated activity projections and live WS connect.
 */

import type { ScreenLabels } from "./screen-labels";

export type ActivityViewMode = "board" | "table" | "timeline";

export type ActivityCardStatus =
  | "success"
  | "running"
  | "error"
  | "self_refine"
  | "paused";

export interface ActivityExecutionCard {
  readonly id: string;
  readonly agentName: string;
  readonly versionLabel: string;
  readonly status: ActivityCardStatus;
  readonly statusLabel: string;
  readonly meta: string;
  readonly teaser?: string;
  readonly actions: readonly string[];
  readonly linked?: boolean;
  readonly custom?: boolean;
}

export interface ActivityBoardColumn {
  readonly id: string;
  readonly title: string;
  readonly patternLabel: string;
  readonly stats: string;
  readonly healthTone: "healthy" | "watch" | "degraded";
  readonly cards: readonly ActivityExecutionCard[];
}

export interface ActivityTableRow {
  readonly id: string;
  readonly timestamp: string;
  readonly swarm: string;
  readonly business: string;
  readonly pattern: string;
  readonly agent: string;
  readonly version: string;
  readonly status: ActivityCardStatus;
  readonly statusLabel: string;
  readonly duration: string;
  readonly tokens: string;
  readonly cost: string;
  readonly error?: string;
  readonly graphRevision: string;
  readonly lifecycle: string;
  readonly checkpoint: string;
}

export interface ActivityTimelineLane {
  readonly id: string;
  readonly label: string;
  readonly bars: readonly {
    readonly id: string;
    readonly label: string;
    readonly startPct: number;
    readonly widthPct: number;
    readonly tone: ActivityCardStatus;
  }[];
}

export interface ActivityInsightKpi {
  readonly id: string;
  readonly label: string;
  readonly value: string;
  readonly detail?: string;
}

export interface ActivityRolloutCard {
  readonly id: string;
  readonly title: string;
  readonly body: string;
  readonly tone: "opportunity" | "anomaly";
  readonly actions: readonly string[];
}

export interface ActivityLandingView {
  readonly labels: ScreenLabels;
  readonly eyebrow: string;
  readonly title: string;
  readonly description: string;
  readonly workspaceLabel: string;
  readonly dateRangeLabel: string;
  readonly searchPlaceholder: string;
  readonly filterChips: readonly string[];
  readonly toggleFilters: readonly { readonly id: string; readonly label: string }[];
  readonly boardColumns: readonly ActivityBoardColumn[];
  readonly tableRows: readonly ActivityTableRow[];
  readonly timelineLanes: readonly ActivityTimelineLane[];
  readonly kpis: readonly ActivityInsightKpi[];
  readonly chartNote: string;
  readonly rolloutCards: readonly ActivityRolloutCard[];
  readonly collectiveImpact: string;
  readonly bulkActions: readonly string[];
  readonly freshnessLabel: string;
  readonly footerNote: string;
}

export const LOCAL_ACTIVITY_LANDING: ActivityLandingView = {
  labels: {
    "search_activity": "Search activity",
    "ops_intelligence": "Ops Intelligence",
    "rollout_opportunities_anomalies": "Rollout Opportunities & Anomalies",
    "collective_improvement_impact": "Collective Improvement Impact",
    "no_activity_yet_start_a_swarm_from_common_patter": "No activity yet — start a swarm from Common Patterns.",
    "no_activity_matches_the_current_filters": "No activity matches the current filters.",
    "select": "Select",
    "timestamp": "Timestamp",
    "swarm_business": "Swarm · Business",
    "pattern": "Pattern",
    "agent_version": "Agent · Version",
    "status": "Status",
    "duration_tokens_cost": "Duration / Tokens / Cost",
    "lifecycle_checkpoint": "Lifecycle · Checkpoint",
    "actions": "Actions",
    "activity_and_ops_intelligence": "Activity and ops intelligence",
    "view_mode": "View mode",
    "activity_filters": "Activity filters",
    "bulk_actions": "Bulk actions",
    "ops_intelligence_2": "Ops intelligence",
    "activity_board": "Activity board",
    "activity_table": "Activity table",
    "activity_timeline": "Activity timeline",
  },
  eyebrow: "ACTIVITY",
  title: "Activity & Ops Intelligence",
  description:
    "Filterable fleet history with common-version impact, board/table/timeline views, and rollout intelligence.",
  workspaceLabel: "Video Studio",
  dateRangeLabel: "Last 7 days",
  searchPlaceholder: "Search run ID, agent, error, output…",
  filterChips: [
    "Common Agent / Version",
    "Common Pattern",
    "Status",
    "Lifecycle / retry",
    "Gate state",
    "Critique severity",
  ],
  toggleFilters: [
    { id: "outdated", label: "Only outdated common versions" },
    { id: "contributed", label: "Contributed to commons?" },
  ],
  boardColumns: [],
  tableRows: [],
  timelineLanes: [],
  kpis: [
    { id: "events", label: "Events (page)", value: "0", detail: "Load Host feed" },
    { id: "insight-count", label: "Insight count", value: "0", detail: "—" },
    { id: "categories", label: "Categories", value: "0", detail: "—" },
  ],
  chartNote: "Awaiting Host GET /api/v1/activity",
  rolloutCards: [],
  collectiveImpact:
    "Collective impact appears when Host projects it — not fabricated here.",
  bulkActions: ["Bulk replay w/ latest", "Create improvement proposal"],
  freshnessLabel: "pending Host feed",
  footerNote:
    "Activity binds to GET /api/v1/activity via BoundActivityHome · process-local façade until Host persists.",
};
