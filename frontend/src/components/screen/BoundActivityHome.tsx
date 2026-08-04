"use client";

/**
 * Live Activity binder — Host GET /api/v1/activity (+ insights).
 * No fabricated board rows when Host is empty or down.
 */
import React, { useCallback, useEffect, useState } from "react";

import type { ActivityLandingView } from "../../lib/projections/activity-landing";
import { LOCAL_ACTIVITY_LANDING } from "../../lib/projections/activity-landing";
import { buildLiveActivityView } from "../../lib/projections/activity-live";
import type { ScreenUiAction } from "../../lib/ui/screen-actions";
import type { InteractionStatus } from "../../lib/ui/interaction-runtime";
import { ActivityHome } from "../ActivityHome";
import { InteractionStatusBar } from "../ui/InteractionStatusBar";

export function BoundActivityHome(): JSX.Element {
  const [view, setView] = useState<ActivityLandingView>(LOCAL_ACTIVITY_LANDING);
  const [status, setStatus] = useState<InteractionStatus>({
    kind: "idle",
    message: "",
  });

  const refresh = useCallback(async (): Promise<void> => {
    setStatus({ kind: "busy", message: "Loading Host activity…" });
    try {
      const { fetchActivityFeed, fetchActivityInsights } = await import(
        "../../lib/api/product-ops"
      );
      const [feed, insights] = await Promise.all([
        fetchActivityFeed({ limit: 50 }),
        fetchActivityInsights(),
      ]);
      if (!feed.ok) {
        setView(
          buildLiveActivityView({
            feed: null,
            hostReachable: false,
            hostMessage: feed.message,
          }),
        );
        setStatus({ kind: "error", message: feed.message });
        return;
      }
      setView(
        buildLiveActivityView({
          feed: feed.data,
          hostReachable: true,
          eventCount: insights.ok ? insights.data.event_count : feed.data.items.length,
          categories: insights.ok ? insights.data.categories : undefined,
        }),
      );
      setStatus({
        kind: "success",
        message: `Host activity: ${feed.data.items.length} event(s).`,
      });
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Activity load failed.";
      setView(
        buildLiveActivityView({
          feed: null,
          hostReachable: false,
          hostMessage: message,
        }),
      );
      setStatus({ kind: "error", message });
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

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
        statusMessage={status.kind === "idle" ? undefined : status.message}
      />
    </>
  );
}
