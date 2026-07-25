import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

import React from "react";
import { renderToStaticMarkup } from "react-dom/server";

import { ActionControl } from "../../components/projection/ActionControl";
import { ProjectionStatus } from "../../components/projection/ProjectionStatus";
import type { GeneratedActionReference, GeneratedOperationData, GeneratedOperationRequest, GeneratedOperationResult } from "../api/client";
import { ProjectionMapper } from "../projections/ProjectionMapper";
import { LiveProjectionController, type AuthorizedSubscriptionContext, type LiveOperationalEvent, type LiveProjectionSnapshot, type LiveSubscriptionHandlers } from "./LiveProjectionController";

const FIXTURES = resolve(dirname(fileURLToPath(import.meta.url)), "../../test/fixtures/frontend-redesign/v1");
const READ_RUN = "read_run_api_v1_workflow_runs__run_id__get" as const;
type RunProjection = GeneratedOperationData<typeof READ_RUN>;
type ReplayAnomaly = "bounded" | "expired" | "denied" | "schema_mismatch" | "duplicate" | "out_of_order" | "sequence_gap";
interface SnapshotFixture { readonly expectedSequence: number; readonly run: RunProjection; }
interface LiveFixture {
  readonly fixtureVersion: string; readonly scope: string; readonly schemaVersion: string; readonly authorizedTopics: readonly string[];
  readonly initial: SnapshotFixture; readonly replacement: SnapshotFixture; readonly replayAnomalies: readonly ReplayAnomaly[];
  readonly status: { readonly freshness: string; readonly degradedState: string; readonly actions: readonly GeneratedActionReference[] };
  readonly unavailable: { readonly message: string; readonly action: GeneratedActionReference };
}
interface RunEvent { readonly status: string; }
async function fixture(): Promise<LiveFixture> {
  return JSON.parse(await readFile(resolve(FIXTURES, "live-projection-traces.json"), "utf8")) as LiveFixture;
}

test("uses the versioned live trace fixture", async (): Promise<void> => {
  assert.equal((await fixture()).fixtureVersion, "frontend-redesign/v1");
});

class ScriptedGeneratedRunClientFake {
  public readonly requests: GeneratedOperationRequest<typeof READ_RUN>[] = [];
  private responseIndex = 0;
  public constructor(
    private readonly responses: readonly Promise<GeneratedOperationResult<RunProjection>>[],
    private readonly timeline: string[],
  ) {}
  public request(operation: typeof READ_RUN, request: GeneratedOperationRequest<typeof READ_RUN>): Promise<GeneratedOperationResult<RunProjection>> {
    assert.equal(operation, READ_RUN);
    this.timeline.push("REST");
    this.requests.push(request);
    const response = this.responses[this.responseIndex++];
    if (response === undefined) return Promise.reject(new Error("The generated-client fake has no scripted response."));
    return response;
  }
}

class FakeSubscription {
  public aborted = false;
  public constructor(private readonly handlers: LiveSubscriptionHandlers) {}
  public abort(): void { this.aborted = true; }
  public disconnected(): void { this.handlers.onDisconnected(); }
  public stale(): void { this.handlers.onStale(); }
}

function success(data: RunProjection): GeneratedOperationResult<RunProjection> {
  return { ok: true, data, correlationId: data.correlation_id };
}
function deferred<T,>(): { readonly promise: Promise<T>; readonly resolve: (value: T) => void } {
  let resolvePromise: ((value: T) => void) | undefined;
  const promise = new Promise<T>((resolve: (value: T) => void): void => { resolvePromise = resolve; });
  return { promise, resolve: (value: T): void => resolvePromise?.(value) };
}
function operationalEvent(fixtureData: LiveFixture, sequence: number, status: string): LiveOperationalEvent<RunEvent> {
  return { resourceScope: fixtureData.scope, schemaVersion: fixtureData.schemaVersion, sequence, eventId: `event-${sequence}`, payload: { status } };
}
function controllerFor(
  fixtureData: LiveFixture,
  client: ScriptedGeneratedRunClientFake,
  timeline: string[],
  subscriptions: FakeSubscription[],
): LiveProjectionController<RunProjection, RunEvent> {
  const snapshots = [fixtureData.initial, fixtureData.replacement];
  let snapshotIndex = 0;
  return new LiveProjectionController<RunProjection, RunEvent>({
    snapshotLoader: { loadSnapshot: async (scope: string): Promise<LiveProjectionSnapshot<RunProjection>> => {
      const snapshot = snapshots[snapshotIndex++];
      assert.ok(snapshot);
      const result = await client.request(READ_RUN, { path: { run_id: scope } });
      if (!result.ok) throw new Error(result.message);
      return { projection: result.data, schemaVersion: fixtureData.schemaVersion, expectedSequence: snapshot.expectedSequence,
        subscription: { scope, authorizedTopics: fixtureData.authorizedTopics, sequenceContext: { after_sequence: snapshot.expectedSequence - 1 } } };
    } },
    subscriptionFactory: { subscribe: (context: AuthorizedSubscriptionContext, handlers: LiveSubscriptionHandlers): FakeSubscription => {
      assert.deepEqual(context.authorizedTopics, fixtureData.authorizedTopics);
      timeline.push("SSE");
      const subscription = new FakeSubscription(handlers); subscriptions.push(subscription); return subscription;
    } },
    eventDecoder: { decode: (value: unknown): LiveOperationalEvent<RunEvent> | null => value as LiveOperationalEvent<RunEvent> },
    applyEvent: (projection: RunProjection, event: LiveOperationalEvent<RunEvent>): RunProjection => ({ ...projection, status: event.payload.status }),
  });
}

