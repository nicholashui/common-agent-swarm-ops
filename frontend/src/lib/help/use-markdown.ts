/**
 * Load markdown from same-origin /docs candidates with soft-miss fallback.
 */

"use client";

import { useEffect, useState } from "react";

export type MarkdownLoadState =
  | { readonly status: "idle" }
  | { readonly status: "loading" }
  | {
      readonly status: "ready";
      readonly markdown: string;
      readonly resolvedPath: string;
    }
  | {
      readonly status: "error";
      readonly message: string;
      readonly path: string;
    }
  | { readonly status: "empty"; readonly message: string };

const markdownCache = new Map<string, string>();

export function clearMarkdownCacheForTests(): void {
  markdownCache.clear();
}

function looksLikeHtmlDocument(text: string, contentType: string | null): boolean {
  const type = (contentType ?? "").toLowerCase();
  if (type.includes("text/html")) return true;
  const head = text.slice(0, 256).trim().toLowerCase();
  return (
    head.startsWith("<!doctype html") ||
    head.startsWith("<html") ||
    head.includes("<script") && head.includes("</html>")
  );
}

export async function fetchMarkdownCandidates(
  candidates: readonly string[],
  fetchImpl: typeof fetch = fetch,
): Promise<MarkdownLoadState> {
  if (candidates.length === 0) {
    return { status: "empty", message: "No document for this screen yet." };
  }

  let lastHardError: { path: string; message: string } | null = null;

  for (const path of candidates) {
    const cached = markdownCache.get(path);
    if (cached !== undefined) {
      return { status: "ready", markdown: cached, resolvedPath: path };
    }

    try {
      const response = await fetchImpl(path, {
        method: "GET",
        credentials: "same-origin",
        headers: { accept: "text/markdown, text/plain, */*" },
      });

      if (response.status === 404) {
        continue; // soft miss
      }

      const contentType = response.headers.get("content-type");
      const text = await response.text();

      if (!response.ok) {
        lastHardError = {
          path,
          message: `HTTP ${response.status} for ${path}`,
        };
        continue;
      }

      if (looksLikeHtmlDocument(text, contentType)) {
        continue; // soft miss (SPA/index fallback)
      }

      const markdown = text;
      markdownCache.set(path, markdown);
      return { status: "ready", markdown, resolvedPath: path };
    } catch (error) {
      lastHardError = {
        path,
        message: error instanceof Error ? error.message : "Network error",
      };
    }
  }

  if (lastHardError) {
    return {
      status: "error",
      path: lastHardError.path,
      message: lastHardError.message,
    };
  }

  return { status: "empty", message: "No document for this screen yet." };
}

/**
 * @param active - when false, stay idle and do not fetch
 */
export function useMarkdown(
  candidates: readonly string[],
  active: boolean,
): MarkdownLoadState {
  const [state, setState] = useState<MarkdownLoadState>({ status: "idle" });
  const key = candidates.join("|");

  useEffect(() => {
    if (!active) {
      setState({ status: "idle" });
      return;
    }
    if (candidates.length === 0) {
      setState({ status: "empty", message: "No document for this screen yet." });
      return;
    }

    let cancelled = false;
    setState({ status: "loading" });
    void fetchMarkdownCandidates(candidates).then((result) => {
      if (!cancelled) setState(result);
    });

    return () => {
      cancelled = true;
    };
    // key encodes candidates
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [active, key]);

  return state;
}
