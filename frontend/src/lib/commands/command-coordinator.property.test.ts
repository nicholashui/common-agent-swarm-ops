import assert from "node:assert/strict";
import test from "node:test";

import fc from "fast-check";

import type { GeneratedActionReference } from "../api/client";
import {
  CommandCoordinator,
  type CommandAmbiguousOutcome,
  type CommandDeniedOutcome,
  type CommandInvocationResult,
  type CommandManualRecoveryOutcome,
  type CommandQueuedOutcome,
  type CommandRateLimitedOutcome,
  type CommandReconciliationOutcome,
  type CommandSubmissionOutcome,
  type CommandTransport,
  type CommandTransportRequest,
  type CommandUuidSource,
} from "./CommandCoordinator";
import type { CommandIntent } from "./CommandCoordinator";

interface Payload { readonly operation: string; }
interface Projection { readonly projection: string; }
interface Terminal { readonly terminal: string; }
type TraceOperation = "retry" | "reconcile";
type TraceOutcome = CommandAmbiguousOutcome | CommandDeniedOutcome | CommandManualRecoveryOutcome | CommandQueuedOutcome | CommandRateLimitedOutcome;

interface ObservedRequest { readonly request: CommandTransportRequest<Payload>; readonly uuidCallsAtDispatch: number; }

class FixedUuidSource implements CommandUuidSource {
  public calls = 0;
  public constructor(private readonly identity: string) {}
  public randomUUID(): string { this.calls += 1; return this.identity; }
}

class ProbeTransport implements CommandTransport<Payload, Projection, Terminal> {
  public readonly requests: ObservedRequest[] = [];
  private readonly pendingResolvers: Array<(outcome: TraceOutcome) => void> = [];
  public constructor(private readonly getUuidCallCount: () => number) {}
  public submit(request: CommandTransportRequest<Payload>): Promise<CommandSubmissionOutcome<Terminal>> { return this.capture(request); }
  public reconcile(request: CommandTransportRequest<Payload>): Promise<CommandReconciliationOutcome<Projection, Terminal>> { return this.capture(request); }
  public resolveNext(outcome: TraceOutcome): void {
    const resolve = this.pendingResolvers.shift();
    if (resolve === undefined) assert.fail("a pending transport request must exist before it is resolved");
    resolve(outcome);
  }
  private capture(request: CommandTransportRequest<Payload>): Promise<TraceOutcome> {
    this.requests.push({ request, uuidCallsAtDispatch: this.getUuidCallCount() });
    return new Promise<TraceOutcome>((resolve: (outcome: TraceOutcome) => void): void => { this.pendingResolvers.push(resolve); });
  }
}

interface ContinuationStep { readonly operation: TraceOperation; readonly outcome: Exclude<TraceOutcome, CommandQueuedOutcome>; }
interface CommandTrace {
  readonly intent: CommandIntent<Payload>;
  readonly queuedIntent: CommandIntent<Payload>;
  readonly denial: CommandDeniedOutcome;
  readonly retryOutcome: Exclude<TraceOutcome, CommandQueuedOutcome>;
  readonly continuation: readonly ContinuationStep[];
}

interface Harness {
  readonly coordinator: CommandCoordinator<Payload, Projection, Terminal>;
  readonly transport: ProbeTransport;
  readonly uuid: FixedUuidSource;
}

const identifierArbitrary = fc.uuid();
const textArbitrary = fc.string({ minLength: 1, maxLength: 48 });
const actionReferenceFor = (id: string, label: string): GeneratedActionReference => ({ id: `returned-${id}`, label, eligible: true });
const ambiguousOutcomeArbitrary: fc.Arbitrary<CommandAmbiguousOutcome> = textArbitrary.map((correlationIdentifier: string): CommandAmbiguousOutcome => ({ kind: "ambiguous", correlationIdentifier }));
const deniedOutcomeArbitrary: fc.Arbitrary<CommandDeniedOutcome> = fc.tuple(fc.constantFrom("authorization", "policy", "approval"), textArbitrary, textArbitrary)
  .map(([denialKind, message, correlationIdentifier]): CommandDeniedOutcome => ({ kind: "denied", denialKind, message, correlationIdentifier }));
