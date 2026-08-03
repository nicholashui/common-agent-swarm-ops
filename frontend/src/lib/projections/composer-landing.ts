/**
 * Local Swarm Composer fixture for ui_03_swarm_composer.md / .svg.
 * Primary path is Host AI pick (POST /api/v1/composer/*); local reply is fallback only.
 */

import type { ScreenLabels } from "./screen-labels";

export type ComposerGraphStyle = "parallel_verify" | "verification_loop" | "dynamic_router" | "supervisor";

export interface ComposerAgentSlot {
  readonly id: string;
  readonly label: string;
  readonly version: string;
  readonly verified?: boolean;
  /** Host AI-picked pack agent id when available. */
  readonly agentId?: string;
}

export interface ComposerPatternCard {
  readonly id: string;
  readonly name: string;
  readonly version: string;
  readonly whenToUse: string;
  readonly metrics: string;
  readonly usedIn: string;
  readonly recommended?: boolean;
  readonly domainTags: readonly string[];
  readonly graphStyle: ComposerGraphStyle;
  readonly previewSummary: {
    readonly totalSlots: string;
    readonly parallelism: string;
    readonly estCostLatency: string;
    readonly verificationCoverage: string;
  };
}

export interface ComposerHitlOption {
  readonly id: string;
  readonly label: string;
}

export interface ComposerHitlQuestion {
  readonly id: string;
  readonly kind: string;
  readonly severity: string;
  readonly question: string;
  readonly options: readonly ComposerHitlOption[];
}

export interface ComposerChatMessage {
  readonly id: string;
  readonly role: "user" | "assistant";
  readonly text?: string;
  readonly lines?: readonly string[];
  readonly recommendation?: {
    readonly patternId: string;
    readonly patternName: string;
    readonly version: string;
    readonly rationale: string;
    readonly metrics: string;
    readonly slots: readonly ComposerAgentSlot[];
  };
  /** Present when AI cannot resolve without human (e.g. requirement conflict). */
  readonly hitl?: {
    readonly questions: readonly ComposerHitlQuestion[];
  };
}

/** Loadable Compose sample: full requirement text for the UI textarea. */
export type ComposerSampleKind = "happy_path" | "hitl_demo" | "domain_bias";

export interface ComposerSample {
  readonly id: string;
  readonly label: string;
  /** Short line under the label in the sample list. */
  readonly summary: string;
  readonly kind: ComposerSampleKind;
  /** Full requirements body loaded into the composer input. */
  readonly body: string;
}

export interface ComposerLandingView {
  readonly labels: ScreenLabels;
  readonly eyebrow: string;
  readonly title: string;
  readonly description: string;
  readonly swarmName: string;
  readonly architectTitle: string;
  readonly architectSubtitle: string;
  readonly messages: readonly ComposerChatMessage[];
  /** @deprecated Prefer `samples` — kept as short labels for chips. */
  readonly goalChips: readonly string[];
  /** Full loadable sample specs for the ACC Compose UI. */
  readonly samples: readonly ComposerSample[];
  readonly inputPlaceholder: string;
  readonly patterns: readonly ComposerPatternCard[];
  readonly filters: readonly string[];
  readonly activeFilter: string;
  readonly suggestNewLabel: string;
  readonly handoffNotes: readonly string[];
  readonly footerNote: string;
}

