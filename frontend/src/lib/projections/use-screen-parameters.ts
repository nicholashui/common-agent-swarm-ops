"use client";

import { useSyncExternalStore } from "react";

import {
  getScreenParameters,
  subscribeScreenParameters,
  type ScreenParameterKey,
  type ScreenParameterMap,
} from "./screen-parameters";

/**
 * React binding: always renders the current stored parameters for a screen.
 * Updates when `setScreenParameters` / `updateScreenParameters` run.
 */
export function useScreenParameters<K extends ScreenParameterKey>(
  key: K,
): ScreenParameterMap[K] {
  return useSyncExternalStore(
    subscribeScreenParameters,
    (): ScreenParameterMap[K] => getScreenParameters(key),
    (): ScreenParameterMap[K] => getScreenParameters(key),
  );
}
