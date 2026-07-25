"""Single in-process FastAPI Host application."""

from __future__ import annotations

import inspect
import json
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, replace

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.adapters.governed import LocalInlineGovernedAdapter
from app.api.v1.adoption_services import AdoptionServices, get_adoption_services
from app.api.v1.dependencies import (
    AuthenticatedRequestContext,
    PermissionAuthorizationService,
    get_request_correlation_id,
    reject_client_authority_fields,
    set_authenticated_request_context,
)
from app.api.v1.errors import (
    PUBLIC_ENVELOPE_HEADER,
    PublicApiException,
    install_public_api_exception_handlers,
    public_error_response,
    public_success_response,
)
from app.api.v1.router import api_router
from app.api.v1.services import ControlPlaneServices, get_control_plane_services
from app.core.configuration import ConfigurationService
from app.core.ingress import IngressGuard, IngressPolicy
from app.core.transport import (
    ProductionTransportMiddleware,
    PublicApiRateLimitMiddleware,
    TransportSecurityPolicy,
)
from app.events.service import (
    ActivityProjectionSource,
    CommittedOutboxPublication,
    EventReplayPolicy,
    EventReplayService,
    OutboxPublisher,
    ProjectionService,
)
from app.governance.library_delegate import GovernedLibraryDelegate
from app.models.contracts import ErrorCode, ErrorDetail, Result
from app.models.control_plane import (
    DeliveryState,
    DeploymentConfiguration,
    EventReplayWindow,
    OutboxId,
    OutboxRecord,
    ReplayRecoveryOutcome,
)
from app.models.identifiers import CorrelationId, OrganizationId
from app.repositories.control_plane import InMemoryControlPlaneDatabase

API_V1_PREFIX = "/api/v1"

TrustedContextResolver = Callable[
    [Request],
    AuthenticatedRequestContext | None | Awaitable[AuthenticatedRequestContext | None],
]


class TrustedContextMiddleware(BaseHTTPMiddleware):
    """Install only a server-derived identity context before public-route processing."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Resolve application-owned authentication without inspecting browser authority fields."""
        if is_public_api_path(request.url.path):
            resolver = getattr(request.app.state, "trusted_context_resolver", None)
            if callable(resolver):
                resolved = resolver(request)
                context = await resolved if inspect.isawaitable(resolved) else resolved
                if isinstance(context, AuthenticatedRequestContext):
                    set_authenticated_request_context(request, context)
        return await call_next(request)


class _ControlPlaneEventStore:
    """Adapt the transactional event repository to replay without bypassing tenant scope."""

    def __init__(self, database: InMemoryControlPlaneDatabase) -> None:
        self._database = database

    def replay_window(
        self,
        organization_id: OrganizationId,
        topic: str,
        after_sequence: int,
        maximum_events: int,
    ) -> Result[EventReplayWindow, ErrorDetail]:
        with self._database.unit_of_work() as unit_of_work:
            return unit_of_work.events.replay_window(
                organization_id, topic, after_sequence, maximum_events
            )

    def append_replay_recovery(
        self, record: ReplayRecoveryOutcome
    ) -> Result[ReplayRecoveryOutcome, ErrorDetail]:
        with self._database.unit_of_work() as unit_of_work:
            return unit_of_work.events.append_replay_recovery(record)


class _CommittedControlPlaneOutboxStore:
    """Expose committed in-memory outbox rows only to the post-commit publisher."""

    def __init__(self, database: InMemoryControlPlaneDatabase) -> None:
        self._database = database

    def pending(
        self, organization_id: OrganizationId
    ) -> Result[tuple[CommittedOutboxPublication, ...], ErrorDetail]:
        """Return tenant-owned pending delivery rows from one committed database snapshot."""
        with self._database.unit_of_work() as unit_of_work:
            repository = unit_of_work.events
            state_getter = getattr(repository, "_state", None)
            if not callable(state_getter):
                return Result.failure(self._unavailable())
            state = state_getter()
            publications = tuple(
                CommittedOutboxPublication(outbox, state.events[outbox.event_id])
                for outbox in state.outbox.values()
                if (
                    outbox.metadata.organization_id == organization_id
                    and outbox.state is DeliveryState.PENDING
                    and outbox.event_id in state.events
                )
            )
            return Result.success(publications)

    def mark_published(
        self, organization_id: OrganizationId, outbox_id: OutboxId
    ) -> Result[OutboxRecord, ErrorDetail]:
        """Mark a previously committed tenant-owned row published after its sink accepts it."""
        with self._database.unit_of_work() as unit_of_work:
            repository = unit_of_work.events
            state_getter = getattr(repository, "_state", None)
            if not callable(state_getter):
                return Result.failure(self._unavailable())
            state = state_getter()
            outbox = state.outbox.get(outbox_id)
            if outbox is None or outbox.metadata.organization_id != organization_id:
                return Result.failure(self._unavailable())
            state.outbox[outbox_id] = replace(outbox, state=DeliveryState.PUBLISHED)
            return Result.success(state.outbox[outbox_id])

    @staticmethod
    def _unavailable() -> ErrorDetail:
        return ErrorDetail(
            ErrorCode.REPOSITORY_UNAVAILABLE,
            "Operational event delivery is temporarily unavailable.",
            CorrelationId("outbox"),
            retryable=True,
        )


