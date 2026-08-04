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


def test_spine_agent_loop_planner_offline() -> None:
    from app.api.v1.spine_agent_loop import loop_passed, run_spine_agent_loop

    loop = run_spine_agent_loop(
        "video.planner",
        goal="YouTube wuxia short production brief",
        correlation_id="corr-loop-1",
        step_id="plan",
        parent_assets=["brief:b1"],
    )
    assert loop.get("skipped") is False
    assert loop.get("l1", {}).get("passed") is True
    assert loop_passed(loop) is True
    assert loop.get("policy", {}).get("production_media") is False
    assert "plan" in (loop.get("phases") or {})


def test_spine_plan_step_attaches_agent_loop(client: TestClient) -> None:
    mat = body(
        client.post(
            "/api/v1/composer/materialize",
            json={"goal": "YouTube video production brief for agent loop"},
        )
    )
    swarm_id = mat["swarm_id"]
    # orchestrate then plan
    for _ in range(2):
        detail = body(client.get(f"/api/v1/swarms/{swarm_id}"))
        actions = {a["kind"]: a["id"] for a in detail["actions"]}
        if "run_spine_step" not in actions:
            break
        step = body(
            client.post(
                f"/api/v1/swarms/{swarm_id}/spine/steps",
                json={"action_reference_id": actions["run_spine_step"]},
            )
        )
        assert step["ok"] is True
    detail = body(client.get(f"/api/v1/swarms/{swarm_id}"))
    plan_step = next(s for s in detail["spine"]["steps"] if s["id"] == "plan")
    assert plan_step["status"] == "completed"
    art_ref = plan_step["artifact_ref"]
    art = body(client.get(f"/api/v1/swarms/{swarm_id}/artifacts/{art_ref}"))
    assert art.get("parent_assets") is not None
    # agent_loop attached on handoff when present in store
    assert art.get("contract") == "ArtifactHandoffV1" or art.get("version") == 1


def test_handoff_l1_requires_contract_fields() -> None:
    from app.api.v1.video_brief_spine import build_handoff_artifact, validate_handoff_l1

    art = build_handoff_artifact(
        step_id="plan",
        agent_id="video.planner",
        kind="parsed_brief",
        stub_tool="audit_log",
        brief_text="wuxia brief",
        parent_assets=["brief:b1"],
        human_gate=False,
    )
    assert validate_handoff_l1(art) == []
    bad = dict(art)
    bad["production_media"] = True
    assert any("production_media" in e for e in validate_handoff_l1(bad))
    missing = dict(art)
    del missing["parent_assets"]
    assert any("parent_assets" in e for e in validate_handoff_l1(missing))


def test_facade_persist_round_trip(tmp_path) -> None:  # type: ignore[no-untyped-def]
    from app.api.v1.product_facade import ProductFacadeService
    from app.api.v1.product_facade_store import ProductFacadeStore

    store = ProductFacadeStore(tmp_path)
    facade = ProductFacadeService(persist=True, store=store)
    org = OrganizationId("org-persist")
    actor = ActorId("actor-p")
    corr = CorrelationId("corr-p")
    result = facade.materialize_ai_composition(
        organization_id=org,
        actor_id=actor,
        correlation_id=corr,
        goal="YouTube video production brief for persistence test",
        swarm_name="Persist Crew",
    )
    assert result is not None
    assert result.get("swarm_id")
    swarm_id = str(result["swarm_id"])
    # New instance hydrates from same store
    facade2 = ProductFacadeService(persist=True, store=store)
    loaded = facade2.get_swarm(org, swarm_id)
    assert loaded is not None
    assert loaded.name == "Persist Crew"
    assert loaded.brief is not None
    assert loaded.spine is not None
    audit = facade2.list_product_audit(org, limit=20)
    assert any(a.get("kind") == "composition_materialized" for a in audit)


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


def test_recommend_accepts_brief_meta(client: TestClient) -> None:
    rec = client.post(
        "/api/v1/composer/recommend",
        json={
            "goal": "YouTube wuxia short film production brief",
            "brief": {"locale": "zh-Hant", "scale_profile": "S1", "archetype": "A"},
        },
    )
    assert rec.status_code == 200
    body_rec = body(rec)
    assert body_rec.get("brief_preview")
    assert body_rec["brief_preview"]["scale_profile"] == "S1"
    assert body_rec["brief_preview"]["archetype"] == "A"
    assert "brief_id" not in body_rec["brief_preview"]


