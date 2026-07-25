"""Organization-scoped persistence for immutable swarm graph revisions."""

# ruff: noqa: E501
from __future__ import annotations

from dataclasses import replace
from threading import RLock
from typing import Protocol, runtime_checkable

from app.models.contracts import ErrorCode, ErrorDetail, RepositoryError, Result
from app.models.control_plane import (
    GraphRevision,
    GraphRevisionId,
    GraphValidationReport,
    SwarmInstance,
    SwarmInstanceId,
)
from app.models.identifiers import CorrelationId, OrganizationId


def _error(code: ErrorCode, message: str) -> ErrorDetail:
    return ErrorDetail(code, message, CorrelationId("graph-repository"))


@runtime_checkable
class GraphRepository(Protocol):
    """Persist organization-owned graph aggregates and append-only validation reports."""

    def create_instance(self, instance: SwarmInstance) -> Result[SwarmInstance, RepositoryError]: ...

    def get_instance(
        self, organization_id: OrganizationId, swarm_instance_id: SwarmInstanceId
    ) -> Result[SwarmInstance, RepositoryError]: ...

    def append_revision(
        self, revision: GraphRevision, expected_revision: int
    ) -> Result[GraphRevision, RepositoryError]: ...

    def get_revision(
        self, organization_id: OrganizationId, graph_revision_id: GraphRevisionId
    ) -> Result[GraphRevision, RepositoryError]: ...

    def append_validation(
        self, report: GraphValidationReport
    ) -> Result[GraphValidationReport, RepositoryError]: ...

    def latest_validation(
        self, organization_id: OrganizationId, graph_revision_id: GraphRevisionId
    ) -> Result[GraphValidationReport, RepositoryError]: ...


class InMemoryGraphRepository:
    """Lock-protected deterministic graph store with compare-and-swap revision writes."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._instances: dict[SwarmInstanceId, SwarmInstance] = {}
        self._revisions: dict[GraphRevisionId, GraphRevision] = {}
        self._validations: dict[GraphRevisionId, tuple[GraphValidationReport, ...]] = {}

    def create_instance(self, instance: SwarmInstance) -> Result[SwarmInstance, RepositoryError]:
        """Persist a new empty swarm aggregate exactly once."""
        with self._lock:
            if instance.swarm_instance_id in self._instances:
                return Result.failure(_error(ErrorCode.CONFLICT, "Swarm instance already exists."))
            self._instances[instance.swarm_instance_id] = instance
            return Result.success(instance)

    def get_instance(
        self, organization_id: OrganizationId, swarm_instance_id: SwarmInstanceId
    ) -> Result[SwarmInstance, RepositoryError]:
        """Read an aggregate only through its owning organization."""
        with self._lock:
            return self._scoped(
                organization_id, self._instances.get(swarm_instance_id), "Swarm instance"
            )

    def append_revision(
        self, revision: GraphRevision, expected_revision: int
    ) -> Result[GraphRevision, RepositoryError]:
        """Atomically append only the expected next revision and advance the aggregate pointer."""
        with self._lock:
            instance = self._instances.get(revision.swarm_instance_id)
            if instance is None or instance.metadata.organization_id != revision.metadata.organization_id:
                return Result.failure(_error(ErrorCode.NOT_FOUND, "Swarm instance was not found."))
            if (
                expected_revision != instance.current_revision
                or revision.revision != expected_revision + 1
                or revision.graph_revision_id in self._revisions
            ):
                return Result.failure(_error(ErrorCode.CONFLICT, "Swarm revision conflict."))
            metadata = replace(
                instance.metadata,
                correlation_id=revision.metadata.correlation_id,
                version=instance.metadata.version + 1,
                updated_at=revision.metadata.created_at,
            )
            self._instances[instance.swarm_instance_id] = replace(
                instance,
                metadata=metadata,
                current_revision=revision.revision,
                current_graph_revision_id=revision.graph_revision_id,
            )
            self._revisions[revision.graph_revision_id] = revision
            return Result.success(revision)

    def get_revision(
        self, organization_id: OrganizationId, graph_revision_id: GraphRevisionId
    ) -> Result[GraphRevision, RepositoryError]:
        """Read one immutable graph revision only through its owning organization."""
        with self._lock:
            return self._scoped(
                organization_id, self._revisions.get(graph_revision_id), "Graph revision"
            )

    def append_validation(
        self, report: GraphValidationReport
    ) -> Result[GraphValidationReport, RepositoryError]:
        """Retain each complete validation outcome without changing its graph revision."""
        with self._lock:
            revision = self._revisions.get(report.graph_revision_id)
            if revision is None or revision.metadata.organization_id != report.metadata.organization_id:
                return Result.failure(_error(ErrorCode.NOT_FOUND, "Graph revision was not found."))
            history = self._validations.get(report.graph_revision_id, ())
            if any(item.graph_validation_id == report.graph_validation_id for item in history):
                return Result.failure(_error(ErrorCode.CONFLICT, "Graph validation already exists."))
            self._validations[report.graph_revision_id] = (*history, report)
            return Result.success(report)

    def latest_validation(
        self, organization_id: OrganizationId, graph_revision_id: GraphRevisionId
    ) -> Result[GraphValidationReport, RepositoryError]:
        """Return the newest validation result for later run-eligibility checks."""
        with self._lock:
            revision = self._revisions.get(graph_revision_id)
            scoped = self._scoped(organization_id, revision, "Graph revision")
            if not scoped.is_success:
                return Result.failure(scoped.error or _error(ErrorCode.NOT_FOUND, "Graph revision was not found."))
            history = self._validations.get(graph_revision_id, ())
            if not history:
                return Result.failure(_error(ErrorCode.NOT_FOUND, "Graph validation was not found."))
            return Result.success(history[-1])

    @staticmethod
    def _scoped[T: SwarmInstance | GraphRevision](
        organization_id: OrganizationId, record: T | None, label: str
    ) -> Result[T, RepositoryError]:
        if record is None or record.metadata.organization_id != organization_id:
            return Result.failure(_error(ErrorCode.NOT_FOUND, f"{label} was not found."))
        return Result.success(record)
