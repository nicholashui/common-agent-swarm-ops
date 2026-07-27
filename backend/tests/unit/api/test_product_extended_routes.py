"""Product extended façade: knowledge, settings, finance, audit, collab, blueprints, developer."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.api.v1.dependencies import AuthenticatedRequestContext, get_authenticated_request_context
from app.api.v1.product_facade import reset_product_facade_for_tests
from app.main import create_app
from app.models.identifiers import ActorId, CorrelationId, OrganizationId

ORG_ID = OrganizationId("org-ext")
CORRELATION_ID = CorrelationId("corr-ext")


def body(response) -> dict:
    payload = response.json()
    if isinstance(payload, dict) and "data" in payload and "meta" in payload:
        return payload["data"]
    return payload


def action_id(bootstrap: dict, kind: str) -> str:
    for a in bootstrap["actions"]:
        if a["kind"] == kind:
            return a["id"]
    raise AssertionError(f"missing action kind {kind}")


@pytest.fixture
def client() -> Iterator[TestClient]:
    reset_product_facade_for_tests()
    application = create_app()
    context = AuthenticatedRequestContext(
        tenant_id=ORG_ID,
        actor_id=ActorId("ext-actor"),
        correlation_id=CORRELATION_ID,
    )
    application.dependency_overrides[get_authenticated_request_context] = lambda: context
    with TestClient(application) as test_client:
        yield test_client
    application.dependency_overrides.clear()
    reset_product_facade_for_tests()


def test_knowledge_settings_finance_audit_profile(client: TestClient) -> None:
    boot = body(client.get("/api/v1/developer/actions"))
    src = client.post(
        "/api/v1/knowledge/sources",
        json={
            "action_reference_id": action_id(boot, "knowledge_add_source"),
            "type": "upload",
            "display_name": "specs",
        },
    )
    assert src.status_code == 201
    assert body(src)["id"].startswith("ksrc_")

    settings = body(client.get("/api/v1/settings/workspace"))
    save = next(a for a in settings["actions"] if a["kind"] == "settings_save")
    put = client.put(
        "/api/v1/settings/workspace",
        json={"action_reference_id": save["id"], "locale": "zh-Hant"},
    )
    assert put.status_code == 200
    assert body(put)["locale"] == "zh-Hant"

    fin = body(client.get("/api/v1/finance/summary"))
    budget = next(a for a in fin["actions"] if a["kind"] == "finance_budget")
    b = client.post(
        "/api/v1/finance/budgets",
        json={"action_reference_id": budget["id"], "budget_limit": 1000, "currency": "USD"},
    )
    assert b.status_code == 200
    assert body(b)["budget_limit"] == 1000

    boot2 = body(client.get("/api/v1/developer/actions"))
    exp = client.post(
        "/api/v1/audit/exports",
        json={"action_reference_id": action_id(boot2, "audit_export"), "format": "csv"},
    )
    assert exp.status_code == 201
    assert body(exp)["download_ref"]

    integ = client.post(
        "/api/v1/audit/integrity-checks",
        json={"action_reference_id": action_id(body(client.get("/api/v1/developer/actions")), "audit_integrity")},
    )
    assert integ.status_code == 200
    assert body(integ)["status"] == "passed"

    prefs = body(client.get("/api/v1/actors/me/preferences"))
    pref_save = prefs["actions"][0]["id"]
    p = client.put(
        "/api/v1/actors/me/preferences",
        json={"action_reference_id": pref_save, "theme": "dark"},
    )
    assert p.status_code == 200
    assert body(p)["theme"] == "dark"


def test_secrets_tokens_webhooks_blueprints_collab(client: TestClient) -> None:
    boot = body(client.get("/api/v1/developer/actions"))
    secret = client.post(
        "/api/v1/secrets",
        json={
            "action_reference_id": action_id(boot, "secret_create"),
            "name": "api-key",
            "value": "super-secret-never-stored-in-response",
        },
    )
    assert secret.status_code == 201
    sec_body = body(secret)
    assert "value" not in sec_body
    assert sec_body["id"].startswith("sec_")

    boot2 = body(client.get("/api/v1/developer/actions"))
    token = client.post(
        "/api/v1/developer/tokens",
        json={
            "action_reference_id": action_id(boot2, "developer_token"),
            "label": "ci",
            "scopes": ["registry.read"],
        },
    )
    assert token.status_code == 201
    assert "token_value_shown_once" in body(token)

    boot3 = body(client.get("/api/v1/developer/actions"))
    wh = client.post(
        "/api/v1/developer/webhooks",
        json={
            "action_reference_id": action_id(boot3, "developer_webhook"),
            "url": "https://example.com/hooks",
            "events": ["run.completed"],
        },
    )
    assert wh.status_code == 201

    bps = body(client.get("/api/v1/blueprints"))
    create = bps["actions"][0]["id"]
    bp = client.post(
        "/api/v1/blueprints",
        json={"action_reference_id": create, "name": "Core pack"},
    )
    assert bp.status_code == 201
    bp_id = body(bp)["id"]

    boot4 = body(client.get("/api/v1/developer/actions"))
    share = client.post(
        "/api/v1/collaboration/shares",
        json={
            "action_reference_id": action_id(boot4, "share_create"),
            "resource_type": "blueprint",
            "resource_id": bp_id,
            "role": "viewer",
        },
    )
    assert share.status_code == 201

    presence = client.get("/api/v1/collaboration/presence")
    assert presence.status_code == 200


def test_notifications_and_run_controls(client: TestClient) -> None:
    n = body(client.get("/api/v1/notifications"))
    mark = n["actions"][0]["id"]
    marked = client.post(
        "/api/v1/notifications/mark-read",
        json={"action_reference_id": mark, "ids": []},
    )
    assert marked.status_code == 200
    assert body(marked)["marked"] >= 1

    cancel = client.post("/api/v1/runs/run_demo/cancel", json={})
    assert cancel.status_code == 200
    assert body(cancel)["status"] == "cancelling"

    replay = client.post("/api/v1/runs/run_demo/replay", json={})
    assert replay.status_code == 200
    assert body(replay)["status"] == "replay_queued"

    openapi = client.get("/api/v1/openapi.json")
    assert openapi.status_code == 200
    assert body(openapi)["openapi"].startswith("3.")


def test_prior_facade_still_works(client: TestClient) -> None:
    agents = client.get("/api/v1/commons/agents?limit=3")
    assert agents.status_code == 200
    assert len(body(agents)["items"]) >= 1