const manualRecoveryOutcomeArbitrary: fc.Arbitrary<CommandManualRecoveryOutcome> = fc.tuple(textArbitrary, textArbitrary, textArbitrary)
  .map(([recoveryStatus, failureSummary, correlationIdentifier]): CommandManualRecoveryOutcome => ({ kind: "manual_recovery", recoveryStatus, failureSummary, correlationIdentifier }));
const rateLimitedOutcomeArbitrary: fc.Arbitrary<CommandRateLimitedOutcome> = fc.tuple(textArbitrary, fc.integer({ min: 0, max: 3_600 }), textArbitrary)
  .map(([message, retryAfterSeconds, correlationIdentifier]): CommandRateLimitedOutcome => ({ kind: "rate_limited", message, retryAfterSeconds, correlationIdentifier }));
const unresolvedOutcomeArbitrary: fc.Arbitrary<Exclude<TraceOutcome, CommandQueuedOutcome>> = fc.oneof(ambiguousOutcomeArbitrary, deniedOutcomeArbitrary, manualRecoveryOutcomeArbitrary, rateLimitedOutcomeArbitrary);
const continuationArbitrary: fc.Arbitrary<ContinuationStep> = fc.tuple(fc.constantFrom<TraceOperation>("retry", "reconcile"), unresolvedOutcomeArbitrary)
  .map(([operation, outcome]): ContinuationStep => ({ operation, outcome }));
const commandTraceArbitrary: fc.Arbitrary<CommandTrace> = fc.tuple(identifierArbitrary, identifierArbitrary, textArbitrary, textArbitrary, textArbitrary, deniedOutcomeArbitrary, unresolvedOutcomeArbitrary, fc.array(continuationArbitrary, { maxLength: 8 }))
  .map(([id, queuedId, label, queuedLabel, operation, denial, retryOutcome, continuation]): CommandTrace => ({
    intent: { actionReferenceId: `action-${id}`, actionReference: actionReferenceFor(id, label), payload: { operation } },
    queuedIntent: { actionReferenceId: `action-${queuedId}`, actionReference: actionReferenceFor(queuedId, queuedLabel), payload: { operation } },
    denial,
    retryOutcome,
    continuation,
  }));

function createHarness(identity: string): Harness {
  const uuid = new FixedUuidSource(identity);
  const transport = new ProbeTransport((): number => uuid.calls);
  return { coordinator: new CommandCoordinator<Payload, Projection, Terminal>({ uuid, clock: { now: (): number => 1_700_000_000_000 }, transport }), transport, uuid };
}

function requireRecord(harness: Harness, intent: CommandIntent<Payload>): string {
  const record = harness.coordinator.getRecord(intent.actionReferenceId);
  if (record === undefined) assert.fail("the submitted command intent must retain a record");
  return record.idempotencyIdentity;
}

function assertDurableIdentity(harness: Harness, intent: CommandIntent<Payload>, identity: string): void {
  assert.equal(requireRecord(harness, intent), identity);
  assert.equal(harness.uuid.calls, 1, "one command intent must allocate exactly one idempotency identity");
  assert.ok(harness.transport.requests.length > 0);
  for (const observed of harness.transport.requests) {
    assert.equal(observed.request.actionReferenceId, intent.actionReferenceId);
    assert.equal(observed.uuidCallsAtDispatch, 1, "the identity must exist before dispatch");
    assert.equal(observed.request.idempotencyIdentity, identity);
    assert.equal(observed.request.headers["Idempotency-Key"], identity);
  }
}

