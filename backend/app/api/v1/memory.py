"""Versioned scoped-memory retrieval routes."""

from __future__ import annotations

from typing import Annotated, Literal

from fastapi import APIRouter, Depends

from app.api.v1.dependencies import AuthenticatedRequestContext, get_authenticated_request_context
from app.api.v1.schemas import (
    MemoryProvenanceResponse,
    MemoryRetrievalRequest,
    MemoryRetrievalResponse,
    MemoryRetrievalResultResponse,
)
from app.api.v1.services import ControlPlaneServices, get_control_plane_services
from app.memory.retrieval import RetrievalRequest, RetrievalResponse, RetrievalTier

router = APIRouter(prefix="/memory", tags=["memory"])

type RetrievalTierValue = Literal["tier-0-semantic", "tier-1-relationship", "tier-2-synthesis"]


def _tier_value(tier: RetrievalTier) -> RetrievalTierValue:
    """Convert the closed internal enum into the versioned API literal contract."""
    match tier:
        case RetrievalTier.SEMANTIC:
            return "tier-0-semantic"
        case RetrievalTier.RELATIONSHIP:
            return "tier-1-relationship"
        case RetrievalTier.SYNTHESIS:
            return "tier-2-synthesis"
    raise ValueError(f"Unsupported retrieval tier: {tier}")


@router.post("/retrieve", response_model=MemoryRetrievalResponse)
async def retrieve_memory(
    request: MemoryRetrievalRequest,
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
    services: Annotated[ControlPlaneServices, Depends(get_control_plane_services)],
) -> MemoryRetrievalResponse:
    """Retrieve only knowledge in the authenticated requester's approved local scopes."""
    response = services.knowledge_retriever.retrieve(
        RetrievalRequest(
            requester=services.retrieval_requester(context.organization_id, context.actor_id),
            query=request.query,
            requires_relationships=request.requires_relationships,
        )
    )
    return _response(response, str(context.correlation_id))


def _response(response: RetrievalResponse, correlation_id: str) -> MemoryRetrievalResponse:
    """Render evidence, confidence, uncertainty, and correction guidance safely."""
    return MemoryRetrievalResponse(
        results=[
            MemoryRetrievalResultResponse(
                tier=_tier_value(result.tier),
                content_reference=result.content_reference,
                source_record_ids=[str(record_id) for record_id in result.source_record_ids],
                provenance=[
                    MemoryProvenanceResponse(
                        evidence_id=str(reference.evidence_id),
                        digest=reference.digest,
                        kind=reference.kind,
                    )
                    for reference in result.provenance
                ],
                confidence=result.confidence,
            )
            for result in response.results
        ],
        no_knowledge=response.no_knowledge,
        searched_tiers=[_tier_value(tier) for tier in response.searched_tiers],
        correlation_id=correlation_id,
        retrieved_at=response.retrieved_at,
        uncertainty=response.uncertainty,
        correction_control="Refine the query or request access to an approved memory scope.",
    )
