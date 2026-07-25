import type { GeneratedActionReference, GeneratedJsonValue } from "../api/client";
import {
  commandReducer,
  createCommandRecord,
  isCommandControlDisabled,
  type CommandDenialKind,
  type CommandRecord,
} from "./command-reducer";

export type CommandInvocationSource = "user" | "programmatic";

export interface CommandIntent<TPayload> {
  readonly actionReferenceId: string;
  readonly actionReference: GeneratedActionReference;
  readonly payload: TPayload;
}

export interface CommandUuidSource {
  randomUUID(): string;
}

export interface CommandClock {
  now(): number;
}

export interface CommandTransportRequest<TPayload> {
  readonly actionReferenceId: string;
  readonly actionReference: GeneratedActionReference;
  readonly payload: TPayload;
  readonly idempotencyIdentity: string;
  readonly headers: Readonly<{ readonly "Idempotency-Key": string }>;
  readonly requestedAt: string;
}

export interface CommandQueuedOutcome {
  readonly kind: "queued";
  readonly pendingReference: GeneratedJsonValue;
  readonly correlationIdentifier?: string;
}

export interface CommandAmbiguousOutcome {
  readonly kind: "ambiguous";
  readonly correlationIdentifier?: string;
}

export interface CommandRateLimitedOutcome {
  readonly kind: "rate_limited";
  readonly message: string;
  readonly retryAfterSeconds: number;
  readonly correlationIdentifier?: string;
  readonly actionReference?: GeneratedActionReference;
}

export interface CommandDeniedOutcome {
  readonly kind: "denied";
  readonly denialKind: CommandDenialKind;
  readonly message: string;
  readonly correlationIdentifier?: string;
  readonly actionReference?: GeneratedActionReference;
}

export interface CommandManualRecoveryOutcome {
  readonly kind: "manual_recovery";
  readonly recoveryStatus: string;
  readonly failureSummary: string;
  readonly correlationIdentifier?: string;
  readonly escalationActionReference?: GeneratedActionReference;
}

export interface CommandTerminalOutcome<TTerminal> {
  readonly kind: "terminal";
  readonly outcome: TTerminal;
  readonly correlationIdentifier?: string;
}

export interface CommandReconciledOutcome<TProjection> {
  readonly kind: "reconciled";
  readonly projection: TProjection;
  readonly correlationIdentifier?: string;
}

export type CommandSubmissionOutcome<TTerminal> =
  | CommandQueuedOutcome
  | CommandAmbiguousOutcome
  | CommandRateLimitedOutcome
  | CommandDeniedOutcome
  | CommandManualRecoveryOutcome
  | CommandTerminalOutcome<TTerminal>;

export type CommandReconciliationOutcome<TProjection, TTerminal> =
  | CommandQueuedOutcome
  | CommandAmbiguousOutcome
  | CommandRateLimitedOutcome
  | CommandDeniedOutcome
  | CommandManualRecoveryOutcome
  | CommandReconciledOutcome<TProjection>
  | CommandTerminalOutcome<TTerminal>;

export interface CommandTransport<TPayload, TProjection, TTerminal> {
  submit(request: CommandTransportRequest<TPayload>): Promise<CommandSubmissionOutcome<TTerminal>>;
  reconcile(request: CommandTransportRequest<TPayload>): Promise<CommandReconciliationOutcome<TProjection, TTerminal>>;
}

export interface CommandCoordinatorDependencies<TPayload, TProjection, TTerminal> {
  readonly uuid: CommandUuidSource;
  readonly clock: CommandClock;
  readonly transport: CommandTransport<TPayload, TProjection, TTerminal>;
}

export interface CommandInvocationAccepted<TPayload, TProjection, TTerminal> {
  readonly accepted: true;
  readonly record: CommandRecord<TPayload, TProjection, TTerminal>;
}

export interface CommandInvocationBlocked<TPayload, TProjection, TTerminal> {
  readonly accepted: false;
  readonly reason: "not_user_gesture" | "control_disabled" | "not_reconcilable";
  readonly record?: CommandRecord<TPayload, TProjection, TTerminal>;
}

export type CommandInvocationResult<TPayload, TProjection, TTerminal> =
  | CommandInvocationAccepted<TPayload, TProjection, TTerminal>
  | CommandInvocationBlocked<TPayload, TProjection, TTerminal>;

/** Coordinates one durable command identity for each action-control intent. */
export class CommandCoordinator<TPayload, TProjection, TTerminal> {
  private readonly records = new Map<string, CommandRecord<TPayload, TProjection, TTerminal>>();
  private readonly latestRecordKeysByAction = new Map<string, string>();
  private readonly activeReconciliations = new Set<string>();

