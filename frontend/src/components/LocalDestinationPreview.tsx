import React from "react";

import type { LocalDestinationCopy } from "../lib/projections/local-preview";
import { PageHeader } from "./design";

export function LocalDestinationPreview({
  copy,
}: Readonly<{ copy: LocalDestinationCopy }>): JSX.Element {
  return (
    <section
      aria-label={`${copy.title} local preview`}
      className="operational-screen local-destination-preview"
    >
      <PageHeader
        description={copy.description}
        eyebrow={copy.eyebrow}
        title={copy.title}
      />
      <div className="panel">
        <p className="local-destination-preview__banner">
          Local preview — backend projection is not connected. The browser
          renders only returned authorized data when available.
        </p>
      </div>
    </section>
  );
}
