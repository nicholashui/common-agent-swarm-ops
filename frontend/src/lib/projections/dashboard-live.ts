/**
 * Live dashboard projection — Host swarms + pack catalog only.
 * No fabricated success rates, savings, or fake fleet rows.
 */

import type { SwarmListItem } from "../api/product-swarms";
import { PACK_AGENT_CATALOG_COUNTS } from "./pack-agents-catalog.generated";
import {
  type DashboardLandingView,
  type DashboardRecentRun,
  type DashboardRunningSwarm,
  type DashboardStatusTone,
  type DashboardStatCard,
  LOCAL_DASHBOARD_LANDING,
} from "./dashboard-landing";
import {
  STUB_RUN_HONESTY,
  VIDEO_SPINE_WORKFLOW_ID,
  agentWorkflowSpineHref,
} from "./video-spine-template";

export type LiveDashboardInput = {
  readonly swarms: readonly SwarmListItem[];
  readonly hostReachable: boolean;
  readonly hostMessage?: string;
  readonly loading?: boolean;
  readonly asOf?: string;
  readonly catalogCounts?: {
    readonly total: number;
    readonly video: number;
    readonly specials: number;
  };
  /** Count of Host activity events in spine/package categories (Epic E). */
  readonly spineActivityCount?: number;
};

function formatRelative(iso: string, nowMs: number): string {
  if (!iso) return "—";
  const t = Date.parse(iso);
  if (Number.isNaN(t)) return "—";
  const sec = Math.max(0, Math.floor((nowMs - t) / 1000));
  if (sec < 60) return `${sec}s`;
  if (sec < 3600) return `${Math.floor(sec / 60)}m`;
  if (sec < 86400) return `${Math.floor(sec / 3600)}h`;
  return `${Math.floor(sec / 86400)}d`;
}

function sparkFromValue(value: number): readonly number[] {
  const n = Math.max(0, Math.min(100, Math.round(value)));
  // Gentle ramp ending at real value — not a fabricated growth story.
  return [0, n * 0.2, n * 0.4, n * 0.55, n * 0.7, n * 0.8, n * 0.88, n * 0.93, n * 0.97, n];
}

function mapStatus(status: string): {
  readonly tone: DashboardStatusTone;
  readonly label: string;
} {
  const s = status.trim().toLowerCase();
  if (s === "running") return { tone: "running", label: "Running" };
  if (s === "live" || s === "active") return { tone: "live", label: "Live" };
  if (s === "complete" || s === "completed" || s === "success" || s === "succeeded") {
    return { tone: "complete", label: "Complete" };
  }
  if (s === "failed" || s === "error" || s === "denied") {
    return { tone: "failed", label: s === "denied" ? "Denied" : "Failed" };
  }
  if (s === "waiting_for_approval" || s === "paused") {
    return { tone: "paused", label: s === "waiting_for_approval" ? "Package gate" : "Paused" };
  }
  if (s === "ready") return { tone: "paused", label: "Spine ready" };
  if (s === "draft") return { tone: "paused", label: "Draft" };
  if (s.includes("refine")) return { tone: "self_refining", label: status };
  return { tone: "live", label: status || "Unknown" };
}

function canvasHref(swarmId: string): string {
  return `/swarms/${encodeURIComponent(swarmId)}/canvas`;
}

function sortByUpdatedDesc(
  items: readonly SwarmListItem[],
): readonly SwarmListItem[] {
  return [...items].sort((a, b) => {
    const ta = Date.parse(a.updatedAt || a.createdAt) || 0;
    const tb = Date.parse(b.updatedAt || b.createdAt) || 0;
    return tb - ta;
  });
}

function mapRunningSwarm(item: SwarmListItem, nowMs: number): DashboardRunningSwarm {
  const spine = Boolean(item.hasSpine);
  const displayStatus = spine && item.spineStatus ? item.spineStatus : item.status;
  const { tone, label } = mapStatus(displayStatus);
  const members = item.memberCount;
  return {
    id: item.id,
    name: item.name,
    pattern: spine
      ? `${item.spineWorkflowId ?? VIDEO_SPINE_WORKFLOW_ID} · ${STUB_RUN_HONESTY}`
      : `rev ${item.revision} · Host draft`,
    status: tone,
    statusLabel: spine ? `Spine · ${label}` : label,
    progressLabel: spine
      ? `spine ${item.spineStatus ?? "ready"} · ${members} member(s)`
      : `${members} member${members === 1 ? "" : "s"} · rev ${item.revision}`,
    // Drafts are not scored runs — show full bar as "assembled", not fake progress.
    // Spine waiting_for_approval → partial progress only (never invent "complete production").
    progressPercent: spine
      ? item.spineStatus === "completed"
        ? 100
        : item.spineStatus === "waiting_for_approval"
          ? 88
          : item.spineStatus === "running"
            ? 45
            : 20
      : members > 0
        ? 100
        : 8,
    elapsed: formatRelative(item.updatedAt || item.createdAt, nowMs),
    costRate: "—",
    commonsOnLatest: spine
      ? STUB_RUN_HONESTY
      : item.lastRunId
        ? `last run ${item.lastRunId.slice(0, 12)}…`
        : "no Host run yet",
    canvasHref: canvasHref(item.id),
  };
}

