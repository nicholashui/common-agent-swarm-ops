"""Product façade: Common Registry agents, patterns, proposals, forks."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query, status

from app.api.v1.dependencies import AuthenticatedRequestContext, get_authenticated_request_context
from app.api.v1.errors import PublicApiException
from app.api.v1.product_facade import ProductFacadeService, get_product_facade
from app.api.v1.schemas import (
    AgentForkRequest,
    AgentForkResponse,
    PatternInstantiateRequest,
    PlaygroundRunRequest,
    ProposalCreateRequest,
    ProposalCreateResponse,
    PublicError,
    SwarmCreateResponse,
)

router = APIRouter(prefix="/commons", tags=["commons"])


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


def _not_found(correlation_id: str) -> None:
    # Match host fail-closed: not found collapses to authorization denial for protected resources.
    _denied(correlation_id)


def _validation(correlation_id: str, message: str) -> None:
    raise PublicApiException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        error=PublicError(
            code="validation_failed",
            message=message,
            correlation_id=correlation_id,
            retryable=False,
        ),
    )


@router.get("/agents")
async def list_common_agents(
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
    q: Annotated[str | None, Query(max_length=200)] = None,
    domain: Annotated[str | None, Query(max_length=100)] = None,
    pack: Annotated[str | None, Query(max_length=100)] = None,
    status_filter: Annotated[str | None, Query(alias="status", max_length=50)] = None,
    cursor: Annotated[str | None, Query(max_length=50)] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 36,
) -> dict[str, Any]:
    """List redacted common-agent catalog cards with action references."""
    return facade.list_agents(
        context.organization_id,
        q=q,
        domain=domain,
        pack=pack,
        status=status_filter,
        cursor=cursor,
        limit=limit,
    )


@router.get("/agents/{agent_id}")
async def read_common_agent(
    agent_id: str,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
    version: Annotated[str | None, Query(max_length=100)] = None,
) -> dict[str, Any]:
    """Read one agent projection (pack-backed) for agent detail."""
    detail = facade.agent_detail(context.organization_id, agent_id, version)
    if detail is None:
        _not_found(str(context.correlation_id))
    assert detail is not None
    return detail


@router.get("/agents/{agent_id}/versions/{version}")
async def read_common_agent_version(
    agent_id: str,
    version: str,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> dict[str, Any]:
    """Versioned agent detail alias used by product matrix paths."""
    detail = facade.agent_detail(context.organization_id, agent_id, version)
    if detail is None:
        _not_found(str(context.correlation_id))
    assert detail is not None
    return detail


@router.post(
    "/agents/{agent_id}/proposals",
    response_model=ProposalCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def propose_agent_improvement(
    agent_id: str,
    request: ProposalCreateRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> ProposalCreateResponse:
    """Submit an improvement proposal; does not mutate published agent versions."""
    record = facade.create_proposal(
        organization_id=context.organization_id,
        actor_id=context.actor_id,
        correlation_id=context.correlation_id,
        target_type="agent",
        target_id=agent_id,
        base_version=request.base_version,
        summary=request.summary,
        evidence_refs=list(request.evidence_refs),
        action_reference_id=request.action_reference_id,
    )
    if record is None:
        _denied(
            str(context.correlation_id),
            "Proposal requires a current eligible action reference for this agent.",
        )
    assert record is not None
    return ProposalCreateResponse(
        proposal_id=record.proposal_id,
        status=record.status,
        target_type=record.target_type,
        target_id=record.target_id,
        base_version=record.base_version,
        correlation_id=str(context.correlation_id),
    )


@router.post(
    "/agents/{agent_id}/forks",
    response_model=AgentForkResponse,
    status_code=status.HTTP_201_CREATED,
)
async def fork_common_agent(
    agent_id: str,
    request: AgentForkRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> AgentForkResponse:
    """Create an organization draft fork of a catalog agent."""
    result = facade.fork_agent(
        organization_id=context.organization_id,
        actor_id=context.actor_id,
        agent_id=agent_id,
        action_reference_id=request.action_reference_id,
        label=request.label,
    )
    if result is None:
        _denied(str(context.correlation_id), "Fork requires an eligible action reference.")
    assert result is not None
    return AgentForkResponse(
        fork_id=result["fork_id"],
        forked_from_id=result["forked_from"]["id"],
        forked_from_version=result["forked_from"]["version"],
        status=result["status"],
        label=result["label"],
    )


@router.post("/agents/{agent_id}/playground-runs")
async def run_agent_playground(
    agent_id: str,
    request: PlaygroundRunRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> dict[str, Any]:
    """Accept a playground run intent without provider/production activation."""
    result = facade.playground_run(
        organization_id=context.organization_id,
        agent_id=agent_id,
        action_reference_id=request.action_reference_id,
        prompt=request.prompt,
    )
    if result is None:
        _denied(
            str(context.correlation_id),
            "Playground requires an eligible playground action reference.",
        )
    assert result is not None
    return result


@router.get("/patterns")
async def list_common_patterns(
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> dict[str, Any]:
    """List pattern templates for composer / registry."""
    return facade.list_patterns(context.organization_id)


@router.get("/patterns/{pattern_id}/versions/{version}")
async def read_common_pattern_version(
    pattern_id: str,
    version: str,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> dict[str, Any]:
    """Read one pattern template projection."""
    payload = facade.list_patterns(context.organization_id)
    for item in payload["items"]:
        if item["id"] == pattern_id:
            return {
                **item,
                "version": version,
                "graph_template": {
                    "nodes": [],
                    "edges": [],
                    "slots": [],
                },
            }
    _not_found(str(context.correlation_id))
    raise AssertionError("unreachable")


@router.post(
    "/patterns/{pattern_id}/instantiate",
    response_model=SwarmCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def instantiate_pattern(
    pattern_id: str,
    request: PatternInstantiateRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> SwarmCreateResponse:
    """Create a swarm draft from a pattern using an instantiate action reference."""
    swarm = facade.create_swarm(
        organization_id=context.organization_id,
        actor_id=context.actor_id,
        correlation_id=context.correlation_id,
        name=request.name or f"From {pattern_id}",
        action_reference_id=request.action_reference_id,
        pattern_ref=pattern_id,
        goal_summary=None,
        initial_graph={
            "nodes": [
                {
                    "id": "pattern-root",
                    "kind": "pattern_slot",
                    "pattern_id": pattern_id,
                    "position": {"x": 0, "y": 0},
                }
            ],
            "edges": [],
            "policy": {},
        },
    )
    if swarm is None:
        _denied(
            str(context.correlation_id),
            "Instantiate requires an eligible pattern action reference.",
        )
    assert swarm is not None
    return SwarmCreateResponse(
        swarm_id=swarm.swarm_id,
        revision=swarm.revision,
        status=swarm.status,
        name=swarm.name,
    )


@router.post(
    "/patterns/proposals",
    response_model=ProposalCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def propose_pattern(
    request: ProposalCreateRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> ProposalCreateResponse:
    """Submit a new-pattern proposal (graph remains host-held)."""
    # Prefer resource from action; client may pass pattern id in base_version field when inventing.
    action = facade.peek_action(context.organization_id, request.action_reference_id)
    target_id = action.resource_ref if action is not None else "new-pattern"
    record = facade.create_proposal(
        organization_id=context.organization_id,
        actor_id=context.actor_id,
        correlation_id=context.correlation_id,
        target_type="pattern",
        target_id=target_id,
        base_version=request.base_version,
        summary=request.summary,
        evidence_refs=list(request.evidence_refs),
        action_reference_id=request.action_reference_id,
    )
    if record is None:
        _denied(
            str(context.correlation_id),
            "Pattern proposal requires an eligible action reference.",
        )
    assert record is not None
    return ProposalCreateResponse(
        proposal_id=record.proposal_id,
        status=record.status,
        target_type=record.target_type,
        target_id=record.target_id,
        base_version=record.base_version,
        correlation_id=str(context.correlation_id),
    )


@router.get("/health")
async def commons_health(
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    facade: Annotated[ProductFacadeService, Depends(get_product_facade)],
) -> dict[str, Any]:
    """Dashboard common-registry health summary."""
    _ = context
    return facade.commons_health()
