/**
 * Local canvas landing fixture for ui_04_canvas.md / ui_04_canvas.svg.
 * Presentation-only until live graph projections and run SSE connect.
 */

export type CanvasViewMode = "design" | "run" | "compare";
export type CanvasPaletteTab = "common" | "custom" | "patterns";
export type CanvasNodeKind = "common" | "custom" | "verifier";
export type CanvasNodeStatus = "idle" | "running" | "done" | "error";

export interface CanvasPaletteItem {
  readonly id: string;
  readonly name: string;
  readonly meta: string;
  readonly kind: CanvasNodeKind | "fork";
  readonly tab: CanvasPaletteTab;
}

export interface CanvasGraphNode {
  readonly id: string;
  readonly label: string;
  readonly kind: CanvasNodeKind;
  readonly versionLabel: string;
  readonly status: CanvasNodeStatus;
  readonly statusLabel: string;
  readonly metrics: string;
  readonly linked: boolean;
  readonly groupId?: string;
  readonly progressPercent?: number;
}

export interface CanvasGraphGroup {
  readonly id: string;
  readonly title: string;
  readonly versionLabel: string;
  readonly nodeIds: readonly string[];
}

export interface CanvasLandingView {
  readonly swarmName: string;
  readonly patternBadge: string;
  readonly commonsSummary: string;
  readonly viewMode: CanvasViewMode;
  readonly palette: readonly CanvasPaletteItem[];
  readonly groups: readonly CanvasGraphGroup[];
  readonly nodes: readonly CanvasGraphNode[];
  readonly edges: readonly {
    readonly id: string;
    readonly from: string;
    readonly to: string;
    readonly label: string;
    readonly style: "solid" | "dashed" | "dotted";
  }[];
  readonly validation: readonly { readonly category: string; readonly result: string }[];
  readonly runBar?: {
    readonly progressLabel: string;
    readonly costSoFar: string;
    readonly statusLabel: string;
  };
  readonly footerNote: string;
}

export const LOCAL_CANVAS_LANDING: CanvasLandingView = {
  swarmName: "TradingResearch α",
  patternBadge: "Based on: Parallel Indep. + Verify v1.4",
  commonsSummary: "12/14 on latest common · 2 forks",
  viewMode: "design",
  palette: [
    {
      id: "p-data",
      name: "DataFetcher",
      meta: "Common v2.1 · 94% · drag →",
      kind: "common",
      tab: "common",
    },
    {
      id: "p-sent",
      name: "SentimentAgent",
      meta: "Common v1.9 · 91%",
      kind: "common",
      tab: "common",
    },
    {
      id: "p-pred",
      name: "MarketPredictor",
      meta: "Common v2.0 · 92%",
      kind: "common",
      tab: "common",
    },
    {
      id: "p-ver",
      name: "VerifierNode",
      meta: "Common v3.0 · 97%",
      kind: "verifier",
      tab: "common",
    },
    {
      id: "p-custom",
      name: "CustomReportAgent",
      meta: "Fork of Common v2.3",
      kind: "fork",
      tab: "custom",
    },
    {
      id: "p-pattern",
      name: "Parallel + Verify macro",
      meta: "Pattern v1.4 · expand group",
      kind: "common",
      tab: "patterns",
    },
  ],
  groups: [
    {
      id: "big-row",
      title: "⊞ Parallel Data & Analysis (BIG ROW)",
      versionLabel: "v1.4",
      nodeIds: ["data", "sentiment", "predictor"],
    },
  ],
  nodes: [
    {
      id: "data",
      label: "DataFetcher",
      kind: "common",
      versionLabel: "Common v2.1",
      status: "done",
      statusLabel: "Done",
      metrics: "tok 612 · $0.02 · 1.2s",
      linked: true,
      groupId: "big-row",
    },
    {
      id: "sentiment",
      label: "Sentiment",
      kind: "common",
      versionLabel: "Common v1.9",
      status: "running",
      statusLabel: "Run",
      metrics: "tok 847 · streaming…",
      linked: true,
      groupId: "big-row",
      progressPercent: 59,
    },
    {
      id: "predictor",
      label: "MarketPredictor",
      kind: "common",
      versionLabel: "Common v2.0",
      status: "idle",
      statusLabel: "Idle",
      metrics: "waiting for upstream",
      linked: true,
      groupId: "big-row",
    },
    {
      id: "verifier",
      label: "VerifierNode",
      kind: "verifier",
      versionLabel: "Common v3.0",
      status: "idle",
      statusLabel: "Idle",
      metrics: "iteration 0/3",
      linked: true,
    },
    {
      id: "report",
      label: "CustomReportAgent",
      kind: "custom",
      versionLabel: "Fork of Common v2.3",
      status: "idle",
      statusLabel: "Idle",
      metrics: "awaiting verified synthesis",
      linked: false,
    },
  ],
  edges: [
    {
      id: "e1",
      from: "data",
      to: "sentiment",
      label: "Data flow",
      style: "solid",
    },
    {
      id: "e2",
      from: "sentiment",
      to: "predictor",
      label: "State flow",
      style: "dashed",
    },
    {
      id: "e3",
      from: "predictor",
      to: "verifier",
      label: "Evidence",
      style: "solid",
    },
    {
      id: "e4",
      from: "verifier",
      to: "predictor",
      label: "Iteration",
      style: "dotted",
    },
    {
      id: "e5",
      from: "verifier",
      to: "report",
      label: "Approved synthesis",
      style: "solid",
    },
  ],
  validation: [
    { category: "version", result: "passed" },
    { category: "schema", result: "passed" },
    { category: "tool_policy", result: "passed" },
    { category: "budget", result: "passed" },
    { category: "verification", result: "passed" },
    { category: "rollback", result: "available" },
    { category: "approval", result: "not_required" },
  ],
  runBar: {
    progressLabel: "Local preview · not running",
    costSoFar: "$0.00",
    statusLabel: "Design mode",
  },
  footerNote:
    "Local preview canvas · nodes show redacted provenance only · Run/SSE require authorized graph commands.",
};
