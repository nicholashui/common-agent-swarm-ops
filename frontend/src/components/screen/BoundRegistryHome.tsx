"use client";

/**
 * Slim registry binder — only RegistryHome + LOCAL_REGISTRY_LANDING (slim catalog).
 * Intentionally does NOT import screen-parameters (that graph pulls full pack-agents
 * + every landing and blocks hydration for ~seconds, freezing search/facets/modes).
 */
import React, { useCallback, useState } from "react";

import { LOCAL_REGISTRY_LANDING } from "../../lib/projections/registry-landing";
import type { ScreenUiAction } from "../../lib/ui/screen-actions";
import type { InteractionStatus } from "../../lib/ui/interaction-runtime";
import { RegistryHome } from "../RegistryHome";
import { InteractionStatusBar } from "../ui/InteractionStatusBar";

export function BoundRegistryHome(): JSX.Element {
  const view = LOCAL_REGISTRY_LANDING;
  const [status, setStatus] = useState<InteractionStatus>({
    kind: "idle",
    message: "",
  });

  const onAction = useCallback(async (action: ScreenUiAction): Promise<void> => {
    switch (action.kind) {
      case "feedback":
        setStatus({ kind: "info", message: action.message });
        return;
      case "local.save_prefs":
        setStatus({ kind: "success", message: action.summary });
        return;
      case "local.mark_read":
        setStatus({
          kind: "success",
          message:
            action.ids.length === 0
              ? "No items to mark."
              : `Marked ${action.ids.length} item(s) read in session.`,
        });
        return;
      case "commons.propose": {
        setStatus({
          kind: "busy",
          message: `Submitting proposal for ${action.agentId}…`,
        });
        const { proposeAgentImprovement } = await import(
          "../../lib/api/product-commons"
        );
        const result = await proposeAgentImprovement(action.agentId, {
          summary: action.summary,
        });
        if (!result.ok) {
          setStatus({ kind: "error", message: result.message });
          return;
        }
        setStatus({
          kind: "success",
          message: `Proposal ${result.proposalId} ${result.status} for ${result.targetId}.`,
        });
        return;
      }
      case "governed.fail_closed":
        setStatus({
          kind: "error",
          message: `${action.message}${
            action.actionHint
              ? ` ${action.actionHint}`
              : " Provide a host action reference; the browser will not invent one."
          }`,
        });
        return;
      default:
        setStatus({
          kind: "info",
          message: `Action “${action.kind}” is not a local registry discovery control.`,
        });
    }
  }, []);

  const statusMessage = status.kind === "idle" ? undefined : status.message;

  return (
    <>
      <InteractionStatusBar status={status} />
      <RegistryHome
        onAction={onAction}
        statusMessage={statusMessage}
        view={view}
      />
    </>
  );
}
