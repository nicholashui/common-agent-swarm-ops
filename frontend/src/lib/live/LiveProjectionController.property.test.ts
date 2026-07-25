import assert from "node:assert/strict";
import test from "node:test";
import fc from "fast-check";
import { LiveProjectionController, type AuthorizedSubscriptionContext, type LiveOperationalEvent, type LiveProjectionSnapshot } from "./LiveProjectionController";

interface CounterProjection { readonly value: number; }
interface CounterEvent { readonly delta: number; }
const nonBlankStringArbitrary = fc.string({ minLength: 1, maxLength: 64 }).filter((value: string): boolean => value.trim().length > 0);

function deferred<T>(): { readonly promise: Promise<T>; readonly resolve: (value: T) => void } {
  let resolvePromise: ((value: T) => void) | undefined;
  const promise = new Promise<T>((resolve: (value: T) => void): void => { resolvePromise = resolve; });
  return { promise, resolve: (value: T): void => resolvePromise?.(value) };
}

type UnsafeReplayOutcome = "duplicate" | "gap" | "expiry" | "denial" | "bounded" | "incompatible";

interface ReplacementResynchronizationScenario {
  readonly outcome: UnsafeReplayOutcome;
  readonly scope: string;
  readonly initialValue: number;
  readonly initialExpectedSequence: number;
  readonly incrementalDelta: number;
  readonly replacementValue: number;
  readonly replacementExpectedSequence: number;
}

const unsafeReplayOutcomeArbitrary = fc.constantFrom<UnsafeReplayOutcome>(
  "duplicate",
  "gap",
  "expiry",
  "denial",
  "bounded",
  "incompatible",
);
const replacementResynchronizationScenarioArbitrary: fc.Arbitrary<ReplacementResynchronizationScenario> = fc.tuple(
  unsafeReplayOutcomeArbitrary,
  nonBlankStringArbitrary,
  fc.integer({ min: -10_000, max: 10_000 }),
  fc.integer({ min: 0, max: 10_000 }),
  fc.integer({ min: -100, max: 100 }),
  fc.integer({ min: -10_000, max: 10_000 }),
  fc.integer({ min: 0, max: 10_000 }),
).map(([outcome, scope, initialValue, initialExpectedSequence, incrementalDelta, replacementValue, replacementExpectedSequence]): ReplacementResynchronizationScenario => ({
  outcome,
  scope,
  initialValue,
  initialExpectedSequence,
  incrementalDelta,
  replacementValue,
  replacementExpectedSequence,
}));

function replacementSnapshotFor(scenario: ReplacementResynchronizationScenario): LiveProjectionSnapshot<CounterProjection> {
  return {
    projection: { value: scenario.replacementValue },
    schemaVersion: "1.0.0",
    expectedSequence: scenario.replacementExpectedSequence,
    subscription: {
      scope: scenario.scope,
      authorizedTopics: ["run.updated"],
      sequenceContext: { after_sequence: scenario.replacementExpectedSequence - 1 },
    },
  };
}

function unsafeEventFor(scenario: ReplacementResynchronizationScenario): LiveOperationalEvent<CounterEvent> | null {
  const expectedAfterIncrementalEvent = scenario.initialExpectedSequence + 1;
  switch (scenario.outcome) {
    case "duplicate":
      return { resourceScope: scenario.scope, schemaVersion: "1.0.0", sequence: scenario.initialExpectedSequence, eventId: "duplicate", payload: { delta: scenario.incrementalDelta } };
    case "gap":
      return { resourceScope: scenario.scope, schemaVersion: "1.0.0", sequence: expectedAfterIncrementalEvent + 1, eventId: "gap", payload: { delta: scenario.incrementalDelta } };
    case "incompatible":
      return { resourceScope: scenario.scope, schemaVersion: "incompatible-schema", sequence: expectedAfterIncrementalEvent, eventId: "incompatible", payload: { delta: scenario.incrementalDelta } };
    case "expiry":
    case "denial":
    case "bounded":
      return null;
  }
}

