import assert from "node:assert/strict";
import test from "node:test";

import fc from "fast-check";
import React from "react";
import { renderToStaticMarkup } from "react-dom/server";

import { ExternalNavigationControl, mapAllowedActionContract } from "../../components/projection/SafeContent";
import type { GeneratedActionReference, GeneratedJsonValue } from "../api/client";
import { BrowserSessionSafeCache, SessionTransitionCoordinator, type SessionStorageLike } from "./session-runtime";

const SAFE_FIELDS = ["name", "status", "summary"] as const;
type SafeField = (typeof SAFE_FIELDS)[number];

interface CacheCandidate {
  readonly allowlistedFields: readonly SafeField[];
  readonly projection: Readonly<Record<string, GeneratedJsonValue>>;
  readonly eventCursor: string | null;
  readonly prohibitedValues: readonly string[];
  readonly transitionCount: number;
}

interface DestinationCandidate {
  readonly reference: GeneratedActionReference;
  readonly authorizesNavigation: boolean;
}

class MemoryStorage implements SessionStorageLike {
  private readonly values = new Map<string, string>();

  public getItem(key: string): string | null {
    return this.values.get(key) ?? null;
  }

  public setItem(key: string, value: string): void {
    this.values.set(key, value);
  }

  public removeItem(key: string): void {
    this.values.delete(key);
  }

  public serializedValues(): readonly string[] {
    return [...this.values.values()];
  }
}

const identifierArbitrary = fc.uuid().map((value: string): string => value.replaceAll("-", ""));
const cacheCandidateArbitrary: fc.Arbitrary<CacheCandidate> = fc.tuple(
  fc.subarray([...SAFE_FIELDS]),
  fc.array(identifierArbitrary, { minLength: SAFE_FIELDS.length, maxLength: SAFE_FIELDS.length }),
  fc.array(identifierArbitrary, { minLength: 5, maxLength: 5 }),
  fc.option(identifierArbitrary, { nil: null }),
  fc.integer({ min: 1, max: 3 }),
).map(([allowlistedFields, safeValues, sensitiveValues, eventCursor, transitionCount]): CacheCandidate => {
  const prohibitedValues = [
    `TOKEN_${sensitiveValues[0]!}`,
    `CREDENTIAL_${sensitiveValues[1]!}`,
    `PROTECTED_${sensitiveValues[2]!}`,
    `RAW_${sensitiveValues[3]!}`,
    `PRIVILEGED_${sensitiveValues[4]!}`,
  ];
  return {
    allowlistedFields,
    projection: {
      name: `Name ${safeValues[0]!}`,
      status: `Status ${safeValues[1]!}`,
      summary: `Summary ${safeValues[2]!}`,
      access_token: prohibitedValues[0]!,
      tool_credential: prohibitedValues[1]!,
      protected_field: prohibitedValues[2]!,
      raw_protected_data: prohibitedValues[3]!,
      privileged_artifact_content: prohibitedValues[4]!,
    },
    eventCursor: eventCursor === null ? null : `cursor-${eventCursor}`,
    prohibitedValues,
    transitionCount,
  };
});

interface DestinationValue {
  readonly value: string;
  readonly isSafeHttps: boolean;
}

const destinationArbitrary: fc.Arbitrary<DestinationValue> = fc.oneof(
  identifierArbitrary.map((id: string): DestinationValue => ({ value: `https://approved.example/${id}`, isSafeHttps: true })),
  fc.constant({ value: "http://unapproved.example/resource", isSafeHttps: false }),
  fc.constant({ value: "javascript:alert(1)", isSafeHttps: false }),
  fc.constant({ value: "not a URL", isSafeHttps: false }),
);
const openContextArbitrary: fc.Arbitrary<GeneratedJsonValue> = fc.oneof(fc.boolean(), fc.constant("new-context"));
const destinationCandidateArbitrary: fc.Arbitrary<DestinationCandidate> = fc.tuple(
  identifierArbitrary,
  destinationArbitrary,
  fc.boolean(),
  fc.boolean(),
  fc.boolean(),
  fc.boolean(),
  openContextArbitrary,
).map(([id, destination, isExternalNavigation, allowed, hasId, hasLabel, openInNewContext]): DestinationCandidate => {
  const reference: GeneratedActionReference = {
    kind: isExternalNavigation ? "external_navigation" : "command",
    allowed,
    destination: destination.value,
    open_in_new_context: openInNewContext,
    ...(hasId ? { id: `external-${id}` } : {}),
    ...(hasLabel ? { label: `Open ${id}` } : {}),
  };
  return {
    reference,
    authorizesNavigation: isExternalNavigation
      && allowed
      && destination.isSafeHttps
      && hasId
      && hasLabel
      && typeof openInNewContext === "boolean",
  };
});

