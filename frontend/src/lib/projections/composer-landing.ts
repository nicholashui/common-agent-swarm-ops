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

/**
 * Loadable Plan samples — video pack (and optional specials) only.
 * Specs must map to existing business/video/agents + business/specials/agents.
 * No trading / COBOL / out-of-domain demos.
 */
export const COMPOSER_SAMPLES: readonly ComposerSample[] = [
  {
    id: "sample-wuxia",
    label: "YouTube wuxia short",
    summary: "Happy path · hierarchical + verify",
    kind: "happy_path",
    body: [
      "Wuxia short for YouTube (video domain only):",
      "- 90s cinematic opening + strong hook in first 3 seconds",
      "- verification / judge gate before publish",
      "- social cut + captions (accessibility)",
      "- mid-tier cost band",
      "Bind from video pack: orchestrator, planner, screenwriter, director, editor, judge.",
    ].join("\n"),
  },
  {
    id: "sample-trend-research",
    label: "Trend research → script",
    summary: "Web/trend research + copy · video pack",
    kind: "happy_path",
    body: [
      "Video content research pipeline for a vertical short series:",
      "- web research + trend intelligence on topic hooks",
      "- competitor glance for format novelty",
      "- copywriter / screenwriter handoff",
      "- critic or judge quality gate before production",
      "Use only video.* agents (e.g. webresearch, trendintelligence, copywriter, screenwriter, critic, judge).",
    ].join("\n"),
  },
  {
    id: "sample-social-budget",
    label: "Social under budget",
    summary: "Lean video crew · cost-efficient",
    kind: "happy_path",
    body: [
      "Short-form social video crew under budget.",
      "Fast turnaround for 15–30s clips, captions, light music bed.",
      "Prefer cost-efficient video crew; still need a minimum QC / judge gate.",
      "Agents from video pack only (orchestrator, editor, accessibility, sounddesign, judge).",
    ].join("\n"),
  },
  {
    id: "sample-conflict",
    label: "Cost vs quality (HITL demo)",
    summary: "Triggers needs_hitl · video production conflict",
    kind: "hitl_demo",
    body: [
      "Video production conflict: lowest cost AND premium cinematic quality film with no compromise.",
      "Either we ship same-day ASAP or we do a thorough multi-phase feature pipeline —",
      "I cannot decide which priority wins.",
      "Trade-off undecided. Conflict.",
      "Domain remains video (not software, not trading).",
    ].join("\n"),
  },
  {
    id: "sample-feature",
    label: "Full feature hierarchy",
    summary: "Orch → Planner → video departments",
    kind: "happy_path",
    body: [
      "Full feature film production hierarchy (video domain).",
      "Need Orchestrator → Planner → departments: story, direction, cinematography, picture, sound, and final QC/judge gate.",
      "Multi-phase, thorough. Bind video.* pack agents only.",
    ].join("\n"),
  },
  {
    id: "sample-brand-spot",
    label: "Brand spot + compliance",
    summary: "Brand / creative + legal-ish gates · video",
    kind: "happy_path",
    body: [
      "30s brand film for social and CTV:",
      "- brand strategist + creative director framing",
      "- director / cinematographer look",
      "- editor cut + music supervisor cues",
      "- compliance / judge review before publish",
      "Use video pack agents (brandstrategist, creativedirector, director, cinematographer, editor, musicsupervisor, compliance, judge).",
    ].join("\n"),
  },
  {
    id: "sample-explicit-conflict",
    label: "UGC vs cinematic (HITL)",
    summary: "Video scope conflict · HITL only",
    kind: "hitl_demo",
    body: [
      "There is a contradiction in video scope: we want either a cheap UGC-style social pipeline",
      "or a broadcast-quality cinematic drama series. Trade-off undecided. Conflict.",
      "Stay in video domain — human resolves priority only, not agent shopping.",
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
    "big_rows_verifier_cycle": "Parallel crew → judge cycle",
    "goal_chip_applied_chip": "Goal chip applied: ${chip}",
    "enter_a_goal_before_sending": "Enter a goal before sending.",
    "save_draft_requires_an_authorized_compose_contra": "Save Draft requires an authorized compose contract.",
    "load_template_requires_an_authorized_template_pr": "Load Template requires an authorized template projection.",
    "regenerate_requires_the_composer_recommend_strea": "Regenerate requires the composer recommend stream.",
    "search_patterns_2": "Search patterns…",
    "swarm_composer": "Plan",
    "close_composer": "Close plan",
    "chat_composer": "Plan requirements",
    "goal_examples": "Goal examples",
    "send_goal": "Send goal",
    "pattern_filters": "Pattern filters",
  },
  eyebrow: "",
  title: "Plan",
  description:
    "Form a multi-agent work from available agents · requirements in · workflow diagram out · human only on conflicts · then Execute",
  swarmName: "Untitled AI Swarm",
  architectTitle: "AI Swarm Architect (Host)",
  architectSubtitle:
    "Goal/spec in · catalog agents only · AI plan draws workflow · Accept AI → Execute · fail-closed",
  messages: [
    {
      id: "m0",
      role: "assistant",
      text:
        "Paste a goal or short production spec. I AI-pick pattern + agents and draw a crew workflow diagram. You only answer when I cannot resolve a conflict. Accept to open Execute.",
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
    "AI-pick mainly: materialize when decision_status=ai_resolved, then open Execute.",
    "Human only for open_questions (needs_hitl) e.g. requirement conflicts.",
    "Building blocks = Host catalog agents only · production fail-closed.",
  ],
  footerNote:
    "Plan · AI-pick mainly · human exception path for conflicts · open Execute for instance · process-local drafts.",
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
