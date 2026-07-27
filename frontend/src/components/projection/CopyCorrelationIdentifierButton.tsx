"use client";

/**
 * @duty CopyCorrelationIdentifierButton — support copy control
 * @role Copy server-returned correlation id for support; grants no resource access.
 * @controls IconControl button (copyCorrelation).
 * @must Copy only the provided identifier string.
 * @mustnot Fetch resources or embed secrets.
 * @redesign docs/frontend_redesign/component_duty_catalog.md §3.3; Req 8.6
 */
import React from "react";

import { IconControl } from "../IconControl";

export interface CopyCorrelationIdentifierButtonProps {
  readonly correlationIdentifier: string;
}

/** Copies only the correlation identifier returned by the Public API. */
export function CopyCorrelationIdentifierButton({ correlationIdentifier }: CopyCorrelationIdentifierButtonProps): JSX.Element {
  return <IconControl kind="copyCorrelation" onClick={(): void => {
    if (typeof navigator !== "undefined" && navigator.clipboard !== undefined) {
      void navigator.clipboard.writeText(correlationIdentifier);
    }
  }}>⧉</IconControl>;
}
