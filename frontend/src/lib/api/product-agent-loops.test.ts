import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";

import {
  fetchAgentLoopInventory,
  fetchAgentLoopTools,
  fetchAgentLoopV3Policy,
  runAgentLoop,
  runSwarmMemberLoops,
  runWorkflowLoops,
} from "./product-agent-loops";

const here = dirname(fileURLToPath(import.meta.url));

test("fetchAgentLoopInventory maps inventory payload", async () => {
  const fetchImpl = async (input: RequestInfo | URL): Promise<Response> => {
    assert.equal(String(input), "/api/v1/agent-loops/inventory");
    return Response.json({
      total_agents: 114,
      loop_capable: 90,
      items: [
        { agent_id: "video.planner", loop_capable: true },
        { agent_id: "video.broken", loop_capable: false },
      ],
    });
  };
  const result = await fetchAgentLoopInventory({
    fetchImpl: fetchImpl as typeof fetch,
  });
  assert.equal(result.ok, true);
  if (result.ok) {
    assert.equal(result.totalAgents, 114);
    assert.equal(result.loopCapable, 90);
    assert.equal(result.items[0]?.agentId, "video.planner");
  }
});

test("runSwarmMemberLoops posts crew payload to swarm route", async () => {
  const fetchImpl = async (
    input: RequestInfo | URL,
    init?: RequestInit,
  ): Promise<Response> => {
    assert.equal(String(input), "/api/v1/swarms/swarm_1/agent-loops");
    assert.equal(init?.method, "POST");
    const body = JSON.parse(String(init?.body)) as {
      action_reference_id: string;
      goal?: string;
      agent_ids?: string[];
    };
    assert.equal(body.action_reference_id, "act_loops");
    assert.equal(body.goal, "Offline crew");
    assert.deepEqual(body.agent_ids, ["video.planner"]);
    return Response.json({
      crew: { passed: 1, failed: 0, completed: 1 },
    });
  };
  const result = await runSwarmMemberLoops("swarm_1", "act_loops", {
    fetchImpl: fetchImpl as typeof fetch,
    goal: "Offline crew",
    agentIds: ["video.planner"],
  });
  assert.equal(result.ok, true);
  if (result.ok) {
    assert.equal(result.passed, 1);
    assert.equal(result.completed, 1);
  }
});

test("runWorkflowLoops posts to DNA workflow offline loop route", async () => {
  const fetchImpl = async (
    input: RequestInfo | URL,
    init?: RequestInit,
  ): Promise<Response> => {
    assert.equal(
      String(input),
      "/api/v1/agent-loops/workflows/wf_video_spine_v1/run",
    );
    assert.equal(init?.method, "POST");
    const body = JSON.parse(String(init?.body)) as {
      goal: string;
      max_nodes: number;
      stop_on_failure: boolean;
    };
    assert.equal(body.goal, "YouTube short");
    assert.equal(body.max_nodes, 8);
    assert.equal(body.stop_on_failure, false);
    return Response.json({
      ok: true,
      workflow_id: "wf_video_spine_v1",
      passed: 3,
      failed: 1,
      completed: 4,
    });
  };
  const result = await runWorkflowLoops("wf_video_spine_v1", "YouTube short", {
    fetchImpl: fetchImpl as typeof fetch,
    maxNodes: 8,
  });
  assert.equal(result.ok, true);
  if (result.ok) {
    assert.equal(result.workflowId, "wf_video_spine_v1");
    assert.equal(result.passed, 3);
    assert.equal(result.failed, 1);
    assert.equal(result.completed, 4);
  }
});

test("fetchAgentLoopTools maps catalog", async () => {
  const fetchImpl = async (input: RequestInfo | URL): Promise<Response> => {
    assert.equal(String(input), "/api/v1/agent-loops/tools");
    return Response.json({
      media_live_env: false,
      tools: [{ tool_id: "media.sora", active_mode: "stub" }],
    });
  };
  const result = await fetchAgentLoopTools({
    fetchImpl: fetchImpl as typeof fetch,
  });
  assert.equal(result.ok, true);
  if (result.ok) {
    assert.equal(result.mediaLiveEnv, false);
    assert.equal(result.tools[0]?.toolId, "media.sora");
    assert.equal(result.tools[0]?.activeMode, "stub");
  }
});

test("fetchAgentLoopV3Policy and runAgentLoop map v3 fields", async () => {
  const fetchImpl = async (
    input: RequestInfo | URL,
    init?: RequestInit,
  ): Promise<Response> => {
    const url = String(input);
    if (url.includes("/v3/policy")) {
      return Response.json({
        patterns: ["Cynefin", "AAR"],
        critic_modes: ["standard"],
        activation_policy: { production_media: false },
      });
    }
    assert.match(url, /\/agent-loops\/agents\/video\.planner\/run/);
    assert.equal(init?.method, "POST");
    return Response.json({
      agent_id: "video.planner",
      status: "ok",
      v3: { phase0: { cynefin: { domain: "complicated" } } },
    });
  };
  const pol = await fetchAgentLoopV3Policy({
    fetchImpl: fetchImpl as typeof fetch,
  });
  assert.equal(pol.ok, true);
  if (pol.ok) {
    assert.equal(pol.productionMedia, false);
    assert.ok(pol.patterns.includes("Cynefin"));
  }
  const run = await runAgentLoop("video.planner", "Plan short", {
    fetchImpl: fetchImpl as typeof fetch,
  });
  assert.equal(run.ok, true);
  if (run.ok) {
    assert.equal(run.hasV3, true);
    assert.equal(run.cynefinDomain, "complicated");
  }
});

test("Execute live swarm canvas wires member + DNA spine offline loop controls", () => {
  const boundPath = join(
    here,
    "../../components/screen/BoundScreenHome.tsx",
  );
  const source = readFileSync(boundPath, "utf8");
  assert.match(source, /Run member loops \(offline\)/);
  assert.match(source, /Run DNA spine loops \(offline\)/);
  assert.match(source, /runSwarmMemberLoops/);
  assert.match(source, /runWorkflowLoops/);
  assert.match(source, /wf_video_spine_v1/);
  assert.match(source, /not production media/);
  assert.match(source, /offline · not production media/);
});
