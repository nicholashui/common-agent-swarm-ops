/**
 * @duty AuthenticatedShell — host chrome for authorized workspace
 * @role Provide navigation, workspace label, demo banner, and outlet for bound screens.
 * @controls Shell navigation only; screen content supplies its own actions.
 * @must Require an authenticated session; redirect anonymous users to /login.
 * @must Reflect server/session signals; never fabricate tenancy or health probes.
 * @mustnot Enable production activation or store API secrets.
 * @redesign docs/frontend_redesign/ui_00_menu.md; component_duty_catalog.md §3.1
 */
import type { ReactNode } from "react";
import { redirect } from "next/navigation";

import { SessionBoundary } from "../lib/session/SessionBoundary";
import { getServerSessionSignal } from "../lib/session/server-session";
import { DemoModeBanner } from "./DemoModeBanner";
import { ShellNavigation } from "./ShellNavigation";

export function AuthenticatedShell({
  children,
}: Readonly<{ children: ReactNode }>): JSX.Element {
  const sessionSignal = getServerSessionSignal();

  // Fail-closed browser gate: AppShell routes require a signed session cookie.
  // Public entry remains /login (and /api/auth/*) only.
  if (sessionSignal.state !== "authenticated") {
    redirect("/login");
  }

  const menuProjection = {
    workspaceName: sessionSignal.workspaceLabel ?? "Returned workspace",
    workspaceScopeLabel: sessionSignal.demo
      ? "Demo session scope"
      : sessionSignal.email
        ? `Signed in as ${sessionSignal.email}`
        : "Authorized session scope",
    environmentLabel: sessionSignal.demo ? "demo" : undefined,
    connectionStateLabel: sessionSignal.demo ? "Demo" : "Signed in",
    connectionDetail: sessionSignal.demo
      ? "Status: demo workspace · local preview projections"
      : `Status: signed in · ${sessionSignal.email ?? "session"}`,
  };

  return (
    <ShellNavigation menuProjection={menuProjection}>
      <SessionBoundary signal={sessionSignal}>
        {sessionSignal.demo ? <DemoModeBanner /> : null}
        {children}
      </SessionBoundary>
    </ShellNavigation>
  );
}