/** Canonical loadable samples (also documented in compose_acc_samples.md). */
export const COMPOSER_SAMPLES: readonly ComposerSample[] = [
  {
    id: "sample-wuxia",
    label: "YouTube wuxia short",
    summary: "Happy path · hierarchical + verify",
    kind: "happy_path",
    body: [
      "Wuxia short for YouTube:",
      "- 90s cinematic opening + strong hook in first 3 seconds",
      "- verification loop before publish",
      "- social cut + captions",
      "- mid-tier cost band",
      "Domain: video production",
    ].join("\n"),
  },
  {
    id: "sample-market",
    label: "Market intel + verify",
    summary: "Parallel research + final critic",
    kind: "happy_path",
    body: [
      "Build a daily market intelligence swarm with a report-quality verification loop.",
      "Prefer parallel research branches, then a final critic before the brief is published.",
      "Keep token cost reasonable.",
    ].join("\n"),
  },
  {
    id: "sample-social-budget",
    label: "Social under budget",
    summary: "Lean crew · cost-efficient",
    kind: "happy_path",
    body: [
      "Short-form social video crew under budget.",
      "Fast turnaround for 15–30s clips, captions, light music bed.",
      "Prefer cost-efficient crew; still need a minimum quality check.",
    ].join("\n"),
  },
  {
    id: "sample-conflict",
    label: "Cost vs quality (HITL demo)",
    summary: "Triggers needs_hitl · human picks priority only",
    kind: "hitl_demo",
    body: [
      "Lowest cost AND premium quality cinematic film with no compromise.",
      "Either we ship same-day ASAP or we do a thorough multi-phase feature pipeline —",
      "I cannot decide which priority wins.",
      "Trade-off undecided. Conflict.",
    ].join("\n"),
  },
  {
    id: "sample-feature",
    label: "Full feature hierarchy",
    summary: "Orch → Planner → departments",
    kind: "happy_path",
    body: [
      "Full feature film production hierarchy.",
      "Need Orchestrator → Planner → departments: story, direction, picture, sound, and final QC gate.",
      "Video domain. Multi-phase, thorough.",
    ].join("\n"),
  },
  {
    id: "sample-cobol",
    label: "Legacy COBOL / software",
    summary: "Specials / software domain bias",
    kind: "domain_bias",
    body: [
      "Legacy COBOL analysis swarm for a migration assessment.",
      "Software implementation planning, API inventory, risk register.",
      "Prefer specials / software-oriented agents when available.",
    ].join("\n"),
  },
  {
    id: "sample-explicit-conflict",
    label: "Scope contradiction (HITL)",
    summary: "UGC vs broadcast · explicit conflict",
    kind: "hitl_demo",
    body: [
      "There is a contradiction in scope: we want either a cheap UGC pipeline",
      "or a broadcast-quality drama series. Trade-off undecided. Conflict.",
    ].join("\n"),
  },
];

