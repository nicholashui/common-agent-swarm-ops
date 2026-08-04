/**
 * Shared loaders that replace LOCAL_* demo fleets with Host GET projections.
 * Each builder starts from the local shell labels and overwrites data fields only.
 */

import {
  fetchApprovalsInbox,
  fetchBlueprints,
  fetchCommonsHealth,
  fetchFinanceSummary,
  fetchKnowledgeSources,
  fetchNotifications,
  fetchRunningSwarms,
  fetchWorkspaceSettings,
  fetchPreferences,
  fetchCollaborationPresence,
  fetchCommonImpact,
} from "../api/product-ops";
import { listSwarms } from "../api/product-swarms";
import {
  LOCAL_KNOWLEDGE_LANDING,
  type KnowledgeLandingView,
} from "./knowledge-landing";
import {
  LOCAL_COSTS_LANDING,
  type CostsLandingView,
} from "./costs-landing";
import {
  LOCAL_NOTIFICATIONS_LANDING,
  type NotificationsLandingView,
} from "./notifications-landing";
import {
  BLUEPRINT_SAMPLES,
  LOCAL_BLUEPRINTS_LANDING,
  type BlueprintsLandingView,
} from "./blueprints-landing";
import {
  LOCAL_SETTINGS_LANDING,
  type SettingsLandingView,
} from "./settings-landing";
import {
  LOCAL_PROFILE_LANDING,
  type ProfileLandingView,
} from "./profile-landing";
import {
  LOCAL_COLLABORATION_LANDING,
  type CollaborationLandingView,
} from "./collaboration-landing";
import {
  LOCAL_MONITORING_LANDING,
  type MonitoringLandingView,
} from "./monitoring-landing";
import {
  LOCAL_MOBILE_LANDING,
  type MobileLandingView,
} from "./mobile-landing";
import {
  LOCAL_CANVAS_LANDING,
  type CanvasLandingView,
} from "./canvas-landing";
import { buildLiveDashboardView } from "./dashboard-live";
import type { DashboardLandingView } from "./dashboard-landing";
import { PACK_AGENT_CATALOG_COUNTS } from "./pack-agents-catalog.generated";

function str(v: unknown, fallback = "—"): string {
  if (typeof v === "string" && v.trim()) return v;
  if (typeof v === "number" || typeof v === "boolean") return String(v);
  return fallback;
}

export async function loadLiveDashboard(): Promise<DashboardLandingView> {
  const [swarms, health, impact] = await Promise.all([
    listSwarms(),
    fetchCommonsHealth(),
    fetchCommonImpact(),
  ]);
  const base = buildLiveDashboardView({
    swarms: swarms.ok ? swarms.items : [],
    hostReachable: swarms.ok,
    hostMessage: swarms.ok ? undefined : swarms.message,
    loading: false,
    catalogCounts: health.ok
      ? {
          total: health.data.total_agents,
          video: health.data.by_pack.video ?? PACK_AGENT_CATALOG_COUNTS.video,
          specials:
            health.data.by_pack.specials ?? PACK_AGENT_CATALOG_COUNTS.specials,
        }
      : undefined,
  });
  if (impact.ok && impact.data.note) {
    return {
      ...base,
      insightsIntro: impact.data.note,
      commonHealth: health.ok
        ? base.commonHealth.map((card) =>
            card.id === "catalog-agents"
              ? {
                  ...card,
                  value: String(health.data.total_agents),
                  detail: Object.entries(health.data.by_pack)
                    .map(([k, v]) => `${k} ${v}`)
                    .join(" · "),
                  trend: `Host commons health · ${health.data.state}`,
                }
              : card,
          )
        : base.commonHealth,
    };
  }
  return base;
}

