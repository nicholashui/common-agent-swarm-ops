/**
 * Local Governance & Audit Trail fixture for ui_14_audit.md / .svg.
 * Presentation-only. Append-only redacted log — no mutation of history,
 * no private tool parameters, no secret values.
 */

import type { ScreenLabels } from "./screen-labels";

export type AuditActionType =
  | "rollout"
  | "approval"
  | "merge"
  | "rollback"
  | "config"
  | "secret"
  | "gate"
  | "critique"
  | "lifecycle";

export interface AuditLogRow {
  readonly id: string;
  readonly timestamp: string;
  readonly actor: string;
  readonly action: string;
  readonly actionType: AuditActionType;
  readonly target: string;
  readonly summary: string;
  readonly status: "success" | "failure" | "denied";
  readonly statusLabel: string;
  readonly correlationId: string;
  readonly prevHash: string;
  readonly entryHash: string;
  readonly graphRevision?: string;
  readonly commonVersion?: string;
  readonly detailLines: readonly string[];
  readonly links: readonly { readonly label: string; readonly href: string }[];
}

export interface AuditLandingView {
  readonly labels: ScreenLabels;
  readonly eyebrow: string;
  readonly title: string;
  readonly description: string;
  readonly searchPlaceholder: string;
  readonly timeRangeLabel: string;
  readonly actorFilterLabel: string;
  readonly actionTypes: readonly string[];
  readonly integrity: {
    readonly label: string;
    readonly detail: string;
    readonly lastHash: string;
  };
  readonly rows: readonly AuditLogRow[];
  readonly paginationLabel: string;
  readonly reports: readonly string[];
  readonly safetyNote: string;
  readonly footerNote: string;
}

