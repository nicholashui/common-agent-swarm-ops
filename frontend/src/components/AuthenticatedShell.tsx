import type { ReactNode } from "react";

import { SessionBoundary } from "../lib/session/SessionBoundary";
import { getServerSessionSignal } from "../lib/session/server-session";
import { DemoModeBanner } from "./DemoModeBanner";
import { ShellNavigation } from "./ShellNavigation";

export function AuthenticatedShell({
  children,
}: Readonly<{ children: ReactNode }>): JSX.Element {
  const sessionSignal = getServerSessionSignal();
  const menuProjection = {
    workspaceName: sessionSignal.workspaceLabel ?? "Returned workspace",
    workspaceScopeLabel: sessionSignal.demo
      ? "Demo session scope"
      : sessionSignal.email
        ? `Signed in as ${sessionSignal.email}`
        : "Authorized session scope",
    environmentLabel: sessionSignal.demo ? "demo" : undefined,
    connectionStateLabel: sessionSignal.demo ? "Demo" : "Local session",
    connectionDetail: sessionSignal.demo
      ? "Status: demo workspace · local preview projections"
      : "Status: local session · projections pending backend",
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
