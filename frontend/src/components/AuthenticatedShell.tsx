import type { ReactNode } from "react";

import { SessionBoundary } from "../lib/session/SessionBoundary";
import { getServerSessionSignal } from "../lib/session/server-session";
import { ShellNavigation } from "./ShellNavigation";

export function AuthenticatedShell({ children }: Readonly<{ children: ReactNode }>): JSX.Element {
  const sessionSignal = getServerSessionSignal();
  return <ShellNavigation><SessionBoundary signal={sessionSignal}>{children}</SessionBoundary></ShellNavigation>;
}
