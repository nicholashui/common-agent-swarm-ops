/**
 * Local video-domain samples for Operate menu screens.
 * Shown only when the user toggles ▦ (or when Host lists are empty by default).
 * Not Host authority — deploy/approve still fail-closed.
 */

import type { ActivityLandingView } from "./activity-landing";
import type { MonitoringLandingView } from "./monitoring-landing";
import type { NotificationsLandingView } from "./notifications-landing";
import type { CostsLandingView } from "./costs-landing";
import type { KnowledgeLandingView } from "./knowledge-landing";
import type { GeneratedJsonObject } from "../api/client";

export const OPERATE_SAMPLE_IDS = {
  activity: "sample-activity",
  monitoring: "sample-monitoring",
  notifications: "sample-notifications",
  costs: "sample-costs",
  approval: "sample-approval",
  knowledge: "sample-knowledge",
} as const;

/** Activity board/table sample rows (video pack). */
export function applyActivitySamples(
  base: ActivityLandingView,
): ActivityLandingView {
  return {
    ...base,
    description:
      "Sample activity (video pack demos). Toggle ▦ to hide. Not Host history.",
    workspaceLabel: "Sample · Video Studio",
    boardColumns: [
      {
        id: "sample-research",
        title: "Research intake",
        patternLabel: "Sample · research",
        stats: "3 events · sample",
        healthTone: "healthy",
        cards: [
          {
            id: "sa-1",
            agentName: "video.webresearch",
            versionLabel: "video pack",
            status: "success",
            statusLabel: "Success",
            meta: "2m ago · sample",
            teaser: "Hook research bundle · sample",
            actions: ["View in Execute"],
            linked: true,
          },
          {
            id: "sa-2",
            agentName: "video.trendintelligence",
            versionLabel: "video pack",
            status: "running",
            statusLabel: "Running",
            meta: "streaming… sample",
            teaser: "Lifecycle: running · sample",
            actions: ["View in Execute"],
            linked: true,
          },
        ],
      },
      {
        id: "sample-qc",
        title: "Script + quality",
        patternLabel: "Sample · verify",
        stats: "2 events · sample",
        healthTone: "watch",
        cards: [
          {
            id: "sa-3",
            agentName: "video.screenwriter",
            versionLabel: "video pack",
            status: "success",
            statusLabel: "Success",
            meta: "6m ago · sample",
            teaser: "Script package · sample",
            actions: ["View in Execute"],
            linked: true,
          },
          {
            id: "sa-4",
            agentName: "video.judge",
            versionLabel: "video pack",
            status: "self_refine",
            statusLabel: "iter 2/5",
            meta: "QC sample · hook check",
            teaser: "Sample judge feedback loop",
            actions: ["Open Detail"],
            linked: true,
          },
        ],
      },
    ],
    tableRows: [
      {
        id: "st-1",
        timestamp: "12:01",
        swarm: "Wuxia Short · sample",
        business: "Video",
        pattern: "Hierarchical + Verify",
        agent: "video.webresearch",
        version: "video pack",
        status: "success",
        statusLabel: "Success",
        duration: "1.2s",
        tokens: "612",
        cost: "—",
        graphRevision: "sample-r1",
        lifecycle: "complete",
        checkpoint: "sample-ck",
      },
      {
        id: "st-2",
        timestamp: "11:58",
        swarm: "Brand Spot · sample",
        business: "Video",
        pattern: "Brand + gate",
        agent: "video.judge",
        version: "video pack",
        status: "self_refine",
        statusLabel: "Refining",
        duration: "41s",
        tokens: "1.1k",
        cost: "—",
        graphRevision: "sample-r2",
        lifecycle: "self_refine",
        checkpoint: "sample-ck2",
      },
    ],
    timelineLanes: [
      {
        id: "lane-s1",
        label: "Research",
        bars: [
          {
            id: "b1",
            label: "Web research",
            startPct: 4,
            widthPct: 28,
            tone: "success",
          },
        ],
      },
      {
        id: "lane-s2",
        label: "QC",
        bars: [
          {
            id: "b2",
            label: "Judge 2/5",
            startPct: 40,
            widthPct: 30,
            tone: "self_refine",
          },
        ],
      },
    ],
    kpis: [
      { id: "s-ev", label: "Sample events", value: "5", detail: "demo only" },
      { id: "s-ok", label: "Sample success", value: "—", detail: "not Host" },
      { id: "s-cost", label: "Sample cost", value: "—", detail: "not billing" },
    ],
    chartNote: "Sample trend only · toggle ▦ to hide",
    rolloutCards: [
      {
        id: "sr-1",
        title: "Sample · judge gate opportunity",
        body: "Demo insight only — not a Host rollout proposal.",
        tone: "opportunity",
        actions: ["Details"],
      },
    ],
    collectiveImpact:
      "Sample collective impact copy only. Host impact requires Ops projections.",
    freshnessLabel: "sample · not Host feed",
    footerNote:
      "Operate sample data · video pack demos · hide with ▦ · Host GET /api/v1/activity when live.",
  };
}

