import assert from "node:assert/strict";
import test from "node:test";

import React from "react";
import { renderToStaticMarkup } from "react-dom/server";

import { ActionControl } from "./ActionControl";
import { ProjectionStatus, isProjectionRecoveryAction } from "./ProjectionStatus";
import type { ActionReferenceView, OpaqueReferenceView } from "../../lib/projections/ProjectionMapper";

const refreshAction: ActionReferenceView = {
  id: "refresh-1", label: "Refresh operational projection", eligible: true, kind: "refresh",
  source: { id: "refresh-1", label: "Refresh operational projection", eligible: true, kind: "refresh" },
};
const reconnectAction: ActionReferenceView = {
  id: "reconnect-1", label: "Reconnect live updates", eligible: true, kind: "reconnect",
  source: { id: "reconnect-1", label: "Reconnect live updates", eligible: true, kind: "reconnect" },
};
const criticalAction: ActionReferenceView = {
  id: "promote-1", label: "Promote rollout", eligible: true, freshnessCritical: true, irreversible: true, kind: "promote",
  source: { id: "promote-1", label: "Promote rollout", eligible: true, freshness_critical: true, irreversible: true, kind: "promote" },
};
const alertReference: OpaqueReferenceView = {
  id: "run-1", label: "Affected run", source: { id: "run-1", label: "Affected run" },
};

// Requirements 5.2–5.7, 6.15, 7.4, 10.7
const requiredProps = {
  projection: { stateLabel: "Live", asOf: "2026-03-02T12:00:00Z", freshness: "Delayed", degradedState: true },
  actions: [refreshAction, reconnectAction, criticalAction],
  alerts: [{ summary: "The returned run backlog is delayed.", affectedReference: alertReference }],
  onInvokeAction: (): void => {},
  onResolveAlert: (): void => {},
} as const;

test("renders returned freshness values, stale label, named icon, alert summary, and only returned recovery controls", () => {
  const markup = renderToStaticMarkup(<ProjectionStatus {...requiredProps} stale />);

  assert.match(markup, /Status: Stale/);
  assert.match(markup, />Stale</);
  assert.match(markup, /2026-03-02T12:00:00Z/);
  assert.match(markup, />Delayed</);
  assert.match(markup, />true</);
  assert.match(markup, /The returned run backlog is delayed\./);
  assert.match(markup, /data-opaque-reference-id="run-1"/);
  assert.match(markup, /Refresh operational projection/);
  assert.match(markup, /Reconnect live updates/);
  assert.doesNotMatch(markup, /Promote rollout/);
  assert.equal(isProjectionRecoveryAction(refreshAction), true);
  assert.equal(isProjectionRecoveryAction(reconnectAction), true);
  assert.equal(isProjectionRecoveryAction(criticalAction), false);
});

test("stale gating blocks freshness-critical actions but permits returned refresh and reconnect actions", () => {
  let invocations = 0;
  const blocked = ActionControl({ action: criticalAction, stale: true, onInvoke: (): void => { invocations += 1; } });
  assert.equal(blocked.props.disabled, true);
  blocked.props.onClick();
  assert.equal(invocations, 0);

  const refresh = ActionControl({ action: refreshAction, stale: true, onInvoke: (): void => { invocations += 1; } });
  const reconnect = ActionControl({ action: reconnectAction, stale: true, onInvoke: (): void => { invocations += 1; } });
  assert.equal(refresh.props.disabled, false);
  assert.equal(reconnect.props.disabled, false);
  refresh.props.onClick();
  reconnect.props.onClick();
  assert.equal(invocations, 2);
});

test("unavailable status renders only the returned safe error and returned recovery controls", () => {
  const markup = renderToStaticMarkup(<ProjectionStatus {...requiredProps} unavailable={{ message: "Health data is temporarily unavailable." }} stale={false} />);

  assert.match(markup, /Health data is temporarily unavailable\./);
  assert.match(markup, /Refresh operational projection/);
  assert.match(markup, /Reconnect live updates/);
  assert.doesNotMatch(markup, /2026-03-02T12:00:00Z|Delayed|The returned run backlog|Promote rollout|Status: Live/);
});
