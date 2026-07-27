"use client";

/**
 * Markdown document view for the shell main content area (and reusable elsewhere).
 * Independent of the right help drawer (help_spec.md).
 */
import React, { useEffect, useMemo, useState } from "react";

import { MarkdownDocument } from "../../lib/help/markdown-render";
import {
  fetchMarkdownCandidates,
  type MarkdownLoadState,
} from "../../lib/help/use-markdown";

export function MarkdownViewerPage({
  path,
}: Readonly<{ path: string }>): JSX.Element {
  const candidates = useMemo(() => {
    const trimmed = path.trim();
    if (!trimmed) return [] as string[];
    const normalized = trimmed.startsWith("/") ? trimmed : `/${trimmed}`;
    // Only allow same-origin public docs paths
    if (!normalized.startsWith("/docs/")) return [] as string[];
    if (normalized.includes("..")) return [] as string[];
    return [normalized];
  }, [path]);

  const [state, setState] = useState<MarkdownLoadState>({ status: "idle" });

  useEffect(() => {
    let cancelled = false;
    if (candidates.length === 0) {
      setState({
        status: "error",
        path: path || "(none)",
        message: "Document path must be under /docs/.",
      });
      return;
    }
    setState({ status: "loading" });
    void fetchMarkdownCandidates(candidates).then((result) => {
      if (!cancelled) setState(result);
    });
    return () => {
      cancelled = true;
    };
  }, [candidates, path]);

  return (
    <section aria-label="Document viewer" className="docs-page">
      <header className="docs-page__header">
        <div>
          <p className="eyebrow">Documentation</p>
          <h1>User guide</h1>
          <p className="docs-page__path">
            <code>{path || "—"}</code>
          </p>
        </div>
      </header>
      <div className="docs-page__body">
        {state.status === "loading" || state.status === "idle" ? (
          <p className="docs-page__status">Loading document…</p>
        ) : null}
        {state.status === "empty" ? (
          <p className="docs-page__status">{state.message}</p>
        ) : null}
        {state.status === "error" ? (
          <p className="docs-page__status docs-page__status--error" role="alert">
            Could not load {state.path}: {state.message}
          </p>
        ) : null}
        {state.status === "ready" ? (
          <MarkdownDocument
            markdown={state.markdown}
            markdownPath={state.resolvedPath}
          />
        ) : null}
      </div>
    </section>
  );
}
