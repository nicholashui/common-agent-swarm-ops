import assert from "node:assert/strict";
import test from "node:test";

import {
  InMemoryLiveProjectionCursorStore,
  LiveProjectionController,
  type AuthorizedSubscriptionContext,
  type LiveOperationalEvent,
  type LiveProjectionSnapshot,
  type LiveSubscriptionHandlers,
} from "./LiveProjectionController";

interface CounterProjection {
  readonly count: number;
}

interface CounterEvent {
  readonly delta: number;
}

class FakeSubscription {
  public aborted = false;

  public constructor(private readonly handlers: LiveSubscriptionHandlers) {}

  public abort(): void { this.aborted = true; }
  public connected(): void { this.handlers.onConnected(); }
  public disconnected(): void { this.handlers.onDisconnected(); }
  public stale(): void { this.handlers.onStale(); }
  public emit(event: unknown): void { this.handlers.onOperationalEvent(event); }
}

function snapshot(scope: string, count: number, expectedSequence: number): LiveProjectionSnapshot<CounterProjection> {
  return {
    projection: { count },
    schemaVersion: "1.0.0",
    expectedSequence,
    subscription: {
      scope,
      authorizedTopics: ["run.updated"],
      sequenceContext: { after_sequence: expectedSequence - 1 },
    },
  };
}

function event(scope: string, sequence: number, delta: number, eventId = `event-${sequence}`): LiveOperationalEvent<CounterEvent> {
  return { resourceScope: scope, schemaVersion: "1.0.0", sequence, eventId, payload: { delta } };
}

function deferred<T>(): { readonly promise: Promise<T>; readonly resolve: (value: T) => void } {
  let resolvePromise: ((value: T) => void) | undefined;
  const promise = new Promise<T>((resolve: (value: T) => void): void => { resolvePromise = resolve; });
  return { promise, resolve: (value: T): void => resolvePromise?.(value) };
}

test("loads a snapshot before subscribing, then accepts only the exact next event and persists its cursor", async () => {
  const initial = deferred<LiveProjectionSnapshot<CounterProjection>>();
  const contexts: AuthorizedSubscriptionContext[] = [];
  const subscriptions: FakeSubscription[] = [];
  const cursors = new InMemoryLiveProjectionCursorStore();
  const controller = new LiveProjectionController<CounterProjection, CounterEvent>({
    snapshotLoader: { loadSnapshot: (): Promise<LiveProjectionSnapshot<CounterProjection>> => initial.promise },
    subscriptionFactory: {
      subscribe: (context: AuthorizedSubscriptionContext, handlers: LiveSubscriptionHandlers): FakeSubscription => {
        contexts.push(context);
        const subscription = new FakeSubscription(handlers);
        subscriptions.push(subscription);
        return subscription;
      },
    },
    eventDecoder: { decode: (value: unknown): LiveOperationalEvent<CounterEvent> | null => value as LiveOperationalEvent<CounterEvent> },
    applyEvent: (projection: CounterProjection, accepted: LiveOperationalEvent<CounterEvent>): CounterProjection => ({ count: projection.count + accepted.payload.delta }),
    cursorStore: cursors,
  });

  const started = controller.start("run-1");
  assert.equal(controller.getState("run-1")?.connection, "loadingSnapshot");
  assert.equal(contexts.length, 0);
  const initialSnapshot = snapshot("run-1", 2, 5);
  initial.resolve(initialSnapshot);
  await started;

  assert.strictEqual(contexts[0], initialSnapshot.subscription);
  assert.equal(subscriptions.length, 1);
  await controller.handleOperationalEvent("run-1", event("run-1", 5, 3));
  assert.deepEqual(controller.getState("run-1"), {
    projection: { count: 5 }, subscriptionScope: "run-1", expectedSequence: 6,
    schemaVersion: "1.0.0", eventCursor: "event-5", connection: "live",
  });
  assert.equal(cursors.read("run-1"), "event-5");
});

