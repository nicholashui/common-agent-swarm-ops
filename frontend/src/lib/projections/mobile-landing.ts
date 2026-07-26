/**
 * Local Mobile / PWA Companion fixture for ui_17_mobile.md / .svg.
 * Presentation-only. Read-heavy, action-oriented; redacted summaries.
 * Approvals use server-issued IDs — no embedded approval ops in payloads.
 */

export type MobileTabId =
  | "home"
  | "activity"
  | "compose"
  | "registry"
  | "more";

export interface MobileRunningSwarm {
  readonly id: string;
  readonly name: string;
  readonly status: string;
  readonly statusTone: "running" | "live" | "blocked";
  readonly pattern: string;
  readonly meta: string;
  readonly canvasHref: string;
  readonly blockedReason?: string;
}

export interface MobileNotification {
  readonly id: string;
  readonly kind: "gate" | "anomaly" | "critique";
  readonly title: string;
  readonly body: string;
  readonly meta: string;
  readonly actions: readonly {
    readonly id: string;
    readonly label: string;
    readonly href?: string;
    readonly primary?: boolean;
  }[];
  readonly highRisk?: boolean;
}

export interface MobileActivityItem {
  readonly id: string;
  readonly title: string;
  readonly status: string;
  readonly version: string;
  readonly meta: string;
  readonly lifecycle: string;
}

export interface MobileLandingView {
  readonly brand: string;
  readonly workspaceLabel: string;
  readonly timeLabel: string;
  readonly liveSummary: string;
  readonly stats: readonly { readonly id: string; readonly label: string; readonly value: string }[];
  readonly runningSwarms: readonly MobileRunningSwarm[];
  readonly notifications: readonly MobileNotification[];
  readonly activity: readonly MobileActivityItem[];
  readonly registryHits: readonly {
    readonly id: string;
    readonly name: string;
    readonly version: string;
    readonly metric: string;
  }[];
  readonly offlineNote: string;
  readonly safetyNote: string;
  readonly footerNote: string;
}

export const LOCAL_MOBILE_LANDING: MobileLandingView = {
  brand: "caso",
  workspaceLabel: "Trading Lab",
  timeLabel: "9:41",
  liveSummary: "Live · 6 running · 92% success",
  stats: [
    { id: "running", label: "Running", value: "6" },
    { id: "burn", label: "Cost burn", value: "$0.20/min" },
  ],
  runningSwarms: [
    {
      id: "s1",
      name: "TradingResearch α",
      status: "Running",
      statusTone: "running",
      pattern: "Parallel + Verify v1.4",
      meta: "8/8 latest · elapsed 12m · $0.14/min",
      canvasHref: "/canvas",
    },
    {
      id: "s2",
      name: "ContentPipeline β",
      status: "Live",
      statusTone: "live",
      pattern: "Hierarchical v2.0",
      meta: "5/5 latest · elapsed 4m · $0.06/min",
      canvasHref: "/canvas",
    },
  ],
  notifications: [
    {
      id: "n1",
      kind: "gate",
      title: "Approval gate",
      body: "ReportAgent v3.0 · 19 swarms",
      meta: "8m left · L1 pass · L2 0.94 · gate criteria returned",
      actions: [
        { id: "approve", label: "Approve", primary: true },
        { id: "review", label: "Review", href: "/evaluations" },
      ],
    },
    {
      id: "n2",
      kind: "anomaly",
      title: "Error spike · ReportAgent v2.1",
      body: "3 swarms affected · tap to rollback",
      meta: "Rollback eligibility: server-determined",
      highRisk: false,
      actions: [
        { id: "rollback", label: "Rollback", primary: true },
        { id: "traces", label: "Traces", href: "/operations" },
      ],
    },
    {
      id: "n3",
      kind: "critique",
      title: "Critique severity major",
      body: "waiting_for_critique · SynthesisAgent",
      meta: "Evidence ref only · resolution open",
      actions: [
        {
          id: "detail",
          label: "Open detail",
          href: "/registry/agents/local-preview",
        },
      ],
    },
  ],
  activity: [
    {
      id: "a1",
      title: "TradingResearch α",
      status: "Success",
      version: "VerifierNode Common v3.0",
      meta: "12s · redacted metrics",
      lifecycle: "complete · graph rev r-18",
    },
    {
      id: "a2",
      title: "ContentPipeline β",
      status: "Blocked",
      version: "ReportAgent Common v2.1",
      meta: "missing approval · gate g-44",
      lifecycle: "blocked · retry eligible",
    },
    {
      id: "a3",
      title: "OpsBrief ε",
      status: "Self-refine",
      version: "VerifierNode Common v3.0",
      meta: "iter 2/5 · L2 in progress",
      lifecycle: "self_refine",
    },
  ],
  registryHits: [
    {
      id: "r1",
      name: "VerifierNode",
      version: "Common v3.0",
      metric: "97% · High Verify",
    },
    {
      id: "r2",
      name: "DataFetcher",
      version: "Common v2.1",
      metric: "94% · 12.4k runs",
    },
  ],
  offlineNote:
    "Offline cache (recent activity, registry search) is reserved for PWA service worker — local preview only.",
  safetyNote:
    "Mobile summaries remain redacted. Approval and recovery actions use the same server-issued IDs and evidence views as desktop. High-risk signals: blocked reason, lifecycle, gate criteria, L1/L2/L3, critique severity, artifact QC/rights/provenance alerts, rollback/retry eligibility.",
  footerNote:
    "Local preview mobile companion · bottom nav 44px+ targets · canvas stays deep-link / read-only on mobile. Push permission and service worker not enabled in this preview.",
};
