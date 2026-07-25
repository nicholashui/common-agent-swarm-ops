"use client";

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
