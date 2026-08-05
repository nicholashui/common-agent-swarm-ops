/**
 * Local Common Agent detail fixture for ui_05_agent_detail.md / .svg.
 * Prefer pack-backed settings via buildAgentDetailView(agentId) from self-contained packs.
 */

import type { ScreenLabels } from "./screen-labels";
import { getPackAgent, type PackAgentRecord } from "./pack-agents.generated";

export type AgentDetailTabId =
  | "history"
  | "config"
  | "playground"
  | "knowledge"
  | "ops";

export interface AgentDetailStat {
  readonly id: string;
  readonly label: string;
  readonly value: string;
  readonly detail?: string;
}

export interface AgentDetailUsageRow {
  readonly id: string;
  readonly timestamp: string;
  readonly swarm: string;
  readonly pattern: string;
  readonly status: string;
  readonly statusTone: "success" | "running" | "error" | "self_refine";
  readonly duration: string;
  readonly tokens: string;
  readonly cost: string;
  readonly summary: string;
}

export interface AgentDetailVersion {
  readonly id: string;
  readonly label: string;
  readonly state: "past" | "current" | "proposal";
  readonly delta?: string;
}

export interface AgentDetailKnowledgeSource {
  readonly id: string;
  readonly name: string;
  readonly type: string;
  readonly status: string;
  readonly chunks: string;
  readonly added: string;
}

export interface AgentDetailLandingView {
  readonly labels: ScreenLabels;
  readonly eyebrow: string;
  readonly agentName: string;
  readonly versionBadge: string;
  readonly statusLabel: string;
  readonly velocityLabel: string;
  readonly headerStats: readonly AgentDetailStat[];
  readonly insightStrip: string;
  readonly yourUsageNote: string;
  readonly historyFilters: readonly string[];
  readonly usageRows: readonly AgentDetailUsageRow[];
  readonly paginationLabel: string;
  readonly versions: readonly AgentDetailVersion[];
  readonly currentVersionNote: string;
  readonly metaCriticNote: string;
  readonly evidenceNote: string;
  readonly configSummaries: readonly {
    readonly id: string;
    readonly title: string;
    readonly lines: readonly string[];
  }[];
  readonly playgroundMessages: readonly {
    readonly id: string;
    readonly role: "user" | "assistant" | "system";
    readonly text: string;
  }[];
  readonly evalScores: readonly { readonly metric: string; readonly score: string }[];
  readonly knowledgeStats: readonly AgentDetailStat[];
  readonly knowledgeSources: readonly AgentDetailKnowledgeSource[];
  readonly opsAlert: string;
  readonly opsWhereUsed: string;
  readonly opsMetrics: readonly AgentDetailStat[];
  readonly footerNote: string;
  /** Public path to SPEC.md for markdown rendering (e.g. /docs/agents/video.accessibility/SPEC.md). */
  readonly specDocPath?: string | null;
  /** Public path to README.md when present. */
  readonly readmeDocPath?: string | null;
  /** Structure-map fields (common-agent-structure layout, not SVG embed). */
  readonly structure?: {
    readonly role: string;
    readonly category: string;
    readonly folderPath: string;
    readonly promptReference: string;
    readonly rubricReference: string;
    readonly tools: readonly string[];
    readonly networkAccess: boolean;
    readonly productionActivationRequested: boolean;
    readonly critiqueIn: readonly string[];
    readonly critiqueOut: readonly string[];
    readonly hasSpec: boolean;
    readonly hasSources: boolean;
    readonly architecture: string;
  };
}

const AGENT_DETAIL_LABELS: ScreenLabels = {
  "timestamp": "Timestamp",
  "swarm_pattern": "Swarm · Pattern",
  "status": "Status",
  "duration_tokens_cost": "Duration / Tokens / Cost",
  "summary": "Summary",
  "action": "Action",
  "eval_harness": "Eval Harness",
  "live_metrics": "Live Metrics",
  "after_good_run": "After good run",
  "search_knowledge": "Search knowledge",
  "name": "Name",
  "type": "Type",
  "chunks": "Chunks",
  "added": "Added",
  "actions": "Actions",
  "where_used_this_exact_version": "Where used (this exact version)",
  "a_b_test_requires_an_authorized_rollout_contract": "A/B Test requires an authorized rollout contract.",
  "fork_to_custom_requires_an_authorized_fork_actio": "Fork to Custom requires an authorized fork action.",
  "playground_is_local_preview_only_until_authorize": "Playground is local-preview only until authorized.",
  "test_this_common_agent_with_a_prompt": "Test this common agent with a prompt…",
  "search_test_chunk_text_score_source": "Search test · chunk text, score, source…",
  "common_agent_detail": "Common agent detail",
  "quick_actions": "Quick actions",
  "agent_detail_tabs": "Agent detail tabs",
  "history_filters": "History filters",
  "cross_swarm_usage": "Cross-swarm usage",
  "playground_options": "Playground options",
  "playground_panels": "Playground panels",
};