test("serializes replay-anomaly resynchronization and discards incremental state and cursors", async () => {
  const recovered = deferred<LiveProjectionSnapshot<CounterProjection>>();
  let loads = 0;
  const subscriptions: FakeSubscription[] = [];
  const cursors = new InMemoryLiveProjectionCursorStore();
  const controller = new LiveProjectionController<CounterProjection, CounterEvent>({
    snapshotLoader: { loadSnapshot: (): Promise<LiveProjectionSnapshot<CounterProjection>> => {
      loads += 1;
      return loads === 1 ? Promise.resolve(snapshot("run-1", 4, 7)) : recovered.promise;
    } },
    subscriptionFactory: { subscribe: (_context: AuthorizedSubscriptionContext, handlers: LiveSubscriptionHandlers): FakeSubscription => {
      const subscription = new FakeSubscription(handlers); subscriptions.push(subscription); return subscription;
    } },
    eventDecoder: { decode: (value: unknown): LiveOperationalEvent<CounterEvent> | null => value as LiveOperationalEvent<CounterEvent> },
    applyEvent: (projection: CounterProjection, accepted: LiveOperationalEvent<CounterEvent>): CounterProjection => ({ count: projection.count + accepted.payload.delta }),
    cursorStore: cursors,
  });

  await controller.start("run-1");
  await controller.handleOperationalEvent("run-1", event("run-1", 7, 1, "cursor-before-gap"));
  const firstRecovery = controller.handleOperationalEvent("run-1", event("run-1", 10, 1));
  const secondRecovery = controller.handleReplayAnomaly("run-1");
  assert.equal(loads, 2);
  assert.equal(subscriptions[0]?.aborted, true);
  assert.deepEqual(controller.getState("run-1"), {
    projection: null, subscriptionScope: "run-1", expectedSequence: null,
    schemaVersion: null, eventCursor: null, connection: "resynchronizing",
  });
  assert.equal(cursors.read("run-1"), null);

  recovered.resolve(snapshot("run-1", 20, 30));
  await Promise.all([firstRecovery, secondRecovery]);
  assert.equal(subscriptions.length, 2);
  assert.deepEqual(controller.getState("run-1"), {
    projection: { count: 20 }, subscriptionScope: "run-1", expectedSequence: 30,
    schemaVersion: "1.0.0", eventCursor: null, connection: "live",
  });
});

test("represents connection changes without changing projection facts and abort blocks stale callbacks", async () => {
  const subscriptions: FakeSubscription[] = [];
  const controller = new LiveProjectionController<CounterProjection, CounterEvent>({
    snapshotLoader: { loadSnapshot: (): Promise<LiveProjectionSnapshot<CounterProjection>> => Promise.resolve(snapshot("run-1", 9, 12)) },
    subscriptionFactory: { subscribe: (_context: AuthorizedSubscriptionContext, handlers: LiveSubscriptionHandlers): FakeSubscription => {
      const subscription = new FakeSubscription(handlers); subscriptions.push(subscription); return subscription;
    } },
    eventDecoder: { decode: (value: unknown): LiveOperationalEvent<CounterEvent> | null => value as LiveOperationalEvent<CounterEvent> },
    applyEvent: (projection: CounterProjection, accepted: LiveOperationalEvent<CounterEvent>): CounterProjection => ({ count: projection.count + accepted.payload.delta }),
  });

  await controller.start("run-1");
  subscriptions[0]?.disconnected();
  assert.equal(controller.getState("run-1")?.connection, "reconnecting");
  assert.deepEqual(controller.getState("run-1")?.projection, { count: 9 });
  subscriptions[0]?.stale();
  assert.equal(controller.getState("run-1")?.connection, "stale");

  controller.abort();
  assert.equal(subscriptions[0]?.aborted, true);
  subscriptions[0]?.emit(event("run-1", 12, 8));
  await Promise.resolve();
  assert.deepEqual(controller.getState("run-1")?.projection, { count: 9 });
});
