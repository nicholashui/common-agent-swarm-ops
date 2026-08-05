"""Host offline knowledge router, research, thinking hooks."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any, cast

import pytest
from fastapi.testclient import TestClient
from httpx import Response

from app.api.v1.dependencies import AuthenticatedRequestContext, get_authenticated_request_context
from app.knowledge.service import reset_knowledge_router_service_for_tests
from app.main import create_app
from app.models.identifiers import ActorId, CorrelationId, OrganizationId
from app.rag.service import reset_rag_service_for_tests
from app.research.service import reset_research_service_for_tests
from app.thinking.service import reset_thinking_service_for_tests

ORG_ID = OrganizationId("org-krt")
CORRELATION_ID = CorrelationId("corr-krt")


def body(response: Response) -> dict[str, Any]:
    payload = cast(dict[str, Any], response.json())
    if "data" in payload and "meta" in payload:
        return cast(dict[str, Any], payload["data"])
    return payload


@pytest.fixture
def client() -> Iterator[TestClient]:
    reset_knowledge_router_service_for_tests()
    reset_research_service_for_tests()
    reset_thinking_service_for_tests()
    reset_rag_service_for_tests()
    application = create_app()
    context = AuthenticatedRequestContext(
        tenant_id=ORG_ID,
        actor_id=ActorId("krt-actor"),
        correlation_id=CORRELATION_ID,
    )
    application.dependency_overrides[get_authenticated_request_context] = lambda: context
    with TestClient(application) as test_client:
        yield test_client
    application.dependency_overrides.clear()
    reset_knowledge_router_service_for_tests()
    reset_research_service_for_tests()
    reset_thinking_service_for_tests()
    reset_rag_service_for_tests()


def test_knowledge_route_and_fail_closed(client: TestClient) -> None:
    pol = body(client.get("/api/v1/knowledge/policy"))
    assert pol["activation_policy"]["live_web"] is False
    assert "rag" in pol["destinations"]

    route = body(
        client.post(
            "/api/v1/knowledge/route",
            json={
                "query": "How does Host memory retrieval work with provenance?",
                "requester_agent_id": "video.memory",
            },
        )
    )
    assert route["primary"] in {"memory", "rag"}
    assert route["confidence"] > 0
    assert route["suggested_agent_ids"]

    denied = client.post(
        "/api/v1/knowledge/route",
        json={"query": "x", "allow_live_web": True},
    )
    assert denied.status_code in {403, 400}


def test_research_offline_brief(client: TestClient) -> None:
    pol = body(client.get("/api/v1/research/policy"))
    assert "gather_rag" in pol["steps"]
    assert pol["activation_policy"]["live_web"] is False

    result = body(
        client.post(
            "/api/v1/research/query",
            json={"query": "Explain offline Agentic RAG foundation and memory tiers"},
        )
    )
    assert result["ok"] is True
    assert result["plan"]
    assert result["brief"]["findings"]
    assert "Planning" in result["patterns_used"]
    assert result["activation_policy"]["tavily"] is False

    denied = client.post(
        "/api/v1/research/query",
        json={"query": "x", "allow_live_web": True},
    )
    assert denied.status_code in {403, 400}


def test_thinking_catalog_and_recommend(client: TestClient) -> None:
    catalog = body(client.get("/api/v1/thinking/catalog"))
    assert catalog["count"] >= 8
    ids = {m["id"] for m in catalog["items"]}
    assert "cynefin" in ids
    assert "premortem" in ids

    rec = body(
        client.post(
            "/api/v1/thinking/recommend",
            json={"goal": "Explore uncertain multi-agent research strategy"},
        )
    )
    assert rec["ok"] is True
    assert rec["cognitive_profile"]["operating_mode"] in {"fast", "full"}
    assert rec["cognitive_profile"]["max_steps"] >= 2
    assert rec["selected_models"]


def test_host_tools_knowledge_research_thinking() -> None:
    from app.video.tool_activation import HostToolRegistry, reset_host_tool_registry_for_tests

    reset_host_tool_registry_for_tests()
    reset_knowledge_router_service_for_tests()
    reset_research_service_for_tests()
    reset_thinking_service_for_tests()
    reset_rag_service_for_tests()
    reg = HostToolRegistry()
    ids = {t["tool_id"] for t in reg.list_catalog()["tools"]}
    assert "knowledge.route" in ids
    assert "research.query" in ids
    assert "thinking.recommend" in ids

    k = reg.invoke(
        "knowledge.route",
        agent_id="video.memory",
        arguments={"query": "aesthetic composition lookbook"},
    )
    assert k.ok
    assert "primary=" in k.detail

    r = reg.invoke(
        "research.query",
        agent_id="video.webresearch",
        arguments={"query": "Host memory retrieval tiers"},
    )
    assert r.ok
    assert "conf=" in r.detail

    t = reg.invoke(
        "thinking.recommend",
        agent_id="video.planner",
        arguments={"goal": "Plan a simple stub status check"},
    )
    assert t.ok
    assert "mode=" in t.detail
