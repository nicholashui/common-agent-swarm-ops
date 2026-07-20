import type { ReactNode } from "react";

import type { RunStatus } from "../lib/demo-data";

export function StatusBadge({ status }: { readonly status: RunStatus }): JSX.Element {
  return <span className={`status status--${status}`}><span aria-hidden="true">{status === "running" ? "◌" : status === "success" ? "✓" : status === "error" ? "!" : "Ⅱ"}</span>{status}</span>;
}

export function VersionPill({ version, label = "Common" }: { readonly version: string; readonly label?: string }): JSX.Element {
  return <span className="version-pill">{label} v{version}</span>;
}

export function PageHeader({ eyebrow, title, description, actions }: { readonly eyebrow: string; readonly title: string; readonly description: string; readonly actions?: ReactNode }): JSX.Element {
  return <header className="page-header"><div><p className="eyebrow">{eyebrow}</p><h1>{title}</h1><p className="lede">{description}</p></div>{actions ? <div className="page-actions">{actions}</div> : null}</header>;
}

export function MetricCard({ label, value, detail, tone = "indigo" }: { readonly label: string; readonly value: string; readonly detail: string; readonly tone?: "indigo" | "green" | "amber" | "violet" }): JSX.Element {
  return <article className={`metric-card metric-card--${tone}`}><p>{label}</p><strong>{value}</strong><span>{detail}</span></article>;
}

export function EmptyState({ title, children }: { readonly title: string; readonly children: ReactNode }): JSX.Element {
  return <div className="empty-state"><span aria-hidden="true">✦</span><h2>{title}</h2><p>{children}</p></div>;
}