export function applyMonitoringSamples(
  base: MonitoringLandingView,
): MonitoringLandingView {
  return {
    ...base,
    description:
      "Sample monitoring fleet (video demos). Toggle ▦ to hide. No synthetic Host traces claimed as live.",
    liveLabel: "Sample · demo fleet",
    fleet: [
      {
        id: "sf-run",
        label: "Sample running",
        value: "2",
        detail: "demo swarms",
        tone: "green",
      },
      {
        id: "sf-gate",
        label: "Sample gates",
        value: "1",
        detail: "judge waiting",
        tone: "amber",
      },
      {
        id: "sf-wuxia",
        label: "Wuxia Short · sample",
        value: "running",
        detail: "rev 2 · 6 members",
        tone: "indigo",
      },
      {
        id: "sf-brand",
        label: "Brand Spot · sample",
        value: "live",
        detail: "rev 1 · 5 members",
        tone: "green",
      },
    ],
    filters: [
      { id: "time", label: "Time range", value: "Sample window" },
      { id: "swarm", label: "Swarm", value: "Wuxia Short · sample" },
      { id: "status", label: "Status", value: "Success" },
    ],
    traceTitle: "Sample trace · demo-run-1",
    traceMeta: "sample corr · not Host SSE",
    traceTree: [
      {
        id: "root",
        label: "Sample swarm root",
        kind: "root",
        status: "running",
        children: [
          {
            id: "parallel",
            label: "Parallel research",
            kind: "group",
            status: "success",
            children: [
              {
                id: "web",
                label: "video.webresearch",
                kind: "agent",
                version: "v1",
                status: "success",
                meta: "sample · done",
              },
              {
                id: "trend",
                label: "video.trendintelligence",
                kind: "agent",
                version: "v1",
                status: "success",
                meta: "sample · done",
              },
            ],
          },
          {
            id: "qc",
            label: "Script + judge",
            kind: "group",
            status: "self_refine",
            children: [
              {
                id: "judge",
                label: "video.judge",
                kind: "verify",
                version: "v1",
                status: "self_refine",
                meta: "iter 2 · sample",
              },
            ],
          },
        ],
      },
    ],
    selectedSpan: {
      title: "Selected span · video.judge",
      metrics: "Sample duration · tokens redacted",
      detailLines: [
        "Lifecycle: refining (sample)",
        "Host SSE: not connected",
        "Demo only · toggle ▦ to hide",
      ],
    },
    alertRules: [
      {
        id: "ar1",
        condition: "Sample · error rate > 5% on video.*",
        action: "→ notify (demo)",
        enabled: true,
      },
    ],
    anomalies: [
      {
        id: "an1",
        title: "Sample anomaly · judge latency",
        body: "Demo signal only — not a Host anomaly feed item.",
        freshness: "sample",
        highRisk: false,
      },
    ],
    metricBars: [
      {
        id: "m1",
        label: "Sample success",
        value: "—",
        percent: 72,
        tone: "good",
      },
      {
        id: "m2",
        label: "Sample token burn",
        value: "—",
        percent: 40,
        tone: "mid",
      },
    ],
    eventTypesNote: "Sample metrics · not Host SSE",
    footerNote:
      "Operate sample monitoring · hide with ▦ · live Host uses /swarms/running when available.",
  };
}

