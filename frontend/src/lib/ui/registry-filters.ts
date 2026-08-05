/**
 * Pure local filters for RegistryHome discovery (presentation-only).
 */

import type {
  RegistryAgentCard,
  RegistryPatternCard,
  RegistryViewMode,
} from "../projections/registry-landing";
import {
  isVideoGroupFacet,
  videoGroupForCategory,
} from "../projections/video-agent-groups";
import type { SpecialAgentCatalogEntry } from "../specials/specials-catalog";

export const REGISTRY_VIEW_MODES: readonly {
  readonly id: RegistryViewMode;
  readonly label: string;
}[] = [
  { id: "cards", label: "Cards" },
  { id: "table", label: "Table" },
  { id: "graph", label: "Graph viz" },
] as const;

function agentHaystack(agent: RegistryAgentCard): string {
  return [
    agent.id,
    agent.name,
    agent.description,
    agent.versionLabel,
    agent.usage,
    agent.success,
    agent.avgTokens,
    agent.latency,
    agent.category ?? "",
    agent.architecture ?? "",
    agent.critiqueCompat ?? "",
    ...agent.badges,
    ...agent.domains,
  ]
    .join(" ")
    .toLowerCase();
}

/** Soft facet match: badge/domain/category/id prefix/usage + video group tags. */
export function agentMatchesFacet(
  agent: RegistryAgentCard,
  facet: string,
): boolean {
  const f = facet.trim().toLowerCase();
  if (f.length === 0) return true;
  // Ten video groups (1-ATL … 10-Sup)
  if (isVideoGroupFacet(f)) {
    const cat = (agent.category ?? "").trim().toLowerCase();
    if (cat === f) return true;
    const g = videoGroupForCategory(agent.category);
    if (g && g.id.toLowerCase() === f) return true;
    // Allow short tag match e.g. "atl" via badge
    if (agent.badges.some((b) => b.toLowerCase() === f)) return true;
    return false;
  }
  if (agent.badges.some((badge) => badge.toLowerCase() === f || badge.toLowerCase().includes(f))) {
    return true;
  }
  if (agent.domains.some((domain) => domain.toLowerCase() === f || domain.toLowerCase().includes(f))) {
    return true;
  }
  if ((agent.category ?? "").toLowerCase() === f) return true;
  if (agent.id.toLowerCase().startsWith(`${f}.`)) return true;
  if (agent.id.toLowerCase().includes(`.${f}`)) return true;
  if (agent.usage.toLowerCase().includes(f)) return true;
  if (agent.versionLabel.toLowerCase().includes(f)) return true;
  return false;
}

export function agentMatchesSearch(
  agent: RegistryAgentCard,
  search: string,
): boolean {
  const tokens = search
    .trim()
    .toLowerCase()
    .split(/\s+/)
    .filter((token) => token.length > 0);
  if (tokens.length === 0) return true;
  const hay = agentHaystack(agent);
  return tokens.every((token) => hay.includes(token));
}

/**
 * Domain facets (video/specials) use OR within the domain group.
 * Video group tags (1-ATL…10-Sup) use OR within the group set.
 * Other facets (draft, registered, …) use AND.
 * Search tokens all must match (AND).
 */
export function filterRegistryAgents(
  agents: readonly RegistryAgentCard[],
  search: string,
  activeFacets: ReadonlySet<string>,
  domainFacets: readonly string[] = ["video", "specials"],
): readonly RegistryAgentCard[] {
  const domainSet = new Set(
    domainFacets.map((facet) => facet.trim().toLowerCase()).filter(Boolean),
  );
  const selectedDomains: string[] = [];
  const selectedVideoGroups: string[] = [];
  const selectedOther: string[] = [];
  for (const facet of activeFacets) {
    const key = facet.trim().toLowerCase();
    if (key.length === 0) continue;
    if (domainSet.has(key)) selectedDomains.push(key);
    else if (isVideoGroupFacet(key)) selectedVideoGroups.push(key);
    else selectedOther.push(key);
  }

  return agents.filter((agent) => {
    if (selectedDomains.length > 0) {
      const hitsDomain = selectedDomains.some((facet) =>
        agentMatchesFacet(agent, facet),
      );
      if (!hitsDomain) return false;
    }
    if (selectedVideoGroups.length > 0) {
      const hitsGroup = selectedVideoGroups.some((facet) =>
        agentMatchesFacet(agent, facet),
      );
      if (!hitsGroup) return false;
    }
    for (const facet of selectedOther) {
      if (!agentMatchesFacet(agent, facet)) return false;
    }
    return agentMatchesSearch(agent, search);
  });
}

