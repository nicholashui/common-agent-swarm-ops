import assert from "node:assert/strict";
import test from "node:test";

import type {
  GeneratedActionReference,
  GeneratedOperationData,
  GeneratedOperationId,
  GeneratedOperationRequest,
  GeneratedOperationResult,
} from "../api/client";
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

const DISPATCH_RUN = "dispatch_run_api_v1_workflow_runs_dispatch_post" as const;
const READ_RUN = "read_run_api_v1_workflow_runs__run_id__get" as const;

type DispatchOperation = typeof DISPATCH_RUN;
type ReadRunOperation = typeof READ_RUN;
type CommandOperation = DispatchOperation | ReadRunOperation;
type DispatchResponse = GeneratedOperationData<DispatchOperation>;
type RunProjection = GeneratedOperationData<ReadRunOperation>;
type GeneratedCommandError = Extract<GeneratedOperationResult<unknown>, { readonly ok: false }>;

interface Payload { readonly runId: string; }
interface ReconciledProjection { readonly runId: string; readonly status: string; }
interface TerminalOutcome { readonly runId: string; readonly status: string; }
interface ScriptedGeneratedClientStep {
  readonly operation: CommandOperation;
  readonly result: Promise<GeneratedOperationResult<DispatchResponse | RunProjection>>;
}
interface RecordedGeneratedCommandRequest {
  readonly operation: CommandOperation;
  readonly request: GeneratedOperationRequest<DispatchOperation> | GeneratedOperationRequest<ReadRunOperation>;
}
interface GeneratedCommandClient {
  request<TOperation extends CommandOperation>(
    operation: TOperation,
    request: GeneratedOperationRequest<TOperation>,
  ): Promise<GeneratedOperationResult<GeneratedOperationData<TOperation>>>;
}

const ACTION_REFERENCE: GeneratedActionReference = { id: "dispatch-run", label: "Dispatch run", eligible: true };
const COMMAND_INTENT: CommandIntent<Payload> = {
  actionReferenceId: "dispatch-run",
  actionReference: ACTION_REFERENCE,
  payload: { runId: "run-fixture" },
};

class FixedUuidSource implements CommandUuidSource {
  public calls = 0;
  public randomUUID(): string { this.calls += 1; return "generated-command-identity"; }
}

class FixedClock implements CommandClock {
  public now(): number { return Date.UTC(2025, 0, 1, 0, 0, 0); }
}

class ScriptedGeneratedCommandClient implements GeneratedCommandClient {
  public readonly requests: RecordedGeneratedCommandRequest[] = [];

  public constructor(private readonly steps: ScriptedGeneratedClientStep[]) {}

  public request<TOperation extends CommandOperation>(
    operation: TOperation,
    request: GeneratedOperationRequest<TOperation>,
  ): Promise<GeneratedOperationResult<GeneratedOperationData<TOperation>>> {
    const step = this.steps.shift();
    assert.ok(step, "the generated-client fake must have a response for each request");
    assert.equal(step.operation, operation);
    this.requests.push({
      operation,
      request: request as GeneratedOperationRequest<DispatchOperation> | GeneratedOperationRequest<ReadRunOperation>,
    });
    return step.result as unknown as Promise<GeneratedOperationResult<GeneratedOperationData<TOperation>>>;
  }
}

class GeneratedCommandTransport implements CommandTransport<Payload, ReconciledProjection, TerminalOutcome> {
  public readonly submitRequests: CommandTransportRequest<Payload>[] = [];
  public readonly reconcileRequests: CommandTransportRequest<Payload>[] = [];

  public constructor(private readonly client: GeneratedCommandClient) {}

  public async submit(request: CommandTransportRequest<Payload>): Promise<CommandSubmissionOutcome<TerminalOutcome>> {
    this.submitRequests.push(request);
    const result = await this.client.request(DISPATCH_RUN, {
      path: {},
      body: { run_id: request.payload.runId, idempotency_key: request.idempotencyIdentity, confirm: true },
    });
    if (!result.ok) return mapGeneratedError(result);
    if (result.data.status === "queued") {
      return { kind: "queued", pendingReference: { run_id: result.data.run_id }, correlationIdentifier: result.correlationId };
    }
    return { kind: "terminal", outcome: { runId: result.data.run_id, status: result.data.status }, correlationIdentifier: result.correlationId };
  }

