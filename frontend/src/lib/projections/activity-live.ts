/**
 * Map Host GET /api/v1/activity (+ insights) into ActivityLandingView.
 * Fail-closed: no fabricated board cards when feed is empty.
 */

import type { ActivityFeed, ActivityItem } from "../api/product-ops";
import {
  LOCAL_ACTIVITY_LANDING,
  type ActivityCardStatus,
  type ActivityLandingView,
  type ActivityTableRow,
} from "./activity-landing";

function mapStatus(status: string, severity: string): {
  readonly status: ActivityCardStatus;
  readonly label: string;
} {
  const s = `${status} ${severity}`.toLowerCase();
  if (s.includes("error") || s.includes("fail")) {
    return { status: "error", label: "Error" };
  }
  if (s.includes("run")) return { status: "running", label: "Running" };
  if (s.includes("refine")) return { status: "self_refine", label: "Refining" };
  if (s.includes("pause")) return { status: "paused", label: "Paused" };
  return { status: "success", label: status || "Recorded" };
}

function formatTime(iso: string): string {
  if (!iso) return "—";
  try {
    const d = new Date(iso);
    return d.toISOString().slice(11, 16);
  } catch {
    return iso.slice(0, 16);
  }
}

function toTableRow(item: ActivityItem): ActivityTableRow {
  const { status, label } = mapStatus(item.status, item.severity);
  return {
    id: item.id,
    timestamp: formatTime(item.occurred_at),
    swarm: item.subject_reference || "—",
    business: item.category || "ops",
    pattern: item.category || "—",
    agent: item.summary.slice(0, 48) || "—",
    version: "Host",
    status,
    statusLabel: label,
    duration: "—",
    tokens: "—",
    cost: "—",
    graphRevision: "—",
    lifecycle: item.status || "recorded",
    checkpoint: item.correlation_id?.slice(0, 12) ?? "—",
  };
}

export function buildLiveActivityView(input: {
  readonly feed: ActivityFeed | null;
  readonly hostReachable: boolean;
  readonly hostMessage?: string;
  readonly eventCount?: number;
  readonly categories?: readonly string[];
}): ActivityLandingView {
  const items = input.feed?.items ?? [];
  const tableRows = items.map(toTableRow);
  const asOf = input.feed?.freshness?.as_of ?? "pending";

  // Board: group by category (real Host categories only)
  const byCategory = new Map<string, ActivityItem[]>();
  for (const item of items) {
    const key = item.category || "general";
    const list = byCategory.get(key) ?? [];
    list.push(item);
    byCategory.set(key, list);
  }
  const boardColumns =
    byCategory.size === 0
      ? []
      : [...byCategory.entries()].slice(0, 6).map(([title, rows]) => ({
          id: title,
          title,
          patternLabel: "Host activity",
          stats: `${rows.length} event(s)`,
          healthTone: "healthy" as const,
          cards: rows.slice(0, 8).map((row) => {
            const mapped = mapStatus(row.status, row.severity);
            return {
              id: row.id,
              agentName: row.summary.slice(0, 64) || row.id,
              versionLabel: row.category,
              status: mapped.status,
              statusLabel: mapped.label,
              meta: formatTime(row.occurred_at),
              teaser: row.subject_reference || undefined,
              actions: ["View in Execute"],
              linked: true,
            };
          }),
        }));

  return {
    ...LOCAL_ACTIVITY_LANDING,
    description: input.hostReachable
      ? "Live Host activity feed (process-local façade). No fabricated runs."
      : input.hostMessage ??
        "Host activity unavailable. Start backend and set BACKEND_API_ORIGIN.",
    workspaceLabel: "Host organization",
    boardColumns,
    tableRows,
    timelineLanes: [],
    kpis: [
      {
        id: "events",
        label: "Events (page)",
        value: String(items.length),
        detail: input.hostReachable ? "GET /api/v1/activity" : "Host down",
      },
      {
        id: "insight-count",
        label: "Insight count",
        value: String(input.eventCount ?? items.length),
        detail: "GET /api/v1/activity/insights",
      },
      {
        id: "categories",
        label: "Categories",
        value: String(
          (input.categories ?? [...byCategory.keys()]).length,
        ),
        detail: (input.categories ?? [...byCategory.keys()]).join(", ") || "—",
      },
    ],
    chartNote: input.hostReachable
      ? `as_of ${asOf} · live Host feed`
      : "No Host feed",
    rolloutCards: [],
    footerNote: input.hostReachable
      ? "Activity from GET /api/v1/activity · redacted summaries only · process-local until Host persists runs."
      : "Activity fixture cleared · connect Host for live feed.",
  };
}
