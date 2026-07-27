/**
 * @duty IconControl — labelled icon-only button
 * @role Icon button with required accessible name from ICON_CONTROL_LABELS.
 * @controls One button (type=button) with aria-label; icon children aria-hidden.
 * @must Always set aria-label from kind; never icon without text alternative.
 * @mustnot Omit accessible name.
 * @redesign docs/frontend_redesign/component_duty_catalog.md §3.2
 */
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
export function IconControl({ kind, children, className, onClick, ...buttonProps }: IconControlProps): JSX.Element {
  const controlClassName = className === undefined ? "icon-control" : `icon-control ${className}`;
  return <button
    {...buttonProps}
    aria-label={getIconControlLabel(kind)}
    className={controlClassName}
    onClick={onClick}
    type="button"
  >
    <span aria-hidden="true">{children}</span>
  </button>;
}
