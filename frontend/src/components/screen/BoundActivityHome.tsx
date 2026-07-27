"use client";

/**
 * Slim activity binder — ActivityHome + activity landing only.
 * Intentionally avoids the multi-home screen binder fan-in.
 */
import React, { useCallback, useState } from "react";

import { LOCAL_ACTIVITY_LANDING } from "../../lib/projections/activity-landing";
import type { ScreenUiAction } from "../../lib/ui/screen-actions";
import type { InteractionStatus } from "../../lib/ui/interaction-runtime";
import { ActivityHome } from "../ActivityHome";
import { InteractionStatusBar } from "../ui/InteractionStatusBar";

export function BoundActivityHome(): JSX.Element {
  const view = LOCAL_ACTIVITY_LANDING;
  const [status, setStatus] = useState<InteractionStatus>({
    kind: "idle",
    message: "",
  });

  const onAction = useCallback(async (action: ScreenUiAction): Promise<void> => {
    switch (action.kind) {
      case "feedback":
        setStatus({ kind: "info", message: action.message });
        return;
      case "local.layout":
        setStatus({
          kind: "success",
          message: action.detail ?? "Layout applied locally.",
        });
        return;
      case "governed.fail_closed":
        setStatus({
          kind: "error",
          message: `${action.message}${
            action.actionHint ? ` ${action.actionHint}` : ""
          }`,
        });
        return;
      case "run.inspect":
        setStatus({
          kind: "info",
          message: `Inspect run ${action.runId} (host when available).`,
        });
        return;
      default:
        setStatus({
          kind: "info",
          message: `Action “${action.kind}” recorded for this session.`,
        });
    }
  }, []);

  return (
    <>
      <InteractionStatusBar status={status} />
      <ActivityHome
        view={view}
        onAction={onAction}
        statusMessage={
          status.kind === "idle" ? undefined : status.message
        }
      />
    </>
  );
}
