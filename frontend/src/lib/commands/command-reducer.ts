import type { GeneratedActionReference, GeneratedJsonValue } from "../api/client";

export type CommandStatus = "submitting" | "queued" | "reconciling" | "rate_limited" | "denied" | "manual_recovery" | "reconciled" | "terminal";
export type CommandDenialKind = "authorization" | "policy" | "approval";

export interface CommandRecord<TPayload, TProjection, TTerminal> {
  readonly actionReferenceId: string;
  readonly actionReference: GeneratedActionReference;
  readonly payload: TPayload;
  readonly idempotencyIdentity: string;
  readonly status: CommandStatus;
  readonly createdAt: string;
  readonly updatedAt: string;
  readonly attempts: number;
  readonly correlationIdentifier?: string;
  readonly pendingReference?: GeneratedJsonValue;
  readonly message?: string;
  readonly retryAfterSeconds?: number;
  readonly rateLimitReceivedAt?: string;
  readonly denialKind?: CommandDenialKind;
  readonly returnedActionReference?: GeneratedActionReference;
  readonly recoveryStatus?: string;
  readonly failureSummary?: string;
  readonly reconciledProjection?: TProjection;
  readonly terminalOutcome?: TTerminal;
}

export interface CommandSubmissionStarted {
  readonly type: "submission_started";
  readonly at: string;
}

export interface CommandQueued {
  readonly type: "queued";
  readonly at: string;
  readonly pendingReference: GeneratedJsonValue;
  readonly correlationIdentifier?: string;
}

export interface CommandReconciliationStarted {
  readonly type: "reconciliation_started";
  readonly at: string;
}

export interface CommandAmbiguous {
  readonly type: "ambiguous";
  readonly at: string;
  readonly correlationIdentifier?: string;
}

export interface CommandRateLimited {
  readonly type: "rate_limited";
  readonly at: string;
  readonly message: string;
  readonly retryAfterSeconds: number;
  readonly correlationIdentifier?: string;
  readonly returnedActionReference?: GeneratedActionReference;
}

export interface CommandDenied {
  readonly type: "denied";
  readonly at: string;
  readonly denialKind: CommandDenialKind;
  readonly message: string;
  readonly correlationIdentifier?: string;
  readonly returnedActionReference?: GeneratedActionReference;
}

export interface CommandManualRecovery {
  readonly type: "manual_recovery";
  readonly at: string;
  readonly recoveryStatus: string;
  readonly failureSummary: string;
  readonly correlationIdentifier?: string;
  readonly returnedActionReference?: GeneratedActionReference;
}

export interface CommandReconciled<TProjection> {
  readonly type: "reconciled";
  readonly at: string;
  readonly projection: TProjection;
  readonly correlationIdentifier?: string;
}

export interface CommandTerminal<TTerminal> {
  readonly type: "terminal";
  readonly at: string;
  readonly outcome: TTerminal;
  readonly correlationIdentifier?: string;
}

export type CommandReducerAction<TProjection, TTerminal> =
  | CommandSubmissionStarted
  | CommandQueued
  | CommandReconciliationStarted
  | CommandAmbiguous
  | CommandRateLimited
  | CommandDenied
  | CommandManualRecovery
  | CommandReconciled<TProjection>
  | CommandTerminal<TTerminal>;

export function createCommandRecord<TPayload, TProjection, TTerminal>(
  actionReferenceId: string,
  actionReference: GeneratedActionReference,
  payload: TPayload,
  idempotencyIdentity: string,
  createdAt: string,
): CommandRecord<TPayload, TProjection, TTerminal> {
  return {
    actionReferenceId,
    actionReference,
    payload,
    idempotencyIdentity,
    status: "submitting",
    createdAt,
    updatedAt: createdAt,
    attempts: 1,
  };
}

