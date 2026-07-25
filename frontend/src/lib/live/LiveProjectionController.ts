import type { GeneratedJsonObject } from "../api/client";
import type { AbortableSseSubscription, ProjectionStateStore } from "../session/session-runtime";

export type LiveConnectionState = "loadingSnapshot" | "subscribing" | "live" | "reconnecting" | "stale" | "resynchronizing";

export interface LiveProjectionState<TProjection> {
  readonly projection: TProjection | null;
  readonly subscriptionScope: string;
  readonly expectedSequence: number | null;
  readonly schemaVersion: string | null;
  readonly eventCursor: string | null;
  readonly connection: LiveConnectionState;
}

export interface AuthorizedSubscriptionContext {
  readonly scope: string;
  readonly authorizedTopics: readonly string[];
  /** Opaque generated sequence context returned with the REST snapshot. */
  readonly sequenceContext: GeneratedJsonObject;
}

export interface LiveProjectionSnapshot<TProjection> {
  readonly projection: TProjection;
  readonly schemaVersion: string;
  readonly expectedSequence: number;
  readonly subscription: AuthorizedSubscriptionContext;
}

export interface LiveOperationalEvent<TEvent> {
  readonly resourceScope: string;
  readonly schemaVersion: string;
  readonly sequence: number;
  readonly eventId: string;
  readonly payload: TEvent;
}

export interface LiveSnapshotLoader<TProjection> {
  loadSnapshot(scope: string): Promise<LiveProjectionSnapshot<TProjection>>;
}

export interface LiveEventDecoder<TEvent> {
  decode(value: unknown): LiveOperationalEvent<TEvent> | null;
}

export interface LiveSubscriptionHandlers {
  onConnected(): void;
  onDisconnected(): void;
  onStale(): void;
  onOperationalEvent(event: unknown): void;
}

export interface AuthorizedLiveSubscriptionFactory {
  subscribe(context: AuthorizedSubscriptionContext, handlers: LiveSubscriptionHandlers): AbortableSseSubscription;
}

export interface LiveProjectionCursorStore {
  save(scope: string, eventCursor: string): void;
  clear(scope: string): void;
}

export interface LiveProjectionControllerOptions<TProjection, TEvent> {
  readonly snapshotLoader: LiveSnapshotLoader<TProjection>;
  readonly subscriptionFactory: AuthorizedLiveSubscriptionFactory;
  readonly eventDecoder: LiveEventDecoder<TEvent>;
  readonly applyEvent: (projection: TProjection, event: LiveOperationalEvent<TEvent>) => TProjection;
  readonly cursorStore?: LiveProjectionCursorStore;
  readonly onStateChange?: (scope: string, state: LiveProjectionState<TProjection>) => void;
}

export class LiveProjectionConfigurationError extends Error {
  public constructor(message: string) {
    super(message);
    this.name = "LiveProjectionConfigurationError";
  }
}

/** Keeps event cursors isolated by authorized subscription scope. */
export class InMemoryLiveProjectionCursorStore implements LiveProjectionCursorStore {
  private readonly cursors = new Map<string, string>();

  public save(scope: string, eventCursor: string): void {
    this.cursors.set(scope, eventCursor);
  }

  public clear(scope: string): void {
    this.cursors.delete(scope);
  }

  public read(scope: string): string | null {
    return this.cursors.get(scope) ?? null;
  }
}

interface ScopeEntry<TProjection> {
  state: LiveProjectionState<TProjection>;
  subscription: AbortableSseSubscription | null;
  streamEpoch: number;
  operation: Promise<void> | null;
}

/**
 * Owns snapshot-first, sequence-guarded live state for each authorized scope.
 * The loader, decoder, and subscription factory are generated-contract adapters.
 */
