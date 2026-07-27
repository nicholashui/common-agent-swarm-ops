"use client";

/**
 * Client binder for /docs/view — reads ?path= and renders markdown in main content.
 */
import { useSearchParams } from "next/navigation";

import { MarkdownViewerPage } from "./MarkdownViewerPage";

export function DocsViewContent(): JSX.Element {
  const params = useSearchParams();
  const path = params.get("path") ?? "/docs/userguide.md";
  return <MarkdownViewerPage path={path} />;
}
