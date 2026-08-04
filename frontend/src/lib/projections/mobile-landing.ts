/**
 * Local Mobile / PWA Companion fixture for ui_17_mobile.md / .svg.
 * Presentation-only. Read-heavy, action-oriented; redacted summaries.
 * Approvals use server-issued IDs — no embedded approval ops in payloads.
 */

import type { ScreenLabels } from "./screen-labels";

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

export interface MobileTabItem {
  readonly id: MobileTabId;
  readonly label: string;
  readonly href?: string;
}

export interface MobileLandingView {
  readonly labels: ScreenLabels;
  readonly brand: string;
  readonly workspaceLabel: string;
  readonly timeLabel: string;
  readonly liveSummary: string;
  readonly tabs: readonly MobileTabItem[];
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
  labels: {
    "compose_opens_the_full_composer_for_guided_creat": "Plan opens guided creation from common patterns.",
    "your_swarms": "Your Swarms",
    "notifications": "Notifications",
    "quick_actions": "Quick Actions",
    "activity_feed": "Activity Feed",
    "registry_quick_search": "Registry Quick Search",
    "search_commons": "Search commons",
    "more": "More",
    "profile": "Profile",
    "monitoring": "Monitoring",
    "settings": "Settings",
    "help_onboarding": "Help & Onboarding",
    "pwa": "PWA",
    "search_commons_2": "Search commons…",
    "mobile_companion": "Mobile companion",
    "phone_preview": "Phone preview",
    "notifications_3_unread": "Notifications, 3 unread",
    "action_sheet": "Action sheet",
    "mobile_bottom_navigation": "Mobile bottom navigation",
  },
  brand: "caso",
  workspaceLabel: "Video Studio",
  timeLabel: "9:41",
  liveSummary: "Live · 6 running · 92% success",
  tabs: [
    { id: "home", label: "Home" },
    { id: "activity", label: "Activity" },
    { id: "compose", label: "Plan", href: "/composer" },
    { id: "registry", label: "Registry" },
    { id: "more", label: "More" },
  ],
  stats: [
    { id: "running", label: "Running", value: "6" },
    { id: "burn", label: "Cost burn", value: "$0.20/min" },
  ],
  runningSwarms: [
    {
      id: "s1",
      name: "Wuxia Short",
      status: "Running",
      statusTone: "running",
      pattern: "Parallel + Verify v1.4",
      meta: "8/8 latest · elapsed 12m · $0.14/min",
      canvasHref: "/canvas",
    },
    {
      id: "s2",
      name: "Brand Spot",
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
      body: "video.editor v3.0 · 19 swarms",
      meta: "8m left · L1 pass · L2 0.94 · gate criteria returned",
      actions: [
        { id: "approve", label: "Approve", primary: true },
        { id: "review", label: "Review", href: "/evaluations" },
      ],
    },
    {
      id: "n2",
      kind: "anomaly",
      title: "Error spike · video.editor v2.1",
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
      body: "waiting_for_critique · video.screenwriter",
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
      title: "Wuxia Short",
      status: "Success",
      version: "video.judge Common v3.0",
      meta: "12s · redacted metrics",
      lifecycle: "complete · graph rev r-18",
    },
    {
      id: "a2",
      title: "Brand Spot",
      status: "Blocked",
      version: "video.editor Common v2.1",
      meta: "missing approval · gate g-44",
      lifecycle: "blocked · retry eligible",
    },
    {
      id: "a3",
      title: "OpsBrief ε",
      status: "Self-refine",
      version: "video.judge Common v3.0",
      meta: "iter 2/5 · L2 in progress",
      lifecycle: "self_refine",
    },
  ],
  registryHits: [
    {
      id: "r1",
      name: "video.judge",
      version: "Common v3.0",
      metric: "97% · High Verify",
    },
    {
      id: "r2",
      name: "video.webresearch",
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