export const LOCAL_COMPOSER_LANDING: ComposerLandingView = {
  labels: {
    "swarm_name": "Swarm name",
    "show_system_context": "Show system context",
    "attach_requirements_file": "Attach requirements file",
    "common_pattern_browser": "Common Pattern Browser",
    "search_patterns": "Search patterns",
    "total_agents_slots": "Total agents / slots",
    "parallelism_factor": "Parallelism factor",
    "est_cost_latency": "Est. cost/latency",
    "verification_coverage": "Verification coverage",
    "recommended": "Recommended",
    "agent": "Agent",
    "verify": "Verify",
    "b1": "→ B1",
    "b2": "→ B2",
    "big_rows_verifier_cycle": "BIG ROWs → verifier cycle ↺",
    "goal_chip_applied_chip": "Goal chip applied: ${chip}",
    "enter_a_goal_before_sending": "Enter a goal before sending.",
    "save_draft_requires_an_authorized_compose_contra": "Save Draft requires an authorized compose contract.",
    "load_template_requires_an_authorized_template_pr": "Load Template requires an authorized template projection.",
    "regenerate_requires_the_composer_recommend_strea": "Regenerate requires the composer recommend stream.",
    "search_patterns_2": "Search patterns…",
    "swarm_composer": "Swarm composer",
    "close_composer": "Close composer",
    "chat_composer": "Chat composer",
    "goal_examples": "Goal examples",
    "send_goal": "Send goal",
    "pattern_filters": "Pattern filters",
  },
  eyebrow: "SWARM COMPOSER · ACC",
  title: "Swarm Composer",
  description:
    "Form a multi-agent work from available agents · requirements in · workflow diagram out · human only on conflicts",
  swarmName: "Untitled AI Swarm",
  architectTitle: "AI Swarm Architect (Host)",
  architectSubtitle:
    "Goal/spec in · catalog agents only · AI plan draws workflow · Accept AI → Canvas · fail-closed",
  messages: [
    {
      id: "m0",
      role: "assistant",
      text:
        "Paste a goal or short production spec. I AI-pick pattern + agents and draw a crew workflow diagram. You only answer when I cannot resolve a conflict.",
    },
  ],
  samples: COMPOSER_SAMPLES,
  goalChips: COMPOSER_SAMPLES.map((s) => s.label),
  inputPlaceholder: "Paste goal or short production spec… ⌘↵",
  patterns: [
    {
      id: "pattern-parallel-verification-v1.4",
      name: "Parallel Independent + Verification",
      version: "1.4",
      whenToUse:
        "Independent sub-swarms in parallel; final verifier loop for quality.",
      metrics: "94% success · 1.2k runs · used in 312 swarms",
      usedIn: "used in 312 swarms",
      recommended: true,
      domainTags: ["Parallelism", "Verification"],
      graphStyle: "parallel_verify",
      previewSummary: {
        totalSlots: "4",
        parallelism: "3",
        estCostLatency: "$0.14/min · 42s",
        verificationCoverage: "full",
      },
    },
    {
      id: "pattern-verification-loop-v1.2",
      name: "Verification Loop",
      version: "1.2",
      whenToUse: "Iterative refine until quality passes.",
      metrics: "97% · 189 swarms",
      usedIn: "used in 189 swarms",
      domainTags: ["Verification"],
      graphStyle: "verification_loop",
      previewSummary: {
        totalSlots: "2",
        parallelism: "1",
        estCostLatency: "$0.08/min · 55s",
        verificationCoverage: "full cycle",
      },
    },
    {
      id: "pattern-dynamic-router-v1.0",
      name: "Dynamic Router Graph",
      version: "1.0",
      whenToUse: "LLM router picks next node at runtime.",
      metrics: "89% · 112 swarms",
      usedIn: "used in 112 swarms",
      domainTags: ["Parallelism", "Cost tier"],
      graphStyle: "dynamic_router",
      previewSummary: {
        totalSlots: "3+",
        parallelism: "dynamic",
        estCostLatency: "$0.11/min · 38s",
        verificationCoverage: "optional gate",
      },
    },
    {
      id: "pattern-supervisor-v2.0",
      name: "Hierarchical Supervisor + Specialists",
      version: "2.0",
      whenToUse: "Central planner delegates to focused craft agents.",
      metrics: "91% success · 8 agents avg",
      usedIn: "used in 214 swarms",
      domainTags: ["Hierarchy"],
      graphStyle: "supervisor",
      previewSummary: {
        totalSlots: "8",
        parallelism: "specialist pool",
        estCostLatency: "$0.16/min · 61s",
        verificationCoverage: "supervisor gate",
      },
    },
  ],
  filters: ["All domains", "Parallelism", "Verification", "Cost tier"],
  activeFilter: "All domains",
  suggestNewLabel: "✧ AI: propose new pattern from this goal (Host)",
  handoffNotes: [
    "AI-pick mainly: materialize when decision_status=ai_resolved.",
    "Human only for open_questions (needs_hitl) e.g. requirement conflicts.",
    "Building blocks = Host catalog agents only · production fail-closed.",
  ],
  footerNote:
    "AI-pick mainly · human exception path for conflicts · Host catalog ranking · process-local drafts.",
};

/** Offline fallback only when Host recommend is unreachable. */
export function buildLocalAssistantReply(
  goal: string,
  patterns: readonly ComposerPatternCard[],
): ComposerChatMessage {
  const recommended =
    patterns.find((pattern) => pattern.recommended) ?? patterns[0];
  return {
    id: `local-${Date.now()}`,
    role: "assistant",
    text: "Host AI unavailable — offline fallback (not a human pick):",
    recommendation: {
      patternId: recommended?.id ?? "pattern-parallel-verification-v1.4",
      patternName: recommended?.name ?? "Parallel Independent + Verification Loop",
      version: recommended?.version ?? "1.4",
      rationale: `Offline AI stub for “${goal.slice(0, 120)}”. Start backend for real Host AI pick from pack catalog.`,
      metrics: recommended?.metrics ?? "offline fallback",
      slots: [
        {
          id: "ls1",
          label: "Orchestrator",
          version: "Common v1.0",
          agentId: "video.orchestrator",
        },
        {
          id: "ls2",
          label: "Planner",
          version: "Common v1.0",
          agentId: "video.planner",
        },
        {
          id: "ls3",
          label: "Director",
          version: "Common v1.0",
          agentId: "video.director",
        },
      ],
    },
  };
}
