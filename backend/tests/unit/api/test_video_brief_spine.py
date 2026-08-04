"""User brief + Phase-1 + spine stub dry-run (product façade)."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any, cast

import pytest
from fastapi.testclient import TestClient
from httpx import Response

from app.api.v1.dependencies import AuthenticatedRequestContext, get_authenticated_request_context
from app.api.v1.product_facade import reset_product_facade_for_tests
from app.api.v1.video_brief_spine import (
    PHASE_1_AGENT_IDS,
    SPINE_WORKFLOW_ID,
    build_user_brief,
    load_design_spine_steps,
    validate_user_brief_text,
)
from app.main import create_app
from app.models.identifiers import ActorId, CorrelationId, OrganizationId

ORG_ID = OrganizationId("org-spine")
CORRELATION_ID = CorrelationId("corr-spine")


def body(response: Response) -> dict[str, Any]:
    payload = cast(dict[str, Any], response.json())
    if "data" in payload and "meta" in payload:
        return cast(dict[str, Any], payload["data"])
    return payload


@pytest.fixture
def client() -> Iterator[TestClient]:
    reset_product_facade_for_tests()
    application = create_app()
    context = AuthenticatedRequestContext(
        tenant_id=ORG_ID,
        actor_id=ActorId("spine-actor"),
        correlation_id=CORRELATION_ID,
    )
    application.dependency_overrides[get_authenticated_request_context] = lambda: context
    with TestClient(application) as test_client:
        yield test_client
    application.dependency_overrides.clear()
    reset_product_facade_for_tests()


def test_validate_user_brief_rejects_empty() -> None:
    assert validate_user_brief_text("") is not None
    assert validate_user_brief_text("   ") is not None
    assert validate_user_brief_text("ok brief") is None


def test_build_user_brief_round_trip_meta() -> None:
    brief, err = build_user_brief(
        text="Wuxia short for social",
        brief_meta={"locale": "zh-Hant", "scale_profile": "S1", "archetype": "A"},
        correlation_id="c1",
    )
    assert err is None
    assert brief is not None
    assert brief["version"] == "UserBriefV1"
    assert brief["locale"] == "zh-Hant"
    assert brief["scale_profile"] == "S1"
    assert brief["archetype"] == "A"
    assert brief["text"] == "Wuxia short for social"


def test_build_user_brief_rejects_secrets() -> None:
    brief, err = build_user_brief(
        text="hello",
        brief_meta={"api_key": "x"},
        correlation_id="c1",
    )
    assert brief is None
    assert err is not None


def test_design_spine_steps_load() -> None:
    steps = load_design_spine_steps()
    assert len(steps) >= 8
    assert steps[0]["id"] == "orchestrate"
    assert steps[-1]["id"] == "package"
    assert steps[-1]["human_gate_required"] is True


def test_materialize_video_brief_persists_and_phase1(client: TestClient) -> None:
    mat = client.post(
        "/api/v1/composer/materialize",
        json={
            "goal": "YouTube wuxia cinematic short film production brief",
            "swarm_name": "Wuxia spine crew",
            "brief": {"locale": "zh-Hant", "scale_profile": "S1", "archetype": "A"},
        },
    )
    assert mat.status_code == 200
    payload = body(mat)
    assert payload["swarm_id"]
    assert payload["brief_id"]
    assert payload["spine_workflow_id"] == SPINE_WORKFLOW_ID
    assert payload["spine"]["production_ready"] is False
    assert payload["member_count"] >= 3

    detail = body(client.get(f"/api/v1/swarms/{payload['swarm_id']}"))
    assert detail["brief"]["text"]
    assert detail["brief"]["scale_profile"] == "S1"
    assert detail["spine"]["workflow_id"] == SPINE_WORKFLOW_ID
    member_ids = {m["agent_id"] for m in detail["members"]}
    for required in PHASE_1_AGENT_IDS:
        assert required in member_ids, f"missing Phase-1 agent {required}"


def test_materialize_empty_goal_fails(client: TestClient) -> None:
    # FastAPI min_length rejects empty goal at schema layer
    response = client.post("/api/v1/composer/materialize", json={"goal": ""})
    assert response.status_code in {400, 422}


def test_spine_dry_run_to_package_gate(client: TestClient) -> None:
    mat = body(
        client.post(
            "/api/v1/composer/materialize",
            json={
                "goal": "Brand video production brief with script and director",
                "swarm_name": "Spine dry-run",
            },
        )
    )
    swarm_id = mat["swarm_id"]
    approval_id = None
    # Advance until package waits (max 10 steps)
    for _ in range(10):
        detail = body(client.get(f"/api/v1/swarms/{swarm_id}"))
        actions = {a["kind"]: a["id"] for a in detail["actions"]}
        if detail["spine"]["status"] == "waiting_for_approval":
            approval_id = detail["spine"]["approval_id"]
            break
        assert "run_spine_step" in actions
        step = client.post(
            f"/api/v1/swarms/{swarm_id}/spine/steps",
            json={"action_reference_id": actions["run_spine_step"]},
        )
        assert step.status_code == 200, step.text
        step_body = body(step)
        assert step_body["ok"] is True
        assert step_body["spine"]["note"]
        # Artifacts accumulate
        arts = step_body["spine"].get("artifacts") or {}
        assert isinstance(arts, dict)

    detail = body(client.get(f"/api/v1/swarms/{swarm_id}"))
    assert detail["spine"]["status"] == "waiting_for_approval"
    assert approval_id or detail["spine"]["approval_id"]
    package = next(s for s in detail["spine"]["steps"] if s["id"] == "package")
    assert package["status"] == "waiting_for_approval"
    assert package["artifact_ref"]

    # Live approvals inbox includes package gate
    inbox = body(client.get("/api/v1/approvals"))
    ids = {i.get("approval_id") for i in inbox["items"]}
    assert detail["spine"]["approval_id"] in ids

    # Deny fails closed
    detail2 = body(client.get(f"/api/v1/swarms/{swarm_id}"))
    actions2 = {a["kind"]: a["id"] for a in detail2["actions"]}
    assert "decide_package" in actions2
    denied = client.post(
        f"/api/v1/swarms/{swarm_id}/spine/package-decision",
        json={
            "action_reference_id": actions2["decide_package"],
            "decision": "denied",
            "reason": "Not ready for package",
        },
    )
    assert denied.status_code == 200
    denied_body = body(denied)
    assert denied_body["spine"]["status"] == "denied"


def test_spine_approve_package(client: TestClient) -> None:
    mat = body(
        client.post(
            "/api/v1/composer/materialize",
            json={"goal": "Cinematic trailer video production brief"},
        )
    )
    swarm_id = mat["swarm_id"]
    for _ in range(10):
        detail = body(client.get(f"/api/v1/swarms/{swarm_id}"))
        if detail["spine"]["status"] == "waiting_for_approval":
            break
        actions = {a["kind"]: a["id"] for a in detail["actions"]}
        r = client.post(
            f"/api/v1/swarms/{swarm_id}/spine/steps",
            json={"action_reference_id": actions["run_spine_step"]},
        )
        assert r.status_code == 200

    detail = body(client.get(f"/api/v1/swarms/{swarm_id}"))
    actions = {a["kind"]: a["id"] for a in detail["actions"]}
    approved = client.post(
        f"/api/v1/swarms/{swarm_id}/spine/package-decision",
        json={
            "action_reference_id": actions["decide_package"],
            "decision": "approved",
            "reason": "Stub package inspected OK",
        },
    )
    assert approved.status_code == 200
    assert body(approved)["spine"]["status"] == "completed"
    # production_ready remains false
    assert body(approved)["spine"]["production_ready"] is False


def test_spine_step_without_action_denied(client: TestClient) -> None:
    mat = body(
        client.post(
            "/api/v1/composer/materialize",
            json={"goal": "YouTube video production brief"},
        )
    )
    bad = client.post(
        f"/api/v1/swarms/{mat['swarm_id']}/spine/steps",
        json={"action_reference_id": "act_not_real"},
    )
    assert bad.status_code == 403


def test_list_swarms_exposes_spine_flags_and_activity(client: TestClient) -> None:
    """Epic E: Dashboard can list spine drafts; activity records spine steps."""
    mat = body(
        client.post(
            "/api/v1/composer/materialize",
            json={"goal": "YouTube video production brief for social"},
        )
    )
    swarm_id = mat["swarm_id"]
    listed = body(client.get("/api/v1/swarms"))
    row = next(i for i in listed["items"] if i["id"] == swarm_id)
    assert row["has_spine"] is True
    assert row["spine_workflow_id"] == SPINE_WORKFLOW_ID
    assert row["spine_status"] == "ready"
    assert row["brief_id"]

    detail = body(client.get(f"/api/v1/swarms/{swarm_id}"))
    actions = {a["kind"]: a["id"] for a in detail["actions"]}
    step = client.post(
        f"/api/v1/swarms/{swarm_id}/spine/steps",
        json={"action_reference_id": actions["run_spine_step"]},
    )
    assert step.status_code == 200
    activity = body(client.get("/api/v1/activity?limit=20"))
    cats = {i["category"] for i in activity["items"]}
    assert "spine" in cats or any(
        "spine" in (i.get("summary") or "").lower() for i in activity["items"]
    )
