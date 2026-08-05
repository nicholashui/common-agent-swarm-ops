"use client";

/**
 * Slim registry binder — only RegistryHome + LOCAL_REGISTRY_LANDING (slim catalog).
 * Intentionally does NOT import screen-parameters (that graph pulls full pack-agents
 * + every landing and blocks hydration for ~seconds, freezing search/facets/modes).
 *
 * Draft UX: compact title buttons next to “Common Registry” (not a wall of copy).
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
  const [draftListBusy, setDraftListBusy] = useState(false);
  const [draftsOpen, setDraftsOpen] = useState(false);

  const refreshDraftList = useCallback(async (): Promise<void> => {
    setDraftListBusy(true);
    try {
      const { listSwarms } = await import("../../lib/api/product-swarms");
      const result = await listSwarms();
      if (!result.ok) {
        setDraftList([]);
        setStatus({ kind: "error", message: result.message });
        return;
      }
      setDraftList(result.items);
    } catch (error) {
      setDraftList([]);
      setStatus({
        kind: "error",
        message:
          error instanceof Error ? error.message : "Failed to list swarms.",
      });
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
            const result = await proposeAgentImprovement(
              action.agentId,
              action.summary,
            );
            if (!result.ok) {
              setStatus({ kind: "error", message: result.message });
              return;
            }
            setStatus({
              kind: "success",
              message: `Proposal recorded for ${action.agentId}.`,
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
                `Added ${result.agentId} to ${result.swarmName}` +
                (result.createdSwarm ? " (new draft)." : " (same draft)."),
            });
            void refreshDraftList();
            return;
          }
          default:
            setStatus({
              kind: "info",
              message: `Action “${action.kind}” is not wired on Registry.`,
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

  // Inline next to h1 "Common Registry": Label · Button (no toast above the title).
  const titleActions = (
    <>
      <span className="registry-home__title-action">
        <span className="registry-home__title-action-label" id="reg-same-draft-label">
          Crew draft
        </span>
        <button
          aria-labelledby="reg-same-draft-label"
          aria-pressed={appendToLastDraft}
          className={
            appendToLastDraft
              ? "ds-cta ds-cta--common ds-cta--sm"
              : "ds-cta ds-cta--secondary ds-cta--sm"
          }
          onClick={() => {
            // Toggle only — do not push InteractionStatusBar above the title.
            setAppendToLastDraft((on) => !on);
          }}
          title={
            appendToLastDraft
              ? "On: further Add to Swarm appends to the same draft"
              : "Off: each Add to Swarm can start a new draft"
          }
          type="button"
        >
          {appendToLastDraft ? "On" : "Off"}
        </button>
      </span>
      <span className="registry-home__title-action">
        <span className="registry-home__title-action-label" id="reg-drafts-label">
          Host drafts
        </span>
        <button
          aria-expanded={draftsOpen}
          aria-labelledby="reg-drafts-label"
          className="ds-cta ds-cta--secondary ds-cta--sm"
          disabled={draftListBusy}
          onClick={() => {
            setDraftsOpen((open) => !open);
            if (!draftsOpen) void refreshDraftList();
          }}
          type="button"
        >
          {draftListBusy
            ? "…"
            : draftsOpen
              ? "Hide"
              : draftList.length > 0
                ? `Show (${draftList.length})`
                : "Show"}
        </button>
      </span>
      {activeDraft ? (
        <span className="registry-home__title-action">
          <span className="registry-home__title-action-label" id="reg-active-label">
            Active
          </span>
          <Link
            aria-labelledby="reg-active-label"
            className="ds-cta ds-cta--primary ds-cta--sm"
            href={`/swarms/${encodeURIComponent(activeDraft.swarmId)}/canvas`}
            title={activeDraft.swarmName}
          >
            Open execute
          </Link>
          <button
            className="ds-cta ds-cta--secondary ds-cta--sm"
            onClick={() => setActiveDraft(null)}
            type="button"
          >
            Clear
          </button>
        </span>
      ) : null}
    </>
  );

  const belowHeader =
    draftsOpen || activeDraft ? (
      <div
        className="registry-home__draft-bar registry-home__draft-bar--compact"
        role="region"
        aria-label="Swarm drafts"
      >
        {activeDraft ? (
          <p className="registry-home__draft-meta">
            Active: <strong>{activeDraft.swarmName}</strong>{" "}
            <code>{activeDraft.swarmId}</code>
          </p>
        ) : null}
        {draftsOpen ? (
          draftList.length > 0 ? (
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
                    · {item.memberCount} member
                    {item.memberCount === 1 ? "" : "s"}
                  </span>
                  <button
                    className="ds-cta ds-cta--secondary ds-cta--sm"
                    onClick={() => {
                      setActiveDraft({
                        swarmId: item.id,
                        swarmName: item.name,
                      });
                      setStatus({
                        kind: "info",
                        message: `Next Add to Swarm will add members to ${item.name}.`,
                      });
                    }}
                    type="button"
                  >
                    Use next
                  </button>
                </li>
              ))}
            </ul>
          ) : (
            <p className="registry-home__draft-meta registry-home__draft-meta--quiet">
              No Host drafts yet. Use <strong>Add to Swarm</strong> on an agent.
            </p>
          )
        ) : null}
      </div>
    ) : null;

  // Status under the header (never above "Common Registry").
  const statusUnderHeader =
    status.kind !== "idle" && status.message.length > 0 ? (
      <InteractionStatusBar status={status} />
    ) : null;

  return (
    <RegistryHome
      belowHeader={
        <>
          {statusUnderHeader}
          {belowHeader}
        </>
      }
      onAction={onAction}
      statusMessage={statusMessage}
      titleActions={titleActions}
      view={view}
    />
  );
}
