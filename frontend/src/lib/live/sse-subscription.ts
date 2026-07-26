import { GENERATED_API_BASE_PATH } from "../api/generated";
import type { AbortableSseSubscription } from "../session/session-runtime";
import type {
  AuthorizedLiveSubscriptionFactory,
  AuthorizedSubscriptionContext,
  LiveSubscriptionHandlers,
} from "./LiveProjectionController";

export const AUTHORIZED_SSE_STREAM_PATH = `${GENERATED_API_BASE_PATH}/events/stream` as const;

export interface SseSubscriptionFactoryOptions {
  /**
   * Returns the last authorized event id for the subscription scope so reconnects
   * can send `Last-Event-ID` (frontend_redesign 8.3 / backend_redesign 1.17).
   */
  readonly getLastEventId?: (scope: string) => string | null;
  /** Override for tests; defaults to same-origin `/api/v1/events/stream`. */
  readonly streamPath?: string;
  /** Injected EventSource constructor (browser global by default). */
  readonly eventSourceFactory?: (url: string) => EventSourceLike;
}

export interface EventSourceLike {
  readonly readyState: number;
  onopen: ((event: Event) => void) | null;
  onerror: ((event: Event) => void) | null;
  onmessage: ((event: MessageEvent) => void) | null;
  addEventListener(type: string, listener: (event: MessageEvent) => void): void;
  close(): void;
}

/**
 * Builds an authorized SSE subscription factory for LiveProjectionController.
 *
 * The stream is observation-only. Sequence validation and REST resync remain in
 * LiveProjectionController; this adapter only opens the authorized transport and
 * resumes with Last-Event-ID when a prior cursor exists.
 */
export function createAuthorizedSseSubscriptionFactory(
  options: SseSubscriptionFactoryOptions = {},
): AuthorizedLiveSubscriptionFactory {
  const streamPath = options.streamPath ?? AUTHORIZED_SSE_STREAM_PATH;
  assertSameOriginVersionedStreamPath(streamPath);
  const eventSourceFactory = options.eventSourceFactory ?? defaultEventSourceFactory;
  const getLastEventId = options.getLastEventId;

  return {
    subscribe(context: AuthorizedSubscriptionContext, handlers: LiveSubscriptionHandlers): AbortableSseSubscription {
      assertScope(context.scope);
      const url = buildSseUrl(streamPath, context, getLastEventId?.(context.scope) ?? null);
      let closed = false;
      let source: EventSourceLike;
      try {
        source = eventSourceFactory(url);
      } catch {
        handlers.onStale();
        return { abort: (): void => undefined };
      }

      source.onopen = (): void => {
        if (!closed) handlers.onConnected();
      };
      source.onerror = (): void => {
        if (closed) return;
        if (source.readyState === 2 /* CLOSED */) {
          handlers.onStale();
          return;
        }
        handlers.onDisconnected();
      };
      source.onmessage = (event: MessageEvent): void => {
        if (closed) return;
        handlers.onOperationalEvent(parseSsePayload(event));
      };
      source.addEventListener("operational", (event: MessageEvent): void => {
        if (closed) return;
        handlers.onOperationalEvent(parseSsePayload(event));
      });

      return {
        abort: (): void => {
          if (closed) return;
          closed = true;
          try {
            source.close();
          } catch {
            /* best-effort close */
          }
        },
      };
    },
  };
}

function buildSseUrl(
  streamPath: string,
  context: AuthorizedSubscriptionContext,
  lastEventId: string | null,
): string {
  const params = new URLSearchParams();
  params.set("scope", context.scope);
  for (const topic of context.authorizedTopics) {
    if (topic.trim().length > 0) params.append("topic", topic);
  }
  // Opaque sequence context travels as a single JSON blob; server re-authorizes.
  params.set("sequence_context", JSON.stringify(context.sequenceContext));
  if (lastEventId !== null && lastEventId.trim().length > 0) {
    params.set("last_event_id", lastEventId.trim());
  }
  const query = params.toString();
  // Prefer Last-Event-ID query for EventSource (cannot set custom headers natively).
  // Controllers that wrap fetch/SSE may also read this as Last-Event-ID.
  return `${streamPath}?${query}`;
}

function parseSsePayload(event: MessageEvent): unknown {
  const data = event.data;
  if (typeof data !== "string") return data;
  try {
    return JSON.parse(data) as unknown;
  } catch {
    return { raw: data, eventId: typeof event.lastEventId === "string" ? event.lastEventId : undefined };
  }
}

function defaultEventSourceFactory(url: string): EventSourceLike {
  if (typeof EventSource === "undefined") {
    throw new Error("EventSource is not available in this runtime.");
  }
  // Native EventSource cannot set Idempotency or custom headers; Last-Event-ID is
  // conveyed via last_event_id query when resuming (see buildSseUrl).
  return new EventSource(url, { withCredentials: true }) as EventSourceLike;
}

function assertSameOriginVersionedStreamPath(path: string): void {
  if (
    !path.startsWith(`${GENERATED_API_BASE_PATH}/`)
    || path.startsWith("//")
    || /^[a-z][a-z\d+.-]*:/i.test(path)
  ) {
    throw new Error("SSE subscriptions must use generated same-origin /api/v1 paths.");
  }
}

function assertScope(scope: string): void {
  if (typeof scope !== "string" || scope.trim().length === 0) {
    throw new Error("An authorized subscription scope is required.");
  }
}
