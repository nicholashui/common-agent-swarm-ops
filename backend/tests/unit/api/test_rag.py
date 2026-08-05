"""Host offline Agentic RAG foundation tests."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any, cast

import pytest
from fastapi.testclient import TestClient
from httpx import Response

from app.api.v1.dependencies import AuthenticatedRequestContext, get_authenticated_request_context
from app.main import create_app
from app.models.identifiers import ActorId, CorrelationId, OrganizationId
from app.rag.service import reset_rag_service_for_tests

ORG_ID = OrganizationId("org-rag")
CORRELATION_ID = CorrelationId("corr-rag")


def body(response: Response) -> dict[str, Any]:
    payload = cast(dict[str, Any], response.json())
    if "data" in payload and "meta" in payload:
        return cast(dict[str, Any], payload["data"])
    return payload


@pytest.fixture
def client() -> Iterator[TestClient]:
    reset_rag_service_for_tests()
    application = create_app()
    context = AuthenticatedRequestContext(
        tenant_id=ORG_ID,
        actor_id=ActorId("rag-actor"),
        correlation_id=CORRELATION_ID,
    )
    application.dependency_overrides[get_authenticated_request_context] = lambda: context
    with TestClient(application) as test_client:
        yield test_client
    application.dependency_overrides.clear()
    reset_rag_service_for_tests()


def test_policy_fail_closed_and_patterns(client: TestClient) -> None:
    pol = body(client.get("/api/v1/rag/policy"))
    assert pol["activation_policy"]["live_web"] is False
    assert pol["activation_policy"]["chroma"] is False
    assert pol["activation_policy"]["lightrag"] is False
    assert "Reflection" in pol["patterns"]
    assert "Planning" in pol["patterns"]
    assert pol["index"]["documents"] >= 1


def test_seeded_query_returns_citations_and_trace(client: TestClient) -> None:
    result = body(
        client.post(
            "/api/v1/rag/query",
            json={"query": "How does Host memory retrieval work with tiers?"},
        )
    )
    assert result["ok"] is True
    run = result["run"]
    assert run["final_answer"]
    assert run["citations"]
    assert run["plan"]
    assert run["trace"]
    assert "Planning" in run["patterns_used"]
    assert "Tool Use" in run["patterns_used"]
    assert run["iterations"] >= 1
    assert run["activation_policy"]["lightrag"] is False
    nodes = {t.get("node") for t in run["trace"]}
    assert "query_analyzer" in nodes
    assert "researcher" in nodes
    assert "critic" in nodes


def test_ingest_improves_specific_query(client: TestClient) -> None:
    ingested = body(
        client.post(
            "/api/v1/rag/ingest",
            json={
                "title": "Purple Widget Protocol",
                "content": (
                    "# Purple Widget Protocol\n\n"
                    "The purple widget protocol requires dual-key approval "
                    "before shipping any widget batch to region north."
                ),
                "source_ref": "local://purple-widget",
                "tags": ["widget"],
            },
        )
    )
    assert ingested["ok"] is True
    assert ingested["children"] >= 1

    result = body(
        client.post(
            "/api/v1/rag/query",
            json={"query": "purple widget protocol dual-key approval region north"},
        )
    )
    assert result["ok"] is True
    run = result["run"]
    cites = " ".join(c.get("source_ref", "") for c in run["citations"])
    answer = run["final_answer"].lower()
    assert "purple" in answer or "local://purple-widget" in cites or run["graded_docs"]


def test_live_flags_denied(client: TestClient) -> None:
    for flag in ("allow_live_web", "allow_chroma", "allow_lightrag"):
        denied = client.post(
            "/api/v1/rag/query",
            json={"query": "anything", flag: True},
        )
        assert denied.status_code in {403, 400}, flag


def test_bus_and_runs_recorded(client: TestClient) -> None:
    body(
        client.post(
            "/api/v1/rag/query",
            json={"query": "Agentic RAG offline foundation patterns", "publish_bus": True},
        )
    )
    bus = body(client.get("/api/v1/rag/bus"))
    assert len(bus["items"]) >= 1
    assert bus["items"][-1]["critique_type"] == "rag_feedback"

    runs = body(client.get("/api/v1/rag/runs"))
    assert len(runs["items"]) >= 1


def test_relational_complexity_and_host_tool() -> None:
    from app.rag.pipeline import analyze_query
    from app.rag.service import reset_rag_service_for_tests
    from app.video.tool_activation import HostToolRegistry, reset_host_tool_registry_for_tests

    a = analyze_query("Compare memory retrieve and agentic rag relation between tiers")
    assert a["complexity"] == "relational"
    assert a["requires_relationships"] is True

    reset_rag_service_for_tests()
    reset_host_tool_registry_for_tests()
    reg = HostToolRegistry()
    ids = {t["tool_id"] for t in reg.list_catalog()["tools"]}
    assert "rag.query" in ids
    out = reg.invoke(
        "rag.query",
        agent_id="video.memory",
        arguments={"query": "Host memory retrieval tiers"},
    )
    assert out.ok is True
    assert "conf=" in out.detail
