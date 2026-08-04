"use client";

import type { ReactNode } from "react";

import { TooltipProvider } from "./tooltip";

/** Root provider: instant open (0ms) for shadcn-style tooltips. */
export function AppTooltipProvider({
  children,
}: {
  readonly children: ReactNode;
}): JSX.Element {
  return <TooltipProvider delayDuration={0}>{children}</TooltipProvider>;
}
