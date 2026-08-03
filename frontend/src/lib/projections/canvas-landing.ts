/**
 * Local canvas landing fixture for ui_04_canvas.md / ui_04_canvas.svg.
 * Presentation-only until live graph projections and run SSE connect.
 */

import type { ScreenLabels } from "./screen-labels";

/** Design = palette tools · Inspect = workflow board (default) · Run = execution posture */
export type CanvasViewMode = "design" | "inspect" | "run" | "compare";
export type CanvasPaletteTab = "common" | "custom" | "patterns";
export type CanvasNodeKind =
  | "common"
  | "custom"
  | "verifier"
  | "supervisor"
  | "router";
export type CanvasNodeStatus =
  | "idle"
  | "queued"
  | "running"
  | "self_refine"
  | "waiting_for_critique"
  | "blocked"
  | "failed"
  | "complete"
  | "done";

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
  readonly iterationLabel?: string;
  readonly blockedReason?: string;
  readonly aggregateEval?: {
    readonly runs: string;
    readonly success: string;
    readonly avgTokens: string;
  };
  readonly improvementHistory?: readonly {
    readonly title: string;
    readonly detail: string;
    readonly impact: string;
  }[];
  readonly liveInspector?: readonly string[];
}

export interface CanvasGraphGroup {
  readonly id: string;
  readonly title: string;
  readonly versionLabel?: string;
  readonly tone: "parallel" | "verification";
  readonly nodeIds: readonly string[];
  readonly cycleLabel?: string;
}

export interface CanvasInspectorTab {
  readonly id: "task" | "artifacts" | "critique" | "quality" | "provenance";
  readonly label: string;
  readonly lines: readonly string[];
}

export interface CanvasLandingView {
  readonly labels: ScreenLabels;
  readonly eyebrow: string;
  readonly settingsEyebrow: string;
  readonly selectedEyebrowTemplate: string;
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
  readonly validation: readonly {
    readonly category: string;
    readonly result: string;
  }[];
  readonly runBar: {
    readonly progressLabel: string;
    readonly progressPercent: number;
    readonly costSoFar: string;
    readonly elapsed: string;
    readonly statusLabel: string;
    readonly activeNodesLabel: string;
  };
  readonly inspectorTabs: readonly CanvasInspectorTab[];
  readonly copilotActions: readonly string[];
  readonly footerNote: string;
  /** Host draft id when live instance (Compose materialize). */
  readonly instanceId?: string;
  readonly instanceStatus?: string;
  readonly instanceRevision?: number;
  /** e.g. Compose ACC · AI-pick */
  readonly sourceLabel?: string;
  readonly fromCompose?: boolean;
}

