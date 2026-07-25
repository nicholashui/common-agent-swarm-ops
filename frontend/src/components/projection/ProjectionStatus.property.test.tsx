import assert from "node:assert/strict";
import test from "node:test";

import fc from "fast-check";
import React from "react";
import { renderToStaticMarkup } from "react-dom/server";

import { ActionControl } from "./ActionControl";
import { ProjectionStatus, type ProjectionStatusData } from "./ProjectionStatus";
import type { GeneratedActionReference } from "../../lib/api/client";
import type { ActionReferenceView, OpaqueReferenceView } from "../../lib/projections/ProjectionMapper";

type ProjectionKind = "health" | "canvas" | "approval" | "rollout" | "alert";
interface FreshnessCase {
  readonly kind: ProjectionKind;
  readonly stale: boolean;
  readonly projection: ProjectionStatusData;
  readonly alert: { readonly summary: string; readonly affectedReference: OpaqueReferenceView };
  readonly recoveryActions: readonly ActionReferenceView[];
  readonly gatedActions: readonly ActionReferenceView[];
}

const identifierArbitrary = fc.uuid().map((value: string): string => value.replaceAll("-", ""));
const textArbitrary = (prefix: string): fc.Arbitrary<string> => identifierArbitrary.map((value: string): string => `${prefix}-${value}`);
const asOfArbitrary = fc.integer({ min: 0, max: 2_000_000_000 }).map((seconds: number): string => new Date(seconds * 1_000).toISOString());

function action(id: string, label: string, kind: string, freshnessCritical = false, irreversible = false): ActionReferenceView {
  const source: GeneratedActionReference = { id, label, eligible: true, kind, freshness_critical: freshnessCritical, irreversible };
  return { id, label, eligible: true, kind, freshnessCritical, irreversible, source };
}

const recoveryActionsArbitrary = fc.tuple(fc.boolean(), fc.boolean(), identifierArbitrary).map(([refresh, reconnect, id]): readonly ActionReferenceView[] => [
  ...(refresh ? [action(`refresh-${id}`, `Refresh-${id}`, "refresh")] : []),
  ...(reconnect ? [action(`reconnect-${id}`, `Reconnect-${id}`, "reconnect")] : []),
]);
const gateArbitrary = fc.constantFrom({ freshnessCritical: true, irreversible: false }, { freshnessCritical: false, irreversible: true }, { freshnessCritical: true, irreversible: true });
const gatedActionsArbitrary = fc.array(fc.tuple(identifierArbitrary, fc.constantFrom("run", "approve", "promote", "rollback"), gateArbitrary)
  .map(([id, kind, gate]): ActionReferenceView => action(`action-${id}`, `${kind}-${id}`, kind, gate.freshnessCritical, gate.irreversible)), { minLength: 1, maxLength: 3 });

function caseArbitrary(kind: ProjectionKind): fc.Arbitrary<FreshnessCase> {
  return fc.tuple(fc.boolean(), asOfArbitrary, textArbitrary(`${kind}-state`), textArbitrary(`${kind}-freshness`), fc.boolean(), textArbitrary(`${kind}-alert`), identifierArbitrary, recoveryActionsArbitrary, gatedActionsArbitrary)
    .map(([stale, asOf, stateLabel, freshness, degradedState, summary, id, recoveryActions, gatedActions]): FreshnessCase => ({
      kind,
      stale,
      projection: { stateLabel, asOf, freshness, degradedState },
      alert: { summary, affectedReference: { id: `${kind}-reference-${id}`, label: `${kind}-reference-${id}`, source: { id: `${kind}-reference-${id}`, label: `${kind}-reference-${id}` } } },
      recoveryActions,
      gatedActions,
    }));
}

function assertInvokes(actionReference: ActionReferenceView, stale: boolean, expectedToInvoke: boolean): void {
  let invoked: GeneratedActionReference | undefined;
  const control = ActionControl({ action: actionReference, stale, onInvoke: (reference: GeneratedActionReference): void => { invoked = reference; } });
  assert.equal(control.props.disabled, !expectedToInvoke);
  control.props.onClick();
  assert.strictEqual(invoked, expectedToInvoke ? actionReference.source : undefined);
}

function assertFreshnessPresentation(item: FreshnessCase): void {
  const markup = renderToStaticMarkup(<ProjectionStatus actions={[...item.recoveryActions, ...item.gatedActions]} alerts={[item.alert]} onInvokeAction={(): void => undefined} onResolveAlert={(): void => undefined} projection={item.projection} stale={item.stale} />);
  const displayedState = item.stale ? "Stale" : item.projection.stateLabel;
  assert.ok(markup.includes(`aria-label="Status: ${displayedState}"`), `${item.kind} must name its status icon exactly`);
  assert.ok(markup.includes(`>${displayedState}</span>`), `${item.kind} must render its textual state exactly`);
  assert.ok(markup.includes(item.projection.asOf ?? ""));
  assert.ok(markup.includes(item.projection.freshness ?? ""));
  assert.ok(markup.includes(`>${String(item.projection.degradedState)}</dd>`));
  assert.ok(markup.includes(item.alert.summary));
  assert.ok(markup.includes(`data-opaque-reference-id="${item.alert.affectedReference.id}"`));
  for (const recoveryAction of item.recoveryActions) {
    assert.ok(markup.includes(recoveryAction.label), `${item.kind} must expose only the returned recovery action`);
    assertInvokes(recoveryAction, item.stale, true);
  }
  for (const gatedAction of item.gatedActions) {
    assert.equal(markup.includes(gatedAction.label), false, `${item.kind} must not present non-recovery actions in the status region`);
    assertInvokes(gatedAction, item.stale, !item.stale);
  }
}

// Feature: frontend-redesign, Property 8: Freshness presentation is exact and safely gates actions
// Validates: Requirements 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 6.15, 7.4
test("Property 8: presents exact freshness and gates actions in every projection context", (): void => {
  fc.assert(fc.property(
    fc.tuple(caseArbitrary("health"), caseArbitrary("canvas"), caseArbitrary("approval"), caseArbitrary("rollout"), caseArbitrary("alert")),
    (items: readonly FreshnessCase[]): void => { items.forEach(assertFreshnessPresentation); },
  ), { numRuns: 100 });
});
