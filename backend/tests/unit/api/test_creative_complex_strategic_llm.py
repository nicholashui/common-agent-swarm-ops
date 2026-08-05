"""Host offline creative / complex-problem / strategic / llm-usage tests."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any, cast

import pytest
from fastapi.testclient import TestClient
from httpx import Response

from app.api.v1.dependencies import AuthenticatedRequestContext, get_authenticated_request_context
from app.aesthetics.service import reset_aesthetics_service_for_tests
from app.complex_problem.service import reset_complex_problem_service_for_tests
from app.creative.service import reset_creative_service_for_tests
from app.intent.service import reset_intent_service_for_tests
from app.knowledge.service import reset_knowledge_router_service_for_tests
from app.llm_usage.service import reset_llm_usage_service_for_tests
from app.main import create_app
from app.models.identifiers import ActorId, CorrelationId, OrganizationId
from app.optimization.service import reset_optimization_service_for_tests
from app.rag.service import reset_rag_service_for_tests
from app.research.service import reset_research_service_for_tests
from app.strategic.service import reset_strategic_service_for_tests
from app.thinking.service import reset_thinking_service_for_tests

ORG_ID = OrganizationId("org-ccsl")
CORRELATION_ID = CorrelationId("corr-ccsl")


def body(response: Response) -> dict[str, Any]:
    payload = cast(dict[str, Any], response.json())
    if "data" in payload and "meta" in payload:
        return cast(dict[str, Any], payload["data"])
    return payload


@pytest.fixture
def client() -> Iterator[TestClient]:
    for reset in (
        reset_creative_service_for_tests,
        reset_complex_problem_service_for_tests,
        reset_strategic_service_for_tests,
        reset_llm_usage_service_for_tests,
        reset_rag_service_for_tests,
        reset_knowledge_router_service_for_tests,
        reset_research_service_for_tests,
        reset_thinking_service_for_tests,
        reset_aesthetics_service_for_tests,
        reset_intent_service_for_tests,
        reset_optimization_service_for_tests,
    ):
        reset()
    application = create_app()
    context = AuthenticatedRequestContext(
        tenant_id=ORG_ID,
        actor_id=ActorId("ccsl-actor"),
        correlation_id=CORRELATION_ID,
    )
    application.dependency_overrides[get_authenticated_request_context] = lambda: context
    with TestClient(application) as test_client:
        yield test_client
    application.dependency_overrides.clear()


def test_creative_ideate(client: TestClient) -> None:
    pol = body(client.get("/api/v1/creative/policy"))
    assert pol["activation_policy"]["live_generation"] is False
    assert pol["ssor_lite"]["max_outlier_dimensions"] == 4
    result = body(
        client.post(
            "/api/v1/creative/ideate",
            json={"brief": "30s noir tea ad with practical lamp", "n_candidates": 3},
        )
    )
    assert result["ok"] is True
    assert len(result["candidates"]) == 3
    assert result["best_candidate_id"]
    assert result["creative_direction"]["logline"]
    assert result["domain"] in {
        "video",
        "scientific",
        "artistic",
        "business",
        "engineering",
        "educational",
    }
    assert result["povs"] and len(result["povs"]) >= 8
    assert result["phase_trace"]
    phase_names = [p["phase"] for p in result["phase_trace"]]
    for required in (
        "multi_pov_mapping",
        "normal_range_definition",
        "sparse_outlier_sampling",
        "cross_dimensional_recombination",
        "value_gated_selection",
        "integration_refinement",
        "output",
    ):
        assert required in phase_names
    # integration_refinement must appear before final output
    assert phase_names.index("integration_refinement") < phase_names.index("output")
    for cand in result["candidates"]:
        assert cand["multi_pov"]
        assert 1 <= len(cand["outlier_dimensions"]) <= 4
        assert cand["outlier_count"] == len(cand["outlier_dimensions"])
        for key in (
            "novelty",
            "usefulness",
            "coherence",
            "feasibility",
            "overall_cr",
            "ssor",
            "balance_b",
            "combination_rarity",
        ):
            assert key in cand
            assert 0.0 < float(cand[key]) <= 1.0
        assert cand["ssor"] == cand["overall_cr"]
        assert cand["surprise_vector"]["outlier_dimensions"] == cand["outlier_dimensions"]
        assert cand["risks_mitigations"]["risk"]
        assert cand["risks_mitigations"]["mitigations"]
        assert cand["refinement_note"]
    # Ranked by overall_cr descending
    crs = [float(c["overall_cr"]) for c in result["candidates"]]
    assert crs == sorted(crs, reverse=True)
    assert result["best_candidate_id"] == result["candidates"][0]["candidate_id"]
    assert result["learned_patterns_scope"] == "process_local"
    assert isinstance(result["learned_patterns"], list)
    handoff = result["handoff"]
    assert handoff["best_candidate_id"] == result["best_candidate_id"]
    assert handoff["concept"]
    assert handoff["prompt_steer"]
    assert handoff["next_agents"]
    assert handoff["creative_direction"]["logline"]
    assert handoff["scope"] == "offline_host_handoff"
    denied = client.post(
        "/api/v1/creative/ideate",
        json={"brief": "x", "allow_live_generation": True},
    )
    assert denied.status_code in {403, 400}


def test_creative_patterns_endpoint_process_local(client: TestClient) -> None:
    empty = body(client.get("/api/v1/creative/patterns"))
    assert empty["ok"] is True
    assert empty["count"] == 0
    assert empty["items"] == []
    assert empty["scope"] == "process_local"
    assert empty["learned_patterns_scope"] == "process_local"
    ideate = body(
        client.post(
            "/api/v1/creative/ideate",
            json={
                "brief": "patterns endpoint seed brief with practical lamp",
                "n_candidates": 2,
                "domain": "video",
            },
        )
    )
    assert ideate["ok"] is True
    populated = body(client.get("/api/v1/creative/patterns?limit=12"))
    assert populated["ok"] is True
    assert populated["count"] >= 1
    assert populated["scope"] == "process_local"
    assert populated["items"][0]["seed_motif"]
    assert populated["items"][0]["scope"] == "process_local"
    # Lean payload: no full candidates dump
    assert "candidates" not in populated
    assert "phase_trace" not in populated


def test_creative_learned_patterns_process_local(client: TestClient) -> None:
    first = body(
        client.post(
            "/api/v1/creative/ideate",
            json={
                "brief": "first offline creative pass for pattern memory",
                "n_candidates": 2,
                "domain": "video",
            },
        )
    )
    assert first["ok"] is True
    assert first["learned_patterns"] == []
    second = body(
        client.post(
            "/api/v1/creative/ideate",
            json={
                "brief": "second offline creative pass after prior motif",
                "n_candidates": 2,
                "domain": "video",
            },
        )
    )
    assert second["ok"] is True
    assert len(second["learned_patterns"]) >= 1
    assert second["learned_patterns"][0]["scope"] == "process_local"
    assert second["learned_patterns"][0]["seed_motif"]
    assert second["learned_patterns"][0]["run_id"] == first["run_id"]


def test_creative_ssor_lite_deterministic_and_domain(client: TestClient) -> None:
    payload = {
        "brief": "30s noir tea ad with practical lamp",
        "n_candidates": 3,
        "domain": "video",
    }
    a = body(client.post("/api/v1/creative/ideate", json=payload))
    b = body(client.post("/api/v1/creative/ideate", json=payload))
    assert a["ok"] is True and b["ok"] is True
    assert a["run_id"] == b["run_id"]
    assert [c["candidate_id"] for c in a["candidates"]] == [
        c["candidate_id"] for c in b["candidates"]
    ]
    assert [c["overall_cr"] for c in a["candidates"]] == [
        c["overall_cr"] for c in b["candidates"]
    ]
    sci = body(
        client.post(
            "/api/v1/creative/ideate",
            json={
                "brief": "Explain a counterintuitive lab result in 60s",
                "n_candidates": 2,
                "domain": "scientific",
            },
        )
    )
    assert sci["ok"] is True
    assert sci["domain"] == "scientific"
    assert sci["domain_weights"]["novelty"] >= 1.0
    sci_pov_names = {p["name"] for p in sci["povs"]}
    assert "hypothesis_space" in sci_pov_names


def test_complex_problem_solve(client: TestClient) -> None:
    result = body(
        client.post(
            "/api/v1/complex-problem/solve",
            json={"problem": "Deliver offline video spine with research and package HITL"},
        )
    )
    assert result["ok"] is True
    assert result["subproblems"]
    assert result["plan"]
    assert result["gates"]
    assert result["recommended_option"]


def test_strategic_plan(client: TestClient) -> None:
    result = body(
        client.post(
            "/api/v1/strategic/plan",
            json={"goal": "Ship a three-film brand campaign offline", "horizon": "campaign"},
        )
    )
    assert result["ok"] is True
    assert result["milestones"]
    assert result["key_results"]
    assert result["next_actions"]


def test_llm_usage_policy_and_record(client: TestClient) -> None:
    pol = body(client.get("/api/v1/llm-usage/policy"))
    assert pol["network_access"] is False
    assert pol["default_provider"] == "local_deterministic"
    rec = body(
        client.post(
            "/api/v1/llm-usage/record",
            json={
                "operation": "agent_loop",
                "estimated_input_tokens": 200,
                "estimated_output_tokens": 100,
                "offline": True,
            },
        )
    )
    assert rec["ok"] is True
    assert rec["within_budget"] is True
    mode = body(
        client.post("/api/v1/llm-usage/recommend-mode", json={"goal": "cheap draft asap"})
    )
    assert mode["mode"] in {"minimal", "balanced", "thorough"}
    denied = client.post(
        "/api/v1/llm-usage/record",
        json={"operation": "x", "offline": False},
    )
    assert denied.status_code in {403, 400}


def test_expanded_skill_evals(client: TestClient) -> None:
    suite = body(client.post("/api/v1/skill-evals/run", json={}))
    assert suite["total"] >= 11
    assert suite["failed"] == 0
    assert suite["ok"] is True
