import assert from "node:assert/strict";
import test from "node:test";

import {
  classifyAnnounce,
  isGovernedStubMessage,
  performScreenAction,
  type ScreenUiAction,
} from "./screen-actions";
import type { InteractionRuntime } from "./interaction-runtime";

function mockRuntime(
  overrides: Partial<InteractionRuntime> = {},
): InteractionRuntime {
  const calls: string[] = [];
  const base = {
    status: { kind: "idle" as const, message: "" },
    busy: false,
    api: {} as InteractionRuntime["api"],
    operator: {} as InteractionRuntime["operator"],
    setInfo: (m: string) => {
      calls.push(`info:${m}`);
    },
    setError: (m: string) => {
      calls.push(`error:${m}`);
    },
    setSuccess: (m: string) => {
      calls.push(`success:${m}`);
    },
    clearStatus: () => {
      calls.push("clear");
    },
    replaceScreen: () => {
      calls.push("replace");
    },
    patchScreen: () => {
      calls.push("patch");
      return {} as never;
    },
    requestGenerated: async () => false,
    inspectRun: async () => false,
    loadApproval: async () => false,
    decideApproval: async () => false,
    refreshContext: async () => false,
    retrieveMemory: async (q: string) => {
      calls.push(`memory:${q}`);
      return true;
    },
    createRun: async () => null,
    dispatchRun: async () => false,
    createAndDispatchRun: async (wf: string) => {
      calls.push(`run:${wf}`);
      return true;
    },
    runEvaluation: async () => {
      calls.push("eval");
      return true;
    },
    loadTopology: async () => false,
    ...overrides,
    _calls: calls,
  };
  return base as unknown as InteractionRuntime & { _calls: string[] };
}

test("isGovernedStubMessage detects authorized stubs", () => {
  assert.equal(
    isGovernedStubMessage("Export requires an authorized export action."),
    true,
  );
  assert.equal(isGovernedStubMessage("Layout applied locally."), false);
});

test("classifyAnnounce maps eval campaign and layout", () => {
  assert.equal(
    classifyAnnounce("Run Batch Eval Campaign requires an authorized eval action.").kind,
    "eval.run_campaign",
  );
  assert.equal(
    classifyAnnounce("Auto layout is local-only feedback.").kind,
    "local.layout",
  );
  assert.equal(
    classifyAnnounce("Export requires an authorized export action.").kind,
    "governed.fail_closed",
  );
});

test("performScreenAction runs evaluation and fail-closed", async () => {
  const runtime = mockRuntime() as InteractionRuntime & { _calls: string[] };
  const ok = await performScreenAction(runtime, { kind: "eval.run_campaign" });
  assert.equal(ok, true);
  assert.ok(runtime._calls.includes("eval"));

  const denied = await performScreenAction(runtime, {
    kind: "governed.fail_closed",
    message: "Merge requires authorized governance.",
  });
  assert.equal(denied, false);
  assert.ok(runtime._calls.some((c) => c.startsWith("error:")));
});

test("performScreenAction knowledge search", async () => {
  const runtime = mockRuntime() as InteractionRuntime & { _calls: string[] };
  const ok = await performScreenAction(runtime, {
    kind: "knowledge.search",
    query: "policy",
  });
  assert.equal(ok, true);
  assert.ok(runtime._calls.includes("memory:policy"));
});

test("ScreenUiAction kinds are structured", () => {
  const actions: ScreenUiAction[] = [
    { kind: "feedback", message: "ok" },
    { kind: "local.pause_swarm", swarmId: "s1" },
    { kind: "canvas.run", workflowId: "wf", version: "1" },
    { kind: "commons.rollout_ab", agentId: "video.accessibility" },
    { kind: "commons.rollout_safe", agentId: "video.accessibility" },
  ];
  assert.equal(actions.length, 5);
});

test("performScreenAction rollout fails closed without host", async () => {
  const runtime = mockRuntime() as InteractionRuntime & { _calls: string[] };
  const prevFetch = globalThis.fetch;
  globalThis.fetch = (async () => {
    throw new Error("offline");
  }) as typeof fetch;
  try {
    const ok = await performScreenAction(runtime, {
      kind: "commons.rollout_ab",
      agentId: "video.accessibility",
    });
    assert.equal(ok, false);
    assert.ok(runtime._calls.some((c) => c.startsWith("error:")));
  } finally {
    globalThis.fetch = prevFetch;
  }
});