function mapRecentRow(item: SwarmListItem, nowMs: number): DashboardRecentRun {
  const spine = Boolean(item.hasSpine);
  const displayStatus = spine && item.spineStatus ? item.spineStatus : item.status;
  const { tone, label } = mapStatus(displayStatus);
  return {
    id: item.id,
    time: formatRelative(item.updatedAt || item.createdAt, nowMs),
    swarm: item.name,
    pattern: spine
      ? `spine · ${item.spineStatus ?? "ready"} · ${STUB_RUN_HONESTY}`
      : item.lastRunId
        ? `run ${item.lastRunId.slice(0, 10)}…`
        : "draft",
    commons: `${item.memberCount} agents`,
    status: tone,
    statusLabel: spine ? `Spine · ${label}` : label,
    duration: "—",
    cost: "—",
    actionLabel: "Open Execute →",
    actionHref: canvasHref(item.id),
  };
}

/**
 * Build dashboard view from Host list + pack catalog.
 * Fail-closed: never invent fleet metrics the Host did not return.
 */
export function buildLiveDashboardView(
  input: LiveDashboardInput,
  nowMs: number = Date.now(),
): DashboardLandingView {
  const counts = input.catalogCounts ?? {
    total: PACK_AGENT_CATALOG_COUNTS.total,
    video: PACK_AGENT_CATALOG_COUNTS.video,
    specials: PACK_AGENT_CATALOG_COUNTS.specials,
  };
  const sorted = sortByUpdatedDesc(input.swarms);
  const totalMembers = sorted.reduce((sum, s) => sum + s.memberCount, 0);
  const draftCount = sorted.filter((s) =>
    s.status.toLowerCase() === "draft",
  ).length;
  const spineDrafts = sorted.filter((s) => s.hasSpine).length;
  const packageWaiting = sorted.filter(
    (s) => s.spineStatus === "waiting_for_approval",
  ).length;
  // Loading / empty shell must not call Date.now() for asOf — SSR vs client
  // hydration would differ by ~1s and trip React hydration mismatch.
  const asOf =
    input.asOf ??
    (input.loading
      ? "pending"
      : new Date(nowMs).toISOString().replace(/\.\d{3}Z$/, "Z"));

  const commonHealth: DashboardStatCard[] = [
    {
      id: "catalog-agents",
      label: "Pack agents (catalog)",
      value: String(counts.total),
      detail: `video ${counts.video} · specials ${counts.specials}`,
      trend: "Closed-world registry inventory",
      tone: "indigo",
      sparkline: sparkFromValue(Math.min(100, counts.total)),
      href: "/registry",
    },
    {
      id: "host-swarms",
      label: "Host swarm drafts",
      value: input.loading ? "…" : String(sorted.length),
      detail: input.loading
        ? "Loading Host list…"
        : input.hostReachable
          ? `${draftCount} draft · ${spineDrafts} with spine · ${sorted.length - draftCount} other`
          : "Host unreachable",
      trend: input.hostReachable
        ? "From GET /api/v1/swarms"
        : input.hostMessage ?? "Start backend · BACKEND_API_ORIGIN",
      tone: input.hostReachable ? "green" : "amber",
      sparkline: sparkFromValue(sorted.length * 10),
      href: "/registry",
    },
    {
      id: "spine-drafts",
      label: "Video spine drafts",
      value: input.loading ? "…" : String(spineDrafts),
      detail:
        packageWaiting > 0
          ? `${packageWaiting} waiting package HITL · ${STUB_RUN_HONESTY}`
          : STUB_RUN_HONESTY,
      trend:
        (input.spineActivityCount ?? 0) > 0
          ? `${input.spineActivityCount} spine activity event(s) on Host`
          : "Materialize a video brief in Plan to attach spine",
      tone: spineDrafts > 0 ? "violet" : "amber",
      sparkline: sparkFromValue(Math.min(100, spineDrafts * 20)),
      href: agentWorkflowSpineHref(),
    },
    {
      id: "members",
      label: "Bound members (all drafts)",
      value: input.loading ? "…" : String(totalMembers),
      detail: "Sum of member_count on Host drafts",
      trend: totalMembers === 0 ? "Add agents from Registry or Plan" : "Live Host totals",
      tone: "violet",
      sparkline: sparkFromValue(Math.min(100, totalMembers * 8)),
    },
    {
      id: "video-pack",
      label: "Video pack agents",
      value: String(counts.video),
      detail: "business/video catalog",
      trend: "Registered · non-active until Host gates",
      tone: "green",
      sparkline: sparkFromValue(Math.min(100, counts.video)),
      href: "/registry",
    },
    {
      id: "specials-pack",
      label: "Specials pack agents",
      value: String(counts.specials),
      detail: "business/specials catalog",
      trend: "Registered pack inventory",
      tone: "amber",
      sparkline: sparkFromValue(Math.min(100, counts.specials * 4)),
      href: "/registry",
    },
  ];

  const runningSwarms = sorted.slice(0, 8).map((s) => mapRunningSwarm(s, nowMs));
  const recentRuns = sorted.slice(0, 12).map((s) => mapRecentRow(s, nowMs));

  const pinned = sorted.slice(0, 3).map((s) => ({
    id: s.id,
    name: s.name,
    kindLabel: `Swarm · ${s.status}`,
    kindTone: "swarm" as const,
    href: canvasHref(s.id),
  }));

  const freshnessLabel = input.loading
    ? "Loading Host fleet…"
    : input.hostReachable
      ? `Host fleet · ${sorted.length} swarm(s)`
      : "Host fleet unavailable";

  return {
    ...LOCAL_DASHBOARD_LANDING,
    title: "Common Health & Fleet Ops",
    description:
      "Live Host drafts and pack catalog. No fabricated success rates or costs.",
    freshnessLabel,
    asOf,
    stale: !input.hostReachable && !input.loading,
    commonHealth,
    quickActions: [
      {
        id: "registry",
        label: "Explore Common Registry Hub",
        description: "Closed-world video & specials agents  →",
        href: "/registry",
        primary: true,
      },
      {
        id: "compose",
        label: "Plan a multi-agent work",
        description: "AI-pick crew · materialize draft  →",
        href: "/composer",
      },
      {
        id: "activity",
        label: "Open Activity",
        description: "Ops history when Host projects it  →",
        href: "/activity",
      },
      {
        id: "spine-template",
        label: "Open spine template",
        description: `${VIDEO_SPINE_WORKFLOW_ID} · ${STUB_RUN_HONESTY}  →`,
        href: agentWorkflowSpineHref(),
      },
    ],
    fleetSectionTitle: "Your Swarms Fleet Ops",
    runningSwarms,
    recentRuns,
    insightsIntro: input.hostReachable
      ? spineDrafts > 0
        ? `Live Host drafts include ${spineDrafts} video spine draft(s). ${STUB_RUN_HONESTY}. No fabricated production completion.`
        : "Aggregate insights appear when Host Ops/eval projections authorize them. Fleet rows above are live Host drafts only."
      : "Connect Host to load fleet drafts. Insights stay empty until Ops projections are authorized.",
    insights: [],
    controlPlane: {
      apiHealthLabel: input.loading
        ? "Checking…"
        : input.hostReachable
          ? "Reachable"
          : "Unreachable",
      apiHealthTone: input.loading
        ? "stale"
        : input.hostReachable
          ? "healthy"
          : "degraded",
      delayedEventWarning: "SSE not used for this snapshot",
      backlogCount: String(sorted.length),
      backlogDetail:
        spineDrafts > 0
          ? `${spineDrafts} spine draft(s) · ${packageWaiting} package gate(s)`
          : "Host drafts listed",
      approvalExpiryAlert:
        packageWaiting > 0
          ? `${packageWaiting} package gate(s) waiting · never auto-approve`
          : "No package gate waiting on listed drafts",
      sseLabel: "REST snapshot",
      sseDetail: input.hostReachable
        ? "GET /api/v1/swarms · process-local drafts"
        : input.hostMessage ?? "Host list failed",
      correlationId: "corr host-list",
      affectedSummary:
        sorted.length === 0
          ? "No Host drafts in this process"
          : `${sorted.length} swarm(s) · ${totalMembers} members · ${spineDrafts} spine`,
      affectedHref: "/registry",
    },
    pinned,
    footerNote: input.hostReachable
      ? `Fleet from Host GET /api/v1/swarms · process-local · pack inventory · ${STUB_RUN_HONESTY} when spine attached.`
      : "Host fleet not loaded · catalog counts still from local pack inventory · start backend with BACKEND_API_ORIGIN.",
  };
}

/** Honest empty shell used as store default / loading skeleton. */
export function buildEmptyLiveDashboardShell(): DashboardLandingView {
  // Fixed nowMs + asOf so server and client first paint match exactly.
  return buildLiveDashboardView(
    {
      swarms: [],
      hostReachable: false,
      loading: true,
      hostMessage: "Awaiting Host list…",
      asOf: "pending",
    },
    0,
  );
}
