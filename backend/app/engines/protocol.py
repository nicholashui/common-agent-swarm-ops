"""Shared structural execution contract for Host-owned workflow engines."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Protocol, TypeVar

from app.models.contracts import ErrorDetail, Result
from app.models.identifiers import CorrelationId, OrganizationId, RunId

ExecutionOutcomeT_co = TypeVar("ExecutionOutcomeT_co", covariant=True)


class WorkflowEngine(Protocol[ExecutionOutcomeT_co]):
    """Execute one already-dispatched, Host-owned workflow run in process.

    Implementations must validate the immutable definition binding, use Host services
    for durable state, and expose no execution HTTP surface.
    """

    def execute(
        self,
        organization_id: OrganizationId,
        run_id: RunId,
        definition: Mapping[str, object],
        correlation_id: CorrelationId,
    ) -> Result[ExecutionOutcomeT_co, ErrorDetail]:
        """Run one active workflow attempt and return its terminal outcome."""