  public async reconcile(request: CommandTransportRequest<Payload>): Promise<CommandReconciliationOutcome<ReconciledProjection, TerminalOutcome>> {
    this.reconcileRequests.push(request);
    const result = await this.client.request(READ_RUN, { path: { run_id: request.payload.runId } });
    if (!result.ok) return mapGeneratedError(result);
    return {
      kind: "reconciled",
      projection: { runId: result.data.run_id, status: result.data.status },
      correlationIdentifier: result.correlationId,
    };
  }
}

function mapGeneratedError(result: GeneratedCommandError): Exclude<CommandSubmissionOutcome<TerminalOutcome>, { readonly kind: "terminal" }> {
  if (result.code === "rate_limited") {
    return {
      kind: "rate_limited", message: result.message, retryAfterSeconds: result.retryAfterSeconds ?? 0,
      ...(result.correlationId === undefined ? {} : { correlationIdentifier: result.correlationId }),
      ...(result.actionReference === undefined ? {} : { actionReference: result.actionReference }),
    };
  }
  const denialKind = result.code === "authorization_denied" ? "authorization"
    : result.code === "policy_denied" ? "policy"
      : result.code === "approval_gate_denied" ? "approval" : undefined;
  if (denialKind !== undefined) {
    return {
      kind: "denied", denialKind, message: result.message,
      ...(result.correlationId === undefined ? {} : { correlationIdentifier: result.correlationId }),
      ...(result.actionReference === undefined ? {} : { actionReference: result.actionReference }),
    };
  }
  if (result.code === "manual_recovery" || result.code === "dead_letter") {
    return {
      kind: "manual_recovery", recoveryStatus: result.code, failureSummary: result.message,
      ...(result.correlationId === undefined ? {} : { correlationIdentifier: result.correlationId }),
      ...(result.actionReference === undefined ? {} : { escalationActionReference: result.actionReference }),
    };
  }
  return { kind: "ambiguous", ...(result.correlationId === undefined ? {} : { correlationIdentifier: result.correlationId }) };
}

function preview(): DispatchResponse["preview"] {
  return { action_id: "dispatch-fixture", emitted_at: "2025-01-01T00:00:00.000Z", intended_effect: "Dispatch the returned run.", summary: "Dispatch run" };
}

function dispatchResponse(status: string): DispatchResponse {
  return { executed: status !== "queued", preview: preview(), run_id: "run-fixture", status };
}

function readRunResponse(status: string): RunProjection {
  return {
    action_preview: null, correlation_id: "corr-reconciled", engine: "workflow-engine", failure_code: null,
    output: null, run_id: "run-fixture", status, updated_at: "2025-01-01T00:00:00.000Z",
    workflow_id: "workflow-fixture", workflow_version: "v1",
  };
}

function success<TData>(data: TData, correlationId = "corr-command"): GeneratedOperationResult<TData> {
  return { ok: true, data, correlationId };
}

function error<TData>(
  code: string,
  message: string,
  retryable: boolean,
  options: { readonly correlationId?: string; readonly retryAfterSeconds?: number; readonly actionReference?: GeneratedActionReference } = {},
): GeneratedOperationResult<TData> {
  return {
    ok: false, code, message, retryable,
    ...(options.correlationId === undefined ? {} : { correlationId: options.correlationId }),
    ...(options.retryAfterSeconds === undefined ? {} : { retryAfterSeconds: options.retryAfterSeconds }),
    ...(options.actionReference === undefined ? {} : { actionReference: options.actionReference }),
  };
}

function deferred<T>(): { readonly promise: Promise<T>; readonly resolve: (value: T) => void } {
  let resolvePromise: ((value: T) => void) | undefined;
  const promise = new Promise<T>((resolve): void => { resolvePromise = resolve; });
  return { promise, resolve: (value: T): void => resolvePromise?.(value) };
}

function createHarness(steps: ScriptedGeneratedClientStep[]): {
  readonly coordinator: CommandCoordinator<Payload, ReconciledProjection, TerminalOutcome>;
  readonly client: ScriptedGeneratedCommandClient;
  readonly transport: GeneratedCommandTransport;
  readonly uuid: FixedUuidSource;
} {
  const client = new ScriptedGeneratedCommandClient(steps);
  const transport = new GeneratedCommandTransport(client);
  const uuid = new FixedUuidSource();
  return { coordinator: new CommandCoordinator({ uuid, clock: new FixedClock(), transport }), client, transport, uuid };
}

