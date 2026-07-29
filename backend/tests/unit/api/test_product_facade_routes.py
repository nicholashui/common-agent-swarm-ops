"""Product façade routes for commons, swarms, activity, and proposals."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.dependencies import AuthenticatedRequestContext, get_authenticated_request_context
from app.api.v1.product_facade import reset_product_facade_for_tests
from app.main import create_app
from app.models.identifiers import ActorId, CorrelationId, OrganizationId

ORG_ID = OrganizationId("org-product")
CORRELATION_ID = CorrelationId("corr-product")


def body(response) -> dict:
    """Unwrap optional public envelope {data, meta} used by Host middleware."""
    payload = response.json()
    if isinstance(payload, dict) and "data" in payload and "meta" in payload:
        return payload["data"]
    return payload


@pytest.fixture
def client() -> Iterator[TestClient]:
    reset_product_facade_for_tests()
    application = create_app()
    context = AuthenticatedRequestContext(
        tenant_id=ORG_ID,
        actor_id=ActorId("product-actor"),
        correlation_id=CORRELATION_ID,
    )
    application.dependency_overrides[get_authenticated_request_context] = lambda: context
    with TestClient(application) as test_client:
        yield test_client
    application.dependency_overrides.clear()
    reset_product_facade_for_tests()


def test_list_common_agents_returns_pack_catalog(client: TestClient) -> None:
    response = client.get("/api/v1/commons/agents?limit=10")
    assert response.status_code == 200
    payload = body(response)
    assert "items" in payload
    assert payload["page"]["limit"] == 10
    assert len(payload["items"]) >= 1
    first = payload["items"][0]
    assert first["id"]
    assert first["actions"]
    assert any(a["kind"] == "propose_improvement" for a in first["actions"])


def test_agent_detail_and_proposal_flow(client: TestClient) -> None:
    listed = body(client.get("/api/v1/commons/agents?q=video.accessibility&limit=5"))
    agent = next((a for a in listed["items"] if a["id"] == "video.accessibility"), None)
    if agent is None:
        detail = client.get("/api/v1/commons/agents/video.accessibility")
        assert detail.status_code == 200
        agent = body(detail)
        actions = agent["actions"]
    else:
        actions = agent["actions"]
    propose = next(a for a in actions if a["kind"] == "propose_improvement")
    response = client.post(
        "/api/v1/commons/agents/video.accessibility/proposals",
        json={
            "action_reference_id": propose["id"],
            "base_version": "current",
            "summary": "Improve caption acceptance criteria.",
            "evidence_refs": ["run_demo"],
        },
    )
    assert response.status_code == 201
    payload = body(response)
    assert payload["proposal_id"].startswith("prop_")
    assert payload["status"] == "submitted"
    assert payload["target_id"] == "video.accessibility"

    # Reuse of consumed action fails closed
    again = client.post(
        "/api/v1/commons/agents/video.accessibility/proposals",
        json={
            "action_reference_id": propose["id"],
            "summary": "Second attempt",
        },
    )
    assert again.status_code == 403


def test_swarm_create_member_run_activity(client: TestClient) -> None:
    create = client.post(
        "/api/v1/swarms",
        json={"name": "Accessibility swarm", "pattern_ref": "verification-loop"},
    )
    assert create.status_code == 201
    swarm_id = body(create)["swarm_id"]

    detail = client.get(f"/api/v1/swarms/{swarm_id}")
    assert detail.status_code == 200
    actions = {a["kind"]: a["id"] for a in body(detail)["actions"]}
    assert "add_to_swarm" in actions
    assert "run_swarm" in actions

    agents = body(client.get("/api/v1/commons/agents?q=video.accessibility&limit=5"))
    agent = next((a for a in agents["items"] if a["id"] == "video.accessibility"), None)
    assert agent is not None
    add_action = next(a for a in agent["actions"] if a["kind"] == "add_to_swarm")
    member = client.post(
        f"/api/v1/swarms/{swarm_id}/members",
        json={
            "action_reference_id": add_action["id"],
            "agent_id": "video.accessibility",
        },
    )
    assert member.status_code == 200
    assert body(member)["node_id"]

    detail2 = body(client.get(f"/api/v1/swarms/{swarm_id}"))
    run_action = next(a for a in detail2["actions"] if a["kind"] == "run_swarm")
    run = client.post(
        f"/api/v1/swarms/{swarm_id}/runs",
        json={"action_reference_id": run_action["id"], "pin_commons": True},
    )
    assert run.status_code == 200
    run_body = body(run)
    assert run_body["status"] == "queued"
    assert run_body["run_id"].startswith("run_")

    activity = client.get("/api/v1/activity")
    assert activity.status_code == 200
    assert len(body(activity)["items"]) >= 1

    health = client.get("/api/v1/commons/health")
    assert health.status_code == 200
    assert body(health)["total_agents"] >= 1


def test_agent_ab_rollout_requires_action_and_is_sandbox_only(client: TestClient) -> None:
    detail = body(client.get("/api/v1/commons/agents/video.accessibility"))
    actions = detail["actions"]
    ab = next(a for a in actions if a["kind"] == "rollout.ab_test")
    assert ab["eligible"] is True

    denied = client.post(
        "/api/v1/commons/agents/video.accessibility/rollouts",
        json={
            "action_reference_id": "act_not_real",
            "type": "ab_test",
            "baseline_version": "current",
            "candidate_version": "candidate",
        },
    )
    assert denied.status_code == 403

    created = client.post(
        "/api/v1/commons/agents/video.accessibility/rollouts",
        json={
            "action_reference_id": ab["id"],
            "type": "ab_test",
            "baseline_version": "current",
            "candidate_version": "candidate",
            "summary": "A/B canary for accessibility acceptance.",
        },
    )
    assert created.status_code == 201
    payload = body(created)
    assert payload["rollout_id"].startswith("roll_")
    assert payload["status"] == "active_canary"
    assert payload["production_activation"] is False
    assert payload["type"] == "ab_test"

    # Consumed action cannot start another campaign
    again = client.post(
        "/api/v1/commons/agents/video.accessibility/rollouts",
        json={
            "action_reference_id": ab["id"],
            "type": "ab_test",
            "baseline_version": "current",
            "candidate_version": "candidate",
        },
    )
    assert again.status_code == 403

    got = client.get(f"/api/v1/commons/rollouts/{payload['rollout_id']}")
    assert got.status_code == 200
    got_body = body(got)
    assert got_body["agent_id"] == "video.accessibility"
    assert any(c["id"] == "pairwise_preference" for c in got_body["criteria"])

    impact = client.get(f"/api/v1/commons/rollouts/{payload['rollout_id']}/impact")
    assert impact.status_code == 200
    impact_body = body(impact)
    assert impact_body["rollout_id"] == payload["rollout_id"]
    assert impact_body["impact"]

    listed = body(client.get("/api/v1/commons/agents/video.accessibility/rollouts"))
    assert any(i["rollout_id"] == payload["rollout_id"] for i in listed["items"])

    # Safe rollout path
    detail2 = body(client.get("/api/v1/commons/agents/video.accessibility"))
    safe = next(a for a in detail2["actions"] if a["kind"] == "rollout.safe_all")
    safe_resp = client.post(
        "/api/v1/commons/agents/video.accessibility/rollouts",
        json={
            "action_reference_id": safe["id"],
            "type": "safe_rollout",
            "baseline_version": "current",
            "candidate_version": "candidate",
        },
    )
    assert safe_resp.status_code == 201
    assert body(safe_resp)["type"] == "safe_rollout"
    assert body(safe_resp)["production_activation"] is False


def test_patterns_and_events_stream_alias(client: TestClient) -> None:
    patterns = client.get("/api/v1/commons/patterns")
    assert patterns.status_code == 200
    assert len(body(patterns)["items"]) >= 1

    stream = client.get("/api/v1/events/stream?topics=activity:new")
    assert stream.status_code == 200
    assert "text/event-stream" in stream.headers.get("content-type", "")


def test_graph_patch_requires_matching_revision(client: TestClient) -> None:
    create = body(client.post("/api/v1/swarms", json={"name": "Graph swarm"}))
    swarm_id = create["swarm_id"]
    detail = body(client.get(f"/api/v1/swarms/{swarm_id}"))
    edit = next(a for a in detail["actions"] if a["kind"] == "edit_graph")
    bad = client.patch(
        f"/api/v1/swarms/{swarm_id}/graph",
        json={
            "action_reference_id": edit["id"],
            "expected_revision": 99,
            "graph": {"nodes": [], "edges": []},
        },
    )
    assert bad.status_code == 409
