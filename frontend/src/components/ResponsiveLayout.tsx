import React, { type ReactNode } from "react";

export interface ResponsiveStackProps {
  readonly children: ReactNode;
  readonly className?: string;
}

export interface ResponsiveSplitProps {
  readonly primary: ReactNode;
  readonly secondary: ReactNode;
  readonly className?: string;
}

export interface ResponsiveActionGroupProps {
  readonly children: ReactNode;
  readonly className?: string;
}

function mergeClassName(baseClassName: string, className: string | undefined): string {
  return className === undefined ? baseClassName : `${baseClassName} ${className}`;
}

/** A spacing-only wrapper that preserves the data and controls provided by its caller. */
export function ResponsiveStack({ children, className }: ResponsiveStackProps): JSX.Element {
  return <div className={mergeClassName("responsive-stack", className)}>{children}</div>;
}

/** Keeps both supplied regions in the DOM while CSS adapts their layout for mobile. */
export function ResponsiveSplit({ primary, secondary, className }: ResponsiveSplitProps): JSX.Element {
  return <div className={mergeClassName("responsive-split", className)}>
    <div className="responsive-split__primary">{primary}</div>
    <div className="responsive-split__secondary">{secondary}</div>
  </div>;
}

/** A wrapping action group that changes density only; it does not alter action availability. */
export function ResponsiveActionGroup({ children, className }: ResponsiveActionGroupProps): JSX.Element {
  return <div className={mergeClassName("responsive-action-group", className)}>{children}</div>;
}