function parseCritiqueEdges(raw: string): {
  readonly inputs: readonly string[];
  readonly outputs: readonly string[];
} {
  if (!raw?.trim()) return { inputs: [], outputs: [] };
  try {
    const parsed = JSON.parse(raw) as { inputs?: unknown; outputs?: unknown };
    return {
      inputs: Array.isArray(parsed.inputs) ? parsed.inputs.map(String) : [],
      outputs: Array.isArray(parsed.outputs) ? parsed.outputs.map(String) : [],
    };
  } catch {
    return { inputs: [], outputs: [] };
  }
}

/** Build agent detail projection from a pack self-contained agent record. */
export function buildAgentDetailView(
  agent: PackAgentRecord,
  agentId?: string,
): AgentDetailLandingView {
  const id = agentId ?? agent.id;
  const critique = parseCritiqueEdges(agent.critiqueCompat);
  return {
    labels: AGENT_DETAIL_LABELS,
    eyebrow: `${agent.pack.toUpperCase()} AGENT DETAIL`,
    agentName: agent.name,
    versionBadge: agent.versionLabel,
    statusLabel: agent.status,
    velocityLabel: agent.productionActivationRequested
      ? "activation requested (host gate required)"
      : "non-active · fail-closed",
    headerStats: [
      {
        id: "pack",
        label: "Pack",
        value: agent.pack,
        detail: agent.folderPath,
      },
      {
        id: "status",
        label: "Status",
        value: agent.status,
        detail: agent.networkAccess ? "network on" : "network off",
      },
      {
        id: "tools",
        label: "Allowed tools",
        value: String(agent.allowedTools.length),
        detail: agent.provider || "local",
      },
    ],
    insightStrip: agent.specExcerpt || agent.description,
    yourUsageNote: agent.specDocPath
      ? "Full SPEC rendered under Config / Spec →"
      : "Open full SPEC.md in pack folder →",
    historyFilters: ["Self-contained", "Config", "Provenance"],
    usageRows: [
      {
        id: "settings",
        timestamp: "settings",
        swarm: agent.folderPath,
        pattern: agent.pack,
        status: agent.status,
        statusTone: agent.status === "draft" ? "self_refine" : "success",
        duration: "—",
        tokens: agent.avgTokens,
        cost: "—",
        summary: agent.role || agent.description.slice(0, 160),
      },
    ],
    paginationLabel: `Agent id: ${id}`,
    versions: [
      {
        id: "current",
        label: agent.versionLabel,
        state: "current",
        delta: agent.hasSpecMd ? "SPEC.md present" : "SPEC.md missing",
      },
    ],
    currentVersionNote:
      `Self-contained folder: ${agent.folderPath}. `
      + `SPEC.md=${agent.hasSpecMd ? "yes" : "no"} · README=${agent.hasReadme ? "yes" : "no"} · sources=${agent.hasSources ? "yes" : "no"}.`,
    metaCriticNote:
      "Settings below are projected from pack agent_spec.json (read-only in browser).",
    evidenceNote:
      "Design provenance lives under agents/<id>/sources/. Production activation remains host-gated.",
    configSummaries: agent.configSummaries.map((section) => ({
      id: section.id,
      title: section.title,
      lines: [...section.lines],
    })),
    playgroundMessages: [
      {
        id: "sys",
        role: "system",
        text:
          "Playground is presentation-only. Runtime execution requires authorized host actions.",
      },
    ],
    evalScores: [
      { metric: "self-contained", score: agent.hasSpecMd && agent.hasSources ? "pass" : "gap" },
      { metric: "network_access", score: agent.networkAccess ? "on" : "off" },
      {
        metric: "production_activation_requested",
        score: agent.productionActivationRequested ? "yes" : "no",
      },
    ],
    knowledgeStats: [
      { id: "prompt", label: "Prompt ref", value: agent.promptReference || "—" },
      { id: "rubric", label: "Rubric ref", value: agent.rubricReference || "—" },
    ],
    knowledgeSources: [
      {
        id: "folder",
        name: agent.folderPath,
        type: "pack-folder",
        status: "local",
        chunks: agent.hasSpecMd ? "SPEC.md" : "—",
        added: "checked-in",
      },
    ],
    opsAlert: agent.productionActivationRequested
      ? "Activation requested flag is set in config — host must still approve."
      : "No production activation requested (fail-closed).",
    opsWhereUsed: `Pack catalog · ${agent.pack}`,
    opsMetrics: [
      { id: "tools", label: "Tools", value: String(agent.allowedTools.length) },
      { id: "provider", label: "Provider", value: agent.provider || "—" },
    ],
    footerNote:
      "Agent settings projected from self-contained pack folders. Browser is non-authority; mutations require host action refs.",
    specDocPath: agent.specDocPath,
    readmeDocPath: agent.readmeDocPath,
    structure: {
      role: agent.role,
      category: agent.category,
      folderPath: agent.folderPath,
      promptReference: agent.promptReference,
      rubricReference: agent.rubricReference,
      tools: [...agent.allowedTools],
      networkAccess: agent.networkAccess,
      productionActivationRequested: agent.productionActivationRequested,
      critiqueIn: critique.inputs,
      critiqueOut: critique.outputs,
      hasSpec: agent.hasSpecMd,
      hasSources: agent.hasSources,
      architecture: agent.architecture,
    },
  };
}

