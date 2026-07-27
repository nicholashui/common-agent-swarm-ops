/**
 * @duty AppShell — top-level authenticated chrome wrapper
 * @role Delegate to AuthenticatedShell for navigation chrome and bound screen outlet.
 * @controls None of its own; hosts shell navigation and children.
 * @must Remain a thin wrapper with no business authority.
 * @mustnot Invent host actions or store credentials.
 * @redesign docs/frontend_redesign/ui_00_menu.md; component_duty_catalog.md §3.1
 */
import type { ReactNode } from "react";

import { AuthenticatedShell } from "./AuthenticatedShell";

export function AppShell({ children }: Readonly<{ children: ReactNode }>): JSX.Element {
  return <AuthenticatedShell>{children}</AuthenticatedShell>;
}
