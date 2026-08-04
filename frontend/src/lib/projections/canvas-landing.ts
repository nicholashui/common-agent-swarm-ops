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
  /** e.g. Plan ACC · AI-pick */
  readonly sourceLabel?: string;
  readonly fromCompose?: boolean;
}

export const LOCAL_CANVAS_LANDING: CanvasLandingView = {
  labels: {
    swarm_canvas: "Execute · orchestration board",
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
    canvas_inspector: "Execute inspector",
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
  eyebrow: "EXECUTE · ORCHESTRATION",
  settingsEyebrow: "INSTANCE SETTINGS",
  selectedEyebrowTemplate: "SELECTED · {kind}",
  swarmName: "Wuxia Short",
  patternBadge: "Based on: Hierarchical + Verify",
  commonsSummary: "6/7 video pack · 1 fork",
  viewMode: "inspect",
  instanceId: "demo-landing",
  instanceStatus: "draft",
  instanceRevision: 0,
  sourceLabel: "Demo landing · open Plan instance for live draft",
  fromCompose: false,
  palette: [
    {
      id: "p-web",
      name: "video.webresearch",
      meta: "video pack · research · drag →",
      kind: "common",
      tab: "common",
    },
    {
      id: "p-trend",
      name: "video.trendintelligence",
      meta: "video pack · hooks",
      kind: "common",
      tab: "common",
    },
    {
      id: "p-writer",
      name: "video.screenwriter",
      meta: "video pack · script",
      kind: "common",
      tab: "common",
    },
    {
      id: "p-judge",
      name: "video.judge",
      meta: "video pack · QC gate",
      kind: "verifier",
      tab: "common",
    },
    {
      id: "p-custom",
      name: "video.copywriter",
      meta: "Fork · social cut",
      kind: "fork",
      tab: "custom",
    },
    {
      id: "p-pattern",
      name: "Parallel research + judge",
      meta: "Pattern · expand group",
      kind: "common",
      tab: "patterns",
    },
  ],
  groups: [
    {
      id: "research-row",
      title: "Parallel research",
      versionLabel: "video pack",
      tone: "parallel",
      nodeIds: ["web", "trend", "copy"],
    },
    {
      id: "script-verify",
      title: "Script + quality gate",
      tone: "verification",
      nodeIds: ["writer", "judge"],
      cycleLabel: "revise ↺",
    },
  ],
  nodes: [
    {
      id: "web",
      label: "video.webresearch",
      kind: "common",
      versionLabel: "video pack",
      status: "complete",
      statusLabel: "Done",
      metrics: "tok 612 · $0.02 · 1.2s",
      linked: true,
      groupId: "research-row",
    },
    {
      id: "trend",
      label: "video.trendintelligence",
      kind: "common",
      versionLabel: "video pack",
      status: "running",
      statusLabel: "Run",
      metrics: "tok 847 · streaming…",
      linked: true,
      groupId: "research-row",
      progressPercent: 59,
    },
    {
      id: "copy",
      label: "video.copywriter",
      kind: "common",
      versionLabel: "video pack",
      status: "queued",
      statusLabel: "Idle",
      metrics: "queued",
      linked: true,
      groupId: "research-row",
    },
    {
      id: "supervisor",
      label: "video.orchestrator",
      kind: "supervisor",
      versionLabel: "meta",
      status: "running",
      statusLabel: "Running",
      metrics: "↓ research · ↓ script",
      linked: true,
    },
    {
      id: "writer",
      label: "video.screenwriter",
      kind: "common",
      versionLabel: "video pack",
      status: "waiting_for_critique",
      statusLabel: "Waiting",
      metrics: "awaiting judge",
      linked: true,
      groupId: "script-verify",
    },
    {
      id: "judge",
      label: "video.judge",
      kind: "verifier",
      versionLabel: "video pack",
      status: "self_refine",
      statusLabel: "Live",
      metrics: "iterating with feedback…",
      linked: true,
      groupId: "script-verify",
      iterationLabel: "↻ 3/5",
      progressPercent: 60,
      aggregateEval: {
        runs: "1.2k",
        success: "94%",
        avgTokens: "640",
      },
      improvementHistory: [
        {
          title: "Hook strength rubric",
          detail: "Structured QC step for first 3 seconds",
          impact: "+12% pass rate · sample runs",
        },
      ],
      liveInspector: [
        "iter 3/5 · judge feedback",
        '"hook weak in first 3s,',
        ' tighten opening beat"',
        "tool: retrieve() 220ms",
        "token burn: 42/s",
        "as_of just now · seq 4421",
      ],
    },
    {
      id: "edit",
      label: "video.editor",
      kind: "custom",
      versionLabel: "Fork · cut package",
      status: "complete",
      statusLabel: "Complete",
      metrics: "tok 1.2k",
      linked: false,
    },
    {
      id: "router",
      label: "video.planner",
      kind: "router",
      versionLabel: "meta",
      status: "idle",
      statusLabel: "Idle",
      metrics: "→ research  → script  → edit",
      linked: true,
    },
  ],
  edges: [
    {
      id: "e1",
      from: "research-row",
      to: "script-verify",
      label: "Handoff",
      style: "solid",
    },
    {
      id: "e2",
      from: "writer",
      to: "judge",
      label: "QC",
      style: "dashed",
    },
    {
      id: "e3",
      from: "judge",
      to: "writer",
      label: "Revise",
      style: "dotted",
    },
    {
      id: "e4",
      from: "supervisor",
      to: "research-row",
      label: "Delegate",
      style: "solid",
    },
    {
      id: "e5",
      from: "router",
      to: "edit",
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
    activeNodesLabel: "Trend + Judge",
  },
  inspectorTabs: [
    {
      id: "task",
      label: "Task",
      lines: [
        "Lifecycle: refining",
        "Iteration: 3/5",
        "Retry: 0",
        "Checkpoint: local-preview",
      ],
    },
    {
      id: "artifacts",
      label: "Artifacts",
      lines: [
        "Parent lineage: script package",
        "QC: pending judge",
        "Rights/consent: not applicable (preview)",
      ],
    },
    {
      id: "critique",
      label: "Critique",
      lines: [
        "Severity: major",
        "Evidence: weak opening hook",
        "Suggested action: tighten first 3 seconds",
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
        "Pinned: video.judge",
        "Registry-linked",
        "Audit ref: local-preview",
      ],
    },
  ],
  copilotActions: [
    "Optimize tokens",
    "Add judge gate where missing",
    "Propose as reusable pattern",
    "Suggest planner route",
  ],
  footerNote:
    "Local preview canvas · nodes show redacted provenance only · Run/SSE require authorized graph commands.",
};
