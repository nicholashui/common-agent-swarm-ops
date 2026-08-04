import assert from "node:assert/strict";
import test from "node:test";

import {
  addAgentToSwarmDraft,
  createSwarmDraft,
  getSwarm,
  listSwarms,
} from "./product-swarms";

test("createSwarmDraft posts to /api/v1/swarms", async () => {
  const fetchImpl = async (
    input: RequestInfo | URL,
    init?: RequestInit,
  ): Promise<Response> => {
    assert.equal(String(input), "/api/v1/swarms");
    assert.equal(init?.method, "POST");
    return Response.json({
      swarm_id: "swarm_abc",
      revision: 0,
      status: "draft",
      name: "My draft",
    });
  };
  const result = await createSwarmDraft({
    name: "My draft",
    fetchImpl: fetchImpl as typeof fetch,
  });
  assert.equal(result.ok, true);
  if (result.ok) {
    assert.equal(result.swarmId, "swarm_abc");
    assert.equal(result.name, "My draft");
  }
});

test("addAgentToSwarmDraft fetches action, creates swarm, posts member", async () => {
  const calls: { url: string; method?: string; body?: string }[] = [];
  const fetchImpl = async (
    input: RequestInfo | URL,
    init?: RequestInit,
  ): Promise<Response> => {
    const url = String(input);
    calls.push({
      url,
      method: init?.method,
      body: typeof init?.body === "string" ? init.body : undefined,
    });
    if (url.includes("/commons/agents/") && (!init?.method || init.method === "GET")) {
      return Response.json({
        data: {
          id: "video.director",
          actions: [
            {
              id: "act_add_1",
              kind: "add_to_swarm",
              label: "Add to Swarm",
              eligible: true,
              resource_ref: "video.director",
            },
          ],
        },
        meta: { correlation_id: "c0" },
      });
    }
    if (url === "/api/v1/swarms" && init?.method === "POST") {
      return Response.json({
        swarm_id: "swarm_new1",
        revision: 0,
        status: "draft",
        name: "Draft with Director",
      });
    }
    if (url.includes("/members") && init?.method === "POST") {
      const body = JSON.parse(String(init.body)) as {
        action_reference_id: string;
        agent_id: string;
      };
      assert.equal(body.action_reference_id, "act_add_1");
      assert.equal(body.agent_id, "video.director");
      return Response.json({
        swarm_id: "swarm_new1",
        revision: 1,
        node_id: "node_video_director",
        member: {
          node_id: "node_video_director",
          agent_id: "video.director",
          agent_version: "current",
          pin_policy: "exact",
        },
      });
    }
    return Response.json({ error: { message: "unexpected" } }, { status: 500 });
  };

  const result = await addAgentToSwarmDraft("video.director", {
    swarmName: "Draft with Director",
    fetchImpl: fetchImpl as typeof fetch,
  });
  assert.equal(result.ok, true);
  if (result.ok) {
    assert.equal(result.swarmId, "swarm_new1");
    assert.equal(result.agentId, "video.director");
    assert.equal(result.nodeId, "node_video_director");
    assert.equal(result.createdSwarm, true);
  }
  assert.equal(calls.length, 3);
  assert.match(calls[0]!.url, /\/commons\/agents\/video\.director$/);
  assert.equal(calls[1]!.url, "/api/v1/swarms");
  assert.match(calls[2]!.url, /\/swarms\/swarm_new1\/members$/);
});

test("addAgentToSwarmDraft fails closed without eligible action", async () => {
  const fetchImpl = async (): Promise<Response> =>
    Response.json({
      data: { id: "x", actions: [] },
      meta: { correlation_id: "c" },
    });
  const result = await addAgentToSwarmDraft("x", {
    fetchImpl: fetchImpl as typeof fetch,
  });
  assert.equal(result.ok, false);
  if (!result.ok) {
    assert.match(result.message, /no eligible add_to_swarm/i);
  }
});

