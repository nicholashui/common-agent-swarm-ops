"""Host API: fleet agent loops (offline Plan→Act→Self-Review for pack agents)."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query, status
from pydantic import Field

from app.api.v1.dependencies import AuthenticatedRequestContext, get_authenticated_request_context
from app.api.v1.errors import PublicApiException
from app.api.v1.product_facade import ProductFacadeService, get_product_facade
from app.api.v1.schemas import PublicError, StrictSchema
from app.video.agent_loop_service import get_agent_loop_service

router = APIRouter(prefix="/agent-loops", tags=["agent-loops"])


class AgentLoopRunRequest(StrictSchema):
    goal: str = Field(min_length=1, max_length=2_000)
    correlation_id: str | None = Field(default=None, max_length=100)
    allow_production: bool = False
    allow_network: bool = False


class AgentLoopCrewRequest(StrictSchema):
    goal: str = Field(min_length=1, max_length=2_000)
    agent_ids: list[str] = Field(min_length=1, max_length=120)
    correlation_id: str | None = Field(default=None, max_length=100)
    stop_on_failure: bool = False
    parallel: bool = False
    max_workers: int = Field(default=4, ge=1, le=16)


class WorkflowLoopRunRequest(StrictSchema):
    goal: str = Field(min_length=1, max_length=2_000)
    correlation_id: str | None = Field(default=None, max_length=100)
    stop_on_failure: bool = True
    max_nodes: int = Field(default=32, ge=1, le=64)


class FleetSampleRequest(StrictSchema):
    goal: str = Field(min_length=1, max_length=2_000)
    limit: int = Field(default=8, ge=1, le=32)


def _bad(correlation_id: str, message: str) -> None:
    raise PublicApiException(
        status_code=status.HTTP_400_BAD_REQUEST,
        error=PublicError(
            code="validation_failed",
            message=message,
            correlation_id=correlation_id,
            retryable=False,
        ),
    )


def _denied(correlation_id: str, message: str) -> None:
    raise PublicApiException(
        status_code=status.HTTP_403_FORBIDDEN,
        error=PublicError(
            code="authorization_denied",
            message=message,
            correlation_id=correlation_id,
            retryable=False,
        ),
    )


@router.get("/inventory")
async def list_agent_loop_inventory(
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    refresh: Annotated[bool, Query()] = False,
) -> dict[str, Any]:
    """List all video pack agents and whether offline loops can load (fleet inventory)."""
    service = get_agent_loop_service()
    items = service.list_inventory(refresh=refresh)
    summary = service.inventory_summary()
    return {
        **summary,
        "items": items,
        "correlation_id": str(context.correlation_id),
    }


@router.get("/runs")
async def list_agent_loop_runs(
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
) -> dict[str, Any]:
    service = get_agent_loop_service()
    return {
        "items": service.list_recent_runs(str(context.organization_id), limit=limit),
        "page": {"next_cursor": None, "limit": limit},
        "correlation_id": str(context.correlation_id),
    }


@router.post("/agents/{agent_id}/run")
async def run_agent_loop(
    agent_id: str,
    request: AgentLoopRunRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
) -> dict[str, Any]:
    """Run Plan→Act→Self-Review for one pack agent (offline, fail-closed)."""
    service = get_agent_loop_service()
    result = service.run(
        agent_id,
        organization_id=str(context.organization_id),
        goal=request.goal,
        correlation_id=request.correlation_id or str(context.correlation_id),
        allow_production=request.allow_production,
        allow_network=request.allow_network,
    )
    if result.get("error") and result.get("ok") is False and "required" in str(result.get("error")):
        _bad(str(context.correlation_id), str(result["error"]))
    if result.get("error") and "not enabled" in str(result.get("error")):
        _denied(str(context.correlation_id), str(result["error"]))
    return result


@router.post("/crew")
async def run_agent_loop_crew(
    request: AgentLoopCrewRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
) -> dict[str, Any]:
    """Run offline loops for an explicit crew of pack agent ids."""
    service = get_agent_loop_service()
    return service.run_crew(
        list(request.agent_ids),
        organization_id=str(context.organization_id),
        goal=request.goal,
        correlation_id=request.correlation_id or str(context.correlation_id),
        stop_on_failure=request.stop_on_failure,
        parallel=request.parallel,
        max_workers=request.max_workers,
    )


@router.get("/tools")
async def list_agent_loop_tools(
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
) -> dict[str, Any]:
    """Host tool catalog for agent-loop Act phase (stub default, live gated)."""
    from app.video.tool_activation import get_host_tool_registry

    catalog = get_host_tool_registry().list_catalog()
    return {
        **catalog,
        "correlation_id": str(context.correlation_id),
    }


@router.get("/memory")
async def list_project_memory(
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
) -> dict[str, Any]:
    service = get_agent_loop_service()
    return {
        "items": service.project_memory(str(context.organization_id), limit=limit),
        "note": (
            "Project memory from agent loops (handoff refs). "
            "Durable when CASOPS_PRODUCT_FACADE_PERSIST is enabled."
        ),
        "correlation_id": str(context.correlation_id),
    }


@router.get("/critiques")
async def list_loop_critiques(
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
) -> dict[str, Any]:
    service = get_agent_loop_service()
    return {
        "items": service.critique_log(str(context.organization_id), limit=limit),
        "note": (
            "Critique messages emitted during offline loops. "
            "Durable when CASOPS_PRODUCT_FACADE_PERSIST is enabled."
        ),
        "correlation_id": str(context.correlation_id),
    }


@router.get("/tool-invocations")
async def list_tool_invocations(
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
) -> dict[str, Any]:
    """Append-only tool invocation log from offline agent-loop Act phases."""
    service = get_agent_loop_service()
    return {
        "items": service.tool_invocation_log(str(context.organization_id), limit=limit),
        "note": (
            "Durable JSONL when façade persist is enabled; empty when memory-only."
        ),
        "correlation_id": str(context.correlation_id),
    }


@router.post("/fleet-sample")
async def run_fleet_sample(
    request: FleetSampleRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
) -> dict[str, Any]:
    """Run offline loops for a bounded sample of the pack fleet."""
    service = get_agent_loop_service()
    return service.run_fleet_sample(
        organization_id=str(context.organization_id),
        goal=request.goal,
        limit=request.limit,
    )


@router.get("/workflows")
async def list_workflow_loops(
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
) -> dict[str, Any]:
    """List DNA/pack workflow graphs available for offline agent-loop execution."""
    from app.video.workflow_loop_runner import WorkflowLoopRunner

    runner = WorkflowLoopRunner()
    items = runner.list_available_workflows()
    return {
        "items": items,
        "count": len(items),
        "note": "Offline sequential loops · not production media",
        "correlation_id": str(context.correlation_id),
    }


@router.post("/workflows/{workflow_id}/run")
async def run_workflow_loops(
    workflow_id: str,
    request: WorkflowLoopRunRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> dict[str, Any]:
    """Run a DNA/pack workflow as ordered offline agent loops + project memory."""
    from app.video.workflow_loop_runner import WorkflowLoopRunner

    runner = WorkflowLoopRunner()
    result = runner.run(
        workflow_id,
        organization_id=str(context.organization_id),
        goal=request.goal,
        correlation_id=request.correlation_id or str(context.correlation_id),
        stop_on_failure=request.stop_on_failure,
        max_nodes=request.max_nodes,
    )
    if result.get("error") and result.get("ok") is False:
        _bad(str(context.correlation_id), str(result["error"]))
    facade._append_audit(  # noqa: SLF001 — product audit seam for workflow loops
        organization_id=str(context.organization_id),
        kind="workflow_loops",
        subject_reference=workflow_id,
        summary=(
            f"Workflow loops {workflow_id} completed={result.get('completed')} "
            f"passed={result.get('passed')}"
        ),
        correlation_id=str(context.correlation_id),
        payload={
            "workflow_id": workflow_id,
            "passed": result.get("passed"),
            "failed": result.get("failed"),
        },
    )
    return result