export const LOCAL_AUDIT_LANDING: AuditLandingView = {
  labels: {
    "search_audit_log": "Search audit log",
    "filters": "Filters",
    "time_range": "Time range",
    "actor": "Actor",
    "action_type": "Action type",
    "correlation_id": "Correlation ID",
    "pre_built_reports": "Pre-built reports",
    "timestamp_utc": "Timestamp (UTC)",
    "user_actor": "User / Actor",
    "action": "Action",
    "target": "Target",
    "before_after_summary": "Before / After summary",
    "status": "Status",
    "event_detail": "EVENT DETAIL",
    "timestamp": "Timestamp",
    "reason_summary": "Reason / summary",
    "prev_hash": "Prev hash",
    "entry_hash": "Entry hash",
    "graph_revision": "Graph revision",
    "common_version": "Common version",
    "context_redacted": "Context (redacted)",
    "linked_context": "Linked context",
    "b7f2c9d0": "b7f2c9d0…",
    "governance_and_audit_trail": "Governance and audit trail",
    "audit_filters": "Audit filters",
    "audit_table": "Audit table",
    "event_detail_2": "Event detail",
    "redacted_diff": "Redacted diff",
  },
  eyebrow: "GOVERNANCE & AUDIT",
  title: "Governance & Audit Trail",
  description:
    "Tamper-evident, filterable, exportable · who did what, when, and why.",
  searchPlaceholder: "Search actor, action, correlation ID…",
  timeRangeLabel: "Last 24 hours",
  actorFilterLabel: "All users & system",
  actionTypes: [
    "Rollout",
    "Approval",
    "Merge",
    "Rollback",
    "Config",
    "Secret",
  ],
  integrity: {
    label: "Chain verified",
    detail: "Hash chain intact · 0 gaps",
    lastHash: "last: 9f3a…c21e",
  },
  rows: [
    {
      id: "a1",
      timestamp: "04:12:31",
      actor: "system · GateKeeper",
      action: "rollback.execute",
      actionType: "rollback",
      target: "video.editor v2.1 → v2.0",
      summary: "Rollback after anomaly · 3 swarms affected",
      status: "success",
      statusLabel: "Success",
      correlationId: "b7f2c9d0",
      prevHash: "7c1e…91aa",
      entryHash: "9f3a…c21e",
      graphRevision: "r-22",
      commonVersion: "Common v2.0",
      detailLines: [
        "Reason: error spike post-rollout (redacted metrics)",
        "Lifecycle: terminal recovery transition",
        "Artifact/QC/rights: references only",
        "C2PA/provenance ref: retained (not replaceable)",
        "Observation vs authority: authoritative state transition + signature",
      ],
      links: [
        { label: "Anomaly event (Monitoring)", href: "/operations" },
        { label: "Affected swarms (3)", href: "/activity" },
        { label: "GateKeeper decision", href: "/operations" },
      ],
    },
    {
      id: "a2",
      timestamp: "04:05:02",
      actor: "nicholas@local",
      action: "approval.resolve",
      actionType: "approval",
      target: "video.editor v3.0 rollout gate",
      summary: "L1 pass · L2 0.94 · human decision recorded",
      status: "success",
      statusLabel: "Success",
      correlationId: "b7f2c9d0",
      prevHash: "4b20…ee11",
      entryHash: "7c1e…91aa",
      commonVersion: "Common v3.0",
      detailLines: [
        "Gate criteria + expiration recorded",
        "Quality evidence: L1/L2 (redacted)",
        "Human decision/comment: approved with canary",
      ],
      links: [{ label: "Open evaluations", href: "/evaluations" }],
    },
    {
      id: "a3",
      timestamp: "03:58:44",
      actor: "meta-critic",
      action: "proposal.merge",
      actionType: "merge",
      target: "video.judge v2.9 → v3.0",
      summary: "+12% pass rate · graph rev retained",
      status: "success",
      statusLabel: "Success",
      correlationId: "c1d2e3f4",
      prevHash: "11aa…0099",
      entryHash: "4b20…ee11",
      commonVersion: "Common v3.0",
      graphRevision: "r-19",
      detailLines: [
        "Before/after metrics redacted",
        "Critique record linked",
        "Cannot mutate historical proposal evidence",
      ],
      links: [{ label: "Registry detail", href: "/registry/agents/local-preview" }],
    },
    {
      id: "a4",
      timestamp: "03:41:10",
      actor: "ops@local",
      action: "rollout.canary.start",
      actionType: "rollout",
      target: "video.editor v3.0 · 5 swarms",
      summary: "Canary authorized · traffic split redacted",
      status: "success",
      statusLabel: "Success",
      correlationId: "d4e5f6a7",
      prevHash: "88ff…2200",
      entryHash: "11aa…0099",
      detailLines: [
        "Canary scope: 5 swarms first",
        "Tool parameters: not inferred from audit projection",
      ],
      links: [{ label: "Activity board", href: "/activity" }],
    },
    {
      id: "a5",
      timestamp: "03:22:57",
      actor: "system",
      action: "config.policy.update",
      actionType: "config",
      target: "Version pinning policy",
      summary: "Affects 14 running swarms · redacted diff",
      status: "success",
      statusLabel: "Success",
      correlationId: "e5f6a7b8",
      prevHash: "2200…aabb",
      entryHash: "88ff…2200",
      detailLines: [
        "Diff: structured policy fields only",
        "Observation events separated from authoritative transitions",
      ],
      links: [{ label: "Settings", href: "/settings" }],
    },
    {
      id: "a6",
      timestamp: "02:59:03",
      actor: "system",
      action: "secret.rotate",
      actionType: "secret",
      target: "XAI_API_KEY",
      summary: "Rotated · value never shown",
      status: "success",
      statusLabel: "Success",
      correlationId: "f6a7b8c9",
      prevHash: "aabb…ccdd",
      entryHash: "2200…aabb",
      detailLines: [
        "Secret values redacted forever",
        "Access itself is audited",
      ],
      links: [{ label: "Settings vault", href: "/settings" }],
    },
    {
      id: "a7",
      timestamp: "02:44:18",
      actor: "alex@local",
      action: "export.request",
      actionType: "config",
      target: "Audit export CSV",
      summary: "Denied · insufficient export authorization",
      status: "denied",
      statusLabel: "Denied",
      correlationId: "a7b8c9d0",
      prevHash: "ccdd…eeff",
      entryHash: "aabb…ccdd",
      detailLines: [
        "Full payloads only via authorized export",
        "This denial is itself an audit entry",
      ],
      links: [],
    },
    {
      id: "a8",
      timestamp: "02:30:00",
      actor: "system · orchestrator",
      action: "task.lifecycle.transition",
      actionType: "lifecycle",
      target: "run-4421 · video.judge",
      summary: "self_refine → complete · iter 3/5",
      status: "success",
      statusLabel: "Success",
      correlationId: "a3f9b1c2",
      prevHash: "0001…root",
      entryHash: "ccdd…eeff",
      graphRevision: "r-12",
      commonVersion: "Common v3.0",
      detailLines: [
        "Task/dependency/gate transition recorded",
        "Iteration/retry retained",
        "Tool summary redacted",
        "Artifact parent chain reference only",
      ],
      links: [
        { label: "Trace (Monitoring)", href: "/operations" },
        { label: "Canvas", href: "/canvas" },
      ],
    },
  ],
  paginationLabel:
    "Cursor pagination · 12,480 entries · click a row for full context drawer →",
  reports: [
    "Commons merge & rollback (7d)",
    "Approval gate decisions (24h)",
    "Secret access events (30d)",
    "Failed / denied actions (7d)",
  ],
  safetyNote:
    "Immutable append-only log · redacted values · access itself is audited. Users can inspect diffs and evidence but cannot mutate historical records, replace a C2PA/provenance reference, or infer private tool parameters.",
  footerNote:
    "Local preview audit · Values redacted · full payloads only via authorized export. Export / Verify integrity require authorized compliance actions.",
};
