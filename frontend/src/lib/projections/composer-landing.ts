/**
 * Local Swarm Composer fixture for ui_03_swarm_composer.md / .svg.
 * Presentation-only until composer recommendation contracts are connected.
 */

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
  readonly footerNote: string;
}

export const LOCAL_COMPOSER_LANDING: ComposerLandingView = {
  title: "Swarm Composer",
  description:
    "Turn goals into Common Pattern + Common Agent compositions — pattern-first, NL-driven.",
  swarmName: "Untitled Swarm from Parallel + Verification",
  architectTitle: "Common Swarm Architect",
  architectSubtitle:
    "Recommends from Registry · prioritizes verification, parallelism, token efficiency",
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
          {
            id: "s4",
            label: "VerifierNode",
            version: "v3.0",
            verified: true,
          },
        ],
      },
    },
  ],
  goalChips: [
    "Daily market intelligence",
    "YouTube wuxia cinematic pipeline",
    "DSE ICT adaptive tutor",
    "Moltbot distributed",
  ],
  inputPlaceholder: "Describe your goal (EN / 繁體中文)… ⌘↵ to send",
  patterns: [
    {
      id: "pattern-parallel-verification-v1.4",
      name: "Parallel Independent + Verification",
      version: "1.4",
      whenToUse:
        "Independent data/analysis branches with a final quality verifier.",
      metrics: "94% success · 23% faster · 1.2k runs",
      usedIn: "used in 312 similar swarms",
      recommended: true,
      domainTags: ["Parallelism", "Verification"],
    },
    {
      id: "pattern-supervisor-v2.0",
      name: "Hierarchical Supervisor + Specialists",
      version: "2.0",
      whenToUse: "Central planner delegates to focused craft agents.",
      metrics: "91% success · 8 agents avg",
      usedIn: "used in 214 swarms",
      domainTags: ["Hierarchy"],
    },
    {
      id: "pattern-map-reduce-v1.2",
      name: "Map-Reduce with Consensus",
      version: "1.2",
      whenToUse: "Shard large inputs, combine, and vote on a result.",
      metrics: "89% success · scalable",
      usedIn: "used in 98 swarms",
      domainTags: ["Parallelism", "Cost tier"],
    },
    {
      id: "pattern-verification-loop-v1.2",
      name: "Verification Loop",
      version: "1.2",
      whenToUse: "Iterative refine/review cycles with gate thresholds.",
      metrics: "96% groundedness · 3 max iterations",
      usedIn: "used in 401 swarms",
      recommended: false,
      domainTags: ["Verification"],
    },
  ],
  filters: ["All domains", "Parallelism", "Verification", "Cost tier"],
  activeFilter: "All domains",
  footerNote:
    "Local preview · recommendations are inert until /api/composer contracts connect. Load into Canvas creates a draft handoff only when authorized.",
};