export class LiveProjectionController<TProjection, TEvent>
  implements ProjectionStateStore, AbortableSseSubscription {
  private readonly scopes = new Map<string, ScopeEntry<TProjection>>();
  private readonly cursorStore: LiveProjectionCursorStore;

  public constructor(private readonly options: LiveProjectionControllerOptions<TProjection, TEvent>) {
    this.cursorStore = options.cursorStore ?? new InMemoryLiveProjectionCursorStore();
  }

  public getState(scope: string): LiveProjectionState<TProjection> | null {
    return this.scopes.get(scope)?.state ?? null;
  }

  /** Loads the authoritative snapshot before opening the authorized stream. */
  public async start(scope: string): Promise<void> {
    assertScope(scope);
    const entry = this.entryFor(scope);
    if (entry.operation !== null) return entry.operation;
    this.invalidateSubscription(entry);
    const epoch = entry.streamEpoch;
    this.publish(scope, entry, emptyState(scope, "loadingSnapshot"));
    return this.runOperation(scope, entry, epoch, false);
  }

  /** Processes one raw event received through the subscription for its scope. */
  public async handleOperationalEvent(scope: string, value: unknown): Promise<void> {
    assertScope(scope);
    const entry = this.scopes.get(scope);
    if (entry === undefined || entry.state.connection !== "live") return;

    const event = this.options.eventDecoder.decode(value);
    const currentProjection = entry.state.projection;
    const expectedSequence = entry.state.expectedSequence;
    if (!isValidEvent(event) || !matchesExpectedEvent(entry.state, scope, event)
      || currentProjection === null || expectedSequence === null) {
      await this.resynchronize(scope);
      return;
    }

    try {
      const projection = this.options.applyEvent(currentProjection, event);
      this.cursorStore.save(scope, event.eventId);
      this.publish(scope, entry, {
        ...entry.state,
        projection,
        expectedSequence: expectedSequence + 1,
        eventCursor: event.eventId,
      });
    } catch {
      await this.resynchronize(scope);
    }
  }

  /** A transport disconnect is observation state only; it asserts no projection fact. */
  public markReconnecting(scope: string): void {
    this.setConnection(scope, "reconnecting");
  }

  public markStale(scope: string): void {
    this.setConnection(scope, "stale");
  }

  /** Replay expiry, denial, bounded replay, and sequence anomalies share one recovery path. */
  public async handleReplayAnomaly(scope: string): Promise<void> {
    assertScope(scope);
    await this.resynchronize(scope);
  }

  /** Aborts every current stream and invalidates callbacks from those streams. */
  public abort(): void {
    for (const [scope, entry] of this.scopes) {
      this.invalidateSubscription(entry);
      entry.operation = null;
      this.publish(scope, entry, { ...entry.state, connection: entry.state.projection === null ? "loadingSnapshot" : "stale" });
    }
  }

  /** Implements the session projection-store contract. */
  public clearRestSnapshot(): void {
    for (const [scope, entry] of this.scopes) {
      this.invalidateSubscription(entry);
      entry.operation = null;
      this.clearCursor(scope);
      this.publish(scope, entry, emptyState(scope, "loadingSnapshot"));
    }
  }

  /** Implements the session projection-store contract. */
  public clearIncrementalState(): void {
    for (const [scope, entry] of this.scopes) {
      this.clearCursor(scope);
      this.publish(scope, entry, {
        ...entry.state,
        expectedSequence: null,
        eventCursor: null,
        connection: entry.state.projection === null ? "loadingSnapshot" : "stale",
      });
    }
  }

  private async resynchronize(scope: string): Promise<void> {
    const entry = this.scopes.get(scope);
    if (entry === undefined) return;
    if (entry.operation !== null) return entry.operation;

    this.invalidateSubscription(entry);
    this.clearCursor(scope);
    this.publish(scope, entry, emptyState(scope, "resynchronizing"));
    return this.runOperation(scope, entry, entry.streamEpoch, true);
  }

  private async runOperation(scope: string, entry: ScopeEntry<TProjection>, epoch: number, resynchronizing: boolean): Promise<void> {
    const operation = this.loadSnapshotAndSubscribe(scope, entry, epoch, resynchronizing);
    entry.operation = operation;
    try {
      await operation;
    } finally {
      if (entry.operation === operation) entry.operation = null;
    }
  }

  private async loadSnapshotAndSubscribe(
    scope: string,
    entry: ScopeEntry<TProjection>,
    epoch: number,
    resynchronizing: boolean,
  ): Promise<void> {
    try {
      const snapshot = this.options.snapshotLoader.loadSnapshot(scope);
      const loaded = await snapshot;
      if (!this.isCurrent(entry, epoch)) return;
      assertSnapshot(scope, loaded);
      this.publish(scope, entry, {
        projection: loaded.projection,
        subscriptionScope: scope,
        expectedSequence: loaded.expectedSequence,
        schemaVersion: loaded.schemaVersion,
        eventCursor: null,
        connection: "subscribing",
      });
      this.openSubscription(scope, entry, epoch, loaded.subscription);
    } catch {
      if (this.isCurrent(entry, epoch)) this.publish(scope, entry, { ...entry.state, connection: "stale" });
    }
  }

  private openSubscription(
    scope: string,
    entry: ScopeEntry<TProjection>,
    epoch: number,
    context: AuthorizedSubscriptionContext,
  ): void {
    const subscription = this.options.subscriptionFactory.subscribe(context, {
      onConnected: (): void => this.setConnectionForEpoch(scope, entry, epoch, "live"),
      onDisconnected: (): void => this.setConnectionForEpoch(scope, entry, epoch, "reconnecting"),
      onStale: (): void => this.setConnectionForEpoch(scope, entry, epoch, "stale"),
      onOperationalEvent: (value: unknown): void => {
        void this.consumeSubscriptionEvent(scope, entry, epoch, value);
      },
    });
    if (!this.isCurrent(entry, epoch)) {
      safeAbort(subscription);
      return;
    }
    entry.subscription = subscription;
    this.publish(scope, entry, { ...entry.state, connection: "live" });
  }

  private async consumeSubscriptionEvent(
    scope: string,
    entry: ScopeEntry<TProjection>,
    epoch: number,
    value: unknown,
  ): Promise<void> {
    if (!this.isCurrent(entry, epoch)) return;
    try {
      await this.handleOperationalEvent(scope, value);
    } catch {
      this.setConnectionForEpoch(scope, entry, epoch, "stale");
    }
  }

  private entryFor(scope: string): ScopeEntry<TProjection> {
    const found = this.scopes.get(scope);
    if (found !== undefined) return found;
    const entry: ScopeEntry<TProjection> = {
      state: emptyState(scope, "loadingSnapshot"),
      subscription: null,
      streamEpoch: 0,
      operation: null,
    };
    this.scopes.set(scope, entry);
    return entry;
  }

  private invalidateSubscription(entry: ScopeEntry<TProjection>): void {
    entry.streamEpoch += 1;
    if (entry.subscription !== null) safeAbort(entry.subscription);
    entry.subscription = null;
  }

  private isCurrent(entry: ScopeEntry<TProjection>, epoch: number): boolean {
    return entry.streamEpoch === epoch;
  }

  private setConnection(scope: string, connection: "reconnecting" | "stale"): void {
    const entry = this.scopes.get(scope);
    if (entry === undefined || entry.operation !== null) return;
    this.publish(scope, entry, { ...entry.state, connection });
  }

  private setConnectionForEpoch(
    scope: string,
    entry: ScopeEntry<TProjection>,
    epoch: number,
    connection: LiveConnectionState,
  ): void {
    if (!this.isCurrent(entry, epoch) || entry.operation !== null && connection !== "live") return;
    this.publish(scope, entry, { ...entry.state, connection });
  }

  private clearCursor(scope: string): void {
    try {
      this.cursorStore.clear(scope);
    } catch {
      // A failed optional persistence cleanup must not leave incremental state active.
    }
  }

  private publish(scope: string, entry: ScopeEntry<TProjection>, state: LiveProjectionState<TProjection>): void {
    entry.state = Object.freeze(state);
    try {
      this.options.onStateChange?.(scope, entry.state);
    } catch {
      // Presentation observers cannot affect live state correctness.
    }
  }
}

