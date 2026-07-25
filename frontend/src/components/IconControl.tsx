import React, { type ButtonHTMLAttributes, type ReactNode } from "react";

export const ICON_CONTROL_LABELS = {
  refresh: "Refresh operational projection",
  reconnect: "Reconnect live updates",
  copyCorrelation: "Copy correlation identifier",
  close: "Close",
} as const;

export type IconControlKind = keyof typeof ICON_CONTROL_LABELS;

export interface IconControlProps extends Omit<ButtonHTMLAttributes<HTMLButtonElement>, "aria-label" | "children" | "type"> {
  readonly kind: IconControlKind;
  readonly children: ReactNode;
}

export function getIconControlLabel(kind: IconControlKind): string {
  return ICON_CONTROL_LABELS[kind];
}

/** Renders an icon-only control with one of the required accessible names. */
export function IconControl({ kind, children, className, ...buttonProps }: IconControlProps): JSX.Element {
  const controlClassName = className === undefined ? "icon-control" : `icon-control ${className}`;
  return <button {...buttonProps} aria-label={getIconControlLabel(kind)} className={controlClassName} type="button">
    <span aria-hidden="true">{children}</span>
  </button>;
}
