"""Host agent loop fleet inventory + offline run."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Any, cast

import pytest
from fastapi.testclient import TestClient
from httpx import Response

from app.api.v1.dependencies import AuthenticatedRequestContext, get_authenticated_request_context
from app.api.v1.product_facade import reset_product_facade_for_tests
from app.api.v1.product_facade_store import ProductFacadeStore
from app.main import create_app
from app.models.identifiers import ActorId, CorrelationId, OrganizationId
from app.video.agent_loop_service import AgentLoopService, reset_agent_loop_service_for_tests

ORG_ID = OrganizationId("org-loops")
CORRELATION_ID = CorrelationId("corr-loops")


def body(response: Response) -> dict[str, Any]:
    payload = cast(dict[str, Any], response.json())
    if "data" in payload and "meta" in payload:
        return cast(dict[str, Any], payload["data"])
    return payload


@pytest.fixture
def client() -> Iterator[TestClient]:
    reset_product_facade_for_tests()
    reset_agent_loop_service_for_tests()
    application = create_app()
    context = AuthenticatedRequestContext(
        tenant_id=ORG_ID,
        actor_id=ActorId("loop-actor"),
        correlation_id=CORRELATION_ID,
    )
    application.dependency_overrides[get_authenticated_request_context] = lambda: context
    with TestClient(application) as test_client:
        yield test_client
    application.dependency_overrides.clear()
    reset_product_facade_for_tests()
    reset_agent_loop_service_for_tests()


def test_inventory_lists_pack_agents(client: TestClient) -> None:
    inv = body(client.get("/api/v1/agent-loops/inventory"))
    assert inv["total_agents"] >= 50
    assert inv["loop_capable"] >= 1
    assert inv["activation_policy"]["production_media"] is False
    assert any(i.get("agent_id") == "video.planner" for i in inv["items"])


def test_run_single_agent_loop(client: TestClient) -> None:
    result = body(
        client.post(
            "/api/v1/agent-loops/agents/video.planner/run",
            json={"goal": "Plan a 90s YouTube wuxia short"},
        )
    )
    assert result.get("agent_id") == "video.planner"
    assert "l1" in result or result.get("ok") is False
    # Default enable_v3 attaches cognitive envelope
    assert "v3" in result
    assert result["v3"]["phase0"]["cynefin"]["domain"] in {
        "simple",
        "complicated",
        "complex",
        "chaotic",
    }
    assert result["v3"]["aar"]["what_next"]
    assert result["v3"]["critic"]["modes"]
    # Production flags rejected
    denied = client.post(
        "/api/v1/agent-loops/agents/video.planner/run",
        json={"goal": "x", "allow_production": True},
    )
    assert denied.status_code in {403, 400}


def test_agent_loop_v3_policy_patterns_and_fast_path(client: TestClient) -> None:
    pol = body(client.get("/api/v1/agent-loops/v3/policy"))
    assert pol["activation_policy"]["production_media"] is False
    assert "Cynefin" in pol["patterns"]
    assert "standard" in pol["critic_modes"]

    # Seed a successful pattern then similar goal can match
    first = body(
        client.post(
            "/api/v1/agent-loops/agents/video.planner/run",
            json={
                "goal": "Plan a short social video for product launch stub tools",
                "enable_v3": True,
                "critic_modes": ["standard", "red_team"],
                "cynefin_override": "simple",
            },
        )
    )
    assert first.get("v3")
    assert first["v3"]["phase0"]["cynefin"]["domain"] == "simple"
    assert first["v3"]["pattern_recorded"]

    patterns = body(client.get("/api/v1/agent-loops/v3/patterns"))
    assert len(patterns["items"]) >= 1

    second = body(
        client.post(
            "/api/v1/agent-loops/agents/video.planner/run",
            json={
                "goal": "Plan a short social video for product launch stub tools again",
                "enable_v3": True,
                "enable_fast_path": True,
                "cynefin_override": "simple",
            },
        )
    )
    assert second.get("v3")
    # May or may not hit fast path depending on token overlap; envelope always present
    assert second["v3"]["step_count"] >= 1
    assert "Premortem" in second["v3"]["patterns_used"]

    # Explicit disable v3 keeps classic payload without envelope
    classic = body(
        client.post(
            "/api/v1/agent-loops/agents/video.planner/run",
            json={"goal": "Classic loop without v3", "enable_v3": False},
        )
    )
    assert classic.get("agent_id") == "video.planner"
    assert "v3" not in classic


def test_tools_memory_critiques_and_fleet_sample(client: TestClient) -> None:
    tools = body(client.get("/api/v1/agent-loops/tools"))
    assert "tools" in tools
    assert tools["policy"]["default"] == "stub"
    assert any(t.get("tool_id") == "media.sora" for t in tools["tools"])

    run = body(
        client.post(
            "/api/v1/agent-loops/agents/video.planner/run",
            json={"goal": "Plan social video with stub tools"},
        )
    )
    assert "tool_invocations" in run
    assert run["tool_invocations"]
    assert run["tool_invocations"][0].get("mode") in {"stub", "live_blocked", "denied"}

    mem = body(client.get("/api/v1/agent-loops/memory"))
    assert isinstance(mem["items"], list)
    assert len(mem["items"]) >= 1

    sample = body(
        client.post(
            "/api/v1/agent-loops/fleet-sample",
            json={"goal": "Fleet sample offline loops", "limit": 3},
        )
    )
    assert sample["completed"] == 3
    assert sample["passed"] + sample["failed"] == 3


def test_workflow_loops_spine_dna(client: TestClient) -> None:
    listed = body(client.get("/api/v1/agent-loops/workflows"))
    assert listed["count"] >= 1
    assert any(i.get("workflow_id") == "wf_video_spine_v1" for i in listed["items"])
    run = body(
        client.post(
            "/api/v1/agent-loops/workflows/wf_video_spine_v1/run",
            json={
                "goal": "YouTube wuxia short film production brief",
                "max_nodes": 4,
                "stop_on_failure": False,
            },
        )
    )
    assert run["workflow_id"] == "wf_video_spine_v1"
    assert run["completed"] >= 1
    assert "project_memory" in run
    assert run["activation_policy"]["production_media"] is False


def test_run_crew_and_swarm_member_loops(client: TestClient) -> None:
    crew = body(
        client.post(
            "/api/v1/agent-loops/crew",
            json={
                "goal": "Video production brief for crew loops",
                "agent_ids": ["video.planner", "video.orchestrator"],
            },
        )
    )
    assert crew["completed"] == 2
    assert crew["passed"] + crew["failed"] == 2
    assert crew.get("mode") == "sequential"

    parallel = body(
        client.post(
            "/api/v1/agent-loops/crew",
            json={
                "goal": "Parallel offline crew loops",
                "agent_ids": ["video.planner", "video.orchestrator"],
                "parallel": True,
                "max_workers": 2,
            },
        )
    )
    assert parallel["completed"] == 2
    assert parallel.get("mode") == "parallel_bounded"
    assert parallel["passed"] + parallel["failed"] == 2

    mat = body(
        client.post(
            "/api/v1/composer/materialize",
            json={"goal": "YouTube video production brief for member loops"},
        )
    )
    swarm_id = mat["swarm_id"]
    detail = body(client.get(f"/api/v1/swarms/{swarm_id}"))
    actions = {a["kind"]: a["id"] for a in detail["actions"]}
    assert "run_member_loops" in actions
    # Limit to two agents for speed
    loops = body(
        client.post(
            f"/api/v1/swarms/{swarm_id}/agent-loops",
            json={
                "action_reference_id": actions["run_member_loops"],
                "agent_ids": ["video.planner", "video.producer"],
            },
        )
    )
    assert loops["swarm_id"] == swarm_id
    assert loops["crew"]["completed"] == 2


def test_memory_critiques_and_tool_invocations_after_run(client: TestClient) -> None:
    body(
        client.post(
            "/api/v1/agent-loops/agents/video.planner/run",
            json={"goal": "Persist memory and tool log for planner loop"},
        )
    )
    mem = body(client.get("/api/v1/agent-loops/memory"))
    assert len(mem["items"]) >= 1
    assert "run_id" in mem["items"][-1]

    critiques = body(client.get("/api/v1/agent-loops/critiques"))
    assert "items" in critiques

    tools_log = body(client.get("/api/v1/agent-loops/tool-invocations"))
    assert "items" in tools_log
    # When façade persist is on, tool JSONL should have at least one row
    if tools_log["items"]:
        assert tools_log["items"][-1].get("agent_id") == "video.planner"


def test_tool_catalog_never_claims_live_on_agent_loop_surface(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Invalid honesty: catalog must not claim live while invoke stays live_blocked."""
    from app.video.tool_activation import HostToolRegistry

    monkeypatch.setenv("CASOPS_MEDIA_LIVE", "1")
    reg = HostToolRegistry()
    catalog = reg.list_catalog()
    assert catalog["media_live_env"] is True
    assert catalog["policy"]["default"] == "stub"
    assert catalog["policy"]["production_media"] is False
    sora = next(t for t in catalog["tools"] if t["tool_id"] == "media.sora")
    assert sora["active_mode"] in {"stub", "live_blocked"}
    assert sora["live_allowed"] is False
    # Real invoke path: never unrestricted live media on this surface
    blocked = reg.invoke("media.sora", agent_id="video.planner", allow_live=True)
    assert blocked.ok is False
    assert blocked.mode in {"live_blocked", "denied"}
    monkeypatch.delenv("CASOPS_MEDIA_LIVE", raising=False)
    catalog_off = HostToolRegistry().list_catalog()
    assert catalog_off["media_live_env"] is False
    assert catalog_off["policy"]["production_media"] is False


