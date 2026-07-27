"use client";

/**
 * Slim composer binder — ComposerHome + composer landing only.
 */
import React, { useCallback, useState } from "react";

import { LOCAL_COMPOSER_LANDING } from "../../lib/projections/composer-landing";
import type { ScreenUiAction } from "../../lib/ui/screen-actions";
import type { InteractionStatus } from "../../lib/ui/interaction-runtime";
import { ComposerHome } from "../ComposerHome";
import { InteractionStatusBar } from "../ui/InteractionStatusBar";

export function BoundComposerHome(): JSX.Element {
  const view = LOCAL_COMPOSER_LANDING;
  const [status, setStatus] = useState<InteractionStatus>({
    kind: "idle",
    message: "",
  });

  const onAction = useCallback(async (action: ScreenUiAction): Promise<void> => {
    switch (action.kind) {
      case "feedback":
        setStatus({ kind: "info", message: action.message });
        return;
      case "governed.fail_closed":
        setStatus({
          kind: "error",
          message: `${action.message}${
            action.actionHint ? ` ${action.actionHint}` : ""
          }`,
        });
        return;
      case "local.save_prefs":
        setStatus({ kind: "success", message: action.summary });
        return;
      default:
        setStatus({
          kind: "info",
          message: `Action “${action.kind}” requires host compose contract when mutating.`,
        });
    }
  }, []);

  return (
    <>
      <InteractionStatusBar status={status} />
      <ComposerHome
        view={view}
        onAction={onAction}
        statusMessage={
          status.kind === "idle" ? undefined : status.message
        }
      />
    </>
  );
}
