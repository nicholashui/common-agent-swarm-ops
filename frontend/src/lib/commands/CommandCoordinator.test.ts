import assert from "node:assert/strict";
import test from "node:test";

import type { GeneratedActionReference } from "../api/client";
import {
  CommandCoordinator,
  type CommandClock,
  type CommandIntent,
  type CommandReconciliationOutcome,
  type CommandSubmissionOutcome,
  type CommandTransport,
  type CommandTransportRequest,
  type CommandUuidSource,
} from "./CommandCoordinator";

interface CommandPayload { readonly reason: string; }
interface ReconciledProjection { readonly runId: string; readonly status: string; }
interface TerminalOutcome { readonly runId: string; readonly status: "cancelled" | "complete"; }

type SubmissionOutcome = CommandSubmissionOutcome<TerminalOutcome>;
type ReconciliationOutcome = CommandReconciliationOutcome<ReconciledProjection, TerminalOutcome>;

const ACTION_REFERENCE: GeneratedActionReference = { id: "cancel-run", label: "Cancel run" };
const COMMAND_INTENT: CommandIntent<CommandPayload> = {
  actionReferenceId: "cancel-run",
  actionReference: ACTION_REFERENCE,
  payload: { reason: "Operator requested cancellation." },
};

class FixedUuidSource implements CommandUuidSource {
  public calls = 0;
  public randomUUID(): string { this.calls += 1; return "idempotency-command-1"; }
}

class FixedClock implements CommandClock {
  public constructor(public value = Date.UTC(2025, 0, 1, 0, 0, 0)) {}
  public now(): number { return this.value; }
}

class ScriptedTransport implements CommandTransport<CommandPayload, ReconciledProjection, TerminalOutcome> {
  public readonly submitRequests: CommandTransportRequest<CommandPayload>[] = [];
  public readonly reconcileRequests: CommandTransportRequest<CommandPayload>[] = [];

  public constructor(
    private readonly submitHandler: (request: CommandTransportRequest<CommandPayload>) => Promise<SubmissionOutcome>,
    private readonly reconcileHandler: (request: CommandTransportRequest<CommandPayload>) => Promise<ReconciliationOutcome>,
  ) {}

  public submit(request: CommandTransportRequest<CommandPayload>): Promise<SubmissionOutcome> {
    this.submitRequests.push(request);
    return this.submitHandler(request);
  }

  public reconcile(request: CommandTransportRequest<CommandPayload>): Promise<ReconciliationOutcome> {
    this.reconcileRequests.push(request);
    return this.reconcileHandler(request);
  }
}

function coordinator(
  transport: CommandTransport<CommandPayload, ReconciledProjection, TerminalOutcome>,
  uuid = new FixedUuidSource(),
  clock = new FixedClock(),
): { readonly coordinator: CommandCoordinator<CommandPayload, ReconciledProjection, TerminalOutcome>; readonly uuid: FixedUuidSource; readonly clock: FixedClock } {
  return { coordinator: new CommandCoordinator({ transport, uuid, clock }), uuid, clock };
}

function deferred<T>(): { readonly promise: Promise<T>; readonly resolve: (value: T) => void } {
  let resolvePromise: ((value: T) => void) | undefined;
  const promise = new Promise<T>((resolve): void => { resolvePromise = resolve; });
  return { promise, resolve: (value): void => resolvePromise?.(value) };
}

function assertSingleIdentity(requests: readonly CommandTransportRequest<CommandPayload>[]): void {
  assert.ok(requests.length > 0);
  for (const request of requests) {
    assert.equal(request.idempotencyIdentity, "idempotency-command-1");
    assert.equal(request.headers["Idempotency-Key"], "idempotency-command-1");
  }
}