export async function loadLiveKnowledge(): Promise<KnowledgeLandingView> {
  const result = await fetchKnowledgeSources();
  if (!result.ok) {
    return {
      ...LOCAL_KNOWLEDGE_LANDING,
      collections: [],
      sources: [],
      searchHits: [],
      contributions: [],
      syncJobs: [],
      description: result.message,
      footerNote: result.message,
    };
  }
  const items = result.data.items ?? [];
  return {
    ...LOCAL_KNOWLEDGE_LANDING,
    description: "Live Host knowledge sources (GET /api/v1/knowledge/sources).",
    collections: [
      {
        id: "host-sources",
        name: "Host knowledge sources",
        scope: "common",
        health: items.length > 0 ? "healthy" : "reindexing",
        healthLabel: items.length > 0 ? "Live" : "Empty",
        chunks: String(items.length),
        syncDetail: result.data.freshness?.as_of
          ? `as_of ${result.data.freshness.as_of}`
          : "Host list",
        bindingKinds: ["rag"],
      },
    ],
    selectedCollectionId: "host-sources",
    sources: items.map((row, index) => ({
      id: str(row.id ?? row.source_id, `src-${index}`),
      name: str(row.display_name ?? row.name, `Source ${index + 1}`),
      type: str(row.type, "upload"),
      status: str(row.status, "indexed"),
      chunks: str(row.chunks ?? row.chunk_count, "0"),
      license: str(row.retention_class ?? row.license, "workspace"),
      bindingKind: "rag",
    })),
    searchHits: [],
    contributions: [],
    syncJobs: [],
    searchQuery: "",
    footerNote:
      "Knowledge from Host GET /api/v1/knowledge/sources · empty until sources are added with action refs.",
  };
}

export async function loadLiveCosts(): Promise<CostsLandingView> {
  const result = await fetchFinanceSummary();
  if (!result.ok) {
    return {
      ...LOCAL_COSTS_LANDING,
      kpis: [],
      swarmBreakdown: [],
      agentUsage: [],
      recommendations: [],
      description: result.message,
      footerNote: result.message,
    };
  }
  const currency = result.data.currency ?? "USD";
  const spend = result.data.spend_mtd ?? 0;
  const limit = result.data.budget_limit;
  return {
    ...LOCAL_COSTS_LANDING,
    description: "Live Host finance summary (GET /api/v1/finance/summary).",
    kpis: [
      {
        id: "spend",
        label: "Spend MTD",
        value: `${currency} ${spend}`,
        detail: "Host façade total",
        tone: "amber",
      },
      {
        id: "budget",
        label: "Budget limit",
        value: limit == null ? "Not set" : `${currency} ${limit}`,
        detail: "Requires Host budget action to change",
        tone: "green",
      },
      {
        id: "util",
        label: "Utilization",
        value:
          limit && limit > 0
            ? `${Math.round((Number(spend) / Number(limit)) * 100)}%`
            : "—",
        detail: "spend / budget when set",
        tone: "indigo",
      },
    ],
    swarmBreakdown: [],
    agentUsage: [],
    recommendations: [],
    budget: {
      monthly: limit == null ? "—" : `${currency} ${limit}`,
      spent: `${currency} ${spend}`,
      remaining:
        limit == null ? "—" : `${currency} ${Number(limit) - Number(spend)}`,
      utilization:
        limit && limit > 0
          ? `${Math.round((Number(spend) / Number(limit)) * 100)}%`
          : "—",
      alertThreshold: "—",
      projectedEom: "Host does not project EOM on this façade yet",
    },
    savings: {
      savedThisMonth: "—",
      efficiencyGain: "—",
      ifAllCommons: "No Host commons-savings projection on this façade",
    },
    footerNote:
      "Costs from GET /api/v1/finance/summary · no fabricated swarm cost bars.",
  };
}

