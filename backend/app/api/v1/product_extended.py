"""Remaining product façade routes: knowledge, settings, finance, audit, collab, blueprints, developer, profile, notifications, runs control."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, status
from pydantic import Field

from app.api.v1.dependencies import AuthenticatedRequestContext, get_authenticated_request_context
from app.api.v1.errors import PublicApiException
from app.api.v1.product_facade import ProductFacadeService, get_product_facade
from app.api.v1.schemas import PublicError, StrictSchema

router = APIRouter(tags=["product-extended"])


def _denied(correlation_id: str, message: str = "Protected resource access is not permitted.") -> None:
    raise PublicApiException(
        status_code=status.HTTP_403_FORBIDDEN,
        error=PublicError(
            code="authorization_denied",
            message=message,
            correlation_id=correlation_id,
            retryable=False,
        ),
    )


class ActionBody(StrictSchema):
    action_reference_id: str = Field(min_length=1, max_length=200)


class KnowledgeSourceCreate(ActionBody):
    type: str = Field(default="upload", max_length=50)
    display_name: str = Field(default="source", max_length=200)
    uri: str | None = Field(default=None, max_length=2_000)
    retention_class: str = Field(default="standard", max_length=50)


class KnowledgeContribute(ActionBody):
    summary: str = Field(min_length=1, max_length=2_000)
    source_refs: list[str] = Field(default_factory=list, max_length=50)


class SettingsPut(ActionBody):
    locale: str | None = Field(default=None, max_length=20)
    timezone: str | None = Field(default=None, max_length=80)
    demo_banner: bool | None = None


class ProviderCreate(ActionBody):
    name: str = Field(min_length=1, max_length=200)
    kind: str = Field(default="llm", max_length=50)


class SecretCreate(ActionBody):
    name: str = Field(min_length=1, max_length=200)
    # Value accepted once then discarded; never returned.
    value: str = Field(min_length=1, max_length=8_000)


class InviteCreate(ActionBody):
    email: str = Field(min_length=3, max_length=320)
    role: str = Field(default="viewer", max_length=50)


class BudgetPut(ActionBody):
    budget_limit: float | None = None
    currency: str = Field(default="USD", max_length=8)


class ExportCreate(ActionBody):
    format: str = Field(default="json", max_length=10)


class MarkReadBody(ActionBody):
    ids: list[str] = Field(default_factory=list, max_length=500)


class PreferencesPut(ActionBody):
    theme: str | None = Field(default=None, max_length=40)
    density: str | None = Field(default=None, max_length=40)
    locale: str | None = Field(default=None, max_length=20)


class ShareCreate(ActionBody):
    resource_type: str = Field(default="swarm", max_length=50)
    resource_id: str = Field(min_length=1, max_length=200)
    role: str = Field(default="viewer", max_length=50)


class BlueprintCreate(ActionBody):
    name: str = Field(min_length=1, max_length=200)


class BlueprintImport(ActionBody):
    format: str = Field(default="json", max_length=10)
    content_ref: str | None = Field(default=None, max_length=500)


class DevTokenCreate(ActionBody):
    label: str = Field(default="api-token", max_length=200)
    scopes: list[str] = Field(default_factory=list, max_length=20)


class WebhookCreate(ActionBody):
    url: str = Field(min_length=1, max_length=2_000)
    events: list[str] = Field(default_factory=list, max_length=50)


class RunControlBody(StrictSchema):
    action_reference_id: str | None = Field(default=None, max_length=200)
    reason: str | None = Field(default=None, max_length=2_000)


# --- Knowledge ---


@router.get("/knowledge/sources")
async def list_knowledge_sources(
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> dict[str, Any]:
    return facade.list_knowledge_sources(context.organization_id)


@router.post("/knowledge/sources", status_code=status.HTTP_201_CREATED)
async def add_knowledge_source(
    request: KnowledgeSourceCreate,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> dict[str, Any]:
    result = facade.add_knowledge_source(
        context.organization_id,
        action_reference_id=request.action_reference_id,
        payload=request.model_dump(),
    )
    if result is None:
        _denied(str(context.correlation_id), "Add source requires eligible action reference.")
    assert result is not None
    return result


@router.post("/knowledge/sources/{source_id}/sync")
async def sync_knowledge_source(
    source_id: str,
    request: ActionBody,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> dict[str, Any]:
    result = facade.sync_knowledge_source(
        context.organization_id, source_id, request.action_reference_id
    )
    if result is None:
        _denied(str(context.correlation_id))
    assert result is not None
    return result


@router.post("/knowledge/contributions", status_code=status.HTTP_201_CREATED)
async def contribute_knowledge(
    request: KnowledgeContribute,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> dict[str, Any]:
    result = facade.contribute_knowledge(
        context.organization_id,
        context.actor_id,
        request.action_reference_id,
        request.model_dump(),
    )
    if result is None:
        _denied(str(context.correlation_id))
    assert result is not None
    return result


# --- Settings / secrets ---


@router.get("/settings/workspace")
async def get_workspace_settings(
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> dict[str, Any]:
    return facade.get_workspace_settings(context.organization_id)


@router.put("/settings/workspace")
async def put_workspace_settings(
    request: SettingsPut,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> dict[str, Any]:
    result = facade.put_workspace_settings(
        context.organization_id,
        request.action_reference_id,
        request.model_dump(exclude_none=True),
    )
    if result is None:
        _denied(str(context.correlation_id))
    assert result is not None
    return result


@router.post("/settings/providers", status_code=status.HTTP_201_CREATED)
async def add_provider(
    request: ProviderCreate,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> dict[str, Any]:
    result = facade.add_provider(
        context.organization_id, request.action_reference_id, request.model_dump()
    )
    if result is None:
        _denied(str(context.correlation_id))
    assert result is not None
    return result


@router.post("/settings/providers/{provider_id}/test")
async def test_provider(
    provider_id: str,
    request: ActionBody,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> dict[str, Any]:
    result = facade.test_provider(
        context.organization_id, provider_id, request.action_reference_id
    )
    if result is None:
        _denied(str(context.correlation_id))
    assert result is not None
    return result


@router.post("/settings/providers/{provider_id}/models:fetch")
async def fetch_provider_models(
    provider_id: str,
    request: ActionBody,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> dict[str, Any]:
    result = facade.fetch_provider_models(
        context.organization_id, provider_id, request.action_reference_id
    )
    if result is None:
        _denied(str(context.correlation_id))
    assert result is not None
    return result


@router.post("/secrets", status_code=status.HTTP_201_CREATED)
async def create_secret(
    request: SecretCreate,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> dict[str, Any]:
    # Discard value immediately after acceptance.
    result = facade.create_secret(
        context.organization_id,
        request.action_reference_id,
        {"name": request.name},
    )
    if result is None:
        _denied(str(context.correlation_id))
    assert result is not None
    return result


@router.post("/secrets/{secret_id}/rotate")
async def rotate_secret(
    secret_id: str,
    request: ActionBody,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> dict[str, Any]:
    result = facade.rotate_secret(
        context.organization_id, secret_id, request.action_reference_id
    )
    if result is None:
        _denied(str(context.correlation_id))
    assert result is not None
    return result


@router.post("/secrets/{secret_id}/reveal")
async def reveal_secret(
    secret_id: str,
    request: ActionBody,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> dict[str, Any]:
    result = facade.reveal_secret(
        context.organization_id, secret_id, request.action_reference_id
    )
    if result is None:
        _denied(str(context.correlation_id))
    assert result is not None
    return result


@router.post("/workspace/invites", status_code=status.HTTP_201_CREATED)
async def invite_member(
    request: InviteCreate,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> dict[str, Any]:
    result = facade.invite_member(
        context.organization_id, request.action_reference_id, request.model_dump()
    )
    if result is None:
        _denied(str(context.correlation_id))
    assert result is not None
    return result


# --- Finance / audit ---


@router.get("/finance/summary")
async def finance_summary(
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> dict[str, Any]:
    return facade.finance_summary(context.organization_id)


@router.post("/finance/budgets")
async def set_budget(
    request: BudgetPut,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> dict[str, Any]:
    result = facade.set_budget(
        context.organization_id, request.action_reference_id, request.model_dump()
    )
    if result is None:
        _denied(str(context.correlation_id))
    assert result is not None
    return result


@router.post("/finance/exports", status_code=status.HTTP_201_CREATED)
async def finance_export(
    request: ExportCreate,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> dict[str, Any]:
    result = facade.create_export_job(
        context.organization_id,
        request.action_reference_id,
        domain="finance",
        format=request.format,
    )
    if result is None:
        _denied(str(context.correlation_id))
    assert result is not None
    return result


@router.post("/audit/exports", status_code=status.HTTP_201_CREATED)
async def audit_export(
    request: ExportCreate,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> dict[str, Any]:
    result = facade.create_export_job(
        context.organization_id,
        request.action_reference_id,
        domain="audit",
        format=request.format,
    )
    if result is None:
        _denied(str(context.correlation_id))
    assert result is not None
    return result


@router.post("/audit/integrity-checks")
async def audit_integrity(
    request: ActionBody,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> dict[str, Any]:
    result = facade.audit_integrity_check(
        context.organization_id, request.action_reference_id
    )
    if result is None:
        _denied(str(context.correlation_id))
    assert result is not None
    return result


# --- Notifications / profile ---


@router.get("/notifications")
async def list_notifications(
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> dict[str, Any]:
    return facade.list_notifications(context.organization_id)


@router.post("/notifications/mark-read")
async def mark_notifications_read(
    request: MarkReadBody,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> dict[str, Any]:
    result = facade.mark_notifications_read(
        context.organization_id, request.action_reference_id, list(request.ids)
    )
    if result is None:
        _denied(str(context.correlation_id))
    assert result is not None
    return result


@router.get("/actors/me/preferences")
async def get_preferences(
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> dict[str, Any]:
    return facade.get_preferences(context.organization_id, context.actor_id)


@router.put("/actors/me/preferences")
async def put_preferences(
    request: PreferencesPut,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> dict[str, Any]:
    result = facade.put_preferences(
        context.organization_id,
        context.actor_id,
        request.action_reference_id,
        request.model_dump(exclude_none=True),
    )
    if result is None:
        _denied(str(context.correlation_id))
    assert result is not None
    return result


# --- Collaboration / blueprints ---


@router.post("/collaboration/shares", status_code=status.HTTP_201_CREATED)
async def create_share(
    request: ShareCreate,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> dict[str, Any]:
    result = facade.create_share(
        context.organization_id, request.action_reference_id, request.model_dump()
    )
    if result is None:
        _denied(str(context.correlation_id))
    assert result is not None
    return result


@router.get("/collaboration/presence")
async def collaboration_presence(
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> dict[str, Any]:
    return facade.presence(context.organization_id)


@router.get("/blueprints")
async def list_blueprints(
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> dict[str, Any]:
    return facade.list_blueprints(context.organization_id)


@router.post("/blueprints", status_code=status.HTTP_201_CREATED)
async def create_blueprint(
    request: BlueprintCreate,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> dict[str, Any]:
    result = facade.create_blueprint(
        context.organization_id, request.action_reference_id, request.model_dump()
    )
    if result is None:
        _denied(str(context.correlation_id))
    assert result is not None
    return result


@router.post("/blueprints/{blueprint_id}/deploy")
async def deploy_blueprint(
    blueprint_id: str,
    request: ActionBody,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> dict[str, Any]:
    result = facade.deploy_blueprint(
        context.organization_id, blueprint_id, request.action_reference_id
    )
    if result is None:
        _denied(str(context.correlation_id))
    assert result is not None
    return result


@router.post("/blueprints/{blueprint_id}/forks", status_code=status.HTTP_201_CREATED)
async def fork_blueprint(
    blueprint_id: str,
    request: ActionBody,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> dict[str, Any]:
    result = facade.fork_blueprint(
        context.organization_id, blueprint_id, request.action_reference_id
    )
    if result is None:
        _denied(str(context.correlation_id))
    assert result is not None
    return result


@router.post("/blueprints/import", status_code=status.HTTP_201_CREATED)
async def import_blueprint(
    request: BlueprintImport,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> dict[str, Any]:
    result = facade.import_blueprint(
        context.organization_id, request.action_reference_id, request.model_dump()
    )
    if result is None:
        _denied(str(context.correlation_id))
    assert result is not None
    return result


# --- Developer platform ---


@router.post("/developer/tokens", status_code=status.HTTP_201_CREATED)
async def create_dev_token(
    request: DevTokenCreate,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> dict[str, Any]:
    result = facade.create_dev_token(
        context.organization_id, request.action_reference_id, request.model_dump()
    )
    if result is None:
        _denied(str(context.correlation_id))
    assert result is not None
    return result


@router.post("/developer/webhooks", status_code=status.HTTP_201_CREATED)
async def create_webhook(
    request: WebhookCreate,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> dict[str, Any]:
    result = facade.create_webhook(
        context.organization_id, request.action_reference_id, request.model_dump()
    )
    if result is None:
        _denied(str(context.correlation_id))
    assert result is not None
    return result


@router.get("/developer/actions")
async def developer_bootstrap_actions(
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> dict[str, Any]:
    """Issue action references for developer portal mutations."""
    return {
        "actions": [
            facade.issue_generic_action(
                context.organization_id, "developer_token", "Create token", "developer"
            ),
            facade.issue_generic_action(
                context.organization_id, "developer_webhook", "Create webhook", "developer"
            ),
            facade.issue_generic_action(
                context.organization_id, "knowledge_add_source", "Add knowledge source", "knowledge"
            ),
            facade.issue_generic_action(
                context.organization_id, "settings_add_provider", "Add provider", "providers"
            ),
            facade.issue_generic_action(
                context.organization_id, "secret_create", "Create secret", "secrets"
            ),
            facade.issue_generic_action(
                context.organization_id, "workspace_invite", "Invite member", "workspace"
            ),
            facade.issue_generic_action(
                context.organization_id, "share_create", "Share", "collaboration"
            ),
            facade.issue_generic_action(
                context.organization_id, "blueprint_create", "Create blueprint", "blueprints"
            ),
            facade.issue_generic_action(
                context.organization_id, "finance_export", "Export finance", "finance"
            ),
            facade.issue_generic_action(
                context.organization_id, "audit_export", "Export audit", "audit"
            ),
            facade.issue_generic_action(
                context.organization_id, "audit_integrity", "Integrity check", "audit"
            ),
            facade.issue_generic_action(
                context.organization_id, "run_cancel", "Cancel run", "runs"
            ),
            facade.issue_generic_action(
                context.organization_id, "run_replay", "Replay run", "runs"
            ),
        ]
    }


# --- Product runs façade aliases ---


@router.post("/runs/{run_id}/cancel")
async def cancel_run(
    run_id: str,
    request: RunControlBody,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> dict[str, Any]:
    return facade.record_run_control(
        context.organization_id,
        run_id,
        kind="cancel",
        action_reference_id=request.action_reference_id,
    )


@router.post("/runs/{run_id}/replay")
async def replay_run(
    run_id: str,
    request: RunControlBody,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> dict[str, Any]:
    return facade.record_run_control(
        context.organization_id,
        run_id,
        kind="replay",
        action_reference_id=request.action_reference_id,
    )


@router.get("/openapi.json")
async def public_openapi_stub(
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
) -> dict[str, Any]:
    """Minimal OpenAPI discovery stub for product tooling (full contract via release pipeline)."""
    _ = context
    return {
        "openapi": "3.1.0",
        "info": {
            "title": "Generic Swarm Business OS Host",
            "version": "0.1.0",
            "description": "Product façade + control-plane routes under /api/v1",
        },
        "paths": {
            "/api/v1/commons/agents": {"get": {"summary": "List common agents"}},
            "/api/v1/swarms": {"post": {"summary": "Create swarm draft"}},
            "/api/v1/activity": {"get": {"summary": "Activity feed"}},
            "/api/v1/events/stream": {"get": {"summary": "Multi-topic SSE"}},
        },
    }
