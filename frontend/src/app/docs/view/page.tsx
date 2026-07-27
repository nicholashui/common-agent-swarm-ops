import { Suspense } from "react";

import { AppShell } from "../../../components/AppShell";
import { DocsViewContent } from "../../../components/help/DocsViewContent";

/**
 * Route-scoped user guide / document view (help_spec.md).
 * Renders inside AppShell main content — not a chrome-less full-window page.
 * Query: /docs/view?path=/docs/registry/userguide.md
 */
export default function DocsViewPage(): JSX.Element {
  return (
    <AppShell>
      <Suspense
        fallback={
          <section aria-label="Document viewer" className="docs-page">
            <p className="docs-page__status">Loading document…</p>
          </section>
        }
      >
        <DocsViewContent />
      </Suspense>
    </AppShell>
  );
}