// Requirements 4.1–4.11, 11.4, 11.5
// Uses generated-operation types and a fixed generated-client fake; no network or hand-written endpoint DTO is used.
test("orders generated REST snapshots before SSE and preserves reconnecting and stale observation state", async (): Promise<void> => {
  const trace = await fixture(); const timeline: string[] = []; const subscriptions: FakeSubscription[] = [];
  const client = new ScriptedGeneratedRunClientFake([Promise.resolve(success(trace.initial.run))], timeline);
  const controller = controllerFor(trace, client, timeline, subscriptions);
  await controller.start(trace.scope);
  assert.deepEqual(timeline, ["REST", "SSE"]);
  assert.deepEqual(client.requests, [{ path: { run_id: trace.scope } }]);
  await controller.handleOperationalEvent(trace.scope, operationalEvent(trace, trace.initial.expectedSequence, "running"));
  assert.equal(controller.getState(trace.scope)?.projection?.status, "running");
  const subscription = subscriptions[0]; assert.ok(subscription);
  const beforeDisconnect = controller.getState(trace.scope)?.projection;
  subscription.disconnected(); assert.equal(controller.getState(trace.scope)?.connection, "reconnecting");
  assert.deepEqual(controller.getState(trace.scope)?.projection, beforeDisconnect);
  subscription.stale(); assert.equal(controller.getState(trace.scope)?.connection, "stale");
});

async function triggerAnomaly(
  controller: LiveProjectionController<RunProjection, RunEvent>, trace: LiveFixture, anomaly: ReplayAnomaly,
): Promise<void> {
  if (anomaly === "bounded" || anomaly === "expired" || anomaly === "denied") return controller.handleReplayAnomaly(trace.scope);
  const sequence = anomaly === "duplicate" ? trace.initial.expectedSequence - 1
    : anomaly === "out_of_order" ? trace.initial.expectedSequence + 2 : trace.initial.expectedSequence + 3;
  const schemaVersion = anomaly === "schema_mismatch" ? `${trace.schemaVersion}-incompatible` : trace.schemaVersion;
  return controller.handleOperationalEvent(trace.scope, { ...operationalEvent(trace, sequence, "ignored"), schemaVersion });
}

test("replaces incremental state before accepting later events for every fixed replay anomaly", async (): Promise<void> => {
  const trace = await fixture();
  for (const anomaly of trace.replayAnomalies) {
    const timeline: string[] = []; const subscriptions: FakeSubscription[] = [];
    const replacement = deferred<GeneratedOperationResult<RunProjection>>();
    const client = new ScriptedGeneratedRunClientFake([Promise.resolve(success(trace.initial.run)), replacement.promise], timeline);
    const controller = controllerFor(trace, client, timeline, subscriptions);
    await controller.start(trace.scope);
    const recovery = triggerAnomaly(controller, trace, anomaly);
    assert.equal(subscriptions[0]?.aborted, true, anomaly);
    assert.deepEqual(controller.getState(trace.scope)?.projection, null, anomaly);
    await controller.handleOperationalEvent(trace.scope, operationalEvent(trace, trace.initial.expectedSequence, "must-not-apply"));
    replacement.resolve(success(trace.replacement.run)); await recovery;
    assert.deepEqual(timeline, ["REST", "SSE", "REST", "SSE"], anomaly);
    assert.equal(controller.getState(trace.scope)?.projection?.status, trace.replacement.run.status, anomaly);
    await controller.handleOperationalEvent(trace.scope, operationalEvent(trace, trace.replacement.expectedSequence, "complete"));
    assert.equal(controller.getState(trace.scope)?.projection?.status, "complete", anomaly);
  }
});

