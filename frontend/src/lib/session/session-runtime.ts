import type { SessionSafeCache } from "./session-safe-cache";

export {
  BrowserSessionSafeCache,
  type AuthorizedProjectionRecord,
  type SessionSafeCache,
  type SessionSafeCacheAllowlistEntry,
  type SessionSafeCacheOptions,
  type SessionStorageLike,
} from "./session-safe-cache";

export interface ProjectionStateStore {
  clearRestSnapshot(): void;
  clearIncrementalState(): void;
}

export interface CommandIntentPresentationStore {
  clearCommandIntentPresentation(): void;
}

export interface AbortableSseSubscription {
  abort(): void;
}

export interface StreamRegistration {
  unregister(): void;
  canApplyOperationalEvent(): boolean;
}

export class SessionTransitionCoordinator {
  private readonly streams = new Map<AbortableSseSubscription, number>();
  private readonly projectionStores = new Set<ProjectionStateStore>();
  private readonly caches = new Set<SessionSafeCache>();
  private readonly commandStores = new Set<CommandIntentPresentationStore>();
  private epoch = 0;
  private phase: "ready" | "transitioning" = "ready";

  public registerProjectionState(store: ProjectionStateStore): () => void {
    this.projectionStores.add(store);
    return (): void => { this.projectionStores.delete(store); };
  }

  public registerCache(cache: SessionSafeCache): () => void {
    this.caches.add(cache);
    return (): void => { this.caches.delete(cache); };
  }

  public registerCommandIntentPresentation(store: CommandIntentPresentationStore): () => void {
    this.commandStores.add(store);
    return (): void => { this.commandStores.delete(store); };
  }

  public registerSseSubscription(subscription: AbortableSseSubscription): StreamRegistration {
    const registeredEpoch = this.epoch;
    this.streams.set(subscription, registeredEpoch);
    return {
      unregister: (): void => { this.streams.delete(subscription); },
      canApplyOperationalEvent: (): boolean => this.phase === "ready" && this.streams.get(subscription) === registeredEpoch,
    };
  }

  public beginSessionTransition(): void {
    this.phase = "transitioning";
    this.epoch += 1;
    for (const subscription of this.streams.keys()) {
      try { subscription.abort(); } catch { /* Cleanup must continue after a failed abort. */ }
    }
    this.streams.clear();
    for (const store of this.projectionStores) {
      store.clearRestSnapshot();
      store.clearIncrementalState();
    }
    for (const cache of this.caches) cache.clearForSessionTransition();
    for (const store of this.commandStores) store.clearCommandIntentPresentation();
  }

  public authorizeNextProjection(): void {
    this.phase = "ready";
  }

  public canRenderAuthorizedProjection(): boolean {
    return this.phase === "ready";
  }
}
