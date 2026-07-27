/**
 * Lightweight agent-detail placeholder for the multi-screen parameter store.
 * Does NOT import pack-agents.generated (full 133-agent payload).
 * Real pack detail is loaded only via resolveAgentDetailView on the agent route.
 */

import type { AgentDetailLandingView } from "./agent-detail-landing";
import type { ScreenLabels } from "./screen-labels";

const STUB_LABELS: ScreenLabels = {
  common_agent_detail: "Common agent detail",
  quick_actions: "Quick actions",
  history_filters: "History filters",
  cross_swarm_usage: "Cross-swarm usage",
  timestamp: "Timestamp",
  swarm_pattern: "Swarm / pattern",
  status: "Status",
  duration_tokens_cost: "Duration / tokens / cost",
  summary: "Summary",
  action: "Action",
  playground_options: "Playground options",
  new: "New",
};

/** Minimal store default — not used for /registry/agents/[id] (uses resolveAgentDetailView). */
export const AGENT_DETAIL_PARAMETER_STUB: AgentDetailLandingView = {
  labels: STUB_LABELS,
  eyebrow: "PACK AGENT DETAIL",
  agentName: "Pack agent",
  versionBadge: "—",
  statusLabel: "registered",
  velocityLabel: "—",
  headerStats: [],
  insightStrip: "Open an agent from the registry for full pack settings.",
  yourUsageNote: "—",
  historyFilters: [],
  usageRows: [],
  paginationLabel: "—",
  versions: [],
  currentVersionNote: "—",
  metaCriticNote: "—",
  evidenceNote: "—",
  configSummaries: [],
  playgroundMessages: [],
  evalScores: [],
  knowledgeStats: [],
  knowledgeSources: [],
  opsAlert: "—",
  opsWhereUsed: "—",
  opsMetrics: [],
  footerNote:
    "Agent detail defaults are lazy; pack payloads load on the agent detail route only.",
};