def test_durable_loop_memory_and_tools_rehydrate_across_service_instances(
    tmp_path: Path,
) -> None:
    """Criterion 2: fresh AgentLoopService on same ProductFacadeStore keeps org memory/tools."""
    store = ProductFacadeStore(root=tmp_path / "facade")
    org = "org-rehydrate-loops"
    first = AgentLoopService(store=store, persist=True)
    run = first.run(
        "video.planner",
        organization_id=org,
        goal="Durable rehydrate must see this planner loop",
    )
    assert run.get("run_id"), run
    assert first.project_memory(org), "first instance must record project memory"
    assert (
        first.inventory_summary().get("activation_policy", {}).get("production_media")
        is False
    )
    # New instance, no shared in-memory dicts — only the durable store
    second = AgentLoopService(store=store, persist=True)
    mem = second.project_memory(org)
    assert len(mem) >= 1, mem
    assert mem[-1].get("agent_id") == "video.planner"
    assert mem[-1].get("run_id") == run["run_id"]
    tools = second.tool_invocation_log(org)
    assert len(tools) >= 1, tools
    assert tools[-1].get("agent_id") == "video.planner"
    assert tools[-1].get("run_id") == run["run_id"]
    assert (
        second.inventory_summary()
        .get("activation_policy", {})
        .get("production_media")
        is False
    )