async function assertDuplicateIsBlocked(harness: Harness, intent: CommandIntent<Payload>): Promise<void> {
  const requestCount = harness.transport.requests.length;
  const duplicate = await harness.coordinator.submit(intent, "user");
  if (duplicate.accepted) assert.fail("the pending initiating control must reject duplicate invocation");
  assert.equal(duplicate.reason, "control_disabled");
  assert.equal(harness.transport.requests.length, requestCount, "a blocked duplicate must not dispatch another command");
}

async function runPendingOperation(harness: Harness, intent: CommandIntent<Payload>, operation: TraceOperation, outcome: TraceOutcome, identity: string): Promise<void> {
  const pending: Promise<CommandInvocationResult<Payload, Projection, Terminal>> = operation === "retry"
    ? harness.coordinator.submit(intent, "user")
    : harness.coordinator.reconcile(intent.actionReferenceId, "user");
  const expectedStatus = operation === "retry" ? "submitting" : "reconciling";
  assert.equal(harness.coordinator.getRecord(intent.actionReferenceId)?.status, expectedStatus);
  assert.equal(harness.coordinator.isActionDisabled(intent.actionReferenceId), true);
  assertDurableIdentity(harness, intent, identity);
  await assertDuplicateIsBlocked(harness, intent);
  harness.transport.resolveNext(outcome);
  const result = await pending;
  if (!result.accepted) assert.fail("a user retry or reconciliation of an unresolved intent must be accepted");
  assert.equal(result.record.idempotencyIdentity, identity);
  assertDurableIdentity(harness, intent, identity);
}

async function runReconciliationTrace(trace: CommandTrace): Promise<void> {
  const identity = `identity-${trace.intent.actionReferenceId}`;
  const harness = createHarness(identity);
  await runPendingOperation(harness, trace.intent, "retry", { kind: "ambiguous" }, identity);
  assert.equal(harness.coordinator.getRecord(trace.intent.actionReferenceId)?.status, "reconciling");
  assert.equal(harness.coordinator.isActionDisabled(trace.intent.actionReferenceId), true);
  await assertDuplicateIsBlocked(harness, trace.intent);
  await runPendingOperation(harness, trace.intent, "reconcile", trace.denial, identity);
  assert.equal(harness.coordinator.getRecord(trace.intent.actionReferenceId)?.status, "denied");
  await runPendingOperation(harness, trace.intent, "retry", trace.retryOutcome, identity);
  for (const step of trace.continuation) {
    const status = harness.coordinator.getRecord(trace.intent.actionReferenceId)?.status;
    assert.ok(status === "reconciling" || status === "denied" || status === "rate_limited" || status === "manual_recovery");
    await runPendingOperation(harness, trace.intent, status === "reconciling" ? "reconcile" : step.operation, step.outcome, identity);
  }
}

async function runQueuedTrace(intent: CommandIntent<Payload>): Promise<void> {
  const identity = `identity-${intent.actionReferenceId}`;
  const harness = createHarness(identity);
  await runPendingOperation(harness, intent, "retry", { kind: "queued", pendingReference: `pending-${intent.actionReferenceId}` }, identity);
  assert.equal(harness.coordinator.getRecord(intent.actionReferenceId)?.status, "queued");
  assert.equal(harness.coordinator.isActionDisabled(intent.actionReferenceId), true);
  await assertDuplicateIsBlocked(harness, intent);
  assertDurableIdentity(harness, intent, identity);
}

// Feature: frontend-redesign, Property 3: A command intent has one durable idempotency identity and one pending-control owner
// Validates: Requirements 3.1, 3.2, 3.3, 3.5, 3.6, 3.11
test("Property 3: preserves one identity and blocks the pending action across generated command traces", async (): Promise<void> => {
  await fc.assert(fc.asyncProperty(commandTraceArbitrary, async (trace: CommandTrace): Promise<void> => {
    await runReconciliationTrace(trace);
    await runQueuedTrace(trace.queuedIntent);
  }), { numRuns: 100 });
});