class _ActivityProjectionStore:
    """Minimal deployment-owned projection store that never exposes protected state directly."""

    def __init__(self) -> None:
        self._sources: dict[tuple[OrganizationId, str], ActivityProjectionSource] = {}

    def read(
        self,
        organization_id: OrganizationId,
        subject_reference: str,
        correlation_id: CorrelationId,
    ) -> Result[ActivityProjectionSource, ErrorDetail]:
        """Return only a tenant-scoped stored projection or a safe unavailable outcome."""
        source = self._sources.get((organization_id, subject_reference))
        if source is None:
            return Result.failure(
                ErrorDetail(
                    ErrorCode.AUTHORIZATION_DENIED,
                    "Activity projection is unavailable.",
                    correlation_id,
                )
            )
        return Result.success(source)

    def save(self, source: ActivityProjectionSource) -> None:
        """Retain a service-produced projection for the authorized read adapter."""
        self._sources[(source.metadata.organization_id, source.subject_reference)] = source


@dataclass(frozen=True, slots=True)
class ControlPlaneComposition:
    """The complete server-owned dependency graph shared by every public route."""

    configuration_service: ConfigurationService
    database: InMemoryControlPlaneDatabase
    services: ControlPlaneServices
    adoption_services: AdoptionServices
    authorization_service: PermissionAuthorizationService
    event_replay_service: EventReplayService
    event_replay_policy: EventReplayPolicy
    activity_projection_store: _ActivityProjectionStore
    projection_service: ProjectionService
    outbox_publisher: OutboxPublisher
    governed_library_delegate: GovernedLibraryDelegate
    governed_local_adapter: LocalInlineGovernedAdapter


def _compose_control_plane(
    deployment_configuration: DeploymentConfiguration | None,
) -> ControlPlaneComposition:
    """Build one in-process, transactionally shared control-plane dependency graph."""
    configuration_service = ConfigurationService()
    if deployment_configuration is not None:
        configuration_service.initialize(deployment_configuration)

    database = InMemoryControlPlaneDatabase()
    services = ControlPlaneServices(control_plane_database=database)
    adoption_services = AdoptionServices()
    authorization_service = PermissionAuthorizationService()
    event_store = _ControlPlaneEventStore(database)
    projection_store = _ActivityProjectionStore()
    deliveries: list[object] = []
    outbox_publisher = OutboxPublisher(
        _CommittedControlPlaneOutboxStore(database),
        deliveries.append,
        authorization_service,
    )
    delegate = GovernedLibraryDelegate()
    return ControlPlaneComposition(
        configuration_service=configuration_service,
        database=database,
        services=services,
        adoption_services=adoption_services,
        authorization_service=authorization_service,
        event_replay_service=EventReplayService(event_store, authorization_service),
        event_replay_policy=EventReplayPolicy(),
        activity_projection_store=projection_store,
        projection_service=ProjectionService(authorization_service),
        outbox_publisher=outbox_publisher,
        governed_library_delegate=delegate,
        governed_local_adapter=LocalInlineGovernedAdapter(delegate, {}),
    )


def is_public_api_path(path: str) -> bool:
    """Return whether a path belongs to the sole public control-plane namespace."""
    return path.startswith(f"{API_V1_PREFIX}/")