export async function loadLiveNotifications(): Promise<NotificationsLandingView> {
  const result = await fetchNotifications();
  if (!result.ok) {
    return {
      ...LOCAL_NOTIFICATIONS_LANDING,
      items: [],
      description: result.message,
      footerNote: result.message,
    };
  }
  const items = result.data.items ?? [];
  return {
    ...LOCAL_NOTIFICATIONS_LANDING,
    description: "Live Host notifications (GET /api/v1/notifications).",
    items: items.map((row, index) => ({
      id: str(row.id, `n-${index}`),
      kind: str(row.kind ?? row.type, "swarm") as
        | "gate"
        | "anomaly"
        | "proposal"
        | "swarm"
        | "common"
        | "critique"
        | "budget",
      priority: str(row.priority, "normal") as "high" | "normal" | "low",
      title: str(row.title ?? row.summary, "Notification"),
      body: str(row.body ?? row.message, ""),
      meta: str(row.meta ?? row.created_at, ""),
      unread: row.read === false || row.unread === true,
      group: "earlier" as const,
      actions: [{ id: "open", label: "Open", href: "/activity" }],
    })),
    badgeCount: items.filter((row) => row.read === false || row.unread === true)
      .length,
    filters: [`All (${items.length})`, "Proposals", "Rollouts", "Gates", "Anomalies"],
    footerNote:
      "Notifications from Host GET /api/v1/notifications · empty until Host emits events.",
  };
}

export async function loadLiveBlueprints(): Promise<BlueprintsLandingView> {
  const result = await fetchBlueprints();
  if (!result.ok) {
    // Host down — still show samples so gallery is usable for planning.
    return {
      ...LOCAL_BLUEPRINTS_LANDING,
      blueprints: BLUEPRINT_SAMPLES,
      showingSamples: true,
      filters: [
        `All (${BLUEPRINT_SAMPLES.length})`,
        "Video",
        "Content",
        "Research",
        "Creative",
      ],
      description: `${result.message} Showing video-pack sample blueprints.`,
      footerNote: `${result.message} · Use sample blueprints (video pack only).`,
    };
  }
  const items = result.data.items ?? [];
  if (items.length === 0) {
    return {
      ...LOCAL_BLUEPRINTS_LANDING,
      blueprints: BLUEPRINT_SAMPLES,
      showingSamples: true,
      filters: [
        `All (${BLUEPRINT_SAMPLES.length})`,
        "Video",
        "Content",
        "Research",
        "Creative",
      ],
      description:
        "Host has no blueprints yet. Showing video-pack sample blueprints. Deploy still needs Host create/deploy actions.",
      footerNote:
        "Samples only · GET /api/v1/blueprints returned empty · Create blueprint on Host or keep browsing samples.",
    };
  }
  const hostCards = items.map((row, index) => ({
    id: str(row.id ?? row.blueprint_id, `bp-${index}`),
    name: str(row.name, `Blueprint ${index + 1}`),
    description: str(row.description, "Host blueprint"),
    pattern: str(row.pattern, "Pattern: Host"),
    agentCount: str(row.agent_count, "—"),
    knowledge: str(row.knowledge, "—"),
    metrics: str(row.metrics, "Host record"),
    author: str(row.author, "Host"),
    domains: Array.isArray(row.domains)
      ? (row.domains as string[])
      : (["Video"] as string[]),
    governance: str(row.governance, "team") as "official" | "team" | "beta",
    previewStyle: "parallel" as const,
    pins: [] as string[],
    vaHints: ["Host blueprint record"],
  }));
  return {
    ...LOCAL_BLUEPRINTS_LANDING,
    showingSamples: false,
    description: "Live Host blueprints (GET /api/v1/blueprints).",
    filters: [
      `All (${hostCards.length})`,
      "Video",
      "Content",
      "Research",
      "Creative",
    ],
    blueprints: hostCards,
    footerNote:
      "Blueprints from GET /api/v1/blueprints · Use sample blueprints to preview video pack templates anytime.",
  };
}

export async function loadLiveSettings(): Promise<SettingsLandingView> {
  const result = await fetchWorkspaceSettings();
  if (!result.ok) {
    return {
      ...LOCAL_SETTINGS_LANDING,
      description: result.message,
      footerNote: result.message,
    };
  }
  const ws = result.data.workspace ?? {};
  const providers = result.data.providers ?? [];
  return {
    ...LOCAL_SETTINGS_LANDING,
    description: "Live Host workspace settings (GET /api/v1/settings/workspace).",
    footerNote: `Locale ${str(ws.locale, "en")} · timezone ${str(ws.timezone, "UTC")} · providers ${providers.length} · Host live.`,
  };
}

