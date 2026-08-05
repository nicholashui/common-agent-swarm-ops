"""Host offline Aesthetics Agent foundation tests."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any, cast

import pytest
from fastapi.testclient import TestClient
from httpx import Response

from app.aesthetics.models import AESTHETIC_DIMENSIONS
from app.aesthetics.service import reset_aesthetics_service_for_tests
from app.api.v1.dependencies import AuthenticatedRequestContext, get_authenticated_request_context
from app.main import create_app
from app.models.identifiers import ActorId, CorrelationId, OrganizationId

ORG_ID = OrganizationId("org-aesthetics")
CORRELATION_ID = CorrelationId("corr-aesthetics")


def body(response: Response) -> dict[str, Any]:
    payload = cast(dict[str, Any], response.json())
    if "data" in payload and "meta" in payload:
        return cast(dict[str, Any], payload["data"])
    return payload


@pytest.fixture
def client() -> Iterator[TestClient]:
    reset_aesthetics_service_for_tests()
    application = create_app()
    context = AuthenticatedRequestContext(
        tenant_id=ORG_ID,
        actor_id=ActorId("aes-actor"),
        correlation_id=CORRELATION_ID,
    )
    application.dependency_overrides[get_authenticated_request_context] = lambda: context
    with TestClient(application) as test_client:
        yield test_client
    application.dependency_overrides.clear()
    reset_aesthetics_service_for_tests()


def test_policy_lists_dimensions_and_fail_closed(client: TestClient) -> None:
    pol = body(client.get("/api/v1/aesthetics/policy"))
    assert pol["activation_policy"]["live_vision"] is False
    assert pol["activation_policy"]["production_media"] is False
    assert set(pol["dimensions"]) == set(AESTHETIC_DIMENSIONS)
    assert "score" in pol["modes"]


def test_evaluate_score_returns_full_vector_not_naked_scalar(client: TestClient) -> None:
    result = body(
        client.post(
            "/api/v1/aesthetics/evaluate",
            json={
                "artifact_ref": "asset://shot_01_take_a",
                "media_type": "image",
                "mode": "score",
                "intent": {
                    "shot_intent_text": "low-key noir portrait with practical lamp",
                    "genre_prior": "noir",
                },
                "emotional_target": {"valence": -0.3, "arousal": 0.6},
            },
        )
    )
    assert result["ok"] is True
    v = result["verdict"]
    assert set(v["aesthetic_vector"].keys()) == set(AESTHETIC_DIMENSIONS)
    assert set(v["confidence"].keys()) == set(AESTHETIC_DIMENSIONS)
    assert 0.0 <= v["aesthetic_quality"] <= 1.0
    assert 0.0 <= v["hack_likelihood"] <= 1.0
    assert isinstance(v["actionable_critique"], list)
    assert len(v["actionable_critique"]) >= 1
    assert v["activation_policy"]["live_vision"] is False
    # Deterministic for same artifact + same intent/profile inputs
    payload = {
        "artifact_ref": "asset://shot_01_take_a",
        "media_type": "image",
        "mode": "score",
        "intent": {
            "shot_intent_text": "low-key noir portrait with practical lamp",
            "genre_prior": "noir",
        },
        "emotional_target": {"valence": -0.3, "arousal": 0.6},
    }
    again = body(client.post("/api/v1/aesthetics/evaluate", json=payload))
    assert again["verdict"]["aesthetic_quality"] == v["aesthetic_quality"]
    assert again["verdict"]["aesthetic_vector"] == v["aesthetic_vector"]


def test_live_vision_flag_denied(client: TestClient) -> None:
    denied = client.post(
        "/api/v1/aesthetics/evaluate",
        json={
            "artifact_ref": "asset://x",
            "allow_live_vision": True,
        },
    )
    assert denied.status_code in {403, 400}


def test_profile_upsert_and_list(client: TestClient) -> None:
    created = body(
        client.post(
            "/api/v1/aesthetics/profiles",
            json={
                "profile_id": "director_test_v1",
                "owner": "org-aesthetics",
                "profile_type": "director",
                "weights": {"light": 2.0, "color_harmony": 1.5},
                "elicited_criteria": ["prefers low-key contrast"],
            },
        )
    )
    assert created["ok"] is True
    assert created["profile"]["profile_id"] == "director_test_v1"
    assert created["profile"]["version"] >= 1

    listed = body(client.get("/api/v1/aesthetics/profiles"))
    ids = {p["profile_id"] for p in listed["items"]}
    assert "neutral_baseline_v1" in ids
    assert "director_test_v1" in ids


def test_compare_ranks_candidates(client: TestClient) -> None:
    result = body(
        client.post(
            "/api/v1/aesthetics/compare",
            json={
                "candidates": ["asset://a", "asset://b", "asset://c"],
                "media_type": "video_clip",
            },
        )
    )
    assert result["ok"] is True
    assert len(result["ranking"]) == 3
    qualities = [r["aesthetic_quality"] for r in result["ranking"]]
    assert qualities == sorted(qualities, reverse=True)
    assert result["best_artifact_ref"] == result["ranking"][0]["artifact_ref"]


def test_align_and_refine_emit_reward_and_steers(client: TestClient) -> None:
    align = body(
        client.post(
            "/api/v1/aesthetics/evaluate",
            json={"artifact_ref": "asset://train_1", "mode": "align"},
        )
    )
    assert align["verdict"]["reward"] is not None
    assert "scalar" in align["verdict"]["reward"]
    assert align["verdict"]["preference_pairs"]

    refine = body(
        client.post(
            "/api/v1/aesthetics/refine",
            json={"artifact_ref": "asset://train_1", "mode": "refine"},
        )
    )
    assert refine["ok"] is True
    assert refine["iteration"] == 1
    assert refine["verdict"]["prompt_steer_hints"]


def test_verdict_markdown_and_compare_preference_pairs(client: TestClient) -> None:
    scored = body(
        client.post(
            "/api/v1/aesthetics/evaluate",
            json={"artifact_ref": "asset://md_1", "mode": "score"},
        )
    )
    assert scored["ok"] is True
    assert "verdict_markdown" in scored
    assert "Aesthetic verdict" in scored["verdict_markdown"]
    assert "aesthetic_quality" in scored["verdict_markdown"].lower() or "Aesthetic quality" in scored[
        "verdict_markdown"
    ]

    compared = body(
        client.post(
            "/api/v1/aesthetics/compare",
            json={"candidates": ["asset://p1", "asset://p2", "asset://p3"]},
        )
    )
    assert compared["ok"] is True
    assert compared["preference_pairs"]
    pair = compared["preference_pairs"][0]
    assert pair["preferred"] == compared["best_artifact_ref"]
    assert pair["source"] == "compare_ranking"
    assert pair["preferred_aq"] >= pair["rejected_aq"]


def test_profile_compose_and_memory_ratchet(client: TestClient) -> None:
    body(
        client.post(
            "/api/v1/aesthetics/profiles",
            json={
                "profile_id": "brand_acme_v1",
                "owner": "org-aesthetics",
                "profile_type": "brand",
                "weights": {"color_harmony": 2.5, "light": 1.0},
            },
        )
    )
    body(
        client.post(
            "/api/v1/aesthetics/profiles",
            json={
                "profile_id": "genre_noir_v1",
                "owner": "org-aesthetics",
                "profile_type": "genre_prior",
                "weights": {"light": 2.2, "novelty": 1.8},
            },
        )
    )
    composed = body(
        client.post(
            "/api/v1/aesthetics/profiles/compose",
            json={
                "base_profile_id": "brand_acme_v1",
                "overlay_profile_id": "genre_noir_v1",
                "new_profile_id": "brand_acme_noir_v1",
                "precedence": "overlay",
            },
        )
    )
    assert composed["ok"] is True
    assert composed["profile"]["profile_id"] == "brand_acme_noir_v1"
    # overlay light wins (2.2 != 1.0 default-ish)
    assert composed["profile"]["weights"]["light"] == 2.2

    # Evaluate under composed profile so memory can ratchet it
    ev = body(
        client.post(
            "/api/v1/aesthetics/evaluate",
            json={
                "artifact_ref": "asset://ratchet_1",
                "profile_id": "brand_acme_noir_v1",
                "mode": "score",
            },
        )
    )
    assert ev["verdict"]["profile_id"] == "brand_acme_noir_v1"
    before_ver = composed["profile"]["version"]
    mem = body(
        client.post(
            "/api/v1/aesthetics/memory/decision",
            json={
                "project_id": "proj_ratchet",
                "artifact_ref": "asset://ratchet_1",
                "decision": "rejected",
                "note": "Director reject",
            },
        )
    )
    assert mem["ok"] is True
    # Ratchet only when profile is non-neutral; may or may not bump version
    if mem.get("profile_ratcheted"):
        assert mem["profile_ratcheted"]["version"] > before_ver


def test_refine_iteration_cap_and_extra_consumers(client: TestClient) -> None:
    consumers = body(client.get("/api/v1/aesthetics/consumers"))
    ids = {c["agent_id"] for c in consumers["items"]}
    assert "video.foodstylist" in ids
    assert "video.travelcine" in ids
    assert "video.realestatephoto" in ids

    r1 = body(
        client.post(
            "/api/v1/aesthetics/refine",
            json={"artifact_ref": "asset://refine_loop", "mode": "refine"},
        )
    )
    r2 = body(
        client.post(
            "/api/v1/aesthetics/refine",
            json={"artifact_ref": "asset://refine_loop", "mode": "refine"},
        )
    )
    r3 = body(
        client.post(
            "/api/v1/aesthetics/refine",
            json={"artifact_ref": "asset://refine_loop", "mode": "refine"},
        )
    )
    assert r1["iteration"] == 1
    assert r2["iteration"] == 2
    assert r3["iteration"] == 3
    assert r3["max_iterations_hint"] == 3
    # After max iterations, stop unless HiTL already required
    if not r3["verdict"].get("escalate_to_hitl"):
        assert r3["next_action"] == "stop_max_iterations"


def test_critique_bus_consumer_and_handoff_attach(client: TestClient) -> None:
    consumers = body(client.get("/api/v1/aesthetics/consumers"))
    assert consumers["count"] >= 5
    assert any(c["agent_id"] == "video.cinematographer" for c in consumers["items"])

    consumer = body(
        client.post(
            "/api/v1/aesthetics/consumers/evaluate",
            json={
                "consumer_agent_id": "video.cinematographer",
                "artifact_ref": "asset://dop_shot",
                "shot_intent_text": "wide establishing dusk",
                "publish_bus": True,
            },
        )
    )
    assert consumer["ok"] is True
    assert consumer["critique_bus_messages"]
    assert consumer["critique_bus_messages"][0]["critique_type"] == "aesthetic_feedback"

    bus = body(client.get("/api/v1/aesthetics/bus?to_agent_id=video.cinematographer"))
    assert len(bus["items"]) >= 1

    verdict = consumer["result"]["verdict"]
    handoff = body(
        client.post(
            "/api/v1/aesthetics/handoff/attach",
            json={
                "handoff": {
                    "artifact_id": "art_1",
                    "kind": "frame",
                    "production_media": False,
                },
                "verdict": verdict,
            },
        )
    )
    assert handoff["ok"] is True
    qc = handoff["handoff"]["qc_status"]
    assert qc.startswith("aesthetic_")
    assert qc in {
        "aesthetic_pass",
        "aesthetic_review",
        "aesthetic_fail",
        "aesthetic_pending_human",
    }
    aesthetic_meta = handoff["handoff"]["qc_meta"]["aesthetic"]
    assert aesthetic_meta["agent_id"] == "specials.aesthetics-agent"
    if verdict.get("escalate_to_hitl"):
        assert qc == "aesthetic_pending_human"
        assert aesthetic_meta["escalate_to_hitl"] is True
    assert handoff["handoff"]["production_media"] is False

    mem = body(
        client.post(
            "/api/v1/aesthetics/memory/decision",
            json={
                "project_id": "proj_demo",
                "artifact_ref": "asset://dop_shot",
                "decision": "accepted",
                "note": "Director lock",
            },
        )
    )
    assert mem["ok"] is True
    listed = body(client.get("/api/v1/aesthetics/memory/proj_demo"))
    assert listed["summary"]["accepted"] >= 1
