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
  /** True when gallery is showing local video-pack samples (not Host records). */
  readonly showingSamples?: boolean;
}

/**
 * Video-pack sample blueprints for gallery demos when Host has none.
 * Pins use real video.* agent ids only (no trading / COBOL).
 */
export const BLUEPRINT_SAMPLES: readonly BlueprintCard[] = [
  {
    id: "sample-wuxia-short",
    name: "Wuxia Short Pipeline",
    description:
      "YouTube wuxia short: research → trend → script → judge gate → edit package.",
    pattern: "Pattern: Hierarchical + Verify",
    agentCount: "7 video pack agents",
    knowledge: "Knowledge: Video corpus",
    metrics: "Sample · not Host-deployed",
    author: "Sample · video pack",
    rating: "Sample",
    domains: ["Video", "Content"],
    governance: "official",
    featured: true,
    previewStyle: "parallel",
    pins: [
      "video.orchestrator@meta",
      "video.planner@meta",
      "video.webresearch@v1",
      "video.screenwriter@v1",
      "video.director@v1",
      "video.editor@v1",
      "video.judge@v1",
    ],
    vaHints: [
      "Sample only · Deploy still requires Host blueprint action",
      "Parallel research + judge verification loop",
      "Pinned video pack agents · new graph revision on deploy",
    ],
    maturityLabel: "sample · registered pack ids",
  },
  {
    id: "sample-trend-script",
    name: "Trend research → script",
    description:
      "Web/trend research to copywriter/screenwriter with judge gate before production.",
    pattern: "Pattern: Research + Verify",
    agentCount: "6 video pack agents",
    knowledge: "Hooks · competitors · script package",
    metrics: "Sample · not Host-deployed",
    author: "Sample · video pack",
    domains: ["Video", "Research", "Content"],
    governance: "team",
    previewStyle: "router",
    pins: [
      "video.orchestrator@meta",
      "video.webresearch@v1",
      "video.trendintelligence@v1",
      "video.copywriter@v1",
      "video.screenwriter@v1",
      "video.judge@v1",
    ],
    vaHints: [
      "Sample only · Host list empty uses these for gallery preview",
      "Research handoff → script → QC gate",
    ],
    maturityLabel: "sample · registered pack ids",
  },
  {
    id: "sample-social-lean",
    name: "Social under budget",
    description:
      "Lean short-form crew: edit, captions, sound, judge — cost-efficient social cuts.",
    pattern: "Pattern: Minimal video crew",
    agentCount: "5 video pack agents",
    knowledge: "15–30s social cut package",
    metrics: "Sample · not Host-deployed",
    author: "Sample · video pack",
    domains: ["Video", "Content"],
    governance: "team",
    previewStyle: "verify",
    pins: [
      "video.orchestrator@meta",
      "video.editor@v1",
      "video.accessibility@v1",
      "video.sounddesign@v1",
      "video.judge@v1",
    ],
    vaHints: ["Sample lean crew · still has judge gate"],
    maturityLabel: "sample · registered pack ids",
  },
  {
    id: "sample-brand-spot",
    name: "Brand spot + compliance",
    description:
      "30s brand film: strategist → creative → director → edit → compliance/judge.",
    pattern: "Pattern: Brand + gate",
    agentCount: "7 video pack agents",
    knowledge: "Brand look · music cues · compliance",
    metrics: "Sample · not Host-deployed",
    author: "Sample · video pack",
    domains: ["Video", "Content", "Creative"],
    governance: "beta",
    previewStyle: "mapreduce",
    pins: [
      "video.brandstrategist@v1",
      "video.creativedirector@v1",
      "video.director@v1",
      "video.cinematographer@v1",
      "video.editor@v1",
      "video.compliance@v1",
      "video.judge@v1",
    ],
    vaHints: [
      "Sample brand path · compliance before publish",
      `${VIDEO_DOMAIN_MIGRATION_CLAIM.agentInventoryCount} video pack agents remain non-active until Host gates pass`,
    ],
    maturityLabel: "sample · registered pack ids",
  },
];

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
    "Swarm blueprint gallery: Host records when present, or video-pack samples via Use sample blueprints. Deploy only through authorized Host actions.",
  searchPlaceholder: "Search blueprints or describe your use case…",
  filters: [
    `All (${BLUEPRINT_SAMPLES.length})`,
    "Video",
    "Content",
    "Research",
    "Creative",
  ],
  sorts: ["Most deployed", "Highest rated"],
  blueprints: BLUEPRINT_SAMPLES,
  showingSamples: true,
  createNote:
    "Save any working swarm as a reusable blueprint, optionally publish to the gallery. Includes: pattern graph + pinned agent versions + knowledge sources + default config.",
  publishNote:
    "Publishing requires evaluation pass. Commons provenance preserved in all derivatives.",
  safetyNote:
    "Instantiation creates a new graph revision with pinned versions; it does not copy opaque tool credentials or bypass required validation/gates. Required critique relationships, L1/L2/L3, rights/consent, continuity, and provenance remain enforced server-side. Catalog or stub graphs do not imply production activation.",
  footerNote:
    "Sample blueprints use video pack agent ids only · Deploy / Fork / Publish require authorized Host blueprint actions.",
  migrationNote: VIDEO_DOMAIN_MIGRATION_CLAIM.disclaimer,
};
