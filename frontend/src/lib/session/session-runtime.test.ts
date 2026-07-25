import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

import { BrowserSessionSafeCache, SessionTransitionCoordinator } from "./session-runtime";

class MemoryStorage {
  private readonly values = new Map<string, string>();
  public getItem(key: string): string | null { return this.values.get(key) ?? null; }
  public setItem(key: string, value: string): void { this.values.set(key, value); }
  public removeItem(key: string): void { this.values.delete(key); }
  public get size(): number { return this.values.size; }
}

test("clears session state in abort-before-render order and rejects stale stream events", () => {
  const steps: string[] = [];
  const coordinator = new SessionTransitionCoordinator();
  coordinator.registerProjectionState({ clearRestSnapshot: (): void => { steps.push("rest"); }, clearIncrementalState: (): void => { steps.push("incremental"); } });
  coordinator.registerCache({ clearForSessionTransition: (): void => { steps.push("cache"); } });
  coordinator.registerCommandIntentPresentation({ clearCommandIntentPresentation: (): void => { steps.push("commands"); } });
  const subscription = { abort: (): void => { steps.push("abort"); } };
  const oldStream = coordinator.registerSseSubscription(subscription);
  assert.equal(oldStream.canApplyOperationalEvent(), true);
  coordinator.beginSessionTransition();
  assert.deepEqual(steps, ["abort", "rest", "incremental", "cache", "commands"]);
  assert.equal(oldStream.canApplyOperationalEvent(), false);
  assert.equal(coordinator.canRenderAuthorizedProjection(), false);
  coordinator.authorizeNextProjection();
  assert.equal(coordinator.canRenderAuthorizedProjection(), true);
  assert.equal(coordinator.registerSseSubscription({ abort: (): void => undefined }).canApplyOperationalEvent(), true);
});

test("clears every allowlisted persisted cache entry and rejects unallowlisted entries", () => {
  const persistence = new MemoryStorage();
  const cache = new BrowserSessionSafeCache({
    sessionVersion: "session-a",
    allowlist: [{ key: "resume", projectionFields: ["state"] }],
    persistence,
  });
  cache.write("resume", { projection: { state: "returned" }, eventCursor: "cursor-1" });
  assert.equal(cache.read("resume")?.eventCursor, "cursor-1");
  assert.throws(() => cache.write("secret", { projection: {}, eventCursor: null }), /allowlisted/);
  cache.clearForSessionTransition();
  assert.equal(cache.read("resume"), null);
  assert.equal(persistence.size, 0);
});


test("configures same-origin API rewriting and required browser security headers", async () => {
  const config = await readFile(new URL("../../../next.config.mjs", import.meta.url), "utf8");
  assert.match(config, /source: "\/api\/v1\/:path\*"/);
  assert.match(config, /connect-src 'self'/);
  assert.match(config, /base-uri 'self'/);
  assert.match(config, /frame-ancestors 'none'/);
  assert.match(config, /object-src 'none'/);
  assert.match(config, /upgrade-insecure-requests/);
  assert.match(config, /Referrer-Policy", "no-referrer/);
  assert.match(config, /X-Content-Type-Options", "nosniff/);
  assert.match(config, /Cache-Control", value: "no-store/);
});