function assertOneDurableIdentity(
  harness: ReturnType<typeof createHarness>,
  expectedCoordinatorRequests: number,
): void {
  const record = harness.coordinator.getRecord(COMMAND_INTENT.actionReferenceId);
  assert.ok(record);
  assert.equal(record.idempotencyIdentity, "generated-command-identity");
  assert.equal(harness.uuid.calls, 1);
  assert.equal(harness.transport.submitRequests.length + harness.transport.reconcileRequests.length, expectedCoordinatorRequests);
  for (const request of [...harness.transport.submitRequests, ...harness.transport.reconcileRequests]) {
    assert.equal(request.idempotencyIdentity, "generated-command-identity");
    assert.equal(request.headers["Idempotency-Key"], "generated-command-identity");
  }
  const dispatch = harness.client.requests.find((request) => request.operation === DISPATCH_RUN);
  assert.ok(dispatch);
  const body = (dispatch.request as GeneratedOperationRequest<DispatchOperation>).body;
  assert.equal(body.idempotency_key, "generated-command-identity");
}

// Requirements 3.1–3.13, 11.2, 11.3
// Uses only generated operation types and a fixed generated-client fake; no network or hand-written endpoint DTO is used.
test("generated command integration blocks duplicate click and classifies cancellation only after the terminal response", async (): Promise<void> => {
  const pending = deferred<GeneratedOperationResult<DispatchResponse | RunProjection>>();
  const harness = createHarness([{ operation: DISPATCH_RUN, result: pending.promise }]);

  const firstSubmission = harness.coordinator.submit(COMMAND_INTENT, "user");
  assert.equal(harness.coordinator.isActionDisabled(COMMAND_INTENT.actionReferenceId), true);
  assert.equal(harness.client.requests.length, 1);
  assert.deepEqual(await harness.coordinator.submit(COMMAND_INTENT, "user"), {
    accepted: false, reason: "control_disabled", record: harness.coordinator.getRecord(COMMAND_INTENT.actionReferenceId),
  });
  assert.equal(harness.client.requests.length, 1);
  assertOneDurableIdentity(harness, 1);

  pending.resolve(success(dispatchResponse("cancelled"), "corr-cancelled"));
  const submission = await firstSubmission;
  assert.equal(submission.accepted, true);
  const record = harness.coordinator.getRecord(COMMAND_INTENT.actionReferenceId);
  assert.equal(record?.status, "terminal");
  assert.deepEqual(record?.terminalOutcome, { runId: "run-fixture", status: "cancelled" });
  assert.equal(record?.correlationIdentifier, "corr-cancelled");
});

test("generated command integration renders a queued response as pending and prevents a second dispatch", async (): Promise<void> => {
  const harness = createHarness([{ operation: DISPATCH_RUN, result: Promise.resolve(success(dispatchResponse("queued"), "corr-queued")) }]);

  await harness.coordinator.submit(COMMAND_INTENT, "user");
  const record = harness.coordinator.getRecord(COMMAND_INTENT.actionReferenceId);
  assert.equal(record?.status, "queued");
  assert.deepEqual(record?.pendingReference, { run_id: "run-fixture" });
  assert.equal(record?.terminalOutcome, undefined);
  assert.equal(harness.coordinator.isActionDisabled(COMMAND_INTENT.actionReferenceId), true);
  assert.equal((await harness.coordinator.submit(COMMAND_INTENT, "user")).accepted, false);
  assert.equal(harness.client.requests.length, 1);
  assertOneDurableIdentity(harness, 1);
});

