"""Host API: catalog of offline skill foundations."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends

from app.api.v1.dependencies import AuthenticatedRequestContext, get_authenticated_request_context
from app.skills_catalog.catalog import list_host_skills

router = APIRouter(prefix="/skills", tags=["skills-catalog"])


@router.get("/catalog")
async def skills_catalog(
    context: Annotated[AuthenticatedRequestContext, Depends(get_authenticated_request_context)],
) -> dict[str, Any]:
    data = list_host_skills()
    return {**data, "correlation_id": str(context.correlation_id)}
