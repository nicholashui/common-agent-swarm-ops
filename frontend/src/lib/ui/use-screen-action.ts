/**
 * Hook for Bound* homes: interaction runtime + structured screen actions.
 */

"use client";

import { useCallback } from "react";

import {
  classifyAnnounce,
  performScreenAction,
  type ScreenUiAction,
} from "./screen-actions";
import { useInteractionRuntime, type InteractionRuntime } from "./interaction-runtime";

export type ScreenActionHandler = (
  action: ScreenUiAction,
) => void | Promise<void | boolean>;

export interface ScreenActionBridge {
  readonly runtime: InteractionRuntime;
  readonly busy: boolean;
  readonly statusMessage: string | undefined;
  readonly onAction: ScreenActionHandler;
  /** Route free-text announce stubs through classify + perform. */
  readonly announce: (message: string) => void;
}

export function useScreenActionBridge(): ScreenActionBridge {
  const runtime = useInteractionRuntime();

  const onAction = useCallback(
    async (action: ScreenUiAction): Promise<void> => {
      await performScreenAction(runtime, action);
    },
    [runtime],
  );

  const announce = useCallback(
    (message: string): void => {
      void performScreenAction(runtime, classifyAnnounce(message));
    },
    [runtime],
  );

  return {
    runtime,
    busy: runtime.busy,
    statusMessage:
      runtime.status.kind === "idle" ? undefined : runtime.status.message,
    onAction,
    announce,
  };
}
