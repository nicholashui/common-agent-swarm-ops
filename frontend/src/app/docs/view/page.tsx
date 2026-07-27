"use client";

import { useSearchParams } from "next/navigation";
import { Suspense } from "react";

import { MarkdownViewerPage } from "../../../components/help/MarkdownViewerPage";

function DocsViewInner(): JSX.Element {
  const params = useSearchParams();
  const path = params.get("path") ?? "/docs/userguide.md";
  return <MarkdownViewerPage path={path} />;
}

/**
 * Full-page document viewer (help_spec.md).
 * Public path query: /docs/view?path=/docs/registry/userguide.md
 * No AppShell — readable without shell chrome; auth still applies if wrapped later.
 */
export default function DocsViewPage(): JSX.Element {
  return (
    <Suspense fallback={<p className="docs-page">Loading document…</p>}>
      <DocsViewInner />
    </Suspense>
  );
}