interface PropertyFourTerminalOutcome {
  readonly kind: "terminal";
  readonly outcome: Terminal;
  readonly correlationIdentifier: string;
}

interface PropertyFourReconciledOutcome {
  readonly kind: "reconciled";
  readonly projection: Projection;
  readonly correlationIdentifier: string;
}

type PropertyFourSubmissionOutcome = CommandQueuedOutcome | CommandRateLimitedOutcome | CommandDeniedOutcome | PropertyFourTerminalOutcome;

interface PropertyFourTrace {
  readonly intent: CommandIntent<Payload>;
  readonly terminal: PropertyFourTerminalOutcome;
  readonly queued: CommandQueuedOutcome;
  readonly rateLimited: CommandRateLimitedOutcome;
  readonly denied: CommandDeniedOutcome;
  readonly reconciled: PropertyFourReconciledOutcome;
  readonly reconciliationTerminal: PropertyFourTerminalOutcome;
}

type PropertyFourReconciliationOutcome = PropertyFourReconciledOutcome | PropertyFourTerminalOutcome;

class OutcomeTransport implements CommandTransport<Payload, Projection, Terminal> {
  public readonly submitRequests: CommandTransportRequest<Payload>[] = [];
  public readonly reconcileRequests: CommandTransportRequest<Payload>[] = [];

  public constructor(
    private readonly submissionOutcome: PropertyFourSubmissionOutcome | CommandAmbiguousOutcome,
    private readonly reconciliationOutcome?: PropertyFourReconciliationOutcome,
  ) {}

  public async submit(request: CommandTransportRequest<Payload>): Promise<CommandSubmissionOutcome<Terminal>> {
    this.submitRequests.push(request);
    return this.submissionOutcome;
  }

  public async reconcile(request: CommandTransportRequest<Payload>): Promise<CommandReconciliationOutcome<Projection, Terminal>> {
    this.reconcileRequests.push(request);
    if (this.reconciliationOutcome === undefined) throw new TypeError("A reconciliation outcome is required.");
    return this.reconciliationOutcome;
  }
}

const returnedActionReferenceArbitrary: fc.Arbitrary<GeneratedActionReference> = fc.tuple(identifierArbitrary, textArbitrary)
  .map(([id, label]: [string, string]): GeneratedActionReference => actionReferenceFor(id, label));
const optionalReturnedActionReferenceArbitrary: fc.Arbitrary<GeneratedActionReference | undefined> = fc.option(returnedActionReferenceArbitrary, { nil: undefined });
const propertyFourIntentArbitrary: fc.Arbitrary<CommandIntent<Payload>> = fc.tuple(identifierArbitrary, textArbitrary, textArbitrary)
  .map(([id, label, operation]: [string, string, string]): CommandIntent<Payload> => ({
    actionReferenceId: `outcome-${id}`,
    actionReference: actionReferenceFor(id, label),
    payload: { operation },
  }));
const propertyFourTerminalOutcomeArbitrary: fc.Arbitrary<PropertyFourTerminalOutcome> = fc.tuple(textArbitrary, textArbitrary)
  .map(([terminal, correlationIdentifier]: [string, string]): PropertyFourTerminalOutcome => ({ kind: "terminal", outcome: { terminal }, correlationIdentifier }));
const propertyFourQueuedOutcomeArbitrary: fc.Arbitrary<CommandQueuedOutcome> = fc.tuple(textArbitrary, textArbitrary)
  .map(([pendingReference, correlationIdentifier]: [string, string]): CommandQueuedOutcome => ({ kind: "queued", pendingReference, correlationIdentifier }));
const propertyFourRateLimitedOutcomeArbitrary: fc.Arbitrary<CommandRateLimitedOutcome> = fc.tuple(textArbitrary, fc.integer({ min: 0, max: 3_600 }), textArbitrary, optionalReturnedActionReferenceArbitrary)
  .map(([message, retryAfterSeconds, correlationIdentifier, actionReference]: [string, number, string, GeneratedActionReference | undefined]): CommandRateLimitedOutcome => ({
    kind: "rate_limited",
    message,
    retryAfterSeconds,
    correlationIdentifier,
    ...(actionReference === undefined ? {} : { actionReference }),
  }));