export async function loadLiveProfile(): Promise<ProfileLandingView> {
  const result = await fetchPreferences();
  if (!result.ok) {
    return {
      ...LOCAL_PROFILE_LANDING,
      activitySummary: result.message,
      footerNote: result.message,
    };
  }
  return {
    ...LOCAL_PROFILE_LANDING,
    activitySummary:
      "Preferences loaded from Host GET /api/v1/actors/me/preferences.",
    footerNote: `Preferences keys: ${Object.keys(result.data).join(", ") || "none"} · Host live.`,
  };
}

export async function loadLiveCollaboration(): Promise<CollaborationLandingView> {
  const [presence, swarms] = await Promise.all([
    fetchCollaborationPresence(),
    listSwarms(),
  ]);
  const swarmItems = swarms.ok ? swarms.items : [];
  return {
    ...LOCAL_COLLABORATION_LANDING,
    description: presence.ok
      ? "Live Host presence + swarm drafts (no peer execution)."
      : presence.message,
    sharedItems: swarmItems.slice(0, 12).map((s) => ({
      id: s.id,
      kind: "swarm" as const,
      title: `${s.name} (Swarm)`,
      detail: `${s.status} · rev ${s.revision} · ${s.memberCount} members`,
      owner: "You",
      scope: "Host draft",
      actions: ["Open", "Duplicate"],
    })),
    sessions: swarmItems.slice(0, 4).map((s) => ({
      id: s.id,
      title: `${s.name} — Execute`,
      presence: presence.ok
        ? str(presence.data.note, "Observation-only presence")
        : "Presence unavailable",
      editors: [] as string[],
      canJoin: true,
    })),
    contributions: [],
    teamActivity: [],
    proposalQueue: [],
    shareModal: {
      ...LOCAL_COLLABORATION_LANDING.shareModal,
      title:
        swarmItems[0] != null
          ? `Share ${swarmItems[0].name}`
          : "Share (no drafts)",
      link:
        swarmItems[0] != null
          ? `https://caso.local/s/${swarmItems[0].id}`
          : "—",
    },
    footerNote: swarms.ok
      ? `Collaboration lists Host drafts (${swarmItems.length}) · presence observation-only.`
      : swarms.message,
  };
}

export async function loadLiveMonitoring(): Promise<MonitoringLandingView> {
  const [running, approvals] = await Promise.all([
    fetchRunningSwarms(),
    fetchApprovalsInbox(),
  ]);
  const items = running.ok ? running.data.items ?? [] : [];
  const approvalItems = approvals.ok ? approvals.data.items ?? [] : [];
  return {
    ...LOCAL_MONITORING_LANDING,
    description: running.ok
      ? "Live Host running swarms + approvals inbox."
      : running.message,
    fleet: [
      {
        id: "running",
        label: "Running swarms",
        value: String(items.length),
        detail: "GET /api/v1/swarms/running",
        tone: "green" as const,
      },
      {
        id: "approvals",
        label: "Approvals inbox",
        value: String(approvalItems.length),
        detail: "GET /api/v1/approvals",
        tone: approvalItems.length > 0 ? ("amber" as const) : ("indigo" as const),
      },
      ...items.slice(0, 4).map((row, index) => ({
        id: str(row.id, `fleet-${index}`),
        label: str(row.name, "Swarm"),
        value: str(row.status, "—"),
        detail: `rev ${row.revision ?? 0} · members ${row.member_count ?? 0}`,
        tone: "green" as const,
      })),
    ],
    filters: [
      { id: "time", label: "Time range", value: "Host live" },
      {
        id: "swarm",
        label: "Swarm",
        value: items[0] ? str(items[0].name) : "None running",
      },
      {
        id: "approvals",
        label: "Approvals",
        value: String(approvalItems.length),
      },
    ],
    traceTitle: "Host running fleets (no synthetic traces)",
    traceMeta: running.ok
      ? `${items.length} running · ${approvalItems.length} approvals`
      : "Host unreachable",
    traceTree: [],
    selectedSpan: {
      title: items[0]
        ? `Selected · ${str(items[0].name)}`
        : "No running swarm selected",
      metrics: items[0]
        ? `rev ${items[0].revision ?? 0} · members ${items[0].member_count ?? 0}`
        : "—",
      detailLines: [
        running.ok
          ? "Trace tree empty until Host projects run spans."
          : running.message,
      ],
    },
    alertRules: [],
    anomalies: [],
    metricBars: [],
    eventTypesNote: "Live Host running list only — no fabricated SSE traces.",
    footerNote: running.ok
      ? `Running from GET /api/v1/swarms/running (${items.length}) · approvals ${approvalItems.length}.`
      : running.message,
  };
}

