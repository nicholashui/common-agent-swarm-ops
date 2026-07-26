"use client";

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