function emptyState<TProjection>(scope: string, connection: LiveConnectionState): LiveProjectionState<TProjection> {
  return {
    projection: null,
    subscriptionScope: scope,
    expectedSequence: null,
    schemaVersion: null,
    eventCursor: null,
    connection,
  };
}

function matchesExpectedEvent<TEvent>(
  state: LiveProjectionState<unknown>,
  scope: string,
  event: LiveOperationalEvent<TEvent>,
): boolean {
  return state.projection !== null
    && state.expectedSequence !== null
    && state.schemaVersion !== null
    && event.resourceScope === scope
    && event.schemaVersion === state.schemaVersion
    && event.sequence === state.expectedSequence;
}

function assertSnapshot<TProjection>(scope: string, snapshot: LiveProjectionSnapshot<TProjection>): void {
  if (!isNonEmptyString(snapshot.schemaVersion)) throw new LiveProjectionConfigurationError("Snapshot schema version is required.");
  if (!isSequence(snapshot.expectedSequence)) throw new LiveProjectionConfigurationError("Snapshot expected sequence is invalid.");
  if (snapshot.subscription.scope !== scope) throw new LiveProjectionConfigurationError("Snapshot subscription scope differs from its requested scope.");
  if (snapshot.subscription.authorizedTopics.some((topic: string): boolean => !isNonEmptyString(topic))) {
    throw new LiveProjectionConfigurationError("Snapshot contains an invalid authorized topic.");
  }
}

function isValidEvent<TEvent>(event: LiveOperationalEvent<TEvent> | null): event is LiveOperationalEvent<TEvent> {
  return event !== null
    && isNonEmptyString(event.resourceScope)
    && isNonEmptyString(event.schemaVersion)
    && isNonEmptyString(event.eventId)
    && isSequence(event.sequence);
}

function isSequence(value: number): boolean {
  return Number.isSafeInteger(value) && value >= 0;
}

function isNonEmptyString(value: string): boolean {
  return value.trim().length > 0;
}

function assertScope(scope: string): void {
  if (!isNonEmptyString(scope)) throw new LiveProjectionConfigurationError("Live projection scope is required.");
}

function safeAbort(subscription: AbortableSseSubscription): void {
  try {
    subscription.abort();
  } catch {
    // Abort cleanup is best-effort; the stream epoch still blocks callbacks.
  }
}
