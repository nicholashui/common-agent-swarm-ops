import assert from "node:assert/strict";
import test from "node:test";

import fc from "fast-check";

import {
  LiveProjectionController,
  type AuthorizedSubscriptionContext,
  type LiveOperationalEvent,
  type LiveProjectionSnapshot,
} from "./LiveProjectionController";

interface CounterProjection {
  readonly value: number;
}

interface CounterEvent {
  readonly delta: number;
}

interface LiveObservationScenario {
  readonly scope: string;
  readonly authorizedTopics: readonly string[];
  readonly expectedSequence: number;
}

const nonBlankStringArbitrary = fc
  .string({ minLength: 1, maxLength: 64 })
  .filter((value: string): boolean => value.trim().length > 0);

const liveObservationScenarioArbitrary: fc.Arbitrary<LiveObservationScenario> = fc.record({
  scope: nonBlankStringArbitrary,
  authorizedTopics: fc.uniqueArray(nonBlankStringArbitrary, { maxLength: 8 }),
  expectedSequence: fc.integer({ min: 0, max: 10_000 }),
});

function snapshotFor(scenario: LiveObservationScenario): LiveProjectionSnapshot<CounterProjection> {
  return {
    projection: { value: 0 },
    schemaVersion: "1.0.0",
    expectedSequence: scenario.expectedSequence,
    subscription: {
      scope: scenario.scope,
      authorizedTopics: scenario.authorizedTopics,
      sequenceContext: { after_sequence: scenario.expectedSequence },
    },
  };
}

function deferred<T>(): { readonly promise: Promise<T>; readonly resolve: (value: T) => void } {
  let resolvePromise: ((value: T) => void) | undefined;
  const promise = new Promise<T>((resolve: (value: T) => void): void => {
    resolvePromise = resolve;
  });
  return {
    promise,
    resolve: (value: T): void => resolvePromise?.(value),
  };
}

// Feature: frontend-redesign, Property 5: Live observation begins from an authorized snapshot and scope
// Validates: Requirements 4.1, 4.2
test("Property 5: starts only after an authorized snapshot and subscribes only to its scope and topics", async (): Promise<void> => {
  await fc.assert(
    fc.asyncProperty(liveObservationScenarioArbitrary, async (scenario: LiveObservationScenario): Promise<void> => {
      const initialSnapshot = deferred<LiveProjectionSnapshot<CounterProjection>>();
      const subscriptionContexts: AuthorizedSubscriptionContext[] = [];
      let appliedEvents = 0;
      const controller = new LiveProjectionController<CounterProjection, CounterEvent>({
        snapshotLoader: {
          loadSnapshot: (): Promise<LiveProjectionSnapshot<CounterProjection>> => initialSnapshot.promise,
        },
        subscriptionFactory: {
          subscribe: (context: AuthorizedSubscriptionContext): { abort(): void } => {
            subscriptionContexts.push(context);
            return { abort: (): void => undefined };
          },
        },
        eventDecoder: {
          decode: (value: unknown): LiveOperationalEvent<CounterEvent> | null => value as LiveOperationalEvent<CounterEvent>,
        },
        applyEvent: (projection: CounterProjection, event: LiveOperationalEvent<CounterEvent>): CounterProjection => {
          appliedEvents += 1;
          return { value: projection.value + event.payload.delta };
        },
      });
      const pendingStart = controller.start(scenario.scope);
      const nextAuthorizedEvent: LiveOperationalEvent<CounterEvent> = {
        resourceScope: scenario.scope,
        schemaVersion: "1.0.0",
        sequence: scenario.expectedSequence,
        eventId: "event-1",
        payload: { delta: 1 },
      };

      await controller.handleOperationalEvent(scenario.scope, nextAuthorizedEvent);
      assert.equal(appliedEvents, 0, "events must not apply before the REST snapshot resolves");
      assert.equal(controller.getState(scenario.scope)?.projection, null);
      assert.deepEqual(subscriptionContexts, [], "no subscription may open before the REST snapshot resolves");

      const authorizedSnapshot = snapshotFor(scenario);
      initialSnapshot.resolve(authorizedSnapshot);
      await pendingStart;

      assert.deepEqual(subscriptionContexts, [authorizedSnapshot.subscription]);
      await controller.handleOperationalEvent(scenario.scope, nextAuthorizedEvent);
      assert.equal(appliedEvents, 1);
      assert.equal(controller.getState(scenario.scope)?.projection?.value, 1);
    }),
    { numRuns: 100 },
  );
});
