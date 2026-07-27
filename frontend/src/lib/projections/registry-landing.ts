/**
 * Local Common Registry Hub fixture for ui_07_registry_hub.md / .svg.
 * Agent cards are generated from pack self-contained folders
 * (business/video/agents + business/specials/agents) via pack-agents.generated.ts.
 */

import type { ScreenLabels } from "./screen-labels";

import type { SpecialsLandingView } from "./specials-landing";
import { LOCAL_SPECIALS_LANDING } from "./specials-landing";
import {
  PACK_AGENT_COUNTS,
  PACK_AGENTS,
  type PackAgentRecord,
} from "./pack-agents.generated";
import { PACK_PROCESS_CATALOG } from "./pack-process.generated";

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
  readonly labels: ScreenLabels;
  readonly eyebrow: string;
  readonly title: string;
  readonly subtitle: string;
  readonly workspaceLabel: string;
  readonly searchPlaceholder: string;
  readonly facets: readonly string[];
  /** Facets treated as domain filters (subset of `facets`). */
  readonly domainFacets: readonly string[];
  readonly successRateFacet: string;
  readonly usedInSwarmsFacet: string;
  readonly highVerificationFacet: string;
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
  /** Specials pack catalog parameters (stored; not hardcoded in the component). */
  readonly specials: SpecialsLandingView;
}

export const LOCAL_REGISTRY_LANDING: RegistryLandingView = {
  labels: {
    "search_registry": "Search registry",
    "no_commons_match_the_current_search_or_facets": "No commons match the current search or facets.",
    "pending_proposals": "Pending Proposals",
    "spec_diff_redacted": "Spec Diff (redacted)",
    "impact_analysis": "Impact Analysis",
    "registry_stats": "Registry Stats",
    "your_impact": "Your Impact",
    "new": "New",
    "success": "Success",
    "avg_tok": "Avg tok",
    "latency": "Latency",
    "agent": "Agent",
    "version": "Version",
    "usage": "Usage",
    "actions": "Actions",
    "my_contributions_forks_require_an_authorized_pro": "My Contributions & Forks require an authorized projection.",
    "pending_proposals_shown_from_local_fixture": "Pending proposals shown from local fixture.",
    "common_registry_hub": "Common registry hub",
    "view_mode": "View mode",
    "registry_facets": "Registry facets",
    "proposal_review": "Proposal review",
    "registry_stats_2": "Registry stats",
  },
  eyebrow: "REGISTRY HUB",
  title: "Common Registry",
  subtitle:
    `All pack agents from self-contained folders (${PACK_AGENT_COUNTS.total}: `
    + `${PACK_AGENT_COUNTS.video} video · ${PACK_AGENT_COUNTS.specials} specials). `
    + "Open a card to view full agent settings.",
  workspaceLabel: "Pack catalog · offline settings",
  searchPlaceholder: "Search agent id, name, pack, role…",
  facets: [
    "video",
    "specials",
    "draft",
    "registered",
    "self-contained",
    "no-network",
  ],
  domainFacets: ["video", "specials"],
  successRateFacet: "registered",
  usedInSwarmsFacet: "self-contained",
  highVerificationFacet: "no-network",
  agents: PACK_AGENTS.map((agent: PackAgentRecord): RegistryAgentCard => ({
    id: agent.id,
    name: agent.name,
    versionLabel: agent.versionLabel,
    description: agent.description,
    success: agent.success,
    avgTokens: agent.avgTokens,
    latency: agent.latency,
    usage: agent.usage,
    badges: agent.badges,
    domains: agent.domains,
    category: agent.category,
    architecture: agent.architecture,
    critiqueCompat: agent.critiqueCompat,
  })),
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
    { id: "total", label: "Total agents", value: String(PACK_AGENT_COUNTS.total) },
    { id: "video", label: "Video pack", value: String(PACK_AGENT_COUNTS.video) },
    { id: "specials", label: "Specials pack", value: String(PACK_AGENT_COUNTS.specials) },
    {
      id: "processes",
      label: "Host process rows",
      value: String(PACK_PROCESS_CATALOG.hostProcessCount),
    },
  ],
  yourImpact:
    "Every listed agent has a self-contained folder (SPEC.md + agent_spec.json + sources/excerpts + study). "
    + "No demo agents. Process index and DNA are cataloged; production activation remains off.",
  /** Demo proposal queue removed — registry is pack catalog only. */
  proposals: [],
  reviewTitle: "Proposal Review — empty (no demo proposals)",
  reviewDiffLines: [
    "# No demo proposal diffs.",
    "# Registry agents come only from business/video + business/specials packs.",
  ],
  impactRows: [
    { label: "Video pack agents", value: String(PACK_AGENT_COUNTS.video) },
    { label: "Specials pack agents", value: String(PACK_AGENT_COUNTS.specials) },
    { label: "Host process rows", value: String(PACK_PROCESS_CATALOG.hostProcessCount) },
    { label: "Design process rows", value: String(PACK_PROCESS_CATALOG.designProcessCount) },
    { label: "DNA workflows", value: String(PACK_PROCESS_CATALOG.dnaWorkflowCount) },
    { label: "Eval artifacts", value: String(PACK_PROCESS_CATALOG.evalArtifactCount) },
    { label: "Total agents in UI", value: String(PACK_AGENT_COUNTS.total) },
  ],
  impactDomains: "Packs: video · specials (no demo domains)",
  footerNote:
    "Registry lists all checked-in pack agents only (114 video + 19 specials). "
    + `Host processes ${PACK_PROCESS_CATALOG.hostProcessCount} · design catalog ${PACK_PROCESS_CATALOG.designProcessCount} · `
    + `DNA ${PACK_PROCESS_CATALOG.dnaWorkflowCount} · safe baseline ${PACK_PROCESS_CATALOG.safeBaseline} (non-active; activation off). `
    + "Regenerate: export_pack_agents_for_ui.py + export_pack_process_for_ui.py",
  specials: LOCAL_SPECIALS_LANDING,
};
