"use client";

/**
 * @duty OperationalAnnouncer — operational status transition announcer
 * @role Announce resource state changes for assistive tech without sensitive payloads.
 * @controls None (visually optional; polite live region).
 * @must Announce only on transition key change.
 * @mustnot Embed credentials, raw traces, or provider internals.
 * @redesign docs/frontend_redesign/component_duty_catalog.md §3.2; Req 8.4
 */
import React, { useEffect, useRef, useState } from "react";

export interface OperationalAnnouncement {
  readonly resourceName: string;
  readonly stateLabel: string;
  readonly asOf: string;
}

export interface OperationalAnnouncerProps extends OperationalAnnouncement {
  readonly className?: string;
}

export function formatOperationalAnnouncement({ resourceName, stateLabel, asOf }: OperationalAnnouncement): string {
  return `${resourceName}: ${stateLabel}; updated ${asOf}`;
}

export function operationalStatusTransitionKey({ resourceName, stateLabel }: OperationalAnnouncement): string {
  return `${resourceName}\u0000${stateLabel}`;
}

export interface OperationalAnnouncementTransition {
  readonly transitionKey: string;
  readonly announcement: string | null;
}

/** Returns one announcement only when a caller-provided state transition changes. */
export function nextOperationalAnnouncement(
  previousTransitionKey: string | null,
  current: OperationalAnnouncement,
): OperationalAnnouncementTransition {
  const transitionKey = operationalStatusTransitionKey(current);
  return {
    transitionKey,
    announcement: previousTransitionKey === null || previousTransitionKey === transitionKey
      ? null
      : formatOperationalAnnouncement(current),
  };
}

/** Announces each changed, caller-provided operational state exactly once. */
export function OperationalAnnouncer({ resourceName, stateLabel, asOf, className }: OperationalAnnouncerProps): JSX.Element {
  const previousTransition = useRef<string | null>(null);
  const [announcement, setAnnouncement] = useState("");

  useEffect((): void => {
    const next = nextOperationalAnnouncement(previousTransition.current, { resourceName, stateLabel, asOf });
    previousTransition.current = next.transitionKey;
    if (next.announcement !== null) setAnnouncement(next.announcement);
  }, [resourceName, stateLabel, asOf]);

  const regionClassName = className === undefined ? "visually-hidden" : `visually-hidden ${className}`;
  return <span role="status" aria-live="polite" aria-atomic="true" className={regionClassName}>{announcement}</span>;
}
