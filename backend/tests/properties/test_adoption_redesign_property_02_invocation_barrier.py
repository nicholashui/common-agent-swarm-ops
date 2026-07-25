"""Property checks for invocation association execution barriers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from hypothesis import given, settings, strategies as st

from app.models.common import RecordMetadata
from app.models.control_plane import InvocationAssociation
from app.models.identifiers import (
    AgentId,
    CorrelationId,
    DomainId,
    InvocationId,
    OrganizationId,
    RecordId,
    RunId,
)
from app.models.runs import RunRecord
from app.repositories.run_repository import InMemoryRunRepository
from app.runs.service import RunService
from app.workflows.validator import RegisteredReferences
from tests.fakes.adoption import DeterministicAdoptionRepositories, FakeFailurePlan

_NOW = datetime(2025, 1, 1, tzinfo=UTC)


@dataclass(frozen=True)
class _InvocationCase:
    """A bounded association write and its generated persistence outcome."""

    case_id: int
    pack_patch: int
    persistence_failure: bool


def _invocation_cases() -> st.SearchStrategy[_InvocationCase]:
    """Generate valid association identities and one-shot persistence failures."""
    return st.builds(
        _InvocationCase,
        case_id=st.integers(min_value=0, max_value=10_000),
        pack_patch=st.integers(min_value=0, max_value=20),
        persistence_failure=st.booleans(),
    )


def _references() -> RegisteredReferences:
    """Return the smallest registered reference set accepted by the run validator."""
    return RegisteredReferences(
        agent_ids=frozenset({"ops.planner"}),
        tool_ids=frozenset({"crm.lookup"}),
        memory_scope_ids=frozenset({"read.scope", "write.scope"}),
        risk_gate_ids=frozenset({"risk.low"}),
        rollback_plan_ids=frozenset({"rollback.crm"}),
        authorization_ids=frozenset({"approval-1"}),
    )


def _definition() -> dict[str, object]:
    """Build a valid queued workflow definition for every generated association."""
    return {
        "definition_type": "workflow_dna",
        "id": "ops.workflow",
        "version": "1.0.0",
        "owner_id": "ops.owner",
        "authorization_id": "approval-1",
        "engine": "legacy",
        "execution_budget": {
            "max_node_visits": 1,
            "max_handoffs": 1,
            "max_wall_clock_seconds": 30,
            "max_tool_requests": 1,
        },
        "memory": {"reads": ["read.scope"], "writes": ["write.scope"]},
        "risk_gate_ids": ["risk.low"],
        "rollback": {"plan_id": "rollback.crm", "compensation_step_ids": ["step-1"]},
        "steps": [
            {
                "id": "step-1",
                "agent_id": "ops.planner",
                "tool_ids": ["crm.lookup"],
                "memory_reads": ["read.scope"],
                "memory_writes": ["write.scope"],
            }
        ],
    }


def _association(case: _InvocationCase, run_id: RunId) -> InvocationAssociation:
    """Build a complete association whose identifiers vary with the generated case."""
    organization_id = OrganizationId(f"org-property-2-{case.case_id}")
    correlation_id = CorrelationId(f"correlation-property-2-{case.case_id}")
    return InvocationAssociation(
        metadata=RecordMetadata(
            record_id=RecordId(f"invocation-record-{case.case_id}"),
            organization_id=organization_id,
            correlation_id=correlation_id,
            schema_version=1,
            version=1,
            created_at=_NOW,
            updated_at=_NOW,
        ),
        invocation_id=InvocationId(f"invocation-{case.case_id}"),
        organization_id=organization_id,
        domain_id=DomainId(f"domain-{case.case_id}"),
        pack_version=f"1.0.{case.pack_patch}",
        agent_id=AgentId(f"agent-{case.case_id}"),
        workflow_id=f"workflow-{case.case_id}",
        run_id=run_id,
        correlation_id=correlation_id,
    )


def _run_service(
    run_repository: InMemoryRunRepository,
    adoption: DeterministicAdoptionRepositories,
) -> RunService:
    """Construct a service with only deterministic run, association, and audit sinks."""
    return RunService(
        run_repository,
        _references(),
        clock=lambda: _NOW,
        invocation_association_repository=adoption.invocations,
        audit_repository=adoption.audit,
    )


def _create_run(
    service: RunService, organization_id: OrganizationId, correlation_id: CorrelationId
) -> RunRecord:
    """Create the queued run that the generated association is allowed to dispatch."""
    result = service.create_queued_run(organization_id, correlation_id, _definition())
    assert result.is_success and result.value is not None
    return result.value


# Feature: adoption-redesign, Property 2: Invocation association is an execution barrier
# **Validates: Requirements 1.8, 1.9**
@settings(max_examples=100, deadline=None)
@given(case=_invocation_cases())
def test_property_02_invocation_association_is_an_execution_barrier(
    case: _InvocationCase,
) -> None:
    """A node starts only after its complete association write succeeds."""
    failure_plan = FakeFailurePlan(
        persistence_operations={"invocation.append"} if case.persistence_failure else set()
    )
    adoption = DeterministicAdoptionRepositories(failure_plan)
    organization_id = OrganizationId(f"org-property-2-{case.case_id}")
    correlation_id = CorrelationId(f"correlation-property-2-{case.case_id}")
    service = _run_service(InMemoryRunRepository(), adoption)
    run = _create_run(service, organization_id, correlation_id)
    association = _association(case, run.run_id)
    start_observations: list[int] = []

    result = service.dispatch(
        organization_id,
        run.run_id,
        f"dispatch-{case.case_id}",
        lambda _claimed: start_observations.append(len(adoption.invocations.records())),
        correlation_id,
        association=association,
    )

    if case.persistence_failure:
        assert not result.is_success
        assert start_observations == []
        assert adoption.invocations.records() == ()
        assert len(adoption.audit.records) == 1
        assert adoption.audit.records[0].action == "invocation.association.denied"
    else:
        assert result.is_success
        assert start_observations == [1]
        assert adoption.invocations.records() == (association,)
        assert adoption.audit.records == ()