export function applyNotificationsSamples(
  base: NotificationsLandingView,
): NotificationsLandingView {
  const items = [
    {
      id: "sn-1",
      kind: "gate" as const,
      priority: "high" as const,
      title: "Sample gate · video.judge",
      body: "Demo approval-style notice for wuxia short QC (not Host gate).",
      meta: "Sample · 8m left (demo)",
      unread: true,
      group: "today-high" as const,
      actions: [
        { id: "review", label: "Review", href: "/operations", primary: true },
      ],
    },
    {
      id: "sn-2",
      kind: "swarm" as const,
      priority: "normal" as const,
      title: "Sample swarm update · Brand Spot",
      body: "Draft members updated in sample gallery only.",
      meta: "Sample · earlier",
      unread: true,
      group: "earlier" as const,
      actions: [{ id: "canvas", label: "Execute →", href: "/canvas" }],
    },
    {
      id: "sn-3",
      kind: "budget" as const,
      priority: "normal" as const,
      title: "Sample budget band · Wuxia Short",
      body: "Demo cost band warning — not Host finance.",
      meta: "Sample · earlier",
      unread: false,
      group: "earlier" as const,
      actions: [{ id: "costs", label: "Costs →", href: "/costs" }],
    },
  ];
  return {
    ...base,
    description:
      "Sample notifications (video demos). Toggle ▦ to hide. Not Host delivery.",
    badgeCount: items.filter((i) => i.unread).length,
    filters: [`All (${items.length})`, "Proposals", "Rollouts", "Gates", "Anomalies"],
    items,
    footerNote:
      "Operate sample notifications · hide with ▦ · Host GET /api/v1/notifications when live.",
  };
}

export function applyCostsSamples(base: CostsLandingView): CostsLandingView {
  return {
    ...base,
    description:
      "Sample cost bands (not billing). Toggle ▦ to hide. Host finance summary is separate.",
    periodLabel: "Sample period",
    kpis: [
      {
        id: "sk-spend",
        label: "Sample spend",
        value: "$—",
        detail: "demo band only",
        tone: "amber",
      },
      {
        id: "sk-budget",
        label: "Sample budget",
        value: "Not Host",
        detail: "toggle ▦ to hide",
        tone: "green",
      },
      {
        id: "sk-util",
        label: "Sample util",
        value: "—",
        detail: "not billing authority",
        tone: "indigo",
      },
    ],
    swarmBreakdown: [
      {
        id: "ss-1",
        name: "Wuxia Short · sample",
        spend: "$—",
        sharePercent: 55,
        tokens: "sample",
      },
      {
        id: "ss-2",
        name: "Brand Spot · sample",
        spend: "$—",
        sharePercent: 45,
        tokens: "sample",
      },
    ],
    agentUsage: [
      {
        id: "sa-1",
        agent: "video.webresearch",
        tokens: "sample",
        cost: "$—",
        inputShare: "60%",
        outputShare: "30%",
        toolShare: "10%",
        commonVersion: "video pack",
      },
      {
        id: "sa-2",
        agent: "video.judge",
        tokens: "sample",
        cost: "$—",
        inputShare: "50%",
        outputShare: "45%",
        toolShare: "5%",
        commonVersion: "video pack",
      },
    ],
    recommendations: [
      {
        id: "sr-1",
        title: "Sample · prefer video.editor over fork",
        body: "Demo recommendation only.",
        savings: "—",
        qualityNote: "Cannot weaken L1/L2 (Host-enforced)",
      },
    ],
    budget: {
      monthly: "Sample",
      spent: "—",
      remaining: "—",
      utilization: "—",
      alertThreshold: "—",
      projectedEom: "Sample only · not Host projection",
    },
    savings: {
      savedThisMonth: "—",
      efficiencyGain: "—",
      ifAllCommons: "Sample savings copy · not Host",
    },
    footerNote:
      "Operate sample costs · hide with ▦ · Host GET /api/v1/finance/summary when live.",
  };
}

