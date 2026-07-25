"""Graph-validated run creation with immutable pre-dispatch provenance."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import datetime

from app.models.common import SCHEMA_VERSION, RecordMetadata, utc_now
from app.models.contracts import ErrorCode, ErrorDetail, Result
from app.models.control_plane import GraphRevisionId, RunProvenance, RunProvenanceId
from app.models.identifiers import CorrelationId, OrganizationId, new_record_id
from app.models.runs import RunRecord
from app.repositories.control_plane import ControlPlaneUnitOfWork
from app.runs.service import RunService
from app.workflows.graph_service import GraphService


class GraphRunCreationService:
    """Create queued runs only from retained successful graph-validation evidence."""

    def __init__(
        self,
        graph_service: GraphService,
        run_service: RunService,
        unit_of_work_factory: Callable[[], ControlPlaneUnitOfWork],
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._graph_service = graph_service
        self._run_service = run_service
        self._unit_of_work_factory = unit_of_work_factory
        self._clock = clock

    def create_queued_run(
        self,
        organization_id: OrganizationId,
        correlation_id: CorrelationId,
        graph_revision_id: GraphRevisionId,
    ) -> Result[RunRecord, ErrorDetail]:
        """Persist the immutable snapshot before exposing its queued run for dispatch."""
        validation = self._graph_service.latest_validation(organization_id, graph_revision_id)
        report = validation.value
        if (
            not validation.is_success
            or report is None
            or not report.eligible_for_run
            or report.workflow_definition is None
            or report.workflow_definition_version is None
            or not (report.agent_version_ids or report.pattern_version_ids)
        ):
            return Result.failure(
                ErrorDetail(
                    ErrorCode.VALIDATION_FAILED,
                    "A successful graph validation is required before a run is created.",
                    correlation_id,
                )
            )

        workflow_definition = _library_definition(report.workflow_definition)
        now = self._clock()
        provenance = RunProvenance(
            metadata=RecordMetadata(
                record_id=new_record_id(),
                organization_id=organization_id,
                correlation_id=correlation_id,
                schema_version=SCHEMA_VERSION,
                version=1,
                created_at=now,
                updated_at=now,
            ),
            run_provenance_id=RunProvenanceId(str(new_record_id())),
            graph_revision_id=report.graph_revision_id,
            workflow_definition=workflow_definition,
            workflow_definition_version=report.workflow_definition_version,
            agent_version_ids=report.agent_version_ids,
            pattern_version_ids=report.pattern_version_ids,
        )
        with self._unit_of_work_factory() as unit_of_work:
            persisted = unit_of_work.provenance.append(provenance)
            if not persisted.is_success:
                unit_of_work.rollback()
                return Result.failure(
                    ErrorDetail(
                        ErrorCode.REPOSITORY_UNAVAILABLE,
                        "Run provenance could not be retained.",
                        correlation_id,
                        retryable=True,
                    )
                )
        return self._run_service.create_queued_run(
            organization_id,
            correlation_id,
            report.workflow_definition,
            provenance_id=provenance.run_provenance_id,
            validated_graph_report=report,
        )


def _library_definition(value: Mapping[str, object]) -> dict[str, object]:
    """Restore a retained immutable graph snapshot to validator-compatible JSON data."""
    return {str(key): _library_value(item) for key, item in value.items()}


def _library_value(value: object) -> object:
    if isinstance(value, Mapping):
        return _library_definition(value)
    if isinstance(value, tuple | frozenset):
        return [_library_value(item) for item in value]
    return value
