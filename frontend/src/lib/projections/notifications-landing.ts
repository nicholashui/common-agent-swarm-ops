/**
 * Local Notifications Center fixture for ui_12_notifications.md / .svg.
 * Presentation-only until notification projections and delivery connect.
 * Payloads carry redacted summaries only — no secrets or approval ops.
 */

export type NotificationPriority = "high" | "normal" | "low";
export type NotificationKind =
  | "gate"
  | "anomaly"
  | "proposal"
  | "swarm"
  | "common"
  | "budget"
  | "critique"
  | "rollout";

export interface NotificationItem {
  readonly id: string;
  readonly kind: NotificationKind;
  readonly priority: NotificationPriority;
  readonly title: string;
  readonly body: string;
  readonly meta: string;
  readonly unread: boolean;
  readonly group: "today-high" | "earlier";
  readonly actions: readonly {
    readonly id: string;
    readonly label: string;
    readonly href?: string;
    readonly primary?: boolean;
  }[];
  readonly gateDetail?: string;
}

export interface NotificationPreference {
  readonly id: string;
  readonly label: string;
  readonly enabled: boolean;
}

export interface NotificationChannel {
  readonly id: string;
  readonly label: string;
  readonly enabled: boolean;
}

export interface NotificationsLandingView {
  readonly title: string;
  readonly description: string;
  readonly badgeCount: number;
  readonly filters: readonly string[];
  readonly items: readonly NotificationItem[];
  readonly notifyAbout: readonly NotificationPreference[];
  readonly channels: readonly NotificationChannel[];
  readonly quietHours: string;
  readonly safetyNote: string;
  readonly footerNote: string;
}

export const LOCAL_NOTIFICATIONS_LANDING: NotificationsLandingView = {
  title: "Notifications Center",
  description:
    "Actionable, centralized alerts · redacted summaries with server-authorized deep links.",
  badgeCount: 7,
  filters: ["All (7)", "Proposals", "Rollouts", "Gates", "Anomalies"],
  items: [
    {
      id: "n1",
      kind: "gate",
      priority: "high",
      title: "Approval gate ready · ReportAgent v3.0 rollout",
      body: "L1 pass · L2 rubric 0.94 · GateKeeper evidence attached · affects 19 swarms.",
      meta: "Expires 8m · corr b7f2c9d0 · unread",
      unread: true,
      group: "today-high",
      gateDetail:
        "Criteria: L1/L2 pass · assignment: workspace operators · expiration in 8m",
      actions: [
        { id: "approve", label: "Approve", primary: true },
        { id: "review", label: "Review", href: "/evaluations" },
      ],
    },
    {
      id: "n2",
      kind: "anomaly",
      priority: "high",
      title: "Anomaly · error spike after ReportAgent v2.1",
      body: "Error rate ↑ in 3 swarms · rollback recommended.",
      meta: "as_of 04:12Z · corr b7f2c9d0",
      unread: true,
      group: "today-high",
      actions: [
        { id: "rollback", label: "Rollback", primary: true },
        { id: "traces", label: "Traces", href: "/operations" },
      ],
    },
    {
      id: "n3",
      kind: "proposal",
      priority: "normal",
      title: "New improvement proposal · CommonMarketPredictor v2.5",
      body: "meta-critic assisted · +3.2% success · awaiting review.",
      meta: "Earlier today · unread",
      unread: true,
      group: "earlier",
      actions: [
        { id: "review-proposal", label: "Review proposal →", href: "/evaluations" },
      ],
    },
    {
      id: "n4",
      kind: "swarm",
      priority: "normal",
      title: "Swarm failed · LegacyModernizer",
      body: "manual_recovery_required · escalation available",
      meta: "Earlier today · recoverable error",
      unread: true,
      group: "earlier",
      actions: [
        { id: "canvas", label: "View in Canvas →", href: "/canvas" },
      ],
    },
    {
      id: "n5",
      kind: "common",
      priority: "low",
      title: "Common improved · VerifierNode v3.0 merged",
      body: "+12% pass rate · your 8 swarms can update.",
      meta: "Earlier today · read",
      unread: false,
      group: "earlier",
      actions: [
        { id: "update", label: "Update to latest", primary: true },
      ],
    },
    {
      id: "n6",
      kind: "critique",
      priority: "normal",
      title: "Directed critique resolved · SynthesisAgent",
      body: "Severity major · evidence ref only · resolution: accepted",
      meta: "Earlier today · unread",
      unread: true,
      group: "earlier",
      actions: [
        { id: "detail", label: "Open agent detail →", href: "/registry/agents/local-preview" },
      ],
    },
    {
      id: "n7",
      kind: "budget",
      priority: "normal",
      title: "Budget threshold · TradingResearch α",
      body: "Cost band warning · redacted burn rate · no secrets in payload",
      meta: "Earlier today · unread",
      unread: true,
      group: "earlier",
      actions: [
        { id: "activity", label: "Open activity →", href: "/activity" },
      ],
    },
  ],
  notifyAbout: [
    { id: "swarm-failures", label: "Swarm failures", enabled: true },
    { id: "proposals", label: "Improvement proposals", enabled: true },
    { id: "rollouts", label: "Rollout impacts", enabled: true },
    { id: "cost", label: "Cost alerts", enabled: true },
    { id: "gates", label: "Approval gates", enabled: true },
  ],
  channels: [
    { id: "in-app", label: "In-app", enabled: true },
    { id: "email", label: "Email", enabled: true },
    { id: "telegram", label: "Telegram", enabled: true },
    { id: "slack", label: "Slack", enabled: false },
    { id: "pwa", label: "PWA push", enabled: true },
  ],
  quietHours: "22:00 – 08:00 · daily digest at 09:00",
  safetyNote:
    "Payloads carry no approval op or secret · actions call authorized commands. Delivery channels receive redacted summaries only.",
  footerNote:
    "Local preview notifications · deep links resolve through authorized opaque references · mark read / snooze / channel prefs require authorized preference actions.",
};