export const LOCAL_CANVAS_LANDING: CanvasLandingView = {
  labels: {
    swarm_canvas: "Swarm canvas · orchestration board",
    swarm_name: "Swarm name",
    view_mode: "View mode",
    auto_layout_is_local_only_feedback: "Auto layout is local-only feedback.",
    export_requires_an_authorized_export_action: "Export requires an authorized export action.",
    a_b_test_requires_an_authorized_rollout_contract: "A/B Test requires an authorized rollout contract.",
    node_palette: "Node palette",
    palette_tabs: "Palette tabs",
    ai_suggest_node: "AI Suggest Node",
    ai_suggest_node_2: "AI Suggest Node",
    search_common_agents: "Search common agents",
    search_common_agents_2: "Search common agents",
    swarm_graph_canvas: "Swarm graph canvas",
    graph_relationship_semantics: "Graph relationship semantics",
    edges: "Edges",
    cancel_requires_an_authorized_cancel_action: "Cancel requires an authorized cancel action.",
    streaming_logs: "Streaming logs",
    canvas_inspector: "Canvas inspector",
    aggregate_eval_all_swarms: "Aggregate eval (all swarms)",
    runs: "Runs",
    success: "Success",
    avg_tok: "Avg tok",
    improvement_history: "Improvement history",
    pin_version_requires_an_authorized_pin_action: "Pin version requires an authorized pin action.",
    live_inspector: "Live Inspector",
    inspector_tabs: "Inspector tabs",
    returned_graph_validation: "Returned graph validation",
    returned_validation: "Returned validation",
    registry_linked: "Registry-linked",
  },
  eyebrow: "SWARM CANVAS · ORCHESTRATION",
  settingsEyebrow: "INSTANCE SETTINGS",
  selectedEyebrowTemplate: "SELECTED · {kind}",
  swarmName: "TradingResearch α",
  patternBadge: "Based on: Parallel Indep. + Verify v1.4",
  commonsSummary: "12/14 on latest common · 2 forks",
  viewMode: "inspect",
  instanceId: "demo-landing",
  instanceStatus: "draft",
  instanceRevision: 0,
  sourceLabel: "Demo landing · open Compose instance for live draft",
  fromCompose: false,
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
      tone: "parallel",
      nodeIds: ["data", "sentiment", "predictor"],
    },
    {
      id: "synth-verify",
      title: "Synthesis + Verification",
      tone: "verification",
      nodeIds: ["synthesis", "verifier"],
      cycleLabel: "cycle ↺",
    },
  ],
  nodes: [
    {
      id: "data",
      label: "DataFetcher",
      kind: "common",
      versionLabel: "Common v2.1",
      status: "complete",
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
      label: "Predictor",
      kind: "common",
      versionLabel: "Common v2.0",
      status: "queued",
      statusLabel: "Idle",
      metrics: "eval 0.92 · queued",
      linked: true,
      groupId: "big-row",
    },
    {
      id: "supervisor",
      label: "Supervisor",
      kind: "supervisor",
      versionLabel: "Common supervisor",
      status: "running",
      statusLabel: "Running",
      metrics: "↓ Worker A · ↓ Worker B",
      linked: true,
    },
    {
      id: "synthesis",
      label: "SynthesisAgent",
      kind: "common",
      versionLabel: "Common v2.2",
      status: "waiting_for_critique",
      statusLabel: "Waiting",
      metrics: "awaiting verifier",
      linked: true,
      groupId: "synth-verify",
    },
    {
      id: "verifier",
      label: "VerifierNode",
      kind: "verifier",
      versionLabel: "Common v3.0",
      status: "self_refine",
      statusLabel: "Live",
      metrics: "iterating with feedback…",
      linked: true,
      groupId: "synth-verify",
      iterationLabel: "↻ 3/5",
      progressPercent: 60,
      aggregateEval: {
        runs: "31.2k",
        success: "97%",
        avgTokens: "640",
      },
      improvementHistory: [
        {
          title: "v3.0 · meta-critic rationale",
          detail: "Added structured verification step",
          impact: "+12% pass rate · 1.8k runs",
        },
      ],
      liveInspector: [
        "iter 3/5 · verifier feedback",
        '"groundedness below 0.9,',
        ' re-check source citations"',
        "tool: retrieve() 220ms",
        "token burn: 42/s",
        "as_of just now · seq 4421",
      ],
    },
    {
      id: "report",
      label: "CustomReportAgent",
      kind: "custom",
      versionLabel: "Fork of Common v2.3",
      status: "complete",
      statusLabel: "Complete",
      metrics: "tok 1.2k",
      linked: false,
    },
    {
      id: "router",
      label: "Dynamic Router",
      kind: "router",
      versionLabel: "LLM-decided",
      status: "idle",
      statusLabel: "Idle",
      metrics: "→ Research  → Synthesis  → Escalate",
      linked: true,
    },
  ],
  edges: [
    {
      id: "e1",
      from: "big-row",
      to: "synth-verify",
      label: "Data flow",
      style: "solid",
    },
    {
      id: "e2",
      from: "synthesis",
      to: "verifier",
      label: "State flow",
      style: "dashed",
    },
    {
      id: "e3",
      from: "verifier",
      to: "synthesis",
      label: "Iteration",
      style: "dotted",
    },
    {
      id: "e4",
      from: "supervisor",
      to: "big-row",
      label: "Delegate",
      style: "solid",
    },
    {
      id: "e5",
      from: "router",
      to: "report",
      label: "Route",
      style: "dashed",
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
    progressLabel: "Running · 2 nodes active",
    progressPercent: 60,
    costSoFar: "$1.68",
    elapsed: "12m",
    statusLabel: "Local preview run bar",
    activeNodesLabel: "Sentiment + Verifier",
  },
  inspectorTabs: [
    {
      id: "task",
      label: "Task",
      lines: [
        "Lifecycle: self_refine",
        "Iteration: 3/5",
        "Retry: 0",
        "Checkpoint: local-preview",
      ],
    },
    {
      id: "artifacts",
      label: "Artifacts",
      lines: [
        "Parent lineage: evidence bundle",
        "QC: pending verifier",
        "Rights/consent: not applicable (preview)",
      ],
    },
    {
      id: "critique",
      label: "Critique",
      lines: [
        "Severity: major",
        "Evidence: groundedness below 0.9",
        "Suggested action: re-check citations",
      ],
    },
    {
      id: "quality",
      label: "Quality",
      lines: [
        "L1: passed",
        "L2: in progress",
        "L3: not run",
        "Human approval: not required",
      ],
    },
    {
      id: "provenance",
      label: "Provenance",
      lines: [
        "Pinned version: Common v3.0",
        "Registry-linked",
        "Audit ref: local-preview",
      ],
    },
  ],
  copilotActions: [
    "Optimize tokens",
    "Add verification where missing",
    "Propose as new Common Pattern",
    "Suggest dynamic router",
  ],
  footerNote:
    "Local preview canvas · nodes show redacted provenance only · Run/SSE require authorized graph commands.",
};