const propertyFourDeniedOutcomeArbitrary: fc.Arbitrary<CommandDeniedOutcome> = fc.tuple(fc.constantFrom("authorization", "policy", "approval"), textArbitrary, textArbitrary, optionalReturnedActionReferenceArbitrary)
  .map(([denialKind, message, correlationIdentifier, actionReference]: ["authorization" | "policy" | "approval", string, string, GeneratedActionReference | undefined]): CommandDeniedOutcome => ({
    kind: "denied",
    denialKind,
    message,
    correlationIdentifier,
    ...(actionReference === undefined ? {} : { actionReference }),
  }));
const propertyFourReconciledOutcomeArbitrary: fc.Arbitrary<PropertyFourReconciledOutcome> = fc.tuple(textArbitrary, textArbitrary)
  .map(([projection, correlationIdentifier]: [string, string]): PropertyFourReconciledOutcome => ({ kind: "reconciled", projection: { projection }, correlationIdentifier }));
const propertyFourTraceArbitrary: fc.Arbitrary<PropertyFourTrace> = fc.tuple(
  propertyFourIntentArbitrary,
  propertyFourTerminalOutcomeArbitrary,
  propertyFourQueuedOutcomeArbitrary,
  propertyFourRateLimitedOutcomeArbitrary,
  propertyFourDeniedOutcomeArbitrary,
  propertyFourReconciledOutcomeArbitrary,
  propertyFourTerminalOutcomeArbitrary,
).map(([intent, terminal, queued, rateLimited, denied, reconciled, reconciliationTerminal]): PropertyFourTrace => ({
  intent,
  terminal,
  queued,
  rateLimited,
  denied,
  reconciled,
  reconciliationTerminal,
}));

function createOutcomeCoordinator(
  submissionOutcome: PropertyFourSubmissionOutcome | CommandAmbiguousOutcome,
  reconciliationOutcome?: PropertyFourReconciliationOutcome,
): { readonly coordinator: CommandCoordinator<Payload, Projection, Terminal>; readonly transport: OutcomeTransport } {
  const transport = new OutcomeTransport(submissionOutcome, reconciliationOutcome);
  return {
    coordinator: new CommandCoordinator<Payload, Projection, Terminal>({
      uuid: new FixedUuidSource("property-four-identity"),
      clock: { now: (): number => 1_700_000_000_000 },
      transport,
    }),
    transport,
  };
}

function assertCompletionMatches(record: ReturnType<CommandCoordinator<Payload, Projection, Terminal>["getRecord"]>, receivedTerminalOutcome: boolean): void {
  if (record === undefined) assert.fail("the command outcome must retain a command record");
  assert.equal(record.status === "terminal", receivedTerminalOutcome);
  assert.equal(record.terminalOutcome !== undefined, receivedTerminalOutcome);
}

