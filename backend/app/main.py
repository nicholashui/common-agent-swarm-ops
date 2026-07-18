"""Single in-process FastAPI Host application."""

from __future__ import annotations

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import RequestResponseEndpoint

from app.api.v1.router import api_router

API_V1_PREFIX = "/api/v1"


def is_public_api_path(path: str) -> bool:
    """Return whether a path belongs to the sole public control-plane namespace."""
    return path.startswith(f"{API_V1_PREFIX}/")


def create_app() -> FastAPI:
    """Create the sole Host process without unversioned docs or control routes."""
    application = FastAPI(
        title="Generic Swarm Business OS Host",
        version="0.1.0",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )

    @application.middleware("http")
    async def enforce_public_route(
        request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Reject every public path outside the versioned control-plane namespace."""
        if not is_public_api_path(request.url.path):
            return JSONResponse(
                status_code=404,
                content={
                    "detail": {
                        "code": "public_route_not_found",
                        "message": "Public control-plane paths are versioned under /api/v1/.",
                    }
                },
            )
        return await call_next(request)

    application.include_router(api_router, prefix=API_V1_PREFIX)
    return application


app = create_app()