  public constructor(private readonly dependencies: CommandCoordinatorDependencies<TPayload, TProjection, TTerminal>) {}

  public getRecord(actionReferenceId: string): CommandRecord<TPayload, TProjection, TTerminal> | undefined {
    const recordKey = this.latestRecordKeysByAction.get(actionReferenceId);
    return recordKey === undefined ? undefined : this.records.get(recordKey);
  }

  public isActionDisabled(actionReferenceId: string): boolean {
    const record = this.getRecord(actionReferenceId);
    return record !== undefined && isCommandControlDisabled(record.status);
  }

  public getRateLimitRemainingSeconds(actionReferenceId: string): number | undefined {
    const record = this.getRecord(actionReferenceId);
    if (record?.status !== "rate_limited" || record.rateLimitReceivedAt === undefined || record.retryAfterSeconds === undefined) return undefined;
    const elapsedSeconds = Math.max(0, Math.floor((this.nowMilliseconds() - Date.parse(record.rateLimitReceivedAt)) / 1000));
    return Math.max(0, record.retryAfterSeconds - elapsedSeconds);
  }

  public async submit(intent: CommandIntent<TPayload>, source: CommandInvocationSource): Promise<CommandInvocationResult<TPayload, TProjection, TTerminal>> {
    if (source !== "user") return { accepted: false, reason: "not_user_gesture", record: this.getRecord(intent.actionReferenceId) };
    const existing = this.getRecord(intent.actionReferenceId);
    if (existing !== undefined && isCommandControlDisabled(existing.status)) return { accepted: false, reason: "control_disabled", record: existing };

    const record = existing === undefined || existing.status === "terminal"
      ? this.createRecord(intent)
      : this.transition(existing, { type: "submission_started", at: this.nowIso() });
    const request = this.transportRequest(record);
    try {
      const outcome = await this.dependencies.transport.submit(request);
      return { accepted: true, record: this.applySubmissionOutcome(record, outcome) };
    } catch {
      return { accepted: true, record: this.transition(record, { type: "ambiguous", at: this.nowIso() }) };
    }
  }


  public async reconcile(actionReferenceId: string, source: CommandInvocationSource): Promise<CommandInvocationResult<TPayload, TProjection, TTerminal>> {
    const record = this.getRecord(actionReferenceId);
    if (source !== "user") return { accepted: false, reason: "not_user_gesture", ...(record === undefined ? {} : { record }) };
    if (record === undefined || record.status === "terminal" || record.status === "reconciled") return { accepted: false, reason: "not_reconcilable", ...(record === undefined ? {} : { record }) };
    const recordKey = commandRecordKey(record.actionReferenceId, record.idempotencyIdentity);
    if (record.status === "submitting" || record.status === "queued" || this.activeReconciliations.has(recordKey)) return { accepted: false, reason: "control_disabled", record };

    const reconcilingRecord = this.transition(record, { type: "reconciliation_started", at: this.nowIso() });
    this.activeReconciliations.add(recordKey);
    try {
      const outcome = await this.dependencies.transport.reconcile(this.transportRequest(reconcilingRecord));
      return { accepted: true, record: this.applyReconciliationOutcome(reconcilingRecord, outcome) };
    } catch {
      return { accepted: true, record: this.transition(reconcilingRecord, { type: "ambiguous", at: this.nowIso() }) };
    } finally {
      this.activeReconciliations.delete(recordKey);
    }
  }

  private createRecord(intent: CommandIntent<TPayload>): CommandRecord<TPayload, TProjection, TTerminal> {
    if (intent.actionReferenceId.trim() === "") throw new TypeError("A returned action reference identifier is required.");
    const idempotencyIdentity = this.dependencies.uuid.randomUUID();
    if (idempotencyIdentity.trim() === "") throw new TypeError("The UUID source must return a non-empty idempotency identity.");
    const record = createCommandRecord<TPayload, TProjection, TTerminal>(
      intent.actionReferenceId,
      intent.actionReference,
      intent.payload,
      idempotencyIdentity,
      this.nowIso(),
    );
    const recordKey = commandRecordKey(record.actionReferenceId, record.idempotencyIdentity);
    this.records.set(recordKey, record);
    this.latestRecordKeysByAction.set(record.actionReferenceId, recordKey);
    return record;
  }

  private applySubmissionOutcome(
    record: CommandRecord<TPayload, TProjection, TTerminal>,
    outcome: CommandSubmissionOutcome<TTerminal>,
  ): CommandRecord<TPayload, TProjection, TTerminal> {
    return this.applyCommonOutcome(record, outcome);
  }