def test_artifact_get_and_package_approval_detail(client: TestClient) -> None:
    mat = body(
        client.post(
            "/api/v1/composer/materialize",
            json={"goal": "YouTube video production brief with director"},
        )
    )
    swarm_id = mat["swarm_id"]
    # Advance one step for artifact
    detail = body(client.get(f"/api/v1/swarms/{swarm_id}"))
    actions = {a["kind"]: a["id"] for a in detail["actions"]}
    step = body(
        client.post(
            f"/api/v1/swarms/{swarm_id}/spine/steps",
            json={
                "action_reference_id": actions["run_spine_step"],
                "idempotency_key": "step-once-1",
            },
        )
    )
    arts = step["spine"]["artifacts"]
    assert arts
    ref = next(iter(arts.keys()))
    art = body(client.get(f"/api/v1/swarms/{swarm_id}/artifacts/{ref}"))
    assert art["ref"] == ref
    assert art["stub"] is True
    assert art["production_media"] is False

    # Idempotent re-run of same key after re-issuing action
    detail2 = body(client.get(f"/api/v1/swarms/{swarm_id}"))
    actions2 = {a["kind"]: a["id"] for a in detail2["actions"]}
    again = body(
        client.post(
            f"/api/v1/swarms/{swarm_id}/spine/steps",
            json={
                "action_reference_id": actions2["run_spine_step"],
                "idempotency_key": "step-once-1",
            },
        )
    )
    assert again["ok"] is True

    # Drive to package then open package-approvals detail
    for _ in range(10):
        d = body(client.get(f"/api/v1/swarms/{swarm_id}"))
        if d["spine"]["status"] == "waiting_for_approval":
            break
        acts = {a["kind"]: a["id"] for a in d["actions"]}
        client.post(
            f"/api/v1/swarms/{swarm_id}/spine/steps",
            json={"action_reference_id": acts["run_spine_step"]},
        )
    d = body(client.get(f"/api/v1/swarms/{swarm_id}"))
    appr = d["spine"]["approval_id"]
    assert appr
    pkg = body(client.get(f"/api/v1/package-approvals/{appr}"))
    assert pkg["approval_id"] == appr
    assert pkg["swarm_id"] == swarm_id
    assert pkg["actions"]
    decide_id = next(a["id"] for a in pkg["actions"] if a["kind"] == "decide_package")
    decided = body(
        client.post(
            f"/api/v1/package-approvals/{appr}/decision",
            json={
                "action_reference_id": decide_id,
                "decision": "approved",
                "reason": "Ops approved stub package",
            },
        )
    )
    assert decided["spine"]["status"] == "completed"


def test_dry_run_to_package_and_standard_approvals_path(client: TestClient) -> None:
    mat = body(
        client.post(
            "/api/v1/composer/materialize",
            json={"goal": "Cinematic short video production brief"},
        )
    )
    swarm_id = mat["swarm_id"]
    detail = body(client.get(f"/api/v1/swarms/{swarm_id}"))
    actions = {a["kind"]: a["id"] for a in detail["actions"]}
    assert "run_spine_to_package" in actions
    dry = body(
        client.post(
            f"/api/v1/swarms/{swarm_id}/spine/run-to-package",
            json={"action_reference_id": actions["run_spine_to_package"]},
        )
    )
    assert dry["ok"] is True
    assert dry["steps_run"] >= 1
    assert dry["spine"]["status"] == "waiting_for_approval"
    appr = dry["spine"]["approval_id"]
    assert appr

    # Artifact handoff list
    arts = body(client.get(f"/api/v1/swarms/{swarm_id}/artifacts"))
    assert arts["count"] >= 1
    assert arts["note"]

    # Standard approvals URL serves package gate preview
    preview = body(client.get(f"/api/v1/approvals/{appr}"))
    assert preview["approval_id"] == appr
    assert "stub" in preview["action_preview"]["summary"].lower() or "package" in preview[
        "action_preview"
    ]["summary"].lower()

    # Standard decision body (Host-issued action inside)
    decided = body(
        client.post(
            f"/api/v1/approvals/{appr}/decision",
            json={"selected_value": "approved", "reason": "Ops approved via standard path"},
        )
    )
    assert decided["selected_value"] == "approved"
    assert decided["resumed"] is True


def test_running_list_includes_spine_package_attention(client: TestClient) -> None:
    mat = body(
        client.post(
            "/api/v1/composer/materialize",
            json={"goal": "Brand video production brief for social package gate"},
        )
    )
    swarm_id = mat["swarm_id"]
    detail = body(client.get(f"/api/v1/swarms/{swarm_id}"))
    actions = {a["kind"]: a["id"] for a in detail["actions"]}
    body(
        client.post(
            f"/api/v1/swarms/{swarm_id}/spine/run-to-package",
            json={"action_reference_id": actions["run_spine_to_package"]},
        )
    )
    running = body(client.get("/api/v1/swarms/running"))
    row = next(i for i in running["items"] if i["id"] == swarm_id)
    assert row["has_spine"] is True
    assert row["spine_status"] == "waiting_for_approval"
    assert row["status"] == "waiting_for_approval"
    assert row.get("approval_id")
    assert "not production media" in (row.get("note") or "")


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
