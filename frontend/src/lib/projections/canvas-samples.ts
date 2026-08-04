/**
 * Loadable Execute sample instances — video pack (and real specials) agents only.
 * No trading / COBOL / fictional non-pack agents.
 */

import type {
  CanvasGraphNode,
  CanvasLandingView,
  CanvasNodeKind,
  CanvasNodeStatus,
} from "./canvas-landing";

export type CanvasSampleKind = "happy_path" | "lean" | "hierarchy" | "research";

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
    versionLabel: opts.versionLabel ?? "video · sample",
    status: opts.status ?? "idle",
    statusLabel: opts.statusLabel ?? "Draft member",
    metrics: opts.metrics ?? "Sample instance · not run",
    linked: true,
  };
}

/**
 * Samples use agent_id-shaped labels that exist under business/video/agents
 * (e.g. video.orchestrator, video.judge).
 */
export const CANVAS_SAMPLES: readonly CanvasSample[] = [
  {
    id: "canvas-wuxia",
    label: "YouTube wuxia short",
    summary: "Hierarchical + verify · video pack",
    kind: "happy_path",
    swarmName: "AI · Hierarchical + Verify · Wuxia Short",
    patternBadge: "Sample · hierarchical-supervisor + verify",
    sourceLabel: "Sample · video pack only",
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
      node("a11y", "video.accessibility", "common"),
      node("judge", "video.judge", "verifier", {
        statusLabel: "Gate",
        metrics: "GATE · sample",
      }),
    ],
  },
  {
    id: "canvas-trend-research",
    label: "Trend research → script",
    summary: "webresearch · trend · writer · judge",
    kind: "research",
    swarmName: "AI · Video Research → Script",
    patternBadge: "Sample · research + verify",
    sourceLabel: "Sample · video research agents",
    nodes: [
      node("orch", "video.orchestrator", "supervisor", { versionLabel: "meta" }),
      node("plan", "video.planner", "common", { versionLabel: "meta" }),
      node("web", "video.webresearch", "common", {
        status: "complete",
        statusLabel: "Done",
      }),
      node("trend", "video.trendintelligence", "common", {
        status: "queued",
        statusLabel: "Queued",
      }),
      node("copy", "video.copywriter", "common"),
      node("writer", "video.screenwriter", "common"),
      node("ver", "video.judge", "verifier", { statusLabel: "Gate" }),
    ],
  },
  {
    id: "canvas-social-lean",
    label: "Social under budget",
    summary: "Lean video crew · cost-efficient",
    kind: "lean",
    swarmName: "AI · Lean Social · Budget",
    patternBadge: "Sample · minimal video crew",
    sourceLabel: "Sample · lean video pack",
    nodes: [
      node("orch", "video.orchestrator", "supervisor", { versionLabel: "meta" }),
      node("edit", "video.editor", "common"),
      node("a11y", "video.accessibility", "common"),
      node("sound", "video.sounddesign", "common"),
      node("judge", "video.judge", "verifier", { statusLabel: "Gate" }),
    ],
  },
  {
    id: "canvas-feature",
    label: "Full feature hierarchy",
    summary: "Orch → Planner → video departments + QC",
    kind: "hierarchy",
    swarmName: "AI · Feature Film Hierarchy",
    patternBadge: "Sample · hierarchical-supervisor",
    sourceLabel: "Sample · full video hierarchy",
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
    id: "canvas-brand-spot",
    label: "Brand spot + compliance",
    summary: "Brand / creative · editor · compliance · judge",
    kind: "happy_path",
    swarmName: "AI · Brand Spot · Compliance",
    patternBadge: "Sample · brand film + gates",
    sourceLabel: "Sample · brand video pack",
    nodes: [
      node("orch", "video.orchestrator", "supervisor", { versionLabel: "meta" }),
      node("brand", "video.brandstrategist", "common"),
      node("cd", "video.creativedirector", "common"),
      node("dir", "video.director", "common"),
      node("edit", "video.editor", "common"),
      node("music", "video.musicsupervisor", "common"),
      node("comp", "video.compliance", "verifier", {
        statusLabel: "Gate",
        metrics: "GATE · compliance",
      }),
      node("judge", "video.judge", "verifier", { statusLabel: "Gate" }),
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
    commonsSummary: `${sample.nodes.length} members · video sample · workflow diagram`,
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
    footerNote: `Sample “${sample.label}” (video pack agents only). Local/demo · not a Host draft · production fail-closed.`,
  };
}