/** Applies only explicitly typed command transitions; it never allocates or replaces an idempotency identity. */
export function commandReducer<TPayload, TProjection, TTerminal>(
  record: CommandRecord<TPayload, TProjection, TTerminal>,
  action: CommandReducerAction<TProjection, TTerminal>,
): CommandRecord<TPayload, TProjection, TTerminal> {
  switch (action.type) {
    case "submission_started":
      return clearOutcome(record, { status: "submitting", updatedAt: action.at, attempts: record.attempts + 1 });
    case "queued":
      return clearOutcome(record, {
        status: "queued", updatedAt: action.at, pendingReference: action.pendingReference,
        ...(action.correlationIdentifier === undefined ? {} : { correlationIdentifier: action.correlationIdentifier }),
      });
    case "reconciliation_started":
      return clearOutcome(record, { status: "reconciling", updatedAt: action.at });
    case "ambiguous":
      return clearOutcome(record, {
        status: "reconciling", updatedAt: action.at,
        ...(action.correlationIdentifier === undefined ? {} : { correlationIdentifier: action.correlationIdentifier }),
      });
    case "rate_limited":
      return clearOutcome(record, {
        status: "rate_limited", updatedAt: action.at, message: action.message,
        retryAfterSeconds: action.retryAfterSeconds, rateLimitReceivedAt: action.at,
        ...(action.correlationIdentifier === undefined ? {} : { correlationIdentifier: action.correlationIdentifier }),
        ...(action.returnedActionReference === undefined ? {} : { returnedActionReference: action.returnedActionReference }),
      });
    case "denied":
      return clearOutcome(record, {
        status: "denied", updatedAt: action.at, denialKind: action.denialKind, message: action.message,
        ...(action.correlationIdentifier === undefined ? {} : { correlationIdentifier: action.correlationIdentifier }),
        ...(action.returnedActionReference === undefined ? {} : { returnedActionReference: action.returnedActionReference }),
      });
    case "manual_recovery":
      return clearOutcome(record, {
        status: "manual_recovery", updatedAt: action.at, recoveryStatus: action.recoveryStatus, failureSummary: action.failureSummary,
        ...(action.correlationIdentifier === undefined ? {} : { correlationIdentifier: action.correlationIdentifier }),
        ...(action.returnedActionReference === undefined ? {} : { returnedActionReference: action.returnedActionReference }),
      });
    case "reconciled":
      return clearOutcome(record, {
        status: "reconciled", updatedAt: action.at, reconciledProjection: action.projection,
        ...(action.correlationIdentifier === undefined ? {} : { correlationIdentifier: action.correlationIdentifier }),
      });
    case "terminal":
      return clearOutcome(record, {
        status: "terminal", updatedAt: action.at, terminalOutcome: action.outcome,
        ...(action.correlationIdentifier === undefined ? {} : { correlationIdentifier: action.correlationIdentifier }),
      });
  }
}

export function isCommandControlDisabled(status: CommandStatus): boolean {
  return status === "submitting" || status === "queued" || status === "reconciling";
}

export function isCommandCompleted<TPayload, TProjection, TTerminal>(record: CommandRecord<TPayload, TProjection, TTerminal>): boolean {
  return record.status === "terminal" && record.terminalOutcome !== undefined;
}

type CommandOutcomeFields<TProjection, TTerminal> = Omit<CommandRecord<unknown, TProjection, TTerminal>, "status" | "updatedAt" | "attempts">;

function clearOutcome<TPayload, TProjection, TTerminal>(
  record: CommandRecord<TPayload, TProjection, TTerminal>,
  update: Partial<CommandRecord<TPayload, TProjection, TTerminal>> & Pick<CommandRecord<TPayload, TProjection, TTerminal>, "status" | "updatedAt">,
): CommandRecord<TPayload, TProjection, TTerminal> {
  const {
    correlationIdentifier: _correlationIdentifier,
    pendingReference: _pendingReference,
    message: _message,
    retryAfterSeconds: _retryAfterSeconds,
    rateLimitReceivedAt: _rateLimitReceivedAt,
    denialKind: _denialKind,
    returnedActionReference: _returnedActionReference,
    recoveryStatus: _recoveryStatus,
    failureSummary: _failureSummary,
    reconciledProjection: _reconciledProjection,
    terminalOutcome: _terminalOutcome,
    ...stableRecord
  } = record;
  return { ...stableRecord, ...update };
}
