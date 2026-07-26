import assert from "node:assert/strict";
import test from "node:test";

import {
  AUTHORIZED_SSE_STREAM_PATH,
  createAuthorizedSseSubscriptionFactory,
  type EventSourceLike,
} from "./sse-subscription";

class FakeEventSource implements EventSourceLike {
  public static lastUrl = "";
  public readyState = 0;
  public onopen: ((event: Event) => void) | null = null;
  public onerror: ((event: Event) => void) | null = null;
  public onmessage: ((event: MessageEvent) => void) | null = null;
  private readonly listeners = new Map<string, Array<(event: MessageEvent) => void>>();
  public closed = false;

  public constructor(url: string) {
    FakeEventSource.lastUrl = url;
  }

  public addEventListener(type: string, listener: (event: MessageEvent) => void): void {
    const list = this.listeners.get(type) ?? [];
    list.push(listener);
    this.listeners.set(type, list);
  }

  public close(): void {
    this.closed = true;
    this.readyState = 2;
  }

  public emitOpen(): void {
    this.readyState = 1;
    this.onopen?.(new Event("open"));
  }

  public emitMessage(data: string, lastEventId = ""): void {
    const event = { data, lastEventId } as MessageEvent;
    this.onmessage?.(event);
  }
}

test("SSE factory opens only same-origin /api/v1/events/stream with scope topics", (): void => {
  const factory = createAuthorizedSseSubscriptionFactory({
    eventSourceFactory: (url: string): EventSourceLike => new FakeEventSource(url),
  });
  const states: string[] = [];
  const events: unknown[] = [];
  const subscription = factory.subscribe(
    {
      scope: "run:run-1",
      authorizedTopics: ["run.status", "run.recovery"],
      sequenceContext: { expected_sequence: 4 },
    },
    {
      onConnected: (): void => {
        states.push("connected");
      },
      onDisconnected: (): void => {
        states.push("disconnected");
      },
      onStale: (): void => {
        states.push("stale");
      },
      onOperationalEvent: (event: unknown): void => {
        events.push(event);
      },
    },
  );

  assert.match(FakeEventSource.lastUrl, new RegExp(`^${AUTHORIZED_SSE_STREAM_PATH}\\?`));
  assert.match(FakeEventSource.lastUrl, /scope=run%3Arun-1/);
  assert.match(FakeEventSource.lastUrl, /topic=run\.status/);
  assert.match(FakeEventSource.lastUrl, /topic=run\.recovery/);
  assert.doesNotMatch(FakeEventSource.lastUrl, /last_event_id=/);
  subscription.abort();
});

test("SSE factory resumes with last_event_id as Last-Event-ID recovery token", (): void => {
  const factory = createAuthorizedSseSubscriptionFactory({
    getLastEventId: (scope: string): string | null => (scope === "run:run-2" ? "evt-42" : null),
    eventSourceFactory: (url: string): EventSourceLike => new FakeEventSource(url),
  });
  factory.subscribe(
    {
      scope: "run:run-2",
      authorizedTopics: ["run.status"],
      sequenceContext: { cursor: "opaque" },
    },
    {
      onConnected: (): void => undefined,
      onDisconnected: (): void => undefined,
      onStale: (): void => undefined,
      onOperationalEvent: (): void => undefined,
    },
  );
  assert.match(FakeEventSource.lastUrl, /last_event_id=evt-42/);
  assert.match(FakeEventSource.lastUrl, /Last-Event-ID|last_event_id/i);
});

test("SSE factory rejects non-/api/v1 stream paths", (): void => {
  assert.throws(
    (): void => {
      createAuthorizedSseSubscriptionFactory({ streamPath: "/api/events/stream" });
    },
    /\/api\/v1/,
  );
  assert.throws(
    (): void => {
      createAuthorizedSseSubscriptionFactory({ streamPath: "https://evil.example/api/v1/events/stream" });
    },
    /\/api\/v1/,
  );
});