export async function loadLiveMobile(): Promise<MobileLandingView> {
  const [swarms, notifications] = await Promise.all([
    listSwarms(),
    fetchNotifications(),
  ]);
  const items = swarms.ok ? swarms.items : [];
  const notes = notifications.ok ? notifications.data.items ?? [] : [];
  return {
    ...LOCAL_MOBILE_LANDING,
    runningSwarms: items.slice(0, 6).map((s) => ({
      id: s.id,
      name: s.name,
      status: s.status,
      statusTone:
        s.status === "running" || s.status === "live"
          ? ("running" as const)
          : ("live" as const),
      pattern: `rev ${s.revision}`,
      meta: `${s.memberCount} members`,
      canvasHref: `/swarms/${encodeURIComponent(s.id)}/canvas`,
    })),
    notifications: notes.slice(0, 6).map((n, index) => ({
      id: str(n.id, `mn-${index}`),
      kind: "gate" as const,
      title: str(n.title ?? n.summary, "Notification"),
      body: str(n.body ?? n.message, ""),
      meta: str(n.created_at, ""),
      actions: [{ id: "open", label: "Open", href: "/activity" }],
    })),
    activity: items.slice(0, 6).map((s) => ({
      id: s.id,
      title: s.name,
      status: s.status,
      version: `rev ${s.revision}`,
      meta: `${s.memberCount} members`,
      lifecycle: s.status,
    })),
    footerNote: swarms.ok
      ? "Mobile companion bound to Host swarms + notifications."
      : swarms.message,
  };
}

export async function loadLiveCanvasLanding(): Promise<CanvasLandingView> {
  const result = await listSwarms();
  if (!result.ok) {
    return {
      ...LOCAL_CANVAS_LANDING,
      swarmName: "No Host draft",
      patternBadge: "Host unreachable",
      commonsSummary: "0 members",
      nodes: [],
      groups: [],
      edges: [],
      sourceLabel: result.message,
      fromCompose: false,
      instanceId: "none",
      footerNote: result.message,
    };
  }
  if (result.items.length === 0) {
    return {
      ...LOCAL_CANVAS_LANDING,
      swarmName: "Untitled draft",
      patternBadge: "No Host drafts yet",
      commonsSummary: "0 members · open Plan or Registry",
      nodes: [],
      groups: [],
      edges: [],
      sourceLabel: "Menu Execute · empty Host fleet",
      fromCompose: false,
      instanceId: "empty",
      footerNote:
        "No Host drafts. Plan → Accept AI, or Registry Add to Swarm. Menu /canvas is empty until then.",
    };
  }
  const first = result.items[0]!;
  return {
    ...LOCAL_CANVAS_LANDING,
    swarmName: first.name,
    patternBadge: `${first.status} · rev ${first.revision}`,
    commonsSummary: `${first.memberCount} members · open full draft for graph`,
    nodes: [],
    groups: [],
    edges: [],
    sourceLabel: `Host list · latest ${first.id}`,
    fromCompose: true,
    instanceId: first.id,
    instanceStatus: first.status,
    instanceRevision: first.revision,
    footerNote: `Latest Host draft ${first.id}. Open /swarms/${first.id}/canvas for members graph.`,
  };
}
