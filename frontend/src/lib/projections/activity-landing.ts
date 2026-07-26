/**
 * Local Activity & Ops Intelligence fixture for ui_06_activity.md / .svg.
 * Presentation-only until generated activity projections and live WS connect.
 */

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
  title: "Activity & Ops Intelligence",
  description:
    "Filterable fleet history with common-version impact, board/table/timeline views, and rollout intelligence.",
  workspaceLabel: "Trading Lab",
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
  boardColumns: [
    {
      id: "ingestion",
      title: "Data Ingestion",
      patternLabel: "Parallel Pattern v1.4",
      stats: "42 runs · 96% · 1.2s avg · $2.1",
      healthTone: "healthy",
      cards: [
        {
          id: "c1",
          agentName: "CommonDataFetcher",
          versionLabel: "Common v2.1",
          status: "success",
          statusLabel: "Success",
          meta: "2m ago · 1.2s · tok 612 · $0.02",
          teaser: "Graph rev r-18 · checkpoint ck-91",
          actions: ["Replay latest", "View in Canvas"],
          linked: true,
        },
        {
          id: "c2",
          agentName: "CommonCleaner",
          versionLabel: "Common v2.0",
          status: "running",
          statusLabel: "Running",
          meta: "streaming… tok 340",
          teaser: "Lifecycle: running · retry 0",
          actions: ["View in Canvas"],
          linked: true,
        },
        {
          id: "c3",
          agentName: "CommonNormalizer",
          versionLabel: "Common v1.9",
          status: "success",
          statusLabel: "Success",
          meta: "14m ago · 2.4s · tok 890",
          teaser: "Pinned version · redacted metrics",
          actions: ["Update common", "Replay latest"],
          linked: true,
        },
      ],
    },
    {
      id: "analysis",
      title: "Analysis + Verification",
      patternLabel: "Verification Loop v1.2",
      stats: "38 runs · 89% · 3.8s avg · $3.4",
      healthTone: "watch",
      cards: [
        {
          id: "c4",
          agentName: "CommonSentiment",
          versionLabel: "Common v1.9",
          status: "error",
          statusLabel: "Error",
          meta: "timeout · retry exhausted",
          teaser: "Gate wait: missing approval · severity major",
          actions: ["Replay latest", "Create proposal"],
          linked: true,
        },
        {
          id: "c5",
          agentName: "CommonPredictor",
          versionLabel: "Common v2.0",
          status: "success",
          statusLabel: "Success",
          meta: "6m ago · 3.1s · tok 640",
          teaser: "Artifact QC: pass · provenance retained",
          actions: ["View in Canvas"],
          linked: true,
        },
        {
          id: "c6",
          agentName: "VerifierNode",
          versionLabel: "Common v3.0",
          status: "self_refine",
          statusLabel: "iter 3/5",
          meta: "verified · groundedness 0.94",
          teaser: "Contributed insight to commons ✓",
          actions: ["Open Detail", "Contribute signals"],
          linked: true,
        },
      ],
    },
    {
      id: "synthesis",
      title: "Synthesis + Report",
      patternLabel: "Map-Reduce v1.1",
      stats: "40 runs · 93% · 2.2s avg · $2.9",
      healthTone: "healthy",
      cards: [
        {
          id: "c7",
          agentName: "SynthesisAgent",
          versionLabel: "Common v2.2",
          status: "success",
          statusLabel: "Success",
          meta: "3m ago · 2.0s · tok 520",
          teaser: "L1/L2 quality pass · L3 not required",
          actions: ["View in Canvas"],
          linked: true,
        },
        {
          id: "c8",
          agentName: "CustomReportAgent",
          versionLabel: "Fork of Common v2.3",
          status: "success",
          statusLabel: "Success",
          meta: "10m ago · 3.4s · tok 1.2k",
          teaser: "Custom fork · contribute back?",
          actions: ["Contribute fork back?"],
          custom: true,
        },
      ],
    },
  ],
  tableRows: [
    {
      id: "t1",
      timestamp: "04:12",
      swarm: "TradingResearch α",
      business: "Trading Lab",
      pattern: "Parallel + Verify v1.4",
      agent: "CommonDataFetcher",
      version: "Common v2.1",
      status: "success",
      statusLabel: "Success",
      duration: "1.2s",
      tokens: "612",
      cost: "$0.02",
      graphRevision: "r-18",
      lifecycle: "complete",
      checkpoint: "ck-91",
    },
    {
      id: "t2",
      timestamp: "03:58",
      swarm: "ContentPipeline β",
      business: "Content Studio",
      pattern: "Verification Loop v1.2",
      agent: "CommonSentiment",
      version: "Common v1.9",
      status: "error",
      statusLabel: "Error",
      duration: "18s",
      tokens: "702",
      cost: "$0.03",
      error: "timeout · retry exhausted",
      graphRevision: "r-22",
      lifecycle: "failed",
      checkpoint: "ck-77",
    },
    {
      id: "t3",
      timestamp: "03:44",
      swarm: "TradingResearch α",
      business: "Trading Lab",
      pattern: "Verification Loop v1.2",
      agent: "VerifierNode",
      version: "Common v3.0",
      status: "self_refine",
      statusLabel: "Self-refine",
      duration: "41s",
      tokens: "1.1k",
      cost: "$0.05",
      graphRevision: "r-19",
      lifecycle: "self_refine",
      checkpoint: "ck-88",
    },
    {
      id: "t4",
      timestamp: "02:10",
      swarm: "DSE Tutor Fleet",
      business: "DSE DeepTutor",
      pattern: "Map-Reduce v1.1",
      agent: "CustomReportAgent",
      version: "Fork v2.3",
      status: "success",
      statusLabel: "Success",
      duration: "3.4s",
      tokens: "1.2k",
      cost: "$0.04",
      graphRevision: "r-11",
      lifecycle: "complete",
      checkpoint: "ck-55",
    },
  ],
  timelineLanes: [
    {
      id: "lane-ingest",
      label: "Data Ingestion",
      bars: [
        {
          id: "b1",
          label: "Fetcher v2.1",
          startPct: 4,
          widthPct: 22,
          tone: "success",
        },
        {
          id: "b2",
          label: "Cleaner v2.0",
          startPct: 28,
          widthPct: 30,
          tone: "running",
        },
      ],
    },
    {
      id: "lane-verify",
      label: "Analysis + Verification",
      bars: [
        {
          id: "b3",
          label: "Sentiment v1.9",
          startPct: 18,
          widthPct: 20,
          tone: "error",
        },
        {
          id: "b4",
          label: "Verifier 3/5",
          startPct: 42,
          widthPct: 28,
          tone: "self_refine",
        },
      ],
    },
    {
      id: "lane-synth",
      label: "Synthesis + Report",
      bars: [
        {
          id: "b5",
          label: "Synthesis v2.2",
          startPct: 55,
          widthPct: 18,
          tone: "success",
        },
        {
          id: "b6",
          label: "Report fork",
          startPct: 76,
          widthPct: 16,
          tone: "success",
        },
      ],
    },
  ],
  kpis: [
    { id: "runs", label: "Total runs", value: "120", detail: "filtered period" },
    { id: "success", label: "Success", value: "93%", detail: "↑ 1.4%" },
    { id: "cost", label: "Cost", value: "$8.4", detail: "redacted band" },
  ],
  chartNote: "Runs over time · success % trend",
  rolloutCards: [
    {
      id: "r1",
      title: "CommonVerifier v1.8 · +12% pass rate",
      body: "Safe to rollout to your 12 swarms on v1.6?",
      tone: "opportunity",
      actions: ["Approve", "A/B", "Details"],
    },
    {
      id: "r2",
      title: "Anomaly · CommonReportAgent",
      body: "Error rate ↑ in 3 swarms after v2.1 rollout.",
      tone: "anomaly",
      actions: ["Rollback", "Investigate traces"],
    },
  ],
  collectiveImpact:
    "Your runs helped improve 4 common agents; ~$412 token savings realized this period.",
  bulkActions: ["Bulk replay w/ latest", "Create improvement proposal"],
  freshnessLabel: "as_of 04:12Z · corr b7f2c9d0",
  footerNote:
    "Board · Table · Timeline views share URL-synced filters · virtualized for 100k+ rows · redacted event summaries only. Actions use server-determined eligibility · preserve immutable version provenance.",
};
