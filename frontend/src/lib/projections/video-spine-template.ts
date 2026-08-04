/**
 * Host product spine template for Agent Workflow UI.
 * DNA id matches Host façade: wf_video_spine_v1 (design DNA, production_ready false).
 * Not from the generated scale/archetype export — single source for product dry-run spine.
 */

import type { AgentWorkflowTemplate } from "./agent-workflow.generated";

/** Same id as Host `SPINE_WORKFLOW_ID` / design DNA. */
export const VIDEO_SPINE_WORKFLOW_ID = "wf_video_spine_v1";

/** Template id used in Agent Workflow selector / deep links. */
export const VIDEO_SPINE_TEMPLATE_ID = "video.host.wf_video_spine_v1";

/** Fail-closed honesty copy (Epic E / G6). */
export const STUB_RUN_HONESTY = "stub run · not production media";

const SPINE_AGENTS: readonly {
  readonly id: string;
  readonly name: string;
  readonly role: string;
}[] = [
  { id: "video.orchestrator", name: "Orchestrator", role: "Orchestration" },
  { id: "video.planner", name: "Planner", role: "Intent & Planning" },
  { id: "video.director", name: "Director", role: "Creative" },
  { id: "video.screenwriter", name: "Screenwriter", role: "Creative" },
  { id: "video.webresearch", name: "Web Research", role: "Research" },
  { id: "video.aiqaconsistency", name: "AI QA Consistency", role: "Verification" },
  { id: "video.producer", name: "Producer", role: "Package gate" },
];

/**
 * Closed-world product spine template (design DNA order).
 * production_ready remains false; package is always human-gated.
 */
export function buildVideoSpineWorkflowTemplate(): AgentWorkflowTemplate {
  return {
    id: VIDEO_SPINE_TEMPLATE_ID,
    packId: "video",
    kind: "dna",
    scaleId: null,
    label: "Host product spine · Video Orchestration",
    background:
      "Minimal runnable video spine used by Plan materialize → Execute dry-run. " +
      "Stub tools only until Host production activation.",
    whenToUse:
      "After Plan materializes a production brief; inspect handoffs before package approval.",
    whoShouldUse: "Operators running Host product façade spine stubs (not full 6-phase production).",
    howToUse:
      "Open Execute on a draft with spine, advance stub steps, approve package on human gate. " +
      STUB_RUN_HONESTY +
      ".",
    source: "business/video/design/workflows/wf_video_spine_v1.dna.json",
    archetypes: [],
    dnaWorkflowId: VIDEO_SPINE_WORKFLOW_ID,
    agentIds: SPINE_AGENTS.map((a) => a.id),
    agents: SPINE_AGENTS.map((a) => ({
      id: a.id,
      name: a.name,
      role: a.role,
      categoryId: "spine",
      status: "registered",
      href: `/registry/agents/${encodeURIComponent(a.id)}`,
    })),
    steps: [
      {
        id: "orchestrate",
        label: "Orchestrate",
        agentId: "video.orchestrator",
        phase: "control",
        humanGate: false,
        next: ["plan"],
      },
      {
        id: "plan",
        label: "Plan / parse brief",
        agentId: "video.planner",
        phase: "intent_planning",
        humanGate: false,
        next: ["direct"],
      },
      {
        id: "direct",
        label: "Creative direction",
        agentId: "video.director",
        phase: "creative",
        humanGate: false,
        next: ["screenwrite"],
      },
      {
        id: "screenwrite",
        label: "Script",
        agentId: "video.screenwriter",
        phase: "creative",
        humanGate: false,
        next: ["research"],
      },
      {
        id: "research",
        label: "Research",
        agentId: "video.webresearch",
        phase: "research",
        humanGate: false,
        next: ["media_gen"],
      },
      {
        id: "media_gen",
        label: "Media stub",
        agentId: "video.director",
        phase: "execution",
        humanGate: false,
        next: ["qc"],
      },
      {
        id: "qc",
        label: "QC",
        agentId: "video.aiqaconsistency",
        phase: "verification",
        humanGate: false,
        next: ["package"],
      },
      {
        id: "package",
        label: "Package",
        agentId: "video.producer",
        phase: "critical_gate",
        humanGate: true,
        next: [],
      },
    ],
    callEdges: [
      {
        fromId: "video.orchestrator",
        toId: "video.planner",
        kind: "handoff",
        label: "orchestrate→plan",
      },
      {
        fromId: "video.planner",
        toId: "video.director",
        kind: "handoff",
        label: "plan→direct",
      },
      {
        fromId: "video.director",
        toId: "video.screenwriter",
        kind: "handoff",
        label: "direct→script",
      },
      {
        fromId: "video.screenwriter",
        toId: "video.webresearch",
        kind: "handoff",
        label: "script→research",
      },
      {
        fromId: "video.webresearch",
        toId: "video.director",
        kind: "handoff",
        label: "research→media",
      },
      {
        fromId: "video.director",
        toId: "video.aiqaconsistency",
        kind: "handoff",
        label: "media→qc",
      },
      {
        fromId: "video.aiqaconsistency",
        toId: "video.producer",
        kind: "gate",
        label: "qc→package (HITL)",
      },
    ],
    phaseOrder: [
      "control",
      "intent_planning",
      "creative",
      "research",
      "execution",
      "verification",
      "critical_gate",
    ],
  };
}

export function isVideoSpineTemplateId(id: string | null | undefined): boolean {
  if (!id) return false;
  return (
    id === VIDEO_SPINE_TEMPLATE_ID ||
    id === VIDEO_SPINE_WORKFLOW_ID ||
    id.includes("wf_video_spine_v1")
  );
}

/** Agent Workflow deep link for the Host product spine template. */
export function agentWorkflowSpineHref(): string {
  return `/registry/agent-workflow?template=${encodeURIComponent(VIDEO_SPINE_TEMPLATE_ID)}`;
}