test("generated command integration reconciles an ambiguous transport outcome with the retained identity", async (): Promise<void> => {
  const harness = createHarness([
    { operation: DISPATCH_RUN, result: Promise.reject(new TypeError("connection closed before generated response")) },
    { operation: READ_RUN, result: Promise.resolve(success(readRunResponse("cancelling"), "corr-reconciled")) },
  ]);

  await harness.coordinator.submit(COMMAND_INTENT, "user");
  assert.equal(harness.coordinator.getRecord(COMMAND_INTENT.actionReferenceId)?.status, "reconciling");
  const reconciliation = await harness.coordinator.reconcile(COMMAND_INTENT.actionReferenceId, "user");
  assert.equal(reconciliation.accepted, true);
  const record = harness.coordinator.getRecord(COMMAND_INTENT.actionReferenceId);
  assert.equal(record?.status, "reconciled");
  assert.deepEqual(record?.reconciledProjection, { runId: "run-fixture", status: "cancelling" });
  assert.equal(record?.correlationIdentifier, "corr-reconciled");
  assert.deepEqual(harness.client.requests.map((request) => request.operation), [DISPATCH_RUN, READ_RUN]);
  assertOneDurableIdentity(harness, 2);
});
test("generated command integration never automatically redispatches after retry exhaustion", async (): Promise<void> => {
  const unavailable = error<DispatchResponse | RunProjection>("transport_unavailable", "The public API request could not be completed.", true, { correlationId: "corr-transport" });
  const harness = createHarness([
    { operation: DISPATCH_RUN, result: Promise.resolve(unavailable) },
    { operation: READ_RUN, result: Promise.resolve(unavailable) },
    { operation: READ_RUN, result: Promise.resolve(unavailable) },
  ]);

  await harness.coordinator.submit(COMMAND_INTENT, "user");
  await harness.coordinator.reconcile(COMMAND_INTENT.actionReferenceId, "user");
  await harness.coordinator.reconcile(COMMAND_INTENT.actionReferenceId, "user");
  assert.equal(harness.coordinator.getRecord(COMMAND_INTENT.actionReferenceId)?.status, "reconciling");
  assert.deepEqual(harness.client.requests.map((request) => request.operation), [DISPATCH_RUN, READ_RUN, READ_RUN]);
  assert.equal(harness.transport.submitRequests.length, 1);
  assertOneDurableIdentity(harness, 3);
});

test("generated command integration preserves returned rate, denial, and manual recovery details", async (): Promise<void> => {
  const returnedAction: GeneratedActionReference = { id: "returned-action", label: "Review returned action" };
  const scenarios = [
    { code: "rate_limited", expectedStatus: "rate_limited", expectedDenial: undefined, retryAfterSeconds: 45 },
    { code: "authorization_denied", expectedStatus: "denied", expectedDenial: "authorization", retryAfterSeconds: undefined },
    { code: "policy_denied", expectedStatus: "denied", expectedDenial: "policy", retryAfterSeconds: undefined },
    { code: "approval_gate_denied", expectedStatus: "denied", expectedDenial: "approval", retryAfterSeconds: undefined },
    { code: "manual_recovery", expectedStatus: "manual_recovery", expectedDenial: undefined, retryAfterSeconds: undefined },
  ] as const;

  for (const scenario of scenarios) {
    const message = `Returned ${scenario.code} message.`;
    const harness = createHarness([{
      operation: DISPATCH_RUN,
      result: Promise.resolve(error<DispatchResponse | RunProjection>(scenario.code, message, false, {
        correlationId: `corr-${scenario.code}`, retryAfterSeconds: scenario.retryAfterSeconds, actionReference: returnedAction,
      })),
    }]);

    await harness.coordinator.submit(COMMAND_INTENT, "user");
    const record = harness.coordinator.getRecord(COMMAND_INTENT.actionReferenceId);
    assert.equal(record?.status, scenario.expectedStatus, scenario.code);
    assert.equal(record?.message, scenario.expectedStatus === "manual_recovery" ? undefined : message, scenario.code);
    assert.equal(record?.denialKind, scenario.expectedDenial, scenario.code);
    assert.strictEqual(record?.returnedActionReference, returnedAction, scenario.code);
    assert.equal(record?.correlationIdentifier, `corr-${scenario.code}`, scenario.code);
    assert.equal(record?.retryAfterSeconds, scenario.retryAfterSeconds, scenario.code);
    if (scenario.code === "manual_recovery") {
      assert.equal(record?.recoveryStatus, "manual_recovery");
      assert.equal(record?.failureSummary, message);
    }
    assert.equal(harness.client.requests.length, 1, scenario.code);
    assertOneDurableIdentity(harness, 1);
  }
});
