import assert from "node:assert/strict";
import test from "node:test";

import fc from "fast-check";
import React from "react";
import { renderToStaticMarkup } from "react-dom/server";

import { formatOperationalAnnouncement, OperationalAnnouncer, operationalStatusTransitionKey } from "./OperationalAnnouncer";
import { ResponsiveActionGroup, ResponsiveSplit, ResponsiveStack } from "./ResponsiveLayout";
import { ActionControl } from "./projection/ActionControl";
import { EvidenceLink } from "./projection/EvidenceLink";
import { ProjectionStatus } from "./projection/ProjectionStatus";
import type { ActionReferenceView, EvidenceReferenceView } from "../lib/projections/ProjectionMapper";

const RETURNED_STATE_UNIONS = [
  ["queued", "running", "self_refine", "waiting_for_critique", "blocked", "failed", "complete", "cancelling", "cancelled", "manual_recovery_required"],
  ["Live", "Delayed", "Reconnecting", "Degraded", "Unavailable", "Stale"],
  ["validating", "quarantined", "processing", "indexed", "rejected", "archived"],
  ["L1 specification validation", "L2 role-rubric evaluation", "L3 baseline preference", "critique", "gate outcome", "human approval"],
  ["pending", "approved", "denied", "expired"], ["recovery required", "reconciled"], ["blocked from delivery", "delivered"],
  ["eligible", "ineligible"], ["rights cleared", "rights restricted"], ["consent granted", "consent missing"],
] as const;

interface Scenario { readonly viewportWidth: number; readonly resourceName: string; readonly asOf: string; readonly freshness: string; readonly recovery: string; readonly approval: string; readonly evidenceSummary: string; readonly id: string; }
const identifierArbitrary = fc.uuid().map((value: string): string => value.replaceAll("-", ""));
const scenarioArbitrary: fc.Arbitrary<Scenario> = fc.tuple(fc.integer({ min: 320, max: 767 }), identifierArbitrary, fc.integer({ min: 0, max: 2_000_000_000 }), identifierArbitrary).map(([viewportWidth, id, seconds, suffix]): Scenario => ({ viewportWidth, resourceName: `Run 🚀 ${id}`, asOf: new Date(seconds * 1_000).toISOString(), freshness: `Freshness Δ ${suffix}`, recovery: `Recovery Δ ${suffix}`, approval: `Approval Δ ${suffix}`, evidenceSummary: `Evidence Δ ${suffix}`, id }));

function actionFor(scenario: Scenario): ActionReferenceView {
  const label = `Reconnect live updates ${scenario.id}`;
  return { id: `action-${scenario.id}`, label, eligible: true, kind: "reconnect", source: { id: `action-${scenario.id}`, label, eligible: true, kind: "reconnect" } };
}

function evidenceFor(scenario: Scenario): EvidenceReferenceView {
  return { id: `evidence-${scenario.id}`, label: `Evidence ${scenario.id}`, presentation: { fields: { summary: scenario.evidenceSummary } }, source: { id: `evidence-${scenario.id}`, label: `Evidence ${scenario.id}`, summary: scenario.evidenceSummary } };
}

function renderOperationalScreen(scenario: Scenario, stateLabel: string, viewportWidth: number): string {
  const action = actionFor(scenario); const evidence = evidenceFor(scenario);
  return renderToStaticMarkup(<main data-viewport-width={viewportWidth}><ResponsiveStack><ProjectionStatus actions={[action]} onInvokeAction={(): void => undefined} onResolveAlert={(): void => undefined} projection={{ stateLabel, asOf: scenario.asOf, freshness: scenario.freshness }} stale={false} /><ResponsiveSplit primary={<dl><dt>Recovery</dt><dd>{scenario.recovery}</dd><dt>Approval</dt><dd>{scenario.approval}</dd><EvidenceLink evidence={evidence} /></dl>} secondary={<ResponsiveActionGroup><ActionControl action={action} onInvoke={(): void => undefined} stale={false} /></ResponsiveActionGroup>} /></ResponsiveStack></main>);
}

function normalizedMarkup(markup: string): string {
  return markup.replace(/ data-viewport-width="\d+"/, "");
}

function assertAccessibleSemantics(scenario: Scenario): void {
  const action = actionFor(scenario);
  const actionMarkup = renderToStaticMarkup(<ActionControl action={action} onInvoke={(): void => undefined} stale={false} />);
  assert.match(actionMarkup, new RegExp(`>${action.label}</button>`));
  assert.doesNotMatch(actionMarkup, /aria-label=/);

  for (const union of RETURNED_STATE_UNIONS) for (const stateLabel of union) {
    const desktopMarkup = renderOperationalScreen(scenario, stateLabel, 1440);
    const mobileMarkup = renderOperationalScreen(scenario, stateLabel, scenario.viewportWidth);
    assert.equal(normalizedMarkup(mobileMarkup), normalizedMarkup(desktopMarkup));
    for (const returnedValue of [stateLabel, scenario.asOf, scenario.freshness, scenario.recovery, scenario.approval, scenario.evidenceSummary, action.label, action.id, `evidence-${scenario.id}`]) {
      assert.ok(mobileMarkup.includes(returnedValue), `mobile layout must preserve ${returnedValue}`);
    }
  }

  const firstStateLabel = RETURNED_STATE_UNIONS[0][0];
  const transitionLabels = [firstStateLabel, firstStateLabel, ...RETURNED_STATE_UNIONS.slice(1).map((union): string => union[0])];
  const liveRegion = renderToStaticMarkup(<OperationalAnnouncer asOf={scenario.asOf} resourceName={scenario.resourceName} stateLabel={firstStateLabel} />);
  assert.match(liveRegion, /role="status"/); assert.match(liveRegion, /aria-live="polite"/); assert.match(liveRegion, /aria-atomic="true"/);
  let previousKey = operationalStatusTransitionKey({ resourceName: scenario.resourceName, stateLabel: transitionLabels[0]!, asOf: scenario.asOf });
  const announcements: string[] = [];
  for (const stateLabel of transitionLabels.slice(1)) {
    const announcement = { resourceName: scenario.resourceName, stateLabel, asOf: scenario.asOf };
    const currentKey = operationalStatusTransitionKey(announcement);
    if (currentKey !== previousKey) announcements.push(formatOperationalAnnouncement(announcement));
    previousKey = currentKey;
  }
  assert.equal(announcements.length, transitionLabels.length - 2);
  assert.deepEqual(announcements, transitionLabels.slice(2).map((stateLabel): string => `${scenario.resourceName}: ${stateLabel}; updated ${scenario.asOf}`));
  assert.equal(operationalStatusTransitionKey({ resourceName: scenario.resourceName, stateLabel: transitionLabels[0]!, asOf: scenario.asOf }), operationalStatusTransitionKey({ resourceName: scenario.resourceName, stateLabel: transitionLabels[0]!, asOf: `${scenario.asOf}-later` }));
}

// Feature: frontend-redesign, Property 14: Accessible semantic information survives labels, transitions, and mobile layout
// Validates: Requirements 10.1, 10.6, 10.7, 10.8
test("Property 14: preserves accessible semantic information across state unions and mobile widths", (): void => {
  fc.assert(fc.property(scenarioArbitrary, assertAccessibleSemantics), { numRuns: 100 });
});