def test_parallel_crew_durable_memory_rehydrates_all_agents(tmp_path: Path) -> None:
    """Parallel crew must not lose memory rows to full-file persist races.

    Regression: concurrent run() snapshots wrote outside the service lock so an
    older save could finish last and drop other agents on rehydrate.
    """
    store = ProductFacadeStore(root=tmp_path / "facade-parallel")
    org = "org-parallel-rehydrate"
    agent_ids = [
        "video.planner",
        "video.orchestrator",
        "video.producer",
        "video.director",
    ]
    first = AgentLoopService(store=store, persist=True)
    # Stress the race with several parallel crews (same store).
    completed_total = 0
    for round_i in range(3):
        crew = first.run_crew(
            agent_ids,
            organization_id=org,
            goal=f"Parallel durable rehydrate round {round_i}",
            parallel=True,
            max_workers=4,
        )
        assert crew.get("mode") == "parallel_bounded", crew
        assert crew.get("completed") == len(agent_ids), crew
        completed_total += int(crew["completed"])

    live_mem = first.project_memory(org, limit=200)
    assert len(live_mem) >= completed_total, (
        f"in-process memory lost rows: {len(live_mem)} < {completed_total}"
    )
    live_agents = {str(row.get("agent_id")) for row in live_mem}
    for aid in agent_ids:
        assert aid in live_agents, f"missing agent in live memory: {aid}"

    # Fresh service instance — only durable store must supply memory
    second = AgentLoopService(store=store, persist=True)
    mem = second.project_memory(org, limit=200)
    assert len(mem) >= completed_total, (
        f"rehydrate dropped parallel memory: {len(mem)} < {completed_total}; {mem}"
    )
    agents = {str(row.get("agent_id")) for row in mem}
    for aid in agent_ids:
        assert aid in agents, f"rehydrate missing agent_id={aid}; agents={agents}"
    tools = second.tool_invocation_log(org, limit=200)
    assert len(tools) >= completed_total, (
        f"rehydrate tool log short: {len(tools)} < {completed_total}"
    )
    tool_agents = {str(row.get("agent_id")) for row in tools}
    for aid in agent_ids:
        assert aid in tool_agents, f"rehydrate tools missing {aid}"
