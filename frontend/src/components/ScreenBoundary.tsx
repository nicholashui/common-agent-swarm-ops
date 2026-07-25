import React, { type ReactNode } from "react";

import type { GeneratedActionReference } from "../lib/api/client";
import type { ActionReferenceView } from "../lib/projections/ProjectionMapper";
import type {
  ScreenCapability,
  ScreenDefinition,
  ScreenUnavailableError,
} from "../lib/screens/screen-manifest";
import { ActionControl } from "./projection/ActionControl";

export interface GeneratedCapabilityResult {
  readonly key: ScreenCapability;
}

export interface ScreenBoundaryUnavailableState {
  readonly error: ScreenUnavailableError;
  readonly recoveryAction?: ActionReferenceView;
}

export interface ScreenBoundaryProps {
  readonly definition: ScreenDefinition;
  readonly capabilities: readonly GeneratedCapabilityResult[];
  readonly shell: ReactNode;
  readonly unavailableState?: ScreenBoundaryUnavailableState;
  readonly onRecoveryAction?: (action: GeneratedActionReference) => void;
  readonly children: ReactNode;
}

function hasRequiredCapability(
  definition: ScreenDefinition,
  capabilities: readonly GeneratedCapabilityResult[],
): boolean {
  return capabilities.some(({ key }) => key === definition.requiredCapability);
}

/**
 * Keeps authenticated shell context visible, but never renders an approved
 * screen's data region before its generated capability is returned.
 */
export function ScreenBoundary({
  definition,
  capabilities,
  shell,
  unavailableState,
  onRecoveryAction,
  children,
}: ScreenBoundaryProps): JSX.Element {
  if (hasRequiredCapability(definition, capabilities)) {
    return <>{shell}{children}</>;
  }

  const error = unavailableState?.error;
  const recoveryAction = unavailableState?.recoveryAction;

  return <>{shell}<section aria-live="polite" aria-atomic="true" aria-label={`${definition.uiId} unavailable`} role="status">
    <h1>Screen unavailable</h1>
    {error ? <p>{error.message}</p> : <p>This authorized screen is currently unavailable.</p>}
    {recoveryAction ? <ActionControl
      action={recoveryAction}
      disabledByOwner={onRecoveryAction === undefined}
      onInvoke={(action): void => onRecoveryAction?.(action)}
      stale={false}
    /> : null}
  </section></>;
}