test("addAgentToSwarmDraft reuses swarmId without creating a second draft", async () => {
  const calls: string[] = [];
  const fetchImpl = async (
    input: RequestInfo | URL,
    init?: RequestInit,
  ): Promise<Response> => {
    const url = String(input);
    calls.push(`${init?.method ?? "GET"} ${url}`);
    if (url.includes("/commons/agents/")) {
      return Response.json({
        data: {
          id: "video.editor",
          actions: [
            {
              id: "act_add_2",
              kind: "add_to_swarm",
              eligible: true,
              resource_ref: "video.editor",
            },
          ],
        },
        meta: {},
      });
    }
    if (url.includes("/members")) {
      return Response.json({
        swarm_id: "swarm_existing",
        revision: 3,
        node_id: "node_video_editor",
        member: { agent_id: "video.editor" },
      });
    }
    return Response.json({ error: { message: "unexpected create" } }, { status: 500 });
  };
  const result = await addAgentToSwarmDraft("video.editor", {
    swarmId: "swarm_existing",
    swarmName: "Shared draft",
    fetchImpl: fetchImpl as typeof fetch,
  });
  assert.equal(result.ok, true);
  if (result.ok) {
    assert.equal(result.swarmId, "swarm_existing");
    assert.equal(result.createdSwarm, false);
    assert.equal(result.agentId, "video.editor");
  }
  assert.equal(calls.some((c) => c.includes("POST /api/v1/swarms") && !c.includes("members")), false);
  assert.ok(calls.some((c) => c.includes("/members")));
});

test("listSwarms maps Host draft items", async () => {
  const fetchImpl = async (
    input: RequestInfo | URL,
    init?: RequestInit,
  ): Promise<Response> => {
    assert.equal(String(input), "/api/v1/swarms");
    assert.equal(init?.method ?? "GET", "GET");
    return Response.json({
      items: [
        {
          id: "swarm_1",
          name: "Draft with Director",
          status: "draft",
          revision: 2,
          member_count: 2,
          last_run_id: null,
          updated_at: "2026-01-01T00:00:00+00:00",
          created_at: "2026-01-01T00:00:00+00:00",
        },
      ],
    });
  };
  const result = await listSwarms({ fetchImpl: fetchImpl as typeof fetch });
  assert.equal(result.ok, true);
  if (result.ok) {
    assert.equal(result.items.length, 1);
    assert.equal(result.items[0]!.id, "swarm_1");
    assert.equal(result.items[0]!.memberCount, 2);
    assert.equal(result.items[0]!.status, "draft");
  }
});

test("getSwarm maps members and nodes", async () => {
  const fetchImpl = async (input: RequestInfo | URL): Promise<Response> => {
    assert.match(String(input), /\/swarms\/swarm_1$/);
    return Response.json({
      id: "swarm_1",
      name: "Crew",
      status: "draft",
      revision: 1,
      members: [
        {
          node_id: "node_video_director",
          agent_id: "video.director",
          agent_version: "current",
        },
      ],
      nodes: [
        {
          id: "node_video_director",
          kind: "common_agent",
          common_agent: { id: "video.director", version: "current" },
        },
      ],
      brief: {
        brief_id: "brief_1",
        text: "wuxia brief",
        locale: "zh-Hant",
        scale_profile: "S1",
        archetype: "A",
      },
      spine: {
        workflow_id: "wf_video_spine_v1",
        status: "ready",
        mode: "stub",
        production_ready: false,
        note: "stub run · not production media",
        steps: [
          {
            id: "orchestrate",
            agent_id: "video.orchestrator",
            status: "queued",
            human_gate_required: false,
          },
        ],
        artifacts: {},
      },
      actions: [
        { id: "act_1", kind: "run_spine_step", label: "Run spine step (stub)" },
      ],
    });
  };
  const result = await getSwarm("swarm_1", {
    fetchImpl: fetchImpl as typeof fetch,
  });
  assert.equal(result.ok, true);
  if (result.ok) {
    assert.equal(result.swarm.name, "Crew");
    assert.equal(result.swarm.members[0]!.agentId, "video.director");
    assert.equal(result.swarm.nodes[0]!.agentId, "video.director");
    assert.equal(result.swarm.brief?.scaleProfile, "S1");
    assert.equal(result.swarm.spine?.workflowId, "wf_video_spine_v1");
    assert.equal(result.swarm.actions[0]!.kind, "run_spine_step");
  }
});
