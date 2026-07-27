"use client";

/**
 * @duty InteractionStatusBar — action feedback live region
 * @role Display InteractionStatus (busy/success/error/info) with optional correlation id.
 * @controls None (display-only).
 * @must Use aria-live; role=alert for errors.
 * @mustnot Show tokens, secrets, or raw provider payloads.
 * @redesign docs/frontend_redesign/component_duty_catalog.md §3.2
 */
import type { InteractionStatus } from "../../lib/ui/interaction-runtime";

export function InteractionStatusBar({
  status,
}: Readonly<{ status: InteractionStatus }>): JSX.Element | null {
  if (status.kind === "idle" || status.message.length === 0) return null;
  const role = status.kind === "error" ? "alert" : "status";
  return (
    <p
      aria-live="polite"
      className={`interaction-status interaction-status--${status.kind}`}
      role={role}
    >
      {status.message}
      {status.correlationId ? (
        <span className="interaction-status__corr"> · {status.correlationId}</span>
      ) : null}
    </p>
  );
}
