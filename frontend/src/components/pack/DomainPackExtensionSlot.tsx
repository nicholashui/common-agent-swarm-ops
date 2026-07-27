"use client";

/**
 * @duty DomainPackExtensionSlot — domain-neutral pack UI extension slot
 * @role Host optional pack UI extensions by slotId from server manifests only.
 * @controls None required; children/metadata via SafeContent (inert).
 * @must Filter extensionsForSlot; no domain hard-coding in shell.
 * @mustnot Execute pack metadata as code or invent pack authority.
 * @redesign docs/frontend_redesign/component_duty_catalog.md §3.5; adoption pack slots
 *
 * Renders domain pack UI extensions for a named host slot without hard-coding
 * any domain (adoption_redesign: host supplies slots; packs supply metadata).
 */
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
