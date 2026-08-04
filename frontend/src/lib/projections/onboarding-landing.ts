/**
 * Local Onboarding, Help & Documentation fixture for ui_16_onboarding.md / .svg.
 * Presentation-only until tour progress and docs CMS connect.
 */

import type { ScreenLabels } from "./screen-labels";

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
  readonly labels: ScreenLabels;
  readonly eyebrow: string;
  /** Template with `{step}` and `{total}` placeholders. */
  readonly stepProgressTemplate: string;
  readonly defaultStepIndex: number;
  readonly title: string;
  readonly subtitle: string;
  readonly steps: readonly OnboardingStep[];
  readonly agentFilters: readonly string[];
  readonly agents: readonly OnboardingAgentCard[];
  readonly recommendedPattern: {
    readonly eyebrow: string;
    readonly name: string;
    readonly detail: string;
  };
  readonly helpCategories: readonly OnboardingDocCategory[];
  readonly sampleProjects: readonly OnboardingSampleProject[];
  readonly tourConcepts: readonly string[];
  readonly defaultHelpPrompt: string;
  readonly vaNote: string;
  readonly footerNote: string;
}

export const LOCAL_ONBOARDING_LANDING: OnboardingLandingView = {
  labels: {
    onboarding_and_help: "Onboarding and help",
    tour_progress: "Tour progress",
    help_center: "Help Center",
    search_help: "Search help",
    search_docs: "Search docs…",
    ai_help: "AI help",
    ai_help_chat: "AI Help Chat",
    sample_projects: "Sample projects",
    sample_guided_projects: "Sample Guided Projects",
    core_concepts: "Core concepts",
    what_you_are_learning: "What you are learning",
    feedback: "Feedback",
    feedback_contribution: "Feedback & Contribution",
    search_commons: "Search commons",
    search_or_describe_what_you_need: "Search or describe what you need…",
    agent_domain_filters: "Agent domain filters",
    recommended_pattern: "Recommended Pattern",
    continue_tour: "Continue the tour with Next, or open a sample project below.",
    use_this_pattern: "Use this pattern",
    preview_only: "Preview only",
    back: "Back",
    next: "Next",
    clear_all: "Clear all",
    none_selected: "None selected",
    commons_selected_suffix: "commons selected",
  },
  eyebrow: "ONBOARDING",
  stepProgressTemplate: "Step {step} of {total}",
  defaultStepIndex: 2,
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
      title: "Plan from a Common Pattern",
      body: "Start from Parallel + Verify or another battle-tested pattern instead of a blank graph.",
      ctaLabel: "Open Plan",
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
      ctaLabel: "Open Execute",
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
    "Research",
    "Verification",
    "Production",
    "Script",
  ],
  agents: [
    {
      id: "data",
      name: "video.webresearch",
      versionLabel: "video pack · 94%",
      description: "Multi-source web research with retries.",
      usage: "12.4k runs · used in 248 swarms",
      domain: "Research",
      selectedByDefault: true,
    },
    {
      id: "ver",
      name: "video.judge",
      versionLabel: "video pack · 97%",
      description: "Quality gate with rubric feedback.",
      usage: "31.2k runs · used in 47 swarms",
      domain: "Verification",
      selectedByDefault: true,
    },
    {
      id: "sent",
      name: "video.trendintelligence",
      versionLabel: "video pack · 91%",
      description: "Trend signals from multiple sources.",
      usage: "8.7k runs · used in 640 swarms",
      domain: "Research",
    },
    {
      id: "synth",
      name: "video.screenwriter",
      versionLabel: "video pack · 93%",
      description: "Script structure and scene beats.",
      usage: "6.1k runs · used in 189 swarms",
      domain: "Script",
      selectedByDefault: true,
    },
    {
      id: "content",
      name: "video.creativedirector",
      versionLabel: "video pack · 91%",
      description: "Creative strategy for cinematic flows.",
      usage: "8.7k runs · used in 640 swarms",
      domain: "Production",
    },
    {
      id: "pred",
      name: "video.analyst",
      versionLabel: "video pack · 92%",
      description: "Performance and hook prediction for shorts.",
      usage: "4.2k runs · used in 312 swarms",
      domain: "Research",
    },
  ],
  recommendedPattern: {
    eyebrow: "Recommended Pattern",
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
      description: "Parallel crews, verification loops, routers, supervisors.",
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
      title: "Wuxia short swarm",
      description: "Parallel research + judge gate with sample video commons preloaded.",
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
  defaultHelpPrompt: "How do I safely rollout a new common version?",
  vaNote:
    "Domain-adapter onboarding may introduce VA roles, production phases, and templates without implying they are universal requirements for every swarm.",
  footerNote:
    "Local preview onboarding · tour progress is local-only until preference projections connect · Skip for now returns to the dashboard.",
};
