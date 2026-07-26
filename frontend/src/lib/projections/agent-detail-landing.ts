/**
 * Local Common Agent detail fixture for ui_05_agent_detail.md / .svg.
 * Presentation-only until generated registry agent projections connect.
 */

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
}

export const LOCAL_AGENT_DETAIL_LANDING: AgentDetailLandingView = {
  agentName: "VerificationLoopAgent",
  versionBadge: "Common v3.0 · 31.2k · 97%",
  statusLabel: "Live",
  velocityLabel: "improvement velocity +12%/mo",
  headerStats: [
    {
      id: "runs",
      label: "Runs",
      value: "31.2k",
      detail: "47 swarms",
    },
    {
      id: "success",
      label: "Success",
      value: "97%",
      detail: "global 91%",
    },
    {
      id: "tokens",
      label: "Avg tokens",
      value: "640",
      detail: "redacted cost band",
    },
  ],
  insightStrip:
    "Used in 47 active swarms globally · Your business: 8 swarms · Success in your usage: 96% (global 91%)",
  yourUsageNote: "View full cross-swarm impact →",
  historyFilters: [
    "All swarms",
    "Version",
    "Last 7 days",
    "Status",
    "Has error?",
  ],
  usageRows: [
    {
      id: "u1",
      timestamp: "04:12 · 2m",
      swarm: "TradingResearch α",
      pattern: "Parallel + Verify v1.4",
      status: "Success",
      statusTone: "success",
      duration: "12s",
      tokens: "612",
      cost: "$0.02",
      summary: "Verified market report · groundedness 0.94",
    },
    {
      id: "u2",
      timestamp: "03:44 · 8m",
      swarm: "ContentPipeline β",
      pattern: "Verification Loop v2.1",
      status: "Self-refine",
      statusTone: "self_refine",
      duration: "41s",
      tokens: "1.1k",
      cost: "$0.05",
      summary: "Iteration 2/5 · citation re-check",
    },
    {
      id: "u3",
      timestamp: "02:10 · 1h",
      swarm: "DSE Tutor Fleet",
      pattern: "Supervisor + Verify",
      status: "Success",
      statusTone: "success",
      duration: "9s",
      tokens: "480",
      cost: "$0.01",
      summary: "Assessment gate passed · L2 quality",
    },
    {
      id: "u4",
      timestamp: "01:02 · 3h",
      swarm: "RiskReview γ",
      pattern: "Dynamic Router",
      status: "Running",
      statusTone: "running",
      duration: "—",
      tokens: "streaming",
      cost: "—",
      summary: "Graph rev r-19 · task waiting_for_critique",
    },
    {
      id: "u5",
      timestamp: "00:20 · 4h",
      swarm: "ResearchDesk δ",
      pattern: "Parallel + Verify v1.4",
      status: "Error",
      statusTone: "error",
      duration: "18s",
      tokens: "702",
      cost: "$0.03",
      summary: "Blocked: missing approval · gate g-44",
    },
    {
      id: "u6",
      timestamp: "Yest · 22h",
      swarm: "OpsBrief ε",
      pattern: "Map/Reduce + Verify",
      status: "Success",
      statusTone: "success",
      duration: "22s",
      tokens: "890",
      cost: "$0.04",
      summary: "Pinned Common v3.0 · audit ref local-preview",
    },
  ],
  paginationLabel: "Server-side pagination · 31,204 runs · showing 6",
  versions: [
    { id: "v28", label: "v2.8", state: "past", delta: "−2% tokens" },
    { id: "v29", label: "v2.9", state: "past", delta: "+3% pass" },
    {
      id: "v30",
      label: "v3.0 (current)",
      state: "current",
      delta: "+12% pass",
    },
    {
      id: "v31",
      label: "v3.1 proposal",
      state: "proposal",
      delta: "pending",
    },
  ],
  currentVersionNote: "v3.0 change · added structured verification step",
  metaCriticNote:
    'Meta-critic: "reduced hallucinations 18% across 2.1k runs" · improved token efficiency +7%.',
  evidenceNote: "redacted diff · evidence refs only · corr b7f2c9d0",
  configSummaries: [
    {
      id: "identity",
      title: "Core Identity",
      lines: [
        "Canonical name: VerificationLoopAgent",
        "Category: quality / verification",
        "Architecture: self_refine + critique cycle",
        "In-scope: groundedness, citation checks, L2 quality",
        "Out-of-scope: final release authority",
        "Escalation: GateKeeper · human approval when blocked",
      ],
    },
    {
      id: "runtime",
      title: "Runtime Limits & Policy",
      lines: [
        "Iteration cap: 5",
        "Retry: 2 · timeout: 90s",
        "Cost band: redacted",
        "Concurrency: 1 per task",
        "Model fallback: policy returned by projection",
        "Approval authority: server-gated only",
      ],
    },
    {
      id: "tools-io",
      title: "Tools · Schema · Relationships",
      lines: [
        "Tools: retrieve (purpose: evidence) · audit required",
        "I/O schema refs: agent.verifier.in/out v3",
        "accepts_critique_from: MetaCritic, HumanReviewer",
        "comments_on: SynthesisAgent, ReportAgent",
        "Rubric: L1 structure · L2 groundedness · L3 judge when required",
        "Config tab renders redacted role/policy/schema summaries — never raw prompts, tools, or credentials.",
      ],
    },
  ],
  playgroundMessages: [
    {
      id: "p1",
      role: "system",
      text: "Isolated playground · inject pattern context optional · no live agent authority.",
    },
    {
      id: "p2",
      role: "user",
      text: "Verify this market brief for groundedness and missing citations.",
    },
    {
      id: "p3",
      role: "assistant",
      text: "Self-refine iter 1/5 · groundedness 0.82 · requesting citation re-check.",
    },
  ],
  evalScores: [
    { metric: "Task success", score: "0.94" },
    { metric: "Groundedness", score: "0.91" },
    { metric: "Efficiency", score: "0.88" },
    { metric: "L2 quality", score: "pass" },
  ],
  knowledgeStats: [
    { id: "chunks", label: "Chunks", value: "1.4k" },
    { id: "indexed", label: "Last indexed", value: "2h ago" },
    { id: "embedding", label: "Embedding", value: "policy-bound" },
    { id: "contrib", label: "Contributions", value: "128 verified" },
  ],
  knowledgeSources: [
    {
      id: "k1",
      name: "Verified failure patterns",
      type: "correction memory",
      status: "indexed",
      chunks: "420",
      added: "via verified runs",
    },
    {
      id: "k2",
      name: "Citation rubric examples",
      type: "few-shot",
      status: "indexed",
      chunks: "96",
      added: "training guide",
    },
    {
      id: "k3",
      name: "Constitutional quality rules",
      type: "constitutional",
      status: "active",
      chunks: "24",
      added: "commons",
    },
    {
      id: "k4",
      name: "Eval benchmarks pack",
      type: "benchmark",
      status: "ready",
      chunks: "60",
      added: "harness",
    },
  ],
  opsAlert:
    "v3.0 active in 47 swarms. Canary recommended — roll out to 5 swarms first to validate metrics.",
  opsWhereUsed:
    "TradingResearch α · ContentPipeline β · DSE Tutor Fleet · +44 more",
  opsMetrics: [
    { id: "active", label: "Active swarms", value: "47" },
    { id: "canary", label: "Canary eligible", value: "5" },
    { id: "risk", label: "Risk flags", value: "3" },
    { id: "delta", label: "Est. latency delta", value: "0.4%" },
  ],
  footerNote:
    "Local preview agent detail · redacted projections only · Propose / Rollout / Playground runs require authorized action references.",
};

export const AGENT_DETAIL_TABS: readonly {
  readonly id: AgentDetailTabId;
  readonly label: string;
}[] = [
  { id: "history", label: "History + Cross-Swarm Usage" },
  { id: "config", label: "Config / Spec" },
  { id: "playground", label: "Playground" },
  { id: "knowledge", label: "Knowledge" },
  { id: "ops", label: "Ops & Rollout" },
];
