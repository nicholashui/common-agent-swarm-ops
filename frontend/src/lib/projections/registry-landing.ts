/**
 * Local Common Registry Hub fixture for ui_07_registry_hub.md / .svg.
 * Presentation-only until generated commons registry projections connect.
 */

export type RegistryViewMode = "cards" | "table" | "graph";

export interface RegistryAgentCard {
  readonly id: string;
  readonly name: string;
  readonly versionLabel: string;
  readonly description: string;
  readonly success: string;
  readonly avgTokens: string;
  readonly latency: string;
  readonly usage: string;
  readonly badges: readonly string[];
  readonly isNew?: boolean;
  readonly domains: readonly string[];
  readonly category?: string;
  readonly architecture?: string;
  readonly critiqueCompat?: string;
}

export interface RegistryPatternCard {
  readonly id: string;
  readonly name: string;
  readonly icon: string;
  readonly whenToUse: string;
  readonly metrics: string;
  readonly previewStyle: "parallel" | "verify" | "router";
}

export interface RegistryProposal {
  readonly id: string;
  readonly title: string;
  readonly detail: string;
  readonly primary?: boolean;
}

export interface RegistryLandingView {
  readonly title: string;
  readonly subtitle: string;
  readonly workspaceLabel: string;
  readonly searchPlaceholder: string;
  readonly facets: readonly string[];
  readonly agents: readonly RegistryAgentCard[];
  readonly patterns: readonly RegistryPatternCard[];
  readonly stats: readonly { readonly id: string; readonly label: string; readonly value: string }[];
  readonly yourImpact: string;
  readonly proposals: readonly RegistryProposal[];
  readonly reviewTitle: string;
  readonly reviewDiffLines: readonly string[];
  readonly impactRows: readonly {
    readonly label: string;
    readonly value: string;
  }[];
  readonly impactDomains: string;
  readonly footerNote: string;
}

export const LOCAL_REGISTRY_LANDING: RegistryLandingView = {
  title: "Common Registry",
  subtitle:
    "Battle-tested, versioned, collectively improved agents & swarm patterns.",
  workspaceLabel: "Trading Lab",
  searchPlaceholder: "Search agents, patterns, or describe what you need…",
  facets: [
    "Trading",
    "Content",
    "Education",
    "Distributed",
    "Success rate > 90%",
    "Used in my swarms",
    "High Verification",
  ],
  agents: [
    {
      id: "market-sentiment",
      name: "MarketSentimentAgent",
      versionLabel: "Common v2.3 · 12.4k · 94%",
      description:
        "Specialized for trading sentiment analysis — standardized I/O.",
      success: "94%",
      avgTokens: "720",
      latency: "1.4s",
      usage: "Used in 1,248 swarms · 23 of yours · +8% efficiency ↑",
      badges: ["High Verify", "Moltbot Compat", "Recently Improved"],
      domains: ["Trading"],
      category: "analysis / sentiment",
      architecture: "parallel worker",
      critiqueCompat: "accepts_critique_from: VerifierNode",
    },
    {
      id: "content-director",
      name: "ContentDirectorAgent",
      versionLabel: "Common v1.8 · 8.7k · 91%",
      description: "Creative strategy for cinematic / YouTube pipelines.",
      success: "91%",
      avgTokens: "980",
      latency: "2.1s",
      usage: "Used in 640 swarms · 5 of yours · +5% quality ↑",
      badges: ["Creative", "Bilingual EN/繁"],
      domains: ["Content"],
      category: "creative direction",
      architecture: "supervisor spoke",
      critiqueCompat: "comments_on: SynthesisAgent",
    },
    {
      id: "verification-loop",
      name: "VerificationLoopAgent",
      versionLabel: "Common v3.0 · 31.2k · 97%",
      description:
        "Output verification — iterative refine loop, top pass rate.",
      success: "97%",
      avgTokens: "640",
      latency: "1.8s",
      usage: "Used in 47 swarms · 8 of yours · +12% pass rate ↑",
      badges: ["High Verify", "Parallel Opt."],
      isNew: true,
      domains: ["Trading", "Content", "Education"],
      category: "quality / verification",
      architecture: "self_refine + critique cycle",
      critiqueCompat: "rubric: L1/L2/L3 · High Verification",
    },
  ],
  patterns: [
    {
      id: "parallel-verify",
      name: "Parallel Independent + Verify",
      icon: "⊞",
      whenToUse: "BIG ROWs · map-reduce · scale-out.",
      metrics: "92% · 234 swarms · 3.2k avg",
      previewStyle: "parallel",
    },
    {
      id: "verify-loop",
      name: "Verification / Iteration Loop",
      icon: "↺",
      whenToUse: "Self-refine until quality passes.",
      metrics: "97% · 189 swarms · 1.8k avg",
      previewStyle: "verify",
    },
    {
      id: "dynamic-router",
      name: "Dynamic Router Graph",
      icon: "◇",
      whenToUse: "LLM router picks next node dynamically.",
      metrics: "89% · 112 swarms · 2.4k avg",
      previewStyle: "router",
    },
  ],
  stats: [
    { id: "total", label: "Total Commons", value: "214" },
    { id: "versions", label: "Active versions", value: "1.8k" },
    { id: "merged", label: "Merged /mo", value: "37" },
    { id: "savings", label: "Eco savings", value: "$18k" },
  ],
  yourImpact:
    "4 improvements helped · $412 saved in your swarms",
  proposals: [
    {
      id: "p1",
      title: "CommonReportAgent → v3.0",
      detail: "meta-critic · 2.1k traces · +18% ↓ hallucination",
      primary: true,
    },
    {
      id: "p2",
      title: "CommonMarketPredictor → v2.5",
      detail: "by @you · awaiting review · affects 19 swarms",
    },
  ],
  reviewTitle: "Proposal Review — Diff + Impact Analysis",
  reviewDiffLines: [
    "- max_iterations: 3",
    "+ max_iterations: 5",
    "+ verification_step: structured_rubric",
    "  eval_rubric: CommonVerificationRubric v1.2",
    "  # redacted diff · evidence refs only",
    '  meta-critic: "added verifier reduced',
    '  hallucinations 18% across 2.1k runs"',
  ],
  impactRows: [
    { label: "Affected swarms", value: "87" },
    { label: "Est. success Δ", value: "+4.2%" },
    { label: "Est. savings /mo", value: "$1.1k" },
  ],
  impactDomains:
    "Domains: Trading (34) · Content (22) · Education (18) · Other (13)",
  footerNote:
    "Local preview registry · redacted metrics and diffs only · Instantiate / Propose / Merge require authorized action references. VA taxonomy is a domain facet; generic registry taxonomy remains primary.",
};
