"use client";

import React, { useState } from "react";
import Link from "next/link";

import type { CommandIntent } from "../lib/commands/CommandCoordinator";
import type { GeneratedJsonObject } from "../lib/api/client";
import {
  createGraphCommandIntent,
  mapComposerProjection,
  type ComposerPatternView,
  type GraphCommandPayload,
} from "../lib/projections/graph-adapters";
import { VersionPill } from "./design";
export { ComposerHome } from "./ComposerHome";

const DEFAULT_COMPOSER_PROJECTION = {
  common_patterns: [
    {
      id: "pattern-parallel-verification-v1.4",
      label: "Parallel research + verification",
      immutable_version: "1.4",
      provenance_reference: "prov:common-pattern:parallel-verification:1.4",
      instantiation_action_reference: {
        id: "instantiate-pattern-parallel-verification-v1.4",
        label: "Instantiate pattern",
        eligible: true,
        kind: "instantiate",
      },
    },
  ],
} as const satisfies GeneratedJsonObject;

export interface ComposerProps {
  readonly projection?: GeneratedJsonObject;
  readonly onCommandIntent?: (
    intent: CommandIntent<GraphCommandPayload>,
  ) => void | Promise<void>;
}

/** Projection-bound composer used by contract tests and command integration. */
export function Composer({
  projection = DEFAULT_COMPOSER_PROJECTION,
  onCommandIntent,
}: ComposerProps): JSX.Element {
  const composer = mapComposerProjection(projection);
  const [selectedPatternId, setSelectedPatternId] = useState<string | undefined>(
    composer.patterns[0]?.id,
  );
  const selectedPattern = composer.patterns.find(
    (pattern) => pattern.id === selectedPatternId,
  );

  return (
    <>
      <header className="composer-header">
        <div>
          <p className="eyebrow">NEW SWARM DRAFT</p>
          <h1>Swarm composer</h1>
          <input aria-label="Swarm name" defaultValue="Untitled swarm" />
        </div>
        <div className="button-row">
          <button className="button button--secondary" type="button">
            Save draft
          </button>
          <Link className="button button--ghost" href="/">
            Close
          </Link>
        </div>
      </header>
      <div className="composer-layout">
        <section className="composer-chat">
          <div className="architect-note">
            <span>✦</span>
            <div>
              <strong>Common Swarm Architect</strong>
              <p>
                Compose from returned common patterns and their immutable
                provenance.
              </p>
            </div>
          </div>
          {selectedPattern === undefined ? (
            <p className="muted">No authorized common pattern is available.</p>
          ) : (
            <Recommendation
              onCommandIntent={onCommandIntent}
              pattern={selectedPattern}
            />
          )}
          <label className="composer-input">
            <textarea
              aria-label="Describe your swarm goal"
              defaultValue="Build a daily market intelligence swarm with evidence verification."
            />
            <button className="button button--primary" type="button">
              Send <span>↑</span>
            </button>
          </label>
        </section>
        <aside className="pattern-browser">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">COMMON PATTERNS</p>
              <h2>Pattern browser</h2>
            </div>
          </div>
          {composer.patterns.map((pattern) => (
            <button
              aria-pressed={selectedPatternId === pattern.id}
              className={
                selectedPatternId === pattern.id
                  ? "pattern-option pattern-option--selected"
                  : "pattern-option"
              }
              key={pattern.id}
              onClick={(): void => setSelectedPatternId(pattern.id)}
              type="button"
            >
              <div className="mini-graph mini-graph--compact" aria-hidden="true">
                <i />
                <i />
                <i />
                <b />
                <b />
              </div>
              <div>
                <VersionPill version={pattern.immutableVersion} label="Common pattern" />
                <strong>{pattern.label}</strong>
                <span>Provenance: {pattern.provenanceReference}</span>
                <em>Immutable version {pattern.immutableVersion}</em>
              </div>
            </button>
          ))}
        </aside>
      </div>
    </>
  );
}

function Recommendation({
  pattern,
  onCommandIntent,
}: {
  readonly pattern: ComposerPatternView;
  readonly onCommandIntent: ComposerProps["onCommandIntent"];
}): JSX.Element {
  const intent =
    pattern.instantiationAction === undefined
      ? undefined
      : createGraphCommandIntent(pattern.instantiationAction);
  const disabled = intent === undefined || onCommandIntent === undefined;
  return (
    <div className="message message--assistant">
      <p>Recommended common pattern</p>
      <article className="recommendation">
        <div>
          <VersionPill version={pattern.immutableVersion} label="Common pattern" />
          <h2>{pattern.label}</h2>
          <p>Provenance: {pattern.provenanceReference}</p>
        </div>
        {pattern.instantiationAction === undefined ? null : (
          <button
            className="button button--primary"
            disabled={disabled}
            onClick={(): void => {
              if (intent !== undefined && onCommandIntent !== undefined) {
                void onCommandIntent(intent);
              }
            }}
            type="button"
          >
            {pattern.instantiationAction.label}
          </button>
        )}
      </article>
    </div>
  );
}
