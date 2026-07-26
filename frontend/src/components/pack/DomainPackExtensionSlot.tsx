"use client";

import React from "react";

import {
  extensionsForSlot,
  type PackUiExtensionManifest,
} from "../../lib/pack-extensions/types";
import { SafeContent } from "../projection/SafeContent";

export interface DomainPackExtensionSlotProps {
  readonly slotId: string;
  /** Server-returned pack UI extension manifests only. */
  readonly extensions: readonly PackUiExtensionManifest[];
  readonly emptyLabel?: string;
}

/**
 * Renders domain pack UI extensions for a named host slot without hard-coding
 * any domain (adoption_redesign: host supplies slots; packs supply metadata).
 */
export function DomainPackExtensionSlot({
  slotId,
  extensions,
  emptyLabel,
}: DomainPackExtensionSlotProps): JSX.Element | null {
  const matched = extensionsForSlot(extensions, slotId);
  if (matched.length === 0) {
    return emptyLabel === undefined
      ? null
      : <p className="pack-extension-slot pack-extension-slot--empty" data-slot-id={slotId}>{emptyLabel}</p>;
  }

  return <section
    aria-label={`Domain pack extensions: ${slotId}`}
    className="pack-extension-slot"
    data-slot-id={slotId}
  >
    {matched.map((extension) => (
      <PackExtensionCard extension={extension} key={`${extension.domainId}:${extension.packVersion}:${extension.slotId}:${extension.title}`} />
    ))}
  </section>;
}

function PackExtensionCard({ extension }: { readonly extension: PackUiExtensionManifest }): JSX.Element {
  return <article
    className="pack-extension-card"
    data-domain-id={extension.domainId}
    data-pack-version={extension.packVersion}
  >
    <header>
      <p className="eyebrow">{extension.domainId} · v{extension.packVersion}</p>
      <h3>{extension.title}</h3>
    </header>
    {extension.panels === undefined || extension.panels.length === 0 ? null : (
      <ul className="pack-extension-card__panels">
        {extension.panels.map((panel) => (
          <li key={panel.panelId}>
            <strong>{panel.title}</strong>
            {panel.summary === undefined ? null : <SafeContent content={panel.summary} />}
          </li>
        ))}
      </ul>
    )}
  </article>;
}
