/**
 * Map Host GET /api/v1/activity (+ insights) into ActivityLandingView.
 * Fail-closed: no fabricated board cards when feed is empty.
 * Surfaces real spine / package-gate events when Host records them (Epic E).
 */

import type { ActivityFeed, ActivityItem } from "../api/product-ops";
import {
  LOCAL_ACTIVITY_LANDING,
  type ActivityCardStatus,
  type ActivityLandingView,
  type ActivityTableRow,
} from "./activity-landing";
import { STUB_RUN_HONESTY } from "./video-spine-template";

function isSpineRelated(item: ActivityItem): boolean {
  const cat = (item.category || "").toLowerCase();
  const summary = (item.summary || "").toLowerCase();
  const status = (item.status || "").toLowerCase();
  return (
    cat === "spine" ||
    cat === "approval" ||
    summary.includes("spine") ||
    summary.includes("package") ||
    status.includes("waiting_for_approval")
  );
}

function mapStatus(status: string, severity: string, category?: string): {
  readonly status: ActivityCardStatus;
  readonly label: string;
} {
  const s = `${status} ${severity} ${category ?? ""}`.toLowerCase();
  if (s.includes("denied") || s.includes("error") || s.includes("fail")) {
    return { status: "error", label: s.includes("denied") ? "Denied" : "Error" };
  }
  if (s.includes("waiting_for_approval") || s.includes("package gate")) {
    return { status: "paused", label: "Waiting approval" };
  }
  if (s.includes("spine") && (s.includes("running") || s.includes("advanced"))) {
    return { status: "running", label: "Spine stub" };
  }
  if (s.includes("run") && !s.includes("spine")) {
    return { status: "running", label: "Running" };
  }
  if (s.includes("refine")) return { status: "self_refine", label: "Refining" };
  if (s.includes("pause")) return { status: "paused", label: "Paused" };
  if (s.includes("approval") || s.includes("approved")) {
    return { status: "success", label: status || "Approval" };
  }
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
  const { status, label } = mapStatus(item.status, item.severity, item.category);
  const spine = isSpineRelated(item);
  return {
    id: item.id,
    timestamp: formatTime(item.occurred_at),
    swarm: item.subject_reference || "—",
    business: item.category || "ops",
    pattern: spine ? `spine · ${STUB_RUN_HONESTY}` : item.category || "—",
    agent: item.summary.slice(0, 48) || "—",
    version: spine ? "stub" : "Host",
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

export function countSpineActivity(
  items: readonly ActivityItem[],
): {
  readonly spine: number;
  readonly packageGates: number;
} {
  let spine = 0;
  let packageGates = 0;
  for (const item of items) {
    if (isSpineRelated(item)) spine += 1;
    const hay = `${item.category} ${item.summary} ${item.status}`.toLowerCase();
    if (hay.includes("package") || hay.includes("waiting_for_approval")) {
      packageGates += 1;
    }
  }
  return { spine, packageGates };
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
  const spineStats = countSpineActivity(items);

  // Board: group by category (real Host categories only); prefer spine/approval columns first
  const byCategory = new Map<string, ActivityItem[]>();
  for (const item of items) {
    const key = item.category || "general";
    const list = byCategory.get(key) ?? [];
    list.push(item);
    byCategory.set(key, list);
  }
  const categoryOrder = [...byCategory.keys()].sort((a, b) => {
    const score = (k: string) =>
      k === "spine" ? 0 : k === "approval" ? 1 : k === "swarm" ? 2 : 3;
    return score(a) - score(b) || a.localeCompare(b);
  });
  const boardColumns =
    byCategory.size === 0
      ? []
      : categoryOrder.slice(0, 6).map((title) => {
          const rows = byCategory.get(title) ?? [];
          const spineCol = title === "spine" || title === "approval";
          return {
            id: title,
            title: spineCol ? `${title} · stub` : title,
            patternLabel: spineCol
              ? STUB_RUN_HONESTY
              : "Host activity",
            stats: `${rows.length} event(s)`,
            healthTone: (title === "approval" ? "watch" : "healthy") as
              | "healthy"
              | "watch"
              | "degraded",
            cards: rows.slice(0, 8).map((row) => {
              const mapped = mapStatus(row.status, row.severity, row.category);
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
          };
        });

  return {
    ...LOCAL_ACTIVITY_LANDING,
    description: input.hostReachable
      ? spineStats.spine > 0
        ? `Live Host activity · ${spineStats.spine} spine/package event(s) · ${STUB_RUN_HONESTY}. No fabricated production media.`
        : "Live Host activity feed (process-local façade). Spine events appear after Execute stub runs. No fabricated runs."
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
        id: "spine-events",
        label: "Spine / package",
        value: String(spineStats.spine),
        detail:
          spineStats.packageGates > 0
            ? `${spineStats.packageGates} package-related · ${STUB_RUN_HONESTY}`
            : STUB_RUN_HONESTY,
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
      ? `as_of ${asOf} · live Host feed · spine stubs never claim production media`
      : "No Host feed",
    rolloutCards: [],
    footerNote: input.hostReachable
      ? `Activity from GET /api/v1/activity · redacted only · process-local · ${STUB_RUN_HONESTY}.`
      : "Activity fixture cleared · connect Host for live feed.",
  };
}