test("serializes simultaneous replay anomalies through one generated REST replacement", async (): Promise<void> => {
  const trace = await fixture();
  const timeline: string[] = [];
  const subscriptions: FakeSubscription[] = [];
  const replacement = deferred<GeneratedOperationResult<RunProjection>>();
  const client = new ScriptedGeneratedRunClientFake([Promise.resolve(success(trace.initial.run)), replacement.promise], timeline);
  const controller = controllerFor(trace, client, timeline, subscriptions);

  await controller.start(trace.scope);
  const firstRecovery = controller.handleReplayAnomaly(trace.scope);
  const concurrentRecovery = controller.handleOperationalEvent(
    trace.scope,
    operationalEvent(trace, trace.initial.expectedSequence + 3, "must-not-apply"),
  );

  assert.equal(client.requests.length, 2);
  assert.equal(subscriptions[0]?.aborted, true);
  assert.deepEqual(controller.getState(trace.scope)?.projection, null);
  replacement.resolve(success(trace.replacement.run));
  await Promise.all([firstRecovery, concurrentRecovery]);

  assert.deepEqual(timeline, ["REST", "SSE", "REST", "SSE"]);
  assert.equal(controller.getState(trace.scope)?.projection?.status, trace.replacement.run.status);
});

test("uses generated action fakes to render stale status and block freshness-critical invocation", async (): Promise<void> => {
  const trace = await fixture(); const client = new ScriptedGeneratedRunClientFake([Promise.resolve(success(trace.initial.run))], []);
  const result = await client.request(READ_RUN, { path: { run_id: trace.scope } }); assert.ok(result.ok);
  const mapper = new ProjectionMapper(); const actions = trace.status.actions.map((source: GeneratedActionReference) => mapper.mapActionReference(source));
  assert.ok(actions.every((action) => action !== null));
  const mappedActions = actions.filter((action): action is NonNullable<typeof action> => action !== null);
  const markup = renderToStaticMarkup(<ProjectionStatus projection={{ stateLabel: result.data.status, asOf: result.data.updated_at, freshness: trace.status.freshness, degradedState: trace.status.degradedState }} stale actions={mappedActions} onInvokeAction={(): void => undefined} onResolveAlert={(): void => undefined} />);
  assert.match(markup, /Status: Stale/); assert.match(markup, />Stale</); assert.match(markup, /Delayed|outbox lag/); assert.doesNotMatch(markup, /Promote rollout/);
  const critical = mappedActions.find((action) => action.id === "promote-fixture"); assert.ok(critical);
  let invoked = 0; const control = ActionControl({ action: critical, stale: true, onInvoke: (): void => { invoked += 1; } });
  assert.equal(control.props.disabled, true); control.props.onClick(); assert.equal(invoked, 0);
});

test("renders an unavailable state from only the generated safe error and returned recovery action", async (): Promise<void> => {
  const trace = await fixture(); const client = new ScriptedGeneratedRunClientFake([Promise.resolve({ ok: false, code: "projection_unavailable", message: trace.unavailable.message, retryable: true, actionReference: trace.unavailable.action })], []);
  const result = await client.request(READ_RUN, { path: { run_id: trace.scope } }); assert.equal(result.ok, false);
  if (result.ok) throw new Error("Expected the generated-client fake to return the unavailable result.");
  const action = new ProjectionMapper().mapActionReference(result.actionReference ?? {}); assert.ok(action);
  const markup = renderToStaticMarkup(<ProjectionStatus projection={{ stateLabel: "PROTECTED_STATE", asOf: "PROTECTED_AS_OF" }} stale={false} actions={[action]} unavailable={{ message: result.message }} onInvokeAction={(): void => undefined} onResolveAlert={(): void => undefined} />);
  assert.match(markup, /The authorized health projection is unavailable\./); assert.match(markup, /Refresh operational projection/);
  assert.doesNotMatch(markup, /PROTECTED_STATE|PROTECTED_AS_OF|Status:/);
});