def create_app(
    *,
    deployment_configuration: DeploymentConfiguration | None = None,
    ingress_policy: IngressPolicy | None = None,
    trusted_context_resolver: TrustedContextResolver | None = None,
) -> FastAPI:
    """Create the sole Host process without unversioned docs or control routes."""
    application = FastAPI(
        title="Generic Swarm Business OS Host",
        version="0.1.0",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    composition = _compose_control_plane(deployment_configuration)
    application.state.control_plane = composition
    application.state.configuration_service = composition.configuration_service
    application.state.control_plane_database = composition.database
    application.state.command_service = composition.services.command_service
    application.state.adoption_services = composition.adoption_services
    application.state.idempotency_service = composition.services.idempotency_service
    application.state.authorization_service = composition.authorization_service
    application.state.event_replay_service = composition.event_replay_service
    application.state.event_replay_policy = composition.event_replay_policy
    application.state.activity_projection_store = composition.activity_projection_store
    application.state.projection_service = composition.projection_service
    application.state.outbox_publisher = composition.outbox_publisher
    application.state.governed_library_delegate = composition.governed_library_delegate
    application.state.governed_local_adapter = composition.governed_local_adapter
    application.state.trusted_context_resolver = trusted_context_resolver
    application.dependency_overrides[get_control_plane_services] = lambda: composition.services
    application.dependency_overrides[get_adoption_services] = lambda: composition.adoption_services

    effective_ingress_policy = ingress_policy or IngressPolicy()
    application.state.ingress_guard = IngressGuard(
        replace(effective_ingress_policy, endpoint_rate_limits={})
    )
    transport_policy = (
        TransportSecurityPolicy.from_deployment(deployment_configuration)
        if deployment_configuration is not None
        else TransportSecurityPolicy()
    )
    configured_rate_limits = (
        deployment_configuration.rate_limits
        if deployment_configuration is not None
        else effective_ingress_policy.endpoint_rate_limits
    )
    if any(
        not isinstance(value, int) or isinstance(value, bool)
        for value in configured_rate_limits.values()
    ):
        raise ValueError("Configured rate limits must be positive integers.")
    rate_limits = {
        route: value for route, value in configured_rate_limits.items() if isinstance(value, int)
    }

    @application.middleware("http")
    async def enforce_public_route(
        request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Restrict, validate, then serialize each versioned public API request."""
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

        correlation_id = get_request_correlation_id(request)
        ingress_guard = getattr(request.app.state, "ingress_guard", None)
        if not isinstance(ingress_guard, IngressGuard):
            ingress_guard = IngressGuard()
        try:
            await ingress_guard.validate_request(request)
            await reject_client_authority_fields(request, correlation_id)
        except PublicApiException as exception:
            response: Response = public_error_response(
                exception.error,
                status_code=exception.status_code,
                headers=exception.headers,
            )
            response.headers["X-Correlation-ID"] = str(correlation_id)
            return response
        response = await call_next(request)
        response = await _public_success_envelope(response, correlation_id)
        response.headers["X-Correlation-ID"] = str(correlation_id)
        return response

    application.add_middleware(
        PublicApiRateLimitMiddleware,
        endpoint_rate_limits=rate_limits,
        window_seconds=effective_ingress_policy.rate_window_seconds,
    )
    application.add_middleware(ProductionTransportMiddleware, policy=transport_policy)
    application.add_middleware(TrustedContextMiddleware)
    install_public_api_exception_handlers(application)
    application.include_router(api_router, prefix=API_V1_PREFIX)
    return application


async def _public_success_envelope(response: Response, correlation_id: str) -> Response:
    """Wrap JSON success bodies while preserving status, headers, and empty responses."""
    if response.headers.get(PUBLIC_ENVELOPE_HEADER) == "1":
        del response.headers[PUBLIC_ENVELOPE_HEADER]
        return response
    if not 200 <= response.status_code < 300 or response.status_code in {204, 205, 304}:
        return response
    if "application/json" not in response.headers.get("content-type", ""):
        return response

    body = getattr(response, "body", None)
    if body is None:
        body_iterator = getattr(response, "body_iterator", None)
        if body_iterator is None:
            return response
        body = b"".join([chunk async for chunk in body_iterator])
    if not body:
        return response
    try:
        payload = json.loads(body)
    except (TypeError, ValueError):
        return Response(
            content=body,
            status_code=response.status_code,
            headers=_copied_headers(response),
            media_type=response.media_type,
            background=response.background,
        )

    wrapped = public_success_response(
        payload,
        correlation_id,
        status_code=response.status_code,
        headers=_copied_headers(response),
    )
    del wrapped.headers[PUBLIC_ENVELOPE_HEADER]
    return wrapped


def _copied_headers(response: Response) -> dict[str, str]:
    """Copy public headers while allowing a replacement response to set body metadata."""
    return {
        name: value
        for name, value in response.headers.items()
        if name.lower() not in {"content-length", "content-type", "x-correlation-id"}
    }


app = create_app()
