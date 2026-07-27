import assert from "node:assert/strict";
import test from "node:test";

import { logoutSession } from "./logout";

test("logoutSession posts to /api/auth/logout and returns redirect", async () => {
  const calls: { url: string; init?: RequestInit }[] = [];
  const fetchImpl = async (
    input: RequestInfo | URL,
    init?: RequestInit,
  ): Promise<Response> => {
    calls.push({ url: String(input), init });
    return new Response(JSON.stringify({ ok: true, redirectTo: "/login" }), {
      status: 200,
      headers: { "content-type": "application/json" },
    });
  };

  const result = await logoutSession(fetchImpl as typeof fetch);
  assert.equal(result.ok, true);
  if (result.ok) {
    assert.equal(result.redirectTo, "/login");
  }
  assert.equal(calls.length, 1);
  assert.equal(calls[0]?.url, "/api/auth/logout");
  assert.equal(calls[0]?.init?.method, "POST");
  assert.equal(calls[0]?.init?.credentials, "same-origin");
});

test("logoutSession fails closed on non-OK response", async () => {
  const fetchImpl = async (): Promise<Response> =>
    new Response("nope", { status: 500 });
  const result = await logoutSession(fetchImpl as typeof fetch);
  assert.equal(result.ok, false);
  if (!result.ok) {
    assert.match(result.message, /sign out/i);
  }
});
