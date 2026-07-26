/**
 * Canonical specials pack catalog aligned to:
 * - docs/special_agents_redesign/agents/*.md
 * - business/specials/manifest.json
 * - backend/app/registry/specials_validator.py SPECIAL_SOURCE_CATALOG
 *
 * Pack contract: data-only draft representation. Sources are untrusted design
 * prose — never executable configuration, tools, network, or production activation.
 */

export type SpecialAgentLifecycle = "draft";
export type SpecialAgentActivation = "non_active";

export interface SpecialAgentCatalogEntry {
  readonly agentId: string;
  readonly sourcePath: string;
  readonly title: string;
  readonly summary: string;
  readonly status: SpecialAgentLifecycle;
  readonly activation: SpecialAgentActivation;
  readonly productionActivationRequested: false;
  readonly allowedTools: readonly [];
  readonly networkAccess: false;
  readonly provider: "local_deterministic";
}

/** Exact 19-record catalog; order matches SPECIAL_SOURCE_CATALOG. */
export const SPECIAL_AGENT_CATALOG: readonly SpecialAgentCatalogEntry[] = [
  {
    agentId: "specials.aesthetics-agent",
    sourcePath: "docs/special_agents_redesign/agents/aesthetics_agent.md",
    title: "Aesthetics Agent",
    summary: "Multimodal aesthetic critic, aligner, and taste-keeper for generative pipelines.",
    status: "draft",
    activation: "non_active",
    productionActivationRequested: false,
    allowedTools: [],
    networkAccess: false,
    provider: "local_deterministic",
  },
  {
    agentId: "specials.agent-loop-creator",
    sourcePath: "docs/special_agents_redesign/agents/agent_loop_creator.md",
    title: "Agent Loop Creator",
    summary: "Hierarchical ReAct-style loop design with controlled iteration and quality gates.",
    status: "draft",
    activation: "non_active",
    productionActivationRequested: false,
    allowedTools: [],
    networkAccess: false,
    provider: "local_deterministic",
  },
  {
    agentId: "specials.agentic-rag-agent",
    sourcePath: "docs/special_agents_redesign/agents/agentic_rag_agent.md",
    title: "Agentic RAG Agent",
    summary: "Hybrid agentic retrieval-augmented generation architecture (design provenance only).",
    status: "draft",
    activation: "non_active",
    productionActivationRequested: false,
    allowedTools: [],
    networkAccess: false,
    provider: "local_deterministic",
  },
  {
    agentId: "specials.autotelic-agent",
    sourcePath: "docs/special_agents_redesign/agents/autotelic_agent.md",
    title: "Autotelic Agent",
    summary: "Safety-oriented intrinsic-goal architecture for bounded self-directed behavior.",
    status: "draft",
    activation: "non_active",
    productionActivationRequested: false,
    allowedTools: [],
    networkAccess: false,
    provider: "local_deterministic",
  },
  {
    agentId: "specials.complex-problem-solution-process-model",
    sourcePath: "docs/special_agents_redesign/agents/complex_problem_solution_process_model.md",
    title: "Complex Problem Solution Process Model",
    summary: "WHAT / WHY / HOW / DO / REVIEW framing for ill-defined problem solving.",
    status: "draft",
    activation: "non_active",
    productionActivationRequested: false,
    allowedTools: [],
    networkAccess: false,
    provider: "local_deterministic",
  },
  {
    agentId: "specials.controller-agent",
    sourcePath: "docs/special_agents_redesign/agents/controller_agent.md",
    title: "Controller Agent",
    summary: "Controllable video generation pipeline playbook (data-only draft).",
    status: "draft",
    activation: "non_active",
    productionActivationRequested: false,
    allowedTools: [],
    networkAccess: false,
    provider: "local_deterministic",
  },
  {
    agentId: "specials.general-creative-agent",
    sourcePath: "docs/special_agents_redesign/agents/general_creative_agent.md",
    title: "General Creative Agent",
    summary: "Sparse outlier recombination creative generation contract (design provenance).",
    status: "draft",
    activation: "non_active",
    productionActivationRequested: false,
    allowedTools: [],
    networkAccess: false,
    provider: "local_deterministic",
  },
  {
    agentId: "specials.intent-analysis-agent",
    sourcePath: "docs/special_agents_redesign/agents/intent_analysis_agent.md",
    title: "Intent Analysis Agent",
    summary: "Deep Intent Analysis (DIA) multi-phase intent extraction framework.",
    status: "draft",
    activation: "non_active",
    productionActivationRequested: false,
    allowedTools: [],
    networkAccess: false,
    provider: "local_deterministic",
  },
  {
    agentId: "specials.knowledge-router-agent",
    sourcePath: "docs/special_agents_redesign/agents/knowledge_router_agent.md",
    title: "Knowledge Router Agent",
    summary: "Hybrid deterministic + learned knowledge routing with traceable critic loops.",
    status: "draft",
    activation: "non_active",
    productionActivationRequested: false,
    allowedTools: [],
    networkAccess: false,
    provider: "local_deterministic",
  },
  {
    agentId: "specials.llm-usage",
    sourcePath: "docs/special_agents_redesign/agents/llm_usage.md",
    title: "LLM Usage Dashboard Agent",
    summary: "Central LLM usage and cost observability design (no live provider hooks).",
    status: "draft",
    activation: "non_active",
    productionActivationRequested: false,
    allowedTools: [],
    networkAccess: false,
    provider: "local_deterministic",
  },
  {
    agentId: "specials.optimization-agent",
    sourcePath: "docs/special_agents_redesign/agents/optimization_agent.md",
    title: "Process Optimization Agent",
    summary: "Agentic process optimization and reliability improvement design.",
    status: "draft",
    activation: "non_active",
    productionActivationRequested: false,
    allowedTools: [],
    networkAccess: false,
    provider: "local_deterministic",
  },
  {
    agentId: "specials.planner-agent",
    sourcePath: "docs/special_agents_redesign/agents/planner_agent.md",
    title: "Software Implementation Planner Agent",
    summary: "SIPA: large-spec → traceable implementation plan conversion.",
    status: "draft",
    activation: "non_active",
    productionActivationRequested: false,
    allowedTools: [],
    networkAccess: false,
    provider: "local_deterministic",
  },
  {
    agentId: "specials.podcast-agent",
    sourcePath: "docs/special_agents_redesign/agents/podcast_agent.md",
    title: "Podcast Agent",
    summary: "Podcast production workflow and host process design provenance.",
    status: "draft",
    activation: "non_active",
    productionActivationRequested: false,
    allowedTools: [],
    networkAccess: false,
    provider: "local_deterministic",
  },
  {
    agentId: "specials.psychological-profile-agent",
    sourcePath: "docs/special_agents_redesign/agents/psychological_profile_agent.md",
    title: "Psychological Profile Agent",
    summary: "Creator psychological profile library for screenwriting frameworks (draft; risk-gated).",
    status: "draft",
    activation: "non_active",
    productionActivationRequested: false,
    allowedTools: [],
    networkAccess: false,
    provider: "local_deterministic",
  },
  {
    agentId: "specials.psychological-recommendation-agent",
    sourcePath: "docs/special_agents_redesign/agents/psychological_recommendation_agent.md",
    title: "Psychological Recommendation Agent",
    summary: "Psychology-informed preference recommendation design (draft; risk-gated).",
    status: "draft",
    activation: "non_active",
    productionActivationRequested: false,
    allowedTools: [],
    networkAccess: false,
    provider: "local_deterministic",
  },
  {
    agentId: "specials.research-agent",
    sourcePath: "docs/special_agents_redesign/agents/research_agent.md",
    title: "Research Agent",
    summary: "Local-first staged research report pipeline design.",
    status: "draft",
    activation: "non_active",
    productionActivationRequested: false,
    allowedTools: [],
    networkAccess: false,
    provider: "local_deterministic",
  },
  {
    agentId: "specials.screenwriter-strategic-goal-achievement-agent",
    sourcePath: "docs/special_agents_redesign/agents/screenwriter_strategic_goal_achievement_agent.md",
    title: "Screenwriter Strategic Goal Achievement Agent",
    summary: "Screenwriting case study of the six-stage self-inquiry goal framework.",
    status: "draft",
    activation: "non_active",
    productionActivationRequested: false,
    allowedTools: [],
    networkAccess: false,
    provider: "local_deterministic",
  },
  {
    agentId: "specials.strategic-goal-achievement-agent",
    sourcePath: "docs/special_agents_redesign/agents/strategic_goal_achievement_agent.md",
    title: "Strategic Goal Achievement Agent",
    summary: "Six-stage self-inquiry system for clarifying and executing goals.",
    status: "draft",
    activation: "non_active",
    productionActivationRequested: false,
    allowedTools: [],
    networkAccess: false,
    provider: "local_deterministic",
  },
  {
    agentId: "specials.techology-advisor-agent",
    sourcePath: "docs/special_agents_redesign/agents/techology_advisor_agent.md",
    title: "Technology Advisor Agent",
    summary: "Model/tool advisory with retrospective failure taxonomy (spelling preserved from source).",
    status: "draft",
    activation: "non_active",
    productionActivationRequested: false,
    allowedTools: [],
    networkAccess: false,
    provider: "local_deterministic",
  },
] as const;

export const SPECIAL_AGENT_CATALOG_COUNT = 19 as const;

export const SPECIALS_PACK_DISCLAIMER =
  "Specials pack: 19 data-only draft agents. Source Markdown under docs/special_agents_redesign/agents is untrusted design provenance — not configuration, tools, network access, or production activation. Host remains domain-neutral; no second control plane.";

export function specialAgentIds(): readonly string[] {
  return SPECIAL_AGENT_CATALOG.map((entry) => entry.agentId);
}

export function isSpecialsCatalogFailClosed(): boolean {
  return SPECIAL_AGENT_CATALOG.every(
    (entry) =>
      entry.status === "draft"
      && entry.activation === "non_active"
      && entry.productionActivationRequested === false
      && entry.allowedTools.length === 0
      && entry.networkAccess === false
      && entry.provider === "local_deterministic",
  );
}