// Feature: frontend-redesign, Property 7: Unsafe replay causes replacement resynchronization
// Validates: Requirements 4.6, 4.7, 4.8
test("Property 7: replaces incremental state after every unsafe replay outcome", async (): Promise<void> => {
  await fc.assert(fc.asyncProperty(replacementResynchronizationScenarioArbitrary, async (scenario: ReplacementResynchronizationScenario): Promise<void> => {
    const recovered = deferred<LiveProjectionSnapshot<CounterProjection>>();
    const subscriptionContexts: AuthorizedSubscriptionContext[] = [];
    const cursors = new Map<string, string>();
    let snapshotLoads = 0;
    let abortedSubscriptions = 0;
    let appliedEvents = 0;
    const initialSnapshot: LiveProjectionSnapshot<CounterProjection> = {
      projection: { value: scenario.initialValue },
      schemaVersion: "1.0.0",
      expectedSequence: scenario.initialExpectedSequence,
      subscription: {
        scope: scenario.scope,
        authorizedTopics: ["run.updated"],
        sequenceContext: { after_sequence: scenario.initialExpectedSequence - 1 },
      },
    };
    const replacementSnapshot = replacementSnapshotFor(scenario);
    const controller = new LiveProjectionController<CounterProjection, CounterEvent>({
      snapshotLoader: {
        loadSnapshot: (): Promise<LiveProjectionSnapshot<CounterProjection>> => {
          snapshotLoads += 1;
          return snapshotLoads === 1 ? Promise.resolve(initialSnapshot) : recovered.promise;
        },
      },
      subscriptionFactory: {
        subscribe: (context: AuthorizedSubscriptionContext): { abort(): void } => {
          subscriptionContexts.push(context);
          return { abort: (): void => { abortedSubscriptions += 1; } };
        },
      },
      eventDecoder: { decode: (value: unknown): LiveOperationalEvent<CounterEvent> | null => value as LiveOperationalEvent<CounterEvent> },
      applyEvent: (projection: CounterProjection, event: LiveOperationalEvent<CounterEvent>): CounterProjection => {
        appliedEvents += 1;
        return { value: projection.value + event.payload.delta };
      },
      cursorStore: {
        save: (scope: string, eventCursor: string): void => { cursors.set(scope, eventCursor); },
        clear: (scope: string): void => { cursors.delete(scope); },
      },
    });

    await controller.start(scenario.scope);
    const incrementalEvent: LiveOperationalEvent<CounterEvent> = {
      resourceScope: scenario.scope,
      schemaVersion: "1.0.0",
      sequence: scenario.initialExpectedSequence,
      eventId: "cursor-before-replay-anomaly",
      payload: { delta: scenario.incrementalDelta },
    };
    await controller.handleOperationalEvent(scenario.scope, incrementalEvent);
    assert.equal(cursors.get(scenario.scope), incrementalEvent.eventId);
    assert.equal(appliedEvents, 1);

    const unsafeEvent = unsafeEventFor(scenario);
    const firstRecovery = unsafeEvent === null
      ? controller.handleReplayAnomaly(scenario.scope)
      : controller.handleOperationalEvent(scenario.scope, unsafeEvent);
    const joinedRecovery = controller.handleReplayAnomaly(scenario.scope);

    assert.equal(snapshotLoads, 2, "each unsafe replay outcome must begin exactly one serialized resynchronization");
    assert.equal(abortedSubscriptions, 1, "resynchronization must abort the affected incremental subscription");
    assert.equal(appliedEvents, 1, "unsafe replay input must not mutate incremental projection state");
    assert.equal(cursors.get(scenario.scope), undefined, "resynchronization must discard the affected event cursor");
    assert.deepEqual(controller.getState(scenario.scope), {
      projection: null,
      subscriptionScope: scenario.scope,
      expectedSequence: null,
      schemaVersion: null,
      eventCursor: null,
      connection: "resynchronizing",
    });

    recovered.resolve(replacementSnapshot);
    await Promise.all([firstRecovery, joinedRecovery]);

    assert.equal(subscriptionContexts.length, 2, "the replacement snapshot must establish a replacement subscription");
    assert.strictEqual(subscriptionContexts[1], replacementSnapshot.subscription);
    assert.equal(appliedEvents, 1, "replacement occurs from the REST snapshot, not unsafe incremental input");
    assert.deepEqual(controller.getState(scenario.scope), {
      projection: replacementSnapshot.projection,
      subscriptionScope: scenario.scope,
      expectedSequence: replacementSnapshot.expectedSequence,
      schemaVersion: replacementSnapshot.schemaVersion,
      eventCursor: null,
      connection: "live",
    });
  }), { numRuns: 100 });
});


