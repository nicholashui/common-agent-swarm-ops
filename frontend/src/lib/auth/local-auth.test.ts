import assert from "node:assert/strict";
import test from "node:test";

import {
  clearLocalAuthStateForTests,
  consumePasswordResetToken,
  createDemoSessionClaims,
  createPasswordResetToken,
  createSessionClaims,
  decodeSessionCookie,
  encodeSessionCookie,
  verifyLocalPassword,
} from "./local-auth";

test("verifies built-in local users and rejects invalid passwords", () => {
  clearLocalAuthStateForTests();
  assert.equal(verifyLocalPassword("demo@local", "demo")?.email, "demo@local");
  assert.equal(verifyLocalPassword("ops@local", "ops")?.workspaceLabel, "Local ops workspace");
  assert.equal(verifyLocalPassword("demo@local", "wrong"), null);
  assert.equal(verifyLocalPassword("missing@local", "demo"), null);
});

test("encodes signed session cookies and rejects tampering or expiry", () => {
  clearLocalAuthStateForTests();
  const claims = createSessionClaims({
    mode: "user",
    email: "ops@local",
    workspaceLabel: "Local ops workspace",
    rememberDevice: true,
  });
  const cookie = encodeSessionCookie(claims);
  assert.deepEqual(decodeSessionCookie(cookie)?.email, "ops@local");
  assert.equal(decodeSessionCookie(`${cookie}x`), null);

  const expired = createSessionClaims(
    {
      mode: "demo",
      email: "demo@local",
      workspaceLabel: "Demo workspace",
    },
    Date.now() - 48 * 60 * 60 * 1000,
  );
  assert.equal(decodeSessionCookie(encodeSessionCookie(expired)), null);
});

test("issues and consumes local password reset tokens", () => {
  clearLocalAuthStateForTests();
  const issued = createPasswordResetToken("demo@local");
  assert.ok(issued);
  assert.equal(createPasswordResetToken("missing@local"), null);
  assert.equal(consumePasswordResetToken(issued.token, "new-pass"), true);
  assert.equal(verifyLocalPassword("demo@local", "demo"), null);
  assert.equal(verifyLocalPassword("demo@local", "new-pass")?.email, "demo@local");
  assert.equal(consumePasswordResetToken(issued.token, "again"), false);
});

test("builds demo claims for local preview sessions", () => {
  clearLocalAuthStateForTests();
  const demo = createDemoSessionClaims();
  assert.equal(demo.mode, "demo");
  assert.equal(demo.email, "demo@local");
});
