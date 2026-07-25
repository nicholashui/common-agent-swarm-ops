import assert from "node:assert/strict";
import test from "node:test";

import fc from "fast-check";

import {
  LiveProjectionController,
  type LiveOperationalEvent,
  type LiveProjectionSnapshot,
  type LiveProjectionState,
} from "./LiveProjectionController";

interface CounterProjection {
  readonly value: number;
}

interface CounterEvent {
  readonly delta: number;
}

interface EventTraceStep {
  readonly scopeKind: "authorized" | "foreign";
  readonly schemaKind: "current" | "incompatible";
  readonly sequenceKind: "exact" | "duplicate" | "gap";
  readonly delta: number;
  readonly eventId: string;
}

interface ExactNextEventTrace {
  readonly scope: string;
  readonly schemaVersion: string;
  readonly initialValue: number;
  readonly expectedSequence: number;
  readonly steps: readonly EventTraceStep[];
}

const nonBlankStringArbitrary = fc
  .string({ minLength: 1, maxLength: 64 })
  .filter((value: string): boolean => value.trim().length > 0);

const eventTraceStepArbitrary: fc.Arbitrary<EventTraceStep> = fc.record({
  scopeKind: fc.constantFrom("authorized", "foreign"),
  schemaKind: fc.constantFrom("current", "incompatible"),
  sequenceKind: fc.constantFrom("exact", "duplicate", "gap"),
  delta: fc.integer({ min: -100, max: 100 }),
  eventId: nonBlankStringArbitrary,
});

const exactNextEventTraceArbitrary: fc.Arbitrary<ExactNextEventTrace> = fc.record({
  scope: nonBlankStringArbitrary,
  schemaVersion: nonBlankStringArbitrary,
  initialValue: fc.integer({ min: -10_000, max: 10_000 }),
  expectedSequence: fc.integer({ min: 0, max: 10_000 }),
  steps: fc.array(eventTraceStepArbitrary, { minLength: 1, maxLength: 50 }),
});

function snapshotFor(trace: ExactNextEventTrace): LiveProjectionSnapshot<CounterProjection> {
  return {
    projection: { value: trace.initialValue },
    schemaVersion: trace.schemaVersion,
    expectedSequence: trace.expectedSequence,
    subscription: {
      scope: trace.scope,
      authorizedTopics: ["run.updated"],
      sequenceContext: { after_sequence: trace.expectedSequence },
    },
  };
}

function sequenceFor(kind: EventTraceStep["sequenceKind"], expectedSequence: number): number {
  switch (kind) {
    case "exact":
      return expectedSequence;
    case "duplicate":
      return expectedSequence === 0 ? expectedSequence + 1 : expectedSequence - 1;
    case "gap":
      return expectedSequence + 1;
  }
}

interface GovernedProjectionFacts {
  readonly projection: CounterProjection | null;
  readonly expectedSequence: number | null;
  readonly schemaVersion: string | null;
  readonly eventCursor: string | null;
}

function governedFacts(state: LiveProjectionState<CounterProjection>): GovernedProjectionFacts {
  return {
    projection: state.projection,
    expectedSequence: state.expectedSequence,
    schemaVersion: state.schemaVersion,
    eventCursor: state.eventCursor,
  };
}

// Feature: frontend-redesign, Property 6: Only the exact next authorized event mutates a live projection
// Validates: Requirements 4.3, 4.4, 4.10, 4.11
test("Property 6: applies only exact authorized events across arbitrary noncontiguous traces", async (): Promise<void> => {
  await fc.assert(
    fc.asyncProperty(exactNextEventTraceArbitrary, async (trace: ExactNextEventTrace): Promise<void> => {
      const cursors = new Map<string, string>();
      const appliedEventIds: string[] = [];
      const controller = new LiveProjectionController<CounterProjection, CounterEvent>({
        snapshotLoader: {
          loadSnapshot: (): Promise<LiveProjectionSnapshot<CounterProjection>> => Promise.resolve(snapshotFor(trace)),
        },
        subscriptionFactory: {
          subscribe: (): { abort(): void } => ({ abort: (): void => undefined }),
        },
        eventDecoder: {
          decode: (value: unknown): LiveOperationalEvent<CounterEvent> | null => value as LiveOperationalEvent<CounterEvent>,
        },
        applyEvent: (projection: CounterProjection, event: LiveOperationalEvent<CounterEvent>): CounterProjection => {
          appliedEventIds.push(event.eventId);
          return { value: projection.value + event.payload.delta };
        },
        cursorStore: {
          save: (scope: string, eventCursor: string): void => { cursors.set(scope, eventCursor); },
          clear: (scope: string): void => { cursors.delete(scope); },
        },
      });
      await controller.start(trace.scope);

      let expectedValue = trace.initialValue;
      let expectedSequence = trace.expectedSequence;
      let expectedCursor: string | null = null;
      const expectedAcceptedEventIds: string[] = [];
      for (const [index, step] of trace.steps.entries()) {
        const eventId = `${step.eventId}-${index}`;
        const accepted = step.scopeKind === "authorized"
          && step.schemaKind === "current"
          && step.sequenceKind === "exact";
        const event: LiveOperationalEvent<CounterEvent> = {
          resourceScope: step.scopeKind === "authorized" ? trace.scope : `${trace.scope}:foreign`,
          schemaVersion: step.schemaKind === "current" ? trace.schemaVersion : `${trace.schemaVersion}:incompatible`,
          sequence: sequenceFor(step.sequenceKind, expectedSequence),
          eventId,
          payload: { delta: step.delta },
        };

        await controller.handleOperationalEvent(trace.scope, event);
        if (accepted) {
          expectedValue += step.delta;
          expectedSequence += 1;
          expectedCursor = eventId;
          expectedAcceptedEventIds.push(eventId);
        } else {
          expectedValue = trace.initialValue;
          expectedSequence = trace.expectedSequence;
          expectedCursor = null;
        }

        assert.deepEqual(controller.getState(trace.scope), {
          projection: { value: expectedValue },
          subscriptionScope: trace.scope,
          expectedSequence,
          schemaVersion: trace.schemaVersion,
          eventCursor: expectedCursor,
          connection: "live",
        });
        assert.equal(cursors.get(trace.scope) ?? null, expectedCursor);
      }

      assert.deepEqual(appliedEventIds, expectedAcceptedEventIds);
      const beforeConnectionChange = controller.getState(trace.scope);
      if (beforeConnectionChange === null) throw new Error("A started live projection must retain state.");
      controller.markReconnecting(trace.scope);
      const reconnectingState = controller.getState(trace.scope);
      if (reconnectingState === null) throw new Error("Reconnecting must retain the live projection state.");
      assert.deepEqual(governedFacts(reconnectingState), governedFacts(beforeConnectionChange));
      controller.markStale(trace.scope);
      const staleState = controller.getState(trace.scope);
      if (staleState === null) throw new Error("Stale must retain the live projection state.");
      assert.deepEqual(governedFacts(staleState), governedFacts(reconnectingState));
    }),
    { numRuns: 100 },
  );
});