test("blocks duplicate click and programmatic invocation while a command is submitting", async () => {
  const pending = deferred<SubmissionOutcome>();
  const transport = new ScriptedTransport(() => pending.promise, async () => ({ kind: "reconciled", projection: { runId: "run-1", status: "cancelled" } }));
  const { coordinator: commandCoordinator, uuid } = coordinator(transport);

  const firstSubmission = commandCoordinator.submit(COMMAND_INTENT, "user");
  assert.equal(commandCoordinator.isActionDisabled(COMMAND_INTENT.actionReferenceId), true);
  assert.equal(transport.submitRequests.length, 1);
  assertSingleIdentity(transport.submitRequests);
  assert.deepEqual(await commandCoordinator.submit(COMMAND_INTENT, "user"), { accepted: false, reason: "control_disabled", record: commandCoordinator.getRecord("cancel-run") });
  assert.deepEqual(await commandCoordinator.submit(COMMAND_INTENT, "programmatic"), { accepted: false, reason: "not_user_gesture", record: commandCoordinator.getRecord("cancel-run") });
  assert.equal(transport.submitRequests.length, 1);

  pending.resolve({ kind: "terminal", outcome: { runId: "run-1", status: "cancelled" }, correlationIdentifier: "corr-cancelled" });
  const result = await firstSubmission;
  assert.equal(result.accepted, true);
  assert.equal(commandCoordinator.getRecord("cancel-run")?.status, "terminal");
  assert.equal(commandCoordinator.isActionDisabled("cancel-run"), false);
  assert.equal(uuid.calls, 1);
});

test("renders a queued command as pending and blocks a further command", async () => {
  const transport = new ScriptedTransport(
    async () => ({ kind: "queued", pendingReference: { run_id: "run-queued" }, correlationIdentifier: "corr-queued" }),
    async () => ({ kind: "reconciled", projection: { runId: "run-queued", status: "queued" } }),
  );
  const { coordinator: commandCoordinator } = coordinator(transport);

  const result = await commandCoordinator.submit(COMMAND_INTENT, "user");
  assert.equal(result.accepted, true);
  const record = commandCoordinator.getRecord("cancel-run");
  assert.deepEqual(record?.pendingReference, { run_id: "run-queued" });
  assert.equal(record?.terminalOutcome, undefined);
  assert.equal(commandCoordinator.isActionDisabled("cancel-run"), true);
  assert.equal((await commandCoordinator.submit(COMMAND_INTENT, "user")).accepted, false);
  assert.equal(transport.submitRequests.length, 1);
});

test("marks cancellation complete only from a terminal public outcome", async () => {
  const terminal = { runId: "run-cancelled", status: "cancelled" } as const;
  const transport = new ScriptedTransport(
    async () => ({ kind: "terminal", outcome: terminal, correlationIdentifier: "corr-cancelled" }),
    async () => ({ kind: "reconciled", projection: { runId: "run-cancelled", status: "cancelled" } }),
  );
  const { coordinator: commandCoordinator } = coordinator(transport);

  const result = await commandCoordinator.submit(COMMAND_INTENT, "user");
  assert.equal(result.accepted, true);
  assert.equal(commandCoordinator.getRecord("cancel-run")?.status, "terminal");
  assert.deepEqual(commandCoordinator.getRecord("cancel-run")?.terminalOutcome, terminal);
});

test("reconciles an ambiguous transport outcome using the original idempotency identity", async () => {
  const transport = new ScriptedTransport(
    async () => { throw new TypeError("connection closed before response"); },
    async () => ({ kind: "reconciled", projection: { runId: "run-ambiguous", status: "cancelling" }, correlationIdentifier: "corr-reconciled" }),
  );
  const { coordinator: commandCoordinator, uuid } = coordinator(transport);

  await commandCoordinator.submit(COMMAND_INTENT, "user");
  assert.equal(commandCoordinator.getRecord("cancel-run")?.status, "reconciling");
  assert.equal(commandCoordinator.isActionDisabled("cancel-run"), true);
  const reconciled = await commandCoordinator.reconcile("cancel-run", "user");
  assert.equal(reconciled.accepted, true);
  assert.equal(commandCoordinator.getRecord("cancel-run")?.status, "reconciled");
  assert.deepEqual(commandCoordinator.getRecord("cancel-run")?.reconciledProjection, { runId: "run-ambiguous", status: "cancelling" });
  assertSingleIdentity([...transport.submitRequests, ...transport.reconcileRequests]);
  assert.equal(uuid.calls, 1);
});

