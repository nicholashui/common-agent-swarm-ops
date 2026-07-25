import type { ReactNode } from "react";

import { AuthenticatedShell } from "./AuthenticatedShell";

export function AppShell({ children }: Readonly<{ children: ReactNode }>): JSX.Element {
  return <AuthenticatedShell>{children}</AuthenticatedShell>;
}
