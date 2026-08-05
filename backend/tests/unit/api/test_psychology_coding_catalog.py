"""Host offline psychology, coding plan, and skills catalog tests."""

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
from app.main import create_app
from app.models.identifiers import ActorId, CorrelationId, OrganizationId
from app.optimization.service import reset_optimization_service_for_tests
from app.psychology.service import reset_psychology_service_for_tests
from app.rag.service import reset_rag_service_for_tests
from app.research.service import reset_research_service_for_tests
from app.strategic.service import reset_strategic_service_for_tests
from app.thinking.service import reset_thinking_service_for_tests

ORG_ID = OrganizationId("org-pcc")
CORRELATION_ID = CorrelationId("corr-pcc")


def body(response: Response) -> dict[str, Any]:
    payload = cast(dict[str, Any], response.json())
    if "data" in payload and "meta" in payload:
        return cast(dict[str, Any], payload["data"])
    return payload


@pytest.fixture
def client() -> Iterator[TestClient]:
    for reset in (
        reset_psychology_service_for_tests,
        reset_coding_service_for_tests,
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
    ):
        reset()
    application = create_app()
    context = AuthenticatedRequestContext(
        tenant_id=ORG_ID,
        actor_id=ActorId("pcc-actor"),
        correlation_id=CORRELATION_ID,
    )
    application.dependency_overrides[get_authenticated_request_context] = lambda: context
    with TestClient(application) as test_client:
        yield test_client
    application.dependency_overrides.clear()


def test_psychology_profile_and_recommend(client: TestClient) -> None:
    pol = body(client.get("/api/v1/psychology/policy"))
    assert pol["activation_policy"]["clinical_claims"] is False
    prof = body(
        client.post(
            "/api/v1/psychology/profile",
            json={"brief": "30s TikTok UGC ad, upbeat, gen z scroll"},
        )
    )
    assert prof["ok"] is True
    assert prof["profile"]["cohort_id"]
    assert prof["profile"]["emotional_target"]
    rec = body(
        client.post(
            "/api/v1/psychology/recommend",
            json={
                "brief": "30s TikTok UGC ad, upbeat",
                "profile_id": prof["profile"]["profile_id"],
            },
        )
    )
    assert rec["ok"] is True
    assert rec["hooks"]


def test_coding_plan_fail_closed(client: TestClient) -> None:
    pol = body(client.get("/api/v1/coding/policy"))
    assert pol["activation_policy"]["arbitrary_shell"] is False
    plan = body(
        client.post(
            "/api/v1/coding/plan",
            json={"goal": "Add aesthetics Host API unit tests"},
        )
    )
    assert plan["ok"] is True
    assert plan["plan_steps"]
    assert plan["touch_points"]
    denied = client.post(
        "/api/v1/coding/plan",
        json={"goal": "x", "allow_shell_exec": True},
    )
    assert denied.status_code in {403, 400}


def test_skills_catalog_lists_foundations(client: TestClient) -> None:
    cat = body(client.get("/api/v1/skills/catalog"))
    assert cat["count"] >= 14
    ids = {i["skill_id"] for i in cat["items"]}
    assert "psychology" in ids
    assert "coding" in ids
    assert "rag" in ids
    assert cat["activation_policy"]["network"] is False


def test_skill_evals_include_new_skills(client: TestClient) -> None:
    suite = body(client.post("/api/v1/skill-evals/run", json={}))
    assert suite["total"] >= 13
    assert suite["failed"] == 0
    assert suite["ok"] is True
