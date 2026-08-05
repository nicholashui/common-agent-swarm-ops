/**
 * VA video pack agent groups (ten categories from agents.md / pack audit).
 * Used for Registry Hub grouping + tag filters.
 */

export type VideoAgentGroup = {
  readonly id: string;
  /** Display label for group headers */
  readonly label: string;
  /** Compact tag on chips */
  readonly tag: string;
  /** Sort order 1–10 */
  readonly order: number;
};

/** Canonical ten groups — ids match pack `category` / va_category. */
export const VIDEO_AGENT_GROUPS: readonly VideoAgentGroup[] = [
  { id: "1-ATL", tag: "1-ATL", label: "Above-the-Line", order: 1 },
  { id: "2-Cam", tag: "2-Cam", label: "Camera & Lighting", order: 2 },
  { id: "3-Edit", tag: "3-Edit", label: "Editorial & Color / Design", order: 3 },
  { id: "4-Snd", tag: "4-Snd", label: "Sound & Music", order: 4 },
  { id: "5-Perf", tag: "5-Perf", label: "Performance & Choreography", order: 5 },
  { id: "6-Dist", tag: "6-Dist", label: "Distribution & Marketing", order: 6 },
  { id: "7-Edu", tag: "7-Edu", label: "Education & Domain-Expert", order: 7 },
  { id: "8-AI", tag: "8-AI", label: "AI-Era Specialists", order: 8 },
  { id: "9-Meta", tag: "9-Meta", label: "Specialist Meta-Agents", order: 9 },
  { id: "10-Sup", tag: "10-Sup", label: "Workflow Support", order: 10 },
] as const;

const BY_ID = new Map(VIDEO_AGENT_GROUPS.map((g) => [g.id.toLowerCase(), g]));

/** Facet keys for the ten groups (chip values). */
export const VIDEO_GROUP_FACET_IDS: readonly string[] = VIDEO_AGENT_GROUPS.map(
  (g) => g.id,
);

export function isVideoGroupFacet(facet: string): boolean {
  return BY_ID.has(facet.trim().toLowerCase());
}

export function videoGroupForCategory(
  category: string | undefined | null,
): VideoAgentGroup | null {
  if (!category) return null;
  return BY_ID.get(category.trim().toLowerCase()) ?? null;
}

export function videoGroupLabel(category: string | undefined | null): string {
  const g = videoGroupForCategory(category);
  if (!g) return category?.trim() || "Ungrouped";
  return `${g.tag} · ${g.label}`;
}

export type AgentWithCategory = {
  readonly id: string;
  readonly category?: string;
};

export type VideoAgentGroupBucket<T extends AgentWithCategory> = {
  readonly group: VideoAgentGroup | null;
  readonly key: string;
  readonly label: string;
  readonly agents: readonly T[];
};

/**
 * Partition agents into the ten video groups (then ungrouped / specials).
 * Order follows VIDEO_AGENT_GROUPS; empty groups omitted.
 */
export function groupAgentsByVideoCategory<T extends AgentWithCategory>(
  agents: readonly T[],
): readonly VideoAgentGroupBucket<T>[] {
  const buckets = new Map<string, T[]>();
  for (const agent of agents) {
    const g = videoGroupForCategory(agent.category);
    const key = g?.id ?? (agent.id.startsWith("video.") ? "ungrouped-video" : "other");
    const list = buckets.get(key) ?? [];
    list.push(agent);
    buckets.set(key, list);
  }

  const out: VideoAgentGroupBucket<T>[] = [];
  for (const g of VIDEO_AGENT_GROUPS) {
    const list = buckets.get(g.id);
    if (!list || list.length === 0) continue;
    out.push({
      group: g,
      key: g.id,
      label: `${g.tag} · ${g.label}`,
      agents: list,
    });
    buckets.delete(g.id);
  }
  for (const [key, list] of buckets) {
    if (list.length === 0) continue;
    out.push({
      group: null,
      key,
      label: key === "ungrouped-video" ? "Video · ungrouped" : "Other packs",
      agents: list,
    });
  }
  return out;
}