test("does not automatically retry an exhausted ambiguous transport trace", async () => {
  const transport = new ScriptedTransport(
    async () => ({ kind: "ambiguous", correlationIdentifier: "corr-transport" }),
    async () => { throw new TypeError("reconciliation unavailable"); },
  );
  const { coordinator: commandCoordinator, uuid } = coordinator(transport);

  await commandCoordinator.submit(COMMAND_INTENT, "user");
  await commandCoordinator.reconcile("cancel-run", "user");
  await commandCoordinator.reconcile("cancel-run", "user");
  assert.equal(commandCoordinator.getRecord("cancel-run")?.status, "reconciling");
  assert.equal(transport.submitRequests.length, 1);
  assert.equal(transport.reconcileRequests.length, 2);
  assert.deepEqual([...transport.submitRequests, ...transport.reconcileRequests].map((request) => request.idempotencyIdentity), ["idempotency-command-1", "idempotency-command-1", "idempotency-command-1"]);
  assert.equal(uuid.calls, 1);
});

test("retains the identity and displays the deterministic rate-limit countdown without automatic retry", async () => {
  let submissionAttempts = 0;
  const transport = new ScriptedTransport(
    async (request) => {
      submissionAttempts += 1;
      return submissionAttempts === 1
        ? { kind: "rate_limited", message: "Retry after the published delay.", retryAfterSeconds: 30, correlationIdentifier: "corr-rate" }
        : { kind: "terminal", outcome: { runId: String(request.payload.reason), status: "complete" } };
    },
    async () => ({ kind: "reconciled", projection: { runId: "run-rate", status: "queued" } }),
  );
  const { coordinator: commandCoordinator, uuid, clock } = coordinator(transport);

  await commandCoordinator.submit(COMMAND_INTENT, "user");
  assert.equal(commandCoordinator.getRecord("cancel-run")?.message, "Retry after the published delay.");
  assert.equal(commandCoordinator.getRateLimitRemainingSeconds("cancel-run"), 30);
  clock.value += 10_000;
  assert.equal(commandCoordinator.getRateLimitRemainingSeconds("cancel-run"), 20);
  assert.equal(transport.submitRequests.length, 1);
  await commandCoordinator.submit(COMMAND_INTENT, "user");
  assertSingleIdentity(transport.submitRequests);
  assert.equal(uuid.calls, 1);
});

test("preserves each returned authorization, policy, and approval denial without creating another command", async () => {
  const denials = ["authorization", "policy", "approval"] as const;
  for (const denialKind of denials) {
    const followUp: GeneratedActionReference = { id: `${denialKind}-help`, label: `${denialKind} help` };
    const transport = new ScriptedTransport(
      async () => ({ kind: "denied", denialKind, message: `${denialKind} denied`, correlationIdentifier: `corr-${denialKind}`, actionReference: followUp }),
      async () => ({ kind: "reconciled", projection: { runId: "run-denied", status: "blocked" } }),
    );
    const { coordinator: commandCoordinator, uuid } = coordinator(transport);

    await commandCoordinator.submit(COMMAND_INTENT, "user");
    const record = commandCoordinator.getRecord("cancel-run");
    assert.equal(record?.status, "denied");
    assert.equal(record?.denialKind, denialKind);
    assert.equal(record?.message, `${denialKind} denied`);
    assert.strictEqual(record?.returnedActionReference, followUp);
    assert.equal(transport.submitRequests.length, 1);
    assert.equal(uuid.calls, 1);
  }
});

test("renders only returned manual-recovery details and escalation action", async () => {
  const escalation: GeneratedActionReference = { id: "escalate-run", label: "Escalate run recovery" };
  const transport = new ScriptedTransport(
    async () => ({ kind: "manual_recovery", recoveryStatus: "manual_recovery_required", failureSummary: "Cancellation worker exhausted its retry budget.", correlationIdentifier: "corr-manual", escalationActionReference: escalation }),
    async () => ({ kind: "reconciled", projection: { runId: "run-manual", status: "manual_recovery_required" } }),
  );
  const { coordinator: commandCoordinator } = coordinator(transport);

  await commandCoordinator.submit(COMMAND_INTENT, "user");
  const record = commandCoordinator.getRecord("cancel-run");
  assert.equal(record?.status, "manual_recovery");
  assert.equal(record?.recoveryStatus, "manual_recovery_required");
  assert.equal(record?.failureSummary, "Cancellation worker exhausted its retry budget.");
  assert.equal(record?.correlationIdentifier, "corr-manual");
  assert.strictEqual(record?.returnedActionReference, escalation);
});