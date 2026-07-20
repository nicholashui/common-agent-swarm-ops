"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ReactNode } from "react";

const navigation = [
  ["Overview", "/"], ["Registry", "/registry"], ["Composer", "/composer"], ["Canvas", "/canvas"], ["Activity", "/activity"],
] as const;

export function AppShell({ children }: { readonly children: ReactNode }): JSX.Element {
  const pathname = usePathname();
  return <div className="app-shell"><header className="topbar"><Link className="brand" href="/"><span className="brand-mark">◈</span><span>common<span>/</span>swarm</span></Link><button className="workspace-switcher" type="button" aria-label="Select workspace">Trading Lab <span>⌄</span></button><button className="command-trigger" type="button" aria-label="Open command palette"><kbd>Ctrl K</kbd><span>Search commons, swarms, and actions</span></button><div className="topbar-actions"><button className="icon-button" type="button" aria-label="Notifications">◌<span className="notification-dot" /></button><button className="avatar" type="button" aria-label="Open profile">NH</button></div></header><div className="workspace"><aside className="sidebar"><nav aria-label="Main navigation">{navigation.map(([label, href]) => <Link className={pathname === href ? "nav-link nav-link--active" : "nav-link"} href={href} key={href}><span aria-hidden="true">{label === "Overview" ? "◫" : label === "Registry" ? "◇" : label === "Composer" ? "✦" : label === "Canvas" ? "⌘" : "◴"}</span>{label}</Link>)}</nav><div className="sidebar-bottom"><Link className="nav-link" href="/operations"><span aria-hidden="true">◉</span>Operator console</Link><p>Control plane · v2.0</p></div></aside><main className="app-main">{children}</main></div></div>;
}
