/**
 * @duty DesignSystemPrimitives — redesign visual system atoms
 * @role DesignStatusPill / DesignCommonBadge aligned to common-style.html.
 * @controls None (spans/pills only).
 * @must Pair status text with color; never status by color alone.
 * @mustnot Encode authorization or live provider claims.
 * @redesign docs/frontend_redesign/component_duty_catalog.md §3.2; common-style.html
 *
 * Shared visual primitives aligned to docs/frontend_redesign/common-style.html.
 * Status always pairs text label with color; Common badge uses indigo mono treatment.
 */

import React from "react";

export type DesignStatusKind =
  | "live"
  | "running"
  | "queued"
  | "self_refine"
  | "delayed"
  | "reconnecting"
  | "degraded"
  | "failed"
  | "error"
  | "recovery"
  | "blocked"
  | "manual_recovery_required"
  | "complete"
  | "success"
  | "done"
  | "unavailable"
  | "stale"
  | "cancelled"
  | "idle";

const STATUS_LABELS: Readonly<Record<DesignStatusKind, string>> = {
  live: "Live",
  running: "Running",
  queued: "Queued",
  self_refine: "Self-Refining",
  delayed: "Delayed",
  reconnecting: "Reconnecting",
  degraded: "Degraded",
  failed: "Failed",
  error: "Error",
  recovery: "Recovery",
  blocked: "Blocked",
  manual_recovery_required: "Recovery required",
  complete: "Complete",
  success: "Success",
  done: "Done",
  unavailable: "Unavailable",
  stale: "Stale",
  cancelled: "Cancelled",
  idle: "Idle",
};

const PULSE_STATUSES = new Set<DesignStatusKind>([
  "live",
  "running",
  "self_refine",
  "reconnecting",
  "recovery",
  "manual_recovery_required",
]);

export function DesignStatusPill({
  status,
  label,
}: Readonly<{
  status: DesignStatusKind | string;
  label?: string;
}>): JSX.Element {
  const kind = (
    status in STATUS_LABELS ? status : "stale"
  ) as DesignStatusKind;
  const text = label ?? STATUS_LABELS[kind];
  const pulse = PULSE_STATUSES.has(kind);

  return (
    <span className={`ds-status ds-status--${kind}`}>
      <span
        aria-hidden="true"
        className={
          pulse ? "ds-status__dot ds-status__dot--pulse" : "ds-status__dot"
        }
      />
      <span className="visually-hidden">Status: </span>
      {text}
    </span>
  );
}

export function DesignCommonBadge({
  version,
  runs,
  success,
}: Readonly<{
  version: string;
  runs?: string;
  success?: string;
}>): JSX.Element {
  return (
    <span className="ds-common-badge">
      <span className="ds-common-badge__label">Common</span>
      <span>v{version.replace(/^v/i, "")}</span>
      {runs ? <span className="ds-common-badge__meta">· {runs}</span> : null}
      {success ? (
        <span className="ds-common-badge__meta">· {success}</span>
      ) : null}
    </span>
  );
}
