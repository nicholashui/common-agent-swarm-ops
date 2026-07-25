"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ReactNode } from "react";

const navigation = [
  ["Overview", "/"], ["Registry", "/registry"], ["Composer", "/composer"], ["Canvas", "/canvas"], ["Activity", "/activity"],
] as const;

export function ShellNavigation({ children }: Readonly<{ children: ReactNode }>): JSX.Element {
  const pathname = usePathname();
  return <div className="app-shell"><a className="skip-link" href="#main-content">Skip to main content</a><header className="topbar"><Link className="brand" href="/"><span className="brand-mark">◈</span><span>common<span>/</span>swarm</span></Link><div className="topbar-actions"><Link className="icon-button" href="/notifications" aria-label="Notifications">◌<span className="notification-dot" /></Link><Link className="avatar" href="/profile" aria-label="Open profile">NH</Link></div></header><div className="workspace"><aside className="sidebar"><nav aria-label="Main navigation">{navigation.map(([label, href]) => <Link className={pathname === href ? "nav-link nav-link--active" : "nav-link"} href={href} key={href}><span aria-hidden="true">{label === "Overview" ? "◫" : label === "Registry" ? "◇" : label === "Composer" ? "✦" : label === "Canvas" ? "⌘" : "◴"}</span>{label}</Link>)}</nav><div className="sidebar-bottom"><Link className="nav-link" href="/operations"><span aria-hidden="true">◉</span>Operator console</Link><p>Control plane · v2.0</p></div></aside><main className="app-main" id="main-content">{children}</main></div><div aria-atomic="true" aria-live="polite" className="visually-hidden" id="operational-live-region" role="status" /></div>;
}
