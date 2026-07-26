/**
 * Local Blueprints & Templates fixture for ui_20_blueprints.md / .svg.
 * Presentation-only. Instantiation creates a new graph revision with pinned
 * versions — does not copy credentials or bypass validation/gates.
 *
 * migration_redesign: gallery chrome must not over-claim video pack maturity,
 * must not treat the safe stub as a blueprint family, and must not imply production activation.
 */

import type { ScreenLabels } from "./screen-labels";

import { VIDEO_DOMAIN_MIGRATION_CLAIM } from "../migration/video-domain-migration";

export type BlueprintGovernance = "official" | "team" | "personal" | "beta";

export interface BlueprintCard {
  readonly id: string;
  readonly name: string;
  readonly description: string;
  readonly pattern: string;
  readonly agentCount: string;
  readonly knowledge: string;
  readonly metrics: string;
  readonly author: string;
  readonly rating?: string;
  readonly domains: readonly string[];
  readonly governance: BlueprintGovernance;
  readonly featured?: boolean;
  readonly previewStyle: "parallel" | "router" | "verify" | "mapreduce";
  readonly pins: readonly string[];
  readonly vaHints: readonly string[];
  /** Optional pack maturity presentation (cataloged|mapped|…); never invent active. */
  readonly maturityLabel?: string;
}

export interface BlueprintsLandingView {
  readonly labels: ScreenLabels;
  readonly eyebrow: string;
  readonly title: string;
  readonly description: string;
  readonly searchPlaceholder: string;
  readonly filters: readonly string[];
  readonly sorts: readonly string[];
  readonly blueprints: readonly BlueprintCard[];
  readonly createNote: string;
  readonly publishNote: string;
  readonly safetyNote: string;
  readonly footerNote: string;
  /** migration_redesign fail-closed banner for video/domain pack claims. */
  readonly migrationNote: string;
}

export const LOCAL_BLUEPRINTS_LANDING: BlueprintsLandingView = {
  labels: {
    "search_blueprints": "Search blueprints",
    "create_your_own_blueprint": "Create Your Own Blueprint",
    "pattern": "Pattern",
    "agents": "Agents",
    "knowledge": "Knowledge",
    "metrics": "Metrics",
    "governance": "Governance",
    "rating": "Rating",
    "pinned_versions": "Pinned versions",
    "pack_maturity_migration_safe": "Pack maturity (migration-safe)",
    "va_compatible_preview_hints": "VA-compatible preview hints",
    "featured": "Featured",
    "blueprints_and_templates_gallery": "Blueprints and templates gallery",
    "domain_filters": "Domain filters",
    "sort_blueprints": "Sort blueprints",
  },
  eyebrow: "BLUEPRINTS & TEMPLATES",
  title: "Blueprints & Templates Gallery",
  description:
    "Swarm blueprint gallery (local presentation): pattern + agents + knowledge config. Deploy or customize only through authorized host actions.",
  searchPlaceholder: "Search blueprints or describe your use case…",
  filters: [
    "All (24)",
    "Trading",
    "Content",
    "Education",
    "Research",
  ],
  sorts: ["Most deployed", "Highest rated"],
  blueprints: [
    {
      id: "market-intel",
      name: "Market Intelligence Pipeline",
      description:
        "Complete daily market analysis: data fetch → sentiment → prediction → synthesis → verified report.",
      pattern: "Pattern: Parallel + Verify v1.4",
      agentCount: "8 Common Agents",
      knowledge: "Knowledge: Trading Corpus",
      metrics: "312 deployments · 94% success · est $0.14/run",
      author: "by @ecosystem",
      rating: "4.9 (142 reviews)",
      domains: ["Trading"],
      governance: "official",
      featured: true,
      previewStyle: "parallel",
      pins: [
        "DataFetcher@v2.1",
        "SentimentAgent@v1.9",
        "MarketPredictor@v2.0",
        "VerifierNode@v3.0",
      ],
      vaHints: [
        "Parallel branches + self-refine verification loop",
        "L1/L2 quality requirements on report handoff",
        "Pinned Common versions · new graph revision on deploy",
      ],
    },
    {
      id: "cinematic",
      name: "Cinematic Content Pipeline",
      description:
        "YouTube wuxia-style content pipeline preview — bilingual. Domain-pack roles remain registered/non-active until host gates pass.",
      pattern: "Pattern: Dynamic Router v2.2",
      agentCount: "6 Agents (cataloged)",
      knowledge: "Script → storyboard → voice → edit → publish (preview graph).",
      metrics: "Preview fixture · not production activation",
      author: "by @content-team",
      domains: ["Creative", "Bilingual", "Video", "Content"],
      governance: "team",
      previewStyle: "router",
      pins: ["ContentDirector@v1.8", "VerifierNode@v3.0"],
      maturityLabel: "cataloged · registered · non-active",
      vaHints: [
        "Router architecture + delivery channel settings (presentation only)",
        "Rights/consent on publish artifact remain server-gated",
        "pack_spine is the sole safe stub — not blueprint realization",
        `${VIDEO_DOMAIN_MIGRATION_CLAIM.agentInventoryCount} common video agents stay L0 until migration evidence`,
      ],
    },
    {
      id: "dse-tutor",
      name: "DSE Adaptive Tutor",
      description: "Hong Kong DSE ICT education",
      pattern: "Pattern: Verification Loop v1.2",
      agentCount: "5 Agents",
      knowledge: "Diagnostic → generate → verify → adapt.",
      metrics: "64 deployments · 96%",
      author: "by @edu-team",
      domains: ["Education", "Adaptive", "Research"],
      governance: "team",
      previewStyle: "verify",
      pins: ["TutorAgent@v1.4", "VerifierNode@v3.0"],
      vaHints: [
        "Domain-adapter template mapping (not universal)",
        "Approval gate optional for assessment release",
      ],
    },
    {
      id: "legacy",
      name: "Legacy Code Modernizer",
      description: "Automated codebase refactoring",
      pattern: "Pattern: Map-Reduce + Verifier v1.1",
      agentCount: "7 Agents",
      knowledge: "Analyze → plan → refactor → verify → PR.",
      metrics: "42 deployments · 87%",
      author: "by @dev-team",
      domains: ["DevOps", "Refactoring", "Research"],
      governance: "beta",
      previewStyle: "mapreduce",
      pins: ["Analyzer@v1.0", "RefactorAgent@v1.2", "VerifierNode@v3.0"],
      vaHints: [
        "Map-reduce parallel shards + verify gate",
        "Artifact handoff schemas for PR generation",
      ],
    },
  ],
  createNote:
    "Save any working swarm as a reusable blueprint, optionally publish to the gallery. Includes: pattern graph + pinned agent versions + knowledge sources + default config.",
  publishNote:
    "Publishing requires evaluation pass. Commons provenance preserved in all derivatives.",
  safetyNote:
    "Instantiation creates a new graph revision with pinned versions; it does not copy opaque tool credentials or bypass required validation/gates. Required critique relationships, L1/L2/L3, rights/consent, continuity, and provenance remain enforced server-side. Catalog or stub graphs do not imply production activation.",
  footerNote:
    "Local preview blueprints · Deploy / Fork / Publish require authorized blueprint actions. Mini graph previews are presentation chrome (React Flow deferred).",
  migrationNote: VIDEO_DOMAIN_MIGRATION_CLAIM.disclaimer,
};
