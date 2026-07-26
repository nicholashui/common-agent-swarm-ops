"use client";

import type { ComponentType } from "react";

import {
  type ScreenParameterKey,
  type ScreenParameterMap,
} from "../../lib/projections/screen-parameters";
import { useScreenParameters } from "../../lib/projections/use-screen-parameters";

/**
 * Binds a presentation home to stored screen parameters.
 * The home component must accept `{ view }` and must not embed fixture defaults.
 */
export function BoundScreenHome<K extends ScreenParameterKey>({
  screen,
  Home,
}: {
  readonly screen: K;
  readonly Home: ComponentType<{ readonly view: ScreenParameterMap[K] }>;
}): JSX.Element {
  const view = useScreenParameters(screen);
  return <Home view={view} />;
}
