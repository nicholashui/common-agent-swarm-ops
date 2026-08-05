"""Host offline intent, optimization, and skill golden harness tests."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any, cast

import pytest
from fastapi.testclient import TestClient
from httpx import Response

from app.api.v1.dependencies import AuthenticatedRequestContext, get_authenticated_request_context
from app.aesthetics.service import reset_aesthetics_service_for_tests
from app.intent.service import reset_intent_service_for_tests
from app.knowledge.service import reset_knowledge_router_service_for_tests
from app.main import create_app
from app.models.identifiers import ActorId, CorrelationId, OrganizationId
from app.optimization.service import reset_optimization_service_for_tests
from app.rag.service import reset_rag_service_for_tests
from app.research.service import reset_research_service_for_tests
from app.thinking.service import reset_thinking_service_for_tests

ORG_ID = OrganizationId("org-ioe")
CORRELATION_ID = CorrelationId("corr-ioe")


def body(response: Response) -> dict[str, Any]:
    payload = cast(dict[str, Any], response.json())
    if "data" in payload and "meta" in payload:
        return cast(dict[str, Any], payload["data"])
    return payload


@pytest.fixture
def client() -> Iterator[TestClient]:
    reset_intent_service_for_tests()
    reset_optimization_service_for_tests()
    reset_rag_service_for_tests()
    reset_knowledge_router_service_for_tests()
    reset_research_service_for_tests()
    reset_thinking_service_for_tests()
    reset_aesthetics_service_for_tests()
    application = create_app()
    context = AuthenticatedRequestContext(
        tenant_id=ORG_ID,
        actor_id=ActorId("ioe-actor"),
        correlation_id=CORRELATION_ID,
    )
    application.dependency_overrides[get_authenticated_request_context] = lambda: context
    with TestClient(application) as test_client:
        yield test_client
    application.dependency_overrides.clear()


def test_intent_analyze_video_brief(client: TestClient) -> None:
    pol = body(client.get("/api/v1/intent/policy"))
    assert pol["activation_policy"]["live_llm"] is False
    assert "purpose" in pol["phases"]

    result = body(
        client.post(
            "/api/v1/intent/analyze",
            json={
                "text": "Create a 30s TikTok UGC ad for tea brand, upbeat, 9:16 vertical",
            },
        )
    )
    assert result["ok"] is True
    assert result["primary_intent"] in {
        "promote",
        "entertain",
        "educate",
        "inform",
        "persuade",
    }
    assert result["recommended_archetype"]
    assert result["emotional_target"]
    assert result["phases"]["synthesis"]["actions"]

    denied = client.post(
        "/api/v1/intent/analyze",
        json={"text": "x", "allow_live_llm": True},
    )
    assert denied.status_code in {403, 400}


def test_optimization_recommend(client: TestClient) -> None:
    pol = body(client.get("/api/v1/optimization/policy"))
    assert "prompt" in pol["kinds"]
    assert pol["activation_policy"]["live_roas"] is False

    result = body(
        client.post(
            "/api/v1/optimization/recommend",
            json={"goal": "Cut token cost on exploratory agent loops", "kind": "cost"},
        )
    )
    assert result["ok"] is True
    assert result["kind"] == "cost"
    assert result["suggestions"]
    assert result["apply_order"]

    denied = client.post(
        "/api/v1/optimization/recommend",
        json={"goal": "x", "allow_live_training": True},
    )
    assert denied.status_code in {403, 400}


def test_skill_golden_harness(client: TestClient) -> None:
    pol = body(client.get("/api/v1/skill-evals/policy"))
    assert "intent" in pol["skills"]
    assert pol["live_llm_judge"] is False

    suite = body(client.post("/api/v1/skill-evals/run", json={}))
    assert suite["total"] >= 7
    assert suite["passed"] == suite["total"]
    assert suite["failed"] == 0
    assert suite["ok"] is True


def test_host_tools_intent_opt_evals() -> None:
    from app.video.tool_activation import HostToolRegistry, reset_host_tool_registry_for_tests

    reset_host_tool_registry_for_tests()
    reset_intent_service_for_tests()
    reset_optimization_service_for_tests()
    reg = HostToolRegistry()
    ids = {t["tool_id"] for t in reg.list_catalog()["tools"]}
    assert "intent.analyze" in ids
    assert "optimization.recommend" in ids
    assert "skill_evals.run" in ids

    i = reg.invoke(
        "intent.analyze",
        agent_id="video.planner",
        arguments={"text": "Plan a short cinematic drama film teaser"},
    )
    assert i.ok
    assert "intent=" in i.detail

    o = reg.invoke(
        "optimization.recommend",
        agent_id="video.promptoptimizer",
        arguments={"goal": "Improve retention hook", "kind": "retention"},
    )
    assert o.ok
    assert "kind=" in o.detail
