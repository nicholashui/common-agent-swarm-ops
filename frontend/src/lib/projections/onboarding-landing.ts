/**
 * Local Onboarding, Help & Documentation fixture for ui_16_onboarding.md / .svg.
 * Presentation-only until tour progress and docs CMS connect.
 */

export interface OnboardingAgentCard {
  readonly id: string;
  readonly name: string;
  readonly versionLabel: string;
  readonly description: string;
  readonly usage: string;
  readonly domain: string;
  readonly selectedByDefault?: boolean;
}

export interface OnboardingStep {
  readonly id: string;
  readonly title: string;
  readonly body: string;
  readonly ctaLabel: string;
  readonly href?: string;
}

export interface OnboardingDocCategory {
  readonly id: string;
  readonly title: string;
  readonly description: string;
  readonly articles: readonly string[];
}

export interface OnboardingSampleProject {
  readonly id: string;
  readonly title: string;
  readonly description: string;
  readonly href: string;
}

export interface OnboardingLandingView {
  readonly title: string;
  readonly subtitle: string;
  readonly steps: readonly OnboardingStep[];
  readonly agentFilters: readonly string[];
  readonly agents: readonly OnboardingAgentCard[];
  readonly recommendedPattern: {
    readonly name: string;
    readonly detail: string;
  };
  readonly helpCategories: readonly OnboardingDocCategory[];
  readonly sampleProjects: readonly OnboardingSampleProject[];
  readonly tourConcepts: readonly string[];
  readonly vaNote: string;
  readonly footerNote: string;
}

export const LOCAL_ONBOARDING_LANDING: OnboardingLandingView = {
  title: "Select Your Common Agents",
  subtitle:
    "Start with battle-tested commons from the Registry. You can always add more later.",
  steps: [
    {
      id: "s1",
      title: "Explore Registry",
      body: "Discover Common Agents and Patterns with metrics, provenance, and improvement history.",
      ctaLabel: "Open Registry",
      href: "/registry",
    },
    {
      id: "s2",
      title: "Compose from a Common Pattern",
      body: "Start from Parallel + Verify or another battle-tested pattern instead of a blank graph.",
      ctaLabel: "Open Composer",
      href: "/composer",
    },
    {
      id: "s3",
      title: "Select Your Common Agents",
      body: "Pick linked commons to pin into your first swarm canvas.",
      ctaLabel: "Continue",
    },
    {
      id: "s4",
      title: "Run with live view",
      body: "Open the canvas, run with authorized commands, and watch lifecycle + verification.",
      ctaLabel: "Open Canvas",
      href: "/canvas",
    },
    {
      id: "s5",
      title: "Review & approve improvements",
      body: "See proposals, L1/L2/L3 evidence, and governance stages before rollout.",
      ctaLabel: "Open Eval",
      href: "/evaluations",
    },
  ],
  agentFilters: [
    "All (87)",
    "Data & ETL",
    "Verification",
    "Analysis",
    "Synthesis",
  ],
  agents: [
    {
      id: "data",
      name: "DataFetcher",
      versionLabel: "Common v2.1 · 94%",
      description: "Multi-source data ingestion with retries.",
      usage: "12.4k runs · used in 248 swarms",
      domain: "Data & ETL",
      selectedByDefault: true,
    },
    {
      id: "ver",
      name: "VerifierNode",
      versionLabel: "Common v3.0 · 97%",
      description: "Iterative verification with rubric.",
      usage: "31.2k runs · used in 47 swarms",
      domain: "Verification",
      selectedByDefault: true,
    },
    {
      id: "sent",
      name: "SentimentAgent",
      versionLabel: "Common v1.9 · 91%",
      description: "Market sentiment from multiple feeds.",
      usage: "8.7k runs · used in 640 swarms",
      domain: "Analysis",
    },
    {
      id: "synth",
      name: "SynthesisAgent",
      versionLabel: "Common v2.2 · 93%",
      description: "Consolidate multi-source outputs.",
      usage: "6.1k runs · used in 189 swarms",
      domain: "Synthesis",
      selectedByDefault: true,
    },
    {
      id: "content",
      name: "ContentDirector",
      versionLabel: "Common v1.8 · 91%",
      description: "Creative strategy for cinematic flows.",
      usage: "8.7k runs · used in 640 swarms",
      domain: "Analysis",
    },
    {
      id: "pred",
      name: "MarketPredictor",
      versionLabel: "Common v2.0 · 92%",
      description: "Price movement prediction engine.",
      usage: "4.2k runs · used in 312 swarms",
      domain: "Analysis",
    },
  ],
  recommendedPattern: {
    name: "Parallel Independent + Verification Loop v1.4",
    detail:
      "Fits your selected commons · 94% success · 23% token saving. Will be pre-loaded in your first canvas.",
  },
  helpCategories: [
    {
      id: "concepts",
      title: "Concepts",
      description: "Commons, pinned versions, graphs, and collective improvement.",
      articles: [
        "What is a Common Agent?",
        "Patterns vs custom swarms",
        "Provenance & redaction",
      ],
    },
    {
      id: "patterns",
      title: "Common Patterns",
      description: "Parallel BIG ROWs, verification loops, routers, supervisors.",
      articles: [
        "Parallel Independent + Verify",
        "Verification / Iteration Loop",
        "Dynamic Router Graph",
      ],
    },
    {
      id: "governance",
      title: "Governance",
      description: "Proposals, approvals, canary, rollback.",
      articles: [
        "Safe rollout of a common version",
        "L1 / L2 / L3 quality model",
        "Audit trail basics",
      ],
    },
    {
      id: "contribution",
      title: "Contribution",
      description: "Propose improvements and contribute knowledge.",
      articles: [
        "Propose from run failures",
        "Knowledge contribution rules",
        "Fork vs linked common",
      ],
    },
    {
      id: "api",
      title: "API",
      description: "OpenAPI, tokens, webhooks, adapters.",
      articles: ["Run a swarm via API", "Scoped tokens", "Webhook signatures"],
    },
    {
      id: "troubleshoot",
      title: "Troubleshooting",
      description: "Blocked tasks, stale projections, recovery.",
      articles: [
        "Waiting for critique",
        "Stale projection recovery",
        "Denied export actions",
      ],
    },
  ],
  sampleProjects: [
    {
      id: "p1",
      title: "Trading research swarm",
      description: "Parallel data + verification with sample commons preloaded.",
      href: "/composer",
    },
    {
      id: "p2",
      title: "Content pipeline + quality loop",
      description: "Cinematic/YouTube style pattern with verifier.",
      href: "/canvas",
    },
    {
      id: "p3",
      title: "DSE tutor assessment flow",
      description: "Domain-adapter example (not a universal requirement).",
      href: "/registry",
    },
  ],
  tourConcepts: [
    "Agents are versioned configurations (pinned Common versions)",
    "Graphs run task / dependency / gate lifecycles",
    "Artifacts carry lineage, rights, QC, and provenance",
    "Critique is directed evidence with severity and resolution",
    "Releases require quality and approval gates",
  ],
  vaNote:
    "Domain-adapter onboarding may introduce VA roles, production phases, and templates without implying they are universal requirements for every swarm.",
  footerNote:
    "Local preview onboarding · tour progress is local-only until preference projections connect · Skip for now returns to the dashboard.",
};
