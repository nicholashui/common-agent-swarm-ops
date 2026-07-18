# ruff: noqa: E501
"""Versioned run, dispatch, topology, and observation routes."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from math import isfinite
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.api.v1.dependencies import AuthenticatedRequestContext, get_authenticated_request_context
from app.api.v1.errors import require_value
from app.api.v1.schemas import (
    ActionPreviewResponse,
    DispatchRequest,
    DispatchResponse,
    GraphStateResponse,
    OperatorEventResponse,
    RunCreateRequest,
    RunResponse,
    ToolEffectResponse,
    TopologyEdgeResponse,
    TopologyNodeResponse,
    TopologyResponse,
)
from app.api.v1.services import (
    ControlPlaneServices,
    OperatorEvent,
    StoredDefinition,
    get_control_plane_services,
)
from app.governance.approvals import ActionPreview
from app.models.identifiers import RunId, WorkflowDefinitionId
from app.models.redaction import REDACTED
from app.models.runs import RunRecord

router = APIRouter(tags=["runs", "observation"])


@router.post("/workflows/{workflow_id}/run", response_model=RunResponse, status_code=status.HTTP_201_CREATED)
async def create_run(
    workflow_id: str,
    request: RunCreateRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    services: Annotated[ControlPlaneServices, Depends(get_control_plane_services)],
) -> RunResponse:
    """Create an organization-scoped queued run from a prior registered definition version."""
    record = require_value(
        services.create_run(
            context.organization_id,
            context.correlation_id,
            WorkflowDefinitionId(workflow_id),
            request.version,
        )
    )
    events = require_value(services.get_events(context.organization_id, record.run_id, context.correlation_id))
    preview = next((event.action_preview for event in events if event.action_preview is not None), None)
    return _run_response(record, _preview_response(preview, record.metadata.updated_at) if preview else None)


@router.post("/workflow-runs/dispatch", response_model=DispatchResponse)
async def dispatch_run(
    request: DispatchRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    services: Annotated[ControlPlaneServices, Depends(get_control_plane_services)],
) -> DispatchResponse:
    """Return a preview first, then dispatch only after an explicit confirmation."""
    record, preview, outcome = require_value(
        services.preview_or_dispatch(
            context.organization_id,
            context.correlation_id,
            RunId(request.run_id),
            request.idempotency_key,
            request.confirm,
        )
    )
    return DispatchResponse(
        run_id=record.run_id,
        status=record.status,
        executed=outcome is not None,
        preview=_preview_response(preview, record.metadata.updated_at),
        idempotent=outcome.is_idempotent if outcome is not None else False,
        retry_permitted=outcome.retry_permitted if outcome is not None else False,
    )


@router.get("/workflow-runs/{run_id}", response_model=RunResponse)
async def read_run(
    run_id: str,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    services: Annotated[ControlPlaneServices, Depends(get_control_plane_services)],
) -> RunResponse:
    """Return only a redacted projection of a run owned by the trusted organization."""
    record = require_value(services.get_run(context.organization_id, RunId(run_id), context.correlation_id))
    events = require_value(services.get_events(context.organization_id, record.run_id, context.correlation_id))
    preview = next((event.action_preview for event in events if event.action_preview is not None), None)
    return _run_response(record, _preview_response(preview, record.metadata.updated_at) if preview else None)


@router.get("/workflows/{workflow_id}/topology", response_model=TopologyResponse)
async def read_topology(
    workflow_id: str,
    version: Annotated[str, Query(min_length=1, max_length=100)],
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    services: Annotated[ControlPlaneServices, Depends(get_control_plane_services)],
) -> TopologyResponse:
    """Expose a safe, versioned topology without revealing raw workflow payloads."""
    definition = require_value(
        services.get_definition(
            context.organization_id,
            WorkflowDefinitionId(workflow_id),
            version,
            context.correlation_id,
        )
    )
    return _topology_response(definition)


@router.get("/workflow-runs/{run_id}/graph-state", response_model=GraphStateResponse)
async def read_graph_state(
    run_id: str,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    services: Annotated[ControlPlaneServices, Depends(get_control_plane_services)],
) -> GraphStateResponse:
    """Return an organization-filtered operational graph-state projection."""
    record = require_value(services.get_run(context.organization_id, RunId(run_id), context.correlation_id))
    events = require_value(services.get_events(context.organization_id, record.run_id, context.correlation_id))
    return GraphStateResponse(
        run_id=record.run_id,
        status=record.status,
        engine=record.engine,
        graph_id=record.graph_id,
        graph_thread_id=record.graph_thread_id,
        updated_at=record.metadata.updated_at,
        failure_code=record.failure.code if record.failure is not None else None,
        tool_effects=[
            ToolEffectResponse(
                adapter_id=effect.adapter_id,
                outcome=effect.outcome,
                effect_digest=effect.effect_digest,
                completed_at=effect.completed_at,
                reversible=effect.reversible,
                compensation_reference=effect.compensation_reference,
            )
            for effect in record.tool_effects
        ],
        action_previews=[
            _preview_response(event.action_preview, event.recorded_at)
            for event in events
            if event.action_preview is not None
        ],
    )


@router.get("/workflow-runs/{run_id}/events", response_model=list[OperatorEventResponse])
async def read_run_events(
    run_id: str,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    services: Annotated[ControlPlaneServices, Depends(get_control_plane_services)],
) -> list[OperatorEventResponse]:
    """Return preview-before-effect observation events for one organization-scoped run."""
    events = require_value(services.get_events(context.organization_id, RunId(run_id), context.correlation_id))
    return [_event_response(event) for event in events]


def _run_response(record: RunRecord, preview: ActionPreviewResponse | None) -> RunResponse:
    projection = record.to_projection()
    return RunResponse(
        run_id=record.run_id,
        workflow_id=record.workflow_definition_id,
        workflow_version=record.workflow_definition_version,
        status=record.status,
        engine=record.engine,
        correlation_id=projection.correlation_id,
        updated_at=projection.updated_at,
        output=_json_safe_mapping(projection.output) if projection.output is not None else None,
        failure_code=projection.failure_code,
        action_preview=preview,
    )


def _topology_response(definition: StoredDefinition) -> TopologyResponse:
    workflow_id = definition.workflow_id
    version = definition.version
    values = definition.definition
    engine = values.get("engine")
    assert isinstance(engine, str)
    if values.get("definition_type") == "pack_graph":
        raw_nodes = values.get("nodes")
        raw_edges = values.get("edges")
        nodes = [_node_response(node) for node in raw_nodes if isinstance(node, Mapping)] if isinstance(raw_nodes, list) else []
        edges = [_edge_response(edge) for edge in raw_edges if isinstance(edge, Mapping)] if isinstance(raw_edges, list) else []
        pattern = values.get("pattern")
        return TopologyResponse(
            workflow_id=workflow_id,
            version=version,
            engine=engine,
            pattern=pattern if isinstance(pattern, str) else "unknown",
            nodes=nodes,
            edges=edges,
        )
    raw_steps = values.get("steps")
    nodes = [_node_response(step) for step in raw_steps if isinstance(step, Mapping)] if isinstance(raw_steps, list) else []
    edges = [
        TopologyEdgeResponse(source=nodes[index].node_id, target=nodes[index + 1].node_id, max_traversals=1)
        for index in range(max(0, len(nodes) - 1))
    ]
    return TopologyResponse(
        workflow_id=workflow_id,
        version=version,
        engine=engine,
        pattern="pipeline",
        nodes=nodes,
        edges=edges,
    )


def _node_response(value: Mapping[str, object]) -> TopologyNodeResponse:
    node_id = value.get("id")
    agent_id = value.get("agent_id")
    tools = value.get("tool_ids")
    assert isinstance(node_id, str) and isinstance(agent_id, str) and isinstance(tools, list)
    return TopologyNodeResponse(
        node_id=node_id,
        agent_id=agent_id,
        tool_ids=[tool for tool in tools if isinstance(tool, str)],
    )


def _edge_response(value: Mapping[str, object]) -> TopologyEdgeResponse:
    source = value.get("from")
    target = value.get("to")
    traversals = value.get("max_traversals")
    assert isinstance(source, str) and isinstance(target, str) and isinstance(traversals, int)
    return TopologyEdgeResponse(source=source, target=target, max_traversals=traversals)


def _event_response(event: OperatorEvent) -> OperatorEventResponse:
    return OperatorEventResponse(
        kind=event.kind,
        recorded_at=event.recorded_at,
        detail=event.detail,
        action_preview=(
            _preview_response(event.action_preview, event.recorded_at)
            if event.action_preview is not None
            else None
        ),
    )


def _preview_response(preview: ActionPreview, emitted_at: datetime) -> ActionPreviewResponse:
    return ActionPreviewResponse(
        action_id=preview.action_id,
        summary=preview.summary,
        intended_effect=preview.intended_effect,
        emitted_at=emitted_at,
        rollback_preview=preview.rollback_preview,
        supporting_evidence=list(preview.supporting_evidence),
        confidence=preview.confidence,
        uncertainty=preview.uncertainty,
        correction_control=preview.correction_control,
    )


def _json_safe_mapping(values: Mapping[str, object]) -> dict[str, object]:
    return {str(key): _json_safe(value) for key, value in values.items()}


def _json_safe(value: object) -> object:
    if value is None or isinstance(value, bool | int | str):
        return value
    if isinstance(value, float):
        return value if isfinite(value) else REDACTED
    if isinstance(value, Mapping):
        return _json_safe_mapping({str(key): item for key, item in value.items()})
    if isinstance(value, list | tuple | set | frozenset):
        return [_json_safe(item) for item in value]
    return REDACTED