/**
 * Default agent detail is pack-backed (no demo VerificationLoop / MarketSentiment fixtures).
 * Prefers video.orchestrator; falls back to first exported pack agent.
 */
function defaultPackAgentDetail(): AgentDetailLandingView {
  const preferred =
    getPackAgent("video.orchestrator")
    ?? getPackAgent("specials.research-agent");
  if (preferred) return buildAgentDetailView(preferred, preferred.id);
  // Empty-shell only if export is missing (should not happen in-repo).
  return {
    labels: AGENT_DETAIL_LABELS,
    eyebrow: "PACK AGENT DETAIL",
    agentName: "Pack agent unavailable",
    versionBadge: "export missing",
    statusLabel: "error",
    velocityLabel: "run export_pack_agents_for_ui.py",
    headerStats: [],
    insightStrip: "Regenerate frontend/src/lib/projections/pack-agents.generated.ts",
    yourUsageNote: "—",
    historyFilters: [],
    usageRows: [],
    paginationLabel: "0 agents",
    versions: [],
    currentVersionNote: "Pack agent export is empty.",
    metaCriticNote: "—",
    evidenceNote: "—",
    configSummaries: [],
    playgroundMessages: [],
    evalScores: [],
    knowledgeStats: [],
    knowledgeSources: [],
    opsAlert: "No pack agents loaded.",
    opsWhereUsed: "—",
    opsMetrics: [],
    footerNote: "No demo agents are registered in the UI catalog.",
    specDocPath: null,
    readmeDocPath: null,
  };
}

/** Normalize route param (Next may leave encoding; trim empty). */
export function normalizeAgentRouteId(agentId: string | undefined): string {
  const raw = (agentId ?? "").trim();
  if (!raw) return "";
  try {
    return decodeURIComponent(raw);
  } catch {
    return raw;
  }
}

function unknownAgentDetail(agentId: string): AgentDetailLandingView {
  return {
    labels: AGENT_DETAIL_LABELS,
    eyebrow: "PACK AGENT DETAIL",
    agentName: `Unknown agent`,
    versionBadge: "not in catalog",
    statusLabel: "unavailable",
    velocityLabel: "check agent id",
    headerStats: [
      {
        id: "id",
        label: "Requested id",
        value: agentId,
        detail: "No matching pack folder in the UI catalog",
      },
    ],
    insightStrip: `No pack agent matches “${agentId}”. Open Registry Hub and pick a listed id.`,
    yourUsageNote: "—",
    historyFilters: [],
    usageRows: [],
    paginationLabel: "0",
    versions: [],
    currentVersionNote: `Unknown id: ${agentId}`,
    metaCriticNote: "—",
    evidenceNote: "—",
    configSummaries: [
      {
        id: "lookup",
        title: "Lookup",
        lines: [
          `agent_id: ${agentId}`,
          "status: not found in pack-agents.generated catalog",
          "hint: ids look like video.planner or specials.aesthetics-agent",
        ],
      },
    ],
    playgroundMessages: [],
    evalScores: [],
    knowledgeStats: [],
    knowledgeSources: [],
    opsAlert: "Agent id not found in closed-world pack catalog.",
    opsWhereUsed: "—",
    opsMetrics: [],
    footerNote:
      "Fail-closed: missing agent ids do not fall back to another agent (e.g. Orchestrator).",
    specDocPath: null,
    readmeDocPath: null,
  };
}

/**
 * Resolve detail view for a route agentId from the full pack catalog (133).
 * Does **not** silently substitute Orchestrator when the id is wrong or missing
 * from params — that was masking Next.js 16 async-params bugs.
 */
export function resolveAgentDetailView(agentId: string | undefined): AgentDetailLandingView {
  const id = normalizeAgentRouteId(agentId);
  if (!id) {
    return LOCAL_AGENT_DETAIL_LANDING;
  }
  const packAgent = getPackAgent(id) ?? getPackAgent(agentId ?? "");
  if (packAgent) return buildAgentDetailView(packAgent, packAgent.id);
  return unknownAgentDetail(id);
}

/** Pack-backed default (no demo registered agents). */
export const LOCAL_AGENT_DETAIL_LANDING: AgentDetailLandingView = defaultPackAgentDetail();

export const AGENT_DETAIL_TABS: readonly {
  readonly id: AgentDetailTabId;
  readonly label: string;
}[] = [
  { id: "config", label: "Spec / Config" },
  { id: "history", label: "History + Cross-Swarm Usage" },
  { id: "playground", label: "Playground" },
  { id: "knowledge", label: "Knowledge" },
  { id: "ops", label: "Ops & Rollout" },
];
