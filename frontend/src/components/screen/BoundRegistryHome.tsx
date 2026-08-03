"use client";

/**
 * Slim registry binder — only RegistryHome + LOCAL_REGISTRY_LANDING (slim catalog).
 * Intentionally does NOT import screen-parameters (that graph pulls full pack-agents
 * + every landing and blocks hydration for ~seconds, freezing search/facets/modes).
 *
 * Also hosts draft-swarm session UX: last draft memory + live Host draft list.
 */
import React, { useCallback, useEffect, useState } from "react";
import Link from "next/link";

import { LOCAL_REGISTRY_LANDING } from "../../lib/projections/registry-landing";
import type { SwarmListItem } from "../../lib/api/product-swarms";
import type { ScreenUiAction } from "../../lib/ui/screen-actions";
import type { InteractionStatus } from "../../lib/ui/interaction-runtime";
import { RegistryHome } from "../RegistryHome";
import { InteractionStatusBar } from "../ui/InteractionStatusBar";

type ActiveDraft = {
  readonly swarmId: string;
  readonly swarmName: string;
};

export function BoundRegistryHome(): JSX.Element {
  const view = LOCAL_REGISTRY_LANDING;
  const [status, setStatus] = useState<InteractionStatus>({
    kind: "idle",
    message: "",
  });
  /** Session memory only (no localStorage): last draft for multi-agent Add to Swarm. */
  const [activeDraft, setActiveDraft] = useState<ActiveDraft | null>(null);
  /** When true (default), further Add to Swarm clicks append to activeDraft. */
  const [appendToLastDraft, setAppendToLastDraft] = useState(true);
  const [draftList, setDraftList] = useState<readonly SwarmListItem[]>([]);
  const [draftListMessage, setDraftListMessage] = useState<string>(
    "Loading Host drafts…",
  );
  const [draftListBusy, setDraftListBusy] = useState(false);

  const refreshDraftList = useCallback(async (): Promise<void> => {
    setDraftListBusy(true);
    try {
      const { listSwarms } = await import("../../lib/api/product-swarms");
      const result = await listSwarms();
      if (!result.ok) {
        setDraftList([]);
        setDraftListMessage(result.message);
        return;
      }
      setDraftList(result.items);
      if (result.items.length === 0) {
        setDraftListMessage(
          "No Host drafts yet. Use Add to Swarm on an agent. Drafts live only in the current backend process (restart clears them).",
        );
      } else {
        setDraftListMessage(
          `${result.items.length} swarm(s) on this Host (including drafts).`,
        );
      }
    } catch (error) {
      setDraftList([]);
      setDraftListMessage(
        error instanceof Error ? error.message : "Failed to list swarms.",
      );
    } finally {
      setDraftListBusy(false);
    }
  }, []);

  useEffect(() => {
    void refreshDraftList();
  }, [refreshDraftList]);

  const onAction = useCallback(
    async (action: ScreenUiAction): Promise<void> => {
      try {
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
          case "commons.add_to_swarm": {
            const targetSwarmId =
              appendToLastDraft && activeDraft && !action.swarmId
                ? activeDraft.swarmId
                : action.swarmId;
            const targetName =
              targetSwarmId && activeDraft?.swarmId === targetSwarmId
                ? activeDraft.swarmName
                : action.swarmName;

            setStatus({
              kind: "busy",
              message: targetSwarmId
                ? `Adding ${action.agentId} to draft ${targetSwarmId}…`
                : `Adding ${action.agentId} to a new swarm draft…`,
            });
            const { addAgentToSwarmDraft } = await import(
              "../../lib/api/product-swarms"
            );
            const result = await addAgentToSwarmDraft(action.agentId, {
              swarmName: targetName,
              swarmId: targetSwarmId,
            });
            if (!result.ok) {
              setStatus({ kind: "error", message: result.message });
              return;
            }
            setActiveDraft({
              swarmId: result.swarmId,
              swarmName: result.swarmName,
            });
            setStatus({
              kind: "success",
              message:
                `Added ${result.agentId} to swarm draft ${result.swarmId} ` +
                `(${result.swarmName}, rev ${result.revision}, node ${result.nodeId}` +
                `${result.createdSwarm ? ", new draft" : ", same draft"}). ` +
                "Open the draft below or use “Open canvas”. " +
                (appendToLastDraft
                  ? "Next Add to Swarm will use this draft."
                  : "“Add to last draft” is off — next click creates another new draft.") +
                " Production stays fail-closed.",
            });
            void refreshDraftList();
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
      } catch (error) {
        const message =
          error instanceof Error
            ? error.message
            : "Unexpected registry action error.";
        setStatus({ kind: "error", message });
      }
    },
    [activeDraft, appendToLastDraft, refreshDraftList],
  );

  const statusMessage = status.kind === "idle" ? undefined : status.message;

  return (
    <>
      <InteractionStatusBar status={status} />
      <div
        className="registry-home__draft-bar"
        role="region"
        aria-label="Active swarm draft"
      >
        <label className="registry-home__draft-toggle">
          <input
            checked={appendToLastDraft}
            onChange={(event) => setAppendToLastDraft(event.target.checked)}
            type="checkbox"
          />
          <span>Add to last draft (same swarm for multiple agents)</span>
        </label>
        {activeDraft ? (
          <p className="registry-home__draft-meta">
            Active draft: <code>{activeDraft.swarmId}</code> ·{" "}
            <strong>{activeDraft.swarmName}</strong>{" "}
            <Link
              className="registry-home__linkish"
              href={`/swarms/${encodeURIComponent(activeDraft.swarmId)}/canvas`}
            >
              Open canvas
            </Link>
            <button
              className="registry-home__linkish"
              onClick={() => {
                setActiveDraft(null);
                setStatus({
                  kind: "info",
                  message:
                    "Cleared active draft. Next Add to Swarm will create a new draft.",
                });
              }}
              type="button"
            >
              Clear
            </button>
          </p>
        ) : (
          <p className="registry-home__draft-meta">
            No active draft in this browser session. First{" "}
            <strong>Add to Swarm</strong> creates one; further adds join it
            while the checkbox is on. Or open a Host draft from the list below.
          </p>
        )}

        <div className="registry-home__draft-list" aria-live="polite">
          <div className="registry-home__draft-list-head">
            <strong>Host drafts (live)</strong>
            <button
              className="registry-home__linkish"
              disabled={draftListBusy}
              onClick={() => void refreshDraftList()}
              type="button"
            >
              {draftListBusy ? "Refreshing…" : "Refresh"}
            </button>
          </div>
          <p className="registry-home__draft-meta">{draftListMessage}</p>
          {draftList.length > 0 ? (
            <ul className="registry-home__draft-items">
              {draftList.map((item) => (
                <li key={item.id}>
                  <Link
                    className="registry-home__linkish"
                    href={`/swarms/${encodeURIComponent(item.id)}/canvas`}
                  >
                    {item.name}
                  </Link>
                  <span className="registry-home__draft-item-meta">
                    {" "}
                    · <code>{item.id}</code> · {item.status} · rev{" "}
                    {item.revision} · {item.memberCount} member
                    {item.memberCount === 1 ? "" : "s"}
                  </span>
                  <button
                    className="registry-home__linkish"
                    onClick={() => {
                      setActiveDraft({
                        swarmId: item.id,
                        swarmName: item.name,
                      });
                      setStatus({
                        kind: "info",
                        message: `Active draft set to ${item.id}. Further Add to Swarm will append members here.`,
                      });
                    }}
                    type="button"
                  >
                    Use for next adds
                  </button>
                </li>
              ))}
            </ul>
          ) : null}
        </div>
      </div>
      <RegistryHome
        onAction={onAction}
        statusMessage={statusMessage}
        view={view}
      />
    </>
  );
}