export function filterRegistryPatterns(
  patterns: readonly RegistryPatternCard[],
  search: string,
): readonly RegistryPatternCard[] {
  const tokens = search
    .trim()
    .toLowerCase()
    .split(/\s+/)
    .filter((token) => token.length > 0);
  if (tokens.length === 0) return patterns;
  return patterns.filter((pattern) => {
    const hay = [pattern.id, pattern.name, pattern.whenToUse, pattern.metrics]
      .join(" ")
      .toLowerCase();
    return tokens.every((token) => hay.includes(token));
  });
}

function specialAgentHaystack(agent: SpecialAgentCatalogEntry): string {
  return [
    agent.agentId,
    agent.title,
    agent.summary,
    agent.status,
    agent.activation,
    agent.provider,
    agent.sourcePath,
    "specials",
    "draft",
    "non-active",
    "non_active",
  ]
    .join(" ")
    .toLowerCase();
}

/** Facet match for the Special Agents Pack panel (same registry facets). */
export function specialAgentMatchesFacet(
  agent: SpecialAgentCatalogEntry,
  facet: string,
): boolean {
  const f = facet.trim().toLowerCase();
  if (f.length === 0) return true;
  if (f === "specials" || f === "draft" || f === "non-active" || f === "non_active") {
    return true;
  }
  // Registered/active video-only facets exclude specials drafts
  if (f === "video" || f === "registered" || f === "active") {
    return false;
  }
  const hay = specialAgentHaystack(agent);
  return hay.includes(f) || agent.agentId.toLowerCase().startsWith(`${f}.`);
}

export function specialAgentMatchesSearch(
  agent: SpecialAgentCatalogEntry,
  search: string,
): boolean {
  const tokens = search
    .trim()
    .toLowerCase()
    .split(/\s+/)
    .filter((token) => token.length > 0);
  if (tokens.length === 0) return true;
  const hay = specialAgentHaystack(agent);
  return tokens.every((token) => hay.includes(token));
}

/**
 * Apply the same Registry Hub search + facets to the Special Agents Pack panel.
 * Domain facets (video/specials) are OR within the domain group; other facets AND.
 */
export function filterSpecialAgents(
  agents: readonly SpecialAgentCatalogEntry[],
  search: string,
  activeFacets: ReadonlySet<string>,
  domainFacets: readonly string[] = ["video", "specials"],
): readonly SpecialAgentCatalogEntry[] {
  const domainSet = new Set(
    domainFacets.map((facet) => facet.trim().toLowerCase()).filter(Boolean),
  );
  const selectedDomains: string[] = [];
  const selectedOther: string[] = [];
  for (const facet of activeFacets) {
    const key = facet.trim().toLowerCase();
    if (key.length === 0) continue;
    if (domainSet.has(key)) selectedDomains.push(key);
    else selectedOther.push(key);
  }

  // Domain facet(s) selected but specials not included → hide entire specials pack
  if (selectedDomains.length > 0 && !selectedDomains.includes("specials")) {
    return [];
  }

  return agents.filter((agent) => {
    for (const facet of selectedOther) {
      if (!specialAgentMatchesFacet(agent, facet)) return false;
    }
    return specialAgentMatchesSearch(agent, search);
  });
}

export function toggleFacetSelection(
  current: ReadonlySet<string>,
  facet: string,
): ReadonlySet<string> {
  const next = new Set(current);
  if (next.has(facet)) next.delete(facet);
  else next.add(facet);
  return next;
}
