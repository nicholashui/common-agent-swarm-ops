/**
 * @duty design primitives — presentation-only UI atoms
 * @role StatusBadge, VersionPill, PageHeader, MetricCard, EmptyState for screen chrome.
 * @controls Optional actions slot on PageHeader (caller-owned eligibility).
 * @must Pair status text with visual tone; no business authorization.
 * @mustnot Encode host authority or credentials.
 * @redesign docs/frontend_redesign/component_duty_catalog.md §3.2; common-style.html
 */
import React, { type ReactNode } from "react";

import type { RunStatus } from "../lib/demo-data";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "./ui/tooltip";

export function StatusBadge({ status }: { readonly status: RunStatus }): JSX.Element {
  return <span className={`status status--${status}`}><span aria-hidden="true">{status === "running" ? "◌" : status === "success" ? "✓" : status === "error" ? "!" : "Ⅱ"}</span>{status}</span>;
}

export function VersionPill({ version, label = "Common" }: { readonly version: string; readonly label?: string }): JSX.Element {
  return <span className="version-pill">{label} v{version}</span>;
}

/**
 * Explanatory copy as a shadcn-style instant tooltip (ⓘ).
 * delayDuration=0 so the popup shows immediately on hover/focus.
 */
export function InfoTooltip({
  text,
  label = "More information",
  side = "bottom",
}: {
  readonly text: string;
  readonly label?: string;
  readonly side?: "top" | "bottom" | "left" | "right";
}): JSX.Element | null {
  const trimmed = text.trim();
  if (!trimmed) return null;
  // Use a span trigger (asChild) so InfoTooltip can sit inside other buttons
  // without illegal <button> nesting / hydration errors.
  return (
    <Tooltip delayDuration={0}>
      <TooltipTrigger asChild>
        <span
          aria-label={`${label}: ${trimmed}`}
          className="info-tooltip"
          role="button"
          tabIndex={0}
          onKeyDown={(event) => {
            if (event.key === "Enter" || event.key === " ") {
              event.preventDefault();
              (event.currentTarget as HTMLElement).focus();
            }
          }}
        >
          <span aria-hidden="true">ⓘ</span>
        </span>
      </TooltipTrigger>
      <TooltipContent side={side} sideOffset={6}>
        {trimmed}
      </TooltipContent>
    </Tooltip>
  );
}

export function PageHeader({ eyebrow, title, description, actions }: { readonly eyebrow: string; readonly title: string; readonly description: string; readonly actions?: ReactNode }): JSX.Element {
  return (
    <header className="page-header">
      <div>
        {eyebrow ? <p className="eyebrow">{eyebrow}</p> : null}
        <div className="page-title-row">
          <h1>{title}</h1>
          <InfoTooltip label="About this screen" text={description} />
        </div>
      </div>
      {actions ? <div className="page-actions">{actions}</div> : null}
    </header>
  );
}

export function MetricCard({ label, value, detail, tone = "indigo" }: { readonly label: string; readonly value: string; readonly detail: string; readonly tone?: "indigo" | "green" | "amber" | "violet" }): JSX.Element {
  return <article className={`metric-card metric-card--${tone}`}><p>{label}</p><strong>{value}</strong><span>{detail}</span></article>;
}

export function EmptyState({ title, children }: { readonly title: string; readonly children: ReactNode }): JSX.Element {
  return <div className="empty-state"><span aria-hidden="true">✦</span><h2>{title}</h2><p>{children}</p></div>;
}
