"""Host offline podcast, screenwriting, tech radar, LQR tests."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any, cast

import pytest
from fastapi.testclient import TestClient
from httpx import Response

from app.api.v1.dependencies import AuthenticatedRequestContext, get_authenticated_request_context
from app.aesthetics.service import reset_aesthetics_service_for_tests
from app.coding.service import reset_coding_service_for_tests
from app.complex_problem.service import reset_complex_problem_service_for_tests
from app.creative.service import reset_creative_service_for_tests
from app.intent.service import reset_intent_service_for_tests
from app.knowledge.service import reset_knowledge_router_service_for_tests
from app.llm_usage.service import reset_llm_usage_service_for_tests
from app.lqr.service import reset_lqr_service_for_tests
from app.main import create_app
from app.models.identifiers import ActorId, CorrelationId, OrganizationId
from app.optimization.service import reset_optimization_service_for_tests
from app.podcast.service import reset_podcast_service_for_tests
from app.psychology.service import reset_psychology_service_for_tests
from app.rag.service import reset_rag_service_for_tests
from app.research.service import reset_research_service_for_tests
from app.screenwriting.service import reset_screenwriting_service_for_tests
from app.strategic.service import reset_strategic_service_for_tests
from app.tech_radar.service import reset_tech_radar_service_for_tests
from app.thinking.service import reset_thinking_service_for_tests

ORG_ID = OrganizationId("org-psrl")
CORRELATION_ID = CorrelationId("corr-psrl")


def body(response: Response) -> dict[str, Any]:
    payload = cast(dict[str, Any], response.json())
    if "data" in payload and "meta" in payload:
        return cast(dict[str, Any], payload["data"])
    return payload


@pytest.fixture
def client() -> Iterator[TestClient]:
    for reset in (
        reset_podcast_service_for_tests,
        reset_screenwriting_service_for_tests,
        reset_tech_radar_service_for_tests,
        reset_lqr_service_for_tests,
        reset_rag_service_for_tests,
        reset_knowledge_router_service_for_tests,
        reset_research_service_for_tests,
        reset_thinking_service_for_tests,
        reset_aesthetics_service_for_tests,
        reset_intent_service_for_tests,
        reset_optimization_service_for_tests,
        reset_creative_service_for_tests,
        reset_complex_problem_service_for_tests,
        reset_strategic_service_for_tests,
        reset_llm_usage_service_for_tests,
        reset_psychology_service_for_tests,
        reset_coding_service_for_tests,
    ):
        reset()
    application = create_app()
    context = AuthenticatedRequestContext(
        tenant_id=ORG_ID,
        actor_id=ActorId("psrl-actor"),
        correlation_id=CORRELATION_ID,
    )
    application.dependency_overrides[get_authenticated_request_context] = lambda: context
    with TestClient(application) as test_client:
        yield test_client
    application.dependency_overrides.clear()


def test_podcast_outline_fail_closed(client: TestClient) -> None:
    pol = body(client.get("/api/v1/podcast/policy"))
    assert pol["activation_policy"]["live_tts"] is False
    out = body(
        client.post(
            "/api/v1/podcast/outline",
            json={"topic": "How Host agent loops stay fail-closed", "duration_min": 25},
        )
    )
    assert out["ok"] is True
    assert out["segments"]
    assert out["vo_plan"]["live_tts"] is False
    denied = client.post(
        "/api/v1/podcast/outline",
        json={"topic": "x", "allow_live_tts": True},
    )
    assert denied.status_code in {403, 400}


def test_screenwriting_plan(client: TestClient) -> None:
    plan = body(
        client.post(
            "/api/v1/screenwriting/plan",
            json={
                "logline_or_goal": "A quiet clerk seeks redemption after a small lie spreads",
                "form": "short",
            },
        )
    )
    assert plan["ok"] is True
    assert plan["beats"]
    assert plan["controlling_idea"]


def test_tech_radar_catalog_and_advise(client: TestClient) -> None:
    cat = body(client.get("/api/v1/tech-radar/catalog"))
    assert cat["count"] >= 4
    assert any(i["id"] == "media_stub" for i in cat["items"])
    adv = body(
        client.post(
            "/api/v1/tech-radar/advise",
            json={"goal": "offline stub video for spine QC", "prefer_offline": True},
        )
    )
    assert adv["ok"] is True
    assert adv["recommended_provider_id"]


def test_lqr_overview(client: TestClient) -> None:
    pol = body(client.get("/api/v1/lqr/policy"))
    assert pol["archetype"] == "E"
    assert pol["activation_policy"]["full_mcts_shot_loop"] is False
    ov = body(client.post("/api/v1/lqr/overview", json={}))
    assert ov["ok"] is True
    assert len(ov["phases"]) >= 6
    assert ov["principles"]


def test_skill_evals_and_catalog_include_new(client: TestClient) -> None:
    suite = body(client.post("/api/v1/skill-evals/run", json={}))
    assert suite["total"] >= 17
    assert suite["failed"] == 0
    cat = body(client.get("/api/v1/skills/catalog"))
    ids = {i["skill_id"] for i in cat["items"]}
    assert "podcast" in ids
    assert "lqr" in ids
    assert "tech_radar" in ids
    assert "screenwriting" in ids