async function assertSubmissionOutcome(intent: CommandIntent<Payload>, outcome: PropertyFourSubmissionOutcome): Promise<void> {
  const harness = createOutcomeCoordinator(outcome);
  const result = await harness.coordinator.submit(intent, "user");
  if (!result.accepted) assert.fail("a user command submission must be accepted");
  const record = harness.coordinator.getRecord(intent.actionReferenceId);
  if (record === undefined) assert.fail("a submitted command must retain its outcome record");

  assertCompletionMatches(record, outcome.kind === "terminal");
  assert.equal(harness.transport.submitRequests.length, 1, "outcome handling must not automatically resubmit a command");
  assert.equal(harness.transport.reconcileRequests.length, 0);

  switch (outcome.kind) {
    case "terminal":
      assert.equal(record.status, "terminal");
      assert.deepEqual(record.terminalOutcome, outcome.outcome);
      assert.equal(record.correlationIdentifier, outcome.correlationIdentifier);
      return;
    case "queued":
      assert.equal(record.status, "queued");
      assert.deepEqual(record.pendingReference, outcome.pendingReference);
      assert.equal(record.correlationIdentifier, outcome.correlationIdentifier);
      assert.equal(record.terminalOutcome, undefined);
      return;
    case "rate_limited":
      assert.equal(record.status, "rate_limited");
      assert.equal(record.message, outcome.message);
      assert.equal(record.retryAfterSeconds, outcome.retryAfterSeconds);
      assert.equal(record.correlationIdentifier, outcome.correlationIdentifier);
      assert.equal(record.returnedActionReference, outcome.actionReference);
      assert.equal(harness.coordinator.getRateLimitRemainingSeconds(intent.actionReferenceId), outcome.retryAfterSeconds);
      assert.equal(record.terminalOutcome, undefined);
      return;
    case "denied":
      assert.equal(record.status, "denied");
      assert.equal(record.denialKind, outcome.denialKind);
      assert.equal(record.message, outcome.message);
      assert.equal(record.correlationIdentifier, outcome.correlationIdentifier);
      assert.equal(record.returnedActionReference, outcome.actionReference);
      assert.equal(record.pendingReference, undefined);
      assert.equal(record.reconciledProjection, undefined);
      assert.equal(record.terminalOutcome, undefined);
  }
}

async function assertReconciliationOutcome(intent: CommandIntent<Payload>, outcome: PropertyFourReconciliationOutcome): Promise<void> {
  const harness = createOutcomeCoordinator({ kind: "ambiguous" }, outcome);
  const submitted = await harness.coordinator.submit(intent, "user");
  if (!submitted.accepted) assert.fail("an ambiguous command submission must be accepted before reconciliation");
  assert.equal(harness.coordinator.getRecord(intent.actionReferenceId)?.status, "reconciling");

  const reconciled = await harness.coordinator.reconcile(intent.actionReferenceId, "user");
  if (!reconciled.accepted) assert.fail("an unresolved command must permit user-initiated reconciliation");
  const record = harness.coordinator.getRecord(intent.actionReferenceId);
  if (record === undefined) assert.fail("a reconciled command must retain its returned outcome");

  assertCompletionMatches(record, outcome.kind === "terminal");
  assert.equal(record.pendingReference, undefined);
  assert.equal(harness.transport.submitRequests.length, 1);
  assert.equal(harness.transport.reconcileRequests.length, 1);

  if (outcome.kind === "terminal") {
    assert.equal(record.status, "terminal");
    assert.deepEqual(record.terminalOutcome, outcome.outcome);
    assert.equal(record.correlationIdentifier, outcome.correlationIdentifier);
    return;
  }

  assert.equal(record.status, "reconciled");
  assert.deepEqual(record.reconciledProjection, outcome.projection);
  assert.equal(record.correlationIdentifier, outcome.correlationIdentifier);
  assert.equal(record.terminalOutcome, undefined);
}

// Feature: frontend-redesign, Property 4: Command outcomes are truthfully classified
// Validates: Requirements 3.7, 3.8, 3.9, 3.12
test("Property 4: classifies generated command outcomes without premature completion", async (): Promise<void> => {
  await fc.assert(fc.asyncProperty(propertyFourTraceArbitrary, async (trace: PropertyFourTrace): Promise<void> => {
    await assertSubmissionOutcome(trace.intent, trace.terminal);
    await assertSubmissionOutcome(trace.intent, trace.queued);
    await assertSubmissionOutcome(trace.intent, trace.rateLimited);
    await assertSubmissionOutcome(trace.intent, trace.denied);
    await assertReconciliationOutcome(trace.intent, trace.reconciled);
    await assertReconciliationOutcome(trace.intent, trace.reconciliationTerminal);
  }), { numRuns: 100 });
});