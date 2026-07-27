"use client";

/**
 * @duty RightHelpPanel — route-aware tabbed help/document drawer
 * @role Load public/docs markdown for the current route; resize and close.
 * @must Soft-miss missing docs; never crash on HTML fallbacks.
 * @mustnot Hardcode business module document maps.
 * @redesign help_spec.md
 */
import React, { useEffect, useMemo, useRef, useState } from "react";

import {
  DEFAULT_HELP_TABS,
  resolveHelpMarkdownCandidates,
  type HelpTabConfig,
} from "../../lib/help/route-docs";
import { MarkdownDocument } from "../../lib/help/markdown-render";
import { useMarkdown } from "../../lib/help/use-markdown";

export const HELP_PANEL_WIDTH_KEY = "casops:help-panel-width";
export const HELP_PANEL_MIN_WIDTH = 280;
export const HELP_PANEL_MAX_WIDTH = 720;
export const HELP_PANEL_DEFAULT_WIDTH = 360;

export function clampHelpPanelWidth(width: number): number {
  return Math.min(HELP_PANEL_MAX_WIDTH, Math.max(HELP_PANEL_MIN_WIDTH, width));
}

export function readStoredHelpPanelWidth(): number {
  if (typeof window === "undefined") return HELP_PANEL_DEFAULT_WIDTH;
  try {
    const raw = window.localStorage.getItem(HELP_PANEL_WIDTH_KEY);
    if (!raw) return HELP_PANEL_DEFAULT_WIDTH;
    const parsed = Number(raw);
    if (!Number.isFinite(parsed)) return HELP_PANEL_DEFAULT_WIDTH;
    return clampHelpPanelWidth(parsed);
  } catch {
    return HELP_PANEL_DEFAULT_WIDTH;
  }
}

export function writeStoredHelpPanelWidth(width: number): void {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(
      HELP_PANEL_WIDTH_KEY,
      String(clampHelpPanelWidth(width)),
    );
  } catch {
    // best-effort only
  }
}

export interface RightHelpPanelProps {
  readonly pathname: string;
  readonly open: boolean;
  readonly width: number;
  readonly dragging: boolean;
  readonly tabs?: readonly HelpTabConfig[];
  readonly onClose: () => void;
  readonly onWidthChange: (width: number) => void;
  readonly onDraggingChange: (dragging: boolean) => void;
}

export function RightHelpPanel({
  pathname,
  open,
  width,
  dragging,
  tabs = DEFAULT_HELP_TABS,
  onClose,
  onWidthChange,
  onDraggingChange,
}: RightHelpPanelProps): JSX.Element | null {
  const defaultTabId = tabs[0]?.id ?? "userguide";
  const [activeTabId, setActiveTabId] = useState(defaultTabId);
  const wasOpen = useRef(false);

  useEffect(() => {
    if (open && !wasOpen.current) {
      setActiveTabId(defaultTabId);
    }
    wasOpen.current = open;
  }, [open, defaultTabId]);

  const activeTab = tabs.find((tab) => tab.id === activeTabId) ?? tabs[0];
  const candidates = useMemo(
    () =>
      activeTab
        ? resolveHelpMarkdownCandidates(pathname, activeTab.id, activeTab.mdPath)
        : [],
    [pathname, activeTab],
  );

  const markdownState = useMarkdown(candidates, open && activeTab !== undefined);

  const dragRef = useRef<{ startX: number; startWidth: number } | null>(null);

  useEffect(() => {
    if (!dragging) return undefined;

    const onMove = (event: PointerEvent): void => {
      const drag = dragRef.current;
      if (!drag) return;
      // drag left → wider
      const delta = drag.startX - event.clientX;
      onWidthChange(clampHelpPanelWidth(drag.startWidth + delta));
    };
    const onUp = (): void => {
      dragRef.current = null;
      onDraggingChange(false);
      document.body.style.cursor = "";
      document.body.style.userSelect = "";
    };

    document.addEventListener("pointermove", onMove);
    document.addEventListener("pointerup", onUp);
    document.addEventListener("pointercancel", onUp);
    return () => {
      document.removeEventListener("pointermove", onMove);
      document.removeEventListener("pointerup", onUp);
      document.removeEventListener("pointercancel", onUp);
    };
  }, [dragging, onDraggingChange, onWidthChange]);

  if (!open) return null;

  const onResizePointerDown = (
    event: React.PointerEvent<HTMLDivElement>,
  ): void => {
    event.preventDefault();
    dragRef.current = { startX: event.clientX, startWidth: width };
    onDraggingChange(true);
    document.body.style.cursor = "col-resize";
    document.body.style.userSelect = "none";
    event.currentTarget.setPointerCapture(event.pointerId);
  };

  const onResizeKeyDown = (event: React.KeyboardEvent<HTMLDivElement>): void => {
    const step = event.shiftKey ? 32 : 16;
    if (event.key === "ArrowLeft") {
      event.preventDefault();
      onWidthChange(clampHelpPanelWidth(width + step));
    } else if (event.key === "ArrowRight") {
      event.preventDefault();
      onWidthChange(clampHelpPanelWidth(width - step));
    } else if (event.key === "Home") {
      event.preventDefault();
      onWidthChange(HELP_PANEL_MAX_WIDTH);
    } else if (event.key === "End") {
      event.preventDefault();
      onWidthChange(HELP_PANEL_MIN_WIDTH);
    }
  };

  return (
    <aside
      aria-label="Help documents"
      className={
        dragging
          ? "help-panel help-panel--dragging"
          : "help-panel"
      }
      style={{ width }}
    >
      <div
        aria-orientation="vertical"
        aria-valuemax={HELP_PANEL_MAX_WIDTH}
        aria-valuemin={HELP_PANEL_MIN_WIDTH}
        aria-valuenow={width}
        className="help-panel__resize"
        onKeyDown={onResizeKeyDown}
        onPointerDown={onResizePointerDown}
        role="separator"
        tabIndex={0}
        title="Resize help panel"
      />
      <header className="help-panel__header">
        <h2 className="help-panel__title">Help</h2>
        <button
          aria-label="Close help panel"
          className="help-panel__close"
          onClick={onClose}
          type="button"
        >
          ×
        </button>
      </header>
      <div
        aria-label="Document types"
        className="help-panel__tabs"
        role="tablist"
      >
        {tabs.map((tab) => (
          <button
            aria-selected={tab.id === activeTabId}
            className={
              tab.id === activeTabId
                ? "help-panel__tab help-panel__tab--active"
                : "help-panel__tab"
            }
            key={tab.id}
            onClick={() => setActiveTabId(tab.id)}
            role="tab"
            type="button"
          >
            {tab.label}
          </button>
        ))}
      </div>
      <div className="help-panel__body" role="tabpanel">
        {markdownState.status === "loading" || markdownState.status === "idle" ? (
          <p className="help-panel__status">Loading document…</p>
        ) : null}
        {markdownState.status === "empty" ? (
          <p className="help-panel__status">{markdownState.message}</p>
        ) : null}
        {markdownState.status === "error" ? (
          <p className="help-panel__status help-panel__status--error" role="alert">
            Could not load {markdownState.path}: {markdownState.message}
          </p>
        ) : null}
        {markdownState.status === "ready" ? (
          <MarkdownDocument
            markdown={markdownState.markdown}
            markdownPath={markdownState.resolvedPath}
          />
        ) : null}
      </div>
    </aside>
  );
}
