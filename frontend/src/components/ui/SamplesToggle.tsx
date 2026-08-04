"use client";

/**
 * Compact ▦ control to show/hide local demo samples on Operate (and similar) screens.
 */
import React from "react";

export function SamplesToggle({
  show,
  onToggle,
  labelShow = "Show samples",
  labelHide = "Hide samples",
  className = "",
}: {
  readonly show: boolean;
  readonly onToggle: () => void;
  readonly labelShow?: string;
  readonly labelHide?: string;
  readonly className?: string;
}): JSX.Element {
  return (
    <button
      aria-label={show ? labelHide : labelShow}
      aria-pressed={show}
      className={
        show
          ? `samples-toggle samples-toggle--on ${className}`.trim()
          : `samples-toggle ${className}`.trim()
      }
      onClick={onToggle}
      title={show ? labelHide : labelShow}
      type="button"
    >
      <span aria-hidden="true">▦</span>
    </button>
  );
}

export function SamplesBanner({
  children,
}: {
  readonly children: React.ReactNode;
}): JSX.Element {
  return (
    <p className="samples-banner" role="status">
      {children}
    </p>
  );
}
