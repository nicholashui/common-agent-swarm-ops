/**
 * Local Swarm Composer fixture for ui_03_swarm_composer.md / .svg.
 * Presentation-only until composer recommendation contracts connect.
 */

export type ComposerGraphStyle = "parallel_verify" | "verification_loop" | "dynamic_router" | "supervisor";

export interface ComposerAgentSlot {
  readonly id: string;
  readonly label: string;
  readonly version: string;
  readonly verified?: boolean;
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
}

export interface ComposerLandingView {
  readonly title: string;
  readonly description: string;
  readonly swarmName: string;
  readonly architectTitle: string;
  readonly architectSubtitle: string;
  readonly messages: readonly ComposerChatMessage[];
  readonly goalChips: readonly string[];
  readonly inputPlaceholder: string;
  readonly patterns: readonly ComposerPatternCard[];
  readonly filters: readonly string[];
  readonly activeFilter: string;
  readonly suggestNewLabel: string;
  readonly handoffNotes: readonly string[];
  readonly footerNote: string;
}

export const LOCAL_COMPOSER_LANDING: ComposerLandingView = {
  title: "Swarm Composer",
  description:
    "Turn goals into Common Pattern + Common Agent compositions — pattern-first, NL-driven.",
  swarmName: "Untitled Swarm from Parallel + Verification",
  architectTitle: "Common Swarm Architect",
  architectSubtitle:
    "Recommends from Registry · prioritizes verification, parallelism, token efficiency, collective improvement",
  messages: [
    {
      id: "m1",
      role: "user",
      lines: [
        "Build a daily market intelligence swarm",
        "with a report-quality verification loop.",
      ],
    },
    {
      id: "m2",
      role: "assistant",
      text: "Recommended starting Common Pattern:",
      recommendation: {
        patternId: "pattern-parallel-verification-v1.4",
        patternName: "Parallel Independent + Verification Loop",
        version: "1.4",
        rationale:
          "Independent branches benefit from parallel; final verifier cuts hallucinations.",
        metrics: "Est. 23% token saving vs sequential · 94% success · 1.2k runs",
        slots: [
          { id: "s1", label: "DataFetcher", version: "Common v2.1" },
          { id: "s2", label: "SentimentAgent", version: "v1.9" },
          { id: "s3", label: "MarketPredictor", version: "v2.0" },
          { id: "s4", label: "VerifierNode", version: "v3.0", verified: true },
        ],
      },
    },
  ],
  goalChips: [
    "Daily market intelligence",
    "YouTube wuxia cinematic pipeline",
    "DSE ICT adaptive tutor",
    "Legacy COBOL analysis swarm",
    "Moltbot distributed",
  ],
  inputPlaceholder: "Describe your goal (EN / 繁體中文)… ⌘↵ to send",
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
  suggestNewLabel: "✧ Suggest new Common Pattern from my goal",
  handoffNotes: [
    "Graph JSON handoff includes linked_common_pattern_id + pinned agent versions + BIG ROW layout.",
    "Suggestions are inert data · \"Load into Canvas\" is a server-authorized action reference.",
  ],
  footerNote:
    "Local preview · recommendations are inert until /api/composer contracts connect.",
};

/** Local multi-turn response when the recommend API is not connected. */
export function buildLocalAssistantReply(
  goal: string,
  patterns: readonly ComposerPatternCard[],
): ComposerChatMessage {
  const recommended =
    patterns.find((pattern) => pattern.recommended) ?? patterns[0];
  return {
    id: `local-${Date.now()}`,
    role: "assistant",
    text: "Local preview recommendation (API not connected):",
    recommendation: {
      patternId: recommended?.id ?? "pattern-parallel-verification-v1.4",
      patternName: recommended?.name ?? "Parallel Independent + Verification Loop",
      version: recommended?.version ?? "1.4",
      rationale: `For “${goal.slice(0, 120)}”, start from a battle-tested common pattern with verification coverage.`,
      metrics: recommended?.metrics ?? "94% success · local preview",
      slots: [
        { id: "ls1", label: "Planner", version: "Common v1.0" },
        { id: "ls2", label: "Worker", version: "Common v1.0" },
        { id: "ls3", label: "VerifierNode", version: "v3.0", verified: true },
      ],
    },
  };
}