/** Sample approval gate projection for Approvals & Rollouts on /operations. */
export function buildSampleApprovalProjection(): GeneratedJsonObject {
  return {
    approval_id: "sample-approval-demo",
    run_id: "sample-run-wuxia",
    risk_tier: "elevated",
    gate_status: "paused",
    stale: false,
    created_at: "2026-06-01T12:00:00Z",
    action_preview: {
      summary: "Sample gate: publish wuxia short after judge QC (demo only).",
      resource_ref: "swarm:sample-wuxia",
    },
    quality_evidence: {
      l1: "pass",
      l2: "0.91",
      l3: "not_required",
      revision: "sample-ev-1",
    },
    actions: [
      {
        id: "sample-approve",
        kind: "approve",
        label: "Approve (sample UI only)",
        enabled: false,
      },
      {
        id: "sample-deny",
        kind: "deny",
        label: "Deny (sample UI only)",
        enabled: false,
      },
    ],
    note: "Sample approval chrome · decisions disabled · not a Host gate id",
  };
}

export function hostDataLooksEmpty(input: {
  readonly activityRows?: number;
  readonly monitoringFleet?: number;
  readonly notificationItems?: number;
  readonly costKpis?: number;
}): boolean {
  const a = input.activityRows ?? 0;
  const m = input.monitoringFleet ?? 0;
  const n = input.notificationItems ?? 0;
  const c = input.costKpis ?? 0;
  return a + m + n + c === 0;
}

/** Knowledge Management Hub samples (video domain corpus demos). */
export function applyKnowledgeSamples(
  base: KnowledgeLandingView,
): KnowledgeLandingView {
  return {
    ...base,
    description:
      "Sample knowledge collections (video pack demos). Toggle ▦ to hide. Not Host sources.",
    collections: [
      {
        id: "sample-video-corpus",
        name: "Video Corpus (sample)",
        scope: "common",
        health: "healthy",
        healthLabel: "Sample",
        chunks: "420",
        syncDetail: "Sample · not Host sync",
        bindingKinds: ["rag", "few-shot", "benchmark"],
      },
      {
        id: "sample-wuxia-lore",
        name: "Wuxia Lore (sample)",
        scope: "business",
        health: "healthy",
        healthLabel: "Sample",
        chunks: "88",
        syncDetail: "Sample · bilingual EN/繁 demo",
        bindingKinds: ["rag", "continuity"],
      },
      {
        id: "sample-hooks",
        name: "Hook library (sample)",
        scope: "business",
        health: "reindexing",
        healthLabel: "Sample reindex",
        chunks: "36",
        syncDetail: "Sample only · hide with ▦",
        bindingKinds: ["rag", "correction"],
      },
    ],
    selectedCollectionId: "sample-video-corpus",
    sources: [
      {
        id: "ss1",
        name: "wuxia_hooks_2026.md",
        type: "markdown",
        status: "indexed",
        chunks: "88",
        license: "sample reference",
        bindingKind: "rag",
      },
      {
        id: "ss2",
        name: "trend_dataset.csv",
        type: "dataset",
        status: "indexed",
        chunks: "120",
        license: "sample validated",
        bindingKind: "benchmark",
      },
      {
        id: "ss3",
        name: "production_wiki (sample)",
        type: "git",
        status: "synced",
        chunks: "64",
        license: "sample workspace",
        bindingKind: "rag",
      },
    ],
    searchQuery: "strong opening hook for wuxia short",
    searchHits: [
      {
        id: "sh1",
        score: "0.94",
        snippet:
          "Hook lands when first 3 seconds establish stakes and motion… (sample)",
        metadata: "wuxia_hooks_2026.md · sample chunk",
      },
      {
        id: "sh2",
        score: "0.88",
        snippet: "Trend filters for short-form hooks… (sample)",
        metadata: "trend_dataset.csv · sample",
      },
    ],
    contributions: [
      {
        id: "sc1",
        title: "Sample contribution · verified run insight",
        detail: "Demo only · not Host queue",
        verification: "sample · not auto-promoted",
      },
    ],
    syncJobs: [
      {
        id: "sj1",
        label: "Git · Video Corpus (sample)",
        status: "ok",
        note: "Sample schedule · not Host",
      },
    ],
    retrievalTrace: [
      "sample retrieve · redacted",
      "source: wuxia_hooks_2026.md",
      "Host memory API not claimed",
    ],
    searchResultNote: "Sample search hits · toggle ▦ to hide",
    footerNote:
      "Knowledge samples · video corpus demos · hide with ▦ · Host GET /api/v1/knowledge/sources when live.",
  };
}
