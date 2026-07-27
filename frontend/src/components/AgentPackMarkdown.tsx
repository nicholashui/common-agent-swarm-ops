"use client";

/**
 * Load pack agent SPEC/README from public/docs/agents and render as markdown
 * (not a raw text dump).
 */
import React, { useEffect, useMemo, useState } from "react";

import { MarkdownDocument } from "../lib/help/markdown-render";
import {
  fetchMarkdownCandidates,
  type MarkdownLoadState,
} from "../lib/help/use-markdown";

function isSafeDocsPath(path: string): boolean {
  const trimmed = path.trim();
  if (!trimmed.startsWith("/docs/agents/")) return false;
  if (trimmed.includes("..")) return false;
  return true;
}

export function AgentPackMarkdown({
  path,
  title,
  className,
}: Readonly<{
  path: string | null | undefined;
  title: string;
  className?: string;
}>): JSX.Element | null {
  const candidates = useMemo(() => {
    if (!path || !isSafeDocsPath(path)) return [] as string[];
    return [path];
  }, [path]);

  const [state, setState] = useState<MarkdownLoadState>({ status: "idle" });

  useEffect(() => {
    let cancelled = false;
    if (candidates.length === 0) {
      setState({ status: "idle" });
      return;
    }
    setState({ status: "loading" });
    void fetchMarkdownCandidates(candidates).then((result) => {
      if (!cancelled) setState(result);
    });
    return () => {
      cancelled = true;
    };
  }, [candidates]);

  if (!path || candidates.length === 0) return null;

  return (
    <section
      aria-label={title}
      className={
        className
          ? `agent-detail__markdown-panel ${className}`
          : "agent-detail__markdown-panel"
      }
    >
      <header className="agent-detail__markdown-header">
        <h2>{title}</h2>
        <p className="agent-detail__muted">
          <code>{path}</code>
        </p>
      </header>
      <div className="agent-detail__markdown-body">
        {state.status === "loading" || state.status === "idle" ? (
          <p className="agent-detail__muted">Loading document…</p>
        ) : null}
        {state.status === "empty" ? (
          <p className="agent-detail__muted">{state.message}</p>
        ) : null}
        {state.status === "error" ? (
          <p className="agent-detail__status" role="alert">
            Could not load {state.path}: {state.message}
          </p>
        ) : null}
        {state.status === "ready" ? (
          <MarkdownDocument
            className="agent-detail__md"
            markdown={state.markdown}
            markdownPath={state.resolvedPath}
          />
        ) : null}
      </div>
    </section>
  );
}
