"use client";

/**
 * @duty Composer — legacy composer screen + export alias
 * @role Presentational/legacy composer path; prefer ComposerHome for routes.
 * @controls Pattern/graph controls mapped from projection; commands via intents.
 * @mustnot Bypass host command coordinator or invent action refs.
 * @redesign docs/frontend_redesign/ui_03_swarm_composer.md
 */
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
  const [swarmName, setSwarmName] = useState("Untitled swarm");
  const [goal, setGoal] = useState(
    "Build a daily market intelligence swarm with evidence verification.",
  );
  const [statusNote, setStatusNote] = useState<string | undefined>();
  const selectedPattern = composer.patterns.find(
    (pattern) => pattern.id === selectedPatternId,
  );

  return (
    <>
      <header className="composer-header">
        <div>
          <p className="eyebrow">NEW SWARM DRAFT</p>
          <h1>Plan</h1>
          <input
            aria-label="Swarm name"
            onChange={(event): void => setSwarmName(event.target.value)}
            value={swarmName}
          />
          {statusNote ? (
            <p aria-live="polite" role="status">
              {statusNote}
            </p>
          ) : null}
        </div>
        <div className="button-row">
          <button
            className="button button--secondary"
            onClick={(): void => {
              setStatusNote(
                `Draft “${swarmName}” saved locally (session only). Host persistence requires an authorized compose action.`,
              );
            }}
            type="button"
          >
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
                Plan from returned common patterns and their immutable
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
              onChange={(event): void => setGoal(event.target.value)}
              value={goal}
            />
            <button
              className="button button--primary"
              onClick={(): void => {
                const trimmed = goal.trim();
                if (trimmed.length === 0) {
                  setStatusNote("Enter a swarm goal before sending.");
                  return;
                }
                if (onCommandIntent !== undefined && selectedPattern?.instantiationAction) {
                  const intent = createGraphCommandIntent(
                    selectedPattern.instantiationAction,
                    undefined,
                  );
                  if (intent !== undefined) {
                    void onCommandIntent(intent);
                    setStatusNote(`Sent compose intent for “${swarmName}”.`);
                    return;
                  }
                }
                setStatusNote(
                  `Compose send for “${swarmName}” requires an authorized compose action reference. Goal kept locally.`,
                );
              }}
              type="button"
            >
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