function expectedProjection(candidate: CacheCandidate): Record<string, GeneratedJsonValue> {
  const projection: Record<string, GeneratedJsonValue> = {};
  for (const field of candidate.allowlistedFields) projection[field] = candidate.projection[field]!;
  return projection;
}

function assertPersistenceRemainsSessionSafe(candidate: CacheCandidate): void {
  const persistence = new MemoryStorage();
  const cache = new BrowserSessionSafeCache({
    sessionVersion: "property-15",
    allowlist: [{ key: "resume", projectionFields: candidate.allowlistedFields }],
    persistence,
  });
  const coordinator = new SessionTransitionCoordinator();
  const steps: string[] = [];
  coordinator.registerProjectionState({
    clearRestSnapshot: (): void => { steps.push("rest"); },
    clearIncrementalState: (): void => { steps.push("incremental"); },
  });
  coordinator.registerCache({
    clearForSessionTransition: (): void => {
      steps.push("cache");
      cache.clearForSessionTransition();
    },
  });
  coordinator.registerCommandIntentPresentation({ clearCommandIntentPresentation: (): void => { steps.push("commands"); } });

  for (let transition = 0; transition < candidate.transitionCount; transition += 1) {
    cache.write("resume", { projection: candidate.projection, eventCursor: candidate.eventCursor });
    const expected = expectedProjection(candidate);
    assert.deepEqual(cache.read("resume")?.projection, expected);
    assert.equal(cache.read("resume")?.eventCursor, candidate.eventCursor);

    const serializedValues = persistence.serializedValues();
    assert.equal(serializedValues.length, 1);
    assert.deepEqual(JSON.parse(serializedValues[0]!).projection, expected);
    assert.equal(JSON.parse(serializedValues[0]!).eventCursor, candidate.eventCursor);
    for (const prohibitedValue of candidate.prohibitedValues) assert.equal(serializedValues[0]!.includes(prohibitedValue), false);

    const registration = coordinator.registerSseSubscription({ abort: (): void => { steps.push("abort"); } });
    assert.equal(registration.canApplyOperationalEvent(), true);
    coordinator.beginSessionTransition();

    assert.deepEqual(steps, ["abort", "rest", "incremental", "cache", "commands"]);
    assert.equal(registration.canApplyOperationalEvent(), false);
    assert.equal(cache.read("resume"), null);
    assert.deepEqual(persistence.serializedValues(), []);
    assert.equal(coordinator.canRenderAuthorizedProjection(), false);
    coordinator.authorizeNextProjection();
    assert.equal(coordinator.canRenderAuthorizedProjection(), true);
    steps.length = 0;
  }
}

function assertNavigationIsCapabilitySafe(candidate: DestinationCandidate): void {
  const action = mapAllowedActionContract(candidate.reference);
  assert.equal(action !== null, candidate.authorizesNavigation);

  const markup = renderToStaticMarkup(<ExternalNavigationControl action={action} />);
  const hasNavigableLink = /<a\b[^>]*\bhref="/.test(markup);
  assert.equal(hasNavigableLink, candidate.authorizesNavigation);
  if (action === null) {
    assert.match(markup, /disabled/);
    assert.doesNotMatch(markup, /<a\b/);
    return;
  }

  assert.ok(markup.includes(`href="${action.destination}"`));
  assert.ok(markup.includes(`>${action.label}</a>`));
  if (action.openInNewContext) assert.match(markup, /target="_blank" rel="noopener noreferrer"/);
  else assert.doesNotMatch(markup, /target="_blank"|rel="noopener noreferrer"/);
}

// Feature: frontend-redesign, Property 15: Browser persistence and external navigation are capability-safe
// Validates: Requirements 10.10, 10.12, 10.13
test("Property 15: browser persistence and external navigation are capability-safe", (): void => {
  fc.assert(fc.property(
    cacheCandidateArbitrary,
    destinationCandidateArbitrary,
    (cacheCandidate: CacheCandidate, destinationCandidate: DestinationCandidate): void => {
      assertPersistenceRemainsSessionSafe(cacheCandidate);
      assertNavigationIsCapabilitySafe(destinationCandidate);
    },
  ), { numRuns: 100 });
});
