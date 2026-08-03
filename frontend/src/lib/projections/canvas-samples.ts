/**
 * Loadable Canvas sample instances (orchestration board demos).
 * Mirrors Compose ACC samples — full crew graphs for the workflow diagram.
 */

import type {
  CanvasGraphNode,
  CanvasLandingView,
  CanvasNodeKind,
  CanvasNodeStatus,
} from "./canvas-landing";

export type CanvasSampleKind = "happy_path" | "lean" | "hierarchy" | "demo";

export type CanvasSample = {
  readonly id: string;
  readonly label: string;
  readonly summary: string;
  readonly kind: CanvasSampleKind;
  readonly swarmName: string;
  readonly patternBadge: string;
  readonly sourceLabel: string;
  readonly nodes: readonly CanvasGraphNode[];
};

function node(
  id: string,
  label: string,
  kind: CanvasNodeKind,
  opts: {
    readonly status?: CanvasNodeStatus;
    readonly statusLabel?: string;
    readonly metrics?: string;
    readonly versionLabel?: string;
  } = {},
): CanvasGraphNode {
  return {
    id,
    label,
    kind,
    versionLabel: opts.versionLabel ?? "Common · sample",
    status: opts.status ?? "idle",
    statusLabel: opts.statusLabel ?? "Draft member",
    metrics: opts.metrics ?? "Sample instance · not run",
    linked: true,
  };
}

/** Canonical loadable Canvas samples (workflow diagram + crew list). */
export const CANVAS_SAMPLES: readonly CanvasSample[] = [
  {
    id: "canvas-wuxia",
    label: "YouTube wuxia short",
    summary: "Hierarchical + verify · Compose-style crew",
    kind: "happy_path",
    swarmName: "AI · Hierarchical + Verify · Wuxia Short",
    patternBadge: "Sample · hierarchical-supervisor + verify",
    sourceLabel: "Sample instance · video crew",
    nodes: [
      node("orch", "video.orchestrator", "supervisor", {
        versionLabel: "meta",
        statusLabel: "Idle",
      }),
      node("plan", "video.planner", "common", {
        versionLabel: "meta",
        statusLabel: "Idle",
      }),
      node("writer", "video.screenwriter", "common"),
      node("dir", "video.director", "common"),
      node("edit", "video.editor", "common"),
      node("judge", "video.judge", "verifier", {
        statusLabel: "Gate",
        metrics: "GATE · sample",
      }),
    ],
  },
  {
    id: "canvas-market",
    label: "Market intel + verify",
    summary: "Parallel research branches · final critic",
    kind: "happy_path",
    swarmName: "AI · Parallel Research · Market Intel",
    patternBadge: "Sample · parallel-research + verify",
    sourceLabel: "Sample instance · research crew",
    nodes: [
      node("orch", "video.orchestrator", "supervisor", { versionLabel: "meta" }),
      node("plan", "video.planner", "common", { versionLabel: "meta" }),
      node("data", "video.webresearch", "common", {
        status: "complete",
        statusLabel: "Done",
      }),
      node("trend", "video.trendintelligence", "common", {
        status: "queued",
        statusLabel: "Queued",
      }),
      node("synth", "video.copywriter", "common"),
      node("ver", "video.judge", "verifier", { statusLabel: "Gate" }),
    ],
  },
  {
    id: "canvas-social-lean",
    label: "Social under budget",
    summary: "Lean crew · cost-efficient",
    kind: "lean",
    swarmName: "AI · Lean Social · Budget",
    patternBadge: "Sample · minimal crew",
    sourceLabel: "Sample instance · lean",
    nodes: [
      node("orch", "video.orchestrator", "supervisor", { versionLabel: "meta" }),
      node("edit", "video.editor", "common"),
      node("a11y", "video.accessibility", "common"),
      node("judge", "video.judge", "verifier", { statusLabel: "Gate" }),
    ],
  },
  {
    id: "canvas-feature",
    label: "Full feature hierarchy",
    summary: "Orch → Planner → departments + QC",
    kind: "hierarchy",
    swarmName: "AI · Feature Film Hierarchy",
    patternBadge: "Sample · hierarchical-supervisor",
    sourceLabel: "Sample instance · full hierarchy",
    nodes: [
      node("orch", "video.orchestrator", "supervisor", { versionLabel: "meta" }),
      node("plan", "video.planner", "common", { versionLabel: "meta" }),
      node("writer", "video.screenwriter", "common"),
      node("dir", "video.director", "common"),
      node("cine", "video.cinematographer", "common"),
      node("edit", "video.editor", "common"),
      node("sound", "video.sounddesign", "common"),
      node("judge", "video.judge", "verifier", { statusLabel: "Gate" }),
    ],
  },
  {
    id: "canvas-trading-demo",
    label: "Trading parallel demo",
    summary: "Classic ui_04 BIG ROW demo crew",
    kind: "demo",
    swarmName: "TradingResearch α",
    patternBadge: "Sample · Parallel Indep. + Verify v1.4",
    sourceLabel: "Sample instance · trading demo",
    nodes: [
      node("supervisor", "Supervisor", "supervisor", {
        status: "running",
        statusLabel: "Running",
        versionLabel: "Common supervisor",
      }),
      node("data", "DataFetcher", "common", {
        status: "complete",
        statusLabel: "Done",
        versionLabel: "Common v2.1",
      }),
      node("sentiment", "Sentiment", "common", {
        status: "running",
        statusLabel: "Run",
        versionLabel: "Common v1.9",
      }),
      node("predictor", "Predictor", "common", {
        status: "queued",
        statusLabel: "Idle",
        versionLabel: "Common v2.0",
      }),
      node("verifier", "VerifierNode", "verifier", {
        status: "self_refine",
        statusLabel: "Live",
        versionLabel: "Common v3.0",
      }),
    ],
  },
];

/**
 * Apply a sample onto a base canvas view (keeps labels, palette, inspector, validation).
 */
export function applyCanvasSample(
  base: CanvasLandingView,
  sample: CanvasSample,
): CanvasLandingView {
  const edges = sample.nodes.slice(0, -1).map((n, i) => ({
    id: `sample-e-${n.id}-${sample.nodes[i + 1]!.id}`,
    from: n.id,
    to: sample.nodes[i + 1]!.id,
    label: "handoff",
    style: "solid" as const,
  }));
  return {
    ...base,
    viewMode: "inspect",
    swarmName: sample.swarmName,
    patternBadge: sample.patternBadge,
    commonsSummary: `${sample.nodes.length} members · sample instance · workflow diagram`,
    instanceId: `sample-${sample.id}`,
    instanceStatus: "draft",
    instanceRevision: 0,
    sourceLabel: sample.sourceLabel,
    fromCompose: false,
    nodes: sample.nodes,
    groups: [],
    edges,
    runBar: {
      ...base.runBar,
      activeNodesLabel: `${sample.nodes.length} agents (sample)`,
      progressLabel: "Sample · not run · inspect workflow",
      progressPercent: 0,
      statusLabel: "draft",
      costSoFar: "—",
      elapsed: "—",
    },
    footerNote: `Sample “${sample.label}” loaded on Canvas. Local/demo only · not a Host draft · production fail-closed.`,
  };
}