  private applyReconciliationOutcome(
    record: CommandRecord<TPayload, TProjection, TTerminal>,
    outcome: CommandReconciliationOutcome<TProjection, TTerminal>,
  ): CommandRecord<TPayload, TProjection, TTerminal> {
    if (outcome.kind === "reconciled") {
      return this.transition(record, {
        type: "reconciled",
        at: this.nowIso(),
        projection: outcome.projection,
        ...(outcome.correlationIdentifier === undefined ? {} : { correlationIdentifier: outcome.correlationIdentifier }),
      });
    }
    return this.applyCommonOutcome(record, outcome);
  }

  private applyCommonOutcome(
    record: CommandRecord<TPayload, TProjection, TTerminal>,
    outcome: Exclude<CommandReconciliationOutcome<TProjection, TTerminal>, CommandReconciledOutcome<TProjection>> | CommandSubmissionOutcome<TTerminal>,
  ): CommandRecord<TPayload, TProjection, TTerminal> {
    const at = this.nowIso();
    switch (outcome.kind) {
      case "queued":
        return this.transition(record, {
          type: "queued", at, pendingReference: outcome.pendingReference,
          ...(outcome.correlationIdentifier === undefined ? {} : { correlationIdentifier: outcome.correlationIdentifier }),
        });
      case "ambiguous":
        return this.transition(record, {
          type: "ambiguous", at,
          ...(outcome.correlationIdentifier === undefined ? {} : { correlationIdentifier: outcome.correlationIdentifier }),
        });
      case "rate_limited":
        return this.transition(record, {
          type: "rate_limited", at, message: outcome.message, retryAfterSeconds: outcome.retryAfterSeconds,
          ...(outcome.correlationIdentifier === undefined ? {} : { correlationIdentifier: outcome.correlationIdentifier }),
          ...(outcome.actionReference === undefined ? {} : { returnedActionReference: outcome.actionReference }),
        });
      case "denied":
        return this.transition(record, {
          type: "denied", at, denialKind: outcome.denialKind, message: outcome.message,
          ...(outcome.correlationIdentifier === undefined ? {} : { correlationIdentifier: outcome.correlationIdentifier }),
          ...(outcome.actionReference === undefined ? {} : { returnedActionReference: outcome.actionReference }),
        });
      case "manual_recovery":
        return this.transition(record, {
          type: "manual_recovery", at, recoveryStatus: outcome.recoveryStatus, failureSummary: outcome.failureSummary,
          ...(outcome.correlationIdentifier === undefined ? {} : { correlationIdentifier: outcome.correlationIdentifier }),
          ...(outcome.escalationActionReference === undefined ? {} : { returnedActionReference: outcome.escalationActionReference }),
        });
      case "terminal":
        return this.transition(record, {
          type: "terminal", at, outcome: outcome.outcome,
          ...(outcome.correlationIdentifier === undefined ? {} : { correlationIdentifier: outcome.correlationIdentifier }),
        });
    }
  }

  private transition(
    record: CommandRecord<TPayload, TProjection, TTerminal>,
    action: Parameters<typeof commandReducer<TPayload, TProjection, TTerminal>>[1],
  ): CommandRecord<TPayload, TProjection, TTerminal> {
    const nextRecord = commandReducer(record, action);
    this.records.set(commandRecordKey(nextRecord.actionReferenceId, nextRecord.idempotencyIdentity), nextRecord);
    this.latestRecordKeysByAction.set(nextRecord.actionReferenceId, commandRecordKey(nextRecord.actionReferenceId, nextRecord.idempotencyIdentity));
    return nextRecord;
  }

  private transportRequest(record: CommandRecord<TPayload, TProjection, TTerminal>): CommandTransportRequest<TPayload> {
    return {
      actionReferenceId: record.actionReferenceId,
      actionReference: record.actionReference,
      payload: record.payload,
      idempotencyIdentity: record.idempotencyIdentity,
      headers: { "Idempotency-Key": record.idempotencyIdentity },
      requestedAt: this.nowIso(),
    };
  }

  private nowIso(): string {
    return new Date(this.nowMilliseconds()).toISOString();
  }

  private nowMilliseconds(): number {
    const value = this.dependencies.clock.now();
    if (!Number.isFinite(value)) throw new RangeError("The command clock must return a finite timestamp.");
    return value;
  }
}

function commandRecordKey(actionReferenceId: string, idempotencyIdentity: string): string {
  return JSON.stringify([actionReferenceId, idempotencyIdentity]);
}
